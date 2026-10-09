import pandas as pd
import numpy as np

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate


# ============================================================
# IEC-104 5-FOLD STRATIFIED CROSS-VALIDATION
# ============================================================

print("\nIEC-104 RANDOM FOREST CROSS-VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# 1. Paths
# ------------------------------------------------------------

DATA_FILE = Path(
    "data/processed/IEC104/iec104_train.csv"
)

RESULT_DIR = Path("results/metrics")
RESULT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. Load training dataset
# ------------------------------------------------------------

print("\nLoading training dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Dataset shape: {df.shape}")


# ------------------------------------------------------------
# 3. Separate features and target
# ------------------------------------------------------------

X = df.drop(columns=["Label"])
y = df["Label"]

print(f"\nFeatures: {X.shape[1]}")
print(f"Records : {X.shape[0]}")


# ------------------------------------------------------------
# 4. Create 5-fold stratified CV
# ------------------------------------------------------------

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


# ------------------------------------------------------------
# 5. Create Random Forest
# ------------------------------------------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)


# ------------------------------------------------------------
# 6. Define evaluation metrics
# ------------------------------------------------------------

scoring = {
    "accuracy": "accuracy",
    "balanced_accuracy": "balanced_accuracy",
    "macro_precision": "precision_macro",
    "macro_recall": "recall_macro",
    "macro_f1": "f1_macro",
    "weighted_f1": "f1_weighted"
}


# ------------------------------------------------------------
# 7. Run cross-validation
# ------------------------------------------------------------

print("\nRunning 5-fold cross-validation...")
print("This may take some time.")

results = cross_validate(
    model,
    X,
    y,
    cv=cv,
    scoring=scoring,
    n_jobs=1,
    return_train_score=False
)

print("Cross-validation completed.")


# ------------------------------------------------------------
# 8. Display fold-by-fold results
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FOLD-BY-FOLD RESULTS")
print("=" * 70)

for i in range(5):

    print(f"\nFold {i + 1}")

    print(
        f"Accuracy           : "
        f"{results['test_accuracy'][i]:.4f}"
    )

    print(
        f"Balanced Accuracy  : "
        f"{results['test_balanced_accuracy'][i]:.4f}"
    )

    print(
        f"Macro Precision    : "
        f"{results['test_macro_precision'][i]:.4f}"
    )

    print(
        f"Macro Recall       : "
        f"{results['test_macro_recall'][i]:.4f}"
    )

    print(
        f"Macro F1           : "
        f"{results['test_macro_f1'][i]:.4f}"
    )

    print(
        f"Weighted F1        : "
        f"{results['test_weighted_f1'][i]:.4f}"
    )


# ------------------------------------------------------------
# 9. Calculate mean and standard deviation
# ------------------------------------------------------------

metric_names = [
    "accuracy",
    "balanced_accuracy",
    "macro_precision",
    "macro_recall",
    "macro_f1",
    "weighted_f1"
]

summary = []

for metric in metric_names:

    values = results[f"test_{metric}"]

    summary.append({
        "Metric": metric,
        "Mean": np.mean(values),
        "Std": np.std(values, ddof=1)
    })


summary_df = pd.DataFrame(summary)


# ------------------------------------------------------------
# 10. Display summary
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("5-FOLD CROSS-VALIDATION SUMMARY")
print("=" * 70)

for _, row in summary_df.iterrows():

    print(
        f"{row['Metric']:<20} "
        f"{row['Mean']:.4f} ± {row['Std']:.4f}"
    )


# ------------------------------------------------------------
# 11. Save fold results
# ------------------------------------------------------------

fold_results = pd.DataFrame({
    "fold": [1, 2, 3, 4, 5],
    "accuracy": results["test_accuracy"],
    "balanced_accuracy": results["test_balanced_accuracy"],
    "macro_precision": results["test_macro_precision"],
    "macro_recall": results["test_macro_recall"],
    "macro_f1": results["test_macro_f1"],
    "weighted_f1": results["test_weighted_f1"]
})

fold_file = (
    RESULT_DIR /
    "random_forest_5fold_results.csv"
)

fold_results.to_csv(
    fold_file,
    index=False
)


# ------------------------------------------------------------
# 12. Save summary
# ------------------------------------------------------------

summary_file = (
    RESULT_DIR /
    "random_forest_5fold_summary.csv"
)

summary_df.to_csv(
    summary_file,
    index=False
)


# ------------------------------------------------------------
# 13. Final output
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("5-FOLD CROSS-VALIDATION COMPLETED")
print("=" * 70)

print(f"\nFold results saved to:")
print(fold_file)

print(f"\nSummary saved to:")
print(summary_file)