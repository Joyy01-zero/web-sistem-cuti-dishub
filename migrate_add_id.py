"""
One-off migration: add unique ID column to the CUTI sheet.

Idempotent — safe to run multiple times:
  1. Adds "ID" header if missing (checks first, never duplicates).
  2. Backfills an ID (secrets.token_urlsafe(9)) for every data row that lacks one.

Safe to run against the OLD codebase before deploying the new code.
Requires: .env with GOOGLE_CREDENTIALS_JSON and SPREADSHEET_ID set.
"""
import secrets

from dotenv import load_dotenv

load_dotenv()

from gspread.utils import rowcol_to_a1
from config.settings import SHEET_CUTI
from services.sheets_service import get_sheets_client, invalidate_cache
import os

SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]


def column_letter(col):
    return rowcol_to_a1(1, col)[:-1]


def migrate():
    client = get_sheets_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    sheet = spreadsheet.worksheet(SHEET_CUTI)

    headers = [h.strip() for h in sheet.row_values(1)]
    if "ID" in headers:
        id_col = headers.index("ID") + 1
        print(f"Header 'ID' sudah ada di kolom {column_letter(id_col)}")
    else:
        id_col = len(headers) + 1
        sheet.update_cell(1, id_col, "ID")
        print(f"Header 'ID' ditambahkan di kolom {column_letter(id_col)}")

    all_values = sheet.get_all_values()
    last_row = len(all_values)
    if last_row < 2:
        print("Tidak ada baris data — selesai.")
        return

    updated_count = 0
    id_column_values = []
    for row_idx in range(2, last_row + 1):
        row = all_values[row_idx - 1]
        id_value = row[id_col - 1].strip() if len(row) >= id_col else ""
        has_data = any(str(c).strip() for c in row)
        if has_data and not id_value:
            id_value = secrets.token_urlsafe(9)
            updated_count += 1
        id_column_values.append([id_value])

    if not updated_count:
        print("Semua baris data sudah punya ID — 0 baris ditulis.")
        return

    letter = column_letter(id_col)
    sheet.update(id_column_values, f"{letter}2:{letter}{last_row}")
    invalidate_cache(SHEET_CUTI)
    print(f"{updated_count} baris diberi ID baru.")


if __name__ == "__main__":
    migrate()
