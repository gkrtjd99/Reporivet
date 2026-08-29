---
id: PLAN-2026-0001
kind: exec-plan
status: in-progress
owner: main
area: harness
created: 2026-08-29
updated: 2026-08-29
base_commit: "accce51bd7190c53caa62fd45c27295b4a14eaf4"
integrated_commit: ""
verified_commit: ""
---

# Rename to Reporivet and prepare public release

## Purpose / Big Picture

Publish the initializer under the public name **Reporivet** while keeping the generated harness repository-native and independent. A user can install or run `reporivet`, initialize a project, and receive the same deterministic Main/Sub, documentation, verification, and gardening workflow. The public source tree must also avoid accidentally tracking local secrets, credentials, personal editor state, caches, raw logs, and build output.

## Progress

- [x] Establish current behavior and constraints.
- [ ] Rename the current package, CLI, current-state documents, templates, and tests to Reporivet.
- [ ] Harden repository and generated-project ignore rules and add a public security-reporting policy.
- [ ] Integrate and independently verify the candidate.
- [ ] Publish the verified source snapshot to `gkrtjd99/Reporivet`.
- [ ] Resolve documentation impact and follow-ups.

## Context and Orientation

The installable package currently lives under `src/project_harness/` and exposes the `project-harness` command through `pyproject.toml`. It renders the independent target runtime from `src/project_harness/assets/project/`. Current product, design, architecture, quality, and README documents still use the pre-public name **Project Harness**. The root `.gitignore` and the generated managed block cover Python caches and `.harness/runs/`, but not common credential files, local environment files, IDE state, broader build output, or infrastructure state. Historical content in `docs/exec-plans/completed/` describes the repository before this rename and remains immutable history.

## Scope

- Rename the Python distribution, import package, console command, current documents, templates, managed markers, tests, and public metadata to Reporivet.
- Preserve the generic generated-runtime names `dev/harness.py`, `dev/harness.toml`, and `.harness/`; use `.reporivet-version` for installer-owned version metadata.
- Expand `.gitignore` and its generated managed block for common secret, personal, cache, log, local-database, test-report, build, package, and infrastructure-state files.
- Keep tracked examples and reproducibility files such as `.env.example`, lockfiles, source code, migrations, and documentation eligible for commit.
- Add `.github/SECURITY.md` for private vulnerability-reporting guidance.
- Audit the current snapshot and existing Git history for high-confidence credential patterns before publication.

## Non-goals

- Rewriting the completed baseline plan or old commit authors and messages.
- Publishing a package to PyPI.
- Adding a secret-management product or treating `.gitignore` as a security boundary.
- Adding new runtime orchestration, plugins, Skills, task databases, or product capabilities.

## Acceptance Criteria

- **AC-1:** `reporivet --help` and `python -m reporivet --help` work, and current source-of-truth files no longer present the project as `project-harness`, `project_harness`, or **Project Harness**.
- **AC-2:** Initialization and upgrade use `reporivet` managed markers and generate an idempotent `.gitignore` block that excludes common secrets, local configuration, personal editor state, raw logs, caches, build/package output, local databases, and infrastructure state while allowing documented examples and lockfiles.
- **AC-3:** Existing ownership, baseline, ExecPlan, deterministic verification, and upgrade behavior remains covered by regression tests; `./dev/verify` passes from a clean Git commit.
- **AC-4:** `.github/SECURITY.md` exists, no tracked file is unintentionally ignored, and a high-confidence scan of the current tree and existing history finds no committed credential or private-key material.
- **AC-5:** The verified source snapshot is published to the public `gkrtjd99/Reporivet` repository, or the exact connector limitation and a ready-to-push Git artifact are recorded if the available GitHub interface cannot perform writes.

## Milestones

### M1 — Reporivet identity remains end-to-end runnable

Rename the package and current-state references in one integrated slice, then run the full regression suite and initialize a fresh temporary project through the renamed CLI.

### M2 — Public repository hygiene is enforced

Apply the hardened ignore policy to this repository and generated projects, verify idempotency and exceptions, add the public security policy, audit tracked content and history, and confirm no intended source file is ignored.

### M3 — Verified publication

Commit the candidate, run the canonical verification gate on the clean integrated commit, close the plan, and publish or produce an exact ready-to-push artifact if connector write operations are unavailable.

## Task Packets

### T1 — Explore and establish the change boundary

#### State

complete

#### Depends on

none

#### Outcome

Identify every current package, CLI, managed-marker, document, template, test, ignore-policy, and publication surface affected by the rename and public release.

#### Non-goals

Implementation writes or historical-plan rewriting.

#### Read

`AGENTS.md`, `README.md`, `ARCHITECTURE.md`, `pyproject.toml`, `.gitignore`, `src/project_harness/**`, `tests/test_project_harness.py`, current documents, packaged templates, and Git metadata.

#### Allowed writes

This plan result only.

#### Protected paths

All implementation paths.

#### Acceptance

AC-1 through AC-5 boundaries are explicit.

#### Verify

`./dev/context --path pyproject.toml`, repository-wide exact-name search, tracked-file listing, and Git remote/repository inspection.

#### Stop conditions

A published compatibility contract, production data migration, unrelated feature scope, or unresolvable repository ownership conflict.

#### Result

Complete. The project has not yet been publicly released as a package, so the CLI/import rename can be atomic. Generic target-runtime names should remain stable. The destination repository exists, is public, and the linked account reports push permission. The currently exposed GitHub connector actions still require verification for actual write support.

### T2 — Implement the Reporivet and repository-hygiene slice

#### State

in-progress

#### Depends on

T1

#### Outcome

A clean Reporivet package and generated harness with hardened, tested ignore behavior and public security guidance.

#### Non-goals

Historical-plan rewriting, PyPI release, unrelated refactors, or new dependencies.

#### Read

This plan; `pyproject.toml`; current-state documents; `src/project_harness/**`; `tests/test_project_harness.py`; root and template `.gitignore`; `.github/workflows/ci.yml`.

#### Allowed writes

`pyproject.toml`, `README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `LICENSE`, `.gitignore`, `.github/**`, `.reporivet-version`, `dev/**`, current `docs/**` excluding `docs/exec-plans/completed/**`, `src/**`, `tests/**`, and this plan.

#### Protected paths

`docs/exec-plans/completed/**`, old Git commit objects, external repositories until local verification succeeds.

#### Acceptance

AC-1, AC-2, and AC-4.

#### Verify

`./dev/check`, renamed CLI smoke initialization, ignore-rule assertions, `git check-ignore`, tracked-file audit, and credential-pattern scan.

#### Stop conditions

The generated project becomes dependent on the installed package, intended source/reproducibility files become ignored, or the rename requires compatibility shims.

#### Result

Pending implementation evidence.

### T3 — Independently verify and publish the integrated candidate

#### State

blocked

#### Depends on

T2

#### Outcome

Judge the clean integrated commit against every criterion and publish the verified snapshot without relying on implementer claims.

#### Non-goals

Redesign, unrelated cleanup, PyPI publication, or bypassing repository permissions.

#### Read

This plan, the complete diff, current-state documents, tests, package metadata, ignore policy, security policy, Git history, and destination repository state.

#### Allowed writes

Verifier evidence, plan completion metadata, release artifacts, and destination-repository content after verification.

#### Protected paths

Acceptance criteria and verified implementation unless a failing criterion is assigned back for repair.

#### Acceptance

All criteria in this plan.

#### Verify

`./dev/verify`, isolated wheel build/install, initialized-project `./dev/verify`, `reporivet doctor`, `git status --ignored`, `git ls-files`, history scan, and destination commit/tree comparison.

#### Stop conditions

The candidate differs from the integrated target, the worktree is dirty, evidence is unavailable, or the connected GitHub interface cannot write repository content.

#### Result

Pending verified target, criterion-by-criterion evidence, residual risks, and publication outcome.

## Architecture Impact

The distribution/import boundary changes from `project-harness` / `project_harness` to `reporivet`. The target repository runtime remains a copied standard-library implementation under `dev/harness.py` and continues not to import the installer. Managed ownership markers change atomically to the Reporivet namespace. No new dependency edge or runtime service is introduced.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| `README.md` | update | Public name, commands, paths, repository URL, and hygiene behavior | Main | pending |
| `AGENTS.md` | update | Current project identity and managed marker | Main | pending |
| `ARCHITECTURE.md` | update | Distribution/import paths and marker namespace | Main | pending |
| `docs/PRODUCT.md` | update | Current product and CLI identity | Main | pending |
| `docs/DESIGN.md` | update | Ownership-marker convention | Main | pending |
| `docs/QUALITY.md` | update | Renamed test ownership | Main | pending |
| `docs/SECURITY.md` | update | Ignore/audit limitations and public-release posture | Main | pending |
| `docs/README.md` and indexes | generate/update | Catalog markers and current title | Main | pending |
| `.github/SECURITY.md` | create | Public vulnerability-reporting route | Main | pending |
| completed baseline plan | none | Immutable historical record of the pre-rename baseline | Main | accepted |

## Interfaces and Dependencies

- Existing project capability inspected: setuptools console scripts, package data, standard-library initializer/runtime, Git ignore semantics, and existing regression suite.
- New production dependency: none.
- Public or cross-repository contract impact: package/import/CLI rename before first public package release; no compatibility shim is required.

## Migration, Rollout, and Recovery

No data migration applies. The rename is an atomic pre-release source change. Recovery is `git revert` of the rename/hygiene commit. Publication must occur only after a clean-commit verification. If GitHub write actions are unavailable, retain the local verified commit and generate a Git bundle/ZIP rather than attempting unauthenticated or partial publication.

## Surprises and Discoveries

- 2026-08-29 — The destination repository exists, is public, empty or near-empty, and the linked account reports administrative and push permissions.
- 2026-08-29 — The root ignore file protects Python caches and raw harness runs but does not yet cover common credentials, local environments, editor state, databases, infrastructure state, or broader build output.
- 2026-08-29 — Existing commits use a non-routable local author identity and contain no user filesystem paths in the current tree.

## Decision Log

- 2026-08-29 — Use **Reporivet** as project name and `reporivet` as distribution, import package, and CLI command.
- 2026-08-29 — Keep generic runtime names (`dev/harness.py`, `.harness/`) but use `.reporivet-version` for the installer-owned upgrade marker.
- 2026-08-29 — Do not rewrite the completed baseline plan; it remains accurate historical evidence.
- 2026-08-29 — Ignore high-risk local files by default but explicitly preserve example environment files and lockfiles; `.gitignore` is defense-in-depth, not secret management.

## Concrete Steps

Run commands from the repository root.

1. Rename `src/project_harness/` and `tests/test_project_harness.py`, then update package metadata, imports, CLI strings, current documents, templates, and managed markers.
2. Replace the root and template ignore policies, add tests for idempotency and protected examples, and create `.github/SECURITY.md`.
3. Run exact-name, tracked-file, ignored-file, private-key, credential-pattern, and history audits.
4. Run `./dev/check`, `./dev/verify`, build a wheel, install it in an isolated environment, initialize a fresh project, and verify/diagnose that project.
5. Commit the candidate, re-run `./dev/verify` on a clean commit, record the SHA, and close this plan.
6. Publish the verified source tree to `gkrtjd99/Reporivet`, then compare the destination tree and CI state.

## Validation and Evidence

- Integrated target: pending
- Verified commit: pending
- Acceptance results: pending
- Commands and durable summaries: pending
- Raw logs: `.harness/runs/` and not committed

## Outcomes and Retrospective

Pending completion.

## Follow-ups

Promote unresolved items to [`tech-debt-tracker.md`](/docs/exec-plans/tech-debt-tracker.md) or the declared external backlog before completion.

- none yet
