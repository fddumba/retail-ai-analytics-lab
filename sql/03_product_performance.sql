-- Top products by revenue
SELECT
    StockCode,
    Description,
    Revenue
FROM product_sales_summary
ORDER BY Revenue DESC;

-- Top products by quantity
SELECT
    StockCode,
    Description,
    Quantity
FROM product_sales_summary
ORDER BY Quantity DESC;

-- Products with high revenue but low quantity
SELECT
    StockCode,
    Description,
    Revenue,
    Quantity
FROM product_sales_summary
WHERE Revenue > 0
  AND Quantity > 0
ORDER BY Revenue DESC, Quantity ASC;

-- Products with high quantity but low revenue
SELECT
    StockCode,
    Description,
    Revenue,
    Quantity
FROM product_sales_summary
WHERE Revenue > 0
  AND Quantity > 0
ORDER BY Quantity DESC, Revenue ASC;
