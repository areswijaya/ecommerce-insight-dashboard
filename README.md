# E-Commerce Insight Dashboard: Olist Marketplace

[![Live Demo](https://img.shields.io/badge/Streamlit%20App-Live%20Demo-FF4B4B.svg)](https://ecommerce-insight-areswijaya.streamlit.app/)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Express-3F4F75.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Tests-16%20Passed-brightgreen.svg)](https://pytest.org/)

Analisis data dan dashboard interaktif untuk mengevaluasi 109.872 item transaksi dari 96.203 pesanan terkirim pada dataset publik **Olist Marketplace** Brasil (Januari 2017 - Agustus 2018).

**Live Demo:** [https://ecommerce-insight-areswijaya.streamlit.app/](https://ecommerce-insight-areswijaya.streamlit.app/)

---

## Pertanyaan Bisnis

1. **Dinamika Pendapatan & Musiman:** Bagaimana tren *Net Realized Revenue* dan laju pertumbuhan bulanan (*Month-over-Month Growth %*) selama Januari 2017 - Agustus 2018, serta kapan puncak musiman terjadi?
2. **Konsentrasi Portofolio Produk (Pareto 80/20):** Berapa banyak kategori yang menyumbang 80% pendapatan kumulatif dari 72 kategori aktif, dan bagaimana variasi *Average Order Value* (AOV) antar-kategori?
3. **Logistik vs Kepuasan Pelanggan:** Seberapa kuat hubungan durasi pengiriman serta keterlambatan kalender terhadap skor ulasan pelanggan (1-5 bintang), dan berapa penurunan rating pada pesanan terlambat dibanding tepat waktu?

---

## Temuan Utama & Rekomendasi

| Pilar Analisis | Temuan Kuantitatif | Rekomendasi Bisnis |
| :--- | :--- | :--- |
| **1. Dinamika Penjualan** | - Pendapatan naik >8x dari **BRL 127.482** (Jan 2017) menjadi **BRL 0,97 juta - 1,13 juta** per bulan pada 2018.<br>- Puncak penjualan terjadi pada **November 2017 (Black Friday)** sebesar **BRL 1.153.229 (+53,54% MoM)**.<br>- AOV stabil di kisaran **BRL 160** (rentang bulanan BRL 146,25 - BRL 169,98). | Pertumbuhan pendapatan digerakkan oleh volume pesanan baru, bukan kenaikan harga. Mulai kampanye pra-promo sejak Oktober untuk meratakan lonjakan sebelum Black Friday. |
| **2. Portofolio Kategori** | - **18 dari 72 kategori aktif (25,0%)** menyumbang **80% total pendapatan**.<br>- Tiga kontributor terbesar: `health_beauty` (BRL 1,41 juta), `watches_gifts` (BRL 1,26 juta), dan `bed_bath_table` (BRL 1,22 juta).<br>- `watches_gifts` mencatat AOV tinggi (BRL 229,77), sedangkan `bed_bath_table` memimpin jumlah pesanan (9.267 pesanan). | Prioritaskan ketersediaan stok dan penempatan promosi pada 18 kategori inti. Buat paket *bundling* antara kategori berfrekuensi tinggi dan produk bernilai tinggi. |
| **3. Logistik & Rating** | - Durasi pengiriman berdistribusi miring ke kanan dengan **Mean 12,54 hari** dan **Median 10,21 hari**.<br>- Korelasi negatif antara durasi kirim dan skor ulasan: **Pearson $r = -0,335$**, **Spearman $r_s = -0,235$**.<br>- Pesanan tepat waktu rata-rata meraih **4,29 bintang**, sedangkan pesanan terlambat turun ke **2,27 bintang** (**selisih -2,02 bintang**).<br>- Proporsi ulasan bintang 1 melonjak dari **6,6%** (tepat waktu) menjadi **53,7%** (terlambat). | Tanggal estimasi berfungsi sebagai batas ekspektasi pelanggan. Tambahkan *buffer* 2-3 hari pada rute jarak jauh dan kirim notifikasi proaktif saat terjadi keterlambatan. |

---

## Keputusan Metodologis

1. **Rentang Waktu 20 Bulan Penuh (Jan 2017 - Agu 2018):** Data akhir 2016 (<400 pesanan) dan pasca-Agustus 2018 (<25 pesanan) dikeluarkan agar laju pertumbuhan bulanan tidak terdistorsi oleh sampel parsial.
2. **Median di Samping Mean pada Durasi Kirim:** Pengiriman jarak jauh menciptakan *outlier* hingga >100 hari, sehingga median (10,21 hari) lebih tepat mewakili pengalaman mayoritas pelanggan dibanding mean (12,54 hari).
3. **Normalisasi Tanggal Kalender untuk SLA:** Tanggal estimasi di dataset Olist tersimpan pada pukul `00:00:00`. Membandingkan timestamp mentah membuat 1.291 pesanan yang tiba pada hari estimasi keliru tercatat terlambat. Normalisasi `.dt.floor('D')` menghilangkan bias klasifikasi tersebut.
4. **Pemisahan Granularitas Item vs Pesanan:** Pendapatan dan Pareto kategori dihitung pada level item (109.872 baris). Durasi pengiriman, status keterlambatan, dan skor ulasan dievaluasi pada level `order_id` unik (96.203 pesanan) agar pesanan multi-item tidak mendapat bobot ganda.

---

## Tech Stack

- **Bahasa:** Python 3.10+
- **Pengolahan Data:** `pandas`, `numpy`
- **Visualisasi:** `plotly`, `matplotlib`, `seaborn`
- **Aplikasi Web:** `streamlit`
- **Pengujian:** `pytest`

---

## Struktur Direktori

```
ecommerce-insight-dashboard/
├── .devcontainer/                  # Konfigurasi dev container (GitHub Codespaces)
├── .streamlit/
│   └── config.toml                 # Tema gelap dan opsi server Streamlit
├── dashboard/
│   ├── dashboard.py                # Aplikasi dashboard Streamlit & grafik Plotly
│   └── style.css                   # Styling kartu, layout responsif, & aksesibilitas
├── data/
│   ├── raw/                        # 5 dataset mentah Olist dari Kaggle
│   └── clean_orders.csv            # Dataset bersih (109.872 baris, 16 kolom)
├── docs/
│   ├── architecture.md             # Diagram alur & Architecture Decision Records
│   └── data_dictionary.md          # Skema 16 kolom & formula metrik
├── tests/
│   ├── __init__.py
│   ├── test_data_integrity.py      # 8 uji integritas data & aturan kalender
│   └── test_dashboard_scenarios.py # 8 uji skenario filter dashboard
├── notebook.ipynb                  # Notebook data wrangling & EDA
├── requirements.txt                # Dependensi Python
├── runtime.txt                     # Versi Python untuk deployment
└── url.txt                         # URL live dashboard
```

---

## Menjalankan Proyek Secara Lokal

### 1. Kloning & Instalasi Dependensi
```bash
git clone https://github.com/areswijaya/ecommerce-insight-dashboard.git
cd ecommerce-insight-dashboard

python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### 2. Reproduksi Notebook Analisis
```bash
jupyter notebook notebook.ipynb
```

### 3. Pengujian Otomatis
```bash
pytest -v tests/
```

### 4. Menjalankan Dashboard
```bash
streamlit run dashboard/dashboard.py
```
Aplikasi berjalan di `http://localhost:8501`.

---

## Kredit

- **Pengembang:** Ilfa Antaries Yusuf Wijaya ([contact.areswijaya@gmail.com](mailto:contact.areswijaya@gmail.com))
- **Dataset:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle)
