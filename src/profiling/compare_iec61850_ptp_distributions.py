import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

NORMAL_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "IEC61850"
    / "iec61850_ptp_ml_ready.csv"
)

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

OUTPUT_DIR = PROJECT_ROOT / "results" / "metrics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "iec61850_ptp_feature_distribution_comparison.csv"
)

print("=" * 70)
print("IEC-61850 PTP FEATURE DISTRIBUTION ANALYSIS")
print("=" * 70)

print("\nLoading ML dataset...")

df = pd.read_csv(NORMAL_FILE)

print(f"Total records: {len(df):,}")

normal = df[df["Label"] == 0].copy()
attack = df[df["Label"] == 1].copy()

print(f"Normal records: {len(normal):,}")
print(f"Attack records: {len(attack):,}")

results = []

print("\n" + "-" * 70)
print("FEATURE COMPARISON")
print("-" * 70)

for feature in FEATURES:

    normal_values = pd.to_numeric(
        normal[feature],
        errors="coerce"
    ).dropna()

    attack_values = pd.to_numeric(
        attack[feature],
        errors="coerce"
    ).dropna()

    normal_mean = normal_values.mean()
    attack_mean = attack_values.mean()

    normal_median = normal_values.median()
    attack_median = attack_values.median()

    normal_std = normal_values.std()
    attack_std = attack_values.std()

    normal_min = normal_values.min()
    attack_min = attack_values.min()

    normal_max = normal_values.max()
    attack_max = attack_values.max()

    # Cohen's d
    pooled_std = np.sqrt(
        (
            (len(normal_values) - 1) * normal_std ** 2
            +
            (len(attack_values) - 1) * attack_std ** 2
        )
        /
        (
            len(normal_values)
            +
            len(attack_values)
            -
            2
        )
    )

    if pooled_std > 0:
        cohens_d = (
            attack_mean - normal_mean
        ) / pooled_std
    else:
        cohens_d = 0.0

    results.append({
        "Feature": feature,
        "Normal_Mean": normal_mean,
        "Attack_Mean": attack_mean,
        "Normal_Median": normal_median,
        "Attack_Median": attack_median,
        "Normal_Std": normal_std,
        "Attack_Std": attack_std,
        "Normal_Min": normal_min,
        "Attack_Min": attack_min,
        "Normal_Max": normal_max,
        "Attack_Max": attack_max,
        "Cohens_d": cohens_d,
        "Absolute_Cohens_d": abs(cohens_d)
    })

result_df = pd.DataFrame(results)

result_df = result_df.sort_values(
    "Absolute_Cohens_d",
    ascending=False
)

print(
    result_df[
        [
            "Feature",
            "Normal_Mean",
            "Attack_Mean",
            "Normal_Median",
            "Attack_Median",
            "Cohens_d",
            "Absolute_Cohens_d"
        ]
    ].to_string(index=False)
)

print("\n" + "-" * 70)
print("TOP FEATURES BY DISTRIBUTION DIFFERENCE")
print("-" * 70)

print(
    result_df[
        [
            "Feature",
            "Absolute_Cohens_d"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nResults saved:")
print(OUTPUT_FILE)

print("\n" + "=" * 70)
print("DISTRIBUTION ANALYSIS COMPLETE")
print("=" * 70)