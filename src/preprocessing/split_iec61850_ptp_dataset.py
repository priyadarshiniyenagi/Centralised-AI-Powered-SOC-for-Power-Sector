import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "IEC61850"
    / "iec61850_ptp_ml_ready.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "IEC61850"
)

TRAIN_FILE = OUTPUT_DIR / "iec61850_ptp_train.csv"
TEST_FILE = OUTPUT_DIR / "iec61850_ptp_test.csv"


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

print("=" * 70)
print("IEC-61850 PTP TRAIN/TEST SPLIT")
print("=" * 70)

print("\nLoading ML-ready dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Total records: {len(df):,}")


# ---------------------------------------------------------
# Separate features and label
# ---------------------------------------------------------

X = df.drop(columns=["Label"])

y = df["Label"]


# ---------------------------------------------------------
# Stratified split
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ---------------------------------------------------------
# Recombine
# ---------------------------------------------------------

train_df = X_train.copy()
train_df["Label"] = y_train.values

test_df = X_test.copy()
test_df["Label"] = y_test.values


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

train_df.to_csv(
    TRAIN_FILE,
    index=False
)

test_df.to_csv(
    TEST_FILE,
    index=False
)


# ---------------------------------------------------------
# Display distributions
# ---------------------------------------------------------

print("\n" + "-" * 70)

print(f"Training records: {len(train_df):,}")
print(f"Testing records:  {len(test_df):,}")


print("\nTraining class distribution:")

print(
    train_df["Label"]
    .value_counts()
    .sort_index()
    .rename(
        index={
            0: "Normal",
            1: "PTP Attack"
        }
    )
)


print("\nTesting class distribution:")

print(
    test_df["Label"]
    .value_counts()
    .sort_index()
    .rename(
        index={
            0: "Normal",
            1: "PTP Attack"
        }
    )
)


print("\nTrain attack percentage:")
print(
    f"{(y_train == 1).mean() * 100:.4f}%"
)


print("\nTest attack percentage:")
print(
    f"{(y_test == 1).mean() * 100:.4f}%"
)


print("\nTraining dataset saved:")
print(TRAIN_FILE)

print("\nTesting dataset saved:")
print(TEST_FILE)


print("\n" + "=" * 70)
print("IEC-61850 PTP TRAIN/TEST SPLIT COMPLETE")
print("=" * 70)