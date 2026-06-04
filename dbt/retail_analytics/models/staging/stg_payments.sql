select
    payment_id,
    order_id,
    payment_method,
    payment_status,
    payment_amount,
    paid_at,
    source_ingestion_date,
    source_run_id,
    curated_run_id,
    processed_at_utc,
    warehouse_loaded_at_utc
from {{ source('warehouse_staging', 'payments_clean') }}
