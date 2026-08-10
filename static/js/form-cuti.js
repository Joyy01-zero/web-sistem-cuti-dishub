document.getElementById('nip').addEventListener('blur', async function() {
    const nip = this.value.trim();
    const status = document.getElementById('nip-status');
    if (!nip) { status.textContent = ''; return; }
    status.textContent = 'Mencari...';
    status.className = 'text-xs mt-0.5 block text-base-content/50';
    try {
        const resp = await fetch(`/api/karyawan/validate/${nip}`);
        const data = await resp.json();
        const span = document.createElement('span');
        if (data.valid) {
            span.className = 'text-success font-medium';
            span.textContent = '✓ NIP terdaftar';
        } else {
            span.className = 'text-error font-medium';
            span.textContent = '✗ NIP tidak terdaftar';
        }
        status.replaceChildren(span);
    } catch(e) { status.textContent = ''; }
});

// Setup Flatpickr Date Picker
document.addEventListener('DOMContentLoaded', function() {
    if (typeof flatpickr !== 'undefined') {
        if (flatpickr.l10ns && flatpickr.l10ns.id) {
            flatpickr.localize(flatpickr.l10ns.id);
        }

        const commonConfig = {
            altInput: true,
            altFormat: "d/m/Y",
            dateFormat: "Y-m-d",
            allowInput: true,
            altInputClass: "input w-full text-sm"
        };

        // Tanggal Lahir: maxDate hari ini (tidak bisa pilih masa depan)
        flatpickr("#tgl_lahir", Object.assign({}, commonConfig, {
            maxDate: "today"
        }));

        // Tanggal Selesai: minDate hari ini (tidak bisa pilih masa lalu)
        const fpSelesai = flatpickr("#tgl_selesai", Object.assign({}, commonConfig, {
            minDate: "today"
        }));

        // Tanggal Mulai: minDate hari ini, dan update minDate Tanggal Selesai secara otomatis
        flatpickr("#tgl_mulai", Object.assign({}, commonConfig, {
            minDate: "today",
            onChange: function(selectedDates, dateStr) {
                if (selectedDates.length > 0 && fpSelesai) {
                    fpSelesai.set("minDate", selectedDates[0]);
                    if (fpSelesai.selectedDates.length > 0 && fpSelesai.selectedDates[0] < selectedDates[0]) {
                        fpSelesai.setDate(selectedDates[0]);
                    }
                }
            }
        }));
    }
});

document.getElementById('formCuti').addEventListener('submit', function(e) {
    const tgl_mulai = document.getElementById('tgl_mulai').value;
    const tgl_selesai = document.getElementById('tgl_selesai').value;
    if (tgl_selesai && tgl_mulai && tgl_selesai < tgl_mulai) {
        e.preventDefault();
        alert('Tanggal selesai tidak boleh sebelum tanggal mulai.');
    }
});
