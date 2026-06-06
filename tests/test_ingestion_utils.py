from datetime import datetime, timezone

import pyarrow.parquet as pq

from src.ingestion.extract_postgres_to_minio import rows_to_parquet_bytes, timestamp_for_path


def test_timestamp_for_path_uses_expected_format():
    value = datetime(2026, 6, 5, 12, 30, 45, tzinfo=timezone.utc)

    assert timestamp_for_path(value) == "20260605T123045Z"


def test_rows_to_parquet_bytes_writes_readable_parquet(tmp_path):
    rows = [
        {"customer_id": 1, "email": "a@example.com"},
        {"customer_id": 2, "email": "b@example.com"},
    ]

    parquet_bytes = rows_to_parquet_bytes(rows)

    output_file = tmp_path / "customers.parquet"
    output_file.write_bytes(parquet_bytes)

    table = pq.read_table(output_file)

    assert table.num_rows == 2
    assert set(table.column_names) == {"customer_id", "email"}
