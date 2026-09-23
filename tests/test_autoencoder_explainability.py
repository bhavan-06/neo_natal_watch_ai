"""
tests/test_autoencoder_explainability.py
-----------------------------------------
Phase O — Controlled Autoencoder Anomaly Explainability & Visualization Verification.
Includes unit, integration, API, edge-case, performance, and regression tests.
"""

import time
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from ml.explainability.autoencoder_explainer import (
    AutoencoderAnomalyExplainer,
    VITAL_COLUMNS,
)
from backend.app.main import app
from backend.app.schemas.predict_schema import VitalSignRecord
from backend.app.services.inference_service import inference_service
from backend.app.db.models import Patient, VitalSign, Pregnancy, FetalAssessment, Prediction
from tests.conftest import TestSessionLocal, client


def create_dummy_30_vital_df(patient_id: str = "TEST-AE-01", is_anomalous: bool = False) -> pd.DataFrame:
    """Helper to generate a valid 30-row sequence DataFrame."""
    now = datetime.utcnow()
    rows = []
    for i in range(30):
        t = now - timedelta(minutes=30 - i)
        hr = 140.0 + (30.0 if (is_anomalous and i >= 20) else np.random.uniform(-5, 5))
        spo2 = 96.0 - (15.0 if (is_anomalous and i >= 20) else np.random.uniform(0, 2))
        rr = 45.0 + np.random.uniform(-3, 3)
        temp = 36.8 + np.random.uniform(-0.2, 0.2)
        sys_bp = 70.0 + np.random.uniform(-4, 4)
        dia_bp = 40.0 + np.random.uniform(-3, 3)

        rows.append({
            "timestamp": t.isoformat(),
            "patient_id": patient_id,
            "heart_rate": hr,
            "spo2": spo2,
            "respiratory_rate": rr,
            "temperature": temp,
            "systolic_bp": sys_bp,
            "diastolic_bp": dia_bp,
        })
    return pd.DataFrame(rows)


def create_dummy_60_records(patient_id: str = "TEST-AE-01") -> list:
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


# 1. Initialization Test
def test_autoencoder_explainer_initialization():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    assert explainer.autoencoder_model is not None
    assert explainer.scaler is not None
    assert explainer.ae_threshold > 0.0


# 2. Invalid Models Dir
def test_autoencoder_explainer_invalid_models_dir():
    with pytest.raises(FileNotFoundError):
        AutoencoderAnomalyExplainer(models_dir="non_existent_dir")


# 3. Sequence Shape Validation
def test_autoencoder_explainer_sequence_shape_validation():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    df_short = create_dummy_30_vital_df().iloc[:25]
    with pytest.raises(ValueError, match="must be exactly 30 rows"):
        explainer.explain_sequence(df_short)


# 4. Missing Vital Columns
def test_autoencoder_explainer_missing_vital_columns():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    df_bad = create_dummy_30_vital_df().drop(columns=["heart_rate"])
    with pytest.raises(ValueError, match="missing required vital columns"):
        explainer.explain_sequence(df_bad)


# 5. Response Keys Test
def test_explain_sequence_returns_expected_keys():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    df_seq = create_dummy_30_vital_df()
    result = explainer.explain_sequence(df_seq)

    expected_keys = [
        "model_name", "patient_id", "timestamp", "model_output_explained",
        "overall_reconstruction_mse", "ae_threshold", "ae_anomaly_score",
        "is_anomalous", "total_vitals_evaluated", "window_size_steps",
        "top_contributing_vitals", "all_vital_contributions",
        "time_series_error_trace", "safety_disclaimer"
    ]
    for key in expected_keys:
        assert key in result, f"Key {key} missing from response"


# 6. Overall MSE Non-Negative
def test_overall_mse_positive():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    result = explainer.explain_sequence(create_dummy_30_vital_df())
    assert result["overall_reconstruction_mse"] >= 0.0


# 7. Score Formula Invariance
def test_score_formula_invariance():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    result = explainer.explain_sequence(create_dummy_30_vital_df())
    mse = result["overall_reconstruction_mse"]
    thresh = result["ae_threshold"]
    expected_score = float(np.clip(0.5 * (mse / thresh), 0.0, 1.0))
    assert abs(result["ae_anomaly_score"] - round(expected_score, 4)) < 1e-4


# 8. Per-Feature MSE Non-Negative
def test_per_feature_mse_non_negative():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    result = explainer.explain_sequence(create_dummy_30_vital_df())
    for item in result["all_vital_contributions"]:
        assert item["reconstruction_mse"] >= 0.0


# 9. Contribution Percentages Sum to ~100%
def test_contribution_percentages_sum_to_100():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    result = explainer.explain_sequence(create_dummy_30_vital_df())
    total_pct = sum(item["contribution_percent"] for item in result["all_vital_contributions"])
    assert abs(total_pct - 100.0) < 0.5


# 10. Top Contributing Vitals Count
def test_top_contributing_vitals_count():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    result = explainer.explain_sequence(create_dummy_30_vital_df(), top_n=3)
    assert len(result["top_contributing_vitals"]) == 3


# 11. Top Contributing Vitals Ordering
def test_top_contributing_vitals_ordering():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    result = explainer.explain_sequence(create_dummy_30_vital_df())
    top_items = result["top_contributing_vitals"]
    for i in range(len(top_items) - 1):
        assert top_items[i]["reconstruction_mse"] >= top_items[i + 1]["reconstruction_mse"]


# 12. Time Series Error Trace Length
def test_time_series_error_trace_length():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    result = explainer.explain_sequence(create_dummy_30_vital_df())
    assert len(result["time_series_error_trace"]) == 30


# 13. Time Series Error Trace Step Indices
def test_time_series_error_trace_step_indices():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    result = explainer.explain_sequence(create_dummy_30_vital_df())
    indices = [t["step_index"] for t in result["time_series_error_trace"]]
    assert indices == list(range(30))


# 14. Time Series Error Trace Exceeds Threshold Flag
def test_time_series_error_trace_exceeds_threshold():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    result = explainer.explain_sequence(create_dummy_30_vital_df())
    thresh = result["ae_threshold"]
    for t in result["time_series_error_trace"]:
        expected_flag = t["timestep_reconstruction_mse"] > thresh
        assert t["exceeds_threshold"] == expected_flag


# 15. Latest Residuals Non-Negative
def test_latest_residuals_non_negative():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    result = explainer.explain_sequence(create_dummy_30_vital_df())
    for item in result["all_vital_contributions"]:
        assert item["latest_absolute_residual"] >= 0.0


# 16. Inference Service Explain Autoencoder
def test_inference_service_explain_autoencoder():
    if not inference_service.is_ready:
        inference_service.load_models()
    records = create_dummy_60_records()
    explanation = inference_service.explain_autoencoder(records)
    assert explanation["model_name"] == "Autoencoder"
    assert len(explanation["top_contributing_vitals"]) == 5


# 17. Inference Service Short Records Validation
def test_inference_service_explain_autoencoder_short_records():
    if not inference_service.is_ready:
        inference_service.load_models()
    records = create_dummy_60_records()[:20]
    with pytest.raises(ValueError, match="required 30"):
        inference_service.explain_autoencoder(records)


# 18. POST /api/v1/predict/anomaly-explain Success
def test_predict_anomaly_explain_endpoint_success(client):
    records = [r.model_dump() for r in create_dummy_60_records()]
    response = client.post("/api/v1/predict/anomaly-explain", json={"records": records})
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "Autoencoder"
    assert "top_contributing_vitals" in data


# 19. POST /api/v1/predict/anomaly-explain Insufficient Vitals
def test_predict_anomaly_explain_endpoint_insufficient_vitals(client):
    records = [r.model_dump() for r in create_dummy_60_records()[:15]]
    response = client.post("/api/v1/predict/anomaly-explain", json={"records": records})
    assert response.status_code in [400, 422]


# 20. GET /api/v1/patients/{id}/anomaly-explain Success
def test_patient_anomaly_explain_endpoint_success(client):
    pid = "AE-TEST-PAT-01"
    db = TestSessionLocal()
    try:
        if not db.query(Patient).filter(Patient.id == pid).first():
            db.add(Patient(id=pid, name="AE Test Patient 1"))
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

    response = client.get(f"/api/v1/patients/{pid}/anomaly-explain")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "Autoencoder"
    assert data["patient_id"] == pid


# 21. GET /api/v1/patients/{id}/anomaly-explain Not Found
def test_patient_anomaly_explain_endpoint_not_found(client):
    response = client.get("/api/v1/patients/NON-EXISTENT-999/anomaly-explain")
    assert response.status_code == 404


# 22. GET /api/v1/patients/{id}/anomaly-explain Insufficient Vitals
def test_patient_anomaly_explain_endpoint_insufficient_vitals(client):
    pid = "AE-TEST-PAT-SHORT"
    db = TestSessionLocal()
    try:
        if not db.query(Patient).filter(Patient.id == pid).first():
            db.add(Patient(id=pid, name="AE Short Patient"))
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

    response = client.get(f"/api/v1/patients/{pid}/anomaly-explain")
    assert response.status_code == 400


# 23. Multi-Patient Isolation
def test_multi_patient_isolation():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    df1 = create_dummy_30_vital_df(patient_id="P-01")
    df2 = create_dummy_30_vital_df(patient_id="P-02")
    res1 = explainer.explain_sequence(df1)
    res2 = explainer.explain_sequence(df2)
    assert res1["patient_id"] == "P-01"
    assert res2["patient_id"] == "P-02"


# 24. Safety Disclaimer Present
def test_safety_disclaimer_present():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    res = explainer.explain_sequence(create_dummy_30_vital_df())
    assert "safety_disclaimer" in res
    assert "SYNTHETIC / ACADEMIC DEMO DATA" in res["safety_disclaimer"]


# 25. NaN & Inf Resilience
def test_nan_and_inf_resilience():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    df = create_dummy_30_vital_df()
    df.loc[5, "heart_rate"] = np.nan
    df.loc[10, "spo2"] = np.nan
    res = explainer.explain_sequence(df)
    assert np.isfinite(res["overall_reconstruction_mse"])
    assert np.isfinite(res["ae_anomaly_score"])


# 26. Performance Sub-250ms
def test_performance_sub_250ms():
    explainer = AutoencoderAnomalyExplainer(models_dir="models")
    df = create_dummy_30_vital_df()
    # Warmup
    explainer.explain_sequence(df)
    t0 = time.time()
    res = explainer.explain_sequence(df)
    elapsed_ms = (time.time() - t0) * 1000.0
    assert elapsed_ms < 250.0, f"Explanation took too long: {elapsed_ms:.2f}ms"


# 27. Regression: Existing Predict Endpoint
def test_regression_existing_predict(client):
    records = [r.model_dump() for r in create_dummy_60_records()]
    response = client.post("/api/v1/predict/", json={"records": records})
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "risk_level" in data


# 28. Regression: Existing SHAP Endpoint
def test_regression_existing_shap(client):
    records = [r.model_dump() for r in create_dummy_60_records()]
    response = client.post("/api/v1/predict/explain", json={"records": records})
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "XGBoost"


# 29. Regression: Existing Prenatal Endpoint
def test_regression_existing_prenatal(client):
    pid = "AE-PRENATAL-REG"
    db = TestSessionLocal()
    try:
        if not db.query(Patient).filter(Patient.id == pid).first():
            db.add(Patient(id=pid, name="AE Prenatal Reg Patient"))
            preg = Pregnancy(id=9977, patient_id=pid, pregnancy_status="active")
            db.add(preg)
            db.add(Prediction(patient_id=pid, pregnancy_id=9977, target="EFW_PERCENTILE_T2", predicted_value=50.0, risk_level="LOW"))
            db.add(FetalAssessment(pregnancy_id=9977, trimester=1, efw_percentile=50.0, assessment_date=datetime(2026, 3, 1)))
            db.add(FetalAssessment(pregnancy_id=9977, trimester=2, efw_percentile=48.0, assessment_date=datetime(2026, 5, 1)))
            db.commit()
    finally:
        db.close()

    response = client.get(f"/api/v1/patients/{pid}/prenatal-analysis")
    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_status"] == "NORMAL_GROWTH_TRAJECTORY"


# 30. Regression: Existing Stream / Prediction Risk Calculation
def test_regression_existing_stream():
    if not inference_service.is_ready:
        inference_service.load_models()
    records = create_dummy_60_records()
    res = inference_service.predict(records)
    assert 0.0 <= res["risk_score"] <= 1.0
    assert res["risk_level"] in ["LOW", "WATCH", "HIGH"]

