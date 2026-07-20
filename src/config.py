"""Project paths for the retail analytics pipeline."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_EXCEL_PATH = DATA_DIR / "Online Retail.xlsx"
PROCESSED_CSV_PATH = DATA_DIR / "processed" / "online_retail_clean.csv"
MARTS_DIR = DATA_DIR / "marts"
