# Panduan Pengujian — Sistem Cuti Dishub

> **Tanggal:** 30 Juli 2026
> **Total perbaikan:** 5 temuan audit
> **File yang dimodifikasi:** `config/settings.py`, `app.py`, `services/sheets_service.py`, `services/security.py`, `routes/public.py`

---

## Daftar Isi

1. [SECRET_KEY — Validasi Startup](#1-secret_key--validasi-startup)
2. [NO SURAT — Penulisan saat Approve](#2-no_surat--penulisan-saat-approve)
3. [X-Forwarded-For Spoofing](#3-x-forwarded-for-spoofing)
4. [Mutasi Data Cache Karyawan](#4-mutasi-data-cache-karyawan)
5. [Format Tanggal Cross-Month](#5-format-tanggal-cross-month)
6. [Smoke Test Aplikasi](#6-smoke-test-aplikasi)

---

## 1. SECRET_KEY — Validasi Startup

### Apa yang diperbaiki
App sekarang menolak startup jika `SECRET_KEY` belum diset atau masih menggunakan nilai default `"change-me-in-production"`. Ini mencegah deployment dengan key yang tidak aman.

### Cara menguji

#### Test A: App GAGAL tanpa SECRET_KEY
1. Pastikan environment variable `SECRET_KEY` **tidak diset** (hapus dari `.env` dan dari env).
2. Jalankan: `python app.py`
3. **Yang diharapkan:** App crash dengan `RuntimeError` berisi pesan:
   ```
   SECRET_KEY belum dikonfigurasi! Set environment variable SECRET_KEY
   dengan nilai random yang aman sebelum menjalankan aplikasi.
   ```

#### Test B: App GAGAL dengan default value
1. Set `SECRET_KEY=change-me-in-production` di `.env`.
2. Jalankan: `python app.py`
3. **Yang diharapkan:** Sama seperti Test A — app crash dengan RuntimeError.

#### Test C: App BERHASIL dengan SECRET_KEY valid
1. Set `SECRET_KEY=rahasia123abc` di `.env` (atau nilai random lain).
2. Jalankan: `python app.py`
3. **Yang diharapkan:** App berjalan normal, server start tanpa error.

### Edge cases
- [ ] SECRET_KEY kosong string (`SECRET_KEY=""`) → harus gagal
- [ ] SECRET_KEY dengan spasi saja (`SECRET_KEY="   "`) → harus gagal (perlu trim check)
- [ ] SECRET_KEY yang sangat panjang (256+ karakter) → harus berhasil

---

## 2. NO SURAT — Penulisan saat Approve

### Apa yang diperbaiki
Fungsi `update_row_status()` sekarang menulis parameter `no_surat` ke kolom "NO SURAT" di spreadsheet ketika diberikan.

### Cara menguji

#### Test A: Approve DENGAN no_surat
1. Login ke admin panel (`/admin/login`).
2. Temukan pengajuan dengan status "Menunggu ACC".
3. Klik Approve dan isi field "No Surat" dengan nilai, misal: `"001/CUTI/VII/2026"`.
4. **Yang diharapkan:**
   - Status berubah menjadi "Disetujui"
   - Kolom "NO SURAT" di Google Sheets terisi `"001/CUTI/VII/2026"`

#### Test B: Approve TANPA no_surat
1. Approve pengajuan tanpa mengisi No Surat (kosongkan).
2. **Yang diharapkan:**
   - Status berubah menjadi "Disetujui"
   - Kolom "NO SURAT" tetap kosong (tidak overwrite data existing)

#### Test C: Reject dengan no_surat
1. Reject pengajuan sambil mengisi no_surat.
2. **Yang diharapkan:**
   - Status berubah menjadi "Ditolak"
   - Kolom "NO SURAT" terisi (karena parameter diberikan)

### Edge cases
- [ ] `no_surat=None` → tidak menulis ke kolom
- [ ] `no_surat=""` (string kosong) → tidak menulis ke kolom
- [ ] `no_surat="   "` (spasi saja) → tidak menulis ke kolom
- [ ] `no_surat` dengan karakter khusus → tetap terisi apa adanya

### Verifikasi di Google Sheets
Buka spreadsheet langsung di browser → sheet "CUTI 2026" → pastikan kolom "NO SURAT" (kolom F) terisi sesuai input.

---

## 3. X-Forwarded-For Spoofing

### Apa yang diperbaiki
`get_real_ip()` sekarang hanya mempercayai header `X-Forwarded-For` jika request berasal dari proxy yang terdaftar di `TRUSTED_PROXIES`. Tanpa proxy terdaftar, IP selalu dari `REMOTE_ADDR`.

### Cara menguji

#### Test A: Tanpa TRUSTED_PROXIES (default)
1. Pastikan `TRUSTED_PROXIES` **tidak diset** di environment.
2. Kirim request ke app dengan header `X-Forwarded-For: 1.2.3.4`.
3. **Yang diharapkan:** App mengabaikan header XFF, menggunakan `REMOTE_ADDR` (misal `127.0.0.1`).

#### Test B: Dengan TRUSTED_PROXIES
1. Set `TRUSTED_PROXIES=10.0.0.1` di environment.
2. Kirim request dari IP `10.0.0.1` dengan header `X-Forwarded-For: 203.0.113.50`.
3. **Yang diharapkan:** App menggunakan `203.0.113.50` sebagai client IP.

#### Test C: Dengan TRUSTED_PROXIES tapi request bukan dari proxy
1. Set `TRUSTED_PROXIES=10.0.0.1`.
2. Kirim request dari IP `192.168.1.100` (bukan proxy terdaftar) dengan header `X-Forwarded-For: 8.8.8.8`.
3. **Yang diharapkan:** App mengabaikan XFF, menggunakan `192.168.1.100`.

### Cara test manual dengan curl
```bash
# Tanpa trusted proxy — XFF diabaikan
curl -H "X-Forwarded-For: 99.99.99.99" http://localhost:5000/

# Cek di log server apakah IP yang tercatat adalah 127.0.0.1, bukan 99.99.99.99
```

### Edge cases
- [ ] `TRUSTED_PROXIES` kosong → XFF selalu diabaikan
- [ ] Multiple IPs di XFF (`"1.1.1.1, 2.2.2.2"`) → mengambil IP pertama saja
- [ ] `TRUSTED_PROXIES` dengan banyak IP (dipisah koma) → salah satu harus match
- [ ] Request tanpa header XFF sama sekali → menggunakan REMOTE_ADDR

---

## 4. Mutasi Data Cache Karyawan

### Apa yang diperbaiki
Fungsi `get_karyawan_by_nip()` sekarang membuat salinan (`dict(r)`) sebelum memodifikasi record, sehingga data cache tidak ikut berubah.

### Cara menguji

#### Test A: Cache tidak berubah setelah lookup
1. Jalankan app dan akses `/` (form cuti) atau `/api/karyawan/validate/<nip>`.
2. Lakukan lookup NIP yang valid (misal NIP `198506152010012001`).
3. Lakukan lookup NIP **yang sama** lagi.
4. **Yang diharapkan:** Data yang dikembalikan konsisten — `TGL_LAHIR` terisi dengan benar setiap saat, tidak bergantung pada urutan lookup.

#### Test B: Bandingkan data cache vs data baru
1. Di Python console (dengan app context):
   ```python
   from services.sheets_service import get_all_records, get_karyawan_by_nip
   from config.settings import SHEET_KARYAWAN

   records = get_all_records(SHEET_KARYAWAN)
   r_before = [r for r in records if r.get("NI PPPK PW") == "198506152010012001"][0]
   print("Before:", r_before.get("TGL_LAHIR"))  # Harus: '' (kosong, tidak ada kolom ini)

   karyawan = get_karyawan_by_nip("198506152010012001")
   print("Returned:", karyawan.get("TGL_LAHIR"))  # Harus: '1985-06-15'

   r_after = [r for r in records if r.get("NI PPPK PW") == "198506152010012001"][0]
   print("After:", r_after.get("TGL_LAHIR"))  # Harus: '' (TIDAK berubah!)
   ```
2. **Yang diharapkan:** `r_after` tidak memiliki `TGL_LAHIR` — cache tidak termutasi.

### Edge cases
- [ ] NIP dengan panjang < 8 digit → `TGL_LAHIR` kosong di copy, tidak di cache
- [ ] NIP yang tidak ditemukan → return `None`, cache tetap bersih
- [ ] Concurrent requests → tidak ada race condition pada cache

---

## 5. Format Tanggal Cross-Month

### Apa yang diperbaiki
Format tanggal cuti yang melintasi bulan sekarang menampilkan nama bulan lengkap untuk kedua tanggal. Contoh: "28 Juni s.d. 3 Juli 2026" (bukan "28 s.d. 3 Juli 2026").

### Cara menguji

#### Test A: Same-day (1 hari)
1. Ajukan cuti untuk 1 hari, misal: `2026-07-15` s/d `2026-07-15`.
2. **Yang diharapkan:** Kolom HARI menampilkan `"15 Juli 2026"`.

#### Test B: Same-month (beberapa hari, bulan sama)
1. Ajukan cuti: `2026-07-10` s/d `2026-07-15`.
2. **Yang diharapkan:** `"10 s.d. 15 Juli 2026"`.

#### Test C: Cross-month ⭐ (yang diperbaiki)
1. Ajukan cuti: `2026-06-28` s/d `2026-07-03`.
2. **Yang diharapkan:** `"28 Juni 2026 s.d. 3 Juli 2026"` ← **BENAR**
3. **Bukan:** `"28 s.d. 3 Juli 2026"` ← **SALAH (bug sebelumnya)**

#### Test D: Cross-year
1. Ajukan cuti: `2026-12-29` s/d `2027-01-03`.
2. **Yang diharapkan:** `"29 Desember 2026 s.d. 3 Januari 2027"`.

#### Test E: Akhir bulan Februari → Maret
1. Ajukan cuti: `2026-02-27` s/d `2026-03-02`.
2. **Yang diharapkan:** `"27 Februari 2026 s.d. 2 Maret 2026"`.

### Verifikasi di Spreadsheet
Buka sheet "CUTI 2026" → kolom "HARI" (kolom C) → pastikan format menampilkan bulan lengkap untuk kedua tanggal.

### Edge cases
- [ ] Tanggal akhir bulan 31 → awal bulan berikutnya
- [ ] Tanggal yang sama tapi beda bulan (misal 30 Juni → 30 Juli) → kedua bulan terlihat
- [ ] Leap year: 28 Feb → 1 Mar

---

## 6. Smoke Test Aplikasi

Jalankan checklist ini setelah semua perbaikan untuk memastikan app berfungsi normal.

### Persiapan
- [ ] `.env` sudah diset: `SECRET_KEY`, `SPREADSHEET_ID`, `GOOGLE_CREDENTIALS_JSON`, `ADMIN_PASSWORD_HASH`
- [ ] `python app.py` berhasil start tanpa error
- [ ] Server berjalan di `http://localhost:5000`

### Halaman Publik
- [ ] `GET /` — form cuti tampil dengan benar
- [ ] Isi form lengkap → submit → pengajuan berhasil masuk spreadsheet
- [ ] `GET /cek-status` — halaman cek status tampil
- [ ] Cek status dengan NIP dan tanggal lahir valid → data pengajuan tampil
- [ ] `GET /api/karyawan/validate/<nip_valid>` → JSON `{"valid": true}`
- [ ] `GET /api/karyawan/validate/00000000` → JSON `{"valid": false}`

### Halaman Admin
- [ ] `GET /admin/login` — form login tampil
- [ ] Login dengan credentials yang benar → masuk dashboard
- [ ] Dashboard menampilkan statistik (menunggu, disetujui, ditolak)
- [ ] Approve pengajuan dengan no_surat → status & no_surat ter-update
- [ ] Reject pengajuan → status berubah menjadi "Ditolak"

### Keamanan
- [ ] Submit form tanpa CSRF token → 403 Forbidden
- [ ] Rate limiting: >10 submit dalam 1 jam → 429 Too Many Requests
- [ ] Header keamanan ada di response: `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`
- [ ] Session cookie punya flag `HttpOnly`, `SameSite=Lax`

### Error Handling
- [ ] Akses halaman yang tidak ada → 404
- [ ] NIP tidak terdaftar → flash message error
- [ ] Tanggal lahir salah → flash message error
- [ ] Google Sheets API down → error message yang user-friendly (bukan stack trace)

---

## Checklist Cepat (Copy-Paste)

```
□ [FIX 1] SECRET_KEY kosong → app gagal start dengan pesan jelas
□ [FIX 1] SECRET_KEY valid → app start normal
□ [FIX 2] Approve + no_surat → kolom NO SURAT terisi
□ [FIX 2] Approve tanpa no_surat → kolom NO SURAT tidak berubah
□ [FIX 3] Tanpa TRUSTED_PROXIES → XFF diabaikan
□ [FIX 3] Dengan TRUSTED_PROXIES → XFF dipercaya dari proxy terdaftar
□ [FIX 4] Lookup NIP → cache tidak termutasi
□ [FIX 5] Tanggal cross-month → "28 Juni 2026 s.d. 3 Juli 2026"
□ [FIX 5] Tanggal same-month → "10 s.d. 15 Juli 2026"
□ [FIX 5] Tanggal same-day → "15 Juli 2026"
□ App start, form submit, admin login, approve/reject → semua normal
```

---

*File ini dibuat otomatis sebagai bagian dari remediasi temuan audit.*
