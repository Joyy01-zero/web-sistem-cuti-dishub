# Audit Status — Sistem Cuti Dishub

> **Total temuan:** 46
> **Sudah difix:** 36 (78%)
> **Sisa:** 10
> **Terakhir update:** 31 Juli 2026

---

## Keterangan

- **Severity** = Seberapa parah bug-nya jika TIDAK difix
- **Fix Risk** = Seberapa besar kemungkinan fix-nya memperkenalkan bug baru

---

## Sudah Difix (36)

| # | ID | Severity | Fix Risk | Temuan | Batch |
|---|-----|----------|----------|--------|-------|
| 1 | SEC-1 | HIGH | LOW | Debug mode via env var | Batch 3 |
| 2 | SEC-3 | HIGH | MEDIUM | Credential JSON in .gitignore (tidak pernah di-commit) | Batch 2 |
| 3 | SEC-4 | MEDIUM | LOW | Hapus X-XSS-Protection header | Batch 2 |
| 4 | SEC-5 | MEDIUM | MEDIUM | Rate limit POST-only | Batch 3 |
| 5 | SEC-6 | MEDIUM | MEDIUM | Rate limit memory cleanup | Batch 3 |
| 6 | SEC-7 | MEDIUM | MEDIUM | Logout via POST + CSRF | Batch 3 |
| 7 | BUG-1 | HIGH | MEDIUM | append_row head_row param | Batch 3 |
| 8 | BUG-3 | MEDIUM | LOW | append_row return None | Batch 2 |
| 9 | BUG-5 | MEDIUM | LOW | Dead code pending_nip | Batch 2 |
| 10 | PERF-1 | HIGH | MEDIUM | Histori single-pass index | Batch 3 |
| 11 | PERF-2 | MEDIUM | LOW | DATA_TTL 10→60 detik | Batch 1 |
| 12 | PERF-3 | MEDIUM | MEDIUM | detail() use cached data | Batch 3 |
| 13 | PERF-4 | MEDIUM | LOW | generate_surat_route pakai cached data (resolved bersama PERF-3) | Batch 3 |
| 14 | UX-1 | MEDIUM | LOW | Flash auto-dismiss selector | Batch 2 |
| 15 | UX-2 | MEDIUM | MEDIUM | Loading state on form submit | Batch 3 |
| 16 | UX-3 | LOW | LOW | autocomplete=username | Batch 4 |
| 17 | UX-4 | LOW | LOW | Default status option value | Batch 4 |
| 18 | UX-5 | LOW | LOW | SEO meta tags | Batch 4 |
| 19 | UX-6 | LOW | LOW | Mobile menu event listener | Batch 4 |
| 20 | CODE-1 | MEDIUM | LOW | Template path existence check | Batch 2 |
| 21 | CODE-2 | MEDIUM | LOW | Hapus NAMA_KARYAWAN_BAGIAN2 | Batch 2 |
| 22 | CODE-3 | MEDIUM | LOW | KUOTA_TAHUNAN dari env var | Batch 2 |
| 23 | CODE-4 | MEDIUM | MEDIUM | SHEET_CUTI auto-detect + error msg | Batch 2+3 |
| 24 | CODE-5 | MEDIUM | LOW | Admin username dari config | Batch 2 |
| 25 | CODE-6 | LOW | LOW | Shared BULAN_NAMA di constants.py | Batch 4 |
| 26 | CODE-7 | LOW | LOW | Dead code pending_nip (duplikat, sama dengan BUG-5) | Batch 2 |
| 27 | CODE-8 | LOW | LOW | Hapus duplikat .claude/ | Batch 2 |
| 28 | COMP-1 | MEDIUM | MEDIUM | Requirements exact version pinning | Batch 3 |
| 29 | COMP-2 | LOW | LOW | CSS oklch() fallback | Batch 4 |
| 30 | COMP-3 | LOW | LOW | overflow-x: hidden | Batch 4 |
| 31 | COMP-4 | LOW | LOW | DaisyUI + Tailwind version pin | Batch 4 |
| 32 | — | CRITICAL | LOW | SECRET_KEY validation on startup | Batch 1 |
| 33 | — | HIGH | LOW | update_row_status tulis no_surat | Batch 1 |
| 34 | — | HIGH | LOW | X-Forwarded-For spoofing fix | Batch 1 |
| 35 | — | HIGH | LOW | get_karyawan_by_nip cache mutation | Batch 1 |
| 36 | — | MEDIUM | LOW | Cross-month date display | Batch 1 |

---

## Sisa Belum Difix (10)

### Fix Risk HIGH — Butuh refactor besar

| # | ID | Severity | Fix Risk | Temuan | Alasan |
|---|-----|----------|----------|--------|--------|
| 1 | SEC-2 | HIGH | HIGH | CSP allows 'unsafe-inline' | Butuh refactor semua inline JS ke file terpisah + generate nonce per-request. Salah = semua halaman blank. |
| 2 | BUG-2 | HIGH | HIGH | Row-based detail access fragile | Butuh: (1) tambah kolom ID di sheet, (2) generate ID saat submit, (3) ubah semua route, (4) migrasi data existing. |

### Fix Risk HIGH — Butuh dependency baru

| # | ID | Severity | Fix Risk | Temuan | Alasan |
|---|-----|----------|----------|--------|--------|
| 3 | BUG-4 | MEDIUM | HIGH | Login lockout tidak shared | Butuh Redis atau file-based shared store. Deployment complexity naik. |

### LOW severity, very minor

| # | ID | Severity | Fix Risk | Temuan | Alasan |
|---|-----|----------|----------|--------|--------|
| 4 | PERF-5 | LOW | LOW | hitung_kuota_terpakai linear scan | Sudah di-cache. Impact negligible. |
| 5 | COMP-5 | LOW | LOW | JS async/await tanpa transpilation | Target audience pakai modern browser. IE11 not required. |

---

## Ringkasan per Batch

| Batch | Tanggal | Fix | Temuan |
|-------|---------|-----|--------|
| Batch 1 | 30 Jul 2026 | 5 | SECRET_KEY, no_surat, XFF, cache, cross-month |
| Batch 2 | 30 Jul 2026 | 12 | Debug mode, X-XSS, admin username, kuota, template path, dead code, flash dismiss, .gitignore |
| Batch 3 | 31 Jul 2026 | 11 | Rate limit, logout POST, memory cleanup, append_row, N+1, detail cache, loading state, sheet error, requirements, PERF-4 resolved |
| Batch 4 | 31 Jul 2026 | 8 | autocomplete, status option, SEO, mobile menu, BULAN_NAMA, oklch fallback, overflow-x, DaisyUI pin |
| **Total** | | **36** | **dari 46 temuan (78%)** |

---

*File ini diupdate otomatis setiap batch fix selesai.*
