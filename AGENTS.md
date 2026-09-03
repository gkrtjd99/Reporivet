<!-- reporivet:start -->
# Repository Agent Operating Contract

`AGENTS.md` is the canonical, host-neutral entry point for repository work. Host adapters may import it, but they do not replace its authority.

## Start here

1. Read [`docs/README.md`](docs/README.md) for the knowledge and generated-surface map.
2. For substantive work, the Main Skill creates or resumes exactly one matching ordinary Markdown Plan in [`docs/exec-plans/active/`](docs/exec-plans/active/); Reporivet setup itself never creates a Plan.
3. Read only the current authority, code, and tests named by that Plan or the local task.
4. Use the project-owned commands documented in [`docs/QUALITY.md`](docs/QUALITY.md) and [`docs/OPERATIONS.md`](docs/OPERATIONS.md).

The default package onboarding is integrated `reporivet setup`. It is a bounded one-shot package-side transaction: while the user invokes setup, the installed package or an explicitly selected local source may audit, collect visible definition answers, render an exact preview, and apply the approved target changes. `reporivet init` is structure-only and `reporivet define` remains the lower-level resumable definition interface. Setup does not spawn or dispatch Agents, execute project commands, create a Plan, or install a target runtime. After approved setup, the package may be removed and ordinary target work continues from project-owned Markdown, Plans, runbooks, Git, project commands, and host-native Agents.

Do not preload every document, dependency tree, cache, generated output, or historical record.

## Sources of truth

- Product intent and requirements: [`docs/PRODUCT.md`](docs/PRODUCT.md) and [`docs/product-specs/`](docs/product-specs/)
- Current structure and dependency direction: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Design and accessibility: [`docs/DESIGN.md`](docs/DESIGN.md) and [`docs/design-docs/`](docs/design-docs/)
- Shared engineering defaults, including Ablation: [`docs/design-docs/core-beliefs.md`](docs/design-docs/core-beliefs.md)
- Quality and project-owned verification: [`docs/QUALITY.md`](docs/QUALITY.md)
- Running, release, observation, backup, rollback, recovery, and incidents: [`docs/OPERATIONS.md`](docs/OPERATIONS.md) and [`docs/runbooks/`](docs/runbooks/)
- Security: [`docs/SECURITY.md`](docs/SECURITY.md)
- Plan lifecycle: [`docs/PLANS.md`](docs/PLANS.md)
- Durable decisions and historical execution: [`docs/decisions/`](docs/decisions/) and [`docs/exec-plans/completed/`](docs/exec-plans/completed/)

When current sources conflict, stop and report the conflict. Do not silently choose the easiest interpretation.

## One-shot generated-target boundary

A fresh target receives project-owned authority documents, Plan templates and directories, deterministic static runbooks, and at most an exact root `CLAUDE.md` adapter containing only `@AGENTS.md`. It receives no Reporivet role or procedure Skill, `.reporivet-version`, generated `.claude/settings.json`, copied module or runtime, doctor gate, registry or package-resolution instruction, command wrapper, or hidden state.

Only a complete, unique, user-confirmed strict structured procedure record with exactly these nine fields—`slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, and `rollback`—qualifies for a static runbook. The output is ordinary Markdown at `docs/runbooks/<slug>.md`; it has no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration. Incomplete, malformed, generic, inferred, Proposed, Open, Sources-only, or duplicate records produce no runbook. A project may add or maintain its own operational material; Reporivet does not generate a continuing target Skill.

An optional external user-scoped `/reporivet-setup` wrapper is outside the target. It is instruction-only, relays the deterministic package-side preview/apply flow, never installs or resolves Reporivet, and never edits target files itself. An explicit setup rerun may classify legacy role/procedure Skills, settings, markers, or managed blocks only through exact canonical ownership evidence. Destructive cleanup is preview-bound, requires an external backup, revalidates preimages, rolls back the transaction on failure, and refuses later rollback after user changes; modified, ambiguous, unsafe, symlinked, nonregular, and project-owned paths are preserved or refused.

## Main, implementation, and verification

- **Main** owns user intent, scope, non-goals, acceptance criteria, decomposition, dispatch order, integration, decisions, and final evidence judgment. Main's host-native procedure may describe dispatch, but Reporivet itself does not spawn or dispatch Agents. Main alone serializes Plan edits and terminal movement.
- **Task Owner** is the default role for every broad or multi-part root and has `May delegate: yes`. The Owner first returns a finite child manifest inside its approved envelope; Main serializes accepted child rows and complete matching packets into the Plan, then resumes that serialized Owner. Only the resumed Task Owner dispatches its declared dependency-ready descendants through host-native Agent execution.
- **Implementation Sub** receives one bounded Task Packet with exact reads, allowed writes, protected paths, acceptance criteria, project-owned commands, stop conditions, and return evidence. It must not broaden scope, change acceptance, delegate again, or approve its own work.
- **Verification Sub** starts from a fresh context, identifies the integrated candidate, treats implementation narration as unverified, runs applicable project-owned checks, and returns criterion-level results and residual risks. It is read-only, nonrepairing, and nondelegating unless Main assigns a separate implementation packet.

### Broad-milestone native-Agent dispatch

For every broad or multi-part root, the default packet is `Role: Task Owner` with `May delegate: yes`. Narrow or inherently serial roots remain direct nondelegating leaves. This is a host/project operating rule, not a Reporivet runtime:

`T<n> (broad root Owner) -> T<n>-A/B/C/... (declared child packets, all ready leaves dispatched concurrently) -> T<n>-I (Owner-local aggregation) -> T<n>-V1/V2/... (parallel fresh verification)`

Main dispatches independent root Owners concurrently. Each Owner first returns a finite child manifest within its approved envelope; Main alone serializes the accepted child rows and complete matching packets into the Plan, freezes their boundaries, and resumes that serialized Owner. Only the resumed serialized Task Owner dispatches its own declared dependency-ready descendants through host-native Agent execution. Ordinary leaf Agents never delegate. A narrow or inherently serial root follows its declared direct, nondelegating path instead.

Every child row retains an explicit owner and matching bounded packet. Descendants inherit the parent's scope, acceptance, non-goals, protected paths, child budget, and frozen interfaces and cannot broaden them. Parallel mutable siblings require disjoint allowed-write sets and separate exact-baseline worktrees. Owner-local aggregation is distinct from Main's final repository integration; fresh verification nodes depend on the integrated candidate and are read-only, nonrepairing, and nondelegating.

Reporivet installs no scheduler, dispatcher, task store, lease, lock, command runner, Gate, evidence archive, automatic closure, hidden state, or other runtime for this workflow. It installs no Agent spawn/dispatch mechanism or project command execution engine; project commands and CI remain project/host-owned. Meaningful behavior changes should separate implementation and verification contexts. Main integrates returned evidence without normally repeating the verifier's detailed command run.

## Working boundaries

- Prefer the smallest durable change that satisfies current requirements.
- Preserve explicit ownership and dependency direction.
- Do not add speculative infrastructure, compatibility shims, command runners, generated workflows, task databases, journals, evidence archives, or hidden orchestration state.
- Stop before changing public APIs, persisted data, authentication, authorization, payments, infrastructure, or production deployment unless the approved Plan explicitly covers the change.
- Do not weaken acceptance tests, rewrite unrelated code, add production dependencies, or perform external actions without explicit authority.
- Record out-of-scope discoveries in the active Plan or [`docs/exec-plans/tech-debt-tracker.md`](docs/exec-plans/tech-debt-tracker.md); do not implement them implicitly.

## Project-specific working agreements

### Confirmed

- Python 3.11 or newer is required for package work.
- Exact project-owned checks and operational commands live in `docs/QUALITY.md` and `docs/OPERATIONS.md`.
- Current implementation work is coordinated through one active Markdown Plan when the change is substantive.
- Package absence after approved setup is expected and is not an unknown, blocker, or residual risk for ordinary target work.

### Proposed

- None.

### Open

- None.

### Sources

- [`docs/decisions/ADR-0002-one-shot-bootstrapper-boundary.md`](docs/decisions/ADR-0002-one-shot-bootstrapper-boundary.md)
- [`docs/product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md`](docs/product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md)
- [`docs/design-docs/DESIGN-REPORIVET-004-one-shot-setup.md`](docs/design-docs/DESIGN-REPORIVET-004-one-shot-setup.md)
- [`docs/QUALITY.md`](docs/QUALITY.md)
- [`docs/OPERATIONS.md`](docs/OPERATIONS.md)
- [`docs/PLANS.md`](docs/PLANS.md)
<!-- reporivet:end -->
