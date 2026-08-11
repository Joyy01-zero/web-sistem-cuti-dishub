"""Verifikasi: nonce di inline script == nonce di CSP header (dashboard & detail)."""
import os
import re

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
rows = get_all_records(SHEET_CUTI)
pid = str(rows[0].get("ID", "")).strip() if rows else "x"

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess["_user_id"] = ADMIN_USERNAME
        sess["_fresh"] = True
        sess["_csrf_token"] = "testtoken"

    for url in [f"/admin/dashboard", f"/admin/detail/{pid}"]:
        r = c.get(url)
        csp = r.headers.get("Content-Security-Policy", "")
        nonce = re.search(r"nonce-([A-Za-z0-9_\-]+)", csp)
        script_nonce = re.search(r'<script nonce="([^"]+)"', r.get_data(as_text=True))
        ok = nonce and script_nonce and nonce.group(1) == script_nonce.group(1)
        print(f"{url}: HTTP {r.status_code} | script nonce match CSP: {ok}")
        if not ok:
            print(f"  CSP nonce: {nonce.group(1) if nonce else None}")
            print(f"  script nonce: {script_nonce.group(1) if script_nonce else None}")
