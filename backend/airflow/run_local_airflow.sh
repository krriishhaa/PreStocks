#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export AIRFLOW_HOME="${ROOT_DIR}/backend/.airflow"
export AIRFLOW__CORE__DAGS_FOLDER="${ROOT_DIR}/backend/airflow/dags"
export PYTHONPATH="${ROOT_DIR}"
export POSTGRES_URL="${POSTGRES_URL:-sqlite:///backend/prestocks_infra.db}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export PATH="${ROOT_DIR}/backend/.venv/bin:${PATH}"

mkdir -p "${AIRFLOW_HOME}"
echo "Starting Airflow standalone..."
echo "AIRFLOW_HOME=${AIRFLOW_HOME}"
echo "DAGS_FOLDER=${AIRFLOW__CORE__DAGS_FOLDER}"

"${ROOT_DIR}/backend/.venv/bin/airflow" standalone

