# ============================================================
# EPSS Shipment Live - Persistence Layer
# Reads/writes shipments to Google Sheets
# ============================================================

import streamlit as st
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def get_client():
    """Create the gspread client from Streamlit Secrets."""
    try:
        creds_dict = dict(st.secrets["google"]["service_account"])
        if "\\n" in creds_dict["private_key"]:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Could not connect to Google Sheets: {e}")
        return None


def get_sheet():
    """Return the storage spreadsheet object."""
    client = get_client()
    if client is None:
        return None
    try:
        sheet_id = st.secrets["shipment"]["sheet_id"]
        return client.open_by_key(sheet_id)
    except Exception as e:
        st.error(f"Could not open the shipment sheet: {e}")
        return None


def load_shipments():
    """Load all shipments from the 'Shipments' tab."""
    sheet = get_sheet()
    if sheet is None:
        return []
    try:
        worksheet = sheet.worksheet("Shipments")
        records = worksheet.get_all_values()
        shipments = []
        for row in records[1:]:
            if row and row[0]:
                try:
                    shipments.append(json.loads(row[0]))
                except Exception:
                    pass
        return shipments
    except Exception as e:
        st.warning(f"Could not load shipments: {e}")
        return []


def save_shipments(shipments_list):
    """Save all shipments to the 'Shipments' tab (overwrites)."""
    sheet = get_sheet()
    if sheet is None:
        return False
    try:
        worksheet = sheet.worksheet("Shipments")
        worksheet.clear()
        data = [["data"]]
        for s in shipments_list:
            data.append([json.dumps(s, default=str)])
        worksheet.update(values=data, range_name="A1")
        return True
    except Exception as e:
        st.warning(f"Could not save shipments: {e}")
        return False


def append_log(action, user_id, shipment_id):
    """Append one line to AuditLog."""
    sheet = get_sheet()
    if sheet is None:
        return False
    try:
        worksheet = sheet.worksheet("AuditLog")
        line = json.dumps({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_id,
            "action": action,
            "shipment_id": shipment_id,
        })
        worksheet.append_row([line])
        return True
    except Exception:
        return False
