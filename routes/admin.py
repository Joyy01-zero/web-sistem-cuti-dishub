from config.settings import SHEET_CUTI
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_file,
    abort,
)
from flask_login import login_user, logout_user, login_required, current_user
from models import AdminUser
from services.auth_service import verify_password, check_lockout, record_failed_attempt, clear_attempts
from services.sheets_service import (
    get_all_records,
    get_pengajuan_by_status,
    get_karyawan_by_nip,
    get_all_seksi,
    get_stats,
    update_row_status,
    get_sheet,
)
from services.kuota_service import sisa_kuota, hitung_kuota_terpakai, get_tahun_sekarang
from services.surat_service import generate_surat
from services.security import validate_csrf, get_real_ip, safe_error_message
from datetime import datetime
import io

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        validate_csrf()  # CSRF check

        ip = get_real_ip()  # Real IP behind proxy
        is_locked, remaining = check_lockout(ip)

        if is_locked:
            flash(f"Akun terkunci. Coba lagi dalam {remaining} detik.", "danger")
            return render_template("login.html")

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Always verify password even if username wrong (timing attack prevention)
        password_ok = verify_password(password)
        username_ok = (username == "admin_kepegawaian")

        if username_ok and password_ok:
            clear_attempts(ip)
            user = AdminUser(username)
            login_user(user, remember=False)
            session.permanent = True
            flash("Login berhasil.", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            record_failed_attempt(ip)
            is_locked, remaining = check_lockout(ip)
            if is_locked:
                flash(
                    f"Password salah. Akun terkunci selama {remaining} detik.",
                    "danger",
                )
            else:
                flash("Username atau password salah.", "danger")

    return render_template("login.html")


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Anda telah logout.", "info")
    return redirect(url_for("admin.login"))


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    status_filter = request.args.get("status", "")
    bulan_filter = request.args.get("bulan", "")
    seksi_filter = request.args.get("seksi", "")

    if not status_filter:
        status_filter = "Menunggu ACC"

    pengajuan = get_pengajuan_by_status(status_filter, bulan_filter, seksi_filter)
    semua_seksi = get_all_seksi()
    stats = get_stats()

    return render_template(
        "dashboard.html",
        pengajuan=pengajuan,
        semua_seksi=semua_seksi,
        bulan_filter=bulan_filter,
        seksi_filter=seksi_filter,
        status_filter=status_filter,
        stats=stats,
    )


@admin_bp.route("/detail/<int:row_num>")
@login_required
def detail(row_num):
    if row_num < 2:
        abort(404)

    sheet = get_sheet(SHEET_CUTI)
    try:
        row = sheet.row_values(row_num)
        headers = sheet.row_values(1)
        if len(row) < len(headers):
            row.extend([""] * (len(headers) - len(row)))
        data = dict(zip(headers, row))
    except Exception:
        flash("Data tidak ditemukan.", "danger")
        return redirect(url_for("admin.dashboard"))

    return render_template("detail_pengajuan.html", data=data, row_num=row_num)


@admin_bp.route("/generate-surat/<int:row_num>")
@login_required
def generate_surat_route(row_num):
    if row_num < 2:
        abort(404)

    sheet = get_sheet(SHEET_CUTI)
    try:
        row = sheet.row_values(row_num)
        headers = sheet.row_values(1)
        if len(row) < len(headers):
            row.extend([""] * (len(headers) - len(row)))
        data = dict(zip(headers, row))
    except Exception:
        flash("Data tidak ditemukan.", "danger")
        return redirect(url_for("admin.dashboard"))

    try:
        docx_bytes = generate_surat(data)
        nama_file = data.get("NAMA", "unknown").replace(" ", "_")
        filename = f"Surat_Cuti_{nama_file}.docx"
        return send_file(
            io.BytesIO(docx_bytes),
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        flash(safe_error_message(e, "generate surat"), "danger")
        return redirect(url_for("admin.dashboard"))


@admin_bp.route("/update-status/<int:row_num>", methods=["POST"])
@login_required
def update_status(row_num):
    validate_csrf()  # CSRF check

    if row_num < 2:
        abort(404)

    status = request.form.get("status", "").strip()
    no_surat = request.form.get("no_surat", "").strip()

    if status not in ("Disetujui", "Ditolak", "Dibatalkan"):
        flash("Status tidak valid.", "danger")
        return redirect(url_for("admin.dashboard"))

    if status == "Disetujui" and not no_surat:
        flash("Nomor Surat wajib diisi untuk status Disetujui.", "danger")
        return redirect(url_for("admin.detail", row_num=row_num))

    # Validate no_surat format (alphanumeric + / only)
    if no_surat and not all(c.isalnum() or c in "/- .," for c in no_surat):
        flash("Format Nomor Surat tidak valid.", "danger")
        return redirect(url_for("admin.detail", row_num=row_num))

    try:
        update_row_status(SHEET_CUTI, row_num, status, no_surat if status == "Disetujui" else None)
        flash(f"Status berhasil diubah ke {status}.", "success")
    except Exception as e:
        flash(safe_error_message(e, "update status"), "danger")

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/histori")
@login_required
def histori():
    semua = get_all_records(SHEET_CUTI)
    tahun_filter = request.args.get("tahun", str(get_tahun_sekarang()))
    bulan_filter = request.args.get("bulan", "")
    seksi_filter = request.args.get("seksi", "")
    status_filter = request.args.get("status", "")

    filtered = semua
    if tahun_filter:
        filtered = [r for r in filtered if str(r.get("TAHUN", "")) == tahun_filter]
    if bulan_filter:
        filtered = [r for r in filtered if bulan_filter.lower() in str(r.get("MASEHI", "")).lower()]
    if seksi_filter:
        filtered = [r for r in filtered if seksi_filter.lower() in str(r.get("SEKSI", "")).lower()]
    if status_filter:
        filtered = [r for r in filtered if r.get("STATUS", "").strip() == status_filter]

    semua_seksi = get_all_seksi()

    tahun = int(tahun_filter) if tahun_filter else get_tahun_sekarang()
    karyawan_kuota = {}
    for r in semua:
        nip = str(r.get("NIP", "")).strip()
        if nip and nip not in karyawan_kuota:
            karyawan_kuota[nip] = {
                "nama": r.get("NAMA", ""),
                "terpakai": hitung_kuota_terpakai(nip, tahun),
                "sisa": sisa_kuota(nip, tahun),
            }

    return render_template(
        "histori.html",
        pengajuan=filtered,
        semua_seksi=semua_seksi,
        tahun_filter=tahun_filter,
        bulan_filter=bulan_filter,
        seksi_filter=seksi_filter,
        status_filter=status_filter,
        karyawan_kuota=karyawan_kuota,
    )


@admin_bp.route("/export-excel")
@login_required
def export_excel():
    dari_tahun = request.args.get("tahun", str(get_tahun_sekarang()))
    semua = get_all_records(SHEET_CUTI)
    filtered = [r for r in semua if str(r.get("TAHUN", "")) == dari_tahun]

    if not filtered:
        flash("Tidak ada data untuk diexport.", "warning")
        return redirect(url_for("admin.histori"))

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = f"Cuti {dari_tahun}"

    headers = [
        "NO", "MASEHI", "HARI", "NAMA", "KEPERLUAN", "NO SURAT",
        "JABATAN", "SEKSI", "SHIF", "KABID/KASI", "NIP", "STATUS",
        "TGL_SUBMIT", "TAHUN",
    ]
    ws.append(headers)

    for i, row in enumerate(filtered, 1):
        ws.append([
            i,
            row.get("MASEHI", ""),
            row.get("HARI", ""),
            row.get("NAMA", ""),
            row.get("KEPERLUAN", ""),
            row.get("NO SURAT", ""),
            row.get("JABATAN", ""),
            row.get("SEKSI", ""),
            row.get("SHIF", ""),
            row.get("KABID/KASI", ""),
            row.get("NIP", ""),
            row.get("STATUS", ""),
            row.get("TGL_SUBMIT", ""),
            row.get("TAHUN", ""),
        ])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    filename = f"Rekap_Cuti_{dari_tahun}.xlsx"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
