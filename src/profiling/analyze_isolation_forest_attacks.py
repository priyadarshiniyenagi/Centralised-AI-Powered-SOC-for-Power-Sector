import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest

# ============================================================
# ATTACK-WISE ISOLATION FOREST ANALYSIS
# ============================================================

DATA_DIR = Path(
    "data/processed/IEC104/anomaly"
)

RESULT_DIR = Path(
    "results/metrics"
)

print("=" * 70)
print("ATTACK-WISE ISOLATION FOREST ANALYSIS")
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

X_normal_test = test_normal[feature_columns]

X_attack_test = test_attack[feature_columns]

# ------------------------------------------------------------
# 3. Train Isolation Forest
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
# 4. Predict attacks
# ------------------------------------------------------------

print("Predicting attack samples...")

raw_predictions = model.predict(X_attack_test)

# Isolation Forest:
# +1 = normal
# -1 = anomaly

attack_predictions = np.where(
    raw_predictions == -1,
    1,
    0
)

test_attack = test_attack.copy()

test_attack["Predicted_Anomaly"] = attack_predictions

test_attack["Detected"] = (
    test_attack["Predicted_Anomaly"] == 1
)

# ------------------------------------------------------------
# 5. Attack-wise statistics
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("ATTACK-WISE RESULTS")
print("=" * 70)

results = []

for attack_type, group in test_attack.groupby("Label"):

    total = len(group)

    detected = group["Detected"].sum()

    missed = total - detected

    detection_rate = detected / total

    results.append(
        {
            "Attack Type": attack_type,
            "Total Samples": total,
            "Detected": detected,
            "Missed": missed,
            "Detection Rate": detection_rate
        }
    )

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "Detection Rate"
)

# Print formatted results

for _, row in results_df.iterrows():

    print(
        f"{row['Attack Type']:<32}"
        f"Total: {int(row['Total Samples']):>7,}   "
        f"Detected: {int(row['Detected']):>7,}   "
        f"Missed: {int(row['Missed']):>5,}   "
        f"Rate: {row['Detection Rate'] * 100:>7.2f}%"
    )

# ------------------------------------------------------------
# 6. Overall attack statistics
# ------------------------------------------------------------

total_attacks = len(test_attack)

total_detected = test_attack["Detected"].sum()

total_missed = total_attacks - total_detected

overall_detection_rate = (
    total_detected / total_attacks
)

print("\n" + "-" * 70)

print(
    f"Total attacks     : {total_attacks:,}"
)

print(
    f"Detected attacks  : {total_detected:,}"
)

print(
    f"Missed attacks    : {total_missed:,}"
)

print(
    f"Overall detection : "
    f"{overall_detection_rate * 100:.2f}%"
)

# ------------------------------------------------------------
# 7. Save attack-wise results
# ------------------------------------------------------------

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_file = (
    RESULT_DIR /
    "iec104_isolation_forest_attack_wise.csv"
)

results_df.to_csv(
    output_file,
    index=False
)

print("\nAttack-wise results saved:")
print(output_file)

# ------------------------------------------------------------
# 8. Save missed attack records
# ------------------------------------------------------------

missed_attacks = test_attack[
    test_attack["Detected"] == False
].copy()

missed_file = (
    RESULT_DIR /
    "iec104_isolation_forest_missed_attacks.csv"
)

missed_attacks.to_csv(
    missed_file,
    index=False
)

print("\nMissed attack records saved:")
print(missed_file)

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)