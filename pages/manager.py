# ============================================================
# EPSS Shipment Live - Manager Dashboard
# ============================================================

import streamlit as st
import pandas as pd
import io
from datetime import datetime
from auth import current_user, is_logged_in
from config import EVENTS

if not is_logged_in():
    st.warning("Please log in first.")
    st.stop()

user = current_user()

if user["role"] != "Manager":
    st.error("Access denied. This page is for Managers only.")
    st.stop()

st.title("📊 Live Dashboard")
st.caption(f"Manager: **{user['name']}** | Updated: {datetime.now().strftime('%H:%M:%S')}")
st.divider()

if "shipments" not in st.session_state:
    st.session_state.shipments = []

shipments = st.session_state.shipments

# ============================================================
# GROUP SHIPMENTS BY CURRENT STATUS
# ============================================================
status_groups = {}
for s in shipments:
    status = s.get("status", "Assigned")
    status_groups.setdefault(status, []).append(s)

# ============================================================
# SNAPSHOT CARDS — with time + duration
# ============================================================
st.subheader("📸 Snapshot")

statuses_order = [
    "Assigned", "Loading Started", "Loading Finished", "Trip Started",
    "Arrived Hub", "Unloading Started", "Unloading Finished",
    "Return Started", "Returned / Arrived"
]

# Statuses considered "active" for warning if >2 hours
ACTIVE_STATUSES = [
    "Loading Started", "Trip Started", "Arrived Hub",
    "Unloading Started", "Return Started"
]

cols = st.columns(3)
for i, status in enumerate(statuses_order):
    col = cols[i % 3]
    with col:
        group = status_groups.get(status, [])
        with st.container(border=True):
            st.markdown(f"**{status} ({len(group)})**")
            if group:
                # Find the event key for this status
                status_event_key = None
                for ev in EVENTS:
                    if ev["en"] == status:
                        status_event_key = ev["key"]
                        break

                for s in group:
                    ts = s.get("events", {}).get(status_event_key, "") if status_event_key else ""
                    st.write(f"• {s['driver']} ({s['hub']})")
                    if ts:
                        try:
                            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M")
                            diff = datetime.now() - dt
                            total_min = int(diff.total_seconds() / 60)
                            if total_min < 60:
                                dur = f"{total_min} min ago"
                            else:
                                hrs = total_min // 60
                                mins = total_min % 60
                                dur = f"{hrs}h {mins}m ago"

                            warn = " ⚠️" if status in ACTIVE_STATUSES and total_min > 120 else ""
                            st.caption(f"   🕐 {ts}  |  {dur}{warn}")
                        except Exception:
                            st.caption(f"   🕐 {ts}")
            else:
                st.caption("_No shipments_")

st.divider()

# ============================================================
# LIVE SHIPMENTS TABLE
# ============================================================
st.subheader("🚚 Active Shipments")

if not shipments:
    st.info("No shipments yet.")
else:
    rows = []
    for s in shipments:
        rows.append({
            "Shipment ID": s.get("shipment_id", ""),
            "Driver": s.get("driver", ""),
            "Plate": s.get("plate", ""),
            "Hub": s.get("hub", ""),
            "Warehouse": s.get("warehouse", ""),
            "Status": s.get("status", ""),
            "Created": s.get("created_at", ""),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Excel export
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Shipments')
    st.download_button(
        label="📥 Download Shipments (Excel)",
        data=output.getvalue(),
        file_name=f"EPSS_Shipments_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

st.divider()

# ============================================================
# FULL TIMELINE VIEW
# ============================================================
st.subheader("📋 Full Timeline")

if shipments:
    for s in sorted(shipments, key=lambda x: x.get("created_at", ""), reverse=True):
        with st.expander(f"{s['shipment_id']} — {s['driver']} — {s['status']}"):
            st.write(f"**Hub:** {s['hub']}  |  **Warehouse:** {s['warehouse']}")
            st.write(f"**Plate:** {s.get('plate', '')}")
            st.divider()
            events = s.get("events", {})
            for e in EVENTS:
                ts = events.get(e["key"], "—")
                mark = "✅" if ts != "—" else "⬜"
                st.write(f"{mark} **{e['en']} / {e['am']}** — {ts}")
else:
    st.info("No shipment data yet.")
