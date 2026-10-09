import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "soc"
    / "prioritized_soc_alerts.csv"
)

DATABASE_FILE = (
    PROJECT_ROOT
    / "database"
    / "soc.db"
)


# ============================================================
# LOAD PRIORITIZED INCIDENTS
# ============================================================

print("=" * 60)
print("UPDATING SOC SQLITE DATABASE")
print("=" * 60)

print("\nLoading prioritized incidents...")

incidents = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(
    f"Incidents loaded: {len(incidents)}"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

DATABASE_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

connection = sqlite3.connect(
    DATABASE_FILE
)

cursor = connection.cursor()


# ============================================================
# CREATE / RECREATE INCIDENT TABLE
# ============================================================

cursor.execute(
    """
    DROP TABLE IF EXISTS soc_incidents
    """
)


cursor.execute(
    """
    CREATE TABLE soc_incidents (

        incident_id TEXT PRIMARY KEY,

        protocol TEXT,

        event_type TEXT,

        detection_source TEXT,

        event_count INTEGER,

        start_time TEXT,

        end_time TEXT,

        duration_seconds REAL,

        severity TEXT,

        priority_score INTEGER,

        priority TEXT,

        source_count INTEGER,

        destination_count INTEGER,

        recommended_action TEXT

    )
    """
)


# ============================================================
# INSERT INCIDENTS
# ============================================================

insert_sql = """
INSERT INTO soc_incidents (
    incident_id,
    protocol,
    event_type,
    detection_source,
    event_count,
    start_time,
    end_time,
    duration_seconds,
    severity,
    priority_score,
    priority,
    source_count,
    destination_count,
    recommended_action
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


for _, row in incidents.iterrows():

    cursor.execute(
        insert_sql,
        (
            row["Incident_ID"],
            row["Protocol"],
            row["SOC_Event_Type"],
            row["Detection_Source"],
            int(row["Event_Count"]),
            row["Start_Time"],
            row["End_Time"],
            float(row["Duration_Seconds"]),
            row["Severity"],
            int(row["Priority_Score"]),
            row["Priority"],
            int(row["Source_Count"]),
            int(row["Destination_Count"]),
            row["Recommended_Action"]
        )
    )


# ============================================================
# COMMIT
# ============================================================

connection.commit()


# ============================================================
# VERIFY DATABASE
# ============================================================

cursor.execute(
    "SELECT COUNT(*) FROM soc_incidents"
)

count = cursor.fetchone()[0]


print("\n" + "=" * 60)
print("DATABASE UPDATE COMPLETE")
print("=" * 60)

print(
    f"Records inserted: {count}"
)


print("\nPriority distribution:")

priority_df = pd.read_sql_query(
    """
    SELECT priority, COUNT(*) AS count
    FROM soc_incidents
    GROUP BY priority
    ORDER BY count DESC
    """,
    connection
)

print(
    priority_df.to_string(index=False)
)


print("\nProtocol distribution:")

protocol_df = pd.read_sql_query(
    """
    SELECT protocol, COUNT(*) AS count
    FROM soc_incidents
    GROUP BY protocol
    """,
    connection
)

print(
    protocol_df.to_string(index=False)
)


# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()


print("\nDatabase:")
print(DATABASE_FILE)