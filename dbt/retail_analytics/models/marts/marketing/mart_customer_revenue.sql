select
    c.customer_id,
    c.full_name,
    c.email,
    c.loyalty_tier,
    c.city,
    c.state,
    count(o.order_id) as lifetime_orders,
    round(sum(o.payment_amount), 2) as lifetime_revenue,
    max(o.order_date) as most_recent_order_date,
    min(o.order_date) as first_order_date
from {{ ref('dim_customers') }} c
left join {{ ref('fact_orders') }} o
    on c.customer_id = o.customer_id
group by
    c.customer_id,
    c.full_name,
    c.email,
    c.loyalty_tier,
    c.city,
    c.state
