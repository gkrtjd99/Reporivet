---
id: ARCHITECTURE
kind: architecture
status: active
area: repository
summary: Current package, template, generated-runtime, definition, and verification architecture
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
- Generated command surface: POSIX wrappers around one copied standard-library runtime.

## Repository map

| Path | Responsibility | Public boundary |
|---|---|---|
| `src/reporivet/cli.py` | CLI parsing and command dispatch | `reporivet init`, `define`, `audit`, `upgrade`, `doctor` |
| `src/reporivet/initializer.py` | Safe inventory, rendering, ownership-aware writes, adoption, upgrades, and diagnostics | Python package internals |
| `src/reporivet/assets/project/` | Versioned templates and canonical generated runtime | Packaged data consumed by the initializer |
| `src/reporivet/assets/project/dev/harness.py` | Definition, audit, context, documents, plans, traceability, checks, Verification Run, Gate, closure, and gardening | Copied as `dev/harness.py` |
| `tests/` | Package, generated-runtime, security, evidence, closure, and distribution regression tests | `python3 -m unittest discover -s tests -v` |
| `dev/` | This repository's dogfooded generated-runtime entry points | `./dev/*` |
| `docs/` | Current-state, protocol, specification, design, planning, and historical knowledge | Read through `docs/README.md` |

## Components and dependency direction

| Component | Owns | May depend on | Must not depend on |
|---|---|---|---|
| CLI | User-facing arguments and exit codes | Initializer public functions | Generated target state |
| Initializer | Inventory, ownership, templates, adoption, upgrades | Standard library, packaged assets | Host plugins, LLM APIs, or external state |
| Packaged assets | Target repository contract and runtime source | Declared template variables | Initializer process state |
| Generated runtime | Definition validation, audit, routing, plans, checks, evidence, Gate, and closure | Standard library, repository files, Git, configured tools | Installed `reporivet` package after generation |
| Tests | Observable behavior and safety invariants | Public CLI and generated runtime | Network services, credentials, or model evaluation |

Dependency direction is:

```text
installed CLI -> initializer/package inventory -> rendered repository assets
repository wrapper -> dev/harness.py -> repository files, local Git, configured commands
```

The reverse edge from a generated repository to the installed package is forbidden.

## Package-side flows

### Initialization

1. Resolve or create the target root.
2. Inspect repository markers and infer a provisional runtime profile and command set.
3. Refuse symlinked paths and project-owned collisions at canonical managed paths.
4. Upsert only bounded managed blocks in `AGENTS.md` and `.gitignore`.
5. Create project-owned documents and `dev/harness.toml` only when missing.
6. Create or refresh only files carrying a `reporivet:managed` marker.
7. Generate document catalogs and run structural checks unless explicitly skipped.
8. For existing implementations, create `PLAN-0000` and require command review.

### Definition, audit, and adoption

- `reporivet define --root <path>` explicitly creates the repository harness and project-owned definition draft; `init` and `upgrade` do not start definition implicitly.
- `reporivet audit --root <path>` inventories authority, manifests, commands, source/test paths, conflicts, and proposed additions without writing files or executing project commands.
- `reporivet define --root <path> --adopt` audits first, refuses conflicts before writes, preserves existing README, instructions, architecture, CI, and configuration, and leaves inferred commands in review state.

### Upgrade and doctor

`upgrade` refreshes marked managed files and blocks and creates newly introduced missing scaffolds. It never rewrites current-state documents, specifications, plans, decisions, runbooks, or project-owned `dev/harness.toml`. New configurations receive explicit conservative `[gate]` defaults. Existing configurations without `[gate]` keep their exact bytes; the runtime applies conservative shadow defaults in memory and `doctor` emits an advisory.

## Repository-local runtime flow

1. `./dev/define status|validate|finalize` computes persisted progress, structurally validates evidence, and transactionally produces a final specification plus one first-slice ExecPlan. It does not invent product answers.
2. `./dev/audit` reproduces the deterministic read-only repository inventory without importing the installed package.
3. `./dev/code-map` derives a non-authoritative map from actual, configured, or confirmed planned paths. `./dev/context --path|--area|--plan` routes to matching authority, module contracts, maps, specifications, and active plans.
4. `./dev/check` provides fast structural and configured-command feedback.
5. One `./dev/verify` invocation creates exactly one `.harness/runs/<utc-run-id>-verify/` and runs security, catalog, documentation, plan, architecture, project, and optional smoke checks in fixed order.
6. Checks record `pass`, `fail`, `error`, `skipped`, or `unknown`. The run preserves `manifest.json`, `gate.json`, `report.md`, per-check JSON, and available logs even when the candidate fails or infrastructure errors.
7. Gate evaluates only explicit local base/head/target evidence and changed paths. It emits `PASS`, `REVIEW`, `BLOCK`, or `INCONCLUSIVE` under shadow or enforce mode; it never fetches, assumes a remote, or infers a parent.
8. `./dev/close-plan` binds a clean current `HEAD` to the plan base, invokes the canonical verification implementation exactly once, records the run/hash/verdict/SHA/criterion evidence, and moves the plan transactionally. `REVIEW` requires a genuine human reason; `BLOCK` and `INCONCLUSIVE` cannot be overridden.
9. `./dev/garden` reports maintenance candidates without deleting or rewriting content.

## CI and evidence

Generated and dogfood verification workflows retain immutable action SHAs and `contents: read`, fetch full history through checkout, select the explicit PR head or push head, export explicit base/head/target evidence, invoke `./dev/verify` once after bootstrap, append the latest report to the step summary, and upload `.harness/runs/` on success or failure. An all-zero push base is treated as unavailable rather than replaced with an inferred parent.

## Persistent data and external systems

The initializer writes only to the selected project root. It has no database, daemon, telemetry service, GitHub API client, secret store, plugin protocol, model client, or LLM API dependency.

Configured project commands execute only as argument arrays committed in `dev/harness.toml`. Built-in validation and local Git-evidence operations use fixed argument arrays owned by the copied runtime. Both inherit the caller's local environment and permissions. Verification artifacts are ignored local/CI evidence, not an external state system.

## Mechanical invariants

- Package version comes from `reporivet.__version__`; wheel metadata and managed markers must agree.
- Canonical package runtime and dogfood runtime differ only by the rendered version token; every managed wrapper is rendered from one `PYTHON`-aware template and remains executable.
- Upgrade preserves `dev/harness.toml` byte-for-byte.
- The regression suite covers definition/resume, audit/adoption, traceability, routing, Verification Run, Gate, closure, CI, ownership, and security boundaries.
- Wheel tests require a complete packaged-asset inventory with no bytecode, Skill bundle, target bundle, model, or daemon surface.
- An isolated installed CLI can generate and diagnose a project; after uninstall, repository-local definition, audit, context, planning, checks, verification, closure, and gardening continue to work.

## Known limits

- Generated shell wrappers target POSIX environments.
- Command inference is intentionally provisional and requires explicit review.
- Markdown/frontmatter validators support the committed schema, not arbitrary YAML or semantic product judgment.
- Remote publication and old-repository lifecycle operations are outside the package and this release work.
