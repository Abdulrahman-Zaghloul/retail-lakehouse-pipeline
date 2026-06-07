-- Daily sales performance
-- Use case: dashboard line chart or KPI table for daily revenue trends.

SELECT
    order_date,
    order_count,
    customer_count,
    units_sold,
    gross_payment_amount,
    gross_items_amount,
    average_order_value
FROM dbt_analytics.mart_daily_sales
ORDER BY order_date DESC
LIMIT 30;
