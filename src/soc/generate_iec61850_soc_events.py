import pandas as pd
import joblib
from pathlib import Path


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

NORMAL_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "IEC61850"
    / "capture61850-attackfree_PTP.csv"
)

ATTACK_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "IEC61850"
    / "capture61850-ptpattack.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "saved_models"
    / "iec61850_ptp_random_forest.joblib"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "soc"
    / "iec61850_soc_events.csv"
)


# --------------------------------------------------
# Features used by the trained model
# --------------------------------------------------

FEATURES = [
    "frame.len",
    "frame.cap_len",
    "frame.time_delta",
    "frame.time_relative",
    "ptp.v2.messagelength",
    "ptp.v2.sequenceid",
    "ptp.v2.domainnumber",
    "ptp.v2.correction.ns",
    "ptp.v2.correction.subns",
    "ptp.v2.sourceportid",
    "ptp.v2.versionptp",
    "goose.length",
    "goose.sqNum",
    "goose.stNum",
    "goose.confRev"
]


# --------------------------------------------------
# Load one capture
# --------------------------------------------------

def load_capture(file_path, ground_truth):

    columns = [
        "frame.time",
        "eth.src",
        "eth.dst"
    ] + FEATURES

    print(f"\nLoading: {file_path.name}")

    df = pd.read_csv(
        file_path,
        usecols=columns,
        low_memory=False
    )

    # Convert model features to numeric
    for column in FEATURES:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Same missing-value handling used during preprocessing
    df[FEATURES] = df[FEATURES].fillna(0)

    df["Ground_Truth_Label"] = ground_truth

    return df


# --------------------------------------------------
# Main SOC event generation
# --------------------------------------------------

def main():

    print("=" * 60)
    print("IEC61850 PTP SOC EVENT GENERATION")
    print("=" * 60)

    # Load trained model
    print("\nLoading trained Random Forest model...")

    model = joblib.load(MODEL_FILE)

    print("Model loaded successfully.")

    # Load normal capture
    normal_df = load_capture(
        NORMAL_FILE,
        "Normal"
    )

    # Load attack capture
    attack_df = load_capture(
        ATTACK_FILE,
        "PTP Attack"
    )

    # Combine captures
    df = pd.concat(
        [normal_df, attack_df],
        ignore_index=True
    )

    print(f"\nTotal replay records: {len(df):,}")

    # Model input
    X = df[FEATURES]

    print("\nRunning AI detection...")

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]

    df["Model_Prediction"] = predictions
    df["Confidence"] = probabilities

    # Keep only events detected by the AI model
    events = df[df["Model_Prediction"] == 1].copy()

    # --------------------------------------------------
    # SOC fields
    # --------------------------------------------------

    events.insert(
        0,
        "Event_ID",
        [
            f"IEC61850-{i:06d}"
            for i in range(1, len(events) + 1)
        ]
    )

    events["Protocol"] = "IEC61850-PTP"

    events["Detection_Source"] = (
        "IEC61850_PTP_RandomForest"
    )

    events["Event_Type"] = "PTP Anomaly"

    events["Detection_Status"] = "Detected"

    events["Mode"] = "Replay"

    # --------------------------------------------------
    # Severity
    # --------------------------------------------------

    def assign_severity(confidence):

        if confidence >= 0.90:
            return "High"

        elif confidence >= 0.70:
            return "Medium"

        else:
            return "Low"

    events["Severity"] = events["Confidence"].apply(
        assign_severity
    )

    # --------------------------------------------------
    # Rename network fields
    # --------------------------------------------------

    events.rename(
        columns={
            "frame.time": "Timestamp",
            "eth.src": "Source_MAC",
            "eth.dst": "Destination_MAC"
        },
        inplace=True
    )

    # --------------------------------------------------
    # Select SOC columns
    # --------------------------------------------------

    soc_columns = [
        "Event_ID",
        "Timestamp",
        "Protocol",
        "Detection_Source",
        "Event_Type",
        "Detection_Status",
        "Confidence",
        "Severity",
        "Source_MAC",
        "Destination_MAC",
        "Ground_Truth_Label",
        "Mode"
    ]

    events = events[soc_columns]

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    events.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    actual_attacks = (
        df["Ground_Truth_Label"] == "PTP Attack"
    ).sum()

    detected_attacks = (
        (events["Ground_Truth_Label"] == "PTP Attack")
    ).sum()

    false_alarms = (
        (events["Ground_Truth_Label"] == "Normal")
    ).sum()

    print("\n" + "=" * 60)
    print("SOC EVENT GENERATION COMPLETE")
    print("=" * 60)

    print(f"Total records       : {len(df):,}")
    print(f"Actual attack rows  : {actual_attacks:,}")
    print(f"Detected SOC events : {len(events):,}")
    print(f"Attack detections   : {detected_attacks:,}")
    print(f"False alarms        : {false_alarms:,}")

    print("\nSeverity distribution:")
    print(events["Severity"].value_counts())

    print(f"\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()