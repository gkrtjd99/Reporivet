# Source contract authoring

This source repository authors its portable operating contract in the block below.
Edit this block, then run `./dev/agent-contract-sync`; do not edit `AGENTS.md` directly.
`./dev/agent-contract-sync --check` detects drift without writes. Provider-specific
instructions outside the block are not projected. Generated target repositories
keep AGENTS canonical and do not receive this source-only tool or CLAUDE file.

<!-- reporivet:portable:start -->
<!-- reporivet:start -->
# Reporivet Repository Operating Contract

## Purpose

Initialize and safely maintain a small repository-local entrypoint for coding agents.

This file is a short map and operating contract. Durable knowledge belongs in the linked, version-controlled artifacts.

## Start here

1. Read [`docs/README.md`](docs/README.md) for the source knowledge map.
2. Read [`docs/PRODUCT.md`](docs/PRODUCT.md) and [`docs/product-specs/SPEC-REPORIVET-003-agent-entrypoints.md`](docs/product-specs/SPEC-REPORIVET-003-agent-entrypoints.md) for current requirements.
3. Read [`ARCHITECTURE.md`](ARCHITECTURE.md), [`docs/QUALITY.md`](docs/QUALITY.md), and [`docs/SECURITY.md`](docs/SECURITY.md).
4. Check [`docs/exec-plans/active/`](docs/exec-plans/active/) for matching complex work, then read only the source-of-truth documents and code needed by the current task.

Do not preload all documentation, dependencies, generated output, caches, or raw logs.

## Sources of truth

- Product intent and current requirements: [`docs/PRODUCT.md`](docs/PRODUCT.md) and [`docs/product-specs/SPEC-REPORIVET-003-agent-entrypoints.md`](docs/product-specs/SPEC-REPORIVET-003-agent-entrypoints.md)
- Current system structure: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Quality and evaluation boundary: [`docs/QUALITY.md`](docs/QUALITY.md)
- Security and file-ownership boundary: [`docs/SECURITY.md`](docs/SECURITY.md)
- Design principles and durable design documents: [`docs/design-docs/core-beliefs.md`](docs/design-docs/core-beliefs.md) and [`docs/design-docs/`](docs/design-docs/)
- Planning policy and active work: [`docs/PLANS.md`](docs/PLANS.md), [`docs/exec-plans/active/`](docs/exec-plans/active/)
- Historical execution and decisions: [`docs/exec-plans/completed/`](docs/exec-plans/completed/), [`docs/decisions/`](docs/decisions/)

When current sources conflict, stop and report the conflict. Do not silently choose the easiest interpretation.

## Work classification

Small, local, reversible changes may proceed without a durable plan. Create an ExecPlan for cross-cutting, risky, long-running, multi-agent, public-contract, persistent-data, security, infrastructure, or deployment changes.

Copy [`docs/exec-plans/_template.md`](docs/exec-plans/_template.md) manually for a new source plan. Tasks live inside that plan; do not create a second task registry, state database, packet directory, or orchestration layer.

## Agent operating roles

Roles are defined by responsibility, not runtime identity. Each Task Packet states the required capabilities, tool access, concurrency, retry, and time budget for that task.

- Main owns intent, scope, non-goals, acceptance criteria, permissions (allowed writes and protected paths), decomposition, delegation, plan writing and lifecycle, integration order, the verification target, final integration, evidence acceptance, and completion approval.
- Main은 Task 간 공유 인터페이스·경로 소유권·의존성·통합 순서를 설계한다.
- Small tasks should omit unnecessary hierarchy. When delegation is useful, the maximum depth is Main → Task Lead → leaf.
- Only an explicitly designated Task Lead may delegate within its assigned parent Task Packet. Without further approval for each leaf, it may compose and assign bounded leaf packets whose allowed writes are a subset of the parent, whose protected paths, acceptance criteria, and stop conditions are inherited unchanged, and whose execution stays within the parent budget. Lead의 역할은 상위 계약 안의 leaf 분해·경계 설계·packet 구성과 배정, scheduling leaf work, coordinating repairs, consolidating results로 제한한다. Scope changes return to Main; the Lead cannot change permissions or plan state, edit the durable ExecPlan, perform final integration, or approve acceptance.
- Every leaf receives one bounded Task Packet. A leaf must not delegate, broaden scope, change acceptance, write outside allowed paths, create durable work systems, or approve its own work. Delegation cannot expand authority beyond the parent packet or host execution permissions and must not be used to bypass a denied action.
- An Implementer owns only the assigned writes and focused verification. An Independent Verifier judges an exact candidate in a separate context without relying on implementer explanation; when the host cannot provide that separation, report that independent verification was not performed.
- Read-only exploration, review, test analysis, and log analysis may run in parallel. Parallel writes require all of: disjoint write paths, separate Git worktrees, frozen shared interfaces, Main-owned integration, and fresh verification of the integrated commit.
- 공유 계약은 병렬 수행 동안 고정한다. 변경이 필요하면 영향 작업을 멈추고 경계 소유자(Main: Task 간, Lead: parent 내부)가 계약을 조정한 뒤 재배정한다. parent 범위·계약·권한 변경은 Main에게 반환한다. 이 절차는 host/project의 더 제한적인 병렬 정책을 완화하지 않으며, 독립 경계를 만들 수 없으면 순차 수행한다.
- Verifier는 반례·실패 경로·회귀를 능동적으로 찾고 테스트 자체의 가정도 의심한다. 수정 후에는 새 exact candidate를 재검증한다. 결함에는 위반한 요구사항·trigger·영향과 재현 또는 구체적인 코드 근거를 제시한다. 우려·취향·미검증 영역은 결함과 구분하고 결함 개수를 강제하지 않는다.
- Verifier는 각 수락 기준을 `PASS`(증거로 충족 확인), `FAIL`(위반 또는 필요한 동작 누락), `UNPROVEN`(확보한 증거로 충족 여부 미확인)으로 판정하고 근거를 연결한다. 의도·추정·다른 검사의 성공만으로 `UNPROVEN`을 `PASS`로 바꾸지 않는다. 필수 수락 기준에 `FAIL` 또는 `UNPROVEN`이 남으면 완료 수락을 추천하지 않는다. 최종 수락 권한은 Main 또는 human reviewer에게 남는다.
- 결함 보고에는 기존 테스트·검사가 해당 실패 경로를 왜 검출하지 못하는지 설명한다. 관련 검사를 확인하지 못했다면 그 한계를 명시한다.
- 수선 시 Main 또는 지정 Lead는 확인된 결함과 재현 근거를 하나의 요청으로 취합하고, 가능하면 기존 Implementer를 재개한다. 요청에는 현재 후보, 수정 허용 경로, 실패 근거, 재검증 대상을 포함한다. 원인이 불명확하면 추가 구현 전에 범위를 제한한 진단을 수행한다. 기존 시간·재시도 예산과 같은 접근법 두 번 실패 시 중단 조건은 유지한다.
- Focused task checks provide fast feedback; Main owns the final canonical verification target and acceptance decision. Results stay concise and identify the exact target, environment, commands, verification scope, evidence, blockers, and whether a verdict is a recommendation or approval.

Memory is auxiliary context and never overrides current project sources of truth or higher-priority execution instructions.

## Engineering invariants

- For normative rules and decisions, record reason, scope and prevented failure; review repository and dependency capabilities, official primary sources for external choices, no-change and practical alternatives with rejection reasons, verification/enforcement, and revisit/retirement conditions.
- Deliver working, observable end-to-end slices; keep the integrated repository runnable.
- Choose the smallest durable implementation that meets current requirements and known operating constraints.
- Preserve explicit module ownership and dependency direction; encode stable boundaries in tests or lint rules.
- Inspect existing project facilities and dependencies before adding infrastructure or packages.
- Do not add speculative abstractions, compatibility shims, fallback paths, configuration, or indirection.
- Remove obsolete internal paths atomically. Public contracts, persisted data, deployed protocols, and external configuration require explicit migration, rollout, and rollback decisions.
- A temporary exception requires an owner, exit criteria, removal trigger, and tracked follow-up.
- Optimize for agent legibility: searchable source, deterministic commands, structured logs, inspectable schemas, and actionable errors.

## Stop and escalate before

- changing public APIs, persisted data, authentication, authorization, payments, infrastructure, or production deployment;
- adding or replacing a production dependency;
- writing outside the assigned scope or protected paths;
- weakening an acceptance test merely to make an implementation pass;
- rewriting unrelated code or formatting the repository broadly;
- continuing after the same approach has failed twice.

Record out-of-scope discoveries in the active plan or [`docs/exec-plans/tech-debt-tracker.md`](docs/exec-plans/tech-debt-tracker.md). Do not implement them implicitly.

## Deterministic commands

- Source checks: `PYTHON=python3 ./dev/check`
- Portable contract projection: `./dev/agent-contract-sync` (source repository only)
- Portable contract drift check: `./dev/agent-contract-sync --check` (read-only)

`dev/check` runs the source unit/integration/distribution tests, source contract drift check, Python syntax compilation, and `git diff --check`. It fails visibly when a required command fails; no target runtime, Gate, or automatic plan closure is installed.

## Done means

A change is complete only when observable behavior and non-goals are satisfied, the exact integrated candidate passes applicable verification, independent review is complete when required, current-state documents match reality, Documentation Impact is resolved, decisions and follow-ups are recorded, and the Main Agent or human reviewer accepts the evidence.

An exact candidate is a commit SHA or a base commit with nonignored file hashes, modes, and a deletion list. A fingerprint identifies the reviewed state; it is not approval by itself. Do not create a commit merely to satisfy evidence formatting.

An agent saying “done” is not completion evidence.
<!-- reporivet:end -->
<!-- reporivet:portable:end -->
