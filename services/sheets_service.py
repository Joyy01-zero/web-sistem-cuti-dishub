import gspread
from google.oauth2.service_account import Credentials
import json
import os
import time
from config.settings import SHEET_CUTI, SHEET_KARYAWAN

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# === Client cache (singleton) ===
_client_cache = {"client": None, "ts": 0}
CLIENT_TTL = 3600  # re-auth max once per hour


def get_sheets_client():
    now = time.time()
    if _client_cache["client"] and (now - _client_cache["ts"]) < CLIENT_TTL:
        return _client_cache["client"]

    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    client = gspread.authorize(creds)
    _client_cache["client"] = client
    _client_cache["ts"] = now
    return client


# === Worksheet cache ===
_worksheet_cache = {"sheets": {}, "ts": 0}
WORKSHEET_TTL = 300  # re-open worksheet max every 5 min


def get_sheet(sheet_name):
    from config.settings import SPREADSHEET_ID

    now = time.time()
    cache_key = sheet_name
    cached = _worksheet_cache["sheets"].get(cache_key)
    if cached and (now - _worksheet_cache["ts"]) < WORKSHEET_TTL:
        return cached

    client = get_sheets_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    sheet = spreadsheet.worksheet(sheet_name)
    _worksheet_cache["sheets"][cache_key] = sheet
    _worksheet_cache["ts"] = now
    return sheet


# === Data cache ===
_data_cache = {}
DATA_TTL = 10  # cache data for 10 seconds (fast enough for live, slow enough to save API calls)


def _get_cached_data(sheet_name):
    now = time.time()
    cached = _data_cache.get(sheet_name)
    if cached and (now - cached["ts"]) < DATA_TTL:
        return cached["data"]

    sheet = get_sheet(sheet_name)
    head_row = 2 if sheet_name == SHEET_KARYAWAN else 1
    try:
        data = sheet.get_all_records(head=head_row)
    except Exception:
        all_values = sheet.get_all_values()
        if not all_values:
            data = []
        else:
            raw_headers = all_values[head_row - 1]
            seen = {}
            headers = []
            for h in raw_headers:
                h = h.strip()
                if not h: continue
                if h in seen:
                    seen[h] += 1
                    headers.append(f"{h}_{seen[h]}")
                else:
                    seen[h] = 0
                    headers.append(h)
            data = []
            for row in all_values[head_row:]:
                row_padded = row + [""] * (len(headers) - len(row))
                data.append(dict(zip(headers, row_padded)))
    _data_cache[sheet_name] = {"data": data, "ts": now}
    return data


def invalidate_cache(sheet_name=None):
    """Call after writes to force fresh reads."""
    if sheet_name:
        _data_cache.pop(sheet_name, None)
    else:
        _data_cache.clear()
    # Also force worksheet re-fetch after writes
    _worksheet_cache["ts"] = 0


def get_all_records(sheet_name):
    return _get_cached_data(sheet_name)


def get_karyawan_by_nip(nip):
    records = get_all_records(SHEET_KARYAWAN)
    for r in records:
        if str(r.get("NI PPPK PW", "")).strip() == str(nip).strip():
            r = dict(r)  # copy to avoid mutating cached data
            nip_str = str(nip).strip()
            if len(nip_str) >= 8:
                r["TGL_LAHIR"] = f"{nip_str[:4]}-{nip_str[4:6]}-{nip_str[6:8]}"
            else:
                r["TGL_LAHIR"] = ""
            return r
    return None


def get_pengajuan_by_nip(nip):
    records = get_all_records(SHEET_CUTI)
    return [r for r in records if str(r.get("NIP", "")).strip() == str(nip).strip()]


def get_pengajuan_by_status(status_filter=None, bulan_filter=None, seksi_filter=None):
    records = get_all_records(SHEET_CUTI)
    result = []
    for i, r in enumerate(records):
        # Row number = i + 2 (1-indexed, +1 for header)
        r["_row"] = i + 2

        if status_filter and status_filter != "Semua":
            if r.get("STATUS", "").strip() != status_filter:
                continue
        if bulan_filter:
            if bulan_filter.lower() not in str(r.get("MASEHI", "")).lower():
                continue
        if seksi_filter:
            if r.get("SEKSI", "").strip() != seksi_filter:
                continue
        result.append(r)
    return result


def append_row(sheet_name, data: dict):
    sheet = get_sheet(sheet_name)
    headers = sheet.row_values(1)
    row = [data.get(h, "") for h in headers]
    sheet.append_row(row)
    invalidate_cache(sheet_name)
    return len(sheet.get_all_values())


def update_cell(sheet_name, row_num, col_name, value):
    sheet = get_sheet(sheet_name)
    headers = sheet.row_values(1)
    if col_name not in headers:
        raise ValueError(f"Kolom '{col_name}' tidak ditemukan")
    col_index = headers.index(col_name) + 1
    sheet.update_cell(row_num, col_index, value)
    invalidate_cache(sheet_name)


def update_row_status(sheet_name, row_num, status, no_surat=None):
    update_cell(sheet_name, row_num, "STATUS", status)
    if no_surat is not None and str(no_surat).strip():
        update_cell(sheet_name, row_num, "NO SURAT", str(no_surat).strip())


def get_all_seksi(sheet_name="CUTI 2026"):
    records = get_all_records(sheet_name)
    return sorted(set(r.get("SEKSI", "").strip() for r in records if r.get("SEKSI", "").strip()))


def get_stats():
    records = get_all_records(SHEET_CUTI)
    menunggu = sum(1 for r in records if r.get("STATUS", "").strip() == "Menunggu ACC")
    disetujui = sum(1 for r in records if r.get("STATUS", "").strip() == "Disetujui")
    ditolak = sum(1 for r in records if r.get("STATUS", "").strip() == "Ditolak")
    return {"menunggu": menunggu, "disetujui": disetujui, "ditolak": ditolak, "total": len(records)}
