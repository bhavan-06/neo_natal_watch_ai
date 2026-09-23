"""
ml/explainability/transformer_explainer.py
--------------------------------------------
Authoritative Transformer Self-Attention Explainer service for NeoNatal Watch AI.

Phase P — Controlled Transformer Attention Explainability & Multi-Horizon Forecasting Integration.
Extracts exact Multi-Head Self-Attention matrices from existing models/transformer.keras
without modifying model architecture, retrain weights, or changing prediction probabilities.

SAFETY NOTICE:
Transformer attention weights show how the model distributed attention
across the input sequence window. They do NOT establish clinical causation,
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

logger = logging.getLogger("TransformerExplainer")

MODELS_DIR_DEFAULT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models"))
VITAL_COLUMNS = [
    "heart_rate",
    "spo2",
    "respiratory_rate",
    "temperature",
    "systolic_bp",
    "diastolic_bp",
]


class TransformerAttentionExplainer:
    """
    Lightweight, deterministic Transformer Self-Attention Explainer.
    Reuses existing models/transformer.keras and models/scaler.pkl.
    Does NOT retrain, refit, or modify the model architecture or weights.
    """

    def __init__(self, models_dir: str = MODELS_DIR_DEFAULT):
        self.models_dir = models_dir
        self.transformer_model: Optional[tf.keras.Model] = None
        self.scaler = None
        self.vital_columns = VITAL_COLUMNS
        self.num_layers = 2
        self.num_heads = 4
        self.sequence_length = 30
        self._load_resources()

    def _load_resources(self):
        transformer_path = os.path.join(self.models_dir, "transformer.keras")
        scaler_path = os.path.join(self.models_dir, "scaler.pkl")

        if not os.path.exists(transformer_path):
            raise FileNotFoundError(f"Transformer model not found at {transformer_path}")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler not found at {scaler_path}")

        self.transformer_model = tf.keras.models.load_model(transformer_path, compile=False)
        self.scaler = joblib.load(scaler_path)

        # Inspect layer normalization sub-models for intermediate attention extraction
        try:
            ln1 = self.transformer_model.get_layer("layer_normalization")
            ln3 = self.transformer_model.get_layer("layer_normalization_2")
            self.sub_model1 = tf.keras.models.Model(inputs=self.transformer_model.inputs, outputs=ln1.output)
            self.sub_model2 = tf.keras.models.Model(inputs=self.transformer_model.inputs, outputs=ln3.output)
            self.mha1 = self.transformer_model.get_layer("multi_head_attention")
            self.mha2 = self.transformer_model.get_layer("multi_head_attention_1")
        except Exception as err:
            logger.warning(f"Error binding attention sub-models: {err}")

        logger.info(
            f"Loaded Transformer explainer with {self.num_layers} layers and "
            f"{self.num_heads} attention heads for 30-step sequence length."
        )

    def explain_sequence(
        self,
        df_seq_30: pd.DataFrame,
        top_n: int = 5
    ) -> Dict[str, Any]:
        """
        Calculates exact Multi-Head Attention weights for a 30-step sequence DataFrame.

        Args:
            df_seq_30: DataFrame with exactly 30 rows containing VITAL_COLUMNS.
            top_n: Number of top attended time steps to return (default 5).

        Returns:
            Structured dictionary with multi-head attention maps, temporal attention summary,
            prediction risk score, and safety metadata.
        """
        if self.transformer_model is None:
            raise RuntimeError("Transformer model is not loaded.")

        if len(df_seq_30) != 30:
            raise ValueError(f"Sequence length must be exactly 30 rows, received {len(df_seq_30)} rows.")

        missing_cols = [c for c in self.vital_columns if c not in df_seq_30.columns]
        if missing_cols:
            raise ValueError(f"DataFrame missing required vital columns: {missing_cols}")

        # Scale vital signs sequence
        scaled_seq_30 = self.scaler.transform(df_seq_30[self.vital_columns].fillna(0.0))  # (30, 6)
        sequence_input = np.expand_dims(scaled_seq_30, axis=0)  # (1, 30, 6)

        # Baseline prediction check (prediction before attention extraction)
        prob_before = float(self.transformer_model.predict(sequence_input, batch_size=1, verbose=0)[0, 0])

        # Intermediate activations for MultiHeadAttention inputs
        ln1_out = self.sub_model1.predict(sequence_input, batch_size=1, verbose=0)
        ln3_out = self.sub_model2.predict(sequence_input, batch_size=1, verbose=0)

        # Extract attention matrices with return_attention_scores=True
        _, attn1_scores = self.mha1(ln1_out, ln1_out, return_attention_scores=True)  # (1, 4, 30, 30)
        _, attn2_scores = self.mha2(ln3_out, ln3_out, return_attention_scores=True)  # (1, 4, 30, 30)

        # Verification check: prediction after attention extraction
        prob_after = float(self.transformer_model.predict(sequence_input, batch_size=1, verbose=0)[0, 0])
        if abs(prob_before - prob_after) > 1e-6:
            logger.warning("Prediction shifted during attention extraction!")

        # Convert tensors to numpy arrays: shape (4, 30, 30) per layer
        layer_0_attn = attn1_scores.numpy()[0]  # (4, 30, 30)
        layer_1_attn = attn2_scores.numpy()[0]  # (4, 30, 30)

        # Layer 0 and Layer 1 mean attention across 4 heads: (30, 30)
        layer_0_mean = np.mean(layer_0_attn, axis=0)  # (30, 30)
        layer_1_mean = np.mean(layer_1_attn, axis=0)  # (30, 30)

        # Overall mean attention matrix across 2 layers and 4 heads: (30, 30)
        overall_attn_matrix = 0.5 * (layer_0_mean + layer_1_mean)  # (30, 30)

        # Temporal attention summary: mean attention received by key step j across query steps i
        temporal_weights_unnorm = np.mean(overall_attn_matrix, axis=0)  # (30,)
        total_weight_sum = float(np.sum(temporal_weights_unnorm))
        temporal_weights = (
            (temporal_weights_unnorm / total_weight_sum)
            if total_weight_sum > 1e-12 else np.full(30, 1.0 / 30.0)
        )

        timestamps = (
            df_seq_30["timestamp"].astype(str).tolist()
            if "timestamp" in df_seq_30.columns else [f"step_{i}" for i in range(30)]
        )

        # Build time step entries
        time_step_entries = []
        for step_idx in range(30):
            step_ts = timestamps[step_idx]
            weight_val = float(temporal_weights[step_idx])
            pct_val = float(weight_val * 100.0)

            time_step_entries.append({
                "step_index": step_idx,
                "timestamp": step_ts,
                "attention_weight": round(weight_val, 6),
                "attention_percent": round(pct_val, 2),
            })

        # Rank by attention weight descending
        time_step_entries_sorted = sorted(time_step_entries, key=lambda x: x["attention_weight"], reverse=True)
        top_attended_timesteps = time_step_entries_sorted[:top_n]

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
            "model_name": "Transformer",
            "patient_id": patient_id,
            "timestamp": timestamp,
            "model_output_explained": "Multi-Head Self-Attention temporal weights",
            "transformer_risk_score": round(prob_before, 4),
            "num_layers": self.num_layers,
            "num_heads_per_layer": self.num_heads,
            "sequence_length_steps": self.sequence_length,
            "raw_attention_dimensions": "[2, 4, 30, 30]",
            "top_attended_timesteps": top_attended_timesteps,
            "temporal_attention_sequence": time_step_entries,
            "layer_0_mean_attention": np.round(layer_0_mean, 4).tolist(),
            "layer_1_mean_attention": np.round(layer_1_mean, 4).tolist(),
            "overall_mean_attention_matrix": np.round(overall_attn_matrix, 4).tolist(),
            "forecasting_capability_status": (
                "UNSUPPORTED — The existing Transformer artifact is a single-output binary classifier "
                "for deterioration risk. Multi-horizon future vital forecasting requires a sequence-to-sequence "
                "or regression target and is not supported without model retraining."
            ),
            "safety_disclaimer": (
                "Transformer attention weights show how the model distributed attention "
                "across the input sequence. They do not establish clinical causation, "
                "diagnosis, treatment recommendations, or clinical importance. "
                "SYNTHETIC / ACADEMIC DEMO DATA — NOT FOR CLINICAL USE."
            )
        }

