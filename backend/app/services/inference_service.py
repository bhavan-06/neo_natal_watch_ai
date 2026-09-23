"""
NeoNatal Watch AI — Optimized Inference Service
-------------------------------------------------
OPTIMIZATIONS FOR LOW-SPEC HARDWARE (8GB RAM, Integrated GPU):
  1. TensorFlow is configured BEFORE any imports to limit RAM usage.
  2. CPU thread count is capped to match the 4-core Ryzen 3 CPU.
  3. OneDNN warnings are suppressed to keep logs clean.
  4. Models are loaded with compile=False (faster load, less overhead).
  5. batch_size=1 for single-request inference (saves memory vs batching).
"""

# -----------------------------------------------------------------------
# MUST HAPPEN BEFORE any TensorFlow import
# -----------------------------------------------------------------------
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"        # Suppress TF C++ logs
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"        # Disable oneDNN (stability on AMD)
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true" # Don't pre-allocate GPU memory
os.environ["OMP_NUM_THREADS"] = "4"              # Match Ryzen 3's 4 cores
os.environ["TF_NUM_INTRAOP_THREADS"] = "4"
os.environ["TF_NUM_INTEROP_THREADS"] = "2"

import pandas as pd
import numpy as np
import joblib
import logging
from typing import Dict, Any

from ml.models.fusion import FusionModel
from ml.features.features import engineer_features
from ml.preprocessing.preprocess import VITAL_COLUMNS

logger = logging.getLogger("InferenceService")


class InferenceService:
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.fusion_model = None
        self.scaler = None
        self.is_ready = False

    def load_models(self):
        """
        Loads all models into memory with low-RAM optimizations applied.
        TensorFlow thread count and memory growth are configured inside
        FusionModel before any Keras model is loaded.
        """
        logger.info("Loading AI Models and Scaler into memory...")
        try:
            # Configure TF thread usage BEFORE loading models
            import tensorflow as tf
            try:
                tf.config.threading.set_intra_op_parallelism_threads(4)   # Ryzen 3 has 4 cores
                tf.config.threading.set_inter_op_parallelism_threads(2)
            except RuntimeError:
                # TF context already initialized (e.g. during tests) — skip reconfiguration
                logger.info("TF threading already configured, skipping.")

            # Limit GPU memory growth (important for integrated 486 MB GPU)
            for gpu in tf.config.list_physical_devices("GPU"):
                tf.config.experimental.set_memory_growth(gpu, True)

            self.fusion_model = FusionModel(models_dir=self.models_dir)
            self.scaler = joblib.load(f"{self.models_dir}/scaler.pkl")
            self.is_ready = True
            logger.info("Inference Service is READY.")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise e

    def predict(self, records: list) -> Dict[str, Any]:
        """
        Takes 60 raw records, processes them, and returns a risk prediction.
        Also broadcasts a WebSocket alert if risk level is HIGH.
        """
        if not self.is_ready:
            raise RuntimeError("Models are not loaded yet.")

        # Convert list of Pydantic dicts to DataFrame
        df = pd.DataFrame([r.model_dump() for r in records])

        # Ensure timestamp is datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        # Add required missingness flags for XGBoost
        for col in VITAL_COLUMNS:
            df[f"{col}_was_missing"] = df[col].isnull().astype(int)

        patient_id = df["patient_id"].iloc[-1]
        current_time = df["timestamp"].iloc[-1].isoformat()

        # 1. Feature Engineering for XGBoost
        df_features = engineer_features(df, window_sizes=[15, 30, 60])
        flat_input = df_features.iloc[-1:]

        # 2. Sequence Preparation for Deep Learning
        df_seq = df.iloc[-30:].copy()
        df_seq[VITAL_COLUMNS] = self.scaler.transform(df_seq[VITAL_COLUMNS])
        sequence_input = np.expand_dims(df_seq[VITAL_COLUMNS].values, axis=0)

        # 3. Generate Prediction — use batch_size=1 to save RAM
        fusion_prob, ind_probs = self.fusion_model.predict_risk(
            flat_features=flat_input,
            sequence_features=sequence_input,
            batch_size=1,   # Low-spec optimization: process one sample at a time
        )

        score = float(fusion_prob[0])

        if score < 0.30:
            level = "LOW"
        elif score < 0.70:
            level = "WATCH"
        else:
            level = "HIGH"

        result = {
            "patient_id": patient_id,
            "timestamp": current_time,
            "risk_score": round(score, 4),
            "risk_level": level,
            "individual_models": {
                "xgboost": round(float(ind_probs["xgboost"][0]), 4),
                "cnn_lstm": round(float(ind_probs["cnn_lstm"][0]), 4),
                "autoencoder": round(float(ind_probs["autoencoder"][0]), 4),
                "transformer": round(float(ind_probs["transformer"][0]), 4),
            },
            "message": "Prediction successful",
        }

        # Phase 15 & L: Alert System and Deduplication
        if level == "HIGH":
            # Deduplication: only broadcast if this is a NEW high risk transition
            # Or if it's been more than X minutes (for this prototype, just state transition)
            if not getattr(self, "alert_state", {}).get(patient_id, False):
                if not hasattr(self, "alert_state"):
                    self.alert_state = {}
                self.alert_state[patient_id] = True
                
                try:
                    import asyncio
                    from ..api.endpoints.ws_manager import manager
                    alert_payload = {
                        "type": "high_risk",
                        "patient_id": patient_id,
                        "timestamp": current_time,
                        "risk_score": result["risk_score"],
                        "message": "ALERT: High deterioration risk detected.",
                    }
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(manager.broadcast(alert_payload))
                except Exception as alert_err:
                    logger.warning(f"Alert broadcast failed: {alert_err}")
        else:
            # Reset alert state for patient when risk drops below HIGH
            if hasattr(self, "alert_state") and patient_id in self.alert_state:
                self.alert_state[patient_id] = False

        return result

    def explain_xgboost(self, records: list, top_n: int = 5) -> Dict[str, Any]:
        """
        Generates a SHAP explanation for the XGBoost model given 60 raw records.
        Does NOT modify the model or run inference predictions.
        """
        if not self.is_ready:
            raise RuntimeError("Models are not loaded yet.")

        if not hasattr(self, "shap_explainer") or self.shap_explainer is None:
            from ml.explainability.shap_explainer import XGBoostShapExplainer
            self.shap_explainer = XGBoostShapExplainer(models_dir=self.models_dir)

        df = pd.DataFrame([r.model_dump() for r in records])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        for col in VITAL_COLUMNS:
            df[f"{col}_was_missing"] = df[col].isnull().astype(int)

        df_features = engineer_features(df, window_sizes=[15, 30, 60])
        flat_input = df_features.iloc[-1:]

        explanation = self.shap_explainer.explain_instance(flat_input, top_n=top_n)
        explanation["patient_id"] = df["patient_id"].iloc[-1]
        explanation["timestamp"] = df["timestamp"].iloc[-1].isoformat()
        return explanation

    def explain_autoencoder(self, records: list, top_n: int = 5) -> Dict[str, Any]:
        """
        Generates an Autoencoder reconstruction error explanation for a 30-vital sequence.
        Does NOT modify the model or run inference predictions.
        """
        if not self.is_ready:
            raise RuntimeError("Models are not loaded yet.")

        if not hasattr(self, "ae_explainer") or self.ae_explainer is None:
            from ml.explainability.autoencoder_explainer import AutoencoderAnomalyExplainer
            self.ae_explainer = AutoencoderAnomalyExplainer(models_dir=self.models_dir)

        df = pd.DataFrame([r.model_dump() for r in records])
        if len(df) < 30:
            raise ValueError(f"Insufficient vitals sequence. Received {len(df)} records, required 30.")

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
        df_seq_30 = df.iloc[-30:].copy()

        explanation = self.ae_explainer.explain_sequence(df_seq_30, top_n=top_n)
        return explanation

    def explain_transformer(self, records: list, top_n: int = 5) -> Dict[str, Any]:
        """
        Generates Multi-Head Self-Attention temporal weights for the Transformer model.
        Does NOT modify the model or run inference predictions.
        """
        if not self.is_ready:
            raise RuntimeError("Models are not loaded yet.")

        if not hasattr(self, "transformer_explainer") or self.transformer_explainer is None:
            from ml.explainability.transformer_explainer import TransformerAttentionExplainer
            self.transformer_explainer = TransformerAttentionExplainer(models_dir=self.models_dir)

        df = pd.DataFrame([r.model_dump() for r in records])
        if len(df) < 30:
            raise ValueError(f"Insufficient vitals sequence. Received {len(df)} records, required 30.")

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
        df_seq_30 = df.iloc[-30:].copy()

        explanation = self.transformer_explainer.explain_sequence(df_seq_30, top_n=top_n)
        return explanation

    def get_transformer_forecast(self, records: list) -> Dict[str, Any]:
        """
        Returns forecasting audit status for the existing Transformer model.
        Reports exact technical limitation without fabricating fake forecasts.
        """
        if not self.is_ready:
            raise RuntimeError("Models are not loaded yet.")

        df = pd.DataFrame([r.model_dump() for r in records])
        if len(df) < 30:
            raise ValueError(f"Insufficient vitals sequence. Received {len(df)} records, required 30.")

        patient_id = str(df["patient_id"].iloc[-1]) if "patient_id" in df.columns else "UNKNOWN"

        return {
            "model_name": "Transformer",
            "patient_id": patient_id,
            "forecasting_supported": False,
            "technical_limitation": (
                "Multi-horizon forecasting requires a forecasting-capable model/training target "
                "and cannot be truthfully implemented using the current classifier artifact without "
                "retraining or architecture changes."
            ),
            "current_model_task": "Binary Classification (Deterioration Risk Probability)",
            "output_shape": "[1, 1]",
            "output_activation": "sigmoid",
            "safety_disclaimer": (
                "Forecasts are model-generated research outputs based on the available input sequence. "
                "They are not clinical predictions, diagnoses, or treatment recommendations. "
                "SYNTHETIC / ACADEMIC simulation DATA — NOT FOR CLINICAL USE."
            )
        }


# Global singleton instance
inference_service = InferenceService(models_dir="models")



