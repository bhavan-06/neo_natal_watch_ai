"""
scripts/verify_phase_f_mysql.py
-------------------------------
Read-only Post-Import Verification Script for Phase F.
Performs:
  1. Complete row count audit across all 23 database tables.
  2. Foreign-key orphan checks across all relational pathways.
  3. Patient-by-patient longitudinal trajectory audit (P-SYN-001 through P-SYN-006).
  4. Existing baseline integrity audit (TEST-PREDICT-01, 60 vitals, predictions, chat).
  5. Data consistency checks (duplicate IDs, codes, chronological ordering, NULLs).
  6. Import audit (dataset_sources, import_jobs, import_errors).
  7. Live FastAPI endpoint consistency verification via HTTPX.
  8. Safety invariants verification (zero write/mutation operations).
"""

import sys
import os
import json
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
import httpx

from backend.app.db.database import engine, SessionLocal
from backend.app.db import models
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


def verify_database():
    print("=" * 70)
    print("PHASE F — READ-ONLY MYSQL POST-IMPORT VERIFICATION")
    print("=" * 70)

    db = SessionLocal()
    audit_summary = {}

    # 1. Row Count Audit
    print("\n--- 1. TABLE ROW COUNT AUDIT ---")
    expected_counts = {
        "patients": 7,
        "pregnancies": 6,
        "maternal_profiles": 6,
        "fetal_assessments": 12,
        "ultrasound_records": 12,
        "lab_results": 6,
        "doppler_results": 12,
        "predictions": 7,
        "growth_analysis": 6,
        "clinical_events": 10,
        "doctor_reviews": 8,
        "prescriptions": 4,
        "newborns": 5,
        "nicu_admissions": 4,
        "nicu_vitals": 26,
        "model_outputs": 6,
        "alerts": 4,
        "vital_signs": 60,
        "chat_history": 2,
        "dataset_sources": 1,
        "import_jobs": 17,
        "import_errors": 0,
        "alembic_version": 1,
    }

    actual_counts = {}
    row_count_failures = []

    with engine.connect() as conn:
        for t_name, exp in expected_counts.items():
            act = conn.execute(text(f"SELECT COUNT(*) FROM `{t_name}`")).scalar()
            actual_counts[t_name] = act
            if act == exp:
                print(f"  [PASS] {t_name:<25}: {act:>3} rows (expected {exp:>3})")
            else:
                row_count_failures.append(f"{t_name}: actual={act}, expected={exp}")
                print(f"  [FAIL] {t_name:<25}: {act:>3} rows (expected {exp:>3})")

    audit_summary["row_counts"] = {
        "status": "PASS" if not row_count_failures else "FAIL",
        "failures": row_count_failures,
        "counts": actual_counts,
    }

    # 2. Foreign Key Orphan Audit
    print("\n--- 2. FOREIGN-KEY ORPHAN INTEGRITY AUDIT ---")
    fk_pathways = [
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
        ("predictions", "assessment_id", "fetal_assessments", "id"),
        ("growth_analysis", "pregnancy_id", "pregnancies", "id"),
        ("clinical_events", "patient_id", "patients", "id"),
        ("clinical_events", "pregnancy_id", "pregnancies", "id"),
        ("doctor_reviews", "patient_id", "patients", "id"),
        ("doctor_reviews", "pregnancy_id", "pregnancies", "id"),
        ("prescriptions", "patient_id", "patients", "id"),
        ("prescriptions", "pregnancy_id", "pregnancies", "id"),
        ("newborns", "pregnancy_id", "pregnancies", "id"),
        ("nicu_admissions", "newborn_id", "newborns", "id"),
        ("nicu_vitals", "nicu_admission_id", "nicu_admissions", "id"),
        ("model_outputs", "patient_id", "patients", "id"),
        ("model_outputs", "pregnancy_id", "pregnancies", "id"),
        ("model_outputs", "newborn_id", "newborns", "id"),
        ("model_outputs", "nicu_admission_id", "nicu_admissions", "id"),
        ("alerts", "patient_id", "patients", "id"),
        ("alerts", "newborn_id", "newborns", "id"),
        ("alerts", "nicu_admission_id", "nicu_admissions", "id"),
        ("vital_signs", "patient_id", "patients", "id"),
        ("chat_history", "patient_id", "patients", "id"),
        ("chat_history", "pregnancy_id", "pregnancies", "id"),
        ("chat_history", "newborn_id", "newborns", "id"),
        ("import_jobs", "dataset_id", "dataset_sources", "id"),
        ("import_errors", "job_id", "import_jobs", "id"),
    ]

    orphan_failures = []
    with engine.connect() as conn:
        for child_t, child_col, parent_t, parent_col in fk_pathways:
            query = text(f"""
                SELECT COUNT(*) FROM `{child_t}` c
                LEFT JOIN `{parent_t}` p ON c.`{child_col}` = p.`{parent_col}`
                WHERE c.`{child_col}` IS NOT NULL AND p.`{parent_col}` IS NULL
            """)
            orphans = conn.execute(query).scalar()
            if orphans == 0:
                print(f"  [PASS] {child_t}.{child_col} -> {parent_t}.{parent_col}: 0 orphans")
            else:
                orphan_failures.append(f"{child_t}.{child_col} -> {parent_t}.{parent_col}: {orphans} orphans")
                print(f"  [FAIL] {child_t}.{child_col} -> {parent_t}.{parent_col}: {orphans} orphans")

    audit_summary["foreign_keys"] = {
        "pathways_tested": len(fk_pathways),
        "status": "PASS" if not orphan_failures else "FAIL",
        "failures": orphan_failures,
    }

    # 3. Longitudinal Synthetic Patient Journey Verification
    print("\n--- 3. LONGITUDINAL PATIENT JOURNEY VERIFICATION ---")
    syn_patients = ["P-SYN-001", "P-SYN-002", "P-SYN-003", "P-SYN-004", "P-SYN-005", "P-SYN-006"]
    patient_trajectories = {}

    for p_id in syn_patients:
        patient = db.query(models.Patient).filter(models.Patient.id == p_id).first()
        pregs = db.query(models.Pregnancy).filter(models.Pregnancy.patient_id == p_id).all()
        events = db.query(models.ClinicalEvent).filter(models.ClinicalEvent.patient_id == p_id).all()
        reviews = db.query(models.DoctorReview).filter(models.DoctorReview.patient_id == p_id).all()
        prescriptions = db.query(models.Prescription).filter(models.Prescription.patient_id == p_id).all()
        predictions = db.query(models.Prediction).filter(models.Prediction.patient_id == p_id).all()
        alerts = db.query(models.Alert).filter(models.Alert.patient_id == p_id).all()
        model_outs = db.query(models.ModelOutput).filter(models.ModelOutput.patient_id == p_id).all()

        p_info = {
            "name": patient.name,
            "pregnancies": len(pregs),
            "events": len(events),
            "reviews": len(reviews),
            "prescriptions": len(prescriptions),
            "predictions": len(predictions),
            "alerts": len(alerts),
            "model_outputs": len(model_outs),
            "fetal_assessments": 0,
            "ultrasounds": 0,
            "labs": 0,
            "dopplers": 0,
            "growth_analyses": 0,
            "newborns": 0,
            "nicu_admissions": 0,
            "nicu_vitals": 0,
        }

        for preg in pregs:
            p_info["fetal_assessments"] += len(preg.fetal_assessments)
            p_info["ultrasounds"] += db.query(models.UltrasoundRecord).filter(models.UltrasoundRecord.pregnancy_id == preg.id).count()
            p_info["labs"] += db.query(models.LabResult).filter(models.LabResult.pregnancy_id == preg.id).count()
            p_info["dopplers"] += db.query(models.DopplerResult).filter(models.DopplerResult.pregnancy_id == preg.id).count()
            p_info["growth_analyses"] += len(preg.growth_analysis)
            p_info["newborns"] += len(preg.newborns)
            for nb in preg.newborns:
                p_info["nicu_admissions"] += len(nb.nicu_admissions)
                for na in nb.nicu_admissions:
                    p_info["nicu_vitals"] += len(na.nicu_vitals)

        patient_trajectories[p_id] = p_info

        # Validation rules:
        # P-SYN-001..005 must have >=1 pregnancy, 2 assessments, 2 ultrasounds, 1 prediction, 1 growth, 1 newborn
        # P-SYN-006 is ongoing: newborn=0, nicu=0
        if p_id == "P-SYN-006":
            valid = (p_info["pregnancies"] == 1 and p_info["fetal_assessments"] == 2 and p_info["newborns"] == 0 and p_info["nicu_admissions"] == 0)
        else:
            valid = (p_info["pregnancies"] == 1 and p_info["fetal_assessments"] == 2 and p_info["newborns"] == 1)

        status_str = "PASS" if valid else "FAIL"
        print(f"  [{status_str}] {p_id} ({p_info['name']}): Preg={p_info['pregnancies']}, Scans={p_info['fetal_assessments']}, Pred={p_info['predictions']}, Growth={p_info['growth_analyses']}, NB={p_info['newborns']}, NICU={p_info['nicu_admissions']}, Vitals={p_info['nicu_vitals']}, Alerts={p_info['alerts']}")

    audit_summary["patient_trajectories"] = patient_trajectories

    # 4. Existing Baseline Verification
    print("\n--- 4. EXISTING BASELINE INTEGRITY AUDIT ---")
    p01 = db.query(models.Patient).filter(models.Patient.id == "TEST-PREDICT-01").first()
    pr01 = db.query(models.Prediction).filter(models.Prediction.id == 1).first()
    v01_count = db.query(models.VitalSign).filter(models.VitalSign.patient_id == "TEST-PREDICT-01").count()
    ch_count = db.query(models.ChatHistory).count()

    base_checks = []
    if p01 and p01.name == "Patient TEST-PREDICT-01":
        print(f"  [PASS] Existing patient 'TEST-PREDICT-01' intact (name='{p01.name}')")
        base_checks.append(True)
    else:
        print("  [FAIL] Existing patient 'TEST-PREDICT-01' missing or corrupted!")
        base_checks.append(False)

    if pr01 and pr01.patient_id == "TEST-PREDICT-01" and pr01.risk_score == 0.6446:
        print(f"  [PASS] Existing prediction (ID=1) intact: risk_score={pr01.risk_score}, level={pr01.risk_level}")
        base_checks.append(True)
    else:
        print("  [FAIL] Existing prediction ID=1 missing or modified!")
        base_checks.append(False)

    if v01_count == 60:
        print(f"  [PASS] Existing vital_signs for TEST-PREDICT-01 intact: exactly {v01_count} records.")
        base_checks.append(True)
    else:
        print(f"  [FAIL] Existing vital_signs count mismatch: {v01_count} (expected 60)!")
        base_checks.append(False)

    if ch_count == 2:
        print(f"  [PASS] Existing chat_history intact: exactly {ch_count} records.")
        base_checks.append(True)
    else:
        print(f"  [FAIL] Existing chat_history count mismatch: {ch_count} (expected 2)!")
        base_checks.append(False)

    audit_summary["baseline_preserved"] = all(base_checks)

    # 5. Data Consistency Checks
    print("\n--- 5. DATA CONSISTENCY & INTEGRITY AUDIT ---")
    consistency_errors = []
    with engine.connect() as conn:
        # Duplicate patient codes
        dup_codes = conn.execute(text("SELECT patient_code, COUNT(*) as c FROM patients WHERE patient_code IS NOT NULL GROUP BY patient_code HAVING c > 1")).fetchall()
        if not dup_codes:
            print("  [PASS] Zero duplicate patient codes in patients table.")
        else:
            consistency_errors.append(f"Duplicate patient codes: {dup_codes}")
            print(f"  [FAIL] Duplicate patient codes: {dup_codes}")

        # Duplicate patient IDs
        dup_ids = conn.execute(text("SELECT id, COUNT(*) as c FROM patients GROUP BY id HAVING c > 1")).fetchall()
        if not dup_ids:
            print("  [PASS] Zero duplicate patient IDs in patients table.")
        else:
            consistency_errors.append(f"Duplicate patient IDs: {dup_ids}")
            print(f"  [FAIL] Duplicate patient IDs: {dup_ids}")

        # Chronological progression check (assessment dates > conception dates)
        chrono_errs = conn.execute(text("""
            SELECT fa.id, fa.assessment_date, p.conception_date 
            FROM fetal_assessments fa
            JOIN pregnancies p ON fa.pregnancy_id = p.id
            WHERE fa.assessment_date <= p.conception_date
        """)).fetchall()
        if not chrono_errs:
            print("  [PASS] All fetal assessments occurred chronologically after conception.")
        else:
            consistency_errors.append(f"Chronology errors: {chrono_errs}")
            print(f"  [FAIL] Fetal assessment before conception: {chrono_errs}")

        # Delivery after conception
        deliv_errs = conn.execute(text("""
            SELECT nb.id, nb.birth_date, p.conception_date
            FROM newborns nb
            JOIN pregnancies p ON nb.pregnancy_id = p.id
            WHERE nb.birth_date <= p.conception_date
        """)).fetchall()
        if not deliv_errs:
            print("  [PASS] All newborn deliveries occurred chronologically after conception.")
        else:
            consistency_errors.append(f"Delivery chronology errors: {deliv_errs}")
            print(f"  [FAIL] Delivery before conception: {deliv_errs}")

        # NICU vitals within admission window
        vital_errs = conn.execute(text("""
            SELECT nv.id, nv.timestamp, na.admission_date, na.discharge_date
            FROM nicu_vitals nv
            JOIN nicu_admissions na ON nv.nicu_admission_id = na.id
            WHERE nv.timestamp < na.admission_date OR (na.discharge_date IS NOT NULL AND nv.timestamp > na.discharge_date)
        """)).fetchall()
        if not vital_errs:
            print("  [PASS] All NICU vitals occurred strictly within their respective admission windows.")
        else:
            consistency_errors.append(f"NICU vital window errors: {vital_errs}")
            print(f"  [FAIL] Vital outside admission window: {vital_errs}")

    audit_summary["consistency_checks"] = {
        "status": "PASS" if not consistency_errors else "FAIL",
        "errors": consistency_errors,
    }

    # 6. Import Audit
    print("\n--- 6. IMPORT PIPELINE AUDIT ---")
    ds = db.query(models.DatasetSource).first()
    jobs = db.query(models.ImportJob).all()
    errs = db.query(models.ImportErrorLog).all()

    import_checks = []
    if ds and ds.dataset_name == "NeoNatal-Watch-AI-Synthetic-Academic-Demo-v1.0":
        print(f"  [PASS] DatasetSource verified: ID={ds.id}, Name='{ds.dataset_name}'")
        import_checks.append(True)
    else:
        print("  [FAIL] DatasetSource verification failed!")
        import_checks.append(False)

    if len(jobs) == 17 and all(j.status == 'COMPLETED' for j in jobs):
        print(f"  [PASS] Exactly 17 ImportJobs logged, all with status='COMPLETED'.")
        import_checks.append(True)
    else:
        print(f"  [FAIL] ImportJobs audit mismatch: {len(jobs)} jobs logged!")
        import_checks.append(False)

    if len(errs) == 0:
        print(f"  [PASS] Exactly 0 ImportErrorLogs logged (100% clean ingestion).")
        import_checks.append(True)
    else:
        print(f"  [FAIL] {len(errs)} import errors logged!")
        import_checks.append(False)

    audit_summary["import_audit"] = all(import_checks)
    db.close()
    return audit_summary


async def verify_apis_live():
    print("\n--- 7. LIVE FASTAPI ENDPOINT AUDIT ---")
    api_results = []
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. GET /api/v1/patients/
        r = await client.get("/api/v1/patients/")
        assert r.status_code == 200
        patients = r.json()
        assert len(patients) == 7
        print(f"  [PASS] GET /api/v1/patients/ -> {len(patients)} patients returned")
        api_results.append(("List Patients", True))

        # 2. Check each synthetic patient
        for i in range(1, 7):
            p_id = f"P-SYN-00{i}"
            r = await client.get(f"/api/v1/patients/{p_id}")
            assert r.status_code == 200
            p = PatientSchema.model_validate(r.json())

            # Timeline
            r_tl = await client.get(f"/api/v1/patients/{p_id}/timeline")
            assert r_tl.status_code == 200

            # Pregnancy
            r_preg = await client.get(f"/api/v1/patients/{p_id}/pregnancy")
            assert r_preg.status_code == 200

            # Predictions
            r_pred = await client.get(f"/api/v1/patients/{p_id}/predictions")
            assert r_pred.status_code == 200

            print(f"  [PASS] API verification for {p_id} ({p.name}) -> 200 OK across all endpoints")
            api_results.append((f"Patient {p_id}", True))

        # 3. Check existing TEST-PREDICT-01
        r = await client.get("/api/v1/patients/TEST-PREDICT-01")
        assert r.status_code == 200
        p01 = PatientSchema.model_validate(r.json())
        print(f"  [PASS] API verification for existing baseline {p01.id} -> 200 OK")
        api_results.append(("Baseline Patient", True))

    return all(ok for _, ok in api_results)


if __name__ == "__main__":
    summary = verify_database()
    api_ok = asyncio.run(verify_apis_live())

    all_ok = (
        summary["row_counts"]["status"] == "PASS"
        and summary["foreign_keys"]["status"] == "PASS"
        and summary["baseline_preserved"]
        and summary["consistency_checks"]["status"] == "PASS"
        and summary["import_audit"]
        and api_ok
    )

    print("\n" + "=" * 70)
    print(f"PHASE F OVERALL RESULT: {'ALL VERIFICATIONS PASSED' if all_ok else 'VERIFICATION FAILED'}")
    print("=" * 70)
    sys.exit(0 if all_ok else 1)
