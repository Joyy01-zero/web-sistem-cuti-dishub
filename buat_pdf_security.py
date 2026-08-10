#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Buat PDF presentasi keamanan untuk demo Dishub."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUT = "DEMO_KEAMANAN_Dishub.pdf"

# ---------- Warna tema Dishub (navy + gold) ----------
NAVY = HexColor("#1f3a64")
NAVY_2 = HexColor("#2d4f82")
GOLD = HexColor("#c9a227")
PAPER = HexColor("#f5f6f9")
INK = HexColor("#272a33")
MUTED = HexColor("#5c6170")
WHITE = HexColor("#ffffff")
GREEN = HexColor("#16a34a")
RED = HexColor("#dc2626")
AMBER = HexColor("#d97706")

# ---------- Styles ----------
st_title = ParagraphStyle(
    "title", fontName="Helvetica-Bold", fontSize=20, leading=26,
    textColor=NAVY, alignment=TA_CENTER, spaceAfter=4)
st_subtitle = ParagraphStyle(
    "subtitle", fontName="Helvetica", fontSize=11, leading=16,
    textColor=MUTED, alignment=TA_CENTER, spaceAfter=2)
st_slide = ParagraphStyle(
    "slide", fontName="Helvetica-Bold", fontSize=16, leading=22,
    textColor=WHITE, alignment=TA_LEFT)
st_body = ParagraphStyle(
    "body", fontName="Helvetica", fontSize=11, leading=17,
    textColor=INK, alignment=TA_LEFT, spaceAfter=8)
st_body_bold = ParagraphStyle(
    "bodybold", fontName="Helvetica-Bold", fontSize=11, leading=17,
    textColor=INK, alignment=TA_LEFT, spaceAfter=8)
st_bullet = ParagraphStyle(
    "bullet", fontName="Helvetica", fontSize=11, leading=18,
    textColor=INK, leftIndent=14, bulletIndent=4, spaceAfter=4)
st_talk = ParagraphStyle(
    "talk", fontName="Helvetica-Oblique", fontSize=10.5, leading=16,
    textColor=NAVY_2, alignment=TA_LEFT, leftIndent=10,
    borderWidth=0, spaceBefore=4)
st_note = ParagraphStyle(
    "note", fontName="Helvetica-Oblique", fontSize=9.5, leading=14,
    textColor=MUTED, alignment=TA_LEFT, spaceBefore=6)

def header(canvas, doc):
    """Header/footer tiap halaman."""
    canvas.saveState()
    # Header bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 14*mm, A4[0], 14*mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(15*mm, A4[1] - 9*mm, "Sistem Cuti Online — Dishub Kota Bogor")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(A4[0] - 15*mm, A4[1] - 9*mm, "Demo Keamanan Sistem")
    # Footer
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(A4[0]/2, 10*mm, f"Halaman {doc.page}")
    canvas.restoreState()

def slide_header(title, num):
    """Bar biru dengan judul slide."""
    t = Table([[Paragraph(title, st_slide)]],
              colWidths=[A4[0] - 30*mm], rowHeights=[16*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t

def badge(text, color):
    """Pill badge."""
    b = Paragraph(f'<font color="white"><b>{text}</b></font>',
                  ParagraphStyle("badge", fontName="Helvetica-Bold", fontSize=9,
                                 alignment=TA_CENTER, textColor=WHITE))
    t = Table([[b]], colWidths=[52*mm], rowHeights=[8*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    return t

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=15*mm, rightMargin=15*mm,
    topMargin=24*mm, bottomMargin=16*mm,
    title="Demo Keamanan — Sistem Cuti Online Dishub",
    author="KKL Dishub Kota Bogor",
)

story = []

# ============ HALAMAN 1: COVER ============
story.append(Spacer(1, 40*mm))
story.append(Paragraph("🛡️ Sistem Cuti Online", st_title))
story.append(Paragraph("Dishub Kota Bogor", st_title))
story.append(Spacer(1, 8*mm))
story.append(Paragraph("PAPARAN KEAMANAN SISTEM", st_title))
story.append(Spacer(1, 4*mm))
story.append(Paragraph("Bagaimana data pegawai dan proses cuti dilindungi", st_subtitle))
story.append(Spacer(1, 30*mm))
t_cover = Table([[
    Paragraph("Sub Bagian Umum & Kepegawaian", ParagraphStyle("c1", fontName="Helvetica", fontSize=11, textColor=INK, alignment=TA_CENTER)),
], [
    Paragraph("KKL Ilmu Komputer — Universitas Djuanda", ParagraphStyle("c2", fontName="Helvetica", fontSize=10, textColor=MUTED, alignment=TA_CENTER)),
]], colWidths=[A4[0] - 30*mm])
t_cover.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 2),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
]))
story.append(t_cover)
story.append(PageBreak())

# ============ HALAMAN 2: Ringkasan ============
story.append(slide_header("Ringkasan Keamanan yang Diterapkan", 2))
story.append(Spacer(1, 6*mm))
data_ringkas = [
    ["No", "Lapisan Keamanan", "Fungsi"],
    ["1", "CSRF Token", "Mencegah form palsu dari website lain"],
    ["2", "Rate Limiting", "Mencegah spam & serangan brute force"],
    ["3", "Security Headers", "Anti-clickjacking, anti-sniffing, batasi sumber script"],
    ["4", "API Validasi Aman", "Tidak membocorkan data pribadi pegawai"],
    ["5", "Password Terenkripsi", "Password admin di-hash dengan bcrypt"],
    ["6", "Konfigurasi Wajib", "Sistem menolak jalan tanpa SECRET_KEY aman"],
    ["7", "Data Pegawai Terlindungi", "Template berisi data asli tidak masuk repository"],
    ["8", "Anti-Bypass Proxy", "Header X-Forwarded-For hanya dipercaya dari proxy resmi"],
]
t_ringkas = Table(data_ringkas, colWidths=[12*mm, 55*mm, 108*mm])
t_ringkas.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PAPER]),
    ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#d3d6e0")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(t_ringkas)
story.append(Spacer(1, 5*mm))
story.append(Paragraph(
    "Seluruh lapisan di atas berjalan otomatis di setiap permintaan (request) ke sistem.",
    st_talk))
story.append(PageBreak())

# ============ HALAMAN 3: CSRF ============
story.append(slide_header("1. Anti-Pemalsuan Form (CSRF)", 3))
story.append(Spacer(1, 6*mm))
story.append(badge("SUDAH DITERAPKAN", GREEN))
story.append(Spacer(1, 6*mm))
story.append(Paragraph(
    "CSRF (Cross-Site Request Forgery) adalah serangan di mana website jahat "
    "mengirimkan data atas nama korban tanpa sepengetahuan korban.", st_body))
story.append(Paragraph("<b>Cara kerja proteksinya:</b>", st_body_bold))
for b in [
    "Setiap form (pengajuan cuti, cek status, login admin) diberi <b>token rahasia unik</b>",
    "Token disimpan di sesi pengguna dan dikirim bersama form",
    "Server memverifikasi token <b>sebelum</b> memproses data",
    "Permintaan tanpa token valid ditolak (403 Forbidden)",
]:
    story.append(Paragraph(b, st_bullet, bulletText="•"))
story.append(Spacer(1, 4*mm))
story.append(Paragraph(
    "<b>Manfaat:</b> Walaupun seseorang membuat website tiruan, form palsu dari website "
    "tersebut tidak akan pernah diterima oleh sistem.", st_talk))
story.append(Spacer(1, 8*mm))
story.append(Paragraph(
    "<b>Verifikasi cepat:</b> Kirim form tanpa token → sistem merespons 403 Forbidden.",
    st_note))
story.append(PageBreak())

# ============ HALAMAN 4: Rate Limiting ============
story.append(slide_header("2. Anti-Spam & Anti-Brute Force (Rate Limiting)", 4))
story.append(Spacer(1, 6*mm))
story.append(badge("SUDAH DITERAPKAN", GREEN))
story.append(Spacer(1, 6*mm))
story.append(Paragraph(
    "Sistem membatasi jumlah permintaan dari satu alamat IP dalam periode tertentu. "
    "Ini menghentikan bot, script otomatis, dan percobaan tebak kata sandi.", st_body))
data_rate = [
    ["Aktivitas", "Batas Maksimal", "Periode"],
    ["Submit form pengajuan cuti", "10 kali", "1 jam"],
    ["Validasi NIP (API)", "30 kali", "1 menit"],
    ["Cek status pengajuan", "20 kali", "1 menit"],
    ["Login admin gagal", "5 kali", "Terkunci 15 menit"],
]
t_rate = Table(data_rate, colWidths=[80*mm, 40*mm, 55*mm])
t_rate.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PAPER]),
    ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#d3d6e0")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(t_rate)
story.append(Spacer(1, 5*mm))
story.append(Paragraph(
    "<b>Manfaat:</b> Pengguna normal tidak akan pernah merasakan pembatasan ini — "
    "hanya bot dan penyerang yang terhenti.", st_talk))
story.append(PageBreak())

# ============ HALAMAN 5: Security Headers ============
story.append(slide_header("3. Security Headers (Proteksi Browser)", 5))
story.append(Spacer(1, 6*mm))
story.append(badge("SUDAH DITERAPKAN", GREEN))
story.append(Spacer(1, 6*mm))
story.append(Paragraph(
    "Setiap halaman yang dikirim sistem dilengkapi header keamanan yang diperintahkan "
    "ke browser untuk berperilaku aman:", st_body))
data_header = [
    ["Header", "Fungsi", "Mencegah"],
    ["X-Frame-Options", "Halaman tidak bisa dibungkus iframe website lain", "Clickjacking"],
    ["X-Content-Type-Options", "Browser tidak menebak jenis file", "MIME sniffing"],
    ["Content-Security-Policy", "Hanya script/style dari sumber resmi yang dimuat", "Serangan XSS"],
]
t_header = Table(data_header, colWidths=[48*mm, 70*mm, 57*mm])
t_header.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PAPER]),
    ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#d3d6e0")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(t_header)
story.append(Spacer(1, 5*mm))
story.append(Paragraph(
    "<b>Manfaat:</b> Walaupun ada celah, browser menolak mengeksekusi hal yang berbahaya.",
    st_talk))
story.append(PageBreak())

# ============ HALAMAN 6: API Aman ============
story.append(slide_header("4. API Validasi NIP — Tanpa Kebocoran Data", 6))
story.append(Spacer(1, 6*mm))
story.append(badge("SUDAH DITERAPKAN", GREEN))
story.append(Spacer(1, 6*mm))
story.append(Paragraph(
    "API validasi NIP sengaja dirancang <b>hanya menjawab 'terdaftar atau tidak'</b>. "
    "Tidak ada data pribadi yang dikembalikan.", st_body))
data_api = [
    ["Permintaan", "Respons API", "Keterangan"],
    ["NIP terdaftar", '{"valid": true}', "Hanya konfirmasi"],
    ["NIP tidak terdaftar", '{"valid": false}', "Hanya penolakan"],
    ["Format salah", "400 Bad Request", "Input ditolak"],
]
t_api = Table(data_api, colWidths=[55*mm, 60*mm, 60*mm])
t_api.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PAPER]),
    ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#d3d6e0")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(t_api)
story.append(Spacer(1, 5*mm))
for b in [
    "Nama, jabatan, seksi, dan data pribadi lainnya <b>tidak pernah</b> dikirim lewat API",
    "Pegawai mengisi data pribadi secara manual setelah NIP dinyatakan valid",
    "Sistem tidak bisa dimanfaatkan untuk 'mengintip' data pegawai lain",
]:
    story.append(Paragraph(b, st_bullet, bulletText="•"))
story.append(Spacer(1, 4*mm))
story.append(Paragraph(
    "<b>Manfaat:</b> Siapa pun yang mengetahui NIP tidak dapat mengambil data pribadi "
    "pegawai lain dari sistem.", st_talk))
story.append(PageBreak())

# ============ HALAMAN 7: Password + Config ============
story.append(slide_header("5. Password Terenkripsi & Konfigurasi Aman", 7))
story.append(Spacer(1, 6*mm))
story.append(badge("SUDAH DITERAPKAN", GREEN))
story.append(Spacer(1, 6*mm))
story.append(Paragraph("<b>Password Admin — di-hash dengan bcrypt</b>", st_body_bold))
for b in [
    "Password tidak pernah disimpan sebagai teks biasa",
    "bcrypt adalah standar industri untuk penyimpanan kata sandi",
    "Bahkan jika data bocor, password tidak dapat dibaca/dibalik",
]:
    story.append(Paragraph(b, st_bullet, bulletText="•"))
story.append(Spacer(1, 6*mm))
story.append(Paragraph("<b>Konfigurasi wajib sebelum berjalan</b>", st_body_bold))
for b in [
    "Sistem menolak start jika kunci rahasia (SECRET_KEY) belum diset atau masih default",
    "Mencegah deployment yang tidak sengaja memakai konfigurasi tidak aman",
    "IP pengguna tidak bisa dipalsukan untuk melewati batas akses (anti-bypass)",
]:
    story.append(Paragraph(b, st_bullet, bulletText="•"))
story.append(Spacer(1, 4*mm))
story.append(Paragraph(
    "<b>Manfaat:</b> Sistem dirancang agar tidak mungkin ter-deploy dalam keadaan tidak aman.",
    st_talk))
story.append(PageBreak())

# ============ HALAMAN 8: Data Pegawai ============
story.append(slide_header("6. Data Pegawai Terlindungi", 8))
story.append(Spacer(1, 6*mm))
story.append(badge("SUDAH DITERAPKAN", GREEN))
story.append(Spacer(1, 6*mm))
story.append(Paragraph(
    "File yang berisi data pegawai asli (template surat cuti) <b>tidak disimpan di "
    "repository publik</b>.", st_body))
for b in [
    "Template surat berisi contoh nama & data pegawai nyata dikeluarkan dari repository",
    "Riwayat git dibersihkan sehingga data tidak bisa dilacak kembali",
    "Repository hanya berisi kode program — tanpa data pribadi",
]:
    story.append(Paragraph(b, st_bullet, bulletText="•"))
story.append(Spacer(1, 6*mm))
story.append(Paragraph("<b>Nama sheet juga dikonfigurasi via variabel</b>", st_body_bold))
for b in [
    "Nama sheet ('CUTI 2026', 'DATA_KARYAWAN') dikelola lewat satu file konfigurasi",
    "Tidak ada nama sheet yang tersebar di kode program",
    "Perubahan nama sheet cukup dilakukan di satu tempat",
]:
    story.append(Paragraph(b, st_bullet, bulletText="•"))
story.append(PageBreak())

# ============ HALAMAN 9: Belum diterapkan ============
story.append(slide_header("Rekomendasi Tahap Selanjutnya", 9))
story.append(Spacer(1, 6*mm))
story.append(badge("DISARANKAN — TAHAP PRODUCTION", AMBER))
story.append(Spacer(1, 6*mm))
data_next = [
    ["No", "Peningkatan", "Keterangan", "Prioritas"],
    ["1", "HTTPS / SSL", "Enkripsi data saat dikirim melalui jaringan", "Tinggi"],
    ["2", "Audit Log", "Catatan siapa mengubah status pengajuan & kapan", "Sedang"],
    ["3", "Backup Otomatis", "Cadangan data Google Sheets secara berkala", "Sedang"],
    ["4", "Login Karyawan", "Sesi login per pegawai, bukan hanya NIP + tanggal lahir", "Rendah"],
]
t_next = Table(data_next, colWidths=[12*mm, 42*mm, 80*mm, 35*mm])
t_next.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PAPER]),
    ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#d3d6e0")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(t_next)
story.append(Spacer(1, 6*mm))
story.append(Paragraph(
    "Keamanan dasar sudah solid. Peningkatan di atas direkomendasikan sebelum sistem "
    "digunakan secara luas di lingkungan Dishub.", st_talk))
story.append(Spacer(1, 6*mm))
story.append(Paragraph(
    "Terima kasih. — Sub Bagian Umum & Kepegawaian, KKL Ilmu Komputer Universitas Djuanda",
    st_subtitle))

doc.build(story, onFirstPage=header, onLaterPages=header)
print(f"OK: {OUT}")
