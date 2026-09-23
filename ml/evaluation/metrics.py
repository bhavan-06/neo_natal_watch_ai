"""
=============================================================================
NeoNatal Watch AI — Evaluation Metrics
=============================================================================
Calculates and plots standard clinical machine learning metrics.
Crucial metrics for this highly imbalanced dataset:
- PR-AUC (Precision-Recall Area Under Curve)
- Precision, Recall, F1-Score
- ROC-AUC
=============================================================================
"""
import os
import json
import logging
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    precision_recall_curve,
    roc_curve,
    auc,
    confusion_matrix,
    classification_report,
    average_precision_score,
    roc_auc_score
)
import seaborn as sns

logger = logging.getLogger("Metrics")

def evaluate_model(
    y_true: np.ndarray, 
    y_probs: np.ndarray, 
    threshold: float = 0.5,
    model_name: str = "Model",
    save_dir: str = "reports/figures"
) -> dict:
    """
    Evaluates predictions against true labels and plots curves.
    """
    os.makedirs(save_dir, exist_ok=True)
    
    y_pred = (y_probs >= threshold).astype(int)
    
    # 1. Core Metrics
    pr_auc = average_precision_score(y_true, y_probs)
    roc_auc = roc_auc_score(y_true, y_probs)
    
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    
    metrics = {
        "pr_auc": float(pr_auc),
        "roc_auc": float(roc_auc),
        "precision": float(report["1"]["precision"]) if "1" in report else 0.0,
        "recall": float(report["1"]["recall"]) if "1" in report else 0.0,
        "f1": float(report["1"]["f1-score"]) if "1" in report else 0.0,
        "confusion_matrix": cm.tolist()
    }
    
    # 2. Plot PR Curve
    precision, recall, _ = precision_recall_curve(y_true, y_probs)
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color="crimson", lw=2, label=f"PR curve (AUC = {pr_auc:.3f})")
    plt.xlabel("Recall (Sensitivity)")
    plt.ylabel("Precision (PPV)")
    plt.title(f"{model_name} - Precision-Recall Curve")
    plt.legend(loc="upper right")
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(save_dir, f"{model_name.lower()}_pr_curve.png"), dpi=100)
    plt.close()
    
    # 3. Plot ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_probs)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color="steelblue", lw=2, label=f"ROC curve (AUC = {roc_auc:.3f})")
    plt.plot([0, 1], [0, 1], color="gray", lw=2, linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"{model_name} - ROC Curve")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(save_dir, f"{model_name.lower()}_roc_curve.png"), dpi=100)
    plt.close()
    
    # 4. Plot Confusion Matrix
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["Normal (0)", "Event (1)"], 
                yticklabels=["Normal (0)", "Event (1)"])
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title(f"{model_name} - Confusion Matrix (Threshold={threshold})")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"{model_name.lower()}_confusion_matrix.png"), dpi=100)
    plt.close()
    
    logger.info(f"--- {model_name} Evaluation ---")
    logger.info(f"PR-AUC:  {pr_auc:.4f}")
    logger.info(f"ROC-AUC: {roc_auc:.4f}")
    logger.info(f"Recall:  {metrics['recall']:.4f}")
    logger.info(f"Precision: {metrics['precision']:.4f}")
    logger.info(f"F1-Score:  {metrics['f1']:.4f}")
    
    return metrics

