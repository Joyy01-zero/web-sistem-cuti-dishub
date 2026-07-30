# Sistem Pengajuan Cuti Online — Dinas Perhubungan Kota Bogor

Sistem pengajuan cuti berbasis web untuk Dinas Perhubungan Kota Bogor.

## Fitur

- **Karyawan**: Ajukan cuti online tanpa login, cek status via NIP + Tanggal Lahir
- **Admin**: Dashboard kelola pengajuan, generate surat .docx, rekap & export Excel
- **Kuota**: Otomatis hitung sisa kuota cuti 12x/tahun per karyawan
- **Database**: Google Sheets (realtime, familiar di Dishub)

## Setup

### 1. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Setup Google Cloud

1. Buka [console.cloud.google.com](https://console.cloud.google.com)
2. Buat project baru: "Sistem Cuti Dishub"
3. Aktifkan **Google Sheets API** dan **Google Drive API**
4. Buat **Service Account** → download file JSON credentials
5. Buat Google Sheets baru → Share ke email Service Account (Editor)

### 3. Buat `.env`

Copy `.env.example` ke `.env`, isi semua nilai:

```bash
cp .env.example .env
```

### 4. Generate password admin

```bash
python generate_hash.py
```

### 5. Setup Google Sheets

```bash
python setup_sheets.py
```

### 6. Jalankan

```bash
python app.py
```

Buka http://localhost:5000

## Deploy ke Railway

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

Set environment variables di Railway Dashboard (sama dengan isi `.env`).

## Struktur

```
app.py                  # Entry point Flask
config/settings.py      # Konfigurasi
routes/public.py        # Route karyawan (publik)
routes/admin.py         # Route admin (terproteksi)
services/               # Logic bisnis
templates/              # HTML templates
static/                 # CSS + JS
template_surat/         # Template .docx surat cuti
```
