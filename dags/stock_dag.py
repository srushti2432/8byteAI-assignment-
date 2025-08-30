import os
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

# Make /opt/airflow/scripts importable
from pathlib import Path
import sys

SCRIPTS_DIR = Path("/opt/airflow/scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.append(str(SCRIPTS_DIR))

from fetch_and_store import run as fetch_and_store_run  # noqa: E402


DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
}

with DAG(
    dag_id="stock_daily_pipeline",
    default_args=DEFAULT_ARGS,
    description="Fetch Alpha Vantage TIME_SERIES_DAILY and upsert into Postgres",
    schedule_interval="@daily",   
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["stocks", "alphavantage", "postgres"],
) as dag:

    def task_fetch_parse_store(**context):
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if not api_key:
            raise ValueError("ALPHAVANTAGE_API_KEY is not set")
        symbols_csv = os.getenv("STOCK_SYMBOLS", "IBM")
        output_size = os.getenv("OUTPUT_SIZE", "compact")
        fetch_and_store_run(symbols_csv=symbols_csv, api_key=api_key, output_size=output_size)

    run_pipeline = PythonOperator(
        task_id="fetch_parse_upsert",
        python_callable=task_fetch_parse_store,
        provide_context=True,
    )

    run_pipeline
