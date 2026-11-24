"""Pengujian skenario filter dan integrasi antarmuka Streamlit.

Jalankan dari folder proyek: python -m unittest discover -s tests -v
"""
from datetime import date
import unittest
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "clean_orders.csv"


def simulate_pipeline(df_raw, start_date, end_date, selected_categories):
    """Meniru alur penyaringan dan agregasi metrik di dashboard.py."""
    mask_date = (df_raw["order_purchase_timestamp"].dt.date >= start_date) & (
        df_raw["order_purchase_timestamp"].dt.date <= end_date
    )
    mask_cat = df_raw["product_category_name_english"].isin(selected_categories)
    df_filtered = df_raw[mask_date & mask_cat].copy()
    df_orders = df_filtered.drop_duplicates(subset=["order_id"]).copy()

    if df_filtered.empty or df_orders.empty:
        return {"empty": True, "revenue": 0, "orders": 0, "aov": 0}

    total_revenue = df_filtered["total_order_value"].sum()
    total_orders = df_orders["order_id"].nunique()
    aov = total_revenue / total_orders if total_orders > 0 else 0

    cat_agg = (
        df_filtered.groupby("product_category_name_english")
        .agg(total_revenue=("total_order_value", "sum"), total_orders=("order_id", "nunique"))
        .reset_index()
        .sort_values(by="total_revenue", ascending=False)
        .reset_index(drop=True)
    )

    total_cats_count = len(cat_agg)
    top_n = total_cats_count if total_cats_count <= 5 else min(15, total_cats_count)

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
        "corr_spearman": corr_s,
    }


class DashboardScenariosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df_raw = pd.read_csv(DATA_PATH)
        cls.df_raw["order_purchase_timestamp"] = pd.to_datetime(cls.df_raw["order_purchase_timestamp"])
        cls.df_raw["order_delivered_customer_date"] = pd.to_datetime(cls.df_raw["order_delivered_customer_date"])
        cls.df_raw["order_estimated_delivery_date"] = pd.to_datetime(cls.df_raw["order_estimated_delivery_date"])
        cls.df_raw["is_delayed"] = cls.df_raw["is_delayed"].astype(bool)
        cls.all_cats = cls.df_raw["product_category_name_english"].dropna().unique().tolist()
        cls.min_date = cls.df_raw["order_purchase_timestamp"].min().date()
        cls.max_date = cls.df_raw["order_purchase_timestamp"].max().date()

    # Skenario filter dashboard

    def test_scenario_1_all_categories(self):
        res = simulate_pipeline(self.df_raw, self.min_date, self.max_date, self.all_cats)
        self.assertFalse(res["empty"])
        self.assertEqual(res["orders"], 96203)
        self.assertEqual(res["top_n"], 15)
        self.assertIsNotNone(res["gap"])
        self.assertEqual(round(res["gap"], 2), 2.02)

    def test_scenario_2_single_category(self):
        res = simulate_pipeline(self.df_raw, self.min_date, self.max_date, ["health_beauty"])
        self.assertFalse(res["empty"])
        self.assertEqual(res["top_n"], 1)
        self.assertGreater(res["orders"], 0)
        self.assertIsNotNone(res["gap"])

    def test_scenario_3_four_categories(self):
        cats = ["health_beauty", "watches_gifts", "bed_bath_table", "sports_leisure"]
        res = simulate_pipeline(self.df_raw, self.min_date, self.max_date, cats)
        self.assertFalse(res["empty"])
        self.assertEqual(res["top_n"], 4)

    def test_scenario_4_five_categories(self):
        cats = ["health_beauty", "watches_gifts", "bed_bath_table", "sports_leisure", "computers_accessories"]
        res = simulate_pipeline(self.df_raw, self.min_date, self.max_date, cats)
        self.assertFalse(res["empty"])
        self.assertEqual(res["top_n"], 5)

    def test_scenario_5_six_categories(self):
        cats = [
            "health_beauty",
            "watches_gifts",
            "bed_bath_table",
            "sports_leisure",
            "computers_accessories",
            "furniture_decor",
        ]
        res = simulate_pipeline(self.df_raw, self.min_date, self.max_date, cats)
        self.assertFalse(res["empty"])
        self.assertEqual(res["top_n"], 6)

    def test_scenario_6_single_month(self):
        res = simulate_pipeline(self.df_raw, date(2017, 11, 1), date(2017, 11, 30), self.all_cats)
        self.assertFalse(res["empty"])
        self.assertGreater(res["revenue"], 1_000_000)
        self.assertGreater(res["orders"], 7000)

    def test_scenario_7_single_date(self):
        target_d = date(2017, 11, 24)
        res = simulate_pipeline(self.df_raw, target_d, target_d, self.all_cats)
        self.assertFalse(res["empty"])
        self.assertGreater(res["orders"], 0)
        self.assertGreater(res["revenue"], 0)

    def test_scenario_8_empty_selection(self):
        res = simulate_pipeline(self.df_raw, date(2025, 1, 1), date(2025, 1, 2), [])
        self.assertTrue(res["empty"])
        self.assertEqual(res["revenue"], 0)
        self.assertEqual(res["orders"], 0)

    def test_reset_filters_restores_empty_selection(self):
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(str(BASE_DIR / "dashboard" / "dashboard.py"), default_timeout=30).run()
        at.sidebar.checkbox[0].uncheck().run()
        at.sidebar.multiselect[0].set_value([]).run()
        self.assertEqual(len(at.warning), 1)
        at.sidebar.button(key="reset_filters_btn").click().run()
        self.assertEqual(len(at.warning), 0)
        self.assertTrue(at.sidebar.checkbox[0].value)


if __name__ == "__main__":
    unittest.main()
