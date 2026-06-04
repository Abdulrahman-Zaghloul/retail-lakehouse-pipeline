select
    order_date,
    count(*) as order_count,
    count(distinct customer_id) as customer_count,
    sum(total_quantity) as units_sold,
    round(sum(payment_amount), 2) as gross_payment_amount,
    round(sum(items_total_amount), 2) as gross_items_amount,
    round(avg(payment_amount), 2) as average_order_value
from {{ ref('fact_orders') }}
where payment_status in ('completed', 'refunded')
group by order_date
