import pytest
from uuid import uuid4


@pytest.fixture
def mock_user():
    return {
        "id": str(uuid4()),
        "email": "test@prestocks.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": "$2b$12$mock_hash",
    }


@pytest.fixture
def mock_portfolio(mock_user):
    return {
        "id": str(uuid4()),
        "user_id": mock_user["id"],
        "cash_balance": 100_000.00,
        "total_value": 100_000.00,
    }


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer mock_test_token"}
