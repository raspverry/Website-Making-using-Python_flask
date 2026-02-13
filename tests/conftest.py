import pytest
from app import create_app, db as _db


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "localhost"
    APP_URL = "http://localhost"
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
    APP_NAME = "TestiFlow"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    PLAN_LIMITS = {
        "free": {"spaces": 1, "testimonials_per_space": 10, "widgets": ["wall"], "branding": True},
        "starter": {"spaces": 3, "testimonials_per_space": 50, "widgets": ["wall", "carousel", "badge"], "branding": False},
        "pro": {"spaces": 10, "testimonials_per_space": -1, "widgets": ["wall", "carousel", "badge", "slider"], "branding": False},
        "agency": {"spaces": -1, "testimonials_per_space": -1, "widgets": ["wall", "carousel", "badge", "slider"], "branding": False},
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
