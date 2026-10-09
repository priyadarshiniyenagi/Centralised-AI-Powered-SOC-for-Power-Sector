import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    confusion_matrix,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# ============================================================
# IEC-104 TEMPORAL VALIDATION
# ============================================================

INPUT_FILE = Path(
    "data/processed/IEC104/iec104_combined.csv"
)

RESULT_DIR = Path(
    "results/metrics"
)

MODEL_DIR = Path(
    "saved_models"
)

print("=" * 70)
print("IEC-104 TEMPORAL / CAPTURE-AWARE VALIDATION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load dataset
# ------------------------------------------------------------

print("\nLoading dataset...")

df = pd.read_csv(INPUT_FILE)

# Parse timestamps
df["Timestamp"] = pd.to_datetime(
    df["Timestamp"],
    errors="coerce"
)

print(f"Total rows: {len(df):,}")
print(
    f"Time range: {df['Timestamp'].min()} "
    f"to {df['Timestamp'].max()}"
)

# ------------------------------------------------------------
# 2. Sort chronologically
# ------------------------------------------------------------

df = df.sort_values(
    "Timestamp"
).reset_index(drop=True)

# ------------------------------------------------------------
# 3. Display chronological class blocks
# ------------------------------------------------------------

print("\nChronological class blocks:")

class_blocks = (
    df.groupby("Label")["Timestamp"]
    .agg(["min", "max", "count"])
    .sort_values("min")
)

print(class_blocks)

# ------------------------------------------------------------
# 4. IMPORTANT:
#    We need a normal-only training period.
#
#    SANDI IEC-104 normal traffic occurs in a later capture.
#    Therefore, a strict chronological split cannot train
#    on normal traffic and then test earlier attack captures.
#
#    We therefore create a capture-aware evaluation where:
#    - training = normal traffic
#    - testing = attack traffic from separate captures
#
#    The normal training/test split is kept separate.
# ------------------------------------------------------------

normal_data = df[
    df["Label"] == "attackfree"
].copy()

attack_data = df[
    df["Label"] != "attackfree"
].copy()

print("\nNormal samples:")
print(len(normal_data))

print("\nAttack samples:")
print(len(attack_data))

# ------------------------------------------------------------
# 5. Split NORMAL capture temporally
# ------------------------------------------------------------

normal_data = normal_data.sort_values(
    "Timestamp"
).reset_index(drop=True)

normal_split = int(
    len(normal_data) * 0.80
)

train_normal = normal_data.iloc[
    :normal_split
].copy()

test_normal = normal_data.iloc[
    normal_split:
].copy()

print("\nNormal temporal split:")
print(
    f"Training normal : {len(train_normal)}"
)

print(
    f"Testing normal  : {len(test_normal)}"
)

# ------------------------------------------------------------
# 6. Feature selection
# ------------------------------------------------------------

# Timestamp is deliberately not used as a feature.

exclude_columns = [
    "Flow ID",
    "Src IP",
    "Dst IP",
    "Src Port",
    "Dst Port",
    "Timestamp",
    "Label",
    "Bwd PSH Flags",
    "Bwd URG Flags",
    "Fwd Bytes/Bulk Avg",
    "Fwd Packet/Bulk Avg",
    "Fwd Bulk Rate Avg"
]
feature_columns = [
    column
    for column in df.columns
    if column not in exclude_columns
]

X_train = train_normal[
    feature_columns
]

X_test_normal = test_normal[
    feature_columns
]

X_test_attack = attack_data[
    feature_columns
]

# ------------------------------------------------------------
# 7. Train Isolation Forest
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
# 8. Test
# ------------------------------------------------------------

X_test = pd.concat(
    [
        X_test_normal,
        X_test_attack
    ],
    ignore_index=True
)

y_test = np.concatenate(
    [
        np.zeros(len(X_test_normal), dtype=int),
        np.ones(len(X_test_attack), dtype=int)
    ]
)

print("\nTesting:")
print(
    f"Normal samples : {len(X_test_normal):,}"
)

print(
    f"Attack samples : {len(X_test_attack):,}"
)

scores = model.score_samples(
    X_test
)

# Use the same threshold established previously
THRESHOLD = -0.50

y_pred = (
    scores < THRESHOLD
).astype(int)

# ------------------------------------------------------------
# 9. Metrics
# ------------------------------------------------------------

accuracy = np.mean(
    y_pred == y_test
)

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

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\n" + "=" * 70)
print("TEMPORAL / CAPTURE-AWARE RESULTS")
print("=" * 70)

print(f"\nAccuracy           : {accuracy:.4f}")
print(f"Balanced Accuracy  : {balanced_accuracy:.4f}")
print(f"Precision          : {precision:.4f}")
print(f"Recall             : {recall:.4f}")
print(f"F1-Score           : {f1:.4f}")

print("\nConfusion Matrix:")
print(cm)

print("\nInterpretation:")
print("                 Predicted Normal   Predicted Anomaly")
print(
    f"Actual Normal       {cm[0,0]:>8}          {cm[0,1]:>8}"
)
print(
    f"Actual Attack       {cm[1,0]:>8}          {cm[1,1]:>8}"
)

# ------------------------------------------------------------
# 10. Attack-wise temporal results
# ------------------------------------------------------------

attack_results = []

attack_data = attack_data.copy()

attack_scores = model.score_samples(
    X_test_attack
)

attack_predictions = (
    attack_scores < THRESHOLD
).astype(int)

attack_data["Predicted_Anomaly"] = (
    attack_predictions
)

for attack_type, group in attack_data.groupby(
    "Label"
):

    total = len(group)

    detected = group[
        "Predicted_Anomaly"
    ].sum()

    missed = total - detected

    rate = detected / total

    attack_results.append(
        {
            "Attack Type": attack_type,
            "Total": total,
            "Detected": detected,
            "Missed": missed,
            "Detection Rate": rate
        }
    )

attack_results_df = pd.DataFrame(
    attack_results
).sort_values(
    "Detection Rate"
)

print("\n" + "=" * 70)
print("ATTACK-WISE TEMPORAL RESULTS")
print("=" * 70)

for _, row in attack_results_df.iterrows():

    print(
        f"{row['Attack Type']:<32}"
        f"Total: {int(row['Total']):>7,}   "
        f"Detected: {int(row['Detected']):>7,}   "
        f"Missed: {int(row['Missed']):>5,}   "
        f"Rate: {row['Detection Rate'] * 100:>7.2f}%"
    )

# ------------------------------------------------------------
# 11. Save results
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
            "F1-Score",
            "Threshold"
        ],
        "Value": [
            accuracy,
            balanced_accuracy,
            precision,
            recall,
            f1,
            THRESHOLD
        ]
    }
)

metrics_file = (
    RESULT_DIR /
    "iec104_temporal_validation_metrics.csv"
)

metrics.to_csv(
    metrics_file,
    index=False
)

attack_file = (
    RESULT_DIR /
    "iec104_temporal_attack_results.csv"
)

attack_results_df.to_csv(
    attack_file,
    index=False
)

cm_file = (
    RESULT_DIR /
    "iec104_temporal_confusion_matrix.csv"
)

pd.DataFrame(
    cm,
    index=[
        "Actual_Normal",
        "Actual_Attack"
    ],
    columns=[
        "Predicted_Normal",
        "Predicted_Attack"
    ]
).to_csv(
    cm_file
)

# ------------------------------------------------------------
# 12. Save model
# ------------------------------------------------------------

import joblib

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_DIR /
    "iec104_temporal_isolation_forest.joblib"
)

print("\nResults saved:")
print(metrics_file)
print(attack_file)
print(cm_file)

print("\n" + "=" * 70)
print("TEMPORAL VALIDATION COMPLETE")
print("=" * 70)