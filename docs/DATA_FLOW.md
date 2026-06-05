# Data Flow

## 1. Source Data Generation

Synthetic retail data is generated and loaded into the PostgreSQL source database.

### Command

```bash
make generate-source-data
```

### Generated Source Tables

* customers
* products
* orders
* order_items
* payments
* shipments

---

## 2. Raw Ingestion

The raw ingestion job extracts source tables from PostgreSQL and writes Parquet files to the MinIO raw data lake.

### Command

```bash
make ingest-raw
```

### Raw Destination Example

```text
s3://retail-raw/raw/orders/
└── ingestion_date=YYYY-MM-DD/
    └── run_id=YYYYMMDDTHHMMSSZ/
        └── orders.parquet
```

### Manifest File

Each ingestion run also generates a manifest file containing metadata about the extraction process.

```text
s3://retail-raw/raw/_manifests/
└── ingestion_date=YYYY-MM-DD/
    └── run_id=YYYYMMDDTHHMMSSZ/
        └── manifest.json
```

---

## 3. Curated Transformation

Spark reads the latest raw ingestion run, standardizes data, performs quality checks, and creates curated datasets.

### Command

```bash
make spark-curated
```

### Curated Destination Example

```text
s3://retail-curated/curated/order_summary/
└── processing_date=YYYY-MM-DD/
    └── run_id=YYYYMMDDTHHMMSSZ/
```

### Curated Datasets

* customers_clean
* products_clean
* orders_clean
* order_items_clean
* payments_clean
* shipments_clean
* order_summary

---

## 4. Warehouse Load

Spark loads the latest curated datasets into PostgreSQL warehouse staging tables.

### Command

```bash
make load-warehouse
```

### Warehouse Staging Tables

```text
staging.customers_clean
staging.products_clean
staging.orders_clean
staging.order_items_clean
staging.payments_clean
staging.shipments_clean
staging.order_summary
```

---

## 5. dbt Modeling

dbt transforms staging tables into analytics-ready dimensions, facts, and marts.

### Commands

```bash
make dbt-run
make dbt-test
```

### Analytics Models

#### Dimensions

* dim_customers
* dim_products
* dim_dates

#### Facts

* fact_orders
* fact_order_items

#### Marts

* mart_daily_sales
* mart_customer_revenue

---

## 6. Airflow Orchestration

Airflow orchestrates the entire pipeline through a Directed Acyclic Graph (DAG).

### Command

```bash
make airflow-test
```

### DAG Name

```text
retail_lakehouse_pipeline
```

---

## End-to-End Flow

```text
Generate Source Data
          ↓
PostgreSQL Source Database
          ↓
Raw Ingestion (Python)
          ↓
MinIO Raw Data Lake
          ↓
Spark Curated Transformations
          ↓
MinIO Curated Data Lake
          ↓
Warehouse Load (Spark)
          ↓
PostgreSQL Warehouse
          ↓
dbt Models
          ↓
Dimensions, Facts, and Marts
          ↓
Airflow Orchestration & Monitoring
```
