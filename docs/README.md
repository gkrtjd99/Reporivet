# Reporivet Knowledge Map

This directory records current product intent, architecture, quality, security, source plans, decisions, experiments, and historical context. It does not impose a document schema on initialized projects.

## Reading protocol

현재 작업에 해당하는 아래 경로를 선택한다. 관련 문서가 가리키는 명세·코드·검사를 필요한 범위에서 읽는다. 모든 문서를 미리 읽거나 진입점을 반복해서 읽을 필요는 없다.

## Stable entry points

| Need | Read |
|---|---|
| Product purpose and current requirements | [`PRODUCT.md`](PRODUCT.md), [`product-specs/SPEC-REPORIVET-003-agent-entrypoints.md`](product-specs/SPEC-REPORIVET-003-agent-entrypoints.md) |
| Current architecture and dependency direction | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) |
| Quality expectations and evaluation limits | [`QUALITY.md`](QUALITY.md) |
| Security boundaries and controls | [`SECURITY.md`](SECURITY.md) |
| Engineering principles | [`design-docs/core-beliefs.md`](design-docs/core-beliefs.md) |
| Current complex work and manual plan policy | [`PLANS.md`](PLANS.md), [`exec-plans/active/`](exec-plans/active/) |
| Entrypoint migration | [`references/entrypoint-migration.md`](references/entrypoint-migration.md) |
| Agent navigation evaluation | [`references/agent-navigation-evaluation.md`](references/agent-navigation-evaluation.md) |
| Durable decisions | [`decisions/`](decisions/) |
| Historical execution | [`exec-plans/completed/`](exec-plans/completed/) |

## Route by change type

| 하려는 변경 | 먼저 볼 문서 | 이어서 볼 근거 |
|---|---|---|
| CLI 동작이나 생성 결과 변경 | [`PRODUCT.md`](PRODUCT.md), [`product-specs/SPEC-REPORIVET-003-agent-entrypoints.md`](product-specs/SPEC-REPORIVET-003-agent-entrypoints.md) | 관련 구현과 테스트 |
| 파일 쓰기·관리 블록·소유권 변경 | [`SECURITY.md`](SECURITY.md), [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | 파일 갱신 구현과 안전성 테스트 |
| 구조·의존성·설계 변경 | [`../ARCHITECTURE.md`](../ARCHITECTURE.md), [`design-docs/index.md`](design-docs/index.md) | 관련 설계 원칙과 결정 |
| 검사 방법이나 완료 기준 확인 | [`QUALITY.md`](QUALITY.md) | 실제 검사 스크립트와 테스트 |
| 복잡하거나 위험한 변경 계획 | [`PLANS.md`](PLANS.md) | 관련 현재 문서와 진행 중 계획 |
| 문서 내용 수정 | 수정 대상 문서의 원본 근거 | 영향을 받는 링크·관련 문서 |
| 에이전트 탐색 평가 | [`references/agent-navigation-evaluation.md`](references/agent-navigation-evaluation.md) | 평가 프로토콜과 제어된 fixture |
| 과거 결정의 이유 조사 | 관련 [`decisions/`](decisions/) 또는 [`exec-plans/completed/`](exec-plans/completed/) | 현재 문서에서 대체 여부 확인 |

## Document authority and lifecycle

- `AGENTS.md` remains a compact portable routing contract. This source repository authors its portable block in `CLAUDE.md` and projects it with `./dev/agent-contract-sync`; generated targets do not receive the helper or this source-only file.
- Current-state documents describe implemented reality and verified intent. User-owned target documents remain authoritative for their own meaning.
- Observed paths are non-authoritative evidence. A path's existence does not prove that its contents are current requirements or a runnable command.
- Active ExecPlans are living source records manually copied from the template. Completed plans and accepted decisions are historical records; supersede them rather than rewriting their bodies.
- Evaluation notes distinguish actual before/after observations from hypotheses and do not claim semantic routing or general performance from a bounded fixture. PLAN-0007's prior-template observations remain historical and are not evidence for the current UX template.
- `init`/`upgrade --dry-run` previews are escaped human unified diffs from one immutable operation and may contain instruction content; `audit` remains content-free. Fingerprints identify a plan but are not approval or locking.
- Retirement requires an explicit plan action, replacement or rationale, and removal of current references.

## Historical material

The previous runtime-centered specifications, designs, module contract, and migration note remain in this repository as historical records with supersession banners. They are not current product authority. The accepted ADR-0001 body is preserved unchanged; the current boundary is ADR-0002.
