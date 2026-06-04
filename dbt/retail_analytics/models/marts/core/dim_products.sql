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
    updated_at
from {{ ref('stg_products') }}
