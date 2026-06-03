from __future__ import annotations

import os
from datetime import datetime, timezone

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


CURATED_DATASETS = [
    "customers_clean",
    "products_clean",
    "orders_clean",
    "order_items_clean",
    "payments_clean",
    "shipments_clean",
    "order_summary",
]

WAREHOUSE_SCHEMA = "staging"


def utc_now_string() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("retail-load-curated-to-warehouse")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def get_jdbc_url() -> str:
    host = os.environ["POSTGRES_WAREHOUSE_HOST"]
    port = os.environ["POSTGRES_WAREHOUSE_PORT"]
    db = os.environ["POSTGRES_WAREHOUSE_DB"]

    return f"jdbc:postgresql://{host}:{port}/{db}"


def read_latest_curated_dataset(
    spark: SparkSession,
    curated_bucket: str,
    dataset_name: str,
) -> DataFrame:
    path = f"s3a://{curated_bucket}/curated/{dataset_name}/"

    df = spark.read.parquet(path)

    latest_run_id = df.select(F.max("run_id").alias("latest_run_id")).first()["latest_run_id"]

    if latest_run_id is None:
        raise ValueError(f"No curated data found for dataset: {dataset_name}")

    latest_df = (
        df.filter(F.col("run_id") == latest_run_id)
        .withColumnRenamed("run_id", "curated_partition_run_id")
        .withColumnRenamed("processing_date", "curated_processing_date")
        .withColumn("warehouse_loaded_at_utc", F.current_timestamp())
    )

    row_count = latest_df.count()
    print(f"Read latest curated dataset {dataset_name}: run_id={latest_run_id}, rows={row_count:,}")

    return latest_df


def write_to_warehouse(
    df: DataFrame,
    jdbc_url: str,
    user: str,
    password: str,
    schema_name: str,
    table_name: str,
) -> None:
    target_table = f"{schema_name}.{table_name}"
    row_count = df.count()

    (
        df.write.format("jdbc")
        .mode("overwrite")
        .option("url", jdbc_url)
        .option("dbtable", target_table)
        .option("user", user)
        .option("password", password)
        .option("driver", "org.postgresql.Driver")
        .save()
    )

    print(f"Loaded warehouse table {target_table}: {row_count:,} rows")


def main() -> None:
    curated_bucket = os.environ["MINIO_BUCKET_CURATED"]
    jdbc_url = get_jdbc_url()
    warehouse_user = os.environ["POSTGRES_WAREHOUSE_USER"]
    warehouse_password = os.environ["POSTGRES_WAREHOUSE_PASSWORD"]

    print("Starting curated data load into PostgreSQL warehouse")
    print(f"Curated bucket: {curated_bucket}")
    print(f"Warehouse JDBC URL: {jdbc_url}")
    print(f"Warehouse schema: {WAREHOUSE_SCHEMA}")
    print(f"Load started at: {utc_now_string()}")

    spark = create_spark_session()

    for dataset_name in CURATED_DATASETS:
        df = read_latest_curated_dataset(
            spark=spark,
            curated_bucket=curated_bucket,
            dataset_name=dataset_name,
        )

        write_to_warehouse(
            df=df,
            jdbc_url=jdbc_url,
            user=warehouse_user,
            password=warehouse_password,
            schema_name=WAREHOUSE_SCHEMA,
            table_name=dataset_name,
        )

    print("Warehouse load complete.")
    spark.stop()


if __name__ == "__main__":
    main()
