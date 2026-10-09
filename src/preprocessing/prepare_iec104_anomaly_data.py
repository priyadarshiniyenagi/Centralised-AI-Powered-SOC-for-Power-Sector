import pandas as pd
from pathlib import Path

# ============================================================
# PREPARE IEC-104 DATA FOR ANOMALY DETECTION
# ============================================================

INPUT_FILE = Path(
    "data/processed/IEC104/iec104_behavior_ml_ready.csv"
)

OUTPUT_DIR = Path(
    "data/processed/IEC104/anomaly"
)

print("=" * 70)
print("PREPARING IEC-104 ANOMALY-DETECTION DATA")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load behavioral dataset
# ------------------------------------------------------------

print("\nLoading dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Total rows: {len(df):,}")
print(f"Total columns: {len(df.columns)}")

# ------------------------------------------------------------
# 2. Create binary anomaly label
# ------------------------------------------------------------

# attackfree = normal
# every other class = attack/anomaly

df["Anomaly"] = (
    df["Label"] != "attackfree"
).astype(int)

print("\nBinary class distribution:")

normal_count = (df["Anomaly"] == 0).sum()
attack_count = (df["Anomaly"] == 1).sum()

print(f"  Normal  : {normal_count:,}")
print(f"  Anomaly : {attack_count:,}")

# ------------------------------------------------------------
# 3. Stratified 80/20 split
# ------------------------------------------------------------

from sklearn.model_selection import train_test_split

train_df, test_df = train_test_split(
    df,
    test_size=0.20,
    random_state=42,
    stratify=df["Anomaly"]
)

print("\nInitial 80/20 split:")
print(f"  Training rows: {len(train_df):,}")
print(f"  Testing rows : {len(test_df):,}")

# ------------------------------------------------------------
# 4. Training data for Isolation Forest
# ------------------------------------------------------------

# IMPORTANT:
# Only NORMAL traffic is allowed during training.

train_normal = train_df[
    train_df["Anomaly"] == 0
].copy()

print("\nIsolation Forest training data:")
print(f"  Normal training samples: {len(train_normal):,}")

# ------------------------------------------------------------
# 5. Test data
# ------------------------------------------------------------

test_normal = test_df[
    test_df["Anomaly"] == 0
].copy()

test_attack = test_df[
    test_df["Anomaly"] == 1
].copy()

print("\nTest data:")
print(f"  Normal samples : {len(test_normal):,}")
print(f"  Attack samples : {len(test_attack):,}")

# ------------------------------------------------------------
# 6. Remove labels from feature matrix
# ------------------------------------------------------------

feature_columns = [
    column
    for column in df.columns
    if column not in ["Label", "Anomaly"]
]

print("\nFeature information:")
print(f"  Number of features: {len(feature_columns)}")

X_train_normal = train_normal[feature_columns]

X_test_normal = test_normal[feature_columns]

X_test_attack = test_attack[feature_columns]

# ------------------------------------------------------------
# 7. Save datasets
# ------------------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

train_normal.to_csv(
    OUTPUT_DIR / "anomaly_train_normal.csv",
    index=False
)

test_normal.to_csv(
    OUTPUT_DIR / "anomaly_test_normal.csv",
    index=False
)

test_attack.to_csv(
    OUTPUT_DIR / "anomaly_test_attack.csv",
    index=False
)

print("\nFiles saved:")

print(
    OUTPUT_DIR / "anomaly_train_normal.csv"
)

print(
    OUTPUT_DIR / "anomaly_test_normal.csv"
)

print(
    OUTPUT_DIR / "anomaly_test_attack.csv"
)

print("\n" + "=" * 70)
print("ANOMALY DATA PREPARATION COMPLETE")
print("=" * 70)