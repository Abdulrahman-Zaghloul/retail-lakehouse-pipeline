select
    order_id,
    customer_id,
    order_status,
    order_ts,
    order_date,
    updated_at,
    source_ingestion_date,
    source_run_id,
    curated_run_id,
    processed_at_utc,
    warehouse_loaded_at_utc
from {{ source('warehouse_staging', 'orders_clean') }}
