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
    """Verify that clean_orders.csv exists with expected row count (109,872) and 16 columns."""
    assert len(df_clean) == 109872
    assert len(df_clean.columns) == 16

def test_only_delivered_orders(df_clean):
    """Verify that all records strictly represent delivered orders."""
    statuses = df_clean["order_status"].unique()
    assert list(statuses) == ["delivered"]

def test_purchase_date_boundaries(df_clean):
    """Ensure purchase timestamps fall within the 20-month core operational window (2017-01-01 to 2018-08-31)."""
    min_date = df_clean["order_purchase_timestamp"].min()
    max_date = df_clean["order_purchase_timestamp"].max()
    assert min_date >= pd.Timestamp("2017-01-01"), f"Min date {min_date} violates lower boundary 2017-01-01"
    assert max_date <= pd.Timestamp("2018-08-31 23:59:59"), f"Max date {max_date} violates upper boundary 2018-08-31"

def test_no_critical_missing_values(df_clean):
    """Ensure essential analytical and operational columns contain zero null values."""
    critical_cols = [
        "order_id", "order_status", "order_purchase_timestamp",
        "product_id", "product_category_name_english",
        "price", "freight_value", "total_order_value",
        "actual_delivery_days", "estimated_delivery_days",
        "delay_days", "is_delayed"
    ]
    for col in critical_cols:
        null_count = df_clean[col].isna().sum()
        assert null_count == 0, f"Column {col} contains {null_count} unexpected null values!"

def test_total_order_value_calculation(df_clean):
    """Validate arithmetic precision: total_order_value = price + freight_value."""
    calc_total = df_clean["price"] + df_clean["freight_value"]
    diff = np.abs(df_clean["total_order_value"] - calc_total)
    assert (diff > 0.02).sum() == 0, "Inconsistency detected in total_order_value sum!"

def test_non_negative_metrics(df_clean):
    """Verify positive pricing and non-negative freight and delivery durations."""
    assert (df_clean["price"] <= 0).sum() == 0, "Non-positive price detected!"
    assert (df_clean["freight_value"] < 0).sum() == 0, "Negative freight value detected!"
    assert (df_clean["actual_delivery_days"] < 0).sum() == 0, "Negative actual delivery days detected!"
    assert (df_clean["estimated_delivery_days"] < 0).sum() == 0, "Negative estimated delivery days detected!"

def test_delay_flag_logic_and_calendar_normalization(df_clean):
    """Ensure delay boolean flag strictly aligns with calendar date normalization."""
    expected_delayed = df_clean["delay_days"] > 0
    assert (df_clean["is_delayed"] == expected_delayed).all(), "Inconsistency in is_delayed boolean flag!"
    
    # Deliveries on the estimated date itself (delay_days == 0) must not be flagged as delayed
    same_day_deliveries = df_clean[df_clean["delay_days"] == 0]
    assert (~same_day_deliveries["is_delayed"]).all(), "Same-day delivery incorrectly flagged as delayed!"

def test_review_score_valid_range_and_correlation(df_clean):
    """Verify review scores [1, 5], order-level Satisfaction Gap > 1.8, and significant negative correlation."""
    df_order = df_clean.drop_duplicates(subset=["order_id"]).dropna(subset=["review_score"])
    
    assert df_order["review_score"].min() >= 1.0
    assert df_order["review_score"].max() <= 5.0
    
    ontime_rating = df_order[~df_order["is_delayed"]]["review_score"].mean()
    late_rating = df_order[df_order["is_delayed"]]["review_score"].mean()
    gap = ontime_rating - late_rating
    
    assert ontime_rating > 4.20, f"On-time rating ({ontime_rating:.2f}) below expected 4.20"
    assert late_rating < 2.50, f"Delayed rating ({late_rating:.2f}) above expected 2.50"
    assert gap > 1.80, f"Satisfaction gap ({gap:.2f}) less than expected 1.80 stars"
    
    corr_pearson = df_order["actual_delivery_days"].corr(df_order["review_score"])
    assert corr_pearson < -0.30, f"Pearson correlation ({corr_pearson:.3f}) not sufficiently negative"
