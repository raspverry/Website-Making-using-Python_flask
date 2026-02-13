# PageGuard - Tech Stack
*Last updated: February 13, 2026*

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT                                │
│  Browser → Tailwind CSS + Vanilla JS                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS
┌─────────────────────▼───────────────────────────────────────┐
│                     FLASK APP                                │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Landing  │  │   Auth   │  │Dashboard │  │   API    │   │
│  │  Routes   │  │  Routes  │  │  Routes  │  │  Routes  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              CORE SERVICES                            │   │
│  │                                                       │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  Scanner   │  │  AI Fix    │  │  Billing   │     │   │
│  │  │  Engine    │  │  Suggest   │  │  (Stripe)  │     │   │
│  │  └─────┬──────┘  └─────┬──────┘  └────────────┘     │   │
│  │        │                │                             │   │
│  │  BeautifulSoup    OpenAI API                          │   │
│  │  + lxml           (GPT-4o-mini)                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              DATA LAYER                               │   │
│  │  Flask-SQLAlchemy → SQLite (dev) / PostgreSQL (prod)  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Stack Detail

### Backend Framework

| Component | Choice | Version | Why |
|-----------|--------|---------|-----|
| **Web Framework** | Flask | 3.1.0 | 경량, 유연, 빠른 프로토타이핑. 우리 규모에 Django는 overkill |
| **WSGI Server** | Gunicorn | 23.0.0 | 프로덕션 표준. 멀티워커 지원 |
| **Python** | CPython | 3.11+ | 안정성 + 성능 (3.11 10-60% 속도 향상) |

### Database

| Component | Choice | Why |
|-----------|--------|-----|
| **Dev DB** | SQLite | 설정 불필요, 로컬 개발에 최적 |
| **Prod DB** | PostgreSQL | 동시성, 안정성, Railway/Render 기본 지원 |
| **ORM** | Flask-SQLAlchemy 3.1.1 | Flask 통합 최적. SQL injection 방지 |
| **Migration** | Flask-Migrate (Alembic) 4.0.7 | 스키마 변경 추적 & 롤백 |

### Authentication & Security

| Component | Choice | Why |
|-----------|--------|-----|
| **Session Auth** | Flask-Login 0.6.3 | 세션 기반 인증. JWT보다 간단하고 우리 케이스에 적합 |
| **Password Hash** | Werkzeug (scrypt/pbkdf2) | Flask 기본 내장. 업계 표준 해싱 |
| **CSRF Protection** | Flask-WTF 1.2.2 | 모든 POST 폼에 CSRF 토큰 자동 적용 |
| **Email Validation** | email-validator 2.2.0 | RFC 준수 이메일 형식 검증 |

### Accessibility Scanner

| Component | Choice | Why |
|-----------|--------|-----|
| **HTML Parser** | BeautifulSoup4 4.13.3 | 가장 범용적인 HTML 파서. malformed HTML도 처리 |
| **XML Parser** | lxml 5.3.1 | BS4의 백엔드. C 기반으로 빠름 |
| **HTTP Client** | requests 2.32.3 | 페이지 페칭. 간단하고 안정적 |
| **Phase 2: Browser** | Playwright (계획) | JS 렌더링 후 스캔. SPA 사이트 지원 |

**스캐너 아키텍처:**
```python
fetch_page(url)           # requests로 HTML 다운로드
  → discover_pages()      # BeautifulSoup로 내부 링크 추출
  → check_page()          # 10개 WCAG 규칙 체크
    → ViolationResult[]   # 위반 목록 반환
  → calculate_score()     # 심각도 가중치 기반 점수 산출
```

### AI Integration

| Component | Choice | Why |
|-----------|--------|-----|
| **AI Provider** | OpenAI API | GPT-4o-mini: 빠르고 저렴 ($0.15/1M input tokens) |
| **Fallback** | Rule-based dict | API 없어도 10개 규칙에 대한 사전 정의 수정안 제공 |
| **API Call** | requests (직접 호출) | openai SDK 불필요. 단일 엔드포인트만 사용 |

**비용 추정:**
- 위반 1개당 AI 호출: ~300 input + 300 output tokens
- 비용: ~$0.0001/위반
- 스캔 1회 평균 10 위반 = ~$0.001/스캔
- 1,000 스캔/월 = ~$1/월

### Payments

| Component | Choice | Why |
|-----------|--------|-----|
| **Payment Provider** | Stripe | 업계 표준. Checkout Session으로 빠른 통합 |
| **SDK** | stripe-python 11.4.1 | 공식 SDK |
| **Billing Model** | Subscription (monthly) | SaaS 표준. Stripe Billing으로 관리 |
| **Webhook Events** | checkout.session.completed, customer.subscription.deleted | 최소한의 이벤트로 플랜 관리 |

### Frontend

| Component | Choice | Why |
|-----------|--------|-----|
| **CSS** | Tailwind CSS (CDN) | 빌드 없이 CDN으로 바로 사용. 빠른 UI 개발 |
| **Templating** | Jinja2 | Flask 기본 내장. 서버 렌더링 |
| **JavaScript** | Vanilla JS (minimal) | 프레임워크 불필요. 클립보드 복사, 별점 등 최소한만 |
| **Phase 2: Interactivity** | HTMX (계획) | AJAX 업데이트. JS 코드 최소화 |

**왜 React/Vue가 아닌가?**
- SPA 프레임워크는 이 제품에 overkill
- 서버 렌더링이 SEO에 유리 (랜딩 페이지 중요)
- 개발 속도: Jinja2 템플릿이 더 빠름
- 유지보수: 빌드 파이프라인 불필요

### Email

| Component | Choice | Why |
|-----------|--------|-----|
| **Framework** | Flask-Mail 0.10.0 | Flask 통합 |
| **Phase 2: Provider** | Postmark 또는 SendGrid (계획) | 트랜잭셔널 이메일 전문 |

### Deployment

| Component | Choice | Why |
|-----------|--------|-----|
| **Platform** | Railway 또는 Render | Git push → 자동 배포. PostgreSQL 내장. $5-20/mo |
| **Domain** | pageguard.dev | .dev는 HTTPS 강제 (보안 이미지). 기술 제품에 적합 |
| **SSL** | 플랫폼 자동 관리 | Let's Encrypt 기반 |

**대안 비교:**
| Platform | 가격 | PostgreSQL | 장점 | 단점 |
|----------|------|------------|------|------|
| Railway | $5/mo~ | 포함 | 가장 빠른 배포 | 비용 예측 어려움 |
| Render | $7/mo~ | 포함 | 무료 tier 있음 | 콜드 스타트 |
| Fly.io | $5/mo~ | 별도 설정 | 글로벌 엣지 | 설정 복잡 |
| **권장: Railway** | | | | |

### Testing

| Component | Choice | Why |
|-----------|--------|-----|
| **Test Framework** | pytest 8.3.4 | Python 표준 |
| **Flask Testing** | pytest-flask 1.3.0 | test_client 통합 |
| **Test DB** | SQLite in-memory | 빠른 테스트 실행 |
| **Current Coverage** | 27 tests passing | 페이지, 인증, 스캐너, API, 모델 |

### Monitoring (Phase 2)

| Component | Choice | Why |
|-----------|--------|-----|
| **Error Tracking** | Sentry (무료 tier) | Python/Flask 자동 통합. 5K 이벤트/mo 무료 |
| **Uptime** | UptimeRobot (무료) | 5분 간격 모니터링 |
| **Analytics** | Plausible ($9/mo) 또는 PostHog (무료) | GDPR 친화적 |

---

## Directory Structure

```
/
├── CLAUDE.md              # 프로젝트 브레인 (컨텍스트 문서)
├── BUSINESS_PLAN.md       # 사업계획서
├── prd.md                 # Product Requirements Document
├── ROADMAP.md             # 프로젝트 로드맵
├── TECH_STACK.md          # 이 파일
├── README.md              # 공개 README
├── requirements.txt       # pip dependencies (18 packages)
├── config.py              # 환경 설정 (env vars)
├── run.py                 # Flask entry point
├── .env.example           # 환경 변수 템플릿
├── .gitignore             # Git 제외 파일
│
├── app/
│   ├── __init__.py        # App factory, extension init, blueprint registration
│   ├── models.py          # SQLAlchemy models (5 tables)
│   ├── auth.py            # /auth/* routes (signup, login, logout)
│   ├── dashboard.py       # /dashboard/* routes (sites, scans, results)
│   ├── scanner.py         # WCAG scanning engine (10 rules, crawler)
│   ├── ai_suggestions.py  # AI fix generation (OpenAI + fallback)
│   ├── billing.py         # /billing/* routes (Stripe checkout, webhook)
│   ├── landing.py         # / and /pricing routes
│   ├── api.py             # /api/v1/* REST endpoints
│   │
│   ├── templates/
│   │   ├── base.html                    # Base layout (nav, flash, footer)
│   │   ├── auth/login.html              # Login form
│   │   ├── auth/signup.html             # Signup form
│   │   ├── dashboard/index.html         # Site list (score badges)
│   │   ├── dashboard/add_site.html      # Add site form
│   │   ├── dashboard/site_detail.html   # Site detail (scores, history)
│   │   ├── dashboard/scan_results.html  # Violation list (filters, fixes)
│   │   ├── dashboard/billing.html       # Billing management
│   │   ├── landing/index.html           # Marketing page (ADA urgency)
│   │   └── landing/pricing.html         # Pricing table (4 plans)
│   │
│   └── static/           # (reserved for future static assets)
│
└── tests/
    ├── __init__.py
    ├── conftest.py        # Test config, fixtures (app, client, db)
    └── test_app.py        # 27 tests (pages, auth, scanner, API, models)
```

---

## Dependency Graph

```
Flask 3.1.0
├── Flask-SQLAlchemy 3.1.1 → SQLAlchemy 2.0.36
├── Flask-Login 0.6.3
├── Flask-Migrate 4.0.7 → Alembic
├── Flask-WTF 1.2.2
├── Flask-Mail 0.10.0
└── Werkzeug 3.1.3

Scanner:
├── beautifulsoup4 4.13.3
├── lxml 5.3.1
└── requests 2.32.3

Payments:
└── stripe 11.4.1

Utils:
├── python-dotenv 1.0.1
├── email-validator 2.2.0
└── gunicorn 23.0.0

Database (prod):
└── psycopg2-binary 2.9.10

Testing:
├── pytest 8.3.4
└── pytest-flask 1.3.0
```

**총 직접 의존성:** 18 packages
**보안 주의:** 프로덕션 배포 전 `pip audit` 실행 권장

---

## Scaling Considerations

### 현재 (0-100 사용자)
- SQLite (dev), PostgreSQL (prod)
- 단일 Gunicorn 프로세스
- 동기 스캐닝 (요청-응답 내에서 완료)
- 충분함

### Phase 2 (100-1,000 사용자)
- Celery + Redis로 스캔 비동기 처리
- 스캔 큐잉 (동시 요청 관리)
- Gunicorn 워커 4-8개
- PostgreSQL connection pooling

### Phase 3 (1,000+ 사용자)
- 스캐너 워커 분리 (별도 프로세스/서버)
- CDN (CloudFlare) for static assets
- 읽기 전용 DB 레플리카 (필요시)
- 지역별 배포 고려

**현실적으로:** $1K MRR 시점 (30-50 고객)에서는 단일 서버로 충분합니다.
스케일링 고민은 $5K MRR 이후에 해도 늦지 않습니다.
