from backend.infra.cleaners import clean_market_rows, clean_news_rows
from backend.infra.validators import validate_market_rows, validate_news_rows


def test_market_cleaning_and_validation():
    raw = [
        {"asset_class": "stocks", "symbol": " nvda ", "as_of": "2026-06-28", "close": 156.2},
        {"asset_class": "stocks", "symbol": "NVDA", "as_of": "2026-06-28", "close": 156.2},
        {"asset_class": "stocks", "symbol": "AAPL", "as_of": "2026-06-28", "close": -10},
    ]
    cleaned = clean_market_rows(raw)
    assert len(cleaned) == 2
    valid, errors = validate_market_rows(cleaned)
    assert len(valid) == 1
    assert len(errors) == 1


def test_news_cleaning_and_validation():
    raw = [
        {
            "source_type": "reuters",
            "source": "Reuters",
            "title": "Fed keeps rates unchanged",
            "url": "https://example.com/a",
        },
        {
            "source_type": "reuters",
            "source": "Reuters",
            "title": "Fed keeps rates unchanged",
            "url": "https://example.com/a",
        },
        {"source_type": "reuters", "source": "Reuters", "title": "Short", "url": "https://example.com/b"},
    ]
    cleaned = clean_news_rows(raw)
    assert len(cleaned) == 2
    valid, errors = validate_news_rows(cleaned)
    assert len(valid) == 1
    assert len(errors) == 1

