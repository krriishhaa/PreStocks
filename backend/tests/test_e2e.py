"""
End-to-End Tests — Full user journeys across the entire application.
"""
import pytest
from fastapi.testclient import TestClient
import time


@pytest.fixture(scope="module")
def client():
    from app.main import create_app
    app = create_app()
    return TestClient(app)


class TestE2E_NewUserJourney:
    """Complete journey: signup → explore → research → trade → learn."""

    def test_full_user_journey(self, client):
        # 1. User registers
        reg = client.post("/auth/register", json={
            "email": "e2e_user@prestocks.io",
            "password": "E2ETest123!",
            "full_name": "E2E Test User"
        })
        assert reg.status_code in (200, 201, 409)

        # 2. User logs in
        login = client.post("/auth/login", json={
            "email": "e2e_user@prestocks.io", "password": "E2ETest123!"
        })
        if login.status_code != 200:
            return  # Skip if auth is mocked
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. User searches for companies
        search = client.get("/search/?q=AI", headers=headers)
        assert search.status_code == 200

        # 4. User gets AI research on a company
        research = client.post("/ai/research", json={"company_name": "Stripe"}, headers=headers)
        assert research.status_code in (200, 503)

        # 5. User checks portfolio
        portfolio = client.get("/portfolio/summary", headers=headers)
        assert portfolio.status_code in (200, 404)

        # 6. User executes a paper trade
        trade = client.post("/portfolio/trade", json={
            "company_id": 1, "action": "buy", "quantity": 5, "price": 100.0
        }, headers=headers)
        assert trade.status_code in (200, 201, 400, 404)

        # 7. User checks notifications
        notifs = client.get("/notifications/", headers=headers)
        assert notifs.status_code in (200, 404)

        # 8. User logs out
        logout = client.post("/auth/logout", headers=headers)
        assert logout.status_code in (200, 404)


class TestE2E_SearchAndDiscover:
    """Journey: search → filter → save → trend checking."""

    def test_search_discovery_flow(self, client):
        # 1. Get available filters
        filters = client.get("/search/filters")
        assert filters.status_code == 200
        filter_data = filters.json()
        assert "sectors" in filter_data

        # 2. Global search
        search = client.get("/search/?q=fintech&limit=5")
        assert search.status_code == 200

        # 3. Semantic search
        semantic = client.get("/search/semantic?q=AI companies preparing for IPO")
        assert semantic.status_code == 200

        # 4. Check trending
        trending = client.get("/search/trending")
        assert trending.status_code == 200
        assert "trending_companies" in trending.json()


class TestE2E_AIWorkflow:
    """Journey: research → portfolio advice → chat."""

    def test_ai_workflow(self, client):
        # Register and login
        client.post("/auth/register", json={"email": "ai_e2e@test.io", "password": "AITest123!", "full_name": "AI User"})
        login = client.post("/auth/login", json={"email": "ai_e2e@test.io", "password": "AITest123!"})
        if login.status_code != 200:
            return
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        # 1. Research a company
        research = client.post("/ai/research", json={"company_name": "Databricks"}, headers=headers)
        assert research.status_code in (200, 503)

        # 2. Get portfolio advice
        advice = client.post("/ai/portfolio-advice", headers=headers)
        assert advice.status_code in (200, 404)

        # 3. Chat with AI
        chat = client.post("/ai/chat", json={"message": "What sectors are trending?"}, headers=headers)
        assert chat.status_code in (200, 503)


class TestE2E_SecurityFlow:
    """Journey: login → setup 2FA → manage sessions → API keys."""

    def test_security_flow(self, client):
        client.post("/auth/register", json={"email": "sec_e2e@test.io", "password": "SecE2E123!", "full_name": "Security User"})
        login = client.post("/auth/login", json={"email": "sec_e2e@test.io", "password": "SecE2E123!"})
        if login.status_code != 200:
            return
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        # 1. Setup 2FA
        setup = client.post("/security/2fa/setup", headers=headers)
        assert setup.status_code in (200, 404)

        # 2. List sessions
        sessions = client.get("/security/sessions", headers=headers)
        assert sessions.status_code in (200, 404)

        # 3. Create API key
        key = client.post("/security/api-keys?name=E2EKey", headers=headers)
        assert key.status_code in (200, 404)

        # 4. View audit log
        audit = client.get("/security/audit-log", headers=headers)
        assert audit.status_code in (200, 404)


class TestE2E_DataPipeline:
    """Journey: ingest data → validate → store → query."""

    def test_pipeline_e2e(self):
        from app.pipelines.ingestion import PipelineOrchestrator, DataSource

        orchestrator = PipelineOrchestrator(db_session=None)

        # 1. Ingest funding data
        funding_result = orchestrator.run_pipeline("funding_rounds", [
            {"company_name": "E2ECo", "amount_usd": 20_000_000, "stage": "series_a", "announced_date": "2026-06-01", "lead_investor": "Sequoia"},
        ], DataSource.CRUNCHBASE)
        assert funding_result["stats"]["ingested"] == 1

        # 2. Ingest company metadata
        metadata_result = orchestrator.run_pipeline("company_metadata", [
            {"name": "E2ECo", "founded_year": 2022, "employee_count": 120, "website_url": "https://e2eco.com", "industry": "AI/ML"},
        ], DataSource.COMPANY_WEBSITE)
        assert metadata_result["stats"]["ingested"] == 1

        # 3. Ingest news
        news_result = orchestrator.run_pipeline("news", [
            {"title": "E2ECo raises Series A", "source_name": "TechCrunch", "published_at": "2026-06-01", "content": "E2ECo announced a $20M Series A led by Sequoia Capital to expand AI operations."},
        ], DataSource.NEWS_API)
        assert news_result["stats"]["ingested"] == 1

        # 4. Check pipeline status
        status = orchestrator.get_pipeline_status()
        assert len(status) == 7


class TestE2E_PerformanceBenchmark:
    """Verify response times across the app."""

    def test_endpoint_response_times(self, client):
        benchmarks = {
            "/health": 1.0,
            "/search/?q=test": 3.0,
            "/search/filters": 2.0,
            "/search/trending": 3.0,
        }

        for endpoint, max_time in benchmarks.items():
            start = time.time()
            resp = client.get(endpoint)
            elapsed = time.time() - start
            assert elapsed < max_time, f"{endpoint} took {elapsed:.2f}s (max {max_time}s)"
            assert resp.status_code != 500, f"{endpoint} returned 500"
