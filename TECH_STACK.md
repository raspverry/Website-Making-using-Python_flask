# PageGuard - Tech Stack
*Last updated: February 13, 2026*

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND                                 │
│           Next.js 16 (TypeScript, Tailwind CSS)              │
│           App Router, Server Components, SSR                 │
│                  localhost:3000                               │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API (JSON)
┌─────────────────────▼───────────────────────────────────────┐
│                   FASTAPI BACKEND                            │
│                  localhost:8000                               │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Auth     │  │  Sites   │  │  Agent   │  │ Billing  │   │
│  │  Router   │  │  Router  │  │  Router  │  │  Router  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              CORE SERVICES                            │   │
│  │                                                       │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  Scanner   │  │  AI Fix    │  │  Report    │     │   │
│  │  │  Engine    │  │  Suggest   │  │  (PDF)     │     │   │
│  │  └─────┬──────┘  └─────┬──────┘  └────────────┘     │   │
│  │        │                │                             │   │
│  │  BeautifulSoup    OpenAI API                          │   │
│  │  + lxml           (gpt-5-mini, configurable)          │   │
│  │                                                       │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  Email     │  │  Plan      │  │  Task      │     │   │
│  │  │  (SMTP)    │  │  Service   │  │  Runner    │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MIDDLEWARE                                │   │
│  │  slowapi (Rate Limiting) + Security Headers           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              DATA LAYER                               │   │
│  │  SQLAlchemy 2.0+ → SQLite (dev) / PostgreSQL (prod)  │   │
│  │  Alembic → Schema migrations                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Stack Detail

### Backend Framework

| Component | Choice | Why |
|-----------|--------|-----|
| **Web Framework** | FastAPI | async I/O, 자동 API 문서 (Swagger/ReDoc), Pydantic 유효성 검사. 고성능 |
| **ASGI Server** | Uvicorn | 프로덕션급 ASGI 서버. 비동기 요청 처리에 최적화 |
| **Python** | CPython 3.11+ | 안정성 + 성능 (3.11 10-60% 속도 향상) |
| **Validation** | Pydantic 2.0+ | 타입 안전한 요청/응답 스키마. FastAPI와 네이티브 통합 |

### Database

| Component | Choice | Why |
|-----------|--------|-----|
| **Dev DB** | SQLite | 설정 불필요, 로컬 개발에 최적 |
| **Prod DB** | PostgreSQL | 동시성, 안정성, Railway/Render 기본 지원 |
| **ORM** | SQLAlchemy 2.0+ | 독립 ORM. 타입 안전, SQL injection 방지 |
| **Migration** | Alembic | 독립 마이그레이션 도구. 스키마 변경 추적 & 롤백 |

### Authentication & Security

| Component | Choice | Why |
|-----------|--------|-----|
| **JWT Auth** | PyJWT | 무상태(stateless) 토큰 인증. API 서버에 최적. 세션 관리 불필요 |
| **Password Hash** | bcrypt | 업계 표준 해싱 알고리즘. GPU 공격 저항성 |
| **Rate Limiting** | slowapi | 인증(5/min), 스캔(10/min) 엔드포인트 보호. 브루트포스 방지 |
| **Security Headers** | 커스텀 미들웨어 | X-Frame-Options, X-Content-Type-Options, XSS Protection, Referrer-Policy |
| **Email Validation** | Pydantic validators | 스키마 수준에서 이메일 형식 검증 |
| **CSRF** | 불필요 | 무상태 JWT API이므로 CSRF 토큰이 필요 없음 |

### Accessibility Scanner

| Component | Choice | Why |
|-----------|--------|-----|
| **HTML Parser** | BeautifulSoup4 | 가장 범용적인 HTML 파서. malformed HTML도 처리 |
| **XML Parser** | lxml | BS4의 백엔드. C 기반으로 빠름 |
| **HTTP Client** | requests | 페이지 페칭. 간단하고 안정적 |
| **Phase 2: Browser** | Playwright (계획) | JS 렌더링 후 스캔. SPA 사이트 지원 |

**스캐너 아키텍처:**
```python
fetch_page(url)           # requests로 HTML 다운로드
  → discover_pages()      # BeautifulSoup로 내부 링크 추출
  → check_page()          # 13개 WCAG 규칙 체크
    → ViolationResult[]   # 위반 목록 반환
  → calculate_score()     # 심각도 가중치 기반 점수 산출
```

### AI Integration

| Component | Choice | Why |
|-----------|--------|-----|
| **AI Provider** | OpenAI API | gpt-5-mini (기본값, `AI_MODEL` env로 변경 가능). 빠르고 저렴 |
| **SDK** | openai (공식 SDK) | 타입 안전한 공식 Python SDK 사용 |
| **Fallback** | Rule-based dict | API 없어도 13개 규칙에 대한 사전 정의 수정안 제공 |
| **모델 변경** | 환경 변수 (`AI_MODEL`) | 코드 수정 없이 모델 교체 가능. `backend/config.py`에서 설정 |

**비용 추정:**
- 위반 1개당 AI 호출: ~300 input + 300 output tokens
- 비용: ~$0.0001/위반
- 스캔 1회 평균 10 위반 = ~$0.001/스캔
- 1,000 스캔/월 = ~$1/월

### Payments

| Component | Choice | Why |
|-----------|--------|-----|
| **Payment Provider** | Stripe | 업계 표준. Checkout Session으로 빠른 통합 |
| **SDK** | stripe-python | 공식 SDK |
| **Billing Model** | Subscription (monthly) | SaaS 표준. Stripe Billing으로 관리 |
| **Webhook Events** | checkout.session.completed, customer.subscription.deleted | 최소한의 이벤트로 플랜 관리 |

### Frontend

| Component | Choice | Why |
|-----------|--------|-----|
| **Framework** | Next.js 16 | App Router, Server Components, SSR. SEO에 최적 |
| **Language** | TypeScript | 타입 안전성. 컴파일 타임 에러 검출 |
| **CSS** | Tailwind CSS | 빌드 타임 CSS 생성. 유틸리티 우선 스타일링 |
| **Routing** | App Router | 파일 시스템 기반 라우팅. 레이아웃, 로딩 UI, 에러 처리 내장 |
| **API Client** | 타입 안전 fetch | `lib/api.ts`에서 FastAPI 엔드포인트와 타입 안전하게 통신 |

**왜 Next.js 16인가?**
- Server Components로 초기 로딩 최적화
- App Router의 레이아웃 시스템 (인증 네비게이션, 대시보드 레이아웃)
- TypeScript로 프론트엔드-백엔드 타입 일관성 유지
- SSR로 SEO 유리 (랜딩 페이지, 마케팅 콘텐츠)
- React 생태계 활용 (컴포넌트 재사용, 상태 관리)

**주요 컴포넌트:**
- `AuthNav.tsx` - 인증 상태 인식 네비게이션
- `CountdownTimer.tsx` - ADA 마감일 카운트다운
- `ScoreCircle.tsx` - 접근성 점수 표시 (aria 지원)
- `PricingCard.tsx` - 요금제 카드 (Stripe 체크아웃)
- `ViolationCard.tsx` - 위반 사항 표시
- `Footer.tsx` - 푸터 (법적 페이지 링크)

### Email

| Component | Choice | Why |
|-----------|--------|-----|
| **전송** | smtplib (Python 표준 라이브러리) | 외부 의존성 없음. SMTP 직접 전송 |
| **Dev Fallback** | 콘솔 출력 | SMTP 미설정 시 터미널에 이메일 내용 출력 |
| **Phase 2: Provider** | Postmark 또는 SendGrid (계획) | 트랜잭셔널 이메일 전문. 높은 전달률 |

### Reports

| Component | Choice | Why |
|-----------|--------|-----|
| **PDF 생성** | ReportLab | 전문적인 PDF 컴플라이언스 리포트 생성. Pro 플랜 기능 |
| **텍스트 리포트** | 내장 서비스 | 모든 플랜에서 텍스트 기반 리포트 제공 |

### Deployment

| Component | Choice | Why |
|-----------|--------|-----|
| **Platform** | Railway 또는 Render | Git push → 자동 배포. PostgreSQL 내장. $5-20/mo |
| **Domain** | pageguard.dev | .dev는 HTTPS 강제 (보안 이미지). 기술 제품에 적합 |
| **SSL** | 플랫폼 자동 관리 | Let's Encrypt 기반 |
| **Frontend 배포** | Vercel (권장) 또는 동일 플랫폼 | Next.js 네이티브 지원. 글로벌 CDN |

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
| **Test Framework** | pytest | Python 표준 |
| **API Testing** | FastAPI TestClient | httpx 기반. async 엔드포인트 테스트 지원 |
| **Test DB** | SQLite in-memory | 빠른 테스트 실행 |
| **Current Coverage** | 37+ tests passing | 인증, 스캐너 (13규칙), API, 모델, 에이전트 |

### Multi-Agent CLI System

| Component | Choice | Why |
|-----------|--------|-----|
| **Orchestrator** | `agents/orchestrator.py` | 팀 워크플로우 조율, 작업 위임 |
| **Scanner Agent** | `agents/scanner_agent.py` | 웹사이트 크롤링, WCAG 2.2 위반 감지 |
| **Fix Agent** | `agents/fix_agent.py` | 위반 사항별 코드 수정안 생성 |
| **Report Agent** | `agents/report_agent.py` | 컴플라이언스 리포트 및 리스크 평가 생성 |
| **AI Provider** | Anthropic Claude (선택) | `--ai-orchestrate` 모드에서 에이전트 간 AI 협업 |

### Monitoring (Phase 2)

| Component | Choice | Why |
|-----------|--------|-----|
| **Error Tracking** | Sentry (무료 tier) | Python/FastAPI 자동 통합. 5K 이벤트/mo 무료 |
| **Uptime** | UptimeRobot (무료) | 5분 간격 모니터링 |
| **Analytics** | Plausible ($9/mo) 또는 PostHog (무료) | GDPR 친화적 |

---

## Directory Structure

```
/
├── frontend/                  # Next.js 16 프론트엔드
│   ├── package.json           # Node.js 의존성
│   ├── tsconfig.json          # TypeScript 설정
│   ├── tailwind.config.ts     # Tailwind 설정
│   └── src/
│       ├── app/               # App Router 페이지
│       │   ├── page.tsx       # 랜딩 (ADA 카운트다운)
│       │   ├── layout.tsx     # 루트 레이아웃 (nav, footer, skip-nav)
│       │   ├── pricing/       # 요금제 페이지 (Stripe 체크아웃)
│       │   ├── login/         # 로그인 (JWT)
│       │   ├── signup/        # 회원가입 (JWT)
│       │   ├── privacy/       # 개인정보처리방침
│       │   ├── terms/         # 이용약관
│       │   ├── disclaimer/    # 면책조항
│       │   └── dashboard/     # 보호된 대시보드
│       │       └── sites/[uid]/
│       │           ├── page.tsx        # 사이트 상세 + 스캔 결과
│       │           └── agent/page.tsx  # AI Q&A 채팅
│       ├── components/        # 재사용 가능한 UI 컴포넌트
│       ├── lib/               # API 클라이언트, 설정
│       └── types/             # TypeScript 인터페이스
│
├── backend/                   # FastAPI 백엔드
│   ├── main.py                # 앱 진입점 + 미들웨어 + 라우터
│   ├── config.py              # 환경 설정 (AI_MODEL, DB, Stripe 등)
│   ├── database.py            # SQLAlchemy 엔진 + 세션
│   ├── models.py              # SQLAlchemy 모델 (5 테이블)
│   ├── schemas.py             # Pydantic DTOs
│   ├── dependencies.py        # Auth 의존성 (JWT Bearer)
│   ├── middleware.py           # Rate limiting + Security headers
│   ├── routers/               # API 라우터 (auth, sites, agent, billing, account)
│   ├── services/              # 비즈니스 로직 (scanner, ai, report, email, plan, task)
│   ├── alembic/               # DB 마이그레이션
│   └── requirements.txt       # Python 의존성
│
├── agents/                    # 멀티 에이전트 CLI 시스템
│   ├── orchestrator.py        # 팀 워크플로우 조율
│   ├── scanner_agent.py       # 크롤링 + 위반 감지
│   ├── fix_agent.py           # 코드 수정안 생성
│   ├── report_agent.py        # 컴플라이언스 리포트
│   ├── base.py                # 기본 에이전트 클래스
│   ├── constants.py           # 공유 설정
│   └── run.py                 # CLI 진입점
│
├── tests/                     # 테스트
│   └── test_backend.py        # FastAPI 테스트 (37 passing)
│
├── CLAUDE.md                  # 프로젝트 브레인 (컨텍스트 문서)
├── BUSINESS_PLAN.md           # 사업계획서
├── prd.md                     # Product Requirements Document
├── ROADMAP.md                 # 프로젝트 로드맵
└── TECH_STACK.md              # 이 파일
```

---

## Dependency Graph

```
FastAPI (Backend Core)
├── uvicorn[standard]         # ASGI 서버
├── sqlalchemy 2.0+           # ORM (독립 사용)
├── alembic                   # DB 마이그레이션 (독립 사용)
├── pydantic 2.0+             # 요청/응답 유효성 검사
├── pyjwt                     # JWT 토큰 생성/검증
├── bcrypt                    # 비밀번호 해싱
├── slowapi                   # Rate limiting 미들웨어
├── httpx                     # 비동기 HTTP 클라이언트
└── python-dotenv             # 환경 변수 로딩

Scanner:
├── beautifulsoup4            # HTML 파싱
├── lxml                      # XML/HTML 파서 백엔드
└── requests                  # HTTP 페이지 페칭

AI:
└── openai                    # gpt-5-mini (AI_MODEL 환경 변수로 변경 가능)

Payments:
└── stripe                    # Stripe 결제 SDK

Reports:
└── reportlab                 # PDF 리포트 생성

Database (prod):
└── psycopg2-binary           # PostgreSQL 드라이버

Frontend (Next.js 16):
├── react + react-dom         # UI 라이브러리
├── typescript                # 타입 안전성
├── tailwindcss               # 유틸리티 CSS (빌드 타임)
└── next                      # App Router, SSR, Server Components

Testing:
└── pytest                    # FastAPI TestClient 포함
```

**백엔드 직접 의존성:** 16 packages (`backend/requirements.txt`)
**보안 주의:** 프로덕션 배포 전 `pip audit` 실행 권장

---

## Scaling Considerations

### 현재 (0-100 사용자)
- SQLite (dev), PostgreSQL (prod)
- 단일 Uvicorn 프로세스 (async로 동시 요청 처리)
- ThreadPoolExecutor로 백그라운드 스캔 비동기 처리
- FastAPI의 async/await로 I/O 바운드 작업 효율적 처리
- 충분함

### Phase 2 (100-1,000 사용자)
- Celery + Redis로 스캔 작업 큐잉 (현재 ThreadPoolExecutor에서 업그레이드)
- Uvicorn 워커 다중화 (`--workers 4-8`)
- PostgreSQL connection pooling (SQLAlchemy pool 설정)
- Next.js ISR (Incremental Static Regeneration)으로 프론트엔드 성능 최적화

### Phase 3 (1,000+ 사용자)
- 스캐너 워커 분리 (별도 프로세스/서버)
- CDN (CloudFlare) for static assets
- 읽기 전용 DB 레플리카 (필요시)
- 지역별 배포 고려
- Vercel Edge Functions로 프론트엔드 글로벌 배포

**현실적으로:** $1K MRR 시점 (30-50 고객)에서는 단일 서버로 충분합니다.
FastAPI의 비동기 처리 덕분에 동기 프레임워크 대비 동시 처리 능력이 월등히 높습니다.
스케일링 고민은 $5K MRR 이후에 해도 늦지 않습니다.
