from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


SOURCE_TABLES = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "payments": "payment_id",
    "shipments": "shipment_id",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def timestamp_for_path(value: datetime) -> str:
    return value.strftime("%Y%m%dT%H%M%SZ")


def get_postgres_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["POSTGRES_SOURCE_HOST"],
        port=os.environ["POSTGRES_SOURCE_PORT"],
        dbname=os.environ["POSTGRES_SOURCE_DB"],
        user=os.environ["POSTGRES_SOURCE_USER"],
        password=os.environ["POSTGRES_SOURCE_PASSWORD"],
        row_factory=dict_row,
    )


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["MINIO_ENDPOINT"],
        aws_access_key_id=os.environ["MINIO_ROOT_USER"],
        aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
        region_name="us-east-1",
    )


def fetch_table_rows(conn: psycopg.Connection, table_name: str, order_column: str) -> list[dict[str, Any]]:
    query = f"SELECT * FROM {table_name} ORDER BY {order_column};"

    with conn.cursor() as cur:
        cur.execute(query)
        return list(cur.fetchall())


def rows_to_parquet_bytes(rows: list[dict[str, Any]]) -> bytes:
    buffer = BytesIO()

    if rows:
        table = pa.Table.from_pylist(rows)
    else:
        table = pa.table({})

    pq.write_table(table, buffer, compression="snappy")
    return buffer.getvalue()


def upload_bytes_to_s3(
    s3_client,
    bucket: str,
    key: str,
    body: bytes,
    content_type: str,
) -> None:
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType=content_type,
    )


def extract_table(
    conn: psycopg.Connection,
    s3_client,
    bucket: str,
    table_name: str,
    order_column: str,
    run_id: str,
    ingestion_date: str,
) -> dict[str, Any]:
    print(f"Extracting table: {table_name}")

    rows = fetch_table_rows(conn, table_name, order_column)
    parquet_bytes = rows_to_parquet_bytes(rows)

    object_key = (
        f"raw/{table_name}/"
        f"ingestion_date={ingestion_date}/"
        f"run_id={run_id}/"
        f"{table_name}.parquet"
    )

    upload_bytes_to_s3(
        s3_client=s3_client,
        bucket=bucket,
        key=object_key,
        body=parquet_bytes,
        content_type="application/octet-stream",
    )

    result = {
        "table_name": table_name,
        "row_count": len(rows),
        "bucket": bucket,
        "object_key": object_key,
        "file_size_bytes": len(parquet_bytes),
    }

    print(
        f"Uploaded {table_name}: "
        f"{len(rows):,} rows, "
        f"{len(parquet_bytes):,} bytes -> "
        f"s3://{bucket}/{object_key}"
    )

    return result


def upload_manifest(
    s3_client,
    bucket: str,
    run_id: str,
    ingestion_date: str,
    extracted_at: datetime,
    table_results: list[dict[str, Any]],
) -> None:
    manifest = {
        "run_id": run_id,
        "ingestion_date": ingestion_date,
        "extracted_at": extracted_at.isoformat(),
        "source": {
            "type": "postgres",
            "database": os.environ["POSTGRES_SOURCE_DB"],
            "host": os.environ["POSTGRES_SOURCE_HOST"],
            "port": os.environ["POSTGRES_SOURCE_PORT"],
        },
        "tables": table_results,
    }

    manifest_key = f"raw/_manifests/ingestion_date={ingestion_date}/run_id={run_id}/manifest.json"

    upload_bytes_to_s3(
        s3_client=s3_client,
        bucket=bucket,
        key=manifest_key,
        body=json.dumps(manifest, indent=2).encode("utf-8"),
        content_type="application/json",
    )

    print(f"Uploaded manifest -> s3://{bucket}/{manifest_key}")


def main() -> None:
    extracted_at = utc_now()
    run_id = timestamp_for_path(extracted_at)
    ingestion_date = extracted_at.date().isoformat()
    bucket = os.environ["MINIO_BUCKET_RAW"]

    print("Starting PostgreSQL to MinIO raw ingestion")
    print(f"Run ID: {run_id}")
    print(f"Raw bucket: {bucket}")

    s3_client = get_s3_client()

    table_results = []

    with get_postgres_connection() as conn:
        for table_name, order_column in SOURCE_TABLES.items():
            result = extract_table(
                conn=conn,
                s3_client=s3_client,
                bucket=bucket,
                table_name=table_name,
                order_column=order_column,
                run_id=run_id,
                ingestion_date=ingestion_date,
            )
            table_results.append(result)

    upload_manifest(
        s3_client=s3_client,
        bucket=bucket,
        run_id=run_id,
        ingestion_date=ingestion_date,
        extracted_at=extracted_at,
        table_results=table_results,
    )

    print("Raw ingestion complete.")


if __name__ == "__main__":
    main()
