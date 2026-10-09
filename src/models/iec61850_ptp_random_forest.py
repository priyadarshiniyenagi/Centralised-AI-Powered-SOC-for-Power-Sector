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
    confusion_matrix,
    classification_report
)


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRAIN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "IEC61850"
    / "iec61850_ptp_train.csv"
)

TEST_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "IEC61850"
    / "iec61850_ptp_test.csv"
)

MODEL_DIR = PROJECT_ROOT / "saved_models"
METRICS_DIR = PROJECT_ROOT / "results" / "metrics"

MODEL_DIR.mkdir(exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_DIR / "iec61850_ptp_random_forest.joblib"

METRICS_FILE = (
    METRICS_DIR
    / "iec61850_ptp_random_forest_metrics.csv"
)

CONFUSION_FILE = (
    METRICS_DIR
    / "iec61850_ptp_random_forest_confusion_matrix.csv"
)


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

print("=" * 70)
print("IEC-61850 PTP RANDOM FOREST")
print("=" * 70)

print("\nLoading training data...")

train_df = pd.read_csv(TRAIN_FILE)

print(f"Training records: {len(train_df):,}")


print("\nLoading testing data...")

test_df = pd.read_csv(TEST_FILE)

print(f"Testing records: {len(test_df):,}")


# ---------------------------------------------------------
# Separate features and labels
# ---------------------------------------------------------

X_train = train_df.drop(columns=["Label"])
y_train = train_df["Label"]

X_test = test_df.drop(columns=["Label"])
y_test = test_df["Label"]


print(f"\nFeatures: {X_train.shape[1]}")


# ---------------------------------------------------------
# Train model
# ---------------------------------------------------------

print("\nTraining class-weighted Random Forest...")

model = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)


# ---------------------------------------------------------
# Predictions
# ---------------------------------------------------------

print("\nGenerating predictions...")

y_pred = model.predict(X_test)

y_prob = model.predict_proba(X_test)[:, 1]


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)

balanced_accuracy = balanced_accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

macro_f1 = f1_score(
    y_test,
    y_pred,
    average="macro",
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_prob
)

pr_auc = average_precision_score(
    y_test,
    y_prob
)


# ---------------------------------------------------------
# Print metrics
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("MODEL RESULTS")
print("=" * 70)

print(f"Accuracy:           {accuracy:.4f}")
print(f"Balanced Accuracy:  {balanced_accuracy:.4f}")
print(f"Precision:          {precision:.4f}")
print(f"Recall:             {recall:.4f}")
print(f"F1 Score:           {f1:.4f}")
print(f"Macro F1:           {macro_f1:.4f}")
print(f"ROC-AUC:            {roc_auc:.4f}")
print(f"PR-AUC:             {pr_auc:.4f}")


# ---------------------------------------------------------
# Classification report
# ---------------------------------------------------------

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Normal",
            "PTP Attack"
        ],
        zero_division=0
    )
)


# ---------------------------------------------------------
# Confusion matrix
# ---------------------------------------------------------

cm = confusion_matrix(
    y_test,
    y_pred
)

print("Confusion Matrix:")
print(cm)


# ---------------------------------------------------------
# Save metrics
# ---------------------------------------------------------

metrics = pd.DataFrame({
    "Metric": [
        "Accuracy",
        "Balanced Accuracy",
        "Precision",
        "Recall",
        "F1",
        "Macro F1",
        "ROC-AUC",
        "PR-AUC"
    ],
    "Value": [
        accuracy,
        balanced_accuracy,
        precision,
        recall,
        f1,
        macro_f1,
        roc_auc,
        pr_auc
    ]
})

metrics.to_csv(
    METRICS_FILE,
    index=False
)


# ---------------------------------------------------------
# Save confusion matrix
# ---------------------------------------------------------

cm_df = pd.DataFrame(
    cm,
    index=["Actual_Normal", "Actual_Attack"],
    columns=["Predicted_Normal", "Predicted_Attack"]
)

cm_df.to_csv(
    CONFUSION_FILE
)


# ---------------------------------------------------------
# Feature importance
# ---------------------------------------------------------

feature_importance = pd.DataFrame({
    "Feature": X_train.columns,
    "Importance": model.feature_importances_
}).sort_values(
    "Importance",
    ascending=False
)

feature_importance.to_csv(
    METRICS_DIR / "iec61850_ptp_feature_importance.csv",
    index=False
)


# ---------------------------------------------------------
# Save model
# ---------------------------------------------------------

joblib.dump(
    model,
    MODEL_FILE
)


print("\nModel saved:")
print(MODEL_FILE)

print("\nMetrics saved:")
print(METRICS_FILE)

print("\nConfusion matrix saved:")
print(CONFUSION_FILE)

print("\n" + "=" * 70)
print("IEC-61850 PTP RANDOM FOREST COMPLETE")
print("=" * 70)