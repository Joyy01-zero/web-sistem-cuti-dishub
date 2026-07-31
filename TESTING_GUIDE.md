# Panduan Testing Manual — Sistem Cuti Dishub

> **Untuk:** Yasin (developer/admin)
> **Tanggal:** 30 Juli 2026
> **Server:** http://127.0.0.1:5000 (pastikan `python app.py` sudah jalan)

---

## Daftar Isi

1. [SECRET_KEY — Validasi Startup](#1-secret_key)
2. [Form Cuti — Submit & Redirect](#2-form-cuti)
3. [Cek Status — Auto & Manual](#3-cek-status)
4. [Admin Login & Dashboard](#4-admin-login)
5. [Approve/Reject + No Surat](#5-approve-reject)
6. [Dark Mode](#6-dark-mode)
7. [Month Picker](#7-month-picker)
8. [Mobile Responsiveness](#8-mobile)
9. [Edge Cases](#9-edge-cases)

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
Form submit berhasil → auto-redirect ke cek-status → data langsung tampil.

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
4. ✅ Harap: redirect ke halaman `/cek-status` dengan data pengajuan langsung tampil
5. ✅ Harap: flash hijau "Pengajuan berhasil dikirim!"

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
4. ✅ Harap: tampil nama, NIP, sisa kuota, dan daftar pengajuan

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
4. ✅ Harap: redirect ke dashboard dengan 4 kartu statistik (Menunggu, Disetujui, Ditolak, Total)
5. Coba filter **Bulan** → pilih dari dropdown (bukan text input)
6. ✅ Harap: data ter-filter sesuai bulan yang dipilih
7. Coba filter **Status** → pilih "Semua"
8. ✅ Harap: tampil semua data

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

## 6. Dark Mode

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

## 7. Month Picker

### Apa yang dicek
Filter bulan di dashboard dan histori pakai dropdown.

### Step-by-step:

1. Login admin → Dashboard
2. Lihat filter **Bulan** → ✅ Harap: dropdown select (bukan text input)
3. Pilih "Juli" → ✅ Harap: data ter-filter
4. Pilih "Semua" → ✅ Harap: tampil semua data
5. Buka halaman **Histori** → ✅ Harap: filter bulan juga dropdown

---

## 8. Mobile Responsiveness

### Apa yang dicek
Semua halaman responsif di mobile.

### Step-by-step:

1. Buka di HP (atau Chrome DevTools → toggle device toolbar)
2. **Form cuti:**
   - ✅ Harap: form 1 kolom, input cukup besar untuk di-tap (44px min)
   - ✅ Harap: tabel bisa di-scroll horizontal
3. **Navbar:**
   - ✅ Harap: hamburger menu (☰) muncul di mobile
   - Tap ☰ → ✅ Harap: menu dropdown muncul
4. **Dashboard:**
   - ✅ Harap: kartu statistik stack vertikal
   - ✅ Harap: filter form grid responsif
5. **Cek status:**
   - ✅ Harap: form dan hasil tampil rapi

---

## 9. Edge Cases

### Session expired:
1. Login admin
2. Tunggu > 30 menit (atau sesuai `SESSION_TIMEOUT_MINUTES`)
3. Klik halaman admin
4. ✅ Harap: redirect ke login

### Google Sheets down:
1. Matikan internet / block sheets.googleapis.com
2. Buka halaman apapun
3. ✅ Harap: error message user-friendly (bukan stack trace)

### Double submit:
1. Isi form cuti
2. Klik submit cepat 2x
3. ✅ Harap: hanya 1 pengajuan yang masuk (atau loading indicator mencegah double click)

---

## Checklist Cepat (Copy-Paste)

```
□ SECRET_KEY kosong → app gagal start
□ SECRET_KEY valid → app start normal
□ Submit form cuti → redirect ke cek-status → data tampil
□ NIP valid → "✓ NIP terdaftar"
□ NIP invalid → "✗ NIP tidak terdaftar"
□ Cek status manual → data pengajuan tampil
□ Tanggal lahir salah → flash error
□ Login admin → dashboard tampil
□ Filter bulan → dropdown select
□ Approve + no_surat → tercatat di Google Sheets
□ Reject + no_surat → tercatat di Google Sheets
□ Approve tanpa no_surat → error wajib isi
□ Dark mode toggle → berfungsi
□ Dark mode tersimpan setelah tutup browser
□ Mobile → navbar hamburger, form 1 kolom
□ Session expired → redirect ke login
```

---

*File ini berisi test yang hanya bisa dilakukan secara manual di browser.*
*Test via curl/terminal sudah dilakukan otomatis — hasilnya:*
- ✅ API validate NIP valid/invalid → OK
- ✅ CSRF token missing → 403 Forbidden
- ✅ Security headers (X-Content-Type-Options, X-Frame-Options, CSP) → OK
- ✅ Rate limit API (30/min) → 429 setelah 28 request
- ✅ Rate limit form (10/hr GET+POST) → 429 setelah 10 request
- ✅ XSS di NIP field → di-reject (non-numeric)
- ✅ NIP terlalu panjang (>20 digit) → di-reject
- ✅ 404 page → tampil
- ⚠️ GET `/` juga kena rate limit 10/hr (temuan audit belum difix)
