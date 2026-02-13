import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///testiflow.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Stripe
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    # Stripe Price IDs
    STRIPE_PRICE_STARTER = os.environ.get("STRIPE_PRICE_STARTER", "")
    STRIPE_PRICE_PRO = os.environ.get("STRIPE_PRICE_PRO", "")
    STRIPE_PRICE_AGENCY = os.environ.get("STRIPE_PRICE_AGENCY", "")

    # Mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@testiflow.com")

    # App
    APP_NAME = "TestiFlow"
    APP_URL = os.environ.get("APP_URL", "http://localhost:5000")

    # Upload
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload

    # Plan limits
    PLAN_LIMITS = {
        "free": {"spaces": 1, "testimonials_per_space": 10, "widgets": ["wall"], "branding": True},
        "starter": {"spaces": 3, "testimonials_per_space": 50, "widgets": ["wall", "carousel", "badge"], "branding": False},
        "pro": {"spaces": 10, "testimonials_per_space": -1, "widgets": ["wall", "carousel", "badge", "slider"], "branding": False},
        "agency": {"spaces": -1, "testimonials_per_space": -1, "widgets": ["wall", "carousel", "badge", "slider"], "branding": False},
    }
