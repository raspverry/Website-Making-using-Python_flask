"""Tests for FastAPI backend API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import Base, get_db


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_pageguard.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


client = TestClient(app)


class TestHealth:
    def test_root(self):
        res = client.get("/")
        assert res.status_code == 200
        assert "PageGuard" in res.json()["name"]

    def test_health(self):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


class TestAuth:
    def test_signup_success(self):
        res = client.post("/api/v1/auth/signup", json={
            "email": "test@example.com", "password": "password123", "name": "Test User"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["plan"] == "free"

    def test_signup_duplicate_email(self):
        client.post("/api/v1/auth/signup", json={
            "email": "dupe@example.com", "password": "password123", "name": "User 1"
        })
        res = client.post("/api/v1/auth/signup", json={
            "email": "dupe@example.com", "password": "password456", "name": "User 2"
        })
        assert res.status_code == 409

    def test_signup_short_password(self):
        res = client.post("/api/v1/auth/signup", json={
            "email": "test@example.com", "password": "short", "name": "Test"
        })
        assert res.status_code == 400

    def test_login_success(self):
        client.post("/api/v1/auth/signup", json={
            "email": "login@example.com", "password": "password123", "name": "Login User"
        })
        res = client.post("/api/v1/auth/login", json={
            "email": "login@example.com", "password": "password123"
        })
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_login_invalid_password(self):
        client.post("/api/v1/auth/signup", json={
            "email": "invalid@example.com", "password": "password123", "name": "User"
        })
        res = client.post("/api/v1/auth/login", json={
            "email": "invalid@example.com", "password": "wrongpassword"
        })
        assert res.status_code == 401

    def test_login_nonexistent_user(self):
        res = client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com", "password": "password123"
        })
        assert res.status_code == 401


class TestSites:
    def _get_token(self):
        res = client.post("/api/v1/auth/signup", json={
            "email": "sites@example.com", "password": "password123", "name": "Site User"
        })
        return res.json()["access_token"]

    def test_create_site(self):
        token = self._get_token()
        res = client.post("/api/v1/sites", json={"url": "https://example.com"},
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["url"] == "https://example.com"

    def test_list_sites(self):
        token = self._get_token()
        client.post("/api/v1/sites", json={"url": "https://example.com"},
                    headers={"Authorization": f"Bearer {token}"})
        res = client.get("/api/v1/sites", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_get_site(self):
        token = self._get_token()
        create_res = client.post("/api/v1/sites", json={"url": "https://example.com"},
                                headers={"Authorization": f"Bearer {token}"})
        uid = create_res.json()["uid"]
        res = client.get(f"/api/v1/sites/{uid}", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["uid"] == uid

    def test_site_not_found(self):
        token = self._get_token()
        res = client.get("/api/v1/sites/nonexistent", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 404

    def test_sites_require_auth(self):
        res = client.get("/api/v1/sites")
        assert res.status_code == 401

    def test_create_site_no_auth(self):
        res = client.post("/api/v1/sites", json={"url": "https://example.com"})
        assert res.status_code == 401


class TestAgent:
    def test_agent_requires_auth(self):
        res = client.post("/api/v1/sites/abc/agent/ask", json={"question": "test"})
        assert res.status_code == 401
