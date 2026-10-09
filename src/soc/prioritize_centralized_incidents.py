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
    / "centralized_soc_incidents.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "soc"
    / "prioritized_soc_alerts.csv"
)


# ============================================================
# LOAD INCIDENTS
# ============================================================

print("=" * 60)
print("CENTRALIZED SOC ALERT PRIORITIZATION")
print("=" * 60)

print("\nLoading incidents...")

incidents = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(
    f"Incidents loaded: {len(incidents)}"
)


# ============================================================
# PRIORITY SCORE
# ============================================================

def calculate_priority_score(row):

    severity = row["Severity"]
    event_count = row["Event_Count"]
    duration = row["Duration_Seconds"]

    # Base score from severity
    severity_score = {
        "Low": 20,
        "Medium": 35,
        "High": 60,
        "Critical": 80
    }

    score = severity_score.get(
        severity,
        20
    )

    # Event volume
    if event_count >= 10000:
        score += 30

    elif event_count >= 1000:
        score += 20

    elif event_count >= 100:
        score += 10

    elif event_count >= 10:
        score += 5

    else:
        score += 2

    # Duration
    if duration >= 600:
        score += 10

    elif duration >= 300:
        score += 7

    elif duration >= 60:
        score += 5

    else:
        score += 2

    return score


# ============================================================
# CALCULATE SCORES
# ============================================================

incidents["Priority_Score"] = incidents.apply(
    calculate_priority_score,
    axis=1
)


# ============================================================
# ASSIGN PRIORITY
# ============================================================

def assign_priority(score):

    if score >= 90:
        return "Critical"

    elif score >= 70:
        return "High"

    elif score >= 50:
        return "Medium"

    else:
        return "Low"


incidents["Priority"] = (
    incidents["Priority_Score"]
    .apply(assign_priority)
)


# ============================================================
# RECOMMENDED ACTION
# ============================================================

def recommended_action(row):

    event_type = str(
        row["SOC_Event_Type"]
    ).lower()

    priority = row["Priority"]

    if priority == "Critical":

        return (
            "Immediate SOC investigation; "
            "isolate affected OT segment if required"
        )

    if "portscan" in event_type:

        return (
            "Investigate source and "
            "check exposed OT services"
        )

    if "dos" in event_type:

        return (
            "Investigate traffic surge and "
            "protect affected OT service"
        )

    if "mitm" in event_type:

        return (
            "Investigate communication integrity "
            "and verify trusted endpoints"
        )

    if "ptp" in event_type:

        return (
            "Verify PTP timing traffic and "
            "investigate abnormal synchronization"
        )

    if "fuzzy" in event_type:

        return (
            "Inspect malformed protocol traffic "
            "and affected IEC104 devices"
        )

    if "starvation" in event_type:

        return (
            "Investigate IEC104 communication "
            "availability and traffic patterns"
        )

    if "flood" in event_type:

        return (
            "Investigate abnormal traffic volume "
            "and affected endpoints"
        )

    if "ntpddos" in event_type:

        return (
            "Investigate abnormal NTP traffic "
            "and affected infrastructure"
        )

    if "unknown" in event_type:

        return (
            "Perform manual SOC investigation "
            "to determine event origin"
        )

    return (
        "Review incident details "
        "and investigate affected assets"
    )


incidents["Recommended_Action"] = incidents.apply(
    recommended_action,
    axis=1
)


# ============================================================
# SORT BY PRIORITY
# ============================================================

priority_order = {
    "Critical": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4
}

incidents["Priority_Order"] = (
    incidents["Priority"]
    .map(priority_order)
)

incidents = incidents.sort_values(
    by=[
        "Priority_Order",
        "Priority_Score",
        "Event_Count"
    ],
    ascending=[
        True,
        False,
        False
    ]
)

incidents = incidents.drop(
    columns=["Priority_Order"]
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

incidents.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("ALERT PRIORITIZATION COMPLETE")
print("=" * 60)

print(
    f"Total incidents: {len(incidents)}"
)

print("\nPriority distribution:")

print(
    incidents["Priority"]
    .value_counts()
)


print("\nTop prioritized incidents:")

print(
    incidents[
        [
            "Incident_ID",
            "Protocol",
            "SOC_Event_Type",
            "Event_Count",
            "Severity",
            "Priority_Score",
            "Priority"
        ]
    ].head(10).to_string(index=False)
)


print("\nSaved to:")

print(OUTPUT_FILE)