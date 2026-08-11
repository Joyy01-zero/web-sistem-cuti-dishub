from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from config.constants import BULAN_NAMA
from config.settings import SHEET_CUTI
from services.kuota_service import (
    boleh_ajukan,
    get_tahun_sekarang,
    hitung_hari_kerja,
    sisa_kuota,
    sisa_kuota_hamil,
)
from services.security import rate_limit, safe_error_message, validate_csrf
from services.sheets_service import (
    append_row,
    generate_pengajuan_id,
    get_karyawan_by_nip,
    get_pengajuan_by_nip,
)

public_bp = Blueprint("public", __name__)


@public_bp.route("/", methods=["GET", "POST"])
@rate_limit(max_requests=10, window_seconds=3600, methods=["POST"])  # 10 submit per jam per IP (GET not limited)
def form_cuti():
    if request.method == "POST":
        validate_csrf()  # CSRF check

        nip = request.form.get("nip", "").strip()
        nama = request.form.get("nama", "").strip()
        jabatan = request.form.get("jabatan", "").strip()
        seksi = request.form.get("seksi", "").strip()
        shif = request.form.get("shif", "").strip()
        tgl_mulai = request.form.get("tgl_mulai", "").strip()
        tgl_selesai = request.form.get("tgl_selesai", "").strip()
        keperluan = request.form.get("keperluan", "").strip()
        kabid_kasi = request.form.get("kabid_kasi", "").strip()
        catatan = request.form.get("catatan", "").strip()

        # Validasi field wajib
        missing = []
        if not nip: missing.append("NIP")
        if not nama: missing.append("Nama")
        if not jabatan: missing.append("Jabatan")
        if not seksi: missing.append("Bidang/Seksi")
        if not shif: missing.append("Shif")
        if not tgl_mulai: missing.append("Tanggal Mulai")
        if not tgl_selesai: missing.append("Tanggal Selesai")
        if not keperluan: missing.append("Keperluan")
        if not kabid_kasi: missing.append("Kabid/Kasi")
        if missing:
            flash(f"Field wajib belum diisi: {', '.join(missing)}.", "danger")
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

        # Hitung durasi hari kerja
        durasi_hari_kerja = hitung_hari_kerja(tgl_mulai, tgl_selesai)
        if durasi_hari_kerja <= 0:
            flash("Durasi cuti tidak valid (0 hari kerja).", "danger")
            return render_template("form_cuti.html", form_data=request.form)

        # Validasi kuota
        tahun = get_tahun_sekarang()
        if not boleh_ajukan(nip, tahun, keperluan, durasi_hari_kerja):
            if keperluan in ("Cuti Hamil/Melahirkan", "Cuti Melahirkan"):
                flash("Kuota cuti hamil/melahirkan (90 hari kerja) tidak mencukupi.", "danger")
            else:
                flash("Kuota cuti tahunan (12 hari kerja) tidak mencukupi.", "danger")
            return render_template("form_cuti.html", form_data=request.form)

        # Format hari
        if tgl_mulai_dt.date() == tgl_selesai_dt.date():
            hari = f"{tgl_mulai_dt.day} {BULAN_NAMA[tgl_mulai_dt.month]} {tgl_mulai_dt.year}"
        elif tgl_mulai_dt.month != tgl_selesai_dt.month or tgl_mulai_dt.year != tgl_selesai_dt.year:
            # Cross-month or cross-year: show full dates for both
            hari = (
                f"{tgl_mulai_dt.day} {BULAN_NAMA[tgl_mulai_dt.month]} {tgl_mulai_dt.year} "
                f"s.d. {tgl_selesai_dt.day} {BULAN_NAMA[tgl_selesai_dt.month]} {tgl_selesai_dt.year}"
            )
        else:
            hari = (
                f"{tgl_mulai_dt.day} s.d. {tgl_selesai_dt.day} "
                f"{BULAN_NAMA[tgl_selesai_dt.month]} {tgl_selesai_dt.year}"
            )

        bulan_str = f"{BULAN_NAMA[tgl_mulai_dt.month]} {tgl_mulai_dt.year}"

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
            "ID": generate_pengajuan_id(),
            "CATATAN": catatan,
            "DURASI_HARI_KERJA": str(durasi_hari_kerja),
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
    """Validate NIP exists. Always HTTP 200 so responses can't be used to enumerate NIPs."""
    nip_clean = nip.strip()
    if not nip_clean.isdigit() or len(nip_clean) > 20:
        return jsonify({"valid": False, "message": "NIP tidak terdaftar."})
    karyawan = get_karyawan_by_nip(nip_clean)
    if not karyawan:
        return jsonify({"valid": False, "message": "NIP tidak terdaftar."})
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
            sisa_hamil = sisa_kuota_hamil(nip, tahun)
            return render_template(
                "cek_status.html",
                pengajuan=pengajuan,
                nama=karyawan.get("NAMA", ""),
                nip=nip,
                sisa_kuota=sisa,
                sisa_kuota_hamil=sisa_hamil,
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
        sisa_hamil = sisa_kuota_hamil(nip, tahun)

        return render_template(
            "cek_status.html",
            pengajuan=pengajuan,
            nama=karyawan.get("NAMA", ""),
            nip=nip,
            sisa_kuota=sisa,
            sisa_kuota_hamil=sisa_hamil,
            tahun=tahun,
            submitted=True,
        )

    return render_template("cek_status.html", submitted=False)
