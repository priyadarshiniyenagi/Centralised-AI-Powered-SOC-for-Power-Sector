import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

IEC104_FILE = (
    PROJECT_ROOT
    / "results"
    / "soc"
    / "iec104_soc_events.csv"
)

IEC61850_FILE = (
    PROJECT_ROOT
    / "results"
    / "soc"
    / "iec61850_soc_events.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "soc"
    / "combined_soc_events.csv"
)


# ============================================================
# LOAD IEC104 EVENTS
# ============================================================

print("=" * 60)
print("CENTRALIZED SOC EVENT COMBINATION")
print("=" * 60)

print("\nLoading IEC104 events...")

iec104 = pd.read_csv(
    IEC104_FILE,
    low_memory=False
)

print(f"IEC104 events: {len(iec104):,}")


# ============================================================
# IEC104 STANDARDIZATION
# ============================================================

# Detection source
iec104["Detection_Source"] = (
    "IEC104_IsolationForest"
)

# Preserve actual attack/anomaly type
if "Attack_Type" in iec104.columns:

    iec104["SOC_Event_Type"] = (
        iec104["Attack_Type"]
        .fillna("Unknown Anomaly")
        .astype(str)
    )

else:

    iec104["SOC_Event_Type"] = (
        iec104["Event_Type"]
        .fillna("Unknown Anomaly")
        .astype(str)
    )


# Use actual IP addresses as generic SOC source/destination
if "Source_IP" in iec104.columns:

    iec104["Source"] = (
        iec104["Source_IP"]
        .fillna("Unknown")
        .astype(str)
    )

else:

    iec104["Source"] = "Unknown"


if "Destination_IP" in iec104.columns:

    iec104["Destination"] = (
        iec104["Destination_IP"]
        .fillna("Unknown")
        .astype(str)
    )

else:

    iec104["Destination"] = "Unknown"


# ============================================================
# LOAD IEC61850 EVENTS
# ============================================================

print("\nLoading IEC61850 events...")

iec61850 = pd.read_csv(
    IEC61850_FILE,
    low_memory=False
)

print(
    f"IEC61850 events: {len(iec61850):,}"
)


# ============================================================
# IEC61850 STANDARDIZATION
# ============================================================

iec61850["Detection_Source"] = (
    "IEC61850_PTP_RandomForest"
)

iec61850["SOC_Event_Type"] = (
    "PTP Anomaly"
)


if "Source_MAC" in iec61850.columns:

    iec61850["Source"] = (
        iec61850["Source_MAC"]
        .fillna("Unknown")
        .astype(str)
    )

else:

    iec61850["Source"] = "Unknown"


if "Destination_MAC" in iec61850.columns:

    iec61850["Destination"] = (
        iec61850["Destination_MAC"]
        .fillna("Unknown")
        .astype(str)
    )

else:

    iec61850["Destination"] = "Unknown"


# ============================================================
# COMMON COLUMNS
# ============================================================

common_columns = [
    "Timestamp",
    "Protocol",
    "Detection_Source",
    "Event_Type",
    "SOC_Event_Type",
    "Detection_Status",
    "Confidence",
    "Severity",
    "Source",
    "Destination",
    "Ground_Truth_Label",
    "Mode"
]


# Add missing columns where necessary
for column in common_columns:

    if column not in iec104.columns:
        iec104[column] = None

    if column not in iec61850.columns:
        iec61850[column] = None


# ============================================================
# SELECT COMMON FORMAT
# ============================================================

iec104 = iec104[common_columns]

iec61850 = iec61850[common_columns]


# ============================================================
# COMBINE
# ============================================================

combined = pd.concat(
    [iec104, iec61850],
    ignore_index=True
)


# ============================================================
# TIMESTAMP PARSING
# ============================================================

print("\nParsing timestamps...")

combined["Timestamp"] = pd.to_datetime(
    combined["Timestamp"],
    format="mixed",
    errors="coerce",
    utc=True
)

valid_timestamps = (
    combined["Timestamp"].notna().sum()
)

invalid_timestamps = (
    combined["Timestamp"].isna().sum()
)

print(
    f"Valid timestamps  : {valid_timestamps:,}"
)

print(
    f"Invalid timestamps: {invalid_timestamps:,}"
)


# ============================================================
# SORT
# ============================================================

combined = combined.sort_values(
    "Timestamp",
    na_position="last"
).reset_index(
    drop=True
)


# ============================================================
# CENTRALIZED EVENT ID
# ============================================================

combined.insert(
    0,
    "Event_ID",
    [
        f"SOC-{i:06d}"
        for i in range(1, len(combined) + 1)
    ]
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

combined.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("CENTRALIZED SOC EVENT STREAM CREATED")
print("=" * 60)

print(
    f"Total SOC events: {len(combined):,}"
)

print("\nEvents by protocol:")

print(
    combined["Protocol"]
    .value_counts()
)

print("\nEvents by SOC event type:")

print(
    combined["SOC_Event_Type"]
    .value_counts()
)

print("\nDetection sources:")

print(
    combined["Detection_Source"]
    .value_counts()
)

print("\nValid source addresses:")

print(
    (combined["Source"] != "Unknown").sum()
)

print("\nValid destination addresses:")

print(
    (combined["Destination"] != "Unknown").sum()
)

print("\nSaved to:")

print(OUTPUT_FILE)