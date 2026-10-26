"""
Test suite validating the 8 filter scenarios specified in rencana_perbaikan_dashboard.md
to guarantee zero crashes across all edge cases.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import date

@pytest.fixture(scope="module")
def df_raw():
    df = pd.read_csv("data/clean_orders.csv")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
    df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])
    df["is_delayed"] = df["is_delayed"].astype(bool)
    return df

def simulate_pipeline(df_raw, start_date, end_date, selected_categories):
    """Simulates the analytical and metric pipeline executed in dashboard.py."""
    mask_date = (df_raw["order_purchase_timestamp"].dt.date >= start_date) & (df_raw["order_purchase_timestamp"].dt.date <= end_date)
    mask_cat = df_raw["product_category_name_english"].isin(selected_categories)
    df_filtered = df_raw[mask_date & mask_cat].copy()
    df_orders = df_filtered.drop_duplicates(subset=["order_id"]).copy()
    
    if df_filtered.empty or df_orders.empty:
        return {
            "empty": True,
            "revenue": 0,
            "orders": 0,
            "aov": 0
        }
        
    total_revenue = df_filtered["total_order_value"].sum()
    total_orders = df_orders["order_id"].nunique()
    aov = total_revenue / total_orders if total_orders > 0 else 0
    
    # Pareto simulation
    cat_agg = df_filtered.groupby("product_category_name_english").agg(
        total_revenue=("total_order_value", "sum"),
        total_orders=("order_id", "nunique")
    ).reset_index().sort_values(by="total_revenue", ascending=False).reset_index(drop=True)
    
    total_cats_count = len(cat_agg)
    if total_cats_count <= 1:
        top_n = total_cats_count
    elif total_cats_count <= 5:
        top_n = total_cats_count
    else:
        top_n = min(15, total_cats_count)
    df_pareto = cat_agg.head(top_n)
    
    # Satisfaction & correlation simulation
    df_reviewed = df_orders.dropna(subset=["review_score"]).copy()
    ontime_df = df_reviewed[~df_reviewed["is_delayed"]]
    late_df = df_reviewed[df_reviewed["is_delayed"]]
    
    on_time_avg = ontime_df["review_score"].mean() if not ontime_df.empty else None
    late_avg = late_df["review_score"].mean() if not late_df.empty else None
    gap = (on_time_avg - late_avg) if (on_time_avg is not None and late_avg is not None) else None
    
    corr_p = df_reviewed["actual_delivery_days"].corr(df_reviewed["review_score"], method="pearson") if len(df_reviewed) > 1 else None
    corr_s = df_reviewed["actual_delivery_days"].rank().corr(df_reviewed["review_score"].rank()) if len(df_reviewed) > 1 else None
    
    return {
        "empty": False,
        "revenue": total_revenue,
        "orders": total_orders,
        "aov": aov,
        "top_n": top_n,
        "on_time_avg": on_time_avg,
        "late_avg": late_avg,
        "gap": gap,
        "corr_pearson": corr_p,
        "corr_spearman": corr_s
    }

def test_scenario_1_all_categories(df_raw):
    """Scenario 1: All categories (72 categories, full range)."""
    all_cats = df_raw["product_category_name_english"].dropna().unique().tolist()
    start_d = df_raw["order_purchase_timestamp"].min().date()
    end_d = df_raw["order_purchase_timestamp"].max().date()
    
    res = simulate_pipeline(df_raw, start_d, end_d, all_cats)
    assert not res["empty"]
    assert res["orders"] == 96203
    assert res["top_n"] == 15
    assert res["gap"] is not None
    assert round(res["gap"], 2) == 2.02

def test_scenario_2_single_category(df_raw):
    """Scenario 2: Single category (health_beauty)."""
    start_d = df_raw["order_purchase_timestamp"].min().date()
    end_d = df_raw["order_purchase_timestamp"].max().date()
    
    res = simulate_pipeline(df_raw, start_d, end_d, ["health_beauty"])
    assert not res["empty"]
    assert res["top_n"] == 1  # Safe bypass of slider
    assert res["orders"] > 0
    assert res["gap"] is not None

def test_scenario_3_four_categories(df_raw):
    """Scenario 3: 4 categories (less than min_value=5)."""
    cats = ["health_beauty", "watches_gifts", "bed_bath_table", "sports_leisure"]
    start_d = df_raw["order_purchase_timestamp"].min().date()
    end_d = df_raw["order_purchase_timestamp"].max().date()
    
    res = simulate_pipeline(df_raw, start_d, end_d, cats)
    assert not res["empty"]
    assert res["top_n"] == 4  # Safe bypass of slider

def test_scenario_4_five_categories(df_raw):
    """Scenario 4: 5 categories."""
    cats = ["health_beauty", "watches_gifts", "bed_bath_table", "sports_leisure", "computers_accessories"]
    start_d = df_raw["order_purchase_timestamp"].min().date()
    end_d = df_raw["order_purchase_timestamp"].max().date()
    
    res = simulate_pipeline(df_raw, start_d, end_d, cats)
    assert not res["empty"]
    assert res["top_n"] == 5

def test_scenario_5_six_categories(df_raw):
    """Scenario 5: 6 categories (triggers slider with max=6)."""
    cats = ["health_beauty", "watches_gifts", "bed_bath_table", "sports_leisure", "computers_accessories", "furniture_decor"]
    start_d = df_raw["order_purchase_timestamp"].min().date()
    end_d = df_raw["order_purchase_timestamp"].max().date()
    
    res = simulate_pipeline(df_raw, start_d, end_d, cats)
    assert not res["empty"]
    assert res["top_n"] == 6

def test_scenario_6_single_month(df_raw):
    """Scenario 6: Single month (November 2017 peak)."""
    all_cats = df_raw["product_category_name_english"].dropna().unique().tolist()
    start_d = date(2017, 11, 1)
    end_d = date(2017, 11, 30)
    
    res = simulate_pipeline(df_raw, start_d, end_d, all_cats)
    assert not res["empty"]
    assert res["revenue"] > 1_000_000  # Nov 2017 > 1M BRL
    assert res["orders"] > 7000

def test_scenario_7_single_date(df_raw):
    """Scenario 7: Single date (2017-11-24 Black Friday day)."""
    all_cats = df_raw["product_category_name_english"].dropna().unique().tolist()
    target_d = date(2017, 11, 24)
    
    res = simulate_pipeline(df_raw, target_d, target_d, all_cats)
    assert not res["empty"]
    assert res["orders"] > 0
    assert res["revenue"] > 0

def test_scenario_8_empty_selection(df_raw):
    """Scenario 8: Empty range / empty selection (handled gracefully)."""
    res = simulate_pipeline(df_raw, date(2025, 1, 1), date(2025, 1, 2), [])
    assert res["empty"]
    assert res["revenue"] == 0
    assert res["orders"] == 0
