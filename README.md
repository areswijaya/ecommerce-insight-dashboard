# E-Commerce Insight Dashboard

[![Streamlit App](https://img.shields.io/badge/Streamlit_App-Live_Demo-FF4B4B?style=flat)](https://ecommerce-insight-areswijaya.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat)
![Plotly](https://img.shields.io/badge/Plotly-Dashboard-3F4F75?style=flat)

Proyek analisis data dan dashboard interaktif pada 109,872 item transaksi (96,203 pesanan terkirim) dari dataset publik Olist Marketplace Brasil (Januari 2017 - Agustus 2018).

> **English summary:** End-to-end e-commerce analytics project and interactive Streamlit dashboard covering 109,872 line items across 96,203 delivered orders from the Brazilian Olist Marketplace dataset (Jan 2017 - Aug 2018). It examines monthly revenue and MoM growth dynamics, 80/20 Pareto product category concentration across 72 categories, and the effect of calendar-normalized delivery delays on customer review ratings.

## Metode

1. **Pembersihan data**: saring 5 tabel relasional mentah (`data/raw/`) untuk pesanan berstatus `delivered` pada rentang 20 bulan penuh (1 Jan 2017 - 31 Agu 2018) menjadi 109,872 baris item (96,203 `order_id` unik), terjemahkan nama kategori ke bahasa Inggris (nilai kosong diisi `'others'`), dan rata-ratakan `review_score` per `order_id`.
2. **Dinamika pendapatan & AOV**: hitung nilai item `total_order_value = price + freight_value`, laju pertumbuhan bulanan (*Month-over-Month* / MoM), dan *Average Order Value* (`AOV = Total Pendapatan / Jumlah order_id unik`).
3. **Analisis Pareto 80/20 kategori**: urutkan 72 kategori aktif berdasarkan kontribusi pendapatan kumulatif untuk memisahkan penggerak utama (80% omset) dari kategori ekor panjang.
4. **Normalisasi kalender SLA & pemisahan granularitas**: normalkan `order_delivered_customer_date` dan `order_estimated_delivery_date` ke tingkat hari (`.dt.floor('D')`) karena batas estimasi Olist tercatat pukul `00:00:00`. Evaluasi durasi kirim dan skor ulasan dijalankan pada level `order_id` unik agar pesanan multi-item tidak mendapat bobot ganda.
5. **Dashboard Streamlit (`dashboard/dashboard.py`)**: 5 bagian analitis dengan filter periode dan kategori di sidebar (`Reset Filter`), visualisasi Plotly interaktif, tabel ringkasan, dan ekspor CSV.

## Temuan Utama

### Tren penjualan & musiman

- Pendapatan bulanan naik lebih dari 8 kali lipat dari `127,482.37` BRL (Januari 2017) menjadi `966,168.41` - `1,132,878.93` BRL per bulan pada 2018 (total `15,371,741.09` BRL selama 20 bulan).
- Puncak penjualan terjadi pada November 2017 (Black Friday) sebesar `1,153,229.37` BRL (`+53.54%` MoM), disusul penurunan `-26.89%` pada Desember 2017.
- AOV bulanan stabil di rentang `146.25` - `169.98` BRL (rata-rata keseluruhan `159.78` BRL), menunjukkan pertumbuhan pendapatan didorong peningkatan jumlah pesanan, bukan kenaikan harga rata-rata.

### Konsentrasi kategori Pareto 80/20

- Tepat `18` dari `72` kategori aktif (`25.0%`) menyumbang `80%` total pendapatan, sementara `54` kategori lainnya berada di ekor panjang.
- Tiga penyumbang terbesar: `health_beauty` (`1,407,759.78` BRL, `9.16%`, AOV `163.50` BRL), `watches_gifts` (`1,261,223.27` BRL, `8.20%`, AOV `229.77` BRL), dan `bed_bath_table` (`1,224,602.68` BRL, `7.97%`, AOV `132.15` BRL dari `9,267` pesanan).

### Logistik & kepuasan pelanggan

| Metrik (96,203 pesanan unik; 95,560 berulas) | Nilai |
|---|---|
| Rata-rata / Median durasi kirim (96,203 pesanan) | `12.54` hari / `10.21` hari |
| Rata-rata / Median durasi kirim (95,560 pesanan berulas) | `12.50` hari / `10.20` hari |
| Korelasi durasi vs rating (Pearson / Spearman) | `-0.335` / `-0.235` |
| Rata-rata rating tepat waktu vs terlambat | `4.29` (median `5.0`) vs `2.27` (median `1.0`), selisih `-2.02` bintang |
| Proporsi ulasan bintang 1 (tepat waktu vs terlambat) | `6.6%` vs `53.7%` |
| Koreksi salah klasifikasi lewat normalisasi `.dt.floor('D')` | `1,291` pesanan (dari `7,822` menjadi `6,531` pesanan terlambat) |

## Keterbatasan

- **Hanya pesanan terkirim dalam rentang stabil**: data akhir 2016 (`< 400` pesanan), pasca-Agustus 2018 (`< 25` pesanan), serta status non-`delivered` dikeluarkan untuk menjaga konsistensi tren bulanan dan evaluasi pengiriman.
- **Tanpa identitas pelanggan lintas transaksi**: file `customers_dataset.csv` (`customer_unique_id`) tidak tersedia di `data/raw/`, sedangkan `customer_id` pada `orders_dataset.csv` bernilai unik 1:1 per pesanan, sehingga analisis retensi dan RFM tidak diterapkan.
- **Nilai kotor transaksi**: `total_order_value` menjumlahkan `price + freight_value` tanpa data HPP, margin keuntungan, atau potongan voucher.
- **Pesanan multi-kategori**: sebanyak `778` dari `96,203` pesanan memuat item dari lebih dari satu kategori; jumlah pesanan per kategori dihitung per masing-masing kategori (`nunique(order_id)`).

## Struktur Proyek

```text
ecommerce-insight-dashboard/
├── .devcontainer/
│   └── devcontainer.json
├── .streamlit/
│   └── config.toml
├── dashboard/
│   ├── dashboard.py
│   └── style.css
├── data/
│   ├── raw/
│   └── clean_orders.csv
├── docs/
│   ├── architecture.md
│   └── data_dictionary.md
├── tests/
│   ├── __init__.py
│   ├── test_dashboard_scenarios.py
│   └── test_data_integrity.py
├── notebook.ipynb
├── requirements.txt
├── runtime.txt
├── url.txt
├── .gitattributes
├── .gitignore
└── README.md
```

## Cara Menjalankan

```bash
pip install -r requirements.txt
python -m streamlit run dashboard/dashboard.py
```

Aplikasi terbuka di `http://localhost:8501`.

Untuk memproses ulang `data/clean_orders.csv` dari data mentah, jalankan seluruh sel `notebook.ipynb`. Untuk menjalankan rangkaian uji integritas data, skenario filter dashboard, dan kebersihan repositori:

```bash
python -m unittest discover -s tests -v
```

## Kontak

Ilfa Antaries Yusuf Wijaya
- Email: contact.areswijaya@gmail.com
- LinkedIn: [linkedin.com/in/areswijaya](https://www.linkedin.com/in/areswijaya)
- GitHub: [github.com/areswijaya](https://github.com/areswijaya)
