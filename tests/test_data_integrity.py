"""Pemeriksaan integritas data, konsistensi formula, dan kebersihan repositori.

Jalankan dari folder proyek: python -m unittest discover -s tests -v
"""
import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "clean_orders.csv"


def _relative_luminance(hex_color):
    hex_color = hex_color.lstrip("#")
    rgb = [int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(c1, c2):
    l1, l2 = sorted([_relative_luminance(c1), _relative_luminance(c2)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


class DataIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DATA_PATH.exists():
            raise FileNotFoundError(f"Dataset tidak ditemukan: {DATA_PATH}")
        cls.df = pd.read_csv(DATA_PATH)
        cls.df["order_purchase_timestamp"] = pd.to_datetime(cls.df["order_purchase_timestamp"])
        cls.df["order_delivered_customer_date"] = pd.to_datetime(cls.df["order_delivered_customer_date"])
        cls.df["order_estimated_delivery_date"] = pd.to_datetime(cls.df["order_estimated_delivery_date"])

    # Konsistensi data

    def test_clean_dataset_exists_and_row_count(self):
        self.assertEqual(len(self.df), 109872)
        self.assertEqual(len(self.df.columns), 16)

    def test_only_delivered_orders(self):
        self.assertEqual(list(self.df["order_status"].unique()), ["delivered"])

    def test_purchase_date_boundaries(self):
        min_date = self.df["order_purchase_timestamp"].min()
        max_date = self.df["order_purchase_timestamp"].max()
        self.assertGreaterEqual(min_date, pd.Timestamp("2017-01-01"))
        self.assertLessEqual(max_date, pd.Timestamp("2018-08-31 23:59:59"))

    def test_no_critical_missing_values(self):
        critical_cols = [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "product_id",
            "product_category_name_english",
            "price",
            "freight_value",
            "total_order_value",
            "actual_delivery_days",
            "estimated_delivery_days",
            "delay_days",
            "is_delayed",
        ]
        for col in critical_cols:
            self.assertEqual(int(self.df[col].isna().sum()), 0, f"Kolom {col} mengandung nilai kosong")

    def test_total_order_value_calculation(self):
        calc_total = self.df["price"] + self.df["freight_value"]
        diff = np.abs(self.df["total_order_value"] - calc_total)
        self.assertEqual(int((diff > 0.02).sum()), 0)

    def test_non_negative_metrics(self):
        self.assertEqual(int((self.df["price"] <= 0).sum()), 0)
        self.assertEqual(int((self.df["freight_value"] < 0).sum()), 0)
        self.assertEqual(int((self.df["actual_delivery_days"] < 0).sum()), 0)
        self.assertEqual(int((self.df["estimated_delivery_days"] < 0).sum()), 0)

    def test_delay_flag_logic_and_calendar_normalization(self):
        expected_delayed = self.df["delay_days"] > 0
        self.assertTrue((self.df["is_delayed"] == expected_delayed).all())

        # Pengiriman tepat pada tanggal kalender estimasi (delay_days == 0) tidak boleh dicap terlambat.
        same_day = self.df[self.df["delay_days"] == 0]
        self.assertTrue((~same_day["is_delayed"]).all())

    def test_review_score_valid_range_and_correlation(self):
        df_order = self.df.drop_duplicates(subset=["order_id"]).dropna(subset=["review_score"])
        self.assertGreaterEqual(df_order["review_score"].min(), 1.0)
        self.assertLessEqual(df_order["review_score"].max(), 5.0)

        ontime_rating = df_order[~df_order["is_delayed"]]["review_score"].mean()
        late_rating = df_order[df_order["is_delayed"]]["review_score"].mean()
        gap = ontime_rating - late_rating

        self.assertGreater(ontime_rating, 4.20)
        self.assertLess(late_rating, 2.50)
        self.assertGreater(gap, 1.80)

        corr_pearson = df_order["actual_delivery_days"].corr(df_order["review_score"])
        self.assertLess(corr_pearson, -0.30)

    # Kebersihan repositori

    def test_theme_config(self):
        config_text = (BASE_DIR / ".streamlit" / "config.toml").read_text(encoding="utf-8")
        self.assertIn('primaryColor = "#3B82F6"', config_text)

    def test_no_em_or_en_dash(self):
        text_files = [
            BASE_DIR / "dashboard" / "dashboard.py",
            BASE_DIR / "dashboard" / "style.css",
            BASE_DIR / "README.md",
            BASE_DIR / "docs" / "architecture.md",
            BASE_DIR / "docs" / "data_dictionary.md",
            BASE_DIR / "notebook.ipynb",
            BASE_DIR / "tests" / "test_data_integrity.py",
            BASE_DIR / "tests" / "test_dashboard_scenarios.py",
            BASE_DIR / ".devcontainer" / "devcontainer.json",
            BASE_DIR / ".streamlit" / "config.toml",
            BASE_DIR / ".gitignore",
            BASE_DIR / ".gitattributes",
            BASE_DIR / "requirements.txt",
        ]
        for file_path in text_files:
            content = file_path.read_text(encoding="utf-8")
            self.assertNotIn("\u2014", content, f"Em dash ditemukan di {file_path.name}")
            self.assertNotIn("\u2013", content, f"En dash ditemukan di {file_path.name}")

    def test_devcontainer_is_valid_json(self):
        devcontainer_raw = (BASE_DIR / ".devcontainer" / "devcontainer.json").read_text(encoding="utf-8")
        self.assertNotIn("\u2705", devcontainer_raw)
        self.assertIsInstance(json.loads(devcontainer_raw), dict)

    def test_palette_contrast(self):
        text_pairs = [
            ("#F8FAFC", "#0F172A"),
            ("#CBD5E1", "#0F172A"),
            ("#94A3B8", "#0F172A"),
            ("#38BDF8", "#0F172A"),
            ("#F8FAFC", "#1E293B"),
            ("#CBD5E1", "#1E293B"),
            ("#94A3B8", "#1E293B"),
            ("#38BDF8", "#1E293B"),
            ("#34D399", "#1E293B"),
            ("#FFFFFF", "#0369A1"),
        ]
        for fg, bg in text_pairs:
            self.assertGreaterEqual(_contrast_ratio(fg, bg), 4.5, f"Kontras gagal untuk {fg} di atas {bg}")


if __name__ == "__main__":
    unittest.main()
