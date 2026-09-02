---
owner: architecture
status: active
last_reviewed: 2026-09-02
---

# Architecture

## Current system map

Reporivet has two deliberately separate ownership domains:

1. **Installed-package behavior** performs deterministic inventory, visible guided definition, one-shot setup preview/apply, and explicit legacy transition transactions while the user invokes those operations.
2. **Durable target content** carries project authority through Markdown documents, ordinary Plans, static runbooks, an optional exact host adapter, Git, and project-owned execution.

The default onboarding entry point is `reporivet setup`. `reporivet init` is structure-only and `reporivet define` remains the lower-level resumable definition interface. Setup is a bounded one-shot package-side transaction: it may inspect and prepare another repository while invoked, then hands ownership to that repository. It never creates a Plan, spawns or dispatches Agents, executes project commands, or installs a target runtime. Package removal after setup does not reduce ordinary target work.

```text
host/project workflow
    -> AGENTS.md
    -> docs/README.md
    -> one matching active Markdown Plan
    -> task-relevant current authority
    -> project-owned commands and evidence

installed Reporivet package (setup time only)
    -> validate root and paths
    -> audit or collect guided answers
    -> render exact document/runbook preview
    -> apply the approved bounded transaction
    -> hand off an independent target
```

The optional external user-scoped `/reporivet-setup` wrapper is outside target assets. It only relays the deterministic package-side preview/apply flow, never installs or resolves Reporivet, and never edits target files itself.

## Package modules

| Module | Responsibility | Boundary |
| --- | --- | --- |
| [`src/reporivet/cli.py`](src/reporivet/cli.py) | Parse `setup`, `define`, `audit`, `init`, `upgrade`, and `migrate`; validate command combinations; dispatch package-side operations. | It exposes package commands only, never spawns Agents, executes project commands, or defines a target runtime. |
| [`src/reporivet/initializer.py`](src/reporivet/initializer.py) | Validate repository roots, perform safe path traversal, read package assets, run deterministic audit, and create missing entry points. | It rejects unsafe targets and preserves existing project-owned content. |
| [`src/reporivet/procedures.py`](src/reporivet/procedures.py) | Validate complete user-confirmed strict procedure records, serialize their canonical records, and render deterministic static runbooks. | It renders only ordinary Markdown runbooks; it never renders target Skills, executes a procedure, or infers missing fields. |
| [`src/reporivet/guided.py`](src/reporivet/guided.py) | Manage visible guided definition, evidence-separated drafts, exact setup previews, transaction checks, and compact Plan structure checks. | It never promotes scanner inference to confirmed project truth, creates a Plan, or provides ongoing target diagnosis. |
| [`src/reporivet/setup.py`](src/reporivet/setup.py) | Coordinate the bounded one-shot setup envelope across audit, visible guided definition, exact preview/apply, and transition cleanup when explicitly approved. | It is package-side coordination only; it does not create Plans, spawn Agents, execute project commands, or maintain target runtime state. |
| [`src/reporivet/migration.py`](src/reporivet/migration.py) | Preview, apply, restore after failure, and explicitly roll back recognized legacy transactions with an external backup and fingerprints. | It mutates only an approved, revalidated transaction and refuses unsafe rollback. |
| [`src/reporivet/assets/project/document-first/`](src/reporivet/assets/project/document-first/) | Store package-owned templates for current documents, compact Plans, static runbooks, metadata, and the optional exact adapter. | Assets are setup inputs; generated substantive content becomes project-owned and contains no package import. |

`src/reporivet/__main__.py` and the `reporivet` console entry point both delegate to the same CLI `main` function. Package version metadata lives in `src/reporivet/__init__.py`; no package version marker is generated in a target.

## Durable generated repository structure

```text
AGENTS.md                         canonical host-neutral entry point
CLAUDE.md                         optional exact host adapter
ARCHITECTURE.md                   current structure, ownership, and dependency direction

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
  decisions/                     decision history
  exec-plans/
    _template.md                 compact `format: 2` contract
    active/                      current substantive work
    completed/                   terminal historical outcomes
    tech-debt-tracker.md         bounded out-of-scope discoveries
  references/                    durable protocols and explanatory notes
  runbooks/
    index.md                     static runbook catalog
    _template.md                 manual runbook template
    <slug>.md                    ordinary Markdown for eligible procedures
```

A fresh target contains no Reporivet role or procedure Skill, `.reporivet-version`, generated `.claude/settings.json`, copied module/runtime, doctor gate, registry or package-resolution instruction, command wrapper, or hidden state. When selected, `CLAUDE.md` is exactly `@AGENTS.md\n`. Existing legacy paths are transition candidates only during an explicit setup rerun and only after exact canonical ownership evidence; names, markers, frontmatter, or locations alone never authorize deletion.

Only a complete, unique, user-confirmed strict nine-field procedure record qualifies for a static runbook. The exact fields are `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, and `rollback`. The rendered `docs/runbooks/<slug>.md` is ordinary Markdown with no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration. Incomplete, malformed, generic, inferred, Proposed, Open, Sources-only, or duplicate records render no runbook.

## Ownership and dependency direction

- `procedures.py <- guided.py <- setup.py <- cli.py` is the package-side dependency direction: CLI calls setup, setup coordinates visible definition, and guided uses pure procedure validation/rendering.
- `cli.py` depends on initializer, guided, migration, and the integrated setup service.
- Guided setup and transition code reuse root/path safety rather than bypassing it.
- Package behavior may render assets; assets and generated documents do not import package code.
- The optional host adapter points to `AGENTS.md`; canonical documents never depend on a host adapter.
- Plans refer to project-owned commands; project execution does not depend on package parsing.
- Current summaries point to versioned specifications, designs, and decisions; historical records do not mutate to follow current implementation.

Stable safety and distribution boundaries are encoded in the existing tests under [`tests/`](tests/).

## State and mutation model

- Audit and setup preview are read-only with respect to target content.
- Guided answers and deterministic observations first produce a visible Markdown draft.
- Integrated setup is the default onboarding path; lower-level `define` remains available, while structure-only `init` only creates missing bundle structure.
- Setup shows exact filesystem actions before approval, binds destructive actions to that preview, and revalidates the target immediately before mutation.
- Setup creates missing documents and static runbooks only where ownership permits; it never creates a Plan, executes project commands, dispatches Agents, or installs a target runtime.
- An explicit setup rerun may remove or convert only exact canonical legacy artifacts after an external backup; modified, ambiguous, unsafe, symlinked, nonregular, and project-owned paths are preserved or refused.
- A failed transaction restores the approved preimage when safe. Later rollback compares the successful postimage and refuses to overwrite user changes.
- Plans are ordinary Markdown. Main searches history, resumes one matching active Plan, or creates the first unused current-year Plan from the template; Main serializes edits and manually moves terminal Plans.

There is no current `doctor` command or ongoing diagnosis contract. No secondary task state, hidden completion record, Agent spawn/dispatch runtime, command runner, CI/deployment engine, Gate, or evidence archive is required or installed.

## Dogfood repository exceptions

This repository retains `dev/harness.toml` as inactive project-owned legacy configuration; it is not an execution authority and is not produced for new targets. Retained `.harness/runs` is retired historical sensitive state. Current code does not read its contents. Current code does not write it. Current code does not delete it.

These retained paths are preservation cases, not architectural dependencies.

## Runtime, data, and external systems

[`docs/QUALITY.md`](docs/QUALITY.md) owns source and package checks. [`docs/OPERATIONS.md`](docs/OPERATIONS.md) owns running, releasing, observing, backup, rollback, recovery, and incidents. Project-owned CI may call those same underlying commands, but checked-in workflow files are not generated or governed by Reporivet. Generated targets own their commands, tests, CI, deployment, operations, secrets, and acceptance evidence.

### Confirmed

- Python 3.11 or newer and the standard library are sufficient for production package code.
- Package modules and assets are under `src/reporivet/`; generated repository authority is outside package imports.
- Fresh integrated setup creates neither project command wrappers nor hidden run-state storage, and structure-only `init` remains available.
- Fresh targets contain Markdown, Plans, static runbooks, and at most the exact optional adapter; those surfaces remain useful after package removal.
- Package absence after approved setup is expected and is not an unknown, blocker, or residual risk for ordinary target work.
- Source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive; this historical package lifecycle does not establish a continuing target dependency.

### Proposed

- None.

### Open

- Publication, signing, release, deployment, project-owned CI, and durable evidence archival remain unestablished or outside Reporivet's authority.
- No deployed service topology is currently defined; CI and deployment remain project-owned and outside Reporivet.

### Sources

- [`docs/decisions/ADR-0002-one-shot-bootstrapper-boundary.md`](docs/decisions/ADR-0002-one-shot-bootstrapper-boundary.md)
- [`docs/product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md`](docs/product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md)
- [`docs/design-docs/DESIGN-REPORIVET-004-one-shot-setup.md`](docs/design-docs/DESIGN-REPORIVET-004-one-shot-setup.md)
- [`docs/PLANS.md`](docs/PLANS.md)
- [`docs/decisions/ADR-0001-document-first-product-boundary.md`](docs/decisions/ADR-0001-document-first-product-boundary.md) (historical)
- [`pyproject.toml`](pyproject.toml)
