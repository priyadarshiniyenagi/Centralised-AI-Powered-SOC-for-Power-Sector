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
print("IEC-61850 PTP RAW CAPTURE TIMELINE ANALYSIS")
print("=" * 70)


def analyze_file(file_path, label):

    print("\n" + "-" * 70)
    print(label)
    print("-" * 70)

    print(f"File: {file_path}")

    df = pd.read_csv(
        file_path,
        usecols=[
            "frame.time",
            "frame.time_epoch",
            "frame.time_relative",
            "frame.number"
        ]
    )

    print(f"Records: {len(df):,}")

    print("\nFirst 5 records:")
    print(df.head().to_string(index=False))

    print("\nLast 5 records:")
    print(df.tail().to_string(index=False))

    print("\nTime statistics:")

    print(
        f"frame.time_relative min: "
        f"{pd.to_numeric(df['frame.time_relative'], errors='coerce').min()}"
    )

    print(
        f"frame.time_relative max: "
        f"{pd.to_numeric(df['frame.time_relative'], errors='coerce').max()}"
    )

    print(
        f"frame.number min: "
        f"{pd.to_numeric(df['frame.number'], errors='coerce').min()}"
    )

    print(
        f"frame.number max: "
        f"{pd.to_numeric(df['frame.number'], errors='coerce').max()}"
    )

    print("\nAbsolute time range:")

    print(
        "First frame.time:",
        df["frame.time"].iloc[0]
    )

    print(
        "Last frame.time:",
        df["frame.time"].iloc[-1]
    )

    print("\nRelative-time quantiles:")

    relative = pd.to_numeric(
        df["frame.time_relative"],
        errors="coerce"
    )

    print(
        relative.quantile(
            [0, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0]
        )
    )

    return df


normal_df = analyze_file(
    NORMAL_FILE,
    "NORMAL PTP CAPTURE"
)

attack_df = analyze_file(
    ATTACK_FILE,
    "PTP ATTACK CAPTURE"
)


print("\n" + "=" * 70)
print("TIMELINE COMPARISON")
print("=" * 70)

normal_relative = pd.to_numeric(
    normal_df["frame.time_relative"],
    errors="coerce"
)

attack_relative = pd.to_numeric(
    attack_df["frame.time_relative"],
    errors="coerce"
)

print("\nNormal capture duration:")
print(
    f"{normal_relative.min():.6f} "
    f"to "
    f"{normal_relative.max():.6f} seconds"
)

print("\nAttack capture duration:")
print(
    f"{attack_relative.min():.6f} "
    f"to "
    f"{attack_relative.max():.6f} seconds"
)

print("\nNormal records:", len(normal_df))
print("Attack records:", len(attack_df))

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)