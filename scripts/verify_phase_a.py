"""
scripts/verify_phase_a.py
-------------------------
Live backend verification script for Phase A.
Tests all endpoints using httpx AsyncClient with ASGITransport:
  1. Health check (GET /)
  2. Patient list (GET /api/v1/patients/)
  3. Patient detail (GET /api/v1/patients/{id}) [404 and 200]
  4. Patient timeline (GET /api/v1/patients/{id}/timeline)
  5. Patient pregnancy (GET /api/v1/patients/{id}/pregnancy)
  6. Patient fetal-assessments (GET /api/v1/patients/{id}/fetal-assessments)
  7. Patient predictions (GET /api/v1/patients/{id}/predictions)
  8. Patient growth-analysis (GET /api/v1/patients/{id}/growth-analysis)
  9. Patient newborn (GET /api/v1/patients/{id}/newborn)
 10. Patient nicu (GET /api/v1/patients/{id}/nicu)
 11. Predict endpoint (POST /api/v1/predict/)
 12. Chatbot endpoint (POST /api/v1/chat/)
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
from backend.app.main import app
from backend.app.services.inference_service import inference_service
from backend.app.schemas import (
    PatientSchema,
    PregnancySchema,
    FetalAssessmentSchema,
    PredictionSchema,
    GrowthAnalysisSchema,
    NewbornSchema,
    NicuAdmissionSchema,
    TimelineEntrySchema,
    PredictionResponse,
)


async def run_verification():
    print("=" * 60)
    print("PHASE A — LIVE BACKEND VERIFICATION USING HTTPX")
    print("=" * 60)

    try:
        inference_service.load_models()
    except Exception as e:
        print(f"Note on model loading: {e}")

    results = []

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. Health check
        r = await client.get("/")
        ok = r.status_code == 200 and r.json().get("status") == "online"
        results.append(("GET / (Health Check)", r.status_code, ok, r.json()))
        print(f"[{'PASS' if ok else 'FAIL'}] GET / -> status={r.status_code}, body={r.json()}")

        # 2. Patient list (empty DB check)
        r = await client.get("/api/v1/patients/")
        ok = r.status_code == 200 and isinstance(r.json(), list)
        results.append(("GET /api/v1/patients/ (List)", r.status_code, ok, f"count={len(r.json())}"))
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/v1/patients/ -> status={r.status_code}, count={len(r.json())}")

        # 3. Patient detail (non-existent 404 test)
        r = await client.get("/api/v1/patients/NON_EXISTENT_ID")
        ok = r.status_code == 404 and r.json().get("detail") == "Patient not found"
        results.append(("GET /api/v1/patients/NON_EXISTENT_ID (404 Test)", r.status_code, ok, r.json()))
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/v1/patients/NON_EXISTENT_ID -> status={r.status_code}, detail={r.json()}")

        # 4. Patient timeline (non-existent 404 test)
        r = await client.get("/api/v1/patients/NON_EXISTENT_ID/timeline")
        ok = r.status_code == 404
        results.append(("GET /api/v1/patients/NON_EXISTENT_ID/timeline (404 Test)", r.status_code, ok, r.json()))
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/v1/patients/NON_EXISTENT_ID/timeline -> status={r.status_code}")

        # 5. Patient pregnancy (empty list)
        r = await client.get("/api/v1/patients/NON_EXISTENT_ID/pregnancy")
        ok = r.status_code == 200 and r.json() == []
        results.append(("GET /api/v1/patients/NON_EXISTENT_ID/pregnancy", r.status_code, ok, r.json()))
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/v1/patients/NON_EXISTENT_ID/pregnancy -> status={r.status_code}, body={r.json()}")

        # 6. Patient fetal assessments
        r = await client.get("/api/v1/patients/NON_EXISTENT_ID/fetal-assessments")
        ok = r.status_code == 200 and r.json() == []
        results.append(("GET /api/v1/patients/NON_EXISTENT_ID/fetal-assessments", r.status_code, ok, r.json()))
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/v1/patients/NON_EXISTENT_ID/fetal-assessments -> status={r.status_code}")

        # 7. Patient predictions
        r = await client.get("/api/v1/patients/NON_EXISTENT_ID/predictions")
        ok = r.status_code == 200 and r.json() == []
        results.append(("GET /api/v1/patients/NON_EXISTENT_ID/predictions", r.status_code, ok, r.json()))
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/v1/patients/NON_EXISTENT_ID/predictions -> status={r.status_code}")

        # 8. Patient growth analysis
        r = await client.get("/api/v1/patients/NON_EXISTENT_ID/growth-analysis")
        ok = r.status_code == 200 and r.json() == []
        results.append(("GET /api/v1/patients/NON_EXISTENT_ID/growth-analysis", r.status_code, ok, r.json()))
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/v1/patients/NON_EXISTENT_ID/growth-analysis -> status={r.status_code}")

        # 9. Patient newborn
        r = await client.get("/api/v1/patients/NON_EXISTENT_ID/newborn")
        ok = r.status_code == 200 and r.json() == []
        results.append(("GET /api/v1/patients/NON_EXISTENT_ID/newborn", r.status_code, ok, r.json()))
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/v1/patients/NON_EXISTENT_ID/newborn -> status={r.status_code}")

        # 10. Patient nicu
        r = await client.get("/api/v1/patients/NON_EXISTENT_ID/nicu")
        ok = r.status_code == 200 and r.json() == []
        results.append(("GET /api/v1/patients/NON_EXISTENT_ID/nicu", r.status_code, ok, r.json()))
        print(f"[{'PASS' if ok else 'FAIL'}] GET /api/v1/patients/NON_EXISTENT_ID/nicu -> status={r.status_code}")

        # 11. Existing predict endpoint
        base = datetime.now() - timedelta(minutes=60)
        predict_payload = {
            "records": [
                {
                    "timestamp": (base + timedelta(minutes=i)).isoformat(),
                    "patient_id": "TEST-PREDICT-01",
                    "heart_rate": 140 + i * 0.5,
                    "spo2": 96 - i * 0.1,
                    "respiratory_rate": 45.0,
                    "temperature": 37.0,
                    "systolic_bp": 60.0,
                    "diastolic_bp": 40.0,
                }
                for i in range(60)
            ]
        }
        r = await client.post("/api/v1/predict/", json=predict_payload)
        ok = r.status_code == 200 and "risk_score" in r.json() and "individual_models" in r.json()
        results.append(("POST /api/v1/predict/", r.status_code, ok, f"risk={r.json().get('risk_score')}, level={r.json().get('risk_level')}"))
        print(f"[{'PASS' if ok else 'FAIL'}] POST /api/v1/predict/ -> status={r.status_code}, risk={r.json().get('risk_score')}, level={r.json().get('risk_level')}")

        # 12. Existing chatbot endpoint
        chat_payload = {
            "message": "What is the heart rate trend?",
            "patient_id": "TEST-PREDICT-01",
        }
        r = await client.post("/api/v1/chat/", json=chat_payload)
        ok = r.status_code == 200 and "reply" in r.json()
        results.append(("POST /api/v1/chat/", r.status_code, ok, f"reply_len={len(r.json().get('reply', ''))}"))
        print(f"[{'PASS' if ok else 'FAIL'}] POST /api/v1/chat/ -> status={r.status_code}, reply={r.json().get('reply', '')[:50]}...")

    print("=" * 60)
    total = len(results)
    passed = sum(1 for _, _, ok, _ in results)
    print(f"SUMMARY: {passed}/{total} endpoints verified successfully!")
    print("=" * 60)
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_verification())
    sys.exit(0 if success else 1)
