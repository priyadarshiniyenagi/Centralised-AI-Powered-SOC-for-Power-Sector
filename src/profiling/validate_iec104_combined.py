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
    "results",
    "profiling"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("\nIEC-104 COMBINED DATASET VALIDATION")
print("=" * 80)

# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print(f"\nRows    : {len(df):,}")
print(f"Columns : {len(df.columns):,}")

# --------------------------------------------------
# 1. Missing values
# --------------------------------------------------

print("\n" + "=" * 80)
print("1. MISSING VALUES")
print("=" * 80)

missing = df.isna().sum()

missing = missing[missing > 0].sort_values(
    ascending=False
)

if len(missing) == 0:
    print("No missing values found.")
else:
    print(missing)

# --------------------------------------------------
# 2. Infinite values
# --------------------------------------------------

print("\n" + "=" * 80)
print("2. INFINITE VALUES")
print("=" * 80)

numeric_df = df.select_dtypes(include=np.number)

infinite_counts = np.isinf(numeric_df).sum()

infinite_counts = infinite_counts[
    infinite_counts > 0
]

if len(infinite_counts) == 0:
    print("No infinite values found.")
else:
    print(infinite_counts)

# --------------------------------------------------
# 3. Duplicate rows
# --------------------------------------------------

print("\n" + "=" * 80)
print("3. DUPLICATE ROWS")
print("=" * 80)

duplicate_count = df.duplicated().sum()

print(f"Duplicate rows: {duplicate_count:,}")

# --------------------------------------------------
# 4. Constant columns
# --------------------------------------------------

print("\n" + "=" * 80)
print("4. CONSTANT COLUMNS")
print("=" * 80)

constant_columns = []

for column in df.columns:

    unique_count = df[column].nunique(
        dropna=False
    )

    if unique_count <= 1:
        constant_columns.append(column)

print(f"Number of constant columns: {len(constant_columns)}")

for column in constant_columns:
    print(f"- {column}")

# --------------------------------------------------
# 5. Data types
# --------------------------------------------------

print("\n" + "=" * 80)
print("5. DATA TYPES")
print("=" * 80)

print(df.dtypes.value_counts())

# --------------------------------------------------
# 6. Numerical / non-numerical columns
# --------------------------------------------------

print("\n" + "=" * 80)
print("6. FEATURE TYPES")
print("=" * 80)

numeric_columns = df.select_dtypes(
    include=np.number
).columns.tolist()

non_numeric_columns = df.select_dtypes(
    exclude=np.number
).columns.tolist()

print(f"\nNumerical columns: {len(numeric_columns)}")

for column in numeric_columns:
    print(f"- {column}")

print(f"\nNon-numerical columns: {len(non_numeric_columns)}")

for column in non_numeric_columns:
    print(f"- {column}")

# --------------------------------------------------
# 7. Unique-value count
# --------------------------------------------------

print("\n" + "=" * 80)
print("7. UNIQUE VALUE COUNTS")
print("=" * 80)

unique_counts = (
    df.nunique(dropna=False)
    .sort_values()
)

print(unique_counts.to_string())

# Save unique counts
unique_file = os.path.join(
    OUTPUT_DIR,
    "iec104_unique_counts.csv"
)

unique_counts.to_csv(
    unique_file,
    header=["unique_count"]
)

# --------------------------------------------------
# 8. Correlation analysis
# --------------------------------------------------

print("\n" + "=" * 80)
print("8. HIGH CORRELATION ANALYSIS")
print("=" * 80)

# Exclude Label
feature_numeric = df[
    numeric_columns
].copy()

correlation_matrix = feature_numeric.corr()

high_correlations = []

columns = correlation_matrix.columns

for i in range(len(columns)):

    for j in range(i + 1, len(columns)):

        correlation = correlation_matrix.iloc[i, j]

        if abs(correlation) >= 0.95:

            high_correlations.append(
                (
                    columns[i],
                    columns[j],
                    correlation
                )
            )

high_corr_df = pd.DataFrame(
    high_correlations,
    columns=[
        "Feature_1",
        "Feature_2",
        "Correlation"
    ]
)

high_corr_df = high_corr_df.sort_values(
    "Correlation",
    key=lambda x: x.abs(),
    ascending=False
)

print(
    f"Highly correlated feature pairs "
    f"(absolute correlation >= 0.95): "
    f"{len(high_corr_df)}"
)

if len(high_corr_df) > 0:
    print(high_corr_df.to_string(index=False))

# Save
correlation_file = os.path.join(
    OUTPUT_DIR,
    "iec104_high_correlations.csv"
)

high_corr_df.to_csv(
    correlation_file,
    index=False
)

# --------------------------------------------------
# 9. Save validation summary
# --------------------------------------------------

summary_file = os.path.join(
    OUTPUT_DIR,
    "iec104_validation_summary.txt"
)

with open(
    summary_file,
    "w",
    encoding="utf-8"
) as file:

    file.write("IEC-104 COMBINED DATASET VALIDATION\n")
    file.write("=" * 60 + "\n\n")

    file.write(
        f"Rows: {len(df):,}\n"
    )

    file.write(
        f"Columns: {len(df.columns):,}\n"
    )

    file.write(
        f"Duplicate rows: {duplicate_count:,}\n"
    )

    file.write(
        f"Constant columns: {len(constant_columns)}\n"
    )

    file.write(
        f"Numerical columns: {len(numeric_columns)}\n"
    )

    file.write(
        f"Non-numerical columns: {len(non_numeric_columns)}\n"
    )

print("\n" + "=" * 80)
print("VALIDATION COMPLETED")
print("=" * 80)

print("\nResults saved in:")
print(OUTPUT_DIR)