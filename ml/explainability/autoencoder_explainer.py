"""
ml/explainability/autoencoder_explainer.py
--------------------------------------------
Authoritative Autoencoder Anomaly Explainer service for NeoNatal Watch AI.

Phase O — Controlled Autoencoder Anomaly Explainability & Visualization.
Calculates per-feature reconstruction errors, percentage feature contributions,
time-step error traces, and latest step physical residuals to explain WHY
an Autoencoder reconstruction anomaly score was generated.

SAFETY NOTICE:
Autoencoder reconstruction errors highlight vital sign sequence deviations
relative to learned normal patterns. They do NOT represent clinical causation,
diagnosis, treatment recommendations, or clinical importance.
SYNTHETIC / ACADEMIC DEMO DATA — NOT FOR CLINICAL USE.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AutoencoderExplainer")

MODELS_DIR_DEFAULT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models"))
VITAL_COLUMNS = [
    "heart_rate",
    "spo2",
    "respiratory_rate",
    "temperature",
    "systolic_bp",
    "diastolic_bp",
]


class AutoencoderAnomalyExplainer:
    """
    Lightweight, deterministic Autoencoder Reconstruction Explainer.
    Reuses existing models/autoencoder.keras, models/scaler.pkl, and models/ae_threshold.json.
    Does NOT retrain, refit, or modify the model architecture or weights.
    """

    def __init__(self, models_dir: str = MODELS_DIR_DEFAULT):
        self.models_dir = models_dir
        self.autoencoder_model: Optional[tf.keras.Model] = None
        self.scaler = None
        self.ae_threshold: float = 0.004240
        self.vital_columns = VITAL_COLUMNS
        self._load_resources()

    def _load_resources(self):
        ae_path = os.path.join(self.models_dir, "autoencoder.keras")
        scaler_path = os.path.join(self.models_dir, "scaler.pkl")
        thresh_path = os.path.join(self.models_dir, "ae_threshold.json")

        if not os.path.exists(ae_path):
            raise FileNotFoundError(f"Autoencoder model not found at {ae_path}")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler not found at {scaler_path}")
        if not os.path.exists(thresh_path):
            raise FileNotFoundError(f"Threshold file not found at {thresh_path}")

        self.autoencoder_model = tf.keras.models.load_model(ae_path, compile=False)
        self.scaler = joblib.load(scaler_path)
        with open(thresh_path, "r") as f:
            self.ae_threshold = float(json.load(f)["anomaly_threshold"])

        logger.info(
            f"Loaded Autoencoder explainer with threshold {self.ae_threshold} "
            f"for {len(self.vital_columns)} vital features."
        )

    def explain_sequence(
        self,
        df_seq_30: pd.DataFrame,
        top_n: int = 5
    ) -> Dict[str, Any]:
        """
        Calculates exact reconstruction error decomposition for a 30-step sequence DataFrame.

        Args:
            df_seq_30: DataFrame with exactly 30 rows containing VITAL_COLUMNS.
            top_n: Number of top contributing vital features to return (default 5).

        Returns:
            Structured dictionary with per-feature MSEs, percentage contributions,
            time-series error traces, physical residuals, and safety metadata.
        """
        if self.autoencoder_model is None:
            raise RuntimeError("Autoencoder model is not loaded.")

        if len(df_seq_30) != 30:
            raise ValueError(f"Sequence length must be exactly 30 rows, received {len(df_seq_30)} rows.")

        missing_cols = [c for c in self.vital_columns if c not in df_seq_30.columns]
        if missing_cols:
            raise ValueError(f"DataFrame missing required vital columns: {missing_cols}")

        # Extract and scale vital signs sequence
        raw_vitals_30 = df_seq_30[self.vital_columns].copy().fillna(0.0).values
        scaled_seq_30 = self.scaler.transform(df_seq_30[self.vital_columns].fillna(0.0))  # (30, 6)

        # 3D model input (1, 30, 6)
        sequence_input = np.expand_dims(scaled_seq_30, axis=0)

        # Predict reconstruction (1, 30, 6)
        ae_reconstruction = self.autoencoder_model.predict(sequence_input, batch_size=1, verbose=0)

        # Element-wise squared error in scaled space: (30, 6)
        sq_error_matrix = np.square(scaled_seq_30 - ae_reconstruction[0])

        # Aggregate MSE across all steps and features
        ae_mse = float(np.mean(sq_error_matrix))

        # Replicate exact Autoencoder anomaly risk score formula from fusion.py
        ae_score = float(np.clip(0.5 * (ae_mse / self.ae_threshold), 0.0, 1.0))
        is_anomalous = bool(ae_mse > self.ae_threshold)

        # Per-feature MSE across 30 time steps: (6,)
        per_feature_mse = np.mean(sq_error_matrix, axis=0)  # (6,)
        total_feature_mse_sum = float(np.sum(per_feature_mse))

        # Latest step (index 29) physical unscaled values and residuals
        latest_scaled = scaled_seq_30[-1:]  # (1, 6)
        latest_reconstructed_scaled = ae_reconstruction[0, -1:]  # (1, 6)

        latest_unscaled = self.scaler.inverse_transform(latest_scaled)[0]
        latest_reconstructed_unscaled = self.scaler.inverse_transform(latest_reconstructed_scaled)[0]

        # Feature decomposition entries
        feature_entries = []
        for idx, col_name in enumerate(self.vital_columns):
            feat_mse = float(per_feature_mse[idx])
            contrib_pct = float(
                (feat_mse / total_feature_mse_sum * 100.0)
                if total_feature_mse_sum > 1e-12 else (100.0 / len(self.vital_columns))
            )

            actual_val = float(latest_unscaled[idx])
            recon_val = float(latest_reconstructed_unscaled[idx])
            abs_residual = float(abs(actual_val - recon_val))

            feature_entries.append({
                "vital_name": col_name,
                "reconstruction_mse": round(feat_mse, 6),
                "contribution_percent": round(contrib_pct, 2),
                "latest_actual_value": round(actual_val, 2),
                "latest_reconstructed_value": round(recon_val, 2),
                "latest_absolute_residual": round(abs_residual, 4),
            })

        # Rank by reconstruction MSE descending
        feature_entries.sort(key=lambda x: x["reconstruction_mse"], reverse=True)
        top_contributing_vitals = feature_entries[:top_n]

        # Time-series error trace across 30 steps
        time_series_trace = []
        timestamps = (
            df_seq_30["timestamp"].astype(str).tolist()
            if "timestamp" in df_seq_30.columns else [f"step_{i}" for i in range(30)]
        )

        # Time-step MSE across 6 features: (30,)
        per_timestep_mse = np.mean(sq_error_matrix, axis=1)

        for step_idx in range(30):
            step_ts = timestamps[step_idx]
            step_mse = float(per_timestep_mse[step_idx])
            time_series_trace.append({
                "step_index": step_idx,
                "timestamp": step_ts,
                "timestep_reconstruction_mse": round(step_mse, 6),
                "exceeds_threshold": bool(step_mse > self.ae_threshold),
            })

        patient_id = (
            str(df_seq_30["patient_id"].iloc[-1])
            if "patient_id" in df_seq_30.columns and len(df_seq_30["patient_id"]) > 0
            else "UNKNOWN"
        )
        timestamp = (
            str(df_seq_30["timestamp"].iloc[-1])
            if "timestamp" in df_seq_30.columns and len(df_seq_30["timestamp"]) > 0
            else "UNKNOWN"
        )

        return {
            "model_name": "Autoencoder",
            "patient_id": patient_id,
            "timestamp": timestamp,
            "model_output_explained": "Sequence reconstruction error decomposition (MSE)",
            "overall_reconstruction_mse": round(ae_mse, 6),
            "ae_threshold": round(self.ae_threshold, 6),
            "ae_anomaly_score": round(ae_score, 4),
            "is_anomalous": is_anomalous,
            "total_vitals_evaluated": len(self.vital_columns),
            "window_size_steps": 30,
            "top_contributing_vitals": top_contributing_vitals,
            "all_vital_contributions": feature_entries,
            "time_series_error_trace": time_series_trace,
            "safety_disclaimer": (
                "Autoencoder reconstruction errors highlight vital sign sequence deviations "
                "relative to learned normal patterns. They do not represent clinical causation, "
                "diagnosis, treatment recommendations, or clinical importance. "
                "SYNTHETIC / ACADEMIC DEMO DATA — NOT FOR CLINICAL USE."
            )
        }

