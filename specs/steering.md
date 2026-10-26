# SPECIFICATION: Project Steering & Governance Guardrails (Simplified)

**Project:** E-Commerce Insight Dashboard  
**Status:** Approved & Verified (100%)  
**Version:** 2.1.0 (Audited & Synchronized)  
**North Star Reference:** `PROJECT_CONTEXT.md`

---

## 1. Prinsip Kemudi Proyek (Steering Principles)

1. **Defensible & Transparent:** Setiap baris kode dan setiap angka metrik yang ditampilkan harus dapat dijelaskan logika matematisnya secara percaya diri oleh kandidat dalam wawancara kerja.
2. **KISS Principle (Keep It Simple & Solid):** Hindari abstraksi perangkat lunak yang rumit, arsitektur multi-modul yang berlebihan, atau model prediktif yang tidak diminta. Prioritaskan alur data yang bersih: `Raw Data -> notebook.ipynb -> clean_orders.csv -> dashboard.py`.
3. **Mathematical & Statistical Rigor:** Manfaatkan latar belakang Matematika untuk menyajikan analisis statistik yang benar: membedakan Mean dan Median saat data miring (*skewed*), menggunakan persentase perubahan relatif yang presisi, menormalisasi tanggal kalender untuk mengukur SLA, dan menguji korelasi statistik secara objektif pada tingkat entitas yang tepat (level pesanan unik).

---

## 2. Batasan Ruang Lingkup (Scope Boundaries)

### Dalam Lingkup (In-Scope):
- Pembersihan dan penggabungan 5 tabel relasional mentah Olist menjadi 1 dataset terpadu `clean_orders.csv` (109.872 baris dan 16 kolom).
- Pembatasan data pada periode stabil 20 bulan: **1 Januari 2017 s.d. 31 Agustus 2018**.
- Analisis tren pendapatan bulanan, pesanan, dan laju pertumbuhan bulanan (*MoM Growth %*).
- Analisis distribusi kumulatif Pareto 80/20 untuk **72 kategori produk** serta penghitungan AOV.
- Analisis korelasi durasi/keterlambatan pengiriman kalender terhadap skor ulasan dan perbandingan kepuasan *On-time vs Late* pada level pesanan unik.
- Dashboard interaktif Streamlit satu halaman (*single-page executive view*) menggunakan Plotly Express dan Graph Objects dengan tema adaptif bebas bentrok visual.
- Skrip pengujian otomatis `tests/test_data_integrity.py` dengan 8 fungsi spesifik menggunakan `pytest`.
- Dokumentasi `README.md` berstandar portofolio industri.

### Di Luar Lingkup (Out-of-Scope / Anti-Drift):
- Segmentasi pelanggan RFM multi-kuantil yang dipaksakan pada data dengan 97% *one-time buyers*.
- Model Machine Learning prediktif (Time Series Forecasting, Prediksi Churn, NLP Sentimen Ulasan).
- Arsitektur berbasis database server (PostgreSQL/MySQL) atau modul OOP yang rumit.
- Sistem login / multi-user authentication.

---

## 3. Definisi Selesai (Definition of Done - DoD)

| Komponen | Kriteria Definition of Done (DoD) |
| :--- | :--- |
| **Data Wrangling** | - Dataset mentah berhasil dibersihkan dan difilter pada rentang 2017-01 s.d. 2018-08.<br>- Kolom `estimated_delivery_days` terhitung dan keterlambatan dinormalisasi kalender (`.dt.floor('D')`).<br>- File `data/clean_orders.csv` berhasil diekspor dengan 16 kolom tanpa error. |
| **Notebook Analisis** | - Seluruh sel di `notebook.ipynb` dapat dijalankan dari atas ke bawah (*Restart & Run All*) tanpa error.<br>- Terdapat narasi teks penjelas (*Markdown*) di setiap tahapan analisis, memuat penjelasan statistik dan kesimpulan bisnis yang runtut. |
| **Streamlit Dashboard** | - Dashboard dapat dijalankan dengan perintah `streamlit run dashboard/dashboard.py`.<br>- Tampilan visual harmonis pada Dark Mode maupun Light Mode tanpa teks yang tidak terbaca.<br>- Visualisasi Plotly transparan tanpa pemotongan sumbu Y ($l=75\text{ px}$).<br>- Filter tanggal dan toggle kategori cerdas di sidebar merespons secara mulus tanpa ledakan 72 tag chip.<br>- Bagian *Strategic Action Playbook* tampil lengkap dengan rekomendasi terapan. |
| **Testing & QA** | - 8 pengujian otomatis di `tests/test_data_integrity.py` berjalan sukses (100% *pass* via `pytest`). |
| **Dokumentasi** | - `README.md` memuat penjelasan latar belakang bisnis, 3 pertanyaan SMART, temuan analitis utama, badge Python 3.9+, dan panduan instalasi/eksekusi proyek yang jelas. |

---

## 4. Manajemen Risiko & Strategi Mitigasi (Risk Register)

| ID Risiko | Deskripsi Risiko | Dampak | Probabilitas | Rencana Mitigasi |
| :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | **Outliers pada Durasi Pengiriman:** Terdapat pesanan dengan waktu pengiriman sangat lama (>100 hari) akibat kendala geografis pedalaman Brasil. | Sedang | Tinggi | Gunakan nilai **Median** dan rentang interkuartil (**IQR / Boxplot**) di samping Mean untuk menyajikan gambaran waktu pengiriman yang tahan terhadap pencilan (*robust to outliers*), serta batasi sumbu visual boxplot (0–45 hari). |
| **RSK-02** | **Bias Klasifikasi Timestamp pada SLA:** Jam pengiriman aktual di siang hari memicu klasifikasi salah sebagai pesanan terlambat pada tanggal estimasi yang tersimpan jam 00:00:00. | Tinggi | Tinggi | Terapkan **normalisasi tanggal kalender (`.dt.floor('D')`)** sebelum menghitung `delay_days`. |
| **RSK-03** | **Bias Bobot Pesanan Multi-Item:** Pesanan dengan banyak barang mendistorsi perhitungan ulasan dan waktu pengiriman. | Tinggi | Tinggi | Pisahkan komputasi di `dashboard.py`: revenue pada level item, performa logistik dan kepuasan pada level pesanan unik (`drop_duplicates(subset=['order_id'])`). |
| **RSK-04** | **Konflik Tema UI (White-on-White):** Peramban Dark Mode menyebabkan teks putih di atas latar belakang terang menjadi tidak terbaca. | Tinggi | Sedang | Konfigurasi tema terpadu di `.streamlit/config.toml`, hapus hardcoded light background, dan jadikan kanvas grafik Plotly transparan. |

---

## 5. Pedoman Menghadapi Wawancara Kerja (Interview Defense Guide)

Berikut poin-poin kunci yang disiapkan untuk menjawab pertanyaan teknis pewawancara:

1. **"Mengapa Anda memotong data hanya pada tahun 2017 hingga Agustus 2018?"**
   - *Jawaban:* "Saat audit data, saya menemukan bahwa tahun 2016 hanya memiliki kurang dari 400 transaksi karena merupakan fase awal peluncuran. Sementara itu, data setelah Agustus 2018 hanya berisi rekam jejak parsial kurang dari 25 pesanan. Menyertakan bulan yang tidak lengkap akan menimbulkan bias statistik pada laju pertumbuhan bulanan (MoM). Periode 20 bulan ini memberikan sampel yang konsisten dan representatif untuk analisis komersial."
2. **"Mengapa Anda menggunakan Median selain Mean untuk durasi pengiriman?"**
   - *Jawaban:* "Distribusi waktu pengiriman di industri logistik biasanya memiliki kemiringan positif (*right-skewed*) dengan *long-tail outliers* akibat kendala rute di daerah pelosok. Nilai Mean (12,54 hari) sangat sensitif terhadap pencilan tersebut, sedangkan Median (10,21 hari) mencerminkan durasi tipikal yang dialami oleh mayoritas (50%) pelanggan secara lebih akurat."
3. **"Bagaimana Anda menerapkan prinsip Pareto 80/20 pada data ini?"**
   - *Jawaban:* "Saya mengurutkan 72 kategori produk aktif berdasarkan total pendapatan secara menurun, lalu menghitung fungsi distribusi persentase kumulatifnya. Hasilnya membuktikan hukum Pareto secara nyata: tepat 18 kategori teratas (25,0%) menyumbang 80% dari total omset bisnis. Temuan ini membantu tim komersial memprioritaskan stok dan promosi pada 18 kategori inti tanpa membuang anggaran pada 54 kategori ekor panjang (*long-tail*)."
4. **"Mengapa Anda menerapkan normalisasi kalender pada perhitungan keterlambatan pengiriman?"**
   - *Jawaban:* "Di dataset Olist, tanggal estimasi hanya tersimpan pada jam 00:00:00. Jika dikurangkan langsung dengan timestamp pengiriman aktual (misal jam 15:00 di tanggal yang sama), paket tersebut akan memiliki delay +0,62 hari dan dicap terlambat. Normalisasi kalender mengoreksi 1.292 pesanan yang sebenarnya tiba tepat pada hari yang dijanjikan, menghasilkan angka Satisfaction Gap yang jauh lebih akurat: pesanan on-time meraih rating 4,29 ⭐, sedangkan pesanan terlambat anjlok menjadi 2,27 ⭐ (penurunan drastis -2,02 bintang)."
