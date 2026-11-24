# Ringkasan 3D casing PCB1 dan PCB2 (25 Nov 2026)

Branch `pcb-v3-2026-11-24`, belum di-push. Label: **TERBUKTI** (diukur atau dicek program), **DUGAAN**, **BELUM DICEK**.
Detail angka ada di `laporan/_tahap*_report.txt`. Skrip pembangun ada di `skrip/`.

## 1. Apa yang dikerjakan
| Tahap | Hasil |
|---|---|
| 0-1 | Audit repo, ekspor STEP baru PCB1 dan PCB2 dari EasyEDA (modul tidak terpasang di STEP, hanya yang punya model). Papan cocok dengan Gerber 23 Nov (TERBUKTI) |
| 2-3 | Model modul asli dipasang di perakitan FreeCAD dan dicek tabrakan (`perakitan/assembly_*_v2_modul-asli.FCStd`) |
| 4 | Casing PCB1 dan PCB2 diperbarui pada salinan (file asli `casing/3d-pcb1.FCStd` dan `3D-pcb2.FCStd` tidak diubah) |
| 5 | PCB1: klip chest strap SlimeVR dipasang di bawah lantai. PCB2: helm BELUM dikerjakan (model tidak ada) |

## 2. Casing PCB2 (`casing/3D-pcb2_v4_baterai-bawah.FCStd`)
- Holder 18650 **menggantung di bawah papan** (di atas papan nabrak SuperMini dan TP4056). Dudukan PCB naik 7.5 -> 25.5 mm, dinding 11.1 -> **32.3 mm**.
- Lubang tombol SW1 4.0 x 4.0 mm, plunger menonjol 0.8 mm. Takik USB-C TP4056 lebar 13 mm di dinding kiri.
- Tabrakan semua pasangan: 0 mm3 (TERBUKTI untuk model yang dipakai). Jarak holder ke lantai 1.0 mm.

## 3. Casing PCB1 (`casing/3d-pcb1_v3_chest-mount.FCStd`)
- Holder 18650 di atas papan (puncak z=32.6), dinding 29.2 -> **34.0 mm**, sisa 1.4 mm ke pelat tutup.
- Tombol SW1 dan SW2: selongsong di tutup (OD 8.0 / ID 4.4) plus **pin tombol cetak terpisah** (`casing/PCB1_v2_Pin_tombol.stl`, cetak 2). Ini rancangan tambahan, bukan dari desain asal.
- Celah kabel sensor air 7 mm di dinding y=0 (x=82.6).
- Dua lubang sekrup klip chest di lantai: (40.41, 56.49) dan (86.37, 56.49), jarak 45.96 mm.

## 4. Masalah terbuka (urut kepentingan)
1. **Holder 18650: pin model berjarak 74.3 mm, pad PCB1 dan PCB2 berjarak 70.0 mm**, lubang 1.1 mm sedangkan pin model 0.5 x 1.5 mm (diagonal 1.6 mm). Ukur holder fisik dengan jangka sorong sebelum print. PCB sudah di produksi.
2. **Model GPS tidak utuh** (16 x 12 x 2.6 mm; modul asli sekitar 36 x 23). **Model DevKit (U3) belum ada.** Keduanya masih blok generik; tabrakan U9 dengan U2, U3, U8 belum bisa dipercaya.
3. **USB TP4056 PCB1 menghadap ke tengah papan** (84 mm dari dinding), DUGAAN dari catatan pad IN. Belum ada bukaan. Perlu ekstensi USB-C atau keputusan lain.
4. **Helm PCB2:** belum ada model helm dan adaptor accessory slot. Sayap helm = hiasan, klip IBEW = klip pelat nama (CC BY-NC).
5. Arah USB TP4056 PCB2, arah MT3608, arah SuperMini (pad 5V di U1.16 kanan atas), urutan pin GY-521: semua DUGAAN.
6. Diameter lubang pilot boss klip chest tidak terukur. Arah klip (lengan menghadap +y) DUGAAN.
7. Panjang sekrup tutup belum dihitung (tiang lebih tinggi).
8. Bukaan USB DevKit dan antena Ra-02 di PCB1 belum ada.

## 5. Cara buka
`FreeCAD.exe perakitan\_buka_PCB2_v4.py` (atau `_buka_PCB1_v4.py`). Skrip itu menampilkan semua objek, karena `.FCStd` hasil skrip tidak menyimpan visibilitas.

## 6. Tidak ikut commit
Model pihak ketiga di `modul/` dan `mekanik/` (`.gitignore`). Unduh ulang sesuai README di folder itu.
