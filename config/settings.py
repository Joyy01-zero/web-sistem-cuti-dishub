import os

from dotenv import load_dotenv

load_dotenv()

# App
SECRET_KEY = os.environ.get("SECRET_KEY", "")
TRUSTED_PROXIES = os.environ.get("TRUSTED_PROXIES", "").split(",") if os.environ.get("TRUSTED_PROXIES") else []
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "")

# Admin
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin_kepegawaian")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")

# Google Sheets
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")

# Kuota cuti per tahun
KUOTA_TAHUNAN = int(os.environ.get("KUOTA_TAHUNAN", "12"))

# Instansi
NAMA_INSTANSI = "Dinas Perhubungan Kota Bogor"
BAGIAN = "Sub Bagian Umum dan Kepegawaian"

# Session
SESSION_TIMEOUT_MINUTES = 30

# Rate limiting
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15
MAX_SUBMIT_PER_HOUR = 10

# Sheet names
SHEET_CUTI = os.environ.get("SHEET_CUTI", "CUTI " + str(__import__("datetime").datetime.now().year))
SHEET_KARYAWAN = "DATA_KARYAWAN"
SHEET_HARI_LIBUR = "HARI_LIBUR"
