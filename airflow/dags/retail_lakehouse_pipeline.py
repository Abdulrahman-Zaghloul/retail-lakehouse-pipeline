from __future__ import annotations

from datetime import datetime
from pathlib import Path

try:
    from airflow.sdk import DAG
except ImportError:
    from airflow import DAG

try:
    from airflow.providers.standard.operators.bash import BashOperator
except ImportError:
    from airflow.operators.bash import BashOperator


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def project_bash_command(command: str) -> str:
    return f"""
    set -euo pipefail
    cd "{PROJECT_ROOT}"

    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    else
        echo "ERROR: Could not find project Python virtual environment."
        echo "Expected either venv/bin/activate or .venv/bin/activate"
        exit 1
    fi

    {command}
    """


with DAG(
    dag_id="retail_lakehouse_pipeline",
    description="End-to-end retail lakehouse pipeline: source generation, raw ingestion, Spark curation, warehouse load, and dbt tests.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["retail", "lakehouse", "data-engineering"],
) as dag:

    start_services = BashOperator(
        task_id="start_local_services",
        bash_command=project_bash_command("make up"),
    )

    generate_source_data = BashOperator(
        task_id="generate_source_data",
        bash_command=project_bash_command("make generate-source-data"),
    )

    ingest_raw = BashOperator(
        task_id="ingest_raw_to_minio",
        bash_command=project_bash_command("make ingest-raw"),
    )

    build_curated = BashOperator(
        task_id="build_curated_layer_with_spark",
        bash_command=project_bash_command("make spark-curated"),
    )

    load_warehouse = BashOperator(
        task_id="load_curated_data_to_warehouse",
        bash_command=project_bash_command("make load-warehouse"),
    )

    dbt_run = BashOperator(
        task_id="run_dbt_models",
        bash_command=project_bash_command("cd dbt/retail_analytics && dbt run"),
    )

    dbt_test = BashOperator(
        task_id="run_dbt_tests",
        bash_command=project_bash_command("cd dbt/retail_analytics && dbt test"),
    )

    (
        start_services
        >> generate_source_data
        >> ingest_raw
        >> build_curated
        >> load_warehouse
        >> dbt_run
        >> dbt_test
    )
