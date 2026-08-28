---
id: PRODUCT
kind: product
status: active
area: product
summary: Current users, capabilities, requirements, and non-goals of Project Harness
applies_to:
  - "src/**"
  - "tests/**"
---

# Product

## Purpose

Project Harness initializes and safely maintains a repository-local, document-first operating environment for coding agents. The resulting project can be understood, changed, verified, and cleaned up from version-controlled repository artifacts without a custom plugin, Skill, task database, or long-running orchestrator.

## Users and jobs

- A developer adopting agent-assisted development needs a trustworthy initial repository structure rather than a growing prompt file.
- A Main Agent needs a small entry map, explicit sources of truth, restartable plans, deterministic commands, and evidence-bound completion.
- A Sub Agent needs one bounded Task Packet with exact read/write scope, acceptance, verification, and stop conditions.
- A maintainer needs safe re-runs and upgrades that do not overwrite project-owned knowledge.

## Current capabilities

- Initialize a new or existing project through `project-harness init`.
- Detect common project languages, runtimes, package managers, tests, and draft commands without treating inference as verified truth.
- Generate a short `AGENTS.md`, current-state documents, durable document templates, ExecPlan templates, technical-debt tracking, and repository-local command entry points.
- Generate an existing-project baseline plan and block false-green verification until inferred commands are reviewed.
- Maintain project-owned versus harness-owned file boundaries across reinitialization and `upgrade`.
- Validate document metadata, catalogs, links, plan lifecycle, Task Packets, configured executables, and integrated Git commits.
- Report long-term maintenance candidates through `garden` without automatic deletion.
- Optionally generate GitHub Actions for verification and scheduled garden reporting.
- Diagnose an initialized project through `project-harness doctor`.

## Requirements and invariants

- **REQ-OWN-1:** Project-owned documents and `dev/harness.toml` are never overwritten after creation.
- **REQ-MAN-1:** Upgradable files and blocks carry explicit managed markers.
- **REQ-CMD-1:** Completion commands are committed as argument arrays and are never silently omitted because a local tool is missing.
- **REQ-PLAN-1:** Complex work remains restartable from one ExecPlan and the repository, without chat history.
- **REQ-AGENT-1:** Main owns scope, integration, document lifecycle, verification target, and completion; Sub work remains bounded.
- **REQ-GIT-1:** A plan can close only against a clean, explicitly declared Git `HEAD` that passes the canonical gate.
- **REQ-PORT-1:** The generated runtime has no dependency on the initializer package after generation.
- **REQ-SAFE-1:** Initialization refuses to replace an existing unmarked canonical command path.

## Non-goals

- Scheduling or supervising autonomous agents.
- Coordinating several Main Agents against one goal.
- Providing leases, journals, replay, budgets, or durable runtime task state.
- Automatically deciding semantic architecture quality or deleting documentation.
- Creating, reviewing, or merging GitHub pull requests.
- Installing host-wide LLM plugins or Skills.

## Open questions

- Native Windows wrapper generation is not implemented.
- Additional project profiles should be added only when real repositories demonstrate repeated needs that cannot be expressed in `dev/harness.toml`.
