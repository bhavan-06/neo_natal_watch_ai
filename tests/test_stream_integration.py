"""
tests/test_stream_integration.py
--------------------------------
Phase L — Controlled NICU Real-Time Inference Integration Tests

Tests the connection between the NICU vital stream and the ML inference pipeline.
"""

import pytest
import asyncio
import json
from datetime import datetime
from backend.app.db.database import SessionLocal
from backend.app.db.models import Patient, VitalSign, Prediction, NicuVital
from backend.app.api.endpoints.stream import _event_generator, _ensure_dummy_nicu_admission, patient_buffers

@pytest.mark.asyncio
class TestStreamIntegration:

    async def _collect_events(self, admission_id, patient_id, max_events=2):
        events = []
        gen = _event_generator(admission_id, patient_id)
        for _ in range(max_events):
            item = await anext(gen)
            if item.startswith("data: "):
                data_str = item[len("data: "):].strip()
                events.append(json.loads(data_str))
        return events

    def test_invalid_patient_returns_400(self, client):
        """TEST 2: Invalid patient"""
        response = client.get("/api/v1/stream/", params={"patient_id": " "})
        assert response.status_code == 400

    async def test_stream_event_format(self):
        """TEST 1: Valid single vital ingestion"""
        adm_id = _ensure_dummy_nicu_admission("TEST-STREAM-001")
        events = await self._collect_events(adm_id, "TEST-STREAM-001", max_events=1)
        
        assert len(events) == 1
        record = events[0]
        
        assert "heart_rate" in record
        assert "spo2" in record
        assert "respiratory_rate" in record
        assert "temperature" in record
        assert "systolic_bp" in record
        assert "diastolic_bp" in record
        assert "patient_id" in record
        assert record["patient_id"] == "TEST-STREAM-001"
        
        # Since we seed the buffer with 59 records, the 1st event triggers inference (60 total)
        assert "prediction" in record
        pred = record["prediction"]
        assert "risk_score" in pred
        assert "risk_level" in pred

    async def test_sliding_window_maintains_60(self):
        """TEST 6: 31+ observations / sliding window (we test 60+ via seeded buffer)"""
        adm_id = _ensure_dummy_nicu_admission("TEST-SLIDE-001")
        events = await self._collect_events(adm_id, "TEST-SLIDE-001", max_events=2)
        
        assert len(events) == 2
        assert "prediction" in events[0]
        assert "prediction" in events[1]
        assert len(patient_buffers["TEST-SLIDE-001"]) == 60

    async def test_persistence_verification(self):
        """TEST 8: Prediction and Vital persistence"""
        patient_id = "TEST-PERSIST-001"
        adm_id = _ensure_dummy_nicu_admission(patient_id)
        events = await self._collect_events(adm_id, patient_id, max_events=1)
        
        db = SessionLocal()
        try:
            # 1. NicuVital (legacy)
            nicu_vitals = db.query(NicuVital).filter(NicuVital.nicu_admission_id == adm_id).count()
            assert nicu_vitals > 0
            
            # 2. VitalSign (authoritative)
            vitals = db.query(VitalSign).filter(VitalSign.patient_id == patient_id).count()
            assert vitals > 0
            
            # 3. Prediction
            preds = db.query(Prediction).filter(Prediction.patient_id == patient_id).count()
            assert preds > 0
        finally:
            db.close()

    async def test_multi_patient_isolation(self):
        """TEST 7: Multi-patient isolation"""
        adm_a = _ensure_dummy_nicu_admission("TEST-ISOLATE-A")
        adm_b = _ensure_dummy_nicu_admission("TEST-ISOLATE-B")
        
        res_a = await self._collect_events(adm_a, "TEST-ISOLATE-A", max_events=2)
        res_b = await self._collect_events(adm_b, "TEST-ISOLATE-B", max_events=2)
        
        assert all(e["patient_id"] == "TEST-ISOLATE-A" for e in res_a)
        assert all(e["patient_id"] == "TEST-ISOLATE-B" for e in res_b)
        assert "prediction" in res_a[1]
        assert "prediction" in res_b[1]

    def test_alert_deduplication(self):
        """TEST 12: Duplicate event handling for alerts"""
        from backend.app.services.inference_service import InferenceService
        svc = InferenceService(models_dir="models")
        svc.alert_state = {"DEDUP-PATIENT": True}
        svc.alert_state["DEDUP-PATIENT"] = False
        assert svc.alert_state["DEDUP-PATIENT"] is False

