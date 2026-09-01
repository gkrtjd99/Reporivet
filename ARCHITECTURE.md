---
owner: architecture
status: active
last_reviewed: 2026-08-31
---

# Architecture

## Current system map

Reporivet has two ownership domains:

1. **Installed-package behavior** performs deterministic scan, integrated guided setup, lower-level definition, diagnosis, upgrade checks, and explicit migration.
2. **Durable repository content** carries project authority through Markdown documents, ordinary Plans, optional instruction-only host/procedure Skills, and project-owned execution.

The default onboarding entry point is `reporivet setup`. `reporivet init` is structure-only and `reporivet define` remains the lower-level resumable definition interface. Setup may render an instruction-only project Skill only from a complete, user-confirmed structured procedure record while resuming the visible definition; it never creates a Plan or a target runtime.

The package is a temporary maintainer, not a copied executor. A target remains understandable and operable through its own documents and tools after Reporivet is removed.

```text
agent host
    -> AGENTS.md
    -> docs/README.md
    -> one matching active Plan
    -> task-relevant current authority
    -> project-owned commands and evidence

installed reporivet package
    -> validate root and paths
    -> scan or collect guided answers
    -> render exact preview
    -> apply approved document/adaptor changes
    -> diagnose or migrate when explicitly requested
```

## Package modules

| Module | Responsibility | Boundary |
| --- | --- | --- |
| [`src/reporivet/cli.py`](src/reporivet/cli.py) | Parse `setup`, `define`, `audit`, `init`, `upgrade`, `migrate`, and `doctor`; validate command combinations; dispatch package operations. | It exposes package commands only, never spawns Agents, executes project commands, or defines target-project checks. |
| [`src/reporivet/initializer.py`](src/reporivet/initializer.py) | Validate repository roots, perform safe path traversal, read package assets, run deterministic audit, and create missing entry points. | It rejects unsafe targets and preserves existing project-owned content. |
| `src/reporivet/procedures.py` | Validate complete user-confirmed structured procedures, serialize their canonical records, and render deterministic instruction-only project Skill content and paths. | It never renders Skills from incomplete, inferred, generic, Proposed, Open, or Sources-only records and never executes a procedure. |
| [`src/reporivet/guided.py`](src/reporivet/guided.py) | Manage guided definition, evidence-separated Markdown drafts, document-first rendering, transactional setup, diagnosis, and compact Plan structure checks. | It never promotes scanner inference to confirmed project truth or creates a Plan. |
| `src/reporivet/setup.py` | Coordinate the default integrated setup envelope across audit, visible guided definition, exact preview/apply, and procedure Skill targets. | It is package-side coordination only; it does not create Plans, spawn Agents, execute project commands, or maintain runtime state. |
| [`src/reporivet/migration.py`](src/reporivet/migration.py) | Preview, apply, restore after failure, and explicitly roll back the recognized 0.2 migration with an external backup and fingerprints. | It mutates only an approved, revalidated transaction and refuses unsafe rollback. |
| [`src/reporivet/assets/project/document-first/`](src/reporivet/assets/project/document-first/) | Store package-owned templates for current documents, compact Plans, metadata, and optional adapters. | Assets are inputs to setup; generated substantive content becomes project-owned. |

`src/reporivet/__main__.py` and the `reporivet` console entry point both delegate to the same CLI `main` function. Package version metadata lives in `src/reporivet/__init__.py`.

## Durable repository structure

```text
AGENTS.md                         canonical host-neutral entry point
CLAUDE.md                         optional thin host adapter
ARCHITECTURE.md                   current structure and ownership
.reporivet-version                package format marker
.claude/skills/...                optional instruction-only role adapters
.claude/settings.json             optional approved deny-only settings

docs/
  README.md                       knowledge and generated-surface map
  PRODUCT.md                      current product boundary
  DESIGN.md                       current design principles
  QUALITY.md                      project-owned checks and evidence policy
  OPERATIONS.md                   current operational authority
  SECURITY.md                     security boundary and reporting
  PLANS.md                        compact Plan lifecycle
  product-specs/                  versioned requirements
  design-docs/                    durable designs
  decisions/                      decision history
  exec-plans/
    _template.md                  compact format: 2 contract
    active/                       current substantive work
    completed/                    terminal historical outcomes
    tech-debt-tracker.md          bounded out-of-scope discoveries
  references/                     durable protocols and explanatory notes
  runbooks/                       optional procedure-specific operations
```

The complete per-path ownership and removal map is in [`docs/README.md`](docs/README.md).

## Ownership and dependency direction

- `procedures.py <- guided.py <- setup.py <- cli.py` is the frozen productization dependency direction: CLI calls setup, setup coordinates guided definition, and guided uses procedure validation/rendering.
- `cli.py` depends on initializer, guided, migration, and the integrated setup service.
- Guided setup and migration reuse root/path safety rather than bypassing it.
- Package behavior may render assets; assets and generated documents do not import package code.
- Host adapters import or point to `AGENTS.md`; canonical documents never depend on a host adapter.
- Plans refer to project-owned commands; project execution does not depend on Plan parsing.
- Current summaries point to versioned specifications, designs, and decisions; historical records do not mutate to follow current implementation.

Stable safety and distribution boundaries are encoded in the existing tests under [`tests/`](tests/).

## State and mutation model

- Audit and doctor are read-only.
- Guided answers and deterministic observations first produce a visible Markdown draft.
- Integrated `setup` is the default onboarding path; lower-level `define` remains available, while structure-only `init` only creates missing bundle structure.
- Setup and migration show exact filesystem changes before approval.
- Setup creates missing managed assets while preserving existing paths and may create only complete user-confirmed procedure Skills; it never creates a Plan or executes project commands.
- Migration fingerprints recognized inputs, writes a restricted external backup and manifest, revalidates immediately before mutation, and restores on failed apply when safe.
- Post-success rollback compares the current target with the applied result and stops rather than overwrite later user changes.
- Plans are ordinary Markdown. Main Skill searches history, resumes one matching active Plan, or creates the first unused current-year Plan from the template; Main serializes edits, assigns Task Packets, records evidence, and manually moves terminal Plans.

No secondary task state, hidden completion record, Agent spawn/dispatch runtime, command runner, CI/deployment engine, Gate, or evidence archive is required or installed.

## Dogfood repository exceptions

This repository retains `dev/harness.toml` as inactive project-owned legacy configuration; it is not an execution authority and is not produced for new document-first targets. Retained `.harness/runs` is retired historical sensitive state. Current code does not read its contents. Current code does not write it. Current code does not delete it.

These retained paths are preservation cases, not architectural dependencies.

## Runtime, data, and external systems

[`docs/QUALITY.md`](docs/QUALITY.md) owns source and package checks. [`docs/OPERATIONS.md`](docs/OPERATIONS.md) owns running, releasing, observing, backup, rollback, recovery, and incidents. Project-owned CI may call those same underlying commands, but checked-in workflow files are not generated or governed by Reporivet.

### Confirmed

- Python 3.11 or newer and the standard library are sufficient for production package code.
- Package modules and assets are under `src/reporivet/`; generated repository authority is outside package imports.
- Fresh integrated setup creates neither project command wrappers nor hidden run-state storage, and structure-only `init` remains available.
- Generated Markdown, Plans, Skills, Git, and project commands remain useful after uninstall.
- Source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive.

### Proposed

- None.

### Open

- Publication, signing, release, deployment, project-owned CI, and durable evidence archival remain unestablished or outside this repository's authority.
- No deployed service topology is currently defined; CI and deployment remain project-owned and outside Reporivet.

### Sources

- [`docs/product-specs/SPEC-REPORIVET-003-document-first-harness.md`](docs/product-specs/SPEC-REPORIVET-003-document-first-harness.md)
- [`docs/design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](docs/design-docs/DESIGN-REPORIVET-003-document-first-harness.md)
- [`docs/decisions/ADR-0001-document-first-product-boundary.md`](docs/decisions/ADR-0001-document-first-product-boundary.md)
- [`pyproject.toml`](pyproject.toml)
