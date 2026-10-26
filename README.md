# 🛍️ E-Commerce Insight Dashboard: Olist Marketplace Analysis
[![Live Demo](https://img.shields.io/badge/Streamlit%20App-Live%20Demo-FF4B4B.svg)](https://ecommerce-insights-dashboard-areswidjaja.streamlit.app/)
[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Express-3F4F75.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Tests-16%20Passed-brightgreen.svg)](https://pytest.org/)

Proyek analisis data komprehensif dan dashboard interaktif berbasis data publik transaksi e-commerce Brasil (**Olist Marketplace**) yang mencakup lebih dari 100.000 transaksi. Portofolio ini dirancang khusus untuk peran **Junior / Entry-Level Data Analyst & BI Analyst**, menonjolkan kekuatan logika matematika, ketelitian pembersihan data (*data wrangling*), pemahaman statistik terapan, disiplin rekayasa data (*Spec-Driven Development*), pengujian kualitas data otomatis, serta kemampuan *visual storytelling* yang aplikatif bagi pengambil keputusan bisnis.

🔗 **Tautan Aplikasi Aktif (Live Interactive Dashboard):**  
👉 [https://ecommerce-insights-dashboard-areswidjaja.streamlit.app/](https://ecommerce-insights-dashboard-areswidjaja.streamlit.app/)

---

## 📌 Latar Belakang & Pernyataan Masalah

E-commerce marketplace modern menghadapi tantangan ganda: memacu pertumbuhan omset sekaligus menjaga kepuasan dan retensi pelanggan. Proyek ini menjawab tantangan tersebut dengan menganalisis kinerja penjualan, efisiensi portofolio produk, dan korelasi logistik pengiriman terhadap reputasi platform.

### Tiga Pertanyaan Bisnis SMART:
1. **Dinamika Pendapatan Bulanan & Laju Pertumbuhan (MoM):**  
   *Bagaimana dinamika pendapatan realisasi bulanan (Net Realized Revenue) dan laju pertumbuhannya (Month-over-Month Growth %) selama periode Januari 2017 hingga Agustus 2018, serta kapan titik puncak penjualan (peak season) terjadi?*
2. **Analisis Pareto 80/20 Portofolio Kategori Produk:**  
   *Berapa banyak dan kategori produk mana saja yang menyumbang 80% pendapatan kumulatif (Prinsip Pareto 80/20) dari total 72 kategori produk aktif, serta bagaimana nilai rata-rata pesanan (Average Order Value / AOV) pada kategori-kategori utama tersebut?*
3. **Pengaruh Durasi & Keterlambatan Pengiriman terhadap Kepuasan Pelanggan:**  
   *Bagaimana hubungan korelasi antara durasi pengiriman riil serta keterlambatan pengiriman kalender terhadap skor ulasan pelanggan (review score 1–5) pada level pesanan unik, dan seberapa signifikan penurunan skor kepuasan pada pesanan yang terlambat dibandingkan pesanan tepat waktu?*

---

## 💡 Temuan Kunci (Key Business Findings)

| Pilar Analisis | Temuan Statistik & Kuantitatif | Implikasi Bisnis |
| :--- | :--- | :--- |
| **1. Pertumbuhan Penjualan & Musiman** | - Pendapatan tumbuh >8x lipat dari BRL 127K (Jan 2017) menjadi stabil di kisaran **BRL 1,0M – 1,1M per bulan** pada 2018.<br>- Puncak rekor penjualan terjadi pada **November 2017 (Black Friday)** mencapai **BRL 1.153.229 (+53,54% MoM)**.<br>- Nilai AOV stabil di ~BRL 160 (Rata-rata: BRL 160,63). | Pertumbuhan didorong oleh akuisisi volume pesanan secara luas. Kampanye *pre-sale* harus dimulai sejak Oktober untuk mengkapitalisasi lonjakan Black Friday. |
| **2. Portofolio Produk (Pareto 80/20)** | - Tepat **18 dari 72 kategori produk (25,0%)** menghasilkan **80% total omset** bisnis.<br>- Kategori teratas: `health_beauty` (BRL 1,41M), `watches_gifts` (BRL 1,26M), dan `bed_bath_table` (BRL 1,22M).<br>- `watches_gifts` memiliki AOV tinggi (BRL 229,77), sedangkan `bed_bath_table` adalah *volume driver*. | Alokasikan 80% budget promosi pada 18 kategori inti. Buat paket *bundling* antara produk bernilai tinggi dengan produk bervolume tinggi. |
| **3. Logistik vs Kepuasan Pelanggan** | - Durasi pengiriman memiliki kemiringan (*right-skewed*) dengan **Mean 12,54 hari** dan **Median 10,21 hari**.<br>- Terdapat korelasi negatif signifikan (**Pearson $r = -0,335$**, Spearman $r_s = -0,362$).<br>- **Satisfaction Gap:** Pesanan tepat waktu meraih rating rata-rata **4,29 ⭐**, sedangkan pesanan terlambat kalender anjlok menjadi **2,27 ⭐** (**penurunan drastis -2,02 bintang**).<br>- Lonjakan ulasan buruk bintang 1 melonjak dari **6,6%** (tepat waktu) ke **53,7%** (terlambat) ($>8\times$ lipat). | Batas estimasi pengiriman (SLA) adalah batas toleransi psikologis utama konsumen. Tambahkan *buffer* 2–3 hari pada estimasi rute jauh dan kirimkan notifikasi kompensasi proaktif. |

---

## 🛠️ Tech Stack & Pustaka

- **Bahasa Pemrograman:** Python (3.9+)
- **Manipulasi & Analisis Data:** `pandas`, `numpy`
- **Visualisasi Data:** `plotly` (Plotly Express & Subplots), `matplotlib`, `seaborn`
- **Framework Web Dashboard:** `streamlit`
- **Pengujian Mutu Otomatis (QA & CI):** `pytest`

---

## 📁 Arsitektur Repositori Proyek

Struktur repositori ini memisahkan secara jelas antara **Jalur Demonstrasi Analisis (*Data Science Pipeline*)** dan **Jalur Eksekusi Web (*Web Dashboard Runtime*)**:

```
submission/
├── .streamlit/
│   └── config.toml               # [DEPLOYMENT] Konfigurasi dark mode Streamlit Cloud
│
├── data/
│   ├── raw/                      # [ANALYSIS] 5 dataset mentah relasional yang diproses
│   │   ├── orders_dataset.csv
│   │   ├── order_items_dataset.csv
│   │   ├── order_reviews_dataset.csv
│   │   ├── products_dataset.csv
│   │   └── product_category_name_translation.csv
│   │
│   └── clean_orders.csv          # [RUNTIME] Dataset analitis bersih (16 kolom tervalidasi)
│
├── dashboard/                    # [RUNTIME] Kode antarmuka dashboard interaktif
│   ├── dashboard.py              # Logika aplikasi Streamlit & visualisasi Plotly
│   └── style.css                 # Desain kartu elevated dark, responsif & tipografi Inter
│
├── specs/                        # [SPECIFICATIONS] Dokumentasi Spec-Driven Development (SDD)
│   ├── requirements.md           # Formula matematis, kamus data, & aturan bisnis
│   ├── design.md                 # Arsitektur sistem, pemisahan level data, & ADRs
│   ├── tasks.md                  # Roadmap pengerjaan proyek & status verifikasi
│   └── steering.md               # Batasan ruang lingkup analitis & panduan interview
│
├── tests/                        # [QUALITY ASSURANCE] 16 pengujian otomatis dengan pytest
│   ├── __init__.py
│   ├── test_data_integrity.py    # 8 pengujian integritas data, rentang tanggal, formula
│   └── test_dashboard_scenarios.py # 8 pengujian ketahanan skenario filter dashboard
│
├── notebook.ipynb                # [ANALYSIS] Notebook alur analitis transparan & reproducible
├── requirements.txt              # Daftar dependensi lengkap terkelompok
├── runtime.txt                   # Versi Python cloud (python-3.10)
├── url.txt                       # Tautan aplikasi live demo
├── .gitignore                    # Pengabaian cache Python, venv, & secrets
└── README.md                     # Dokumentasi portofolio ini
```

---

## 🚀 Panduan Menjalankan Proyek Secara Mandiri

### 1. Kloning Repositori & Persiapan Lingkungan
```bash
# Kloning repositori
git clone https://github.com/[username-anda]/ecommerce-insight-dashboard.git
cd ecommerce-insight-dashboard

# Buat dan aktifkan virtual environment (opsional)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux

# Instal dependensi proyek
pip install -r requirements.txt
```

### 2. Mereproduksi Proses Analisis Data (Jupyter Notebook)
Untuk memverifikasi proses pembersihan data dari data mentah (*raw data*) hingga menghasilkan data analitis bersih:
```bash
jupyter notebook notebook.ipynb
```
*Notebook memuat alur lengkap: membaca 5 tabel mentah dari `data/raw/`, normalisasi kalender SLA, deteksi pencilan logistik, analisis Pareto 80/20, uji korelasi statistik, hingga ekspor ke `data/clean_orders.csv`.*

### 3. Menjalankan Rangkaian Pengujian Otomatis (QA Testing)
Verifikasi integritas dataset bersih, formula matematika, dan ketahanan 8 skenario filter antarmuka menggunakan `pytest`:
```bash
pytest -v tests/
```
*Hasil yang diharapkan: 16 pengujian lulus 100% (16 passed).*

### 4. Menjalankan Dashboard Streamlit Interaktif
Jalankan dashboard analitis interaktif secara lokal:
```bash
streamlit run dashboard/dashboard.py
```
Aplikasi akan otomatis terbuka pada peramban lokal di alamat: `http://localhost:8501`.

---

## ☁️ Panduan Deployment ke Streamlit Community Cloud

1. *Push* seluruh isi repositori ini ke cabang `main` pada repositori GitHub Anda.
2. Buka [share.streamlit.io](https://share.streamlit.io/) dan masuk menggunakan akun GitHub Anda.
3. Klik **New app**, lalu tentukan parameter:
   - **Repository:** `[username-anda]/ecommerce-insight-dashboard`
   - **Branch:** `main`
   - **Main file path:** `dashboard/dashboard.py`
4. Klik **Deploy!**. Streamlit Cloud akan membaca `requirements.txt`, `runtime.txt`, dan `.streamlit/config.toml` secara otomatis.

---

## 🎓 Pedoman Pertanggungjawaban Wawancara Kerja (Interview Defense)

1. **Mengapa membatasi rentang data pada 2017 hingga Agustus 2018?**  
   *Data akhir 2016 (<400 pesanan) merupakan masa awal rintisan platform dengan data sangat renggang, sedangkan data setelah Agustus 2018 (<25 pesanan) tidak lengkap. Membatasi sampel pada 20 bulan stabil mencegah bias statistik pada perhitungan laju pertumbuhan bulanan.*
2. **Mengapa menggunakan Median selain Mean pada durasi pengiriman?**  
   *Distribusi waktu pengiriman memiliki kemiringan positif (*right-skewed*) dengan nilai ekstrem mencapai >100 hari pada rute pelosok Brasil. Nilai Median (10,21 hari) lebih tahan terhadap pencilan (*outliers*) dan mencerminkan pengalaman tipikal mayoritas pelanggan dibandingkan Mean (12,54 hari).*
3. **Bagaimana Anda menerapkan prinsip Pareto 80/20 pada data ini?**  
   *Saya mengurutkan 72 kategori produk aktif berdasarkan total pendapatan secara menurun, lalu menghitung fungsi distribusi persentase kumulatifnya. Hasilnya membuktikan hukum Pareto secara nyata: tepat 18 kategori teratas (25,0%) menyumbang 80% dari total omset bisnis.*
4. **Mengapa menerapkan normalisasi tanggal kalender pada keterlambatan pengiriman?**  
   *Di dataset Olist, tanggal estimasi hanya tersimpan pada jam 00:00:00. Pengurangan timestamp langsung menyebabkan 1.292 pesanan yang tiba tepat pada siang hari di tanggal estimasi salah diklasifikasikan terlambat. Normalisasi kalender mengoreksi ini, menghasilkan Satisfaction Gap yang presisi: pesanan on-time meraih rating 4,29 ⭐, sedangkan pesanan terlambat anjlok menjadi 2,27 ⭐ (-2,02 bintang) serta lonjakan ulasan bintang 1 dari 6,6% ke 53,7%.*
5. **Mengapa memisahkan analisis level item dan level pesanan?**  
   *Pendapatan dan performa produk melekat pada level item transaksi ($109.872$ item). Namun, durasi logistik pengiriman dan skor kepuasan ulasan diberikan oleh pelanggan per nomor pesanan ($96.203$ pesanan unik). Jika kepuasan dihitung per item, pesanan multi-item akan terbobot ganda secara tidak adil dan mendistorsi koefisien korelasi riil.*

---

## 👤 Informasi Penulis & Kredit Portofolio
- **Nama Pengembang:** **Ilfa Antaries Yusuf Wijaya**
- **Peran:** Junior Data Analyst Portfolio
- **Latar Belakang:** Lulusan S1 Matematika (*Mathematics Graduate*)
- **Email Kontak:** [contact.areswijaya@gmail.com](mailto:contact.areswijaya@gmail.com)

---

## 📄 Lisensi & Atribusi
Dataset bersumber dari **Brazilian E-Commerce Public Dataset by Olist** yang tersedia secara publik di Kaggle. Proyek dikembangkan sebagai bagian dari portofolio profesional Junior Data Analyst & BI Analyst.
