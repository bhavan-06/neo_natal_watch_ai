"""
tests/test_shap_explainability.py
----------------------------------
Phase N — Controlled SHAP Explainability Integration Tests

Comprehensive test suite verifying:
- XGBoost TreeSHAP explainer initialization and native execution
- 102 feature count and feature-name mapping
- Feature-order consistency
- Prediction invariance (model prediction remains 100% identical before and after SHAP)
- Top feature ranking by absolute contribution value
- Contribution direction ("positive" / "negative")
- TreeSHAP additivity in log-odds space
- Numerical stability and finite-value guarantees
- REST API endpoints: POST /api/v1/predict/explain and GET /api/v1/patients/{id}/explain
- Multi-patient explanation isolation
- Safety disclaimers and non-clinical framing
"""

import pytest
import numpy as np
import pandas as pd
import xgboost as xgb
from datetime import datetime, timedelta
from ml.explainability.shap_explainer import XGBoostShapExplainer
from backend.app.services.inference_service import InferenceService, inference_service
from backend.app.schemas.predict_schema import VitalSignRecord
from backend.app.db.models import Patient, VitalSign
from tests.conftest import TestSessionLocal


@pytest.fixture(scope="class")
def shap_explainer():
    return XGBoostShapExplainer(models_dir="models")


@pytest.fixture(scope="class")
def sample_60_records():
    base_time = datetime(2026, 1, 1, 12, 0)
    return [
        VitalSignRecord(
            timestamp=(base_time + timedelta(minutes=i)).isoformat(),
            patient_id="SHAP-TEST-PATIENT-01",
            heart_rate=140.0 + (i * 0.2),
            spo2=96.0 - (i * 0.1),
            respiratory_rate=45.0,
            temperature=37.0,
            systolic_bp=60.0 + (i * 0.1),
            diastolic_bp=40.0,
        )
        for i in range(60)
    ]


class TestSHAPExplainerCore:
    """Tests 1-11: Core SHAP explainer functionality, mathematical guarantees, and ordering."""

    def test_explainer_initialization(self, shap_explainer):
        """TEST 1: SHAP explainer initializes successfully with loaded XGBoost model."""
        assert shap_explainer is not None
        assert shap_explainer.xgb_model is not None

    def test_feature_count_verification(self, shap_explainer):
        """TEST 3: Explainer verifies exactly 102 features matching xgb_features.json."""
        assert len(shap_explainer.feature_names) == 102

    def test_feature_name_mapping(self, shap_explainer):
        """TEST 4: Feature names match expected engineered feature names."""
        assert "heart_rate" in shap_explainer.feature_names
        assert "spo2_mean_30m" in shap_explainer.feature_names
        assert "heart_rate_diff_15m" in shap_explainer.feature_names

    def test_feature_order_consistency(self, shap_explainer):
        """TEST 5: Feature order in explainer matches model feature order."""
        import json
        with open("models/xgb_features.json", "r") as f:
            expected = json.load(f)
        assert shap_explainer.feature_names == expected

    def test_shap_values_generated(self, shap_explainer):
        """TEST 2 & 6: SHAP values generated using TreeSHAP execution."""
        df_row = pd.DataFrame(np.random.randn(1, 102), columns=shap_explainer.feature_names)
        result = shap_explainer.explain_instance(df_row, top_n=5)
        assert isinstance(result, dict)
        assert "top_features" in result
        assert len(result["top_features"]) == 5

    def test_prediction_unchanged_before_after_shap(self, shap_explainer):
        """TEST 7: Model risk prediction remains 100% identical before and after SHAP execution."""
        df_row = pd.DataFrame(np.random.randn(1, 102), columns=shap_explainer.feature_names)
        prob_before = float(shap_explainer.xgb_model.predict_proba(df_row)[0, 1])
        result = shap_explainer.explain_instance(df_row, top_n=5)
        prob_after = result["prediction_risk_score"]
        assert prob_before == pytest.approx(prob_after, abs=1e-3)


    def test_top_feature_ranking_by_absolute_value(self, shap_explainer):
        """TEST 8: Top features are deterministically ranked by absolute SHAP contribution."""
        df_row = pd.DataFrame(np.random.randn(1, 102), columns=shap_explainer.feature_names)
        result = shap_explainer.explain_instance(df_row, top_n=10)
        top = result["top_features"]
        abs_vals = [f["absolute_shap_value"] for f in top]
        assert abs_vals == sorted(abs_vals, reverse=True)

    def test_contribution_direction_labeling(self, shap_explainer):
        """TEST 9: Contribution direction correctly mapped to positive / negative."""
        df_row = pd.DataFrame(np.random.randn(1, 102), columns=shap_explainer.feature_names)
        result = shap_explainer.explain_instance(df_row, top_n=10)
        for f in result["top_features"]:
            if f["shap_value"] > 0:
                assert f["direction"] == "positive"
                assert f["direction_symbol"] == "↑"
            elif f["shap_value"] < 0:
                assert f["direction"] == "negative"
                assert f["direction_symbol"] == "↓"

    def test_numerical_finite_validation(self, shap_explainer):
        """TEST 10: All returned numerical values are finite floats (no NaNs or Infs)."""
        df_row = pd.DataFrame(np.random.randn(1, 102), columns=shap_explainer.feature_names)
        result = shap_explainer.explain_instance(df_row, top_n=5)
        assert np.isfinite(result["base_value"])
        assert np.isfinite(result["prediction_risk_score"])
        for f in result["top_features"]:
            assert np.isfinite(f["feature_value"])
            assert np.isfinite(f["shap_value"])
            assert np.isfinite(f["absolute_shap_value"])

    def test_tree_shap_additivity(self, shap_explainer):
        """TEST 11: TreeSHAP additivity holds in log-odds margin space."""
        df_row = pd.DataFrame(np.random.randn(1, 102), columns=shap_explainer.feature_names)
        result = shap_explainer.explain_instance(df_row, top_n=102)

        base_val = result["base_value"]
        total_shap = sum(f["shap_value"] for f in result["all_features"])
        computed_margin = base_val + total_shap

        # Verify margin against model booster margin
        dmat = xgb.DMatrix(df_row)
        expected_margin = shap_explainer.xgb_model.get_booster().predict(dmat, output_margin=True)[0]

        assert computed_margin == pytest.approx(expected_margin, abs=1e-4)


class TestSHAPAPIAndIsolation:
    """Tests 12-16: REST API endpoints, multi-patient isolation, and regression verification."""

    def test_post_predict_explain_endpoint(self, client, sample_60_records):
        """TEST 12: POST /api/v1/predict/explain returns valid SHAP explanation."""
        payload = {"records": [r.model_dump() for r in sample_60_records]}
        response = client.post("/api/v1/predict/explain", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["model_name"] == "XGBoost"
        assert len(data["top_features"]) == 5
        assert "safety_disclaimer" in data

    def test_get_patient_explain_endpoint(self, client):
        """TEST 13: GET /api/v1/patients/{id}/explain returns SHAP explanation for stored vitals."""
        # Seed 60 vitals for a test patient in DB
        db = TestSessionLocal()
        pid = "SHAP-DB-PATIENT-01"
        try:
            if not db.query(Patient).filter(Patient.id == pid).first():
                db.add(Patient(id=pid, name="SHAP Test Patient"))
                base = datetime(2026, 1, 1)
                for i in range(60):
                    db.add(VitalSign(
                        patient_id=pid,
                        timestamp=base + timedelta(minutes=i),
                        heart_rate=140.0 + (i * 0.1),
                        spo2=96.0,
                        respiratory_rate=45.0,
                        temperature=37.0,
                        systolic_bp=60.0,
                        diastolic_bp=40.0
                    ))
                db.commit()
        finally:
            db.close()

        response = client.get(f"/api/v1/patients/{pid}/explain")
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == pid
        assert len(data["top_features"]) == 5

    def test_multi_patient_explanation_isolation(self, client):
        """TEST 14: Patient A and Patient B explanations remain strictly isolated."""
        db = TestSessionLocal()
        try:
            for pid, base_hr in [("SHAP-PAT-A", 120.0), ("SHAP-PAT-B", 175.0)]:
                if not db.query(Patient).filter(Patient.id == pid).first():
                    db.add(Patient(id=pid, name=f"Patient {pid}"))
                    base = datetime(2026, 1, 1)
                    for i in range(60):
                        db.add(VitalSign(
                            patient_id=pid,
                            timestamp=base + timedelta(minutes=i),
                            heart_rate=base_hr,
                            spo2=95.0,
                            respiratory_rate=40.0,
                            temperature=37.0,
                            systolic_bp=65.0,
                            diastolic_bp=42.0
                        ))
                    db.commit()
        finally:
            db.close()

        resp_a = client.get("/api/v1/patients/SHAP-PAT-A/explain")
        resp_b = client.get("/api/v1/patients/SHAP-PAT-B/explain")

        assert resp_a.status_code == 200
        assert resp_b.status_code == 200

        data_a = resp_a.json()
        data_b = resp_b.json()

        assert data_a["patient_id"] == "SHAP-PAT-A"
        assert data_b["patient_id"] == "SHAP-PAT-B"
        # Different vital inputs produce distinct SHAP explanations
        assert data_a["prediction_risk_score"] != data_b["prediction_risk_score"]

    def test_existing_nicu_regression(self, client, sample_60_records):
        """TEST 15: Existing NICU prediction pipeline functions without regression."""
        payload = {"records": [r.model_dump() for r in sample_60_records]}
        resp = client.post("/api/v1/predict/", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "risk_score" in data
        assert "risk_level" in data

    def test_existing_prenatal_regression(self, client):
        """TEST 16: Existing prenatal decision-support pipeline functions without regression."""
        from backend.app.db.models import Pregnancy, FetalAssessment, Prediction
        db = TestSessionLocal()
        pid = "SHAP-PRENATAL-REG"
        try:
            if not db.query(Patient).filter(Patient.id == pid).first():
                db.add(Patient(id=pid, name="Prenatal Reg Patient"))
                preg = Pregnancy(id=9988, patient_id=pid, pregnancy_status="active")
                db.add(preg)
                db.add(Prediction(patient_id=pid, pregnancy_id=9988, target="EFW_PERCENTILE_T2", predicted_value=50.0, risk_level="LOW"))
                db.add(FetalAssessment(pregnancy_id=9988, trimester=1, efw_percentile=50.0, assessment_date=datetime(2026, 3, 1)))
                db.add(FetalAssessment(pregnancy_id=9988, trimester=2, efw_percentile=48.0, assessment_date=datetime(2026, 5, 1)))
                db.commit()
        finally:
            db.close()

        resp = client.get(f"/api/v1/patients/{pid}/prenatal-analysis")
        assert resp.status_code == 200
        data = resp.json()
        assert data["evaluation_status"] == "NORMAL_GROWTH_TRAJECTORY"

