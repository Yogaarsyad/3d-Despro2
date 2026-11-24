## Panduan Visualisasi 3D PCB & Casing (EasyEDA ke FreeCAD)

Dokumentasi ini menjelaskan alur pengambilan model 3D papan sirkuit dari **EasyEDA** dalam format `.step` hingga proses visualisasi, pengukuran dimensi, dan penyimpanan proyek ke dalam format **FreeCAD** (`.FCStd`).

### Struktur Folder
| Folder | Isi |
|---|---|
| `pcb/` | Ekspor STEP terbaru dari EasyEDA (`3D_PCB1_2026-11-24.step`, `3D_PCB2_2026-11-24.step`, `3D_PCB3_2026-11-22.step`) |
| `casing/` | FreeCAD asli casing per papan (`3d-pcb1.FCStd`, `3D-pcb2.FCStd`, `3d-pcb3.FCStd`) |
| `perakitan/` | Casing + PCB baru + blok modul, untuk cek tabrakan (`assembly_PCB1/2_2026-11-24.FCStd`) |
| `modul/` | Model 3D modul dari luar (STEP/3MF), lihat `modul/README.md` untuk ukuran dan status |
| `mekanik/helm/` | Model pihak ketiga untuk helm (sayap helm, klip hard hat), lihat `mekanik/README.md` |
| `mekanik/chest/` | Model pihak ketiga untuk chest strap |
| `laporan/` | Laporan build dan cek tabrakan (tahap 0-5) |
| `skrip/` | Skrip FreeCAD pembangun perakitan dan casing baru |
| `RINGKASAN_3D_2026-11-25.md` | Ringkasan status, parameter, dan masalah terbuka |
| `arsip/` | Berkas lama (STEP 21 Nov, `(3)PANDU_PCB.FCStd`), tidak dipakai lagi |

* **Berkas `.step`**: Model pertukaran CAD 3D standar hasil ekspor langsung dari EasyEDA.
* **Berkas `.FCStd`**: Dokumen asli FreeCAD yang menyimpan objek 3D PCB dan rancangan mekanik *casing*.

---

### Tahap 1: Mengunduh Berkas `.step` dari EasyEDA
1. Buka situs **EasyEDA** melalui peramban dan masuk menggunakan akun yang memiliki akses ke proyek **`Pandu-Capstone-v3-footprint-fix`**.
2. Buka tab **Participated**, pilih proyek tersebut, lalu klik tombol **Open in Editor**.
3. Pada panel **Project Design** di sisi kiri, buka tata letak papan yang ingin diekspor (`PCB1`, `PCB2`, atau `PCB3`).
4. Pastikan satuan kerja sudah dalam milimeter dengan memilih **`mm`** pada menu *dropdown* di bilah alat bagian atas.
5. Klik tombol **`3D`** pada bilah alat atas untuk memastikan seluruh komponen 3D sudah terpasang dengan benar.
6. Klik menu **`Export (R)`** di pojok kiri atas, pilih **`3D File...`**, lalu pilih format **STEP** (`.step`).
7. Simpan berkas hasil unduhan ke dalam folder repositori lokal proyek ini.

---

### Tahap 2: Visualisasi 3D dan Simpan ke `.FCStd` di FreeCAD
1. Buka aplikasi **FreeCAD** (disarankan versi 1.1.4 atau lebih baru).
2. Klik **`Empty File`** pada halaman awal untuk membuat lembar kerja baru.
3. Impor berkas `.step` dengan menekan **`Ctrl + I`** atau melalui menu **`File` > `Import...`**, lalu pilih berkas `.step` yang telah diunduh.
4. Klik ikon **Fit All** (ikon kaca pembesar dengan kotak di bilah alat atas) agar model 3D PCB tampil utuh di tengah layar.
5. Gunakan navigasi tetikus untuk memeriksa model dari berbagai sudut:
   * **Memutar tampilan**: Tahan tombol tengah tetikus sambil menggeser kursor.
   * **Memperbesar/memperkecil**: Gulir roda tetikus ke atas atau ke bawah.
   * **Menggeser posisi**: Tahan tombol tengah tetikus bersamaan dengan tombol `Shift`.
6. **Mengukur Dimensi & Lubang Baut**:
   * Klik ikon **Measure** (jangka sorong) di bilah alat atas.
   * Klik dinding dalam lubang *mounting* untuk melihat diameter lubang dalam satuan `mm`, atau klik dua permukaan berbeda untuk mengukur jarak dan tinggi komponen.
7. Simpan proyek ke format asli FreeCAD dengan menekan **`Ctrl + S`** atau melalui menu **`File` > `Save`**, lalu beri nama berkas dengan ekstensi **`.FCStd`**.

---

### Tahap 3: Membuka Langsung Berkas `.FCStd` dari Repositori
Jika Anda hanya ingin melihat visualisasi 3D tanpa melakukan ekspor ulang dari EasyEDA:
1. Klon atau unduh repositori ini ke komputer lokal Anda.
2. Pastikan perangkat lunak **FreeCAD** sudah terpasang.
3. Klik dua kali langsung pada salah satu berkas proyek seperti `(3)PANDU_PCB.FCStd`, `3d-pcb1.FCStd`, `3D-pcb2.FCStd`, atau `3d-pcb3.FCStd` di File Explorer.
4. Gunakan panel **Model** di sisi kiri layar FreeCAD untuk menyembunyikan atau menampilkan bagian *casing* maupun papan PCB dengan menekan tombol **`Spasi`** pada bagian yang dipilih.
