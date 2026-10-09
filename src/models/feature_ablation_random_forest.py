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
    classification_report,
    confusion_matrix
)


# ============================================================
# IEC-104 FEATURE ABLATION EXPERIMENT
# Remove the two most important features
# ============================================================

print("\nIEC-104 FEATURE ABLATION EXPERIMENT")
print("=" * 70)


# ------------------------------------------------------------
# 1. Paths
# ------------------------------------------------------------

TRAIN_FILE = Path("data/processed/IEC104/iec104_train.csv")
TEST_FILE = Path("data/processed/IEC104/iec104_test.csv")

RESULT_DIR = Path("results/metrics")
MODEL_DIR = Path("saved_models")

RESULT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. Features to remove
# ------------------------------------------------------------

FEATURES_TO_REMOVE = [
    "Dst Port",
    "FWD Init Win Bytes"
]

print("\nFeatures being removed:")

for feature in FEATURES_TO_REMOVE:
    print(f"- {feature}")


# ------------------------------------------------------------
# 3. Load datasets
# ------------------------------------------------------------

print("\nLoading training dataset...")
train_df = pd.read_csv(TRAIN_FILE)

print("Loading testing dataset...")
test_df = pd.read_csv(TEST_FILE)


# ------------------------------------------------------------
# 4. Separate features and target
# ------------------------------------------------------------

X_train = train_df.drop(columns=["Label"])
y_train = train_df["Label"]

X_test = test_df.drop(columns=["Label"])
y_test = test_df["Label"]


# ------------------------------------------------------------
# 5. Remove selected features
# ------------------------------------------------------------

X_train = X_train.drop(
    columns=FEATURES_TO_REMOVE
)

X_test = X_test.drop(
    columns=FEATURES_TO_REMOVE
)


print("\nDataset after feature removal:")
print(f"Training shape: {X_train.shape}")
print(f"Testing shape : {X_test.shape}")

print(f"Remaining features: {X_train.shape[1]}")


# ------------------------------------------------------------
# 6. Train Random Forest
# ------------------------------------------------------------

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=100,
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

macro_precision = precision_score(
    y_test,
    y_pred,
    average="macro",
    zero_division=0
)

macro_recall = recall_score(
    y_test,
    y_pred,
    average="macro",
    zero_division=0
)

macro_f1 = f1_score(
    y_test,
    y_pred,
    average="macro",
    zero_division=0
)

weighted_f1 = f1_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)


# ------------------------------------------------------------
# 9. Overall performance
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FEATURE ABLATION PERFORMANCE")
print("=" * 70)

print(f"\nAccuracy            : {accuracy:.4f}")
print(f"Balanced Accuracy  : {balanced_accuracy:.4f}")
print(f"Macro Precision    : {macro_precision:.4f}")
print(f"Macro Recall       : {macro_recall:.4f}")
print(f"Macro F1           : {macro_f1:.4f}")
print(f"Weighted F1        : {weighted_f1:.4f}")


# ------------------------------------------------------------
# 10. Classification report
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

report = classification_report(
    y_test,
    y_pred,
    zero_division=0
)

print(report)


# ------------------------------------------------------------
# 11. Confusion matrix
# ------------------------------------------------------------

labels = sorted(y_test.unique())

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=labels
)

cm_df = pd.DataFrame(
    cm,
    index=labels,
    columns=labels
)

print("\n" + "=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

print(cm_df)


# ------------------------------------------------------------
# 12. Save metrics
# ------------------------------------------------------------

metrics = {
    "removed_features": ", ".join(FEATURES_TO_REMOVE),
    "remaining_features": X_train.shape[1],
    "accuracy": accuracy,
    "balanced_accuracy": balanced_accuracy,
    "macro_precision": macro_precision,
    "macro_recall": macro_recall,
    "macro_f1": macro_f1,
    "weighted_f1": weighted_f1
}

metrics_df = pd.DataFrame([metrics])

metrics_file = (
    RESULT_DIR /
    "feature_ablation_random_forest_metrics.csv"
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
    "feature_ablation_random_forest_confusion_matrix.csv"
)

cm_df.to_csv(
    cm_file
)


# ------------------------------------------------------------
# 14. Save model
# ------------------------------------------------------------

model_file = (
    MODEL_DIR /
    "feature_ablation_random_forest.joblib"
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
    "feature_ablation_random_forest_feature_importance.csv"
)

feature_importance.to_csv(
    importance_file,
    index=False
)


# ------------------------------------------------------------
# 16. Final output
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FEATURE ABLATION EXPERIMENT COMPLETED")
print("=" * 70)

print(f"\nMetrics saved to:")
print(metrics_file)

print(f"\nConfusion matrix saved to:")
print(cm_file)

print(f"\nModel saved to:")
print(model_file)

print(f"\nFeature importance saved to:")
print(importance_file)