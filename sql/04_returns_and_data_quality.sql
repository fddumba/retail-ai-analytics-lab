-- Count of cancelled invoice rows
SELECT COUNT(*) AS CancelledInvoiceRows
FROM fact_sales
WHERE is_cancelled_invoice = TRUE;

-- Count of negative quantity rows
SELECT COUNT(*) AS NegativeQuantityRows
FROM fact_sales
WHERE is_negative_quantity = TRUE;

-- Count of rows missing CustomerID
SELECT COUNT(*) AS MissingCustomerIDRows
FROM fact_sales
WHERE is_missing_customer_id = TRUE;

-- Count of non-positive UnitPrice rows
SELECT COUNT(*) AS NonPositiveUnitPriceRows
FROM fact_sales
WHERE is_non_positive_unit_price = TRUE;

-- Revenue impact of negative quantity rows
SELECT SUM(Revenue) AS NegativeQuantityRevenueImpact
FROM fact_sales
WHERE is_negative_quantity = TRUE;

-- Percentage of rows affected by each issue
SELECT
    ROUND(100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM fact_sales), 0), 2) AS CancelledInvoicePct
FROM fact_sales
WHERE is_cancelled_invoice = TRUE;

SELECT
    ROUND(100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM fact_sales), 0), 2) AS NegativeQuantityPct
FROM fact_sales
WHERE is_negative_quantity = TRUE;

SELECT
    ROUND(100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM fact_sales), 0), 2) AS MissingCustomerIDPct
FROM fact_sales
WHERE is_missing_customer_id = TRUE;

SELECT
    ROUND(100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM fact_sales), 0), 2) AS NonPositiveUnitPricePct
FROM fact_sales
WHERE is_non_positive_unit_price = TRUE;
