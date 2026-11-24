# Model mekanik pihak ketiga

Semua unduhan, bukan buatan tim. Cek lisensi sebelum dipakai atau dipublikasikan.

| Folder / file | Sumber | Lisensi | Ukuran (mm) | Catatan |
|---|---|---|---|---|
| `helm/wings-for-the-hardhat/` | Printables, "Wings for the hardhat" oleh Tibu (2023) | CC BY 4.0 (wajib sebut sumber) | 84.8 x 100.9 x 4.7 (kiri dan kanan sama) | Hiasan sayap untuk hard hat. Bukan adaptor slot |
| `helm/ibew-105-hard-hat-clip/` | Printables, "IBEW 105 Hard Hat Clip" oleh avenge (2025), remix dari IBEW 353 | CC BY-NC 4.0 (non-komersial) | 33.0 x 59.5 x 9.0 | Klip pelat datar dengan tulisan "IBEW 105" |
| `chest/slimevr-chest-mount-clip_thing6545989/` | Thingiverse thing:6545989 oleh Astrlx | CC BY-SA | 61.2 x 59.8 x 15.5 | STL 63 MB, 1,26 juta segitiga. Back-cover SlimeVR dengan klip chest mount kamera olahraga |
| `chest/chestmountplate.stl` | Sumber belum tercatat | belum diketahui | 103.6 x 109.7 x 12.7 | 121 ribu segitiga |

Belum ada: model helm utuh, dan model chest strap GoPro itu sendiri (hanya klip dan pelat yang cocok dengan mount GoPro, belum terbukti).

## Adaptor slot helm (hasil crop, `helm/adaptor_slot/`)
Dibuat dengan `skrip/09_crop_adaptor_slot.py` dari irisan horizontal STL asli, lalu dipotong ke bagian pelat dan kaki pemasang saja.
| File | Ukuran (mm) | Asal | Lisensi turunan |
|---|---|---|---|
| `lidah_slot_ibew.step/.stl` | 33.0 x 31.3 x 3.5 | klip IBEW 105 (kepala bertulisan dibuang) | CC BY-NC 4.0 (non-komersial, sebut sumber) |
| `pelat_slot_sayap.step/.stl` | 33.0 x 16.8 x 3.0 | pelat dasar sayap (sayap hiasan dibuang) | CC BY 4.0 (sebut sumber: Tibu) |
BELUM DICEK terhadap slot helm fisik: lebar, tebal, dan arah masuk.

## File ini tidak ikut repo
Model di folder `helm/` dan `chest/` tidak di-commit (STL SlimeVR 63 MB, dan lisensi CC BY-SA / BY-NC / BY yang berbeda).
Unduh ulang dari halaman sumber di tabel di atas ke folder yang sama.
