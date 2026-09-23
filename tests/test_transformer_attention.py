"""
tests/test_transformer_attention.py
------------------------------------
Phase P — Controlled Transformer Attention Explainability Verification.
Includes unit, integration, API, edge-case, performance, and regression tests.
"""

import time
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from ml.explainability.transformer_explainer import (
    TransformerAttentionExplainer,
    VITAL_COLUMNS,
)
from backend.app.main import app
from backend.app.schemas.predict_schema import VitalSignRecord
from backend.app.services.inference_service import inference_service
from backend.app.db.models import Patient, VitalSign, Pregnancy, FetalAssessment, Prediction
from tests.conftest import TestSessionLocal, client


def create_dummy_30_vital_df(patient_id: str = "TEST-TF-01") -> pd.DataFrame:
    """Helper to generate a valid 30-row sequence DataFrame."""
    now = datetime.utcnow()
    rows = []
    for i in range(30):
        t = now - timedelta(minutes=30 - i)
        rows.append({
            "timestamp": t.isoformat(),
            "patient_id": patient_id,
            "heart_rate": 140.0 + np.random.uniform(-5, 5),
            "spo2": 96.0 + np.random.uniform(-1, 1),
            "respiratory_rate": 45.0 + np.random.uniform(-2, 2),
            "temperature": 36.8 + np.random.uniform(-0.1, 0.1),
            "systolic_bp": 70.0 + np.random.uniform(-3, 3),
            "diastolic_bp": 40.0 + np.random.uniform(-2, 2),
        })
    return pd.DataFrame(rows)


def create_dummy_60_records(patient_id: str = "TEST-TF-01") -> list:
    """Helper to generate a list of 60 VitalSignRecord schemas."""
    now = datetime.utcnow()
    records = []
    for i in range(60):
        t = now - timedelta(minutes=60 - i)
        records.append(
            VitalSignRecord(
                timestamp=t.isoformat(),
                patient_id=patient_id,
                heart_rate=140.0 + np.random.uniform(-5, 5),
                spo2=96.0 + np.random.uniform(-1, 1),
                respiratory_rate=45.0 + np.random.uniform(-2, 2),
                temperature=36.8,
                systolic_bp=70.0,
                diastolic_bp=40.0,
            )
        )
    return records


# 1. Transformer Model Availability
def test_transformer_explainer_initialization():
    explainer = TransformerAttentionExplainer(models_dir="models")
    assert explainer.transformer_model is not None
    assert explainer.scaler is not None


# 2. Input Shape Validation
def test_transformer_input_shape_validation():
    explainer = TransformerAttentionExplainer(models_dir="models")
    df_short = create_dummy_30_vital_df().iloc[:25]
    with pytest.raises(ValueError, match="must be exactly 30 rows"):
        explainer.explain_sequence(df_short)


# 3. Feature Count & Order
def test_transformer_feature_count_and_columns():
    explainer = TransformerAttentionExplainer(models_dir="models")
    assert len(explainer.vital_columns) == 6
    assert explainer.vital_columns == VITAL_COLUMNS


# 4. Sequence Length
def test_transformer_sequence_length():
    explainer = TransformerAttentionExplainer(models_dir="models")
    assert explainer.sequence_length == 30


# 5. Attention Extraction
def test_transformer_attention_extraction():
    explainer = TransformerAttentionExplainer(models_dir="models")
    res = explainer.explain_sequence(create_dummy_30_vital_df())
    assert res["model_name"] == "Transformer"
    assert "top_attended_timesteps" in res


# 6. Attention Tensor Dimensions
def test_transformer_attention_dimensions():
    explainer = TransformerAttentionExplainer(models_dir="models")
    res = explainer.explain_sequence(create_dummy_30_vital_df())
    assert res["raw_attention_dimensions"] == "[2, 4, 30, 30]"


# 7. Number of Heads
def test_transformer_number_of_heads():
    explainer = TransformerAttentionExplainer(models_dir="models")
    assert explainer.num_heads == 4


# 8. Number of Layers
def test_transformer_number_of_layers():
    explainer = TransformerAttentionExplainer(models_dir="models")
    assert explainer.num_layers == 2


# 9. Finite Attention Values
def test_transformer_finite_attention_values():
    explainer = TransformerAttentionExplainer(models_dir="models")
    res = explainer.explain_sequence(create_dummy_30_vital_df())
    matrix = np.array(res["overall_mean_attention_matrix"])
    assert np.all(np.isfinite(matrix))


# 10. Attention Aggregation
def test_transformer_attention_aggregation():
    explainer = TransformerAttentionExplainer(models_dir="models")
    res = explainer.explain_sequence(create_dummy_30_vital_df())
    l0 = np.array(res["layer_0_mean_attention"])
    l1 = np.array(res["layer_1_mean_attention"])
    overall = np.array(res["overall_mean_attention_matrix"])
    assert l0.shape == (30, 30)
    assert l1.shape == (30, 30)
    assert np.allclose(overall, 0.5 * (l0 + l1), atol=1e-4)


# 11. Temporal Attention Output
def test_transformer_temporal_attention_output():
    explainer = TransformerAttentionExplainer(models_dir="models")
    res = explainer.explain_sequence(create_dummy_30_vital_df())
    seq = res["temporal_attention_sequence"]
    assert len(seq) == 30
    total_weight = sum(item["attention_weight"] for item in seq)
    assert abs(total_weight - 1.0) < 1e-3


# 12. Deterministic Attention
def test_transformer_deterministic_attention():
    explainer = TransformerAttentionExplainer(models_dir="models")
    df = create_dummy_30_vital_df()
    res1 = explainer.explain_sequence(df)
    res2 = explainer.explain_sequence(df)
    assert res1["overall_mean_attention_matrix"] == res2["overall_mean_attention_matrix"]


# 13. Prediction Before Attention
def test_prediction_before_attention():
    explainer = TransformerAttentionExplainer(models_dir="models")
    df = create_dummy_30_vital_df()
    scaled = explainer.scaler.transform(df[VITAL_COLUMNS])
    seq_in = np.expand_dims(scaled, axis=0)
    prob_before = float(explainer.transformer_model.predict(seq_in, verbose=0)[0, 0])
    assert 0.0 <= prob_before <= 1.0


# 14. Prediction After Attention
def test_prediction_after_attention():
    explainer = TransformerAttentionExplainer(models_dir="models")
    df = create_dummy_30_vital_df()
    res = explainer.explain_sequence(df)
    prob_after = res["transformer_risk_score"]
    assert 0.0 <= prob_after <= 1.0


# 15. Prediction Consistency (Shift = 0)
def test_prediction_consistency():
    explainer = TransformerAttentionExplainer(models_dir="models")
    df = create_dummy_30_vital_df()
    scaled = explainer.scaler.transform(df[VITAL_COLUMNS])
    seq_in = np.expand_dims(scaled, axis=0)
    prob_direct = float(explainer.transformer_model.predict(seq_in, verbose=0)[0, 0])
    res = explainer.explain_sequence(df)
    prob_explained = res["transformer_risk_score"]
    assert abs(prob_direct - prob_explained) < 1e-4



# 16. Multi-Patient Isolation
def test_multi_patient_isolation():
    explainer = TransformerAttentionExplainer(models_dir="models")
    df1 = create_dummy_30_vital_df(patient_id="P-01")
    df2 = create_dummy_30_vital_df(patient_id="P-02")
    res1 = explainer.explain_sequence(df1)
    res2 = explainer.explain_sequence(df2)
    assert res1["patient_id"] == "P-01"
    assert res2["patient_id"] == "P-02"


# 17. API Endpoint POST /api/v1/predict/attention-explain
def test_api_predict_attention_explain(client):
    records = [r.model_dump() for r in create_dummy_60_records()]
    response = client.post("/api/v1/predict/attention-explain", json={"records": records})
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "Transformer"
    assert "temporal_attention_sequence" in data


# 18. Unknown Patient Handling
def test_api_patient_attention_explain_not_found(client):
    response = client.get("/api/v1/patients/NON-EXISTENT-999/attention-explain")
    assert response.status_code == 404


# 19. Insufficient Data Handling
def test_api_patient_attention_explain_insufficient_vitals(client):
    pid = "TF-PAT-SHORT"
    db = TestSessionLocal()
    try:
        if not db.query(Patient).filter(Patient.id == pid).first():
            db.add(Patient(id=pid, name="TF Short Patient"))
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

    response = client.get(f"/api/v1/patients/{pid}/attention-explain")
    assert response.status_code == 400


# 20. SHAP Regression
def test_regression_shap(client):
    records = [r.model_dump() for r in create_dummy_60_records()]
    response = client.post("/api/v1/predict/explain", json={"records": records})
    assert response.status_code == 200
    assert response.json()["model_name"] == "XGBoost"


# 21. Autoencoder Explainability Regression
def test_regression_autoencoder(client):
    records = [r.model_dump() for r in create_dummy_60_records()]
    response = client.post("/api/v1/predict/anomaly-explain", json={"records": records})
    assert response.status_code == 200
    assert response.json()["model_name"] == "Autoencoder"


# 22. Prenatal Regression
def test_regression_prenatal(client):
    pid = "TF-PRENATAL-REG"
    db = TestSessionLocal()
    try:
        if not db.query(Patient).filter(Patient.id == pid).first():
            db.add(Patient(id=pid, name="TF Prenatal Reg Patient"))
            preg = Pregnancy(id=9966, patient_id=pid, pregnancy_status="active")
            db.add(preg)
            db.add(Prediction(patient_id=pid, pregnancy_id=9966, target="EFW_PERCENTILE_T2", predicted_value=50.0, risk_level="LOW"))
            db.add(FetalAssessment(pregnancy_id=9966, trimester=1, efw_percentile=50.0, assessment_date=datetime(2026, 3, 1)))
            db.add(FetalAssessment(pregnancy_id=9966, trimester=2, efw_percentile=48.0, assessment_date=datetime(2026, 5, 1)))
            db.commit()
    finally:
        db.close()

    response = client.get(f"/api/v1/patients/{pid}/prenatal-analysis")
    assert response.status_code == 200
    assert response.json()["evaluation_status"] == "NORMAL_GROWTH_TRAJECTORY"


# 23. NICU Stream Regression
def test_regression_nicu_stream():
    if not inference_service.is_ready:
        inference_service.load_models()
    records = create_dummy_60_records()
    res = inference_service.predict(records)
    assert 0.0 <= res["risk_score"] <= 1.0
    assert res["risk_level"] in ["LOW", "WATCH", "HIGH"]
