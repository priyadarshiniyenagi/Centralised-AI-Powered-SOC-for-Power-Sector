
import sqlite3
import streamlit as st
from pathlib import Path

st.title("🛡️ AI Security Assistant")
st.caption("PowerSEC SOC | OT/SCADA Cybersecurity")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_FILE = PROJECT_ROOT / "database" / "soc.db"


def answer_question(question):
    question_lower = question.lower().strip()

    # Helpers for identifying explanation versus search questions
    explanation_terms = [
        "what is", "explain", "meaning", "define",
        "why", "how can it affect", "impact",
        "dangerous", "harmful",
    ]

    search_terms = [
        "show me", "list", "display", "find",
        "how many", "count", "number of",
        "incidents", "records",
    ]

    is_explanation = any(
        term in question_lower for term in explanation_terms
    )
    is_search = any(
        term in question_lower for term in search_terms
    )

    # ---------------------------------------------------------
    # Port scanning explanation - BEFORE database search
    # ---------------------------------------------------------
    if (
        any(term in question_lower for term in [
            "port scan", "port scanning", "portscan"
        ])
        and is_explanation
        and not is_search
    ):
        return """
### What is a Port Scanning Attack?

A **port scanning attack** occurs when a system probes network ports
to discover accessible services and identify potential entry points.

Port scanning can also be performed legitimately by authorized
administrators, so the SOC must verify whether the activity is expected.

### Why is it a concern in a power-sector network?

1. **Service discovery:** Unexpected scans may reveal exposed services
   on OT devices.
2. **Reconnaissance:** Attackers may scan systems before attempting
   to exploit vulnerabilities.
3. **SCADA security:** Unauthorized probing of SCADA and IEC-104
   devices may indicate suspicious activity.
4. **Follow-up threats:** Scanning may precede attempts to exploit
   services or gain unauthorized access.

### Recommended SOC Investigation

- Verify the source, destination, ports, and timestamp.
- Determine whether the scanner is authorized.
- Review network logs for repeated or unusual connection attempts.
- Check for related alerts or attempted exploitation.
- Preserve evidence and follow approved OT response procedures.

**Important:** A port scan alone does not prove that a system was compromised.
"""

    # ---------------------------------------------------------
    # MITM explanation
    # ---------------------------------------------------------
    if (
        any(term in question_lower for term in [
            "man-in-the-middle", "man in the middle", "mitm"
        ])
        and is_explanation
        and not is_search
    ):
        return """
### What is a Man-in-the-Middle (MITM) Attack?

A **MITM attack** occurs when an attacker intercepts communication
between two systems and may monitor or modify exchanged data.

### Why is it dangerous in an IEC-104 power system?

IEC-104 carries supervisory control and monitoring information
between control centres and remote devices.

A MITM attack may:

1. **Compromise data integrity:** Measurements or messages may be altered.
2. **Hide abnormal conditions:** Operators may receive misleading information.
3. **Affect control communication:** Manipulated messages could interfere
   with supervisory operations if the system is vulnerable.
4. **Reduce trust:** Operators may be unable to rely on exchanged data.

### Recommended SOC Investigation

- Review incident timestamps and communicating endpoints.
- Check for unexpected network paths or endpoint identities.
- Examine packet captures and logs for suspicious patterns.
- Compare measurements with trusted data where possible.
- Preserve evidence and follow approved OT response procedures.

Your database is known to contain four recorded MITM incidents.
Verify their current details in the incident list.

**Important:** Confirm suspected manipulation using logs and trusted system data.
"""

    # ---------------------------------------------------------
    # IEC-104 starvation explanation
    # ---------------------------------------------------------
    if (
        any(term in question_lower for term in [
            "iec-104 starvation", "iec 104 starvation",
            "iec104 starvation", "iec104starvationattack",
            "starvation attack",
        ])
        and is_explanation
        and not is_search
    ):
        return """
### What is an IEC-104 Starvation Attack?

An **IEC-104 starvation attack** targets communication availability
in systems using IEC 60870-5-104, a protocol used between control
centres and electrical substation equipment.

The attack may interfere with communication resources and prevent
legitimate messages from being processed normally.

### Possible Effects

1. **Communication delays:** Legitimate messages may be delayed.
2. **Reduced availability:** Communication may become unreliable.
3. **Monitoring impact:** Operators may receive delayed status information.
4. **Operational risk:** Monitoring and control may become more difficult.

### Recommended SOC Investigation

- Check IEC-104 traffic volume and communication patterns.
- Review timestamps and identify affected endpoints.
- Look for repeated requests or communication failures.
- Correlate the event with other security alerts.
- Preserve logs and follow approved response procedures.

Your database is known to contain two recorded IEC-104 starvation incidents:
INC-000031 and INC-000032.

Verify their current severity and priority in the incident records.
"""

    # ---------------------------------------------------------
    # NTP-DDoS explanation
    # ---------------------------------------------------------
    if (
        any(term in question_lower for term in [
            "ntp-ddos", "ntp ddos", "ntpddos"
        ])
        and is_explanation
        and not is_search
    ):
        return """
### What is an NTP-DDoS Attack?

An **NTP-based Distributed Denial-of-Service (NTP-DDoS) attack**
uses Network Time Protocol infrastructure in an attempt to overwhelm
a target with traffic. NTP is commonly used to synchronize system clocks.

### Possible Effects on a Power-Sector Network

1. **Network congestion:** Excessive traffic may consume network capacity.
2. **Service disruption:** Network services may become slow or unavailable.
3. **Monitoring delays:** Congestion may delay communication and monitoring.
4. **Operational risk:** Disrupted communication can reduce service availability.

### Recommended SOC Investigation

- Check traffic volume, source addresses, destinations, and timestamps.
- Look for unusual NTP traffic patterns and traffic spikes.
- Identify affected services and verify their availability.
- Correlate network telemetry with related alerts.
- Preserve logs and follow approved response procedures.

Your database is known to contain two recorded NTP-DDoS incidents:
INC-000037 and INC-000038.

Confirm the current incident details in the SOC database.
"""

    # ---------------------------------------------------------
    # DoS explanation
    # ---------------------------------------------------------
    if (
        any(term in question_lower for term in [
            "dos attack", "denial of service", "dosattack"
        ])
        and is_explanation
        and not is_search
        and "ntp" not in question_lower
        and "ddos" not in question_lower
    ):
        return """
### What is a DoS Attack?

A **Denial-of-Service (DoS) attack** attempts to make a system,
network, or service unavailable to legitimate users.

### Possible Effects on a Power-Sector SCADA System

1. **Communication disruption:** SCADA systems may lose reliable
   communication with remote devices.
2. **Loss of visibility:** Operators may receive delayed or missing
   measurements and status updates.
3. **Delayed response:** Investigating abnormal conditions may become harder.
4. **Operational risk:** Critical monitoring services may become unavailable.

### Recommended SOC Investigation

- Review the alert timestamp, source, destination, and traffic volume.
- Check for unusual traffic spikes and repeated connections.
- Verify whether affected devices remain responsive.
- Compare the event with normal activity and approved maintenance.
- Preserve logs and follow approved OT response procedures.

Your database is known to contain two recorded DoS incidents:
INC-000003 and INC-000004.

Verify the stored severity, priority, and recommended actions before
taking response measures.
"""

    # ---------------------------------------------------------
    # Fuzzy attack explanation
    # ---------------------------------------------------------
    if (
        any(term in question_lower for term in [
            "fuzzy attack", "fuzzyattack"
        ])
        and is_explanation
        and not is_search
    ):
        return """
### What is a Fuzzy Attack?

A **fuzzy attack** sends malformed, unexpected, or unusual input data
to identify weaknesses or trigger unexpected system behaviour.

### Why can it be dangerous in an IEC-104 power system?

1. **Communication disruption:** Malformed messages may cause errors.
2. **Availability impact:** Vulnerable devices may become unresponsive.
3. **Unexpected behaviour:** Improperly handled messages may cause software errors.
4. **Monitoring interruption:** Communication issues may affect status visibility.
5. **Operational risk:** Unreliable communication may complicate response.

### Recommended SOC Investigation

- Review the affected device and alert timestamp.
- Inspect packet captures for malformed or unusual messages.
- Check for repeated connection failures or interruptions.
- Verify whether the affected device is operating normally.
- Preserve logs and follow approved OT response procedures.

Review fuzzy-attack records and prioritize them according to their
recorded severity and priority.

**Important:** Verify actual effects using logs, packet captures, and device status.
"""

    # ---------------------------------------------------------
    # Database-backed incident prioritization
    # ---------------------------------------------------------
    if (
        any(term in question_lower for term in [
            "which incidents", "investigated first",
            "investigate first", "highest priority",
            "most dangerous incidents", "prioritize incidents",
            "incidents should be investigated",
        ])
        and any(term in question_lower for term in [
            "why", "first", "priority", "prioritize",
            "investigated", "investigate",
        ])
    ):
        if not DATABASE_FILE.exists():
            return "SOC database not found. Please check the database path."

        try:
            with sqlite3.connect(DATABASE_FILE) as connection:
                connection.row_factory = sqlite3.Row

                rows = connection.execute("""
                    SELECT incident_id, protocol, event_type,
                           severity, priority, recommended_action
                    FROM soc_incidents
                    ORDER BY
                        CASE LOWER(priority)
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                            ELSE 5
                        END,
                        priority_score DESC
                    LIMIT 10
                """).fetchall()

            if not rows:
                return "No incidents were found in the SOC database."

            answer = (
                "## 🚨 Incidents to Investigate First\n\n"
                "The following incidents are ranked using their recorded "
                "priority, with priority score used to order incidents "
                "within each priority level. Confirm urgency against the "
                "actual operational impact.\n\n"
            )

            for row in rows:
                answer += (
                    f"### {row['incident_id']}\n"
                    f"- **Event:** {row['event_type']}\n"
                    f"- **Protocol:** {row['protocol']}\n"
                    f"- **Severity:** {row['severity']}\n"
                    f"- **Priority:** {row['priority']}\n"
                    f"- **Recommended action:** "
                    f"{row['recommended_action']}\n\n"
                )

            answer += (
                "### Why investigate these first?\n\n"
                "Critical-priority incidents are listed first, followed "
                "by high-, medium-, and low-priority incidents. This is "
                "a triage order based on database labels, not proof of "
                "actual compromise. Validate alerts against logs and "
                "operational impact, and follow approved OT/SCADA "
                "response procedures."
            )

            return answer

        except sqlite3.Error as error:
            return f"Unable to prioritize SOC incidents: {error}"


    # ---------------------------------------------------------
    # Basic OT/SCADA investigation guidance
    # ---------------------------------------------------------
    if any(term in question_lower for term in [
        "investigate", "investigation steps", "what should i do",
        "how to respond", "incident response",
    ]):
        if any(term in question_lower for term in [
            "port scan", "port scanning", "portscan"
        ]):
            return """
### Port Scan Investigation Guide

1. **Validate the alert:** Confirm source, destination, timestamp, and ports.
2. **Review scan patterns:** Check whether many ports or OT assets
   were contacted within a short period.
3. **Identify the source:** Determine whether the scanner is authorized.
4. **Check follow-up activity:** Review related alerts and connection attempts.
5. **Assess OT impact:** Verify whether legitimate communications were affected.
6. **Escalate and document:** Follow approved OT security procedures
   and preserve relevant logs.

A port scan alone does not prove that a system was compromised.
"""

        return """
### OT/SCADA Incident Investigation Guide

1. **Validate the alert:** Check incident ID, event type, severity,
   priority, timestamp, and detection source.
2. **Review the logs:** Examine network and security logs for unusual traffic.
3. **Identify affected assets:** Determine which OT devices, links,
   or services may be affected.
4. **Correlate events:** Compare related alerts across protocols and time windows.
5. **Follow approved procedures:** Escalate to the authorized OT/SCADA team.
   Do not isolate or restart operational equipment without authorization.
6. **Document findings:** Record evidence, actions, decisions, and outcomes.
"""

    # ---------------------------------------------------------
    # Attack type mapping used for counts and incident filtering
    # ---------------------------------------------------------
    attack_types = {
        "iec-104 starvation": "iec104starvationattack",
        "iec104 starvation": "iec104starvationattack",
        "starvation": "iec104starvationattack",
        "port scanning": "portscanattack",
        "port scan": "portscanattack",
        "portscan": "portscanattack",
        "ntp-ddos": "ntpddosattack",
        "ntp ddos": "ntpddosattack",
        "ntpddos": "ntpddosattack",
        "ddos": "ntpddosattack",
        "dos": "dosattack",
        "denial of service": "dosattack",
        "dos attack": "dosattack",
        "dosattack": "dosattack",
        "fuzzy attack": "fuzzyattack",
        "fuzzyattack": "fuzzyattack",
        "fuzzy": "fuzzyattack",
        "man-in-the-middle": "mitmattack",
        "man in the middle": "mitmattack",
        "mitm": "mitmattack",
        "flood attack": "floodattack",
        "floodattack": "floodattack",
        "flood": "floodattack",
        "unknown anomaly": "Unknown Anomaly",
        "unknown": "Unknown Anomaly",
    }

    # ---------------------------------------------------------
    # Attack count questions
    # ---------------------------------------------------------
    if any(term in question_lower for term in [
        "how many", "count", "number of"
    ]):
        matched_attack = next(
            (
                event_type
                for keyword, event_type in attack_types.items()
                if keyword in question_lower
            ),
            None,
        )

        try:
            with sqlite3.connect(DATABASE_FILE) as connection:
                if matched_attack:
                    result = connection.execute(
                        """
                        SELECT COUNT(*)
                        FROM soc_incidents
                        WHERE LOWER(event_type) = LOWER(?)
                        """,
                        (matched_attack,),
                    ).fetchone()

                    return (
                        f"The SOC database contains **{result[0]} "
                        f"{matched_attack} incident records**."
                    )

                
                if "critical" in question_lower:
                    condition = """
                        LOWER(priority) = 'critical'
                        OR LOWER(severity) = 'critical'
                    """
                    label = "critical"
                elif "medium" in question_lower:
                    condition = """
                        LOWER(severity) = 'medium'
                    """
                    label = "medium-severity"
                elif "high" in question_lower:
                    condition = """
                        LOWER(severity) = 'high'
                    """
                    label = "high-severity"
                else:
                    count = connection.execute(
                        "SELECT COUNT(*) FROM soc_incidents"
                    ).fetchone()[0]
                    return f"Your SOC database contains **{count} incidents**."


                count = connection.execute(
                    f"SELECT COUNT(*) FROM soc_incidents WHERE {condition}"
                ).fetchone()[0]

                return (
                    f"Your SOC database contains **{count} {label} incidents**."
                )

        except sqlite3.Error as error:
            return f"Unable to count SOC incidents: {error}"

    # ---------------------------------------------------------
    # Attack statistics
    # ---------------------------------------------------------
    if any(term in question_lower for term in [
        "attack statistics", "attack types",
        "which attacks", "types of attacks",
    ]):
        try:
            with sqlite3.connect(DATABASE_FILE) as connection:
                rows = connection.execute("""
                    SELECT event_type, COUNT(*) AS total
                    FROM soc_incidents
                    GROUP BY event_type
                    ORDER BY total DESC
                """).fetchall()

            if not rows:
                return "No attack records were found in the SOC database."

            answer = "**SOC Incident Statistics**\n\n"
            for event_type, total in rows:
                answer += f"- **{event_type}:** {total} incident(s)\n"

            return answer

        except sqlite3.Error as error:
            return f"Unable to retrieve attack statistics: {error}"

    if not DATABASE_FILE.exists():
        return "SOC database not found. Please check the database path."

    try:
        with sqlite3.connect(DATABASE_FILE) as connection:
            connection.row_factory = sqlite3.Row

            # Protocol statistics
            if any(term in question_lower for term in [
                "protocol statistics", "which protocols",
                "protocols have", "incidents by protocol",
            ]):
                rows = connection.execute("""
                    SELECT protocol, COUNT(*) AS total
                    FROM soc_incidents
                    GROUP BY protocol
                    ORDER BY total DESC
                """).fetchall()

                if not rows:
                    return "No protocol records were found."

                answer = "**SOC Protocol Statistics**\n\n"
                for row in rows:
                    answer += f"- **{row['protocol']}:** {row['total']} incident(s)\n"

                return answer
            
            # SOC incident summary
            if (
                "summary" in question_lower
                and any(term in question_lower for term in [
                    "incident", "security", "soc", "current"
                ])
            ):
                total = connection.execute("""
                    SELECT COUNT(*) FROM soc_incidents
                """).fetchone()[0]

                severity_rows = connection.execute("""
                    SELECT severity, COUNT(*) AS total
                    FROM soc_incidents
                    GROUP BY severity
                    ORDER BY total DESC
                """).fetchall()

                priority_rows = connection.execute("""
                    SELECT priority, COUNT(*) AS total
                    FROM soc_incidents
                    GROUP BY priority
                    ORDER BY total DESC
                """).fetchall()

                protocol_rows = connection.execute("""
                    SELECT protocol, COUNT(*) AS total
                    FROM soc_incidents
                    GROUP BY protocol
                    ORDER BY total DESC
                """).fetchall()

                attack_rows = connection.execute("""
                    SELECT event_type, COUNT(*) AS total
                    FROM soc_incidents
                    GROUP BY event_type
                    ORDER BY total DESC
                """).fetchall()

                critical_priority = connection.execute("""
                    SELECT COUNT(*)
                    FROM soc_incidents
                    WHERE LOWER(priority) = 'critical'
                """).fetchone()[0]

                answer = (
                    "## 🛡️ Current SOC Incident Summary\n\n"
                    f"**Total incidents:** {total}\n\n"
                    f"**Critical-priority incidents:** {critical_priority}\n\n"
                    "### Incidents by Severity\n\n"
                )

                for row in severity_rows:
                    answer += f"- **{row['severity']}:** {row['total']}\n"

                answer += "\n### Incidents by Priority\n\n"

                for row in priority_rows:
                    answer += f"- **{row['priority']}:** {row['total']}\n"

                answer += "\n### Incidents by Protocol\n\n"

                for row in protocol_rows:
                    answer += f"- **{row['protocol']}:** {row['total']}\n"

                answer += "\n### Incidents by Attack Type\n\n"

                for row in attack_rows:
                    answer += f"- **{row['event_type']}:** {row['total']}\n"

                answer += (
                    "\n### Recommended Next Step\n\n"
                    "Investigate high-severity and critical-priority "
                    "incidents first. Verify each alert against the "
                    "underlying logs and follow approved OT/SCADA "
                    "incident-response procedures."
                )

                return answer


            
            
            
            # ---------------------------------------------------------
            # Combined incident filtering
            # Supports attack type + severity + priority + protocol
            # ---------------------------------------------------------

            conditions = []
            params = []

            # 1. Detect priority filters
            if "priority" in question_lower:
                if "critical" in question_lower:
                    conditions.append("LOWER(priority) = ?")
                    params.append("critical")
                elif "high" in question_lower:
                    conditions.append("LOWER(priority) = ?")
                    params.append("high")
                elif "medium" in question_lower:
                    conditions.append("LOWER(priority) = ?")
                    params.append("medium")
                elif "low" in question_lower:
                    conditions.append("LOWER(priority) = ?")
                    params.append("low")

            # 2. Detect severity filters
            if "severity" in question_lower:
                if "critical" in question_lower:
                    conditions.append("LOWER(severity) = ?")
                    params.append("critical")
                elif "high" in question_lower:
                    conditions.append("LOWER(severity) = ?")
                    params.append("high")
                elif "medium" in question_lower:
                    conditions.append("LOWER(severity) = ?")
                    params.append("medium")
                elif "low" in question_lower:
                    conditions.append("LOWER(severity) = ?")
                    params.append("low")

            # Also support phrases such as "high-severity incidents"
            elif "severity" not in question_lower:
                if "high-severity" in question_lower or "high severity" in question_lower:
                    conditions.append("LOWER(severity) = ?")
                    params.append("high")
                elif "medium-severity" in question_lower or "medium severity" in question_lower:
                    conditions.append("LOWER(severity) = ?")
                    params.append("medium")
                elif "low-severity" in question_lower or "low severity" in question_lower:
                    conditions.append("LOWER(severity) = ?")
                    params.append("low")
                elif "critical-severity" in question_lower or "critical severity" in question_lower:
                    conditions.append("LOWER(severity) = ?")
                    params.append("critical")

            # 3. Detect protocol filters
            if (
                "iec61850" in question_lower
                or "iec 61850" in question_lower
                or "ptp" in question_lower
            ):
                conditions.append("LOWER(protocol) LIKE ?")
                params.append("%iec61850%")

            elif (
                "iec-104" in question_lower
                or "iec 104" in question_lower
                or "iec104" in question_lower
            ):
                conditions.append("LOWER(protocol) LIKE ?")
                params.append("%iec-104%")

            # 4. Detect attack type.
            # Check longer phrases first to avoid matching "dos"
            # before more specific terms such as "ntp ddos".
            matched_attack = next(
                (
                    event_type
                    for keyword, event_type in sorted(
                        attack_types.items(),
                        key=lambda item: len(item[0]),
                        reverse=True,
                    )
                    if keyword in question_lower
                ),
                None,
            )

            if matched_attack:
                conditions.append("LOWER(event_type) = LOWER(?)")
                params.append(matched_attack)

            # 5. Build one query containing ALL detected filters.
            sql = """
                SELECT incident_id, protocol, event_type,
                       severity, priority, recommended_action
                FROM soc_incidents
            """

            if conditions:
                sql += " WHERE " + " AND ".join(conditions)

            sql += " ORDER BY priority_score DESC"

            # Do not return every incident for an unrelated question.
            if not conditions and not is_search:
                return (
                    "I'm designed to answer questions about SOC incidents, "
                    "attack types, security priorities, protocols, and "
                    "OT/SCADA cybersecurity. Please ask a question related "
                    "to your SOC data."
                )

            rows = connection.execute(sql, params).fetchall()
            
        # Frequency and percentage analysis
        if (
            "most frequently" in question_lower
            or "what percentage" in question_lower
            or "percentage" in question_lower
        ):
            if not rows:
                return "No matching incidents were found in the SOC database."

            attack_counts = {}

            for row in rows:
                attack_type = row["event_type"] or "Unknown"
                attack_counts[attack_type] = (
                    attack_counts.get(attack_type, 0) + 1
                )

            total = len(rows)
            most_common = max(
                attack_counts,
                key=attack_counts.get
            )
            count = attack_counts[most_common]
            percentage = (count / total) * 100

            return (
                f"## Most Frequent Attack Type\n\n"
                f"**Attack type:** {most_common}\n\n"
                f"**Incidents:** {count} out of {total}\n\n"
                f"**Percentage:** {percentage:.2f}%\n\n"
                f"Focusing on the matching incidents, "
                f"{most_common} is the most frequent attack type. "
                f"The SOC should {next((row['recommended_action'] for row in rows if row['event_type'] == most_common and row['recommended_action']), 'investigate the affected incidents')}."
            )

            
        # ---------------------------------------------------------
        # Filtered incident summary grouped by attack type
        # ---------------------------------------------------------
        if (
            "summar" in question_lower
            and "attack type" in question_lower
        ):
            if not rows:
                return "No matching incidents were found in the SOC database."

            grouped = {}

            for row in rows:
                event_type = row["event_type"]
                if event_type not in grouped:
                    grouped[event_type] = {
                        "count": 0,
                        "actions": []
                    }

                grouped[event_type]["count"] += 1

                action = row["recommended_action"]
                if action and action not in grouped[event_type]["actions"]:
                    grouped[event_type]["actions"].append(action)

            answer = (
                "## SOC Incident Summary by Attack Type\n\n"
                f"**Total matching incidents:** {len(rows)}\n\n"
            )

            for event_type, details in sorted(
                grouped.items(),
                key=lambda item: item[1]["count"],
                reverse=True
            ):
                answer += (
                    f"### {event_type} ({details['count']} incidents)\n\n"
                    "**Recommended response actions:**\n\n"
                )

                for action in details["actions"]:
                    answer += f"- {action}\n"

                answer += "\n"

            answer += (
                "### Response Guidance\n\n"
                "Prioritize incidents according to their recorded priority "
                "and operational impact. Validate alerts against SOC logs "
                "and follow approved OT/SCADA response procedures."
            )

            return answer




        if not rows:
            return "No matching incidents were found in the SOC database."

        answer = f"Found {len(rows)} matching SOC incident(s):\n\n"

        for row in rows:
            answer += (
                f"- **Incident:** {row['incident_id']}\n"
                f"  - Protocol: {row['protocol']}\n"
                f"  - Event: {row['event_type']}\n"
                f"  - Severity: {row['severity']}\n"
                f"  - Priority: {row['priority']}\n"
                f"  - Recommended action: {row['recommended_action']}\n\n"
            )

        return answer

    except sqlite3.Error as error:
        return f"Unable to read SOC incidents: {error}"


# ---------------------------------------------------------
# Streamlit chat interface
# ---------------------------------------------------------
if "soc_chat_history" not in st.session_state:
    st.session_state.soc_chat_history = []

for message in st.session_state.soc_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask about SOC incidents or OT/SCADA security...")

if question:
    st.session_state.soc_chat_history.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    answer = answer_question(question)

    st.session_state.soc_chat_history.append(
        {"role": "assistant", "content": answer}
    )

    with st.chat_message("assistant"):
        st.markdown(answer)
