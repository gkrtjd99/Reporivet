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

Roles are responsibilities, not model identity. Each Task Packet states required capabilities, tool access, concurrency, retry, and time budget. Detailed delegation, contract restoration, host boundaries, and Result requirements live in [`docs/PLANS.md`](docs/PLANS.md).

- Main owns purpose/intent, scope, non-goals, acceptance, permissions, plan lifecycle, and global design. Main fixes each task's bounded authoritative source and separate execution-context boundary, shared interfaces, path ownership, dependencies, integration order, and the exact verification target; Main reads only bounded code/evidence needed for judgment, not broad exploration, repeated implementation, raw-log analysis, or long debugging in the Main session. If reading expands, isolate it as a separate bounded task. Difficult work uses a separate required stronger execution context, not a Main implementation session; integration execution may be delegated, but Main retains order, exact candidate, final integration, evidence acceptance, and completion approval. Main does not replace a delegated Owner's executable design judgment by implementing it directly.
- Keep hierarchy minimal. When delegation is useful, the maximum depth is Main → Task Owner → leaf, and the more restrictive host/project policy always wins.
- Only an explicitly designated Task Owner may delegate within its assigned parent packet. Without further approval for each bounded leaf, it composes packets whose allowed writes are a subset of the parent, whose protected paths, acceptance criteria, and stop conditions are inherited unchanged, and whose execution stays within the parent budget. The Owner directly owns executable design, verification method, comparison of important diffs and decisive evidence, and repair-cause judgment; those judgments must not be delegated wholesale. No coding share, direct-implementation ratio, or call-count quota is imposed. Scope, permission, acceptance, or shared-contract changes return to Main; the Owner cannot edit the durable plan, perform final integration, or approve acceptance.
- Every leaf receives one bounded packet and its assigned acceptance criteria. A leaf must not delegate, broaden scope, change acceptance, write outside allowed paths, create durable work systems, or approve its own work. The packet may permit local implementation, investigation, and check choices; core design, scope, permissions, acceptance criteria, and prohibitions cannot be changed and return to the Owner or Main. Delegation must not be used to bypass a denied action.
- An Implementer owns only assigned writes and focused verification. An Independent Verifier judges the exact candidate in a separate context against current requirements and execution environment without relying on implementer or Owner conclusions; Owner comparison is not independent verification. If separation is unavailable, report that independent verification was not performed.
- Read-only work may run in parallel. Mutable work is sequential unless all existing conditions hold: disjoint write paths, separate Git worktrees, frozen shared interfaces, Main-owned integration, and fresh verification of the integrated candidate.
- 공유 계약은 병렬 수행 동안 고정한다. 변경이 필요하면 영향 작업을 멈추고 경계 소유자(Main: Task 간, Owner: parent 내부)가 계약을 조정한 뒤 재배정한다. parent 범위·계약·권한 변경은 Main에게 반환한다. 이 절차는 host/project의 더 제한적인 병렬 정책을 완화하지 않으며, 독립 경계를 만들 수 없으면 순차 수행한다.
- Independent verification, focused checks, verdict definitions, defect reports, repair, and Result/evidence details follow [`docs/PLANS.md`](docs/PLANS.md); Main owns final canonical verification and acceptance. A required acceptance criterion left `FAIL` or `UNPROVEN` blocks an acceptance recommendation; final acceptance authority remains with Main or a human reviewer.

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
