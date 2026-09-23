"""
tests/test_ml_pipeline.py
--------------------------
Phase K — ML Foundation Verification Tests

Tests the complete ML inference pipeline:
  1. Model artifact loading
  2. Feature engineering
  3. Individual model inference (XGBoost, CNN-LSTM, Transformer, Autoencoder)
  4. Fusion ensemble
  5. Risk level classification
  6. End-to-end inference service

⚠️ SYNTHETIC / ACADEMIC DEMO DATA — NOT FOR CLINICAL USE
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


# =========================================================================
# 1. MODEL ARTIFACT TESTS
# =========================================================================

class TestModelArtifacts:
    """Verify all model artifacts exist and load correctly."""

    def test_xgboost_artifact_exists(self):
        path = os.path.join(MODELS_DIR, "xgboost_model.json")
        assert os.path.isfile(path), f"XGBoost model artifact missing: {path}"
        assert os.path.getsize(path) > 0, "XGBoost model artifact is empty"

    def test_cnn_lstm_artifact_exists(self):
        path = os.path.join(MODELS_DIR, "cnn_lstm.keras")
        assert os.path.isfile(path), f"CNN-LSTM model artifact missing: {path}"
        assert os.path.getsize(path) > 0, "CNN-LSTM model artifact is empty"

    def test_transformer_artifact_exists(self):
        path = os.path.join(MODELS_DIR, "transformer.keras")
        assert os.path.isfile(path), f"Transformer model artifact missing: {path}"
        assert os.path.getsize(path) > 0, "Transformer model artifact is empty"

    def test_autoencoder_artifact_exists(self):
        path = os.path.join(MODELS_DIR, "autoencoder.keras")
        assert os.path.isfile(path), f"Autoencoder model artifact missing: {path}"
        assert os.path.getsize(path) > 0, "Autoencoder model artifact is empty"

    def test_scaler_artifact_exists(self):
        path = os.path.join(MODELS_DIR, "scaler.pkl")
        assert os.path.isfile(path), f"Scaler artifact missing: {path}"
        assert os.path.getsize(path) > 0, "Scaler artifact is empty"

    def test_xgb_features_json_exists(self):
        path = os.path.join(MODELS_DIR, "xgb_features.json")
        assert os.path.isfile(path), f"XGBoost features list missing: {path}"
        with open(path, "r") as f:
            features = json.load(f)
        assert isinstance(features, list), "xgb_features.json must be a list"
        assert len(features) > 0, "xgb_features.json is empty"

    def test_ae_threshold_json_exists_and_valid(self):
        path = os.path.join(MODELS_DIR, "ae_threshold.json")
        assert os.path.isfile(path), f"Autoencoder threshold missing: {path}"
        with open(path, "r") as f:
            data = json.load(f)
        assert "anomaly_threshold" in data, "ae_threshold.json missing 'anomaly_threshold' key"
        assert isinstance(data["anomaly_threshold"], float), "anomaly_threshold must be float"
        assert data["anomaly_threshold"] > 0, "anomaly_threshold must be positive"

    def test_xgboost_model_loads(self):
        import xgboost as xgb
        model = xgb.XGBClassifier()
        model.load_model(os.path.join(MODELS_DIR, "xgboost_model.json"))
        # Verify it has a predict_proba method
        assert hasattr(model, "predict_proba"), "XGBoost model missing predict_proba"

    def test_scaler_loads(self):
        import joblib
        scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
        assert hasattr(scaler, "transform"), "Scaler missing transform method"
        assert hasattr(scaler, "n_features_in_"), "Scaler not fitted"
        assert scaler.n_features_in_ == 6, f"Scaler expects 6 features, got {scaler.n_features_in_}"

    def test_keras_models_load(self):
        """Load all three Keras models and verify they have predict methods."""
        import tensorflow as tf
        for name in ["cnn_lstm.keras", "transformer.keras", "autoencoder.keras"]:
            path = os.path.join(MODELS_DIR, name)
            model = tf.keras.models.load_model(path, compile=False)
            assert hasattr(model, "predict"), f"{name} missing predict method"


# =========================================================================
# 2. FEATURE ENGINEERING TESTS
# =========================================================================

class TestFeatureEngineering:
    """Verify the feature engineering pipeline produces correct output."""

    def _make_df(self, n_rows=60):
        """Create a minimal DataFrame mimicking inference input."""
        base_time = pd.Timestamp("2026-01-01 00:00:00")
        return pd.DataFrame({
            "patient_id": ["TEST-FE-001"] * n_rows,
            "timestamp": [base_time + pd.Timedelta(minutes=i) for i in range(n_rows)],
            "heart_rate": np.random.uniform(130, 160, n_rows),
            "spo2": np.random.uniform(94, 99, n_rows),
            "respiratory_rate": np.random.uniform(40, 55, n_rows),
            "temperature": np.random.uniform(36.5, 37.5, n_rows),
            "systolic_bp": np.random.uniform(55, 70, n_rows),
            "diastolic_bp": np.random.uniform(35, 48, n_rows),
        })

    def test_engineer_features_adds_columns(self):
        from ml.features.features import engineer_features
        df = self._make_df()
        df_feat = engineer_features(df, window_sizes=[15, 30, 60])
        # Original columns + rolling stats + rate of change
        # Rolling: 6 vitals * 4 stats * 3 windows = 72
        # Rate-of-change: 6 vitals * 3 windows = 18
        # Total new: 90
        original_cols = len(df.columns)
        new_cols = len(df_feat.columns) - original_cols
        assert new_cols == 90, f"Expected 90 new feature columns, got {new_cols}"

    def test_engineer_features_no_nans(self):
        from ml.features.features import engineer_features
        df = self._make_df()
        df_feat = engineer_features(df, window_sizes=[15, 30, 60])
        nan_count = df_feat.isnull().sum().sum()
        assert nan_count == 0, f"Feature engineering left {nan_count} NaN values"

    def test_feature_names_match_xgb_requirements(self):
        """Verify that feature engineering with [15, 30, 60] produces all columns XGBoost needs."""
        from ml.features.features import engineer_features, VITAL_COLUMNS

        df = self._make_df()
        # Add missingness flags (as done in inference_service.predict)
        for col in VITAL_COLUMNS:
            df[f"{col}_was_missing"] = 0

        df_feat = engineer_features(df, window_sizes=[15, 30, 60])

        with open(os.path.join(MODELS_DIR, "xgb_features.json"), "r") as f:
            required_features = json.load(f)

        available = set(df_feat.columns)
        missing = [f for f in required_features if f not in available]
        assert len(missing) == 0, f"Missing XGBoost features: {missing}"


# =========================================================================
# 3. INDIVIDUAL MODEL INFERENCE TESTS
# =========================================================================

class TestXGBoostInference:
    """Verify XGBoost inference produces valid output."""

    def test_xgboost_predict_proba(self):
        import xgboost as xgb
        from ml.features.features import engineer_features, VITAL_COLUMNS

        model = xgb.XGBClassifier()
        model.load_model(os.path.join(MODELS_DIR, "xgboost_model.json"))

        with open(os.path.join(MODELS_DIR, "xgb_features.json"), "r") as f:
            feature_names = json.load(f)

        # Create synthetic input
        n = 60
        base_time = pd.Timestamp("2026-01-01")
        df = pd.DataFrame({
            "patient_id": ["XGB-TEST"] * n,
            "timestamp": [base_time + pd.Timedelta(minutes=i) for i in range(n)],
            "heart_rate": np.full(n, 140.0),
            "spo2": np.full(n, 96.0),
            "respiratory_rate": np.full(n, 45.0),
            "temperature": np.full(n, 37.0),
            "systolic_bp": np.full(n, 60.0),
            "diastolic_bp": np.full(n, 40.0),
        })
        for col in VITAL_COLUMNS:
            df[f"{col}_was_missing"] = 0

        df_feat = engineer_features(df, window_sizes=[15, 30, 60])
        X = df_feat.iloc[-1:][feature_names]

        proba = model.predict_proba(X)
        assert proba.shape == (1, 2), f"Expected shape (1, 2), got {proba.shape}"
        assert 0.0 <= proba[0, 1] <= 1.0, f"Probability out of range: {proba[0, 1]}"


class TestDeepLearningInference:
    """Verify CNN-LSTM, Transformer, and Autoencoder inference."""

    @pytest.fixture(scope="class")
    def sequence_input(self, request):
        """Create a (1, 30, 6) synthetic sequence."""
        np.random.seed(42)
        return np.random.uniform(0.0, 1.0, (1, 30, 6)).astype(np.float32)

    def test_cnn_lstm_inference(self, sequence_input):
        import tensorflow as tf
        model = tf.keras.models.load_model(
            os.path.join(MODELS_DIR, "cnn_lstm.keras"), compile=False
        )
        output = model.predict(sequence_input, verbose=0)
        assert output.shape == (1, 1), f"CNN-LSTM output shape: {output.shape}"
        score = float(output[0, 0])
        assert 0.0 <= score <= 1.0, f"CNN-LSTM score out of range: {score}"

    def test_transformer_inference(self, sequence_input):
        import tensorflow as tf
        model = tf.keras.models.load_model(
            os.path.join(MODELS_DIR, "transformer.keras"), compile=False
        )
        output = model.predict(sequence_input, verbose=0)
        assert output.shape == (1, 1), f"Transformer output shape: {output.shape}"
        score = float(output[0, 0])
        assert 0.0 <= score <= 1.0, f"Transformer score out of range: {score}"

    def test_autoencoder_inference(self, sequence_input):
        import tensorflow as tf
        model = tf.keras.models.load_model(
            os.path.join(MODELS_DIR, "autoencoder.keras"), compile=False
        )
        reconstruction = model.predict(sequence_input, verbose=0)
        assert reconstruction.shape == sequence_input.shape, (
            f"Autoencoder output shape mismatch: {reconstruction.shape} vs {sequence_input.shape}"
        )

    def test_autoencoder_anomaly_score(self, sequence_input):
        """Verify autoencoder MSE -> pseudo-probability conversion."""
        import tensorflow as tf
        model = tf.keras.models.load_model(
            os.path.join(MODELS_DIR, "autoencoder.keras"), compile=False
        )
        with open(os.path.join(MODELS_DIR, "ae_threshold.json"), "r") as f:
            threshold = json.load(f)["anomaly_threshold"]

        reconstruction = model.predict(sequence_input, verbose=0)
        mse = np.mean(np.square(sequence_input - reconstruction), axis=(1, 2))
        ae_prob = np.clip(0.5 * (mse / threshold), 0.0, 1.0)

        assert ae_prob.shape == (1,), f"AE prob shape: {ae_prob.shape}"
        assert 0.0 <= ae_prob[0] <= 1.0, f"AE pseudo-prob out of range: {ae_prob[0]}"


# =========================================================================
# 4. FUSION MODEL TESTS
# =========================================================================

class TestFusionModel:
    """Verify the FusionModel loads and produces valid ensemble output."""

    @pytest.fixture(scope="class")
    def fusion(self, request):
        from ml.models.fusion import FusionModel
        return FusionModel(models_dir=MODELS_DIR)

    @pytest.fixture(scope="class")
    def demo_inputs(self, request):
        """Create matching flat and sequence inputs."""
        from ml.features.features import engineer_features, VITAL_COLUMNS

        n = 60
        base_time = pd.Timestamp("2026-01-01")
        df = pd.DataFrame({
            "patient_id": ["FUSION-TEST"] * n,
            "timestamp": [base_time + pd.Timedelta(minutes=i) for i in range(n)],
            "heart_rate": np.full(n, 140.0),
            "spo2": np.full(n, 96.0),
            "respiratory_rate": np.full(n, 45.0),
            "temperature": np.full(n, 37.0),
            "systolic_bp": np.full(n, 60.0),
            "diastolic_bp": np.full(n, 40.0),
        })
        for col in VITAL_COLUMNS:
            df[f"{col}_was_missing"] = 0

        df_feat = engineer_features(df, window_sizes=[15, 30, 60])
        flat_input = df_feat.iloc[-1:]

        # Scale sequence
        import joblib
        scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
        df_seq = df.iloc[-30:].copy()
        df_seq[VITAL_COLUMNS] = scaler.transform(df_seq[VITAL_COLUMNS])
        seq_input = np.expand_dims(df_seq[VITAL_COLUMNS].values, axis=0)

        return flat_input, seq_input

    def test_fusion_loads_all_models(self, fusion):
        assert fusion.xgb_model is not None
        assert fusion.cnn_lstm_model is not None
        assert fusion.transformer_model is not None
        assert fusion.autoencoder_model is not None
        assert fusion.ae_threshold > 0

    def test_fusion_weights_sum_to_one(self, fusion):
        total = sum(fusion.weights.values())
        assert abs(total - 1.0) < 1e-6, f"Fusion weights sum to {total}, expected 1.0"

    def test_fusion_predict_risk_output(self, fusion, demo_inputs):
        flat_input, seq_input = demo_inputs
        fusion_prob, ind_probs = fusion.predict_risk(flat_input, seq_input, batch_size=1)

        # Fusion probability
        assert fusion_prob.shape == (1,), f"Fusion prob shape: {fusion_prob.shape}"
        assert 0.0 <= fusion_prob[0] <= 1.0, f"Fusion prob out of range: {fusion_prob[0]}"

        # Individual model probabilities
        for model_name in ["xgboost", "cnn_lstm", "autoencoder", "transformer"]:
            assert model_name in ind_probs, f"Missing model: {model_name}"
            score = float(ind_probs[model_name][0])
            assert 0.0 <= score <= 1.0, f"{model_name} score out of range: {score}"

    def test_fusion_deterministic(self, fusion, demo_inputs):
        """Same input must produce the same output (deterministic inference)."""
        flat_input, seq_input = demo_inputs
        prob1, _ = fusion.predict_risk(flat_input, seq_input, batch_size=1)
        prob2, _ = fusion.predict_risk(flat_input, seq_input, batch_size=1)
        assert abs(prob1[0] - prob2[0]) < 1e-4, (
            f"Fusion not deterministic: {prob1[0]} vs {prob2[0]}"
        )


# =========================================================================
# 5. RISK LEVEL TESTS
# =========================================================================

class TestRiskLevelClassification:
    """Verify risk level boundaries."""

    def _classify(self, score):
        if score < 0.30:
            return "LOW"
        elif score < 0.70:
            return "WATCH"
        else:
            return "HIGH"

    def test_low_risk(self):
        assert self._classify(0.0) == "LOW"
        assert self._classify(0.15) == "LOW"
        assert self._classify(0.29) == "LOW"

    def test_watch_risk(self):
        assert self._classify(0.30) == "WATCH"
        assert self._classify(0.50) == "WATCH"
        assert self._classify(0.69) == "WATCH"

    def test_high_risk(self):
        assert self._classify(0.70) == "HIGH"
        assert self._classify(0.85) == "HIGH"
        assert self._classify(1.0) == "HIGH"

    def test_boundary_low_watch(self):
        assert self._classify(0.299999) == "LOW"
        assert self._classify(0.3) == "WATCH"

    def test_boundary_watch_high(self):
        assert self._classify(0.699999) == "WATCH"
        assert self._classify(0.7) == "HIGH"


# =========================================================================
# 6. END-TO-END INFERENCE SERVICE TESTS
# =========================================================================

class TestInferenceServiceE2E:
    """Verify the full InferenceService pipeline."""

    @pytest.fixture(scope="class")
    def service(self, request):
        from backend.app.services.inference_service import InferenceService
        svc = InferenceService(models_dir=MODELS_DIR)
        svc.load_models()
        return svc

    def _make_records(self, patient_id="E2E-TEST-001", n=60):
        """Create Pydantic-like record objects for inference."""
        from backend.app.schemas.predict_schema import VitalSignRecord
        from datetime import datetime, timedelta

        base_time = datetime(2026, 1, 1)
        return [
            VitalSignRecord(
                timestamp=(base_time + timedelta(minutes=i)).isoformat(),
                patient_id=patient_id,
                heart_rate=140.0,
                spo2=96.0,
                respiratory_rate=45.0,
                temperature=37.0,
                systolic_bp=60.0,
                diastolic_bp=40.0,
            )
            for i in range(n)
        ]

    def test_service_is_ready(self, service):
        assert service.is_ready is True

    def test_service_predict_returns_dict(self, service):
        records = self._make_records()
        result = service.predict(records)
        assert isinstance(result, dict)
        assert "risk_score" in result
        assert "risk_level" in result
        assert "individual_models" in result

    def test_service_predict_risk_score_range(self, service):
        records = self._make_records()
        result = service.predict(records)
        assert 0.0 <= result["risk_score"] <= 1.0

    def test_service_predict_risk_level_valid(self, service):
        records = self._make_records()
        result = service.predict(records)
        assert result["risk_level"] in ["LOW", "WATCH", "HIGH"]

    def test_service_predict_individual_scores(self, service):
        records = self._make_records()
        result = service.predict(records)
        models = result["individual_models"]
        for name in ["xgboost", "cnn_lstm", "autoencoder", "transformer"]:
            assert name in models
            assert 0.0 <= models[name] <= 1.0

    def test_service_predict_patient_id_preserved(self, service):
        records = self._make_records(patient_id="ID-PRESERVE-TEST")
        result = service.predict(records)
        assert result["patient_id"] == "ID-PRESERVE-TEST"

    def test_service_not_loaded_raises(self):
        from backend.app.services.inference_service import InferenceService
        svc = InferenceService(models_dir=MODELS_DIR)
        # Don't call load_models
        with pytest.raises(RuntimeError, match="Models are not loaded"):
            svc.predict([])


# =========================================================================
# 7. MYSQL PERSISTENCE TESTS (via API)
# =========================================================================

class TestMySQLPersistence:
    """Verify that predictions are persisted to the database."""

    def test_prediction_persisted(self, client, vital_records):
        """After calling /predict, check that predictions table has a new row."""
        response = client.post("/api/v1/predict/", json={"records": vital_records})
        assert response.status_code == 200

        # Query the database for the prediction
        from tests.conftest import TestSessionLocal
        from backend.app.db.models import Prediction

        db = TestSessionLocal()
        try:
            pred = db.query(Prediction).filter(
                Prediction.patient_id == "TEST-PATIENT-001"
            ).order_by(Prediction.id.desc()).first()
            assert pred is not None, "Prediction not found in database"
            assert pred.risk_score is not None
            assert pred.risk_level in ["LOW", "WATCH", "HIGH"]
            assert pred.xgb_score is not None
            assert pred.cnn_lstm_score is not None
            assert pred.ae_score is not None
            assert pred.transformer_score is not None
        finally:
            db.close()

    def test_vital_signs_persisted(self, client, vital_records):
        """Verify that vital signs are stored in the database after /predict."""
        response = client.post("/api/v1/predict/", json={"records": vital_records})
        assert response.status_code == 200

        from tests.conftest import TestSessionLocal
        from backend.app.db.models import VitalSign

        db = TestSessionLocal()
        try:
            vitals = db.query(VitalSign).filter(
                VitalSign.patient_id == "TEST-PATIENT-001"
            ).count()
            assert vitals > 0, "No vital signs found in database"
        finally:
            db.close()
