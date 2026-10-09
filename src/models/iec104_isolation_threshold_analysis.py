import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    balanced_accuracy_score,
    confusion_matrix
)

# ============================================================
# IEC-104 ISOLATION FOREST THRESHOLD ANALYSIS
# ============================================================

DATA_DIR = Path(
    "data/processed/IEC104/anomaly"
)

RESULT_DIR = Path(
    "results/metrics"
)

print("=" * 70)
print("IEC-104 ISOLATION FOREST THRESHOLD ANALYSIS")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------

print("\nLoading datasets...")

train_normal = pd.read_csv(
    DATA_DIR / "anomaly_train_normal.csv"
)

test_normal = pd.read_csv(
    DATA_DIR / "anomaly_test_normal.csv"
)

test_attack = pd.read_csv(
    DATA_DIR / "anomaly_test_attack.csv"
)

# ------------------------------------------------------------
# 2. Select features
# ------------------------------------------------------------

exclude_columns = [
    "Label",
    "Anomaly"
]

feature_columns = [
    column
    for column in train_normal.columns
    if column not in exclude_columns
]

X_train = train_normal[feature_columns]

X_normal = test_normal[feature_columns]

X_attack = test_attack[feature_columns]

X_test = pd.concat(
    [
        X_normal,
        X_attack
    ],
    ignore_index=True
)

y_test = np.concatenate(
    [
        np.zeros(len(X_normal), dtype=int),
        np.ones(len(X_attack), dtype=int)
    ]
)

# ------------------------------------------------------------
# 3. Train model
# ------------------------------------------------------------

print("\nTraining Isolation Forest...")

model = IsolationForest(
    n_estimators=200,
    contamination="auto",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train)

# ------------------------------------------------------------
# 4. Obtain anomaly scores
# ------------------------------------------------------------

print("Calculating anomaly scores...")

# Isolation Forest score:
# More negative = more anomalous

scores = model.score_samples(X_test)

normal_scores = scores[:len(X_normal)]
attack_scores = scores[len(X_normal):]

print("\nScore ranges:")
print(
    f"Normal  : {normal_scores.min():.6f} "
    f"to {normal_scores.max():.6f}"
)

print(
    f"Attack  : {attack_scores.min():.6f} "
    f"to {attack_scores.max():.6f}"
)

# ------------------------------------------------------------
# 5. Define thresholds
# ------------------------------------------------------------

# More negative threshold = stricter
# Less negative threshold = more sensitive

thresholds = [
    -0.60,
    -0.58,
    -0.56,
    -0.54,
    -0.52,
    -0.50,
    -0.48,
    -0.46,
    -0.44,
    -0.42
]

results = []

print("\n" + "=" * 70)
print("THRESHOLD RESULTS")
print("=" * 70)

print(
    f"{'Threshold':>12}"
    f"{'Attack Recall':>16}"
    f"{'Normal Recall':>16}"
    f"{'False Positives':>17}"
    f"{'F1':>12}"
    f"{'Bal Accuracy':>16}"
)

for threshold in thresholds:

    # More negative than threshold = anomaly
    y_pred = (
        scores < threshold
    ).astype(int)

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    tn, fp, fn, tp = cm.ravel()

    attack_recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    normal_recall = tn / (tn + fp)

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    balanced_accuracy = balanced_accuracy_score(
        y_test,
        y_pred
    )

    results.append(
        {
            "Threshold": threshold,
            "Attack Recall": attack_recall,
            "Normal Recall": normal_recall,
            "False Positives": fp,
            "Missed Attacks": fn,
            "True Positives": tp,
            "Precision": precision,
            "F1": f1,
            "Balanced Accuracy": balanced_accuracy
        }
    )

    print(
        f"{threshold:>12.2f}"
        f"{attack_recall * 100:>15.2f}%"
        f"{normal_recall * 100:>15.2f}%"
        f"{fp:>17,}"
        f"{f1:>12.4f}"
        f"{balanced_accuracy:>15.4f}"
    )

# ------------------------------------------------------------
# 6. Save results
# ------------------------------------------------------------

results_df = pd.DataFrame(results)

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_file = (
    RESULT_DIR /
    "iec104_isolation_threshold_analysis.csv"
)

results_df.to_csv(
    output_file,
    index=False
)

print("\nThreshold analysis saved:")
print(output_file)

print("\n" + "=" * 70)
print("THRESHOLD ANALYSIS COMPLETE")
print("=" * 70)