"""Cek header Google Sheet CUTI — verifikasi apakah kolom CATATAN ada."""
import json
import os
import sys

# Load .env secara manual (tanpa print isinya)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
with open(env_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

from services.sheets_service import get_sheet
from config.settings import SHEET_CUTI

sheet = get_sheet(SHEET_CUTI)
headers = sheet.row_values(1)
print("HEADERS:", headers)
print("CATATAN ada:", "CATATAN" in headers)
