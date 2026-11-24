# Ringkasan 3D casing PCB1 dan PCB2 (25 Nov 2026)

Branch `pcb-v3-2026-11-24`, belum di-push. Label: **TERBUKTI** (diukur atau dicek program), **DUGAAN**, **BELUM DICEK**.
Detail angka ada di `laporan/_tahap*_report.txt`. Skrip pembangun ada di `skrip/`.

## 1. Apa yang dikerjakan
| Tahap | Hasil |
|---|---|
| 0-1 | Audit repo, ekspor STEP baru PCB1 dan PCB2 dari EasyEDA (modul tidak terpasang di STEP, hanya yang punya model). Papan cocok dengan Gerber 23 Nov (TERBUKTI) |
| 2-3 | Model modul asli dipasang di perakitan FreeCAD dan dicek tabrakan (`perakitan/assembly_*_v2_modul-asli.FCStd`) |
| 4 | Casing PCB1 dan PCB2 diperbarui pada salinan (file asli `casing/3d-pcb1.FCStd` dan `3D-pcb2.FCStd` tidak diubah) |
| 5 | PCB1: klip chest strap SlimeVR di bawah lantai, DevKit dan GPS asli, lubang USB extend. PCB2: adaptor slot helm di-crop, belum dipasang |

## 2. Casing PCB2 (`casing/3D-pcb2_v4_baterai-bawah.FCStd`)
- Holder 18650 **menggantung di bawah papan** (di atas papan nabrak SuperMini dan TP4056). Dudukan PCB naik 7.5 -> 25.5 mm, dinding 11.1 -> **32.3 mm**.
- Lubang tombol SW1 4.0 x 4.0 mm, plunger menonjol 0.8 mm. Takik USB-C TP4056 lebar 13 mm di dinding kiri.
- Tabrakan semua pasangan: 0 mm3 (TERBUKTI untuk model yang dipakai). Jarak holder ke lantai 1.0 mm.

## 3. Casing PCB1 (`casing/3d-pcb1_v4_usb-extend.FCStd`)
- Holder 18650 di atas papan (puncak z=32.6), dinding 29.2 -> **34.0 mm**, sisa 1.4 mm ke pelat tutup.
- Tombol SW1 dan SW2: selongsong di tutup (OD 8.0 / ID 4.4) plus **pin tombol cetak terpisah** (`casing/PCB1_v2_Pin_tombol.stl`, cetak 2). Ini rancangan tambahan, bukan dari desain asal.
- Celah kabel sensor air 7 mm di dinding y=0 (x=82.6).
- Dua lubang sekrup klip chest di lantai: (40.41, 56.49) dan (86.37, 56.49), jarak 45.96 mm.
- Lubang kabel USB TP4056: d9.0 di dinding y=0 (x=46.5, z=7.0) untuk kabel extend + rubber plug waterproof (rencana Calvin). Diameter 9.0 DUGAAN, sesuaikan ukuran plug.
- Perakitan terbaru `perakitan/assembly_PCB1_v8_gps-antena.FCStd`: DevKit V1 asli (30 pin cocok pad, selisih 0.00 mm, TERBUKTI) dan GPS GY-NEO6MV2 + antena (cocok silkscreen Gerber, tanpa tabrakan). Hanya U9/U3 yang tadinya blok generik, sekarang model asli.

## 4. Masalah terbuka (urut kepentingan)
1. **Holder 18650: pin model berjarak 74.3 mm, pad PCB1 dan PCB2 berjarak 70.0 mm**, lubang 1.1 mm sedangkan pin model 0.5 x 1.5 mm (diagonal 1.6 mm). Ukur holder fisik dengan jangka sorong sebelum print. PCB sudah di produksi.
2. **Helm PCB2:** adaptor slot sudah di-crop (`mekanik/helm/adaptor_slot/`: `lidah_slot_ibew` 33.0 x 31.3 x 3.5 dan `pelat_slot_sayap` 33.0 x 16.8 x 3.0) tapi belum dipasang ke casing. Butuh ukuran slot helm (lebar, tebal), arah masuk, dan pilihan bagian. Turunan IBEW = CC BY-NC.
3. DevKit: pin menonjol 6 mm di bawah PCB, tersisa 0.46 mm dari lantai casing. Gunting pin ~2 mm atau naikkan modul. Rute kabel USB extend nabrak kaki D1 6.6 mm3 (atur rute saat pasang).
4. Arah USB TP4056 PCB2 (dinding kiri), USB DevKit (menghadap -y, 44 mm dari dinding), arah MT3608, arah SuperMini (pad 5V di U1.16 kanan atas), urutan pin GY-521, ujung header GPS: semua DUGAAN.
5. Diameter lubang pilot boss klip chest tidak terukur. Arah klip (lengan menghadap +y) DUGAAN.
6. Panjang sekrup tutup belum dihitung (tiang lebih tinggi).
7. Bukaan antena Ra-02 di PCB1 belum ada (model Ra-02 belum dicocokkan).

## 5. Cara buka
`FreeCAD.exe perakitan\_buka_PCB1_v8.py` (terbaru PCB1) atau `perakitan\_buka_PCB2_v4.py` (PCB2). Skrip itu menampilkan semua objek dan mewarnai per bagian (`perakitan/_warna.py`), karena `.FCStd` hasil skrip tidak menyimpan visibilitas dan warna.

## 6. Tidak ikut commit
Model pihak ketiga di `modul/` dan `mekanik/` (`.gitignore`). Unduh ulang sesuai README di folder itu.
