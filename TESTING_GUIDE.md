# Panduan Testing Manual — Sistem Cuti Dishub

> **Untuk:** Yasin (developer/admin) & Teman Penguji  
> **Terakhir update:** 8 Agustus 2026  
> **Server:** http://127.0.0.1:5000 (pastikan `python app.py` sudah jalan)  
> **Panduan Uji Coba Bersama Teman:** Lihat [PANDUAN_TESTING_TEMAN.md](file:///c:/Users/yasin/KKL/Project/sistem-cuti-dishub/PANDUAN_TESTING_TEMAN.md) untuk cara akses via Wi-Fi lokal / online.

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
12. [URL Admin Berbasis ID (Batch 5)](#12-url-admin-id)
13. [CSP Tanpa unsafe-inline (Batch 5)](#13-csp)
14. [Shared Login Lockout (Batch 5)](#14-lockout)
15. [Edge Cases](#15-edge-cases)

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
Form submit berhasil → auto-redirect ke cek-status → data langsung tampil. Loading state muncul saat submit. Setiap pengajuan mendapat ID unik di sheet.

### Step-by-step

1. Buka http://127.0.0.1:5000/
2. Isi form:
   - **NIP:** NIP yang terdaftar di sheet `DATA_KARYAWAN` (kolom `NI PPPK PW`). Contoh saat ini: `198107052025` (A. ADAM) — cek sheet bila berganti
   - Klik di luar field → ✅ Harap: muncul "✓ NIP terdaftar" hijau
   - **Nama Lengkap:** isi manual
   - **Tanggal Lahir:** sesuai 8 digit pertama NIP (format `YYYY-MM-DD`, dari NIP otomatis)
   - **Jabatan:** isi manual
   - **Bidang/Seksi:** isi manual (text bebas)
   - **Shif:** opsional
   - **Tanggal Mulai & Selesai:** pilih tanggal
   - **Keperluan:** pilih dari dropdown
   - **Kabid/Kasi:** isi nama atasan
3. Klik **Kirim Pengajuan**
4. ✅ Harap: tombol berubah jadi "Memproses..." dan disabled (loading state)
5. ✅ Harap: redirect ke halaman `/cek-status` dengan data pengajuan langsung tampil
6. ✅ Harap: flash hijau "Pengajuan berhasil dikirim!"
7. Buka Google Sheets → sheet `CUTI <tahun>` → baris baru
8. ✅ Harap: kolom **ID** terisi token acak (contoh: `nbvFs8ur_avr`)

### Edge case — NIP tidak valid:
1. Isi NIP: `000000000000`
2. ✅ Harap: muncul "✗ NIP tidak terdaftar" merah

### Edge case — Tanggal selesai < mulai:
1. Tanggal mulai: 15 Agustus, selesai: 10 Agustus
2. Klik submit → ✅ Harap: alert browser "Tanggal selesai tidak boleh sebelum tanggal mulai" (validasi JS)
3. Jika lolos (mis. JS mati) → ✅ Harap: flash error dengan pesan yang sama

### Edge case — Format tanggal cuti (fix Batch 5):
1. **Cuti 1 hari** (mulai = selesai) → ✅ Harap: HARI di sheet tampil `10 Agustus 2026` (bukan "10 s.d. 10 Agustus 2026")
2. **Cuti beberapa hari, satu bulan** → ✅ Harap: `10 s.d. 12 Agustus 2026`
3. **Cuti lintas bulan** → ✅ Harap: `28 Agustus 2026 s.d. 2 September 2026`

---

## 3. Cek Status — Auto & Manual

### Apa yang dicek
Cek status manual (isi NIP + TGL_LAHIR sendiri) dan auto (redirect dari form).

### Step-by-step — Manual:

1. Buka http://127.0.0.1:5000/cek-status
2. Isi:
   - **NIP:** NIP terdaftar (sama seperti di seksi 2)
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
Login admin, dashboard statistik, filter bulan/seksi/status, link detail berbasis ID.

### Step-by-step:

1. Buka http://127.0.0.1:5000/admin/login
2. Isi:
   - **Username:** `admin_kepegawaian`
   - **Password:** (sesuai `ADMIN_PASSWORD_HASH` di `.env`; jika lupa, reset via `python generate_hash.py`)
3. Klik **Login**
4. ✅ Harap: tombol "Memproses..." saat loading
5. ✅ Harap: redirect ke dashboard dengan 4 kartu statistik (Menunggu, Disetujui, Ditolak, Total)
6. Coba filter **Bulan** → pilih dari dropdown (bukan text input)
7. ✅ Harap: data ter-filter sesuai bulan yang dipilih
8. Coba filter **Status** → pilih "Semua"
9. ✅ Harap: tampil semua data
10. Lihat kolom aksi tiap baris → ✅ Harap: tombol **Detail** dan **Surat**, linknya berbentuk `/admin/detail/<token>` (Batch 5)

### Edge case — Login salah:
1. Isi password salah
2. ✅ Harap: flash error "Username atau password salah"
3. Setelah 5x gagal → lockout 15 menit (detail di [seksi 14](#14-lockout))

---

## 5. Approve/Reject + No Surat

### Apa yang dicek
Approve & reject menulis STATUS dan NO SURAT ke baris yang benar di sheet (berbasis ID, bukan nomor baris).

### Step-by-step — Approve:

1. Login admin → Dashboard
2. Klik **Detail** pada pengajuan berstatus "Menunggu ACC"
3. Di halaman detail, isi **Nomor Surat:** `001/CUTI/VIII/2026`
4. Klik **Setujui** → muncul dialog konfirmasi "Setujui pengajuan ini?" → klik OK
5. ✅ Harap: flash sukses, status berubah "Disetujui"
6. Buka Google Sheets → sheet `CUTI <tahun>` → cari pengajuan tersebut (cocokkan NAMA/NIP)
7. ✅ Harap: kolom `STATUS` = "Disetujui" dan `NO SURAT` = `001/CUTI/VIII/2026`

### Step-by-step — Reject:

1. Buka detail pengajuan "Menunggu ACC"
2. Klik **Tolak** → dialog konfirmasi "Tolak pengajuan ini?" → OK
3. ✅ Harap: status berubah "Ditolak"
4. Buka Google Sheets → ✅ Harap: kolom `STATUS` = "Ditolak"

### Edge case — Approve tanpa nomor surat:
1. Klik Setujui tanpa mengisi Nomor Surat
2. ✅ Harap: browser menahan submit (field required); jika dipaksa → flash error "Nomor Surat wajib diisi untuk status Disetujui"

### Edge case — Baris digeser di sheet (inti fix BUG-2):
1. Di Google Sheets, sisipkan baris kosong di atas sebuah pengajuan "Menunggu ACC" (insert row above)
2. Di app, buka detail pengajuan itu → Setujui dengan nomor surat
3. ✅ Harap: STATUS & NO SURAT tertulis pada pengajuan yang BENAR (dicari via ID), bukan baris di atasnya

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
3. Pilih satu bulan → ✅ Harap: data ter-filter
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

## 12. URL Admin Berbasis ID (Batch 5)

### Apa yang dicek
Halaman admin memakai ID unik pengajuan, bukan nomor baris sheet. URL lama berbasis angka tidak berfungsi lagi.

### Step-by-step:

1. Login admin → buka Dashboard
2. ✅ Harap: link "Detail" berbentuk `/admin/detail/<token>` (bukan `/admin/detail/<angka>`)
3. Buka detail → setujui/tolak → ✅ status berubah pada pengajuan yang benar
4. Buka URL lama `/admin/detail/5` → ✅ Harap: 404
5. Buka `/admin/detail/sembarang-nilai-palsu` → ✅ Harap: 404
6. Bookmark satu URL detail → refresh → ✅ Harap: tetap membuka pengajuan yang sama meskipun sheet diedit

### Migrasi kolom ID (satu kali, sudah dijalankan 6 Agustus 2026):

1. Jalankan `python migrate_add_id.py`
2. ✅ Harap: header "ID" ada di sheet CUTI, semua baris lama yang berisi data punya ID
3. Jalankan lagi → ✅ Harap: "0 baris ditulis" (idempoten, aman diulang kapan pun)

---

## 13. CSP Tanpa unsafe-inline (Batch 5)

### Apa yang dicek
Content-Security-Policy tidak lagi mengizinkan skrip/style inline; semua JS dipindah ke file eksternal dengan nonce per-request.

### Step-by-step:

1. Buka DevTools → Console di semua halaman (form, cek status, login, dashboard, detail, histori)
2. ✅ Harap: tidak ada error "Content Security Policy"
3. Cek header: `curl -sI http://127.0.0.1:5000/ | grep -i content-security`
4. ✅ Harap: ada `script-src 'self' 'nonce-...'`, TIDAK ada `unsafe-inline`
5. Refresh dua kali → nonce harus berbeda tiap request
6. Fungsionalitas yang dulunya inline harus tetap jalan:
   - Validasi NIP (blur di field NIP) → "✓ NIP terdaftar"
   - Dark mode toggle
   - Dialog konfirmasi Setujui/Tolak
   - Form logout di navbar

---

## 14. Shared Login Lockout (Batch 5)

### Apa yang dicek
Lockout login tersimpan di file (`instance/auth_state.json`) — shared antar worker dan bertahan setelah restart.

### Step-by-step:

1. 5x login dengan password salah → ✅ Harap: flash "Akun terkunci. Coba lagi dalam ... detik."
2. Restart app (`Ctrl+C` lalu `python app.py`)
3. Coba login lagi → ✅ Harap: masih terkunci (bukti state tersimpan di file)
4. Login sukses setelah masa kunci habis → ✅ Harap: counter ter-reset
5. Buka folder `instance/` → ✅ Harap: ada `auth_state.json`, dan file ini tidak masuk git

### Darurat — buka kunci manual:
- Hapus file `instance/auth_state.json` → lockout semua IP langsung ter-reset

---

## 15. Edge Cases

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
□ Baris baru di sheet punya kolom ID terisi token
□ NIP valid → "✓ NIP terdaftar"
□ NIP invalid → "✗ NIP tidak terdaftar"
□ Cuti 1 hari → HARI tampil satu tanggal (bukan "X s.d. X")
□ Cek status manual → loading state → data pengajuan tampil
□ Tanggal lahir salah → flash error
□ Login admin → loading state → dashboard tampil
□ Filter bulan → dropdown select
□ Link Detail berbentuk /admin/detail/<token>; /admin/detail/5 → 404
□ Approve + nomor surat → STATUS & NO SURAT tercatat di baris yang benar
□ Sisipkan baris di sheet → approve tetap kena pengajuan yang benar (via ID)
□ Reject → status "Ditolak"
□ Approve tanpa nomor surat → error wajib isi
□ Dialog konfirmasi Setujui/Tolak muncul sebelum submit
□ Logout → POST + CSRF, GET → 405
□ Dark mode toggle → berfungsi, tersimpan setelah tutup browser
□ CSP header ada nonce, tanpa unsafe-inline; console bebas error CSP
□ 5x login salah → lockout; restart app → masih terkunci
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
| Security headers | ✅ X-Content-Type-Options, X-Frame-Options, CSP nonce tanpa unsafe-inline |
| Rate limit API (30/min) | ✅ 429 setelah 30 request |
| Rate limit form POST (10/hr) | ✅ 429 setelah 10 request |
| Rate limit GET `/` (tidak di-rate-limit) | ✅ 15 request tanpa 429 |
| XSS di NIP field | ✅ di-reject (non-numeric) |
| NIP terlalu panjang (>20 digit) | ✅ di-reject |
| 404 page | ✅ tampil |
| Logout GET → 405 | ✅ Method Not Allowed |
| Session cookie HttpOnly + SameSite=Lax | ✅ dikonfigurasi di app.py |
| End-to-end Batch 5 (6 Agu 2026) | ✅ submit→ID `nbvFs8ur_avr`→approve→NO SURAT tertulis→baris test dibersihkan |
| Lockout persisten (6 Agu 2026) | ✅ terkunci → restart app → masih terkunci |
| Migrasi ID (6 Agu 2026) | ✅ header ID di kolom O, re-run menulis 0 baris |

---

*File ini berisi test yang hanya bisa dilakukan secara manual di browser.*
*Test via curl/terminal dijalankan otomatis oleh AI agent.*
