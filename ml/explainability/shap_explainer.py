"""
ml/explainability/shap_explainer.py
------------------------------------
Authoritative SHAP Explainer service for the XGBoost structured risk model.

Phase N — Controlled SHAP Explainability Integration.
Uses native TreeSHAP computation via XGBoost booster for CPU-light,
100% exact, deterministic feature contribution scoring.

SAFETY NOTICE:
SHAP values explain how model features contributed to this prediction.
They do NOT represent clinical causation, diagnosis, treatment recommendations,
or clinical importance.
SYNTHETIC / ACADEMIC DEMO DATA — NOT FOR CLINICAL USE.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
import xgboost as xgb
from typing import Dict, Any, List, Optional

logger = logging.getLogger("SHAPExplainer")

MODELS_DIR_DEFAULT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models"))


class XGBoostShapExplainer:
    """
    Lightweight, deterministic SHAP explainer for XGBoost structured model.
    Reuses existing models/xgboost_model.json and models/xgb_features.json.
    Does NOT retrain, refit, or modify the model.
    """

    def __init__(self, models_dir: str = MODELS_DIR_DEFAULT):
        self.models_dir = models_dir
        self.xgb_model: Optional[xgb.XGBClassifier] = None
        self.feature_names: List[str] = []
        self._load_resources()

    def _load_resources(self):
        feat_path = os.path.join(self.models_dir, "xgb_features.json")
        model_path = os.path.join(self.models_dir, "xgboost_model.json")

        if not os.path.exists(feat_path):
            raise FileNotFoundError(f"Feature list not found at {feat_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"XGBoost model not found at {model_path}")

        with open(feat_path, "r") as f:
            self.feature_names = json.load(f)

        self.xgb_model = xgb.XGBClassifier()
        self.xgb_model.load_model(model_path)
        logger.info(f"Loaded XGBoost model with {len(self.feature_names)} features for SHAP explainability.")

    def explain_instance(
        self,
        df_row: pd.DataFrame,
        top_n: int = 5
    ) -> Dict[str, Any]:
        """
        Calculates exact TreeSHAP feature contributions for a single instance (1-row DataFrame).

        Args:
            df_row: DataFrame with 1 row containing engineered features.
            top_n: Number of top contributing features to return (default 5).

        Returns:
            Structured dictionary with top features, base value, direction, and safety metadata.
        """
        if self.xgb_model is None:
            raise RuntimeError("XGBoost model is not loaded.")

        if df_row.empty or len(df_row) != 1:
            raise ValueError("df_row must be a single-row DataFrame.")

        # Reorder and align features strictly to expected 102 features
        X_aligned = df_row.reindex(columns=self.feature_names).fillna(0.0)

        # Baseline prediction check: verify prediction before SHAP
        prob_before = float(self.xgb_model.predict_proba(X_aligned)[0, 1])

        # Native TreeSHAP computation via XGBoost C API (100% exact TreeSHAP)
        dmat = xgb.DMatrix(X_aligned)
        contribs = self.xgb_model.get_booster().predict(dmat, pred_contribs=True)

        if contribs.shape[1] != len(self.feature_names) + 1:
            raise ValueError(f"Unexpected SHAP contribs shape {contribs.shape}, expected 103 columns.")

        shap_values = contribs[0, :-1]
        base_value = float(contribs[0, -1])

        # Verification: prediction after SHAP calculation is identical
        prob_after = float(self.xgb_model.predict_proba(X_aligned)[0, 1])
        if abs(prob_before - prob_after) > 1e-6:
            logger.warning("Prediction shifted during SHAP calculation!")

        # Parse feature contributions
        feature_entries = []
        for idx, feat_name in enumerate(self.feature_names):
            val = float(X_aligned.iloc[0, idx])
            s_val = float(shap_values[idx])

            # Clean NaNs / Infs
            if not np.isfinite(val):
                val = 0.0
            if not np.isfinite(s_val):
                s_val = 0.0

            direction = "positive" if s_val > 0 else ("negative" if s_val < 0 else "neutral")

            feature_entries.append({
                "feature_name": feat_name,
                "feature_value": round(val, 4),
                "shap_value": round(s_val, 6),
                "absolute_shap_value": round(abs(s_val), 6),
                "direction": direction,
                "direction_symbol": "↑" if s_val > 0 else ("↓" if s_val < 0 else "•")
            })

        # Rank by absolute SHAP contribution descending
        feature_entries.sort(key=lambda x: x["absolute_shap_value"], reverse=True)
        top_features = feature_entries[:top_n]

        return {
            "model_name": "XGBoost",
            "model_output_explained": "Log-odds margin contribution (TreeSHAP)",
            "prediction_risk_score": round(prob_before, 4),
            "base_value": round(base_value, 6),
            "total_features_evaluated": len(self.feature_names),
            "top_features": top_features,
            "all_features": feature_entries,  # Available if client requests full list
            "safety_disclaimer": (
                "SHAP values explain how model features contributed to this prediction. "
                "They do not represent clinical causation, diagnosis, treatment recommendations, "
                "or clinical importance. SYNTHETIC / ACADEMIC DEMO DATA — NOT FOR CLINICAL USE."
            )
        }

