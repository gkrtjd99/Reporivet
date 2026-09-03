---
owner: product
status: active
last_reviewed: 2026-09-02
---

# Product

## Product, users, problem, and success

Reporivet is a Python 3.11+ package for establishing a repository-local, document-first operating contract for coding agents during an explicit setup transaction. It performs deterministic discovery, guided definition, setup preview/apply, and explicit legacy transition from the installed package or an explicitly selected local source. The durable result is project-owned Markdown authority, compact Plans, ordinary static runbooks, and at most a thin exact host adapter.

Reporivet is a one-shot package-side bootstrapper, not a permanent executor inside a target repository. Once approved setup has handed off the generated content, the package may be removed without reducing ordinary project work. The project owns commands, tests, CI, deployment, secrets, operations, and acceptance evidence.

## Default onboarding and handoff

`reporivet setup` is the default integrated onboarding path. While invoked, it coordinates deterministic audit, visible guided definition, resumable answers, exact preview, and explicitly approved application. `reporivet init` remains a structure-only, non-overwriting create-if-missing path. Lower-level `reporivet define` remains available for direct draft/resume/status/finalize work. Setup creates no Plan, runtime, target Skill, marker, generated settings, or hidden state; it does not execute project commands or spawn or dispatch Agents.

An optional external user-scoped `/reporivet-setup` wrapper may guide the same deterministic preview/apply flow. It is outside the target, is instruction-only, never installs or resolves Reporivet, and never edits target files itself. Main's host/project procedure creates or resumes the first ordinary Markdown Plan after setup when substantive work needs one.

A fresh target receives canonical authority documents, Plan templates and directories, deterministic static runbooks for eligible procedures, and an optional root `CLAUDE.md` containing exactly `@AGENTS.md` and one trailing newline. It receives no Reporivet role or procedure Skill, `.reporivet-version`, generated `.claude/settings.json`, copied module/runtime, doctor gate, registry instruction, package-resolution instruction, command wrapper, scheduler, dispatcher, task store, Gate, evidence archive, or automatic closure mechanism.

## Static procedure runbooks

A procedure produces output only when its `Confirmed` section contains one complete, unique, user-confirmed strict structured record with exactly these nine fields: `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, and `rollback`. All fields are required; no aliases, extra fields, values, or defaults are inferred. The result is ordinary Markdown at `docs/runbooks/<slug>.md`, with no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration. Incomplete, malformed, generic, inferred, Proposed, Open, Sources-only, or duplicate records produce no runbook. The runbook is descriptive project documentation, not an executor.

## Users and needs

- **Repository maintainers** need an inspectable operating contract that survives package removal.
- **Main agents** need canonical routing, one durable work record, bounded delegation, and explicit evidence ownership.
- **Implementation agents** need narrow Task Packets with exact reads, allowed writes, protected paths, acceptance criteria, and stop conditions.
- **Verification agents and reviewers** need fresh-context, criterion-level evidence tied to an identifiable integrated candidate.

## Current scope

During explicit package-side setup or transition, Reporivet may:

- scan a repository deterministically without sending project content to a model;
- coordinate the integrated `setup` flow while retaining lower-level `define` and structure-only `init`;
- collect plain-language answers through guided definition;
- render a visible Markdown draft with separated evidence classes;
- show an exact setup or legacy-transition preview;
- apply only the approved preview after path-safety and preimage revalidation;
- create missing document-first assets and the optional exact root adapter;
- render static runbooks only for complete, unique, user-confirmed nine-field procedures; and
- back up, apply, restore, or explicitly roll back recognized legacy surfaces through a bounded external transaction.

Reporivet provides no ongoing target diagnosis contract. In particular, `reporivet doctor` is retired rather than optional. Setup validates only its own approved transaction and its postconditions.

The durable target repository contains:

- a host-neutral `AGENTS.md` entry point;
- current product, architecture, design, quality, operations, security, and Plan authority;
- versioned specifications, designs, decisions, Plans, references, and optional static runbooks;
- an optional exact `CLAUDE.md` host adapter; and
- project-owned source, tests, commands, CI, deployment, secrets, Git, operations, and evidence.

The product does not install a copied command executor, target Skill, package marker, generated settings, runtime configuration, command registry, generated CI workflow, task database, journal, evidence archive, or package-independent Reporivet maintenance command into a target.

## Conditional capability artifacts

The universal target authority remains `PRODUCT.md`, `ARCHITECTURE.md`, `DESIGN.md`, `QUALITY.md`, `OPERATIONS.md`, `SECURITY.md`, and `PLANS.md`. When the visible definition draft has an exact capability value in **Confirmed**, setup may also create these ordinary project-owned documents:

- `docs/FRONTEND.md` only for `web_ui=yes`; it records frontend source ownership, framework/routing/components, state and data fetching, forms, styling, accessibility, performance, and client-side loading/error/retry behavior. It does not own service reliability.
- `docs/RELIABILITY.md` only for `deployed_runtime=yes`; it records service/runtime failure modes, SLI/SLO, observability, deployment/rollback, recovery, and incident boundaries. It is supplemental and subordinate to `docs/OPERATIONS.md`, which remains universal operational authority.

Missing, `no`, Proposed, Open, Sources-only, inferred, or otherwise unverified answers create neither optional document. Audit signals and provenance identify sources but do not establish confirmation. Each optional document must state its owner, authority route, constraints, sources, and project-owned verification boundary; `docs/QUALITY.md` owns checks and `docs/OPERATIONS.md` owns operational procedures. Setup selection is not Plan state or verification evidence, and setup does not create a Plan or execute project commands.

## Core workflow

1. **Set up** the target with the integrated `reporivet setup` flow; use structure-only `init` only when guided onboarding is not wanted.
2. **Scan** the target deterministically and keep observations attributable.
3. **Define** the project in plain language through setup or lower-level `define`, preserving uncertainty rather than guessing.
4. **Preview** the complete Markdown draft and exact filesystem changes.
5. **Approve and apply** only after explicit approval, external backup where destructive cleanup is planned, and immediate revalidation.
6. **Hand off** to the Main host/project procedure, which creates or resumes the first ordinary Markdown Plan; setup creates no Plan.
7. **Work** through canonical documents, bounded Task Packets, static runbooks, and project-owned commands; the host, not Reporivet, performs Agent dispatch and command execution.
8. **Verify** the integrated candidate from a fresh context and record criterion-level evidence in the Plan.
9. **Remove the package** after setup when desired; generated Markdown, Plans, runbooks, Git, and project commands remain useful.
10. **Transition legacy artifacts** only through an explicitly approved setup rerun or recognized legacy migration transaction with exact ownership evidence and an external backup.

### Bounded task ownership

Broad or multi-part roots default to `Role: Task Owner` with `May delegate: yes`; narrow or inherently serial roots remain direct nondelegating leaves. Main dispatches independent root Owners concurrently. Each Owner first returns a finite child manifest within its approved envelope, after which Main alone serializes the accepted child rows and complete matching packets into the Plan and resumes that Owner. Only the resumed serialized Task Owner dispatches its own declared dependency-ready descendants through host-native Agent execution; ordinary leaves never delegate.

Descendants inherit the parent's scope, acceptance, non-goals, protected paths, child budget, and frozen interfaces and cannot broaden them. Mutable siblings require disjoint allowed-write sets and separate exact-baseline worktrees. Owner-local aggregation is distinct from Main's final repository integration; fresh verification is read-only, nonrepairing, nondelegating, and candidate-specific. Reporivet provides no scheduler, dispatcher, task database, runner, Gate, evidence archive, automatic closure, hidden state, or workflow runtime.

## Requirements

### Rich content

- Current authority must explain product intent, system boundaries, quality, security, operations, and Plan lifecycle without requiring package internals.
- Durable records must preserve decisions, historical execution, and unresolved follow-ups.
- Confirmed facts, proposals, open questions, and sources must remain visibly distinct.
- Historical and superseded records must not become accidental current authority.

### One-shot independence

- The package may be installed or selected from local source only while the user invokes setup or an explicit package-side transition.
- Generated authority must never instruct an Agent to locate, install, resolve, import, invoke, or verify Reporivet or doctor.
- Package absence after setup is expected and must not be recorded as `UNKNOWN`, blocking, or risky for ordinary target work.
- Project-owned commands and CI are authoritative for execution; Reporivet does not execute them.
- Fresh targets do not receive Reporivet Skills, markers, generated settings, runtime, command wrappers, or hidden state.

### Safety

- Reads and writes must stay beneath a validated repository root, except for the explicitly selected external backup.
- Mutating operations must reject unsafe symlinked or nonregular targets.
- Existing project-owned or ambiguous files must be preserved unless an explicit, fingerprinted transition owns the change.
- Legacy deletion authority requires exact canonical bytes or an exact strict parse-and-rerender proof; path names and markers alone are insufficient.
- A destructive setup rerun or migration must use an external backup, bind approval to the complete preview fingerprint, revalidate immediately before mutation, restore the transaction after a safe apply failure, and refuse rollback that would overwrite later user changes.
- No generated runbook may carry frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration.

## Success criteria

- A maintainer can identify current authority from `AGENTS.md` and `docs/README.md`.
- A substantive change can be coordinated using only one compact Markdown Plan and its Task Packets.
- A verifier can tie results to an integrated candidate and each acceptance criterion.
- Removing Reporivet after setup leaves generated Markdown, ordinary Plans, static runbooks, Git, and project commands useful; only package-side setup or transition capability disappears.
- Complete unique Confirmed procedures alone produce deterministic plain-Markdown runbooks.
- Exact ownership, preview approval, backup binding, path safety, preimage revalidation, transactional cleanup, and guarded later rollback protect existing targets.
- The generated surface stays bounded to current documents, Plan directories/templates, static runbooks, the optional exact adapter, and project-owned content.

## Non-goals

Reporivet does not aim to:

- replace project-specific build, test, release, deployment, observability, backup, recovery, or incident systems;
- provide a general workflow engine, scheduler, queue, lock manager, policy server, runtime, or evidence database;
- infer project facts or promote scanner observations to confirmed requirements;
- install target Skills, model bundles, prompts that encode project authority outside Markdown, or hidden agent memory;
- support arbitrary compatibility layers for retired repository layouts;
- claim that a source checkout, package artifact, release, installation, or deployment has been verified without direct evidence;
- spawn or dispatch Agents, execute project commands, operate CI or deployment, manage execution evidence, or move Plans to terminal states automatically; or
- publish, sign, or release packages as part of package-side behavior.

## Evidence model

### Confirmed

- The source tree implements package-side scan, guided definition, one-shot setup, compact Plan checks, static runbook rendering, and explicit legacy transition boundaries through the current candidate.
- Historical verification of the prior document-first candidate passed AC-1 through AC-10 and AC-12; this is historical evidence, not evidence for a later integrated product candidate.
- Python 3.11 or newer is required and the package declares no production dependencies.
- The console entry point is `reporivet`.
- Completed PLAN-2026-0003 records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive; this is package lifecycle evidence, not a continuing target dependency.

### Proposed

- None.

### Open

- Publication, signing, release, deployment, CI repair/readiness, and a permanent evidence archive remain unestablished and outside this product boundary.
- Project-specific deployment, service-level, backup, and recovery requirements remain undefined because Reporivet is currently a local CLI/package rather than a documented deployed service.

### Sources

- [`product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md`](product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md)
- [`design-docs/DESIGN-REPORIVET-004-one-shot-setup.md`](design-docs/DESIGN-REPORIVET-004-one-shot-setup.md)
- [`decisions/ADR-0002-one-shot-bootstrapper-boundary.md`](decisions/ADR-0002-one-shot-bootstrapper-boundary.md)
- [`PLANS.md`](PLANS.md)
- [`product-specs/SPEC-REPORIVET-003-document-first-harness.md`](product-specs/SPEC-REPORIVET-003-document-first-harness.md) (historical)
- [`design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](design-docs/DESIGN-REPORIVET-003-document-first-harness.md) (historical)
- [`../pyproject.toml`](../pyproject.toml)
