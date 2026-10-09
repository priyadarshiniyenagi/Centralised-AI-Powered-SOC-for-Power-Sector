import pandas as pd
from pathlib import Path

# ============================================================
# IEC-104 SOC EVENT CORRELATION
# ============================================================

INPUT_FILE = Path(
    "results/soc/iec104_soc_events.csv"
)

OUTPUT_DIR = Path(
    "results/soc"
)

CORRELATION_WINDOW_SECONDS = 300  # 5 minutes

print("=" * 70)
print("IEC-104 SOC EVENT CORRELATION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load SOC events
# ------------------------------------------------------------

print("\nLoading SOC events...")

events = pd.read_csv(INPUT_FILE)

print(
    f"Total events: {len(events):,}"
)

# ------------------------------------------------------------
# 2. Parse timestamps
# ------------------------------------------------------------

events["Timestamp"] = pd.to_datetime(
    events["Timestamp"],
    errors="coerce"
)

# Remove records with invalid timestamps

invalid_timestamps = events["Timestamp"].isna().sum()

if invalid_timestamps > 0:

    print(
        f"Removing {invalid_timestamps} "
        "events with invalid timestamps."
    )

    events = events.dropna(
        subset=["Timestamp"]
    )

# ------------------------------------------------------------
# 3. Sort events
# ------------------------------------------------------------

events = events.sort_values(
    [
        "Protocol",
        "Attack_Type",
        "Timestamp"
    ]
).reset_index(drop=True)

# ------------------------------------------------------------
# 4. Correlate events
# ------------------------------------------------------------

print("\nCorrelating events...")

incident_ids = []

current_incident = 0

previous_protocol = None
previous_attack = None
previous_timestamp = None

for _, row in events.iterrows():

    current_protocol = row["Protocol"]
    current_attack = row["Attack_Type"]
    current_timestamp = row["Timestamp"]

    # Start a new incident when:
    # - protocol changes
    # - attack type changes
    # - time gap exceeds 5 minutes

    new_incident = False

    if previous_protocol is None:
        new_incident = True

    elif current_protocol != previous_protocol:
        new_incident = True

    elif current_attack != previous_attack:
        new_incident = True

    else:

        time_difference = (
            current_timestamp -
            previous_timestamp
        ).total_seconds()

        if time_difference > CORRELATION_WINDOW_SECONDS:
            new_incident = True

    if new_incident:

        current_incident += 1

    incident_ids.append(
        f"INC-{current_incident:06d}"
    )

    previous_protocol = current_protocol
    previous_attack = current_attack
    previous_timestamp = current_timestamp

events["Incident_ID"] = incident_ids

# ------------------------------------------------------------
# 5. Generate incident summary
# ------------------------------------------------------------

print("\nGenerating incident summaries...")

incidents = (
    events
    .groupby("Incident_ID")
    .agg(
        Protocol=("Protocol", "first"),
        Attack_Type=("Attack_Type", "first"),
        Start_Time=("Timestamp", "min"),
        End_Time=("Timestamp", "max"),
        Event_Count=("Event_ID", "count"),
        Source_Count=("Source_IP", "nunique"),
        Destination_Count=("Destination_IP", "nunique"),
        Severity=("Severity", "first")
    )
    .reset_index()
)

# ------------------------------------------------------------
# 6. Calculate incident duration
# ------------------------------------------------------------

incidents["Duration_Seconds"] = (
    incidents["End_Time"] -
    incidents["Start_Time"]
).dt.total_seconds()

# Reorder columns

incidents = incidents[
    [
        "Incident_ID",
        "Protocol",
        "Attack_Type",
        "Start_Time",
        "End_Time",
        "Duration_Seconds",
        "Event_Count",
        "Source_Count",
        "Destination_Count",
        "Severity"
    ]
]

# ------------------------------------------------------------
# 7. Display statistics
# ------------------------------------------------------------

print(
    f"\nTotal incidents created: "
    f"{len(incidents):,}"
)

print("\nIncidents by attack type:")

print(
    incidents["Attack_Type"]
    .value_counts()
)

print("\nIncidents by severity:")

print(
    incidents["Severity"]
    .value_counts()
)

# ------------------------------------------------------------
# 8. Display first incidents
# ------------------------------------------------------------

print("\nFirst 10 incidents:")

print(
    incidents.head(10).to_string(
        index=False
    )
)

# ------------------------------------------------------------
# 9. Save correlated events
# ------------------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

correlated_file = (
    OUTPUT_DIR /
    "iec104_correlated_events.csv"
)

events.to_csv(
    correlated_file,
    index=False
)

# ------------------------------------------------------------
# 10. Save incident summary
# ------------------------------------------------------------

incident_file = (
    OUTPUT_DIR /
    "iec104_incidents.csv"
)

incidents.to_csv(
    incident_file,
    index=False
)

print("\nFiles saved:")

print(correlated_file)
print(incident_file)

print("\n" + "=" * 70)
print("EVENT CORRELATION COMPLETE")
print("=" * 70)