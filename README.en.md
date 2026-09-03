# Reporivet

Reporivet is a Python 3.11+ package for establishing a repository-local, document-first operating contract for coding agents during explicit setup. The default onboarding command is the integrated `reporivet setup` flow: it audits, collects visible guided definition, renders an exact preview, and applies an approved one-shot package-side transaction. `reporivet init` remains the structure-only, create-if-missing path, and lower-level `reporivet define` remains available for resumable definition work. Reporivet does not leave a copied executor, target Skill, marker, generated settings, or runtime in the target; the project owns commands, tests, CI, deployment, operations, secrets, Git, and evidence.

Korean: [`README.md`](README.md)

## Product boundary

```text
host/project workflow
    -> AGENTS.md
    -> docs/README.md
    -> one matching active Markdown Plan
    -> task-relevant authority
    -> project-owned commands and evidence

Reporivet package (only while setup or transition is invoked)
    -> setup / init / define / audit / migrate
    -> visible draft, exact preview, and approved transaction
```

Setup is a bounded one-shot package-side transaction. An installed package or explicitly selected local source may be used while the user invokes setup or a legacy transition; after handoff, the package may be removed without reducing ordinary target work. The target remains useful through its Markdown, Plans, static runbooks, Git, project commands, and host-native Agents. Reporivet does not execute project commands, spawn or dispatch Agents, create a Plan, or provide a continuing target runtime or diagnosis command.

An optional external user-scoped `/reporivet-setup` wrapper is instruction-only and outside the target. It only relays the deterministic preview/apply flow; it never installs, resolves, downloads, or imports Reporivet and never edits target files itself.

## Current generated tree

A one-shot setup creates missing project-owned paths and preserves existing project-owned or ambiguous content.

```text
AGENTS.md
ARCHITECTURE.md

docs/
  README.md
  PRODUCT.md
  DESIGN.md                                      universal design document for every project
  FRONTEND.md                                    created only when `web_ui=yes` is Confirmed
  QUALITY.md
  OPERATIONS.md
  RELIABILITY.md                                 created only when `deployed_runtime=yes` is Confirmed
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
    <slug>.md                                   static procedure documentation

CLAUDE.md                                      optional exact adapter: @AGENTS.md
```

The draft appears only while guided definition needs resuming. Setup creates the empty Plan directories when needed but never creates an active Plan file. The Main host/project procedure searches active and completed history, resumes one matching active Plan, or creates the first ordinary Markdown Plan with the lowest unused current-year ID.

## Conditional capability documents

`reporivet setup` adds two capability questions to the visible definition. An exact **Confirmed** `yes` for `web_ui` creates `docs/FRONTEND.md`; an exact **Confirmed** `yes` for `deployed_runtime` creates `docs/RELIABILITY.md`. The questions are independent, so both documents may be selected. `no`, Proposed, Open, Sources-only, inferred values, and audit observations alone never create an optional document.

`DESIGN.md` is the universal authority for visual language, interaction, and accessibility. `FRONTEND.md` covers frontend implementation and client-side loading/error/retry behavior; it does not own service reliability. `RELIABILITY.md` is a supplemental document for service/runtime failure modes, SLI/SLO, observability, deployment/rollback, recovery, and incident boundaries. It never replaces or outranks the universal operational authority in `OPERATIONS.md`. Both documents require project ownership, sources and provenance, applicable candidate/environment, and project-owned checks; they must not invent unconfirmed topology, telemetry, SLO, or recovery claims.

Fresh targets contain no Reporivet role or procedure Skill, `.reporivet-version`, generated `.claude/settings.json`, copied module/runtime, doctor gate, registry or package-resolution instruction, command wrapper, scheduler, dispatcher, task store, Gate, evidence archive, or hidden state. Existing legacy paths may be examined only during an explicit setup rerun with exact canonical ownership evidence; names, markers, frontmatter, or locations alone never authorize deletion.

## Static procedure runbooks

Only one complete, unique, user-confirmed strict structured procedure record qualifies. It must contain exactly these nine fields: `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, and `rollback`. The deterministic output is ordinary Markdown at `docs/runbooks/<slug>.md`, with no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration. Incomplete, malformed, generic, inferred, Proposed, Open, Sources-only, or duplicate records produce no runbook. A runbook is reviewed project documentation, not an executor.

## Install for setup-time users

Public installation guidance is for invoking setup or an explicit package-side transition:

```bash
pipx install reporivet
```

Pip is also supported from the same wheel:

```bash
python -m pip install reporivet
```

These are two ways to install one setup-time package. They do not create a continuing package requirement for a generated target. Completed PLAN-2026-0003 records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive. Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside scope.

## Contributors only: source checkout

Contributors may run package-side commands directly from a checkout with an explicitly selected Python 3.11-or-newer interpreter. These commands are not the public installation path and are not commands a generated target must run after setup:

```bash
PYTHON=/absolute/path/to/python3.11-or-newer
"$PYTHON" --version

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/reporivet-pycache" \
PYTHONPATH=src \
"$PYTHON" -m reporivet --help
```

## Default onboarding

Choose an absolute target path and use the integrated setup command while Reporivet is available for setup:

```bash
ROOT=/absolute/path/to/target
reporivet setup --root "$ROOT"
```

`setup` coordinates the read-only audit, visible guided definition, answer resume, exact preview, and explicitly approved apply. It reports actual Open items and revalidates the target immediately before mutation. It does not execute project commands, create a Plan, spawn or dispatch Agents, or leave a target runtime or package-resolution requirement.

A fresh target receives Markdown authority, Plan templates/directories, deterministic static runbooks for eligible records, and at most an exact root `CLAUDE.md` containing `@AGENTS.md` plus one trailing newline. It receives none of the retired Reporivet target artifacts described above. Package absence after setup is expected and is not `UNKNOWN`, blocking, or a residual risk.

`reporivet init --root "$ROOT"` is the structure-only, non-overwriting create-if-missing path. It does not perform the guided interview or create a Plan. The Main host/project procedure, not Reporivet, creates or resumes the first ordinary Markdown Plan.

## Lower-level definition interface

`define` remains available when a maintainer needs the visible resumable definition flow directly:

```bash
reporivet define start --root "$ROOT"
reporivet define resume --root "$ROOT"
reporivet define resume --root "$ROOT" --answers /absolute/path/to/answers.json
reporivet define status --root "$ROOT"
reporivet define finalize --root "$ROOT"
```

The visible Markdown draft is the only resume state. Each topic keeps **Confirmed**, **Proposed**, **Open**, and **Sources** separate. No answer is inferred or rewritten into authority. Finalization produces only the approved document and static-runbook preview; it does not generate a target Skill or execute a procedure.

## Package CLI

| Command | Purpose | Mutation boundary |
| --- | --- | --- |
| `reporivet setup` | Default integrated audit, guided definition, exact preview, and approved one-shot setup. | Writes only after explicit approval and safety revalidation; never creates a Plan or executes project commands. |
| `reporivet init` | Structure-only, non-overwriting create-if-missing bundle. | Preserves existing project-owned content and does not run guided setup or create a Plan. |
| `reporivet define start/resume/status/finalize` | Lower-level visible guided definition and exact preview/apply. | Writes only documented draft steps and approved bounded setup paths. |
| `reporivet audit` | Deterministic package-side repository inventory. | Read-only; it does not execute project commands. |
| `reporivet upgrade` | Maintain missing current bundle paths during package-side maintenance. | Refuses recognized legacy 0.2 surfaces rather than guessing ownership. |
| `reporivet migrate` | Preview, apply, or roll back a recognized legacy 0.2 transaction. | Requires exact approval and an external backup for destructive apply. |

`reporivet doctor` is retired; there is no ongoing Reporivet diagnosis contract. Use project-owned checks for target verification. The installed `reporivet <command>` and `PYTHONPATH=src "$PYTHON" -m reporivet <command>` forms are setup-time or contributor-only package operations, not post-setup target requirements.

## Main / Task Owner / Implementation Sub / Verification Sub

- **Main** owns intent, scope, non-goals, acceptance, the overall task tree, integration, decisions, candidate identity, evidence judgment, and every serialized Plan edit. Main uses host-native Agent dispatch; Reporivet does not spawn or dispatch Agents.
- **Task Owner** is the default role for every broad or multi-part root and has `May delegate: yes`. The Owner first returns a finite child manifest inside its approved envelope; Main serializes accepted child rows and complete matching packets into the Plan, then resumes that serialized Owner. Only the resumed serialized Task Owner dispatches its declared dependency-ready descendants through host-native Agent execution.
- **Implementation Sub** receives one bounded Task Packet with exact reads, allowed writes, protected paths, project-owned checks, acceptance criteria, and stop conditions. Narrow or inherently serial roots remain direct nondelegating leaves, and ordinary leaf Agents never delegate, broaden scope, or approve their own work.
- **Verification Sub** starts from a fresh context, identifies the integrated candidate, runs applicable project-owned checks, and returns criterion-level results and residual risks. Read-only verification leaves may run in parallel, never delegate, and depend on the integrated candidate; they do not repair it unless Main dispatches a separate implementation task.

For every broad or multi-part root, this is a common host/project rule:

`T<n> (broad root Owner) -> T<n>-A/B/C/... (declared child packets, all ready leaves dispatched concurrently) -> T<n>-I (Owner-local aggregation) -> T<n>-V1/V2/... (parallel fresh verification)`

Main dispatches independent root Owners concurrently. Every child task retains its owner, state, dependencies, outcome, result, and matching bounded packet. Parallel mutable siblings require disjoint allowed-write sets, frozen shared interfaces, and separate exact-baseline worktrees. Owner-local aggregation is distinct from Main's final repository integration; fresh verification follows the integrated candidate and is read-only, nonrepairing, and nondelegating. Main alone serializes Plan edits and manually moves a terminal Plan to `completed/`; no command decides completion.

This is a host/project operating contract, not a Reporivet runtime. Reporivet installs no Agent spawn/dispatch mechanism, command runner, CI/deployment system, scheduler, dispatcher, task store, lease, lock, Gate, evidence archive, hidden state, or automatic closure.

## Explicit legacy transition, backup, and rollback

An ordinary fresh setup does not silently remove legacy artifacts. An owner may explicitly rerun setup against an existing target. Cleanup or conversion is allowed only for paths proven to be exact Reporivet-owned bytes or exact strict parse-and-rerender matches. Modified, project-owned, ambiguous, unknown, unsafe, symlinked, and nonregular paths are preserved or refused.

Destructive actions require a complete visible preview, explicit approval, an absolute external backup bound into the preview fingerprint, immediate preimage revalidation, and transaction rollback after a safe failure. Later rollback uses the external manifest and refuses if a successful postimage has changed. No recursive `.claude` deletion is used; only transaction-proven empty child directories may be removed.

The historical `migrate --from 0.2` interface remains a separate package-side transition for recognized legacy surfaces:

```bash
BACKUP_DIR=/absolute/path/outside/target/reporivet-backup

PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --root "$ROOT" \
  --from 0.2 \
  --preview \
  --backup-dir "$BACKUP_DIR"
```

Review every action and approve only the emitted fingerprint:

```bash
MIGRATION_PREVIEW_SHA256='paste-the-emitted-sha256'

PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --root "$ROOT" \
  --from 0.2 \
  --apply \
  --approve-preview "$MIGRATION_PREVIEW_SHA256" \
  --backup-dir "$BACKUP_DIR"
```

Rollback accepts the exact external manifest:

```bash
PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --rollback /absolute/path/to/external-backup/manifest.json
```

## Project checks

Select the interpreter and external bytecode cache as shown above, then run project-owned checks:

```bash
PYTHONPATH=src "$PYTHON" -m unittest discover -s tests -v
PYTHONPATH=src "$PYTHON" -m compileall -q src tests
git diff --check
```

These checks are contributor/source-checkout commands. A fresh Verification Sub runs applicable project-owned checks against one identifiable integrated candidate; Reporivet does not execute them. Artifact build and release checks are environment-dependent and are not established by these source commands. [`docs/QUALITY.md`](docs/QUALITY.md) is authoritative for evidence; [`docs/OPERATIONS.md`](docs/OPERATIONS.md) is authoritative for running and release boundaries.

## Non-goals

Reporivet is not:

- a general orchestration platform, scheduler, task service, or hidden state store;
- a replacement for project build, test, CI, release, deployment, observability, backup, recovery, or incident systems;
- a copied multi-host prompt, executor, model, judge, or target Skill bundle;
- an authority that infers project facts or turns scanner observations into approved requirements;
- a guarantee that host deny rules form a sandbox;
- evidence of a release, installation, artifact, publication, or deployment that was not directly verified; or
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
- Current decision/specification/design: ADR-0002, SPEC-REPORIVET-004, and DESIGN-REPORIVET-004
