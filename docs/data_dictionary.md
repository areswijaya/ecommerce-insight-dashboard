# Data Dictionary & Feature Engineering

Spesifikasi skema `data/clean_orders.csv`, definisi kolom, dan formula metrik bisnis.

---

## 1. Skema Kolom `data/clean_orders.csv`

Dataset bersih terdiri dari **109.872 baris** dan **16 kolom**, mencakup item transaksi pada pesanan berstatus `delivered` selama periode 1 Januari 2017 - 31 Agustus 2018.

| Nama Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `order_id` | `string` | Pengenal unik pada tingkat pesanan. |
| `order_status` | `string` | Status pesanan (seluruh baris bernilai `'delivered'`). |
| `order_purchase_timestamp` | `datetime64[ns]` | Waktu pembelian dibuat oleh pelanggan. |
| `order_delivered_customer_date` | `datetime64[ns]` | Waktu paket diterima oleh pelanggan. |
| `order_estimated_delivery_date` | `datetime64[ns]` | Tanggal estimasi pengiriman yang dijanjikan (tersimpan pukul `00:00:00`). |
| `order_year_month` | `string` | Periode bulan transaksi berformat `YYYY-MM`. |
| `product_id` | `string` | Pengenal unik pada tingkat produk. |
| `product_category_name_english` | `string` | Kategori produk dalam bahasa Inggris (72 kategori aktif; nilai kosong diisi `'others'`). |
| `price` | `float64` | Harga barang dalam Brazilian Real (BRL). |
| `freight_value` | `float64` | Biaya pengiriman item dalam Brazilian Real (BRL). |
| `total_order_value` | `float64` | Total nilai item: $\text{price} + \text{freight\_value}$ (BRL). |
| `actual_delivery_days` | `float64` | Durasi pengiriman riil dari pembelian hingga paket diterima (dalam hari). |
| `estimated_delivery_days` | `float64` | Durasi estimasi pengiriman dari pembelian hingga tanggal janji (dalam hari). |
| `delay_days` | `float64` | Selisih hari kalender antara tanggal terima aktual dan tanggal estimasi. |
| `is_delayed` | `bool` | `True` jika `delay_days > 0`, menandakan pengiriman melewati tanggal kalender estimasi. |
| `review_score` | `float64` | Rata-rata skor ulasan pelanggan per pesanan pada skala 1 hingga 5 bintang. |

---

## 2. Formula Metrik Analitis

### A. Net Realized Revenue
Total nilai barang dan ongkos kirim pada pesanan terkirim:
$$\text{Net Revenue} = \sum (\text{price} + \text{freight\_value})$$

### B. Month-over-Month (MoM) Growth Rate
Laju perubahan pendapatan antar-bulan berurutan:
$$\text{MoM Growth}_t = \left(\frac{\text{Net Revenue}_t - \text{Net Revenue}_{t-1}}{\text{Net Revenue}_{t-1}}\right) \times 100\%$$
Bulan pertama (Januari 2017) berfungsi sebagai baseline netral.

### C. Average Order Value (AOV)
Rata-rata nilai belanja per pesanan unik:
$$\text{AOV} = \frac{\text{Total Net Revenue}}{\text{Jumlah Unik } \text{order\_id}}$$

### D. Distribusi Kumulatif Pareto (80/20)
Kontribusi pendapatan kumulatif hingga kategori peringkat ke-$k$:
$$\text{Cumulative \%}_k = \left(\frac{\sum_{j=1}^k \text{Revenue}_j}{\text{Total Revenue}}\right) \times 100\%$$
Kelompok inti 80% mencakup tepat 18 dari 72 kategori aktif.

### E. Normalisasi Kalender Keterlambatan (SLA)
Karena estimasi Olist tercatat pukul `00:00:00`, kedua timestamp dinormalisasi ke tingkat hari kalender:
$$\text{date\_delivered\_calendar} = \text{floor}(\text{order\_delivered\_customer\_date}, \text{'D'})$$
$$\text{date\_estimated\_calendar} = \text{floor}(\text{order\_estimated\_delivery\_date}, \text{'D'})$$
$$\text{delay\_days} = \frac{\text{date\_delivered\_calendar} - \text{date\_estimated\_calendar}}{86400 \text{ detik}}$$
$$\text{is\_delayed} = \text{delay\_days} > 0$$

### F. Satisfaction Gap
Selisih rata-rata skor ulasan antara pesanan terlambat dan tepat waktu pada level pesanan unik:
$$\text{Satisfaction Gap} = \overline{\text{Review}}_{\text{Delayed}} - \overline{\text{Review}}_{\text{On-Time}}$$
Pada dataset Olist: $2,27 - 4,29 = -2,02 \text{ bintang}$.
