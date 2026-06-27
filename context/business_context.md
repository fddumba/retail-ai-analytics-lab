# Online Retail Business Context

## Dataset Overview

The UCI Online Retail dataset contains transaction-line records for a UK-based, non-store online retailer. Each row represents one item line on an invoice, not necessarily a complete order. The observed workbook covers **December 1, 2010 through December 9, 2011** and contains **541,909 rows across 8 columns**.

## Column Meanings

| Column | Practical meaning |
| --- | --- |
| `InvoiceNo` | Identifier for an invoice or transaction. Values beginning with `C` commonly indicate cancellations, but this needs business confirmation. |
| `StockCode` | Product or item identifier. Some codes may represent fees, postage, discounts, or adjustments rather than merchandise. |
| `Description` | Human-readable item description. |
| `Quantity` | Number of units on the invoice line. Negative values may represent returns, cancellations, or corrections. |
| `InvoiceDate` | Date and time recorded for the invoice. |
| `UnitPrice` | Price per unit in sterling according to the UCI dataset description. |
| `CustomerID` | Customer identifier. It is missing on some rows and should be treated as an identifier, not a measurable number. |
| `Country` | Country associated with the customer or transaction. |

## Confirmed Facts From the Data

The following statements are directly supported by the workbook:

- The dataset has **541,909 rows** and **8 columns**.
- The invoice date range is **2010-12-01 08:26:00 to 2011-12-09 12:50:00**.
- `CustomerID` is missing on **135,080 rows (24.93%)**.
- `Description` is missing on **1,454 rows (0.27%)**.
- There are **5,268 exact duplicate rows** after the first occurrence.
- There are **10,624 rows with a negative quantity**.
- There are **2,517 rows with a zero or negative unit price**, including **2 negative-price rows**.
- Quantity and unit price contain extreme values, so totals and averages should be checked for outlier sensitivity.

## Assumptions Requiring Human Confirmation

These are plausible interpretations, not confirmed facts:

- An `InvoiceNo` beginning with `C` represents a cancelled transaction.
- A negative `Quantity` always represents a return or cancellation.
- `Country` represents the customer's billing or shipping country.
- `InvoiceDate` uses UK local time and does not require timezone conversion.
- `UnitPrice` is net of tax and is directly comparable across every row.
- Rows with a zero unit price are gifts, samples, promotions, or data-entry issues.
- Exact duplicate rows are accidental duplicates rather than legitimate repeated events.
- Missing `CustomerID` values represent guest customers or unregistered transactions.
- Stock codes that do not look like ordinary product codes should be excluded from product KPIs.

These decisions should be documented before producing final business metrics.

## Revenue Formula

The basic line-level formula is:

```text
Revenue = Quantity × UnitPrice
```

Important interpretation notes:

- Negative quantities create negative revenue and may represent returns or cancellations.
- Zero prices create zero revenue.
- Gross sales, returns, and net revenue should ideally be reported separately.
- A final revenue definition may need rules for cancellations, discounts, tax, shipping, and non-product stock codes.

## Data Quality Warnings

- Missing customer IDs limit customer-level analysis, retention metrics, and customer segmentation.
- Missing descriptions reduce product interpretability.
- Exact duplicate records can inflate quantity and revenue if they are accidental.
- Negative quantities and cancellation-style invoices can distort gross sales if treated as normal purchases.
- Zero and negative prices require investigation.
- Extreme quantities and prices can dominate averages and charts.
- The dataset ends partway through December 2011, so month-to-month comparisons involving December can be misleading.
- One invoice can appear across many rows because the data is at invoice-line level.
- Product descriptions may vary in spelling, capitalization, or wording for the same stock code.

## Likely Business Questions

- How are sales and net revenue changing over time?
- Which products generate the most revenue and unit volume?
- Which countries contribute the most revenue and orders?
- What days, weeks, months, or hours have the strongest sales?
- What percentage of activity is associated with returns or cancellations?
- Which customers have the highest lifetime value?
- How many customers make repeat purchases?
- What is the average order value?
- Which products are frequently purchased together?
- Which products or countries have unusually high return rates?
- How much analysis is affected by missing customer IDs?

## Common Dashboard KPIs

KPI definitions must state whether cancellations, returns, duplicates, free items, and missing customer IDs are included.

- Gross revenue
- Return or cancellation value
- Net revenue
- Units sold
- Units returned
- Number of invoices or orders
- Number of cancelled invoices
- Average order value
- Average units per order
- Unique customers
- Repeat customer rate
- Revenue per customer
- Unique products sold
- Revenue by country
- Revenue by product
- Return rate by quantity and by value
- Monthly, weekly, and daily revenue growth

## Notes for Future AI Assistant and Agent Use

- Give the AI a data dictionary and explicit KPI definitions before allowing it to answer business questions.
- Require the AI to distinguish confirmed data facts from business assumptions.
- Make the AI disclose filters used for cancellations, returns, duplicates, missing customers, and non-positive prices.
- Use a governed cleaned dataset rather than allowing the AI to modify the raw workbook.
- Limit generated SQL or Python to approved tables, columns, and read-only operations.
- Validate AI-generated calculations against known benchmark queries.
- Ask the AI to show formulas, date ranges, grouping levels, and row filters with each answer.
- Add guardrails for ambiguous terms such as "sales," "orders," "customers," and "top products."
- Preserve lineage from every dashboard or AI response back to the raw file and cleaning rules.
- Future agents should propose actions separately from executing them, especially when an action could modify data or publish results.
