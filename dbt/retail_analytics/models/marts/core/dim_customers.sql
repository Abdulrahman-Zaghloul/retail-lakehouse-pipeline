select
    customer_id,
    first_name,
    last_name,
    first_name || ' ' || last_name as full_name,
    email,
    phone,
    signup_date,
    loyalty_tier,
    city,
    state,
    country,
    created_at,
    updated_at
from {{ ref('stg_customers') }}
