# PageGuard - Project Roadmap
*Last updated: February 13, 2026*

---

## Timeline Overview

```
Feb 2026          Mar 2026          Apr 2026          May 2026          Jun 2026
|----Phase 1------|----Phase 2------|----Phase 3------|----Phase 4------|----Phase 5----|
  MVP Complete      Launch &          Scale &           Optimize &        Expand
  Deploy & Validate  First Revenue     Deepen            Automate          Features
```

**North Star Metric:** Monthly Recurring Revenue (MRR)
**Primary Goal:** $1,000 MRR by April 2026

---

## Phase 1: Build & Validate (Feb 13 - Feb 28, 2026)

**Goal:** 배포하고 시장 반응 확인. 코드 더 쓰지 말고 사람 앞에 놓기.

### Week 1 (Feb 13-19)
- [x] MVP 코드 완성
- [x] 27개 테스트 통과
- [x] 사업계획서 / PRD / 로드맵 작성
- [ ] Railway 또는 Render에 배포
- [ ] 커스텀 도메인 연결 (pageguard.dev)
- [ ] SSL 인증서 설정
- [ ] Stripe 테스트 키로 결제 플로우 검증
- [ ] 실제 웹사이트 5개 이상 스캔 테스트

### Week 2 (Feb 20-28)
- [ ] Stripe 라이브 키 전환
- [ ] Reddit 포스트 시작 (3-5개)
  - r/smallbusiness: "Free ADA compliance scan - deadline is April 24"
  - r/webdev: "I built an accessibility scanner, try it free"
  - r/entrepreneur: "ADA lawsuit risk checker for SMBs"
  - r/legaladvice: "ADA website compliance - what you need to know"
  - r/Wordpress: "Free WCAG scan for your WordPress site"
- [ ] Indie Hackers 프로필 + 빌드 스토리
- [ ] Twitter/X 계정 생성 + 첫 스레드

**Milestone:** 무료 가입 50명+, 실제 스캔 100회+

---

## Phase 2: Launch & First Revenue (Mar 1-31, 2026)

**Goal:** 첫 유료 고객 확보. Product Hunt 런칭.

### Week 3-4 (Mar 1-14)
- [ ] Product Hunt 런칭 준비
  - 스크린샷, 데모 GIF
  - 런칭 메이커 프로필
  - 사전 팔로워 확보
- [ ] Product Hunt 런칭 실행
- [ ] SEO 콘텐츠 발행
  - "ADA Website Compliance Checklist 2026"
  - "WCAG 2.2 Requirements Explained Simply"
  - "How to Fix Common Accessibility Issues"
- [ ] PDF 리포트 생성 기능 구현 (v1.1)
- [ ] 예약 스캔 기능 구현 (APScheduler)
- [ ] 이메일 알림 시스템 구현

### Week 5-6 (Mar 15-31)
- [ ] 웹 에이전시 직접 아웃리치 시작
  - Upwork/Clutch에서 에이전시 리스트 수집
  - 주 50개 콜드 이메일
  - 무료 스캔 결과 + "클라이언트에게 이 리포트를 보내세요" pitch
- [ ] 유료 전환 A/B 테스트
  - 무료 스캔 후 업그레이드 프롬프트 최적화
  - 이메일 드립 캠페인 (가입 후 Day 1, 3, 7)
- [ ] Google Ads 소규모 실험 ($5-10/day)
  - 키워드: "ADA compliance scan", "WCAG checker", "website accessibility audit"

**Milestone:** 유료 고객 5명+, MRR $200+

---

## Phase 3: Scale & Deepen (Apr 1-30, 2026)

**Goal:** $1K MRR 달성. ADA 데드라인 (Apr 24) 직전 최대 수요 기간.

### Technical
- [ ] Playwright 기반 심층 스캔 구현 (v1.2)
  - JavaScript 렌더링 후 접근성 체크
  - 색상 대비(color contrast) 실제 계산
  - 키보드 네비게이션 기본 테스트
- [ ] 스캔 속도 최적화
  - 비동기 처리 (Celery + Redis)
  - 스캔 큐잉
- [ ] 컴플라이언스 배지 기능

### Growth
- [ ] "ADA 데드라인 D-Day" 마케팅 캠페인
- [ ] 케이스 스터디: 첫 유료 고객의 성공 사례
- [ ] 파트너십: WordPress 호스팅 업체와 협업
- [ ] Referral 프로그램 (추천인에게 1개월 무료)

**Milestone:** $1,000 MRR, 유료 고객 15-35명

---

## Phase 4: Optimize & Automate (May 2026)

**Goal:** 안정적 성장 기반 구축. 자동화.

- [ ] 온보딩 자동화
  - 가입 → 첫 스캔 → 결과 → 업그레이드 퍼널 자동화
  - 이메일 시퀀스 최적화
- [ ] Churn 관리
  - 이탈 조짐 감지 (스캔 안 하는 고객)
  - 리텐션 이메일
- [ ] 스캐너 규칙 확장 (15-20개)
  - 폼 오토컴플릿
  - 미디어 캡션/자막
  - 테이블 헤더
  - 포커스 인디케이터
- [ ] 성능 대시보드 (사용자용)
  - 시간별 점수 변화 그래프
  - 위반 트렌드

**Milestone:** $2,000+ MRR

---

## Phase 5: Expand (Jun 2026+)

**Goal:** 제품 확장 & 시장 확대.

- [ ] 팀 액세스 기능 (Agency 플랜)
- [ ] 클라이언트 포탈 (에이전시 → 클라이언트 리포트 공유)
- [ ] WordPress 플러그인
- [ ] Slack 알림 인테그레이션
- [ ] 다국어 지원 (한국어, 일본어, 독일어)
- [ ] 유럽 EAA (European Accessibility Act) 대응
- [ ] 연간 결제 옵션 (20% 할인)

**Milestone:** $5,000+ MRR

---

## Key Decision Points

| 시점 | 확인 사항 | 판단 기준 |
|------|-----------|-----------|
| Feb 28 | 시장 반응 검증 | 무료 가입 50명 미만 → 메시징 수정 또는 피봇 검토 |
| Mar 31 | 첫 수익 달성 | 유료 0명 → 가격/기능 재검토 |
| Apr 24 | ADA 데드라인 후 수요 | 수요 급감 → 유럽 EAA/일반 WCAG 수요로 피봇 |
| Jun 30 | $1K MRR 도달 여부 | 미달 → 제품/시장/가격 전면 재검토 |

---

## Risk Mitigation Timeline

```
Feb: 배포 + 검증 → 반응 없으면 빠르게 메시징 수정
Mar: 유료 전환 → 안 되면 가격/기능 조정 (free → freemium 강화)
Apr: ADA 데드라인 → 데드라인 후에도 수요 있는지 확인
May: 안정화 → 자동화로 운영 비용 최소화
Jun: 확장 or 피봇 → 데이터 기반 의사결정
```

---

## Metrics Dashboard

| Metric | Week 1 | Month 1 | Month 2 | Month 3 |
|--------|--------|---------|---------|---------|
| 무료 가입 | 10 | 50 | 150 | 300 |
| 유료 고객 | 0 | 3 | 10 | 25 |
| MRR | $0 | $150 | $500 | $1,000+ |
| 일 스캔 수 | 5 | 30 | 80 | 150 |
| Churn | - | - | <5% | <5% |
