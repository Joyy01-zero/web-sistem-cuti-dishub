"""Cek jumlah karyawan di DATA_KARYAWAN."""
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
ws = sh.worksheet("DATA_KARYAWAN")

rows = ws.get_all_records(head=2)
print(f"Total karyawan: {len(rows)}")
print(f"Headers row 1: {ws.row_values(1)}")
print(f"Headers row 2: {ws.row_values(2)}")
for i, r in enumerate(rows[:5], 1):
    print(f"  {i}. NIP={r.get('NI PPPK PW','?')} | NAMA={r.get('NAMA','?')}")
