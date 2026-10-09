import pandas as pd
from pathlib import Path

# ============================================================
# IEC-104 SOC ALERT PRIORITIZATION
# ============================================================

INPUT_FILE = Path(
    "results/soc/iec104_incidents.csv"
)

OUTPUT_DIR = Path(
    "results/soc"
)

print("=" * 70)
print("IEC-104 SOC ALERT PRIORITIZATION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load incidents
# ------------------------------------------------------------

print("\nLoading correlated incidents...")

incidents = pd.read_csv(
    INPUT_FILE
)

print(
    f"Total incidents: {len(incidents)}"
)

# ------------------------------------------------------------
# 2. Base severity score
# ------------------------------------------------------------

severity_scores = {
    "High": 60,
    "Medium": 35
}

incidents["Severity_Score"] = (
    incidents["Severity"]
    .map(severity_scores)
    .fillna(20)
)

# ------------------------------------------------------------
# 3. Event-volume score
# ------------------------------------------------------------

def calculate_event_score(event_count):

    if event_count >= 10000:
        return 30

    elif event_count >= 1000:
        return 20

    elif event_count >= 100:
        return 10

    elif event_count >= 10:
        return 5

    else:
        return 2


incidents["Event_Volume_Score"] = (
    incidents["Event_Count"]
    .apply(calculate_event_score)
)

# ------------------------------------------------------------
# 4. Duration score
# ------------------------------------------------------------

def calculate_duration_score(duration):

    if duration >= 600:
        return 10

    elif duration >= 300:
        return 7

    elif duration >= 60:
        return 5

    else:
        return 2


incidents["Duration_Score"] = (
    incidents["Duration_Seconds"]
    .apply(calculate_duration_score)
)

# ------------------------------------------------------------
# 5. Calculate total priority score
# ------------------------------------------------------------

incidents["Priority_Score"] = (
    incidents["Severity_Score"]
    + incidents["Event_Volume_Score"]
    + incidents["Duration_Score"]
)

# ------------------------------------------------------------
# 6. Convert score to priority
# ------------------------------------------------------------

def determine_priority(score):

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
    .apply(determine_priority)
)

# ------------------------------------------------------------
# 7. Recommended response
# ------------------------------------------------------------

def recommended_action(priority):

    if priority == "Critical":
        return (
            "Immediate SOC investigation and "
            "containment assessment"
        )

    elif priority == "High":
        return (
            "Prompt SOC investigation"
        )

    elif priority == "Medium":
        return (
            "Review and correlate with related events"
        )

    else:
        return (
            "Monitor and review if activity persists"
        )


incidents["Recommended_Action"] = (
    incidents["Priority"]
    .apply(recommended_action)
)

# ------------------------------------------------------------
# 8. Sort by priority score
# ------------------------------------------------------------

incidents = incidents.sort_values(
    "Priority_Score",
    ascending=False
).reset_index(drop=True)

# ------------------------------------------------------------
# 9. Display results
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PRIORITIZED SOC ALERTS")
print("=" * 70)

display_columns = [
    "Incident_ID",
    "Attack_Type",
    "Event_Count",
    "Duration_Seconds",
    "Severity",
    "Priority_Score",
    "Priority"
]

print(
    incidents[display_columns]
    .to_string(index=False)
)

# ------------------------------------------------------------
# 10. Priority distribution
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PRIORITY DISTRIBUTION")
print("=" * 70)

print(
    incidents["Priority"]
    .value_counts()
)

# ------------------------------------------------------------
# 11. Save prioritized incidents
# ------------------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_file = (
    OUTPUT_DIR /
    "iec104_prioritized_alerts.csv"
)

incidents.to_csv(
    output_file,
    index=False
)

print("\nPrioritized alerts saved:")
print(output_file)

print("\n" + "=" * 70)
print("ALERT PRIORITIZATION COMPLETE")
print("=" * 70)