import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.ensemble import IsolationForest

# ============================================================
# IEC-104 SOC EVENT GENERATOR
# ============================================================

INPUT_FILE = Path(
    "data/processed/IEC104/iec104_combined.csv"
)

RESULT_DIR = Path(
    "results/soc"
)

print("=" * 70)
print("IEC-104 SOC EVENT GENERATOR")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load dataset
# ------------------------------------------------------------

print("\nLoading IEC-104 dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Total records: {len(df):,}")

# ------------------------------------------------------------
# 2. Parse timestamp
# ------------------------------------------------------------

df["Timestamp"] = pd.to_datetime(
    df["Timestamp"],
    errors="coerce"
)

# ------------------------------------------------------------
# 3. Prepare binary labels
# ------------------------------------------------------------

df["Anomaly"] = (
    df["Label"] != "attackfree"
).astype(int)

# ------------------------------------------------------------
# 4. Select behavioral features
# ------------------------------------------------------------

exclude_columns = [
    "Flow ID",
    "Src IP",
    "Dst IP",
    "Src Port",
    "Dst Port",
    "Timestamp",
    "Label",
    "Anomaly",
    "Bwd PSH Flags",
    "Bwd URG Flags",
    "Fwd Bytes/Bulk Avg",
    "Fwd Packet/Bulk Avg",
    "Fwd Bulk Rate Avg"
]

feature_columns = [
    column
    for column in df.columns
    if column not in exclude_columns
]

print(
    f"Behavioral features: {len(feature_columns)}"
)

# ------------------------------------------------------------
# 5. Train anomaly detector using normal traffic
# ------------------------------------------------------------

normal_data = df[
    df["Label"] == "attackfree"
].copy()

print(
    f"Normal training records: {len(normal_data):,}"
)

X_train = normal_data[
    feature_columns
]

print("\nTraining Isolation Forest...")

model = IsolationForest(
    n_estimators=200,
    contamination="auto",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train)

print("Training completed.")

# ------------------------------------------------------------
# 6. Calculate anomaly scores
# ------------------------------------------------------------

print("\nCalculating anomaly scores...")

df["ML_Score"] = model.score_samples(
    df[feature_columns]
)

# Same threshold used during our evaluation
THRESHOLD = -0.50

df["ML_Detected"] = (
    df["ML_Score"] < THRESHOLD
).astype(int)

# ------------------------------------------------------------
# 7. Create SOC event records
# ------------------------------------------------------------

print("\nGenerating SOC events...")

events = []

event_counter = 1

for _, row in df.iterrows():

    # Generate event when:
    # 1. Dataset label indicates an attack
    # OR
    # 2. ML model identifies anomalous behavior

    is_attack_label = (
        row["Label"] != "attackfree"
    )

    is_ml_anomaly = (
        row["ML_Detected"] == 1
    )

    if not (is_attack_label or is_ml_anomaly):
        continue

    # --------------------------------------------------------
    # Determine event type
    # --------------------------------------------------------

    if is_attack_label:
        event_type = "Known Attack"
    else:
        event_type = "Behavioral Anomaly"

    # --------------------------------------------------------
    # Determine attack type
    # --------------------------------------------------------

    if is_attack_label:
        attack_type = row["Label"]
    else:
        attack_type = "Unknown Anomaly"

    # --------------------------------------------------------
    # Determine severity
    # --------------------------------------------------------

    # Explicit rule-based severity.
    # This is a preliminary SOC rule and can be refined later.

    if attack_type in [
        "dosattack",
        "ntpddosattack"
    ]:
        severity = "High"

    elif attack_type in [
        "mitmattack",
        "iec104starvationattack",
        "fuzzyattack"
    ]:
        severity = "High"

    elif attack_type in [
        "portscanattack",
        "floodattack"
    ]:
        severity = "Medium"

    else:
        severity = "Medium"

    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    if event_type == "Known Attack":

        description = (
            f"Detected {attack_type} activity "
            f"in IEC-104 traffic."
        )

    else:

        description = (
            "Behavioral anomaly detected in "
            "IEC-104 traffic by the anomaly detector."
        )

    # --------------------------------------------------------
    # Create event
    # --------------------------------------------------------

    event = {
        "Event_ID": f"EVT-{event_counter:06d}",
        "Timestamp": row["Timestamp"],
        "Protocol": "IEC-104",
        "Source_IP": row["Src IP"],
        "Destination_IP": row["Dst IP"],
        "Source_Port": row["Src Port"],
        "Destination_Port": row["Dst Port"],
        "Event_Type": event_type,
        "Attack_Type": attack_type,
        "ML_Score": row["ML_Score"],
        "ML_Detected": row["ML_Detected"],
        "Severity": severity,
        "Description": description
    }

    events.append(event)

    event_counter += 1

# ------------------------------------------------------------
# 8. Convert to DataFrame
# ------------------------------------------------------------

events_df = pd.DataFrame(events)

print(
    f"\nTotal SOC events generated: "
    f"{len(events_df):,}"
)

# ------------------------------------------------------------
# 9. Event statistics
# ------------------------------------------------------------

print("\nEvent type distribution:")

print(
    events_df["Event_Type"]
    .value_counts()
)

print("\nAttack type distribution:")

print(
    events_df["Attack_Type"]
    .value_counts()
)

print("\nSeverity distribution:")

print(
    events_df["Severity"]
    .value_counts()
)

# ------------------------------------------------------------
# 10. Save SOC events
# ------------------------------------------------------------

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_file = (
    RESULT_DIR /
    "iec104_soc_events.csv"
)

events_df.to_csv(
    output_file,
    index=False
)

print("\nSOC event dataset saved:")
print(output_file)

print("\n" + "=" * 70)
print("SOC EVENT GENERATION COMPLETE")
print("=" * 70)