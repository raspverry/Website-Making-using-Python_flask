# TestiFlow

**Collect, manage, and showcase customer testimonials.**

TestiFlow is a SaaS platform that helps businesses collect customer testimonials through shareable forms and display them on their websites with beautiful embeddable widgets.

## Features

- **Shareable Collection Forms** - Branded forms that make it easy for customers to submit testimonials
- **Approval Workflow** - Review, approve, or reject testimonials before they go live
- **Embeddable Widgets** - Wall of Love, Carousel, and Badge widgets with one-line embed code
- **Star Ratings** - Collect and display star ratings alongside testimonials
- **Custom Branding** - Remove TestiFlow branding on paid plans
- **REST API** - Full API access for custom integrations
- **Stripe Billing** - Built-in subscription management

## Tech Stack

- **Backend:** Python / Flask
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Frontend:** Tailwind CSS (via CDN)
- **Payments:** Stripe
- **Auth:** Flask-Login

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run the development server
python run.py
```

The app will be available at `http://localhost:5000`.

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
app/
├── __init__.py       # Flask app factory
├── models.py         # Database models (User, Space, Testimonial, Widget, Subscription)
├── auth.py           # Authentication (signup, login, logout)
├── dashboard.py      # Dashboard (manage spaces & testimonials)
├── public.py         # Public testimonial collection forms
├── widget.py         # Embeddable widget rendering & data API
├── billing.py        # Stripe subscription management
├── landing.py        # Landing page & pricing
├── api/              # REST API
└── templates/        # Jinja2 HTML templates
```

## Pricing

| Plan | Price | Spaces | Testimonials |
|------|-------|--------|-------------|
| Free | $0/mo | 1 | 10 per space |
| Starter | $19/mo | 3 | 50 per space |
| Pro | $49/mo | 10 | Unlimited |
| Agency | $99/mo | Unlimited | Unlimited |

## License

MIT
