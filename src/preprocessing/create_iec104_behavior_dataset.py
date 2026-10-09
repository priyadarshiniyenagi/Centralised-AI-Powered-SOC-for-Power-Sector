import pandas as pd
from pathlib import Path

# ============================================================
# CREATE BEHAVIORAL FEATURE DATASET
# ============================================================

INPUT_FILE = Path(
    "data/processed/IEC104/iec104_ml_ready.csv"
)

OUTPUT_FILE = Path(
    "data/processed/IEC104/iec104_behavior_ml_ready.csv"
)

print("=" * 70)
print("CREATING IEC-104 BEHAVIORAL FEATURE DATASET")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load ML-ready dataset
# ------------------------------------------------------------

print("\nLoading dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

# ------------------------------------------------------------
# 2. Remove network identifier features
# ------------------------------------------------------------

remove_columns = [
    "Src Port",
    "Dst Port"
]

print("\nRemoving identifier-related features:")

for column in remove_columns:
    if column in df.columns:
        print(f"  Removing: {column}")
        df = df.drop(columns=[column])
    else:
        print(f"  WARNING: {column} not found")

# ------------------------------------------------------------
# 3. Separate feature and label information
# ------------------------------------------------------------

if "Label" not in df.columns:
    raise ValueError("Label column not found!")

feature_columns = [
    column for column in df.columns
    if column != "Label"
]

# ------------------------------------------------------------
# 4. Check for missing/infinite values
# ------------------------------------------------------------

print("\nChecking data quality...")

missing_values = df[feature_columns].isna().sum().sum()

print(f"Missing values: {missing_values}")

# Check infinite values only in numeric columns
numeric_df = df[feature_columns].select_dtypes(include="number")

infinite_values = (
    numeric_df.isin([float("inf"), float("-inf")])
    .sum()
    .sum()
)

print(f"Infinite values: {infinite_values}")

# ------------------------------------------------------------
# 5. Dataset information
# ------------------------------------------------------------

print("\nFinal dataset:")
print(f"  Rows: {len(df):,}")
print(f"  Features: {len(feature_columns)}")
print(f"  Total columns: {len(df.columns)}")

print("\nClass distribution:")

class_counts = df["Label"].value_counts()

for label, count in class_counts.items():
    percentage = count / len(df) * 100
    print(f"  {label:<30} {count:>8,} ({percentage:>7.4f}%)")

# ------------------------------------------------------------
# 6. Save dataset
# ------------------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nDataset saved successfully:")
print(OUTPUT_FILE)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)