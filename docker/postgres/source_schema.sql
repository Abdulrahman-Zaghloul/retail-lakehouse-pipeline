DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    signup_date DATE NOT NULL,
    loyalty_tier TEXT NOT NULL CHECK (loyalty_tier IN ('bronze', 'silver', 'gold', 'platinum')),
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'US',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE products (
    product_id BIGINT PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    brand TEXT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    order_status TEXT NOT NULL CHECK (
        order_status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled', 'refunded')
    ),
    order_ts TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    line_total NUMERIC(12, 2) NOT NULL CHECK (line_total >= 0)
);

CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    payment_method TEXT NOT NULL CHECK (
        payment_method IN ('credit_card', 'debit_card', 'paypal', 'gift_card', 'apple_pay')
    ),
    payment_status TEXT NOT NULL CHECK (
        payment_status IN ('pending', 'completed', 'failed', 'cancelled', 'refunded')
    ),
    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
    paid_at TIMESTAMPTZ
);

CREATE TABLE shipments (
    shipment_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    carrier TEXT NOT NULL CHECK (carrier IN ('UPS', 'FedEx', 'USPS', 'DHL')),
    tracking_number TEXT NOT NULL UNIQUE,
    shipment_status TEXT NOT NULL CHECK (
        shipment_status IN ('label_created', 'in_transit', 'delivered', 'returned')
    ),
    shipped_at TIMESTAMPTZ NOT NULL,
    delivered_at TIMESTAMPTZ
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_order_ts ON orders(order_ts);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_shipments_order_id ON shipments(order_id);
