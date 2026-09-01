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

    # Sheet 3: HARI_LIBUR
    libur_headers = ["TANGGAL", "KETERANGAN", "TAHUN"]
    if "HARI_LIBUR" not in existing:
        ws = spreadsheet.add_worksheet("HARI_LIBUR", rows=100, cols=3)
        for col, header in enumerate(libur_headers, 1):
            ws.update_cell(1, col, header)
        
        # Hardcoded data 2025 & 2026
        hari_libur_data = [
            ["2025-01-27", "Tahun Baru Imlek", "2025"],
            ["2025-08-17", "Hari Kemerdekaan RI", "2025"],
            ["2026-01-01", "Tahun Baru Masehi", "2026"],
            ["2026-01-27", "Isra Miraj", "2026"],
            ["2026-01-28", "Cuti Bersama Isra Miraj", "2026"],
            ["2026-03-28", "Hari Raya Nyepi", "2026"],
            ["2026-03-29", "Cuti Bersama Nyepi", "2026"],
            ["2026-04-02", "Wafat Isa Almasih", "2026"],
            ["2026-04-03", "Cuti Bersama Wafat Isa Almasih", "2026"],
            ["2026-05-01", "Hari Buruh Internasional", "2026"],
            ["2026-05-14", "Kenaikan Isa Almasih", "2026"],
            ["2026-05-20", "Hari Kebangkitan Nasional", "2026"],
            ["2026-05-25", "Hari Raya Waisak", "2026"],
            ["2026-06-01", "Hari Lahir Pancasila", "2026"],
            ["2026-06-18", "Idul Adha", "2026"],
            ["2026-06-19", "Cuti Bersama Idul Adha", "2026"],
            ["2026-07-08", "Tahun Baru Islam 1448 H", "2026"],
            ["2026-08-17", "Hari Kemerdekaan RI", "2026"],
            ["2026-09-16", "Maulid Nabi Muhammad SAW", "2026"],
            ["2026-12-25", "Hari Raya Natal", "2026"],
            ["2026-12-26", "Cuti Bersama Natal", "2026"],
        ]
        for row in hari_libur_data:
            ws.append_row(row)
        print("Created sheet: HARI_LIBUR (with default data)")
    else:
        print("Sheet 'HARI_LIBUR' already exists — skipping")

    print("\nSetup complete!")

    # Sheet 4: AUTH_STATE (login lockout)
    auth_headers = ["IP", "COUNT", "FIRST_ATTEMPT"]
    if "AUTH_STATE" not in existing:
        ws = spreadsheet.add_worksheet("AUTH_STATE", rows=100, cols=3)
        for col, header in enumerate(auth_headers, 1):
            ws.update_cell(1, col, header)
        print("Created sheet: AUTH_STATE")
    else:
        print("Sheet 'AUTH_STATE' already exists — skipping")

    print(f"\nSetup complete!")
    print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")


if __name__ == "__main__":
    setup()
