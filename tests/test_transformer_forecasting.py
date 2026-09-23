
"""
tests/test_transformer_forecasting.py
--------------------------------------
Phase P — Multi-Horizon Forecasting Audit Verification.

Verifies the technical limitation audit for the existing Transformer model:
The existing Transformer artifact (models/transformer.keras) is a single-output binary
classifier for deterioration risk (output shape (1, 1), sigmoid activation).
Multi-horizon future vital forecasting requires a forecasting-capable model/training target
and cannot be truthfully implemented using the current classifier artifact without retraining.
"""

import pytest
from datetime import datetime, timedelta
from backend.app.schemas.predict_schema import VitalSignRecord
from backend.app.services.inference_service import inference_service
from backend.app.db.models import Patient, VitalSign
from tests.conftest import TestSessionLocal, client


def create_dummy_60_records(patient_id: str = "FC-TEST-PAT") -> list:
    now = datetime.utcnow()
    return [
        VitalSignRecord(
            timestamp=(now - timedelta(minutes=60 - i)).isoformat(),
            patient_id=patient_id,
            heart_rate=140.0,
            spo2=96.0,
            respiratory_rate=45.0,
            temperature=36.8,
            systolic_bp=70.0,
            diastolic_bp=40.0
        )
        for i in range(60)
    ]


def test_transformer_forecasting_audit_limitation_statement():
    """Verifies exact technical limitation reporting without fabricating fake forecasts."""
    if not inference_service.is_ready:
        inference_service.load_models()

    records = create_dummy_60_records()
    res = inference_service.get_transformer_forecast(records)

    assert res["model_name"] == "Transformer"
    assert res["forecasting_supported"] is False
    assert "technical_limitation" in res
    assert "Multi-horizon forecasting requires a forecasting-capable model/training target" in res["technical_limitation"]
    assert res["current_model_task"] == "Binary Classification (Deterioration Risk Probability)"
    assert res["output_shape"] == "[1, 1]"
    assert res["output_activation"] == "sigmoid"


def test_api_predict_forecast_audit_endpoint(client):
    """Verifies POST /api/v1/predict/forecast returns technical limitation audit."""
    records = [r.model_dump() for r in create_dummy_60_records()]
    response = client.post("/api/v1/predict/forecast", json={"records": records})

    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "Transformer"
    assert data["forecasting_supported"] is False
    assert "Multi-horizon forecasting requires a forecasting-capable model/training target" in data["technical_limitation"]


def test_api_patient_forecast_audit_endpoint(client):
    """Verifies GET /api/v1/patients/{id}/forecast returns technical limitation audit for patient."""
    pid = "FC-PAT-SUCCESS"
    db = TestSessionLocal()
    try:
        if not db.query(Patient).filter(Patient.id == pid).first():
            db.add(Patient(id=pid, name="Forecast Audit Patient"))
            now = datetime.utcnow()
            for i in range(30):
                db.add(VitalSign(
                    patient_id=pid,
                    timestamp=now - timedelta(minutes=30 - i),
                    heart_rate=140.0,
                    spo2=96.0,
                    respiratory_rate=45.0,
                    temperature=36.8,
                    systolic_bp=70.0,
                    diastolic_bp=40.0
                ))
            db.commit()
    finally:
        db.close()

    response = client.get(f"/api/v1/patients/{pid}/forecast")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "Transformer"
    assert data["patient_id"] == pid
    assert data["forecasting_supported"] is False


def test_forecast_insufficient_vitals_handling(client):
    """Verifies insufficient vitals returns 400."""
    pid = "FC-PAT-SHORT"
    db = TestSessionLocal()
    try:
        if not db.query(Patient).filter(Patient.id == pid).first():
            db.add(Patient(id=pid, name="FC Short Patient"))
            now = datetime.utcnow()
            for i in range(10):
                db.add(VitalSign(
                    patient_id=pid,
                    timestamp=now - timedelta(minutes=10 - i),
                    heart_rate=140.0,
                    spo2=96.0,
                    respiratory_rate=45.0,
                    temperature=36.8,
                    systolic_bp=70.0,
                    diastolic_bp=40.0
                ))
            db.commit()
    finally:
        db.close()

    response = client.get(f"/api/v1/patients/{pid}/forecast")
    assert response.status_code == 400

