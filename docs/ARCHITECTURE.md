# Architecture

## Overview

This project implements a local-first retail lakehouse analytics platform.

The platform simulates a modern batch data engineering workflow:

```text
PostgreSQL source database
        ↓
Python raw ingestion
        ↓
MinIO raw data lake
        ↓
Spark curated transformations
        ↓
MinIO curated data lake
        ↓
Spark warehouse load
        ↓
PostgreSQL warehouse staging
        ↓
dbt dimensional models
        ↓
Analytics facts, dimensions, and marts
        ↓
Airflow orchestration
```

---

## Components

### PostgreSQL Source Database

The source database simulates an operational retail application database.

It contains:

- customers
- products
- orders
- order_items
- payments
- shipments

This represents the type of normalized transactional data that data engineers commonly extract from.

---

### Python Raw Ingestion

The ingestion job extracts each source table from PostgreSQL and writes it to the raw data lake as Parquet.

Raw files are written to MinIO under paths like:

```text
raw/customers/
└── ingestion_date=YYYY-MM-DD/
    └── run_id=YYYYMMDDTHHMMSSZ/
        └── customers.parquet
```

The raw layer is append-only and preserves historical extraction runs.

---

### MinIO Raw Data Lake

MinIO provides local S3-compatible object storage.

The raw bucket stores source extracts before transformation.

---

### Spark Curated Transformations

Spark reads the latest raw Parquet files, standardizes data types, cleans fields, adds metadata, and creates curated datasets.

Curated datasets include:

- customers_clean
- products_clean
- orders_clean
- order_items_clean
- payments_clean
- shipments_clean
- order_summary

---

### MinIO Curated Data Lake

The curated bucket stores cleaned and enriched Parquet datasets.

Curated data is partitioned by processing date and run ID.

---

### PostgreSQL Warehouse

The warehouse database stores staging tables loaded from the curated data lake.

These tables are used as dbt sources.

---

### dbt Analytics Layer

dbt builds analytics-ready models such as:

#### Dimensions

- dim_customers
- dim_products
- dim_dates

#### Facts

- fact_orders
- fact_order_items

#### Marts

- mart_daily_sales
- mart_customer_revenue

dbt also runs data quality tests such as:

- Uniqueness checks
- Not-null checks
- Relationship checks

---

### Airflow Orchestration

Airflow runs the full pipeline end-to-end:

```text
Start Services
      ↓
Generate Source Data
      ↓
Ingest Raw Data
      ↓
Build Curated Layer
      ↓
Load Warehouse
      ↓
dbt Run
      ↓
dbt Test
```

---

## Design Principles

### Local-First Development

The project runs locally with Docker before moving to cloud services.

This reduces cost and makes development easier.

---

### Layered Data Architecture

The project separates:

```text
Raw Layer
    ↓
Curated Layer
    ↓
Warehouse Staging
    ↓
Analytics Layer
```

This improves:

- Reliability
- Traceability
- Maintainability

---

### Reproducibility

The project uses:

- Docker
- Makefile commands
- dbt models
- Airflow DAGs

This allows the pipeline to be reproduced consistently across environments.

---

### Observability

Each ingestion and Spark run includes:

- Run IDs
- Processing timestamps

Additional visibility is provided by:

- Airflow execution monitoring
- dbt test results
- dbt model documentation
