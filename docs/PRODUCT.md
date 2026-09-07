---
id: PRODUCT
kind: product
status: active
area: product
summary: Current users, capabilities, requirements, and non-goals of Reporivet
applies_to:
  - "src/**"
  - "tests/**"
---

# Product

## Purpose

Reporivet initializes and safely maintains a repository-local, document-first operating environment for coding agents. It supports explicit project definition, read-only inventory and adoption, restartable implementation, and evidence-bound completion. A generated project remains understandable and operable from version-controlled repository artifacts after the installed package is removed.

## Users and jobs

- A developer starting a project needs a structured definition that separates confirmed facts, proposals, open questions, and sources.
- A maintainer adopting existing code needs a deterministic audit and additive installation that preserves repository authority.
- A Main Agent needs a small entry map, explicit sources of truth, one living ExecPlan, bounded Task Packets, traceability, and evidence-bound completion.
- A Sub Agent needs exact read/write scope, acceptance IDs, verification commands, and stop conditions.
- A release or verification maintainer needs one canonical run, inspectable artifacts, an explicit Git target, conservative risk judgment, and package-removal evidence.

## Current capabilities

- Initialize a new or existing project through `reporivet init` without overwriting project-owned authority.
- Start or resume a fourteen-section project definition with `reporivet define`, persisted progress, stable `JRN-*`, `REQ-P0-*`, and `AC-*` identifiers, and separate Confirmed, Proposed, Open, and Sources evidence.
- Validate and transactionally finalize confirmed definition evidence into one product specification and one first-slice ExecPlan.
- Inventory an existing repository deterministically through `reporivet audit` or `./dev/audit` without writes or project-command execution.
- Adopt through `reporivet define --adopt`, preserving README, instructions, architecture, CI, configuration, and other authority while keeping inferred commands in review.
- Generate a short `AGENTS.md`, current-state documents, durable templates, one-plan Task Packets, technical-debt tracking, and repository-local command entry points.
- Validate opt-in product-to-plan-to-task-to-evidence traceability while leaving historical non-opt-in plans unchanged.
- Create module contracts only for justified boundaries, generate a non-authoritative actual-path code map, and route context by path, area, or plan.
- Run exactly one shared Verification Run per `./dev/verify`, preserving check JSON, logs, `manifest.json`, `gate.json`, and `report.md` on success, candidate failure, or infrastructure error.
- Evaluate explicit local target evidence and changed paths under conservative Gate policy with `PASS`, `REVIEW`, `BLOCK`, and `INCONCLUSIVE` verdicts in shadow or enforce mode.
- Close a plan only against one clean verified commit and persist the run ID, manifest SHA-256, verdict, verified SHA, criterion evidence, and any genuine human REVIEW reason.
- Generate CI that verifies an explicit head/base target once and uploads `.harness/runs/` on success or failure.
- Diagnose ownership and configuration through `reporivet doctor`, and report maintenance candidates through `garden` without automatic deletion.
- Preserve repository-local definition, audit, context, planning, checks, verification, closure, and gardening after uninstalling Reporivet.
- Block common secret, personal, raw-log, cache, infrastructure-state, and build-output files and reject force-added tracked sensitive material.

Detailed journey, P0 requirement, and acceptance authority for definition, adoption, traceability, evidence, Gate, and migration is [`SPEC-REPORIVET-002`](product-specs/SPEC-REPORIVET-002-project-definition-adoption-and-evidence-gate.md).

## Requirements and invariants

- **REQ-OWN-1:** Project-owned documents and `dev/harness.toml` are created only when absent and are never overwritten by upgrade.
- **REQ-MAN-1:** Upgradable files and shared blocks carry explicit managed ownership markers.
- **REQ-DEF-1:** Commands validate persisted definition structure; they do not invent semantic product answers or promote proposals to facts.
- **REQ-AUD-1:** Audit is deterministic, read-only, path-safe, and does not execute project commands.
- **REQ-CMD-1:** Configured completion commands are argument arrays and missing tools fail visibly rather than disappearing.
- **REQ-PLAN-1:** Complex work remains restartable from one ExecPlan and the repository without chat history or another task system.
- **REQ-TRACE-1:** Confirmed opt-in traceability must connect product journeys and P0 requirements to criteria, tasks, evidence, and the verified commit.
- **REQ-AGENT-1:** Main owns scope, integration, document lifecycle, verification target, and completion; Sub work remains bounded.
- **REQ-VERIFY-1:** `./dev/verify` is the only completion gate and produces one shared run with deterministic check and Gate artifacts.
- **REQ-GIT-1:** Gate and closure use only explicit local base/head/target evidence; they never infer a parent, assume a remote, or fetch.
- **REQ-CLOSE-1:** Missing or mismatched evidence cannot produce PASS, and BLOCK or INCONCLUSIVE cannot be overridden.
- **REQ-PORT-1:** The copied generated runtime has no dependency on the initializer package after generation.
- **REQ-SAFE-1:** Initialization and adoption refuse symlinked, nonregular, or unmarked canonical command collisions before writes.
- **REQ-SAFE-2:** Ignore and tracked-file controls protect local secrets and artifacts while preserving source, examples, migrations, and lockfiles.

## CLI interaction and internationalization

CLI commands use explicit subcommands, visible exit codes, and actionable errors. `--dry-run` does not create or modify a target path. Definition starts only when explicitly requested; initialization and upgrade do not invent product work. Audit is deterministic and read-only, and adoption audits before writing and fails closed on authority conflicts. Commands compute progress and validate structure; a human or Main supplies semantic answers and resolves conflicts. Generated entry points use stable names under `dev/` so agents do not invent project commands.

The CLI emits plain UTF-8 text and accepts Unicode project names, summaries, areas, plan titles, and safe REVIEW reasons. Generated operational documents use stable English headings for predictable parsing; project content may use any UTF-8 language.

## Non-goals

- Running or supervising autonomous agents, model judges, or an LLM evaluation service.
- Providing a task database, lease service, scheduler, daemon, journal, replay engine, plugin, MCP bridge, or external control plane.
- Generating host-specific Skill/runtime target bundles or maintaining duplicate completion gates.
- Automatically deciding semantic product quality, resolving requirement conflicts, or manufacturing REVIEW acceptance through a confidence score, semantic interviewer, or automatic human-approval substitute.
- Creating, reviewing, merging, or publishing GitHub changes or packages.
- Backing up, archiving, deprecating through an external write, deleting, or otherwise operating the former repository.
- Rewriting historical completed plans or project-owned authority to retrofit new behavior.

## Open questions

- Native Windows wrapper generation is not implemented.
- Additional project profiles should be added only when repeated repository evidence cannot be expressed in `dev/harness.toml`.
