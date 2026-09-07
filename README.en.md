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

### Agent entry points

- `AGENTS.md` is the repository operating contract and documentation entry point for every agent.
- In this source repository only, author the portable block in `CLAUDE.md`, then run `./dev/agent-contract-sync` to project its exact bytes to the entire `AGENTS.md`. Do not edit the projection directly. `./dev/agent-contract-sync --check` detects drift without writes; provider-specific text outside the block is not copied.
- Generated projects do not receive this source-only sync tool, tool-specific `CLAUDE.md`, `.claude/`, or nested `AGENTS.md` files. If a tool requires its own entry point, the project may add a thin adapter that points to the same `AGENTS.md`.
- In generated targets, `AGENTS.md` remains canonical even when a tool-specific entry point exists.

The two-lifetime structure is documented in [`DESIGN-REPORIVET-001`](docs/design-docs/DESIGN-REPORIVET-001-initializer-and-runtime.md), definition/adoption/evidence Gate design in [`DESIGN-REPORIVET-002`](docs/design-docs/DESIGN-REPORIVET-002-project-definition-adoption-and-evidence-gate.md), generated behavior in [`SPEC-REPORIVET-001`](docs/product-specs/SPEC-REPORIVET-001-generated-project.md), and detailed requirements in [`SPEC-REPORIVET-002`](docs/product-specs/SPEC-REPORIVET-002-project-definition-adoption-and-evidence-gate.md).

## Generated repository structure

A normal initialization does not guess application code or infrastructure. It creates the documentation, command, and verification surfaces that let the project operate from its own repository.

```text
project/
├── AGENTS.md                    Short operating contract and document router
├── ARCHITECTURE.md              Source of truth for the implemented structure
├── .gitignore                   Project content plus a managed security block
├── .reporivet-version           Managed asset version
├── dev/
│   ├── harness.py               Local runtime that works after package removal
│   ├── harness.toml             Authority for project commands, paths, and policy
│   └── bootstrap, define, audit, code-map, context, check, verify, ...
├── docs/
│   ├── README.md                Knowledge map and reading order
│   ├── PRODUCT.md               Current purpose, users, requirements, and non-goals
│   ├── DESIGN.md                Visual design, only with visual-design capability
│   ├── FRONTEND.md              Frontend implementation, only with frontend capability
│   ├── PRODUCT_SENSE.md         Product judgment, only with product-sense capability
│   ├── QUALITY.md               Tests, Verification Run, and Gate expectations
│   ├── SECURITY.md              Trust, secrets, command execution, and review boundaries
│   ├── PLANS.md                 ExecPlan, Task Packet, and closure policy
│   ├── RELIABILITY.md           Only with reliability capability
│   ├── product-specs/           Durable behavioral specifications
│   ├── design-docs/             Durable designs and trade-off records
│   ├── exec-plans/              Active work and completed history
│   ├── module-contracts/        Only justified multi-file boundaries
│   ├── decisions/               Consequential decisions that can be superseded
│   ├── runbooks/                Operational steps with evidence and rollback
│   ├── references/              Curated references and the definition protocol
│   └── generated/code-map.md    Non-authoritative map derived from repository evidence
├── .harness/runs/               Git-ignored local verification evidence and raw logs
└── .github/workflows/           Only with --with-ci
```

When an existing implementation is detected, Reporivet may add `docs/exec-plans/active/PLAN-0000-establish-repository-baseline.md`, and inferred commands remain in `configuration = "review"` until a person confirms them. Neither `init` nor `upgrade` implicitly creates a project-definition draft; it appears only after an explicit `reporivet define --root .`.

### Why the surfaces are separate

| Surface | Responsibility | Reason for separation |
|---|---|---|
| `AGENTS.md` | Entry order, scope limits, Main/Sub ownership, and stop conditions | Point to authority without preloading long-lived knowledge |
| Current-state documents | Product, structure, design, quality, and security that are true now | Prevent plans or historical records from being mistaken for current reality |
| Durable documents | Long-lived specifications, designs, decisions, and runbooks | Preserve contracts and rationale in Git across sessions and agents |
| ExecPlan | Scope, non-goals, Tasks, acceptance, and evidence for complex work | Make work restartable and constrain expansion without a separate task database |
| `dev/` | Deterministic commands shared by every agent and CI | Use observable command results rather than explanations as evidence |
| `.harness/runs/` | Manifest, Gate, report, check JSON, and available logs | Bind results to a candidate commit while separating raw output from durable knowledge |

### Agent reading order and context use

Files do not enter model context merely because they exist on disk. An agent reads `AGENTS.md` first and then uses the narrowest available router input:

```bash
./dev/context --path src/example.py
./dev/context --area identity
./dev/context --plan PLAN-2026-0001
```

`context` does not print every document body. It returns paths and one-line summaries for matching module contracts, code-map entries, durable documents, product specifications, and active plans. The agent then reads only what the current Task needs. `AGENTS.md` forbids preloading all documentation, dependencies, generated output, completed plans, caches, or raw logs. A small local change need not read or create a large ExecPlan, and a Sub Agent receives only the exact read/write scope in its Task Packet.

This reduces context use but is not an operating-system read sandbox. Keep document `area` and `applies_to` metadata specific and keep code-map, catalog, and documentation checks green to limit routing drift; Main and human reviewers retain the final semantic scope judgment.

### What initialization does not create

Reporivet does not guess project authority, so normal initialization does not create a project `README.md`, source or test code, `Dockerfile`, Docker Compose, Kubernetes manifests, Helm charts, Terraform, or deployment configuration. Cloud, Kubernetes, or Terraform entries in `.gitignore` and `SECURITY.md` are general safeguards against committing credentials and local state, not infrastructure configuration. Audit and adoption may inventory and preserve existing infrastructure files, but they do not create them.

## What Reporivet guarantees

- `AGENTS.md` is a repository map of approximately 140 lines or fewer, not a long manual.
- The project owns its product, design, architecture, quality, security, and reliability documents after initialization.
- Complex work is managed by one ExecPlan in `docs/exec-plans/active/` and its Task Packets.
- Main owns planning, document lifecycle, integration, verification targets, and completion.
- Sub performs one task with a bounded read/write scope, acceptance criteria, and stop condition.
- Explicit definition separates Confirmed, Proposed, Open, and Sources evidence and validates `JRN-* -> REQ-P0-* -> AC-*` relationships.
- `audit` is deterministic and read-only; `define --adopt` preserves existing authority and stops before writes on conflict.
- Opt-in ExecPlan traceability connects product criteria to Tasks, criterion-level evidence, and a verified commit.
- Project-configured commands run only as argv arrays committed in `dev/harness.toml`; built-in validation and local Git-evidence operations use fixed argv. A missing configured executable fails rather than disappearing.
- One `./dev/verify` uses a fixed check order and preserves a manifest, Gate, report, check JSON, and available logs under one `.harness/runs/<run>-verify/`.
- Gate uses only explicit local base/head/target and changed paths to return `PASS`, `REVIEW`, `BLOCK`, or `INCONCLUSIVE`.
- The generated `.gitignore` blocks build output, environment files, keys, credentials, and personal IDE settings by default.
- `./dev/security-check` rejects sensitive paths and high-confidence credential signatures that entered Git through force-add or similar overrides.
- `garden` reports stale plans, documents, paths, and references as candidates; it does not delete them automatically.
- Reinitialization and upgrades do not overwrite project-owned documents or existing `dev/harness.toml` bytes.
- The generated runtime does not import the installed package, so repository-local commands remain usable after Reporivet is removed.

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

Supported profiles are `service`, `web`, `application`, `library`, `cli`, and `other`. By default, `web` enables visual-design and frontend documents; `service`, `web`, and `application` enable reliability. Product-sense is opt-in. The selected document capabilities determine whether `DESIGN.md` (visual only), `FRONTEND.md`, `PRODUCT_SENSE.md`, and `RELIABILITY.md` are created; existing project-owned documents remain preserved during upgrade.

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

## Project definition and existing-repository adoption

`init` and `upgrade` never start product definition implicitly. A person starts it explicitly and edits the repository-owned draft.

```bash
reporivet define --root .
./dev/define status
./dev/define validate
./dev/define finalize
```

The fourteen sections keep Confirmed, Proposed, Open, and Sources separate. `finalize` rejects blocking Open items, placeholders, contradictions, and invalid stable-ID links, then transactionally creates one final product specification and one first vertical-slice ExecPlan from validated evidence. Follow the [Project Definition Protocol](docs/references/project-definition-protocol.md) for the complete procedure.

For an existing repository, inspect authority and command candidates with a no-write audit before adoption:

```bash
reporivet audit --root .
reporivet define --root . --adopt
./dev/audit
```

Adoption preserves the existing README, user-owned `AGENTS.md` text, architecture, CI, catalogs, and configuration. Inferred commands remain `configuration = "review"` until a person verifies them.

## Generated operating commands

```bash
./dev/bootstrap                         # Install from the lockfile, etc.
./dev/define status                     # Report definition progress and next section
./dev/define validate                   # Validate evidence structure and trace links
./dev/define finalize                   # Create final spec and first ExecPlan
./dev/audit                             # Inventory without writes or command execution
./dev/code-map                          # Refresh the evidence-backed code map
./dev/context --path src/example.py    # Route to docs, contracts, and active plans
./dev/run                               # Run the application
./dev/check                             # Fast feedback
./dev/verify                            # Only canonical completion gate and evidence run
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

`close-plan` runs the canonical Verification Run exactly once against the plan's explicit base and the current clean `HEAD`. `PASS` closes directly; `REVIEW` requires a reason written by a person through `--accept-review "..."`; `BLOCK` and `INCONCLUSIVE` cannot be overridden. Success records the run ID, finalized manifest SHA-256, Gate verdict, verified SHA, criterion evidence, and applicable REVIEW reason before moving the plan to `completed/`. Commit that historical record separately without running a second `./dev/verify`.

## Document lifecycle

| Document | Meaning | Management |
|---|---|---|
| `PRODUCT.md`, `ARCHITECTURE.md`, etc. | Current state | Update with implementation |
| `product-specs/`, `design-docs/`, `runbooks/` | Long-lived shared knowledge | Manage with front matter and a catalog |
| `exec-plans/active/` | Current execution state | Main keeps it updated |
| `exec-plans/completed/`, accepted ADRs | Historical record | Supersede instead of deleting |
| `generated/` | Regenerable facts | Only the generator edits them |
| `.harness/runs/` | Local Verification Run evidence and raw logs | Git-ignored, review before sharing, disposable |

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
- `dev/harness.toml`
- Product specs, design documents, ExecPlans, ADRs, runbooks, and definition evidence
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

- On pull requests and `main` pushes, bind explicit base/head/target evidence and run `bootstrap` followed by exactly one `verify`
- Append the report to the step summary and upload `.harness/runs/` regardless of success or failure
- Upload a weekly or manually triggered `garden` report

Actions use immutable SHA pins, `contents: read`, and full checkout history. An all-zero push base remains unavailable instead of triggering parent inference. If the target project needs additional runtime installation after initialization, extend the workflow for that project while keeping `dev/harness.toml` and CI aligned.

## Testing this repository

```bash
python3 -m unittest discover -s tests -v
```

The tests cover definition/resume/finalization, deterministic audit/adoption, traceability, conditional contracts/code map/context, Verification Run status and artifacts, Gate/closure, initialization and upgrade ownership, CI structure, security, wheel inventory, isolated installation, and repository-local operation after package uninstall.

The `0.2.0` target is a local release-ready boundary. It builds, inspects, installs, uninstalls, and exercises the wheel without network access; it does not publish to PyPI or create a GitHub Release.

## Non-goals

- An orchestrator that automatically coordinates multiple Main agents
- A task database, lease, scheduler, journal, replay system, daemon, plugin, or MCP bridge
- Unattended pull-request creation/merge, package publication, deployment, or another external write
- Skills, runtime target bundles, or model judges for a particular LLM product
- Replacing semantic product judgment, conflict resolution, or human REVIEW acceptance with scripts
- Backup, archive, deprecation writes, deletion, or other operation of the former repository

Mechanically decidable rules are enforced by CI. Decisions that require judgment—simplicity, design validity, and document retirement—remain evidence-based decisions by Main and independent reviewers.

## Reference

The primary design reference is OpenAI's [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/ko-KR/index/harness-engineering/). The concise repository-specific mapping is maintained in [`docs/references/openai-harness-engineering.md`](docs/references/openai-harness-engineering.md).
