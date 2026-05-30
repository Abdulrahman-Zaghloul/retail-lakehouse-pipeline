from __future__ import annotations

import os
from datetime import datetime, timezone

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


SOURCE_TABLES = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "payments": "payment_id",
    "shipments": "shipment_id",
}


def utc_now_string() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def processing_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("retail-curated-layer")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def read_latest_raw_table(spark: SparkSession, raw_bucket: str, table_name: str) -> DataFrame:
    path = f"s3a://{raw_bucket}/raw/{table_name}/"

    df = spark.read.parquet(path)

    latest_run_id = df.select(F.max("run_id").alias("latest_run_id")).first()["latest_run_id"]

    if latest_run_id is None:
        raise ValueError(f"No raw data found for table: {table_name}")

    latest_df = (
        df.filter(F.col("run_id") == latest_run_id)
        .withColumnRenamed("run_id", "source_run_id")
        .withColumnRenamed("ingestion_date", "source_ingestion_date")
    )

    print(f"Read latest raw table {table_name}: run_id={latest_run_id}, rows={latest_df.count():,}")

    return latest_df


def add_processing_metadata(df: DataFrame, run_id: str) -> DataFrame:
    return (
        df.withColumn("curated_run_id", F.lit(run_id))
        .withColumn("processed_at_utc", F.current_timestamp())
    )


def clean_customers(df: DataFrame, run_id: str) -> DataFrame:
    cleaned = (
        df.select(
            F.col("customer_id").cast("long"),
            F.initcap(F.trim(F.col("first_name"))).alias("first_name"),
            F.initcap(F.trim(F.col("last_name"))).alias("last_name"),
            F.lower(F.trim(F.col("email"))).alias("email"),
            F.col("phone"),
            F.col("signup_date").cast("date"),
            F.lower(F.trim(F.col("loyalty_tier"))).alias("loyalty_tier"),
            F.initcap(F.trim(F.col("city"))).alias("city"),
            F.upper(F.trim(F.col("state"))).alias("state"),
            F.upper(F.trim(F.col("country"))).alias("country"),
            F.col("created_at").cast("timestamp"),
            F.col("updated_at").cast("timestamp"),
            F.col("source_ingestion_date"),
            F.col("source_run_id"),
        )
        .dropDuplicates(["customer_id"])
    )

    return add_processing_metadata(cleaned, run_id)


def clean_products(df: DataFrame, run_id: str) -> DataFrame:
    cleaned = (
        df.select(
            F.col("product_id").cast("long"),
            F.upper(F.trim(F.col("sku"))).alias("sku"),
            F.trim(F.col("product_name")).alias("product_name"),
            F.initcap(F.trim(F.col("category"))).alias("category"),
            F.initcap(F.trim(F.col("subcategory"))).alias("subcategory"),
            F.initcap(F.trim(F.col("brand"))).alias("brand"),
            F.col("unit_price").cast("decimal(10,2)").alias("unit_price"),
            F.col("is_active").cast("boolean").alias("is_active"),
            F.col("created_at").cast("timestamp"),
            F.col("updated_at").cast("timestamp"),
            F.col("source_ingestion_date"),
            F.col("source_run_id"),
        )
        .dropDuplicates(["product_id"])
    )

    return add_processing_metadata(cleaned, run_id)


def clean_orders(df: DataFrame, run_id: str) -> DataFrame:
    cleaned = (
        df.select(
            F.col("order_id").cast("long"),
            F.col("customer_id").cast("long"),
            F.lower(F.trim(F.col("order_status"))).alias("order_status"),
            F.col("order_ts").cast("timestamp").alias("order_ts"),
            F.to_date(F.col("order_ts")).alias("order_date"),
            F.col("updated_at").cast("timestamp"),
            F.col("source_ingestion_date"),
            F.col("source_run_id"),
        )
        .dropDuplicates(["order_id"])
    )

    return add_processing_metadata(cleaned, run_id)


def clean_order_items(df: DataFrame, run_id: str) -> DataFrame:
    cleaned = (
        df.select(
            F.col("order_item_id").cast("long"),
            F.col("order_id").cast("long"),
            F.col("product_id").cast("long"),
            F.col("quantity").cast("integer"),
            F.col("unit_price").cast("decimal(10,2)").alias("unit_price"),
            F.col("discount_amount").cast("decimal(10,2)").alias("discount_amount"),
            F.col("line_total").cast("decimal(12,2)").alias("line_total"),
            F.col("source_ingestion_date"),
            F.col("source_run_id"),
        )
        .withColumn(
            "calculated_line_total",
            F.round((F.col("quantity") * F.col("unit_price")) - F.col("discount_amount"), 2).cast("decimal(12,2)"),
        )
        .withColumn(
            "is_valid_line_total",
            F.col("line_total") == F.col("calculated_line_total"),
        )
        .dropDuplicates(["order_item_id"])
    )

    return add_processing_metadata(cleaned, run_id)


def clean_payments(df: DataFrame, run_id: str) -> DataFrame:
    cleaned = (
        df.select(
            F.col("payment_id").cast("long"),
            F.col("order_id").cast("long"),
            F.lower(F.trim(F.col("payment_method"))).alias("payment_method"),
            F.lower(F.trim(F.col("payment_status"))).alias("payment_status"),
            F.col("amount").cast("decimal(12,2)").alias("payment_amount"),
            F.col("paid_at").cast("timestamp"),
            F.col("source_ingestion_date"),
            F.col("source_run_id"),
        )
        .dropDuplicates(["payment_id"])
    )

    return add_processing_metadata(cleaned, run_id)


def clean_shipments(df: DataFrame, run_id: str) -> DataFrame:
    cleaned = (
        df.select(
            F.col("shipment_id").cast("long"),
            F.col("order_id").cast("long"),
            F.upper(F.trim(F.col("carrier"))).alias("carrier"),
            F.upper(F.trim(F.col("tracking_number"))).alias("tracking_number"),
            F.lower(F.trim(F.col("shipment_status"))).alias("shipment_status"),
            F.col("shipped_at").cast("timestamp"),
            F.col("delivered_at").cast("timestamp"),
            F.col("source_ingestion_date"),
            F.col("source_run_id"),
        )
        .dropDuplicates(["shipment_id"])
    )

    return add_processing_metadata(cleaned, run_id)


def build_order_summary(
    orders: DataFrame,
    order_items: DataFrame,
    payments: DataFrame,
    shipments: DataFrame,
    customers: DataFrame,
    run_id: str,
) -> DataFrame:
    item_summary = (
        order_items.groupBy("order_id")
        .agg(
            F.count("*").alias("order_item_count"),
            F.sum("quantity").alias("total_quantity"),
            F.round(F.sum("line_total"), 2).cast("decimal(12,2)").alias("items_total_amount"),
            F.sum(F.when(F.col("is_valid_line_total") == F.lit(False), 1).otherwise(0)).alias("invalid_line_count"),
        )
    )

    customer_fields = customers.select(
        "customer_id",
        "loyalty_tier",
        "city",
        "state",
        "country",
    )

    payment_fields = payments.select(
        "order_id",
        "payment_method",
        "payment_status",
        "payment_amount",
        "paid_at",
    )

    shipment_fields = shipments.select(
        "order_id",
        "carrier",
        "shipment_status",
        "shipped_at",
        "delivered_at",
    )

    summary = (
        orders.join(customer_fields, on="customer_id", how="left")
        .join(item_summary, on="order_id", how="left")
        .join(payment_fields, on="order_id", how="left")
        .join(shipment_fields, on="order_id", how="left")
        .select(
            "order_id",
            "customer_id",
            "order_status",
            "order_ts",
            "order_date",
            "loyalty_tier",
            "city",
            "state",
            "country",
            "order_item_count",
            "total_quantity",
            "items_total_amount",
            "invalid_line_count",
            "payment_method",
            "payment_status",
            "payment_amount",
            "paid_at",
            "carrier",
            "shipment_status",
            "shipped_at",
            "delivered_at",
            "source_ingestion_date",
            "source_run_id",
        )
    )

    return add_processing_metadata(summary, run_id)


def write_curated_dataset(df: DataFrame, curated_bucket: str, dataset_name: str, run_id: str, proc_date: str) -> None:
    path = f"s3a://{curated_bucket}/curated/{dataset_name}/processing_date={proc_date}/run_id={run_id}/"

    row_count = df.count()

    (
        df.write.mode("overwrite")
        .parquet(path)
    )

    print(f"Wrote curated dataset {dataset_name}: {row_count:,} rows -> {path}")


def main() -> None:
    raw_bucket = os.environ["MINIO_BUCKET_RAW"]
    curated_bucket = os.environ["MINIO_BUCKET_CURATED"]

    run_id = utc_now_string()
    proc_date = processing_date()

    print("Starting Spark curated layer build")
    print(f"Curated run ID: {run_id}")
    print(f"Raw bucket: {raw_bucket}")
    print(f"Curated bucket: {curated_bucket}")

    spark = create_spark_session()

    raw_tables = {
        table_name: read_latest_raw_table(spark, raw_bucket, table_name)
        for table_name in SOURCE_TABLES
    }

    curated_tables = {
        "customers_clean": clean_customers(raw_tables["customers"], run_id),
        "products_clean": clean_products(raw_tables["products"], run_id),
        "orders_clean": clean_orders(raw_tables["orders"], run_id),
        "order_items_clean": clean_order_items(raw_tables["order_items"], run_id),
        "payments_clean": clean_payments(raw_tables["payments"], run_id),
        "shipments_clean": clean_shipments(raw_tables["shipments"], run_id),
    }

    curated_tables["order_summary"] = build_order_summary(
        orders=curated_tables["orders_clean"],
        order_items=curated_tables["order_items_clean"],
        payments=curated_tables["payments_clean"],
        shipments=curated_tables["shipments_clean"],
        customers=curated_tables["customers_clean"],
        run_id=run_id,
    )

    for dataset_name, df in curated_tables.items():
        write_curated_dataset(
            df=df,
            curated_bucket=curated_bucket,
            dataset_name=dataset_name,
            run_id=run_id,
            proc_date=proc_date,
        )

    print("Order summary by status:")
    (
        curated_tables["order_summary"]
        .groupBy("order_status")
        .agg(
            F.count("*").alias("order_count"),
            F.round(F.sum("payment_amount"), 2).alias("total_payment_amount"),
        )
        .orderBy(F.desc("order_count"))
        .show(truncate=False)
    )

    print("Spark curated layer build complete.")

    spark.stop()


if __name__ == "__main__":
    main()
