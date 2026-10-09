import pandas as pd
import joblib

from pathlib import Path
from sklearn.metrics import confusion_matrix


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TEST_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "IEC61850"
    / "iec61850_ptp_test.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "saved_models"
    / "iec61850_ptp_random_forest.joblib"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "metrics"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


MISSED_ATTACKS_FILE = (
    OUTPUT_DIR
    / "iec61850_ptp_missed_attacks.csv"
)

FALSE_ALARMS_FILE = (
    OUTPUT_DIR
    / "iec61850_ptp_false_alarms.csv"
)


print("=" * 70)
print("IEC-61850 PTP ERROR ANALYSIS")
print("=" * 70)


# ---------------------------------------------------------
# Load test data
# ---------------------------------------------------------

print("\nLoading test dataset...")

df = pd.read_csv(TEST_FILE)

X = df.drop(columns=["Label"])
y = df["Label"]


print(f"Test records: {len(df):,}")
print(f"Features: {X.shape[1]}")


# ---------------------------------------------------------
# Load model
# ---------------------------------------------------------

print("\nLoading Random Forest model...")

model = joblib.load(MODEL_FILE)


# ---------------------------------------------------------
# Predictions
# ---------------------------------------------------------

print("Generating predictions...")

predictions = model.predict(X)

probabilities = model.predict_proba(X)[:, 1]


# ---------------------------------------------------------
# Add predictions
# ---------------------------------------------------------

analysis_df = df.copy()

analysis_df["Predicted_Label"] = predictions
analysis_df["Attack_Probability"] = probabilities


# ---------------------------------------------------------
# Confusion matrix
# ---------------------------------------------------------

cm = confusion_matrix(
    y,
    predictions
)

print("\nConfusion Matrix:")
print(cm)


# ---------------------------------------------------------
# Identify errors
# ---------------------------------------------------------

missed_attacks = analysis_df[
    (analysis_df["Label"] == 1)
    & (analysis_df["Predicted_Label"] == 0)
].copy()

false_alarms = analysis_df[
    (analysis_df["Label"] == 0)
    & (analysis_df["Predicted_Label"] == 1)
].copy()


# ---------------------------------------------------------
# Print error counts
# ---------------------------------------------------------

print("\n" + "-" * 70)

print(
    f"Missed PTP attacks: {len(missed_attacks)}"
)

print(
    f"False alarms:       {len(false_alarms)}"
)


# ---------------------------------------------------------
# Missed attacks
# ---------------------------------------------------------

print("\n" + "-" * 70)

print("MISSED PTP ATTACKS")

if len(missed_attacks) > 0:

    print(
        missed_attacks[
            [
                "Attack_Probability",
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
                "ptp.v2.versionptp"
            ]
        ].to_string(index=False)
    )

else:

    print("No missed attacks.")


# ---------------------------------------------------------
# False alarms
# ---------------------------------------------------------

print("\n" + "-" * 70)

print("FALSE ALARMS")

if len(false_alarms) > 0:

    print(
        false_alarms[
            [
                "Attack_Probability",
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
                "ptp.v2.versionptp"
            ]
        ].to_string(index=False)
    )

else:

    print("No false alarms.")


# ---------------------------------------------------------
# Save errors
# ---------------------------------------------------------

missed_attacks.to_csv(
    MISSED_ATTACKS_FILE,
    index=False
)

false_alarms.to_csv(
    FALSE_ALARMS_FILE,
    index=False
)


# ---------------------------------------------------------
# Feature importance
# ---------------------------------------------------------

print("\n" + "-" * 70)

print("TOP FEATURE IMPORTANCE")

feature_importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
}).sort_values(
    "Importance",
    ascending=False
)

print(
    feature_importance.head(15).to_string(
        index=False
    )
)


# ---------------------------------------------------------
# Save feature importance
# ---------------------------------------------------------

feature_importance.to_csv(
    OUTPUT_DIR
    / "iec61850_ptp_feature_importance.csv",
    index=False
)


print("\nMissed attacks saved:")
print(MISSED_ATTACKS_FILE)

print("\nFalse alarms saved:")
print(FALSE_ALARMS_FILE)


print("\n" + "=" * 70)
print("IEC-61850 PTP ERROR ANALYSIS COMPLETE")
print("=" * 70)