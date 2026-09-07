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

Initialize and safely maintain repository-local, document-first operating harnesses for coding agents.

This file is a short map and operating contract. Durable knowledge belongs in the linked, version-controlled artifacts.

## Start here

1. Run `./dev/context` with `--path`, `--area`, or `--plan` when one is known.
2. Read [`docs/README.md`](docs/README.md) for the knowledge map.
3. Check [`docs/exec-plans/active/`](docs/exec-plans/active/) for matching complex work.
4. Read only the source-of-truth documents and code needed by the current task.

Do not preload all documentation, dependencies, generated output, caches, or raw logs.

## Sources of truth

- Product intent and current requirements: [`docs/PRODUCT.md`](docs/PRODUCT.md) and [`docs/product-specs/`](docs/product-specs/)
- Project-definition procedure: [`docs/references/project-definition-protocol.md`](docs/references/project-definition-protocol.md)
- Current system structure: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Design principles and durable design documents: [`docs/design-docs/core-beliefs.md`](docs/design-docs/core-beliefs.md) and [`docs/design-docs/`](docs/design-docs/)
- Quality, security, and reliability: [`docs/QUALITY.md`](docs/QUALITY.md), [`docs/SECURITY.md`](docs/SECURITY.md), and `docs/RELIABILITY.md` when present
- Planning policy and active work: [`docs/PLANS.md`](docs/PLANS.md), [`docs/exec-plans/active/`](docs/exec-plans/active/)
- Historical execution and decisions: [`docs/exec-plans/completed/`](docs/exec-plans/completed/), [`docs/decisions/`](docs/decisions/)

When current sources conflict, stop and report the conflict. Do not silently choose the easiest interpretation.

## Work classification

Small, local, reversible changes may proceed without a durable plan. Create an ExecPlan for cross-cutting, risky, long-running, multi-agent, public-contract, persistent-data, security, infrastructure, or deployment changes.

Use `./dev/new-plan "<title>" --area <area>`. Tasks live inside that plan; do not create a second task registry, state database, packet directory, or orchestration layer.

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

- Setup: `./dev/bootstrap`
- Definition status/validation/finalization: `./dev/define`
- Read-only repository inventory: `./dev/audit`
- Derived path map: `./dev/code-map`
- Routed context: `./dev/context`
- Fast feedback: `./dev/check`
- Canonical completion gate: `./dev/verify`
- Observable smoke checks: `./dev/smoke`
- Tracked-secret guard: `./dev/security-check`
- Document catalog: `./dev/docs-index`
- Maintenance candidates: `./dev/garden`

The committed [`dev/harness.toml`](dev/harness.toml) is authoritative. Missing configured tools fail visibly; checks must not disappear because of the local environment.

## Done means

A change is complete only when observable behavior and non-goals are satisfied, the integrated commit passes applicable verification, independent review is complete when required, current-state documents match reality, Documentation Impact is resolved, decisions and follow-ups are recorded, and the Main Agent or human reviewer accepts the evidence.

An agent saying “done” is not completion evidence.
<!-- reporivet:end -->
<!-- reporivet:portable:end -->
