# Version 2: Business Intelligence Dashboard

This folder contains the **Version 2 Business Intelligence Dashboard** for the
UCI Online Retail dataset.

Version 2 builds on the basic dashboard from Version 1 by adding interactive
filters, more KPIs, more charts, a filtered data preview, and a download option
for the filtered dataset.

## Purpose of This Version

The purpose of Version 2 is to turn the cleaned online retail data into a more
interactive business intelligence dashboard.

Instead of only viewing fixed summary charts, users can now explore the data by
changing filters in the sidebar. This makes it easier to answer practical
business questions such as:

- Which countries generate the most revenue?
- Which products are the top revenue drivers?
- How does revenue change over time?
- How many invoices appear in each month?
- How much of the data includes returns or negative quantities?
- How do missing customers, returns, and unusual prices affect the analysis?

This version is still beginner-friendly and uses Python, pandas, Plotly, and
Streamlit.

## Dataset Used

The dashboard reads this cleaned CSV file:

```text
data/online_retail_clean.csv
```

This file is based on the UCI Online Retail dataset. Each row represents one
invoice line, meaning one product entry on one invoice.

The dashboard creates or recalculates a revenue column using:

```text
Revenue = Quantity * UnitPrice
```

The raw Excel file is not modified by this dashboard.

## How to Run the Dashboard

Open a terminal from the project root folder and run:

```bash
python -m streamlit run version_2_bi_dashboard/app.py
```

If the required packages are not installed yet, install them first with:

```bash
python -m pip install -r requirements.txt
```

Streamlit will start a local web app and usually open it in your browser
automatically.

## Main BI Features

Version 2 includes:

- Interactive sidebar filters
- Filtered KPI cards
- Revenue and invoice trend charts
- Country and product revenue breakdowns
- Revenue vs quantity comparison
- Return and negative quantity summary
- Filtered data preview table
- Download button for the filtered data
- Notes explaining important business-rule limitations

## Sidebar Filters

The sidebar lets users filter the dataset by:

- Date range
- Country
- Product description search
- Whether to include or exclude negative `Quantity` rows
- Whether to include or exclude zero or negative `UnitPrice` rows
- Whether to include or exclude rows with missing `CustomerID`

These filters help users explore how different business rules change the
dashboard results.

## KPIs Shown

The dashboard shows these filtered KPIs:

- Total revenue
- Invoice lines
- Unique invoices
- Unique customers
- Unique products
- Average order value
- Units sold
- Units returned or negative quantity total

The KPI values change whenever the sidebar filters are updated.

## Charts Shown

The dashboard includes:

- Monthly revenue trend
- Revenue by country
- Top 10 products by revenue
- Monthly number of invoices
- Revenue vs quantity by country or product
- Return / negative quantity summary

These charts are intended for business intelligence exploration, not final
accounting reporting.

## Download Filtered Data

After applying filters, users can preview the filtered rows in the dashboard.

The dashboard also includes a download button that exports the filtered data as
a CSV file. This is useful for saving a subset of the data for additional
analysis or review.

## Important Limitations

This dashboard depends on the current cleaned CSV file and the current business
rules. Some important questions are still intentionally visible:

- Returns and cancellations may need more detailed business handling.
- Negative quantities can reduce revenue and may represent returns or
  corrections.
- Some rows have missing `CustomerID` values.
- Some rows may contain zero or negative `UnitPrice` values.
- Some stock codes may represent postage, discounts, fees, or adjustments
  instead of normal products.
- Revenue is calculated at the line level as `Quantity * UnitPrice`.
- The dashboard helps explore the data, but it does not decide final accounting
  rules.

These limitations are common in real analytics projects. A dashboard can show
patterns, but business definitions still need to be confirmed.

## Version 1 vs Version 2

**Version 1 Basic Dashboard** is a simpler starting point. It shows fixed
summary metrics and charts for the cleaned dataset.

**Version 2 Business Intelligence Dashboard** is more interactive. It adds
sidebar filters, more KPIs, more charts, a data preview table, and a filtered
CSV download.

In short:

- Version 1 answers: "What does the overall dataset look like?"
- Version 2 answers: "How do the results change when I filter and explore the
  data?"

## Version 2 vs Future AI Versions

Version 2 is not an AI assistant or an AI agent.

It is an interactive BI dashboard where users choose filters and read charts
themselves.

Future versions may add AI features:

- **Version 3: AI Data Assistant** could let users ask natural-language
  questions about the dataset.
- **Version 4: AI Analysis Agent** could perform more guided analysis,
  investigate patterns, and suggest next steps.

Those future AI versions are separate stages of the project. This folder only
contains the Version 2 Business Intelligence Dashboard.
