# Model uji cetak

Format: **STL** (satuan mm, skala 100%). Cetak dengan filamen, layer, dan setelan yang sama dengan casing final, rebah seperti posisi bawaan file.
Dibuat oleh `skrip/23_pcb1_v10_final.py` (sudut, lidah) dan `skrip/26_kupon_kalibrasi.py` (`Kal_*`). Titik timbul menandai varian: 1 titik = paling kecil/tipis, 3 titik = paling besar/tebal.

| Urutan | File | Yang diuji | Lulus kalau |
|---|---|---|---|
| 1 | `Kal_1_ukuran_100mm.stl` | penyusutan X dan Y (takik tiap 25 mm) | kedua lengan 100 mm, selisih tidak lebih dari 0.5 mm di penggaris |
| 2 | `Kal_2_lubang_sekrup.stl` | baris dekat titik asal: pilot 2.3/2.5/2.7; tengah: lolos 3.2/3.4/3.6; baris dekat titik: tempat kepala 5.8/6.0/6.2 | di varian 2 titik: sekrup M3 mengulir kencang di pilot tanpa retak, lolos bebas di lubang tengah, kepala ISO 7380 masuk rata |
| 3 | `Kupon_lidah_2.9/3.1/3.3mm.stl` | tebal lidah helm | satu varian masuk slot helm asli dengan ditekan ringan, duri mengait, tidak goyang |
| 4 | `Kal_3_slot_helm_3.3/3.5/3.7.stl` | slot tiruan 30 x 14 mm, untuk uji tanpa helm | lidah 3.1 masuk slot 3.5, duri menonjol di sisi bawah dan menahan saat ditarik |
| 5 | `Kal_4_alur_oring_membran.stl` | alur O-ring 2.4/2.6/2.8 (dalam 1.5) dan lekukan membran 12 x 1.0 | cord 2 mm duduk di alur 2.6, menonjol sekitar 0.5 mm; karet 1 mm rata di lekukan |
| 6 | `Kupon_sudut_dasar.stl` + `Kupon_sudut_tutup.stl` | sudut PCB1 asli: sekrup, alur, tutup rapat | tutup menekan cord merata di sekeliling sudut, sekrup tidak memecahkan plastik |

Kalau hanya varian lain (1 atau 3 titik) yang lulus, laporkan nomornya; ukuran di casing disesuaikan di skrip sebelum cetak final.
