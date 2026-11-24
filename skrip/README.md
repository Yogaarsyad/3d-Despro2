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

Skrip membutuhkan model pihak ketiga di `modul/` dan `mekanik/` (tidak ikut repo, lihat README di folder itu).
File `.FCStd` hasil skrip tidak menyimpan visibilitas objek. Buka lewat `perakitan/_buka_*.py`
(`FreeCAD.exe perakitan\_buka_PCB2_v4.py`) supaya semua objek tampil.
