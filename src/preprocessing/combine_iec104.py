import os
import pandas as pd

DATA_DIR = os.path.join("data", "raw", "IEC104")
OUTPUT_DIR = os.path.join("data", "processed", "IEC104")

os.makedirs(OUTPUT_DIR, exist_ok=True)

files = [
    "capture104-attackfree.csv",
    "capture104-dosattack.csv",
    "capture104-floodattack.csv",
    "capture104-fuzzyattack.csv",
    "capture104-iec104starvationattack.csv",
    "capture104-mitmattack.csv",
    "capture104-ntpddosattack.csv",
    "capture104-portscanattack.csv"
]

dataframes = []

print("\nCOMBINING IEC-104 DATASETS")
print("=" * 70)

for filename in files:

    file_path = os.path.join(DATA_DIR, filename)

    print(f"\nReading: {filename}")

    df = pd.read_csv(file_path)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    dataframes.append(df)


# Combine all datasets
combined_df = pd.concat(dataframes, ignore_index=True)

print("\n" + "=" * 70)
print("COMBINED DATASET")
print("=" * 70)

print(f"Total rows    : {len(combined_df):,}")
print(f"Total columns : {len(combined_df.columns):,}")

print("\nClass distribution:")
print(combined_df["Label"].value_counts())

print("\nClass distribution (%):")
print(
    (combined_df["Label"].value_counts(normalize=True) * 100)
    .round(4)
)

# Check duplicate rows
duplicates = combined_df.duplicated().sum()

print(f"\nDuplicate rows: {duplicates:,}")

# Save combined dataset
output_file = os.path.join(
    OUTPUT_DIR,
    "iec104_combined.csv"
)

combined_df.to_csv(output_file, index=False)

print("\nSaved combined dataset:")
print(output_file)

print("\nCOMBINATION COMPLETED")