import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# ============================================================
# IEC-104 ISOLATION FOREST ANOMALY DETECTOR
# ============================================================

DATA_DIR = Path(
    "data/processed/IEC104/anomaly"
)

MODEL_DIR = Path(
    "saved_models"
)

RESULT_DIR = Path(
    "results/metrics"
)

print("=" * 70)
print("IEC-104 ISOLATION FOREST ANOMALY DETECTOR")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load datasets
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

print(f"Normal training samples : {len(train_normal):,}")
print(f"Normal test samples     : {len(test_normal):,}")
print(f"Attack test samples     : {len(test_attack):,}")

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

X_normal_test = test_normal[feature_columns]

X_attack_test = test_attack[feature_columns]

# ------------------------------------------------------------
# 3. Combine test data
# ------------------------------------------------------------

X_test = pd.concat(
    [
        X_normal_test,
        X_attack_test
    ],
    ignore_index=True
)

# Ground truth:
# 0 = Normal
# 1 = Attack/Anomaly

y_test = np.concatenate(
    [
        np.zeros(len(X_normal_test), dtype=int),
        np.ones(len(X_attack_test), dtype=int)
    ]
)

print(f"\nNumber of features: {len(feature_columns)}")
print(f"Total test samples: {len(X_test):,}")

# ------------------------------------------------------------
# 4. Train Isolation Forest
# ------------------------------------------------------------

print("\nTraining Isolation Forest...")

model = IsolationForest(
    n_estimators=200,
    contamination="auto",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train)

print("Training completed.")

# ------------------------------------------------------------
# 5. Predict
# ------------------------------------------------------------

print("\nRunning anomaly detection...")

# Isolation Forest:
#   +1 = normal
#   -1 = anomaly

raw_predictions = model.predict(X_test)

# Convert:
# +1 -> 0 (Normal)
# -1 -> 1 (Attack)

y_pred = np.where(
    raw_predictions == -1,
    1,
    0
)

# ------------------------------------------------------------
# 6. Evaluate
# ------------------------------------------------------------

accuracy = np.mean(y_pred == y_test)

balanced_accuracy = balanced_accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

print("\n" + "=" * 70)
print("ANOMALY DETECTION RESULTS")
print("=" * 70)

print(f"\nAccuracy           : {accuracy:.4f}")
print(f"Balanced Accuracy  : {balanced_accuracy:.4f}")
print(f"Precision          : {precision:.4f}")
print(f"Recall             : {recall:.4f}")
print(f"F1-Score           : {f1:.4f}")

# ------------------------------------------------------------
# 7. Confusion matrix
# ------------------------------------------------------------

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\nConfusion Matrix:")
print(cm)

print("\nInterpretation:")
print("                 Predicted Normal   Predicted Anomaly")
print(f"Actual Normal       {cm[0,0]:>8}          {cm[0,1]:>8}")
print(f"Actual Attack       {cm[1,0]:>8}          {cm[1,1]:>8}")

# ------------------------------------------------------------
# 8. Classification report
# ------------------------------------------------------------

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Normal",
            "Attack"
        ],
        digits=4,
        zero_division=0
    )
)

# ------------------------------------------------------------
# 9. Count predictions
# ------------------------------------------------------------

normal_predictions = np.sum(y_pred == 0)
anomaly_predictions = np.sum(y_pred == 1)

print("Prediction distribution:")
print(f"  Predicted Normal  : {normal_predictions:,}")
print(f"  Predicted Anomaly : {anomaly_predictions:,}")

# ------------------------------------------------------------
# 10. Save model
# ------------------------------------------------------------

import joblib

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

model_path = MODEL_DIR / "iec104_isolation_forest.joblib"

joblib.dump(
    model,
    model_path
)

print(f"\nModel saved:")
print(model_path)

# ------------------------------------------------------------
# 11. Save metrics
# ------------------------------------------------------------

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

metrics = pd.DataFrame(
    {
        "Metric": [
            "Accuracy",
            "Balanced Accuracy",
            "Precision",
            "Recall",
            "F1-Score"
        ],
        "Value": [
            accuracy,
            balanced_accuracy,
            precision,
            recall,
            f1
        ]
    }
)

metrics_path = (
    RESULT_DIR /
    "iec104_isolation_forest_metrics.csv"
)

metrics.to_csv(
    metrics_path,
    index=False
)

# Save confusion matrix

cm_df = pd.DataFrame(
    cm,
    index=[
        "Actual_Normal",
        "Actual_Attack"
    ],
    columns=[
        "Predicted_Normal",
        "Predicted_Attack"
    ]
)

cm_path = (
    RESULT_DIR /
    "iec104_isolation_forest_confusion_matrix.csv"
)

cm_df.to_csv(
    cm_path
)

print(f"\nMetrics saved:")
print(metrics_path)

print(f"Confusion matrix saved:")
print(cm_path)

print("\n" + "=" * 70)
print("ISOLATION FOREST COMPLETE")
print("=" * 70)