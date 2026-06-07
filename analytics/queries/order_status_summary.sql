-- Order status summary
-- Use case: operations dashboard.

SELECT
    order_status,
    COUNT(*) AS order_count,
    ROUND(SUM(payment_amount), 2) AS total_payment_amount,
    ROUND(AVG(payment_amount), 2) AS average_payment_amount,
    COUNT(DISTINCT customer_id) AS customer_count
FROM dbt_analytics.fact_orders
GROUP BY order_status
ORDER BY order_count DESC;
