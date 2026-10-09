import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "soc"
    / "combined_soc_events.csv"
)

OUTPUT_EVENTS = (
    PROJECT_ROOT
    / "results"
    / "soc"
    / "correlated_soc_events.csv"
)

OUTPUT_INCIDENTS = (
    PROJECT_ROOT
    / "results"
    / "soc"
    / "centralized_soc_incidents.csv"
)


# ============================================================
# SETTINGS
# ============================================================

WINDOW_MINUTES = 5


# ============================================================
# CREATE INCIDENT
# ============================================================

def create_incident(event_list, incident_number):

    df = pd.DataFrame(event_list)

    start_time = df["Timestamp"].min()
    end_time = df["Timestamp"].max()

    duration = (
        end_time - start_time
    ).total_seconds()

    severity_order = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4
    }

    severity = max(
        df["Severity"].fillna("Low"),
        key=lambda x: severity_order.get(x, 1)
    )

    return {
        "Incident_ID":
            f"INC-{incident_number:06d}",

        "Protocol":
            df["Protocol"].iloc[0],

        "SOC_Event_Type":
            df["SOC_Event_Type"].iloc[0],

        "Detection_Source":
            ", ".join(
                df["Detection_Source"]
                .dropna()
                .unique()
            ),

        "Event_Count":
            len(df),

        "Start_Time":
            start_time,

        "End_Time":
            end_time,

        "Duration_Seconds":
            duration,

        "Severity":
            severity,

        "Source_Count":
            df["Source"].nunique(),

        "Destination_Count":
            df["Destination"].nunique(),

        "Event_IDs":
            ",".join(
                df["Event_ID"].astype(str)
            )
    }


# ============================================================
# LOAD EVENTS
# ============================================================

print("=" * 60)
print("CENTRALIZED SOC EVENT CORRELATION")
print("=" * 60)

print("\nLoading centralized events...")

events = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(
    f"Total events loaded: {len(events):,}"
)


# ============================================================
# TIMESTAMP PREPARATION
# ============================================================

events["Timestamp"] = pd.to_datetime(
    events["Timestamp"],
    format="mixed",
    errors="coerce",
    utc=True
)

invalid = events["Timestamp"].isna().sum()

print(
    f"Invalid timestamps: {invalid:,}"
)

events = events.dropna(
    subset=["Timestamp"]
)

events = events.sort_values(
    "Timestamp"
).reset_index(
    drop=True
)


# ============================================================
# CORRELATION
# ============================================================

print("\nCorrelating events...")

incidents = []

incident_counter = 1


# Group by protocol AND SOC event type
for (protocol, event_type), group in events.groupby(
    ["Protocol", "SOC_Event_Type"]
):

    group = group.sort_values(
        "Timestamp"
    )

    current_events = []
    current_start = None


    for _, event in group.iterrows():

        timestamp = event["Timestamp"]


        # First event
        if current_start is None:

            current_start = timestamp
            current_events = [event]

            continue


        time_difference = (
            timestamp - current_start
        ).total_seconds()


        # Same incident if within 5 minutes
        if time_difference <= WINDOW_MINUTES * 60:

            current_events.append(event)


        else:

            # Finish current incident
            incidents.append(
                create_incident(
                    current_events,
                    incident_counter
                )
            )

            incident_counter += 1


            # Start next incident
            current_start = timestamp
            current_events = [event]


    # Finish final incident
    if current_events:

        incidents.append(
            create_incident(
                current_events,
                incident_counter
            )
        )

        incident_counter += 1


# ============================================================
# CREATE INCIDENT DATAFRAME
# ============================================================

incident_df = pd.DataFrame(
    incidents
)


if incident_df.empty:

    print("\nNo incidents were created.")

    raise SystemExit


# ============================================================
# ASSIGN INCIDENT ID TO EVENTS
# ============================================================

events["Incident_ID"] = None


for _, incident in incident_df.iterrows():

    event_ids = (
        incident["Event_IDs"]
        .split(",")
    )

    events.loc[
        events["Event_ID"].isin(event_ids),
        "Incident_ID"
    ] = incident["Incident_ID"]


# ============================================================
# PREPARE INCIDENT OUTPUT
# ============================================================

incident_output = incident_df.drop(
    columns=["Event_IDs"]
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_EVENTS.parent.mkdir(
    parents=True,
    exist_ok=True
)

events.to_csv(
    OUTPUT_EVENTS,
    index=False
)

incident_output.to_csv(
    OUTPUT_INCIDENTS,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("CORRELATION COMPLETE")
print("=" * 60)

print(
    f"Total events    : {len(events):,}"
)

print(
    f"Total incidents : {len(incident_output):,}"
)


print("\nIncidents by protocol:")

print(
    incident_output["Protocol"]
    .value_counts()
)


print("\nIncidents by SOC event type:")

print(
    incident_output["SOC_Event_Type"]
    .value_counts()
)


print("\nIncidents by severity:")

print(
    incident_output["Severity"]
    .value_counts()
)


print("\nSaved event file:")
print(OUTPUT_EVENTS)


print("\nSaved incident file:")
print(OUTPUT_INCIDENTS)