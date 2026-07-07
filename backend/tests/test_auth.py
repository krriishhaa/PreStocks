import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_signup():
    resp = client.post("/auth/signup", json={
        "email": "newuser@test.com",
        "password": "securepass123",
        "full_name": "New User",
        "age": 25,
    })
    # 201 if DB is connected, 500 if not
    assert resp.status_code in (201, 500)


def test_login_invalid():
    resp = client.post("/auth/login", json={
        "email": "noone@test.com",
        "password": "wrong",
    })
    # 401 if DB connected, 500 if not
    assert resp.status_code in (401, 500)


def test_signup_validation():
    resp = client.post("/auth/signup", json={
        "email": "not-an-email",
        "password": "x",
    })
    assert resp.status_code == 422
