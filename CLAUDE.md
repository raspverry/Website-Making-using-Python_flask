# TestiFlow - Testimonial & Social Proof Platform

## Project Overview
TestiFlow is a SaaS platform that helps businesses collect, manage, and showcase customer testimonials. Users create "Spaces" for their products/services, share collection forms, and embed beautiful testimonial widgets on their websites.

**Revenue Target:** $1,000 MRR (Monthly Recurring Revenue)
**Business Model:** Freemium SaaS with tiered pricing

## Pricing Plans
| Plan | Price | Spaces | Testimonials | Features |
|------|-------|--------|-------------|----------|
| Free | $0/mo | 1 | 10 | Basic wall widget, TestiFlow branding |
| Starter | $19/mo | 3 | 50 | All widgets, no branding, email notifications |
| Pro | $49/mo | 10 | Unlimited | Video testimonials, custom branding, analytics |
| Agency | $99/mo | Unlimited | Unlimited | API access, white-label, priority support |

## Tech Stack
- **Backend:** Python 3.11+ / Flask 3.x
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **ORM:** Flask-SQLAlchemy + Flask-Migrate (Alembic)
- **Auth:** Flask-Login + Werkzeug password hashing (bcrypt)
- **Payments:** Stripe (stripe-python SDK)
- **Frontend:** Tailwind CSS + HTMX (minimal JS, server-rendered)
- **Email:** Flask-Mail (SMTP)
- **Deployment:** Railway / Render / Fly.io
- **Testing:** pytest + pytest-flask

## Project Structure
```
/
├── CLAUDE.md              # This file - project documentation
├── README.md              # Public-facing README
├── requirements.txt       # Python dependencies
├── config.py             # App configuration (env-based)
├── run.py                # Application entry point
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── models.py         # SQLAlchemy models
│   ├── auth.py           # Auth routes (login/signup/logout)
│   ├── dashboard.py      # Dashboard routes (spaces, testimonials)
│   ├── public.py         # Public routes (collection forms)
│   ├── widget.py         # Widget embed routes & JS generation
│   ├── billing.py        # Stripe subscription management
│   ├── landing.py        # Landing page & pricing routes
│   ├── api/
│   │   └── __init__.py   # REST API for widget data
│   ├── templates/
│   │   ├── base.html     # Base layout with Tailwind
│   │   ├── auth/         # login.html, signup.html
│   │   ├── dashboard/    # index.html, space.html, settings.html
│   │   ├── public/       # collect.html, thankyou.html
│   │   ├── widgets/      # wall.html, carousel.html
│   │   └── landing/      # index.html, pricing.html
│   └── static/
│       ├── css/          # Tailwind output
│       ├── js/           # HTMX, widget embed script
│       └── images/       # Logo, marketing assets
├── migrations/           # Alembic database migrations
└── tests/               # pytest test files
```

## Database Models
- **User**: Account info, plan tier, Stripe customer ID
- **Space**: A project/product that collects testimonials (belongs to User)
- **Testimonial**: Customer testimonial with text/rating/avatar (belongs to Space)
- **Widget**: Widget configuration for embedding (belongs to Space)
- **Subscription**: Stripe subscription tracking (belongs to User)

## Key Features (MVP)
1. User registration & authentication
2. Space creation and management (CRUD)
3. Public testimonial collection forms (shareable link)
4. Testimonial management (approve/reject/tag/star)
5. Embeddable widgets (Wall of Love, Carousel, Badge)
6. Stripe subscription billing
7. Marketing landing page with pricing

## Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py

# Run tests
pytest tests/ -v

# Database migrations
flask db init
flask db migrate -m "description"
flask db upgrade
```

## Environment Variables
```
FLASK_SECRET_KEY=<random-secret>
DATABASE_URL=sqlite:///testiflow.db
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=<email>
MAIL_PASSWORD=<app-password>
```

## Widget Embed Code (What Users Copy-Paste)
```html
<div id="testiflow-widget" data-space="SPACE_ID"></div>
<script src="https://app.testiflow.com/widget.js"></script>
```

## Competitive Landscape
- Testimonial.to ($25K+ MRR) - Video-first testimonials
- Famewall ($1K+ MRR) - Simple testimonial walls
- Senja - Review collection & sharing
- **Our edge:** Simpler, cheaper, faster setup. Focus on solo founders & small agencies.

## Go-to-Market Strategy
1. Launch on Product Hunt
2. Post on Indie Hackers, Reddit (r/SaaS, r/startups)
3. Create free tools (testimonial request email templates)
4. Content marketing (blog: "How to get more testimonials")
5. Widget "Powered by TestiFlow" viral loop
6. Twitter/X build-in-public journey

## Status
- [x] Market research & product definition
- [x] Project structure setup
- [x] Core backend (models, auth, dashboard)
- [x] Testimonial collection system
- [x] Widget embed system (Wall of Love, Carousel, Badge)
- [x] Landing page & pricing
- [x] Stripe integration (checkout, webhooks, subscription management)
- [x] Testing (18 tests passing)
- [ ] Deployment to production
- [ ] Domain & SSL setup
- [ ] Product Hunt launch
