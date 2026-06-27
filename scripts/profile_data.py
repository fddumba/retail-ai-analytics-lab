"""Create a beginner-friendly Markdown profile of the Online Retail workbook.

Run from the project root:
    python scripts/profile_data.py

Optional:
    python scripts/profile_data.py --input "data/another_file.xlsx"
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_OUTPUT = PROJECT_ROOT / "context" / "data_profile.md"


def find_excel_file(data_dir: Path) -> Path:
    """Find the Online Retail workbook without changing it."""
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
            f"No Excel file was found in '{data_dir}'. "
            "Place Online Retail.xlsx in the data folder and try again."
        )
    if len(excel_files) > 1:
        names = ", ".join(file_path.name for file_path in excel_files)
        raise RuntimeError(
            f"More than one Excel file was found in '{data_dir}': {names}. "
            "Use --input to select the correct workbook."
        )
    return excel_files[0]


def read_workbook(file_path: Path) -> pd.DataFrame:
    """Read the workbook and provide clear guidance for common errors."""
    try:
        return pd.read_excel(file_path, engine="openpyxl")
    except ImportError as error:
        raise RuntimeError(
            "The workbook could not be read because openpyxl is not installed. "
            "Run 'pip install -r requirements.txt' and try again."
        ) from error
    except PermissionError as error:
        raise RuntimeError(
            f"Permission was denied while reading '{file_path}'. "
            "Close the workbook in Excel and try again."
        ) from error
    except Exception as error:
        raise RuntimeError(
            f"Could not read '{file_path}'. The file may be damaged, locked, "
            f"or not a valid Excel workbook. Original error: {error}"
        ) from error


def display_value(value: object) -> str:
    """Convert a value into safe, readable Markdown text."""
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value).replace("|", r"\|").replace("\n", " ")


def markdown_table(headers: Iterable[object], rows: Iterable[Iterable[object]]) -> str:
    """Build a Markdown table without requiring the optional tabulate package."""
    safe_headers = [display_value(header) for header in headers]
    lines = [
        "| " + " | ".join(safe_headers) + " |",
        "| " + " | ".join("---" for _ in safe_headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(display_value(value) for value in row) + " |")
    return "\n".join(lines)


def display_source_path(source_file: Path) -> str:
    """Prefer a short project-relative path, but support external input files."""
    try:
        return str(source_file.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(source_file.resolve())


def profile_dataframe(data: pd.DataFrame, source_file: Path) -> str:
    """Return the requested data profile as Markdown."""
    missing_rows = [
        (column, int(data[column].isna().sum()), f"{data[column].isna().mean():.2%}")
        for column in data.columns
    ]
    type_rows = [(column, str(dtype)) for column, dtype in data.dtypes.items()]

    date_column = "InvoiceDate"
    parsed_dates = pd.to_datetime(data.get(date_column), errors="coerce")
    valid_dates = parsed_dates.dropna()
    if valid_dates.empty:
        date_min = date_max = "No valid InvoiceDate values found"
    else:
        date_min = valid_dates.min().strftime("%Y-%m-%d %H:%M:%S")
        date_max = valid_dates.max().strftime("%Y-%m-%d %H:%M:%S")

    numeric_data = data.select_dtypes(include="number")
    if numeric_data.empty:
        numeric_table = "No numeric columns were detected."
    else:
        summary = numeric_data.describe().transpose().reset_index()
        summary = summary.rename(columns={"index": "Column"})
        numeric_table = markdown_table(summary.columns, summary.round(2).itertuples(index=False))

    quantity = pd.to_numeric(data.get("Quantity"), errors="coerce")
    unit_price = pd.to_numeric(data.get("UnitPrice"), errors="coerce")
    negative_quantity_count = int((quantity < 0).sum())
    non_positive_price_count = int((unit_price <= 0).sum())
    zero_price_count = int((unit_price == 0).sum())
    negative_price_count = int((unit_price < 0).sum())

    sample = data.head(5)

    source_display = display_source_path(source_file)

    return f"""# Online Retail Data Profile

Generated from the raw workbook. The profiling process reads but does not modify the source file.

## Source

- File: `{source_display}`
- Rows: **{len(data):,}**
- Columns: **{len(data.columns):,}**

## Column Names

{", ".join(f"`{column}`" for column in data.columns)}

## Data Types

{markdown_table(("Column", "Pandas data type"), type_rows)}

## Missing Values

{markdown_table(("Column", "Missing values", "Missing percentage"), missing_rows)}

## Duplicate Rows

- Exact duplicate rows after the first occurrence: **{int(data.duplicated().sum()):,}**

## Date Range

- Earliest `InvoiceDate`: **{date_min}**
- Latest `InvoiceDate`: **{date_max}**

## Sample Rows

{markdown_table(sample.columns, sample.itertuples(index=False, name=None))}

## Numeric Summary

{numeric_table}

## Negative Quantity Rows

- Rows where `Quantity < 0`: **{negative_quantity_count:,}**
- These rows may represent returns, cancellations, corrections, or other adjustments.
  Their business meaning should be confirmed before filtering them out.

## Zero or Negative UnitPrice Rows

- Rows where `UnitPrice <= 0`: **{non_positive_price_count:,}**
- Rows where `UnitPrice == 0`: **{zero_price_count:,}**
- Rows where `UnitPrice < 0`: **{negative_price_count:,}**
- These rows require review before revenue reporting.

## Reproduce This Profile

From the project root, run:

```bash
python scripts/profile_data.py
```
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to the source Excel workbook. Defaults to the workbook in data/.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Markdown output path. Defaults to context/data_profile.md.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_file = args.input.resolve() if args.input else find_excel_file(DEFAULT_DATA_DIR)
    output_file = args.output.resolve()

    data = read_workbook(source_file)
    profile = profile_dataframe(data, source_file)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(profile, encoding="utf-8")
    print(f"Profile created: {output_file}")
    print(f"Source workbook was read only: {source_file}")


if __name__ == "__main__":
    main()
