# Panduan Testing Manual — Sistem Cuti Dishub

> **Untuk:** Yasin (developer/admin)
> **Terakhir update:** 31 Juli 2026
> **Server:** http://127.0.0.1:5000 (pastikan `python app.py` sudah jalan)

---

## Daftar Isi

1. [SECRET_KEY — Validasi Startup](#1-secret_key)
2. [Form Cuti — Submit & Redirect](#2-form-cuti)
3. [Cek Status — Auto & Manual](#3-cek-status)
4. [Admin Login & Dashboard](#4-admin-login)
5. [Approve/Reject + No Surat](#5-approve-reject)
6. [Logout via POST](#6-logout)
7. [Dark Mode](#7-dark-mode)
8. [Month Picker](#8-month-picker)
9. [Loading State on Submit](#9-loading-state)
10. [Mobile Responsiveness](#10-mobile)
11. [SEO Meta Tags](#11-seo)
12. [Edge Cases](#12-edge-cases)

---

## 1. SECRET_KEY

### Apa yang dicek
App menolak start jika SECRET_KEY belum diset atau masih default.

### Step-by-step

**Test A — Gagal tanpa SECRET_KEY:**
1. Buka file `.env` di project root
2. Hapus baris `SECRET_KEY=...` atau set kosong: `SECRET_KEY=`
3. Terminal: `python app.py`
4. ✅ Harap: app crash dengan pesan `RuntimeError: SECRET_KEY belum dikonfigurasi!`
5. Kembalikan SECRET_KEY setelah test

**Test B — Berhasil dengan SECRET_KEY valid:**
1. Set `SECRET_KEY=rahasia123abc` di `.env`
2. Terminal: `python app.py`
3. ✅ Harap: server start normal, `Running on http://127.0.0.1:5000`

---

## 2. Form Cuti — Submit & Redirect

### Apa yang dicek
Form submit berhasil → auto-redirect ke cek-status → data langsung tampil. Loading state muncul saat submit.

### Step-by-step

1. Buka http://127.0.0.1:5000/
2. Isi form:
   - **NI PPPK PW:** `199709052025211062` (atau NIP valid lain)
   - Klik di luar field → ✅ Harap: muncul "✓ NIP terdaftar" hijau
   - **Nama Lengkap:** isi manual (contoh: "ABDUL MALIK")
   - **Tanggal Lahir:** pilih tanggal (otomatis dari NIP)
   - **Jabatan:** isi manual
   - **Bidang/Seksi:** pilih dari dropdown
   - **Tanggal Mulai & Selesai:** pilih tanggal
   - **Keperluan:** isi alasan cuti
3. Klik **Ajukan Cuti**
4. ✅ Harap: tombol berubah jadi "Memproses..." dan disabled (loading state)
5. ✅ Harap: redirect ke halaman `/cek-status` dengan data pengajuan langsung tampil
6. ✅ Harap: flash hijau "Pengajuan berhasil dikirim!"

### Edge case — NIP tidak valid:
1. Isi NIP: `000000000000`
2. ✅ Harap: muncul "✗ NIP tidak terdaftar" merah

### Edge case — Tanggal selesai < mulai:
1. Tanggal mulai: 15 Juli, selesai: 10 Juli
2. ✅ Harap: flash error "Tanggal selesai tidak boleh sebelum tanggal mulai"

---

## 3. Cek Status — Auto & Manual

### Apa yang dicek
Cek status manual (isi NIP + TGL_LAHIR sendiri) dan auto (redirect dari form).

### Step-by-step — Manual:

1. Buka http://127.0.0.1:5000/cek-status
2. Isi:
   - **NI PPPK PW:** `199709052025211062`
   - **Tanggal Lahir:** sesuai 8 digit pertama NIP (format: `YYYY-MM-DD`)
3. Klik **Cek Status**
4. ✅ Harap: tombol "Memproses..." saat loading
5. ✅ Harap: tampil nama, NIP, sisa kuota, dan daftar pengajuan

### Edge case — Tanggal lahir salah:
1. Isi tanggal lahir yang salah
2. ✅ Harap: flash error "Tanggal lahir tidak sesuai"

### Edge case — NIP tidak ada pengajuan:
1. Cek NIP yang belum pernah mengajukan cuti
2. ✅ Harap: tampil "Belum ada pengajuan cuti"

---

## 4. Admin Login & Dashboard

### Apa yang dicek
Login admin, dashboard statistik, filter bulan.

### Step-by-step:

1. Buka http://127.0.0.1:5000/admin/login
2. Isi:
   - **Username:** `admin_kepegawaian`
   - **Password:** (sesuai `.env`)
3. Klik **Login**
4. ✅ Harap: tombol "Memproses..." saat loading
5. ✅ Harap: redirect ke dashboard dengan 4 kartu statistik (Menunggu, Disetujui, Ditolak, Total)
6. Coba filter **Bulan** → pilih dari dropdown (bukan text input)
7. ✅ Harap: data ter-filter sesuai bulan yang dipilih
8. Coba filter **Status** → pilih "Semua"
9. ✅ Harap: tampil semua data

### Edge case — Login salah:
1. Isi password salah
2. ✅ Harap: flash error, setelah 5x gagal → lockout 15 menit

---

## 5. Approve/Reject + No Surat

### Apa yang dicek
Approve & reject menulis no_surat ke sheet.

### Step-by-step — Approve:

1. Login admin → Dashboard
2. Klik pengajuan status "Menunggu ACC"
3. Isi **No Surat:** `001/CUTI/VII/2026`
4. Klik **Approve**
5. ✅ Harap: status berubah "Disetujui"
6. Buka Google Sheets → sheet "CUTI 2026" → cari baris tersebut
7. ✅ Harap: kolom "NO SURAT" terisi `001/CUTI/VII/2026`

### Step-by-step — Reject:

1. Klik pengajuan status "Menunggu ACC"
2. Isi **No Surat:** `REF/REJECT/001` (opsional)
3. Klik **Reject**
4. ✅ Harap: status berubah "Ditolak"
5. Buka Google Sheets → ✅ Harap: kolom "NO SURAT" terisi jika diisi

### Edge case — Approve tanpa no_surat:
1. Klik Approve tanpa isi No Surat
2. ✅ Harap: flash error "Nomor Surat wajib diisi untuk status Disetujui"

---

## 6. Logout via POST

### Apa yang dicek
Logout sekarang pakai POST + CSRF (bukan GET). Mencegah CSRF logout.

### Step-by-step:

1. Login admin → Dashboard
2. Lihat tombol **Logout** di navbar
3. Klik **Logout**
4. ✅ Harap: redirect ke halaman login, session cleared
5. ✅ Harap: tombol "Memproses..." saat loading

### Edge case — Logout via GET:
1. Buka http://127.0.0.1:5000/admin/logout langsung di browser
2. ✅ Harap: **405 Method Not Allowed** (bukan logout)

---

## 7. Dark Mode

### Apa yang dicek
Toggle dark mode di desktop dan mobile.

### Step-by-step:

1. Buka http://127.0.0.1:5000/
2. Lihat navbar → klik tombol 🌙 (bulan) di pojok kanan
3. ✅ Harap: halaman berubah ke dark mode (background gelap, teks terang)
4. Klik tombol ☀️ (matahari) → ✅ Harap: kembali ke light mode
5. **Tutup browser** → buka lagi
6. ✅ Harap: tema tersimpan (localStorage), tetap di mode terakhir

### Mobile:
1. Buka di HP → tap tombol 🌙/☀️ di navbar
2. ✅ Harap: toggle berfungsi sama

---

## 8. Month Picker

### Apa yang dicek
Filter bulan di dashboard dan histori pakai dropdown.

### Step-by-step:

1. Login admin → Dashboard
2. Lihat filter **Bulan** → ✅ Harap: dropdown select (bukan text input)
3. Pilih "Juli" → ✅ Harap: data ter-filter
4. Pilih "Semua" → ✅ Harap: tampil semua data
5. Buka halaman **Histori** → ✅ Harap: filter bulan juga dropdown

---

## 9. Loading State on Submit

### Apa yang dicek
Semua form menampilkan loading state saat submit.

### Step-by-step:

1. Buka form cuti, login, atau cek status
2. Isi form lengkap
3. Klik tombol submit
4. ✅ Harap: tombol berubah jadi "Memproses..." dan disabled (tidak bisa di-click lagi)
5. ✅ Harap: setelah selesai, halaman redirect atau flash muncul

### Verifikasi — Double submit prevention:
1. Isi form cuti
2. Klik submit, lalu langsung klik lagi cepat
3. ✅ Harap: hanya 1 request yang masuk (tombol sudah disabled)

---

## 10. Mobile Responsiveness

### Apa yang dicek
Semua halaman responsif di mobile.

### Step-by-step:

1. Buka di HP (atau Chrome DevTools → toggle device toolbar)
2. **Form cuti:**
   - ✅ Harap: form 1 kolom, input cukup besar untuk di-tap (44px min)
   - ✅ Harap: tabel bisa di-scroll horizontal
3. **Navbar:**
   - ✅ Harap: hamburger menu (☰) muncul di mobile
   - Tap ☰ → ✅ Harap: menu dropdown muncul (pakai event listener, bukan inline onclick)
4. **Dashboard:**
   - ✅ Harap: kartu statistik stack vertikal
   - ✅ Harap: filter form grid responsif
5. **Cek status:**
   - ✅ Harap: form dan hasil tampil rapi

---

## 11. SEO Meta Tags

### Apa yang dicek
Halaman punya meta tags yang benar.

### Step-by-step:

1. Buka http://127.0.0.1:5000/
2. Klik kanan → "View Page Source"
3. Cari `<head>` section
4. ✅ Harap: ada `<meta name="description" content="...">`
5. ✅ Harap: ada `<meta property="og:title" content="...">`
6. ✅ Harap: ada `<meta property="og:description" content="...">`
7. ✅ Harap: ada `<title>Sistem Cuti Dishub</title>` (atau judul halaman)

---

## 12. Edge Cases

### Session expired:
1. Login admin
2. Tunggu > 30 menit (atau sesuai `SESSION_TIMEOUT_MINUTES`)
3. Klik halaman admin
4. ✅ Harap: redirect ke login

### Google Sheets down:
1. Matikan internet / block sheets.googleapis.com
2. Buka halaman apapun
3. ✅ Harap: error message user-friendly (bukan stack trace)

### Flash auto-dismiss:
1. Submit form cuti (berhasil atau gagal)
2. ✅ Harap: flash message muncul
3. Tunggu 5 detik
4. ✅ Harap: flash message hilang otomatis (fade out)

### Rate limit — GET tidak di-rate-limit:
1. Buka http://127.0.0.1:5000/ sebanyak 15x
2. ✅ Harap: tidak ada 429 error (GET tidak di-rate-limit)

---

## Checklist Cepat (Copy-Paste)

```
□ SECRET_KEY kosong → app gagal start
□ SECRET_KEY valid → app start normal
□ Submit form cuti → loading state "Memproses..." → redirect ke cek-status → data tampil
□ NIP valid → "✓ NIP terdaftar"
□ NIP invalid → "✗ NIP tidak terdaftar"
□ Cek status manual → loading state → data pengajuan tampil
□ Tanggal lahir salah → flash error
□ Login admin → loading state → dashboard tampil
□ Filter bulan → dropdown select
□ Approve + no_surat → tercatat di Google Sheets
□ Reject + no_surat → tercatat di Google Sheets
□ Approve tanpa no_surat → error wajib isi
□ Logout → POST + CSRF, GET → 405
□ Dark mode toggle → berfungsi
□ Dark mode tersimpan setelah tutup browser
□ Flash auto-dismiss → hilang setelah 5 detik
□ Mobile → navbar hamburger (event listener), form 1 kolom
□ SEO meta tags → ada di page source
□ Session expired → redirect ke login
□ GET `/` 15x → tidak kena rate limit
```

---

## Test Otomatis (via curl/terminal)

Test berikut sudah dijalankan otomatis dan hasilnya valid:

| Test | Hasil |
|------|-------|
| API validate NIP valid | ✅ `{"valid": true}` |
| API validate NIP invalid | ✅ `{"valid": false}` |
| API validate non-numeric NIP | ✅ `{"valid": false}` |
| CSRF token missing → POST | ✅ 403 Forbidden |
| Security headers | ✅ X-Content-Type-Options, X-Frame-Options, CSP ada |
| Rate limit API (30/min) | ✅ 429 setelah 28 request |
| Rate limit form POST (10/hr) | ✅ 429 setelah 10 request |
| Rate limit GET `/` (tidak di-rate-limit) | ✅ 15 request tanpa 429 |
| XSS di NIP field | ✅ di-reject (non-numeric) |
| NIP terlalu panjang (>20 digit) | ✅ di-reject |
| 404 page | ✅ tampil |
| Logout GET → 405 | ✅ Method Not Allowed |
| Session cookie HttpOnly + SameSite=Lax | ✅ dikonfigurasi di app.py |

---

*File ini berisi test yang hanya bisa dilakukan secara manual di browser.*
*Test via curl/terminal dijalankan otomatis oleh AI agent.*
