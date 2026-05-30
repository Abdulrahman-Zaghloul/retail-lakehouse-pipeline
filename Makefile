include .env
export

.PHONY: help tree status up down restart ps logs clean install schema-source generate-source-data source-counts ingest-raw list-raw

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

tree:
	tree -L 3

status:
	git status

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down
	docker compose up -d

ps:
	docker compose ps

logs:
	docker compose logs -f

clean:
	docker compose down -v

install:
	pip install --upgrade pip
	pip install -r requirements.txt

schema-source:
	PGPASSWORD=$(POSTGRES_SOURCE_PASSWORD) psql \
		-h $(POSTGRES_SOURCE_HOST) \
		-p $(POSTGRES_SOURCE_PORT) \
		-U $(POSTGRES_SOURCE_USER) \
		-d $(POSTGRES_SOURCE_DB) \
		-f docker/postgres/source_schema.sql

generate-source-data:
	python -m src.generation.generate_retail_data

source-counts:
	PGPASSWORD=$(POSTGRES_SOURCE_PASSWORD) psql \
		-h $(POSTGRES_SOURCE_HOST) \
		-p $(POSTGRES_SOURCE_PORT) \
		-U $(POSTGRES_SOURCE_USER) \
		-d $(POSTGRES_SOURCE_DB) \
		-c "SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers UNION ALL SELECT 'products', COUNT(*) FROM products UNION ALL SELECT 'orders', COUNT(*) FROM orders UNION ALL SELECT 'order_items', COUNT(*) FROM order_items UNION ALL SELECT 'payments', COUNT(*) FROM payments UNION ALL SELECT 'shipments', COUNT(*) FROM shipments ORDER BY table_name;"

ingest-raw:
	python -m src.ingestion.extract_postgres_to_minio

list-raw:
	docker compose run --rm --entrypoint /bin/sh create-minio-buckets \
		-c "mc alias set local http://minio:9000 $(MINIO_ROOT_USER) $(MINIO_ROOT_PASSWORD) >/dev/null && mc ls --recursive local/$(MINIO_BUCKET_RAW)"
