import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest

# ============================================================
# ANALYZE MISSED NTP-DDoS ATTACKS
# ============================================================

DATA_DIR = Path(
    "data/processed/IEC104/anomaly"
)

RESULT_DIR = Path(
    "results/metrics"
)

print("=" * 70)
print("NTP-DDoS MISSED-ATTACK ANALYSIS")
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

# ------------------------------------------------------------
# 2. Select numerical behavioral features
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

# ------------------------------------------------------------
# 3. Train same Isolation Forest
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
# 4. Select NTP-DDoS test samples
# ------------------------------------------------------------

ntpddos = test_attack[
    test_attack["Label"] == "ntpddosattack"
].copy()

print(
    f"\nNTP-DDoS test samples: {len(ntpddos):,}"
)

# ------------------------------------------------------------
# 5. Predict NTP-DDoS samples
# ------------------------------------------------------------

ntp_predictions = model.predict(
    ntpddos[feature_columns]
)

ntpddos["Predicted_Anomaly"] = np.where(
    ntp_predictions == -1,
    1,
    0
)

ntpddos["Detection_Status"] = np.where(
    ntpddos["Predicted_Anomaly"] == 1,
    "Detected",
    "Missed"
)

detected = ntpddos[
    ntpddos["Detection_Status"] == "Detected"
].copy()

missed = ntpddos[
    ntpddos["Detection_Status"] == "Missed"
].copy()

print(f"Detected NTP-DDoS: {len(detected):,}")
print(f"Missed NTP-DDoS  : {len(missed):,}")

# ------------------------------------------------------------
# 6. Obtain anomaly scores
# ------------------------------------------------------------

# More negative = more anomalous
ntpddos["Anomaly_Score"] = model.score_samples(
    ntpddos[feature_columns]
)

detected["Anomaly_Score"] = model.score_samples(
    detected[feature_columns]
)

missed["Anomaly_Score"] = model.score_samples(
    missed[feature_columns]
)

print("\nAnomaly score statistics:")

print(
    f"Detected mean score : "
    f"{detected['Anomaly_Score'].mean():.6f}"
)

print(
    f"Missed mean score   : "
    f"{missed['Anomaly_Score'].mean():.6f}"
)

print(
    f"Detected minimum    : "
    f"{detected['Anomaly_Score'].min():.6f}"
)

print(
    f"Missed minimum      : "
    f"{missed['Anomaly_Score'].min():.6f}"
)

# ------------------------------------------------------------
# 7. Compare feature statistics
# ------------------------------------------------------------

print("\nCalculating feature differences...")

normal_means = train_normal[
    feature_columns
].mean()

detected_means = detected[
    feature_columns
].mean()

missed_means = missed[
    feature_columns
].mean()

# Difference between missed NTP-DDoS and normal traffic
normal_difference = (
    (missed_means - normal_means)
    .abs()
)

# Difference between detected and missed NTP-DDoS
detection_difference = (
    (detected_means - missed_means)
    .abs()
)

comparison = pd.DataFrame(
    {
        "Normal_Mean": normal_means,
        "Detected_NTPDDoS_Mean": detected_means,
        "Missed_NTPDDoS_Mean": missed_means,
        "Abs_Difference_Missed_vs_Normal":
            normal_difference,
        "Abs_Difference_Detected_vs_Missed":
            detection_difference
    }
)

# ------------------------------------------------------------
# 8. Rank features
# ------------------------------------------------------------

comparison_normal = comparison.sort_values(
    "Abs_Difference_Missed_vs_Normal",
    ascending=False
)

comparison_detection = comparison.sort_values(
    "Abs_Difference_Detected_vs_Missed",
    ascending=False
)

print("\n" + "=" * 70)
print("TOP FEATURES DIFFERENT FROM NORMAL TRAFFIC")
print("=" * 70)

print(
    comparison_normal.head(15).to_string()
)

print("\n" + "=" * 70)
print("TOP FEATURES DIFFERENT BETWEEN DETECTED AND MISSED NTP-DDoS")
print("=" * 70)

print(
    comparison_detection.head(15).to_string()
)

# ------------------------------------------------------------
# 9. Save complete feature comparison
# ------------------------------------------------------------

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

comparison_file = (
    RESULT_DIR /
    "ntpddos_feature_comparison.csv"
)

comparison.to_csv(
    comparison_file
)

# ------------------------------------------------------------
# 10. Save missed NTP-DDoS records
# ------------------------------------------------------------

missed_file = (
    RESULT_DIR /
    "ntpddos_missed_records.csv"
)

missed.to_csv(
    missed_file,
    index=False
)

# ------------------------------------------------------------
# 11. Save detected NTP-DDoS records
# ------------------------------------------------------------

detected_file = (
    RESULT_DIR /
    "ntpddos_detected_records.csv"
)

detected.to_csv(
    detected_file,
    index=False
)

print("\nFiles saved:")

print(comparison_file)
print(missed_file)
print(detected_file)

print("\n" + "=" * 70)
print("NTP-DDoS ANALYSIS COMPLETE")
print("=" * 70)