# ============================================================
# EPSS Shipment Live - Configuration
# ============================================================

import pandas as pd
import os

EXCEL_FILE = "EPSS_Shipment_Data.xlsx"

if not os.path.exists(EXCEL_FILE):
    raise FileNotFoundError(f"Missing {EXCEL_FILE} — please upload it to the repo root.")

# ============================================================
# DRIVERS
# ============================================================
_drv_df = pd.read_excel(EXCEL_FILE, sheet_name="Drivers")
DRIVERS = []
DRIVER_PLATE = {}
DRIVER_VEHICLE = {}

for _, row in _drv_df.iterrows():
    name = str(row.get("DriverName", "")).strip()
    plate = str(row.get("PlateNumber", "")).strip()
    vtype = str(row.get("VehicleType", "")).strip()
    if name and name != "nan" and plate and plate != "nan":
        DRIVERS.append(name)
        DRIVER_PLATE[name] = plate
        DRIVER_VEHICLE[name] = vtype

# ============================================================
# HUBS
# ============================================================
_hub_df = pd.read_excel(EXCEL_FILE, sheet_name="Hubs")
HUBS = _hub_df["HubName"].dropna().astype(str).tolist()

# ============================================================
# WAREHOUSES
# ============================================================
_wh_df = pd.read_excel(EXCEL_FILE, sheet_name="Warehouses")
WAREHOUSES = _wh_df["WarehouseName"].dropna().astype(str).tolist()

# ============================================================
# THE 9 EVENTS — English + Amharic (FINAL)
# ============================================================
EVENTS = [
    {"key": "assigned",     "en": "Assigned",           "am": "ተመድቧል"},
    {"key": "load_start",   "en": "Loading Started",    "am": "መጫን ተጀምሯል"},
    {"key": "load_done",    "en": "Loading Finished",   "am": "መጫን ተጠናቋል"},
    {"key": "trip_start",   "en": "Trip Started",       "am": "ጉዞ ተጀምሯል"},
    {"key": "hub_arrive",   "en": "Arrived Hub",        "am": "ቅርንጫፍ ደርሷል"},
    {"key": "unload_start", "en": "Unloading Started",  "am": "ማውረድ ተጀምሯል"},
    {"key": "unload_done",  "en": "Unloading Finished", "am": "ማውረድ ተጠናቋል"},
    {"key": "return_start", "en": "Return Started",     "am": "መመለስ ጉዞ ተጀምሯል"},
    {"key": "returned",     "en": "Returned / Arrived", "am": "መጣና ደርሷል"},
]
