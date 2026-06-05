SHELL := /bin/bash

include .env
export

PROJECT_VENV_ACTIVATE = if [ -f "venv/bin/activate" ]; then source venv/bin/activate; elif [ -f ".venv/bin/activate" ]; then source .venv/bin/activate; else echo "ERROR: Could not find project venv or .venv"; exit 1; fi
AIRFLOW_VENV_ACTIVATE = if [ -f ".venv-airflow/bin/activate" ]; then source .venv-airflow/bin/activate; else echo "ERROR: Could not find .venv-airflow"; exit 1; fi

.PHONY: help tree status up down restart ps logs clean install schema-source generate-source-data source-counts ingest-raw list-raw spark-version spark-curated list-curated load-warehouse warehouse-tables warehouse-counts dbt-debug dbt-run dbt-test dbt-build airflow-list airflow-test pipeline-local

help:
	@echo "Available commands:"
	@echo "  make tree                  Show project folder structure"
	@echo "  make status                Show git status"
	@echo "  make up                    Start local Docker services"
	@echo "  make down                  Stop local Docker services"
	@echo "  make restart               Restart local Docker services"
	@echo "  make ps                    Show running Docker services"
	@echo "  make logs                  Show Docker logs"
	@echo "  make clean                 Stop services and remove volumes"
	@echo "  make install               Install Python dependencies"
	@echo "  make schema-source         Apply source database schema"
	@echo "  make generate-source-data  Generate fake retail source data"
	@echo "  make source-counts         Show source table row counts"
	@echo "  make ingest-raw            Extract PostgreSQL source tables to MinIO raw bucket"
	@echo "  make list-raw              List files in the MinIO raw bucket"
	@echo "  make spark-version         Show Spark version from Docker container"
	@echo "  make spark-curated         Build curated datasets with Spark"
	@echo "  make list-curated          List files in the MinIO curated bucket"
	@echo "  make load-warehouse        Load latest curated datasets into PostgreSQL warehouse"
	@echo "  make warehouse-tables      List warehouse staging tables"
	@echo "  make warehouse-counts      Show warehouse staging table row counts"
	@echo "  make dbt-debug             Test dbt warehouse connection"
	@echo "  make dbt-run               Run dbt models"
	@echo "  make dbt-test              Run dbt tests"
	@echo "  make dbt-build             Run dbt models and tests"
	@echo "  make airflow-list          List Airflow DAGs"
	@echo "  make airflow-test          Test the full Airflow DAG"
	@echo "  make pipeline-local        Run the full pipeline locally without Airflow"

tree:
	tree -L 3

status:
	git status

up:
	docker compose up -d postgres-source postgres-warehouse minio create-minio-buckets

down:
	docker compose down

restart:
	docker compose down
	docker compose up -d postgres-source postgres-warehouse minio create-minio-buckets

ps:
	docker compose ps

logs:
	docker compose logs -f

clean:
	docker compose down -v

install:
	$(PROJECT_VENV_ACTIVATE); pip install --upgrade pip; pip install -r requirements.txt

schema-source:
	PGPASSWORD=$(POSTGRES_SOURCE_PASSWORD) psql \
		-h $(POSTGRES_SOURCE_HOST) \
		-p $(POSTGRES_SOURCE_PORT) \
		-U $(POSTGRES_SOURCE_USER) \
		-d $(POSTGRES_SOURCE_DB) \
		-f docker/postgres/source_schema.sql

generate-source-data:
	$(PROJECT_VENV_ACTIVATE); python -m src.generation.generate_retail_data

source-counts:
	PGPASSWORD=$(POSTGRES_SOURCE_PASSWORD) psql \
		-h $(POSTGRES_SOURCE_HOST) \
		-p $(POSTGRES_SOURCE_PORT) \
		-U $(POSTGRES_SOURCE_USER) \
		-d $(POSTGRES_SOURCE_DB) \
		-c "SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers UNION ALL SELECT 'products', COUNT(*) FROM products UNION ALL SELECT 'orders', COUNT(*) FROM orders UNION ALL SELECT 'order_items', COUNT(*) FROM order_items UNION ALL SELECT 'payments', COUNT(*) FROM payments UNION ALL SELECT 'shipments', COUNT(*) FROM shipments ORDER BY table_name;"

ingest-raw:
	$(PROJECT_VENV_ACTIVATE); python -m src.ingestion.extract_postgres_to_minio

list-raw:
	docker compose run --rm --entrypoint /bin/sh create-minio-buckets \
		-c "mc alias set local http://minio:9000 $(MINIO_ROOT_USER) $(MINIO_ROOT_PASSWORD) >/dev/null && mc ls --recursive local/$(MINIO_BUCKET_RAW)"

spark-version:
	docker compose run --rm spark /opt/spark/bin/spark-submit --version

spark-curated:
	docker compose run --rm spark /opt/spark/bin/spark-submit \
		--packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
		--conf spark.jars.ivy=/tmp/.ivy2 \
		--conf spark.sql.session.timeZone=UTC \
		--conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
		--conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
		--conf spark.hadoop.fs.s3a.access.key=$(MINIO_ROOT_USER) \
		--conf spark.hadoop.fs.s3a.secret.key=$(MINIO_ROOT_PASSWORD) \
		--conf spark.hadoop.fs.s3a.path.style.access=true \
		--conf spark.hadoop.fs.s3a.connection.ssl.enabled=false \
		--conf spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider \
		spark/jobs/build_curated_layer.py

list-curated:
	docker compose run --rm --entrypoint /bin/sh create-minio-buckets \
		-c "mc alias set local http://minio:9000 $(MINIO_ROOT_USER) $(MINIO_ROOT_PASSWORD) >/dev/null && mc ls --recursive local/$(MINIO_BUCKET_CURATED)"

load-warehouse:
	PGPASSWORD=$(POSTGRES_WAREHOUSE_PASSWORD) psql \
		-h $(POSTGRES_WAREHOUSE_HOST) \
		-p $(POSTGRES_WAREHOUSE_PORT) \
		-U $(POSTGRES_WAREHOUSE_USER) \
		-d $(POSTGRES_WAREHOUSE_DB) \
		-c "CREATE SCHEMA IF NOT EXISTS staging;"
	docker compose run --rm spark /opt/spark/bin/spark-submit \
		--packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262,org.postgresql:postgresql:42.7.3 \
		--conf spark.jars.ivy=/tmp/.ivy2 \
		--conf spark.sql.session.timeZone=UTC \
		--conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
		--conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
		--conf spark.hadoop.fs.s3a.access.key=$(MINIO_ROOT_USER) \
		--conf spark.hadoop.fs.s3a.secret.key=$(MINIO_ROOT_PASSWORD) \
		--conf spark.hadoop.fs.s3a.path.style.access=true \
		--conf spark.hadoop.fs.s3a.connection.ssl.enabled=false \
		--conf spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider \
		spark/jobs/load_curated_to_warehouse.py

warehouse-tables:
	PGPASSWORD=$(POSTGRES_WAREHOUSE_PASSWORD) psql \
		-h $(POSTGRES_WAREHOUSE_HOST) \
		-p $(POSTGRES_WAREHOUSE_PORT) \
		-U $(POSTGRES_WAREHOUSE_USER) \
		-d $(POSTGRES_WAREHOUSE_DB) \
		-c "\dt staging.*"

warehouse-counts:
	PGPASSWORD=$(POSTGRES_WAREHOUSE_PASSWORD) psql \
		-h $(POSTGRES_WAREHOUSE_HOST) \
		-p $(POSTGRES_WAREHOUSE_PORT) \
		-U $(POSTGRES_WAREHOUSE_USER) \
		-d $(POSTGRES_WAREHOUSE_DB) \
		-c "SELECT 'customers_clean' AS table_name, COUNT(*) AS row_count FROM staging.customers_clean UNION ALL SELECT 'products_clean', COUNT(*) FROM staging.products_clean UNION ALL SELECT 'orders_clean', COUNT(*) FROM staging.orders_clean UNION ALL SELECT 'order_items_clean', COUNT(*) FROM staging.order_items_clean UNION ALL SELECT 'payments_clean', COUNT(*) FROM staging.payments_clean UNION ALL SELECT 'shipments_clean', COUNT(*) FROM staging.shipments_clean UNION ALL SELECT 'order_summary', COUNT(*) FROM staging.order_summary ORDER BY table_name;"

dbt-debug:
	$(PROJECT_VENV_ACTIVATE); cd dbt/retail_analytics && dbt debug

dbt-run:
	$(PROJECT_VENV_ACTIVATE); cd dbt/retail_analytics && dbt run

dbt-test:
	$(PROJECT_VENV_ACTIVATE); cd dbt/retail_analytics && dbt test

dbt-build:
	$(PROJECT_VENV_ACTIVATE); cd dbt/retail_analytics && dbt build

airflow-list:
	$(AIRFLOW_VENV_ACTIVATE); \
	export AIRFLOW_HOME=$$(pwd)/airflow; \
	export AIRFLOW__CORE__DAGS_FOLDER=$$(pwd)/airflow/dags; \
	export AIRFLOW__CORE__LOAD_EXAMPLES=False; \
	airflow dags list | grep retail || true

airflow-test:
	$(AIRFLOW_VENV_ACTIVATE); \
	export AIRFLOW_HOME=$$(pwd)/airflow; \
	export AIRFLOW__CORE__DAGS_FOLDER=$$(pwd)/airflow/dags; \
	export AIRFLOW__CORE__LOAD_EXAMPLES=False; \
	airflow dags test retail_lakehouse_pipeline 2026-06-04

pipeline-local:
	make up
	make generate-source-data
	make ingest-raw
	make spark-curated
	make load-warehouse
	make dbt-build
