# ============================================================
# EPSS Shipment Live - Main App
# ============================================================

import streamlit as st
from auth import init_session, is_logged_in, show_login_page, current_user, logout
from persistence import load_shipments, save_shipments

st.set_page_config(
    page_title="EPSS Shipment Live",
    page_icon="📦",
    layout="wide"
)

init_session()

# ============================================================
# LOAD SHIPMENTS FROM GOOGLE SHEET (once per session)
# ============================================================
if "shipments_loaded" not in st.session_state:
    st.session_state.shipments = load_shipments()
    st.session_state.shipments_loaded = True

if not is_logged_in():
    show_login_page()
    st.stop()

user = current_user()
role = user["role"]

# ============================================================
# HIDE UNWANTED PAGES BY ROLE
# ============================================================
HIDE_BY_ROLE = {
    "Driver":  ["manager"],
    "Manager": ["driver"],
}

to_hide = HIDE_BY_ROLE.get(role, [])

if to_hide:
    css_rules = ""
    for page in to_hide:
        css_rules += f"""
        [data-testid="stSidebarNav"] a[href*="{page}"] {{ display: none !important; }}
        """
    st.markdown(f"<style>{css_rules}</style>", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("📦 EPSS Shipment Live")
    st.write(f"**{user['name']}**")
    st.write(f"Role: `{role}`")
    if role == "Driver" and user.get("plate"):
        st.write(f"Plate: `{user['plate']}`")
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
    st.info("👉 Click **driver** in the sidebar to start your shipment.")
elif role == "Manager":
    st.info("👉 Click **manager** in the sidebar to view the live dashboard.")
