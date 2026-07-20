# BI/Data Engineering Pipeline Overview

## Purpose

This upgrade turns the project from dashboard-only analytics into a reusable data processing pipeline that prepares reliable BI-ready data.

## Pipeline Flow

The pipeline follows this flow:

```text
data/Online Retail.xlsx
→ src/extract.py
→ src/validation.py
→ src/transform.py
→ data/processed/online_retail_clean.csv
→ src/build_marts.py
→ data/marts/*.csv
→ dashboards, SQL, and Power BI
```

## File Responsibilities

- src/config.py centralizes file paths.
- src/extract.py reads the raw Excel workbook.
- src/validation.py checks required columns and summarizes data quality.
- src/transform.py cleans and enriches the data, calculates Revenue, and adds business flags.
- src/build_marts.py creates BI-ready fact, dimension, and summary tables.

## Generated Outputs

The pipeline produces:

- data/processed/online_retail_clean.csv
- data/marts/fact_sales.csv
- data/marts/dim_product.csv
- data/marts/dim_customer.csv
- data/marts/dim_country.csv
- data/marts/dim_date.csv
- data/marts/monthly_sales_summary.csv
- data/marts/country_sales_summary.csv
- data/marts/product_sales_summary.csv

These generated CSV outputs are ignored by Git and can be recreated by running the pipeline.

## How to Run

Run the following commands from the project root:

```bash
python src/transform.py
python src/build_marts.py
```

## Why This Matters

This upgrade demonstrates production-style analytics engineering: reusable code, centralized configuration, validation, clear transformation logic, and BI-ready marts.
