# Version 1: Basic Dashboard

This folder contains the **Version 1 Basic Dashboard** for the UCI Online
Retail dataset. It is a simple Streamlit application that presents key retail
metrics and trends in a clear, fixed dashboard.

## Purpose

The purpose of Version 1 is to create a beginner-friendly starting point for
retail data analysis. It demonstrates how Python, pandas, and Streamlit can be
used to turn a cleaned transaction dataset into an interactive web dashboard.

This version focuses on straightforward summary metrics and charts. It does
not include user filters, advanced business intelligence features, or an AI
assistant.

## Dataset Used

The dashboard reads:

```text
data/online_retail_clean.csv
```

This is the lightly cleaned working version of the UCI Online Retail dataset.
The original raw file is stored at `data/Online Retail.xlsx` and is not
modified by the dashboard.

Each row represents one product line on an invoice. The dashboard calculates
line-level revenue with:

```text
Revenue = Quantity × UnitPrice
```

## How to Run the Dashboard

Open a terminal in the project root folder and run:

```bash
python -m streamlit run version_1_basic_dashboard/app.py
```

Streamlit will start a local web server and normally open the dashboard in
your browser. If the required packages are not installed, install the project
dependencies first:

```bash
python -m pip install -r requirements.txt
```

## Metrics Shown

The dashboard displays:

- Total revenue
- Number of invoice lines
- Number of unique invoices
- Number of unique customers
- Number of unique products
- Dataset date range

## Charts Shown

The dashboard includes:

- Monthly revenue trend
- Top 10 products by revenue
- Top 10 countries by revenue
- Monthly number of unique invoices

## Important Limitations

This dashboard uses a lightly cleaned dataset. Exact duplicate rows were
removed, but several data-quality and business-definition questions remain:

- Returns and cancellations may still be included.
- Negative quantities may create negative revenue.
- Missing `CustomerID` values remain in the dataset.
- Zero or negative unit prices may still be present.
- Revenue includes negative values and should be interpreted as a basic net
  calculation, not a finalized accounting measure.
- Some stock codes may represent postage, discounts, fees, or adjustments
  instead of standard products.
- December 2011 is incomplete, so monthly comparisons involving that month
  may be misleading.
- The dashboard is fixed and does not provide filters or drill-down analysis.

These limitations are intentionally visible because defining and validating
business rules is an important part of a real analytics project.

## Version 1 Compared with Later Versions

Version 1 is the foundation of the project. It uses Python and Streamlit to
show a fixed set of essential metrics and charts.

Later versions are planned to build on this foundation:

- **Version 2: BI Dashboard** will focus on richer business intelligence,
  filtering, and interactive analysis.
- **Version 3: AI Data Assistant** will allow users to ask questions about the
  data using natural language.
- **Version 4: AI Analysis Agent** will explore more advanced, guided analysis
  workflows and insights.

Those later versions are separate stages of the project and are not included
in this Version 1 dashboard.
