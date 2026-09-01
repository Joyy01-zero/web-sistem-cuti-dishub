"""Buat dan isi sheet KABID_KASI dari pasangan KABID/KASI + NIP di CUTI."""
import json
import os

from dotenv import load_dotenv

load_dotenv()

import gspread
from google.oauth2.service_account import Credentials

from config.settings import SHEET_CUTI

SHEET_KABID_KASI = "KABID_KASI"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def main():
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(os.environ["SPREADSHEET_ID"])

    try:
        target = spreadsheet.worksheet(SHEET_KABID_KASI)
        target.clear()
    except gspread.exceptions.WorksheetNotFound:
        target = spreadsheet.add_worksheet(SHEET_KABID_KASI, rows=100, cols=2)

    source = spreadsheet.worksheet(SHEET_CUTI)
    rows = source.get_all_records(head=1)
    unique = {}
    for row in rows:
        nama = str(row.get("KABID/KASI", "")).strip()
        nip = str(row.get("NIP", "")).strip()
        if nama and nip:
            unique.setdefault((nama, nip), None)

    values = [["NAMA", "NIP"]]
    values.extend([list(pair) for pair in sorted(unique)])
    target.resize(rows=max(len(values), 100), cols=2)
    target.update("A1:B" + str(len(values)), values)
    print(f"Sheet {SHEET_KABID_KASI} siap: {len(unique)} pasangan unik")


if __name__ == "__main__":
    main()
