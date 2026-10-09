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

TRAIN_FILE = PROJECT_ROOT / "data" / "processed" / "IEC61850" / "iec61850_ptp_train.csv"
TEST_FILE = PROJECT_ROOT / "data" / "processed" / "IEC61850" / "iec61850_ptp_test.csv"

MODEL_FILE = PROJECT_ROOT / "saved_models" / "iec61850_ptp_ablation_no_time_relative.joblib"
METRICS_FILE = PROJECT_ROOT / "results" / "metrics" / "iec61850_ptp_ablation_no_time_relative_metrics.csv"
CM_FILE = PROJECT_ROOT / "results" / "metrics" / "iec61850_ptp_ablation_no_time_relative_confusion_matrix.csv"

print("=" * 70)
print("IEC-61850 PTP FEATURE ABLATION")
print("Removing: frame.time_relative")
print("=" * 70)

print("\nLoading datasets...")

train_df = pd.read_csv(TRAIN_FILE)
test_df = pd.read_csv(TEST_FILE)

X_train = train_df.drop(columns=["Label"])
y_train = train_df["Label"]

X_test = test_df.drop(columns=["Label"])
y_test = test_df["Label"]

print(f"Original features: {X_train.shape[1]}")

# Remove highly dominant timing feature
X_train = X_train.drop(columns=["frame.time_relative"])
X_test = X_test.drop(columns=["frame.time_relative"])

print(f"Features after removal: {X_train.shape[1]}")

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("Training complete.")

print("\nGenerating predictions...")

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, predictions)
balanced_accuracy = balanced_accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions, zero_division=0)
recall = recall_score(y_test, predictions, zero_division=0)
f1 = f1_score(y_test, predictions, zero_division=0)
roc_auc = roc_auc_score(y_test, probabilities)
pr_auc = average_precision_score(y_test, probabilities)

cm = confusion_matrix(y_test, predictions)

tn, fp, fn, tp = cm.ravel()

print("\n" + "=" * 70)
print("RESULTS")
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

print("\n" + "-" * 70)
print("FEATURE IMPORTANCE")
print("-" * 70)

feature_importance = pd.DataFrame({
    "Feature": X_train.columns,
    "Importance": model.feature_importances_
}).sort_values("Importance", ascending=False)

print(feature_importance.head(15).to_string(index=False))

# Save model
joblib.dump(model, MODEL_FILE)

# Save metrics
metrics = pd.DataFrame([{
    "Model": "Random Forest - No frame.time_relative",
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

metrics.to_csv(METRICS_FILE, index=False)

# Save confusion matrix
cm_df = pd.DataFrame(
    cm,
    index=["Actual Normal", "Actual Attack"],
    columns=["Predicted Normal", "Predicted Attack"]
)

cm_df.to_csv(CM_FILE)

print("\nModel saved:")
print(MODEL_FILE)

print("\nMetrics saved:")
print(METRICS_FILE)

print("\nConfusion matrix saved:")
print(CM_FILE)

print("\n" + "=" * 70)
print("FEATURE ABLATION COMPLETE")
print("=" * 70)