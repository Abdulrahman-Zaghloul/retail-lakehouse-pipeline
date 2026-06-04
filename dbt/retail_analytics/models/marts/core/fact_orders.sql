select
    order_id,
    customer_id,
    order_status,
    order_ts,
    order_date,
    order_item_count,
    total_quantity,
    items_total_amount,
    payment_method,
    payment_status,
    payment_amount,
    paid_at,
    carrier,
    shipment_status,
    shipped_at,
    delivered_at,
    case
        when order_status = 'delivered' then true
        else false
    end as is_delivered,
    case
        when order_status in ('cancelled', 'refunded') then true
        else false
    end as is_negative_outcome
from {{ ref('stg_order_summary') }}
