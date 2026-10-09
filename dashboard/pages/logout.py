
import streamlit as st

# Clear authentication details
for key in ("authenticated", "username", "role", "user_id"):
    st.session_state.pop(key, None)

st.rerun()
