import os
import pandas as pd

# ============================================================
# IEC 104 DATASET PROFILING
# This script ONLY analyzes the datasets.
# It does NOT modify the original CSV files.
# ============================================================

DATA_DIR = os.path.join(
    "data",
    "raw",
    "IEC104"
)

OUTPUT_DIR = os.path.join(
    "results",
    "profiling"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def profile_dataset(file_path):
    """
    Profile one IEC 104 CSV dataset.
    """

    print("\n" + "=" * 70)
    print(f"FILE: {os.path.basename(file_path)}")
    print("=" * 70)

    # Read the dataset
    df = pd.read_csv(file_path)

    print(f"Rows    : {df.shape[0]:,}")
    print(f"Columns : {df.shape[1]:,}")

    # --------------------------------------------------------
    # Label information
    # --------------------------------------------------------

    if "Label" in df.columns:
        print("\nLabel distribution:")
        print(df["Label"].value_counts(dropna=False))

    else:
        print("\nWARNING: 'Label' column not found.")

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print("\nData types:")
    print(df.dtypes.value_counts())

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing = df.isna().sum()

    missing_percentage = (
        missing / len(df) * 100
    ).sort_values(ascending=False)

    missing_table = pd.DataFrame({
        "missing_count": missing,
        "missing_percentage": missing_percentage
    })

    missing_table = missing_table[
        missing_table["missing_count"] > 0
    ]

    print("\nColumns containing missing values:")
    print(len(missing_table))

    # --------------------------------------------------------
    # Constant columns
    # --------------------------------------------------------

    constant_columns = [
        column
        for column in df.columns
        if df[column].nunique(dropna=False) <= 1
    ]

    print("\nConstant columns:")
    print(len(constant_columns))

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    duplicate_count = df.duplicated().sum()

    print("\nDuplicate rows:")
    print(duplicate_count)

    # --------------------------------------------------------
    # Numerical and categorical columns
    # --------------------------------------------------------

    numerical_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        exclude="number"
    ).columns.tolist()

    print("\nNumerical columns:")
    print(len(numerical_columns))

    print("Categorical/non-numerical columns:")
    print(len(categorical_columns))

    # --------------------------------------------------------
    # Save profiling results
    # --------------------------------------------------------

    base_name = os.path.splitext(
        os.path.basename(file_path)
    )[0]

    missing_file = os.path.join(
        OUTPUT_DIR,
        f"{base_name}_missing.csv"
    )

    missing_table.to_csv(
        missing_file
    )

    constant_file = os.path.join(
        OUTPUT_DIR,
        f"{base_name}_constant_columns.txt"
    )

    with open(
        constant_file,
        "w",
        encoding="utf-8"
    ) as file:

        for column in constant_columns:
            file.write(column + "\n")

    print("\nProfiling results saved.")


# ============================================================
# Find all IEC 104 CSV files
# ============================================================

csv_files = [
    os.path.join(DATA_DIR, file)
    for file in os.listdir(DATA_DIR)
    if file.lower().endswith(".csv")
]

csv_files.sort()

print("\nIEC 104 DATASET PROFILING")
print("=" * 70)

print(f"Dataset folder: {DATA_DIR}")
print(f"CSV files found: {len(csv_files)}")

for file_path in csv_files:

    profile_dataset(file_path)

print("\n" + "=" * 70)
print("PROFILING COMPLETED")
print("=" * 70)