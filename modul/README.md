# Model 3D modul

Ukuran = kotak pembatas (bounding box) hasil baca STEP di FreeCAD 24 Nov 2026, sumbu mentah (tiap file punya
asal dan orientasi sendiri). Ini ukuran MODEL, bukan hasil ukur modul fisik.

| File | Ukuran model (mm) | Ref | Catatan |
|---|---|---|---|
| `mt3608-boost.step` | 37.15 x 17.43 x 7.30 | PCB1 U2 | Panjang cocok footprint 37.15. Tinggi 7.3 (blok lama 6.0) |
| `tp4056-typec.step` | 29.30 x 17.40 x 4.14 | U7 (PCB1, PCB2) | Lebar cocok 17.4. Panjang 29.3 vs footprint 28 (konektor USB-C menonjol?) |
| `gy521-mpu6050.step` | 20.32 x 15.54 x 11.72 | PCB1 U8 | Tinggi 11.72 kemungkinan termasuk pin header |
| `esp32c3-supermini_v5.step` | 24.0 x 17.8 x 4.2 | PCB2 U1 | Panjang 24.0 vs footprint 22.5 |
| `gps-gy-neo6mv2.step` | 16.0 x 12.2 x 2.6 | PCB1 U9 | Hanya sebagian modul (semua objeknya solid, sudah dicek), tidak dipakai |
| `ra02-lora.step` | 27.9 x 20.4 x 4.6 | Ra-02 | Belum dicocokkan dengan footprint breakout |
| `esp32-devkit-v1.step` | 28.15 x 51.5 x 15.1 (papan 1.6, pin turun 10.5) | PCB1 U3 | COCOK: 30 pin pitch 2.54, baris 25.4 mm, jarak pin ke pad 0.00 mm (TERBUKTI). USB di ujung pin VIN/3V3 |
| `gps-neo6m.step` | 26.3 x 35.6 x 11.9 (isinya shell, bukan solid) | PCB1 U9 | Papan + chip + header pin 4 titik (pin 8.9 di atas, 3.1 di bawah), TANPA patch antena keramik. Pusat pasangan pin cocok dengan pad (selisih 0.01 mm). Catatan: cek awal gue salah karena hanya menghitung solid |
| `gps-gy-neo6mv2-ant.step` | 35.6 x 26.2 x 12.3 | PCB1 U9 | DIPAKAI di perakitan v8: papan + patch antena 25 x 25 x 4.4, tanpa header pin. Footprint silkscreen 35 x 25 |
| `18650-holder-02b.step` | 77.3 x 21.0 x 22.0 | BT1 (PCB1), H2 (PCB2) | Holder 18650 (cangkang saja, tanpa sel). Pin solder 0.5 x 1.5 mm berjarak **74.3 mm**, padahal pad di PCB1 dan PCB2 berjarak **70.0 mm** dengan lubang 1.1 mm. BELUM COCOK, ukur holder fisik |
| `header-male-1x4.step` | 10.17 x 13.54 x 2.50 | PCB1 U10 | Pin header jantan 1x4 (kabel XKC-Y25-V berujung female) |
| `esp32-final-model.3mf` | 110 x 56 x 28 (satuan file: meter) | bukan U3 | Terlalu besar untuk DevKit (51.5 x 28.2). Kemungkinan casing atau rakitan ESP32 lengkap. 1,08 juta segitiga. Belum dipakai |

Belum ada model: sensor XKC-Y25-V (di luar papan, kabel female ke header jantan U10). Baterai 18650 (BT1) sudah ada di STEP PCB.

## File ini tidak ikut repo
Unduh sendiri dan simpan dengan nama di kolom kiri tabel di atas. Nama file asli unduhan:
`1x4 Male Pin Header.STEP`, `ESP32-C3 supermini v5.step`, `GY-NEO6MV2--3DModel-STEP-740395.STEP`, `NEO-6M.STEP`, `GY-NEO6MV2-withAnt v2.step`, `esp32_dev_kit_v1_asm.stp`,
`MPU_6050.step`, `MT3608 Converter.STEP`, `TP4056_Charging_Module_Type_C.step`, `lora-ra-02-ai-thinker.STEP`,
`18650-battery-and-holder-02b.step`, `esp32-final-model.3mf`.
Sumber situs per file tidak tercatat. Ukur modul fisik sebelum percaya angka di atas.
