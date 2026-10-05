# ============================================================
# EPSS Shipment Live - Configuration
# ============================================================

import pandas as pd
import os

EXCEL_FILE = "EPSS_Shipment_Users.xlsx"

if not os.path.exists(EXCEL_FILE):
    raise FileNotFoundError(f"Missing {EXCEL_FILE} — please upload it to the repo root.")

# ============================================================
# DRIVERS — from "Drivers" sheet
# ============================================================
_drv_df = pd.read_excel(EXCEL_FILE, sheet_name="Drivers")
DRIVERS = []
DRIVER_PLATE = {}

for _, row in _drv_df.iterrows():
    name = str(row["DriverName"]).strip()
    plate = str(row["PlateNumber"]).strip()
    if name and plate and name != "nan":
        DRIVERS.append(name)
        DRIVER_PLATE[name] = plate

# ============================================================
# HUBS — from "Hubs" sheet
# ============================================================
_hub_df = pd.read_excel(EXCEL_FILE, sheet_name="Hubs")
HUBS = _hub_df["HubName"].dropna().astype(str).tolist()

# ============================================================
# WAREHOUSES — from "Warehouses" sheet
# ============================================================
_wh_df = pd.read_excel(EXCEL_FILE, sheet_name="Warehouses")
WAREHOUSES = _wh_df["WarehouseName"].dropna().astype(str).tolist()

# ============================================================
# THE 9 EVENTS — English + Amharic
# ============================================================
EVENTS = [
    {"key": "assigned",   "en": "Assigned",           "am": "ተመድቧል"},
    {"key": "load_start", "en": "Loading Started",    "am": "መጫን ተጀምሯል"},
    {"key": "load_done",  "en": "Loading Finished",   "am": "መጫን ተጠናቋል"},
    {"key": "trip_start", "en": "Trip Started",       "am": "ጉዞ ተጀምሯል"},
    {"key": "hub_arrive", "en": "Arrived Hub",        "am": "ቅርንጫፍ ደርሷል"},
    {"key": "unload_start","en": "Unloading Started", "am": "ማውረድ ተጀምሯል"},
    {"key": "unload_done","en": "Unloading Finished", "am": "ማውረድ ተጠናቋል"},
    {"key": "return_start","en": "Return Started",    "am": "መመለስ ጉዞ ተጀምሯል"},
    {"key": "returned",   "en": "Returned / Arrived", "am": "መጣና ደርሷል"},
]
