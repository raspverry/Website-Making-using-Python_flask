# ---- Backend (FastAPI) ----
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies for lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libxml2-dev libxslt-dev && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY backend/ ./backend/

# Create data directory for SQLite (dev mode)
RUN mkdir -p /app/data

ENV DATABASE_URL=sqlite:////app/data/pageguard.db
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "backend.main:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120"]
