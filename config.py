import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///pageguard.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

    # Stripe
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_STARTER = os.environ.get("STRIPE_PRICE_STARTER", "")
    STRIPE_PRICE_PRO = os.environ.get("STRIPE_PRICE_PRO", "")
    STRIPE_PRICE_AGENCY = os.environ.get("STRIPE_PRICE_AGENCY", "")

    # Mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@pageguard.dev")

    # App
    APP_NAME = "PageGuard"
    APP_URL = os.environ.get("APP_URL", "http://localhost:5000")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Scanner
    SCAN_MAX_PAGES_FREE = 5
    SCAN_MAX_PAGES_PAID = 50
    SCAN_TIMEOUT = 30  # seconds per page

    # Plan limits
    PLAN_LIMITS = {
        "free": {"sites": 1, "scans_per_month": 1, "max_pages": 5, "ai_fixes": False, "pdf_report": False},
        "starter": {"sites": 1, "scans_per_month": 4, "max_pages": 50, "ai_fixes": True, "pdf_report": True},
        "pro": {"sites": 5, "scans_per_month": 30, "max_pages": 50, "ai_fixes": True, "pdf_report": True},
        "agency": {"sites": 20, "scans_per_month": -1, "max_pages": 100, "ai_fixes": True, "pdf_report": True},
    }
