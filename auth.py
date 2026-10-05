# ============================================================
# EPSS Shipment Live - Authentication
# ============================================================

import streamlit as st
import pandas as pd


# ============================================================
# LOAD USERS FROM EXCEL
# ============================================================
@st.cache_data
def load_users():
    """Load users from the Excel file."""
    try:
        df = pd.read_excel("EPSS_Shipment_Users.xlsx", sheet_name="Users")
        users = {}
        for _, row in df.iterrows():
            email = str(row["Email"]).strip().lower()
            if not email or email == "nan":
                continue
            users[email] = {
                "password": str(row["Password"]).strip(),
                "name": str(row["Name"]).strip(),
                "role": str(row["Role"]).strip(),
            }
        return users
    except Exception as e:
        st.error(f"Could not load users: {e}")
        return {}


USERS = load_users()


# ============================================================
# SESSION MANAGEMENT
# ============================================================
def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.user_role = None


def login(email, password):
    email_clean = email.strip().lower()
    if email_clean in USERS:
        if USERS[email_clean]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user_email = email_clean
            st.session_state.user_name = USERS[email_clean]["name"]
            st.session_state.user_role = USERS[email_clean]["role"]
            return True
    return False


def logout():
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.user_role = None


def is_logged_in():
    return st.session_state.get("logged_in", False)


def current_user():
    return {
        "email": st.session_state.get("user_email"),
        "name": st.session_state.get("user_name"),
        "role": st.session_state.get("user_role"),
    }


# ============================================================
# LOGIN PAGE
# ============================================================
def show_login_page():
    st.title("📦 EPSS Shipment Live")
    st.caption("Ethiopian Pharmaceutical Supply Service — Real-time Shipment Tracking")
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True, type="primary"):
            if login(email, password):
                st.rerun()
            else:
                st.error("Invalid email or password.")

        st.caption("Demo password: **1234**")
