-- Revenue by loyalty tier
-- Use case: marketing and customer retention dashboard.

SELECT
    c.loyalty_tier,
    COUNT(DISTINCT c.customer_id) AS customer_count,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.payment_amount), 2) AS revenue,
    ROUND(AVG(o.payment_amount), 2) AS average_order_value
FROM dbt_analytics.dim_customers c
LEFT JOIN dbt_analytics.fact_orders o
    ON c.customer_id = o.customer_id
GROUP BY c.loyalty_tier
ORDER BY revenue DESC NULLS LAST;
