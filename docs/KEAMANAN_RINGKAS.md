# Implementasi Keamanan — Web Cuti Dishub Kota Bogor

**Stack:** Flask + Google Sheets API | **Prinsip:** Defense in Depth (keamanan berlapis)

---

## 14 Kontrol Keamanan

### 1. Login lockout (`services/auth_service.py:23-58`)
5x login gagal → **akun** terkunci 15 menit (bukan per IP). State **persist di Google Sheets**, survive restart Railway.
Lockout berdasarkan USERNAME, bukan IP — karena di jaringan seluler Indonesia (CGNAT), IP berubah tiap request sehingga per-IP lockout tidak efektif. Dengan Google Sheets, akun yang sudah dikunci tetap terkunci meskipun server restart. Mencegah brute force password admin dari IP manapun.

### 2. Hashing bcrypt (`services/auth_service.py:9-11`)
Password admin disimpan sebagai hash satu arah via `bcrypt.checkpw()`. Tidak ada password plaintext di kode.
Bcrypt sengaja dibuat lambat (cost factor tinggi) sehingga brute force membutuhkan waktu sangat lama. Jika environment variable bocor, attacker hanya mendapat hash — password asli tidak bisa dipulihkan.

### 3. Session hardening (`app.py:22-25`)
- `HttpOnly` — cookie tidak bisa dibaca JS (cegah pencurian session via XSS)
- `SameSite=Lax` — cookie tidak dikirim dari request lintas situs (cegah CSRF)
- `Secure` — cookie hanya dikirim via HTTPS (cegah sadap di jaringan)
- Timeout 30 menit idle — session otomatis expired jika tidak aktif

Tiga atribut cookie ini adalah standar keamanan session. Tanpa salah satu saja, ada vektor serangan yang terbuka.

### 4. Proteksi CSRF (`services/security.py:18-31`)
Token acak 32 byte per sesi, divalidasi pakai `hmac.compare_digest()` (constant-time). Logout juga POST, bukan GET.
CSRF adalah serangan di mana attacker membuat halaman palsu yang otomatis mengirim form ke aplikasi kita saat user sudah login. Token CSRF memastikan form hanya bisa dikirim dari halaman asli aplikasi. `hmac.compare_digest()` dipakai supaya perbandingan token selalu memakan waktu sama — mencegah attacker menebak token karakter per karakter dari selisih waktu respons (timing attack).

### 5. CSP nonce dinamis (`services/security.py:141-148`)
Nonce baru setiap request. `script-src 'self' 'nonce-xxx'` — **tanpa `unsafe-inline`**. Inline script yang di-inject attacker otomatis diblokir browser.
CSP (Content Security Policy) adalah pertahanan terakhir melawan XSS. Jika attacker berhasil menyisipkan script ke halaman (misalnya lewat input yang lolos validasi), browser akan menolak menjalankan script tersebut karena tidak punya nonce yang benar. Nonce berbeda di setiap request, jadi tidak bisa diprediksi.

### 6. Security headers (`services/security.py:133-149`)
Dipasang di **setiap response** via `after_request`:
- `X-Content-Type-Options: nosniff` — browser tidak boleh menebak tipe konten, cegah MIME sniffing
- `X-Frame-Options: SAMEORIGIN` — halaman tidak bisa di-iframe dari domain lain, cegah clickjacking
- `Referrer-Policy: strict-origin-when-cross-origin` — URL referrer hanya dikirim ke origin yang sama, cegah kebocoran URL sensitif

Header ini dipasang di `after_request` Flask sehingga menjamin **setiap** response mendapat header, tanpa kecuali.

### 7. Rate limiting (`services/security.py:66-113`)
Decorator per-endpoint, in-memory, thread-safe. Form cuti: 10 POST/jam. Melebihi → HTTP 429.
Tanpa rate limiting, attacker bisa mengirim ribuan pengajuan cuti palsu per detik atau melakukan brute force terhadap endpoint publik. Pembatasan per IP memastikan satu orang tidak bisa mengganggu seluruh sistem.

### 8. Anti-spoofing XFF (`services/security.py:120-126`)
Header `X-Forwarded-For` hanya dipercaya dari proxy terdaftar (`TRUSTED_PROXIES`). Mencegah bypass rate limit.
Ketika aplikasi di balik reverse proxy (Railway), IP asli client ada di header `X-Forwarded-For`. Tapi header ini bisa dipalsukan. Tanpa validasi, attacker bisa mengirim header palsu untuk menyamar sebagai IP lain dan bypass rate limiting maupun lockout.

### 9. Anti-enumerasi NIP (`routes/public.py:158-168`)
Endpoint validasi **selalu HTTP 200** — NIP valid maupun tidak. Perbedaan hanya di body JSON. Mencegah pemetaan massal NIP.
Jika endpoint mengembalikan 404 untuk NIP tidak terdaftar dan 200 untuk yang terdaftar, attacker bisa mengirim ribuan request untuk memetakan siapa saja yang terdaftar. Dengan selalu 200, attacker tidak bisa membedakan dari status code.

### 10. Privasi cek status (`routes/public.py:210-248`)
Cek status butuh **NIP + tanggal lahir**. NIP saja tidak cukup.
Seseorang yang hanya mengetahui NIP pegawai tetap tidak bisa melihat data pengajuan cuti tanpa mengetahui tanggal lahir. Ini menambah lapisan privasi — meskipun NIP mengandung info tanggal lahir di 8 digit pertama, tetap harus divalidasi.

### 11. ID unik per pengajuan (`services/sheets_service.py:203-204`)
Pakai `secrets.token_urlsafe(9)`, bukan nomor baris. Mencegah akses data orang lain (IDOR).
Jika pakai nomor baris (1, 2, 3), attacker tinggal ganti angka di URL untuk akses data orang lain (Insecure Direct Object Reference). Dengan random ID 12 karakter, tidak ada pola yang bisa ditebak.

### 12. Input sanitasi (`routes/public.py` + `routes/admin.py`)
Semua input di-`strip()`, divalidasi formatnya, status pakai whitelist. Error message generik — tidak expose info internal.
Validasi di server (bukan hanya di browser) memastikan data yang masuk ke database bersih. Error message sengaja dibuat generik supaya attacker tidak tahu detail internal sistem seperti nama tabel, versi library, atau stack trace.

### 13. Manajemen kredensial (`config/settings.py` + `.gitignore`)
Semua rahasia dari environment variable. `.gitignore` blokir `.env`, `credentials.json`, `instance/`.
Environment variable memisahkan rahasia dari kode — kode bisa di-share tanpa risiko bocor kredensial. `.gitignore` memastikan file sensitif tidak pernah ter-commit ke repository Git.

### 14. Validasi SECRET_KEY (`app.py:14-19`)
Aplikasi **menolak berjalan** jika SECRET_KEY kosong/default. Mencegah deploy lupa konfigurasi.
SECRET_KEY dipakai Flask untuk menandatangani session cookie. Tanpa key yang aman, attacker bisa memalsukan session dan menyamar sebagai admin.

---

## Diagram Alur Request

```
Request Masuk
  → get_real_ip()         [8. Anti-spoofing XFF]
  → @rate_limit()         [7. Rate limiting]
  → @login_required       [3. Session hardening]
  → validate_csrf()       [4. CSRF token]
  → Input sanitasi        [12. Validasi format]
  → Business logic
  → Response + headers    [5. CSP, 6. Security headers]
```

---

## Contoh Tes Saat Demo

| No | Tes | Cara | Expected |
|----|-----|------|----------|
| 1 | Lockout | Login salah 5x | Akun terkunci 15 menit |
| 4 | CSRF | Kirim POST tanpa token (curl) | HTTP 403 |
| 5 | CSP | Console: `document.write('<script>alert(1)</script>')` | Diblokir browser |
| 7 | Rate limit | 11x POST form cuti | HTTP 429 |
| 9 | Anti-enumerasi | GET `/api/karyawan/validate/999` | HTTP 200, `valid: false` |
| 3 | Session timeout | Idle 30 menit | Redirect ke login |
