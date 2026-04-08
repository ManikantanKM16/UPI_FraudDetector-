import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, roc_auc_score, confusion_matrix

def find_best_threshold(y_true, scores, target_recall=0.95):
    """Find threshold that achieves target recall with max precision."""
    precision, recall, thresholds = precision_recall_curve(y_true, scores)
    
    # Find thresholds where recall >= target
    valid_idx = np.where(recall >= target_recall)[0]
    
    if len(valid_idx) == 0:
        print(f"Cannot achieve {target_recall:.0%} recall. Best recall: {recall.max():.2%}")
        return thresholds[np.argmax(recall[:-1])]
    
    # Among those, pick highest precision
    best_idx = valid_idx[np.argmax(precision[valid_idx])]
    best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
    
    print(f"Best threshold: {best_threshold:.4f}")
    print(f"  Precision: {precision[best_idx]:.2%}")
    print(f"  Recall:    {recall[best_idx]:.2%}")
    print(f"  ROC-AUC:   {roc_auc_score(y_true, scores):.4f}")
    
    # Plot PR curve
    plt.figure(figsize=(8,5))
    plt.plot(recall, precision, 'b-', linewidth=2)
    plt.axvline(x=recall[best_idx], color='r', linestyle='--', label=f'Threshold={best_threshold:.3f}')
    plt.xlabel('Recall (Fraud Detection Rate)')
    plt.ylabel('Precision (Accuracy of Alerts)')
    plt.title('Precision-Recall Curve — UPI Fraud Detector')
    plt.legend()
    plt.savefig('evaluate/pr_curve.png', dpi=150, bbox_inches='tight')
    print("Saved PR curve to evaluate/pr_curve.png")
    
    return best_threshold

if __name__ == "__main__":
    import os; os.makedirs('evaluate', exist_ok=True)
    results = pd.read_csv('data/test_results.csv')
    best_t = find_best_threshold(
        results['y_true'],
        results['ensemble_score'],
        target_recall=0.95
    )
    # Save for use in API
    import json
    with open('models/saved/threshold.json', 'w') as f:
        json.dump({'threshold': float(best_t)}, f)