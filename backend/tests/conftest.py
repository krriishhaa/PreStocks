"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
    os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret-key"
    from app.main import create_app
    return create_app()


@pytest.fixture(scope="session")
def client(app):
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """Get a valid auth token for tests."""
    client.post("/auth/register", json={
        "email": "fixture@test.io", "password": "FixtureTest123!", "full_name": "Fixture User"
    })
    resp = client.post("/auth/login", json={"email": "fixture@test.io", "password": "FixtureTest123!"})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return "mock-token"


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
