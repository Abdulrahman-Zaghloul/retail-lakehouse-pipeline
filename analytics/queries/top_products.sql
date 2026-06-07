-- Top products by revenue
-- Use case: product performance dashboard.

SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.line_total), 2) AS product_revenue,
    COUNT(DISTINCT oi.order_id) AS order_count
FROM dbt_analytics.fact_order_items oi
JOIN dbt_analytics.dim_products p
    ON oi.product_id = p.product_id
JOIN dbt_analytics.fact_orders o
    ON oi.order_id = o.order_id
WHERE o.payment_status IN ('completed', 'refunded')
GROUP BY
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand
ORDER BY product_revenue DESC
LIMIT 25;
