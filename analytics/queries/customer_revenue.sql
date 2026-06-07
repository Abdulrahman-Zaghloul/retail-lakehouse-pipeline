-- Top customers by lifetime revenue
-- Use case: customer segmentation and marketing dashboard.

SELECT
    customer_id,
    full_name,
    email,
    loyalty_tier,
    city,
    state,
    lifetime_orders,
    lifetime_revenue,
    first_order_date,
    most_recent_order_date
FROM dbt_analytics.mart_customer_revenue
ORDER BY lifetime_revenue DESC NULLS LAST
LIMIT 25;
