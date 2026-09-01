# Reporivet

Reporivet is a Python 3.11+ package for establishing and safely maintaining a repository-local, document-first operating contract for coding agents.

The default onboarding command is the integrated `reporivet setup` flow. It coordinates audit, visible guided definition, exact preview, and approved document/adaptor changes. `reporivet init` remains the structure-only, create-if-missing path, and lower-level `reporivet define` remains available for resumable definition work. Complete user-confirmed structured procedures may produce optional instruction-only project Skills through resumed setup. Reporivet does not leave a copied executor in the target repository; the project owns commands, tests, CI, deployment, operations, secrets, and evidence.

Korean: [`README.md`](README.md)

## Product boundary

```text
agent host
    -> AGENTS.md
    -> docs/README.md
    -> one matching active Plan
    -> task-relevant authority
    -> project-owned commands and evidence

Reporivet package
    -> setup / init / define / audit / doctor / migrate
    -> documents, metadata, and optional thin adapters
```

Removing the package must leave generated Markdown, Plans, Skills, Git, and project commands useful. Reporivet itself does not create a Plan or a target runtime; the Main Skill creates or resumes the first ordinary Markdown Plan when the project needs one.

Reporivet does not generate project command wrappers, CI workflows, task databases, journals, evidence archives, background services, or an automatic Plan completion mechanism. It does not spawn or dispatch Agents, execute project commands, operate CI or deployment, or provide a scheduler, Gate, or hidden state store.

## Current generated tree

A document-first setup creates missing paths and preserves existing project-owned or ambiguous content.

```text
AGENTS.md
ARCHITECTURE.md
.reporivet-version
.gitignore                                      bounded managed block

docs/
  README.md
  PRODUCT.md
  DESIGN.md
  QUALITY.md
  OPERATIONS.md
  SECURITY.md
  PLANS.md
  product-specs/
    index.md
    _template.md
    project-definition.draft.md                 guided definition only
  design-docs/
    index.md
    _template.md
    core-beliefs.md
  decisions/
    README.md
    _template.md
  exec-plans/
    _template.md
    active/.gitkeep
    completed/.gitkeep
    tech-debt-tracker.md
  references/
    README.md
    project-definition-protocol.md
  runbooks/
    index.md
    _template.md

CLAUDE.md                                      Claude profile; thin import
.claude/skills/reporivet-main/SKILL.md         instruction-only role adapter
.claude/skills/reporivet-implementation/SKILL.md
.claude/skills/reporivet-verification/SKILL.md
.claude/settings.json                          opt-in deny-only settings
```

`project-definition.draft.md` appears only after guided definition starts and remains the visible resume state until a maintainer deliberately removes it. The `.gitkeep` files only preserve empty Plan directories and may be removed when tracked Plans exist. Reporivet changes only its bounded `.gitignore` block and preserves all other ignore rules.

`CLAUDE.md` and the three Skills are host-specific and removable without changing canonical authority. `.claude/settings.json` is absent by default, requires exact preview approval, and is never merged with or written over an existing file.

Fresh document-first targets receive neither a `dev/` execution surface nor a `.harness/` state tree. This dogfood repository retains `dev/harness.toml` only as inactive project-owned legacy configuration; it is not current execution authority and is not generated for new targets. Retained `.harness/runs` is retired historical sensitive state. Current code does not read its contents, write it, or delete it; do not use it as current evidence or working storage.

See [`docs/README.md`](docs/README.md) for per-path ownership, optionality, and removal boundaries.

## Install for users

Public installation guidance is pipx-primary:

```bash
pipx install reporivet
```

Pip is also supported from the same wheel:

```bash
python -m pip install reporivet
```

These are the two user installation forms for one wheel; pipx is the preferred isolated CLI environment. Completed PLAN-2026-0003 records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive. Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside scope.

## Contributors only: source checkout

Contributors may run the package directly from a checkout with an explicitly selected Python 3.11-or-newer interpreter. These commands are not the public installation path:

```bash
PYTHON=/absolute/path/to/python3.11-or-newer
"$PYTHON" --version

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/reporivet-pycache" \
PYTHONPATH=src \
"$PYTHON" -m reporivet --help
```

## Default onboarding

Choose an absolute target path and use the integrated setup command from an installed Reporivet:

```bash
ROOT=/absolute/path/to/target
reporivet setup --root "$ROOT"
```

`setup` coordinates the read-only audit, visible guided definition, resumable answers, exact preview, and explicitly approved apply. It reports all seven evidence topics, including the actual Open items, and does not execute project commands or create a Plan. Only a complete, user-confirmed structured procedure record can add an instruction-only project Skill, and that happens through resumed setup; incomplete, inferred, generic, Proposed, Open, and Sources records add none.

`reporivet init --root "$ROOT"` is the structure-only, non-overwriting create-if-missing path. It does not perform the guided interview or create a Plan. The Main Skill, not Reporivet, creates or resumes the first ordinary Markdown Plan by inspecting active and completed history and choosing the lowest unused current-year ID when no matching active Plan exists.

## Lower-level definition interface

`define` remains available when a maintainer needs the visible resumable definition flow directly:

```bash
reporivet define start --root "$ROOT"
reporivet define resume --root "$ROOT"
reporivet define resume --root "$ROOT" --answers /absolute/path/to/answers.json
reporivet define status --root "$ROOT"
reporivet define finalize --root "$ROOT"
```

The visible Markdown draft is the only resume state. Each of the seven topics keeps **Confirmed**, **Proposed**, **Open**, and **Sources** separate. Explicit answers enter Confirmed with only whitespace normalization; scanner observations remain Proposed; blanks remain Open. No LLM rewrites answers, chooses authority, or promotes inference to fact. To opt into deny-only Claude settings, include `--with-claude-settings` in both final preview and approved apply. Existing settings are always preserved.

## Package CLI

| Command | Purpose | Mutation boundary |
| --- | --- | --- |
| `reporivet setup` | Default integrated audit, guided definition, exact preview, and approved setup. | Writes only after explicit approval and safety revalidation; never creates a Plan or executes project commands. |
| `reporivet init` | Structure-only, non-overwriting create-if-missing bundle. | Preserves existing project-owned content and does not run guided setup or create a Plan. |
| `reporivet define start/resume/status/finalize` | Lower-level visible guided definition and exact preview/apply. | Only the documented draft steps and approved apply write bounded definition/setup paths. |
| `reporivet audit` | Deterministic repository inventory. | Read-only; it does not execute project commands. |
| `reporivet upgrade` | Maintain missing current bundle paths. | Refuses recognized legacy 0.2 surfaces and requires explicit migration. |
| `reporivet migrate` | Preview, apply, or roll back the 0.2 migration transaction. | Requires external backup and exact approval for apply. |
| `reporivet doctor` | Diagnose document-first structure. | Read-only. |

Use the installed `reporivet <command>` for normal project use. `PYTHONPATH=src "$PYTHON" -m reporivet <command>` is a contributor-only source-checkout form.

## Main / Implementation Sub / Verification Sub

- **Main** owns intent, scope, non-goals, acceptance, the overall task tree, integration, decisions, candidate identity, evidence judgment, and every serialized Plan edit. Main Skill instructions may describe host-native Agent dispatch for a project workflow, but Reporivet does not spawn or dispatch Agents.
- **Implementation Sub** receives one bounded Task Packet with exact reads, allowed writes, protected paths, acceptance criteria, project-owned checks, stop conditions, and required return evidence. If a child is itself broad, only a packet marked `Role: Task Owner` and `May delegate: yes` may run its predeclared bounded descendants such as `T<n>-A-1`; ordinary leaf Agents do not delegate, broaden scope, or approve their own work. Descendants inherit the parent's scope, protected paths, and acceptance.
- **Verification Sub** starts from a fresh context, identifies the integrated candidate, runs applicable project-owned checks, and returns criterion-level results and residual risks. Read-only verification leaves may run in parallel, do not delegate by default, and depend on the integrated candidate. They do not repair it unless Main dispatches a separate implementation task. Project command execution remains with the project and its host workflow, not Reporivet.

For every milestone classified as broad, this is a common installed-project rule:

`T<n> (broad milestone) -> T<n>-A/B/C/... (owned child packets, all ready leaves dispatched concurrently) -> T<n>-I (integration) -> T<n>-V1/V2/... (parallel fresh verification)`

This rule does not apply to inherently single or serial milestones. Examples may still use `T1`, but every broad milestone follows the generic shape. Each child task retains its own owner, state, dependencies, outcome, result, and matching bounded packet. Parallel mutable siblings require disjoint allowed-write sets, frozen shared interfaces, and separate worktrees. They converge on an explicit integration node before fresh verification nodes run.

Main alone serializes Plan edits, manually records integration and verification, and moves a terminal Plan to `completed/`; no command decides completion. This is a host/project operating contract, not a Reporivet runtime: Reporivet installs no Agent spawn/dispatch mechanism, command runner, CI/deployment system, scheduler, task store, lease, lock, Gate, evidence archive, hidden state, or automatic dispatcher/closure.

## Explicit 0.2 migration and rollback

Ordinary setup does not silently remove recognized legacy surfaces. Choose an absolute backup directory outside the target and preview the complete transaction:

```bash
ROOT=/absolute/path/to/target
BACKUP_DIR=/absolute/path/outside/target/reporivet-backup

PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --root "$ROOT" \
  --from 0.2 \
  --preview \
  --backup-dir "$BACKUP_DIR"
```

Review every action, then apply the exact fingerprint:

```bash
MIGRATION_PREVIEW_SHA256='paste-the-emitted-sha256'

PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --root "$ROOT" \
  --from 0.2 \
  --apply \
  --approve-preview "$MIGRATION_PREVIEW_SHA256" \
  --backup-dir "$BACKUP_DIR"
```

Apply revalidates the approved preview, creates a mode-restricted external backup and manifest, preserves project-owned or ambiguous paths, and attempts automatic restoration after a failed apply when safe. The backup covers only migration-owned paths; it is not a general repository or production backup.

Roll back with the exact emitted manifest:

```bash
PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --rollback /absolute/path/to/external-backup/manifest.json
```

Rollback refuses if later user changes would be overwritten. Keep the external backup until the migrated candidate passes project-owned checks and the maintainer accepts it. See [`docs/OPERATIONS.md`](docs/OPERATIONS.md) for recovery and incident boundaries.

## Project checks

Select the interpreter and external bytecode cache as shown above, then run:

```bash
PYTHONPATH=src "$PYTHON" -m unittest discover -s tests -v
PYTHONPATH=src "$PYTHON" -m compileall -q src tests
PYTHONPATH=src "$PYTHON" -m reporivet doctor --root .
git diff --check
```

Artifact build and release checks are environment-dependent and are not established by these source commands. [`docs/QUALITY.md`](docs/QUALITY.md) is authoritative for evidence; [`docs/OPERATIONS.md`](docs/OPERATIONS.md) is authoritative for running and release boundaries.

## Non-goals

Reporivet is not:

- a general orchestration platform, scheduler, task service, or hidden state store;
- a replacement for project build, test, CI, release, deployment, observability, backup, recovery, or incident systems;
- a copied multi-host prompt, executor, model, or judge bundle;
- an authority that infers project facts or turns scanner observations into approved requirements;
- a guarantee that host deny rules form a sandbox;
- evidence of a release, installation, artifact, publication, or deployment that was not directly verified;
- package-side publication, signing, or release automation.

## Current authority

- Knowledge and generated surfaces: [`docs/README.md`](docs/README.md)
- Product: [`docs/PRODUCT.md`](docs/PRODUCT.md)
- Architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Design: [`docs/DESIGN.md`](docs/DESIGN.md)
- Quality: [`docs/QUALITY.md`](docs/QUALITY.md)
- Operations: [`docs/OPERATIONS.md`](docs/OPERATIONS.md)
- Security: [`docs/SECURITY.md`](docs/SECURITY.md)
- Plans: [`docs/PLANS.md`](docs/PLANS.md)
