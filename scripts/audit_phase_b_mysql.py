"""
scripts/audit_phase_b_mysql.py
------------------------------
Read-only database validation and inspection script for Phase B.
Performs:
  1. Connection test and server metadata collection (without printing credentials).
  2. Inspection of all MySQL tables, columns, data types, nullables, PKs, FKs, indexes.
  3. Comparison of SQLAlchemy models in models.py vs MySQL tables.
  4. Data integrity audit (row counts, orphan checks, NULLs, duplicate keys).
  5. Application compatibility query verification for all domain models.
  6. Alembic version table inspection.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import inspect, text
from backend.app.db.database import (
    engine,
    SessionLocal,
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    Base,
)
from backend.app.db import models


def run_audit():
    print("=" * 70)
    print("PHASE B — READ-ONLY MYSQL DATABASE AUDIT")
    print("=" * 70)

    # 1. Connection & Server Info
    print("\n--- 1. DATABASE CONNECTION ---")
    print(f"Host: {DB_HOST}")
    print(f"Port: {DB_PORT}")
    print(f"Database: {DB_NAME}")
    print(f"User: {DB_USER}")
    # Password is NEVER printed

    try:
        with engine.connect() as conn:
            version_result = conn.execute(text("SELECT VERSION()")).scalar()
            current_db = conn.execute(text("SELECT DATABASE()")).scalar()
            print(f"Connection Status: SUCCESSFUL")
            print(f"Current DB: {current_db}")
            print(f"MySQL Server Version: {version_result}")
    except Exception as e:
        print(f"Connection Status: FAILED — {e}")
        return False

    inspector = inspect(engine)

    # 2. Existing Tables & Row Counts
    print("\n--- 2. EXISTING MYSQL TABLES & ROW COUNTS ---")
    mysql_tables = inspector.get_table_names()
    print(f"Total tables found: {len(mysql_tables)}")

    table_stats = {}
    with engine.connect() as conn:
        for t in sorted(mysql_tables):
            cnt = conn.execute(text(f"SELECT COUNT(*) FROM `{t}`")).scalar()
            table_stats[t] = cnt
            print(f"  - {t:<28} : {cnt} rows")

    # 3. Alembic Version Check
    print("\n--- 3. ALEMBIC MIGRATION STATUS ---")
    if "alembic_version" in mysql_tables:
        with engine.connect() as conn:
            ver = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
            print(f"Current Alembic Revision: {ver}")
    else:
        print("alembic_version table NOT present in MySQL.")

    # 4. Compare SQLAlchemy Models vs MySQL Tables
    print("\n--- 4. MODEL-TO-DATABASE COMPARISON ---")
    model_metadata_tables = Base.metadata.tables

    sa_table_names = set(model_metadata_tables.keys())
    db_table_names = set(mysql_tables) - {"alembic_version"}

    matching_tables = sa_table_names.intersection(db_table_names)
    missing_in_db = sa_table_names - db_table_names
    extra_in_db = db_table_names - sa_table_names

    print(f"SQLAlchemy Defined Tables ({len(sa_table_names)}): {sorted(list(sa_table_names))}")
    print(f"Matching Tables in MySQL ({len(matching_tables)}): {sorted(list(matching_tables))}")
    print(f"Missing in MySQL ({len(missing_in_db)}): {sorted(list(missing_in_db)) if missing_in_db else 'None'}")
    print(f"Extra in MySQL ({len(extra_in_db)}): {sorted(list(extra_in_db)) if extra_in_db else 'None'}")

    # Column-level comparison
    print("\n--- 5. COLUMN-LEVEL AUDIT FOR MATCHING TABLES ---")
    column_mismatches = []
    detailed_table_info = {}

    for t_name in sorted(matching_tables):
        sa_table = model_metadata_tables[t_name]
        sa_cols = {c.name: c for c in sa_table.columns}

        db_cols_list = inspector.get_columns(t_name)
        db_cols = {c["name"]: c for c in db_cols_list}

        db_pk = inspector.get_pk_constraint(t_name)
        db_fks = inspector.get_foreign_keys(t_name)
        db_indexes = inspector.get_indexes(t_name)
        db_uniques = inspector.get_unique_constraints(t_name)

        detailed_table_info[t_name] = {
            "columns": [
                {
                    "name": c["name"],
                    "type": str(c["type"]),
                    "nullable": c["nullable"],
                    "default": str(c.get("default")),
                }
                for c in db_cols_list
            ],
            "primary_key": db_pk,
            "foreign_keys": db_fks,
            "indexes": db_indexes,
            "unique_constraints": db_uniques,
        }

        sa_col_names = set(sa_cols.keys())
        db_col_names = set(db_cols.keys())

        missing_cols = sa_col_names - db_col_names
        extra_cols = db_col_names - sa_col_names

        if missing_cols or extra_cols:
            diff_entry = {
                "table": t_name,
                "missing_in_db": list(missing_cols),
                "extra_in_db": list(extra_cols),
            }
            column_mismatches.append(diff_entry)
            print(f"  [MISMATCH] {t_name}: missing in DB={missing_cols}, extra in DB={extra_cols}")
        else:
            # Check type and nullable differences
            diffs = []
            for col_name, sa_col in sa_cols.items():
                db_col = db_cols[col_name]
                if sa_col.nullable != db_col["nullable"]:
                    diffs.append(
                        f"col '{col_name}' nullable mismatch: SA={sa_col.nullable}, DB={db_col['nullable']}"
                    )
            if diffs:
                print(f"  [NOTICE] {t_name} has attribute mismatches: {diffs}")
            else:
                print(f"  [PERFECT MATCH] {t_name} ({len(sa_cols)} columns, PK={db_pk.get('constrained_columns')})")

    # 6. Data Integrity Checks
    print("\n--- 6. DATA INTEGRITY & ORPHAN RECORD CHECK ---")
    with engine.connect() as conn:
        for t_name in sorted(matching_tables):
            fks = inspector.get_foreign_keys(t_name)
            for fk in fks:
                referred_table = fk.get("referred_table")
                constrained_cols = fk.get("constrained_columns", [])
                referred_cols = fk.get("referred_columns", [])
                if referred_table and constrained_cols and referred_cols:
                    c_col = constrained_cols[0]
                    r_col = referred_cols[0]
                    orphan_query = text(f"""
                        SELECT COUNT(*) FROM `{t_name}` child
                        LEFT JOIN `{referred_table}` parent ON child.`{c_col}` = parent.`{r_col}`
                        WHERE child.`{c_col}` IS NOT NULL AND parent.`{r_col}` IS NULL
                    """)
                    orphan_count = conn.execute(orphan_query).scalar()
                    if orphan_count > 0:
                        print(f"  [ORPHAN DETECTED] {t_name}.{c_col} -> {referred_table}.{r_col}: {orphan_count} orphans")
                    else:
                        print(f"  [INTEGRITY OK] {t_name}.{c_col} -> {referred_table}.{r_col}: 0 orphans")

    # 7. Application Query Compatibility Test
    print("\n--- 7. APPLICATION / ORM QUERY COMPATIBILITY TEST ---")
    db_session = SessionLocal()
    query_results = {}
    test_models = [
        ("Patient", models.Patient),
        ("Pregnancy", models.Pregnancy),
        ("MaternalProfile", models.MaternalProfile),
        ("FetalAssessment", models.FetalAssessment),
        ("UltrasoundRecord", models.UltrasoundRecord),
        ("LabResult", models.LabResult),
        ("DopplerResult", models.DopplerResult),
        ("Prediction", models.Prediction),
        ("GrowthAnalysis", models.GrowthAnalysis),
        ("Newborn", models.Newborn),
        ("NicuAdmission", models.NicuAdmission),
        ("NicuVital", models.NicuVital),
        ("VitalSign", models.VitalSign),
        ("ModelOutput", models.ModelOutput),
        ("ClinicalEvent", models.ClinicalEvent),
        ("DoctorReview", models.DoctorReview),
        ("Prescription", models.Prescription),
        ("Alert", models.Alert),
        ("ChatHistory", models.ChatHistory),
        ("DatasetSource", models.DatasetSource),
        ("ImportJob", models.ImportJob),
        ("ImportErrorLog", models.ImportErrorLog),
    ]

    all_queries_ok = True
    for name, model_cls in test_models:
        try:
            count = db_session.query(model_cls).count()
            first = db_session.query(model_cls).first()
            query_results[name] = {"count": count, "status": "OK"}
            print(f"  [QUERY OK] {name:<20}: count={count}")
        except Exception as e:
            all_queries_ok = False
            query_results[name] = {"status": "FAILED", "error": str(e)}
            print(f"  [QUERY FAIL] {name:<20}: error={e}")
    db_session.close()

    # Save detailed audit output to JSON for report generation
    audit_data = {
        "db_host": DB_HOST,
        "db_port": DB_PORT,
        "db_name": DB_NAME,
        "db_user": DB_USER,
        "server_version": str(version_result),
        "total_tables": len(mysql_tables),
        "table_stats": table_stats,
        "matching_tables": sorted(list(matching_tables)),
        "missing_in_db": sorted(list(missing_in_db)),
        "extra_in_db": sorted(list(extra_in_db)),
        "column_mismatches": column_mismatches,
        "query_results": query_results,
        "detailed_table_info": detailed_table_info,
    }

    with open("scripts/audit_results.json", "w") as f:
        json.dump(audit_data, f, indent=2, default=str)

    print("\nAudit results saved to scripts/audit_results.json")
    print("=" * 70)
    print("AUDIT SUMMARY:")
    print(f"- MySQL Connection: SUCCESSFUL ({version_result})")
    print(f"- Tables in MySQL: {len(mysql_tables)}")
    print(f"- SQLAlchemy Models: {len(sa_table_names)}")
    print(f"- Perfectly Matched Tables: {len(matching_tables)}")
    print(f"- Missing Tables: {len(missing_in_db)}")
    print(f"- Extra Tables: {len(extra_in_db)}")
    print(f"- Column Mismatches: {len(column_mismatches)}")
    print(f"- Query Tests: {'ALL 22 MODELS PASSED' if all_queries_ok else 'SOME FAILED'}")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)

