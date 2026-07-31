from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from datetime import datetime
from services.sheets_service import (
    get_karyawan_by_nip,
    get_pengajuan_by_nip,
    append_row,
)
from services.kuota_service import boleh_ajukan, sisa_kuota, get_tahun_sekarang
from config.settings import SHEET_CUTI
from services.security import validate_csrf, rate_limit, get_real_ip, safe_error_message

public_bp = Blueprint("public", __name__)


@public_bp.route("/", methods=["GET", "POST"])
@rate_limit(max_requests=10, window_seconds=3600)  # 10 submit per jam per IP
def form_cuti():
    if request.method == "POST":
        validate_csrf()  # CSRF check

        nip = request.form.get("nip", "").strip()
        nama = request.form.get("nama", "").strip()
        tgl_lahir = request.form.get("tgl_lahir", "").strip()
        jabatan = request.form.get("jabatan", "").strip()
        seksi = request.form.get("seksi", "").strip()
        shif = request.form.get("shif", "").strip()
        tgl_mulai = request.form.get("tgl_mulai", "").strip()
        tgl_selesai = request.form.get("tgl_selesai", "").strip()
        keperluan = request.form.get("keperluan", "").strip()
        kabid_kasi = request.form.get("kabid_kasi", "").strip()

        # Validasi field wajib
        if not all(
            [nip, nama, tgl_lahir, jabatan, seksi, tgl_mulai, tgl_selesai, keperluan, kabid_kasi]
        ):
            flash("Semua field wajib diisi.", "danger")
            return render_template("form_cuti.html", form_data=request.form)

        # Validasi NIP format (hanya angka)
        if not nip.isdigit():
            flash("NIP harus berupa angka.", "danger")
            return render_template("form_cuti.html", form_data=request.form)

        # Validasi NIP terdaftar
        karyawan = get_karyawan_by_nip(nip)
        if not karyawan:
            flash("NIP tidak terdaftar di database karyawan.", "danger")
            return render_template("form_cuti.html", form_data=request.form)

        # Validasi tgl lahir
        if str(karyawan.get("TGL_LAHIR", "")).strip() != tgl_lahir:
            flash("Tanggal lahir tidak sesuai data karyawan.", "danger")
            return render_template("form_cuti.html", form_data=request.form)

        # Validasi tanggal
        try:
            tgl_mulai_dt = datetime.strptime(tgl_mulai, "%Y-%m-%d")
            tgl_selesai_dt = datetime.strptime(tgl_selesai, "%Y-%m-%d")
            if tgl_selesai_dt < tgl_mulai_dt:
                flash("Tanggal selesai tidak boleh sebelum tanggal mulai.", "danger")
                return render_template("form_cuti.html", form_data=request.form)
        except ValueError:
            flash("Format tanggal tidak valid.", "danger")
            return render_template("form_cuti.html", form_data=request.form)

        # Validasi kuota
        tahun = get_tahun_sekarang()
        if not boleh_ajukan(nip, tahun):
            flash("Kuota cuti tahun ini sudah habis.", "danger")
            return render_template("form_cuti.html", form_data=request.form)

        # Format hari
        bulan_nama = [
            "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember",
        ]
        if tgl_mulai == tgl_selesai:
            hari = f"{tgl_mulai_dt.day} {bulan_nama[tgl_mulai_dt.month]} {tgl_mulai_dt.year}"
        elif tgl_mulai_dt.month != tgl_selesai_dt.month or tgl_mulai_dt.year != tgl_selesai_dt.year:
            # Cross-month or cross-year: show full dates for both
            hari = (
                f"{tgl_mulai_dt.day} {bulan_nama[tgl_mulai_dt.month]} {tgl_mulai_dt.year} "
                f"s.d. {tgl_selesai_dt.day} {bulan_nama[tgl_selesai_dt.month]} {tgl_selesai_dt.year}"
            )
        else:
            hari = (
                f"{tgl_mulai_dt.day} s.d. {tgl_selesai_dt.day} "
                f"{bulan_nama[tgl_selesai_dt.month]} {tgl_selesai_dt.year}"
            )

        bulan_str = f"{bulan_nama[tgl_mulai_dt.month]} {tgl_mulai_dt.year}"

        # Tulis ke Sheets
        data = {
            "MASEHI": bulan_str,
            "HARI": hari,
            "NAMA": nama,
            "KEPERLUAN": keperluan,
            "NO SURAT": "",
            "JABATAN": jabatan,
            "SEKSI": seksi,
            "SHIF": shif,
            "KABID/KASI": kabid_kasi,
            "NIP": nip,
            "STATUS": "Menunggu ACC",
            "TGL_SUBMIT": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "TAHUN": str(tahun),
        }

        try:
            append_row(SHEET_CUTI, data)
            flash("Pengajuan berhasil dikirim! Simpan NIP Anda untuk cek status.", "success")
            # Store NIP in session and redirect to cek-status
            session['pending_nip'] = nip
            return redirect(url_for("public.cek_status"))
        except Exception as e:
            flash(safe_error_message(e, "mengirim pengajuan"), "danger")
            return render_template("form_cuti.html", form_data=request.form)

    return render_template("form_cuti.html", form_data={})


@public_bp.route("/api/karyawan/validate/<nip>")
@rate_limit(max_requests=30, window_seconds=60)
def api_validate_nip(nip):
    """Validate NIP exists. Returns only validation result, no personal data."""
    nip_clean = nip.strip()
    if not nip_clean.isdigit() or len(nip_clean) > 20:
        return jsonify({"valid": False, "message": "Format NIP tidak valid."}), 400
    karyawan = get_karyawan_by_nip(nip_clean)
    if not karyawan:
        return jsonify({"valid": False, "message": "NIP tidak terdaftar."}), 404
    return jsonify({"valid": True, "message": "NIP terdaftar."})



@public_bp.route("/cek-status", methods=["GET", "POST"])
@rate_limit(max_requests=20, window_seconds=60)
def cek_status():
    # Auto-show if redirected from form submission
    if request.method == "GET" and "pending_nip" in session:
        nip = session.pop("pending_nip")
        session.pop("pending_tgl_lahir", None)
        karyawan = get_karyawan_by_nip(nip)
        if karyawan:
            pengajuan = get_pengajuan_by_nip(nip)
            tahun = get_tahun_sekarang()
            sisa = sisa_kuota(nip, tahun)
            return render_template(
                "cek_status.html",
                pengajuan=pengajuan,
                nama=karyawan.get("NAMA", ""),
                nip=nip,
                sisa_kuota=sisa,
                tahun=tahun,
                submitted=True,
            )

    if request.method == "POST":
        validate_csrf()  # CSRF check

        nip = request.form.get("nip", "").strip()
        tgl_lahir = request.form.get("tgl_lahir", "").strip()

        if not nip or not tgl_lahir:
            flash("NIP dan Tanggal Lahir wajib diisi.", "danger")
            return render_template("cek_status.html")

        if not nip.isdigit():
            flash("NIP harus berupa angka.", "danger")
            return render_template("cek_status.html")

        karyawan = get_karyawan_by_nip(nip)
        if not karyawan:
            flash("NIP tidak ditemukan.", "danger")
            return render_template("cek_status.html")

        if str(karyawan.get("TGL_LAHIR", "")).strip() != tgl_lahir:
            flash("Tanggal lahir tidak sesuai.", "danger")
            return render_template("cek_status.html")

        pengajuan = get_pengajuan_by_nip(nip)
        tahun = get_tahun_sekarang()
        sisa = sisa_kuota(nip, tahun)

        return render_template(
            "cek_status.html",
            pengajuan=pengajuan,
            nama=karyawan.get("NAMA", ""),
            nip=nip,
            sisa_kuota=sisa,
            tahun=tahun,
            submitted=True,
        )

    return render_template("cek_status.html", submitted=False)
