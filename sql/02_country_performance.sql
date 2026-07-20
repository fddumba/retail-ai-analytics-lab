-- Top countries by revenue
SELECT
    Country,
    Revenue
FROM country_sales_summary
ORDER BY Revenue DESC;

-- Top countries by invoice count
SELECT
    Country,
    InvoiceCount
FROM country_sales_summary
ORDER BY InvoiceCount DESC;

-- Top countries by quantity
SELECT
    Country,
    Quantity
FROM country_sales_summary
ORDER BY Quantity DESC;

-- Revenue share by country
SELECT
    Country,
    Revenue,
    ROUND(100.0 * Revenue / NULLIF(SUM(Revenue) OVER (), 0), 2) AS RevenueSharePct
FROM country_sales_summary
ORDER BY Revenue DESC;
