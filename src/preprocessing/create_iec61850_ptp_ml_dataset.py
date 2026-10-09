import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

NORMAL_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "IEC61850"
    / "capture61850-attackfree_PTP.csv"
)

ATTACK_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "IEC61850"
    / "capture61850-ptpattack.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "IEC61850"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "iec61850_ptp_ml_ready.csv"


# ---------------------------------------------------------
# Selected behavioral features
# ---------------------------------------------------------

FEATURES = [
    "frame.len",
    "frame.cap_len",
    "frame.time_delta",
    "frame.time_relative",

    "ptp.v2.messagelength",
    "ptp.v2.sequenceid",
    "ptp.v2.domainnumber",
    "ptp.v2.correction.ns",
    "ptp.v2.correction.subns",
    "ptp.v2.sourceportid",
    "ptp.v2.versionptp",

    "goose.length",
    "goose.sqNum",
    "goose.stNum",
    "goose.confRev",
]


print("=" * 70)
print("IEC-61850 PTP ML DATASET CREATION")
print("=" * 70)


# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------

print("\nLoading normal PTP dataset...")

normal = pd.read_csv(
    NORMAL_FILE,
    low_memory=False
)

print(f"Normal records: {len(normal):,}")


print("\nLoading PTP attack dataset...")

attack = pd.read_csv(
    ATTACK_FILE,
    low_memory=False
)

print(f"Attack records: {len(attack):,}")


# ---------------------------------------------------------
# Verify features
# ---------------------------------------------------------

missing_features = [
    feature
    for feature in FEATURES
    if feature not in normal.columns
    or feature not in attack.columns
]

if missing_features:

    print("\nERROR: Missing features:")
    for feature in missing_features:
        print(f"  - {feature}")

    raise ValueError("Required features are missing.")


# ---------------------------------------------------------
# Select features
# ---------------------------------------------------------

normal_data = normal[FEATURES].copy()
attack_data = attack[FEATURES].copy()


# ---------------------------------------------------------
# Create labels
# ---------------------------------------------------------

normal_data["Label"] = 0
attack_data["Label"] = 1


# ---------------------------------------------------------
# Combine datasets
# ---------------------------------------------------------

combined = pd.concat(
    [normal_data, attack_data],
    ignore_index=True
)


# ---------------------------------------------------------
# Clean numeric data
# ---------------------------------------------------------

for column in FEATURES:

    combined[column] = pd.to_numeric(
        combined[column],
        errors="coerce"
    )


# Replace infinite values

combined = combined.replace(
    [float("inf"), float("-inf")],
    pd.NA
)


# ---------------------------------------------------------
# Missing-value handling
# ---------------------------------------------------------

missing_before = combined[FEATURES].isna().sum().sum()

print(f"\nMissing feature values before filling: {missing_before:,}")


for column in FEATURES:

    median_value = combined[column].median()

    combined[column] = combined[column].fillna(
        median_value
    )


missing_after = combined[FEATURES].isna().sum().sum()

print(
    f"Missing feature values after filling: "
    f"{missing_after:,}"
)


# ---------------------------------------------------------
# Remove duplicate rows
# ---------------------------------------------------------

duplicates = combined.duplicated().sum()

print(f"Duplicate rows: {duplicates:,}")

combined = combined.drop_duplicates().reset_index(drop=True)


# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

combined.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# Final summary
# ---------------------------------------------------------

print("\n" + "-" * 70)

print(f"Final records: {len(combined):,}")
print(f"Features: {len(FEATURES):,}")

print("\nClass distribution:")

print(
    combined["Label"]
    .value_counts()
    .sort_index()
    .rename(
        index={
            0: "Normal",
            1: "PTP Attack"
        }
    )
)


print("\nFinal columns:")

for column in combined.columns:
    print(f"  {column}")


print("\nDataset saved:")
print(OUTPUT_FILE)


print("\n" + "=" * 70)
print("IEC-61850 PTP ML DATASET CREATION COMPLETE")
print("=" * 70)