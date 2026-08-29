---
id: ARCHITECTURE
kind: architecture
status: active
area: repository
summary: Current package, template, generated-runtime, and verification architecture
applies_to:
  - "src/**"
  - "tests/**"
  - "dev/**"
---

# Architecture

This document describes implemented reality. Proposed structure belongs in an active ExecPlan until it exists and is verified.

## Runtime profile

- Project kind: Python command-line initializer.
- Primary language: Python 3.11 or newer.
- Runtime dependencies: Python standard library only.
- Distribution: a Python wheel exposing the `reporivet` console command.

## Repository map

| Path | Responsibility | Public boundary |
|---|---|---|
| `src/reporivet/cli.py` | CLI parsing and command dispatch | `reporivet init`, `upgrade`, `doctor` |
| `src/reporivet/initializer.py` | Safe project inspection, rendering, ownership-aware writes, command inference, upgrades, and diagnostics | Python package internals |
| `src/reporivet/assets/project/` | Versioned templates and generated repository runtime | Packaged data consumed by the initializer |
| `src/reporivet/assets/project/dev/harness.py` | Canonical generated runtime for context, documents, plans, checks, verification, and gardening | Copied to target repositories as `dev/harness.py` |
| `tests/` | End-to-end initializer and generated-runtime regression tests | `python3 -m unittest discover -s tests -v` |
| `dev/` | This repository's dogfooded harness entry points | `./dev/*` |
| `docs/` | This repository's current-state and historical operating knowledge | Read through `docs/README.md` |

## Components and dependency direction

| Component | Owns | May depend on | Must not depend on |
|---|---|---|---|
| CLI | User-facing arguments and exit codes | Initializer public functions | Generated target state |
| Initializer | File ownership, templates, detection, upgrades | Standard library, packaged assets | Host-specific plugins or LLM APIs |
| Packaged assets | Target repository contract and runtime source | Template variables only | Initializer process state |
| Generated runtime | Repository-local context, validation, command execution, Git-bound plan closure | Standard library, target repository files and configured tools | Installed `reporivet` package after generation |
| Tests | Observable behavior and safety invariants | Public CLI and generated runtime | Network services or user accounts |

Dependency direction is `CLI -> initializer -> packaged assets`. A generated target runs independently as `wrapper -> dev/harness.py -> repository files/configured commands`.

## Initialization flow

1. Resolve or create the target root.
2. Inspect repository markers and infer a draft runtime profile and command set.
3. Refuse collisions with existing project-owned canonical command paths.
4. Upsert only marked blocks in `AGENTS.md` and `.gitignore`.
5. Create project-owned documents and `dev/harness.toml` only when missing.
6. Create or refresh only files carrying a `reporivet:managed` marker.
7. Generate document catalogs and run structural checks unless explicitly skipped.
8. For existing implementations, create `PLAN-0000` and require command review.

## Upgrade flow

`upgrade` reads the existing project-owned configuration, refreshes marked harness files and blocks, creates newly introduced missing scaffolds, and preserves all unmarked or project-owned content. It never rewrites current-state documents, plans, decisions, runbooks, specifications, or `dev/harness.toml`.

## Generated runtime flow

1. `./dev/context` routes an agent to stable entry documents, relevant durable documents, and active plans.
2. `./dev/check` validates catalogs, documents, and plans before fast configured commands.
3. `./dev/verify` adds strict baseline and architecture gates, configured completion commands, and optional smoke commands.
4. Every configured command is executed without a shell, streamed to the console, and logged under `.harness/runs/`.
5. `./dev/close-plan` requires a clean Git worktree, verifies current `HEAD`, records its SHA, and archives the plan.
6. `./dev/garden` reports maintenance candidates without deleting or rewriting content.

## Persistent data and external systems

The initializer writes only to the selected project root. It has no database, daemon, telemetry service, network client, GitHub API client, secret store, plugin protocol, or LLM API dependency.

The generated runtime may execute only command arrays explicitly committed in the target's `dev/harness.toml`. Those commands inherit the caller's local environment and permissions.

## Mechanical invariants

- `python3 -m unittest discover -s tests -v` covers ownership, idempotence, sensitive/local/build ignore behavior and safe exceptions, conflict handling, document indexing, plan validation, deterministic command failure, dry-run behavior, and Git-bound closure.
- `python3 -m compileall -q src tests` checks Python syntax and import compilation.
- Wheel smoke tests confirm all packaged assets are included and an installed console command can initialize and verify a project.
- Target repositories enforce current-state document metadata, catalog drift, links, ExecPlan lifecycle, Task Packet fields, strict baseline readiness, executable availability, and clean-Git plan closure.

## Known limits

- Generated shell wrappers target POSIX environments.
- Command inference is intentionally provisional for an existing implementation and requires explicit review.
- Semantic design quality, conflicting requirements, and document retirement still require Main or human judgment.
- Remote repository creation is outside the package; publishing uses ordinary Git or a connected GitHub integration.
