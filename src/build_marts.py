"""Build simple BI-ready data marts from the processed retail dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from .config import MARTS_DIR, PROCESSED_CSV_PATH
except ImportError:  # pragma: no cover - allows direct script execution
    from config import MARTS_DIR, PROCESSED_CSV_PATH


def save_dataframe(data_frame: pd.DataFrame, output_path: Path) -> Path:
    """Persist a DataFrame to disk as a CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data_frame.to_csv(output_path, index=False)
    return output_path


def build_fact_sales(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Create a fact table with transaction-level sales measures."""
    fact_frame = data_frame[
        [
            "InvoiceNo",
            "InvoiceDate",
            "StockCode",
            "Description",
            "CustomerID",
            "Country",
            "Quantity",
            "UnitPrice",
            "Revenue",
            "is_cancelled_invoice",
            "is_negative_quantity",
            "is_missing_customer_id",
            "is_non_positive_unit_price",
        ]
    ].copy()
    fact_frame["InvoiceDate"] = pd.to_datetime(fact_frame["InvoiceDate"], errors="coerce")
    return fact_frame


def build_dim_product(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Create a product dimension from distinct StockCode and Description values."""
    return data_frame[["StockCode", "Description"]].drop_duplicates().reset_index(drop=True)


def build_dim_customer(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Create a customer dimension from distinct customer identifiers."""
    return (
        data_frame[["CustomerID", "Country"]]
        .drop_duplicates()
        .dropna(subset=["CustomerID"])
        .reset_index(drop=True)
    )


def build_dim_country(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Create a country dimension from distinct country values."""
    return data_frame[["Country"]].drop_duplicates().reset_index(drop=True)


def build_dim_date(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Create a date dimension from invoice dates."""
    date_frame = pd.DataFrame({"InvoiceDate": pd.to_datetime(data_frame["InvoiceDate"], errors="coerce")})
    date_frame = date_frame.dropna().drop_duplicates().sort_values("InvoiceDate").reset_index(drop=True)
    date_frame["Year"] = date_frame["InvoiceDate"].dt.year
    date_frame["Month"] = date_frame["InvoiceDate"].dt.month
    date_frame["Day"] = date_frame["InvoiceDate"].dt.day
    return date_frame


def build_monthly_sales_summary(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Create a monthly sales summary for trend analysis."""
    return (
        data_frame.assign(InvoiceMonth=lambda frame: frame["InvoiceDate"].dt.to_period("M"))
        .groupby("InvoiceMonth", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Quantity=("Quantity", "sum"),
            InvoiceCount=("InvoiceNo", "nunique"),
        )
        .sort_values("InvoiceMonth")
        .reset_index(drop=True)
    )


def build_country_sales_summary(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Create a country-level sales summary."""
    return (
        data_frame.groupby("Country", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Quantity=("Quantity", "sum"),
            InvoiceCount=("InvoiceNo", "nunique"),
        )
        .sort_values("Revenue", ascending=False)
        .reset_index(drop=True)
    )


def build_product_sales_summary(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Create a product-level sales summary."""
    return (
        data_frame.groupby(["StockCode", "Description"], as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Quantity=("Quantity", "sum"),
            InvoiceCount=("InvoiceNo", "nunique"),
        )
        .sort_values("Revenue", ascending=False)
        .reset_index(drop=True)
    )


def main() -> None:
    """Load processed data, build marts, and save them to the marts directory."""
    marts_dir = MARTS_DIR
    marts_dir.mkdir(parents=True, exist_ok=True)

    processed_data = pd.read_csv(PROCESSED_CSV_PATH)
    processed_data["InvoiceDate"] = pd.to_datetime(processed_data["InvoiceDate"], errors="coerce")

    outputs = {
        "fact_sales.csv": build_fact_sales(processed_data),
        "dim_product.csv": build_dim_product(processed_data),
        "dim_customer.csv": build_dim_customer(processed_data),
        "dim_country.csv": build_dim_country(processed_data),
        "dim_date.csv": build_dim_date(processed_data),
        "monthly_sales_summary.csv": build_monthly_sales_summary(processed_data),
        "country_sales_summary.csv": build_country_sales_summary(processed_data),
        "product_sales_summary.csv": build_product_sales_summary(processed_data),
    }

    for file_name, frame in outputs.items():
        output_path = save_dataframe(frame, marts_dir / file_name)
        print(f"Saved mart: {output_path}")


if __name__ == "__main__":
    main()
