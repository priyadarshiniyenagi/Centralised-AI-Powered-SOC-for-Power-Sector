import os
import pandas as pd
import numpy as np

INPUT_FILE = os.path.join(
    "data",
    "processed",
    "IEC104",
    "iec104_combined.csv"
)

OUTPUT_DIR = os.path.join(
    "data",
    "processed",
    "IEC104"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "iec104_ml_ready.csv"
)

print("\nCREATING IEC-104 ML-READY DATASET")
print("=" * 70)

# --------------------------------------------------
# 1. Load combined dataset
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print(f"\nOriginal shape: {df.shape}")

# --------------------------------------------------
# 2. Remove exact duplicate rows
# --------------------------------------------------

duplicate_count = df.duplicated().sum()

print(f"Duplicate rows found: {duplicate_count}")

if duplicate_count > 0:
    df = df.drop_duplicates().reset_index(drop=True)

print(f"Shape after duplicate removal: {df.shape}")

# --------------------------------------------------
# 3. Remove constant features
# --------------------------------------------------

constant_columns = [
    "Bwd PSH Flags",
    "Bwd URG Flags",
    "Fwd Bytes/Bulk Avg",
    "Fwd Packet/Bulk Avg",
    "Fwd Bulk Rate Avg"
]

print("\nRemoving constant features:")

for column in constant_columns:
    print(f"- {column}")

df = df.drop(
    columns=constant_columns
)

# --------------------------------------------------
# 4. Remove identifier columns from ML dataset
# --------------------------------------------------

identifier_columns = [
    "Flow ID",
    "Src IP",
    "Dst IP",
    "Timestamp"
]

print("\nRemoving identifier columns from ML dataset:")

for column in identifier_columns:
    print(f"- {column}")

df = df.drop(
    columns=identifier_columns
)

# --------------------------------------------------
# 5. Validate numerical values
# --------------------------------------------------

print("\nChecking numerical values...")

numeric_columns = df.select_dtypes(
    include=np.number
).columns

infinite_values = np.isinf(
    df[numeric_columns]
).sum().sum()

missing_values = df.isna().sum().sum()

print(f"Missing values  : {missing_values}")
print(f"Infinite values : {infinite_values}")

# --------------------------------------------------
# 6. Separate features and target
# --------------------------------------------------

X = df.drop(
    columns=["Label"]
)

y = df["Label"]

print("\nML dataset:")
print(f"Features : {X.shape[1]}")
print(f"Records  : {X.shape[0]}")

print("\nTarget classes:")
print(y.value_counts())

# --------------------------------------------------
# 7. Save ML-ready dataset
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSaved ML-ready dataset:")
print(OUTPUT_FILE)

# --------------------------------------------------
# 8. Save feature list
# --------------------------------------------------

FEATURE_FILE = os.path.join(
    OUTPUT_DIR,
    "iec104_ml_features.txt"
)

with open(
    FEATURE_FILE,
    "w",
    encoding="utf-8"
) as file:

    for feature in X.columns:
        file.write(feature + "\n")

print("\nSaved feature list:")
print(FEATURE_FILE)

print("\n" + "=" * 70)
print("ML-READY DATASET CREATED SUCCESSFULLY")
print("=" * 70)