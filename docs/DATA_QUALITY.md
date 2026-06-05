# Data Quality

## Overview

This project implements data quality controls across multiple layers of the pipeline to ensure data integrity, traceability, and reliability.

---

## Source Layer Checks

The PostgreSQL source database enforces data quality through schema-level constraints.

### Implemented Constraints

* Primary keys
* Foreign keys
* Not-null constraints
* Accepted value checks
* Positive amount validations

### Examples

* `order_items.quantity > 0`
* `products.unit_price >= 0`
* `orders.order_status` must be one of:

```text
pending
paid
shipped
delivered
cancelled
refunded
```

These checks prevent invalid data from entering the pipeline.

---

## Raw Layer Checks

The raw ingestion process generates a manifest file for every extraction run.

### Manifest Contents

* Run ID
* Extraction timestamp
* Source database information
* Extracted tables
* Row counts
* Object storage paths
* File sizes

### Example Manifest Location

```text
raw/_manifests/
└── ingestion_date=YYYY-MM-DD/
    └── run_id=YYYYMMDDTHHMMSSZ/
        └── manifest.json
```

The manifest provides a complete audit trail for every ingestion run.

---

## Curated Layer Checks

Spark transformations apply standardization, validation, and enrichment logic before data is promoted to the curated layer.

### Data Standardization

* Normalize customer email casing
* Standardize product SKU formatting
* Standardize state and country values
* Trim whitespace from text fields

### Data Type Validation

* Cast timestamps to proper timestamp types
* Cast numeric fields to decimal types
* Validate boolean fields

### Record Validation

* Remove duplicate primary keys
* Calculate expected order item totals
* Compare calculated totals against source totals

### Order Item Quality Flag

The curated order item dataset includes:

```text
is_valid_line_total
```

This flag identifies whether:

```text
(quantity × unit_price) − discount_amount
```

matches the source `line_total`.

This allows downstream monitoring of pricing and calculation anomalies.

---

## Warehouse Layer Checks

Warehouse staging tables are validated using row-count checks.

### Validation Command

```bash
make warehouse-counts
```

### Expected Baseline Counts

| Table             | Expected Rows |
| ----------------- | ------------: |
| customers_clean   |         1,000 |
| products_clean    |           250 |
| orders_clean      |         3,000 |
| order_items_clean |         6,052 |
| payments_clean    |         3,000 |
| shipments_clean   |         2,044 |
| order_summary     |         3,000 |

> Note: Counts may vary if synthetic data generation logic changes.

---

## dbt Tests

dbt validates the analytics layer using automated tests.

### Test Types

* Not-null tests
* Unique tests
* Relationship tests

### Validation Command

```bash
make dbt-test
```

### Expected Result

```text
PASS=37
WARN=0
ERROR=0
```

These tests verify that dimensions, facts, and marts meet expected quality standards.

---

## Orchestration Validation

The complete pipeline is validated through Airflow orchestration.

### Validation Command

```bash
make airflow-test
```

### Success Criteria

A successful pipeline run indicates:

* Source data generation completed
* Raw ingestion completed
* Curated layer build completed
* Warehouse load completed
* dbt models built successfully
* dbt tests passed
* No task failures occurred

---

## Data Quality Summary

The project implements quality controls at every major layer:

```text
Source Database
    ↓
Schema Constraints
    ↓
Raw Ingestion
    ↓
Manifest Validation
    ↓
Spark Curated Layer
    ↓
Data Cleaning & Validation
    ↓
Warehouse
    ↓
Row Count Verification
    ↓
dbt
    ↓
Automated Data Tests
    ↓
Airflow
    ↓
End-to-End Pipeline Validation
```

This layered approach helps ensure that data remains accurate, auditable, and analytics-ready throughout the pipeline lifecycle.
