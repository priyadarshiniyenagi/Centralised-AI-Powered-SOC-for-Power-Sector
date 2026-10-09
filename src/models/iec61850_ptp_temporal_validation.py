import pandas as pd
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "IEC61850"
    / "iec61850_ptp_ml_ready.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "saved_models"
    / "iec61850_ptp_temporal_rf.joblib"
)

METRICS_FILE = (
    PROJECT_ROOT
    / "results"
    / "metrics"
    / "iec61850_ptp_temporal_validation_metrics.csv"
)

CM_FILE = (
    PROJECT_ROOT
    / "results"
    / "metrics"
    / "iec61850_ptp_temporal_validation_confusion_matrix.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "results" / "metrics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("IEC-61850 PTP TEMPORAL VALIDATION")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Total records: {len(df):,}")
print(f"Total columns: {df.shape[1]}")

# ------------------------------------------------------------------
# IMPORTANT:
# The ML-ready dataset does not contain the original timestamp.
# Therefore this experiment cannot perform true chronological
# validation from this file.
#
# We will reconstruct a stress-test split from the existing
# stratified dataset only if an ordering column is available.
# ------------------------------------------------------------------

if "frame.time_relative" not in df.columns:
    raise ValueError(
        "frame.time_relative is missing. "
        "Cannot perform the intended temporal validation."
    )

# Sort by frame-relative time.
# This provides an ordered stress-test split, although it is NOT
# equivalent to a true capture/session-aware temporal split.

print("\nSorting records by frame.time_relative...")

df = df.sort_values(
    by="frame.time_relative"
).reset_index(drop=True)

# ------------------------------------------------------------------
# 80% earliest records -> training
# 20% latest records -> testing
# ------------------------------------------------------------------

split_index = int(len(df) * 0.80)

train_df = df.iloc[:split_index].copy()
test_df = df.iloc[split_index:].copy()

print("\nTemporal split:")
print(f"Training records: {len(train_df):,}")
print(f"Testing records:  {len(test_df):,}")

print("\nTraining class distribution:")
print(train_df["Label"].value_counts())

print("\nTesting class distribution:")
print(test_df["Label"].value_counts())

# ------------------------------------------------------------------
# Features
# ------------------------------------------------------------------

X_train = train_df.drop(columns=["Label"])
y_train = train_df["Label"]

X_test = test_df.drop(columns=["Label"])
y_test = test_df["Label"]

print(f"\nFeatures: {X_train.shape[1]}")

# ------------------------------------------------------------------
# Check whether both classes exist in train/test
# ------------------------------------------------------------------

if y_train.nunique() < 2:
    raise ValueError(
        "Training set contains only one class. "
        "Temporal split is not suitable for this dataset."
    )

if y_test.nunique() < 2:
    raise ValueError(
        "Testing set contains only one class. "
        "Temporal split is not suitable for this dataset."
    )

# ------------------------------------------------------------------
# Train Random Forest
# ------------------------------------------------------------------

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("Training complete.")

# ------------------------------------------------------------------
# Prediction
# ------------------------------------------------------------------

print("\nGenerating predictions...")

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

# ------------------------------------------------------------------
# Metrics
# ------------------------------------------------------------------

accuracy = accuracy_score(y_test, predictions)

balanced_accuracy = balanced_accuracy_score(
    y_test,
    predictions
)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    probabilities
)

pr_auc = average_precision_score(
    y_test,
    probabilities
)

cm = confusion_matrix(
    y_test,
    predictions
)

tn, fp, fn, tp = cm.ravel()

# ------------------------------------------------------------------
# Results
# ------------------------------------------------------------------

print("\n" + "=" * 70)
print("TEMPORAL VALIDATION RESULTS")
print("=" * 70)

print(f"Accuracy:            {accuracy:.4f}")
print(f"Balanced Accuracy:   {balanced_accuracy:.4f}")
print(f"Precision:           {precision:.4f}")
print(f"Recall:              {recall:.4f}")
print(f"F1 Score:            {f1:.4f}")
print(f"ROC-AUC:             {roc_auc:.4f}")
print(f"PR-AUC:              {pr_auc:.4f}")

print("\nConfusion Matrix:")
print(cm)

print(f"\nTrue Negatives:  {tn}")
print(f"False Positives: {fp}")
print(f"False Negatives: {fn}")
print(f"True Positives:  {tp}")

print(f"\nMissed attacks: {fn}")
print(f"False alarms:   {fp}")

# ------------------------------------------------------------------
# Feature importance
# ------------------------------------------------------------------

print("\n" + "-" * 70)
print("TOP FEATURE IMPORTANCE")
print("-" * 70)

feature_importance = pd.DataFrame({
    "Feature": X_train.columns,
    "Importance": model.feature_importances_
}).sort_values(
    "Importance",
    ascending=False
)

print(
    feature_importance
    .head(15)
    .to_string(index=False)
)

# ------------------------------------------------------------------
# Save model
# ------------------------------------------------------------------

joblib.dump(
    model,
    MODEL_FILE
)

# ------------------------------------------------------------------
# Save metrics
# ------------------------------------------------------------------

metrics = pd.DataFrame([{
    "Model": "IEC61850 PTP Random Forest - Temporal Stress Test",
    "Train_Records": len(train_df),
    "Test_Records": len(test_df),
    "Features": X_train.shape[1],
    "Accuracy": accuracy,
    "Balanced_Accuracy": balanced_accuracy,
    "Precision": precision,
    "Recall": recall,
    "F1": f1,
    "ROC_AUC": roc_auc,
    "PR_AUC": pr_auc,
    "False_Alarms": fp,
    "Missed_Attacks": fn
}])

metrics.to_csv(
    METRICS_FILE,
    index=False
)

# ------------------------------------------------------------------
# Save confusion matrix
# ------------------------------------------------------------------

cm_df = pd.DataFrame(
    cm,
    index=[
        "Actual Normal",
        "Actual Attack"
    ],
    columns=[
        "Predicted Normal",
        "Predicted Attack"
    ]
)

cm_df.to_csv(
    CM_FILE
)

print("\nModel saved:")
print(MODEL_FILE)

print("\nMetrics saved:")
print(METRICS_FILE)

print("\nConfusion matrix saved:")
print(CM_FILE)

print("\n" + "=" * 70)
print("TEMPORAL VALIDATION COMPLETE")
print("=" * 70)