from docx import Document
import io
import os
import copy

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "template_surat",
    "template_cuti_pkwt.docx",
)

# Mapping: teks asli di template → field dari data Sheets
# Bagian 1: Surat Permohonan Cuti
PERMOHONAN_REPLACEMENTS = {
    "WAHYU EKO SAPUTRO": "NAMA",
    "Tenaga Operasional Lalu Lintas": "JABATAN",
    "Pengendalian dan Ketertiban": "SEKSI",
    "28 s.d. 29 Juli 2026": "HARI",
    "Normal": "SHIF",
    "KEPERLUAN KELUARGA": "KEPERLUAN",
    "FAIZAL RACHMAN, S.E": "KABID/KASI",
}

# Bagian 2: Surat Cuti Resmi
RESMI_REPLACEMENTS = {
    "167": "NO SURAT (nomor)",
    "VI": "NO SURAT (bulan romawi)",
}

# Nama yang muncul di Bagian 2 (karyawan)


def generate_surat(data: dict) -> bytes:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template surat tidak ditemukan: {TEMPLATE_PATH}")
    doc = Document(TEMPLATE_PATH)

    nama = data.get("NAMA", "")
    nip = data.get("NIP", "")
    jabatan = data.get("JABATAN", "")
    seksi = data.get("SEKSI", "")
    shif = data.get("SHIF", "")
    hari = data.get("HARI", "")
    keperluan = data.get("KEPERLUAN", "")
    kabid = data.get("KABID/KASI", "")
    no_surat = data.get("NO SURAT", "")
    tgl_submit = data.get("TGL_SUBMIT", "")

    # Build full replacement map (teks asli → nilai baru)
    text_replacements = {
        "WAHYU EKO SAPUTRO": nama,
        "Tenaga Operasional Lalu Lintas": jabatan,
        "Pengendalian dan Ketertiban": seksi,
        "28 s.d. 29 Juli 2026": hari,
        "KEPERLUAN KELUARGA": keperluan.upper(),
        "FAIZAL RACHMAN, S.E": kabid,
    }

    # Shif — only replace "Normal" if it appears in Shif context
    # (avoid replacing "Normal" elsewhere in doc)
    shif_replacements = {"Normal": shif}

    # No surat — replace "167 /PKWT/VI/2026" pattern
    # Parse no_surat like "167/PKWT/VI/2026"
    if no_surat:
        parts = no_surat.replace(" ", "").split("/")
        if len(parts) >= 4:
            nomor, _, bulan_romawi, tahun = parts[0], parts[1], parts[2], parts[3]
            no_surat_replacements = {
                "167": nomor,
                "VI": bulan_romawi,
                "2026": tahun,
            }
        else:
            no_surat_replacements = {"167 /PKWT/VI/2026": no_surat}
    else:
        no_surat_replacements = {}

    # Tanggal surat (bagian 2) — replace "Maret 2026"
    bulan_nama = [
        "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember",
    ]
    if tgl_submit:
        try:
            from datetime import datetime
            dt = datetime.strptime(tgl_submit[:10], "%Y-%m-%d")
            tgl_str = f"{bulan_nama[dt.month]} {dt.year}"
        except Exception:
            tgl_str = tgl_submit
    else:
        tgl_str = ""

    # Date replacements for Bogor, [bulan] [tahun]
    # "Juli 2026" in bagian 1, "Maret 2026" in bagian 2
    date_replacements = {}
    if tgl_str:
        date_replacements["Juli 2026"] = tgl_str
        date_replacements["Maret 2026"] = tgl_str

    # Merge all
    all_replacements = {}
    all_replacements.update(text_replacements)
    all_replacements.update(shif_replacements)
    all_replacements.update(no_surat_replacements)
    all_replacements.update(date_replacements)

    # Replace in paragraphs
    for paragraph in doc.paragraphs:
        _replace_in_paragraph(paragraph, all_replacements)

    # Replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    _replace_in_paragraph(paragraph, all_replacements)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def _replace_in_paragraph(paragraph, replacements):
    """Replace text across runs, handling cases where target spans multiple runs."""
    full_text = paragraph.text
    if not any(old in full_text for old in replacements):
        return

    for old_text, new_text in replacements.items():
        if old_text not in full_text:
            continue

        # Try simple run-level replacement first
        replaced = False
        for run in paragraph.runs:
            if old_text in run.text:
                run.text = run.text.replace(old_text, new_text)
                replaced = True
                break

        if replaced:
            continue

        # Target spans multiple runs — concatenate runs, find, replace, redistribute
        runs = paragraph.runs
        if not runs:
            continue

        combined = "".join(r.text for r in runs)
        if old_text not in combined:
            continue

        new_combined = combined.replace(old_text, new_text)

        # Put all text in first run, clear rest
        runs[0].text = new_combined
        for r in runs[1:]:
            r.text = ""
