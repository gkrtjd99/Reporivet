---
owner: operations
status: active
last_reviewed: 2026-09-02
---

# Operations

## Operating model

This is the sole current authority for running, releasing, observing, backup, rollback, recovery, and incidents for Reporivet. Reporivet is a local Python CLI/package used during explicit package-side setup or transition, not a deployed service. The repository contains no confirmed production topology, daemon, database, scheduled job, service-level objective, or remote control plane.

Project-owned quality checks live in [`QUALITY.md`](QUALITY.md). Security boundaries and reporting live in [`SECURITY.md`](SECURITY.md). Procedure-specific output, when required, is an ordinary static runbook under [`runbooks/`](runbooks/) and is subordinate to this file.

Setup is a bounded one-shot transaction. After approved handoff, the target owns its documents, Plans, runbooks, commands, tests, CI, deployment, operations, secrets, Git, and evidence. Removing the package is expected and does not reduce ordinary project work. Reporivet does not provide a continuing target runtime, diagnosis command, command runner, or project-command execution service.

## Conditional reliability guidance

`RELIABILITY.md` appears only when the visible definition draft contains exactly `deployed_runtime=yes` in **Confirmed**. It is a project-owned, ordinary Markdown supplement for service/runtime failure modes, SLI/SLO, observability, deployment/rollback, recovery, and incident boundaries. It is subordinate to this document: `OPERATIONS.md` remains the universal authority for running, releasing, observing, backup, rollback, recovery, and incidents, and its procedures and approvals cannot be replaced by the supplement.

`FRONTEND.md`, when `web_ui=yes` is explicitly Confirmed, covers frontend implementation and client-side loading/error/retry behavior only; it is not service reliability authority. Missing, `no`, Proposed, Open, Sources-only, inferred, or unverified capability values create no optional file. Audit observations and provenance do not establish confirmation, and setup selection is not Plan state or operational evidence.

Reliability statements require an accountable project owner, an attributable source, the applicable environment and candidate or time range, and direct project-owned evidence. Keep unavailable or uncertain topology, SLI/SLO, telemetry, deployment, recovery, and incident facts Open or Proposed rather than inventing them. `QUALITY.md` remains the route for project checks; record exact operational observations and results in the active Plan or applicable runbook.

## Procedure requirements

Every project-owned executable procedure must name its owner, prerequisites, exact command, expected evidence, stop conditions, sensitive-data boundary, and rollback or recovery path. Keep unavailable facts Open, use project-owned tools, and require explicit authority before any external or irreversible action.

A Reporivet static runbook is descriptive documentation, not an executor. It is rendered only from one complete, unique, user-confirmed strict structured record with exactly these nine fields: `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, and `rollback`. Its output is ordinary Markdown at `docs/runbooks/<slug>.md`, with no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration. Incomplete, malformed, generic, inferred, Proposed, Open, Sources-only, or duplicate records render no runbook.

Reporivet does not spawn or dispatch Agents, execute project commands, operate CI/deployment, or provide a scheduler, task database, Gate, evidence archive, hidden state, or automatic closure. Those responsibilities stay with the host and project.

## Installation and one-shot onboarding

Public installation guidance is for invoking package-side setup or transition:

```bash
pipx install reporivet
```

Pip is supported from the same wheel:

```bash
python -m pip install reporivet
```

An explicitly selected local source is also valid for contributors. These installation forms are not a post-setup target requirement. Once setup has handed off the generated target, the package may be removed.

Completed PLAN-2026-0003 records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive. This is package lifecycle evidence, not evidence of a continuing target dependency. Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside scope.

## Required operational knowledge

### Running package-side commands

Select Python 3.11 or newer explicitly when running from a source checkout:

```bash
PYTHON=/absolute/path/to/python3.11-or-newer
"$PYTHON" --version
```

Contributors only may run package-side commands from a source checkout without installing it:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/reporivet-pycache" \
PYTHONPATH=src \
"$PYTHON" -m reporivet --help
```

If an independently verified installation supplies the console script, the equivalent entry point is:

```bash
reporivet --help
```

These commands operate the package-side setup surface only. They do not become commands that a generated target must run after handoff.

### Read-only inventory

```bash
PYTHONPATH=src "$PYTHON" -m reporivet audit --root /absolute/path/to/target
```

`audit` inventories relevant repository paths without executing project commands or writing target files. It is a package-side observation, not a continuing target health service. There is no current `reporivet doctor` command.

### Default integrated setup

Use an installed Reporivet, or an explicitly selected local source, for the one-shot setup transaction:

```bash
reporivet setup --root /absolute/path/to/target
```

`setup` performs a deterministic audit, presents the visible definition topics, reports actual Open items, resumes user answers, renders the exact preview, and applies only after explicit approval and immediate revalidation. It does not execute project commands, spawn or dispatch Agents, create a Plan, install a runtime, or leave a target package requirement.

A fresh target receives the project-owned Markdown authority, Plan templates/directories, deterministic static runbooks for eligible procedures, and at most an exact root `CLAUDE.md` adapter. It receives no Reporivet role or procedure Skill, `.reporivet-version`, generated `.claude/settings.json`, copied runtime, doctor gate, registry/package-resolution instruction, command wrapper, or hidden state.

Only a complete, unique, user-confirmed strict nine-field procedure record produces `docs/runbooks/<slug>.md`; the output has no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration. A project may add its own operational documents after handoff without Reporivet.

`reporivet init --root /absolute/path/to/target` is the structure-only, non-overwriting create-if-missing entry point. `reporivet define` remains the lower-level direct draft/resume/status/finalize interface. Setup and init create no Plan; the host/project Main procedure searches active and completed history and creates or resumes the first ordinary Markdown Plan when needed.

### Explicit setup rerun and legacy cleanup

An owner may explicitly rerun setup against an existing target. Cleanup or conversion of historical Reporivet role/procedure Skills, settings, markers, or managed blocks is considered only when exact canonical ownership evidence proves the package created the path. Exact canonical bytes or a strict parse-and-rerender proof are required; a name, marker, frontmatter, or location alone is insufficient.

Modified, unknown, ambiguous, project-owned, unsafe, symlinked, and nonregular paths are preserved or refused. Any destructive action is shown in an exact preview, bound to its complete fingerprint and an absolute external backup directory, and revalidated immediately before mutation. A failed apply restores the whole approved transaction when safe. Later rollback uses the external manifest and refuses if a successful postimage has changed.

No recursive `.claude` deletion is used. Only transaction-proven empty child directories may be removed. Backup manifests and rollback state remain outside the target, and package absence after setup is expected rather than a blocker or residual risk.

### Lower-level definition procedure

Contributors or maintainers needing direct control may use the package-side command:

```bash
reporivet define start --root /absolute/path/to/target
reporivet define resume --root /absolute/path/to/target --answers /absolute/path/to/answers.json
reporivet define status --root /absolute/path/to/target
reporivet define finalize --root /absolute/path/to/target
```

The visible Markdown draft is the only resume state. Each topic keeps **Confirmed**, **Proposed**, **Open**, and **Sources** separate. Finalization does not manufacture answers or create a target Skill; eligible procedures become static runbooks only through the approved setup transaction.

## Release boundary

Reporivet does not publish, sign, or release packages. Release ownership remains with the project maintainer and any release action requires separate authority. A release candidate requires:

1. an explicitly selected version and candidate commit;
2. current product, architecture, quality, operations, security, and public README content;
3. passing required checks from [`QUALITY.md`](QUALITY.md);
4. artifact checks in an environment with the declared build backend available; and
5. explicit authorization for any tag, push, upload, publication, or announcement.

Current repository evidence establishes source behavior and records the exact wheel lifecycle for source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` with wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4`. That lifecycle is not evidence of a published release, package index state, signing, deployment, or CI repair/readiness. The verification artifacts are temporary and are not a durable or downloadable evidence archive. No external release action is implied by a passing source suite.

### Observing

The package-side CLI is synchronous and local:

- normal reports and previews are written to standard output;
- actionable errors are written to standard error and return a nonzero exit status;
- audit output is a read-only package-side inventory;
- setup output identifies exact actions, approval fingerprint, preserved paths, and transaction results; and
- transition output identifies backup, manifest, rollback, and refusal information needed for the approved transaction.

There is no current Reporivet diagnosis or target health command. Project test output, Git status, and exact project-command exit status are the target's behavioral evidence. There is no confirmed service telemetry, uptime monitor, dashboard, alert route, or production log store. Do not invent those procedures. Avoid copying secrets or sensitive repository content into Plan summaries, bug reports, or public logs.

### 0.2 migration: preview and backup

The historical `reporivet migrate --from 0.2` command remains a separate explicit package-side transaction for recognized legacy 0.2 surfaces. Choose an absolute backup directory outside the target repository. The path and its manifest are sensitive.

Preview without mutating the target:

```bash
PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --root /absolute/path/to/target \
  --from 0.2 \
  --preview \
  --backup-dir /absolute/path/outside/target/reporivet-backup
```

Review every planned create, replace, retire, preserve, and refusal action. The preview emits the SHA-256 approval fingerprint. Do not approve a fingerprint from a different root, backup path, or repository state.

Apply the exact preview:

```bash
PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --root /absolute/path/to/target \
  --from 0.2 \
  --apply \
  --approve-preview <PREVIEW_SHA256> \
  --backup-dir /absolute/path/outside/target/reporivet-backup
```

Before mutation, apply revalidates the approved preview and target fingerprints. The transaction creates a mode-restricted external backup and manifest. It preserves project-owned or customized paths, retains historical sensitive state without reading its contents, and stops on unsafe or ambiguous targets. This backup covers only paths owned by the migration transaction; it is not a general repository, database, credential, or production backup.

### Rollback

Use the exact manifest emitted by a successful transition:

```bash
PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --rollback /absolute/path/to/external-backup/manifest.json
```

Rollback accepts only the manifest path. It validates the manifest, backup contents, target root, and current applied fingerprints. If a user changed an applied path after migration, rollback refuses rather than overwrite that later work.

Keep the external backup until the transitioned candidate has passed project checks and the maintainer has accepted it. Backup deletion is a separate maintainer decision and is not performed by the rollback command.

### Recovery

For a failed setup or transition apply:

1. stop further writes to the target;
2. retain the exact command, standard output, standard error, preview fingerprint, backup path, and manifest path if one was emitted;
3. allow the built-in failed-apply restoration to finish; it restores the approved preimage when that can be done safely;
4. run read-only `audit`, inspect repository status, and use project-owned checks;
5. do not retry apply until the cause, target fingerprints, and backup location are understood; and
6. render and approve a new preview after any repository change.

For an interrupted or ambiguous transaction, do not guess which files are authoritative. Preserve the target and external backup, gather read-only inventory, and escalate with exact manifest and path findings. This repository has no confirmed broader disaster-recovery procedure because it has no documented production service or persistent application data.

### Incidents

Treat unexpected mutation, suspected path escape, secret exposure, corrupt backup, unsafe rollback refusal, or inconsistent preview/apply state as an incident.

1. Stop mutating commands and preserve local evidence without copying sensitive file contents into public channels.
2. Record the exact package version, command, target path, exit status, and relevant manifest or fingerprint identifiers.
3. Use read-only audit, Git status, and project-owned checks to bound impact.
4. For a vulnerability or suspected exploit, follow [`.github/SECURITY.md`](../.github/SECURITY.md) and use private reporting.
5. For a non-security defect, report the smallest reproducible facts through the repository issue route when authorized.
6. Resume mutation only after a maintainer chooses recovery or rollback based on current fingerprints.

No on-call rotation, response-time promise, support escalation service, or production incident channel is currently confirmed.

## Current CI caveat

The retained `.github/workflows/ci.yml` does not match the current direct-command authority and must not be treated as completion or release evidence until separately repaired and verified. Reporivet does not generate or rewrite project-owned CI.

### Confirmed

- Source-checkout CLI operation, read-only audit, guided definition, one-shot setup, and explicit transition transactions are implemented within the package-side boundary.
- Setup and transition operations require exact previews, external backups for destructive actions, fingerprints, immediate revalidation, and guarded rollback.
- Reporivet is currently documented as a local CLI/package used during setup or transition, not a deployed service or target runtime.
- Source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive; this is setup-time package evidence only.
- Package absence after approved setup is expected; target documents, Plans, runbooks, Git, and project-owned checks remain useful without the package.

### Proposed

- None.

### Open

- Durable evidence archival is not provided; the recorded lifecycle verification artifacts are temporary and are not a durable or downloadable archive.
- Release tagging, changelog, publication, signing, provenance, deployment, and CI repair/readiness remain outside Reporivet and unestablished.
- Deployment, service observation, database backup, service recovery objectives, on-call ownership, and incident response targets are not applicable or remain undefined until a deployed surface is introduced.
- Project-owned CI requires separate repair outside this documentation-only change.

### Sources

- [`QUALITY.md`](QUALITY.md)
- [`SECURITY.md`](SECURITY.md)
- [`../docs/decisions/ADR-0002-one-shot-bootstrapper-boundary.md`](../docs/decisions/ADR-0002-one-shot-bootstrapper-boundary.md)
- [`../docs/product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md`](../docs/product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md)
- [`../docs/design-docs/DESIGN-REPORIVET-004-one-shot-setup.md`](../docs/design-docs/DESIGN-REPORIVET-004-one-shot-setup.md)
- [`../docs/product-specs/SPEC-REPORIVET-003-document-first-harness.md`](../docs/product-specs/SPEC-REPORIVET-003-document-first-harness.md) (historical)
- [`../docs/design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](../docs/design-docs/DESIGN-REPORIVET-003-document-first-harness.md) (historical)
- [`../pyproject.toml`](../pyproject.toml)
