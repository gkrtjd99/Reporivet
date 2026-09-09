---
id: {{PLAN_ID}}
kind: exec-plan
status: proposed
owner: main
area: {{AREA}}
created: {{DATE}}
updated: {{DATE}}
base_commit: "{{BASE_COMMIT}}"
---

# {{PLAN_TITLE}}

Copy this template manually for a source plan; it is not generated target output.

## Purpose / Big Picture

TODO: explain what becomes observably possible and how a person or agent can confirm it.

## Progress

- [ ] Establish current behavior and constraints.
- [ ] Deliver the smallest working milestone.
- [ ] Integrate and independently review the candidate.
- [ ] Resolve documentation impact and follow-ups.

## Context and Orientation

TODO: explain relevant repository paths, modules, terms, current behavior, and authoritative documents for a reader with no chat history.

## Scope

- TODO

## Non-goals

- TODO

## Acceptance Criteria

- **AC-1:** TODO observable behavior or evidence.

## Milestones

### M1 — Smallest observable slice

TODO: state the working behavior, implementation outline, and verification.

## Task Packets

### T1 — Explore and establish the change boundary

#### State

ready

#### Task type

support

#### Depends on

none

#### Execution constraints

- Required capabilities: TODO
- Tool access: TODO
- Concurrency: TODO
- Retry budget: TODO
- Time budget: TODO

#### Outcome

TODO

#### Non-goals

TODO

#### Read

TODO: exact documents and paths.

#### Allowed writes

없음. Main이 이 계획에 결과를 기록한다. 구현 쓰기는 별도 허용 경로를 배정받아야 한다.

#### Protected paths

Everything not explicitly allowed.

#### Acceptance

AC-1

#### Verify

Actual repository or project-owned read-only checks; no inferred commands.

#### Stop conditions

Conflicting sources, public-contract or data-migration impact, missing authority, or scope expansion.

#### Result

TODO: status; exact integrated candidate (exact target commit SHA or base + nonignored file hashes/modes + deletion list) or read-only scope; execution environment; commands run; verification scope; results and evidence; blockers; limitations; verifier recommendation; Main or human approval separately.

### T2 — Implement the smallest working slice

#### State

blocked

#### Task type

implementation

#### Depends on

T1

#### Execution constraints

- Required capabilities: TODO
- Tool access: TODO
- Concurrency: TODO
- Retry budget: TODO
- Time budget: TODO

#### Outcome

TODO

#### Non-goals

TODO

#### Read

TODO

#### Allowed writes

TODO

#### Protected paths

All paths outside Allowed writes.

#### Acceptance

AC-1

#### Verify

Actual focused checks named by the task; do not infer or install project commands.

#### Stop conditions

Allowed writes are insufficient, acceptance must change, a protected contract changes, or the same approach fails twice.

#### Result

TODO: status; exact integrated candidate (exact target commit SHA or base + nonignored file hashes/modes + deletion list); changed paths; environment; commands; verification scope; evidence; blockers; limitations; recommendation; Main or human approval separately.

### T3 — Independently review the integrated candidate

#### State

blocked

#### Task type

verification

#### Depends on

T2

#### Execution constraints

- Required capabilities: TODO
- Tool access: TODO
- Concurrency: TODO
- Retry budget: TODO
- Time budget: TODO

#### Outcome

Judge the exact integrated candidate in a separate context without relying on implementer explanation. If a separate context is unavailable, report that independent verification was not performed.

#### Non-goals

Redesign or unrelated cleanup.

#### Read

This plan, changed code, tests, and current-state documents.

#### Allowed writes

Verifier evidence only unless Main assigns a repair.

#### Protected paths

Implementation and acceptance criteria.

#### Acceptance

All criteria in this plan.

#### Verify

Actual source or project-owned checks plus declared reproduction commands.

Verifier는 반례·실패 경로·회귀를 능동적으로 찾고 테스트 자체의 가정도 의심한다. 수정 후에는 새 exact candidate를 재검증한다.

#### Stop conditions

The candidate differs from the reviewed target, evidence is unavailable, or requirements conflict.

#### Result

TODO: status; exact integrated candidate (exact target commit SHA or base + nonignored file hashes/modes + deletion list) or read-only scope; environment; commands; verification scope; results and evidence; blockers; limitations; verifier recommendation; Main or human approval separately. If no independent context was available, state that independent verification was not performed.

결함에는 위반한 요구사항·trigger·영향과 재현 또는 구체적인 코드 근거를 제시한다. 우려·취향·미검증 영역은 결함과 구분하고 결함 개수를 강제하지 않는다.

결함 보고에는 기존 테스트·검사가 해당 실패 경로를 왜 검출하지 못하는지 설명한다. 관련 검사를 확인하지 못했다면 그 한계를 명시한다.

Verifier는 각 수락 기준을 `PASS`(증거로 충족 확인), `FAIL`(위반 또는 필요한 동작 누락), `UNPROVEN`(확보한 증거로 충족 여부 미확인)으로 판정하고 근거를 연결한다. 의도·추정·다른 검사의 성공만으로 `UNPROVEN`을 `PASS`로 바꾸지 않는다. 필수 수락 기준에 `FAIL` 또는 `UNPROVEN`이 남으면 완료 수락을 추천하지 않는다. 최종 수락 권한은 Main 또는 human reviewer에게 남는다.

## Architecture Impact

TODO: affected modules, dependency edges, invariants, and required machine checks; write `none` with a reason when there is no impact.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| `docs/PRODUCT.md` | TODO: none/create/update/supersede/retire | TODO | Main | pending |
| `ARCHITECTURE.md` | TODO | TODO | Main | pending |

## Interfaces and Dependencies

Main은 Task 간 공유 인터페이스·경로 소유권·의존성·통합 순서를 설계한다. 지정된 Lead는 상위 계약 안의 leaf 분해·경계 설계를 담당한다. TODO: 필요한 경계와 소유자·의존성·통합 순서를 적는다.

공유 계약은 병렬 수행 동안 고정한다. 변경이 필요하면 영향 작업을 멈추고 경계 소유자(Main: Task 간, Lead: parent 내부)가 계약을 조정한 뒤 재배정한다. parent 범위·계약·권한 변경은 Main에게 반환한다. 이 절차는 host/project의 더 제한적인 병렬 정책을 완화하지 않으며, 독립 경계를 만들 수 없으면 순차 수행한다.

- Existing project capability inspected: TODO
- New production dependency: none / TODO
- Public or cross-repository contract impact: none / TODO

## Migration, Rollout, and Recovery

수선 시 Main 또는 지정 Lead는 확인된 결함과 재현 근거를 하나의 요청으로 취합하고, 가능하면 기존 Implementer를 재개한다. 요청에는 현재 후보, 수정 허용 경로, 실패 근거, 재검증 대상을 포함한다. 원인이 불명확하면 추가 구현 전에 범위를 제한한 진단을 수행한다. 기존 시간·재시도 예산과 같은 접근법 두 번 실패 시 중단 조건은 유지한다. 구현자 재개는 별도 문맥의 독립 검증을 대체하지 않으며 수정 후 새 exact candidate를 재검증한다.

TODO: record compatibility, rollout, rollback, retry, idempotency, and cleanup requirements; write `not applicable` with a reason where appropriate.

## Surprises and Discoveries

- {{DATE}} — Plan created; no discoveries recorded yet.

## Decision Log

- {{DATE}} — Initial scope proposed by Main; approval pending.

## Concrete Steps

Run commands from the repository root. Keep this section current and record exact commands and results; do not create a separate task registry or automatic run directory.

1. Read current sources and the matching active plan.
2. TODO implementation or observation step.
3. Run the declared source/project checks.
4. Have an independent reviewer inspect the exact candidate when required.

## Validation and Evidence

각 기준의 Result는 `PASS`, `FAIL`, `UNPROVEN` 중 하나로 기록한다. 실행 전에는 `UNPROVEN`을 사용하고, FAIL/UNPROVEN이면 Evidence에 미충족 사항 또는 증거 부족을 적는다. 판정은 Task state나 Main/human approval을 대체하지 않는다.

| Acceptance criterion | Task | Result | Evidence path or note | Verified candidate | Reviewer recommendation | Main/human approval |
|---|---|---|---|---|---|---|
| AC-1 | T2/T3 | UNPROVEN | pending | pending | pending | pending |

- Integrated target: pending
- Verified candidate: pending
- Acceptance results: pending
- Commands and durable summaries: pending
- Raw transcripts/logs: do not commit unless explicitly required and reviewed.

## Outcomes and Retrospective

TODO: summarize delivered behavior, remaining limits, and what should become a reusable rule, test, tool, or document.

## Follow-ups

Promote unresolved items to [`tech-debt-tracker.md`](tech-debt-tracker.md) or the declared external backlog before completion.

- none yet
