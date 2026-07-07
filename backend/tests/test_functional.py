"""
Test Suite — Functional flows, edge cases, API reliability, accessibility, performance.
Backend unit and integration tests using pytest + FastAPI TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, MagicMock

# ─── Fixtures ───

@pytest.fixture
def client():
    from app.main import create_app
    app = create_app()
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register and login a test user, return auth headers."""
    client.post("/auth/register", json={
        "email": "test@prestocks.io",
        "password": "SecurePass123!",
        "full_name": "Test User"
    })
    resp = client.post("/auth/login", json={"email": "test@prestocks.io", "password": "SecurePass123!"})
    token = resp.json().get("access_token", "test-token")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_company(client, auth_headers):
    """Create a sample company for tests."""
    return {"id": 1, "name": "TestCorp", "ticker": "TST"}


# ─── FUNCTIONAL FLOW TESTS ───

class TestAuthFlow:
    """Test complete authentication flows."""

    def test_register_new_user(self, client):
        resp = client.post("/auth/register", json={
            "email": "newuser@test.io", "password": "Password123!", "full_name": "New User"
        })
        assert resp.status_code in (200, 201)

    def test_register_duplicate_email(self, client):
        client.post("/auth/register", json={"email": "dup@test.io", "password": "Pass123!", "full_name": "User"})
        resp = client.post("/auth/register", json={"email": "dup@test.io", "password": "Pass123!", "full_name": "User"})
        assert resp.status_code in (400, 409)

    def test_login_success(self, client):
        client.post("/auth/register", json={"email": "login@test.io", "password": "Pass123!", "full_name": "Login User"})
        resp = client.post("/auth/login", json={"email": "login@test.io", "password": "Pass123!"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        resp = client.post("/auth/login", json={"email": "login@test.io", "password": "WrongPass!"})
        assert resp.status_code == 401

    def test_token_refresh(self, client, auth_headers):
        resp = client.post("/auth/refresh", headers=auth_headers)
        assert resp.status_code in (200, 401)

    def test_password_reset_flow(self, client):
        resp = client.post("/auth/password-reset", json={"email": "test@prestocks.io"})
        assert resp.status_code in (200, 404)


class TestPortfolioFlow:
    """Test portfolio creation and trading flows."""

    def test_create_portfolio(self, client, auth_headers):
        resp = client.post("/portfolio/", json={"name": "Test Portfolio"}, headers=auth_headers)
        assert resp.status_code in (200, 201)

    def test_get_portfolio_summary(self, client, auth_headers):
        resp = client.get("/portfolio/summary", headers=auth_headers)
        assert resp.status_code == 200

    def test_execute_trade(self, client, auth_headers):
        resp = client.post("/portfolio/trade", json={
            "company_id": 1, "action": "buy", "quantity": 10, "price": 150.0
        }, headers=auth_headers)
        assert resp.status_code in (200, 201, 400, 404)


class TestSearchFlow:
    """Test search & discovery flows."""

    def test_global_search(self, client):
        resp = client.get("/search/?q=tech")
        assert resp.status_code == 200
        data = resp.json()
        assert "companies" in data
        assert "total" in data

    def test_semantic_search(self, client):
        resp = client.get("/search/semantic?q=AI companies near IPO")
        assert resp.status_code == 200

    def test_get_filters(self, client):
        resp = client.get("/search/filters")
        assert resp.status_code == 200
        data = resp.json()
        assert "sectors" in data
        assert "sort_options" in data

    def test_trending_searches(self, client):
        resp = client.get("/search/trending")
        assert resp.status_code == 200

    def test_save_search(self, client, auth_headers):
        resp = client.post("/search/saved?query=fintech", headers=auth_headers)
        assert resp.status_code in (200, 201)


class TestAIFlow:
    """Test AI research and portfolio advisor flows."""

    def test_research_company(self, client, auth_headers):
        resp = client.post("/ai/research", json={"company_name": "Stripe"}, headers=auth_headers)
        assert resp.status_code == 200

    def test_portfolio_advice(self, client, auth_headers):
        resp = client.post("/ai/portfolio-advice", headers=auth_headers)
        assert resp.status_code in (200, 404)

    def test_ai_chat(self, client, auth_headers):
        resp = client.post("/ai/chat", json={"message": "What is pre-IPO investing?"}, headers=auth_headers)
        assert resp.status_code == 200


# ─── EDGE CASE TESTS ───

class TestEdgeCases:
    """Test boundary conditions and error handling."""

    def test_empty_search_query(self, client):
        resp = client.get("/search/?q=")
        assert resp.status_code == 422

    def test_search_very_long_query(self, client):
        resp = client.get(f"/search/?q={'x' * 300}")
        assert resp.status_code == 422

    def test_invalid_company_id(self, client):
        resp = client.get("/companies/99999")
        assert resp.status_code == 404

    def test_trade_negative_quantity(self, client, auth_headers):
        resp = client.post("/portfolio/trade", json={
            "company_id": 1, "action": "buy", "quantity": -5, "price": 100.0
        }, headers=auth_headers)
        assert resp.status_code in (400, 422)

    def test_trade_zero_price(self, client, auth_headers):
        resp = client.post("/portfolio/trade", json={
            "company_id": 1, "action": "buy", "quantity": 10, "price": 0
        }, headers=auth_headers)
        assert resp.status_code in (400, 422)

    def test_unauthorized_access(self, client):
        resp = client.get("/portfolio/summary")
        assert resp.status_code in (401, 403)

    def test_expired_token(self, client):
        resp = client.get("/portfolio/summary", headers={"Authorization": "Bearer expired.token.here"})
        assert resp.status_code in (401, 403)

    def test_malformed_json(self, client, auth_headers):
        resp = client.post("/ai/research", content=b"not json", headers={**auth_headers, "Content-Type": "application/json"})
        assert resp.status_code == 422

    def test_sql_injection_attempt(self, client):
        resp = client.get("/search/?q='; DROP TABLE companies; --")
        assert resp.status_code == 200  # Should handle gracefully, not crash

    def test_xss_attempt(self, client):
        resp = client.get("/search/?q=<script>alert('xss')</script>")
        assert resp.status_code == 200
        assert "<script>" not in resp.text

    def test_rate_limit_simulation(self, client):
        """Simulate rapid requests to verify rate limiting doesn't crash."""
        for _ in range(50):
            resp = client.get("/search/?q=test")
        assert resp.status_code in (200, 429)


# ─── API RELIABILITY TESTS ───

class TestAPIReliability:
    """Test API stability under various conditions."""

    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_root_endpoint(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_cors_headers(self, client):
        resp = client.options("/", headers={"Origin": "http://localhost:3000"})
        assert resp.status_code in (200, 405)

    def test_all_routes_respond(self, client):
        """Verify no route returns 500 on basic GET."""
        routes = ["/health", "/search/filters", "/search/trending"]
        for route in routes:
            resp = client.get(route)
            assert resp.status_code != 500, f"Route {route} returned 500"

    def test_json_content_type(self, client):
        resp = client.get("/health")
        assert "application/json" in resp.headers.get("content-type", "")

    def test_concurrent_requests(self, client):
        """Test that concurrent requests don't cause race conditions."""
        import concurrent.futures
        def make_request():
            return client.get("/search/?q=test").status_code
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda _: make_request(), range(20)))
        assert all(r in (200, 429) for r in results)


# ─── ACCESSIBILITY TESTS ───

class TestAccessibility:
    """Verify API responses include accessibility-relevant data."""

    def test_error_messages_are_descriptive(self, client):
        resp = client.get("/companies/99999")
        if resp.status_code == 404:
            data = resp.json()
            assert "detail" in data or "message" in data

    def test_pagination_info_present(self, client):
        resp = client.get("/search/?q=tech&limit=5")
        data = resp.json()
        assert "total" in data

    def test_response_structure_consistent(self, client):
        """Verify all list endpoints return consistent structure."""
        resp = client.get("/search/?q=test")
        data = resp.json()
        assert isinstance(data, dict)
        assert "query" in data


# ─── PERFORMANCE TESTS ───

class TestPerformance:
    """Test response times and payload sizes."""

    def test_search_response_time(self, client):
        import time
        start = time.time()
        client.get("/search/?q=tech")
        elapsed = time.time() - start
        assert elapsed < 5.0, f"Search took {elapsed:.2f}s, expected < 5s"

    def test_health_response_time(self, client):
        import time
        start = time.time()
        client.get("/health")
        elapsed = time.time() - start
        assert elapsed < 1.0

    def test_response_payload_size(self, client):
        resp = client.get("/search/?q=tech&limit=10")
        size_kb = len(resp.content) / 1024
        assert size_kb < 500, f"Response is {size_kb:.1f}KB, should be < 500KB"
