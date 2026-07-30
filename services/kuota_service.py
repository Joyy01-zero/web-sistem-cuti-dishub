from config.settings import KUOTA_TAHUNAN, SHEET_CUTI
from services.sheets_service import get_all_records
from datetime import datetime


def hitung_kuota_terpakai(nip: str, tahun: int) -> int:
    semua_data = get_all_records(SHEET_CUTI)
    terpakai = sum(
        1
        for row in semua_data
        if str(row.get("NIP", "")).strip() == str(nip).strip()
        and str(row.get("TAHUN", "")) == str(tahun)
        and row.get("STATUS", "").strip() == "Disetujui"
    )
    return terpakai


def sisa_kuota(nip: str, tahun: int) -> int:
    return KUOTA_TAHUNAN - hitung_kuota_terpakai(nip, tahun)


def boleh_ajukan(nip: str, tahun: int) -> bool:
    return sisa_kuota(nip, tahun) > 0


def get_tahun_sekarang() -> int:
    return datetime.now().year
