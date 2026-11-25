# Skrip pembangun (FreeCAD 1.1, tanpa tampilan)

Jalankan berurutan dari PowerShell. Path di dalam skrip masih absolut ke komputer Calvin
(`C:/Users/calvi/Favorites/Downloads/DESPRO_2/...`); ubah dulu kalau dipakai di komputer lain.

```powershell
& "$env:LOCALAPPDATA\Programs\FreeCAD 1.1\bin\freecadcmd.exe" -c "exec(open(r'skrip\01_modul_asli.py').read())"
```

| Skrip | Menghasilkan |
|---|---|
| `01_modul_asli.py` | `perakitan/assembly_PCB1_v2_modul-asli.FCStd` dan `..._PCB2_...` (casing lama + PCB baru + modul asli) |
| `02_pcb2_baterai_bawah_dan_pcb1_holder.py` | `casing/3D-pcb2_v4_baterai-bawah.FCStd`, `perakitan/assembly_PCB2_v4_...`, dan angka holder untuk PCB1 |
| `03_pcb1_casing.py` | `casing/3d-pcb1_v2_baterai-atas.FCStd`, `perakitan/assembly_PCB1_v3_...` (dinding 34 mm, selongsong tombol, celah kabel) |
| `04_pcb1_chest_mount.py` | `casing/3d-pcb1_v3_chest-mount.FCStd`, `perakitan/assembly_PCB1_v4_...` (lubang klip chest) |
| `05_pcb1_usb_extend.py` | `casing/3d-pcb1_v4_usb-extend.FCStd`, `perakitan/assembly_PCB1_v5_...` (lubang kabel USB TP4056) |
| `06_pcb1_devkit_asli.py` | `perakitan/assembly_PCB1_v6_devkit-asli.FCStd` |
| `07_pcb1_gps_asli.py` | `perakitan/assembly_PCB1_v7_gps-asli.FCStd` (model NEO-6M berisi shell, tanpa antena) |
| `08_pcb1_gps_antena.py` | `perakitan/assembly_PCB1_v8_gps-antena.FCStd` (model terbaru, dipakai) |
| `10_pcb1_hapus_celah_sensor.py` | `casing/3d-pcb1_v5_sensor-di-tutup.FCStd`, `perakitan/assembly_PCB1_v9_...` (celah kabel sensor air dihapus) |
| `11_waterproof.py` | `casing/3d-pcb1_v6_waterproof.FCStd`, `casing/3D-pcb2_v5_waterproof.FCStd`, perakitan v10/v5 (alur O-ring, dinding tebal, sekrup tambahan, membran tombol) |
| `12_tanpa_usb.py` | varian tanpa lubang USB: `casing/3d-pcb1_v7_tanpa-usb.FCStd`, `casing/3D-pcb2_v6_tanpa-usb.FCStd`, perakitan v11/v6 |
| `13_tanpa_bolongan.py` | `casing/3d-pcb1_v8_...`, `casing/3D-pcb2_v7_...`, perakitan v12/v7 (semua lubang ditutup, sekrup di luar segel) |
| `14_pcb2_lidah_helm.py` | `casing/3D-pcb2_v8_helm-lidah.FCStd`, `perakitan/assembly_PCB2_v8_...` (bantalan dan lidah IBEW) |
| `09_crop_adaptor_slot.py` | `mekanik/helm/adaptor_slot/` (lidah IBEW dan pelat sayap) |

Skrip membutuhkan model pihak ketiga di `modul/` dan `mekanik/` (tidak ikut repo, lihat README di folder itu).
File `.FCStd` hasil skrip tidak menyimpan visibilitas objek. Buka lewat `perakitan/_buka_*.py`
(`FreeCAD.exe perakitan\_buka_PCB2_v4.py`) supaya semua objek tampil.
