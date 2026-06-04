select
    shipment_id,
    order_id,
    carrier,
    tracking_number,
    shipment_status,
    shipped_at,
    delivered_at,
    source_ingestion_date,
    source_run_id,
    curated_run_id,
    processed_at_utc,
    warehouse_loaded_at_utc
from {{ source('warehouse_staging', 'shipments_clean') }}
