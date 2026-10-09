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

print("\nIEC-104 FEATURE SELECTION ANALYSIS")
print("=" * 80)

# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print(f"\nDataset shape: {df.shape}")

# --------------------------------------------------
# Define columns
# --------------------------------------------------

target = "Label"

identifier_columns = [
    "Flow ID",
    "Src IP",
    "Dst IP",
    "Timestamp"
]

constant_columns = [
    column
    for column in df.columns
    if df[column].nunique(dropna=False) <= 1
]

print("\n" + "=" * 80)
print("1. CONSTANT FEATURES")
print("=" * 80)

print(f"Number of constant features: {len(constant_columns)}")

for column in constant_columns:
    print(f"- {column}")

# --------------------------------------------------
# Candidate ML features
# --------------------------------------------------

excluded_columns = identifier_columns + [target]

candidate_features = [
    column
    for column in df.columns
    if column not in excluded_columns
    and column not in constant_columns
]

print("\n" + "=" * 80)
print("2. CANDIDATE ML FEATURES")
print("=" * 80)

print(f"Candidate features: {len(candidate_features)}")

for column in candidate_features:
    print(f"- {column}")

# --------------------------------------------------
# Correlation analysis
# --------------------------------------------------

print("\n" + "=" * 80)
print("3. HIGHLY CORRELATED FEATURE PAIRS")
print("=" * 80)

numeric_features = df[candidate_features].select_dtypes(
    include=np.number
)

correlation_matrix = numeric_features.corr()

high_corr_pairs = []

columns = correlation_matrix.columns

for i in range(len(columns)):

    for j in range(i + 1, len(columns)):

        correlation = correlation_matrix.iloc[i, j]

        if abs(correlation) >= 0.95:

            high_corr_pairs.append({
                "Feature_1": columns[i],
                "Feature_2": columns[j],
                "Correlation": correlation
            })

high_corr_df = pd.DataFrame(high_corr_pairs)

if len(high_corr_df) > 0:

    high_corr_df["Abs_Correlation"] = (
        high_corr_df["Correlation"].abs()
    )

    high_corr_df = high_corr_df.sort_values(
        "Abs_Correlation",
        ascending=False
    )

    print(
        high_corr_df[
            ["Feature_1", "Feature_2", "Correlation"]
        ].to_string(index=False)
    )

else:
    print("No highly correlated pairs found.")

# Save correlation report

correlation_file = os.path.join(
    OUTPUT_DIR,
    "iec104_feature_selection_correlations.csv"
)

high_corr_df.to_csv(
    correlation_file,
    index=False
)

# --------------------------------------------------
# Feature importance candidates
# --------------------------------------------------

print("\n" + "=" * 80)
print("4. FEATURE GROUPS")
print("=" * 80)

groups = {
    "Flow / Packet Count": [
        "Flow Duration",
        "Total Fwd Packet",
        "Total Bwd packets",
        "Total Length of Fwd Packet",
        "Total Length of Bwd Packet"
    ],

    "Packet Length": [
        "Fwd Packet Length Max",
        "Fwd Packet Length Min",
        "Fwd Packet Length Mean",
        "Fwd Packet Length Std",
        "Bwd Packet Length Max",
        "Bwd Packet Length Min",
        "Bwd Packet Length Mean",
        "Bwd Packet Length Std",
        "Packet Length Min",
        "Packet Length Max",
        "Packet Length Mean",
        "Packet Length Std",
        "Packet Length Variance"
    ],

    "Traffic Rate": [
        "Flow Bytes/s",
        "Flow Packets/s",
        "Fwd Packets/s",
        "Bwd Packets/s"
    ],

    "Timing / IAT": [
        "Flow IAT Mean",
        "Flow IAT Std",
        "Flow IAT Max",
        "Flow IAT Min",
        "Fwd IAT Total",
        "Fwd IAT Mean",
        "Fwd IAT Std",
        "Fwd IAT Max",
        "Fwd IAT Min",
        "Bwd IAT Total",
        "Bwd IAT Mean",
        "Bwd IAT Std",
        "Bwd IAT Max",
        "Bwd IAT Min"
    ],

    "TCP Flags": [
        "Fwd PSH Flags",
        "Fwd URG Flags",
        "FIN Flag Count",
        "SYN Flag Count",
        "RST Flag Count",
        "PSH Flag Count",
        "ACK Flag Count",
        "URG Flag Count",
        "CWR Flag Count",
        "ECE Flag Count"
    ],

    "Activity": [
        "Active Mean",
        "Active Std",
        "Active Max",
        "Active Min",
        "Idle Mean",
        "Idle Std",
        "Idle Max",
        "Idle Min"
    ]
}

for group_name, features in groups.items():

    available = [
        feature
        for feature in features
        if feature in candidate_features
    ]

    print(f"\n{group_name}:")
    print(f"  {len(available)} features")

# --------------------------------------------------
# Save candidate feature list
# --------------------------------------------------

feature_file = os.path.join(
    OUTPUT_DIR,
    "iec104_candidate_features.txt"
)

with open(
    feature_file,
    "w",
    encoding="utf-8"
) as file:

    for feature in candidate_features:
        file.write(feature + "\n")

# --------------------------------------------------
# Final summary
# --------------------------------------------------

print("\n" + "=" * 80)
print("FEATURE SELECTION ANALYSIS COMPLETED")
print("=" * 80)

print(f"\nOriginal columns       : {len(df.columns)}")
print(f"Constant features     : {len(constant_columns)}")
print(f"Identifiers excluded  : {len(identifier_columns)}")
print(f"Target excluded       : 1")
print(f"Candidate ML features : {len(candidate_features)}")

print("\nReports saved to:")
print(OUTPUT_DIR)