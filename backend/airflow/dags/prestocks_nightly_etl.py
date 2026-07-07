from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from backend.infra.pipeline import run_single_pipeline


def _run_one_pipeline(pipeline_name: str):
    result = run_single_pipeline(pipeline_name)
    if result.status == "failed":
        raise RuntimeError(f"{pipeline_name} failed with errors: {result.errors}")


with DAG(
    dag_id="prestocks_nightly_etl",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    tags=["prestocks", "etl", "phase-1"],
    default_args={
        "owner": "prestocks",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
) as dag:
    run_market_data = PythonOperator(
        task_id="run_market_data",
        python_callable=_run_one_pipeline,
        op_kwargs={"pipeline_name": "market_data"},
    )
    run_fundamental_data = PythonOperator(
        task_id="run_fundamental_data",
        python_callable=_run_one_pipeline,
        op_kwargs={"pipeline_name": "fundamental_data"},
    )
    run_news_data = PythonOperator(
        task_id="run_news_data",
        python_callable=_run_one_pipeline,
        op_kwargs={"pipeline_name": "news_data"},
    )
    run_economic_data = PythonOperator(
        task_id="run_economic_data",
        python_callable=_run_one_pipeline,
        op_kwargs={"pipeline_name": "economic_data"},
    )

    run_market_data >> run_fundamental_data >> run_news_data >> run_economic_data

