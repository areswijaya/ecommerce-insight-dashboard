# tests/test_data_integrity.py
"""
Unit tests and data integrity validation for E-Commerce Insight Dashboard.
Validates clean dataset structure, mathematical formulas, and statistical logic
reflecting calendar normalization and order-level granularity.
"""
import os
import pytest
import pandas as pd
import numpy as np

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "clean_orders.csv")

@pytest.fixture(scope="module")
def df_clean():
    assert os.path.exists(DATA_PATH), f"Dataset {DATA_PATH} not found!"
    df = pd.read_csv(DATA_PATH)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
    df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])
    return df

def test_clean_dataset_exists_and_row_count(df_clean):
    """1. Memastikan file data/clean_orders.csv ada dengan 109.872 baris dan 16 kolom."""
    assert len(df_clean) == 109872
    assert len(df_clean.columns) == 16

def test_only_delivered_orders(df_clean):
    """2. Memastikan seluruh baris hanya berstatus delivered (FR-01.2)."""
    statuses = df_clean["order_status"].unique()
    assert list(statuses) == ["delivered"]

def test_purchase_date_boundaries(df_clean):
    """3. Memastikan seluruh transaksi berada dalam rentang 2017-01-01 s.d. 2018-08-31 (FR-01.2)."""
    min_date = df_clean["order_purchase_timestamp"].min()
    max_date = df_clean["order_purchase_timestamp"].max()
    assert min_date >= pd.Timestamp("2017-01-01"), f"Min date {min_date} melanggar batas bawah 2017-01-01"
    assert max_date <= pd.Timestamp("2018-08-31 23:59:59"), f"Max date {max_date} melanggar batas atas 2018-08-31"

def test_no_critical_missing_values(df_clean):
    """4. Memastikan kolom krusial bebas dari nilai NaN (FR-01.3 & FR-01.4)."""
    critical_cols = [
        "order_id", "order_status", "order_purchase_timestamp",
        "product_id", "product_category_name_english",
        "price", "freight_value", "total_order_value",
        "actual_delivery_days", "estimated_delivery_days",
        "delay_days", "is_delayed"
    ]
    for col in critical_cols:
        null_count = df_clean[col].isna().sum()
        assert null_count == 0, f"Kolom {col} memiliki {null_count} nilai null!"

def test_total_order_value_calculation(df_clean):
    """5. Memvalidasi presisi matematis total_order_value = price + freight_value (FR-01.4)."""
    calc_total = df_clean["price"] + df_clean["freight_value"]
    diff = np.abs(df_clean["total_order_value"] - calc_total)
    assert (diff > 0.02).sum() == 0, "Ditemukan ketidakkonsistenan penjumlahan harga dan ongkos kirim!"

def test_non_negative_metrics(df_clean):
    """6. Memastikan price > 0, freight_value >= 0, dan durasi pengiriman >= 0 (AC-01)."""
    assert (df_clean["price"] <= 0).sum() == 0, "Ditemukan harga bernilai non-positif!"
    assert (df_clean["freight_value"] < 0).sum() == 0, "Ditemukan ongkir negatif!"
    assert (df_clean["actual_delivery_days"] < 0).sum() == 0, "Ditemukan durasi pengiriman riil negatif!"
    assert (df_clean["estimated_delivery_days"] < 0).sum() == 0, "Ditemukan estimasi pengiriman negatif!"

def test_delay_flag_logic_and_calendar_normalization(df_clean):
    """7. Memastikan konsistensi boolean is_delayed == (delay_days > 0) dengan normalisasi kalender (FR-01.4)."""
    # Pastikan is_delayed konsisten dengan delay_days > 0
    expected_delayed = df_clean["delay_days"] > 0
    assert (df_clean["is_delayed"] == expected_delayed).all(), "Ketidakkonsistenan boolean flag is_delayed!"
    
    # Verifikasi bahwa pesanan di hari estimasi yang sama (delay_days == 0) TIDAK dicap terlambat
    same_day_deliveries = df_clean[df_clean["delay_days"] == 0]
    assert (~same_day_deliveries["is_delayed"]).all(), "Pesanan hari yang sama salah dicap terlambat!"

def test_review_score_valid_range_and_correlation(df_clean):
    """8. Memastikan rentang skor ulasan [1, 5], order-level Satisfaction Gap > 1.8, dan korelasi r < -0.30 (AC-02)."""
    # Evaluasi pada level pesanan unik untuk menghindari bias multi-item
    df_order = df_clean.drop_duplicates(subset=["order_id"]).dropna(subset=["review_score"])
    
    assert df_order["review_score"].min() >= 1.0
    assert df_order["review_score"].max() <= 5.0
    
    ontime_rating = df_order[~df_order["is_delayed"]]["review_score"].mean()
    late_rating = df_order[df_order["is_delayed"]]["review_score"].mean()
    gap = ontime_rating - late_rating
    
    assert ontime_rating > 4.20, f"Rata-rata rating on-time ({ontime_rating:.2f}) di bawah 4.20"
    assert late_rating < 2.50, f"Rata-rata rating late ({late_rating:.2f}) di atas 2.50"
    assert gap > 1.80, f"Satisfaction gap ({gap:.2f}) kurang dari 1.80 bintang"
    
    corr_pearson = df_order["actual_delivery_days"].corr(df_order["review_score"])
    assert corr_pearson < -0.30, f"Korelasi Pearson ({corr_pearson:.3f}) tidak negatif signifikan"
