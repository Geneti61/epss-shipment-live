# ============================================================
# EPSS Shipment Live - Authentication
# Reads from EPSS_Shipment_Data.xlsx
# Drivers sheet: DriverName + Password
# Managers sheet: Email + Password
# ============================================================

import streamlit as st
import pandas as pd
import os


EXCEL_FILE = "EPSS_Shipment_Data.xlsx"


# ============================================================
# LOAD ALL USERS (Drivers + Managers)
# ============================================================
@st.cache_data
def load_users():
    if not os.path.exists(EXCEL_FILE):
        st.error(f"Missing {EXCEL_FILE} — upload it to the repo root.")
        return {}

    users = {}

    # --- Drivers ---
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="Drivers")
        for _, row in df.iterrows():
            name = str(row.get("DriverName", "")).strip()
            pwd = str(row.get("Password", "")).strip()
            if name and name != "nan" and pwd and pwd != "nan":
                # Use first name as username (lowercase, no spaces)
                username = name.split()[0].lower()
                # If duplicate, add plate number
                if username in users:
                    plate = str(row.get("PlateNumber", "")).strip()
                    username = f"{username}{plate}".lower()
                users[username] = {
                    "password": pwd,
                    "full_name": name,
                    "role": "Driver",
                    "plate": str(row.get("PlateNumber", "")).strip(),
                }
    except Exception as e:
        st.warning(f"Could not load Drivers: {e}")

    # --- Managers ---
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="Managers")
        for _, row in df.iterrows():
            email = str(row.get("Email", "")).strip().lower()
            pwd = str(row.get("Password", "")).strip()
            name = str(row.get("Name", "")).strip()
            if email and email != "nan" and pwd and pwd != "nan":
                users[email] = {
                    "password": pwd,
                    "full_name": name,
                    "role": "Manager",
                    "plate": "",
                }
    except Exception as e:
        st.warning(f"Could not load Managers: {e}")

    return users


USERS = load_users()


# ============================================================
# SESSION MANAGEMENT
# ============================================================
def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.user_role = None
        st.session_state.user_plate = None


def login(username, password):
    key = username.strip().lower()
    if key in USERS:
        if USERS[key]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user_id = key
            st.session_state.user_name = USERS[key]["full_name"]
            st.session_state.user_role = USERS[key]["role"]
            st.session_state.user_plate = USERS[key]["plate"]
            return True
    return False


def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_role = None
    st.session_state.user_plate = None


def is_logged_in():
    return st.session_state.get("logged_in", False)


def current_user():
    return {
        "id": st.session_state.get("user_id"),
        "name": st.session_state.get("user_name"),
        "role": st.session_state.get("user_role"),
        "plate": st.session_state.get("user_plate"),
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
        username = st.text_input("Username (or Email for Managers)")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True, type="primary"):
            if login(username, password):
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.caption("Drivers: use your first name. Password: **Epss@2026**")
