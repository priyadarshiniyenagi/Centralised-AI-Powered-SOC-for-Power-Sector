
import streamlit as st

st.set_page_config(
    page_title="PowerSEC SOC",
    page_icon="🛡️",
    layout="wide",
)

# Check whether the user has signed in
authenticated = st.session_state.get("authenticated", False)

# Define the pages
login_page = st.Page(
    "pages/login.py",
    title="Sign In",
    icon="🔐",
    default=not authenticated,
)

home_page = st.Page(
    "pages/home.py",
    title="SOC Home",
    icon="🏠",
    default=authenticated,
)

dashboard_page = st.Page(
    "soc_dashboard.py",
    title="SOC Dashboard",
    icon="📊",
)

logout_page = st.Page(
    "pages/logout.py",
    title="Sign Out",
    icon="🚪",
)

# Show protected pages only after authentication
if authenticated:
    navigation = st.navigation(
        [home_page, dashboard_page, logout_page],
        position="sidebar",
    )
else:
    navigation = st.navigation(
        [login_page],
        position="hidden",
    )

navigation.run()
