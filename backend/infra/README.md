# PreStocks Phase 1 Data Infrastructure

This module implements nightly ETL for:

- Market data (stocks, ETFs, options, crypto, indexes, treasuries, commodities)
- Fundamental data (revenue, EPS, net income, margins, cash flow, debt, ROE, ROIC)
- News data (Reuters, SEC filings, earnings-call signals, press releases, economic news)
- Economic time series (CPI, unemployment, fed funds rate, GDP)

## Stack

- Python ETL workers
- Airflow scheduler (`backend/airflow/dags/prestocks_nightly_etl.py`)
- Postgres via `POSTGRES_URL`
- Redis via `REDIS_URL` for status cache

## Run local ETL

```bash
python -m backend.infra.run_etl
```

## Phase 1.1: Airflow + Postgres + Redis

Use the infra compose stack to run scheduler/web UI and backing services:

```bash
cd backend
docker compose -f docker-compose.infra.yml up airflow-init
docker compose -f docker-compose.infra.yml up -d airflow-webserver airflow-scheduler postgres redis
```

Airflow web UI: `http://localhost:8080`  
Username/password: `admin` / `admin`

## Environment Variables

- `POSTGRES_URL` (required in production; defaults to local sqlite in development)
- `REDIS_URL` (defaults to `redis://localhost:6379/0`)
- `INFRA_HISTORY_DAYS` (default `90`)
- `INFRA_NEWS_LIMIT` (default `50`)
- `INFRA_PIPELINE_MAX_ATTEMPTS` (default `3`)
- `INFRA_PIPELINE_BACKOFF_SECONDS` (default `2`)
- `FINNHUB_API_KEY` (market/fundamental/news fallback provider)
- `FRED_API_KEY` (economic series API fallback)
- `SEC_USER_AGENT` (required friendly User-Agent for SEC feeds)
- `SLACK_WEBHOOK_URL` (optional incident alerts)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `ALERT_TO_EMAIL` (optional email alerts)

## Phase 1.2 Improvements

- Multi-provider data fallbacks (yfinance primary, Finnhub/FRED as fallback where possible)
- Retry and exponential backoff per pipeline run
- Automatic alerts when status is `failed` or `partial_success`

