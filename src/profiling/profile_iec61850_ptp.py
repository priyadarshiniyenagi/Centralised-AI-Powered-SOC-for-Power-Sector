import pandas as pd
from pathlib import Path


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


print("=" * 70)
print("IEC-61850 PTP DATASET PROFILING")
print("=" * 70)


# ---------------------------------------------------------
# Profile normal dataset
# ---------------------------------------------------------

print("\nLoading normal PTP dataset...")

normal = pd.read_csv(NORMAL_FILE)

print(f"Normal records: {len(normal):,}")
print(f"Normal columns: {len(normal.columns):,}")

print("\nNormal labels:")
print(normal["Label"].value_counts(dropna=False))

print("\nNormal non-empty columns:")

non_empty = normal.notna().sum()

print(
    non_empty[non_empty > 0]
    .sort_values(ascending=False)
    .to_string()
)


# ---------------------------------------------------------
# Profile attack dataset
# ---------------------------------------------------------

print("\n" + "-" * 70)

print("\nLoading PTP attack dataset...")

attack = pd.read_csv(ATTACK_FILE)

print(f"Attack records: {len(attack):,}")
print(f"Attack columns: {len(attack.columns):,}")

print("\nAttack labels:")
print(attack["Label"].value_counts(dropna=False))

print("\nAttack non-empty columns:")

non_empty_attack = attack.notna().sum()

print(
    non_empty_attack[non_empty_attack > 0]
    .sort_values(ascending=False)
    .to_string()
)


# ---------------------------------------------------------
# Compare columns
# ---------------------------------------------------------

print("\n" + "-" * 70)

print("\nColumn comparison:")

normal_columns = set(normal.columns)
attack_columns = set(attack.columns)

print(f"Common columns: {len(normal_columns & attack_columns):,}")
print(f"Normal-only columns: {len(normal_columns - attack_columns):,}")
print(f"Attack-only columns: {len(attack_columns - normal_columns):,}")


# ---------------------------------------------------------
# Dataset summary
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("IEC-61850 PTP PROFILING COMPLETE")
print("=" * 70)