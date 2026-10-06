# ============================================================
# EPSS Shipment Live - Authentication
# Drivers log in with PLATE NUMBER
# Managers log in with EMAIL
# ============================================================

import streamlit as st
import pandas as pd
import os


EXCEL_FILE = "EPSS_Shipment_Data.xlsx"


@st.cache_data
def load_users():
    if not os.path.exists(EXCEL_FILE):
        st.error(f"Missing {EXCEL_FILE} — upload it to the repo root.")
        return {}

    users = {}

    # --- Drivers: key = PlateNumber ---
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="Drivers")
        for _, row in df.iterrows():
            name = str(row.get("DriverName", "")).strip()
            plate = str(row.get("PlateNumber", "")).strip()
            pwd = str(row.get("Password", "")).strip()
            if (name and name != "nan"
                and plate and plate != "nan"
                and pwd and pwd != "nan"):
                users[plate] = {
                    "password": pwd,
                    "full_name": name,
                    "role": "Driver",
                    "plate": plate,
                }
    except Exception as e:
        st.warning(f"Could not load Drivers: {e}")

    # --- Managers: key = email ---
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


def login(identifier, password):
    key = identifier.strip()
    # Try exact match first, then lowercase for emails
    for k in USERS.keys():
        if k.lower() == key.lower():
            if USERS[k]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user_id = k
                st.session_state.user_name = USERS[k]["full_name"]
                st.session_state.user_role = USERS[k]["role"]
                st.session_state.user_plate = USERS[k]["plate"]
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

        # Role toggle
        role_choice = st.radio(
            "I am a:",
            ["🚚 Driver", "👔 Manager"],
            horizontal=True,
        )

        if role_choice == "🚚 Driver":
            identifier = st.text_input("Plate Number", placeholder="e.g. 4-23525")
            st.caption("Drivers: Enter your plate number and password.")
        else:
            identifier = st.text_input("Email", placeholder="e.g. name@epss.gov.et")
            st.caption("Managers: Enter your email and password.")

        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True, type="primary"):
            if login(identifier, password):
                st.rerun()
            else:
                st.error("Invalid credentials. Please check and try again.")

        st.divider()
        st.caption("**Driver:** Plate Number + `Epss@2026`")
        st.caption("**Manager:** Email + `Epss@2019`")
