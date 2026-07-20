-- Monthly revenue trend
SELECT
    InvoiceMonth,
    Revenue,
    Quantity,
    InvoiceCount
FROM monthly_sales_summary
ORDER BY InvoiceMonth;

-- Monthly invoice count
SELECT
    InvoiceMonth,
    InvoiceCount
FROM monthly_sales_summary
ORDER BY InvoiceMonth;

-- Monthly quantity sold
SELECT
    InvoiceMonth,
    Quantity
FROM monthly_sales_summary
ORDER BY InvoiceMonth;

-- Best revenue month
SELECT
    InvoiceMonth,
    Revenue
FROM monthly_sales_summary
ORDER BY Revenue DESC
LIMIT 1;

-- Lowest revenue month
SELECT
    InvoiceMonth,
    Revenue
FROM monthly_sales_summary
ORDER BY Revenue ASC
LIMIT 1;
