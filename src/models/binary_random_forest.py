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
    classification_report,
    confusion_matrix
)


# ============================================================
# IEC-104 BINARY INTRUSION DETECTION
# Normal vs Attack
# ============================================================

print("\nIEC-104 BINARY INTRUSION DETECTION")
print("=" * 70)


# ------------------------------------------------------------
# 1. Paths
# ------------------------------------------------------------

TRAIN_FILE = Path("data/processed/IEC104/iec104_train.csv")
TEST_FILE = Path("data/processed/IEC104/iec104_test.csv")

MODEL_DIR = Path("saved_models")
RESULT_DIR = Path("results/metrics")

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. Load datasets
# ------------------------------------------------------------

print("\nLoading training dataset...")
train_df = pd.read_csv(TRAIN_FILE)

print("Loading testing dataset...")
test_df = pd.read_csv(TEST_FILE)

print(f"\nTraining shape: {train_df.shape}")
print(f"Testing shape : {test_df.shape}")


# ------------------------------------------------------------
# 3. Convert multiclass labels to binary labels
# ------------------------------------------------------------

print("\nConverting labels to binary classes...")

train_df["BinaryLabel"] = train_df["Label"].apply(
    lambda x: 0 if x == "attackfree" else 1
)

test_df["BinaryLabel"] = test_df["Label"].apply(
    lambda x: 0 if x == "attackfree" else 1
)


# ------------------------------------------------------------
# 4. Separate features and target
# ------------------------------------------------------------

X_train = train_df.drop(
    columns=["Label", "BinaryLabel"]
)

y_train = train_df["BinaryLabel"]

X_test = test_df.drop(
    columns=["Label", "BinaryLabel"]
)

y_test = test_df["BinaryLabel"]


# ------------------------------------------------------------
# 5. Display binary distribution
# ------------------------------------------------------------

print("\nBinary training distribution:")

print(
    y_train
    .map({0: "Normal", 1: "Attack"})
    .value_counts()
)

print("\nBinary testing distribution:")

print(
    y_test
    .map({0: "Normal", 1: "Attack"})
    .value_counts()
)


# ------------------------------------------------------------
# 6. Train Random Forest
# ------------------------------------------------------------

print("\nTraining binary Random Forest...")
print("Using class_weight='balanced'")

model = RandomForestClassifier(
    n_estimators=100,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# ------------------------------------------------------------
# 7. Predictions
# ------------------------------------------------------------

print("\nGenerating predictions...")

y_pred = model.predict(X_test)

# Probability of Attack class
y_prob = model.predict_proba(X_test)[:, 1]


# ------------------------------------------------------------
# 8. Calculate metrics
# ------------------------------------------------------------

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

roc_auc = roc_auc_score(
    y_test,
    y_prob
)

pr_auc = average_precision_score(
    y_test,
    y_prob
)


# ------------------------------------------------------------
# 9. Display performance
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("BINARY RANDOM FOREST PERFORMANCE")
print("=" * 70)

print(f"\nAccuracy            : {accuracy:.4f}")
print(f"Balanced Accuracy  : {balanced_accuracy:.4f}")
print(f"Precision           : {precision:.4f}")
print(f"Recall              : {recall:.4f}")
print(f"F1 Score            : {f1:.4f}")
print(f"ROC-AUC             : {roc_auc:.4f}")
print(f"PR-AUC              : {pr_auc:.4f}")


# ------------------------------------------------------------
# 10. Classification report
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

target_names = [
    "Normal",
    "Attack"
]

report = classification_report(
    y_test,
    y_pred,
    target_names=target_names,
    zero_division=0
)

print(report)


# ------------------------------------------------------------
# 11. Confusion matrix
# ------------------------------------------------------------

cm = confusion_matrix(
    y_test,
    y_pred
)

cm_df = pd.DataFrame(
    cm,
    index=["Actual Normal", "Actual Attack"],
    columns=["Predicted Normal", "Predicted Attack"]
)

print("\n" + "=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

print(cm_df)


# ------------------------------------------------------------
# 12. Save metrics
# ------------------------------------------------------------

metrics = {
    "accuracy": accuracy,
    "balanced_accuracy": balanced_accuracy,
    "precision": precision,
    "recall": recall,
    "f1": f1,
    "roc_auc": roc_auc,
    "pr_auc": pr_auc
}

metrics_df = pd.DataFrame(
    [metrics]
)

metrics_file = (
    RESULT_DIR /
    "binary_random_forest_metrics.csv"
)

metrics_df.to_csv(
    metrics_file,
    index=False
)


# ------------------------------------------------------------
# 13. Save confusion matrix
# ------------------------------------------------------------

cm_file = (
    RESULT_DIR /
    "binary_random_forest_confusion_matrix.csv"
)

cm_df.to_csv(
    cm_file
)


# ------------------------------------------------------------
# 14. Save model
# ------------------------------------------------------------

model_file = (
    MODEL_DIR /
    "binary_random_forest.joblib"
)

joblib.dump(
    model,
    model_file
)


# ------------------------------------------------------------
# 15. Save feature importance
# ------------------------------------------------------------

feature_importance = pd.DataFrame({
    "Feature": X_train.columns,
    "Importance": model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="Importance",
    ascending=False
)

importance_file = (
    RESULT_DIR /
    "binary_random_forest_feature_importance.csv"
)

feature_importance.to_csv(
    importance_file,
    index=False
)


# ------------------------------------------------------------
# 16. Final output
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("BINARY RANDOM FOREST COMPLETED")
print("=" * 70)

print(f"\nMetrics saved to:")
print(metrics_file)

print(f"\nConfusion matrix saved to:")
print(cm_file)

print(f"\nModel saved to:")
print(model_file)

print(f"\nFeature importance saved to:")
print(importance_file)