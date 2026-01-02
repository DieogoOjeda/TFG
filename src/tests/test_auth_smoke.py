# tests/test_auth_smoke.py
from tests.conftest import auth_headers


def test_login_ok_returns_token(client, student_user):
    r = client.post("/auth/login", json={"email": student_user.email, "password": "pass123456"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data.get("token_type", "bearer") == "bearer"


def test_login_wrong_password_401(client, student_user):
    r = client.post("/auth/login", json={"email": student_user.email, "password": "WRONG"})
    assert r.status_code == 401


def test_me_requires_auth_401(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_me_ok_with_token(client, student_token):
    r = client.get("/auth/me", headers=auth_headers(student_token))
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "student@example.com"
