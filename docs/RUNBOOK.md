# Runbook

This document contains operational procedures for running, validating, troubleshooting, and resetting the retail lakehouse pipeline.

---

# Start the Platform

Start all local services:

```bash
make up
```

Verify containers are running:

```bash
make ps
```

Expected healthy services:

```text
retail_postgres_source
retail_postgres_warehouse
retail_minio
```

---

# Stop the Platform

Stop all running services:

```bash
make down
```

---

# Reset the Platform

⚠️ This removes Docker volumes and deletes all local database and object storage state.

```bash
make clean
```

Rebuild the environment from scratch:

```bash
make up
make schema-source
make generate-source-data
make ingest-raw
make spark-curated
make load-warehouse
make dbt-build
```

---

# Run the Pipeline Manually

Execute the full pipeline locally:

```bash
make pipeline-local
```

This performs:

```text
Start Services
      ↓
Generate Source Data
      ↓
Raw Ingestion
      ↓
Spark Curated Transformation
      ↓
Warehouse Load
      ↓
dbt Build
```

---

# Run the Pipeline with Airflow

Validate the end-to-end DAG execution:

```bash
make airflow-test
```

---

# Access MinIO

### URL

```text
http://localhost:9001
```

### Credentials

```text
Username: minioadmin
Password: minioadmin
```

### Buckets

```text
retail-raw
retail-curated
```

---

# Source Database Validation

Check source table counts:

```bash
make source-counts
```

---

# Raw Data Lake Validation

List raw data files:

```bash
make list-raw
```

---

# Curated Data Lake Validation

List curated data files:

```bash
make list-curated
```

---

# Warehouse Validation

List warehouse staging tables:

```bash
make warehouse-tables
```

Check warehouse row counts:

```bash
make warehouse-counts
```

---

# dbt Operations

Verify dbt connectivity:

```bash
make dbt-debug
```

Run models:

```bash
make dbt-run
```

Run tests:

```bash
make dbt-test
```

Run models and tests together:

```bash
make dbt-build
```

---

# Common Issues

## Docker Services Are Not Running

### Symptoms

```text
Connection refused
Container not found
Database unavailable
```

### Resolution

```bash
make up
make ps
```

Verify all required containers are healthy.

---

## MinIO Buckets Are Missing

### Symptoms

```text
Bucket does not exist
NoSuchBucket errors
```

### Resolution

```bash
docker compose up create-minio-buckets
```

---

## Spark Package Download Is Slow

### Symptoms

The first Spark execution may take several minutes.

### Cause

Spark downloads required Maven packages for:

* S3 / MinIO support
* PostgreSQL JDBC support

### Resolution

No action required.

Subsequent Spark runs are typically much faster because dependencies are cached.

---

## Airflow Cannot Find the DAG

### Verify Environment Variables

```bash
export AIRFLOW_HOME="$PWD/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$PWD/airflow/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
```

### Verify DAG Discovery

```bash
make airflow-list
```

---

## dbt Cannot Connect to PostgreSQL

### Verify Warehouse Container

```bash
make ps
```

Ensure:

```text
retail_postgres_warehouse
```

is running and healthy.

### Test dbt Connectivity

```bash
make dbt-debug
```

---

# Operational Validation Checklist

After a successful pipeline run:

* [ ] PostgreSQL source database is populated
* [ ] Raw Parquet files exist in MinIO
* [ ] Curated Parquet files exist in MinIO
* [ ] Warehouse staging tables are populated
* [ ] dbt models complete successfully
* [ ] dbt tests pass
* [ ] Airflow DAG executes successfully

---

# Pipeline Execution Flow

```text
PostgreSQL Source
        ↓
Raw Ingestion
        ↓
MinIO Raw Layer
        ↓
Spark Curated Transformations
        ↓
MinIO Curated Layer
        ↓
Warehouse Load
        ↓
PostgreSQL Warehouse
        ↓
dbt Models
        ↓
Dimensions, Facts, and Marts
        ↓
Airflow Monitoring & Orchestration
```
