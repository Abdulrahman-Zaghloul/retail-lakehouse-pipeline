# Retail Lakehouse Analytics Platform

A production-style data engineering project that builds a batch analytics platform for retail data.

## Project Goal

This project demonstrates how to design, build, orchestrate, test, and document a modern batch data platform.

The platform will ingest retail data from operational sources, land it in a data lake, transform it through curated layers, load it into a warehouse, and expose business-ready analytics models.

## Target Architecture

PostgreSQL source database
        ↓
Python ingestion
        ↓
S3-compatible data lake
        ↓
Spark transformations
        ↓
Warehouse tables
        ↓
dbt models and tests
        ↓
Dashboards and documentation
        ↓
Airflow orchestration

## Tech Stack
Python
SQL
PostgreSQL
Docker
MinIO for local S3-compatible storage
Apache Spark
dbt
Apache Airflow
GitHub Actions
AWS S3 and Redshift in the cloud phase

## Repository Structure

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

## Project Phases
Local development environment
PostgreSQL source database
Synthetic retail data generation
Raw ingestion to data lake
Spark transformations
Warehouse modeling with dbt
Airflow orchestration
Data quality and testing
Cloud deployment
Portfolio polish

## Current Status
Milestone 1: Repository initialization
