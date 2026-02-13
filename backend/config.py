import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "PageGuard API"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pageguard.db")
    
    # OpenAI - model is configurable!
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-5-mini")
    
    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    
    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_IDS: dict = {
        "starter": os.getenv("STRIPE_PRICE_STARTER", "price_starter"),
        "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro"),
        "agency": os.getenv("STRIPE_PRICE_AGENCY", "price_agency"),
    }
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@pageguard.dev")

    # Scanner
    SCAN_TIMEOUT: int = int(os.getenv("SCAN_TIMEOUT", "30"))
    
    # Plan limits
    # scan_interval_hours: 0 = no auto-scan, 168 = weekly, 24 = daily
    PLAN_LIMITS: dict = {
        "free": {"sites": 1, "scans_per_month": 1, "max_pages": 5, "ai_fixes": False, "scan_interval_hours": 0},
        "starter": {"sites": 1, "scans_per_month": 4, "max_pages": 50, "ai_fixes": True, "scan_interval_hours": 168},
        "pro": {"sites": 5, "scans_per_month": 30, "max_pages": 50, "ai_fixes": True, "scan_interval_hours": 24},
        "agency": {"sites": 20, "scans_per_month": -1, "max_pages": 100, "ai_fixes": True, "scan_interval_hours": 24},
    }


    def validate(self):
        """Validate critical settings. Call on startup."""
        if not self.SECRET_KEY:
            import warnings
            warnings.warn("SECRET_KEY not set! Using insecure default for development only.")
            self.SECRET_KEY = "dev-only-insecure-key-do-not-use-in-production"


settings = Settings()
