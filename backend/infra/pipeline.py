from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import time
from typing import Any

import redis
from sqlalchemy import desc, select

from backend.infra.alerts import send_pipeline_alert
from backend.infra.cleaners import (
    clean_economic_rows,
    clean_fundamental_rows,
    clean_market_rows,
    clean_news_rows,
)
from backend.infra.collectors import (
    collect_economic_data,
    collect_fundamental_data,
    collect_market_data,
    collect_news_data,
)
from backend.infra.config import SETTINGS
from backend.infra.db import (
    economic_data,
    etl_runs,
    fundamental_data,
    get_engine,
    init_infra_db,
    insert_rows,
    market_data,
    news_data,
)
from backend.infra.validators import (
    validate_economic_rows,
    validate_fundamental_rows,
    validate_market_rows,
    validate_news_rows,
)


@dataclass
class PipelineResult:
    pipeline_name: str
    status: str
    records_pulled: int
    records_valid: int
    records_stored: int
    errors: list[str]
    started_at: datetime
    finished_at: datetime


PIPELINE_DEFINITIONS = {
    "market_data": (collect_market_data, clean_market_rows, validate_market_rows, market_data),
    "fundamental_data": (
        collect_fundamental_data,
        clean_fundamental_rows,
        validate_fundamental_rows,
        fundamental_data,
    ),
    "news_data": (collect_news_data, clean_news_rows, validate_news_rows, news_data),
    "economic_data": (collect_economic_data, clean_economic_rows, validate_economic_rows, economic_data),
}


def run_nightly_etl() -> list[PipelineResult]:
    init_infra_db()
    results = [run_single_pipeline(name, update_cache=False) for name in PIPELINE_DEFINITIONS]
    _cache_latest_status(results)
    return results


def run_single_pipeline(pipeline_name: str, update_cache: bool = True) -> PipelineResult:
    init_infra_db()
    if pipeline_name not in PIPELINE_DEFINITIONS:
        valid = ", ".join(sorted(PIPELINE_DEFINITIONS.keys()))
        raise ValueError(f"Unknown pipeline '{pipeline_name}'. Expected one of: {valid}")
    collector, cleaner, validator, table = PIPELINE_DEFINITIONS[pipeline_name]
    result = _run_pipeline(pipeline_name, collector, cleaner, validator, table)
    if update_cache:
        _cache_latest_status([result])
    return result


def get_latest_runs(limit: int = 20) -> list[dict[str, Any]]:
    init_infra_db()
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(select(etl_runs).order_by(desc(etl_runs.c.id)).limit(limit)).mappings().all()
    return [dict(row) for row in rows]


def get_pipeline_status() -> dict[str, Any]:
    runs = get_latest_runs(limit=50)
    latest_by_name: dict[str, dict[str, Any]] = {}
    for row in runs:
        name = row["pipeline_name"]
        if name not in latest_by_name:
            latest_by_name[name] = row
    success_count = sum(1 for run in latest_by_name.values() if run["status"] == "success")
    return {
        "environment": SETTINGS.app_env,
        "database": SETTINGS.postgres_url,
        "alerting": {
            "slack_enabled": bool(SETTINGS.slack_webhook_url),
            "email_enabled": bool(SETTINGS.smtp_host and SETTINGS.alert_to_email),
            "max_attempts": SETTINGS.pipeline_max_attempts,
            "backoff_seconds": SETTINGS.pipeline_backoff_seconds,
        },
        "pipelines_total": len(latest_by_name),
        "pipelines_healthy": success_count,
        "latest": latest_by_name,
    }


def _run_pipeline(
    pipeline_name: str,
    collector,
    cleaner,
    validator,
    table,
) -> PipelineResult:
    started_at = datetime.utcnow()
    errors: list[str] = []
    records_pulled = records_valid = records_stored = 0
    status = "success"

    for attempt in range(1, SETTINGS.pipeline_max_attempts + 1):
        try:
            pulled = collector()
            records_pulled = len(pulled)
            if records_pulled == 0:
                errors.append("Collector returned 0 records.")
                raise RuntimeError("Collector returned 0 records.")

            cleaned = cleaner(pulled)
            valid, validation_errors = validator(cleaned)
            errors.extend(validation_errors)
            records_valid = len(valid)

            records_stored = insert_rows(table, valid)
            if validation_errors:
                status = "partial_success"
            else:
                status = "success"
            break
        except Exception as exc:
            errors.append(f"Attempt {attempt}: {exc}")
            status = "failed"
            if attempt < SETTINGS.pipeline_max_attempts:
                sleep_seconds = SETTINGS.pipeline_backoff_seconds * (2 ** (attempt - 1))
                time.sleep(sleep_seconds)

    finished_at = datetime.utcnow()
    result = PipelineResult(
        pipeline_name=pipeline_name,
        status=status,
        records_pulled=records_pulled,
        records_valid=records_valid,
        records_stored=records_stored,
        errors=errors,
        started_at=started_at,
        finished_at=finished_at,
    )
    _log_run(result)
    if result.status in {"failed", "partial_success"}:
        send_pipeline_alert(result.pipeline_name, result.status, result.errors[:10])
    return result


def _log_run(result: PipelineResult) -> None:
    row = {
        "pipeline_name": result.pipeline_name,
        "run_date": date.today(),
        "status": result.status,
        "records_pulled": result.records_pulled,
        "records_valid": result.records_valid,
        "records_stored": result.records_stored,
        "errors": result.errors,
        "started_at": result.started_at,
        "finished_at": result.finished_at,
    }
    insert_rows(etl_runs, [row])


def _cache_latest_status(results: list[PipelineResult]) -> None:
    try:
        client = redis.Redis.from_url(SETTINGS.redis_url, decode_responses=True)
        payload = {
            "generated_at": datetime.utcnow().isoformat(),
            "pipelines": [
                {
                    "pipeline_name": r.pipeline_name,
                    "status": r.status,
                    "records_stored": r.records_stored,
                }
                for r in results
            ],
        }
        client.set("prestocks:infra:latest_status", str(payload), ex=60 * 60 * 24)
    except Exception:
        # Redis is used as a speed layer only; ETL should still succeed if cache is unavailable.
        return

