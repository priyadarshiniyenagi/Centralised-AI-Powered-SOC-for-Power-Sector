import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path


# ============================================================
# IEC-104 TRAIN / TEST SPLIT
# ============================================================

print("\nIEC-104 TRAIN / TEST SPLIT")
print("=" * 70)


# ------------------------------------------------------------
# 1. Paths
# ------------------------------------------------------------

INPUT_FILE = Path("data/processed/IEC104/iec104_ml_ready.csv")

TRAIN_FILE = Path("data/processed/IEC104/iec104_train.csv")
TEST_FILE = Path("data/processed/IEC104/iec104_test.csv")


# ------------------------------------------------------------
# 2. Load dataset
# ------------------------------------------------------------

print("\nLoading ML-ready dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Dataset shape: {df.shape}")


# ------------------------------------------------------------
# 3. Separate features and target
# ------------------------------------------------------------

X = df.drop(columns=["Label"])
y = df["Label"]

print(f"Features: {X.shape[1]}")
print(f"Records : {X.shape[0]}")


# ------------------------------------------------------------
# 4. Display original class distribution
# ------------------------------------------------------------

print("\nOriginal class distribution:")
print(y.value_counts())


# ------------------------------------------------------------
# 5. Stratified train/test split
# ------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ------------------------------------------------------------
# 6. Reconstruct datasets
# ------------------------------------------------------------

train_df = X_train.copy()
train_df["Label"] = y_train.values

test_df = X_test.copy()
test_df["Label"] = y_test.values


# ------------------------------------------------------------
# 7. Save datasets
# ------------------------------------------------------------

train_df.to_csv(TRAIN_FILE, index=False)
test_df.to_csv(TEST_FILE, index=False)


# ------------------------------------------------------------
# 8. Display results
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SPLIT RESULTS")
print("=" * 70)

print(f"\nTraining records: {len(train_df)}")
print(f"Testing records : {len(test_df)}")

print("\nTraining class distribution:")
print(train_df["Label"].value_counts())

print("\nTesting class distribution:")
print(test_df["Label"].value_counts())


# ------------------------------------------------------------
# 9. Verify feature counts
# ------------------------------------------------------------

print("\nFeature verification:")
print(f"Training features: {train_df.shape[1] - 1}")
print(f"Testing features : {test_df.shape[1] - 1}")


# ------------------------------------------------------------
# 10. Final message
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TRAIN / TEST SPLIT CREATED SUCCESSFULLY")
print("=" * 70)

print(f"\nTraining file:")
print(TRAIN_FILE)

print(f"\nTesting file:")
print(TEST_FILE)