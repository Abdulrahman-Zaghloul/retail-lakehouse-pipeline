-- Monthly revenue trend
-- Use case: executive revenue dashboard.

SELECT
    DATE_TRUNC('month', order_date)::date AS month_start,
    COUNT(order_id) AS order_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    SUM(total_quantity) AS units_sold,
    ROUND(SUM(payment_amount), 2) AS revenue,
    ROUND(AVG(payment_amount), 2) AS average_order_value
FROM dbt_analytics.fact_orders
WHERE payment_status IN ('completed', 'refunded')
GROUP BY 1
ORDER BY 1;
