import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "IEC61850"
    / "iec61850_ptp_ml_ready.csv"
)


print("=" * 70)
print("IEC-61850 PTP ML DATASET QUALITY CHECK")
print("=" * 70)


df = pd.read_csv(INPUT_FILE)

print(f"\nRecords: {len(df):,}")
print(f"Columns: {len(df.columns):,}")


features = [
    column
    for column in df.columns
    if column != "Label"
]


print("\nMissing values by feature:")
print("-" * 70)

missing = df[features].isna().sum()

missing = missing[missing > 0].sort_values(
    ascending=False
)

print(missing.to_string())


print("\n" + "-" * 70)

print("\nMissing percentage by feature:")

missing_percent = (
    df[features]
    .isna()
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print(missing_percent.to_string())


print("\n" + "-" * 70)

print("\nFeatures with all values missing:")

all_missing = [
    column
    for column in features
    if df[column].isna().all()
]

if all_missing:
    for column in all_missing:
        print(f"  {column}")
else:
    print("None")


print("\n" + "-" * 70)

print("\nData types:")

print(df.dtypes.to_string())


print("\n" + "-" * 70)

print("\nClass distribution:")

print(
    df["Label"]
    .value_counts()
    .rename(
        index={
            0: "Normal",
            1: "PTP Attack"
        }
    )
)


print("\n" + "=" * 70)
print("QUALITY CHECK COMPLETE")
print("=" * 70)