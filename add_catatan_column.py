"""Tambah kolom CATATAN di Google Sheet CUTI (di akhir, setelah ID)."""
import os

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
if "CATATAN" in headers:
    print("Kolom CATATAN sudah ada.")
else:
    new_col = len(headers) + 1
    sheet.update_cell(1, new_col, "CATATAN")
    print(f"Kolom CATATAN ditambahkan di kolom {new_col}.")
    print("Headers baru:", sheet.row_values(1))
