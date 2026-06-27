# Online Retail Data Profile

Generated from the raw workbook. The profiling process reads but does not modify the source file.

## Source

- File: `data\Online Retail.xlsx`
- Rows: **541,909**
- Columns: **8**

## Column Names

`InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`

## Data Types

| Column | Pandas data type |
| --- | --- |
| InvoiceNo | object |
| StockCode | object |
| Description | object |
| Quantity | int64 |
| InvoiceDate | datetime64[us] |
| UnitPrice | float64 |
| CustomerID | float64 |
| Country | str |

## Missing Values

| Column | Missing values | Missing percentage |
| --- | --- | --- |
| InvoiceNo | 0 | 0.00% |
| StockCode | 0 | 0.00% |
| Description | 1454 | 0.27% |
| Quantity | 0 | 0.00% |
| InvoiceDate | 0 | 0.00% |
| UnitPrice | 0 | 0.00% |
| CustomerID | 135080 | 24.93% |
| Country | 0 | 0.00% |

## Duplicate Rows

- Exact duplicate rows after the first occurrence: **5,268**

## Date Range

- Earliest `InvoiceDate`: **2010-12-01 08:26:00**
- Latest `InvoiceDate`: **2011-12-09 12:50:00**

## Sample Rows

| InvoiceNo | StockCode | Description | Quantity | InvoiceDate | UnitPrice | CustomerID | Country |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 536365 | 85123A | WHITE HANGING HEART T-LIGHT HOLDER | 6 | 2010-12-01 08:26:00 | 2.55 | 17850.0 | United Kingdom |
| 536365 | 71053 | WHITE METAL LANTERN | 6 | 2010-12-01 08:26:00 | 3.39 | 17850.0 | United Kingdom |
| 536365 | 84406B | CREAM CUPID HEARTS COAT HANGER | 8 | 2010-12-01 08:26:00 | 2.75 | 17850.0 | United Kingdom |
| 536365 | 84029G | KNITTED UNION FLAG HOT WATER BOTTLE | 6 | 2010-12-01 08:26:00 | 3.39 | 17850.0 | United Kingdom |
| 536365 | 84029E | RED WOOLLY HOTTIE WHITE HEART. | 6 | 2010-12-01 08:26:00 | 3.39 | 17850.0 | United Kingdom |

## Numeric Summary

| Column | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Quantity | 541909.0 | 9.55 | 218.08 | -80995.0 | 1.0 | 3.0 | 10.0 | 80995.0 |
| UnitPrice | 541909.0 | 4.61 | 96.76 | -11062.06 | 1.25 | 2.08 | 4.13 | 38970.0 |
| CustomerID | 406829.0 | 15287.69 | 1713.6 | 12346.0 | 13953.0 | 15152.0 | 16791.0 | 18287.0 |

## Negative Quantity Rows

- Rows where `Quantity < 0`: **10,624**
- These rows may represent returns, cancellations, corrections, or other adjustments.
  Their business meaning should be confirmed before filtering them out.

## Zero or Negative UnitPrice Rows

- Rows where `UnitPrice <= 0`: **2,517**
- Rows where `UnitPrice == 0`: **2,515**
- Rows where `UnitPrice < 0`: **2**
- These rows require review before revenue reporting.

## Reproduce This Profile

From the project root, run:

```bash
python scripts/profile_data.py
```
