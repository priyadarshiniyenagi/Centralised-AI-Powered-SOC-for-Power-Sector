import os
import pandas as pd

DATA_DIR = os.path.join("data", "raw", "IEC104")

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

print("\nIEC-104 FEATURE INSPECTION")
print("=" * 80)

# Read only one representative file to inspect the common schema
file_path = os.path.join(DATA_DIR, files[0])

df = pd.read_csv(file_path)

print(f"\nFile: {files[0]}")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\nCOLUMN NAMES")
print("=" * 80)

for i, column in enumerate(df.columns, start=1):
    print(f"{i:3}. {column}")

print("\nDATA TYPES")
print("=" * 80)

for column in df.columns:
    print(f"{column:50} {df[column].dtype}")

print("\nSAMPLE DATA")
print("=" * 80)

print(df.head(5).to_string())

print("\nUNIQUE VALUES FOR NON-NUMERICAL COLUMNS")
print("=" * 80)

categorical_columns = df.select_dtypes(exclude="number").columns

for column in categorical_columns:
    print(f"\n{column}")
    print(df[column].value_counts().head(20))

print("\nNUMERICAL FEATURE SUMMARY")
print("=" * 80)

numeric_columns = df.select_dtypes(include="number").columns

print(
    df[numeric_columns]
    .describe()
    .transpose()
    .to_string()
)

print("\nFEATURE INSPECTION COMPLETED")