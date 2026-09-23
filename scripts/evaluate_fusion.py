"""
Phase 9: Evaluate Model Fusion
Runs the Fusion ensemble on the Test set and generates metrics.

Usage:
    python scripts/evaluate_fusion.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import pandas as pd
import logging
import matplotlib.pyplot as plt

from ml.models.fusion import FusionModel
from ml.evaluation.metrics import evaluate_model

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("Phase9")

def main():
    print("=" * 60)
    print("Phase 9: Evaluate Model Fusion (Ensemble)")
    print("=" * 60)
    
    data_dir = "data/processed"
    reports_dir = "reports/figures"
    
    logger.info("Loading Test Data (Flat and 3D)...")
    
    # Flat features for XGBoost
    test_flat = pd.read_csv(os.path.join(data_dir, "test_features.csv"))
    y_test_flat = test_flat["deterioration_label"].values
    
    # 3D Sequences for DL
    X_test_seq = np.load(os.path.join(data_dir, "X_test.npy"))
    y_test_seq = np.load(os.path.join(data_dir, "y_test.npy"))
    
    # Align flat features to match the sequence windows
    aligned_flat_list = []
    for pid, grp in test_flat.groupby("patient_id"):
        # For a window size of 30, the window labels were drawn from index 29 to n-2
        aligned_flat_list.append(grp.iloc[29:-1])
        
    test_flat_aligned = pd.concat(aligned_flat_list, ignore_index=True)
    y_test_flat = test_flat_aligned["deterioration_label"].values
    
    # Sanity check
    assert np.array_equal(y_test_flat, y_test_seq), "Labels mismatch between flat and seq test sets!"
    test_flat = test_flat_aligned
    
    # Initialize Fusion Model
    fusion = FusionModel(models_dir="models")
    
    logger.info(f"Fusion Weights: {fusion.weights}")
    logger.info("Generating predictions across all models on the Test set...")
    
    fusion_probs, individual_probs = fusion.predict_risk(flat_features=test_flat, sequence_features=X_test_seq)
    
    logger.info("Evaluating Fusion Model...")
    metrics = evaluate_model(
        y_true=y_test_seq,
        y_probs=fusion_probs,
        threshold=0.5,
        model_name="Fusion_Ensemble",
        save_dir=reports_dir
    )
    
    # Compare with individual models
    logger.info("Comparing PR-AUC across all models:")
    from sklearn.metrics import average_precision_score
    
    comparison = {}
    for name, probs in individual_probs.items():
        pr_auc = average_precision_score(y_test_seq, probs)
        comparison[name] = pr_auc
        logger.info(f"  - {name}: PR-AUC = {pr_auc:.4f}")
        
    logger.info(f"  - FUSION ENSEMBLE: PR-AUC = {metrics['pr_auc']:.4f}")
    
    # Plot Comparison Bar Chart
    plt.figure(figsize=(10, 6))
    names = list(comparison.keys()) + ["FUSION_ENSEMBLE"]
    scores = list(comparison.values()) + [metrics["pr_auc"]]
    colors = ['gray'] * 4 + ['crimson']
    
    bars = plt.bar(names, scores, color=colors)
    plt.title("PR-AUC Comparison: Individual Models vs Fusion Ensemble")
    plt.ylabel("Precision-Recall AUC")
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.4f}', va='bottom', ha='center')
        
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "fusion_comparison.png"), dpi=100)
    plt.close()
    
    print("=" * 60)
    print("Phase 9 Complete!")
    print("=" * 60)
    print("Proceed to Phase 11 (FastAPI Backend).")

if __name__ == "__main__":
    main()
