"""
=============================================================================
NeoNatal Watch AI — Train XGBoost Baseline
=============================================================================
WHAT  : Trains the XGBoost model on the engineered tabular features.
WHY   : Deep Learning (Phase 6) takes time to train and is complex to deploy. 
        XGBoost serves as an excellent, robust baseline that handles tabular
        data well. By using the rolling features we engineered in Phase 4,
        it can understand time-series context.
HOW   : Loads train/val/test_features.csv, drops non-feature columns,
        calculates class imbalance weights, trains the model, and evaluates.
=============================================================================
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

import json
import logging
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib

from ml.evaluation.metrics import evaluate_model

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("TrainXGBoost")

# Features to exclude from training (identifiers and labels)
EXCLUDE_COLS = [
    "timestamp", 
    "patient_id", 
    "deterioration_label", 
    "clinical_event", 
    "data_source", 
    "data_warning"
]

def load_data(data_dir: str):
    logger.info("Loading feature-engineered datasets...")
    train_df = pd.read_csv(os.path.join(data_dir, "train_features.csv"))
    val_df   = pd.read_csv(os.path.join(data_dir, "val_features.csv"))
    test_df  = pd.read_csv(os.path.join(data_dir, "test_features.csv"))
    
    # Identify feature columns
    feature_cols = [c for c in train_df.columns if c not in EXCLUDE_COLS]
    
    X_train = train_df[feature_cols].copy()
    y_train = train_df["deterioration_label"].copy()
    
    X_val = val_df[feature_cols].copy()
    y_val = val_df["deterioration_label"].copy()
    
    X_test = test_df[feature_cols].copy()
    y_test = test_df["deterioration_label"].copy()
    
    return X_train, y_train, X_val, y_val, X_test, y_test, feature_cols

def train_xgboost(X_train, y_train, X_val, y_val):
    """
    Initializes and trains the XGBoost model.
    Handles class imbalance using scale_pos_weight.
    """
    # Calculate class imbalance weight
    # scale_pos_weight = count(negative examples) / count(positive examples)
    n_pos = y_train.sum()
    n_neg = len(y_train) - n_pos
    
    # If there are no positive examples, default to 1 (prevent division by zero)
    # Since it's highly imbalanced, cap the weight to prevent over-predicting positives.
    scale_pos_weight = (n_neg / n_pos) if n_pos > 0 else 1.0
    capped_weight = min(scale_pos_weight, 50.0) # Cap at 50 to avoid exploding false positives
    
    logger.info(f"Class imbalance -> Positives: {n_pos}, Negatives: {n_neg}")
    logger.info(f"Calculated scale_pos_weight: {scale_pos_weight:.2f} (Capped at {capped_weight})")
    
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=capped_weight,
        eval_metric="aucpr",  # Optimize for PR-AUC!
        random_state=42,
        early_stopping_rounds=20,
        n_jobs=-1
    )
    
    logger.info("Training XGBoost model...")
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=10
    )
    
    return model

def main():
    print("=" * 60)
    print("Phase 5: Train XGBoost Baseline")
    print("=" * 60)
    
    data_dir = "data/processed"
    models_dir = "models"
    reports_dir = "reports/figures"
    
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    try:
        X_train, y_train, X_val, y_val, X_test, y_test, feature_cols = load_data(data_dir)
    except FileNotFoundError:
        logger.error("Feature files not found! Did you run Phase 4?")
        sys.exit(1)
        
    logger.info(f"Training on {len(X_train)} rows and {len(feature_cols)} features.")
    
    # Train
    model = train_xgboost(X_train, y_train, X_val, y_val)
    
    # Save model
    model_path = os.path.join(models_dir, "xgboost_model.json")
    model.save_model(model_path)
    logger.info(f"Model saved to {model_path}")
    
    # Save feature names for later interpretation
    with open(os.path.join(models_dir, "xgb_features.json"), "w") as f:
        json.dump(feature_cols, f)
        
    # Evaluate on Test Set
    logger.info("Evaluating model on TEST set...")
    y_test_probs = model.predict_proba(X_test)[:, 1]
    
    metrics = evaluate_model(
        y_true=y_test,
        y_probs=y_test_probs,
        threshold=0.5,
        model_name="XGBoost",
        save_dir=reports_dir
    )
    
    # Plot feature importance (Top 20)
    logger.info("Plotting feature importance...")
    importance = model.feature_importances_
    feat_imp = pd.DataFrame({"Feature": feature_cols, "Importance": importance})
    feat_imp = feat_imp.sort_values(by="Importance", ascending=False).head(20)
    
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 8))
    plt.barh(feat_imp["Feature"][::-1], feat_imp["Importance"][::-1], color="teal")
    plt.xlabel("Importance Score")
    plt.title("XGBoost - Top 20 Features")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "xgboost_feature_importance.png"), dpi=100)
    plt.close()
    
    print("=" * 60)
    print("Phase 5 Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

