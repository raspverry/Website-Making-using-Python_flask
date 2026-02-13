"""Tests for FastAPI backend API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import Base, get_db
from backend.middleware import limiter


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

# Disable rate limiting for tests
limiter.enabled = False


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


class TestPlanEnforcement:
    def _setup_user(self, plan="free"):
        """Create user and return token."""
        import time
        email = f"plan-{plan}-{time.time()}@example.com"
        res = client.post("/api/v1/auth/signup", json={
            "email": email, "password": "password123", "name": "Plan User"
        })
        token = res.json()["access_token"]
        # Update plan directly in DB if not free
        if plan != "free":
            from backend.models import User
            db = TestSession()
            user = db.query(User).filter(User.email == email).first()
            user.plan = plan
            db.commit()
            db.close()
        return token

    def test_free_plan_site_limit(self):
        token = self._setup_user("free")
        headers = {"Authorization": f"Bearer {token}"}
        # Free plan allows 1 site
        res1 = client.post("/api/v1/sites", json={"url": "https://example1.com"}, headers=headers)
        assert res1.status_code == 200
        # Second site should fail
        res2 = client.post("/api/v1/sites", json={"url": "https://example2.com"}, headers=headers)
        assert res2.status_code == 403

    def test_pro_plan_allows_more_sites(self):
        token = self._setup_user("pro")
        headers = {"Authorization": f"Bearer {token}"}
        for i in range(5):
            res = client.post("/api/v1/sites", json={"url": f"https://site{i}.com"}, headers=headers)
            assert res.status_code == 200


class TestScanEndpoint:
    def _setup(self):
        import time
        email = f"scan-{time.time()}@example.com"
        res = client.post("/api/v1/auth/signup", json={
            "email": email, "password": "password123", "name": "Scan User"
        })
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        site_res = client.post("/api/v1/sites", json={"url": "https://example.com"}, headers=headers)
        site_uid = site_res.json()["uid"]
        return headers, site_uid

    def test_start_scan_returns_pending(self):
        headers, site_uid = self._setup()
        res = client.post(f"/api/v1/sites/{site_uid}/scan", headers=headers)
        assert res.status_code == 200
        assert res.json()["status"] in ("pending", "running")

    def test_scan_nonexistent_site(self):
        import time
        email = f"noscan-{time.time()}@example.com"
        res = client.post("/api/v1/auth/signup", json={
            "email": email, "password": "password123", "name": "User"
        })
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        res = client.post("/api/v1/sites/nonexistent/scan", headers=headers)
        assert res.status_code == 404


class TestAccountManagement:
    def _create_user(self):
        import time
        email = f"acct-{time.time()}@example.com"
        res = client.post("/api/v1/auth/signup", json={
            "email": email, "password": "password123", "name": "Account User"
        })
        return res.json()["access_token"], email

    def test_get_profile(self):
        token, email = self._create_user()
        res = client.get("/api/v1/account/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["email"] == email

    def test_update_name(self):
        token, _ = self._create_user()
        res = client.patch("/api/v1/account/me",
            json={"name": "New Name"},
            headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["name"] == "New Name"

    def test_change_password(self):
        token, _ = self._create_user()
        res = client.post("/api/v1/account/change-password",
            json={"current_password": "password123", "new_password": "newpassword456"},
            headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200

    def test_delete_account(self):
        token, _ = self._create_user()
        res = client.delete("/api/v1/account/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        # Verify can't access anymore
        res2 = client.get("/api/v1/account/me", headers={"Authorization": f"Bearer {token}"})
        assert res2.status_code == 401


class TestScanner:
    """Test the WCAG scanner engine directly."""

    def test_missing_alt(self):
        from backend.services.scanner import check_page
        html = '<html lang="en"><head><title>Test</title></head><body><main><img src="x.jpg"></main></body></html>'
        result = check_page("https://test.com", html)
        rule_ids = [v.rule_id for v in result.violations]
        assert "img-alt" in rule_ids

    def test_valid_alt(self):
        from backend.services.scanner import check_page
        html = '<html lang="en"><head><title>Test</title></head><body><main><img src="x.jpg" alt="A photo"></main></body></html>'
        result = check_page("https://test.com", html)
        rule_ids = [v.rule_id for v in result.violations]
        assert "img-alt" not in rule_ids

    def test_missing_lang(self):
        from backend.services.scanner import check_page
        html = '<html><head><title>Test</title></head><body><main><p>Hello</p></main></body></html>'
        result = check_page("https://test.com", html)
        rule_ids = [v.rule_id for v in result.violations]
        assert "html-lang" in rule_ids

    def test_missing_form_label(self):
        from backend.services.scanner import check_page
        html = '<html lang="en"><head><title>Test</title></head><body><main><input type="text"></main></body></html>'
        result = check_page("https://test.com", html)
        rule_ids = [v.rule_id for v in result.violations]
        assert "form-label" in rule_ids

    def test_empty_button(self):
        from backend.services.scanner import check_page
        html = '<html lang="en"><head><title>Test</title></head><body><main><button></button></main></body></html>'
        result = check_page("https://test.com", html)
        rule_ids = [v.rule_id for v in result.violations]
        assert "empty-button" in rule_ids

    def test_missing_title(self):
        from backend.services.scanner import check_page
        html = '<html lang="en"><head></head><body><main><h1>Hello</h1></main></body></html>'
        result = check_page("https://test.com", html)
        rule_ids = [v.rule_id for v in result.violations]
        assert "page-title" in rule_ids

    def test_valid_form_label(self):
        from backend.services.scanner import check_page
        html = '<html lang="en"><head><title>Test</title></head><body><main><form><label for="email">Email</label><input type="text" id="email" name="email"></form></main></body></html>'
        result = check_page("https://test.com", html)
        rule_ids = [v.rule_id for v in result.violations]
        assert "form-label" not in rule_ids

    def test_empty_link(self):
        from backend.services.scanner import check_page
        html = '<html lang="en"><head><title>Test</title></head><body><main><a href="/page"></a></main></body></html>'
        result = check_page("https://test.com", html)
        rule_ids = [v.rule_id for v in result.violations]
        assert "empty-link" in rule_ids

    def test_zoom_disabled(self):
        from backend.services.scanner import check_page
        html = '<html lang="en"><head><title>Test</title><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"></head><body><main><h1>Hi</h1></main></body></html>'
        result = check_page("https://test.com", html)
        rule_ids = [v.rule_id for v in result.violations]
        assert "meta-viewport" in rule_ids

    def test_heading_skip(self):
        from backend.services.scanner import check_page
        html = '<html lang="en"><head><title>Test</title></head><body><main><h1>Title</h1><h3>Skipped h2</h3></main></body></html>'
        result = check_page("https://test.com", html)
        rule_ids = [v.rule_id for v in result.violations]
        assert "heading-order" in rule_ids

    def test_score_calculation(self):
        from backend.services.scanner import ScanResult, calculate_score
        result = ScanResult(total_violations=0)
        assert calculate_score(result) == 100

        result2 = ScanResult(total_violations=3, critical_count=1, serious_count=1, moderate_count=1)
        score = calculate_score(result2)
        assert 0 <= score <= 100
        assert score < 100

    def test_score_exact(self):
        from backend.services.scanner import ScanResult, calculate_score
        result = ScanResult(critical_count=2, serious_count=1, moderate_count=3, minor_count=2, total_violations=8)
        score = calculate_score(result)
        # 2*15 + 1*8 + 3*3 + 2*1 = 30 + 8 + 9 + 2 = 49 penalty
        assert score == 51


class TestPDFReport:
    def test_generate_pdf(self):
        from backend.services.report import generate_pdf_report
        scan_data = {
            "score": 72, "pages_scanned": 3, "total_violations": 5,
            "critical_count": 1, "serious_count": 2, "moderate_count": 1, "minor_count": 1,
        }
        violations = [
            {"severity": "critical", "rule_name": "Missing alt text", "wcag_criteria": "1.1.1",
             "page_url": "https://example.com", "description": "Image missing alt",
             "element_html": "<img src='x.jpg'>", "fix_suggestion": "Add alt attribute"},
        ]
        pdf_bytes = generate_pdf_report("https://example.com", scan_data, violations)
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:5] == b"%PDF-"

    def test_generate_text_report(self):
        from backend.services.report import generate_text_report
        scan_data = {"score": 85, "pages_scanned": 1, "total_violations": 2,
                     "critical_count": 0, "serious_count": 1, "moderate_count": 1, "minor_count": 0}
        text = generate_text_report("https://example.com", scan_data, [])
        assert "PageGuard" in text
        assert "85" in text
