import pandas as pd
from pathlib import Path


# ============================================================
# IEC-104 TIMELINE ANALYSIS
# ============================================================

print("\nIEC-104 TIMELINE ANALYSIS")
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
# 2. Load only required columns
# ------------------------------------------------------------

print("\nLoading timestamp and label information...")

df = pd.read_csv(
    DATA_FILE,
    usecols=["Timestamp", "Label"]
)

print(f"Records loaded: {len(df)}")


# ------------------------------------------------------------
# 3. Parse timestamps
# ------------------------------------------------------------

df["Timestamp"] = pd.to_datetime(
    df["Timestamp"],
    errors="coerce"
)

df = df.dropna(subset=["Timestamp"])

df = df.sort_values("Timestamp").reset_index(drop=True)


# ------------------------------------------------------------
# 4. Overall timeline
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("OVERALL TIMELINE")
print("=" * 70)

print(f"\nEarliest timestamp: {df['Timestamp'].min()}")
print(f"Latest timestamp  : {df['Timestamp'].max()}")


# ------------------------------------------------------------
# 5. Label transitions
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("LABEL TRANSITIONS")
print("=" * 70)

df["Previous_Label"] = df["Label"].shift(1)

transitions = df[
    df["Label"] != df["Previous_Label"]
].copy()

transitions = transitions[
    ["Timestamp", "Previous_Label", "Label"]
]

print(
    f"\nNumber of label transitions: "
    f"{len(transitions) - 1}"
)

print("\nFirst 30 transitions:")

print(
    transitions.head(30).to_string(
        index=False
    )
)


# ------------------------------------------------------------
# 6. Continuous time ranges for each label
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TIME RANGE BY LABEL")
print("=" * 70)

label_ranges = (
    df.groupby("Label")["Timestamp"]
    .agg(
        Start="min",
        End="max",
        Records="count"
    )
    .sort_values("Start")
)

print(
    label_ranges.to_string()
)


# ------------------------------------------------------------
# 7. One-minute distribution
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("ONE-MINUTE LABEL DISTRIBUTION")
print("=" * 70)

df["Minute"] = df["Timestamp"].dt.floor("min")

minute_distribution = (
    df.groupby(["Minute", "Label"])
    .size()
    .reset_index(name="Records")
)

minute_pivot = (
    minute_distribution
    .pivot(
        index="Minute",
        columns="Label",
        values="Records"
    )
    .fillna(0)
)


print(
    f"\nNumber of one-minute intervals: "
    f"{len(minute_pivot)}"
)

print("\nFirst 30 one-minute intervals:")

print(
    minute_pivot.head(30).to_string()
)


# ------------------------------------------------------------
# 8. Check whether labels overlap in time
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TIME OVERLAP ANALYSIS")
print("=" * 70)

labels = sorted(df["Label"].unique())

overlap_results = []

for i in range(len(labels)):

    label_a = labels[i]

    range_a = label_ranges.loc[label_a]

    for j in range(i + 1, len(labels)):

        label_b = labels[j]

        range_b = label_ranges.loc[label_b]

        overlap = (
            range_a["Start"] <= range_b["End"]
            and range_b["Start"] <= range_a["End"]
        )

        overlap_results.append({
            "Label_A": label_a,
            "Label_B": label_b,
            "Time_Overlap": overlap
        })


overlap_df = pd.DataFrame(overlap_results)

print(
    overlap_df.to_string(index=False)
)


# ------------------------------------------------------------
# 9. Records per 5-minute interval
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FIVE-MINUTE TIMELINE")
print("=" * 70)

df["Five_Minute"] = (
    df["Timestamp"]
    .dt.floor("5min")
)

five_minute_distribution = (
    df.groupby(
        ["Five_Minute", "Label"]
    )
    .size()
    .reset_index(name="Records")
)

five_minute_pivot = (
    five_minute_distribution
    .pivot(
        index="Five_Minute",
        columns="Label",
        values="Records"
    )
    .fillna(0)
)

print(
    five_minute_pivot.to_string()
)


# ------------------------------------------------------------
# 10. Save results
# ------------------------------------------------------------

transition_file = (
    RESULT_DIR /
    "iec104_label_transitions.csv"
)

transitions.to_csv(
    transition_file,
    index=False
)


range_file = (
    RESULT_DIR /
    "iec104_label_time_ranges.csv"
)

label_ranges.to_csv(
    range_file
)


minute_file = (
    RESULT_DIR /
    "iec104_minute_distribution.csv"
)

minute_pivot.to_csv(
    minute_file
)


overlap_file = (
    RESULT_DIR /
    "iec104_time_overlap.csv"
)

overlap_df.to_csv(
    overlap_file,
    index=False
)


five_minute_file = (
    RESULT_DIR /
    "iec104_five_minute_distribution.csv"
)

five_minute_pivot.to_csv(
    five_minute_file
)


# ------------------------------------------------------------
# 11. Final output
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TIMELINE ANALYSIS COMPLETED")
print("=" * 70)

print(f"\nSaved:")
print(transition_file)
print(range_file)
print(minute_file)
print(overlap_file)
print(five_minute_file)