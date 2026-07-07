from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from urllib.parse import quote_plus

import feedparser
import pandas as pd
import requests
import yfinance as yf
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from backend.infra.assets import ASSET_UNIVERSE, ECONOMIC_SERIES
from backend.infra.config import SETTINGS


def collect_market_data(history_days: int = 90) -> list[dict[str, Any]]:
    all_rows: list[dict[str, Any]] = []
    start_date = datetime.utcnow() - timedelta(days=history_days)

    market_groups = {
        "stocks": ASSET_UNIVERSE["stocks"],
        "etfs": ASSET_UNIVERSE["etfs"],
        "indexes": ASSET_UNIVERSE["indexes"],
        "crypto": ASSET_UNIVERSE["crypto"],
        "treasuries": ASSET_UNIVERSE["treasuries"],
        "commodities": ASSET_UNIVERSE["commodities"],
    }

    for asset_class, symbols in market_groups.items():
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(start=start_date, interval="1d")
                if history.empty:
                    continue
                for idx, row in history.iterrows():
                    all_rows.append(
                        {
                            "asset_class": asset_class,
                            "symbol": symbol,
                            "as_of": idx.date(),
                            "open": _safe_float(row.get("Open")),
                            "high": _safe_float(row.get("High")),
                            "low": _safe_float(row.get("Low")),
                            "close": _safe_float(row.get("Close")),
                            "volume": _safe_float(row.get("Volume")),
                            "meta": {},
                        }
                    )
            except Exception:
                all_rows.extend(_collect_finnhub_market_history(symbol, asset_class, start_date))
                continue

    all_rows.extend(collect_option_snapshots())
    return all_rows


def collect_option_snapshots() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    as_of = datetime.utcnow().date()
    for symbol in ASSET_UNIVERSE["options_underlyings"]:
        try:
            ticker = yf.Ticker(symbol)
            expirations = ticker.options
            if not expirations:
                continue
            expiry = expirations[0]
            chain = ticker.option_chain(expiry)
            calls = chain.calls
            puts = chain.puts
            call_oi = float(calls["openInterest"].fillna(0).sum()) if not calls.empty else 0.0
            put_oi = float(puts["openInterest"].fillna(0).sum()) if not puts.empty else 0.0
            rows.append(
                {
                    "asset_class": "options",
                    "symbol": symbol,
                    "as_of": as_of,
                    "open": None,
                    "high": None,
                    "low": None,
                    "close": call_oi + put_oi,
                    "volume": float(
                        (calls["volume"].fillna(0).sum() if not calls.empty else 0)
                        + (puts["volume"].fillna(0).sum() if not puts.empty else 0)
                    ),
                    "meta": {
                        "expiration": expiry,
                        "call_open_interest": call_oi,
                        "put_open_interest": put_oi,
                    },
                }
            )
        except Exception:
            continue
    return rows


def collect_fundamental_data() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    as_of = datetime.utcnow().date()

    for symbol in ASSET_UNIVERSE["stocks"]:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            cashflow = ticker.cashflow
            income_stmt = ticker.financials
            rows.append(
                {
                    "symbol": symbol,
                    "as_of": as_of,
                    "revenue": _safe_float(info.get("totalRevenue")),
                    "eps": _safe_float(info.get("trailingEps")),
                    "net_income": _first_frame_value(income_stmt, "Net Income"),
                    "margins": _safe_float(info.get("profitMargins")),
                    "cash_flow": _first_frame_value(cashflow, "Operating Cash Flow"),
                    "debt": _safe_float(info.get("totalDebt")),
                    "roe": _safe_float(info.get("returnOnEquity")),
                    "roic": _safe_float(info.get("returnOnAssets")),
                    "meta": {
                        "market_cap": _safe_float(info.get("marketCap")),
                        "ebitda": _safe_float(info.get("ebitda")),
                        "sector": info.get("sector"),
                    },
                }
            )
        except Exception:
            finnhub_row = _collect_finnhub_fundamentals(symbol, as_of)
            if finnhub_row:
                rows.append(finnhub_row)
            continue
    return rows


def collect_news_data(limit_per_source: int = 50) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fn in (
        _collect_reuters_news,
        _collect_sec_filings,
        _collect_press_releases,
        _collect_earnings_call_news,
        _collect_economic_news,
    ):
        try:
            rows.extend(fn(limit_per_source))
        except Exception:
            continue
    rows.extend(_collect_finnhub_news(limit_per_source))
    return rows


def collect_economic_data() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if SETTINGS.fred_api_key:
        rows.extend(_collect_fred_api_series())

    if rows:
        return rows

    for series_id, series_name in ECONOMIC_SERIES.items():
        try:
            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={quote_plus(series_id)}"
            df = pd.read_csv(url)
            df = df.dropna().tail(12)
            for _, row in df.iterrows():
                value = row.get(series_id)
                if value in (".", None):
                    continue
                rows.append(
                    {
                        "series_id": series_id,
                        "series_name": series_name,
                        "period_date": datetime.strptime(row["DATE"], "%Y-%m-%d").date(),
                        "value": float(value),
                    }
                )
        except Exception:
            continue
    return rows


def _collect_reuters_news(limit: int) -> list[dict[str, Any]]:
    feed = feedparser.parse("https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best")
    rows = []
    for entry in feed.entries[:limit]:
        rows.append(
            {
                "source_type": "reuters",
                "source": "Reuters",
                "title": entry.get("title", ""),
                "published_at": _published_to_datetime(entry),
                "url": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "symbol": None,
            }
        )
    return rows


def _collect_sec_filings(limit: int) -> list[dict[str, Any]]:
    session = _retry_session()
    resp = session.get(
        "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-k&owner=include&output=atom",
        headers={"User-Agent": SETTINGS.sec_user_agent},
        timeout=15,
    )
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    rows = []
    for entry in feed.entries[:limit]:
        rows.append(
            {
                "source_type": "sec_filings",
                "source": "SEC EDGAR",
                "title": entry.get("title", ""),
                "published_at": _published_to_datetime(entry),
                "url": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "symbol": None,
            }
        )
    return rows


def _collect_press_releases(limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for symbol in ASSET_UNIVERSE["stocks"]:
        ticker = yf.Ticker(symbol)
        news = getattr(ticker, "news", []) or []
        for item in news[:limit]:
            publisher = str(item.get("publisher", "Yahoo Finance"))
            if "wire" not in publisher.lower() and "release" not in publisher.lower():
                continue
            rows.append(
                {
                    "source_type": "press_releases",
                    "source": publisher,
                    "title": item.get("title", ""),
                    "published_at": datetime.utcfromtimestamp(item.get("providerPublishTime", 0))
                    if item.get("providerPublishTime")
                    else None,
                    "url": item.get("link", ""),
                    "summary": "",
                    "symbol": symbol,
                }
            )
    return rows


def _collect_earnings_call_news(limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # Lightweight fallback: use ticker calendar + upcoming earnings dates as earnings-call signals.
    for symbol in ASSET_UNIVERSE["stocks"]:
        ticker = yf.Ticker(symbol)
        try:
            calendar = ticker.calendar
            if isinstance(calendar, pd.DataFrame) and not calendar.empty:
                for idx, row in calendar.iterrows():
                    rows.append(
                        {
                            "source_type": "earnings_calls",
                            "source": "Yahoo Finance Earnings Calendar",
                            "title": f"{symbol} earnings event: {idx}",
                            "published_at": datetime.utcnow(),
                            "url": "",
                            "summary": str(row.to_dict()),
                            "symbol": symbol,
                        }
                    )
                    if len(rows) >= limit:
                        return rows
        except Exception:
            continue
    return rows


def _collect_economic_news(limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    url = "https://www.bea.gov/news/rss.xml"
    resp = _retry_session().get(url, timeout=10)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    for entry in feed.entries[:limit]:
        rows.append(
            {
                "source_type": "economic_data",
                "source": "US BEA",
                "title": entry.get("title", ""),
                "published_at": _published_to_datetime(entry),
                "url": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "symbol": None,
            }
        )
    return rows


def _safe_float(value: Any):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_frame_value(frame: pd.DataFrame | None, label: str):
    if frame is None or frame.empty or label not in frame.index:
        return None
    row = frame.loc[label]
    if isinstance(row, pd.Series):
        return _safe_float(row.dropna().iloc[0]) if not row.dropna().empty else None
    return None


def _published_to_datetime(entry: Any) -> datetime | None:
    published_parsed = entry.get("published_parsed")
    if not published_parsed:
        return None
    return datetime(*published_parsed[:6])


def _retry_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _collect_finnhub_market_history(symbol: str, asset_class: str, start_date: datetime) -> list[dict[str, Any]]:
    if not SETTINGS.finnhub_api_key:
        return []
    try:
        end_ts = int(datetime.utcnow().timestamp())
        start_ts = int(start_date.timestamp())
        resolution = "D"
        url = (
            f"https://finnhub.io/api/v1/stock/candle?symbol={quote_plus(symbol)}"
            f"&resolution={resolution}&from={start_ts}&to={end_ts}&token={SETTINGS.finnhub_api_key}"
        )
        data = _retry_session().get(url, timeout=12).json()
        if data.get("s") != "ok":
            return []
        rows = []
        for idx, ts in enumerate(data.get("t", [])):
            rows.append(
                {
                    "asset_class": asset_class,
                    "symbol": symbol,
                    "as_of": datetime.utcfromtimestamp(ts).date(),
                    "open": _safe_float(data.get("o", [None])[idx]),
                    "high": _safe_float(data.get("h", [None])[idx]),
                    "low": _safe_float(data.get("l", [None])[idx]),
                    "close": _safe_float(data.get("c", [None])[idx]),
                    "volume": _safe_float(data.get("v", [None])[idx]),
                    "meta": {"source": "finnhub"},
                }
            )
        return rows
    except Exception:
        return []


def _collect_finnhub_fundamentals(symbol: str, as_of) -> dict[str, Any] | None:
    if not SETTINGS.finnhub_api_key:
        return None
    try:
        metric_url = (
            f"https://finnhub.io/api/v1/stock/metric?symbol={quote_plus(symbol)}"
            f"&metric=all&token={SETTINGS.finnhub_api_key}"
        )
        data = _retry_session().get(metric_url, timeout=12).json()
        metric = data.get("metric", {})
        if not metric:
            return None
        return {
            "symbol": symbol,
            "as_of": as_of,
            "revenue": _safe_float(metric.get("revenuePerShareTTM")),
            "eps": _safe_float(metric.get("epsTTM")),
            "net_income": _safe_float(metric.get("netMargin")),
            "margins": _safe_float(metric.get("operatingMarginTTM")),
            "cash_flow": _safe_float(metric.get("cashFlowPerShareTTM")),
            "debt": _safe_float(metric.get("totalDebt/totalEquityQuarterly")),
            "roe": _safe_float(metric.get("roeTTM")),
            "roic": _safe_float(metric.get("roaTTM")),
            "meta": {"source": "finnhub"},
        }
    except Exception:
        return None


def _collect_finnhub_news(limit: int) -> list[dict[str, Any]]:
    if not SETTINGS.finnhub_api_key:
        return []
    rows: list[dict[str, Any]] = []
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    for symbol in ASSET_UNIVERSE["stocks"][:5]:
        try:
            url = (
                "https://finnhub.io/api/v1/company-news"
                f"?symbol={quote_plus(symbol)}&from={week_ago}&to={today}&token={SETTINGS.finnhub_api_key}"
            )
            data = _retry_session().get(url, timeout=12).json()
            for item in data[:limit]:
                rows.append(
                    {
                        "source_type": "press_releases",
                        "source": item.get("source", "Finnhub"),
                        "title": item.get("headline", ""),
                        "published_at": datetime.utcfromtimestamp(item.get("datetime", 0))
                        if item.get("datetime")
                        else None,
                        "url": item.get("url", ""),
                        "summary": item.get("summary", ""),
                        "symbol": symbol,
                    }
                )
        except Exception:
            continue
    return rows


def _collect_fred_api_series() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    session = _retry_session()
    for series_id, series_name in ECONOMIC_SERIES.items():
        try:
            url = (
                "https://api.stlouisfed.org/fred/series/observations"
                f"?series_id={quote_plus(series_id)}&api_key={quote_plus(SETTINGS.fred_api_key)}&file_type=json"
            )
            data = session.get(url, timeout=12).json()
            observations = data.get("observations", [])[-12:]
            for obs in observations:
                value = obs.get("value")
                if value in (".", None):
                    continue
                rows.append(
                    {
                        "series_id": series_id,
                        "series_name": series_name,
                        "period_date": datetime.strptime(obs["date"], "%Y-%m-%d").date(),
                        "value": float(value),
                    }
                )
        except Exception:
            continue
    return rows

