"""
=============================================================================
NeoNatal Watch AI — Train Autoencoder
=============================================================================
WHAT  : Trains the Autoencoder using ONLY NORMAL data (Unsupervised).
WHY   : By showing the model only healthy, stable vital signs, it learns
        to reconstruct them perfectly. When we feed it a deterioration event,
        it will output a high error rate. This allows us to detect anomalies
        without relying heavily on rare labeled event data.
=============================================================================
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import json
import logging
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

from ml.models.autoencoder import build_autoencoder_model
from ml.evaluation.metrics import evaluate_model

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("Train_Autoencoder")

def load_3d_data(data_dir: str):
    logger.info(f"Loading 3D window arrays from {data_dir}...")
    X_train = np.load(os.path.join(data_dir, "X_train.npy"))
    y_train = np.load(os.path.join(data_dir, "y_train.npy"))
    
    X_val = np.load(os.path.join(data_dir, "X_val.npy"))
    y_val = np.load(os.path.join(data_dir, "y_val.npy"))
    
    X_test = np.load(os.path.join(data_dir, "X_test.npy"))
    y_test = np.load(os.path.join(data_dir, "y_test.npy"))
    
    return X_train, y_train, X_val, y_val, X_test, y_test

def main():
    print("=" * 60)
    print("Phase 7: Train Autoencoder (Anomaly Detection)")
    print("=" * 60)
    
    data_dir = "data/processed"
    models_dir = "models"
    reports_dir = "reports/figures"
    
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    try:
        X_train, y_train, X_val, y_val, X_test, y_test = load_3d_data(data_dir)
    except FileNotFoundError:
        logger.error("NPY files not found! Did you run Phase 2?")
        sys.exit(1)
        
    # 1. Isolate Normal Data for Training
    # Autoencoders for anomaly detection are trained exclusively on "Normal" (0) data
    logger.info("Filtering training data to NORMAL (label=0) samples only...")
    X_train_normal = X_train[y_train == 0]
    X_val_normal = X_val[y_val == 0]
    
    logger.info(f"Training on {len(X_train_normal)} normal windows (discarded {len(y_train) - len(X_train_normal)} event windows)")
    
    # 2. Build Model
    sequence_length = X_train.shape[1]
    n_features = X_train.shape[2]
    
    model = build_autoencoder_model(
        sequence_length=sequence_length,
        n_features=n_features,
        learning_rate=0.001
    )
    
    model.summary(print_fn=logger.info)
    
    # 3. Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", 
            mode="min", 
            patience=5, 
            restore_best_weights=True,
            verbose=1
        )
    ]
    
    # 4. Train Model (X_train_normal mapped to X_train_normal)
    logger.info("Starting Unsupervised Training...")
    history = model.fit(
        X_train_normal, X_train_normal,
        validation_data=(X_val_normal, X_val_normal),
        epochs=30,
        batch_size=64,
        callbacks=callbacks,
        verbose=2
    )
    
    # 5. Save Model
    model_path = os.path.join(models_dir, "autoencoder.keras")
    model.save(model_path)
    logger.info(f"Autoencoder saved to {model_path}")
    
    # 6. Evaluate on Test Set
    logger.info("Evaluating Anomaly Detection on TEST set...")
    
    # Predict reconstruction
    X_test_pred = model.predict(X_test, batch_size=64)
    
    # Calculate Mean Squared Error per window
    # Shape of X is (samples, timesteps, features) -> mean across timesteps and features
    mse = np.mean(np.square(X_test - X_test_pred), axis=(1, 2))
    
    # Also calculate MSE on validation set to find a good threshold
    X_val_pred = model.predict(X_val, batch_size=64)
    val_mse = np.mean(np.square(X_val - X_val_pred), axis=(1, 2))
    
    # We set the anomaly threshold to the 95th percentile of validation normal errors
    val_normal_mse = val_mse[y_val == 0]
    threshold_value = np.percentile(val_normal_mse, 95)
    logger.info(f"Calculated 95th percentile threshold from normal validation data: {threshold_value:.5f}")
    
    # Save threshold
    with open(os.path.join(models_dir, "ae_threshold.json"), "w") as f:
        json.dump({"anomaly_threshold": float(threshold_value)}, f)
        
    # In order to use our standard `evaluate_model` tool (which expects probabilities [0,1] and a 0.5 threshold)
    # we will scale the MSE such that threshold_value == 0.5
    # y_probs = 0.5 * (mse / threshold_value)
    # We clip to [0, 1] to keep it as a pseudo-probability
    y_test_probs = np.clip(0.5 * (mse / threshold_value), 0.0, 1.0)
    
    metrics = evaluate_model(
        y_true=y_test,
        y_probs=y_test_probs,
        threshold=0.5,
        model_name="Autoencoder",
        save_dir=reports_dir
    )
    
    print("=" * 60)
    print("Phase 7 Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

