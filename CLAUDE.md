# PageGuard - AI Web Accessibility Compliance Scanner

## WHY THIS PROJECT EXISTS
**The US ADA Title II compliance deadline is April 24, 2026.**
We are building this in February 2026. Thousands of businesses are panicking RIGHT NOW.
95.9% of websites fail basic WCAG requirements. Non-compliance penalties: up to $150,000 per violation.
This is not "nice to have" - it's "fix this or get sued."

## Project Documents
- **BUSINESS_PLAN.md** - 사업계획서 (시장, 수익모델, GTM 전략, 재무전망)
- **prd.md** - Product Requirements Document (기능 명세, 데이터 모델, API 스펙)
- **ROADMAP.md** - 프로젝트 로드맵 (Phase 1-5, 마일스톤, 일정)
- **TECH_STACK.md** - 기술 스택 문서 (아키텍처, 의존성, 스케일링)

## Multi-Agent System
PageGuard includes a multi-agent system (`agents/`) where specialized Claude agents collaborate:

| Agent | File | Role |
|-------|------|------|
| **Orchestrator** | `agents/orchestrator.py` | Coordinates team workflow, delegates tasks |
| **Scanner Agent** | `agents/scanner_agent.py` | Crawls websites, detects WCAG 2.2 violations |
| **Fix Agent** | `agents/fix_agent.py` | Generates code fixes for each violation |
| **Report Agent** | `agents/report_agent.py` | Creates compliance reports & risk assessments |

### Running the Multi-Agent System
```bash
# Direct audit (no API key needed for basic scan)
python -m agents.run https://example.com

# AI-orchestrated audit (requires ANTHROPIC_API_KEY)
python -m agents.run https://example.com --ai-orchestrate

# Single agent mode
python -m agents.run https://example.com --agent scanner
```

### In-App AI Agent
The web app also has a built-in AI agent (`app/agent.py` + `app/agent_routes.py`) accessible at
`/agent/sites/<uid>/agent` that provides executive summaries, prioritized remediation plans,
trend analysis, and interactive Q&A about accessibility issues.

## Revenue Target
- **Goal:** $1,000 MRR (Monthly Recurring Revenue) within 60 days of launch
- **Path:** 13-35 customers at $29-79/month
- **Timeline:** Launch by early March 2026, ride the April deadline panic wave

## What PageGuard Does
1. User enters a website URL
2. PageGuard crawls the site and scans every page for WCAG 2.2 Level AA violations
3. Results show: compliance score (0-100), violations by severity, affected elements
4. AI generates plain-English explanations + actual code fix suggestions
5. Exportable PDF compliance report (for legal/stakeholder use)
6. Ongoing monitoring: scheduled re-scans with email alerts when new issues appear
7. Compliance badge: "Verified Accessible by PageGuard" embed for fixed sites

## Pricing Plans
| Plan | Price | Sites | Scans | Features |
|------|-------|-------|-------|----------|
| Free | $0/mo | 1 | 1 scan | Basic report, 5 pages max |
| Starter | $29/mo | 1 | Weekly | AI fix suggestions, email alerts, full report |
| Pro | $79/mo | 5 | Daily | PDF reports, compliance badge, priority |
| Agency | $199/mo | 20 | Daily | White-label, team access, API, client portal |

## Architecture (v2 - Feb 2026)

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
│  ├─ AI Service (OpenAI, configurable)│
│  ├─ Report (PDF + text)             │
│  ├─ Email (SMTP / console fallback) │
│  ├─ Plan Service (limit enforcement)│
│  └─ Task Runner (async scan jobs)   │
├─────────────────────────────────────┤
│  Middleware:                         │
│  ├─ Rate Limiting (slowapi)         │
│  └─ Security Headers                │
├─────────────────────────────────────┤
│  Database: SQLite (dev) / PG (prod) │
│  Migrations: Alembic                │
└─────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 16 + TypeScript | SSR, App Router, Server Components |
| Styling | Tailwind CSS | Utility-first, no build overhead |
| Backend | FastAPI (Python) | Async I/O, auto API docs, Pydantic validation |
| Database | SQLAlchemy + SQLite/PostgreSQL | Type-safe ORM, easy migration |
| Migrations | Alembic | Schema versioning, safe deployments |
| AI | OpenAI API (configurable model) | Fix suggestions, summaries, Q&A |
| Scanner | BeautifulSoup + requests | HTML parsing, WCAG rule engine |
| Payments | Stripe | Checkout, webhooks, plan management |
| PDF | ReportLab | Professional compliance reports |
| Email | SMTP (smtplib) | Notifications, alerts, password reset |
| Rate Limiting | slowapi | Brute force / abuse protection |
| Security | bcrypt + PyJWT | Password hashing + token auth |

### AI Model Configuration
- Default model: `gpt-5-mini` (configurable via `AI_MODEL` env var)
- Model can be swapped anytime without code changes
- Set in `backend/config.py` → `Settings.AI_MODEL`

## Project Structure
```
/
├── frontend/                # Next.js 16 frontend
│   └── src/
│       ├── app/             # App Router pages
│       │   ├── page.tsx     # Landing (ADA countdown)
│       │   ├── layout.tsx   # Root layout (nav, footer, skip-nav)
│       │   ├── pricing/     # Pricing page (Stripe checkout)
│       │   ├── login/       # Login (functional, JWT)
│       │   ├── signup/      # Signup (functional, JWT)
│       │   ├── privacy/     # Privacy Policy
│       │   ├── terms/       # Terms of Service
│       │   ├── disclaimer/  # Disclaimer (not legal advice)
│       │   └── dashboard/   # Protected dashboard
│       │       └── sites/[uid]/
│       │           ├── page.tsx      # Site detail + scan results
│       │           └── agent/page.tsx # AI Q&A chat
│       ├── components/      # Reusable UI components
│       │   ├── AuthNav.tsx         # Auth-aware navigation
│       │   ├── CountdownTimer.tsx  # ADA deadline countdown
│       │   ├── ScoreCircle.tsx     # Compliance score (aria)
│       │   ├── PricingCard.tsx     # Pricing (Stripe checkout)
│       │   ├── ViolationCard.tsx   # Violation display
│       │   └── Footer.tsx          # Footer (legal links)
│       ├── lib/             # API client, config
│       │   ├── api.ts       # Type-safe FastAPI client
│       │   └── config.ts    # Environment config
│       └── types/           # TypeScript interfaces
│           └── index.ts     # User, Site, Scan, Violation types
├── backend/                 # FastAPI backend
│   ├── main.py              # App entry + middleware + routers
│   ├── config.py            # Env config (AI_MODEL, DB, Stripe, etc.)
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models.py            # SQLAlchemy models (User, Site, Scan, Violation, Subscription)
│   ├── schemas.py           # Pydantic DTOs
│   ├── dependencies.py      # Auth dependency (JWT Bearer)
│   ├── middleware.py         # Rate limiting + security headers
│   ├── routers/
│   │   ├── auth.py          # JWT auth (signup/login/forgot/reset)
│   │   ├── sites.py         # Site CRUD + scan + PDF report
│   │   ├── agent.py         # AI Q&A endpoint
│   │   ├── billing.py       # Stripe checkout/webhooks/portal
│   │   └── account.py       # Profile + password + deletion (GDPR)
│   ├── services/
│   │   ├── scanner.py       # WCAG rules engine (13 rules)
│   │   ├── ai_service.py    # OpenAI (configurable model)
│   │   ├── report.py        # PDF + text report generation
│   │   ├── email_service.py # Email notifications (SMTP)
│   │   ├── plan_service.py  # Plan enforcement (limits)
│   │   ├── task_runner.py   # Background task thread pool
│   │   └── scan_task.py     # Async scan execution
│   ├── alembic/             # Database migrations
│   └── requirements.txt     # Python dependencies
├── agents/                  # Multi-agent CLI system
│   ├── orchestrator.py      # Coordinates team
│   ├── scanner_agent.py     # Crawl + detect
│   ├── fix_agent.py         # Generate fixes
│   ├── report_agent.py      # Compliance reports
│   ├── base.py              # Base agent class
│   ├── constants.py         # Shared configuration
│   └── run.py               # CLI entry point
├── app/                     # Legacy Flask app (27 tests passing)
├── tests/
│   ├── test_app.py          # Flask tests (27 passing)
│   └── test_backend.py      # FastAPI tests
├── CLAUDE.md                # This file - project brain
├── BUSINESS_PLAN.md         # Business plan
├── prd.md                   # Product requirements
├── ROADMAP.md               # Project roadmap
└── TECH_STACK.md            # Tech stack docs
```

## Database Models
- **User:** email, password_hash, name, plan, stripe_customer_id, created_at
- **Site:** uid, url, user_id, name, last_scan_at, compliance_score, created_at
- **Scan:** uid, site_id, status, score, pages_scanned, total/critical/serious/moderate/minor counts, created_at, completed_at
- **Violation:** scan_id, rule_id, rule_name, severity, wcag_criteria, description, element_html, page_url, fix_suggestion, selector
- **Subscription:** user_id, stripe_subscription_id, stripe_price_id, plan, status, current_period_end

## WCAG Rules We Check (13 rules)
| # | Rule ID | WCAG | Severity | What it checks |
|---|---------|------|----------|---------------|
| 1 | `img-alt` | 1.1.1 | critical | Missing alt text on images |
| 2 | `form-label` | 1.3.1 | critical | Missing form labels |
| 3 | `color-contrast` | 1.4.3 | serious | Insufficient color contrast (inline + utility classes) |
| 4 | `html-lang` | 3.1.1 | serious | Missing page language attribute |
| 5 | `page-title` | 2.4.2 | serious | Missing document title |
| 6 | `empty-link` | 2.4.4 | serious | Empty links |
| 7 | `empty-button` | 4.1.2 | serious | Empty buttons |
| 8 | `heading-order` | 1.3.1 | moderate | Missing/skipped heading structure |
| 9 | `skip-nav` | 2.4.1 | moderate | Missing skip navigation link |
| 10 | `landmark-main` | 4.1.2 | moderate | Missing main landmark |
| 11 | `meta-viewport` | 1.4.4 | critical | Zoom disabled by viewport meta |
| 12 | `aria-input-name` / `aria-interactive-name` | 4.1.2 | serious/critical | Interactive ARIA elements missing names |
| 13 | `media-autoplay` | 1.4.2 | serious | Auto-playing media without mute |

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/signup` | Create account |
| POST | `/api/v1/auth/login` | Login, get JWT |
| POST | `/api/v1/auth/forgot-password` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Reset with token |

### Sites & Scans
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/sites` | List user's sites |
| POST | `/api/v1/sites` | Add a site |
| GET | `/api/v1/sites/{uid}` | Get site details |
| DELETE | `/api/v1/sites/{uid}` | Delete site + all data |
| POST | `/api/v1/sites/{uid}/scan` | Start async scan |
| GET | `/api/v1/sites/{uid}/latest-scan` | Get latest scan results |
| GET | `/api/v1/sites/{uid}/report/pdf` | Download PDF report (Pro+) |
| GET | `/api/v1/scans/{uid}` | Poll scan status |

### AI Agent
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/sites/{uid}/agent/ask` | Ask AI about violations |
| GET | `/api/v1/sites/{uid}/agent/summary` | Get executive summary |

### Billing
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/billing/checkout` | Create Stripe checkout |
| POST | `/api/v1/billing/portal` | Open billing portal |
| GET | `/api/v1/billing/subscription` | Get subscription status |
| POST | `/api/v1/billing/webhook` | Stripe webhook handler |

### Account
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/account/me` | Get profile |
| PATCH | `/api/v1/account/me` | Update profile |
| DELETE | `/api/v1/account/me` | Delete account (GDPR) |
| POST | `/api/v1/account/change-password` | Change password |

## Security
- **Auth:** JWT tokens (PyJWT) + bcrypt password hashing
- **Rate Limiting:** slowapi on auth (5/min) and scan (10/min) endpoints
- **Security Headers:** X-Frame-Options, X-Content-Type-Options, XSS Protection, Referrer-Policy
- **Secret Key:** Validated on startup, warns if using dev default
- **CORS:** Configurable allowed origins via FRONTEND_URL env var

## Go-to-Market Strategy
1. **URGENCY MARKETING:** "ADA deadline is April 24. Is your website compliant?"
2. Reddit posts in r/smallbusiness, r/webdev, r/entrepreneur, r/legaladvice
3. Content: "ADA Website Compliance Checklist 2026" (SEO-optimized)
4. Direct outreach to web agencies (they need this for clients)
5. Product Hunt launch
6. Free scan tool as lead magnet → conversion to paid monitoring
7. Compliance badge "Powered by PageGuard" → viral loop

## Competitive Edge
- **Price:** Competitors charge $500+/mo (enterprise). We charge $29-79/mo (SMB).
- **AI Fix Suggestions:** Not just "you have a problem" but "here's exactly how to fix it" with code
- **Simplicity:** Enter URL → get results. No technical knowledge needed.
- **Timing:** ADA deadline creates massive urgency that won't exist after April 2026

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
python -m agents.run https://example.com
python -m agents.run https://example.com --ai-orchestrate
```

## Environment Variables
```bash
# Required
SECRET_KEY=your-secure-key    # REQUIRED in production
DATABASE_URL=sqlite:///./pageguard.db

# AI (for fix suggestions)
OPENAI_API_KEY=your-key
AI_MODEL=gpt-5-mini           # Configurable model

# Frontend
FRONTEND_URL=http://localhost:3000

# Stripe (for billing)
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STARTER=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_AGENCY=price_...

# Email (optional - logs to console if not set)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user
SMTP_PASSWORD=pass
FROM_EMAIL=noreply@pageguard.dev

# Multi-agent CLI only
ANTHROPIC_API_KEY=...
```

## Status
- [x] Market research & timing validation (Feb 2026 - ADA deadline Apr 24)
- [x] Product definition & pricing
- [x] Project setup & core infrastructure
- [x] Database models (User, Site, Scan, Violation, Subscription)
- [x] Auth system - JWT (signup/login/forgot/reset password)
- [x] Accessibility scanner engine (13 WCAG rules, multi-page crawling)
- [x] AI fix suggestions (OpenAI API + rule-based fallback)
- [x] Dashboard & scan results UI (functional, data-driven)
- [x] Landing page (ADA urgency-focused with deadline countdown)
- [x] Stripe billing (checkout, webhooks, subscription management)
- [x] Plan enforcement (site limits, scan limits, feature gating)
- [x] PDF compliance reports (ReportLab, Pro plan feature)
- [x] Email notifications (welcome, scan complete, password reset)
- [x] Background async scanning (non-blocking, ThreadPoolExecutor)
- [x] Rate limiting + security headers middleware
- [x] Account management + deletion (GDPR right to erasure)
- [x] Legal pages (Privacy Policy, Terms of Service, Disclaimer)
- [x] Frontend accessibility (skip nav, aria labels, focus styles)
- [x] REST API (full CRUD + scan + report + agent + billing)
- [x] Tests (Flask: 27 passing + FastAPI backend tests)
- [x] Multi-agent CLI system (orchestrator, scanner, fix, report agents)
- [x] Architecture v2: Next.js 16 frontend (11 routes, builds clean)
- [x] Architecture v2: FastAPI backend (full feature set)
- [x] Alembic database migrations
- [ ] Deploy to Railway/Render
- [ ] Domain setup (pageguard.dev)
- [ ] Stripe live keys configuration
- [ ] Product Hunt launch
- [ ] Content marketing: "ADA Website Compliance Checklist 2026"
