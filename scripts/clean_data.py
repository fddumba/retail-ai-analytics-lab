"""Create a reusable cleaned copy of the Online Retail dataset.

This script never overwrites the raw workbook. It standardizes data types,
removes exact duplicate rows, and adds transparent quality flags while
preserving returns, cancellations, free items, and missing customer IDs.

Example:
    python scripts/clean_data.py --output data/processed/online_retail_cleaned.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
EXPECTED_COLUMNS = {
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
}


def find_excel_file(data_dir: Path) -> Path:
    """Find the raw workbook, preferring its standard UCI filename."""
    preferred_file = data_dir / "Online Retail.xlsx"
    if preferred_file.exists():
        return preferred_file

    excel_files = sorted(
        file_path
        for pattern in ("*.xlsx", "*.xls")
        for file_path in data_dir.glob(pattern)
        if not file_path.name.startswith("~$")
    )
    if not excel_files:
        raise FileNotFoundError(
            f"No Excel workbook was found in '{data_dir}'. "
            "Place Online Retail.xlsx there and try again."
        )
    if len(excel_files) > 1:
        raise RuntimeError(
            "Multiple Excel workbooks were found. Use --input to choose the raw file."
        )
    return excel_files[0]


def read_workbook(file_path: Path) -> pd.DataFrame:
    """Read Excel with a clear error message and without modifying the source."""
    try:
        return pd.read_excel(file_path, engine="openpyxl")
    except ImportError as error:
        raise RuntimeError(
            "openpyxl is required. Run 'pip install -r requirements.txt' first."
        ) from error
    except PermissionError as error:
        raise RuntimeError(
            f"Permission was denied for '{file_path}'. Close it in Excel and retry."
        ) from error
    except Exception as error:
        raise RuntimeError(
            f"Could not read '{file_path}'. Check that it is a valid, unlocked "
            f"Excel workbook. Original error: {error}"
        ) from error


def clean_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """Apply conservative, documented cleaning rules."""
    missing_columns = EXPECTED_COLUMNS.difference(data.columns)
    if missing_columns:
        names = ", ".join(sorted(missing_columns))
        raise ValueError(f"The workbook is missing expected columns: {names}")

    cleaned = data.copy()

    # Remove exact repeated records, keeping the first occurrence.
    cleaned = cleaned.drop_duplicates().copy()

    # Standardize text while preserving missing values.
    text_columns = ["InvoiceNo", "StockCode", "Description", "Country"]
    for column in text_columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()

    # Use nullable numeric types so invalid or missing values remain visible.
    cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce").astype("Int64")
    cleaned["UnitPrice"] = pd.to_numeric(cleaned["UnitPrice"], errors="coerce")
    cleaned["CustomerID"] = (
        pd.to_numeric(cleaned["CustomerID"], errors="coerce").astype("Int64")
    )
    cleaned["InvoiceDate"] = pd.to_datetime(cleaned["InvoiceDate"], errors="coerce")

    # Revenue is line-level gross value. Negative quantities produce negative revenue.
    cleaned["Revenue"] = cleaned["Quantity"] * cleaned["UnitPrice"]

    # Keep questionable rows and label them instead of silently deleting them.
    cleaned["IsCancellation"] = cleaned["InvoiceNo"].str.upper().str.startswith("C", na=False)
    cleaned["IsNegativeQuantity"] = cleaned["Quantity"] < 0
    cleaned["IsNonPositiveUnitPrice"] = cleaned["UnitPrice"] <= 0
    cleaned["IsMissingCustomerID"] = cleaned["CustomerID"].isna()

    return cleaned


def validate_output_path(source_file: Path, output_file: Path) -> None:
    """Prevent accidental replacement of the raw workbook."""
    if source_file.resolve() == output_file.resolve():
        raise ValueError(
            "The output path points to the raw workbook. Choose a different output "
            "path so the source file is never overwritten."
        )
    if output_file.suffix.lower() not in {".csv", ".parquet"}:
        raise ValueError("The output file must use a .csv or .parquet extension.")


def save_clean_data(data: pd.DataFrame, output_file: Path) -> None:
    """Save CSV or Parquet according to the requested extension."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if output_file.suffix.lower() == ".csv":
        data.to_csv(output_file, index=False)
    else:
        try:
            data.to_parquet(output_file, index=False)
        except ImportError as error:
            raise RuntimeError(
                "Parquet output requires pyarrow. Install pyarrow or choose a .csv output."
            ) from error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        help="Raw Excel path. Defaults to the workbook found in data/.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="New .csv or .parquet path. The raw workbook cannot be used as output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_file = args.input.resolve() if args.input else find_excel_file(DEFAULT_DATA_DIR)
    output_file = args.output.resolve()
    validate_output_path(source_file, output_file)

    raw_data = read_workbook(source_file)
    cleaned_data = clean_dataframe(raw_data)
    save_clean_data(cleaned_data, output_file)

    print(f"Raw rows: {len(raw_data):,}")
    print(f"Cleaned rows: {len(cleaned_data):,}")
    print(f"Exact duplicate rows removed: {len(raw_data) - len(cleaned_data):,}")
    print(f"Cleaned copy created: {output_file}")
    print(f"Raw workbook was not modified: {source_file}")


if __name__ == "__main__":
    main()
