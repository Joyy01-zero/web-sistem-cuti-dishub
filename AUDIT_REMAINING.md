# Audit Status — Sistem Cuti Dishub

> **Total temuan:** 46
> **Sudah difix:** 39 (85%)
> **Sisa terkonfirmasi:** 2 (keduanya LOW severity, sengaja diskip — lihat tabel bawah)
> **Terakhir update:** 6 Agustus 2026
>
> Catatan: angka sisa kini disesuaikan dengan daftar riil di tabel (versi sebelumnya menulis 10 namun hanya mencantumkan 5 entri).

---

## Keterangan

- **Severity** = Seberapa parah bug-nya jika TIDAK difix
- **Fix Risk** = Seberapa besar kemungkinan fix-nya memperkenalkan bug baru

---

## Sudah Difix (39)

| # | ID | Severity | Fix Risk | Temuan | Batch |
|---|-----|----------|----------|--------|-------|
| 1 | SEC-1 | HIGH | LOW | Debug mode via env var | Batch 3 |
| 2 | SEC-2 | HIGH | HIGH | CSP tanpa 'unsafe-inline' (nonce per-request + semua JS/style eksternal) | Batch 5 |
| 3 | SEC-3 | HIGH | MEDIUM | Credential JSON in .gitignore (tidak pernah di-commit) | Batch 2 |
| 4 | SEC-4 | MEDIUM | LOW | Hapus X-XSS-Protection header | Batch 2 |
| 5 | SEC-5 | MEDIUM | MEDIUM | Rate limit POST-only | Batch 3 |
| 6 | SEC-6 | MEDIUM | MEDIUM | Rate limit memory cleanup | Batch 3 |
| 7 | SEC-7 | MEDIUM | MEDIUM | Logout via POST + CSRF | Batch 3 |
| 8 | BUG-1 | HIGH | MEDIUM | append_row head_row param | Batch 3 |
| 9 | BUG-2 | HIGH | HIGH | Row-based detail access → kolom ID unik per pengajuan + migrasi data | Batch 5 |
| 10 | BUG-3 | MEDIUM | LOW | append_row return None | Batch 2 |
| 11 | BUG-4 | MEDIUM | HIGH | Login lockout shared antar worker (file-based store + filelock) | Batch 5 |
| 12 | BUG-5 | MEDIUM | LOW | Dead code pending_nip | Batch 2 |
| 13 | PERF-1 | HIGH | MEDIUM | Histori single-pass index | Batch 3 |
| 14 | PERF-2 | MEDIUM | LOW | DATA_TTL 10→60 detik | Batch 1 |
| 15 | PERF-3 | MEDIUM | MEDIUM | detail() use cached data | Batch 3 |
| 16 | PERF-4 | MEDIUM | LOW | generate_surat_route pakai cached data (resolved bersama PERF-3) | Batch 3 |
| 17 | UX-1 | MEDIUM | LOW | Flash auto-dismiss selector | Batch 2 |
| 18 | UX-2 | MEDIUM | MEDIUM | Loading state on form submit | Batch 3 |
| 19 | UX-3 | LOW | LOW | autocomplete=username | Batch 4 |
| 20 | UX-4 | LOW | LOW | Default status option value | Batch 4 |
| 21 | UX-5 | LOW | LOW | SEO meta tags | Batch 4 |
| 22 | UX-6 | LOW | LOW | Mobile menu event listener | Batch 4 |
| 23 | CODE-1 | MEDIUM | LOW | Template path existence check | Batch 2 |
| 24 | CODE-2 | MEDIUM | LOW | Hapus NAMA_KARYAWAN_BAGIAN2 | Batch 2 |
| 25 | CODE-3 | MEDIUM | LOW | KUOTA_TAHUNAN dari env var | Batch 2 |
| 26 | CODE-4 | MEDIUM | MEDIUM | SHEET_CUTI auto-detect + error msg | Batch 2+3 |
| 27 | CODE-5 | MEDIUM | LOW | Admin username dari config | Batch 2 |
| 28 | CODE-6 | LOW | LOW | Shared BULAN_NAMA di constants.py | Batch 4 |
| 29 | CODE-7 | LOW | LOW | Dead code pending_nip (duplikat, sama dengan BUG-5) | Batch 2 |
| 30 | CODE-8 | LOW | LOW | Hapus duplikat .claude/ | Batch 2 |
| 31 | COMP-1 | MEDIUM | MEDIUM | Requirements exact version pinning | Batch 3 |
| 32 | COMP-2 | LOW | LOW | CSS oklch() fallback | Batch 4 |
| 33 | COMP-3 | LOW | LOW | overflow-x: hidden | Batch 4 |
| 34 | COMP-4 | LOW | LOW | DaisyUI + Tailwind version pin | Batch 4 |
| 35 | — | CRITICAL | LOW | SECRET_KEY validation on startup | Batch 1 |
| 36 | — | HIGH | LOW | update_row_status tulis no_surat | Batch 1 |
| 37 | — | HIGH | LOW | X-Forwarded-For spoofing fix | Batch 1 |
| 38 | — | HIGH | LOW | get_karyawan_by_nip cache mutation | Batch 1 |
| 39 | — | MEDIUM | LOW | Cross-month date display | Batch 1 |

Bonus yang ikut difix di Batch 5 (di luar daftar audit):
- Regresi format tanggal cuti satu hari di `routes/public.py` (tampil "15 s.d. 15 Juli" → kini "15 Juli").
- `get_all_seksi()` hardcoded "CUTI 2026" → kini mengikuti `SHEET_CUTI` (aman saat ganti tahun).
- `setup_sheets.py` hardcoded "CUTI 2026" → kini mengikuti `SHEET_CUTI`.

---

## Sisa Belum Difix (2)

### LOW severity, very minor

| # | ID | Severity | Fix Risk | Temuan | Alasan skip |
|---|-----|----------|----------|--------|--------|
| 1 | PERF-5 | LOW | LOW | hitung_kuota_terpakai linear scan | Sudah di-cache. Impact negligible. |
| 2 | COMP-5 | LOW | LOW | JS async/await tanpa transpilation | Target audience pakai modern browser. IE11 not required. |

---

## Ringkasan per Batch

| Batch | Tanggal | Fix | Temuan |
|-------|---------|-----|--------|
| Batch 1 | 30 Jul 2026 | 5 | SECRET_KEY, no_surat, XFF, cache, cross-month |
| Batch 2 | 30 Jul 2026 | 12 | Debug mode, X-XSS, admin username, kuota, template path, dead code, flash dismiss, .gitignore |
| Batch 3 | 31 Jul 2026 | 11 | Rate limit, logout POST, memory cleanup, append_row, N+1, detail cache, loading state, sheet error, requirements, PERF-4 resolved |
| Batch 4 | 31 Jul 2026 | 8 | autocomplete, status option, SEO, mobile menu, BULAN_NAMA, oklch fallback, overflow-x, DaisyUI pin |
| Batch 5 | 6 Agu 2026 | 3 | CSP nonce tanpa unsafe-inline (SEC-2), kolom ID unik per pengajuan + migrasi (BUG-2), shared login lockout file-based (BUG-4) |
| **Total** | | **39** | **dari 46 temuan (85%)** |

---

## Catatan Deployment Batch 5

1. Jalankan `python migrate_add_id.py` **sebelum** deploy kode baru (menambah kolom ID + backfill data lama). Script idempoten.
2. Deploy kode baru.
3. Jalankan ulang `python migrate_add_id.py` untuk backfill pengajuan yang masuk di celah antara langkah 1 dan 2.
4. State lockout login tersimpan di `instance/auth_state.json` (shared antar worker). Di Railway/disk ephemeral state reset saat redeploy; set env `AUTH_STATE_FILE` ke path persisten jika perlu.

---

*File ini diupdate setiap batch fix selesai.*
