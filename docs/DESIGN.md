---
id: DESIGN
kind: design
status: active
area: repository
summary: Current interaction, ownership, knowledge, and verification conventions for Reporivet
applies_to:
  - "src/**"
  - "tests/**"
  - "docs/**"
---

# Design

## Design intent

The repository, not a hidden conversation or external control plane, is the operating system for agent work. Durable facts needed to define, resume, constrain, verify, or maintain work are discoverable through a short entry map and version-controlled artifacts.

## Interaction conventions

- CLI commands use explicit subcommands, visible exit codes, and actionable errors.
- `--dry-run` does not create or modify a target path.
- Definition starts only when explicitly requested; initialization and upgrade do not invent product work.
- Audit is deterministic and read-only. Adoption audits before writing and fails closed on authority conflicts.
- Commands compute progress and validate structure; human or Main supplies semantic answers and resolves conflicts.
- Potentially destructive ambiguity, unsafe paths, malformed evidence, and target mismatch fail closed rather than guessing.
- Generated entry points use stable names under `dev/` so agents do not invent project commands.

## Ownership conventions

- The installed initializer and copied repository runtime are separate lifetimes.
- Project-owned files are created only when absent. This includes current-state knowledge, product definitions, plans, and `dev/harness.toml`.
- Harness-owned files have `reporivet:managed` in their first lines and are rendered from canonical package assets.
- Shared files use bounded paired markers; malformed or fenced lookalike markers do not grant ownership.
- Upgrade refreshes only marked files and blocks. Existing configuration without `[gate]` remains byte-identical while conservative defaults apply in memory.
- Unmarked canonical path collisions, symlink traversal, and nonregular inputs are errors.

## Knowledge conventions

- `AGENTS.md` remains a compact routing contract.
- Current-state documents describe implemented reality and verified intent.
- Confirmed, Proposed, Open, and Sources evidence remain distinct throughout definition. Only confirmed declarations satisfy traceability.
- Stable `JRN-*`, `REQ-P0-*`, and `AC-*` identifiers connect product intent to plans, tasks, and criterion evidence when traceability is enabled.
- Module contracts exist only for justified durable boundaries. `docs/generated/code-map.md` is derived and non-authoritative.
- Active ExecPlans are living execution state; completed plans and accepted decisions are history.
- Structured Verification Run artifacts are inspectable evidence. Raw command logs remain ignored and disposable.

## Main and Sub conventions

- Main defines intent, acceptance, non-goals, allowed writes, protected paths, integration order, verification target, and completion.
- Sub Agents receive one bounded Task Packet and cannot broaden scope, delegate again, change acceptance, or approve their own work.
- Read-heavy work may be parallelized; mutable work is sequential unless paths, interfaces, and worktrees are isolated.
- Implementation explanation is not verification evidence. REVIEW acceptance remains human-owned.

## Implementation conventions

- Use the Python standard library unless a production dependency materially reduces total lifecycle complexity and is explicitly approved.
- Execute configured commands as argument arrays without shell interpolation.
- Keep command detection separate from command approval.
- Prefer narrow parsers, fixed data structures, and deterministic schemas over a registry, plugin system, policy DSL, or compatibility framework.
- Add a mechanical rule only when it is objective, stable, and produces an actionable repair path.
- Preserve explicit local evidence rather than inferring Git parents, remotes, or network state.

## Verification and Gate

One `./dev/verify` invocation owns one shared run and fixed check order. Checks record `pass`, `fail`, `error`, `skipped`, or `unknown`; required failure takes precedence over required infrastructure error. Manifest, Gate, report, per-check JSON, and available logs survive non-green outcomes.

Gate classifies explicit changed paths as `contained`, `wide`, `irreversible`, or `unknown` and returns:

1. `BLOCK` for a required check failure.
2. `INCONCLUSIVE` for required error/unknown, malformed policy, or target mismatch/error.
3. `REVIEW` for protected, unknown, wide, irreversible, or policy-required dirty conditions.
4. `PASS` only for a clean, confirmed, contained target with every required check passing.

Shadow mode allows deterministic `PASS` and `REVIEW` to return success while preserving the verdict. Enforce mode allows only `PASS`. Neither mode can override `BLOCK` or `INCONCLUSIVE`. `close-plan` reuses this canonical implementation once and transactionally binds closure evidence to one clean commit.

Detailed trade-offs are recorded in [`DESIGN-REPORIVET-002`](design-docs/DESIGN-REPORIVET-002-project-definition-adoption-and-evidence-gate.md).

## Accessibility and internationalization

The CLI emits plain UTF-8 text and accepts Unicode project names, summaries, areas, plan titles, and safe REVIEW reasons. Generated operational documents use stable English headings for predictable parsing; project content may use any UTF-8 language.

## Non-goals

- External backup, archive, deletion, deprecation writes, package publication, or repository mutation.
- Host-specific Skill/runtime target bundles, model-backed judges, plugins, daemons, or external orchestration state.
- A second completion gate, confidence score, semantic interviewer, or automatic human-approval substitute.
- Speculative abstractions or broad compatibility layers beyond current requirements.
