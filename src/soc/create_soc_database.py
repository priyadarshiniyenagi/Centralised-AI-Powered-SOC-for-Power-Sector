import sqlite3
from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "soc"
    / "iec104_prioritized_alerts.csv"
)

DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_FILE = DATABASE_DIR / "soc.db"


# ---------------------------------------------------------
# Load prioritized alerts
# ---------------------------------------------------------

print("=" * 70)
print("SOC DATABASE CREATION")
print("=" * 70)

print("\nLoading prioritized alerts...")

df = pd.read_csv(INPUT_FILE)

print(f"Total alerts: {len(df)}")


# ---------------------------------------------------------
# Create SQLite database
# ---------------------------------------------------------

print("\nCreating SQLite database...")

connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()


# ---------------------------------------------------------
# Create incidents table
# ---------------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS soc_incidents (
    incident_id TEXT PRIMARY KEY,
    protocol TEXT,
    attack_type TEXT,
    event_count INTEGER,
    duration_seconds REAL,
    severity TEXT,
    priority_score INTEGER,
    priority TEXT,
    start_time TEXT,
    end_time TEXT,
    source_count INTEGER,
    destination_count INTEGER,
    recommended_action TEXT
)
""")


# ---------------------------------------------------------
# Insert data
# ---------------------------------------------------------

for _, row in df.iterrows():

    cursor.execute("""
    INSERT OR REPLACE INTO soc_incidents (
        incident_id,
        protocol,
        attack_type,
        event_count,
        duration_seconds,
        severity,
        priority_score,
        priority,
        start_time,
        end_time,
        source_count,
        destination_count,
        recommended_action
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["Incident_ID"],
        "IEC-104",
        row["Attack_Type"],
        int(row["Event_Count"]),
        float(row["Duration_Seconds"]),
        row["Severity"],
        int(row["Priority_Score"]),
        row["Priority"],
        row["Start_Time"],
        row["End_Time"],
        int(row["Source_Count"]),
int(row["Destination_Count"]),
        row["Recommended_Action"]
    ))


# ---------------------------------------------------------
# Commit
# ---------------------------------------------------------

connection.commit()


# ---------------------------------------------------------
# Verify database
# ---------------------------------------------------------

cursor.execute("SELECT COUNT(*) FROM soc_incidents")

count = cursor.fetchone()[0]

print(f"\nRecords inserted: {count}")

print("\nPriority distribution:")

result = pd.read_sql_query("""
SELECT Priority, COUNT(*) AS Count
FROM soc_incidents
GROUP BY Priority
ORDER BY Count DESC
""", connection)

print(result.to_string(index=False))


# ---------------------------------------------------------
# Close
# ---------------------------------------------------------

connection.close()

print("\nDatabase saved:")
print(DATABASE_FILE)

print("\n" + "=" * 70)
print("SOC DATABASE CREATION COMPLETE")
print("=" * 70)