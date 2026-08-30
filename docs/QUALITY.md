---
id: QUALITY
kind: quality
status: active
area: repository
summary: Current quality model, verification statuses, Gate policy, release checks, and residual risks
applies_to:
  - "**"
---

# Quality

## Quality model

Quality means a repository is changed safely, remains understandable after sessions and package installation state change, fails visibly when required evidence is unavailable, preserves inspectable artifacts for non-green outcomes, and can be upgraded without losing project-owned knowledge.

## Verification layers

| Layer | Purpose | Canonical command | Evidence |
|---|---|---|---|
| Syntax | Compile Python sources and tests | `python3 -m compileall -q src tests` | Zero exit status |
| Regression | Exercise initializer and copied runtime end to end | `python3 -m unittest discover -s tests -v` | Full unit/integration/regression result |
| Repository fast feedback | Structural checks plus configured fast commands | `./dev/check` | Catalog, document, plan, architecture preflight, and project output |
| Completion gate | One fixed shared Verification Run | `./dev/verify` | `.harness/runs/<run>-verify/` manifest, Gate, report, checks, and logs |
| Distribution | Build/install/uninstall the wheel and exercise generated projects | Distribution regression and release procedure | Complete asset inventory and package-independent operation |

## Verification Run status

One canonical run executes security, docs-index, documentation, plan, architecture, project, and optional smoke checks in that order. Each check records one of:

- `pass`: the declared check completed successfully.
- `fail`: candidate behavior did not satisfy a required check.
- `error`: the check could not produce reliable evidence because of configuration or infrastructure.
- `skipped`: an optional check was correctly not configured.
- `unknown`: evidence could not be determined and must not be treated as pass.

A required `fail` determines verification failure even when another required stage errors. Otherwise a required `error` or `unknown` determines an error outcome. Optional smoke may be `skipped`; malformed configured smoke is a required error. Artifacts are finalized as far as possible for all outcomes.

## Gate semantics

Changed paths use `contained`, `wide`, `irreversible`, or `unknown` risk. Verdict priority is:

1. Required check failure: `BLOCK`.
2. Required error/unknown, malformed Gate policy, or target mismatch/error: `INCONCLUSIVE`.
3. Protected, unknown, wide, irreversible, or policy-required dirty state: `REVIEW`.
4. Clean explicit contained target with all required checks passing: `PASS`.

In shadow mode, deterministic `PASS` and `REVIEW` return zero; `BLOCK` returns one and `INCONCLUSIVE` returns two. In enforce mode, only `PASS` returns zero. A REVIEW verdict is evidence for human judgment, not an automatic approval.

## Test ownership

Focused modules own distinct behavior:

- `tests/test_reporivet.py`: initialization, ownership, wrappers, doctor, CI, security integration, and upgrades.
- `tests/test_definition.py`: definition start, resume, validation, finalization, and rollback.
- `tests/test_audit_adoption.py`: deterministic read-only audit, authority-preserving adoption, path safety, and rollback.
- `tests/test_traceability.py`: product/spec/plan/task/evidence links and legacy-plan compatibility.
- `tests/test_code_map.py`: justified contracts, deterministic maps, drift, and context routing.
- `tests/test_verification_run.py`: fixed stages, statuses, artifacts, target evidence, recursion rejection, and Gate matrix.
- `tests/test_gate_close_plan.py`: PASS/REVIEW/BLOCK/INCONCLUSIVE closure, one-run binding, path safety, and transaction recovery.
- `tests/test_distribution.py`: wheel inventory, isolated install, generated verify/doctor, uninstall, repository-local commands, and closure.

## Review expectations

Changes to ownership, replacement behavior, path handling, command execution, parsing, target evidence, Gate policy, closure, packaged assets, or CI require regression tests and an independent context that attempts to falsify the acceptance claim. Explanations without commands or artifacts are not evidence.

## Local 0.2.0 release gate

1. Compile source and tests and run the full regression suite.
2. Run strict security, catalog, documentation, plan, architecture, and repository checks.
3. Build a `0.2.0` wheel with no build isolation, dependency resolution, or network access.
4. Confirm every package asset is present and bytecode, cache, Skill, target bundle, model, and daemon surfaces are absent.
5. Install the local wheel into a fresh virtual environment without an index.
6. Run installed CLI help, fresh initialization/definition/audit, generated verification, and initializer doctor.
7. Uninstall Reporivet and rerun repository-local definition, audit, context, planning, checks, verification, closure, and gardening fixtures.
8. Independently review the exact clean candidate and run one final canonical Verification Run with explicit base/head/target evidence.

This is a local release-ready boundary only. It does not publish a wheel or create a GitHub release.

## Known gaps

- Generated wrappers are POSIX shell scripts; Windows-native wrappers are not covered.
- Frontmatter and Markdown parsing intentionally supports the committed schema rather than arbitrary YAML/Markdown.
- Structural evidence does not replace semantic product, architecture, security, or REVIEW judgment.
- Optional smoke evidence is project-specific and remains skipped when no command is configured.
