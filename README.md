# Sistem Pengajuan Cuti Online — Dinas Perhubungan Kota Bogor

Sistem pengajuan cuti berbasis web untuk Dinas Perhubungan Kota Bogor, Sub Bagian Umum dan Kepegawaian. Dibangun dengan Flask dan Google Sheets sebagai database.

## Fitur

### Karyawan (Publik)
- Ajukan cuti online tanpa perlu login
- Cek status pengajuan via NIP + Tanggal Lahir
- Jenis cuti: Tahunan, Sakit, Melahirkan, Besar, Alasan Penting
- Perhitungan kuota otomatis (12 hari kerja/tahun, cuti sakit tidak pakai kuota)

### Admin (Kepegawaian)
- Dashboard kelola pengajuan (ACC / Tolak)
- Generate surat cuti otomatis (.docx)
- Rekap data & export ke Excel (.xlsx)
- Kelola hari libur nasional
- Filter berdasarkan status, seksi, dan bulan
- Riwayat pengajuan lengkap

### Keamanan
- CSRF protection pada semua form
- Rate limiting (anti spam)
- Session timeout otomatis
- Security headers (CSP, HSTS, X-Frame-Options)
- Brute-force protection pada login admin

## Tech Stack

| Komponen | Teknologi |
|---|---|
| Backend | Flask 3.0 (Python 3.11) |
| Database | Google Sheets API (gspread) |
| Frontend | Tailwind CSS 3.4 + DaisyUI 4.12 |
| Datepicker | Flatpickr |
| Surat | python-docx |
| Export | openpyxl |
| Server | Gunicorn |

## Setup Lokal

### 1. Clone & Install

```bash
git clone https://github.com/SNNN-011/sistem-cuti-dishub.git
cd sistem-cuti-dishub

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### 2. Setup Google Cloud

1. Buka [console.cloud.google.com](https://console.cloud.google.com)
2. Buat project baru (misal: "Sistem Cuti Dishub")
3. Aktifkan **Google Sheets API** dan **Google Drive API**
4. Buat **Service Account** di menu IAM > Service Accounts
5. Download file JSON credentials
6. Buat Google Sheets baru, lalu **Share** ke email Service Account sebagai **Editor**

### 3. Buat `.env`

```bash
cp .env.example .env
```

Isi semua variabel:

| Variable | Keterangan |
|---|---|
| `SECRET_KEY` | Random string 32+ karakter untuk keamanan session |
| `SPREADSHEET_ID` | ID Google Sheets (ambil dari URL: `docs.google.com/spreadsheets/d/INI_ID/...`) |
| `ADMIN_USERNAME` | Username admin (default: `admin_kepegawaian`) |
| `ADMIN_PASSWORD_HASH` | Hash bcrypt dari password admin (generate via step 4) |
| `GOOGLE_CREDENTIALS_JSON` | Seluruh isi file JSON service account |

### 4. Generate Password Admin

```bash
python generate_hash.py
```

Copy output hash ke `ADMIN_PASSWORD_HASH` di `.env`.

### 5. Setup Google Sheets

```bash
python setup_sheets.py
```

Script ini akan membuat sheet yang dibutuhkan (DATA_KARYAWAN, CUTI 2026, HARI_LIBUR) dan mengisi data awal dari template CSV.

### 6. Jalankan

```bash
python app.py
```

Buka http://localhost:5000

## Deploy ke Railway

### Via Dashboard (Disarankan)

1. Buka [railway.app](https://railway.app), login dengan GitHub
2. Klik **New Project** > **Deploy from GitHub Repo**
3. Pilih repo `sistem-cuti-dishub`
4. Railway otomatis detect Flask dari `Procfile`
5. Buka tab **Variables**, tambahkan semua environment variables (sama dengan isi `.env`):
   - `SECRET_KEY`
   - `SPREADSHEET_ID`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD_HASH`
   - `GOOGLE_CREDENTIALS_JSON` (seluruh isi JSON service account)
6. Deploy otomatis jalan, tunggu sampai status "Active"
7. Klik tab **Settings** > **Networking** > **Generate Domain** untuk dapat URL publik

### Via CLI

```bash
npm install -g @railway/cli
railway login
railway init
railway up
railway variables set SECRET_KEY="nilai_random_kamu"
railway variables set SPREADSHEET_ID="id_sheets_kamu"
railway variables set ADMIN_USERNAME="admin_kepegawaian"
railway variables set ADMIN_PASSWORD_HASH="hash_bcrypt_kamu"
railway variables set GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

### Catatan Deploy

- Railway otomatis set `PORT` environment variable, Gunicorn akan listen di port tersebut
- Pastikan `SESSION_COOKIE_SECURE = True` sudah aktif (otomatis di production, bukan `__main__`)
- Google Sheets API tidak perlu IP whitelist, cukup service account

## Struktur Project

```
sistem-cuti-dishub/
├── app.py                    # Entry point Flask
├── models.py                 # Model admin user
├── config/
│   ├── settings.py           # Konfigurasi dari env
│   └── constants.py          # Konstanta (nama bulan, dll)
├── routes/
│   ├── public.py             # Route karyawan (publik)
│   └── admin.py              # Route admin (terproteksi)
├── services/
│   ├── auth_service.py       # Autentikasi admin
│   ├── kuota_service.py      # Hitung kuota & hari kerja
│   ├── security.py           # CSRF, rate limit, headers
│   ├── sheets_service.py     # Operasi Google Sheets
│   └── surat_service.py      # Generate surat .docx
├── templates/                # HTML templates (Jinja2)
│   ├── base.html
│   ├── form_cuti.html
│   ├── cek_status.html
│   ├── login.html
│   └── admin/
│       ├── dashboard.html
│       ├── detail_pengajuan.html
│       ├── hari_libur.html
│       └── histori.html
├── static/                   # CSS, JS, vendor
├── template_sheets/          # Template CSV untuk setup
├── requirements.txt          # Dependencies Python
├── package.json              # Dependencies Node (Tailwind)
├── Procfile                  # Railway/Heroku config
├── runtime.txt               # Python version untuk Railway
├── tailwind.config.js        # Konfigurasi Tailwind
└── .env.example              # Template environment variables
```

## Akses Default

| Halaman | URL |
|---|---|
| Form Pengajuan Cuti | `/` |
| Cek Status | `/cek-status` |
| Login Admin | `/admin/login` |
| Dashboard Admin | `/admin/dashboard` |

## License

Dikembangkan untuk Dinas Perhubungan Kota Bogor.
