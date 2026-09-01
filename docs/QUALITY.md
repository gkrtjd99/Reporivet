---
owner: quality
status: active
last_reviewed: 2026-08-31
---

# Quality

## Required checks and commands

This file is the sole current authority for Reporivet's project-owned local checks and acceptance evidence. Commands run directly through Git and a selected Python 3.11-or-newer interpreter; no repository wrapper or retained configuration file is an execution authority. Reporivet does not execute project commands or CI; a project/host owns that execution.

Public installation guidance is pipx-primary (`pipx install reporivet`), with pip supported from the same wheel (`python -m pip install reporivet`). Completed PLAN-2026-0003 records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive.

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

The following commands are for contributors working from a source checkout. They are not the public installation or artifact-readiness path.

### Unit and integration behavior

```bash
"$PYTHON" -m unittest discover -s tests -v
```

The suite covers root and path safety, deterministic audit, guided setup, Claude adapters, package-data boundaries, compact Plan lifecycle, migration transactions, CLI behavior, and document usefulness after package removal.

### Syntax and import surface

```bash
"$PYTHON" -m compileall -q src tests
```

### Distribution boundary

```bash
"$PYTHON" -m unittest tests.test_distribution -v
```

This focused check asserts the expected package-data inventory, absence of retired copied execution assets, current adapter bytes, compact Plan template, and a document-first repository that remains useful after package removal.

### Repository diagnosis

```bash
"$PYTHON" -m reporivet doctor --root .
```

Doctor is read-only. Findings must be resolved or reported; do not weaken structural rules to obtain a passing result.

### Patch hygiene

```bash
git diff --check
```

For a bounded task, also inspect `git status --short` and the final changed-path list so protected and unrelated files are not accidentally included.

## Change-specific evidence

| Change | Minimum additional evidence |
| --- | --- |
| CLI arguments or output | Exercise the affected command and relevant error path using the selected interpreter. |
| Root/path safety or mutation | Run the focused safety tests plus the full suite; use temporary repositories only. |
| Integrated setup or adapters | Verify one audit, actual Open-state reporting, exact preview/apply behavior, generated path inventory, preservation of existing content, and no setup-created Plan. |
| Confirmed procedure Skills | Verify complete structured Confirmed records alone render deterministic instruction-only Skills; unresolved or generic records render none and no command executes. |
| Plan lifecycle | Verify Main Skill first-Plan resume/create behavior, compact frontmatter, required headings, state consistency, candidate identity, and manual terminal movement rules. |
| Migration | Verify preview/apply/rollback, external backup, fingerprint revalidation, failed-apply restoration, and refusal after later user changes. |
| Current documentation or templates | Run doctor, link resolution, bilingual claim parity when public READMEs change, bounded retired-authority scan, full tests, and `git diff --check`. |
| Security-sensitive behavior | Apply [`SECURITY.md`](SECURITY.md), inspect exact paths and permissions, and record residual threats. |

Main defines the applicable target in the Plan. A fresh Verification Sub runs the checks against the identifiable integrated candidate and reports each acceptance criterion as accepted, failed, or not established.

## Evidence contract

- A passing command is evidence only for the exact candidate and environment where it ran.
- Implementation narration, previous-task output, and a clean-looking diff are not substitutes for independent checks.
- Record the command, exit status, relevant result, candidate identity, and residual risks in the active Plan.
- Distinguish not run, unavailable, and failed. Do not report any of them as passing.
- Do not weaken a test, doctor rule, or acceptance criterion merely to make the candidate pass.
- Historical artifacts are not current evidence for a later candidate.

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
- Doctor and patch-hygiene checks are read-only with respect to project content.
- Source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive.

### Proposed

- None.

### Open

- Durable evidence archival is not provided; the recorded lifecycle verification artifacts are temporary and are not a durable or downloadable archive.
- Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside Reporivet.
- Project-owned CI requires separate repair outside this documentation-only change.

### Sources

- [`../pyproject.toml`](../pyproject.toml)
- [`../tests/`](../tests/)
- [`product-specs/SPEC-REPORIVET-003-document-first-harness.md`](product-specs/SPEC-REPORIVET-003-document-first-harness.md)
- [`design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](design-docs/DESIGN-REPORIVET-003-document-first-harness.md)
