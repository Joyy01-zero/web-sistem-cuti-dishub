# Sisa Audit — Sistem Cuti Dishub

> **Total temuan:** 46 (5 sudah difix, 41 tersisa)
> **Tanggal audit:** 30 Juli 2026
> **Status 5 fix pertama:** ✅ SECRET_KEY, ✅ no_surat, ✅ XFF spoofing, ✅ cache mutation, ✅ cross-month date

---

## Sudah Difix (5)

| # | Severity | Temuan | Status |
|---|----------|--------|--------|
| 1 | CRITICAL | SECRET_KEY default `"change-me-in-production"` | ✅ Fix |
| 2 | HIGH | update_row_status ignore no_surat | ✅ Fix |
| 3 | HIGH | X-Forwarded-For spoofable | ✅ Fix |
| 4 | HIGH | get_karyawan_by_nip mutate cache | ✅ Fix |
| 5 | MEDIUM | Cross-month date display salah | ✅ Fix |

---

## Belum Difix — SECURITY (7)

### SEC-1 [HIGH] Debug mode in production
- **File:** `app.py:91` — `app.run(debug=True)`
- **Masalah:** Debug mode expose Werkzeug debugger dengan code execution. Kalau `python app.py` dipakai di production, attacker bisa execute arbitrary code.
- **Fix:** Tambah guard `if os.environ.get("FLASK_ENV") == "production": app.run(debug=False)` atau hapus `debug=True` dan pakai env var.
- **Dampak:** Remote code execution

### SEC-2 [HIGH] CSP allows 'unsafe-inline' scripts
- **File:** `services/security.py:94-101`
- **Masalah:** `script-src 'self' 'unsafe-inline'` membuat CSP tidak efektif untuk XSS prevention. Script inline tetap jalan.
- **Fix:** Generate nonce per-request, pakai `script-src 'self' 'nonce-{nonce}'`. Pindah semua inline JS ke file terpisah.
- **Dampak:** XSS bisa execute script

### SEC-3 [HIGH] Credential JSON tracked in git
- **File:** `sistem-cuti-dishub-a0943db153bf.json` (Google service account)
- **Masalah:** File credentials JSON ada di repo. `.gitignore` punya `*.json` tapi dengan exception `!package.json` / `!package-lock.json`. File credentials harusnya juga di-ignore.
- **Fix:** `git rm --cached sistem-cuti-dishub-a0943db153bf.json`, tambah nama file ke `.gitignore`, rotate credentials di Google Cloud Console.
- **Dampak:** Google Sheets API credentials bocor

### SEC-4 [MEDIUM] X-XSS-Protection deprecated
- **File:** `services/security.py:91`
- **Masalah:** Header `X-XSS-Protection: 1; mode=block` deprecated dan bisa introduce vulnerability di beberapa browser.
- **Fix:** Hapus header ini, rely pada CSP saja.
- **Dampak:** False sense of security

### SEC-5 [MEDIUM] GET form juga kena rate limit
- **File:** `routes/public.py:16` — `@rate_limit(max_requests=10, window_seconds=3600)` di route `/`
- **Masalah:** User yang buka halaman form (GET) juga dihitung. 10x refresh = blocked 1 jam.
- **Fix:** Pindah `@rate_limit` ke dalam function, hanya apply saat `request.method == "POST"`.
- **Dampak:** Legitimate user ter-block

### SEC-6 [MEDIUM] Rate limit memory leak
- **File:** `services/security.py:37` — `_rate_limits` dict
- **Masalah:** Dict tidak pernah prune entry untuk IP yang berhenti visit. Memory grows unbounded.
- **Fix:** Tambah cleanup: hapus entry yang semua timestamp-nya sudah expired. Atau pakai TTL-based store.
- **Dampak:** Memory leak di long-running process

### SEC-7 [MEDIUM] Logout via GET (CSRF logout)
- **File:** `routes/admin.py:77`
- **Masalah:** `/admin/logout` pakai GET. Attacker bisa force logout admin via `<img src="/admin/logout">`.
- **Fix:** Ubah ke POST + CSRF token. Tambah confirmation form di template.
- **Dampak:** Admin bisa di-logout tanpa consent

---

## Belum Difix — BUGS (5)

### BUG-1 [HIGH] append_row hardcoded row 1
- **File:** `services/sheets_service.py:147-149`
- **Masalah:** `append_row` selalu baca `headers = sheet.row_values(1)`. Untuk SHEET_KARYAWAN (title row 1, headers row 2), ini salah.
- **Fix:** Tambah parameter `head_row=1` ke `append_row`. Atau deteksi otomatis berdasarkan sheet name.
- **Dampak:** Data corruption kalau dipakai untuk SHEET_KARYAWAN

### BUG-2 [HIGH] Row-based detail access fragile
- **File:** `routes/admin.py:113-125`
- **Masalah:** `detail(row_num)` akses sheet berdasarkan nomor baris. Kalau ada baris yang di-insert/hapus manual di Google Sheets, row number shift → admin edit record salah.
- **Fix:** Generate unique ID per pengajuan (misal: timestamp + NIP), cari berdasarkan ID bukan row number.
- **Dampak:** Admin bisa edit record yang salah

### BUG-3 [MEDIUM] Race condition di append_row return
- **File:** `services/sheets_service.py:151`
- **Masalah:** `return len(sheet.get_all_values())` baca setelah append. Concurrent request bisa append di antara write dan read → return row number salah.
- **Fix:** Return `None` atau gunakan `append_row` return value dari gspread (sudah ada di versi baru).
- **Dampak:** Minor (return value tidak dipakai caller saat ini)

### BUG-4 [MEDIUM] Login lockout tidak shared across workers
- **File:** `services/auth_service.py:7` — `_login_attempts` dict
- **Masalah:** Lockout state per-process. Dengan gunicorn multi-worker, attacker bisa brute-force 5x per worker.
- **Fix:** Pakai shared store (Redis, atau file-based). Atau single-worker deployment.
- **Dampak:** Brute-force bypass

### BUG-5 [MEDIUM] Dead code — duplicate pending_nip handling
- **File:** `routes/public.py:191-206`
- **Masalah:** Block kedua `pending_nip` check tidak pernah tercapai karena line 135 sudah pop session.
- **Fix:** Hapus block dead code di line 191-206.
- **Dampak:** Dead code, confusing

---

## Belum Difix — UX/UI (6)

### UX-1 [MEDIUM] Flash auto-dismiss tidak work
- **File:** `static/js/main.js:1-10`
- **Masalah:** JS query `.alert` tapi template pakai class berbeda (langsung div dengan bg-color class). Flash messages tidak auto-dismiss.
- **Fix:** Tambah class `alert` ke flash message divs di `base.html`, atau ganti selector di JS.
- **Dampak:** Flash persist sampai navigasi

### UX-2 [MEDIUM] No loading state di form submit
- **File:** Semua form template
- **Masalah:** Tidak ada loading indicator saat submit. User bisa double-click → double submit.
- **Fix:** Tambah spinner/disable button on submit via JS.
- **Dampak:** Duplicate submissions

### UX-3 [LOW] autocomplete="off" di NIP field
- **File:** `templates/form_cuti.html:21`
- **Masalah:** Mencegah browser autofill untuk returning users.
- **Fix:** Ganti dengan `autocomplete="off"` → `autocomplete="username"` atau hapus.
- **Dampak:** Minor inconvenience

### UX-4 [LOW] Default status option confusing
- **File:** `templates/admin/dashboard.html:38`
- **Masalah:** `<option value="">Menunggu ACC</option>` — value kosong tapi label "Menunggu ACC".
- **Fix:** Set value yang eksplisit: `<option value="Menunggu ACC">Menunggu ACC</option>`.
- **Dampak:** Minor inconsistency

### UX-5 [LOW] No SEO meta tags
- **File:** `templates/base.html`
- **Masalah:** Tidak ada `<meta name="description">`.
- **Fix:** Tambah meta tag. (Internal tool, rendah prioritas)
- **Dampak:** Minor

### UX-6 [LOW] Inline onclick di mobile menu
- **File:** `templates/base.html:86`
- **Masalah:** Pakai `onclick` attribute instead of event listener.
- **Fix:** Pindah ke `main.js` dengan `addEventListener`.
- **Dampak:** Minor code quality

---

## Belum Difix — PERFORMANCE (5)

### PERF-1 [HIGH] N+1 queries di histori
- **File:** `routes/admin.py:217-225`
- **Masalah:** Untuk setiap NIP unik, call `hitung_kuota_terpakai()` yang masing-masing baca semua records. 100 NIP = 100 reads.
- **Fix:** Hitung kuota sekali untuk semua NIP dalam satu pass. Atau cache kuota per NIP.
- **Dampak:** Slow page load

### PERF-2 [MEDIUM] DATA_TTL 10 detik terlalu pendek
- **File:** `services/sheets_service.py:55`
- **Masalah:** Cache expire tiap 10 detik. Setiap page load setelah 10s trigger full API read.
- **Fix:** Naikkan ke 60 detik. Tambah manual refresh button di admin.
- **Dampak:** High API usage

### PERF-3 [MEDIUM] detail() 2x API calls
- **File:** `routes/admin.py:116-119`
- **Masalah:** Fetch row data dan headers terpisah. Bisa di-satukan.
- **Fix:** Pakai `get_all_records()` + filter by row_num, atau single batch call.
- **Dampak:** Redundant API calls

### PERF-4 [MEDIUM] generate_surat_route duplicate calls
- **File:** `routes/admin.py:136-139`
- **Masalah:** Sama seperti detail(). Duplicate code dan API calls.
- **Fix:** Refactor ke shared function.
- **Dampak:** Redundant API calls

### PERF-5 [LOW] hitung_kuota_terpakai linear scan
- **File:** `services/kuota_service.py:7`
- **Masalah:** Scan semua CUTI records per NIP. O(n*m) tanpa cache.
- **Fix:** Build index (dict NIP → count) sekali, reuse. (Sudah di-cache, low priority)
- **Dampak:** Negligible dengan cache

---

## Belum Difix — CODE QUALITY (8)

### CODE-1 [MEDIUM] Hardcoded template path
- **File:** `services/surat_service.py:6-9`
- **Masalah:** `TEMPLATE_PATH` hardcoded. Crash kalau file tidak ada.
- **Fix:** Tambah existence check, atau bikin configurable.
- **Dampak:** Runtime error

### CODE-2 [MEDIUM] Dead code — NAMA_KARYAWAN_BAGIAN2
- **File:** `services/surat_service.py:31`
- **Masalah:** `"WAHYU EKO SAPUTRO"` defined but never used.
- **Fix:** Hapus.
- **Dampak:** Dead code

### CODE-3 [MEDIUM] KUOTA_TAHUNAN hardcoded
- **File:** `config/settings.py:18`
- **Masalah:** `KUOTA_TAHUNAN = 12` hardcoded, bukan dari env var.
- **Fix:** `KUOTA_TAHUNAN = int(os.getenv("KUOTA_TAHUNAN", "12"))`
- **Dampak:** Butuh code change untuk ubah kuota

### CODE-4 [MEDIUM] SHEET_CUTI tahun hardcoded
- **File:** `config/settings.py:33`
- **Masalah:** `SHEET_CUTI = "CUTI 2026"` — butuh update manual tiap tahun.
- **Fix:** `SHEET_CUTI = os.getenv("SHEET_CUTI", f"CUTI {datetime.now().year}")`
- **Dampak:** Breaks on year change

### CODE-5 [MEDIUM] Admin username hardcoded di route
- **File:** `routes/admin.py:54`
- **Masalah:** `username == "admin_kepegawaian"` hardcoded, tidak pakai `ADMIN_USERNAME` dari config.
- **Fix:** Ganti dengan `username == ADMIN_USERNAME` (sudah di-import).
- **Dampak:** Config ADMIN_USERNAME di .env tidak dipakai

### CODE-6 [LOW] Duplicate bulan_nama array
- **File:** `routes/public.py:73-76` dan `services/surat_service.py:79-82`
- **Masalah:** Array nama bulan duplikat di 2 file.
- **Fix:** Pindah ke `config/constants.py`, import di kedua file.
- **Dampak:** Maintenance burden

### CODE-7 [LOW] Dead code block
- **File:** `routes/public.py:191-206`
- **Masalah:** Duplicate pending_nip check yang tidak pernah tercapai.
- **Fix:** Hapus.
- **Dampak:** Dead code

### CODE-8 [LOW] Duplicate .claude/ di .gitignore
- **File:** `.gitignore:24`
- **Masalah:** `.claude/` muncul 2x.
- **Fix:** Hapus duplikat.
- **Dampak:** No functional impact

---

## Belum Difix — COMPATIBILITY (5)

### COMP-1 [MEDIUM] Requirements tidak pin minor versions
- **File:** `requirements.txt`
- **Masalah:** `google-auth==2.30.0` mungkin conflict dengan `gspread==6.1.2`.
- **Fix:** Pin semua dependency dengan exact version yang tested.
- **Dampak:** Potential conflict di fresh install

### COMP-2 [LOW] oklch() tidak support browser lama
- **File:** `static/css/style.css`
- **Masalah:** `oklch()` tidak supported di browser pre-2023.
- **Fix:** Tambah fallback: `background-color: #f5f6f9; background-color: oklch(...)`.
- **Dampak:** Colors break di browser lama

### COMP-3 [LOW] overflow-x: clip limited support
- **File:** `static/css/style.css:9`
- **Masalah:** `overflow-x: clip` lebih baru dari `overflow-x: hidden`.
- **Fix:** Ganti dengan `overflow-x: hidden` (universal support).
- **Dampak:** Minor layout issue

### COMP-4 [LOW] DaisyUI version coupling
- **File:** `tailwind.config.js`
- **Masalah:** DaisyUI v4+ butuh Tailwind CSS v3+.
- **Fix:** Pin versions di package.json.
- **Dampak:** Upgrade path bumpy

### COMP-5 [LOW] JS async/await tanpa transpilation
- **File:** `static/js/main.js`
- **Masalah:** Tidak work di IE11.
- **Fix:** (Tidak perlu jika target modern browser saja)
- **Dampak:** None jika IE11 tidak required

---

## Prioritas Fix

| Prioritas | Temuan | Total |
|-----------|--------|-------|
| **Batch 2** (HIGH) | SEC-1, SEC-2, SEC-3, BUG-1, BUG-2, PERF-1, CODE-5 | 7 |
| **Batch 3** (MEDIUM) | SEC-4, SEC-5, SEC-6, SEC-7, BUG-3, BUG-4, BUG-5, UX-1, UX-2, PERF-2, PERF-3, PERF-4, CODE-1, CODE-2, CODE-3, CODE-4, COMP-1 | 17 |
| **Batch 4** (LOW) | Sisanya | 17 |

---

*File ini dipakai sebagai tracking untuk fix bertahap. Update status setelah setiap batch selesai.*
