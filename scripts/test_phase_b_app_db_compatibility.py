"""
scripts/test_phase_b_app_db_compatibility.py
---------------------------------------------
Tests FastAPI application compatibility directly against MySQL (real database):
  1. GET /api/v1/patients/ -> queries real patients from MySQL
  2. GET /api/v1/patients/{id} -> queries patient TEST-PREDICT-01
  3. GET /api/v1/patients/{id}/timeline -> queries timeline for TEST-PREDICT-01
  4. GET /api/v1/patients/{id}/pregnancy -> queries pregnancies from MySQL
  5. GET /api/v1/patients/{id}/fetal-assessments -> queries assessments from MySQL
  6. GET /api/v1/patients/{id}/predictions -> queries predictions from MySQL
  7. GET /api/v1/patients/{id}/growth-analysis -> queries growth analysis from MySQL
  8. GET /api/v1/patients/{id}/newborn -> queries newborns from MySQL
  9. GET /api/v1/patients/{id}/nicu -> queries nicu admissions from MySQL
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
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


async def test_compatibility():
    print("=" * 65)
    print("PHASE B — FASTAPI TO MYSQL LIVE QUERY COMPATIBILITY TEST")
    print("=" * 65)

    test_patient_id = "TEST-PREDICT-01"
    passed = 0
    total = 0

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. GET /api/v1/patients/
        total += 1
        r = await client.get("/api/v1/patients/")
        assert r.status_code == 200
        patients = r.json()
        assert len(patients) >= 1
        PatientSchema.model_validate(patients[0])
        print(f"[PASS] GET /api/v1/patients/ -> {len(patients)} patient(s) found, validated with PatientSchema")
        passed += 1

        # 2. GET /api/v1/patients/{id}
        total += 1
        r = await client.get(f"/api/v1/patients/{test_patient_id}")
        assert r.status_code == 200
        patient = r.json()
        validated = PatientSchema.model_validate(patient)
        assert validated.id == test_patient_id
        print(f"[PASS] GET /api/v1/patients/{test_patient_id} -> ID={validated.id}, Name={validated.name}")
        passed += 1

        # 3. GET /api/v1/patients/{id}/timeline
        total += 1
        r = await client.get(f"/api/v1/patients/{test_patient_id}/timeline")
        assert r.status_code == 200
        timeline = r.json()
        for item in timeline:
            TimelineEntrySchema.model_validate(item)
        print(f"[PASS] GET /api/v1/patients/{test_patient_id}/timeline -> {len(timeline)} timeline event(s)")
        passed += 1

        # 4. GET /api/v1/patients/{id}/pregnancy
        total += 1
        r = await client.get(f"/api/v1/patients/{test_patient_id}/pregnancy")
        assert r.status_code == 200
        pregnancies = r.json()
        for p in pregnancies:
            PregnancySchema.model_validate(p)
        print(f"[PASS] GET /api/v1/patients/{test_patient_id}/pregnancy -> {len(pregnancies)} pregnancy record(s)")
        passed += 1

        # 5. GET /api/v1/patients/{id}/fetal-assessments
        total += 1
        r = await client.get(f"/api/v1/patients/{test_patient_id}/fetal-assessments")
        assert r.status_code == 200
        assessments = r.json()
        for a in assessments:
            FetalAssessmentSchema.model_validate(a)
        print(f"[PASS] GET /api/v1/patients/{test_patient_id}/fetal-assessments -> {len(assessments)} assessment(s)")
        passed += 1

        # 6. GET /api/v1/patients/{id}/predictions
        total += 1
        r = await client.get(f"/api/v1/patients/{test_patient_id}/predictions")
        assert r.status_code == 200
        predictions = r.json()
        assert len(predictions) >= 1
        pred = PredictionSchema.model_validate(predictions[0])
        print(f"[PASS] GET /api/v1/patients/{test_patient_id}/predictions -> {len(predictions)} prediction(s), risk={pred.risk_score}")
        passed += 1

        # 7. GET /api/v1/patients/{id}/growth-analysis
        total += 1
        r = await client.get(f"/api/v1/patients/{test_patient_id}/growth-analysis")
        assert r.status_code == 200
        growth = r.json()
        for g in growth:
            GrowthAnalysisSchema.model_validate(g)
        print(f"[PASS] GET /api/v1/patients/{test_patient_id}/growth-analysis -> {len(growth)} growth record(s)")
        passed += 1

        # 8. GET /api/v1/patients/{id}/newborn
        total += 1
        r = await client.get(f"/api/v1/patients/{test_patient_id}/newborn")
        assert r.status_code == 200
        newborns = r.json()
        for nb in newborns:
            NewbornSchema.model_validate(nb)
        print(f"[PASS] GET /api/v1/patients/{test_patient_id}/newborn -> {len(newborns)} newborn(s)")
        passed += 1

        # 9. GET /api/v1/patients/{id}/nicu
        total += 1
        r = await client.get(f"/api/v1/patients/{test_patient_id}/nicu")
        assert r.status_code == 200
        nicu = r.json()
        for ad in nicu:
            NicuAdmissionSchema.model_validate(ad)
        print(f"[PASS] GET /api/v1/patients/{test_patient_id}/nicu -> {len(nicu)} NICU admission(s)")
        passed += 1

    print("=" * 65)
    print(f"COMPATIBILITY SUMMARY: {passed}/{total} FastAPI-MySQL operations passed!")
    print("=" * 65)
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(test_compatibility())
    sys.exit(0 if success else 1)

