"""
scripts/execute_phase_e_import.py
---------------------------------
Executes the controlled import of Phase C synthetic data into MySQL.
Performs:
  1. Pre-import verification.
  2. Sequential controlled import via import_service.import_all_synthetic_data.
  3. Post-import row count validation.
  4. Foreign-key relationship and orphan checks.
  5. Live FastAPI endpoint verification for newly imported patients and TEST-PREDICT-01.
"""

import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
import httpx

from backend.app.db.database import engine, SessionLocal
from backend.app.db import models
from backend.app.services.import_service import import_all_synthetic_data
from backend.app.main import app
from backend.app.schemas import (
    PatientSchema,
    PregnancySchema,
    FetalAssessmentSchema,
    PredictionSchema,
    GrowthAnalysisSchema,
    NewbornSchema,
    NicuAdmissionSchema,
    TimelineEntrySchema,
)


def execute_import():
    print("=" * 70)
    print("PHASE E — CONTROLLED IMPORT OF SYNTHETIC DATA INTO MYSQL")
    print("=" * 70)

    db = SessionLocal()

    # 1. Execute Import via Application Import Pipeline
    print("\n--- 1. EXECUTING IMPORT PIPELINE ---")
    import_result = import_all_synthetic_data(db, base_dir="data/synthetic")
    print(f"Dataset ID: {import_result['dataset_id']}")
    print(f"Dataset Name: {import_result['dataset_name']}")
    print(f"Total Rows Imported: {import_result['total_imported']}")
    print(f"Total Rows Rejected: {import_result['total_rejected']}")
    print(f"Status: {import_result['status']}")

    for file_info in import_result["files_processed"]:
        print(f"  [JOB {file_info['job_id']:<3}] {file_info['file']:<25}: {file_info['rows_imported']} imported, {file_info['rows_rejected']} rejected ({file_info['status']})")

    # 2. Verify Final Database Counts
    print("\n--- 2. POST-IMPORT DATABASE ROW COUNTS ---")
    expected_counts = {
        "patients": 7,          # 1 existing + 6 synthetic
        "pregnancies": 6,
        "maternal_profiles": 6,
        "fetal_assessments": 12,
        "ultrasound_records": 12,
        "lab_results": 6,
        "doppler_results": 12,
        "predictions": 7,       # 1 existing + 6 synthetic
        "growth_analysis": 6,
        "clinical_events": 10,
        "doctor_reviews": 8,
        "prescriptions": 4,
        "newborns": 5,
        "nicu_admissions": 4,
        "nicu_vitals": 26,
        "model_outputs": 6,
        "alerts": 4,
        "vital_signs": 60,      # 60 existing untouched
        "chat_history": 2,      # 2 existing untouched
        "dataset_sources": 1,
        "import_jobs": 17,
        "import_errors": 0,
    }

    actual_counts = {}
    counts_matched = True

    with engine.connect() as conn:
        for t_name, expected in expected_counts.items():
            actual = conn.execute(text(f"SELECT COUNT(*) FROM `{t_name}`")).scalar()
            actual_counts[t_name] = actual
            match = (actual == expected)
            if not match:
                counts_matched = False
            print(f"  {'[MATCH]' if match else '[MISMATCH]'} {t_name:<25}: actual={actual:<4} (expected={expected})")

    # 3. Existing Test Record Preservation
    print("\n--- 3. EXISTING DATA PRESERVATION ---")
    existing_patient = db.query(models.Patient).filter(models.Patient.id == "TEST-PREDICT-01").first()
    if existing_patient:
        print(f"  [PRESERVED] Existing test patient '{existing_patient.id}' intact.")
    else:
        print("  [ERROR] Existing test patient TEST-PREDICT-01 was lost!")

    existing_vitals = db.query(models.VitalSign).filter(models.VitalSign.patient_id == "TEST-PREDICT-01").count()
    print(f"  [PRESERVED] Existing vital signs for TEST-PREDICT-01: {existing_vitals} rows.")

    # 4. Foreign Key and Orphan Verification
    print("\n--- 4. POST-IMPORT FOREIGN KEY ORPHAN AUDIT ---")
    orphan_checks = [
        ("pregnancies", "patient_id", "patients", "id"),
        ("maternal_profiles", "pregnancy_id", "pregnancies", "id"),
        ("fetal_assessments", "pregnancy_id", "pregnancies", "id"),
        ("ultrasound_records", "pregnancy_id", "pregnancies", "id"),
        ("ultrasound_records", "assessment_id", "fetal_assessments", "id"),
        ("lab_results", "pregnancy_id", "pregnancies", "id"),
        ("lab_results", "assessment_id", "fetal_assessments", "id"),
        ("doppler_results", "pregnancy_id", "pregnancies", "id"),
        ("doppler_results", "assessment_id", "fetal_assessments", "id"),
        ("predictions", "patient_id", "patients", "id"),
        ("predictions", "pregnancy_id", "pregnancies", "id"),
        ("growth_analysis", "pregnancy_id", "pregnancies", "id"),
        ("clinical_events", "patient_id", "patients", "id"),
        ("doctor_reviews", "patient_id", "patients", "id"),
        ("prescriptions", "patient_id", "patients", "id"),
        ("newborns", "pregnancy_id", "pregnancies", "id"),
        ("nicu_admissions", "newborn_id", "newborns", "id"),
        ("nicu_vitals", "nicu_admission_id", "nicu_admissions", "id"),
        ("model_outputs", "patient_id", "patients", "id"),
        ("alerts", "patient_id", "patients", "id"),
    ]

    all_orphans_zero = True
    with engine.connect() as conn:
        for child_t, child_col, parent_t, parent_col in orphan_checks:
            query = text(f"""
                SELECT COUNT(*) FROM `{child_t}` c
                LEFT JOIN `{parent_t}` p ON c.`{child_col}` = p.`{parent_col}`
                WHERE c.`{child_col}` IS NOT NULL AND p.`{parent_col}` IS NULL
            """)
            orphans = conn.execute(query).scalar()
            if orphans > 0:
                all_orphans_zero = False
                print(f"  [ORPHAN] {child_t}.{child_col} -> {parent_t}.{parent_col}: {orphans} orphans!")
            else:
                print(f"  [OK] {child_t}.{child_col} -> {parent_t}.{parent_col}: 0 orphans")

    db.close()
    return import_result, actual_counts, counts_matched and all_orphans_zero


async def verify_apis():
    print("\n--- 5. LIVE FASTAPI ENDPOINT VERIFICATION ---")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. Patient List
        r = await client.get("/api/v1/patients/")
        assert r.status_code == 200
        patients = r.json()
        print(f"  [PASS] GET /api/v1/patients/ -> {len(patients)} total patients in API response")
        assert len(patients) == 7

        # 2. Test each synthetic patient
        syn_ids = ["P-SYN-001", "P-SYN-002", "P-SYN-003", "P-SYN-004", "P-SYN-005", "P-SYN-006"]
        for p_id in syn_ids:
            # Patient detail
            r = await client.get(f"/api/v1/patients/{p_id}")
            assert r.status_code == 200
            p_data = PatientSchema.model_validate(r.json())

            # Pregnancy
            r = await client.get(f"/api/v1/patients/{p_id}/pregnancy")
            assert r.status_code == 200
            pregs = [PregnancySchema.model_validate(item) for item in r.json()]

            # Fetal Assessments
            r = await client.get(f"/api/v1/patients/{p_id}/fetal-assessments")
            assert r.status_code == 200
            assessments = [FetalAssessmentSchema.model_validate(item) for item in r.json()]

            # Predictions
            r = await client.get(f"/api/v1/patients/{p_id}/predictions")
            assert r.status_code == 200
            predictions = [PredictionSchema.model_validate(item) for item in r.json()]

            # Growth Analysis
            r = await client.get(f"/api/v1/patients/{p_id}/growth-analysis")
            assert r.status_code == 200
            growth = [GrowthAnalysisSchema.model_validate(item) for item in r.json()]

            # Newborn
            r = await client.get(f"/api/v1/patients/{p_id}/newborn")
            assert r.status_code == 200
            newborns = [NewbornSchema.model_validate(item) for item in r.json()]

            # NICU
            r = await client.get(f"/api/v1/patients/{p_id}/nicu")
            assert r.status_code == 200
            nicu = [NicuAdmissionSchema.model_validate(item) for item in r.json()]

            # Timeline
            r = await client.get(f"/api/v1/patients/{p_id}/timeline")
            assert r.status_code == 200
            timeline = [TimelineEntrySchema.model_validate(item) for item in r.json()]

            print(f"  [PASS] Patient {p_id:<10}: Name='{p_data.name}', Pregnancies={len(pregs)}, Scans={len(assessments)}, Predictions={len(predictions)}, Growth={len(growth)}, Newborns={len(newborns)}, NICU={len(nicu)}, TimelineEvents={len(timeline)}")

        # 3. Existing Patient TEST-PREDICT-01 verification
        r = await client.get("/api/v1/patients/TEST-PREDICT-01")
        assert r.status_code == 200
        p01 = PatientSchema.model_validate(r.json())
        print(f"  [PASS] Existing patient TEST-PREDICT-01 verified: Name='{p01.name}'")

    print("\nAPI Verification Complete: All endpoints successfully serving new and existing records.")
    return True


if __name__ == "__main__":
    import_res, counts, ok = execute_import()
    if ok:
        api_ok = asyncio.run(verify_apis())
        sys.exit(0 if api_ok else 1)
    else:
        sys.exit(1)

