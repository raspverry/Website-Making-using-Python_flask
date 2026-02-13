import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from backend.config import settings
from backend.database import Base, engine
from backend.middleware import limiter, rate_limit_handler, SecurityHeadersMiddleware
from backend.routers import sites, agent, auth, billing, account

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

# Validate critical settings on startup
settings.validate()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(sites.router)
app.include_router(agent.router)
app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(account.router)

# Create tables
Base.metadata.create_all(bind=engine)

# Start scheduled scan background thread
from backend.services.scheduler import start_scheduler
start_scheduler()


@app.get("/")
def root():
    return {"name": settings.PROJECT_NAME, "version": settings.VERSION}


@app.get("/health")
def health():
    return {"status": "ok"}
