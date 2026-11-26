# File casing yang dicetak

Satuan STL: mm, skala 100%. **Hanya file di tabel ini yang dicetak.** File lain di folder ini (nomor versi lama, `.step`, `.FCStd`) adalah riwayat atau sumber edit.
Cara memakai slicer ada di [README utama](../README.md), model uji cetak di [`kupon/`](kupon/README.md).

Status per 26 Nov 2026: **belum ada yang pernah dicetak atau diuji rendam.** Cetak kupon uji dulu.

## PCB1: Vest Node (dipasang di dada, target tahan rendam)

| File | Jumlah | Ukuran (mm) | Fungsi | Catatan cetak |
|---|---|---|---|---|
| `PCB1_v10_Base.stl` | 1 | 145.9 x 133.2 x 34.0 | Badan casing: dudukan PCB (4 sekrup) dan ruang modul serta baterai. Tepi atasnya punya alur O-ring dan lubang pilot 16 sekrup tutup | Lantai di bed, tanpa support. PETG, dinding tebal |
| `PCB1_v10_Tutup_cetak.stl` | 1 | 145.9 x 133.2 x 16.9 | Tutup: menekan O-ring, 16 lubang sekrup, dua lekukan membran di atas tombol. Sensor air XKC-Y25-V ditempel di sisi dalamnya (belum dimodelkan) | Pelat luar di bed (posisi bawaan file) |
| `PCB1_v10_Pin_tombol.stl` | **2** | 4.0 x 4.0 x 16.4 | Batang penerus tekanan dari membran ke tombol di PCB (tombol daya dan SOS) | Kecil; cetak pelan, siapkan cadangan |
| `PCB1_v10_Dudukan_klip_cetak.stl` | 1 | 69.8 x 68.4 x 3.0 | Pelat berkantong untuk menempatkan klip chest. Diepoksi ke bawah lantai: 38.0 mm dari tepi luar kiri dan kanan (sisi 145.9), 27.4 mm dari tepi luar di sisi tombol, 37.4 mm dari tepi seberangnya | Kantong menghadap atas, tanpa support |
| Klip chest SlimeVR (tidak ada di repo) | 1 | 61.2 x 59.8 x 15.5 | Penghubung casing ke pelat chest harness. File `ChestMountClip_SlimeBackCoverV1.stl`, Thingiverse thing:6545989 oleh Astrlx, CC BY-SA; simpan di `mekanik/chest/` (lihat `mekanik/README.md`) | **Cocok tidaknya dengan harness GoPro belum dibuktikan** |

## PCB2: Helmet Node (di samping helm, tidak diwajibkan tahan rendam)

| File | Jumlah | Ukuran (mm) | Fungsi | Catatan cetak |
|---|---|---|---|---|
| `PCB2_v17_ibew-kunci-tengah_Base.stl` | 1 | 88.3 x 139.0 x 33.9 (termasuk lidah) | Badan casing helm plus lidah berduri yang masuk slot samping helm dari atas dan mengunci | Lantai di bed; support hanya di bawah lidah. PETG disarankan karena kaki lidah harus lentur. Lidah turunan "IBEW 105 Hard Hat Clip" oleh avenge, CC BY-NC (non-komersial, sebut sumber) |
| `PCB2_v7_Tutup_cetak.stl` | 1 | 71.6 x 139.0 x 5.0 | Tutup casing helm, 12 lubang sekrup, lekukan membran di atas tombol SW1 | Pelat di bed. Lekukan membrannya 0.8 mm (karet 1 mm akan menonjol 0.2 mm). Tepi lekukan sekrup terbuka 0.1 mm (bentuk "C"), dibiarkan |

Cek dulu tebal lidah dengan kupon `Kupon_lidah_*` di helm asli sebelum mencetak badan PCB2.

## Barang yang tidak dicetak

| Barang | Jumlah | Fungsi |
|---|---|---|
| Sekrup M3 x 12 button head (ISO 7380), stainless | 28 (16 PCB1 + 12 PCB2), beli 35 | Mengikat tutup |
| Sekrup M3 x 6 | 4, beli 8 | Mengikat PCB1 ke dudukan |
| Sekrup M3 x 8 | 4, beli 8 | Mengikat PCB2 ke dudukan |
| O-ring cord NBR 2 mm | beli 2 m (PCB1 sekitar 0.49 m) | Segel antara badan dan tutup; ujungnya disambung lem sianoakrilat |
| Karet silikon lembaran 1 mm | 10 x 10 cm | Membran di atas tombol, ditempel silikon sealant |
| Epoksi | secukupnya | Menempel dudukan klip dan klip; lapisan anti pori pada PCB1 |
