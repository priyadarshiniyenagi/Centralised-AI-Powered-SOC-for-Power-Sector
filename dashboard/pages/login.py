
import streamlit as st
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.auth_db import (
    initialize_auth_db,
    register_user,
    authenticate_user,
    validate_username,
    validate_password,
)

st.set_page_config(
    page_title="PowerSEC SOC | Authentication",
    page_icon="🛡️",
    layout="centered",
)

initialize_auth_db()

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07111f, #102840);
}

.block-container {
    max-width: 650px;
    padding-top: 3rem;
}

.brand {
    text-align: center;
    color: #f1f5f9;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: 1px;
}

.subtitle {
    text-align: center;
    color: #a9c0d8;
    margin-bottom: 1.8rem;
}

div[data-testid="stFormSubmitButton"] button {
    width: 100%;
}

.hint {
    color: #b5c8dc;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

if st.session_state.get("authenticated"):
    st.switch_page("app.py")
    st.success(
        f"Signed in as {st.session_state.get('username')} "
        f"({st.session_state.get('role')})."
    )
    st.info("Your account is authenticated. The SOC home-page navigation will be connected in the next step.")

    if st.button("Sign out"):
        for key in ("authenticated", "username", "role", "user_id"):
            st.session_state.pop(key, None)
        st.rerun()

    st.stop()

st.markdown('<div class="brand">🛡️ POWERSEC SOC</div>',
            unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">'
    'Centralized AI-Powered Security Operations Center<br>'
    'for Power Sector OT/SCADA Environments'
    '</div>',
    unsafe_allow_html=True,
)

signin_tab, signup_tab = st.tabs(["Sign In", "Create Account"])

with signin_tab:
    st.subheader("Welcome back")
    st.caption("Sign in to access the security operations platform.")

    with st.form("signin_form"):
        login_username = st.text_input(
            "Username",
            placeholder="Enter your username",
            max_chars=24,
        )

        login_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
        )

        signin_submit = st.form_submit_button(
            "Sign In",
            type="primary",
            use_container_width=True,
        )

    if signin_submit:
        if not login_username.strip() or not login_password:
            st.error("Enter both username and password.")
        else:
            user = authenticate_user(login_username, login_password)

            if user:
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = user["user_id"]
                st.session_state["username"] = user["username"]
                st.session_state["role"] = user["role"]
                st.rerun()
            else:
                st.error("Invalid username or password.")

with signup_tab:
    st.subheader("Create your account")
    st.caption("New accounts receive the SOC Analyst role.")

    with st.form("signup_form"):
        new_username = st.text_input(
            "Username",
            placeholder="Example: analyst01",
            max_chars=24,
        )

        new_password = st.text_input(
            "Create password",
            type="password",
            placeholder="Create a strong password",
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Enter the password again",
        )

        st.markdown(
            """
            <div class="hint">
            Password requirements:<br>
            • At least 8 characters<br>
            • One uppercase letter (A–Z)<br>
            • One lowercase letter (a–z)<br>
            • One number (0–9)<br>
            • One special character, such as ! @ # $
            </div>
            """,
            unsafe_allow_html=True,
        )

        signup_submit = st.form_submit_button(
            "Create Account",
            type="primary",
            use_container_width=True,
        )

    if signup_submit:
        valid_username, username_message = validate_username(new_username)
        valid_password, password_message = validate_password(new_password)

        if not valid_username:
            st.error(username_message)
        elif not valid_password:
            st.error(password_message)
        elif new_password != confirm_password:
            st.error("The passwords do not match.")
        else:
            success, message = register_user(
                new_username,
                new_password,
            )

            if success:
                st.success(message)
                st.info("Open the Sign In tab and use your new credentials.")
            else:
                st.error(message)

st.divider()
st.caption("Authorized SOC personnel only.")
