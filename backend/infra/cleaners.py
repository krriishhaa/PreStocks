from datetime import datetime
from typing import Any


def clean_market_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for row in rows:
        symbol = str(row.get("symbol", "")).upper().strip()
        close = row.get("close")
        as_of = row.get("as_of")
        if not symbol or close is None or not as_of:
            continue
        cleaned.append(
            {
                **row,
                "symbol": symbol,
                "as_of": _to_date(as_of),
                "close": float(close),
            }
        )
    return dedupe_by_keys(cleaned, ("asset_class", "symbol", "as_of"))


def clean_fundamental_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for row in rows:
        symbol = str(row.get("symbol", "")).upper().strip()
        as_of = row.get("as_of")
        if not symbol or not as_of:
            continue
        cleaned.append({**row, "symbol": symbol, "as_of": _to_date(as_of)})
    return dedupe_by_keys(cleaned, ("symbol", "as_of"))


def clean_news_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for row in rows:
        title = str(row.get("title", "")).strip()
        source = str(row.get("source", "")).strip()
        source_type = str(row.get("source_type", "")).strip()
        if not title or not source or not source_type:
            continue
        out = {**row, "title": title, "source": source, "source_type": source_type}
        symbol = row.get("symbol")
        if symbol:
            out["symbol"] = str(symbol).upper().strip()
        published = row.get("published_at")
        if published:
            out["published_at"] = _to_datetime(published)
        cleaned.append(out)
    return dedupe_by_keys(cleaned, ("source", "title", "url"))


def clean_economic_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for row in rows:
        series_id = str(row.get("series_id", "")).strip()
        series_name = str(row.get("series_name", "")).strip()
        period_date = row.get("period_date")
        value = row.get("value")
        if not series_id or not series_name or not period_date or value is None:
            continue
        cleaned.append(
            {
                **row,
                "series_id": series_id,
                "series_name": series_name,
                "period_date": _to_date(period_date),
                "value": float(value),
            }
        )
    return dedupe_by_keys(cleaned, ("series_id", "period_date"))


def dedupe_by_keys(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        dedupe_key = tuple(row.get(key) for key in keys)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        out.append(row)
    return out


def _to_date(value: Any):
    if hasattr(value, "date"):
        return value.date() if isinstance(value, datetime) else value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    return value


def _to_datetime(value: Any):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value

