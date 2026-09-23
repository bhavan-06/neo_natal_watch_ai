"""
=============================================================================
NeoNatal Watch AI — Train CNN-LSTM Deep Learning Model
=============================================================================
WHAT  : Trains the Hybrid CNN-LSTM model on 3D sequence tensors.
WHY   : Deep Learning captures complex time-series interactions across
        multiple variables without needing manually engineered features
        (unlike XGBoost).
HOW   : Loads .npy files from Phase 2, calculates class weights to handle
        the 0.29% event rate, and uses EarlyStopping to prevent overfitting.
=============================================================================
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import logging
import tensorflow as tf

from ml.models.cnn_lstm import build_cnn_lstm_model
from ml.evaluation.metrics import evaluate_model

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("Train_CNN_LSTM")

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
    print("Phase 6: Train CNN-LSTM Deep Learning Model")
    print("=" * 60)
    
    data_dir = "data/processed"
    models_dir = "models"
    reports_dir = "reports/figures"
    
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    # 1. Load Data
    try:
        X_train, y_train, X_val, y_val, X_test, y_test = load_3d_data(data_dir)
    except FileNotFoundError:
        logger.error("NPY files not found! Did you run Phase 2?")
        sys.exit(1)
        
    logger.info(f"Training shape: X={X_train.shape}, y={y_train.shape}")
    
    # 2. Handle Class Imbalance
    n_pos = y_train.sum()
    n_neg = len(y_train) - n_pos
    
    # Calculate weights. We cap the positive weight so gradients don't explode.
    weight_for_0 = 1.0
    weight_for_1 = min(n_neg / n_pos, 50.0) if n_pos > 0 else 1.0
    
    class_weight = {
        0: weight_for_0,
        1: weight_for_1
    }
    logger.info(f"Class Weights mapping: {class_weight}")
    
    # 3. Build Model
    sequence_length = X_train.shape[1]
    n_features = X_train.shape[2]
    
    model = build_cnn_lstm_model(
        sequence_length=sequence_length,
        n_features=n_features,
        learning_rate=0.001
    )
    
    model.summary(print_fn=logger.info)
    
    # 4. Setup Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_pr_auc", 
            mode="max",           # We want to maximize PR-AUC
            patience=10,          # Stop if it doesn't improve for 10 epochs
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", 
            factor=0.5, 
            patience=5, 
            min_lr=1e-5,
            verbose=1
        )
    ]
    
    # 5. Train Model
    logger.info("Starting training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=50,
        batch_size=64,
        class_weight=class_weight,
        callbacks=callbacks,
        verbose=2
    )
    
    # 6. Save Model
    model_path = os.path.join(models_dir, "cnn_lstm.keras")
    model.save(model_path)
    logger.info(f"Model saved to {model_path}")
    
    # 7. Evaluate on Test Set
    logger.info("Evaluating model on TEST set...")
    # Keras predict returns shape (n, 1), we flatten it to (n,)
    y_test_probs = model.predict(X_test, batch_size=64).flatten()
    
    metrics = evaluate_model(
        y_true=y_test,
        y_probs=y_test_probs,
        threshold=0.5,
        model_name="CNN_LSTM",
        save_dir=reports_dir
    )
    
    print("=" * 60)
    print("Phase 6 Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

