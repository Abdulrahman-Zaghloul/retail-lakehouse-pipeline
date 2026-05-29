from __future__ import annotations

import os
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from faker import Faker


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

fake = Faker("en_US")
Faker.seed(42)
random.seed(42)


CUSTOMER_COUNT = 1_000
PRODUCT_COUNT = 250
ORDER_COUNT = 3_000


PRODUCT_CATALOG = {
    "Electronics": {
        "Headphones": ["SoundMax", "Auralux", "WavePro"],
        "Chargers": ["VoltEdge", "Powerly", "ChargePro"],
        "Smart Watches": ["FitPulse", "ChronoX", "Wristly"],
    },
    "Home": {
        "Kitchen": ["HomePro", "CookEase", "UrbanNest"],
        "Decor": ["Roomly", "CasaCraft", "Nestique"],
        "Storage": ["Boxora", "TidyUp", "SpaceMint"],
    },
    "Clothing": {
        "Shirts": ["North Thread", "Urban Stitch", "CottonWorks"],
        "Shoes": ["StrideLab", "Runory", "PacePeak"],
        "Jackets": ["Warmly", "TrailWear", "CloudCoat"],
    },
    "Beauty": {
        "Skincare": ["Glowly", "PureSkin", "DermaFresh"],
        "Haircare": ["SilkRoot", "Curlify", "ShineLab"],
        "Fragrance": ["AromaHaus", "Mistique", "Scentra"],
    },
}


def money(value: Decimal | float | int) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["POSTGRES_SOURCE_HOST"],
        port=os.environ["POSTGRES_SOURCE_PORT"],
        dbname=os.environ["POSTGRES_SOURCE_DB"],
        user=os.environ["POSTGRES_SOURCE_USER"],
        password=os.environ["POSTGRES_SOURCE_PASSWORD"],
    )


def random_timestamp_within_last_year() -> datetime:
    now = datetime.now(timezone.utc)
    days_back = random.randint(0, 365)
    seconds_back = random.randint(0, 86_400)
    return now - timedelta(days=days_back, seconds=seconds_back)


def build_customers() -> list[tuple]:
    customers = []
    used_emails = set()

    loyalty_tiers = ["bronze", "silver", "gold", "platinum"]
    loyalty_weights = [0.55, 0.25, 0.15, 0.05]

    for customer_id in range(1, CUSTOMER_COUNT + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()

        email = f"{first_name}.{last_name}.{customer_id}@example.com".lower()
        while email in used_emails:
            email = f"{first_name}.{last_name}.{customer_id}.{random.randint(1, 9999)}@example.com".lower()
        used_emails.add(email)

        signup_date = fake.date_between(start_date="-3y", end_date="today")
        created_at = datetime.combine(signup_date, datetime.min.time(), tzinfo=timezone.utc)
        updated_at = created_at + timedelta(days=random.randint(0, 900))

        customers.append(
            (
                customer_id,
                first_name,
                last_name,
                email,
                fake.phone_number(),
                signup_date,
                random.choices(loyalty_tiers, weights=loyalty_weights, k=1)[0],
                fake.city(),
                fake.state_abbr(),
                "US",
                created_at,
                updated_at,
            )
        )

    return customers


def build_products() -> list[tuple]:
    products = []

    for product_id in range(1, PRODUCT_COUNT + 1):
        category = random.choice(list(PRODUCT_CATALOG.keys()))
        subcategory = random.choice(list(PRODUCT_CATALOG[category].keys()))
        brand = random.choice(PRODUCT_CATALOG[category][subcategory])

        base_price = {
            "Electronics": random.uniform(15, 350),
            "Home": random.uniform(8, 180),
            "Clothing": random.uniform(10, 220),
            "Beauty": random.uniform(5, 120),
        }[category]

        created_at = random_timestamp_within_last_year() - timedelta(days=random.randint(30, 365))
        updated_at = created_at + timedelta(days=random.randint(0, 180))

        products.append(
            (
                product_id,
                f"SKU-{product_id:06d}",
                f"{brand} {subcategory} {product_id}",
                category,
                subcategory,
                brand,
                money(base_price),
                random.choices([True, False], weights=[0.92, 0.08], k=1)[0],
                created_at,
                updated_at,
            )
        )

    return products


def build_orders_and_related_rows(products: list[tuple]) -> tuple[list[tuple], list[tuple], list[tuple], list[tuple]]:
    orders = []
    order_items = []
    payments = []
    shipments = []

    order_statuses = ["pending", "paid", "shipped", "delivered", "cancelled", "refunded"]
    order_status_weights = [0.08, 0.16, 0.18, 0.48, 0.07, 0.03]

    payment_methods = ["credit_card", "debit_card", "paypal", "gift_card", "apple_pay"]
    payment_method_weights = [0.45, 0.25, 0.15, 0.05, 0.10]

    carriers = ["UPS", "FedEx", "USPS", "DHL"]

    product_lookup = {
        product[0]: {
            "unit_price": product[6],
            "is_active": product[7],
        }
        for product in products
    }

    active_product_ids = [
        product_id
        for product_id, product_data in product_lookup.items()
        if product_data["is_active"]
    ]

    order_item_id = 1
    payment_id = 1
    shipment_id = 1

    for order_id in range(1, ORDER_COUNT + 1):
        customer_id = random.randint(1, CUSTOMER_COUNT)
        order_ts = random_timestamp_within_last_year()
        order_status = random.choices(order_statuses, weights=order_status_weights, k=1)[0]
        updated_at = order_ts + timedelta(hours=random.randint(1, 240))

        orders.append((order_id, customer_id, order_status, order_ts, updated_at))

        item_count = random.choices([1, 2, 3, 4, 5], weights=[0.45, 0.28, 0.15, 0.08, 0.04], k=1)[0]
        selected_products = random.sample(active_product_ids, item_count)

        order_total = Decimal("0.00")

        for product_id in selected_products:
            quantity = random.choices([1, 2, 3, 4], weights=[0.70, 0.20, 0.07, 0.03], k=1)[0]
            unit_price = product_lookup[product_id]["unit_price"]

            gross_line_amount = money(unit_price * quantity)
            discount_amount = money(gross_line_amount * Decimal(random.choice([0, 0, 0, 0.05, 0.10, 0.15])))
            line_total = money(gross_line_amount - discount_amount)

            order_total += line_total

            order_items.append(
                (
                    order_item_id,
                    order_id,
                    product_id,
                    quantity,
                    unit_price,
                    discount_amount,
                    line_total,
                )
            )
            order_item_id += 1

        if order_status == "pending":
            payment_status = "pending"
            paid_at = None
        elif order_status == "cancelled":
            payment_status = random.choice(["cancelled", "failed"])
            paid_at = None
        elif order_status == "refunded":
            payment_status = "refunded"
            paid_at = order_ts + timedelta(minutes=random.randint(1, 180))
        else:
            payment_status = "completed"
            paid_at = order_ts + timedelta(minutes=random.randint(1, 180))

        payments.append(
            (
                payment_id,
                order_id,
                random.choices(payment_methods, weights=payment_method_weights, k=1)[0],
                payment_status,
                money(order_total),
                paid_at,
            )
        )
        payment_id += 1

        if order_status in {"shipped", "delivered", "refunded"}:
            shipped_at = order_ts + timedelta(hours=random.randint(6, 72))

            if order_status == "delivered":
                shipment_status = "delivered"
                delivered_at = shipped_at + timedelta(days=random.randint(1, 7))
            elif order_status == "refunded":
                shipment_status = "returned"
                delivered_at = shipped_at + timedelta(days=random.randint(1, 7))
            else:
                shipment_status = "in_transit"
                delivered_at = None

            shipments.append(
                (
                    shipment_id,
                    order_id,
                    random.choice(carriers),
                    f"TRK{shipment_id:012d}",
                    shipment_status,
                    shipped_at,
                    delivered_at,
                )
            )
            shipment_id += 1

    return orders, order_items, payments, shipments


def truncate_tables(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            TRUNCATE TABLE
                shipments,
                payments,
                order_items,
                orders,
                products,
                customers
            RESTART IDENTITY CASCADE;
            """
        )


def insert_rows(conn: psycopg.Connection, table_name: str, columns: list[str], rows: list[tuple]) -> None:
    placeholders = ", ".join(["%s"] * len(columns))
    column_list = ", ".join(columns)

    sql = f"""
        INSERT INTO {table_name} ({column_list})
        VALUES ({placeholders})
    """

    with conn.cursor() as cur:
        cur.executemany(sql, rows)


def main() -> None:
    print("Generating synthetic retail source data...")

    customers = build_customers()
    products = build_products()
    orders, order_items, payments, shipments = build_orders_and_related_rows(products)

    with get_connection() as conn:
        print("Truncating existing source tables...")
        truncate_tables(conn)

        print(f"Inserting {len(customers):,} customers...")
        insert_rows(
            conn,
            "customers",
            [
                "customer_id",
                "first_name",
                "last_name",
                "email",
                "phone",
                "signup_date",
                "loyalty_tier",
                "city",
                "state",
                "country",
                "created_at",
                "updated_at",
            ],
            customers,
        )

        print(f"Inserting {len(products):,} products...")
        insert_rows(
            conn,
            "products",
            [
                "product_id",
                "sku",
                "product_name",
                "category",
                "subcategory",
                "brand",
                "unit_price",
                "is_active",
                "created_at",
                "updated_at",
            ],
            products,
        )

        print(f"Inserting {len(orders):,} orders...")
        insert_rows(
            conn,
            "orders",
            ["order_id", "customer_id", "order_status", "order_ts", "updated_at"],
            orders,
        )

        print(f"Inserting {len(order_items):,} order items...")
        insert_rows(
            conn,
            "order_items",
            [
                "order_item_id",
                "order_id",
                "product_id",
                "quantity",
                "unit_price",
                "discount_amount",
                "line_total",
            ],
            order_items,
        )

        print(f"Inserting {len(payments):,} payments...")
        insert_rows(
            conn,
            "payments",
            ["payment_id", "order_id", "payment_method", "payment_status", "amount", "paid_at"],
            payments,
        )

        print(f"Inserting {len(shipments):,} shipments...")
        insert_rows(
            conn,
            "shipments",
            [
                "shipment_id",
                "order_id",
                "carrier",
                "tracking_number",
                "shipment_status",
                "shipped_at",
                "delivered_at",
            ],
            shipments,
        )

        conn.commit()

    print("Synthetic retail source data generation complete.")


if __name__ == "__main__":
    main()
