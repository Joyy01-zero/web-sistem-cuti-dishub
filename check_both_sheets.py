"""Cek header kedua sheet: CUTI 2026 dan CUTI 2026 demo."""
import json
import os

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
with open(env_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

import gspread
from google.oauth2.service_account import Credentials

creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
creds = Credentials.from_service_account_info(creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets"])
gc = gspread.authorize(creds)
sh = gc.open_by_key(os.environ["SPREADSHEET_ID"])

for ws in sh.worksheets():
    title = ws.title
    if "CUTI" in title.upper():
        row1 = ws.row_values(1)
        print(f"\n=== {title} (gid={ws.id}) ===")
        print(f"Kolom ({len(row1)}): {row1}")
