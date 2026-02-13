# PageGuard - AI Web Accessibility Compliance Scanner

**Is your website ADA compliant? The deadline is April 24, 2026.**

PageGuard scans your website for WCAG 2.2 Level AA accessibility violations, generates a compliance report with scores, and provides AI-powered fix suggestions -- all in under 60 seconds.

96% of websites fail basic accessibility requirements. Non-compliance penalties: up to $150,000 per violation.

## Features

- **Instant Scanning** - Enter a URL, get a compliance report in seconds
- **WCAG 2.2 Level AA** - Checks 10+ rules covering the most common violations
- **Compliance Score** - 0-100 score based on violation severity
- **AI Fix Suggestions** - Plain-English explanations + exact code fixes (paid plans)
- **Multi-Page Crawling** - Automatically discovers and scans internal pages
- **Severity Classification** - Critical, Serious, Moderate, Minor
- **Scan History** - Track compliance over time
- **REST API** - Programmatic access for integrations
- **Stripe Billing** - Subscription management

## What We Check

| Rule | WCAG | Severity |
|------|------|----------|
| Missing image alt text | 1.1.1 | Critical |
| Missing form labels | 1.3.1 | Critical |
| Zoom prevention | 1.4.4 | Critical |
| Missing page language | 3.1.1 | Serious |
| Missing page title | 2.4.2 | Serious |
| Empty links | 2.4.4 | Serious |
| Empty buttons | 4.1.2 | Serious |
| Heading structure | 1.3.1 | Moderate |
| Skip navigation | 2.4.1 | Moderate |
| Missing landmarks | 4.1.2 | Moderate |

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Visit `http://localhost:5000`.

## Running Tests

```bash
pytest tests/ -v
```

## Pricing

| Plan | Price | Sites | Scans | AI Fixes |
|------|-------|-------|-------|----------|
| Free | $0/mo | 1 | 1/month | No |
| Starter | $29/mo | 1 | Weekly | Yes |
| Pro | $79/mo | 5 | Daily | Yes |
| Agency | $199/mo | 20 | Unlimited | Yes |

## Tech Stack

- Python / Flask 3.x
- SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- BeautifulSoup4 + lxml (HTML parsing & WCAG checks)
- OpenAI API (AI fix suggestions)
- Tailwind CSS
- Stripe (payments)

## License

MIT
