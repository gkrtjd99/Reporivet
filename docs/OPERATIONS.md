---
owner: operations
status: active
last_reviewed: 2026-08-31
---

# Operations

## Operating model

This is the sole current authority for running, releasing, observing, backup, rollback, recovery, and incidents for Reporivet. Reporivet is currently a local Python CLI/package, not a documented deployed service. The repository contains no confirmed production topology, daemon, database, scheduled job, service-level objective, or remote control plane.

Project-owned quality checks live in [`QUALITY.md`](QUALITY.md). Security boundaries and reporting live in [`SECURITY.md`](SECURITY.md). Procedure-specific runbooks, if later confirmed, remain indexed under [`runbooks/`](runbooks/) and subordinate to this file.

## Procedure requirements

Every executable procedure must name its owner, prerequisites, exact command, expected evidence, stop conditions, sensitive-data boundary, and rollback or recovery path. Keep unavailable facts Open, use project-owned tools, and require explicit authority before any external or irreversible action.

Reporivet does not spawn or dispatch Agents, execute project commands, operate CI/deployment, or provide a scheduler, task database, Gate, evidence archive, hidden state, or automatic closure. Those responsibilities stay with the host and project.

## Installation and onboarding

Public installation guidance is pipx-primary:

```bash
pipx install reporivet
```

Pip is supported from the same wheel:

```bash
python -m pip install reporivet
```

The default onboarding command is integrated `reporivet setup`. It coordinates audit, visible guided definition, exact preview, and approved apply. `reporivet init` is structure-only; lower-level `reporivet define` remains available. Setup creates no Plan or runtime. Main Skill creates or resumes the first ordinary Markdown Plan, and complete user-confirmed structured procedures may create instruction-only project Skills only through resumed setup.

Completed PLAN-2026-0003 records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive. Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside scope.

## Required operational knowledge

### Running

Select Python 3.11 or newer explicitly:

```bash
PYTHON=/absolute/path/to/python3.11-or-newer
"$PYTHON" --version
```

Contributors only may run the package from a source checkout without installing it:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/reporivet-pycache" \
PYTHONPATH=src \
"$PYTHON" -m reporivet --help
```

If an independently verified installation already supplies the console script, the equivalent entry point is:

```bash
reporivet --help
```

The source-checkout form is contributor-only. Public users should use the pipx-primary or pip-from-the-same-wheel forms above. The exact candidate and wheel lifecycle is recorded in the completed Plan above; its verification artifacts are temporary and are not a durable or downloadable evidence archive.

### Read-only inventory and diagnosis

```bash
PYTHONPATH=src "$PYTHON" -m reporivet audit --root /absolute/path/to/target
PYTHONPATH=src "$PYTHON" -m reporivet doctor --root /absolute/path/to/target
```

`audit` inventories relevant repository paths without executing project commands or writing target files. `doctor` reports document-first structural findings without repairing them.

### Default integrated setup

Use an installed Reporivet for normal project onboarding:

```bash
reporivet setup --root /absolute/path/to/target
```

`setup` performs one deterministic audit, presents the visible seven-topic definition, reports actual Open items, resumes user answers, renders the exact preview, and applies only after explicit approval and revalidation. It does not execute project commands, spawn or dispatch Agents, or create a Plan. A complete user-confirmed structured procedure can render one deterministic instruction-only project Skill through resumed setup; incomplete, inferred, generic, Proposed, Open, and Sources-only records render none.

`reporivet init --root /absolute/path/to/target` is the structure-only, non-overwriting create-if-missing entry point. `reporivet define` remains the lower-level direct draft/resume/status/finalize interface. `upgrade` maintains missing current bundle paths but refuses recognized legacy 0.2 surfaces and routes that case to the explicit migration transaction.

The Main Skill, not Reporivet, searches active and completed history, resumes one matching active ordinary Markdown Plan, or creates the first Plan with the lowest unused current-year ID from the project template. Reporivet creates no Plan or target runtime.

Optional deny-only Claude settings are included only when the same `--with-claude-settings` flag is present during both preview and approved apply. Do not use that option when `.claude/settings.json` already exists; Reporivet refuses to merge or rewrite it.

### Lower-level definition procedure

Contributors or maintainers needing direct control may use the installed command:

```bash
reporivet define start --root /absolute/path/to/target
reporivet define resume --root /absolute/path/to/target --answers /absolute/path/to/answers.json
reporivet define status --root /absolute/path/to/target
reporivet define finalize --root /absolute/path/to/target
```

### Release boundary

Reporivet does not publish, sign, or release packages. Release ownership remains with the project maintainer and any release action requires separate authority. A release candidate requires:

1. an explicitly selected version and candidate commit;
2. current product, architecture, quality, operations, security, and public README content;
3. passing required checks from [`QUALITY.md`](QUALITY.md);
4. artifact checks in an environment with the declared build backend available;
5. explicit authorization for any tag, push, upload, publication, or announcement.

Current repository evidence establishes source behavior and records the exact wheel lifecycle for source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` with wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4`. That lifecycle is not evidence of a published release, package index state, signing, deployment, or CI repair/readiness. The verification artifacts are temporary and are not a durable or downloadable evidence archive. The removal contract is that generated Markdown, Plans, Skills, Git, and project commands remain useful after uninstall; that contract is not itself publication or release evidence. No external release action is implied by a passing source suite.

### Observing

The CLI is synchronous and local:

- normal reports and previews are written to standard output;
- actionable errors are written to standard error and return a nonzero exit status;
- doctor findings are the current structural health signal;
- test output and exact command exit status are the current behavioral evidence;
- migration output identifies preview actions, approval fingerprint, backup, and manifest information needed for the transaction.

There is no confirmed service telemetry, uptime monitor, dashboard, alert route, or production log store. Do not invent those procedures. Avoid copying secrets or sensitive repository content into Plan summaries, bug reports, or public logs.

### 0.2 migration: preview and backup

Migration is an explicit package-side transaction for recognized legacy 0.2 surfaces. Choose an absolute backup directory outside the target repository. The path and its manifest are sensitive.

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

Before mutation, apply revalidates the approved preview and target fingerprints. The transaction creates a mode-restricted external backup and manifest. It preserves project-owned or customized paths, retains historical sensitive state without reading its contents, and stops on unsafe or ambiguous targets.

This backup covers only the paths owned by the migration transaction. It is not a general repository, database, credential, or production backup.

### Rollback

Use the exact manifest emitted by a successful migration:

```bash
PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --rollback /absolute/path/to/external-backup/manifest.json
```

Rollback accepts only the manifest path. It validates the manifest, backup contents, target root, and current applied fingerprints. If a user changed an applied path after migration, rollback refuses rather than overwrite that later work.

Keep the external backup until the migrated candidate has passed project checks and the maintainer has accepted the result. Backup deletion is a separate maintainer decision and is not performed by the rollback command.

### Recovery

For a failed apply:

1. stop further writes to the target;
2. retain the exact command, standard output, standard error, preview fingerprint, backup path, and manifest path if one was emitted;
3. allow the built-in failed-apply restoration to finish; it restores the pre-migration state when that can be done safely;
4. run read-only `doctor` and inspect repository status;
5. do not retry apply until the cause, target fingerprints, and backup location are understood;
6. render and approve a new preview after any repository change.

For an interrupted or ambiguous transaction, do not guess which files are authoritative. Preserve the target and external backup, gather read-only diagnosis, and escalate with the exact manifest and path findings. This repository has no confirmed broader disaster-recovery procedure because it has no documented production service or persistent application data.

### Incidents

Treat unexpected mutation, suspected path escape, secret exposure, corrupt backup, unsafe rollback refusal, or inconsistent preview/apply state as an incident.

1. Stop mutating commands and preserve local evidence without copying sensitive file contents into public channels.
2. Record the exact package version, command, target path, exit status, and relevant manifest or fingerprint identifiers.
3. Use read-only audit, doctor, Git status, and project-owned checks to bound impact.
4. For a vulnerability or suspected exploit, follow [`.github/SECURITY.md`](../.github/SECURITY.md) and use private reporting.
5. For a non-security defect, report the smallest reproducible facts through the repository issue route when authorized.
6. Resume mutation only after a maintainer chooses recovery or rollback based on current fingerprints.

No on-call rotation, response-time promise, support escalation service, or production incident channel is currently confirmed.

## Current CI caveat

The retained `.github/workflows/ci.yml` does not match the current direct-command authority and must not be treated as completion or release evidence until separately repaired and verified. Reporivet does not generate or rewrite project-owned CI.

### Confirmed

- Source-checkout CLI operation, read-only audit, doctor, guided definition, and explicit migration are implemented.
- Migration requires an external backup for preview and apply, fingerprints the approved transaction, and refuses rollback over later user changes.
- Reporivet is currently documented as a local CLI/package, not a deployed service.
- Source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive.

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
- [`product-specs/SPEC-REPORIVET-003-document-first-harness.md`](product-specs/SPEC-REPORIVET-003-document-first-harness.md)
- [`design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](design-docs/DESIGN-REPORIVET-003-document-first-harness.md)
- [`../pyproject.toml`](../pyproject.toml)
