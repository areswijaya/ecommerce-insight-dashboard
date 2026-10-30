# 📖 Data Dictionary & Feature Engineering Reference

Dokumentasi teknis skema dataset hasil olahan (`data/clean_orders.csv`), aturan manipulasi data, formula matematis metrik bisnis, dan batas ruang lingkup analisis.

---

## 1. Skema Kolom `data/clean_orders.csv`

Dataset bersih akhir terdiri dari **109.872 baris** dan **16 kolom**, mewakili seluruh item transaksi pada pesanan berstatus `delivered` dalam rentang waktu operasional inti (1 Januari 2017 – 31 Agustus 2018).

| Nama Kolom | Tipe Data | Deskripsi & Penjelasan Teknis |
| :--- | :--- | :--- |
| `order_id` | `string` | ID unik tingkat pesanan (*order level identifier*). |
| `order_status` | `string` | Status pesanan, difilter khusus pada status `'delivered'`. |
| `order_purchase_timestamp` | `datetime64[ns]` | Waktu tepat transaksi pembelian dilakukan oleh pelanggan. |
| `order_delivered_customer_date` | `datetime64[ns]` | Waktu saat paket berhasil diserahkan kepada pelanggan. |
| `order_estimated_delivery_date` | `datetime64[ns]` | Tanggal estimasi pengiriman yang dijanjikan marketplace (*SLA timestamp*). |
| `order_year_month` | `string` | Format periode tahun dan bulan (`YYYY-MM`) untuk agregasi tren bulanan. |
| `product_id` | `string` | ID unik produk (*item level identifier*). |
| `product_category_name_english` | `string` | Nama kategori produk dalam bahasa Inggris (72 kategori aktif; kategori kosong diimputasi sebagai `'others'`). |
| `price` | `float64` | Harga barang dalam Brazilian Real (BRL). |
| `freight_value` | `float64` | Biaya logistik/ongkos kirim barang dalam Brazilian Real (BRL). |
| `total_order_value` | `float64` | Nilai total item: $\text{price} + \text{freight\_value}$ (BRL). |
| `actual_delivery_days` | `float64` | Durasi pengiriman riil: $(\text{order\_delivered\_customer\_date} - \text{order\_purchase\_timestamp})$ dalam hari. |
| `estimated_delivery_days` | `float64` | Estimasi durasi pengiriman: $(\text{order\_estimated\_delivery\_date} - \text{order\_purchase\_timestamp})$ dalam hari. |
| `delay_days` | `float64` | Selisih hari keterlambatan kalender terhadap batas estimasi pengiriman. |
| `is_delayed` | `bool` | Indikator boolean status keterlambatan: `True` jika pesanan tiba melewati tanggal kalender estimasi. |
| `review_score` | `float64` | Skor ulasan kepuasan pelanggan pada rentang skala 1 hingga 5 bintang. |

---

## 2. Definisi Formula Matematis & Analitis

### A. Net Realized Revenue
Dihitung dari total nilai barang dan ongkos kirim pada pesanan yang berhasil terkirim:
$$\text{Net Revenue} = \sum (\text{price} + \text{freight\_value})$$

### B. Month-over-Month (MoM) Growth Rate
Mengukur laju pertumbuhan pendapatan antar-bulan berurutan:
$$\text{MoM Growth}_t = \left(\frac{\text{Net Revenue}_t - \text{Net Revenue}_{t-1}}{\text{Net Revenue}_{t-1}}\right) \times 100\%$$
*Catatan:* Bulan pertama (Januari 2017) berfungsi sebagai baseline periode netral (`0.0%`).

### C. Average Order Value (AOV)
Rata-rata nilai belanja yang dibayarkan per pesanan unik:
$$\text{AOV} = \frac{\text{Total Net Revenue}}{\text{Jumlah Unik } \text{order\_id}}$$

### D. Distribusi Kumulatif Pareto (80/20 Rule)
Untuk menentukan kontribusi pendapatan kumulatif dari urutan kategori produk ke-$k$:
$$\text{Cumulative \%}_k = \left(\frac{\sum_{j=1}^k \text{Revenue}_j}{\text{Total Revenue Keseluruhan}}\right) \times 100\%$$
*Kategori inti (Core 80%):* Kategori-kategori teratas yang secara kumulatif mencapai $\le 80\%$ total omset (tepat 18 dari 72 kategori).

### E. Normalisasi Kalender Keterlambatan Pengiriman (SLA Delivery)
Karena tanggal estimasi di dataset Olist tersimpan pada jam `00:00:00`, perhitungan langsung antar-timestamp menyebabkan pesanan yang tiba siang hari pada tanggal yang sama salah dicap terlambat. Normalisasi kalender diterapkan:
$$\text{date\_delivered\_calendar} = \text{floor}(\text{order\_delivered\_customer\_date}, \text{'D'})$$
$$\text{date\_estimated\_calendar} = \text{floor}(\text{order\_estimated\_delivery\_date}, \text{'D'})$$
$$\text{delay\_days} = \frac{\text{date\_delivered\_calendar} - \text{date\_estimated\_calendar}}{86400 \text{ detik}}$$
$$\text{is\_delayed} = \text{delay\_days} > 0$$

### F. Satisfaction Gap
Selisih rata-rata kepuasan antara pesanan tepat waktu vs terlambat pada tingkat pesanan unik:
$$\text{Satisfaction Gap} = \overline{\text{Review}}_{\text{On-Time}} - \overline{\text{Review}}_{\text{Delayed}}$$
Pada data Olist terbukti: $4,29 - 2,27 = -2,02 \text{ bintang}$.
