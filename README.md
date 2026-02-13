# PageGuard - AI Web Accessibility Compliance Scanner

**The ADA Title II deadline is April 24, 2026.** 95.9% of websites fail basic WCAG requirements. Non-compliance penalties: up to $150,000 per violation. PageGuard scans your website and tells you exactly what to fix.

## What PageGuard Does

1. Enter your website URL
2. AI scans every page for WCAG 2.2 Level AA violations
3. Get a compliance score (0-100) with severity breakdown
4. AI generates code fix suggestions you can copy and paste
5. Schedule ongoing monitoring with email alerts

## Architecture

```
┌─────────────────────────────────────┐
│         Next.js 16 Frontend         │
│   (TypeScript, Tailwind, App Router)│
│         localhost:3000              │
└──────────────┬──────────────────────┘
               │ REST API
┌──────────────▼──────────────────────┐
│         FastAPI Backend             │
│   (Python 3.11, SQLAlchemy, async)  │
│         localhost:8000              │
├─────────────────────────────────────┤
│  Services:                          │
│  ├─ Scanner (WCAG rules engine)     │
│  ├─ AI Service (OpenAI, gpt-5-mini)│
│  └─ Report (compliance reports)     │
├─────────────────────────────────────┤
│  Database: SQLite (dev) / PG (prod) │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│     Multi-Agent CLI (agents/)       │
│  Orchestrator → Scanner → Fixer    │
│                → Reporter           │
└─────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 16 + TypeScript | SSR, App Router, Server Components |
| Styling | Tailwind CSS | Utility-first, no build overhead |
| Backend | FastAPI (Python) | Async I/O, auto API docs, Pydantic validation |
| Database | SQLAlchemy + SQLite/PostgreSQL | Type-safe ORM, easy migration |
| AI | OpenAI API (`gpt-5-mini`, configurable) | Fix suggestions, summaries, Q&A |
| Scanner | BeautifulSoup + requests | HTML parsing, WCAG rule engine |

## Quick Start

### Frontend (Next.js 16)

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Backend (FastAPI)

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs (Swagger API docs)
```

### Multi-Agent CLI

```bash
# Direct scan (no API key needed)
python -m agents.run https://example.com

# AI-orchestrated (requires ANTHROPIC_API_KEY)
python -m agents.run https://example.com --ai-orchestrate
```

## Environment Variables

```bash
# AI (model is configurable - swap anytime)
OPENAI_API_KEY=your-key
AI_MODEL=gpt-5-mini

# Backend
DATABASE_URL=sqlite:///./pageguard.db
SECRET_KEY=change-in-production
FRONTEND_URL=http://localhost:3000

# Stripe
STRIPE_SECRET_KEY=sk_...
```

## Project Structure

```
/
├── frontend/                # Next.js 16 frontend
│   └── src/
│       ├── app/             # App Router pages
│       │   ├── page.tsx     # Landing (ADA countdown)
│       │   ├── pricing/     # Pricing page
│       │   ├── login/       # Auth pages
│       │   ├── signup/
│       │   └── dashboard/   # Protected dashboard
│       │       └── sites/[uid]/
│       │           ├── page.tsx      # Site detail
│       │           └── agent/page.tsx # AI Q&A
│       ├── components/      # Reusable UI
│       ├── lib/             # API client, config
│       └── types/           # TypeScript interfaces
├── backend/                 # FastAPI backend
│   ├── main.py              # App entry + CORS + routers
│   ├── config.py            # Env config (AI_MODEL etc.)
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic DTOs
│   ├── routers/
│   │   ├── sites.py         # Site CRUD + scan
│   │   ├── agent.py         # AI Q&A endpoint
│   │   └── auth.py          # Authentication
│   └── services/
│       ├── scanner.py       # WCAG rules engine (10 rules)
│       ├── ai_service.py    # OpenAI (configurable model)
│       └── report.py        # Report generation
├── agents/                  # Multi-agent CLI
│   ├── orchestrator.py      # Coordinates team
│   ├── scanner_agent.py     # Crawl + detect
│   ├── fix_agent.py         # Generate fixes
│   ├── report_agent.py      # Compliance reports
│   ├── base.py              # Base agent class
│   └── constants.py         # Shared configuration
├── app/                     # Legacy Flask app (27 tests passing)
├── tests/                   # pytest test suite
├── CLAUDE.md                # Project brain
├── BUSINESS_PLAN.md         # Business plan
├── prd.md                   # Product requirements
├── ROADMAP.md               # Project roadmap
└── TECH_STACK.md            # Tech stack docs
```

## WCAG Rules Checked (10 rules)

| Rule | WCAG | Severity |
|------|------|----------|
| Missing alt text | 1.1.1 | Critical |
| Missing form labels | 1.3.1 | Critical |
| Zoom disabled | 1.4.4 | Critical |
| Missing page language | 3.1.1 | Serious |
| Missing document title | 2.4.2 | Serious |
| Empty links | 2.4.4 | Serious |
| Empty buttons | 4.1.2 | Serious |
| Heading structure | 1.3.1 | Moderate |
| Skip navigation | 2.4.1 | Moderate |
| Main landmark | 4.1.2 | Moderate |

## Pricing Plans

| Plan | Price | Sites | Key Features |
|------|-------|-------|-------------|
| Free | $0/mo | 1 | Basic scan, 5 pages |
| Starter | $29/mo | 1 | AI fixes, weekly scans, email alerts |
| Pro | $79/mo | 5 | Daily scans, PDF reports, badge |
| Agency | $199/mo | 20 | White-label, API, unlimited scans |

**Target:** $1,000 MRR within 60 days of launch.
