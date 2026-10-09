import pandas as pd
from pathlib import Path


# ============================================================
# IEC-104 GROUP / CAPTURE STRUCTURE ANALYSIS
# ============================================================

print("\nIEC-104 GROUP / CAPTURE STRUCTURE ANALYSIS")
print("=" * 70)


# ------------------------------------------------------------
# 1. Paths
# ------------------------------------------------------------

DATA_FILE = Path(
    "data/processed/IEC104/iec104_combined.csv"
)

RESULT_DIR = Path("results/profiling")
RESULT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. Load dataset
# ------------------------------------------------------------

print("\nLoading combined IEC-104 dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Dataset shape: {df.shape}")


# ------------------------------------------------------------
# 3. Basic class information
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CLASS INFORMATION")
print("=" * 70)

class_summary = (
    df.groupby("Label")
    .agg(
        Records=("Label", "size"),
        Unique_Flow_IDs=("Flow ID", "nunique"),
        Unique_Src_IPs=("Src IP", "nunique"),
        Unique_Dst_IPs=("Dst IP", "nunique"),
        Unique_Src_Ports=("Src Port", "nunique"),
        Unique_Dst_Ports=("Dst Port", "nunique")
    )
    .sort_values("Records", ascending=False)
)

print(class_summary)


# ------------------------------------------------------------
# 4. Flow ID overlap between classes
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FLOW ID OVERLAP ANALYSIS")
print("=" * 70)

flow_label_counts = (
    df.groupby("Flow ID")["Label"]
    .nunique()
)

multi_label_flows = flow_label_counts[
    flow_label_counts > 1
]

print(
    f"\nFlow IDs appearing under multiple labels: "
    f"{len(multi_label_flows)}"
)

if len(multi_label_flows) > 0:

    print("\nExamples:")

    example_flow_ids = multi_label_flows.index[:10]

    print(
        df[
            df["Flow ID"].isin(example_flow_ids)
        ][["Flow ID", "Label"]]
        .drop_duplicates()
        .sort_values("Flow ID")
        .to_string(index=False)
    )

else:

    print(
        "No Flow ID appears under multiple labels."
    )


# ------------------------------------------------------------
# 5. Source IP distribution by class
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TOP SOURCE IPs BY CLASS")
print("=" * 70)

for label in df["Label"].unique():

    subset = df[df["Label"] == label]

    print(f"\n[{label}]")

    print(
        subset["Src IP"]
        .value_counts()
        .head(5)
        .to_string()
    )


# ------------------------------------------------------------
# 6. Destination IP distribution by class
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TOP DESTINATION IPs BY CLASS")
print("=" * 70)

for label in df["Label"].unique():

    subset = df[df["Label"] == label]

    print(f"\n[{label}]")

    print(
        subset["Dst IP"]
        .value_counts()
        .head(5)
        .to_string()
    )


# ------------------------------------------------------------
# 7. Destination port distribution by class
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TOP DESTINATION PORTS BY CLASS")
print("=" * 70)

for label in df["Label"].unique():

    subset = df[df["Label"] == label]

    print(f"\n[{label}]")

    print(
        subset["Dst Port"]
        .value_counts()
        .head(10)
        .to_string()
    )


# ------------------------------------------------------------
# 8. Timestamp analysis
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TIMESTAMP ANALYSIS")
print("=" * 70)

df["Timestamp_parsed"] = pd.to_datetime(
    df["Timestamp"],
    errors="coerce"
)

print(
    f"\nUnparseable timestamps: "
    f"{df['Timestamp_parsed'].isna().sum()}"
)


timestamp_summary = (
    df.groupby("Label")["Timestamp_parsed"]
    .agg(["min", "max"])
    .sort_index()
)

print("\nTimestamp range by class:")

print(timestamp_summary)


# ------------------------------------------------------------
# 9. Records per day
# ------------------------------------------------------------

df["Date"] = df["Timestamp_parsed"].dt.date

date_class_counts = (
    df.groupby(["Date", "Label"])
    .size()
    .reset_index(name="Records")
)

print("\nNumber of distinct dates per class:")

dates_per_class = (
    date_class_counts
    .groupby("Label")["Date"]
    .nunique()
    .sort_values(ascending=False)
)

print(dates_per_class)


# ------------------------------------------------------------
# 10. Save results
# ------------------------------------------------------------

class_file = (
    RESULT_DIR /
    "iec104_class_group_summary.csv"
)

class_summary.to_csv(class_file)


timestamp_file = (
    RESULT_DIR /
    "iec104_timestamp_summary.csv"
)

timestamp_summary.to_csv(timestamp_file)


dates_file = (
    RESULT_DIR /
    "iec104_dates_per_class.csv"
)

dates_per_class.to_csv(
    dates_file,
    header=["Distinct_Dates"]
)


# ------------------------------------------------------------
# 11. Final message
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("GROUP STRUCTURE ANALYSIS COMPLETED")
print("=" * 70)

print(f"\nClass summary saved to:")
print(class_file)

print(f"\nTimestamp summary saved to:")
print(timestamp_file)

print(f"\nDate summary saved to:")
print(dates_file)