# PageGuard - AI Web Accessibility Compliance Scanner

## WHY THIS PROJECT EXISTS
**The US ADA Title II compliance deadline is April 24, 2026.**
We are building this in February 2026. Thousands of businesses are panicking RIGHT NOW.
95.9% of websites fail basic WCAG requirements. Non-compliance penalties: up to $150,000 per violation.
This is not "nice to have" - it's "fix this or get sued."

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

## Tech Stack
- **Backend:** Python 3.11+ / Flask 3.x
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **ORM:** Flask-SQLAlchemy + Flask-Migrate
- **Auth:** Flask-Login + Werkzeug password hashing
- **Accessibility Scanner:** Built-in Python HTML parser + WCAG rules engine
- **AI Suggestions:** OpenAI API (GPT-4) for fix generation
- **Payments:** Stripe (stripe-python SDK)
- **Frontend:** Tailwind CSS (CDN) + HTMX
- **Email:** Flask-Mail
- **Deployment:** Railway / Render

## Project Structure
```
/
├── CLAUDE.md              # This file - project brain
├── README.md              # Public README
├── requirements.txt       # Python dependencies
├── config.py             # App configuration
├── run.py                # Entry point
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── models.py         # DB models (User, Site, Scan, Violation)
│   ├── auth.py           # Auth routes
│   ├── dashboard.py      # Dashboard routes
│   ├── scanner.py        # Accessibility scanning engine
│   ├── ai_suggestions.py # AI-powered fix suggestions
│   ├── billing.py        # Stripe integration
│   ├── landing.py        # Marketing pages
│   ├── api.py            # REST API
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/         # login.html, signup.html
│   │   ├── dashboard/    # index.html, site.html, scan_results.html
│   │   └── landing/      # index.html, pricing.html
│   └── static/
└── tests/
    ├── conftest.py
    └── test_app.py
```

## Database Models
- **User:** email, password, name, plan, stripe_customer_id
- **Site:** url, user_id, name, last_scan_date, compliance_score
- **Scan:** site_id, started_at, completed_at, score, pages_scanned, status
- **Violation:** scan_id, rule_id, severity, element, description, fix_suggestion, page_url

## WCAG Rules We Check (MVP)
Priority rules that catch the most common violations:
1. Missing alt text on images (WCAG 1.1.1)
2. Missing form labels (WCAG 1.3.1)
3. Insufficient color contrast (WCAG 1.4.3)
4. Missing page language attribute (WCAG 3.1.1)
5. Missing document title (WCAG 2.4.2)
6. Empty links / buttons (WCAG 2.4.4 / 4.1.2)
7. Missing heading structure (WCAG 1.3.1)
8. Keyboard accessibility issues (WCAG 2.1.1)
9. Missing ARIA labels on interactive elements (WCAG 4.1.2)
10. Missing skip navigation link (WCAG 2.4.1)

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

## Status
- [x] Market research & timing validation (Feb 2026 - ADA deadline Apr 24)
- [x] Product definition & pricing
- [x] Project setup & core infrastructure
- [x] Database models (User, Site, Scan, Violation, Subscription)
- [x] Auth system (signup/login/logout with email validation)
- [x] Accessibility scanner engine (10 WCAG rules, multi-page crawling)
- [x] AI fix suggestions (OpenAI API + rule-based fallback)
- [x] Dashboard & scan results UI (Tailwind CSS, score visualization)
- [x] Landing page (ADA urgency-focused with deadline countdown)
- [x] Stripe billing (checkout, webhooks, plan management)
- [x] REST API (/api/v1/sites/<uid>/latest-scan)
- [x] Tests (27 passing - pages, auth, scanner engine, API, models)
- [ ] Deploy to Railway/Render
- [ ] Domain setup (pageguard.dev)
- [ ] Stripe live keys configuration
- [ ] Product Hunt launch
- [ ] Content marketing: "ADA Website Compliance Checklist 2026"
