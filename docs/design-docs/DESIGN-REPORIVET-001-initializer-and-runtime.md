---
id: DESIGN-REPORIVET-001
kind: design-doc
status: active
area: harness
summary: Separation between the one-time initializer and independent repository-local runtime
applies_to:
  - "src/reporivet/initializer.py"
  - "src/reporivet/assets/project/dev/harness.py"
  - "src/reporivet/assets/project/root/**"
  - "src/reporivet/assets/project/docs/**"
supersedes: []
---

# Initializer and repository-local runtime

## Context

A target repository needs durable operating rules after the initializer is gone. Requiring an installed package, host plugin, or external state service during ordinary development would make the repository less portable and less legible to a fresh agent.

## Current design

The system is split into two lifetimes.

### Initializer lifetime

The installed `reporivet` package inspects the target, renders packaged assets, establishes ownership boundaries, creates a baseline plan for existing code, and can later refresh only explicitly managed artifacts.

### Repository lifetime

The target's copied `dev/harness.py`, shell wrappers, Markdown, TOML, Git history, and optional CI operate independently. They use only the Python standard library plus the project's configured tools.

## Invariants and boundaries

- The target runtime never imports `reporivet`.
- Project intent and current-state knowledge remain project-owned.
- A tool update cannot require rewriting historical plans or decisions.
- Command inference never equals approval for an existing codebase.
- Verification operates on one repository root and one committed command configuration.
- Repository hygiene uses a managed ignore block for prevention and a tracked-file scanner for force-add or pre-existing mistakes.
- Initializer rendering is scoped per artifact so future repository-local tokens are not consumed during installation.
- Main/Sub policies are represented in `AGENTS.md` and Task Packets, not a hidden scheduler.

## Alternatives considered

- A global Skill or plugin was rejected because it creates host-specific installation and upgrade state.
- A task database was rejected because one ExecPlan is sufficient durable state for the intended single-Main operating model.
- Runtime stack auto-detection was rejected because environment-dependent probing can silently change verification between machines.
- Overwriting whole managed documents was rejected because it destroys project knowledge after initialization.

## Verification

Regression tests initialize temporary repositories, execute their copied runtime, mutate project-owned files, re-run and upgrade the initializer, and close plans against real Git commits.
