---
owner: quality
status: active
last_reviewed: 2026-09-02
---

# Quality

## Required checks and commands

This file is the sole current authority for Reporivet's project-owned local checks and acceptance evidence. Commands run directly through Git and a selected Python 3.11-or-newer interpreter; no repository wrapper or retained configuration file is an execution authority. Reporivet does not execute project commands or CI; a project and its host own that execution.

Public installation guidance is for setup-time use: pipx is primary (`pipx install reporivet`), with pip supported from the same wheel (`python -m pip install reporivet`). Completed PLAN-2026-0003 records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive; this package lifecycle record does not make Reporivet a target dependency after setup.

Set `PYTHON` explicitly before running checks:

```bash
PYTHON=/absolute/path/to/python3.11-or-newer
"$PYTHON" --version
```

Use an external bytecode cache so validation does not create repository state:

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/reporivet-pycache"
export PYTHONPATH=src
```

## Contributor-only source checks

The following commands are for contributors working from a source checkout. They are not the public installation or artifact-readiness path, and they are not commands that Reporivet runs on a target.

### Unit and integration behavior

```bash
"$PYTHON" -m unittest discover -s tests -v
```

The suite covers root and path safety, deterministic audit, guided setup, package-data boundaries, compact Plan lifecycle, migration transactions, CLI behavior, static runbook rendering, and document usefulness after package removal.

### Syntax and import surface

```bash
"$PYTHON" -m compileall -q src tests
```

This checks the source checkout's own import surface. Generated target documents do not import the package.

### Distribution boundary

```bash
"$PYTHON" -m unittest tests.test_distribution -v
```

This focused check asserts the expected package-data inventory, absence of retired copied execution and target-Skill assets, current adapter bytes, compact Plan template, static runbook boundary, and a document-first repository that remains useful after package removal.

### One-shot setup and static-runbook evidence

For setup or target-surface changes, inspect a temporary target through the project-owned tests and setup preview. Confirm that a fresh target contains the canonical documents, Plan directories/templates, static runbooks, and at most the exact `CLAUDE.md` adapter, and does not contain target Skills, `.reporivet-version`, generated settings, a runtime, a doctor gate, or package-resolution instructions.

A runbook is eligible only for one complete, unique, user-confirmed strict nine-field record. Its ordinary Markdown output is `docs/runbooks/<slug>.md`; it has no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration. Incomplete, malformed, generic, inferred, Proposed, Open, Sources-only, and duplicate records must produce no runbook.

### Retired diagnosis boundary

There is no current `reporivet doctor` command. Setup validates only its own exact approved transaction and postconditions. Do not replace the retired command with another Reporivet diagnosis or command runner, and do not treat package absence after setup as `UNKNOWN`, blocking, or a residual risk. Project-owned checks remain the verification boundary for the generated target.

### Patch hygiene

```bash
git diff --check
```

For a bounded task, also inspect `git status --short` and the final changed-path list so protected and unrelated files are not accidentally included.

## Change-specific evidence

| Change | Minimum additional evidence |
| --- | --- |
| CLI arguments or output | Exercise the affected package-side command and relevant error path using the selected interpreter. |
| Root/path safety or mutation | Run the focused safety tests plus the full suite; use temporary repositories only. |
| Integrated setup or adapters | Verify one audit, actual Open-state reporting, exact preview/apply behavior, generated path inventory, preservation of existing content, no setup-created Plan, and package-independent handoff. |
| Static procedure runbooks | Verify complete unique Confirmed records alone render deterministic ordinary Markdown; unresolved, duplicate, malformed, or generic records render none and no command executes. |
| Plan lifecycle | Verify Main's first-Plan resume/create behavior, compact frontmatter, required headings, state consistency, candidate identity, manual terminal movement, broad-root Task Owner checkpoints, and direct serial compatibility. |
| Legacy transition | Verify exact ownership proof, preview approval, external backup binding, path safety, preimage revalidation, failed-apply restoration, guarded later rollback, and preservation of modified, ambiguous, unsafe, symlinked, nonregular, and project-owned paths. |
| Current documentation or templates | Verify current authority links, static runbook wording, bilingual claim parity when public READMEs change, bounded retired-authority scan, full tests, and `git diff --check`; for hierarchy changes, confirm broad or multi-part roots default to `Role: Task Owner`/`May delegate: yes`, finite manifest-to-Main-serialization-to-Owner-resume checkpoints, disjoint sibling writes, Owner-local aggregation distinct from Main integration, and fresh read-only verification without a Reporivet runtime claim. |
| Security-sensitive behavior | Apply [`SECURITY.md`](SECURITY.md), inspect exact paths and permissions, and record residual threats. |

Main defines the applicable target in the active Plan. A fresh Verification Sub runs the checks against the identifiable integrated candidate and reports each acceptance criterion as accepted, failed, or not established.

## Evidence contract

- A passing command is evidence only for the exact candidate and environment where it ran.
- Implementation narration, previous-task output, and a clean-looking diff are not substitutes for independent checks.
- Record the command, exit status, relevant result, candidate identity, and residual risks in the active Plan.
- Distinguish not run, unavailable, and failed. Do not report any of them as passing.
- Do not weaken a test or acceptance criterion merely to make the candidate pass.
- Historical artifacts are not current evidence for a later candidate.
- Package installation checks establish setup-time distribution only; they do not establish a continuing package requirement for a generated target.

## Quality gaps

Building a wheel requires the declared Setuptools backend to be available in the selected environment. When release preparation explicitly requires a local artifact and the backend is available, the source-tree wheel check is:

```bash
WHEEL_DIR="$(mktemp -d)"
"$PYTHON" -m pip wheel . \
  --no-build-isolation \
  --no-deps \
  --no-index \
  --wheel-dir "$WHEEL_DIR"
```

A successful source check does not by itself establish wheel installation, uninstall, publication, or deployment. For this candidate, completed PLAN-2026-0003 records the exact wheel lifecycle described above. The verification artifacts are temporary and are not a durable or downloadable evidence archive. Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside this documentation-only scope. Do not substitute a networked build or publication action without explicit authorization.

## CI status

The checked-in `.github/workflows/ci.yml` is project-owned and retained, but its current commands do not match this document-first authority. Until separately repaired and verified, its result is not accepted as current completion evidence. Reporivet does not generate or rewrite project CI.

### Confirmed

- Python 3.11 or newer is the supported interpreter boundary.
- The full source test suite and compile check run without production dependencies.
- Setup preview/apply and patch-hygiene checks are read-only until explicit approval and remain bounded to their declared transaction.
- Source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive; the record is setup-time package evidence only.
- Package absence after approved setup is expected; project-owned checks remain useful without the package.

### Proposed

- None.

### Open

- Durable evidence archival is not provided; the recorded lifecycle verification artifacts are temporary and are not a durable or downloadable archive.
- Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside Reporivet.
- Project-owned CI requires separate repair outside this documentation-only change.

### Sources

- [`../pyproject.toml`](../pyproject.toml)
- [`../tests/`](../tests/)
- [`product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md`](product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md)
- [`design-docs/DESIGN-REPORIVET-004-one-shot-setup.md`](design-docs/DESIGN-REPORIVET-004-one-shot-setup.md)
- [`decisions/ADR-0002-one-shot-bootstrapper-boundary.md`](decisions/ADR-0002-one-shot-bootstrapper-boundary.md)
- [`product-specs/SPEC-REPORIVET-003-document-first-harness.md`](product-specs/SPEC-REPORIVET-003-document-first-harness.md) (historical)
- [`design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](design-docs/DESIGN-REPORIVET-003-document-first-harness.md) (historical)
