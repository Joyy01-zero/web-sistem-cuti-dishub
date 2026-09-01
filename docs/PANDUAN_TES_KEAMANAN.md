# Panduan Tes Manual Keamanan — Web Cuti Dishub

**URL produksi:** `https://ajukan-cuti-dishub.up.railway.app/`
**Tools:** Browser (Chrome), DevTools (F12), Terminal (curl)

---

## Tes 1: Login Lockout (5x gagal → akun terkunci 15 menit)

Menguji apakah brute force login diblokir. Setelah 5 percobaan gagal, akun admin dikunci 15 menit — **tidak peduli dari IP/device mana** login dilakukan. Lockout berdasarkan USERNAME (bukan IP) karena di jaringan seluler Indonesia (CGNAT), IP berubah tiap request. State lockout disimpan di Google Sheets, jadi tetap terkunci meskipun server restart.

**Langkah:**
1. Buka `/admin/login`
2. Masukkan password salah **5 kali** berturut-turut
3. Coba login ke-6

**Expected:** Percobaan ke-5 → "Akun terkunci selama ... detik." Percobaan ke-6 → tetap terkunci.

**Bonus:** Tunggu 15 menit → login berhasil (lockout expired). Restart aplikasi → masih terkunci (state persist di Google Sheets).

**Catatan teknis:** Lockout per akun, bukan per IP. Ini karena CGNAT (100.64.0.x) menyebabkan IP berubah tiap request di jaringan seluler. Per-IP lockout tidak efektif di jaringan ini.

---

## Tes 2: Hashing bcrypt — Tidak ada password plaintext

Menguji apakah password admin benar-benar disimpan sebagai hash, bukan teks asli. Jika ditemukan password plaintext di kode, berarti ada kebocoran kredensial.

**Langkah:**
1. Buka terminal di folder project
2. Jalankan:
```bash
grep -ri "password" *.py services/*.py config/*.py | grep -v "HASH" | grep -v "hash" | grep -v "#" | grep -v "def "
```

**Expected:** Tidak ditemukan string password asli. Yang ada hanya `ADMIN_PASSWORD_HASH` (sudah berbentuk hash).

---

## Tes 3: Session Hardening (Cookie Attributes + Timeout)

Menguji apakah cookie session punya atribut keamanan yang benar. HttpOnly mencegah JS membaca cookie (cegah XSS). SameSite=Lax mencegah cookie dikirim dari situs lain (cegah CSRF). Secure mencegah cookie dikirim di HTTP biasa. Timeout 30 menit membatasi kerusakan jika cookie dicuri.

**Langkah:**
1. Login ke admin
2. Buka DevTools (F12) → Application → Cookies → cari `session`

**Expected:**
- `HttpOnly` tercentang
- `SameSite` = `Lax`
- `Secure` tercentang (di produksi HTTPS)

**Tes timeout:**
1. Login, lalu **jangan aktivitas selama 30 menit**
2. Refresh halaman

**Expected:** Redirect ke halaman login — session sudah expired.

---

## Tes 4: Proteksi CSRF

Menguji apakah form hanya bisa dikirim dari halaman asli aplikasi. Token CSRF wajib ada di setiap POST request. Tanpa token, server harus menolak dengan HTTP 403. Logout juga harus POST (bukan GET) supaya tidak bisa dipicu attacker lewat tautan.

**Langkah:**
```bash
curl -X POST https://ajukan-cuti-dishub.up.railway.app/admin/login \
  -d "username=admin&password=test" -v
```

**Expected:** HTTP 403 — "CSRF token tidak valid."

**Tes logout via GET:**
```
Buka: https://ajukan-cuti-dishub.up.railway.app/admin/logout
```
**Expected:** HTTP 405 Method Not Allowed (logout hanya POST).

---

## Tes 5: Content Security Policy (CSP)

Menguji apakah browser memblokir script yang tidak sah. CSP dengan nonce dinamis memastikan hanya script dari file eksternal yang boleh dijalankan. Script inline (yang biasa dipakai attacker untuk XSS) harus diblokir karena tidak punya nonce yang benar.

**Langkah:**
1. Buka DevTools (F12) → Network → klik request pertama → Headers
2. Cari `Content-Security-Policy`

**Expected:** Ada header, di dalamnya `script-src 'self' 'nonce-xxx'` — **tidak ada** `'unsafe-inline'`.

**Tes inline script diblokir:**
Buka Console, ketik:
```javascript
document.write('<script>alert("XSS")</script>')
```
**Expected:** Error CSP violation di console, alert tidak muncul.

---

## Tes 6: Security Headers

Menguji apakah header keamanan terpasang di setiap response. Header ini melindungi dari MIME sniffing, clickjacking, dan kebocoran URL. Karena dipasang via `after_request`, semua response harus punya header ini tanpa kecuali.

**Langkah:** DevTools → Network → request document → Headers

**Expected ketiga header ini ada:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Referrer-Policy: strict-origin-when-cross-origin`

---

## Tes 7: Rate Limiting

Menguji apakah jumlah request dibatasi per IP. Form cuti dibatasi 10 POST per jam. Ini mencegah spam pengajuan palsu dan brute force. Jika melebihi batas, server harus merespons HTTP 429 (Too Many Requests).

**Langkah:**
```bash
for i in $(seq 1 11); do
  echo -n "Request $i: "
  curl -s -o /dev/null -w "%{http_code}" \
    -X POST https://ajukan-cuti-dishub.up.railway.app/ \
    -d "_csrf_token=dummy&ni_pppk_pw=123&nama=test"
  echo ""
done
```

**Expected:** Request ke-11 → HTTP 429.

---

## Tes 8: Anti-Spoofing X-Forwarded-For

Menguji apakah header `X-Forwarded-For` dari non-proxy diabaikan. Tanpa validasi ini, attacker bisa mengirim header palsu untuk menyamar sebagai IP lain dan bypass rate limiting maupun lockout.

**Langkah:**
```bash
curl -v https://ajukan-cuti-dishub.up.railway.app/ \
  -H "X-Forwarded-For: 1.2.3.4"
```

**Expected:** Aplikasi menggunakan IP asli (remote_addr), bukan 1.2.3.4. Rate limiting tetap berdasarkan IP asli.

---

## Tes 9: Anti-Enumerasi NIP

Menguji apakah endpoint validasi NIP selalu mengembalikan HTTP 200, baik NIP terdaftar maupun tidak. Ini mencegah attacker memetakan massal NIP pegawai — kalau ada perbedaan status code, attacker bisa brute force untuk tahu siapa yang terdaftar.

**Langkah:**
```bash
curl -s -w "\nHTTP: %{http_code}" \
  "https://ajukan-cuti-dishub.up.railway.app/api/karyawan/validate/999999999"
```

**Expected:** HTTP 200 dengan `{"valid": false}` — bukan 404.

---

## Tes 10: Privasi Cek Status (NIP + Tanggal Lahir)

Menguji apakah cek status pengajuan membutuhkan dua faktor. NIP saja tidak cukup — harus disertai tanggal lahir yang benar. Ini menambah lapisan privasi meskipun NIP mengandung info tanggal lahir.

**Langkah:**
1. Buka `/cek-status`
2. Masukkan NIP yang valid + tanggal lahir yang **salah**
3. Submit

**Expected:** "Tanggal lahir tidak sesuai." — data pengajuan tidak muncul.

---

## Tes 11: ID Unik Per Pengajuan (Anti-IDOR)

Menguji apakah pengajuan menggunakan ID random, bukan nomor baris. Jika pakai nomor baris, attacker tinggal ganti angka di URL untuk akses data orang lain (IDOR). Dengan random ID, tidak ada pola yang bisa ditebak.

**Langkah:**
1. Login ke admin
2. Buka beberapa pengajuan di dashboard, catat ID di URL

**Expected:** ID berupa string random seperti `xK9mP2nQr` — tidak berurutan (1, 2, 3).

**Tes akses ID palsu:**
Buka `/admin/detail/random123`
**Expected:** "Data tidak ditemukan." atau 404.

---

## Tes 12: Input Sanitasi

Menguji apakah input yang tidak valid ditolak di server. Validasi harus terjadi di server, bukan hanya di browser (karena browser bisa di-bypass). Error message harus generik — tidak boleh expose info internal.

**NIP non-angka:**
```bash
curl -s "https://ajukan-cuti-dishub.up.railway.app/api/karyawan/validate/abc"
```
**Expected:** `{"valid": false}` — HTTP 200.

**Status tidak valid:**
Login admin → POST update status dengan `status=Hacked`
**Expected:** "Status tidak valid."

**Error message generik:**
Akses `/admin/halaman-tidak-ada`
**Expected:** "Halaman tidak ditemukan" — tanpa stack trace atau info teknis.

---

## Tes 13: Manajemen Kredensial

Menguji apakah kredensial tidak pernah ter-commit ke Git. Semua rahasia harus di environment variable, bukan di kode. `.gitignore` harus memblokir file `.env` dan credentials.

**Langkah:**
```bash
git log --all --diff-filter=A -- "*.env" "credentials.json" 2>/dev/null | head -20
```

**Expected:** Tidak ada file `.env` atau credentials yang pernah ter-commit.

**Tes .gitignore:**
1. Buat file `.env` di folder project
2. Jalankan `git status`

**Expected:** `.env` tidak muncul di untracked files.

---

## Tes 14: Validasi SECRET_KEY

Menguji apakah aplikasi menolak berjalan tanpa SECRET_KEY. SECRET_KEY dipakai Flask untuk menandatangani session cookie. Tanpa key yang aman, attacker bisa memalsukan session.

**Langkah:**
1. Hapus environment variable `SECRET_KEY`
2. Jalankan `python app.py`

**Expected:** Crash dengan `RuntimeError: SECRET_KEY belum dikonfigurasi!`

---

## Checklist Hasil

| No | Tes | Pass? |
|----|-----|-------|
| 1 | Login lockout 5x (per akun) | |
| 2 | Tidak ada password plaintext | |
| 3 | Cookie HttpOnly/SameSite/Secure + timeout | |
| 4 | CSRF token wajib | |
| 5 | CSP tanpa unsafe-inline | |
| 6 | Security headers lengkap | |
| 7 | Rate limiting aktif | |
| 8 | Anti-spoofing XFF | |
| 9 | Anti-enumerasi NIP | |
| 10 | Privasi cek status | |
| 11 | ID unik (anti-IDOR) | |
| 12 | Input sanitasi | |
| 13 | Kredensial aman di Git | |
| 14 | SECRET_KEY wajib ada | |
