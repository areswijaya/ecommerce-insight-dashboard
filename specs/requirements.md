# SPECIFICATION: Requirements & Business Logic (Simplified)

**Project:** E-Commerce Insight Dashboard  
**Status:** Approved & Verified (100%)  
**Version:** 2.1.0 (Audited & Synchronized)  
**North Star Reference:** `PROJECT_CONTEXT.md`

---

## 1. Pendahuluan
Dokumen ini mendefinisikan kebutuhan fungsional, non-fungsional, formula matematis, dan kriteria penerimaan untuk portofolio analisis data e-commerce. Seluruh spesifikasi dirancang agar realistis, berfokus pada ketelitian matematika dan statistik deskriptif, serta mudah dipertanggungjawabkan dalam wawancara kerja *Junior Data Analyst*.

---

## 2. Target Pengguna & Konteks Wawancara Kerja
- **Kandidat (Author):** Fresh Graduate Matematika dengan kemampuan analisis data terstruktur, logika kuantitatif kuat, dan komunikasi visual yang lugas.
- **Interviewer / Stakeholder:** Data Lead, Senior Data Analyst, atau Business Manager yang menilai:
  1. Kerapian pembersihan data (*data wrangling discipline*).
  2. Kebenaran kalkulasi matematis/statistik (Mean vs Median, MoM growth %, distribusi Pareto, korelasi).
  3. Pemahaman granularitas data (memisahkan level item transaksi dari level pesanan unik).
  4. Kemampuan mengubah temuan angka menjadi insight bisnis yang berdampak.

---

## 3. Spesifikasi Kebutuhan Fungsional (Functional Requirements)

### FR-01: Data Wrangling & Ekspor Dataset Bersih
- **FR-01.1:** Membaca tabel mentah dari folder `data/`:
  - `orders_dataset.csv`, `order_items_dataset.csv`, `products_dataset.csv`, `product_category_name_translation.csv`, `order_reviews_dataset.csv`.
- **FR-01.2:** Menerapkan filter status dan batas tanggal stabil:
  - Hanya menyertakan pesanan dengan `order_status == 'delivered'`.
  - Rentang tanggal pembelian: `2017-01-01 00:00:00` s.d. `2018-08-31 23:59:59`.
  - Mengeliminasi pesanan tanpa tanggal pengiriman riil (`order_delivered_customer_date` bernilai null).
- **FR-01.3:** Menangani nilai hilang (*missing values*):
  - Kategori produk yang `NaN` diisi dengan label `'others'`, menghasilkan total **72 kategori produk aktif** (71 terjemahan bahasa Inggris + 1 `'others'`).
- **FR-01.4:** Melakukan rekayasa fitur waktu (*feature engineering*):
  - `total_order_value = price + freight_value`.
  - `actual_delivery_days = (order_delivered_customer_date - order_purchase_timestamp).dt.total_seconds() / 86400`.
  - `estimated_delivery_days = (order_estimated_delivery_date - order_purchase_timestamp).dt.total_seconds() / 86400`.
  - **Presisi Keterlambatan Kalender:** Menormalisasi tanggal pengiriman aktual dan tanggal estimasi ke tingkat hari (`.dt.floor('D')`) sebelum menghitung `delay_days`:
    $$\text{delay\_days} = \frac{\text{date\_delivered\_calendar} - \text{date\_estimated\_calendar}}{86400}$$
  - `is_delayed = delay_days > 0` (pesanan yang tiba di siang hari pada tanggal estimasi tetap dihitung tepat waktu / `is_delayed == False`).
  - **Deduplikasi Ulasan:** Mengagregasi rata-rata `review_score` per `order_id` sebelum penggabungan tabel untuk mencegah penggandaan baris.
- **FR-01.5:** Mengekspor hasil gabungan bersih ke file `data/clean_orders.csv` (109.872 baris dan 16 kolom).

### FR-02: Dinamika Pendapatan Bulanan & Laju Pertumbuhan MoM (Pilar 1)
- **FR-02.1:** Menghitung total pendapatan bersih bulanan:
  $$\text{Net Revenue}_t = \sum_{i \in \text{Month}_t} \text{total\_order\_value}_i$$
- **FR-02.2:** Menghitung laju pertumbuhan bulanan (*Month-over-Month Growth Rate*):
  $$\text{MoM Growth}_t = \left(\frac{\text{Net Revenue}_t - \text{Net Revenue}_{t-1}}{\text{Net Revenue}_{t-1}}\right) \times 100\%$$
  *Catatan:* Bulan pertama (Januari 2017) ditangani secara anggun sebagai *Baseline Period* (`0.0%`).
- **FR-02.3:** Menghitung rata-rata nilai pesanan bulanan (*Average Order Value / AOV*):
  $$\text{AOV}_t = \frac{\text{Net Revenue}_t}{\text{Jumlah Unik } \text{order\_id}_t}$$
- **FR-02.4:** Mengidentifikasi pola musiman (*seasonality*) dan lonjakan transaksi tertinggi (Black Friday pada November 2017).

### FR-03: Analisis Pareto 80/20 Portofolio Kategori Produk (Pilar 2)
- **FR-03.1:** Mengagregasi total pendapatan dan total volume transaksi per kategori produk.
- **FR-03.2:** Mengurutkan kategori berdasarkan total pendapatan dari terbesar ke terkecil (*descending*).
- **FR-03.3:** Menghitung persentase kumulatif pendapatan:
  $$\text{Cumulative \%}_k = \left(\frac{\sum_{j=1}^k \text{Revenue}_j}{\text{Total Revenue Keseluruhan}}\right) \times 100\%$$
- **FR-03.4:** Mengelompokkan kategori ke dalam dua segmen berbasis 72 kategori:
  - **Core Categories (Top 80% Revenue):** 18 kategori teratas (25,0%).
  - **Long-tail Categories (Remaining 20%):** 54 kategori pelengkap (75,0%).
- **FR-03.5:** Menghitung AOV per kategori menggunakan `order_id.nunique()`.

### FR-04: Analisis Pengaruh Durasi & Keterlambatan Pengiriman terhadap Kepuasan (Pilar 3)
- **FR-04.1:** Evaluasi metrik dilakukan pada **level pesanan unik** (`df.drop_duplicates(subset=['order_id'])`) untuk mencegah distorsi pembobotan pesanan multi-item.
- **FR-04.2:** Menghitung korelasi statistik Pearson dan Spearman antara:
  - `actual_delivery_days` vs `review_score`
  - `delay_days` vs `review_score`
- **FR-04.3:** Mengukur perbedaan kepuasan antara pesanan tepat waktu vs pesanan terlambat:
  - Rata-rata rating pesanan tepat waktu (*On-time*): ~4,29 ⭐.
  - Rata-rata rating pesanan terlambat (*Delayed*): ~2,27 ⭐.
  - *Satisfaction Gap* ($\Delta \text{Rating} = \text{Score}_{\text{On-time}} - \text{Score}_{\text{Late}} = -2,02 \text{ bintang}$).
- **FR-04.4:** Menganalisis sebaran durasi pengiriman terhadap skor ulasan (1 s.d. 5) menggunakan grafik boxplot dengan penyembunyian pencilan ekstrem (>50 hari).

### FR-05: Streamlit Interactive Dashboard UI
- **FR-05.1:** File mandiri `dashboard/dashboard.py` yang membaca `data/clean_orders.csv` dengan `@st.cache_data`.
- **FR-05.2:** Filter Sidebar Bebas Ledakan Tag:
  - Rentang tanggal interaktif.
  - Checkbox *"Analisis Seluruh Kategori (72 Kategori)"*. Jika dinonaktifkan, barulah widget multiselect muncul untuk memilih kategori tertentu.
- **FR-05.3:** Executive KPI Ribbon (5 Kartu Utama):
  1. **Total Net Revenue (BRL)**
  2. **Total Delivered Orders**
  3. **Average Order Value / AOV (BRL)**
  4. **Average Delivery Time (Hari)** (Delta: Median Delivery Time)
  5. **Average Review Score (Bintang)** (Delta: On-Time Delivery Rate %)
- **FR-05.4:** Visualisasi Plotly Express & Subplots dengan Latar Belakang Transparan:
  - Grafik 1: Tren Pendapatan & Jumlah Order Bulanan (`make_subplots` dual-axis) + Bar MoM Growth %.
  - Grafik 2: Top Kategori & Garis Kumulatif Pareto 80/20 (`make_subplots` dual-axis) + Horizontal Bar AOV.
  - Grafik 3: Perbandingan Rating On-Time vs Late (`px.bar`) + Boxplot Durasi Pengiriman (`px.box`).
- **FR-05.5:** Bagian *Strategic Action Playbook* (Rekomendasi Komersial, Merchandising, dan Logistik).

---

## 4. Kebutuhan Non-Fungsional (Non-Functional Requirements)

- **NFR-01 (Keterbacaan Antarmuka & Aksesibilitas):** Desain dashboard harus kompatibel penuh dengan Dark Mode dan Light Mode (WCAG AAA contrast), tanpa teks yang tak terbaca (*no white-on-white*), dan tanpa pemotongan sumbu grafik Plotly (*automargin=True*, `l=75`).
- **NFR-02 (Performa & Caching):** Dashboard harus memuat data dalam waktu $<2$ detik menggunakan `@st.cache_data`.
- **NFR-03 (Reproducibility):** Seluruh proses pembersihan data dari file mentah hingga `clean_orders.csv` dapat diulang sekuensial di `notebook.ipynb`.
- **NFR-04 (Integritas Data & Pengujian Otomatis):** Wajib memiliki 8 pengujian unit otomatis di `tests/test_data_integrity.py` dengan status 100% *pass*.

---

## 5. Kriteria Penerimaan (Acceptance Criteria)

Pengujian otomatis memvalidasi 8 fungsi pengujian spesifik:
- **AC-01 (`test_clean_dataset_exists_and_row_count`):** File `data/clean_orders.csv` ada dengan 109.872 baris dan 16 kolom.
- **AC-02 (`test_only_delivered_orders`):** Seluruh baris berstatus `delivered`.
- **AC-03 (`test_purchase_date_boundaries`):** Tanggal pesanan berada dalam rentang `2017-01-01` hingga `2018-08-31`.
- **AC-04 (`test_no_critical_missing_values`):** Kolom kunci bebas nilai NaN (termasuk `estimated_delivery_days`).
- **AC-05 (`test_total_order_value_calculation`):** Presisi penjumlahan $\text{total\_order\_value} = \text{price} + \text{freight\_value}$.
- **AC-06 (`test_non_negative_metrics`):** Harga > 0, ongkir >= 0, durasi pengiriman >= 0, estimasi >= 0.
- **AC-07 (`test_delay_flag_logic_and_calendar_normalization`):** Boolean `is_delayed == (delay_days > 0)`, dan pesanan hari yang sama tidak dicap terlambat.
- **AC-08 (`test_review_score_valid_range_and_correlation`):** Skor ulasan dalam rentang [1, 5], order-level Satisfaction Gap > 1,8 bintang, dan korelasi Pearson $r < -0,30$.
