from backend.infra.alerts import _build_message
from backend.infra.collectors import _retry_session


def test_retry_session_builds_http_adapters():
    session = _retry_session()
    assert "http://" in session.adapters
    assert "https://" in session.adapters


def test_alert_message_contains_pipeline_and_errors():
    text = _build_message("market_data", "failed", ["api timeout", "retry exhausted"])
    assert "Pipeline: market_data" in text
    assert "Status: failed" in text
    assert "- api timeout" in text

