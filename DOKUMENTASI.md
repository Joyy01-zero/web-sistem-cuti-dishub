# Dokumentasi Sistem Pengajuan Cuti Online
## Dinas Perhubungan Kota Bogor

---

## Daftar Isi

1. [Gambaran Umum](#gambaran-umum)
2. [Cara Kerja Sistem](#cara-kerja-sistem)
3. [Panduan untuk Karyawan](#panduan-untuk-karyawan)
4. [Panduan untuk Admin Kepegawaian](#panduan-untuk-admin-kepegawaian)
5. [Pengelolaan Data Google Sheets](#pengelolaan-data-google-sheets)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## Gambaran Umum

Sistem Pengajuan Cuti Online adalah aplikasi web yang memungkinkan karyawan Dinas Perhubungan Kota Bogor mengajukan cuti secara online tanpa perlu datang ke Sub Bagian Umum dan Kepegawaian.

### Keunggulan
- **Tanpa kertas** — pengajuan dan persetujuan dilakukan secara digital
- **Akses dari mana saja** — bisa diakses dari komputer atau HP
- **Otomatis** — kuota cuti dihitung otomatis, surat cuti digenerate otomatis
- **Transparan** — karyawan bisa cek status pengajuan kapan saja
- **Data tersimpan aman** — menggunakan Google Sheets yang bisa diakses kapan saja

### Data yang Disimpan
- Data karyawan (NIP, Nama, Jabatan, Golongan, Seksi)
- Data pengajuan cuti (jenis cuti, tanggal, durasi, status)
- Hari libur nasional
- Kuota cuti per karyawan

---

## Cara Kerja Sistem

```
Karyawan mengisi form → Data masuk ke Google Sheets → Admin review → ACC/Tolak → Surat otomatis
```

1. Karyawan mengisi form pengajuan cuti di website
2. Data pengajuan masuk ke Google Sheets
3. Admin kepegawaian melihat pengajuan di dashboard
4. Admin menyetujui (ACC) atau menolak pengajuan
5. Jika disetujui, surat cuti (.docx) bisa di-download otomatis
6. Karyawan bisa cek status pengajuannya kapan saja

---

## Panduan untuk Karyawan

### Mengajukan Cuti

1. Buka website sistem cuti (URL akan diberikan oleh admin)
2. Isi form pengajuan:
   - **NIP** — Nomor Induk Pegawai
   - **Tanggal Lahir** — untuk verifikasi identitas
   - **Jenis Cuti** — pilih jenis cuti yang diinginkan
   - **Keperluan** — alasan pengajuan cuti
   - **Tanggal Mulai & Selesai** — rentang waktu cuti
   - **No. HP** — nomor yang bisa dihubungi
3. Klik **Ajukan Cuti**
4. Catat **ID Pengajuan** yang muncul setelah berhasil

### Jenis Cuti yang Tersedia

| Jenis Cuti | Kuota per Tahun | Keterangan |
|---|---|---|
| Cuti Tahunan | 12 hari kerja | Hak cuti reguler |
| Cuti Sakit | Tidak dibatasi | Tidak mengurangi kuota |
| Cuti Melahirkan | 90 hari | Khusus karyawan wanita |
| Cuti Besar | Sesuai ketentuan | Setelah 6 tahun berturut-turut |
| Cuti Alasan Penting | Sesuai ketentuan | Keperluan mendesak |

### Mengecek Status Pengajuan

1. Buka website sistem cuti
2. Klik menu **Cek Status**
3. Masukkan **NIP** dan **Tanggal Lahir**
4. Semua pengajuan cuti akan tampil beserta statusnya:
   - **Menunggu ACC** — masih dalam review admin
   - **Disetujui** — cuti sudah di-ACC
   - **Ditolak** — pengajuan ditolak (beserta alasan)

---

## Panduan untuk Admin Kepegawaian

### Login

1. Buka halaman admin: `[URL]/admin/login`
2. Masukkan username dan password
3. Session akan otomatis habis setelah 30 menit tidak aktif

### Dashboard

Dashboard menampilkan:
- **Statistik** — jumlah pengajuan menunggu, disetujui, ditolak
- **Daftar pengajuan** — bisa difilter berdasarkan status, seksi, dan bulan
- **Notifikasi** — pengajuan baru yang perlu ditinjau

### Menyetujui / Menolak Pengajuan

1. Klik pengajuan yang ingin ditinjau
2. Lihat detail lengkap pengajuan
3. Klik **ACC** untuk menyetujui atau **Tolak** untuk menolak
4. Jika menolak, tulis alasan penolakan
5. Karyawan bisa melihat status ini saat cek status

### Generate Surat Cuti

1. Buka detail pengajuan yang sudah di-ACC
2. Klik **Download Surat**
3. File .docx akan ter-download otomatis
4. Surat sudah terisi data karyawan, tanggal cuti, dan nomor surat

### Export Data ke Excel

1. Di dashboard, klik **Export Excel**
2. File .xlsx berisi semua data pengajuan akan ter-download
3. Bisa digunakan untuk pelaporan atau arsip

### Kelola Hari Libur

1. Buka menu **Hari Libur**
2. Tambahkan tanggal hari libur nasional
3. Sistem akan otomatis mengecualikan hari libur saat hitung durasi cuti

---

## Pengelolaan Data Google Sheets

Data utama sistem disimpan di Google Sheets. Admin bisa mengakses langsung jika diperlukan.

### Sheet yang Digunakan

| Sheet | Fungsi |
|---|---|
| `DATA_KARYAWAN` | Data master karyawan (NIP, Nama, Jabatan, Golongan, Seksi) |
| `CUTI 2026` | Data pengajuan cuti tahun berjalan |
| `HARI_LIBUR` | Daftar hari libur nasional |

### Menambah Data Karyawan Baru

1. Buka Google Sheets
2. Pilih sheet `DATA_KARYAWAN`
3. Tambahkan baris baru dengan kolom:
   - NIP
   - Nama
   - Jabatan
   - Golongan
   - Seksi
   - Tanggal Lahir
4. Simpan — data langsung bisa digunakan di sistem

### Backup Data

Google Sheets otomatis menyimpan versi history. Untuk backup manual:
1. Buka Google Sheets
2. File > Download > Microsoft Excel (.xlsx)

---

## Troubleshooting

### Karyawan tidak bisa mengajukan cuti
- Pastikan NIP dan Tanggal Lahir sesuai dengan data di `DATA_KARYAWAN`
- Cek apakah kuota cuti masih tersisa
- Pastikan tidak sedang mengajukan cuti di tanggal yang sama

### Admin tidak bisa login
- Pastikan username dan password benar
- Jika terkunci setelah 5x gagal, tunggu 15 menit
- Hubungi pengelola sistem untuk reset password

### Surat cuti tidak bisa di-download
- Pastikan pengajuan sudah di-ACC
- Coba refresh halaman dan download ulang
- Pastikan browser mengizinkan download file

### Data tidak muncul di dashboard
- Cek koneksi internet
- Pastikan Google Sheets bisa diakses
- Refresh halaman dashboard

### Halaman error / tidak bisa diakses
- Coba clear cache browser
- Pastikan URL yang diakses benar
- Hubungi pengelola sistem

---

## FAQ

**Q: Apakah saya perlu membuat akun untuk mengajukan cuti?**
A: Tidak. Karyawan cukup menggunakan NIP dan Tanggal Lahir.

**Q: Berapa lama proses persetujuan cuti?**
A: Tergantung admin kepegawaian. Karyawan bisa cek status kapan saja.

**Q: Apakah cuti sakit mengurangi kuota?**
A: Tidak. Cuti sakit tidak dihitung dalam kuota cuti tahunan.

**Q: Bisakah mengajukan cuti untuk tanggal yang sudah lewat?**
A: Tidak. Tanggal cuti harus di masa depan.

**Q: Bagaimana jika lupa ID pengajuan?**
A: Cukup cek status dengan NIP dan Tanggal Lahir, semua pengajuan akan muncul.

---

## Kontak

Untuk pertanyaan teknis atau masalah dengan sistem, hubungi:

- **Sub Bagian Umum dan Kepegawaian** — Dinas Perhubungan Kota Bogor

---

*Dokumentasi ini dibuat sebagai bagian dari penyerahan sistem. Terakhir diperbarui: Agustus 2026.*
