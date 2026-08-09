# 📖 Panduan Lengkap Jalankan Aplikasi (Untuk Teman)
### Sistem Pengajuan Cuti Online — Dishub Kota Bogor

Panduan ini dibuat khusus agar **mudah diikuti step-by-step**, bahkan untuk Anda yang belum terbiasa dengan pemrograman atau Git/Python.

---

## 🛠️ Langkah 0: Persyaratan Awal (Hanya Sekali)

Pastikan laptop Anda sudah memiliki software dasar berikut:

1. **Python 3.10+**
   - Download di [python.org/downloads](https://www.python.org/downloads/)
   - ⚠️ **PENTING SAAT INSTALL:** Centang kotak **"Add python.exe to PATH"** di bagian paling bawah sebelum menekan *Install Now*.
2. **Git**
   - Download di [git-scm.com/downloads](https://git-scm.com/downloads) (install dengan opsi default).
3. **File `.env` dari Yasin**
   - Karena demi keamanan file rahasia `.env` tidak dimasukkan ke GitHub, Anda **harus meminta file `.env` dari Yasin** (dikirim via WhatsApp/Flashdisk).

---

## 🚀 Langkah Demi Langkah (Step-by-Step)

### 1️⃣ Clone Repository dari GitHub

1. Buka folder tempat Anda ingin menyimpan proyek (misalnya folder `Documents` atau `Desktop`).
2. Klik kanan di area kosong folder tersebut, pilih **Open in Terminal** (atau **Git Bash Here** / buka PowerShell/CMD).
3. Ketik perintah clone berikut lalu tekan **Enter**:
   ```bash
   git clone https://github.com/USERNAME_YASIN/NAMA_REPO.git
   ```
   *(Ganti URL di atas dengan link repository GitHub Yasin)*

4. Masuk ke dalam folder project yang baru di-clone:
   ```bash
   cd sistem-cuti-dishub
   ```

---

### 2️⃣ Copy / Paste File `.env`

1. Ambil file `.env` yang sudah diberikan oleh Yasin.
2. Copy file `.env` tersebut.
3. Paste persis ke dalam folder `sistem-cuti-dishub` (sejajar dengan file `app.py`).

---

### 3️⃣ Buat Virtual Environment (Lingkungan Python)

Buka terminal di dalam folder `sistem-cuti-dishub`, lalu jalankan perintah berikut:

**Di Windows (Command Prompt / PowerShell):**
```powershell
python -m venv venv
```
*(Tunggu beberapa detik sampai folder bernama `venv` muncul di dalam folder project)*

---

### 4️⃣ Aktifkan Virtual Environment

Jalankan perintah berikut di terminal:

- **Jika Menggunakan Command Prompt (CMD):**
  ```cmd
  venv\Scripts\activate
  ```
- **Jika Menggunakan PowerShell:**
  ```powershell
  .\venv\Scripts\activate
  ```

👉 **Ciri berhasil:** Di sebelah kiri teks baris terminal akan muncul tulisan `(venv)` warna hijau/putih.

> 🚨 **Jika Muncul Error di PowerShell:** *"running scripts is disabled on this system..."*
> 
> Ketik perintah ini di PowerShell lalu tekan Enter:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```
> Setelah itu ulangi perintah `.\venv\Scripts\activate`.

---

### 5️⃣ Install Kebutuhan Library (Dependencies)

Pastikan `(venv)` sudah aktif di terminal, lalu ketik:

```powershell
pip install -r requirements.txt
```

*(Tunggu proses download dan install library selesai hingga terminal kembali siap mengetik)*

---

### 6️⃣ Jalankan Aplikasi

Ketik perintah berikut untuk menjalankan server aplikasi:

```powershell
python app.py
```

Jika berhasil, terminal akan menampilkan tulisan:
```text
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
```
⚠️ **Jangan tutup jendela terminal ini** selama Anda sedang melakukan testing.

---

### 7️⃣ Buka di Browser Laptop

1. Buka browser di laptop Anda (Google Chrome, Microsoft Edge, Firefox, dll).
2. Ketik alamat URL berikut di address bar paling atas:
   ```text
   http://localhost:5000
   ```
3. Selamat! Halaman **Sistem Pengajuan Cuti Dishub** sekarang sudah terbuka di laptop Anda! 🎉

---

## 🧪 Hal yang Bisa Anda Uji Coba (Testing)

### 1. Mengajukan Cuti (Sebagai Karyawan)
- Di halaman utama (`http://localhost:5000`):
- Ketik NIP valid (Contoh NIP: `198107052025` a.n. A. ADAM).
- Cek apakah muncul tanda hijau **"✓ NIP terdaftar"**.
- Isi data formulir pengajuan cuti, lalu klik **Kirim Pengajuan**.
- Pastikan sistem mengarahkan Anda ke halaman **Cek Status** dan data Anda tampil.

### 2. Kelola Pengajuan (Sebagai Admin)
- Buka link: `http://localhost:5000/admin/login`
- Masukkan **Username** dan **Password** Admin (tanyakan ke Yasin).
- Di Dashboard Admin:
  - Cek apakah pengajuan cuti yang baru dimasukkan ada di daftar.
  - Coba klik tombol **Setujui** dan masukkan Nomor Surat Cuti.
  - Coba klik tombol **Cetak Surat (.docx)** untuk men-download surat resmi pengajuan cuti.

---

## ❓ Kendala Umum & Cara Mengatasinya (Troubleshooting)

| Kendala / Error | Penyebab | Solusi |
|---|---|---|
| `'python' is not recognized...` | Python belum masuk ke Environment Variable PATH | Reinstall Python, dan pastikan centang opsi **"Add python.exe to PATH"** saat installer terbuka. |
| `RuntimeError: SECRET_KEY belum dikonfigurasi!` | File `.env` belum dimasukkan | Minta file `.env` ke Yasin, lalu letakkan file `.env` tersebut di dalam folder `sistem-cuti-dishub`. |
| `ModuleNotFoundError: No module named 'flask'` | Virtual Environment belum diaktifkan / library belum di-install | Pastikan `(venv)` aktif di terminal, lalu jalankan `pip install -r requirements.txt`. |
| `Halaman web tidak bisa diakses (Refused to Connect)` | Server Flask belum berjalan | Pastikan perintah `python app.py` sudah dijalankan di terminal dan jendela terminal tidak ditutup. |

---
