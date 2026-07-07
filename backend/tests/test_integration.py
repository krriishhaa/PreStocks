import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["app"] == "PreStocks API"


class TestAuthEndpoints:
    def test_signup_missing_email(self):
        resp = client.post("/auth/signup", json={"password": "secure_pass_123"})
        assert resp.status_code == 422

    def test_signup_short_password(self):
        resp = client.post("/auth/signup", json={
            "email": "short_pw@example.com",
            "password": "short",
        })
        assert resp.status_code == 422

    def test_login_no_body(self):
        resp = client.post("/auth/login", json={})
        assert resp.status_code == 422


class TestProtectedEndpoints:
    def test_portfolio_requires_auth(self):
        resp = client.get("/portfolio")
        assert resp.status_code == 403

    def test_stocks_search_requires_auth(self):
        resp = client.get("/stocks/search?q=AAPL")
        assert resp.status_code == 403

    def test_social_feed_requires_auth(self):
        resp = client.get("/social/feed")
        assert resp.status_code == 403

    def test_learning_modules_requires_auth(self):
        resp = client.get("/learning/modules")
        assert resp.status_code == 403

    def test_place_trade_requires_auth(self):
        resp = client.post("/portfolio/trades", json={
            "ticker": "AAPL", "order_type": "buy", "quantity": 10
        })
        assert resp.status_code == 403

    def test_user_profile_requires_auth(self):
        resp = client.get("/users/me")
        assert resp.status_code == 403

    def test_flags_requires_auth(self):
        resp = client.get("/flags/stock/AAPL")
        assert resp.status_code == 403
