"""Test end-to-end: login admin (session injection) -> GET generate-surat?no_surat=... -> cek docx."""
import io
import os

# Load .env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
with open(env_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

from app import create_app
from config.settings import ADMIN_USERNAME
from services.sheets_service import get_all_records
from config.settings import SHEET_CUTI

app = create_app()

# Ambil ID pengajuan pertama di sheet
rows = get_all_records(SHEET_CUTI)
if not rows:
    print("Sheet kosong — tidak bisa test")
    raise SystemExit(1)
pid = str(rows[0].get("ID", "")).strip()
print(f"Pengajuan ID: {pid}")

with app.test_client() as c:
    # Inject login session (bypass password — test lokal saja)
    with c.session_transaction() as sess:
        sess["_user_id"] = ADMIN_USERNAME
        sess["_fresh"] = True
        sess["_csrf_token"] = "testtoken"

    # 1. Tanpa no_surat -> harus default template
    r1 = c.get(f"/admin/generate-surat/{pid}")
    print(f"Tanpa no_surat: HTTP {r1.status_code}")
    d1 = __import__("docx").Document(io.BytesIO(r1.data))
    for p in d1.paragraphs:
        if "Nomor" in p.text:
            print(f"  -> {p.text.strip()!r}")

    # 2. Dengan no_surat -> harus override
    r2 = c.get(f"/admin/generate-surat/{pid}", query_string={"no_surat": "175/PKWT/VIII/2026"})
    print(f"Dengan no_surat: HTTP {r2.status_code}")
    d2 = __import__("docx").Document(io.BytesIO(r2.data))
    for p in d2.paragraphs:
        if "Nomor" in p.text:
            print(f"  -> {p.text.strip()!r}")
