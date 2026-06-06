# Project Showcase

## Project Name

**Retail Lakehouse Data Engineering Platform**

---

## One-Sentence Summary

Built an end-to-end retail data engineering platform that ingests operational PostgreSQL data into a MinIO data lake, transforms it with Spark, loads it into a PostgreSQL warehouse, models analytics tables with dbt, validates data quality through automated tests, and orchestrates the entire pipeline with Airflow.

---

## Business Problem

Retail companies generate operational data across multiple systems, including:

* Customers
* Products
* Orders
* Payments
* Shipments

These transactional databases are optimized for application performance, not analytics.

As data volume grows, reporting directly against operational databases becomes difficult, expensive, and unreliable.

This project addresses that challenge by building a layered analytics pipeline that separates operational workloads from analytical workloads.

---

## Technical Solution

### End-to-End Pipeline

```text
PostgreSQL
    ↓
Python Ingestion
    ↓
MinIO Raw Data Lake
    ↓
Spark Transformations
    ↓
MinIO Curated Data Lake
    ↓
Spark Warehouse Load
    ↓
PostgreSQL Warehouse
    ↓
dbt Models & Tests
    ↓
Analytics Marts
    ↓
Airflow Orchestration
```

---

## Key Engineering Features

### Data Generation

* Synthetic retail data generation using Faker
* Realistic transactional relationships
* Repeatable development environment

### Source System

* PostgreSQL operational database
* Primary key constraints
* Foreign key relationships
* Data validation checks

### Data Lake

* MinIO S3-compatible object storage
* Raw layer for immutable source extracts
* Curated layer for cleaned and enriched datasets
* Parquet storage format

### Data Processing

* Python ingestion framework
* Spark transformation jobs
* Curated dataset generation
* Warehouse loading workflows

### Analytics Engineering

* dbt source definitions
* Staging models
* Dimensional models
* Analytics marts
* Automated data quality tests

### Orchestration

* Apache Airflow DAG
* End-to-end dependency management
* Pipeline execution monitoring

### Software Engineering Practices

* pytest unit tests
* GitHub Actions CI
* Dockerized infrastructure
* Documentation and runbooks
* Architecture decision records

---

## Final Analytics Models

### Dimensions

* `dim_customers`
* `dim_products`
* `dim_dates`

### Facts

* `fact_orders`
* `fact_order_items`

### Business Marts

* `mart_daily_sales`
* `mart_customer_revenue`

---

## Data Quality Strategy

### Source Layer

* Primary keys
* Foreign keys
* NOT NULL constraints
* Accepted value constraints

### Curated Layer

* Data standardization
* Type validation
* Deduplication
* Business rule validation

### Warehouse Layer

dbt automated tests:

* Unique tests
* Not-null tests
* Relationship tests

### Application Layer

Python unit tests covering:

* Utility functions
* Data generation logic
* Ingestion helpers
* Parquet serialization logic

### Continuous Integration

GitHub Actions automatically validates:

* Dependency installation
* Python syntax compilation
* Unit test execution

on every push and pull request.

---

## Technologies Used

| Layer              | Technology               |
| ------------------ | ------------------------ |
| Source Database    | PostgreSQL               |
| Data Generation    | Python, Faker            |
| Ingestion          | Python, psycopg, PyArrow |
| Object Storage     | MinIO                    |
| Data Format        | Parquet                  |
| Transformations    | Apache Spark             |
| Warehouse          | PostgreSQL               |
| Analytics Modeling | dbt                      |
| Orchestration      | Apache Airflow           |
| Testing            | pytest, dbt tests        |
| CI/CD              | GitHub Actions           |
| Infrastructure     | Docker Compose           |

---

## What This Project Demonstrates

This project demonstrates practical experience with:

* Data pipeline design
* Data lake architecture
* Batch ingestion workflows
* Spark transformations
* Data warehouse loading
* Dimensional modeling
* Data quality validation
* Workflow orchestration
* CI/CD implementation
* Infrastructure automation
* Technical documentation

---
