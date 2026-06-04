select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_amount,
    line_total,
    calculated_line_total,
    is_valid_line_total
from {{ ref('stg_order_items') }}
