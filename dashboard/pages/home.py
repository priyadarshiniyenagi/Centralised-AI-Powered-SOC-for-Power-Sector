
import streamlit as st

st.title("PowerSEC SOC")
st.subheader("Security Operations Center for Power-Sector OT/SCADA")

st.write(
    "Welcome to the centralized AI-powered security "
    "monitoring platform."
)

st.markdown("### SOC Modules")

col1, col2 = st.columns(2)

with col1:
    st.info("**SOC Dashboard**\n\nMonitor incidents, priorities, and security events.")

with col2:
    st.info("**Threat Detection**\n\nReview AI-based intrusion detection results.")

col3, col4 = st.columns(2)

with col3:
    st.info("**Asset Monitoring**\n\nView power-sector assets and their security status.")

with col4:
    st.info("**Incident Response**\n\nReview recommended actions for detected incidents.")

st.caption("PowerSEC SOC | OT/SCADA Cybersecurity")
