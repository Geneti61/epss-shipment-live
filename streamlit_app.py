# ============================================================
# EPSS Shipment Live - Main App
# ============================================================

import streamlit as st
from auth import init_session, is_logged_in, show_login_page, current_user, logout
from persistence import load_shipments

st.set_page_config(
    page_title="EPSS Shipment Live",
    page_icon="📦",
    layout="wide"
)

init_session()

if "shipments_loaded" not in st.session_state:
    st.session_state.shipments = load_shipments()
    st.session_state.shipments_loaded = True

if not is_logged_in():
    show_login_page()
    st.stop()

user = current_user()
role = user["role"]

# ============================================================
# HIDE AUTO-SIDEBAR + BUILD CUSTOM ONE
# ============================================================
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("📦 EPSS Shipment Live")
    st.write(f"**{user['name']}**")
    st.write(f"Role: `{role}`")
    if role == "Driver" and user.get("plate"):
        st.write(f"Plate: `{user['plate']}`")
    st.divider()

    # Custom navigation buttons
    if role == "Driver":
        st.page_link("pages/driver.py", label="🚚 My Shipment")
    elif role == "Manager":
        st.page_link("pages/manager.py", label="📊 Live Dashboard")

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

# ============================================================
# HOME
# ============================================================
st.title("📦 EPSS Shipment Live")
st.success(f"✅ Welcome, **{user['name']}**! You are logged in as **{role}**.")
st.info("👈 Use the sidebar to navigate.")

if role == "Driver":
    st.info("👉 Click **My Shipment** in the sidebar to start your shipment.")
elif role == "Manager":
    st.info("👉 Click **Live Dashboard** in the sidebar to view shipments.")
