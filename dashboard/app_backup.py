import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Power Sector SOC",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# DATABASE PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_FILE = (
    PROJECT_ROOT
    / "database"
    / "soc.db"
)


# ============================================================
# DATABASE FUNCTION
# ============================================================

@st.cache_data
def load_incidents():

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    query = """
        SELECT
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
        FROM soc_incidents
        ORDER BY
            CASE priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
            END,
            priority_score DESC
    """

    df = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return df


# ============================================================
# LOAD DATA
# ============================================================

df = load_incidents()


# ============================================================
# TITLE
# ============================================================

st.title(
    "🛡️ Power Sector Security Operations Center"
)

st.subheader(
    "Centralized AI-Powered SOC for OT/SCADA Security"
)

st.caption(
    "IEC104 + IEC61850 PTP | AI-Based Detection | "
    "Event Correlation | Alert Prioritization"
)


# ============================================================
# TOP METRICS
# ============================================================

total_incidents = len(df)

critical_count = (
    df["priority"] == "Critical"
).sum()

high_count = (
    df["priority"] == "High"
).sum()

medium_count = (
    df["priority"] == "Medium"
).sum()

low_count = (
    df["priority"] == "Low"
).sum()


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Incidents",
        total_incidents
    )

with col2:
    st.metric(
        "Critical",
        critical_count
    )

with col3:
    st.metric(
        "High",
        high_count
    )

with col4:
    st.metric(
        "Medium",
        medium_count
    )

with col5:
    st.metric(
        "Low",
        low_count
    )


st.divider()


# ============================================================
# PROTOCOL AND PRIORITY CHARTS
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "Incidents by Protocol"
    )

    protocol_counts = (
        df["protocol"]
        .value_counts()
    )

    st.bar_chart(
        protocol_counts
    )


with col2:

    st.subheader(
        "Alert Priority Distribution"
    )

    priority_counts = (
        df["priority"]
        .value_counts()
        .reindex(
            ["Critical", "High", "Medium", "Low"],
            fill_value=0
        )
    )

    st.bar_chart(
        priority_counts
    )


# ============================================================
# EVENT TYPE DISTRIBUTION
# ============================================================

st.subheader(
    "Security Event Types"
)

event_type_counts = (
    df["event_type"]
    .value_counts()
)

st.bar_chart(
    event_type_counts
)


st.divider()


# ============================================================
# PRIORITIZED ALERT TABLE
# ============================================================

st.subheader(
    "Prioritized SOC Alerts"
)

display_df = df[
    [
        "incident_id",
        "protocol",
        "event_type",
        "event_count",
        "severity",
        "priority_score",
        "priority"
    ]
].copy()

display_df.columns = [
    "Incident",
    "Protocol",
    "Event Type",
    "Events",
    "Severity",
    "Priority Score",
    "Priority"
]

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True
)


# ============================================================
# INCIDENT DETAILS
# ============================================================

st.divider()

st.subheader(
    "Incident Investigation"
)

incident_options = df["incident_id"].tolist()

selected_incident = st.selectbox(
    "Select an incident",
    incident_options
)

selected = df[
    df["incident_id"] == selected_incident
].iloc[0]


# ============================================================
# INCIDENT INFORMATION
# ============================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.write("**Incident ID**")
    st.write(selected["incident_id"])

    st.write("**Protocol**")
    st.write(selected["protocol"])

    st.write("**Event Type**")
    st.write(selected["event_type"])

    st.write("**Detection Source**")
    st.write(selected["detection_source"])


with col2:

    st.write("**Event Count**")
    st.write(f"{selected['event_count']:,}")

    st.write("**Severity**")
    st.write(selected["severity"])

    st.write("**Priority Score**")
    st.write(selected["priority_score"])

    st.write("**Priority**")
    st.write(selected["priority"])


with col3:

    st.write("**Start Time**")
    st.write(selected["start_time"])

    st.write("**End Time**")
    st.write(selected["end_time"])

    st.write("**Duration**")
    st.write(
        f"{selected['duration_seconds']:.2f} seconds"
    )

    st.write("**Sources**")
    st.write(selected["source_count"])

    st.write("**Destinations**")
    st.write(selected["destination_count"])


# ============================================================
# RECOMMENDED ACTION
# ============================================================

st.subheader(
    "Recommended SOC Action"
)

st.info(
    selected["recommended_action"]
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Prototype SOC developed for power-sector "
    "OT/SCADA cybersecurity monitoring and "
    "AI-based anomaly detection."
)