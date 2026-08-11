"""Kuota cuti service — hitung pemakaian & sisa kuota per karyawan per tahun.

Kuota dihitung dalam satuan **hari kerja** (Senin–Jumat).
- Kuota tahunan: 12 hari kerja (tidak termasuk Sakit & Cuti Hamil).
- Kuota cuti hamil/melahirkan: 90 hari kerja, terpisah dari kuota tahunan.
"""

from datetime import datetime, timedelta

from config.settings import KUOTA_TAHUNAN, SHEET_CUTI
from services.sheets_service import get_all_records

KUOTA_HAMIL = 90  # hari kerja


def hitung_hari_kerja(tgl_mulai_str: str, tgl_selesai_str: str) -> int:
    """Hitung jumlah hari kerja (Senin–Jumat) antara dua tanggal (inklusif).

    Menerima format YYYY-MM-DD. Return 0 jika format tidak valid.
    """
    try:
        mulai = datetime.strptime(str(tgl_mulai_str).strip()[:10], "%Y-%m-%d").date()
        selesai = datetime.strptime(str(tgl_selesai_str).strip()[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return 0

    if selesai < mulai:
        return 0

    count = 0
    current = mulai
    while current <= selesai:
        if current.weekday() < 5:  # 0=Senin, 4=Jumat
            count += 1
        current += timedelta(days=1)
    return count


def _get_durasi(row: dict) -> int:
    """Ambil durasi hari kerja dari row Sheets.

    Prioritas: kolom DURASI_HARI_KERJA, fallback hitung dari HARI/tanggal.
    """
    # Coba ambil dari kolom DURASI_HARI_KERJA
    durasi_raw = row.get("DURASI_HARI_KERJA", "")
    if durasi_raw not in ("", None, 0, "0"):
        try:
            return int(durasi_raw)
        except (ValueError, TypeError):
            pass

    # Fallback: hitung dari tanggal di kolom HARI (format "d Bulan YYYY" atau "d s.d. d Bulan YYYY")
    # Tidak bisa diandalkan, return 1 sebagai fallback minimal
    return 1


def hitung_kuota_terpakai(nip: str, tahun: int) -> int:
    """Hitung total hari kerja cuti tahunan terpakai untuk NIP di tahun tertentu.

    Exclude: Sakit, Cuti Hamil/Melahirkan (punya kuota terpisah).
    """
    semua_data = get_all_records(SHEET_CUTI)
    total = 0
    for row in semua_data:
        if str(row.get("NIP", "")).strip() != str(nip).strip():
            continue
        if str(row.get("TAHUN", "")) != str(tahun):
            continue
        if row.get("STATUS", "").strip() != "Disetujui":
            continue
        keperluan = row.get("KEPERLUAN", "").strip()
        if keperluan in ("Sakit", "Cuti Hamil/Melahirkan"):
            continue
        total += _get_durasi(row)
    return total


def sisa_kuota(nip: str, tahun: int) -> int:
    """Sisa kuota cuti tahunan dalam hari kerja."""
    sisa = KUOTA_TAHUNAN - hitung_kuota_terpakai(nip, tahun)
    return max(sisa, 0)


def boleh_ajukan(nip: str, tahun: int, keperluan: str = "", durasi: int = 1) -> bool:
    """Cek apakah masih boleh mengajukan cuti.

    Args:
        nip: NIP karyawan
        tahun: tahun pengajuan
        keperluan: jenis keperluan cuti
        durasi: durasi hari kerja yang diminta
    """
    if keperluan == "Sakit":
        return True  # sakit tidak pakai kuota

    if keperluan == "Cuti Hamil/Melahirkan":
        sisa = sisa_kuota_hamil(nip, tahun)
        return sisa >= durasi

    return sisa_kuota(nip, tahun) >= durasi


# ── Kuota Cuti Hamil ──────────────────────────────────────────────────

def hitung_kuota_hamil_terpakai(nip: str, tahun: int) -> int:
    """Hitung total hari kerja cuti hamil/melahirkan terpakai."""
    semua_data = get_all_records(SHEET_CUTI)
    total = 0
    for row in semua_data:
        if str(row.get("NIP", "")).strip() != str(nip).strip():
            continue
        if str(row.get("TAHUN", "")) != str(tahun):
            continue
        if row.get("STATUS", "").strip() != "Disetujui":
            continue
        if row.get("KEPERLUAN", "").strip() != "Cuti Hamil/Melahirkan":
            continue
        total += _get_durasi(row)
    return total


def sisa_kuota_hamil(nip: str, tahun: int) -> int:
    """Sisa kuota cuti hamil dalam hari kerja."""
    sisa = KUOTA_HAMIL - hitung_kuota_hamil_terpakai(nip, tahun)
    return max(sisa, 0)


def get_tahun_sekarang() -> int:
    return datetime.now().year
