from typing import Any


def validate_market_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    valid, errors = [], []
    for row in rows:
        close = row.get("close")
        if close is None or float(close) <= 0:
            errors.append(f"Invalid close for {row.get('symbol')} on {row.get('as_of')}")
            continue
        valid.append(row)
    return valid, errors


def validate_fundamental_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    valid, errors = [], []
    for row in rows:
        symbol = row.get("symbol")
        if not symbol:
            errors.append("Missing symbol in fundamentals row")
            continue
        valid.append(row)
    return valid, errors


def validate_news_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    valid, errors = [], []
    for row in rows:
        title = row.get("title", "")
        if len(title.strip()) < 8:
            errors.append("News title too short")
            continue
        valid.append(row)
    return valid, errors


def validate_economic_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    valid, errors = [], []
    for row in rows:
        if row.get("value") is None:
            errors.append(f"Missing value for series {row.get('series_id')}")
            continue
        valid.append(row)
    return valid, errors

