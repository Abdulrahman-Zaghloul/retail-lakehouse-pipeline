select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_amount,
    line_total,
    calculated_line_total,
    is_valid_line_total,
    source_ingestion_date,
    source_run_id,
    curated_run_id,
    processed_at_utc,
    warehouse_loaded_at_utc
from {{ source('warehouse_staging', 'order_items_clean') }}
