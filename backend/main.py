import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import Base, engine
from backend.routers import sites, agent, auth

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
)

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

# Create tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"name": settings.PROJECT_NAME, "version": settings.VERSION}


@app.get("/health")
def health():
    return {"status": "ok"}
