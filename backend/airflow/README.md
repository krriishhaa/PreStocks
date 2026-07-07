# PreStocks Airflow (Phase 1.1)

This folder contains the Airflow orchestration layer for the PreStocks ETL platform.

## What it runs

- DAG: `prestocks_nightly_etl`
- Schedule: `0 2 * * *` (2:00 AM daily)
- Tasks:
  - `run_market_data`
  - `run_fundamental_data`
  - `run_news_data`
  - `run_economic_data`

## Start with Docker

```bash
cd backend
docker compose -f docker-compose.infra.yml up airflow-init
docker compose -f docker-compose.infra.yml up -d airflow-webserver airflow-scheduler postgres redis
```

Airflow UI: `http://localhost:8080`

## Local fallback (without Docker)

If Docker is unavailable, you can run Airflow locally (installed in `backend/.venv`):

```bash
cd /path/to/PreStocks
backend/airflow/run_local_airflow.sh
```

Airflow will print the generated login credentials when starting in standalone mode.

You can also run ETL manually:

```bash
cd backend
.venv/bin/python -m backend.infra.run_etl
```
