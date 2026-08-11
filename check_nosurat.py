"""Lihat pola NO SURAT di sheet CUTI (untuk auto-generate nomor)."""
import os

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
with open(env_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

from services.sheets_service import get_all_records
from config.settings import SHEET_CUTI

rows = get_all_records(SHEET_CUTI)
print(f"Total rows: {len(rows)}")
for r in rows[-12:]:
    print(repr(r.get("NO SURAT", "")), "|", r.get("STATUS", ""), "|", r.get("TAHUN", ""), "|", r.get("KEPERLUAN", ""))
