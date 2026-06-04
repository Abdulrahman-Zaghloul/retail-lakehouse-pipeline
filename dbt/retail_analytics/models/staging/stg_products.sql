select
    product_id,
    sku,
    product_name,
    category,
    subcategory,
    brand,
    unit_price,
    is_active,
    created_at,
    updated_at,
    source_ingestion_date,
    source_run_id,
    curated_run_id,
    processed_at_utc,
    warehouse_loaded_at_utc
from {{ source('warehouse_staging', 'products_clean') }}
