# Plan: Analisis Implementasi Keamanan Web Cuti Dishub

> **Untuk:** Bahan presentasi Yasin — menjelaskan bagaimana masing-masing kontrol keamanan diterapkan di kode, siap demo.

**Goal:** Menghasilkan dokumen lengkap yang menjelaskan implementasi keamanan per-kontrol berdasarkan kode aktual, sehingga Yasin bisa presentasi + demo ke dosen/penguji.

**Tech Stack:** Python Flask, bcrypt, flask-login, gspread, Google Sheets API

---

## Ringkasan Temuan dari Kode

Saya sudah membaca seluruh file kunci. Berikut mapping 14 kontrol keamanan ke lokasi kode:

### 1. Validasi SECRET_KEY saat startup
- **File:** `app.py:14-19`
- **Cara kerja:** Saat `create_app()` dipanggil, kode langsung cek apakah `SECRET_KEY` kosong atau masih `"change-me-in-production"`. Jika ya → `raise RuntimeError` → aplikasi **menolak berjalan**.
- **Config:** `config/settings.py:8` — `SECRET_KEY = os.environ.get("SECRET_KEY", "")`
- **Presentasi:** "Aplikasi tidak bisa jalan sama sekali kalau SECRET_KEY belum di-set. Ini mencegah deployment lupa konfigurasi."

### 2. Hashing kata sandi admin (bcrypt)
- **File:** `services/auth_service.py:9-11`
- **Cara kerja:** `verify_password()` mengambil hash dari env var `ADMIN_PASSWORD_HASH`, lalu `bcrypt.checkpw(password, stored_hash)`. Password asli **tidak pernah disimpan** — hanya hash bcrypt.
- **Config:** `config/settings.py:14` — `ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")`
- **Helper:** `generate_hash.py` — script terpisah untuk generate hash dari password.
- **Presentasi:** "Bcrypt itu one-way hash. Kalau database bocor, attacker cuma dapat hash, bukan password asli."

### 3. Login lockout (5x gagal → kunci 15 menit)
- **File:** `services/auth_service.py:23-58` + `services/sheets_service.py:320-367`
- **Cara kerja:**
  - `check_lockout(ip)` → cek sheet `AUTH_STATE` di Google Sheets
  - `record_failed_attempt(ip)` → increment counter per IP
  - Kalau `count >= 5` → kunci selama 15 menit
  - State **persist di Google Sheets** (bukan in-memory), jadi survive restart/redeploy Railway
- **Config:** `config/settings.py:30-31` — `MAX_LOGIN_ATTEMPTS = 5`, `LOGIN_LOCKOUT_MINUTES = 15`
- **Dipanggil di:** `routes/admin.py:56-85` (route `/admin/login`)
- **Presentasi:** "Lockout state disimpan di Google Sheets, bukan di memory server. Jadi kalau Railway redeploy, IP yang sudah dikunci tetap terkunci."

### 4. Session hardening (HttpOnly, SameSite, Secure, timeout 30 menit)
- **File:** `app.py:22-25`
- **Cara kerja:**
  - `SESSION_COOKIE_HTTPONLY = True` → cookie tidak bisa dibaca JavaScript (mitigasi XSS)
  - `SESSION_COOKIE_SAMESITE = "Lax"` → cookie tidak dikirim dari request cross-site (mitigasi CSRF)
  - `SESSION_COOKIE_SECURE = True` → cookie hanya dikirim via HTTPS
  - `permanent_session_lifetime = timedelta(minutes=30)` → session expired otomatis setelah 30 menit idle
- **Dev mode:** `app.py:96` — `SESSION_COOKIE_SECURE = False` saat development
- **Presentasi:** "Tiga atribut cookie ini adalah standar keamanan session. HttpOnly cegah pencurian via XSS, SameSite cegah CSRF, Secure cegah pengiriman di HTTP biasa."

### 5. Proteksi CSRF (token per sesi + hmac.compare_digest)
- **File:** `services/security.py:18-31`
- **Cara kerja:**
  - `generate_csrf_token()` → buat `secrets.token_hex(32)` simpan di session
  - `validate_csrf()` → bandingkan token dari form dengan token di session pakai `hmac.compare_digest()` (constant-time comparison, cegah timing attack)
  - Token hilang/salah → `abort(403)`
- **Dipasang di template:** Setiap form punya `<input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">`
  - `templates/login.html:17`
  - `templates/form_cuti.html:16`
  - `templates/base.html:65,141` (logout form)
- **Dipanggil di routes:**
  - `routes/admin.py:53` (login POST)
  - `routes/admin.py:93` (logout POST)
  - `routes/admin.py:195` (update status POST)
  - `routes/admin.py:362,396` (hari libur add/delete)
  - `routes/public.py:33` (form cuti POST)
  - `routes/public.py:211` (cek status POST)
- **Logout juga POST:** `routes/admin.py:90` — `@admin_bp.route("/logout", methods=["POST"])` — bukan GET, jadi tidak bisa dipicu lewat link biasa
- **Presentasi:** "CSRF token unik per sesi. Pakai hmac.compare_digest supaya perbandingannya constant-time — attacker tidak bisa menebak token dari waktu respons."

### 6. Content Security Policy (nonce dinamis, tanpa unsafe-inline)
- **File:** `services/security.py:133-148` + `app.py:35-39`
- **Cara kerja:**
  - Setiap request → `secrets.token_urlsafe(16)` disimpan di `g.csp_nonce`
  - CSP header: `script-src 'self' 'nonce-{nonce}'` — **tanpa `unsafe-inline`**
  - Nonce di-inject ke semua template via `context_processor` → tersedia sebagai `csp_nonce()`
  - Semua script di-load dari file eksternal (`src="..."`), bukan inline
- **Template:** Semua `<script>` tags di `base.html` dan `form_cuti.html` menggunakan `src` attribute (external files)
- **Presentasi:** "CSP nonce itu token sekali-pakai per request. Browser hanya mau jalankan script yang punya nonce yang sama dengan yang di header. Jadi kalau attacker berhasil inject script, browser tolak karena nonce-nya beda."

### 7. Security headers (nosniff, X-Frame-Options, Referrer-Policy)
- **File:** `services/security.py:133-149`
- **Cara kerja:** `add_security_headers()` dipasang sebagai `after_request` handler di `app.py:32`
  - `X-Content-Type-Options: nosniff` → browser tidak boleh "menebak" tipe konten
  - `X-Frame-Options: SAMEORIGIN` → halaman tidak bisa di-iframe dari domain lain (cegah clickjacking)
  - `Referrer-Policy: strict-origin-when-cross-origin` → referrer hanya dikirim ke origin yang sama
- **Presentasi:** "Header ini dipasang di SETIAP response, bukan cuma halaman tertentu. after_request Flask menjamin konsistensi."

### 8. Rate limiting per IP
- **File:** `services/security.py:36-113`
- **Cara kerja:**
  - Decorator `@rate_limit(max_requests, window_seconds, methods)` → in-memory dict per IP
  - Thread-safe pakai `threading.Lock()`
  - Cleanup otomatis setiap 100 request (`_cleanup_stale_keys()`)
  - Melebihi batas → `abort(429)`
- **Dipasang di:**
  - `routes/public.py:30` — form cuti: 10 POST per jam
  - `routes/public.py:159` — validasi NIP: 30 per menit
  - `routes/public.py:172` — hitung 90 hari: 30 per menit
  - `routes/public.py:186` — cek status: 20 per menit
- **Presentasi:** "Rate limiting mencegah spam dan brute force. Form cuti dibatasi 10 pengajuan per jam per IP. Kalau lebih, dapat HTTP 429."

### 9. Anti-spoofing X-Forwarded-For
- **File:** `services/security.py:120-126`
- **Cara kerja:** `get_real_ip()` hanya percaya header `X-Forwarded-For` kalau `request.remote_addr` ada di daftar `TRUSTED_PROXIES`. Kalau tidak → pakai `remote_addr` langsung.
- **Config:** `config/settings.py:9` — `TRUSTED_PROXIES` dari env var
- **Presentasi:** "Tanpa ini, attacker bisa set header X-Forwarded-For ke IP palsu dan bypass rate limiting. Kita hanya percaya proxy yang terdaftar."

### 10. Anti-enumerasi NIP
- **File:** `routes/public.py:158-168`
- **Cara kerja:** Endpoint `/api/karyawan/validate/<nip>` **selalu** return HTTP 200, baik NIP valid, tidak valid, maupun salah format. Perbedaan hanya di field `valid` di body JSON.
- **Presentasi:** "Kalau kita return 404 untuk NIP tidak terdaftar, attacker bisa brute force semua NIP untuk tahu siapa yang terdaftar. Dengan selalu 200, attacker tidak bisa membedakan."

### 11. Privasi cek status (NIP + tanggal lahir)
- **File:** `routes/public.py:210-248`
- **Cara kerja:** Cek status butuh **dua faktor**: NI PPPK PW + tanggal lahir. Tanggal lahir di-derive dari 8 digit pertama NIP, tapi tetap divalidasi. NIP saja tidak cukup.
- **Presentasi:** "NIP mengandung tanggal lahir di 8 digit pertama, jadi sebenarnya ini bukan faktor kedua yang kuat. Tapi tetap lebih baik daripada NIP saja — setidaknya attacker harus tahu formatnya."

### 12. ID unik per pengajuan (bukan nomor baris)
- **File:** `services/sheets_service.py:203-204` + `routes/admin.py:39,42-44`
- **Cara kerja:**
  - `generate_pengajuan_id()` → `secrets.token_urlsafe(9)` (12 karakter random)
  - Setiap operasi admin pakai ID, bukan row number
  - `_require_valid_id()` → regex `[A-Za-z0-9_-]{6,64}`, reject yang tidak cocok → `abort(404)`
  - Lookup by ID: `get_pengajuan_by_id()` scan kolom ID
- **Presentasi:** "Kalau pakai nomor baris, attacker bisa ganti angka di URL dan akses data orang lain. Dengan random ID, tidak ada pola yang bisa ditebak."

### 13. Manajemen kredensial (env var + .gitignore)
- **File:** `config/settings.py` (semua dari `os.environ.get()`) + `.gitignore`
- **Cara kerja:**
  - `SECRET_KEY`, `ADMIN_PASSWORD_HASH`, `GOOGLE_CREDENTIALS_JSON`, `SPREADSHEET_ID` → semua dari environment variable
  - `.gitignore` memblokir: `.env`, `*.json` (kecuali package.json), `credentials.json`, `instance/`
  - Tidak ada kredensial hardcode di source code
- **Presentasi:** "Semua rahasia di environment variable, bukan di kode. .gitignore mencegah file credentials ter-commit ke Git."

### 14. Input sanitasi
- **File:** `routes/public.py:35-44` (`.strip()`) + `routes/admin.py:198-212` (validasi status + no_surat format)
- **Cara kerja:**
  - Semua input di-`.strip()` sebelum diproses
  - Validasi field wajib (missing fields check)
  - Validasi format: NI PPPK PW harus digit, tanggal harus YYYY-MM-DD, no_surat alphanumeric + `/- .,`
  - Status hanya boleh "Disetujui", "Ditolak", "Dibatalkan" (whitelist)
  - Error message generik via `safe_error_message()` — tidak expose detail error ke user
- **Presentasi:** "Input divalidasi di server, bukan cuma di browser. Error message sengaja dibuat generik supaya attacker tidak tahu detail internal sistem."

---

## Task Plan (untuk eksekusi)

### Task 1: Buat file dokumentasi implementasi keamanan (.md)
**Objective:** Hasilkan file markdown yang berisi penjelasan per kontrol keamanan berdasarkan analisis kode di atas, siap pakai sebagai bahan presentasi.

**File yang dihasilkan:**
- `docs/IMPLEMENTASI_KEAMANAN.md` (di dalam project)

**Isi:**
- Pendahuluan: konsep defense in depth
- Per kontrol: nama, file + baris kode, cara kerja, kenapa penting, cara demo
- Diagram alur sederhana (opsional, dalam bentuk text)

### Task 2: Buat panduan tes manual (.md)
**Objective:** Hasilkan file panduan langkah-demi-langkah untuk mengetes setiap kontrol keamanan secara manual.

**File yang dihasilkan:**
- `docs/PANDUAN_TES_KEAMANAN.md` (di dalam project)

**Isi per kontrol:**
- Langkah-langkah tes (pakai browser DevTools, curl, atau UI langsung)
- Expected result (apa yang seharusnya terjadi)
- Screenshot indicator (apa yang harus dilihat)

---

## Risiko & Catatan

- **CSP nonce belum dipasang di semua `<script>` tag:** Script tags di `base.html:204` dan `form_cuti.html:116-118` tidak punya `nonce="{{ csp_nonce() }}"`. Karena semua script pakai `src` (external) dan CSP mengizinkan `'self'`, ini tidak masalah saat ini. Tapi kalau ada inline script ditambah tanpa nonce, CSP akan blokir.
- **Rate limiting in-memory:** State rate limiting hilang saat restart. Untuk Railway yang ephemeral, ini berarti rate limit reset setiap deploy. Lockout state sudah persist di Google Sheets, tapi rate limit belum.
- **Lockout via Google Sheets:** Ada latency karena harus baca/tulis Google Sheets setiap login attempt. Tapi ini trade-off yang disengaja untuk persistensi.

## File yang Akan Dibuat

| File | Isi |
|------|-----|
| `docs/IMPLEMENTASI_KEAMANAN.md` | Dokumentasi lengkap implementasi keamanan per kontrol |
| `docs/PANDUAN_TES_KEAMANAN.md` | Panduan tes manual step-by-step |

## File yang Dibaca (referensi)

| File | Peran |
|------|-------|
| `app.py` | App factory, session config, CSP nonce injection |
| `services/security.py` | CSRF, rate limiting, security headers, IP handling |
| `services/auth_service.py` | Bcrypt verification, lockout logic |
| `services/sheets_service.py` | Google Sheets client, auth state persistence, ID generation |
| `config/settings.py` | Semua config dari env var |
| `routes/admin.py` | Admin routes (login, logout, CRUD) |
| `routes/public.py` | Public routes (form cuti, validasi, cek status) |
| `templates/base.html` | Layout, CSRF token di logout form |
| `templates/login.html` | CSRF token di login form |
| `templates/form_cuti.html` | CSRF token di form cuti |
| `.gitignore` | Credential protection |
| `models.py` | AdminUser model |