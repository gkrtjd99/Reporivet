---
id: PLAN-0000
kind: exec-plan
status: complete
owner: main
area: repository
created: 2026-08-28
updated: 2026-08-28
base_commit: "45305d09a4f57b8e7e8f90a6362ff667497604a2"
integrated_commit: 660575e3a955220e8af32096e2775db79b6e03af
verified_commit: 660575e3a955220e8af32096e2775db79b6e03af
---

# Establish repository baseline

## Purpose / Big Picture

Establish a trustworthy, dogfooded operating baseline for Project Harness. A fresh Main Agent can start from `AGENTS.md`, route through `./dev/context` and `docs/README.md`, understand the initializer and independent generated runtime, resume complex work from one self-contained ExecPlan, and judge completion with one repository-local verification command.

## Progress

- [x] Establish current behavior and constraints.
- [x] Deliver the smallest working milestone.
- [x] Integrate and independently verify the candidate.
- [x] Resolve documentation impact and follow-ups.

## Context and Orientation

The installable package entry point is `src/project_harness/cli.py`. Safe target inspection, command inference, ownership handling, rendering, initialization, upgrade, and doctor behavior live in `src/project_harness/initializer.py`. Files copied into target repositories live under `src/project_harness/assets/project/`. The target's independent runtime is `src/project_harness/assets/project/dev/harness.py`. End-to-end behavior is owned by `tests/test_project_harness.py`.

This repository now uses the same generated `AGENTS.md`, current-state documents, durable-document catalogs, `docs/exec-plans/` lifecycle, command wrappers, strict checks, and garden report that it emits for target projects. `dev/harness.toml` is the committed command source of truth for this repository.

## Scope

- Establish product, architecture, design, quality, and security documents from implemented source and tests.
- Record the generated target contract and initializer/runtime lifetime split as durable documents.
- Establish deterministic repository checks and CI entry points.
- Preserve project-owned files while upgrading only explicit managed code and blocks.
- Preserve future ExecPlan tokens until `./dev/new-plan` creates a plan.
- Verify source, packaged assets, an installed wheel, and a generated target repository.
- Bind baseline completion to one clean Git commit.

## Non-goals

- Add a remote scheduler, task database, lease system, plugin, Skill, or long-running agent controller.
- Add Windows-native command wrappers.
- Publish or administer a GitHub repository from the package runtime.
- Treat inferred project commands as approved commands.
- Generalize the limited frontmatter reader into an arbitrary YAML implementation.

## Acceptance Criteria

- **AC-1:** `AGENTS.md` is a compact routing contract and every stable entry document it names exists.
- **AC-2:** Current-state and durable documents describe implemented behavior, have valid metadata, and appear in generated catalogs.
- **AC-3:** Initialization and upgrade preserve project-owned content and refuse ambiguous command-path replacement.
- **AC-4:** Future ExecPlan placeholders survive initialization and resolve only when a new plan is created.
- **AC-5:** `./dev/verify` succeeds through deterministic document, plan, architecture, and regression gates.
- **AC-6:** The built wheel contains all packaged assets, contains no bytecode cache, installs in isolation, and generates a target whose `verify` and `doctor` commands succeed.
- **AC-7:** Plan closure verifies a clean integrated Git commit and records its actual SHA.

## Milestones

### M1 — Safe initializer and independent repository runtime

Deliver the installable CLI, ownership-safe initialization and upgrade, project-owned command configuration, managed repository-local runtime, deterministic checks, and regression coverage while keeping target repositories independent of the installed package.

### M2 — Dogfooded, verified repository baseline

Apply the generated harness to this repository, replace scaffold knowledge with implemented reality, connect CI to the canonical gate, verify the distribution in isolation, and archive this plan against the integrated commit.

## Task Packets

### T1 — Inspect implementation and establish sources of truth

#### State

complete

#### Depends on

none

#### Outcome

Identify actual package boundaries, ownership behavior, generated runtime behavior, command semantics, test coverage, distribution contents, external dependencies, and known limits from source and execution.

#### Non-goals

Feature expansion, speculative platform design, or rewriting implementation before a failing behavior is established.

#### Read

`pyproject.toml`, `README.md`, `src/project_harness/`, packaged assets, `tests/test_project_harness.py`, existing Git history, and the primary OpenAI harness and ExecPlan references recorded in `docs/references/openai-harness-engineering.md`.

#### Allowed writes

This plan's findings and the proposed documentation map.

#### Protected paths

Implementation and packaged templates during read-only exploration.

#### Acceptance

AC-1, AC-2, AC-3, AC-5, AC-6

#### Verify

Inspect source and tests, run the regression suite, build and inspect a wheel, install it into an isolated virtual environment, initialize a service target, and run the target's verification and doctor commands.

#### Stop conditions

A source claim conflicts with execution, an external runtime dependency appears, destructive behavior lacks a test, or the evidence cannot be reproduced.

#### Result

Completed. The package uses only the Python standard library at runtime; initializer and target runtime are separate lifetimes; project-owned versus managed ownership is explicit; regression and isolated-distribution evidence are reproducible; no task database, plugin, or scheduler is present.

### T2 — Establish the dogfooded repository harness

#### State

complete

#### Depends on

T1

#### Outcome

Create and fill the repository-local operating contract, current-state documents, durable specifications, reference map, deterministic commands, CI integration, and baseline plan.

#### Non-goals

Change the intended single-Main operating model, add a remote control plane, or introduce a production dependency.

#### Read

T1 evidence, generated templates, current source, tests, and the OpenAI-aligned design rules in `docs/design-docs/core-beliefs.md`.

#### Allowed writes

`AGENTS.md`, `ARCHITECTURE.md`, `README.md`, `.gitignore`, `.harness-version`, `.github/workflows/ci.yml`, `dev/**`, `docs/**`, initializer rendering logic, and regression tests required by discovered defects.

#### Protected paths

Public CLI semantics unrelated to baseline safety, unrelated feature expansion, and historical Git commits.

#### Acceptance

AC-1, AC-2, AC-3, AC-4, AC-5

#### Verify

Run `./dev/docs-index`, strict document and plan checks, architecture compilation, and the regression suite. Inspect diffs for project-owned file protection and token-rendering scope.

#### Stop conditions

A project-owned file would be overwritten, a current-state statement cannot be supported by source or tests, canonical commands differ between local use and CI, or runtime plan tokens are consumed during installation.

#### Result

Completed. The repository is self-hosted by the emitted harness. A rendering-scope defect that could consume future ExecPlan date tokens during initialization was fixed and covered by a regression test. Core documents are active, catalogs are generated, configuration is ready, and CI calls the same `./dev/bootstrap` and `./dev/verify` interfaces used locally.

### T3 — Independently verify and archive the baseline

#### State

complete

#### Depends on

T2

#### Outcome

Judge the integrated candidate against every acceptance criterion, reproduce repository and distribution evidence, and archive this plan with the actual verified SHA.

#### Non-goals

Redesign, unrelated cleanup, release publication, or accepting implementer narrative without command evidence.

#### Read

This plan, the complete changed tree, current-state documents, regression output, wheel inspection, isolated target output, Git status, and the candidate diff.

#### Allowed writes

Verifier evidence and the completed historical plan record.

#### Protected paths

Acceptance criteria and integrated implementation except for a separately assigned repair after a failed gate.

#### Acceptance

AC-1 through AC-7

#### Verify

Run `./dev/verify` from the committed clean candidate, inspect the wheel, repeat isolated installation and target verification, then run `./dev/close-plan PLAN-0000`.

#### Stop conditions

The worktree is dirty, `HEAD` differs from the declared integrated target, a strict gate fails, packaged assets are incomplete, bytecode enters the wheel, or evidence cannot be reproduced.

#### Result

Completed. `./dev/close-plan PLAN-0000` independently reran the canonical gate against clean commit `660575e3a955220e8af32096e2775db79b6e03af`, recorded that SHA as both integrated and verified, and moved this record to `completed/`. Twelve regression tests pass. The wheel contains thirty-nine files including twenty-nine packaged assets and zero bytecode files. An isolated installed CLI initializes a service target whose repository-local `verify` and initializer `doctor` commands succeed.

## Architecture Impact

The repository now dogfoods the same two-lifetime architecture it distributes: an installed initializer for setup and managed upgrades, followed by a copied repository-local runtime for normal development. Rendering values are scoped per artifact so tokens owned by future repository-local operations are not consumed by installation. No production dependency, external state service, or new cross-system edge was introduced.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| `AGENTS.md` | create | Provide the compact repository map and operating contract | Main | resolved |
| `ARCHITECTURE.md` | create | Record implemented package and runtime boundaries | Main | resolved |
| `docs/PRODUCT.md` | create | Record current users, capabilities, requirements, and non-goals | Main | resolved |
| `docs/DESIGN.md` | create | Record ownership, interaction, knowledge, and agent conventions | Main | resolved |
| `docs/QUALITY.md` | create | Record test, completion, and release evidence | Main | resolved |
| `docs/SECURITY.md` | create | Record filesystem and command trust boundaries | Main | resolved |
| `docs/product-specs/SPEC-HARNESS-001-generated-project.md` | create | Define observable generated-repository behavior | Main | resolved |
| `docs/design-docs/DESIGN-HARNESS-001-initializer-and-runtime.md` | create | Explain the initializer/runtime lifetime split and rendering scope | Main | resolved |
| `docs/references/openai-harness-engineering.md` | create | Map primary upstream design references | Main | resolved |
| Durable-document catalogs | generate | Route agents to long-lived knowledge | harness | resolved |

## Interfaces and Dependencies

- Existing project capabilities inspected: Python packaging, `unittest`, `venv`, `zipfile`, standard-library filesystem, subprocess, TOML support, Git, and GitHub Actions.
- New production dependency: none.
- Public or cross-repository contract impact: generated files and CLI behavior are documented and regression-tested; this baseline does not require a consumer migration.
- Internal compatibility approach: obsolete internal paths were removed rather than preserved as aliases; project-owned target files remain protected by ownership rules.

## Migration, Rollout, and Recovery

This is a repository-only baseline adoption. Generated files are versioned in Git. Recovery is a Git revert of the candidate or completion record. Project-owned documents remain ordinary text. Raw verification logs are ignored and disposable. The initializer's managed upgrade path does not require a data migration or compatibility window.

## Surprises and Discoveries

- 2026-08-28 — A verifying plan cannot contain its own final commit SHA in the same commit without self-reference. Symbolic `HEAD` is accepted only during verification and is replaced by the actual SHA during closure.
- 2026-08-28 — Catalog generation must still run when post-initialization validation is skipped; otherwise a new repository begins with known catalog drift.
- 2026-08-28 — Rendering all project metadata into every asset can consume tokens that belong to future repository-local operations. Rendering is now scoped per artifact.
- 2026-08-28 — Package-data globs can capture bytecode caches, so distribution verification explicitly rejects `__pycache__`, `.pyc`, and `.pyo` entries.
- 2026-08-28 — This package has no runtime or test dependency outside the standard library, so this repository's canonical bootstrap is an explicit no-op rather than a network-dependent editable install.

## Decision Log

- 2026-08-28 — Use OpenAI Harness Engineering as the primary design authority.
- 2026-08-28 — Keep `AGENTS.md` short and route durable detail into version-controlled documents.
- 2026-08-28 — Use one self-contained ExecPlan as durable complex-work state; do not add a Task DB or scheduler.
- 2026-08-28 — Separate project-owned documents from marked, upgradeable harness code and bounded managed blocks.
- 2026-08-28 — Require command review for every pre-existing implementation, even when detection succeeds.
- 2026-08-28 — Fail when configured evidence is unavailable instead of silently skipping it.
- 2026-08-28 — Dogfood the emitted repository runtime in the initializer repository itself.

## Concrete Steps

Run commands from the repository root.

1. `./dev/context --plan PLAN-0000`
2. `./dev/docs-index`
3. `./dev/docs-check --strict`
4. `./dev/plan-check --strict`
5. `./dev/architecture-check --strict`
6. `python3 -m unittest discover -s tests -v`
7. `python3 -m pip wheel . --no-build-isolation --no-deps --wheel-dir dist`
8. Inspect the wheel with `zipfile`, install it into an isolated `venv`, initialize a service target, and run the target's `./dev/verify` and initializer `doctor` commands.
9. Commit the verifying baseline candidate.
10. `./dev/close-plan PLAN-0000`
11. Commit the completed historical record separately.

## Validation and Evidence

- Integrated and verified target: `660575e3a955220e8af32096e2775db79b6e03af`.
- Closure gate: twelve tests pass in `19.034s` on Python 3.13.5 after strict document, plan, and architecture checks.
- Distribution: `project_harness-0.1.0-py3-none-any.whl`, thirty-nine files, twenty-nine packaged assets, zero bytecode entries.
- Isolated installation: the installed CLI initializes a service repository with CI; its `./dev/verify` succeeds; `project-harness doctor` succeeds with only the expected warning that the temporary target is not yet a Git repository.
- Acceptance results: AC-1 through AC-7 are represented by strict repository checks, regression tests, wheel inspection, isolated target execution, and Git-bound closure.
- Raw logs: `.harness/runs/` and temporary smoke directories; neither is committed.

## Outcomes and Retrospective

Project Harness is both the initializer and a working example of its output. The repository has a compact entry map, current-state knowledge, restartable complex-work state, explicit Main/Sub boundaries, deterministic completion commands, ownership-safe upgrades, strict evidence gates, and a non-destructive long-term garden report. The token-rendering defect became a reusable regression rule rather than an undocumented workaround.

## Follow-ups

No unresolved baseline item requires promotion to [`tech-debt-tracker.md`](../tech-debt-tracker.md).
