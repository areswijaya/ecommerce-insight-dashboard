# 🛍️ E-Commerce Insight Dashboard: Olist Marketplace Analysis

[![Live Demo](https://img.shields.io/badge/Streamlit%20App-Live%20Demo-FF4B4B.svg)](https://ecommerce-insight-areswijaya.streamlit.app/)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Express-3F4F75.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Tests-16%20Passed-brightgreen.svg)](https://pytest.org/)

Proyek analisis data komprehensif dan dashboard interaktif yang mengeksplorasi lebih dari 100.000 transaksi riil e-commerce Brasil (**Olist Marketplace**). Proyek ini berfokus pada evaluasi dinamika pertumbuhan komersial, identifikasi konsentrasi portofolio produk menggunakan prinsip Pareto 80/20, serta analisis dampak logistik pengiriman terhadap kepuasan dan retensi pelanggan.

🔗 **Aplikasi Interaktif Langsung (Live Demo):**  
👉 [https://ecommerce-insight-areswijaya.streamlit.app/](https://ecommerce-insight-areswijaya.streamlit.app/)

---

## 📌 Latar Belakang & Masalah Bisnis

Pertumbuhan platform e-commerce bergantung pada keseimbangan antara akuisisi penjualan dan kualitas pemenuhan pesanan (*fulfillment*). Proyek ini dirancang untuk menjawab tiga pertanyaan strategis:

1. **Dinamika Pendapatan Bulanan & Pola Musiman:**  
   Bagaimana pergerakan pendapatan realisasi bulanan (*Net Realized Revenue*) dan laju pertumbuhannya (*Month-over-Month Growth %*) selama periode Januari 2017 hingga Agustus 2018, serta kapan titik puncak penjualan (*peak season*) terjadi?
2. **Portofolio Produk & Konsentrasi Pareto (80/20):**  
   Berapa banyak dan kategori produk mana saja yang menyumbang 80% pendapatan kumulatif dari total 72 kategori aktif, serta bagaimana variasi nilai rata-rata pesanan (*Average Order Value / AOV*) pada kategori-kategori utama tersebut?
3. **Pengaruh Logistik terhadap Kepuasan Pelanggan:**  
   Bagaimana korelasi antara durasi pengiriman riil serta keterlambatan kalender terhadap skor ulasan pelanggan (skala 1-5 bintang), dan seberapa signifikan penurunan kepuasan pada pesanan yang terlambat dibandingkan pesanan tepat waktu?

---

## 💡 Temuan Kunci & Rekomendasi Bisnis

| Pilar Analisis | Temuan Kuantitatif Utama | Implikasi & Rekomendasi Bisnis |
| :--- | :--- | :--- |
| **1. Dinamika Penjualan & Musiman** | - Pendapatan tumbuh >8x lipat dari BRL 127K (Jan 2017) menjadi stabil di kisaran **BRL 1,0M - 1,1M per bulan** pada 2018.<br>- Puncak rekor penjualan terjadi pada **November 2017 (Black Friday)** mencapai **BRL 1.153.229 (+53,54% MoM)**.<br>- Nilai keranjang belanja (AOV) bergerak stabil di kisaran **BRL 160**. | Pertumbuhan omset secara dominan didorong oleh penambahan volume pesanan baru, bukan kenaikan harga rata-rata. Kampanye promosi awal disarankan dimulai sejak Oktober untuk mengantisipasi lonjakan permintaan akhir tahun. |
| **2. Portofolio Produk (Pareto 80/20)** | - Tepat **18 dari 72 kategori aktif (25,0%)** menghasilkan **80% total pendapatan** bisnis.<br>- Tiga kontributor terbesar: `health_beauty` (BRL 1,41M), `watches_gifts` (BRL 1,26M), dan `bed_bath_table` (BRL 1,22M).<br>- `watches_gifts` mencatat AOV tinggi (BRL 229,77), sedangkan `bed_bath_table` merupakan penggerak volume pesanan massal. | Fokuskan alokasi stok dan anggaran pemasaran utama pada 18 kategori inti. Buat program *bundling* strategis antara produk bernilai tinggi dengan produk bervolume tinggi. |
| **3. Logistik vs Kepuasan Pelanggan** | - Durasi pengiriman memiliki kemiringan positif (*right-skewed*) dengan **Mean 12,54 hari** dan **Median 10,21 hari**.<br>- Korelasi negatif signifikan antara waktu kirim dan rating (**Pearson $r = -0,335$**, Spearman $r_s = -0,362$).<br>- **Satisfaction Gap:** Pesanan tepat waktu meraih rata-rata **4,29 ⭐**, sedangkan pesanan terlambat anjlok menjadi **2,27 ⭐** (**penalti kepuasan sebesar -2,02 bintang**).<br>- Proporsi ulasan buruk bintang 1 melonjak drastis dari **6,6%** (tepat waktu) menjadi **53,7%** saat pesanan melewati tanggal estimasi (>8x lipat). | Tanggal estimasi yang dijanjikan bertindak sebagai acuan toleransi psikologis pelanggan. Terapkan *safety buffer* 2-3 hari pada rute jarak jauh dan kirimkan notifikasi kompensasi proaktif sebelum pelanggan mengajukan komplain. |

---

## 🔬 Pendekatan Metodologis & Keputusan Analitis

Analisis ini dibangun dengan disiplin ketelitian data dan statistik terapan:

1. **Pemilihan Rentang Waktu 20 Bulan Stabil (Jan 2017 - Agu 2018):**  
   Data akhir 2016 merupakan fase awal rintisan dengan volume sangat renggang (<400 pesanan), sedangkan data pasca-Agustus 2018 hanya berisi rekam jejak parsial (<25 pesanan). Membatasi sampel pada 20 bulan penuh mencegah bias statistik (*sample bias*) pada metrik pertumbuhan bulanan.
2. **Penggunaan Median di Samping Mean pada Logistik:**  
   Waktu pengiriman memiliki ekor panjang (*long-tail outliers*) hingga >100 hari akibat rute pelosok Brasil. Nilai Median (10,21 hari) mencerminkan pengalaman tipikal mayoritas pelanggan secara lebih akurat daripada Mean (12,54 hari).
3. **Normalisasi Tanggal Kalender untuk SLA Keterlambatan:**  
   Tanggal estimasi pengiriman di dataset Olist tersimpan pada pukul `00:00:00`. Pengurangan langsung antar-*timestamp* menyebabkan 1.292 pesanan yang tiba siang hari pada tanggal yang sama salah dicap terlambat. Normalisasi kalender (`.dt.floor('D')`) mengoreksi bias ini, menghasilkan evaluasi kepuasan pelanggan yang objektif.
4. **Pemisahan Granularitas Item vs Pesanan:**  
   Pendapatan dan performa produk dianalisis pada level item transaksi (109.872 baris). Sementara itu, durasi logistik, ketepatan waktu, dan ulasan dievaluasi pada level pesanan unik (96.203 pesanan) untuk menghindari pembobotan ganda (*duplicate weighting*) pada pesanan bernilai multi-item.
5. **Validasi Empiris Prinsip Pareto 80/20:**  
   Distribusi pendapatan kumulatif dari 72 kategori membuktikan hukum Pareto secara nyata, memisahkan 18 kategori penggerak utama (*core revenue drivers*) dari 54 kategori pelengkap (*long-tail*).

---

## 🛠️ Tech Stack & Pustaka

* **Bahasa:** Python 3.10+
* **Manipulasi & Analisis Data:** `pandas`, `numpy`
* **Visualisasi Data:** `plotly` (Plotly Express & Graph Objects), `matplotlib`, `seaborn`
* **Antarmuka Web Interaktif:** `streamlit`
* **Pengujian Mutu Otomatis (QA):** `pytest`

---

## 📁 Struktur Direktori Proyek

```
ecommerce-insight-dashboard/
├── .devcontainer/                # Konfigurasi container development (GitHub Codespaces)
├── .streamlit/
│   └── config.toml               # Konfigurasi tema visual Streamlit Cloud
│
├── dashboard/
│   ├── dashboard.py              # Logika aplikasi dashboard Streamlit & visualisasi Plotly
│   └── style.css                 # Styling CSS kartu metrik, tema gelap, & tipografi Inter
│
├── data/
│   ├── raw/                      # 5 dataset relasional mentah Olist dari Kaggle
│   └── clean_orders.csv          # Dataset analitis bersih terpadu (16 kolom tervalidasi)
│
├── docs/                         # Dokumentasi teknis & metodologi
│   ├── architecture.md           # Diagram alur sistem & Architecture Decision Records (ADRs)
│   └── data_dictionary.md       # Skema kamus data 16 kolom & formula matematis
│
├── tests/                        # Rangkaian pengujian otomatis (16 unit tests)
│   ├── __init__.py
│   ├── test_data_integrity.py    # 8 pengujian integritas dataset, rentang tanggal, & formula
│   └── test_dashboard_scenarios.py # 8 pengujian ketahanan skenario filter antarmuka
│
├── notebook.ipynb                # Notebook analisis data eksploratif & pipeline pembersihan
├── requirements.txt              # Daftar dependensi pustaka Python
├── runtime.txt                   # Versi Python deployment (python-3.10)
├── url.txt                       # Tautan live interactive dashboard
├── .gitignore                    # Konfigurasi pengabaian file sementara / cache
└── README.md                     # Ringkasan eksekutif & dokumentasi portofolio
```

---

## 🚀 Panduan Menjalankan Proyek Secara Lokal

### 1. Kloning Repositori & Instalasi Lingkungan
```bash
# Kloning repositori
git clone https://github.com/areswijaya/ecommerce-insight-dashboard.git
cd ecommerce-insight-dashboard

# Buat dan aktifkan virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

# Instal seluruh dependensi
pip install -r requirements.txt
```

### 2. Mereproduksi Proses Analisis Data
Buka dan jalankan Jupyter Notebook untuk melihat alur kerja lengkap pembersihan data, eksplorasi statistik, dan pembentukan dataset bersih:
```bash
jupyter notebook notebook.ipynb
```

### 3. Menjalankan Pengujian Otomatis
Verifikasi integritas dataset, formula perhitungan, serta ketahanan filter dashboard menggunakan `pytest`:
```bash
pytest -v tests/
```
*Hasil:* Seluruh 16 pengujian unit lulus (100% *passed*).

### 4. Menjalankan Dashboard Streamlit
Jalankan dashboard interaktif pada browser lokal:
```bash
streamlit run dashboard/dashboard.py
```
Aplikasi akan terbuka otomatis di alamat `http://localhost:8501`.

---

## 👤 Informasi Pengembang & Kredit

* **Pengembang:** **Ilfa Antaries Yusuf Wijaya**
* **Kontak Email:** [contact.areswijaya@gmail.com](mailto:contact.areswijaya@gmail.com)
* **Sumber Dataset:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) yang dipublikasikan secara terbuka di Kaggle.
