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

document.getElementById('formCuti').addEventListener('submit', function(e) {
    const tgl_mulai = document.getElementById('tgl_mulai').value;
    const tgl_selesai = document.getElementById('tgl_selesai').value;
    if (tgl_selesai < tgl_mulai) {
        e.preventDefault();
        alert('Tanggal selesai tidak boleh sebelum tanggal mulai.');
    }
});
