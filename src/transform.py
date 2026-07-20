"""Clean the raw Online Retail data and save a processed CSV file."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from .config import PROCESSED_CSV_PATH, RAW_EXCEL_PATH
    from .extract import read_raw_data
    from .validation import check_required_columns
except ImportError:  # pragma: no cover - allows direct script execution
    from config import PROCESSED_CSV_PATH, RAW_EXCEL_PATH
    from extract import read_raw_data
    from validation import check_required_columns


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


def clean_online_retail_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Apply basic cleaning rules and add business flags."""
    missing_columns = check_required_columns(raw_data)
    if missing_columns:
        missing_names = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns: {missing_names}")

    cleaned_data = raw_data.copy()
    cleaned_data = cleaned_data.drop_duplicates().copy()

    text_columns = ["InvoiceNo", "StockCode", "Description", "Country"]
    for column_name in text_columns:
        cleaned_data[column_name] = cleaned_data[column_name].astype("string").str.strip()

    cleaned_data["Quantity"] = pd.to_numeric(cleaned_data["Quantity"], errors="coerce").astype("Int64")
    cleaned_data["UnitPrice"] = pd.to_numeric(cleaned_data["UnitPrice"], errors="coerce")
    cleaned_data["CustomerID"] = pd.to_numeric(cleaned_data["CustomerID"], errors="coerce").astype("Int64")
    cleaned_data["InvoiceDate"] = pd.to_datetime(cleaned_data["InvoiceDate"], errors="coerce")

    cleaned_data["Revenue"] = cleaned_data["Quantity"] * cleaned_data["UnitPrice"]

    cleaned_data["is_cancelled_invoice"] = (
        cleaned_data["InvoiceNo"].astype("string").str.upper().str.startswith("C", na=False)
    )
    cleaned_data["is_negative_quantity"] = cleaned_data["Quantity"] < 0
    cleaned_data["is_missing_customer_id"] = cleaned_data["CustomerID"].isna()
    cleaned_data["is_non_positive_unit_price"] = cleaned_data["UnitPrice"] <= 0

    return cleaned_data


def save_processed_data(cleaned_data: pd.DataFrame, output_path: Path | None = None) -> Path:
    """Save the cleaned data to the processed CSV path."""
    destination_path = output_path or PROCESSED_CSV_PATH
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_data.to_csv(destination_path, index=False)
    return destination_path


def main() -> None:
    """Load the raw Excel workbook, clean the data, and save the processed output."""
    raw_data = read_raw_data(RAW_EXCEL_PATH)
    cleaned_data = clean_online_retail_data(raw_data)
    output_path = save_processed_data(cleaned_data)

    print(f"Raw rows loaded: {len(raw_data):,}")
    print(f"Processed rows saved: {len(cleaned_data):,}")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
