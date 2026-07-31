# Sisa Audit — Sistem Cuti Dishub

> **Total temuan:** 46 (5 sudah difix, 41 tersisa)
> **Tanggal audit:** 30 Juli 2026
> **Status 5 fix pertama:** ✅ SECRET_KEY, ✅ no_surat, ✅ XFF spoofing, ✅ cache mutation, ✅ cross-month date
>
> **Keterangan kolom:**
> - **Severity** = Seberapa parah bug-nya jika TIDAK difix
> - **Fix Risk** = Seberapa besar kemungkinan fix-nya memperkenalkan bug baru

---

## Sudah Difix (5)

| # | Severity | Fix Risk | Temuan | Status |
|---|----------|----------|--------|--------|
| 1 | CRITICAL | LOW | SECRET_KEY default `"change-me-in-production"` | ✅ Fix |
| 6 | HIGH | LOW | Debug mode in production | ✅ Fix |
| 7 | HIGH | MEDIUM | Credential JSON tracked in git | ✅ Fix |
| 8 | MEDIUM | LOW | X-XSS-Protection deprecated | ✅ Fix |
| 9 | MEDIUM | LOW | Admin username hardcoded | ✅ Fix |
| 10 | MEDIUM | LOW | KUOTA_TAHUNAN hardcoded | ✅ Fix |
| 11 | MEDIUM | MEDIUM | SHEET_CUTI tahun hardcoded | ✅ Fix |
| 12 | MEDIUM | LOW | Hardcoded template path | ✅ Fix |
| 13 | MEDIUM | LOW | Dead code NAMA_KARYAWAN | ✅ Fix |
| 14 | MEDIUM | LOW | Race condition append_row return | ✅ Fix |
| 15 | MEDIUM | LOW | Dead code pending_nip | ✅ Fix |
| 16 | MEDIUM | LOW | Flash auto-dismiss | ✅ Fix |
| 17 | LOW | LOW | Duplicate .claude/ | ✅ Fix |
| 2 | HIGH | LOW | update_row_status ignore no_surat | ✅ Fix |
| 3 | HIGH | LOW | X-Forwarded-For spoofable | ✅ Fix |
| 4 | HIGH | LOW | get_karyawan_by_nip mutate cache | ✅ Fix |
| 5 | MEDIUM | LOW | Cross-month date display salah | ✅ Fix |

---

## Belum Difix — SECURITY (7)

### SEC-1 [Severity: HIGH] [Fix Risk: LOW] Debug mode in production
- **File:** `app.py:91` — `app.run(debug=True)`
- **Masalah:** Debug mode expose Werkzeug debugger dengan code execution. Kalau `python app.py` dipakai di production, attacker bisa execute arbitrary code.
- **Fix:** Tambah guard `if os.environ.get("FLASK_ENV") == "production": app.run(debug=False)` atau hapus `debug=True` dan pakai env var.
- **Dampak:** Remote code execution
- **Kenapa fix risk LOW:** Hanya ubah 1 baris, tidak affect logic lain.

### SEC-2 [Severity: HIGH] [Fix Risk: HIGH] CSP allows 'unsafe-inline' scripts
- **File:** `services/security.py:94-101`
- **Masalah:** `script-src 'self' 'unsafe-inline'` membuat CSP tidak efektif untuk XSS prevention. Script inline tetap jalan.
- **Fix:** Generate nonce per-request, pakai `script-src 'self' 'nonce-{nonce}'`. Pindah semua inline JS ke file terpisah.
- **Dampak:** XSS bisa execute script
- **Kenapa fix risk HIGH:** Mengubah CSP bisa break semua inline JS di template (onclick, script tags). Perlu refactor banyak template + pindah JS ke file terpisah. Salah sedikit = halaman blank.

### SEC-3 [Severity: HIGH] [Fix Risk: MEDIUM] Credential JSON tracked in git
- **File:** `sistem-cuti-dishub-a0943db153bf.json` (Google service account)
- **Masalah:** File credentials JSON ada di repo. `.gitignore` punya `*.json` tapi dengan exception `!package.json` / `!package-lock.json`. File credentials harusnya juga di-ignore.
- **Fix:** `git rm --cached sistem-cuti-dishub-a0943db153bf.json`, tambah nama file ke `.gitignore`, rotate credentials di Google Cloud Console.
- **Dampak:** Google Sheets API credentials bocor
- **Kenapa fix risk MEDIUM:** `git rm --cached` aman, tapi rotate credentials butuh Google Cloud Console access. Kalau credentials baru tidak di-setup dengan benar, semua Sheets API calls gagal.

### SEC-4 [Severity: MEDIUM] [Fix Risk: LOW] X-XSS-Protection deprecated
- **File:** `services/security.py:91`
- **Masalah:** Header `X-XSS-Protection: 1; mode=block` deprecated dan bisa introduce vulnerability di beberapa browser.
- **Fix:** Hapus header ini, rely pada CSP saja.
- **Dampak:** False sense of security
- **Kenapa fix risk LOW:** Hapus 1 baris header. Tidak affect logic.

### SEC-5 [Severity: MEDIUM] [Fix Risk: MEDIUM] GET form juga kena rate limit
- **File:** `routes/public.py:16` — `@rate_limit(max_requests=10, window_seconds=3600)` di route `/`
- **Masalah:** User yang buka halaman form (GET) juga dihitung. 10x refresh = blocked 1 jam.
- **Fix:** Pindah `@rate_limit` ke dalam function, hanya apply saat `request.method == "POST"`.
- **Dampak:** Legitimate user ter-block
- **Kenapa fix risk MEDIUM:** Memindahkan decorator ke dalam function butuh perubahan struktur route. Kalau salah posisi, POST bisa tidak ter-rate-limit sama sekali.

### SEC-6 [Severity: MEDIUM] [Fix Risk: MEDIUM] Rate limit memory leak
- **File:** `services/security.py:37` — `_rate_limits` dict
- **Masalah:** Dict tidak pernah prune entry untuk IP yang berhenti visit. Memory grows unbounded.
- **Fix:** Tambah cleanup: hapus entry yang semua timestamp-nya sudah expired. Atau pakai TTL-based store.
- **Dampak:** Memory leak di long-running process
- **Kenapa fix risk MEDIUM:** Cleanup logic harus thread-safe. Kalau prune terlalu agresif, valid rate limit entries hilang → rate limit tidak efektif.

### SEC-7 [Severity: MEDIUM] [Fix Risk: MEDIUM] Logout via GET (CSRF logout)
- **File:** `routes/admin.py:77`
- **Masalah:** `/admin/logout` pakai GET. Attacker bisa force logout admin via `<img src="/admin/logout">`.
- **Fix:** Ubah ke POST + CSRF token. Tambah confirmation form di template.
- **Dampak:** Admin bisa di-logout tanpa consent
- **Kenapa fix risk MEDIUM:** Butuh ubah route ke POST + ubah template (tambah form). Link logout di navbar/base.html juga harus diubah jadi button form. Kalau salah, logout tidak jalan.

---

## Belum Difix — BUGS (5)

### BUG-1 [Severity: HIGH] [Fix Risk: MEDIUM] append_row hardcoded row 1
- **File:** `services/sheets_service.py:147-149`
- **Masalah:** `append_row` selalu baca `headers = sheet.row_values(1)`. Untuk SHEET_KARYAWAN (title row 1, headers row 2), ini salah.
- **Fix:** Tambah parameter `head_row=1` ke `append_row`. Atau deteksi otomatis berdasarkan sheet name.
- **Dampak:** Data corruption kalau dipakai untuk SHEET_KARYAWAN
- **Kenapa fix risk MEDIUM:** Mengubah `append_row` signature bisa break caller yang ada. Perlu pastikan semua pemanggil tetap kompatibel.

### BUG-2 [Severity: HIGH] [Fix Risk: HIGH] Row-based detail access fragile
- **File:** `routes/admin.py:113-125`
- **Masalah:** `detail(row_num)` akses sheet berdasarkan nomor baris. Kalau ada baris yang di-insert/hapus manual di Google Sheets, row number shift → admin edit record salah.
- **Fix:** Generate unique ID per pengajuan (misal: timestamp + NIP), cari berdasarkan ID bukan row number.
- **Dampak:** Admin bisa edit record yang salah
- **Kenapa fix risk HIGH:** Ini refactor besar — butuh: (1) tambah kolom ID di sheet, (2) generate ID saat submit, (3) ubah semua route yang pakai row_num, (4) migrasi data existing. Satu langkah salah = admin panel tidak jalan.

### BUG-3 [Severity: MEDIUM] [Fix Risk: LOW] Race condition di append_row return
- **File:** `services/sheets_service.py:151`
- **Masalah:** `return len(sheet.get_all_values())` baca setelah append. Concurrent request bisa append di antara write dan read → return row number salah.
- **Fix:** Return `None` atau gunakan `append_row` return value dari gspread (sudah ada di versi baru).
- **Dampak:** Minor (return value tidak dipakai caller saat ini)
- **Kenapa fix risk LOW:** Return value tidak dipakai siapapun. Mengubah return ke None tidak affect apapun.

### BUG-4 [Severity: MEDIUM] [Fix Risk: HIGH] Login lockout tidak shared across workers
- **File:** `services/auth_service.py:7` — `_login_attempts` dict
- **Masalah:** Lockout state per-process. Dengan gunicorn multi-worker, attacker bisa brute-force 5x per worker.
- **Fix:** Pakai shared store (Redis, atau file-based). Atau single-worker deployment.
- **Dampak:** Brute-force bypass
- **Kenapa fix risk HIGH:** Butuh setup Redis/file-based store baru. Bisa require dependency baru. Kalau shared store down, login bisa tidak jalan. Deployment complexity naik.

### BUG-5 [Severity: MEDIUM] [Fix Risk: LOW] Dead code — duplicate pending_nip handling
- **File:** `routes/public.py:191-206`
- **Masalah:** Block kedua `pending_nip` check tidak pernah tercapai karena line 135 sudah pop session.
- **Fix:** Hapus block dead code di line 191-206.
- **Dampak:** Dead code, confusing
- **Kenapa fix risk LOW:** Hapus kode yang tidak pernah dieksekusi. Tidak ada behavior change.

---

## Belum Difix — UX/UI (6)

### UX-1 [Severity: MEDIUM] [Fix Risk: LOW] Flash auto-dismiss tidak work
- **File:** `static/js/main.js:1-10`
- **Masalah:** JS query `.alert` tapi template pakai class berbeda (langsung div dengan bg-color class). Flash messages tidak auto-dismiss.
- **Fix:** Tambah class `alert` ke flash message divs di `base.html`, atau ganti selector di JS.
- **Dampak:** Flash persist sampai navigasi
- **Kenapa fix risk LOW:** Hanya ubah selector di JS atau tambah class di HTML. Tidak affect logic.

### UX-2 [Severity: MEDIUM] [Fix Risk: MEDIUM] No loading state di form submit
- **File:** Semua form template
- **Masalah:** Tidak ada loading indicator saat submit. User bisa double-click → double submit.
- **Fix:** Tambah spinner/disable button on submit via JS.
- **Dampak:** Duplicate submissions
- **Kenapa fix risk MEDIUM:** JS submit handler harus compatible dengan CSRF validation. Kalau button disabled sebelum form submit, request bisa tidak terkirim. Perlu test di semua form (cuti, login, cek-status, approve/reject).

### UX-3 [Severity: LOW] [Fix Risk: LOW] autocomplete="off" di NIP field
- **File:** `templates/form_cuti.html:21`
- **Masalah:** Mencegah browser autofill untuk returning users.
- **Fix:** Ganti dengan `autocomplete="off"` → `autocomplete="username"` atau hapus.
- **Dampak:** Minor inconvenience
- **Kenapa fix risk LOW:** Ganti 1 attribute. Tidak affect logic.

### UX-4 [Severity: LOW] [Fix Risk: LOW] Default status option confusing
- **File:** `templates/admin/dashboard.html:38`
- **Masalah:** `<option value="">Menunggu ACC</option>` — value kosong tapi label "Menunggu ACC".
- **Fix:** Set value yang eksplisit: `<option value="Menunggu ACC">Menunggu ACC</option>`.
- **Dampak:** Minor inconsistency
- **Kenapa fix risk LOW:** Ubah 1 attribute value. Perlu cek backend filter logic masih cocok.

### UX-5 [Severity: LOW] [Fix Risk: LOW] No SEO meta tags
- **File:** `templates/base.html`
- **Masalah:** Tidak ada `<meta name="description">`.
- **Fix:** Tambah meta tag. (Internal tool, rendah prioritas)
- **Dampak:** Minor
- **Kenapa fix risk LOW:** Tambah tag HTML. Tidak affect logic.

### UX-6 [Severity: LOW] [Fix Risk: LOW] Inline onclick di mobile menu
- **File:** `templates/base.html:86`
- **Masalah:** Pakai `onclick` attribute instead of event listener.
- **Fix:** Pindah ke `main.js` dengan `addEventListener`.
- **Dampak:** Minor code quality
- **Kenapa fix risk LOW:** Pindah event handler. Perlu pastikan selector benar.

---

## Belum Difix — PERFORMANCE (5)

### PERF-1 [Severity: HIGH] [Fix Risk: MEDIUM] N+1 queries di histori
- **File:** `routes/admin.py:217-225`
- **Masalah:** Untuk setiap NIP unik, call `hitung_kuota_terpakai()` yang masing-masing baca semua records. 100 NIP = 100 reads.
- **Fix:** Hitung kuota sekali untuk semua NIP dalam satu pass. Atau cache kuota per NIP.
- **Dampak:** Slow page load
- **Kenapa fix risk MEDIUM:** Mengubah query pattern. Kalau logic per-NIP salah, kuota tampil salah di dashboard. Perlu test dengan data real.

### PERF-2 [Severity: MEDIUM] [Fix Risk: LOW] DATA_TTL 10 detik terlalu pendek
- **File:** `services/sheets_service.py:55`
- **Masalah:** Cache expire tiap 10 detik. Setiap page load setelah 10s trigger full API read.
- **Fix:** Naikkan ke 60 detik. Tambah manual refresh button di admin.
- **Dampak:** High API usage
- **Kenapa fix risk LOW:** Ganti 1 angka. Tidak affect logic. Admin bisa manual refresh kalau data stale.

### PERF-3 [Severity: MEDIUM] [Fix Risk: MEDIUM] detail() 2x API calls
- **File:** `routes/admin.py:116-119`
- **Masalah:** Fetch row data dan headers terpisah. Bisa di-satukan.
- **Fix:** Pakai `get_all_records()` + filter by row_num, atau single batch call.
- **Dampak:** Redundant API calls
- **Kenapa fix risk MEDIUM:** Mengubah data fetching pattern. Kalau row_num mapping salah, detail page tampil data yang salah.

### PERF-4 [Severity: MEDIUM] [Fix Risk: LOW] generate_surat_route duplicate calls
- **File:** `routes/admin.py:136-139`
- **Masalah:** Sama seperti detail(). Duplicate code dan API calls.
- **Fix:** Refactor ke shared function dengan PERF-3.
- **Dampak:** Redundant API calls
- **Kenapa fix risk LOW:** Refactor code duplication. Kalau shared function benar, behavior sama.

### PERF-5 [Severity: LOW] [Fix Risk: LOW] hitung_kuota_terpakai linear scan
- **File:** `services/kuota_service.py:7`
- **Masalah:** Scan semua CUTI records per NIP. O(n*m) tanpa cache.
- **Fix:** Build index (dict NIP → count) sekali, reuse. (Sudah di-cache, low priority)
- **Dampak:** Negligible dengan cache
- **Kenapa fix risk LOW:** Sudah di-cache. Perubahan hanya optimization, tidak affect behavior.

---

## Belum Difix — CODE QUALITY (8)

### CODE-1 [Severity: MEDIUM] [Fix Risk: LOW] Hardcoded template path
- **File:** `services/surat_service.py:6-9`
- **Masalah:** `TEMPLATE_PATH` hardcoded. Crash kalau file tidak ada.
- **Fix:** Tambah existence check, atau bikin configurable.
- **Dampak:** Runtime error
- **Kenapa fix risk LOW:** Tambah try/except atau os.path.exists check. Tidak affect logic utama.

### CODE-2 [Severity: MEDIUM] [Fix Risk: LOW] Dead code — NAMA_KARYAWAN_BAGIAN2
- **File:** `services/surat_service.py:31`
- **Masalah:** `"WAHYU EKO SAPUTRO"` defined but never used.
- **Fix:** Hapus.
- **Dampak:** Dead code
- **Kenapa fix risk LOW:** Hapus variabel yang tidak dipakai. Tidak affect apapun.

### CODE-3 [Severity: MEDIUM] [Fix Risk: LOW] KUOTA_TAHUNAN hardcoded
- **File:** `config/settings.py:18`
- **Masalah:** `KUOTA_TAHUNAN = 12` hardcoded, bukan dari env var.
- **Fix:** `KUOTA_TAHUNAN = int(os.getenv("KUOTA_TAHUNAN", "12"))`
- **Dampak:** Butuh code change untuk ubah kuota
- **Kenapa fix risk LOW:** Default tetap 12. Tidak ada behavior change kalau env var tidak diset.

### CODE-4 [Severity: MEDIUM] [Fix Risk: MEDIUM] SHEET_CUTI tahun hardcoded
- **File:** `config/settings.py:33`
- **Masalah:** `SHEET_CUTI = "CUTI 2026"` — butuh update manual tiap tahun.
- **Fix:** `SHEET_CUTI = os.getenv("SHEET_CUTI", f"CUTI {datetime.now().year}")`
- **Dampak:** Breaks on year change
- **Kenapa fix risk MEDIUM:** Kalau nama sheet tidak persis `CUTI {tahun}` (misal ada spasi beda), auto-detect gagal. Perlu fallback manual.

### CODE-5 [Severity: MEDIUM] [Fix Risk: LOW] Admin username hardcoded di route
- **File:** `routes/admin.py:54`
- **Masalah:** `username == "admin_kepegawaian"` hardcoded, tidak pakai `ADMIN_USERNAME` dari config.
- **Fix:** Ganti dengan `username == ADMIN_USERNAME` (sudah di-import).
- **Dampak:** Config ADMIN_USERNAME di .env tidak dipakai
- **Kenapa fix risk LOW:** Ganti string literal dengan variable yang sudah ada. Behavior sama.

### CODE-6 [Severity: LOW] [Fix Risk: LOW] Duplicate bulan_nama array
- **File:** `routes/public.py:73-76` dan `services/surat_service.py:79-82`
- **Masalah:** Array nama bulan duplikat di 2 file.
- **Fix:** Pindah ke `config/constants.py`, import di kedua file.
- **Dampak:** Maintenance burden
- **Kenapa fix risk LOW:** Pindah constant ke shared file. Tidak affect behavior.

### CODE-7 [Severity: LOW] [Fix Risk: LOW] Dead code block
- **File:** `routes/public.py:191-206`
- **Masalah:** Duplicate pending_nip check yang tidak pernah tercapai.
- **Fix:** Hapus.
- **Dampak:** Dead code
- **Kenapa fix risk LOW:** Hapus kode yang tidak pernah dieksekusi.

### CODE-8 [Severity: LOW] [Fix Risk: LOW] Duplicate .claude/ di .gitignore
- **File:** `.gitignore:24`
- **Masalah:** `.claude/` muncul 2x.
- **Fix:** Hapus duplikat.
- **Dampak:** No functional impact
- **Kenapa fix risk LOW:** Hapus baris duplikat di config file.

---

## Belum Difix — COMPATIBILITY (5)

### COMP-1 [Severity: MEDIUM] [Fix Risk: MEDIUM] Requirements tidak pin minor versions
- **File:** `requirements.txt`
- **Masalah:** `google-auth==2.30.0` mungkin conflict dengan `gspread==6.1.2`.
- **Fix:** Pin semua dependency dengan exact version yang tested.
- **Dampak:** Potential conflict di fresh install
- **Kenapa fix risk MEDIUM:** Pin versions yang belum tested bersama bisa introduce dependency conflict baru. Perlu test fresh install.

### COMP-2 [Severity: LOW] [Fix Risk: LOW] oklch() tidak support browser lama
- **File:** `static/css/style.css`
- **Masalah:** `oklch()` tidak supported di browser pre-2023.
- **Fix:** Tambah fallback: `background-color: #f5f6f9; background-color: oklch(...)`.
- **Dampak:** Colors break di browser lama
- **Kenapa fix risk LOW:** CSS fallback pattern universal. Tidak affect modern browser.

### COMP-3 [Severity: LOW] [Fix Risk: LOW] overflow-x: clip limited support
- **File:** `static/css/style.css:9`
- **Masalah:** `overflow-x: clip` lebih baru dari `overflow-x: hidden`.
- **Fix:** Ganti dengan `overflow-x: hidden` (universal support).
- **Dampak:** Minor layout issue
- **Kenapa fix risk LOW:** Ganti 1 CSS property. Behavior hampir identik.

### COMP-4 [Severity: LOW] [Fix Risk: LOW] DaisyUI version coupling
- **File:** `tailwind.config.js`
- **Masalah:** DaisyUI v4+ butuh Tailwind CSS v3+.
- **Fix:** Pin versions di package.json.
- **Dampak:** Upgrade path bumpy
- **Kenapa fix risk LOW:** Pin versions yang sudah jalan. Tidak affect runtime.

### COMP-5 [Severity: LOW] [Fix Risk: LOW] JS async/await tanpa transpilation
- **File:** `static/js/main.js`
- **Masalah:** Tidak work di IE11.
- **Fix:** (Tidak perlu jika target modern browser saja)
- **Dampak:** None jika IE11 tidak required
- **Kenapa fix risk LOW:** Tidak perlu fix. Target audience pakai modern browser.

---

## Prioritas Fix (diurutkan Severity × Fix Risk)

| Prioritas | ID | Severity | Fix Risk | Temuan |
|-----------|-----|----------|----------|--------|
| ⭐ 1 | SEC-1 | HIGH | LOW | Debug mode in production |
| ⭐ 2 | CODE-5 | MEDIUM | LOW | Admin username hardcoded |
| ⭐ 3 | SEC-4 | MEDIUM | LOW | X-XSS-Protection deprecated |
| ⭐ 4 | PERF-2 | MEDIUM | LOW | DATA_TTL terlalu pendek |
| ⭐ 5 | BUG-5 | MEDIUM | LOW | Dead code pending_nip |
| ⭐ 6 | BUG-3 | MEDIUM | LOW | Race condition append_row return |
| 7 | CODE-1 | MEDIUM | LOW | Hardcoded template path |
| 8 | CODE-2 | MEDIUM | LOW | Dead code NAMA_KARYAWAN |
| 9 | CODE-3 | MEDIUM | LOW | KUOTA_TAHUNAN hardcoded |
| 10 | UX-1 | MEDIUM | LOW | Flash auto-dismiss |
| 11 | SEC-3 | HIGH | MEDIUM | Credential JSON in git |
| 12 | SEC-5 | MEDIUM | MEDIUM | GET form rate limited | | ✅ Fix | 13 | SEC-6 | MEDIUM | MEDIUM | Rate limit memory leak | | ✅ Fix | 14 | SEC-7 | MEDIUM | MEDIUM | Logout via GET | | ✅ Fix | 15 | BUG-1 | HIGH | MEDIUM | append_row hardcoded row 1 | | ✅ Fix | 16 | PERF-1 | HIGH | MEDIUM | N+1 queries histori | | ✅ Fix | 17 | PERF-3 | MEDIUM | MEDIUM | detail() 2x API calls | | ✅ Fix | 18 | CODE-4 | MEDIUM | MEDIUM | SHEET_CUTI tahun hardcoded | | ✅ Fix | 19 | UX-2 | MEDIUM | MEDIUM | No loading state | | ✅ Fix | 20 | COMP-1 | MEDIUM | MEDIUM | Requirements pinning | | ✅ Fix | 21 | SEC-2 | HIGH | HIGH | CSP unsafe-inline |
| 22 | BUG-2 | HIGH | HIGH | Row-based detail fragile |
| 23 | BUG-4 | MEDIUM | HIGH | Login lockout not shared |
| — | Sisanya (LOW severity) | LOW | LOW | 14 temuan minor |

**Strategi:** Fix yang **Severity HIGH + Fix Risk LOW** duluan (aman & impactful). Hindari yang **Fix Risk HIGH** sampai ada test suite.

---

*File ini dipakai sebagai tracking untuk fix bertahap. Update status setelah setiap batch selesai.*
