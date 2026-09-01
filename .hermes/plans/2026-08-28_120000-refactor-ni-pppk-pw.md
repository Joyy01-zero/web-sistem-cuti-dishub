# Refactor: NI PPPK PW + KABID/KASI Sheet + Hide Cek Status

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Mengubah sistem dari "NIP = ID karyawan" menjadi "NI PPPK PW = ID karyawan" sesuai format sheet Dishub, tambah sheet KABID_KASI untuk auto-fill NIP KABID/KASI, dan hide tab Cek Status.

**Architecture:** Perubahan di 6 file utama + 1 sheet baru. Validasi karyawan tetap pakai DATA_KARYAWAN (kolom `NI PPPK PW`). NIP di CUTI 2026 otomatis diisi dari sheet KABID_KASI. Tracking kuota by NAMA (bukan NIP, karena NIP di sheet dishub = milik Kabid/Kasi).

**Tech Stack:** Flask, gspread, Google Sheets API, Jinja2, vanilla JS

---

## Context

### Masalah
Sistem sebelumnya salah mengira kolom "NIP" di sheet CUTI 2026 = milik karyawan. Padahal di format Dishub:
- **NIP** = NIP KABID/KASI yang menyetujui
- **NI PPPK PW** = ID unik karyawan (ada di sheet DATA_KARYAWAN)

### Sheet yang relevan
- `CUTI 2026` — data cuti (format dishub, 12 kolom + kolom web: STATUS, TGL_SUBMIT, TAHUN, ID, CATATAN, DURASI_HARI_KERJA)
- `DATA_KARYAWAN` — data karyawan (head=2, kolom `NI PPPK PW` = ID karyawan)
- `KABID_KASI` — **BARU**, kolom: NAMA, NIP

### Mapping kolom CUTI 2026
| Kolom | Isi |
|---|---|
| NAMA | Nama karyawan |
| NIP | NIP KABID/KASI (auto-fill dari sheet KABID_KASI) |
| KABID/KASI | Nama KABID/KASI |

---

## Task 1: Buat sheet KABID_KASI di Google Sheets

**Objective:** Tambah sheet baru "KABID_KASI" dengan kolom NAMA dan NIP.

**Files:**
- Create: `setup_kabid_kasi.py` (one-time script)

**Step 1: Buat script setup**

```python
"""Buat sheet KABID_KASI di spreadsheet."""
import json, os
from dotenv import load_dotenv
load_dotenv()
import gspread
from google.oauth2.service_account import Credentials

creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
creds = Credentials.from_service_account_info(creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets"])
gc = gspread.authorize(creds)
sh = gc.open_by_key(os.environ["SPREADSHEET_ID"])

existing = [ws.title for ws in sh.worksheets()]
if "KABID_KASI" in existing:
    print("Sheet KABID_KASI sudah ada")
else:
    ws = sh.add_worksheet("KABID_KASI", rows=50, cols=2)
    ws.update_cell(1, 1, "NAMA")
    ws.update_cell(1, 2, "NIP")
    print("Sheet KABID_KASI dibuat")
```

**Step 2: Jalankan script**

```bash
cd /c/Users/yasin/KKL/Project/sistem-cuti-dishub
PYTHONPATH= venv/Scripts/python.exe setup_kabid_kasi.py
```

**Step 3: Jalankan script auto-populate**

Script akan extract NAMA+NIP KABID/KASI unik dari sheet CUTI 2026 dan tulis ke sheet KABID_KASI.

```bash
cd /c/Users/yasin/KKL/Project/sistem-cuti-dishub
PYTHONPATH= venv/Scripts/python.exe setup_kabid_kasi.py
```

**Step 4: Verifikasi** — buka Google Sheets, tab KABID_KASI harus terisi data.

**Step 5: Commit**

```bash
git add setup_kabid_kasi.py
git commit -m "feat: add KABID_KASI sheet setup + auto-populate script"
```

---

## Task 2: Tambah config SHEET_KABID_KASI + fungsi baca sheet

**Objective:** Tambah konstanta sheet name dan fungsi untuk baca data KABID/KASI.

**Files:**
- Modify: `config/settings.py:37` — tambah `SHEET_KABID_KASI`
- Modify: `services/sheets_service.py` — tambah `get_all_kabid_kasi()` dan `get_kabid_kasi_by_nama()`

**Step 1: Tambah config**

Di `config/settings.py`, tambah setelah baris 37:
```python
SHEET_KABID_KASI = "KABID_KASI"
```

**Step 2: Tambah fungsi di sheets_service.py**

Tambah import `SHEET_KABID_KASI` di baris 10, lalu tambah 2 fungsi baru:

```python
def get_all_kabid_kasi():
    """Ambil semua data KABID/KASI dari sheet."""
    try:
        return get_all_records(SHEET_KABID_KASI)
    except SheetNotFoundError:
        return []

def get_kabid_kasi_by_nama(nama):
    """Cari NIP KABID/KASI berdasarkan nama."""
    records = get_all_kabid_kasi()
    for r in records:
        if str(r.get("NAMA", "")).strip().lower() == str(nama).strip().lower():
            return dict(r)
    return None
```

**Step 3: Commit**

```bash
git add config/settings.py services/sheets_service.py
git commit -m "feat: add SHEET_KABID_KASI config and reader functions"
```

---

## Task 3: Ubah form — NIP jadi NI PPPK PW, KABID/KASI jadi dropdown

**Objective:** Ganti label "NIP" jadi "NI PPPK PW", ganti input KABID/KASI jadi dropdown dari sheet.

**Files:**
- Modify: `templates/form_cuti.html` — ganti label + input NIP, ganti input KABID/KASI jadi dropdown
- Modify: `static/js/form-cuti.js` — ganti validasi NIP jadi NI PPPK PW

**Step 1: Ubah form_cuti.html**

Ganti bagian NIP (baris 21-27):
```html
<div>
    <label class="block text-[13px] font-medium text-base-content mb-1">NI PPPK PW <span class="text-error">*</span></label>
    <input type="text" id="nip" name="nip" value="{{ form_data.get('nip', '') }}"
           placeholder="Masukkan NI PPPK PW" required autocomplete="username"
           class="input w-full text-sm">
    <span id="nip-status" class="text-xs mt-0.5 block"></span>
</div>
```

Ganti bagian KABID/KASI (baris 87-91) — ubah jadi dropdown:
```html
<div>
    <label class="block text-[13px] font-medium text-base-content mb-1">Kabid/Kasi <span class="text-error">*</span></label>
    <select id="kabid_kasi" name="kabid_kasi" required class="select w-full text-sm">
        <option value="">-- Pilih Kabid/Kasi --</option>
        {% for k in kabid_kasi_list %}
        <option value="{{ k.NAMA }}" {{ 'selected' if form_data.get('kabid_kasi') == k.NAMA }}>{{ k.NAMA }}</option>
        {% endfor %}
    </select>
</div>
```

**Step 2: Ubah form-cuti.js**

Ganti teks "NIP" jadi "NI PPPK PW" di validasi (baris 14, 16):
```javascript
span.textContent = '✓ NI PPPK PW terdaftar';
// ...
span.textContent = '✗ NI PPPK PW tidak terdaftar';
```

**Step 3: Commit**

```bash
git add templates/form_cuti.html static/js/form-cuti.js
git commit -m "feat: ganti label NIP ke NI PPPK PW, KABID/KASI jadi dropdown"
```

---

## Task 4: Ubah route form_cuti — kirim NIP KABID/KASI ke sheet

**Objective:** Saat submit, ambil NIP KABID/KASI dari sheet KABID_KASI dan tulis ke kolom NIP di CUTI 2026.

**Files:**
- Modify: `routes/public.py`

**Step 1: Tambah import**

Tambah import `get_kabid_kasi_by_nama` dan `get_all_kabid_kasi`:
```python
from services.sheets_service import (
    append_row,
    generate_pengajuan_id,
    get_karyawan_by_nip,
    get_pengajuan_by_nip,
    get_kabid_kasi_by_nama,
    get_all_kabid_kasi,
)
```

**Step 2: Ubah GET form_cuti — kirim kabid_kasi_list ke template**

```python
return render_template("form_cuti.html", form_data={}, kabid_kasi_list=get_all_kabid_kasi())
```

Dan di setiap `return render_template("form_cuti.html", ...)` yang ada, tambah `kabid_kasi_list=get_all_kabid_kasi()`.

**Step 3: Ubah POST — ambil NIP KABID/KASI**

Setelah validasi kabid_kasi, tambah:
```python
# Ambil NIP KABID/KASI dari sheet
kabid_data = get_kabid_kasi_by_nama(kabid_kasi)
nip_kabid = kabid_data.get("NIP", "") if kabid_data else ""
```

Ganti `"NIP": nip,` jadi `"NIP": nip_kabid,` di data dict (baris 128).

**Step 4: Ubah validasi — ganti pesan error NIP jadi NI PPPK PW**

Ganti semua pesan "NIP" jadi "NI PPPK PW" di validasi (baris 45, 60-62, 64-68).

**Step 5: Ubah redirect setelah submit**

Ganti redirect ke cek_status jadi redirect ke form_cuti dengan flash success:
```python
flash("Pengajuan berhasil dikirim!", "success")
return redirect(url_for("public.form_cuti"))
```

**Step 6: Ubah API validate**

Ganti pesan di `api_validate_nip` (baris 156, 159, 160):
```python
return jsonify({"valid": False, "message": "NI PPPK PW tidak terdaftar."})
# ...
return jsonify({"valid": True, "message": "NI PPPK PW terdaftar."})
```

**Step 7: Commit**

```bash
git add routes/public.py
git commit -m "feat: NIP KABID/KASI auto-fill dari sheet, ganti label ke NI PPPK PW"
```

---

## Task 5: Hide tab Cek Status dari navigasi

**Objective:** Sembunyikan link "Cek Status" di navbar (desktop + mobile), tapi tetap pertahankan route dan template.

**Files:**
- Modify: `templates/base.html`

**Step 1: Comment out link Cek Status desktop (baris 40-44)**

```html
{# Cek Status disembunyikan — route tetap ada #}
{# <a href="{{ url_for('public.cek_status') }}"
   class="px-3 py-1.5 rounded text-[13px] font-medium whitespace-nowrap transition-colors
          {% if request.endpoint == 'public.cek_status' %}bg-primary/10 text-primary{% else %}text-base-content/70 hover:text-base-content hover:bg-base-200{% endif %}">
    Cek Status
</a> #}
```

**Step 2: Comment out link Cek Status mobile (baris 114-118)**

```html
{# Cek Status disembunyikan #}
{# <a href="{{ url_for('public.cek_status') }}"
   class="block px-3 py-2.5 rounded text-[14px] font-medium transition-colors
          {% if request.endpoint == 'public.cek_status' %}bg-primary/10 text-primary{% else %}text-base-content/70 hover:bg-base-200{% endif %}">
    Cek Status
</a> #}
```

**Step 3: Commit**

```bash
git add templates/base.html
git commit -m "feat: hide Cek Status tab from navigation"
```

---

## Task 6: Ubah kuota tracking — dari NIP ke NAMA

**Objective:** Karena NIP di sheet dishub = milik Kabid/Kasi, kuota harus track by NAMA karyawan.

**Files:**
- Modify: `services/kuota_service.py` — ubah `hitung_kuota_terpakai` dan `hitung_kuota_hamil_terpakai` dari NIP-based ke NAMA-based
- Modify: `routes/admin.py` — ubah kuota_index dari NIP-based ke NAMA-based

**Step 1: Ubah kuota_service.py**

Ganti parameter `nip` jadi `nama` di fungsi-fungsi kuota:

```python
def hitung_kuota_terpakai(nama: str, tahun: int) -> int:
    semua_data = get_all_records(SHEET_CUTI)
    total = 0
    for row in semua_data:
        if str(row.get("NAMA", "")).strip().lower() != str(nama).strip().lower():
            continue
        if str(row.get("TAHUN", "")) != str(tahun):
            continue
        if row.get("STATUS", "").strip() != "Disetujui":
            continue
        keperluan = row.get("KEPERLUAN", "").strip()
        if keperluan in ("Sakit", "Cuti Hamil/Melahirkan", "Cuti Melahirkan"):
            continue
        total += _get_durasi(row)
    return total

def sisa_kuota(nama: str, tahun: int) -> int:
    sisa = KUOTA_TAHUNAN - hitung_kuota_terpakai(nama, tahun)
    return max(sisa, 0)

def boleh_ajukan(nama: str, tahun: int, keperluan: str = "", durasi: int = 1) -> bool:
    if keperluan == "Sakit":
        return True
    if keperluan in ("Cuti Hamil/Melahirkan", "Cuti Melahirkan"):
        sisa = sisa_kuota_hamil(nama, tahun)
        return sisa >= durasi
    return sisa_kuota(nama, tahun) >= durasi

def hitung_kuota_hamil_terpakai(nama: str, tahun: int) -> int:
    semua_data = get_all_records(SHEET_CUTI)
    total = 0
    for row in semua_data:
        if str(row.get("NAMA", "")).strip().lower() != str(nama).strip().lower():
            continue
        if str(row.get("TAHUN", "")) != str(tahun):
            continue
        if row.get("STATUS", "").strip() != "Disetujui":
            continue
        if row.get("KEPERLUAN", "").strip() not in ("Cuti Hamil/Melahirkan", "Cuti Melahirkan"):
            continue
        total += _get_durasi(row)
    return total

def sisa_kuota_hamil(nama: str, tahun: int) -> int:
    sisa = KUOTA_HAMIL - hitung_kuota_hamil_terpakai(nama, tahun)
    return max(sisa, 0)
```

**Step 2: Ubah routes/public.py — ganti `nip` jadi `nama` di pemanggilan kuota**

```python
# baris 93: ganti
if not boleh_ajukan(nama, tahun, keperluan, durasi_hari_kerja):
```

**Step 3: Ubah routes/admin.py — kuota_index pakai NAMA**

Di histori(), ganti `nama_index` jadi `nama_set` dan bangun kuota by nama:
```python
nama_set = set()
for r in semua:
    nama = str(r.get("NAMA", "")).strip()
    if not nama:
        continue
    nama_set.add(nama)
    if str(r.get("TAHUN", "")) != str(tahun):
        continue
    if r.get("STATUS", "").strip() != "Disetujui":
        continue
    keperluan = r.get("KEPERLUAN", "").strip()
    durasi = _get_durasi(r)
    if keperluan in ("Cuti Hamil/Melahirkan", "Cuti Melahirkan"):
        hamil_index[nama] = hamil_index.get(nama, 0) + durasi
    elif keperluan != "Sakit":
        kuota_index[nama] = kuota_index.get(nama, 0) + durasi

karyawan_kuota = {}
for nama in nama_set:
    terpakai = kuota_index.get(nama, 0)
    hamil_terpakai = hamil_index.get(nama, 0)
    entry = {
        "nama": nama,
        "terpakai": terpakai,
        "sisa": max(KUOTA_TAHUNAN - terpakai, 0),
    }
    if hamil_terpakai > 0:
        entry["hamil_terpakai"] = hamil_terpakai
        entry["hamil_sisa"] = max(KUOTA_HAMIL - hamil_terpakai, 0)
    karyawan_kuota[nama] = entry
```

Dan ubah template histori.html: ganti `nip` jadi `nama` di loop kuota.

**Step 4: Commit**

```bash
git add services/kuota_service.py routes/public.py routes/admin.py templates/admin/histori.html
git commit -m "feat: kuota tracking by NAMA instead of NIP"
```

---

## Task 7: Restart server + verifikasi end-to-end

**Objective:** Pastikan semua perubahan bekerja.

**Step 1: Restart server**

```bash
# Kill existing
netstat -ano | grep ":5000.*LISTENING" | awk '{print $5}'
# taskkill /F /PID <pid>
# Start fresh
cd /c/Users/yasin/KKL/Project/sistem-cuti-dishub
source venv/Scripts/activate && python app.py
```

**Step 2: Verifikasi**

1. Buka `http://localhost:5000/` — form harus tampil "NI PPPK PW" (bukan NIP)
2. KABID/KASI harus dropdown (bukan text input)
3. Tab "Cek Status" tidak terlihat di navbar
4. Submit dengan NI PPPK PW valid + pilih KABID/KASI → data masuk sheet CUTI 2026 dengan kolom NIP = NIP KABID/KASI
5. Buka Histori admin → kuota tampil by NAMA

**Step 3: Commit final + push**

```bash
git add -A
git commit -m "refactor: NI PPPK PW + KABID/KASI sheet + hide cek status + kuota by nama"
git push origin main
```

---

## Files yang berubah

| File | Perubahan |
|---|---|
| `config/settings.py` | +1 baris: `SHEET_KABID_KASI` |
| `services/sheets_service.py` | +2 fungsi: `get_all_kabid_kasi()`, `get_kabid_kasi_by_nama()` |
| `services/kuota_service.py` | Ubah parameter `nip` → `nama` di 5 fungsi |
| `routes/public.py` | Ubah validasi, auto-fill NIP KABID/KASI, ganti label |
| `routes/admin.py` | Ubah kuota_index dari NIP ke NAMA |
| `templates/form_cuti.html` | Ganti label NIP→NI PPPK PW, KABID/KASI jadi dropdown |
| `templates/base.html` | Hide link Cek Status (desktop + mobile) |
| `templates/admin/histori.html` | Ganti `nip` jadi `nama` di loop kuota |
| `static/js/form-cuti.js` | Ganti teks "NIP" jadi "NI PPPK PW" |
| `setup_kabid_kasi.py` | BARU: one-time script buat sheet |

## Risks & Tradeoffs

1. **Tracking by NAMA** — kalau ada 2 karyawan dengan nama sama, kuota bisa salah. Solusi masa depan: tambah kolom NI PPPK PW di CUTI 2026.
2. **Data existing** — row lama di CUTI 2026 yang NIP-nya = NIP karyawan (bukan Kabid) perlu di-migrate manual atau diabaikan.
3. **Cek Status hidden** — route masih bisa diakses langsung via URL `/cek-status`. Kalau mau benar-benar disable, comment out route-nya.

## Open Questions

- Apakah data KABID/KASI mau diisi manual di sheet, atau mau saya buat script populate otomatis dari data CUTI 2026 yang ada?
- Apakah ada karyawan dengan nama sama yang perlu di-handle?
