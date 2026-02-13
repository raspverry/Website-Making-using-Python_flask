# PageGuard - Product Requirements Document (PRD)
*Version 1.0 | February 13, 2026*

---

## 1. Overview

### Product
PageGuard - AI 기반 웹 접근성 컴플라이언스 스캐너

### Objective
웹사이트 URL을 입력하면 WCAG 2.2 Level AA 위반사항을 자동 검출하고, AI가 코드 수정 방법까지 제안하는 SaaS 플랫폼

### Success Criteria
- 런칭 후 60일 내 $1,000 MRR 달성
- 무료 사용자 200명+ 확보
- 유료 전환율 3%+

---

## 2. User Personas

### Persona 1: Small Business Sam
- **역할:** 소규모 비즈니스 오너 (레스토랑, 로컬 서비스)
- **기술 수준:** 비기술자. WordPress 사이트 운영
- **Pain:** 변호사한테 "웹사이트 ADA 문제 있을 수 있다" 연락 받음. 뭘 해야 하는지 모름
- **Want:** URL 넣으면 "문제 있다/없다" 바로 알려주고, 어떻게 고치는지 쉬운 말로 설명
- **Plan:** Free → Starter ($29/mo)

### Persona 2: Agency Alex
- **역할:** 소규모 웹 에이전시 운영 (클라이언트 10-30개)
- **기술 수준:** 중급 개발자
- **Pain:** 모든 클라이언트 사이트의 접근성을 일일이 체크할 시간이 없음. 리포트 요청도 받음
- **Want:** 다수 사이트 한번에 관리, 클라이언트에게 보여줄 프로페셔널한 리포트
- **Plan:** Pro ($79/mo) → Agency ($199/mo)

### Persona 3: Developer Dev
- **역할:** 프리랜서 웹 개발자
- **기술 수준:** 고급. 하지만 접근성 전문가는 아님
- **Pain:** 접근성 규칙을 다 외울 수 없고, 하나씩 체크하기 번거로움
- **Want:** 빠른 스캔 + 구체적인 코드 수정안
- **Plan:** Starter ($29/mo)

---

## 3. Feature Requirements

### 3.1 MVP Features (v1.0 - 현재 구현 완료)

#### F1: 사용자 인증
- **Priority:** P0 (필수)
- **Status:** Done
- **Spec:**
  - 이메일 + 비밀번호 가입 (8자 이상, 이메일 형식 검증)
  - 로그인 / 로그아웃
  - JWT 토큰 기반 인증 (PyJWT + bcrypt)
  - Rate limiting (slowapi)

#### F2: 사이트 관리
- **Priority:** P0
- **Status:** Done
- **Spec:**
  - URL + 이름으로 사이트 추가
  - URL 자동 정규화 (https:// 자동 추가)
  - 중복 URL 체크
  - 플랜별 사이트 수 제한 (Free: 1, Starter: 1, Pro: 5, Agency: 20)
  - 사이트 삭제 (관련 스캔/위반 데이터 cascade 삭제)

#### F3: 접근성 스캐너 엔진
- **Priority:** P0
- **Status:** Done
- **Spec:**
  - 13개 WCAG 2.2 Level AA 규칙 검사:
    1. `img-alt` - 이미지 alt 텍스트 누락 (Critical)
    2. `form-label` - 폼 라벨 누락 (Critical)
    3. `meta-viewport` - 줌 비활성화 (Critical)
    4. `html-lang` - 페이지 언어 속성 누락 (Serious)
    5. `page-title` - 페이지 타이틀 누락 (Serious)
    6. `empty-link` - 빈 링크 (Serious)
    7. `empty-button` - 빈 버튼 (Serious)
    8. `heading-order` - 헤딩 레벨 건너뛰기 (Moderate)
    9. `skip-nav` - 스킵 네비게이션 누락 (Moderate)
    10. `landmark-main` - main 랜드마크 누락 (Moderate)
    11. `color-contrast` - 색상 대비 부족 (Serious)
    12. `aria-input-name` / `aria-interactive-name` - 접근 가능한 이름 누락 (Serious/Critical)
    13. `media-autoplay` - 자동 재생 미디어 (Serious)
  - 멀티페이지 크롤링 (내부 링크 자동 발견)
  - 플랜별 페이지 수 제한 (Free: 5, Starter/Pro: 50, Agency: 100)
  - 컴플라이언스 점수 계산 (0-100, 심각도 가중치)

#### F4: AI 수정 제안
- **Priority:** P0
- **Status:** Done
- **Spec:**
  - OpenAI API (gpt-5-mini (AI_MODEL 환경변수로 설정 가능)) 기반 맥락적 수정 제안
  - API 키 없을 시 규칙 기반 폴백 (10개 규칙별 사전 정의된 수정안)
  - 유료 플랜만 AI 수정 제안 활성화
  - 각 위반에 대해: 평문 설명 + 코드 수정 예시

#### F5: 대시보드 UI
- **Priority:** P0
- **Status:** Done
- **Spec:**
  - 사이트 목록 (점수 배지, 마지막 스캔일)
  - 사이트 상세 (점수 카드, 심각도별 카운트, 스캔 히스토리)
  - 스캔 결과 (심각도 필터, 위반 상세, AI 수정 제안)
  - 반응형 디자인 (Next.js 16 App Router + TypeScript, Tailwind CSS)

#### F6: 랜딩 페이지
- **Priority:** P0
- **Status:** Done
- **Spec:**
  - ADA 데드라인 긴급 배너 (빨간색 상단바)
  - "Is your website ADA compliant?" 히어로
  - 벌금/소송/미준수율 스탯 섹션
  - How it works (3단계)
  - WCAG 체크 목록
  - CTA: "Scan Your Website Free"

#### F7: 가격 페이지
- **Priority:** P0
- **Status:** Done
- **Spec:**
  - 4단 가격표 (Free/Starter/Pro/Agency)
  - "Most Popular" 배지 (Pro)
  - 로그인 사용자: 현재 플랜 표시 + 업그레이드 버튼
  - 비로그인: 가입 유도

#### F8: Stripe 결제
- **Priority:** P0
- **Status:** Done
- **Spec:**
  - Stripe Checkout Session (카드 결제)
  - Webhook: checkout.session.completed → 플랜 업그레이드
  - Webhook: customer.subscription.deleted → 플랜 다운그레이드
  - Stripe Customer 자동 생성

#### F9: REST API
- **Priority:** P1
- **Status:** Done
- **Spec:**
  - 전체 REST API 엔드포인트:
    - Auth: 회원가입, 로그인, 비밀번호 찾기/재설정
    - Sites: CRUD + 스캔 실행 + 최신 스캔 조회 + PDF 리포트
    - Agent: AI Q&A + 요약
    - Billing: Stripe 결제/웹훅/포탈/구독 조회
    - Account: 프로필 조회/수정, 비밀번호 변경, 계정 삭제 (GDPR)
  - JWT Bearer 인증
  - JSON 응답 (위반 목록, 점수, 사이트 정보 포함)

---

### 3.2 Phase 2 Features (v1.1 - 유료 고객 확보 후)

#### F10: Playwright 기반 심층 스캔
- **Priority:** P1
- **Status:** Planned
- **Spec:**
  - Playwright로 JavaScript 렌더링 후 스캔 (SPA 지원)
  - 색상 대비(color contrast) 실제 계산
  - 키보드 네비게이션 테스트
  - 현재 BeautifulSoup 스캐너와 병행 운영

#### F11: PDF 리포트 생성
- **Priority:** P1
- **Status:** Done
- **Spec:**
  - 브랜딩된 PDF 컴플라이언스 리포트
  - 점수, 위반 요약, 상세 목록, 수정 제안 포함
  - 화이트라벨 옵션 (Agency 플랜)
  - 다운로드 + 이메일 전송

#### F12: 예약 스캔 & 이메일 알림
- **Priority:** P1
- **Status:** Planned
- **Spec:**
  - APScheduler 또는 Celery 기반 정기 스캔
  - Starter: 주 1회, Pro: 일 1회, Agency: 일 1회
  - 새 위반 발견 시 이메일 알림
  - 점수 변동 알림

#### F13: 컴플라이언스 배지
- **Priority:** P2
- **Status:** Planned
- **Spec:**
  - "Verified Accessible by PageGuard" 임베드 배지
  - 점수 80+ 사이트만 활성화
  - 배지 클릭 → PageGuard 랜딩 (바이럴 루프)
  - Pro/Agency 플랜만

---

### 3.3 Phase 3 Features (v2.0 - $3K MRR 이후)

#### F14: 팀 액세스
- 멀티 유저 / 역할 기반 접근 (Agency 플랜)

#### F15: 클라이언트 포탈
- 에이전시가 클라이언트에게 읽기 전용 리포트 공유

#### F16: 인테그레이션
- WordPress 플러그인
- Slack 알림
- Zapier 연동

#### F17: 다국어 지원
- 한국어, 일본어, 독일어 등

---

## 4. Non-Functional Requirements

### 성능
- 5페이지 스캔: 30초 이내 완료
- 50페이지 스캔: 5분 이내 완료
- 동시 스캔: 최소 10개

### 보안
- 비밀번호: bcrypt 해싱
- Rate Limiting: slowapi
- SQL Injection 방지: SQLAlchemy ORM (parameterized queries)
- XSS 방지: Next.js 자동 이스케이핑
- HTTPS 전용 (프로덕션)

### 가용성
- 목표: 99.9% uptime
- Railway/Render managed infrastructure

### 데이터
- 스캔 결과: 90일 보관 (Free), 무제한 (유료)
- 사용자 데이터: GDPR 준수 삭제 요청 지원

---

## 5. Data Model

```
User
├── id (PK)
├── email (unique, indexed)
├── password_hash
├── name
├── plan (free/starter/pro/agency)
├── stripe_customer_id
└── created_at

Site
├── id (PK)
├── uid (unique, 12char)
├── user_id (FK → User)
├── url
├── name
├── compliance_score (0-100)
├── last_scan_at
└── created_at

Scan
├── id (PK)
├── uid (unique, 12char)
├── site_id (FK → Site)
├── status (pending/running/completed/failed)
├── score (0-100)
├── pages_scanned
├── total_violations
├── critical_count
├── serious_count
├── moderate_count
├── minor_count
├── created_at
└── completed_at

Violation
├── id (PK)
├── scan_id (FK → Scan)
├── rule_id
├── rule_name
├── severity (critical/serious/moderate/minor)
├── wcag_criteria
├── description
├── element_html
├── page_url
├── fix_suggestion
└── selector

Subscription
├── id (PK)
├── user_id (FK → User, unique)
├── stripe_subscription_id
├── stripe_price_id
├── status (active/canceled/past_due)
├── current_period_end
└── created_at
```

---

## 6. API Specification

### Public API

#### GET /api/v1/sites/{site_uid}/latest-scan

**Response (200):**
```json
{
  "site": { "url": "https://example.com", "name": "Example" },
  "scan": {
    "score": 72,
    "status": "completed",
    "pages_scanned": 5,
    "total_violations": 8,
    "critical": 2,
    "serious": 3,
    "moderate": 2,
    "minor": 1,
    "scanned_at": "2026-02-13T10:30:00"
  },
  "violations": [
    {
      "rule_id": "img-alt",
      "rule_name": "Images must have alt text",
      "severity": "critical",
      "wcag": "1.1.1",
      "description": "Image is missing an alt attribute.",
      "element": "<img src=\"photo.jpg\">",
      "page_url": "https://example.com/about",
      "fix": "Add alt=\"Description of image\" to the img tag."
    }
  ]
}
```

**Error (404):**
```json
{ "error": "Site not found" }
```

---

## 7. UI Wireframes (Page Flow)

```
Landing Page (/)
  ├── [Scan Your Website Free] → Signup (/auth/signup)
  └── [View Pricing] → Pricing (/pricing)

Signup (/auth/signup) → Dashboard (/dashboard)
Login (/auth/login) → Dashboard (/dashboard)

Dashboard (/dashboard)
  ├── [+ Add Website] → Add Site (/dashboard/sites/add)
  │                       └── POST → Run Scan → Scan Results
  └── [Site Card] → Site Detail (/dashboard/sites/<uid>)
                      ├── [Run New Scan] → Scan Results
                      ├── [View Report] → Scan Results (/dashboard/scans/<uid>)
                      └── [Remove Site] → Dashboard

Scan Results (/dashboard/scans/<uid>)
  ├── Score Summary (0-100)
  ├── Severity Filter (All/Critical/Serious/Moderate)
  └── Violation Cards (description + element + fix suggestion)
```

---

## 8. Release Plan

| Version | 기능 | 목표 시점 |
|---------|------|-----------|
| v1.0 | MVP (현재) - 스캔, 대시보드, Stripe | Feb 2026 |
| v1.1 | PDF 리포트, 예약 스캔, 이메일 알림 | Mar 2026 |
| v1.2 | Playwright 심층 스캔, 색상 대비 | Apr 2026 |
| v2.0 | 팀 액세스, 클라이언트 포탈, 인테그레이션 | Jun 2026 |
