"""
Run once to create the required Google Sheets structure.
Requires: .env with GOOGLE_CREDENTIALS_JSON and SPREADSHEET_ID set.
"""
import os

from dotenv import load_dotenv

from config.settings import SHEET_CUTI
from services.sheets_service import get_sheets_client

load_dotenv()

SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]


def setup():
    client = get_sheets_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    existing = [ws.title for ws in spreadsheet.worksheets()]
    print(f"Spreadsheet: {spreadsheet.title}")
    print(f"Existing sheets: {existing}")

    # Sheet 1: CUTI <tahun berjalan>
    cuti_headers = [
        "NO", "MASEHI", "HARI", "NAMA", "KEPERLUAN", "NO SURAT",
        "JABATAN", "SEKSI", "SHIF", "KABID/KASI", "NIP",
        "STATUS", "TGL_SUBMIT", "TAHUN", "ID",
    ]

    if SHEET_CUTI not in existing:
        ws = spreadsheet.add_worksheet(SHEET_CUTI, rows=1000, cols=len(cuti_headers))
        for col, header in enumerate(cuti_headers, 1):
            ws.update_cell(1, col, header)
        print(f"Created sheet: {SHEET_CUTI}")
    else:
        print(f"Sheet '{SHEET_CUTI}' already exists — skipping")

    # Sheet 2: DATA_KARYAWAN
    karyawan_headers = [
        "NIP", "NAMA", "TGL_LAHIR", "JABATAN", "SEKSI", "SHIF", "KABID_KASI", "AKTIF",
    ]

    if "DATA_KARYAWAN" not in existing:
        ws = spreadsheet.add_worksheet("DATA_KARYAWAN", rows=500, cols=8)
        for col, header in enumerate(karyawan_headers, 1):
            ws.update_cell(1, col, header)

        # Sample data
        sample = [
            ["19850115 201001 1 001", "Budi Santoso", "1985-01-15", "Staff", "Teknik", "Pagi", "Ahmad Fauzi", "TRUE"],
            [
                "19900320 201501 2 002", "Siti Rahayu", "1990-03-20", "Staff", "Operasional",
                "Siang", "Dewi Lestari", "TRUE",
            ],
        ]
        for row in sample:
            ws.append_row(row)
        print("Created sheet: DATA_KARYAWAN (with 2 sample employees)")
    else:
        print("Sheet 'DATA_KARYAWAN' already exists — skipping")

    # Remove default "Sheet1" if empty
    try:
        sheet1 = spreadsheet.worksheet("Sheet1")
        if sheet1.row_count <= 1 and not any(sheet1.row_values(1)):
            spreadsheet.del_worksheet(sheet1)
            print("Removed empty Sheet1")
    except Exception:
        pass

    print("\nSetup complete!")
    print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")


if __name__ == "__main__":
    setup()
