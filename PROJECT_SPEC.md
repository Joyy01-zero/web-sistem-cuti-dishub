# Sistem Pengajuan Cuti Online — Dinas Perhubungan Kota Bogor
### Dokumen Spesifikasi Proyek KKL (Kuliah Kerja Lapangan)
**Bagian:** Sub Bagian Umum dan Kepegawaian  
**Instansi:** Dinas Perhubungan Kota Bogor  
**Status:** Spesifikasi Lengkap untuk Pengembangan

---

## Daftar Isi

1. [Latar Belakang & Tujuan](#1-latar-belakang--tujuan)
2. [Alur Sistem (Full Flow)](#2-alur-sistem-full-flow)
3. [Tech Stack](#3-tech-stack)
4. [Struktur Folder Project](#4-struktur-folder-project)
5. [Setup & Instalasi](#5-setup--instalasi)
6. [Database — Google Sheets](#6-database--google-sheets)
7. [Fitur Karyawan (Publik)](#7-fitur-karyawan-publik)
8. [Fitur Admin (Terproteksi)](#8-fitur-admin-terproteksi)
9. [Logika Kuota Cuti](#9-logika-kuota-cuti)
10. [Generate Surat (Printout)](#10-generate-surat-printout)
11. [Keamanan Sistem](#11-keamanan-sistem)
12. [Hosting & Deployment](#12-hosting--deployment)
13. [Panduan Serah Terima ke Dishub](#13-panduan-serah-terima-ke-dishub)

---

## 1. Latar Belakang & Tujuan

Saat ini proses pengajuan cuti di Dinas Perhubungan Kota Bogor dilakukan secara manual — karyawan mengisi form fisik, diserahkan ke kepegawaian, lalu data direkap manual ke Excel. Proses ini memakan waktu dan rawan kehilangan data.

**Tujuan sistem ini:**
- Karyawan bisa mengajukan cuti secara online tanpa datang langsung ke kepegawaian
- Admin kepegawaian bisa melihat semua pengajuan, mencetak surat, dan merekap data dari satu dashboard
- Data otomatis tersimpan ke Google Sheets (yang sudah biasa dipakai Dishub) secara realtime
- Memantau kuota cuti 12x/tahun per karyawan secara otomatis

---

## 2. Alur Sistem (Full Flow)

### Fase 1 — Karyawan Mengajukan Cuti
```
Karyawan buka website
  → Isi formulir online (tanpa login):
      - Nama lengkap
      - NIP
      - Tanggal lahir (untuk verifikasi privasi)
      - Jabatan
      - Bidang/Seksi
      - Shif
      - Tanggal cuti (mulai s.d. selesai)
      - Keperluan (Keperluan Keluarga / Sakit / Akad Nikah / Melahirkan / dll)
      - Kabid/Kasi (atasan langsung)
  → Backend validasi:
      - NIP terdaftar di database karyawan?
      - Sisa kuota cuti > 0 untuk tahun ini?
  → Jika lolos: data ditulis ke Google Sheets dengan STATUS = "Menunggu ACC"
  → Karyawan dapat notifikasi di layar: "Pengajuan berhasil dikirim"
```

### Fase 2 — Admin Memproses
```
Admin login ke website (username + password)
  → Dashboard menampilkan:
      - Daftar pengajuan berstatus "Menunggu ACC"
      - Histori semua pengajuan
      - Sisa kuota per karyawan
  → Admin pilih pengajuan → klik "Generate Surat"
  → Sistem otomatis mengisi template surat dari data yang ada
  → Admin klik "Cetak" → print fisik
```

### Fase 3 — ACC Atasan (Proses Fisik)
```
Surat fisik dikirim ke atasan langsung (Kabid/Kasi)
  → Ditandatangani Kabid/Kasi
  → Diteruskan ke Kasubag Umum dan Kepegawaian untuk ACC final
  → Jika DITOLAK: admin update status → "Ditolak", karyawan bisa cek via website
  → Jika DISETUJUI: lanjut ke Fase 4
```

### Fase 4 — Input Data & Update Sheets
```
Admin buka dashboard → update status pengajuan:
  → Status: "Disetujui"
  → Input Nomor Surat (contoh: 167/PKWT/VI/2026)
  → Backend otomatis update Google Sheets:
      - Kolom STATUS terisi "Disetujui"
      - Kolom NO SURAT terisi
      - Kuota cuti karyawan berkurang 1
  → Karyawan bisa cek status: buka website → masukkan NIP + Tanggal Lahir
```

---

## 3. Tech Stack

| Komponen | Teknologi | Alasan |
|---|---|---|
| Backend | Python + Flask | Mudah dipelajari, library lengkap, banyak tutorial |
| Database | Google Sheets API | Sudah familiar di Dishub, realtime, gratis |
| Generate Surat | python-docx | Isi template .docx otomatis dari data |
| Auth | Flask-Login + bcrypt | Standar keamanan password hashing |
| Session | Flask Session | Timeout otomatis |
| Frontend | HTML + CSS + vanilla JS | Ringan, tidak perlu framework berat |
| Hosting | Railway | Gratis untuk skala KKL, mudah deploy |
| Google Sheets Auth | google-auth + gspread | Library resmi Google untuk akses Sheets via Python |

### Dependencies (requirements.txt)
```
flask==3.0.3
flask-login==0.6.3
bcrypt==4.1.3
gspread==6.1.2
google-auth==2.30.0
python-docx==1.1.2
python-dotenv==1.0.1
gunicorn==22.0.0
```

---

## 4. Struktur Folder Project

```
sistem-cuti-dishub/
│
├── app.py                     # Entry point Flask
├── requirements.txt           # Dependencies
├── .env                       # Variabel rahasia (JANGAN di-upload ke GitHub)
├── .env.example               # Contoh .env tanpa nilai rahasia
├── .gitignore                 # Pastikan .env dan credentials.json masuk sini
├── Procfile                   # Untuk Railway: "web: gunicorn app:app"
│
├── config/
│   └── settings.py            # Konfigurasi app (nama instansi, kuota cuti, dll)
│
├── routes/
│   ├── public.py              # Route karyawan: form cuti, cek status
│   └── admin.py               # Route admin: dashboard, printout, update status
│
├── services/
│   ├── sheets_service.py      # Semua operasi baca/tulis Google Sheets
│   ├── auth_service.py        # Login, hash password, session
│   ├── surat_service.py       # Generate surat dari template .docx
│   └── kuota_service.py       # Logika hitung kuota cuti
│
├── templates/
│   ├── base.html              # Layout dasar (navbar, footer)
│   ├── form_cuti.html         # Halaman form karyawan (publik)
│   ├── cek_status.html        # Karyawan cek status via NIP + tgl lahir
│   ├── login.html             # Halaman login admin
│   └── admin/
│       ├── dashboard.html     # Dashboard utama admin
│       ├── detail_pengajuan.html
│       └── histori.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
└── template_surat/
    └── template_cuti_pkwt.docx   # Template surat cuti (dari file Dishub)
```

---

## 5. Setup & Instalasi

### A. Persiapan Awal

**1. Clone / buat project**
```bash
mkdir sistem-cuti-dishub
cd sistem-cuti-dishub
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

**2. Setup Google Sheets & Service Account**

- Buka [console.cloud.google.com](https://console.cloud.google.com)
- Buat project baru: "Sistem Cuti Dishub"
- Aktifkan **Google Sheets API** dan **Google Drive API**
- Buat **Service Account** → download file JSON credentials
- Simpan file JSON sebagai `credentials.json` di folder project
- Buka Google Sheets Dishub → klik Share → tambahkan email Service Account (ada di file JSON, bentuknya `xxx@xxx.iam.gserviceaccount.com`) dengan akses **Editor**

**3. Buat file `.env`**
```env
SECRET_KEY=isi_dengan_string_acak_panjang_minimal_32_karakter
SPREADSHEET_ID=isi_dengan_ID_spreadsheet_dishub
ADMIN_USERNAME=admin_kepegawaian
ADMIN_PASSWORD_HASH=isi_setelah_generate_hash_bcrypt
GOOGLE_CREDENTIALS_JSON=isi_dengan_isi_file_json_service_account_dalam_satu_baris
```

> **Catatan:** `SPREADSHEET_ID` ada di URL Google Sheets:  
> `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit`

**4. Generate password hash admin**
```python
# Jalankan sekali di terminal Python
import bcrypt
password = b"passwordAdminDishub"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed.decode())
# Salin hasilnya ke ADMIN_PASSWORD_HASH di .env
```

---

## 6. Database — Google Sheets

### Struktur Sheet yang Dibutuhkan

**Sheet 1: `CUTI 2026`** (data utama — sama dengan format Dishub yang ada)

| Kolom | Keterangan |
|---|---|
| NO | Nomor urut auto-increment |
| MASEHI | Bulan (contoh: "Juli 2026") |
| HARI | Tanggal cuti (contoh: "28 s.d. 29 Juli 2026") |
| NAMA | Nama lengkap karyawan |
| KEPERLUAN | Alasan cuti |
| NO SURAT | Diisi setelah ACC (contoh: "167/PKWT/VI/2026") |
| JABATAN | Jabatan karyawan |
| SEKSI | Bidang/Seksi |
| SHIF | Shift kerja |
| KABID/KASI | Nama atasan langsung |
| NIP | NIP karyawan |
| STATUS | **TAMBAHAN BARU:** "Menunggu ACC" / "Disetujui" / "Ditolak" / "Dibatalkan" |
| TGL_SUBMIT | **TAMBAHAN BARU:** Timestamp pengajuan |
| TAHUN | **TAMBAHAN BARU:** Tahun (untuk filter kuota) |

> Kolom STATUS, TGL_SUBMIT, dan TAHUN adalah tambahan baru. Kolom lainnya sama persis dengan format Excel Dishub yang sudah ada.

**Sheet 2: `DATA_KARYAWAN`** (master data — diisi sekali oleh admin)

| Kolom | Keterangan |
|---|---|
| NIP | NIP unik karyawan |
| NAMA | Nama lengkap |
| TGL_LAHIR | Format: YYYY-MM-DD (untuk verifikasi privasi) |
| JABATAN | Jabatan |
| SEKSI | Bidang/Seksi |
| SHIF | Shift default |
| KABID_KASI | Atasan langsung default |
| AKTIF | TRUE / FALSE |

### Logika Akses di `sheets_service.py`
```python
import gspread
from google.oauth2.service_account import Credentials
import json, os

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheets_client():
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def get_sheet(sheet_name):
    client = get_sheets_client()
    spreadsheet = client.open_by_key(os.environ["SPREADSHEET_ID"])
    return spreadsheet.worksheet(sheet_name)
```

---

## 7. Fitur Karyawan (Publik)

### 7.1 Form Pengajuan Cuti (`/`)
- Tidak perlu login
- Field yang diisi:
  - Nama lengkap
  - NIP (backend validasi ke Sheet `DATA_KARYAWAN`)
  - Tanggal lahir (validasi privasi — harus cocok dengan data karyawan)
  - Tanggal mulai cuti
  - Tanggal selesai cuti
  - Keperluan (dropdown: Keperluan Keluarga / Sakit / Akad Nikah / Istri Melahirkan / Cuti Istirahat/Pemulihan / Lainnya)
  - Shif (auto-isi dari data karyawan, bisa diubah)
  - Kabid/Kasi (auto-isi dari data karyawan)
- Setelah submit: tampilkan nomor referensi pengajuan

### 7.2 Cek Status Pengajuan (`/cek-status`)
- Input: NIP + Tanggal Lahir (bukan NIP saja — untuk privasi)
- Tampilkan: semua riwayat pengajuan karyawan tersebut + sisa kuota
- Status ditampilkan dengan warna: Menunggu (kuning) / Disetujui (hijau) / Ditolak (merah) / Dibatalkan (abu)

---

## 8. Fitur Admin (Terproteksi)

### 8.1 Login (`/admin/login`)
- Form username + password
- Maks 5x salah → kunci sementara 15 menit
- Session timeout: 30 menit tidak aktif → otomatis logout

### 8.2 Dashboard (`/admin/dashboard`)
- Tabel pengajuan berstatus "Menunggu ACC" (prioritas utama)
- Filter: bulan, seksi, status
- Setiap baris ada tombol: **Detail** | **Generate Surat** | **Setujui** | **Tolak**

### 8.3 Generate Surat (`/admin/generate-surat/<id>`)
- Backend baca data dari Sheets
- Isi template `template_cuti_pkwt.docx` dengan data karyawan
- Hasilkan file .docx yang siap diunduh dan dicetak
- Format surat mengikuti persis template Dishub yang ada (dua bagian: Surat Permohonan + Surat Cuti resmi)

### 8.4 Update Status (`/admin/update-status/<id>`)
- Admin ubah status ke "Disetujui" atau "Ditolak"
- Jika Disetujui: wajib isi Nomor Surat
- Backend update Sheets: kolom STATUS dan NO SURAT

### 8.5 Histori & Rekap (`/admin/histori`)
- Tabel semua pengajuan dengan filter tahun, bulan, seksi, status
- Per karyawan: tampilkan berapa kali cuti disetujui (kuota terpakai) dan sisa kuota
- Tombol export: download data sebagai file Excel (.xlsx)

---

## 9. Logika Kuota Cuti

```python
# services/kuota_service.py

KUOTA_TAHUNAN = 12  # Bisa diubah di config/settings.py

def hitung_kuota_terpakai(nip: str, tahun: int) -> int:
    """
    Hitung jumlah cuti DISETUJUI untuk NIP tertentu di tahun tertentu.
    Status Ditolak dan Dibatalkan TIDAK dihitung.
    """
    sheet = get_sheet("CUTI 2026")
    semua_data = sheet.get_all_records()
    
    terpakai = sum(
        1 for row in semua_data
        if str(row.get("NIP", "")).strip() == str(nip).strip()
        and str(row.get("TAHUN", "")) == str(tahun)
        and row.get("STATUS", "").strip() == "Disetujui"
    )
    return terpakai

def sisa_kuota(nip: str, tahun: int) -> int:
    return KUOTA_TAHUNAN - hitung_kuota_terpakai(nip, tahun)

def boleh_ajukan(nip: str, tahun: int) -> bool:
    return sisa_kuota(nip, tahun) > 0
```

**Aturan logika status:**

| Status | Data tersimpan? | Kuota berkurang? |
|---|---|---|
| Menunggu ACC | ✅ Ya | ❌ Tidak |
| Disetujui | ✅ Ya | ✅ Ya (-1) |
| Ditolak | ✅ Ya (histori) | ❌ Tidak |
| Dibatalkan | ✅ Ya (histori) | ❌ Tidak |

**Kuota reset otomatis:** Backend filter berdasarkan kolom `TAHUN`. Setiap 1 Januari, semua karyawan otomatis kembali ke 12/12 tanpa proses manual apapun.

---

## 10. Generate Surat (Printout)

Template surat mengikuti format Dishub yang sudah ada (file `Cuti-PKWT-2026.docx`), terdiri dari dua bagian dalam satu halaman:

**Bagian 1 — Surat Permohonan Cuti (dari karyawan)**
- Bogor, [tanggal]
- Perihal: Permohonan Cuti
- Kepada: Kepala Sub. Bag Umum dan Kepegawaian
- Data: Nama, Jabatan, Bidang/Seksi, Tanggal Cuti, Shif, Keperluan
- Kolom TTD: Mengetahui Atasan Langsung (kiri) | Pemohon (kanan)

**Bagian 2 — Surat Cuti Resmi (dari Kasubag Kepegawaian)**
- Nomor Surat: [diisi setelah ACC]
- Nama Kasubag: ETIN SUHARTINI, S.E | NIP: 19770726 201101 2 002
- Data karyawan: Nama, Jabatan, Seksi, Tanggal Cuti, Keperluan
- TTD: Ka. Sub. Bag Umum dan Kepegawaian

```python
# services/surat_service.py
from docx import Document
import io

def generate_surat(data: dict) -> bytes:
    """
    Isi template surat cuti dengan data dari Google Sheets.
    Return bytes file .docx siap download.
    """
    doc = Document("template_surat/template_cuti_pkwt.docx")
    
    replacements = {
        "{{NAMA}}": data["NAMA"],
        "{{NIP}}": data["NIP"],
        "{{JABATAN}}": data["JABATAN"],
        "{{SEKSI}}": data["SEKSI"],
        "{{SHIF}}": data["SHIF"],
        "{{TANGGAL_CUTI}}": data["HARI"],
        "{{KEPERLUAN}}": data["KEPERLUAN"],
        "{{KABID_KASI}}": data["KABID/KASI"],
        "{{NO_SURAT}}": data.get("NO SURAT", "___/PKWT/__/2026"),
        "{{TANGGAL_SURAT}}": data.get("TGL_SUBMIT", ""),
    }
    
    for paragraph in doc.paragraphs:
        for key, value in replacements.items():
            if key in paragraph.text:
                for run in paragraph.runs:
                    if key in run.text:
                        run.text = run.text.replace(key, value)
    
    # Tabel juga perlu dicek
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for key, value in replacements.items():
                        if key in paragraph.text:
                            for run in paragraph.runs:
                                if key in run.text:
                                    run.text = run.text.replace(key, value)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
```

> **Catatan:** Template `.docx` perlu disiapkan dulu dengan placeholder `{{NAMA}}`, `{{NIP}}`, dll di posisi yang tepat sesuai format surat Dishub.

---

## 11. Keamanan Sistem

### 11.1 Autentikasi Admin
```python
# services/auth_service.py
import bcrypt, os

def verify_password(password: str) -> bool:
    stored_hash = os.environ["ADMIN_PASSWORD_HASH"].encode()
    return bcrypt.checkpw(password.encode(), stored_hash)
```
- Password disimpan sebagai hash bcrypt — tidak ada yang tahu password aslinya
- Session timeout: 30 menit idle → auto logout
- Maks 5x login gagal → IP di-block sementara 15 menit
- Semua URL `/admin/*` dicek session token, jika tidak valid → redirect ke login

### 11.2 Keamanan Google Sheets
- Sheets di-set **Private** (Restricted) — tidak bisa diakses siapapun yang punya link
- Hanya Service Account + akun Gmail admin kepegawaian yang bisa buka
- Sheet data dikunci (Protected Range) — tidak bisa diedit langsung dari Google Sheets, hanya via website
- `GOOGLE_CREDENTIALS_JSON` disimpan di environment variable Railway, **tidak pernah** di kode atau GitHub

### 11.3 Keamanan Koneksi & Form
- **HTTPS**: Railway pasang SSL otomatis
- **CSRF Protection**: Setiap form punya token CSRF (pakai Flask-WTF atau custom middleware)
- **Rate limiting**: Form karyawan dibatasi 10 submit per IP per jam
- **Input sanitasi**: Semua input di-strip dan divalidasi sebelum ditulis ke Sheets

### 11.4 Privasi Karyawan
- Karyawan cek status pakai **NIP + Tanggal Lahir** (bukan NIP saja)
- Orang lain tidak bisa melihat data pengajuan karyawan lain meskipun tahu NIP-nya

### 11.5 File .gitignore
```
.env
credentials.json
venv/
__pycache__/
*.pyc
.DS_Store
```

---

## 12. Hosting & Deployment

### Saat KKL — Railway (Gratis)

**1. Siapkan `Procfile`**
```
web: gunicorn app:app
```

**2. Deploy ke Railway**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login dan deploy
railway login
railway init
railway up
```

**3. Set environment variables di Railway Dashboard**
- Masuk ke project Railway → Variables
- Tambahkan semua isi `.env` satu per satu
- `GOOGLE_CREDENTIALS_JSON` = paste seluruh isi file JSON credentials dalam satu baris

**4. Dapat link**
- Railway beri link otomatis: `https://nama-project.railway.app`
- Link ini yang diberikan ke kepala kepegawaian Dishub

### Setelah KKL — Niagahoster / Hostinger (Dishub lanjutkan)

| Layanan | Harga | Cara Bayar |
|---|---|---|
| Niagahoster VPS | ~Rp 45.000/bulan | Transfer bank / QRIS |
| Hostinger VPS | ~Rp 35.000/bulan | Transfer bank / QRIS |

- Support bahasa Indonesia, bisa dihubungi via chat
- Upload kode dari GitHub ke server baru
- Set environment variables sama seperti di Railway

---

## 13. Panduan Serah Terima ke Dishub

### Yang harus disiapkan sebelum KKL selesai:

**1. Kode sumber di GitHub**
- Upload ke GitHub (bisa private repository)
- Beri akses ke kepala kepegawaian atau staf IT Dishub
- Pastikan `.env` dan `credentials.json` **tidak** ikut terupload

**2. Pindahkan Google Sheets ke akun Gmail Dishub**
- Buka Google Sheets → Share → Transfer ownership ke Gmail Dishub
- **Jangan** biarkan Sheets di akun Gmail pribadi Anda
- Hapus akses Gmail pribadi Anda setelah transfer selesai

**3. Dokumen README untuk admin Dishub**
- Cara login ke dashboard admin
- Cara memproses pengajuan dan generate surat
- Cara update status dan input nomor surat
- Cara melihat rekap dan download Excel
- Cara ganti password admin (bila perlu)
- Kontak hosting (Niagahoster/Hostinger) untuk perpanjangan

**4. Checklist final sebelum serah terima:**
- [ ] Website bisa diakses dari jaringan eksternal (bukan hanya localhost)
- [ ] Form karyawan bisa disubmit dan data masuk ke Sheets
- [ ] Admin bisa login, lihat dashboard, generate surat, update status
- [ ] Sisa kuota karyawan terhitung dengan benar
- [ ] Surat yang digenerate formatnya sesuai template Dishub
- [ ] Google Sheets sudah pindah ke Gmail Dishub
- [ ] Kode ada di GitHub
- [ ] Dokumen panduan sudah ditulis

---

## Kontak & Referensi

- **gspread docs**: https://docs.gspread.org
- **python-docx**: https://python-docx.readthedocs.io
- **Flask**: https://flask.palletsprojects.com
- **Railway deployment**: https://docs.railway.app
- **Google Service Account**: https://console.cloud.google.com

---

*Dokumen ini dibuat sebagai panduan pengembangan sistem cuti online untuk proyek KKL di Dinas Perhubungan Kota Bogor. Struktur data disesuaikan dengan format Excel yang sudah digunakan (Cuti_P3K_PW.xlsx) dan format surat yang berlaku (Cuti-PKWT-2026.docx).*
