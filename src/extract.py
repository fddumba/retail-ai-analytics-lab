"""Extract the raw Online Retail workbook into a pandas DataFrame."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from .config import RAW_EXCEL_PATH
except ImportError:  # pragma: no cover - allows direct script execution
    from config import RAW_EXCEL_PATH


def read_raw_data(path: Path | None = None) -> pd.DataFrame:
    """Read the raw Excel workbook and return a DataFrame."""
    source_path = path or RAW_EXCEL_PATH
    if not source_path.exists():
        raise FileNotFoundError(f"Raw Excel file not found: {source_path}")

    return pd.read_excel(source_path, engine="openpyxl")


def main() -> None:
    """Run a quick row and column check for the raw workbook."""
    data_frame = read_raw_data()
    print(f"Loaded {len(data_frame):,} rows and {len(data_frame.columns)} columns.")
    print(data_frame.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
