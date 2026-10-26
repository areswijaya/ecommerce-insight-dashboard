# SPECIFICATION: Tasks Breakdown & Implementation Roadmap (Simplified)

**Project:** E-Commerce Insight Dashboard  
**Status:** Completed & Audited (100%)  
**Version:** 2.1.0 (Audited & Synchronized)  
**North Star Reference:** `PROJECT_CONTEXT.md`, `specs/requirements.md`, `specs/design.md`

---

## Ringkasan Roadmap & Milestone

```
[Phase 1] Setup & Environment ─────► [Phase 2] Data Wrangling & Export ─────► [Phase 3] Notebook EDA & Statistik
      [x] COMPLETED (100%)                 [x] COMPLETED (100%)                       [x] COMPLETED (100%)
                                                                                               │
[Phase 5] QA, Testing & Polish ◄──── [Phase 4] Streamlit Dashboard (Plotly) ◄──────────────────┘
      [x] COMPLETED (100%)                 [x] COMPLETED (100%)
```

---

## Phase 1: Setup & Project Environment
Fokus: Menyiapkan dependensi yang lengkap dan memastikan dataset mentah siap diolah.

- [x] **TASK-101:** Perbarui `requirements.txt` dengan pustaka lengkap: `streamlit>=1.38.0`, `pandas>=2.0.0`, `numpy>=1.26.0`, `plotly>=5.18.0`, `matplotlib>=3.8.0`, `seaborn>=0.13.0`, `pytest>=8.0.0`.
- [x] **TASK-102:** Buat folder `tests/` untuk pengujian integritas data.
- [x] **TASK-103:** Konfigurasi `.gitignore` untuk mengabaikan cache Python (`__pycache__/`, `.pytest_cache/`).
- [x] **TASK-104:** Konfigurasi tema gelap terpadu pada `.streamlit/config.toml` untuk mencegah konflik visual.

---

## Phase 2: Data Wrangling & Clean Dataset Generation
Fokus: Menyatukan dan membersihkan dataset mentah di `notebook.ipynb` serta mengekspor `data/clean_orders.csv`.

- [x] **TASK-201:** Tulis tahapan Data Wrangling di `notebook.ipynb`:
  - Membaca tabel: `orders`, `order_items`, `products`, `product_category_name_translation`, `order_reviews`.
  - Filter hanya pesanan berstatus `delivered` pada rentang tanggal: **2017-01-01 s.d. 2018-08-31**.
  - Gabungkan tabel menggunakan fungsi `pd.merge()` yang tepat.
- [x] **TASK-202:** Rekayasa Fitur (*Feature Engineering*):
  - Hitung `total_order_value = price + freight_value`.
  - Hitung `actual_delivery_days` (durasi pengiriman riil dalam hari).
  - Hitung `estimated_delivery_days` (durasi estimasi pengiriman dalam hari).
  - Terapkan **normalisasi tanggal kalender (`.dt.floor('D')`)** untuk menghitung `delay_days` dan flag `is_delayed`.
  - Isi kategori produk `NaN` dengan label `'others'` (total 72 kategori produk aktif).
- [x] **TASK-203:** Ekspor dataframe hasil pembersihan ke file `data/clean_orders.csv` (109.872 baris dan 16 kolom tervalidasi).

---

## Phase 3: Exploratory Data Analysis & Statistical Modeling di Notebook
Fokus: Menyelesaikan analisis 3 pertanyaan bisnis SMART dengan visualisasi yang jelas dan penjelasan naratif di `notebook.ipynb`.

- [x] **TASK-301:** Analisis Pertanyaan 1 (Tren Pendapatan Bulanan & MoM):
  - Agregasi pendapatan dan jumlah pesanan per bulan (`order_year_month`).
  - Hitung laju pertumbuhan bulanan (*MoM Growth %*) dan AOV bulanan (`total_revenue / order_id.nunique()`).
  - Visualisasikan grafik garis tren dengan highlight lonjakan Black Friday November 2017 (BRL 1,15M, +53,5% MoM).
- [x] **TASK-302:** Analisis Pertanyaan 2 (Pareto 80/20 Portofolio Kategori Produk):
  - Agregasi pendapatan per kategori dan urutkan secara *descending*.
  - Hitung persentase kumulatif kontribusi pendapatan dari 72 kategori produk.
  - Identifikasi 18 kategori (25,0%) yang menyumbang 80% pendapatan utama.
  - Visualisasikan grafik Pareto (bar chart kontribusi + garis kumulatif) serta AOV per kategori.
- [x] **TASK-303:** Analisis Pertanyaan 3 (Pengaruh Durasi & Keterlambatan Pengiriman terhadap Kepuasan):
  - Hitung metrik pada level pesanan unik (`df.drop_duplicates(subset=['order_id'])`).
  - Hitung koefisien korelasi statistik antara `actual_delivery_days` vs `review_score` (Pearson $r = -0,335$).
  - Bandingkan rata-rata dan median skor ulasan antara pesanan *On-time* (4,29 ⭐) vs *Late* (2,27 ⭐) (*Satisfaction Gap: -2,02 ⭐*).
  - Visualisasikan distribusi skor ulasan terhadap durasi pengiriman menggunakan boxplot.
- [x] **TASK-304:** Tulis rangkuman *Business Insights & Actionable Recommendations* di akhir notebook.

---

## Phase 4: Streamlit Interactive Dashboard Development
Fokus: Mengembangkan dashboard interaktif yang modern, responsif, dan mudah dibaca di `dashboard/dashboard.py`.

- [x] **TASK-401:** Konfigurasi tata letak halaman dan tema adaptif:
  - Gunakan `st.set_page_config(layout="wide")`.
  - Terapkan styling CSS modern (`dashboard/style.css`) tanpa bentrok warna latar belakang.
- [x] **TASK-402:** Muat data `data/clean_orders.csv` secara efisien dengan caching `@st.cache_data`.
- [x] **TASK-403:** Bangun filter sidebar interaktif cerdas:
  - Rentang waktu dinamis.
  - Mode pilihan seluruh kategori (mencegah ledakan 72 chip tag merah di sidebar).
- [x] **TASK-404:** Bangun **Executive KPI Ribbon** di bagian atas (5 Kartu Utama):
  - Total Net Revenue (BRL)
  - Total Delivered Orders
  - Average Order Value / AOV (BRL)
  - Average Delivery Time (Hari) (Delta: Median Delivery Time)
  - Average Review Score (Bintang) (Delta: On-Time Delivery Rate %)
- [x] **TASK-405:** Bangun **Section 1: Tren Penjualan & Pertumbuhan Bulanan**:
  - Grafik garis ganda `make_subplots` dengan margin memadai ($l=75\text{ px}$) tanpa pemotongan sumbu Y.
  - Anotasi otomatis titik puncak Black Friday Nov 2017.
  - Grafik batang MoM dengan penanganan bulan dasar.
- [x] **TASK-406:** Bangun **Section 2: Analisis Pareto 80/20 Kategori Produk**:
  - Grafik batang Top Kategori Produk dengan kontras Core 80% (18 kategori) vs Long-tail.
  - Grafik batang horizontal AOV per kategori.
- [x] **TASK-407:** Bangun **Section 3: Dampak Pengiriman terhadap Kepuasan Pelanggan**:
  - Dihitung pada level pesanan unik (`df_orders`).
  - Perbandingan rating On-Time (4,29 ⭐) vs Delayed (2,27 ⭐).
  - Boxplot sebaran waktu tempuh pengiriman (0–45 hari).
- [x] **TASK-408:** Tambahkan **Section 4: Strategic Action Playbook** (3 kartu rekomendasi aksi terapan).

---

## Phase 5: Verification, Testing & Portfolio Polish
Fokus: Menjamin keakuratan data, validasi pengujian otomatis, dan dokumentasi akhir.

- [x] **TASK-501:** Kembangkan skrip pengujian otomatis di folder `tests/`:
  - `tests/test_data_integrity.py` (8 pengujian: row count, status delivered, date bounds, null checks, total order value, non-negative, calendar normalization, review score correlation).
  - `tests/test_dashboard_scenarios.py` (8 pengujian skenario filter: all categories, 1, 4, 5, 6 kategori, single month, single date, empty selection).
- [x] **TASK-502:** Jalankan `pytest tests/` dan pastikan 100% *pass* (16 passed in 5.58s).
- [x] **TASK-503:** Uji jalannya dashboard dengan `streamlit run dashboard/dashboard.py` dan pastikan server aktif tanpa error di `http://localhost:8502`.
- [x] **TASK-504:** Perbarui `README.md` secara profesional (Latar belakang, 3 Pertanyaan SMART, metodologi, temuan utama, panduan instalasi/eksekusi, badge Python 3.9+, dan pedoman wawancara kerja).
