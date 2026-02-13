import pytest
from app import create_app, db as _db


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "localhost"
    APP_URL = "http://localhost"
    OPENAI_API_KEY = ""
    STRIPE_SECRET_KEY = ""
    STRIPE_PUBLISHABLE_KEY = ""
    STRIPE_WEBHOOK_SECRET = ""
    STRIPE_PRICE_STARTER = "price_test_starter"
    STRIPE_PRICE_PRO = "price_test_pro"
    STRIPE_PRICE_AGENCY = "price_test_agency"
    MAIL_SERVER = "localhost"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = "test@test.com"
    APP_NAME = "PageGuard"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    SCAN_MAX_PAGES_FREE = 5
    SCAN_MAX_PAGES_PAID = 50
    SCAN_TIMEOUT = 10
    PLAN_LIMITS = {
        "free": {"sites": 1, "scans_per_month": 1, "max_pages": 5, "ai_fixes": False, "pdf_report": False},
        "starter": {"sites": 1, "scans_per_month": 4, "max_pages": 50, "ai_fixes": True, "pdf_report": True},
        "pro": {"sites": 5, "scans_per_month": 30, "max_pages": 50, "ai_fixes": True, "pdf_report": True},
        "agency": {"sites": 20, "scans_per_month": -1, "max_pages": 100, "ai_fixes": True, "pdf_report": True},
    }


@pytest.fixture(scope="function")
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db
