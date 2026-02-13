from app.models import User, Site, Scan, Violation
from app.scanner import check_page, run_scan, calculate_score, ScanResult


# --- Landing & Auth Pages ---

def test_landing_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"PageGuard" in resp.data
    assert b"ADA" in resp.data


def test_pricing_page(client):
    resp = client.get("/pricing")
    assert resp.status_code == 200
    assert b"$29" in resp.data
    assert b"$79" in resp.data
    assert b"$199" in resp.data


def test_signup_page(client):
    resp = client.get("/auth/signup")
    assert resp.status_code == 200
    assert b"Start your free scan" in resp.data


def test_login_page(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200
    assert b"Welcome back" in resp.data


# --- Auth Flows ---

def test_signup_flow(client, db):
    resp = client.post("/auth/signup", data={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "password_confirm": "password123",
    }, follow_redirects=True)
    assert resp.status_code == 200

    user = User.query.filter_by(email="test@example.com").first()
    assert user is not None
    assert user.plan == "free"


def test_signup_validation(client):
    resp = client.post("/auth/signup", data={
        "name": "T",
        "email": "test@example.com",
        "password": "short",
        "password_confirm": "short",
    }, follow_redirects=True)
    assert b"at least 8 characters" in resp.data


def test_login_flow(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    resp = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "password123",
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_login_invalid(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    resp = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "wrong",
    }, follow_redirects=True)
    assert b"Invalid email or password" in resp.data


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard/", follow_redirects=False)
    assert resp.status_code == 302


# --- Site Management ---

def test_add_site(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    client.post("/auth/login", data={"email": "test@example.com", "password": "password123"})

    resp = client.get("/dashboard/sites/add")
    assert resp.status_code == 200


def test_free_plan_site_limit(client, db):
    user = User(name="Test", email="test@example.com", plan="free")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Add one site manually
    site = Site(url="https://example.com", name="Example", user_id=user.id)
    db.session.add(site)
    db.session.commit()

    client.post("/auth/login", data={"email": "test@example.com", "password": "password123"})

    # Try to add another - should be blocked
    resp = client.post("/dashboard/sites/add", data={
        "url": "https://another.com",
        "name": "Another",
    }, follow_redirects=True)

    assert Site.query.filter_by(user_id=user.id).count() == 1


# --- Scanner Engine ---

def test_scanner_missing_alt(app):
    html = '<html lang="en"><head><title>Test</title></head><body><main><img src="photo.jpg"></main></body></html>'
    result = check_page("https://example.com", html)
    rule_ids = [v.rule_id for v in result.violations]
    assert "img-alt" in rule_ids


def test_scanner_valid_alt(app):
    html = '<html lang="en"><head><title>Test</title></head><body><main><img src="photo.jpg" alt="A photo"></main></body></html>'
    result = check_page("https://example.com", html)
    rule_ids = [v.rule_id for v in result.violations]
    assert "img-alt" not in rule_ids


def test_scanner_missing_lang(app):
    html = '<html><head><title>Test</title></head><body><main><h1>Hello</h1></main></body></html>'
    result = check_page("https://example.com", html)
    rule_ids = [v.rule_id for v in result.violations]
    assert "html-lang" in rule_ids


def test_scanner_missing_title(app):
    html = '<html lang="en"><head></head><body><main><h1>Hello</h1></main></body></html>'
    result = check_page("https://example.com", html)
    rule_ids = [v.rule_id for v in result.violations]
    assert "page-title" in rule_ids


def test_scanner_missing_form_label(app):
    html = '<html lang="en"><head><title>Test</title></head><body><main><form><input type="text" name="email"></form></main></body></html>'
    result = check_page("https://example.com", html)
    rule_ids = [v.rule_id for v in result.violations]
    assert "form-label" in rule_ids


def test_scanner_valid_form_label(app):
    html = '<html lang="en"><head><title>Test</title></head><body><main><form><label for="email">Email</label><input type="text" id="email" name="email"></form></main></body></html>'
    result = check_page("https://example.com", html)
    rule_ids = [v.rule_id for v in result.violations]
    assert "form-label" not in rule_ids


def test_scanner_empty_link(app):
    html = '<html lang="en"><head><title>Test</title></head><body><main><a href="/page"></a></main></body></html>'
    result = check_page("https://example.com", html)
    rule_ids = [v.rule_id for v in result.violations]
    assert "empty-link" in rule_ids


def test_scanner_empty_button(app):
    html = '<html lang="en"><head><title>Test</title></head><body><main><button></button></main></body></html>'
    result = check_page("https://example.com", html)
    rule_ids = [v.rule_id for v in result.violations]
    assert "empty-button" in rule_ids


def test_scanner_zoom_disabled(app):
    html = '<html lang="en"><head><title>Test</title><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"></head><body><main><h1>Hi</h1></main></body></html>'
    result = check_page("https://example.com", html)
    rule_ids = [v.rule_id for v in result.violations]
    assert "meta-viewport" in rule_ids


def test_scanner_heading_skip(app):
    html = '<html lang="en"><head><title>Test</title></head><body><main><h1>Title</h1><h3>Skipped h2</h3></main></body></html>'
    result = check_page("https://example.com", html)
    rule_ids = [v.rule_id for v in result.violations]
    assert "heading-order" in rule_ids


def test_score_calculation():
    result = ScanResult(critical_count=2, serious_count=1, moderate_count=3, minor_count=2, total_violations=8)
    score = calculate_score(result)
    # 2*15 + 1*8 + 3*3 + 2*1 = 30 + 8 + 9 + 2 = 49 penalty
    assert score == 51


def test_score_perfect():
    result = ScanResult(total_violations=0)
    assert calculate_score(result) == 100


# --- API ---

def test_api_no_site(client):
    resp = client.get("/api/v1/sites/nonexistent/latest-scan")
    assert resp.status_code == 404


def test_api_no_scan(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    site = Site(url="https://example.com", name="Example", user_id=user.id)
    db.session.add(site)
    db.session.commit()

    resp = client.get(f"/api/v1/sites/{site.uid}/latest-scan")
    assert resp.status_code == 404


def test_api_with_scan(client, db):
    user = User(name="Test", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    site = Site(url="https://example.com", name="Example", user_id=user.id)
    db.session.add(site)
    db.session.commit()

    scan = Scan(site_id=site.id, status="completed", score=75, pages_scanned=3, total_violations=5, critical_count=1, serious_count=2, moderate_count=1, minor_count=1)
    db.session.add(scan)
    db.session.commit()

    v = Violation(scan_id=scan.id, rule_id="img-alt", rule_name="Missing alt", severity="critical", wcag_criteria="1.1.1", description="Missing alt text", page_url="https://example.com")
    db.session.add(v)
    db.session.commit()

    resp = client.get(f"/api/v1/sites/{site.uid}/latest-scan")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["scan"]["score"] == 75
    assert len(data["violations"]) == 1


# --- User Model ---

def test_user_model(db, app):
    with app.app_context():
        user = User(name="Test", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        assert user.check_password("password123")
        assert not user.check_password("wrong")
        assert user.plan == "free"
        assert user.can_add_site()
        assert not user.has_ai_fixes()
