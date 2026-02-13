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
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    
    # Stripe / LemonSqueezy
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Scanner
    SCAN_TIMEOUT: int = int(os.getenv("SCAN_TIMEOUT", "30"))
    
    # Plan limits
    PLAN_LIMITS: dict = {
        "free": {"sites": 1, "scans_per_month": 1, "max_pages": 5, "ai_fixes": False},
        "starter": {"sites": 1, "scans_per_month": 4, "max_pages": 50, "ai_fixes": True},
        "pro": {"sites": 5, "scans_per_month": 30, "max_pages": 50, "ai_fixes": True},
        "agency": {"sites": 20, "scans_per_month": -1, "max_pages": 100, "ai_fixes": True},
    }


settings = Settings()
