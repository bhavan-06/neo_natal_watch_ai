"""
=============================================================================
NeoNatal Watch AI — Model Fusion (Ensemble)
=============================================================================
WHAT  : Combines predictions from all independent models into a single Risk Score.
WHY   : 
  - XGBoost provides high precision but low recall.
  - Deep Learning provides temporal context and balanced recall.
  - Autoencoder acts as a highly sensitive anomaly tripwire.
  Combining them creates a robust, clinical-grade ensemble score that is 
  better than any individual model alone.
=============================================================================
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import xgboost as xgb
import tensorflow as tf

logger = logging.getLogger("Fusion")

class FusionModel:
    def __init__(self, models_dir="models", weights=None):
        """
        Loads all trained models from the disk.
        """
        self.models_dir = models_dir
        
        # Default Weights if none provided
        if weights is None:
            self.weights = {
                "xgboost": 0.35,
                "cnn_lstm": 0.30,
                "autoencoder": 0.20,
                "transformer": 0.15
            }
        else:
            self.weights = weights
            
        # Normalize weights to ensure they sum to 1.0
        total = sum(self.weights.values())
        self.weights = {k: v / total for k, v in self.weights.items()}
        
        self._load_models()

    def _load_models(self):
        logger.info("Loading trained models for Fusion...")
        
        # 1. Load XGBoost
        xgb_path = os.path.join(self.models_dir, "xgboost_model.json")
        self.xgb_model = xgb.XGBClassifier()
        self.xgb_model.load_model(xgb_path)
        
        # Load the feature names XGBoost expects
        with open(os.path.join(self.models_dir, "xgb_features.json"), "r") as f:
            self.xgb_features = json.load(f)
            
        # 2. Load Deep Learning Models
        cnn_lstm_path = os.path.join(self.models_dir, "cnn_lstm.keras")
        self.cnn_lstm_model = tf.keras.models.load_model(cnn_lstm_path, compile=False)
        
        transformer_path = os.path.join(self.models_dir, "transformer.keras")
        self.transformer_model = tf.keras.models.load_model(transformer_path, compile=False)
        
        autoencoder_path = os.path.join(self.models_dir, "autoencoder.keras")
        self.autoencoder_model = tf.keras.models.load_model(autoencoder_path, compile=False)
        
        # Load Autoencoder Threshold
        ae_thresh_path = os.path.join(self.models_dir, "ae_threshold.json")
        with open(ae_thresh_path, "r") as f:
            self.ae_threshold = json.load(f)["anomaly_threshold"]
            
        logger.info("All models loaded successfully.")

    def predict_risk(self, flat_features: pd.DataFrame, sequence_features: np.ndarray, batch_size=64) -> np.ndarray:
        """
        Generates a unified risk score for the given data.
        
        flat_features: Tabular data for XGBoost (must contain the columns in self.xgb_features)
        sequence_features: 3D numpy array for Deep Learning models (n_samples, 30, 6)
        """
        assert len(flat_features) == len(sequence_features), "Mismatch in number of samples!"
        n_samples = len(flat_features)
        
        # 1. XGBoost Prediction
        # Ensure column order matches training
        X_xgb = flat_features[self.xgb_features]
        xgb_probs = self.xgb_model.predict_proba(X_xgb)[:, 1]
        
        # 2. CNN-LSTM Prediction
        cnn_lstm_probs = self.cnn_lstm_model.predict(sequence_features, batch_size=batch_size, verbose=0).flatten()
        
        # 3. Transformer Prediction
        transformer_probs = self.transformer_model.predict(sequence_features, batch_size=batch_size, verbose=0).flatten()
        
        # 4. Autoencoder Prediction
        ae_reconstruction = self.autoencoder_model.predict(sequence_features, batch_size=batch_size, verbose=0)
        ae_mse = np.mean(np.square(sequence_features - ae_reconstruction), axis=(1, 2))
        # Convert MSE to a pseudo-probability between 0 and 1 using the threshold
        # If mse == threshold, prob = 0.5. Cap at 1.0.
        ae_probs = np.clip(0.5 * (ae_mse / self.ae_threshold), 0.0, 1.0)
        
        # 5. Model Fusion (Weighted Average)
        fusion_probs = (
            (xgb_probs * self.weights["xgboost"]) +
            (cnn_lstm_probs * self.weights["cnn_lstm"]) +
            (ae_probs * self.weights["autoencoder"]) +
            (transformer_probs * self.weights["transformer"])
        )
        
        return fusion_probs, {
            "xgboost": xgb_probs,
            "cnn_lstm": cnn_lstm_probs,
            "autoencoder": ae_probs,
            "transformer": transformer_probs
        }

