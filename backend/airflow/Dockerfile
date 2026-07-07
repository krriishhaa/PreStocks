FROM apache/airflow:2.9.3-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && apt-get clean
USER airflow

# Install only ETL/runtime dependencies needed for PreStocks DAG execution.
COPY airflow/requirements-airflow.txt /opt/airflow/requirements-airflow.txt
RUN pip install --no-cache-dir -r /opt/airflow/requirements-airflow.txt

