# Reporivet

[한국어](README.md) | [English](README.en.md)

> **Repository-native harness for long-running, agent-driven software development.**

Reporivet is an initializer that uses OpenAI's [**Harness engineering: leveraging Codex in an agent-first world**](https://openai.com/ko-KR/index/harness-engineering/) as its primary design reference. It turns the repository itself into an operating environment that agents can read, modify, validate, and continuously clean up.

This project is not an agent execution platform or a separate orchestrator. After initialization, a project is operated with only its repository-local `AGENTS.md`, `docs/`, `dev/`, Git, and optional GitHub Actions. It does not require a specific LLM plugin, Skill, task database, or long-running controller.

## Core model

```text
AGENTS.md          Short map and operating contract
     ↓
docs/              Record system for product, structure, design, plans, and decisions
     ↓
ExecPlan           Living document that makes complex work restartable
     ↓
Main / Sub         Main owns scope, integration, and completion; Sub performs bounded tasks
     ↓
dev/               Deterministic context, check, and verification interface
     ↓
CI + garden        Enforced invariants and long-term drift reporting
```

The design background is documented in [`docs/design-docs/DESIGN-REPORIVET-001-initializer-and-runtime.md`](docs/design-docs/DESIGN-REPORIVET-001-initializer-and-runtime.md), and the generated output is specified in [`docs/product-specs/SPEC-REPORIVET-001-generated-project.md`](docs/product-specs/SPEC-REPORIVET-001-generated-project.md).

## What Reporivet guarantees

- `AGENTS.md` is a repository map of approximately 140 lines or fewer, not a long manual.
- The project owns its product, design, architecture, quality, security, and reliability documents after initialization.
- Complex work is managed by one ExecPlan in `docs/exec-plans/active/` and its Task Packets.
- Main owns planning, document lifecycle, integration, verification targets, and completion.
- Sub performs one task with a bounded read/write scope, acceptance criteria, and stop condition.
- Only commands committed in `dev/harness.toml` run at the completion gate.
- A configured executable that is missing causes a failure rather than silently skipping a check.
- Verification logs are stored in `.harness/runs/` and are not committed to Git.
- The generated `.gitignore` blocks build output, environment files, keys, credentials, and personal IDE settings by default.
- `./dev/security-check` rejects sensitive paths and high-confidence credential signatures that entered Git through force-add or similar overrides.
- `garden` reports stale plans, documents, paths, and references as candidates; it does not delete them automatically.
- Reinitialization and upgrades do not overwrite project-owned documents.

## Requirements

- Python 3.11 or later
- A POSIX environment for generated shell entry points
- Git recommended
- The build and test tools required by the target project

The Python runtime has no dependencies outside the standard library.

## Installation

Clone the repository and install it in editable mode.

```bash
git clone https://github.com/gkrtjd99/Reporivet.git
cd Reporivet
python3 -m pip install -e .
```

You can also run it without installing:

```bash
PYTHONPATH=src python3 -m reporivet --help
```

## Initialization

Reporivet can create a new path.

```bash
reporivet init \
  --root /absolute/path/to/project \
  --name "My Project" \
  --summary "The value users get from this project" \
  --project-kind service \
  --with-ci
```

Supported profiles are `service`, `web`, `application`, `library`, `cli`, and `other`. The `service`, `web`, and `application` profiles add `docs/RELIABILITY.md`.

To inspect the planned changes without applying them:

```bash
reporivet init --root ./my-project --name "My Project" --dry-run
```

### Existing projects

When existing source or build files are detected, Reporivet creates this plan automatically:

```text
docs/exec-plans/active/PLAN-0000-establish-repository-baseline.md
```

Command detection for an existing project is only a draft. `dev/harness.toml` starts with `configuration = "review"`, so `check` and `verify` do not pass until a person confirms the actual commands and lockfile and changes the configuration to `ready`.

### New empty projects

A new project starts with `baseline = "draft"` and `configuration = "ready"`. When no source exists yet, `./dev/verify` can run using only document, plan, and structure checks. Once source is added, configure the canonical commands.

## Generated operating commands

```bash
./dev/bootstrap                         # Install from the lockfile, etc.
./dev/context --path src/example.py    # Route to required docs and active plans
./dev/run                               # Run the application
./dev/check                             # Fast feedback
./dev/verify                            # Canonical completion gate
./dev/smoke                             # User-observable path
./dev/security-check                    # Block tracked secrets and personal files

./dev/docs-index                        # Refresh the document catalog
./dev/docs-index --check                # Check catalog drift
./dev/docs-check                        # Check document structure, metadata, and links
./dev/plan-check                        # Check ExecPlans and Task Packets
./dev/architecture-check                # Check structure documents and mechanical boundaries
./dev/garden                            # Report long-term cleanup candidates

./dev/new-plan "Account deletion" --area identity
./dev/task PLAN-2026-0001 T2
./dev/close-plan PLAN-2026-0001
```

Each wrapper calls `dev/harness.py` inside the repository. `dev/harness.toml` is the single source of truth for project-specific commands.

## Completing an ExecPlan

1. Resolve every Task and documentation impact.
2. Change the status to `verifying`.
3. Set `integrated_commit: "HEAD"`.
4. Commit the candidate changes and the verifying plan together so the worktree is clean.
5. Run `./dev/close-plan PLAN-...`.

`close-plan` runs the full verification from the current clean `HEAD`, records the actual SHA in `integrated_commit` and `verified_commit`, then moves the plan to `completed/`. The completion record is kept in a separate commit.

## Document lifecycle

| Document | Meaning | Management |
|---|---|---|
| `PRODUCT.md`, `ARCHITECTURE.md`, etc. | Current state | Update with implementation |
| `product-specs/`, `design-docs/`, `runbooks/` | Long-lived shared knowledge | Manage with front matter and a catalog |
| `exec-plans/active/` | Current execution state | Main keeps it updated |
| `exec-plans/completed/`, accepted ADRs | Historical record | Supersede instead of deleting |
| `generated/` | Regenerable facts | Only the generator edits them |
| `.harness/runs/` | Raw execution logs | Git-ignored and disposable |

`docs-index` updates only the explicit catalog block in each index and preserves human-written explanations.

## Safe upgrades

```bash
reporivet upgrade --root . --dry-run
reporivet upgrade --root .
reporivet doctor --root .
```

Upgradeable targets:

- The managed `reporivet` block in `AGENTS.md`
- The managed block in `.gitignore`
- `.reporivet-version`
- `dev/harness.py` and wrapper scripts
- Initializer-generated GitHub Actions files
- Missing scaffold files added by a new version

Never overwritten:

- `ARCHITECTURE.md`
- `docs/PRODUCT.md`, `DESIGN.md`, `QUALITY.md`, `SECURITY.md`, `RELIABILITY.md`
- Product specs, design documents, ExecPlans, ADRs, and runbooks
- Human-written areas of document indexes

If an existing project already owns paths such as `dev/check` or `dev/verify`, initialization reports the conflict and stops rather than silently replacing them.

## Repository hygiene and secrets

Reporivet adds a managed block to the `.gitignore` of itself and generated projects to reduce accidental commits of:

- Actual `.env` values, tokens, private keys, certificates, keystores, and cloud or Kubernetes credentials
- Terraform state and local deployment state
- Personal IDE, editor, and operating-system settings
- Local databases, raw logs, caches, virtual environments, dependency directories, test and coverage output, and build artifacts

By contrast, `.env.example`, `*.tfvars.example`, `.vscode/extensions.json`, source code, migrations, documentation, and package-manager lockfiles remain trackable. If an intentionally public test key or fixture matches an ignore pattern, review it, record the rationale, and add it explicitly.

`.gitignore` is not a security boundary and does not remove secrets that were already committed. If a secret has ever entered Git, revoke and rotate it first, then remove it from history as needed. Follow [`.github/SECURITY.md`](.github/SECURITY.md) for vulnerability reports.

## CI

Using `--with-ci` generates two workflows:

- `bootstrap` and `verify` on pull requests and pushes to `main`
- A weekly or manually triggered `garden` report upload

If the target project needs additional runtime installation after initialization, extend the workflow for that project. The key requirement is to keep `dev/harness.toml` and CI aligned so they do not perform different verification.

## Testing this repository

```bash
python3 -m unittest discover -s tests -v
```

The tests cover initialization, existing-project baselines, preservation of project-owned documents, safe upgrades, sensitive/personal/build-artifact ignore policy and example/lockfile exceptions, force-added sensitive paths and high-confidence credential signature blocking, catalog drift, preservation of future ExecPlan tokens, Task Packets, strict baselines, missing-tool failures, dry runs, command conflicts, and Git commit-bound plan closure.

## Non-goals

- An orchestrator that automatically coordinates multiple Main agents
- A task database, lease, scheduler, journal, or replay system
- An unattended pull-request merge bot
- Plugins or Skills for a particular LLM product
- Replacing every semantic judgment with scripts

Mechanically decidable rules are enforced by CI. Decisions that require judgment—simplicity, design validity, and document retirement—remain evidence-based decisions by Main and independent reviewers.

## Reference

The primary design reference is OpenAI's [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/ko-KR/index/harness-engineering/). The concise repository-specific mapping is maintained in [`docs/references/openai-harness-engineering.md`](docs/references/openai-harness-engineering.md).
