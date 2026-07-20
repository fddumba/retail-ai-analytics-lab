"""Utilities for validating the Online Retail data quality."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


def check_required_columns(data_frame: pd.DataFrame) -> list[str]:
    """Return a list of missing required columns."""
    return [column_name for column_name in REQUIRED_COLUMNS if column_name not in data_frame.columns]


def summarize_data_quality(data_frame: pd.DataFrame) -> dict[str, object]:
    """Return a simple dictionary summary of data-quality metrics."""
    missing_columns = check_required_columns(data_frame)
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    return {
        "row_count": int(len(data_frame)),
        "missing_customer_id_count": int(data_frame["CustomerID"].isna().sum()),
        "negative_quantity_count": int((data_frame["Quantity"] < 0).sum()),
        "zero_or_negative_unit_price_count": int((data_frame["UnitPrice"] <= 0).sum()),
        "duplicate_row_count": int(data_frame.duplicated().sum()),
        "date_min": data_frame["InvoiceDate"].min(),
        "date_max": data_frame["InvoiceDate"].max(),
    }
