# ============================================================
# EPSS Shipment Live - Driver Page
# ============================================================

import streamlit as st
from datetime import datetime
from auth import current_user, is_logged_in
from config import DRIVERS, DRIVER_PLATE, HUBS, WAREHOUSES, EVENTS
from persistence import save_shipments, append_log

if not is_logged_in():
    st.warning("Please log in first.")
    st.stop()

user = current_user()

if user["role"] != "Driver":
    st.error("Access denied. This page is for Drivers only.")
    st.stop()

st.title("🚚 My Shipment")
st.caption(f"Driver: **{user['name']}** | Plate: **{user.get('plate', '')}**")
st.divider()

if "shipments" not in st.session_state:
    st.session_state.shipments = []


# ============================================================
# FIND MY ACTIVE SHIPMENT
# ============================================================
my_shipments = [
    s for s in st.session_state.shipments
    if s.get("driver") == user["name"] and s.get("status") != "Returned / Arrived"
]

active = my_shipments[0] if my_shipments else None


# ============================================================
# IF NO ACTIVE SHIPMENT → SHOW "START NEW" FORM
# ============================================================
if not active:
    st.subheader("🆕 Start New Shipment")

    hub = st.selectbox("Destination Hub", HUBS)
    warehouse = st.selectbox("Warehouse", WAREHOUSES)

    if st.button("🚀 Start Shipment", type="primary", use_container_width=True):
        shipment_id = f"SHP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        new_shipment = {
            "shipment_id": shipment_id,
            "driver": user["name"],
            "plate": user.get("plate", ""),
            "hub": hub,
            "warehouse": warehouse,
            "events": {
                "assigned": datetime.now().strftime("%Y-%m-%d %H:%M"),
            },
            "status": "Assigned",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        st.session_state.shipments.append(new_shipment)
        save_shipments(st.session_state.shipments)
        append_log("Shipment Started", user["id"], shipment_id)
        st.success(f"✅ Shipment {shipment_id} started!")
        st.rerun()

    st.stop()


# ============================================================
# SHOW ACTIVE SHIPMENT
# ============================================================
st.subheader(f"📦 Shipment {active['shipment_id']}")
st.write(f"**Hub:** {active['hub']}  |  **Warehouse:** {active['warehouse']}")
st.write(f"**Status:** `{active['status']}`")
st.divider()

# --- Timeline of 9 events ---
st.write("**Event Timeline:**")
event_keys = [e["key"] for e in EVENTS]

for i, event in enumerate(EVENTS):
    key = event["key"]
    label_en = event["en"]
    label_am = event["am"]
    done = key in active.get("events", {})
    ts = active.get("events", {}).get(key, "")

    if done:
        st.write(f"✅ **{label_en} / {label_am}** — {ts}")
    else:
        # Determine if this is the NEXT event
        next_event = None
        for ek in event_keys:
            if ek not in active.get("events", {}):
                next_event = ek
                break

        if key == next_event:
            st.write(f"⏳ **{label_en} / {label_am}** — *next*")
        else:
            st.write(f"⬜ {label_en} / {label_am}")

st.divider()

# ============================================================
# NEXT ACTION BUTTON
# ============================================================
next_key = None
for ek in event_keys:
    if ek not in active.get("events", {}):
        next_key = ek
        break

if next_key:
    next_event_obj = next(e for e in EVENTS if e["key"] == next_key)
    label = f"{next_event_obj['en']} / {next_event_obj['am']}"

    if st.button(f"✅ {label}", type="primary", use_container_width=True):
        active["events"][next_key] = datetime.now().strftime("%Y-%m-%d %H:%M")
        active["status"] = next_event_obj["en"]
        save_shipments(st.session_state.shipments)
        append_log(f"Event: {next_key}", user["id"], active["shipment_id"])
        st.success(f"✅ {next_event_obj['en']} recorded!")
        st.rerun()
else:
    st.success("🎉 Shipment complete! All 9 events recorded.")
