"""
Integration Tests — Component interactions, database, full request flows.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="module")
def test_db():
    """Create a test database session."""
    engine = create_engine("sqlite:///./test.db")
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    from app.main import create_app
    app = create_app()
    return TestClient(app)


# ─── AUTH INTEGRATION ───

class TestAuthIntegration:
    """Full auth flow integration."""

    def test_register_login_access_flow(self, client):
        # Register
        reg = client.post("/auth/register", json={
            "email": "flow@test.io", "password": "FlowTest123!", "full_name": "Flow Tester"
        })
        assert reg.status_code in (200, 201, 409)

        # Login
        login = client.post("/auth/login", json={"email": "flow@test.io", "password": "FlowTest123!"})
        if login.status_code == 200:
            token = login.json()["access_token"]
            # Access protected route
            resp = client.get("/portfolio/summary", headers={"Authorization": f"Bearer {token}"})
            assert resp.status_code in (200, 404)

    def test_invalid_token_rejected(self, client):
        resp = client.get("/portfolio/summary", headers={"Authorization": "Bearer invalid_token"})
        assert resp.status_code in (401, 403)


# ─── SEARCH INTEGRATION ───

class TestSearchIntegration:
    """Search across multiple data sources."""

    def test_search_returns_multiple_types(self, client):
        resp = client.get("/search/?q=tech&type=all")
        assert resp.status_code == 200
        data = resp.json()
        assert "companies" in data
        assert "news" in data
        assert "sectors" in data

    def test_search_with_filters(self, client):
        resp = client.get("/search/?q=ai&sort_by=name&limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] <= 5 or len(data["companies"]) <= 5

    def test_filters_endpoint(self, client):
        resp = client.get("/search/filters")
        assert resp.status_code == 200
        data = resp.json()
        assert "sectors" in data
        assert "market_cap_ranges" in data
        assert len(data["market_cap_ranges"]) == 4


# ─── PIPELINE INTEGRATION ───

class TestPipelineIntegration:
    """Test pipelines process data end-to-end."""

    def test_funding_pipeline_full_flow(self):
        from app.pipelines.ingestion import PipelineOrchestrator, DataSource

        orchestrator = PipelineOrchestrator(db_session=None)
        result = orchestrator.run_pipeline("funding_rounds", [
            {"company_name": "TestCo", "amount_usd": 10_000_000, "stage": "seed", "announced_date": "2026-01-01"},
            {"company_name": "BadCo"},  # Missing required fields
            {"company_name": "BigCo", "amount_usd": 500_000_000, "stage": "series_c", "announced_date": "2026-06-01"}
        ], DataSource.CRUNCHBASE)

        assert result["stats"]["ingested"] == 2
        assert result["stats"]["rejected"] == 1

    def test_news_pipeline_with_enrichment(self):
        from app.pipelines.ingestion import PipelineOrchestrator, DataSource

        orchestrator = PipelineOrchestrator(db_session=None)
        result = orchestrator.run_pipeline("news", [
            {"title": "Company sees strong growth and profits beat expectations", "source_name": "Reuters", "published_at": "2026-06-01", "content": "The company reported strong growth in Q2, beating analyst expectations with record profits."},
        ], DataSource.NEWS_API)

        assert result["stats"]["ingested"] == 1
        ingested = result["results"][0]["data_point"]
        assert ingested["confidence_score"] > 0.7

    def test_orchestrator_run_all(self):
        from app.pipelines.ingestion import PipelineOrchestrator, DataSource

        orchestrator = PipelineOrchestrator(db_session=None)
        result = orchestrator.run_all({
            "funding_rounds": [{"company_name": "A", "amount_usd": 1000000, "stage": "seed"}],
            "valuations": [{"company_id": 1, "valuation_usd": 500000000}],
        }, DataSource.CRUNCHBASE)

        assert "funding_rounds" in result
        assert "valuations" in result


# ─── SECURITY INTEGRATION ───

class TestSecurityIntegration:
    """Security feature integration tests."""

    def test_2fa_setup_flow(self, client):
        # Register & login first
        client.post("/auth/register", json={"email": "2fa@test.io", "password": "2FATest123!", "full_name": "2FA User"})
        login = client.post("/auth/login", json={"email": "2fa@test.io", "password": "2FATest123!"})
        if login.status_code == 200:
            token = login.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            resp = client.post("/security/2fa/setup", headers=headers)
            assert resp.status_code in (200, 404)

    def test_api_key_lifecycle(self, client):
        # Login
        client.post("/auth/register", json={"email": "apikey@test.io", "password": "APIKey123!", "full_name": "API User"})
        login = client.post("/auth/login", json={"email": "apikey@test.io", "password": "APIKey123!"})
        if login.status_code == 200:
            headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
            # Create key
            create = client.post("/security/api-keys?name=TestKey", headers=headers)
            if create.status_code == 200:
                key_id = create.json().get("id")
                # List keys
                lst = client.get("/security/api-keys", headers=headers)
                assert lst.status_code == 200
                # Revoke key
                if key_id:
                    rev = client.delete(f"/security/api-keys/{key_id}", headers=headers)
                    assert rev.status_code == 200


# ─── NOTIFICATION INTEGRATION ───

class TestNotificationIntegration:

    def test_create_and_list_alerts(self, client):
        client.post("/auth/register", json={"email": "alerts@test.io", "password": "Alert123!", "full_name": "Alert User"})
        login = client.post("/auth/login", json={"email": "alerts@test.io", "password": "Alert123!"})
        if login.status_code == 200:
            headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
            # Create alert
            client.post("/notifications/alerts", json={
                "company_id": 1, "alert_type": "price", "condition": "above", "threshold": 100.0
            }, headers=headers)
            # List alerts
            resp = client.get("/notifications/alerts", headers=headers)
            assert resp.status_code in (200, 404)
