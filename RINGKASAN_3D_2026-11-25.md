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

## 3. Casing PCB1 (`casing/3d-pcb1_v5_sensor-di-tutup.FCStd`)
- Holder 18650 di atas papan (puncak z=32.6), dinding 29.2 -> **34.0 mm**, sisa 1.4 mm ke pelat tutup.
- Tombol SW1 dan SW2: selongsong di tutup (OD 8.0 / ID 4.4) plus **pin tombol cetak terpisah** (`casing/PCB1_v2_Pin_tombol.stl`, cetak 2). Ini rancangan tambahan, bukan dari desain asal.
- Celah kabel sensor air di dinding **dihapus** (sensor XKC-Y25-V ditempel di dalam, di sisi bawah tutup, jadi kabelnya nggak keluar). Versi terbaru: `casing/3d-pcb1_v5_sensor-di-tutup.FCStd`, `PCB1_v5_Base/Tutup_cetak` (STEP, STL), `perakitan/assembly_PCB1_v9_sensor-di-tutup.FCStd`. Ukuran sensor dan titik tempelnya di tutup BELUM dimodelkan.
- Dua lubang sekrup klip chest di lantai: (40.41, 56.49) dan (86.37, 56.49), jarak 45.96 mm.
- Lubang kabel USB TP4056: d9.0 di dinding y=0 (x=46.5, z=7.0) untuk kabel extend + rubber plug waterproof (rencana Calvin). Diameter 9.0 DUGAAN, sesuaikan ukuran plug.
- Perakitan terbaru `perakitan/assembly_PCB1_v8_gps-antena.FCStd`: DevKit V1 asli (30 pin cocok pad, selisih 0.00 mm, TERBUKTI) dan GPS GY-NEO6MV2 + antena (cocok silkscreen Gerber, tanpa tabrakan). Hanya U9/U3 yang tadinya blok generik, sekarang model asli.

## 3b. Waterproof (target tahan rendam, IP67 = 1 m 30 menit; BELUM DIUJI)
`skrip/11_waterproof.py` menghasilkan `casing/3d-pcb1_v6_waterproof.FCStd` dan `casing/3D-pcb2_v5_waterproof.FCStd` (+ STEP/STL, `perakitan/assembly_PCB1_v10_...`, `..._PCB2_v5_...`).
- Segel tutup: kabel O-ring silikon d2.0 di alur 2.6 x 1.5 mm di muka atas dinding. Dinding ditebalkan 3.5 mm ke luar (ukuran luar PCB1 133.9 x 121.2, PCB2 61.6 x 129.0), koordinat dalam tidak berubah. Panjang kabel O-ring sekitar 486 mm (PCB1) dan 357 mm (PCB2), tambah sekitar 10 mm untuk sambungan.
- Sekrup tutup M3 jaraknya sekitar 40 mm: PCB1 12 buah (4 sudut + 8), PCB2 8 buah (4 sudut + 4). Counterbore d7.2 x 1.4 mm untuk ring karet atau sealing washer di bawah kepala sekrup.
- Tombol: membran silikon 0.5 mm dilem di cekungan d12 x 0.8 mm di atas tutup. PCB1: pin batang d4.0 (16.6 mm) tidak menonjol. PCB2: dinding dinaikkan ke 33.9 mm supaya puncak plunger SW1 sejajar dasar cekungan.
- USB: lubang bulat d9.0 di dinding (PCB1 x=46.5 z=7; PCB2 x=0 y=27.4 z=25) untuk konektor panel-mount, pengganti takik terbuka PCB2. Diameter DUGAAN, sesuaikan konektor yang dibeli.
- Lubang pilot sudut PCB2 yang tembus lantai sudah ditutup dari bawah.
- Cek program: geometri valid, alur menerus tanpa lubang di dasarnya, tutup menutup seluruh alur, tabrakan Base-Tutup 0.00 mm3, boss baru tidak menabrak isi. Yang belum ada: uji rendam.
- Masih jadi jalur bocor yang harus ditangani di perakitan: lubang sekrup klip chest di lantai PCB1 (pakai sealing washer + sealant ulir), kabel sensor air di dalam (aman), antena Ra-02 (belum ada), dan sambungan kabel O-ring.

## 4. Masalah terbuka (urut kepentingan)
1. **Holder 18650: pin model berjarak 74.3 mm, pad PCB1 dan PCB2 berjarak 70.0 mm**, lubang 1.1 mm sedangkan pin model 0.5 x 1.5 mm (diagonal 1.6 mm). Ukur holder fisik sebelum print. PCB sudah diproduksi. Polaritas holder (sisi VBAT_POS) juga DUGAAN.
2. **Waterproof belum diuji rendam.** Perlu: konektor USB-C panel-mount waterproof yang muat di lubang d9 (banyak yang butuh sekitar d16), membran silikon tombol, sealing washer untuk 20 sekrup (12 + 8), segel sekrup klip chest di lantai PCB1.
3. **Baterai Li-ion di kotak tertutup rapat:** belum ada jalur pelepas tekanan (vent membran). Pertimbangkan sebelum dipakai di badan/helm.
4. **USB DevKit dan SuperMini terkunci di dalam kotak tertutup:** update firmware harus lewat OTA atau buka kotak. DevKit menghadap -y (44 mm dari dinding, DUGAAN), SuperMini tidak terjangkau.
5. **Helm PCB2:** adaptor slot sudah di-crop (`mekanik/helm/adaptor_slot/`: `lidah_slot_ibew` 33.0 x 31.3 x 3.5, CC BY-NC; `pelat_slot_sayap` 33.0 x 16.8 x 3.0, CC BY) tapi belum dipasang. Butuh ukuran slot helm, arah masuk, dan pilihan bagian.
6. **Sensor air XKC-Y25-V di sisi bawah tutup PCB1:** ukuran dan titik tempel belum dimodelkan.
7. **Arah/urutan DUGAAN:** USB TP4056 PCB1 dan PCB2, arah MT3608, SuperMini (pad 5V di U1.16 kanan atas; cek ke modul fisik karena menyangkut rel 5V), urutan pin GY-521, ujung header GPS.
8. **Ra-02:** antena ditaruh di dalam (keputusan Calvin), jadi tidak ada bukaan. Model Ra-02 (27.9 x 20.4 x 4.6) belum dicocokkan dengan footprint breakout, dan belum dicek jarak antena ke GPS, holder, dan dinding.
9. **Klip chest SlimeVR:** kecocokan dengan GoPro chest harness belum terbukti, diameter lubang pilot boss tidak terukur, arah klip DUGAAN.
10. DevKit: ujung pin tersisa 0.46 mm dari lantai (gunting pin ~2 mm). Rute kabel USB extend nabrak kaki D1 6.6 mm3.
11. Panjang sekrup (M3x6 PCB1, M3x8 PCB2 untuk dudukan PCB; M3x12 untuk tutup) dihitung dari geometri, belum dicoba.

## 5. Cara buka
`FreeCAD.exe perakitan\_buka_PCB1_v8.py` (terbaru PCB1) atau `perakitan\_buka_PCB2_v4.py` (PCB2). Skrip itu menampilkan semua objek dan mewarnai per bagian (`perakitan/_warna.py`), karena `.FCStd` hasil skrip tidak menyimpan visibilitas dan warna.

## 6. Tidak ikut commit
Model pihak ketiga di `modul/` dan `mekanik/` (`.gitignore`). Unduh ulang sesuai README di folder itu.
