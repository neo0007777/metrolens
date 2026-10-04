import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_standard_v1():
    res = client.post("/api/v1/auth/login", json={"email": "officer@gov.in", "password": "password"})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["role"] == "INSPECTOR"

def test_login_admin_dynamic_role():
    res = client.post("/api/v1/auth/login", json={"email": "admin@gov.in", "password": "password"})
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["role"] == "ADMIN"

def test_login_direct_route():
    # Direct legacy mount without /api/v1 prefix
    res = client.post("/auth/login", json={"email": "officer@gov.in", "password": "password"})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data

def test_login_double_slash_normalization():
    # Double slash like https://domain.com//auth/login
    res = client.post("http://testserver//auth/login", json={"email": "officer@gov.in", "password": "password"})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data

def test_demo_token_protected_endpoints():
    # Demo tokens should be accepted by protected endpoints
    res = client.get("/api/v1/dashboard/stats", headers={"Authorization": "Bearer demo-officer-token"})
    assert res.status_code == 200

    res2 = client.get("/dashboard/stats", headers={"Authorization": "Bearer demo-jwt-token-admin"})
    assert res2.status_code == 200
