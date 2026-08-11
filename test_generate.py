"""Tes generate_surat dengan no_surat tertentu — cek apakah nomor masuk dokumen."""
import io
import os

from docx import Document

from services.surat_service import generate_surat

data = {
    "NAMA": "WAHYU EKO SAPUTRO",
    "JABATAN": "Tenaga Operasional Lalu Lintas",
    "SEKSI": "Pengendalian dan Ketertiban",
    "SHIF": "Normal",
    "HARI": "28 s.d. 29 Juli 2026",
    "KEPERLUAN": "Keperluan Keluarga",
    "KABID/KASI": "FAIZAL RACHMAN, S.E",
    "NO SURAT": "121212",
    "TGL_SUBMIT": "2026-08-10 10:00:00",
}

bytes_out = generate_surat(data)
doc = Document(io.BytesIO(bytes_out))
for p in doc.paragraphs:
    if "Nomor" in p.text or "PKWT" in p.text or "keperluan" in p.text.lower():
        print(repr(p.text.strip()))
