---
id: PLAN-2026-0004
kind: exec-plan
format: 2
status: complete
owner: main
area: packaging
created: 2026-09-01
updated: 2026-09-01
supersedes: ""
superseded_by: ""
base_commit: "5df73f7038f5f36aebeed19f5ab50a920f0e5424"
integrated_commit: ""
verified_commit: ""
---

# Finalize verified artifact readiness and package license metadata

## Original goal

Proceed with the two bounded follow-ups recorded by completed PLAN-2026-0003: update conservative pre-verification artifact-readiness wording, resolve the setuptools license metadata/classifier deprecation, and commit the resulting verified repository state.

## Observable outcome and acceptance

- **AC-1:** Current/public/package authority states that candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded pipx/pip artifact lifecycle, without claiming publication, signing, release, deployment, CI readiness, or a permanent evidence archive.
- **AC-2:** `pyproject.toml` uses nondeprecated SPDX-compatible MIT license metadata, retains the license file in built distributions, removes the deprecated license classifier, preserves Python 3.11+, version `0.2.0`, the console entry point, and zero production dependencies, and builds without the targeted setuptools license deprecation warnings.
- **AC-3:** Focused documentation/distribution checks, the full source suite, compile, doctor, link/parity checks as applicable, patch hygiene, and a fresh local wheel metadata/build inspection pass on one integrated candidate; Main then creates the user-authorized local Git commit without push, tag, publication, signing, release, or deployment.

## Scope

- Current/public/package-template status wording that still describes the already-completed artifact lifecycle as pending, Open, or unverified.
- Build metadata and focused tests directly required to remove the two setuptools license deprecations while retaining MIT license coverage.
- Main integration, fresh verification, terminal Plan movement, and one local commit containing the complete integrated repository state.

## Non-goals

- Rebuilding product behavior, rerunning pipx/pip install/uninstall lifecycles, changing runtime dependencies, changing the project license, publishing artifacts, repairing project-owned CI, pushing, tagging, signing, releasing, or deploying.
- Rewriting completed PLAN-2026-0003, historical documents, generated historical module-contract bodies, or unrelated metadata.

## Task state

| Task | Owner | State | Depends on | Parallel group | Outcome | Result |
|---|---|---|---|---|---|---|
| T1-A | docs-readiness | complete | none | G1 | Align artifact-readiness authority | 8-file bounded update; 96/96 lane suite pass |
| T1-B | license-metadata | complete | none | G1 | Remove setuptools license deprecations | 2-file bounded update; wheel/sdist warning-free |
| T1-I | main | complete | T1-A, T1-B | integration | Integrate exact disjoint changes | candidate `2ccf9752...`; 97/97 full pass; build pass |
| T1-V1 | verification | complete | T1-I | verification | Freshly judge AC-1 through AC-3 | AC-1 fail; AC-2 pass; commit blocked |
| T1-R1 | docs-repair | complete | T1-V1 | repair | Repair five missed current authority surfaces | 6-file bounded update; 98/98 lane suite pass |
| T1-RI | main | complete | T1-R1 | integration | Integrate bounded documentation repair | candidate `acc28429...`; 98/98 full pass |
| T1-V2 | verification | complete | T1-RI | verification | Freshly rejudge AC-1 through AC-3 | AC-1/AC-2/AC-3 pass |
| T2 | main | complete | T1-V2 | serial | Close Plan and create local commit | terminal Plan and local commit |

## Task Packets

### T1-A — Align verified artifact-readiness authority

- **Role:** leaf
- **Parent:** T1
- **Parallel group:** G1
- **May delegate:** no
- **Owner:** docs-readiness
- **Outcome:** replace only stale current/public/package-template statements that classify PLAN-2026-0003 artifact readiness as pending, Open, or unverified; preserve exact verified identity and all release/publication/CI non-goals.
- **Non-goals:** product code, packaging metadata, historical Plan/spec evidence rewrites, new readiness promises, CI repair, release instructions, or procedure changes.
- **Read:** this Plan; completed PLAN-2026-0003 final evidence/follow-ups; current/public/package authority containing matching readiness claims; documentation contract tests.
- **Allowed writes:** `README.md`, `README.en.md`, `docs/PRODUCT.md`, `docs/QUALITY.md`, `docs/OPERATIONS.md`, current SPEC/DESIGN 003, matching document-first package templates, and focused documentation tests only where an actual stale claim requires alignment.
- **Protected paths:** `pyproject.toml`, package Python code, unrelated tests/docs, completed Plans, project-owned CI, settings, migration, `.harness/runs` and descendants, external systems.
- **Acceptance:** AC-1; current and packaged authority agree that artifact verification passed while publication/signing/release/deployment/CI remain separate and unestablished.
- **Verification:** focused documentation-contract tests, bounded stale-status scan, current/package links, bilingual parity when README changes, doctor, and patch hygiene.
- **Stop conditions:** wording would imply publication/release/CI readiness, a historical record must be rewritten, or scope expands beyond stale status.
- **Return:** exact changed paths/hashes, stale statements replaced, commands/results, and residual risks.
- **Result:** Complete. Changed only `README.md`, `README.en.md`, `docs/PRODUCT.md`, `docs/QUALITY.md`, `docs/OPERATIONS.md`, SPEC/DESIGN 003, and `tests/test_documentation_contract.py`. Current authority now records the verified PLAN-2026-0003 source/wheel lifecycle while retaining publication, signing, release, deployment, CI, and durable-evidence non-goals. Package templates contained no matching stale claim. Focused documentation tests passed 6/6, the lane full suite passed 96/96, compile/doctor/55 scoped links/bilingual parity/stale scan/diff passed.

### T1-B — Modernize license metadata

- **Role:** leaf
- **Parent:** T1
- **Parallel group:** G1
- **May delegate:** no
- **Owner:** license-metadata
- **Outcome:** use supported SPDX-compatible MIT metadata, remove the deprecated license classifier, preserve license-file inclusion and every unrelated distribution contract, and add only directly necessary regression coverage.
- **Non-goals:** license change, production dependency, version change, package-data redesign, publication, or unrelated classifier cleanup.
- **Read:** this Plan; `pyproject.toml`; `LICENSE`; distribution tests; current setuptools/PEP 639 behavior needed to eliminate the observed warnings.
- **Allowed writes:** `pyproject.toml` and directly required focused assertions in `tests/test_distribution.py`.
- **Protected paths:** docs/status wording, package code/assets, unrelated tests, completed Plans, project-owned CI, `.harness/runs` and descendants, external publication state.
- **Acceptance:** AC-2; a disposable local build emits neither targeted license-table nor license-classifier deprecation warning, and wheel/sdist metadata plus license-file inclusion remain correct.
- **Verification:** focused distribution tests, TOML/static metadata assertions, disposable Python 3.11+ build with directly required tooling, complete output warning inspection, and archive metadata/license inspection.
- **Stop conditions:** MIT semantics change, a production dependency is required, build compatibility cannot be established, or unrelated metadata must change.
- **Return:** exact changed paths/hashes, metadata rationale, commands/results, and residual risks.
- **Result:** Complete. Changed only `pyproject.toml` and `tests/test_distribution.py`: declared `setuptools>=77`, replaced the deprecated license table with SPDX `license = "MIT"`, added `license-files = ["LICENSE"]`, and removed only the deprecated MIT classifier. Focused tests passed 3/3. A disposable Python 3.13/setuptools 77.0.1 build produced wheel and sdist with exact MIT expression/file metadata, matching LICENSE bytes, version/Python/entry-point/zero-dependency invariants, and no targeted license deprecation warning.

### T1-I — Integrate follow-up leaves

- **Role:** integration
- **Parent:** T1
- **Parallel group:** integration
- **May delegate:** no
- **Owner:** main
- **Outcome:** verify both seed-relative deltas are disjoint and bounded, integrate exact bytes/modes, run shared checks, and freeze one candidate identity excluding only the protected run tree and this Main-owned active Plan.
- **Non-goals:** repair beyond returned scope, acceptance changes, or lifecycle reruns already completed by PLAN-2026-0003.
- **Read:** both leaf returns, this Plan, relevant source/docs/tests, and project quality authority.
- **Allowed writes:** accepted leaf paths plus this Plan.
- **Protected paths:** all other repository content, completed Plans, `.harness/runs` descendants, external systems.
- **Acceptance:** AC-1 and AC-2 integrated without cross-lane conflict or unrelated change.
- **Verification:** focused tests, full suite, compile, doctor, documentation/link parity, local wheel build/inspection, and `git diff --check` with protected exclusions.
- **Stop conditions:** baseline mismatch, overlapping writes, failed mandatory check, protected-path access, or scope expansion.
- **Return:** integrated paths, exact candidate identity, commands/results, and residual risks.
- **Result:** Complete. Main proved primary seed fingerprint `b04731d89ceb0d6879016e300ee00e750ef7abd20c8d9b47e6108c91effe4cec` remained unchanged, verified exact disjoint 8-file and 2-file lane deltas, and integrated ten files byte/mode-exactly. Integrated candidate fingerprint is `2ccf9752968cb6e265bcb58d7528b1b93c7e7d7c21b09f87691b032ecca131bb`, patch SHA-256 `34115d13df23e6c1e7f4b2a24559b5c76f8b3c064773d4349704a3a1c4148773`. Focused checks passed 9/9, full suite 97/97, compile/doctor/diff passed. The minimum-backend integrated build produced read-only wheel `7e8ebf29b81c3720f484565d546540e42aab97ec4cdebfbb43e86bc3c6b25259` and sdist `b0aa4f93109fd6c41d2abdfba382ee12bca469b8129c3e5b0268201b64a70f45`; all license/version/Python/entry-point/dependency checks and targeted-warning absence passed.

### T1-V1 — Fresh follow-up verification

- **Role:** verification
- **Parent:** T1
- **Parallel group:** verification
- **May delegate:** no
- **Owner:** verification
- **Outcome:** independently judge AC-1 through AC-3 against the integrated candidate, treating implementation narration as unverified.
- **Non-goals:** repair, delegation, mutation, publication, push, tag, signing, release, deployment, or detailed pipx/pip lifecycle reruns.
- **Read:** this Plan, integrated diff, current/package authority, `pyproject.toml`, distribution/documentation tests, fresh local build output and artifacts.
- **Allowed writes:** verifier return and disposable `/tmp` evidence only.
- **Protected paths:** candidate, completed Plans, `.harness/runs` descendants, credentials, global/user environments, external systems.
- **Acceptance:** AC-1 through AC-3 pass with exact candidate identity before/after and no targeted warning or readiness-boundary contradiction.
- **Verification:** independent source identity, focused/full checks as applicable, wheel/sdist metadata and license-file inspection, stale-status scan, and release-boundary review.
- **Stop conditions:** candidate changes, mandatory evidence is unavailable, a protected path is accessed, or any criterion is failed/unknown.
- **Return:** criterion verdicts, exact identity, blockers, and residual risks.
- **Result:** Complete with a failed criterion. The verifier independently held HEAD `5df73f7038f5f36aebeed19f5ab50a920f0e5424`, fingerprint `2ccf9752968cb6e265bcb58d7528b1b93c7e7d7c21b09f87691b032ecca131bb`, and patch SHA-256 `34115d13df23e6c1e7f4b2a24559b5c76f8b3c064773d4349704a3a1c4148773` stable before/after. AC-2 passed with fresh warning-free wheel `7e5e3b9bb96afc4f27da36fbc8a05f0f83899e26f974dd6fbeb658f6de10b24f` and sdist `8edcedae9d6739defebe7885d8018637a107300493dbd53a548f93f3024533ea`; focused tests passed 9/9, full suite 97/97, compile, doctor, 153 scoped links, bilingual parity, and diff hygiene passed. AC-1 failed because `ARCHITECTURE.md`, `docs/DESIGN.md`, `docs/references/harness-engineering-skill-migration.md`, and the Open sections of `docs/QUALITY.md` and `docs/OPERATIONS.md` still classify the completed artifact lifecycle as pending/Open. AC-3 therefore remains blocked. Compact evidence: `/tmp/reporivet-plan4-v1-evidence-ilf73d7t/evidence.json`, SHA-256 `1e8036abcb599ba10e92ec63b9e1f007d991a78f5c47c15a00e6bc9c50c7757a`.

### T1-R1 — Repair missed artifact-readiness authority

- **Role:** leaf repair
- **Parent:** T1
- **Parallel group:** repair
- **May delegate:** no
- **Owner:** docs-repair
- **Outcome:** replace only the five verifier-identified current authority statements that still classify the completed PLAN-2026-0003 artifact lifecycle as pending/Open, and extend the directly necessary stale-status regression coverage.
- **Non-goals:** product or packaging changes, broader documentation cleanup, historical-record rewrites, package-template changes without a matching stale claim, CI repair, release promises, or harness-contract changes.
- **Read:** this Plan; fresh T1-V1 evidence; the exact five verifier-identified documents; existing documentation-contract test.
- **Allowed writes:** `ARCHITECTURE.md`, `docs/DESIGN.md`, `docs/references/harness-engineering-skill-migration.md`, `docs/QUALITY.md`, `docs/OPERATIONS.md`, and directly necessary assertions in `tests/test_documentation_contract.py`.
- **Protected paths:** all other repository content, completed Plans, product/package code, packaging metadata, project-owned CI, `.harness/runs` and descendants, external systems.
- **Acceptance:** AC-1; current authority records the exact verified source/wheel lifecycle while only publication, signing, release, deployment, CI, and durable archival gaps remain Open.
- **Verification:** focused documentation-contract tests, exact stale-status scan covering every current authority surface, links, doctor, and patch hygiene.
- **Stop conditions:** wording would imply unsupported readiness, another current stale surface is found outside the allowed set, a historical body must change, or scope expands.
- **Return:** exact changed paths/hashes/modes, statements replaced, commands/results, and residual risks.
- **Result:** Complete. Changed only the five verifier-identified authority documents plus `tests/test_documentation_contract.py`, all mode `0644`. Architecture, design, and migration reference now record the exact verified source candidate and wheel lifecycle; QUALITY and OPERATIONS no longer place the completed lifecycle under Open; regression coverage now scans all five surfaces and both Open sections. Focused tests passed 7/7, lane full suite 98/98, compile, doctor, bounded stale scan, and patch hygiene passed. Returned final hashes were independently matched during T1-RI.

### T1-RI — Integrate documentation repair

- **Role:** integration
- **Parent:** T1
- **Parallel group:** integration
- **May delegate:** no
- **Owner:** main
- **Outcome:** prove the repair is seed-relative and bounded, integrate exact bytes/modes, run shared checks, and freeze a repaired candidate.
- **Non-goals:** additional repair, acceptance changes, or external action.
- **Read:** T1-R1 return, this Plan, repair diff, and current candidate identity.
- **Allowed writes:** accepted T1-R1 paths plus this Plan.
- **Protected paths:** all other repository content, completed Plans, `.harness/runs` descendants, external systems.
- **Acceptance:** AC-1 and AC-2 coexist on one repaired candidate with no unrelated change.
- **Verification:** repair-path identity, focused/full tests, compile, doctor, links/parity, fresh build metadata/warning inspection as applicable, and diff hygiene.
- **Stop conditions:** baseline mismatch, out-of-scope write, mandatory check failure, or protected-path access.
- **Return:** integrated paths, repaired candidate identity, commands/results, and residual risks.
- **Result:** Complete. Main materialized and verified the exact T1-R1 seed, proved the lane delta was exactly the six allowed paths, independently matched every returned SHA-256/mode, and copied exact bytes/modes into the primary candidate. Repaired candidate fingerprint is `acc28429d236212a847afb220a796496d952c0fd009be653d9989f29494e75eb`, patch SHA-256 `fa3147fb2c0312b040e19d26ea2d2d3038e198964e2d473c049e4e6753ace653`, HEAD `5df73f7038f5f36aebeed19f5ab50a920f0e5424`. Focused tests passed 7/7, full suite 98/98, compile, doctor, and diff hygiene passed; identity remained stable after checks.

### T1-V2 — Fresh repaired-candidate verification

- **Role:** verification
- **Parent:** T1
- **Parallel group:** verification
- **May delegate:** no
- **Owner:** verification
- **Outcome:** independently rejudge AC-1 through AC-3 against the repaired integrated candidate, treating all repair narration as unverified.
- **Non-goals:** repair, mutation, delegation, commit, push, tag, signing, publication, release, deployment, or redundant pipx/pip lifecycle reruns.
- **Read:** this Plan, repaired candidate diff/identity, current/package authority, focused tests, and fresh local build output as required.
- **Allowed writes:** verifier return and disposable `/tmp` evidence only.
- **Protected paths:** candidate, completed Plans, `.harness/runs` descendants, credentials, global/user environments, external systems.
- **Acceptance:** AC-1 through AC-3 pre-commit readiness pass with exact identity before/after and no readiness-boundary contradiction or targeted metadata warning.
- **Verification:** independent source identity, exact current-authority stale scan, focused/full checks, wheel/sdist metadata and license inspection, links/parity, doctor, and diff hygiene.
- **Stop conditions:** candidate changes, mandatory evidence is unavailable, a protected path is accessed, or any criterion fails/is unknown.
- **Return:** criterion verdicts, exact identity, blockers, and residual risks.
- **Result:** Complete, PASS. Fresh verifier independently held HEAD `5df73f7038f5f36aebeed19f5ab50a920f0e5424`, fingerprint `acc28429d236212a847afb220a796496d952c0fd009be653d9989f29494e75eb`, and patch SHA-256 `fa3147fb2c0312b040e19d26ea2d2d3038e198964e2d473c049e4e6753ace653` stable before/after. AC-1 passed across five repaired blockers, 15 current/public documents, 28 package templates, 153 scoped links, bilingual/package parity, and stale/Open scans. AC-2 passed with fresh Python 3.13.15/setuptools 77.0.1/build 1.6.0 wheel `4d227e00c691960238007da5848b31a53d444e704121b77f27962ca488f4eed4` and sdist `243b68f5c8d4c54c98884663f0025e3814f5067f28b5f26cfd5d0056b59a89ac`; metadata, exact LICENSE bytes, entry point, zero dependencies, and targeted-warning absence passed. AC-3 passed with documentation 7/7, distribution 3/3, package assets 14/14, Plan lifecycle 15/15, full suite 98/98, compile, doctor, links/parity/stale scans, and diff hygiene. Evidence: `/tmp/reporivet-plan4-v2-evidence-oyvehvti/evidence.json`, independently matched SHA-256 `c6f2d8c1e024494ea22c65d8a50f884de854b5584c96d89948916b03e9b91ba8`.

### T2 — Close and commit

- **Owner:** main
- **Outcome:** record fresh verification, set exact terminal outcome, move this Plan to `completed/`, stage the complete intended repository state, inspect the staged path set and tree, and create the user-authorized local commit.
- **Non-goals:** amend unrelated history, push, tag, sign, publish, release, deploy, or modify external systems.
- **Read:** accepted T1-V2 evidence, this Plan, final diff/status, repository commit rules.
- **Allowed writes:** this Plan lifecycle fields/location and local Git index/commit object.
- **Protected paths:** `.harness/runs` descendants, credentials, remotes, tags, release/publication/deployment state.
- **Acceptance:** AC-3; one local commit contains only the complete intended candidate and terminal Plan record, with no external action.
- **Verification:** staged path review with protected exclusions, `git diff --cached --check`, commit success, post-commit status, and commit summary.
- **Stop conditions:** staged scope differs from accepted candidate, tests fail, commit hooks reveal unresolved failure, signing or push is requested implicitly, or repository identity changes unexpectedly.
- **Return:** commit SHA, subject, path summary, verification state, and residual risks.
- **Result:** Complete through the terminal repository transaction containing this Plan. Main accepted fresh T1-V2, moved the Plan to `completed/`, staged the complete intended candidate with `.harness/runs` descendants excluded, inspected the staged path set/diff, passed `git diff --cached --check`, and created the user-authorized local commit. The commit SHA is reported by Main outside this self-referential Plan record; no push, tag, signing, publication, release, deployment, or external action occurred.

## Broad-milestone decomposition

T1 is broad because documentation authority and build metadata are independent write surfaces. T1-A and T1-B ran concurrently in separately seeded worktrees and converged through T1-I. Fresh T1-V1 then found a bounded documentation-coverage defect, so serial repair T1-R1 converges through T1-RI before fresh T1-V2. No leaf delegates.

## Current checkpoint

Fresh T1-V2 independently passed AC-1 through AC-3 against repaired candidate `acc28429d236212a847afb220a796496d952c0fd009be653d9989f29494e75eb`. The requested documentation-readiness and license-metadata follow-ups are complete and the terminal Plan is contained by the user-authorized local commit; no external action occurred.

## Exact next action

None. This Plan is complete; publication, signing, release, deployment, project-owned CI, and durable evidence archival remain separate work requiring their own authority.

## Decisions

- Preserve PLAN-2026-0003 as completed history; this Plan owns the two explicitly requested follow-ups.
- Treat artifact lifecycle readiness as verified, while publication, signing, release, deployment, and project-owned CI remain outside the established evidence.
- Keep MIT as the project license and change only metadata syntax/classifier details required to remove the observed setuptools deprecations.
- Commit locally only after fresh verification; do not push or release.

## Discoveries

- `docs/QUALITY.md` still labels the completed wheel lifecycle as a separate open criterion and places it under Open/quality-gap wording.
- `pyproject.toml` used deprecated `license = {text = "MIT"}` and the deprecated `License :: OSI Approved :: MIT License` classifier.
- Standards-compliant `project.license` and `project.license-files` require the setuptools 77 PEP 639 implementation floor; setuptools 77.0.1 is the earliest matching release exposed by the configured verification index and builds cleanly.
- Current package templates contained no PLAN-2026-0003-specific stale readiness claim, so no template rewrite was needed.
- Fresh T1-V1 proved the initial bounded stale scan was incomplete: `ARCHITECTURE.md`, `docs/DESIGN.md`, `docs/references/harness-engineering-skill-migration.md`, and the Open sections of `docs/QUALITY.md` and `docs/OPERATIONS.md` still presented the completed artifact lifecycle as pending/Open.

## Documentation impact

- Current/public authority: repaired across all five T1-V1-identified surfaces; regression coverage now includes each surface and the QUALITY/OPERATIONS Open sections.
- Package templates: no change required; no matching stale claim existed.
- Historical completed records: no change.

## Integration summary

- Candidate identity: repaired fingerprint `acc28429d236212a847afb220a796496d952c0fd009be653d9989f29494e75eb`, patch SHA-256 `fa3147fb2c0312b040e19d26ea2d2d3038e198964e2d473c049e4e6753ace653`, HEAD `5df73f7038f5f36aebeed19f5ab50a920f0e5424`.
- Integrated changes: the original eight current/public documentation and contract-test paths, `pyproject.toml`, one distribution test, and the seed-relative six-file repair (three additional authority paths plus corrections to QUALITY, OPERATIONS, and the existing documentation test).
- Residual risks: integrated artifacts are disposable local evidence; publication/signing/release/deployment and project-owned CI remain outside this Plan.

## Verification summary

| Criterion | Candidate | Verifier | Result | Decision-bearing evidence |
|---|---|---|---|---|
| AC-1 | `acc28429...` | T1-V2 | pass | Exact verified lifecycle is current across repaired/public/package authority; unsupported boundaries remain explicit |
| AC-2 | `acc28429...` | T1-V2 | pass | Fresh wheel/sdist use SPDX MIT metadata, exact LICENSE, retained distribution invariants, and no targeted warnings |
| AC-3 | `acc28429...` | T1-V2 + Main T2 | pass | Fresh 98/98 and all focused/structural checks passed; terminal Plan and local commit created without external action |

## Follow-ups

- None in scope. Publication, signing, release, deployment, project-owned CI, and durable evidence archival remain explicit non-goals rather than implied follow-up authorization.

## Outcome

complete
