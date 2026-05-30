# Retail Lakehouse Analytics Platform

A production-style data engineering project that builds a batch analytics platform for retail data.

## Project Goal

This project demonstrates how to design, build, orchestrate, test, and document a modern batch data platform.

The platform will ingest retail data from operational sources, land it in a data lake, transform it through curated layers, load it into a warehouse, and expose business-ready analytics models.

## Target Architecture

1. PostgreSQL source database
	↓
2. Python ingestion
        ↓
3. S3-compatible data lake
        ↓
4. Spark transformations
        ↓
5. Warehouse tables
        ↓
6. dbt models and tests
        ↓
7. Dashboards and documentation
        ↓
8. Airflow orchestration

## Tech Stack
* Python
* SQL
* PostgreSQL
* Docker
* MinIO for local S3-compatible storage
* Apache Spark
* dbt
* Apache Airflow
* GitHub Actions
* AWS S3 and Redshift in the cloud phase

## Repository Structure
```code
.
├── airflow/       # Airflow DAGs and orchestration code
├── dashboards/    # Dashboard exports and screenshots
├── data/          # Local development data, mostly ignored by Git
├── dbt/           # dbt project for warehouse modeling
├── docker/        # Docker-related configuration
├── docs/          # Architecture, decisions, runbooks, notes
├── spark/         # Spark jobs
├── src/           # Python source code
└── tests/         # Automated tests

```
## Project Phases
1. Local development environment
2. PostgreSQL source database
3. Synthetic retail data generation
4. Raw ingestion to data lake
5. Spark transformations
6. Warehouse modeling with dbt
7. Airflow orchestration
8. Data quality and testing
9. Cloud deployment

## Current Status

Milestone 5: Spark curated transformations from raw data lake to curated data lake.
