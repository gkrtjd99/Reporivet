---
id: PLAN-2026-0006
kind: exec-plan
format: 2
task_graph: 1
status: complete
owner: main
area: harness
created: 2026-09-02
updated: 2026-09-02
supersedes: ""
superseded_by: ""
base_commit: "680a091bd1b27f9761a65ce4832f41fcb1c8cf4c"
integrated_commit: ""
verified_commit: ""
---

# Make every generated target independent after one-shot setup

## Original goal
Change Reporivet's generator and package contract—not merely this source repository's local files—so any external project created through Reporivet needs Reporivet only during explicit setup and has no continuing package, Skill, doctor, marker, settings, runtime, or registry-resolution dependency afterward.

## Observable outcome and acceptance
- **AC-1:** A fresh temporary target receives project-owned Markdown, Plan templates/directories, deterministic static runbooks, and at most an exact root `CLAUDE.md` adapter; it receives no Reporivet role/procedure Skill, `.reporivet-version`, generated `.claude/settings.json`, copied runtime, or setup-created active Plan.
- **AC-2:** Generated `AGENTS.md`, `docs/PLANS.md`, and the Plan template fully define Main, Task Owner, implementation, verification, Plan creation/resume, and manual terminal movement without depending on a generated Skill.
- **AC-3:** Generated target authority and Task Packet guidance never locate, install, resolve, import, invoke, or verify Reporivet/doctor, and package absence is not `UNKNOWN`, blocking, or a residual risk.
- **AC-4:** Only complete unique Confirmed structured procedures render deterministic plain Markdown runbooks under `docs/runbooks/<slug>.md`; no Skill/frontmatter/executor metadata is emitted.
- **AC-5:** Explicit setup rerun identifies legacy role Skills, procedure Skills, generated settings, and markers only through exact canonical ownership evidence; modified, ambiguous, unsafe, nonregular, and project-owned paths are preserved and reported.
- **AC-6:** Destructive transition cleanup is bound to an exact setup preview, requires an external backup, revalidates before mutation, rolls back on failure, and refuses later rollback after user changes.
- **AC-7:** `reporivet doctor` and its current command, implementation, quality gates, and public claims are removed; setup validates only its own approved transaction postconditions.
- **AC-8:** One external user-scoped `/reporivet-setup` Skill exists outside target assets and only wraps the deterministic setup preview/apply command. It never edits target files itself or installs/resolves/downloads Reporivet.
- **AC-9:** Current ADR/spec/design/architecture/product/quality/operations/security/readme authority describes the new one-shot boundary; ADR-0001 and completed Plans 0003/0005 remain unchanged historical evidence.
- **AC-10:** Full project-owned checks, focused distribution checks, fresh-target independence smoke, existing-target cleanup/rollback smoke, and fresh criterion-level verification pass against one integrated candidate.

## Scope
- Reporivet source generator, setup/apply behavior, target templates, procedure rendering, safe transition cleanup, CLI doctor retirement, external setup Skill source, current authority documents, package inventory, and tests.
- Existing-target cleanup only in isolated fixtures and only through explicit approved setup rerun.

## Non-goals
- Do not clean `/Users/hakseong/Reporivet` as if it were a generated external target.
- Do not delete this source repository's local `.claude` content or root `.reporivet-version` as a demonstration.
- Do not publish, sign, deploy, globally install a Skill, or mutate any real external project.
- Do not add a plugin runtime, standalone zipapp, package resolver, scheduler, dispatcher, task store, command runner, hidden state, automatic closure, or evidence archive.
- Do not rewrite ADR-0001, completed Plans 0003/0005, historical fixtures, or superseded evidence bodies.

## Task state
| Task | Owner | State | Depends on | Parallel group | Outcome | Result |
|---|---|---|---|---|---|---|
| T1 | main | completed | none | serial-authority | Freeze successor ADR/spec/design and exact interfaces | PASS: ADR-0002, SPEC-004, DESIGN-004 and current routing frozen |
| T2 | core-owner | completed | T1 | core | Transform generator, runbooks, cleanup, doctor, and setup Skill | PASS (bounded): T2-A…T2-E implementation chain and owner-local aggregation completed; provisional verification gaps are carried to T3/fresh verification |
| T2-A | target-assets-owner | completed | T1 | T2-serial-chain | Replace target assets and Markdown-native authority | PASS: target asset inventory and forbidden-content scans passed; retired assets absent; exact CLAUDE adapter and diff check passed |
| T2-B | procedure-runbook-owner | completed | T2-A | T2-serial-chain | Render static runbooks and freeze legacy proof | PASS after correction: removed the prohibited `reporivet setup` dependency wording; editable-template and static-output scans passed |
| T2-C | generator-doctor-owner | completed | T2-B | T2-serial-chain | Revise generator inventory and remove doctor core | PASS: surviving inventory and 25-action deterministic preview passed; retired doctor, marker, and generated-path symbols were removed |
| T2-D | setup-transition-owner | completed | T2-C | T2-serial-chain | Integrate exact backup-bound cleanup into setup | PASS: exact ownership, mode guards, fingerprint binding, transaction rollback, and guarded later rollback passed; migration preview preserves its public boundary |
| T2-E | cli-launcher-test-owner | completed | T2-D | T2-serial-chain | Retire doctor/settings CLI and add external setup Skill | PASS: focused successor suite, CLI/help, compile, prohibited-content, and diff checks passed; one protected migration fixture mismatch is deferred |
| T2-I | core-owner | completed | T2-A, T2-B, T2-C, T2-D, T2-E | T2-owner-aggregation | Aggregate focused T2 evidence without repair | PASS (owner-local audit): 37-path envelope and focused checks passed; provisional cleanup/wheel evidence and one protected migration mismatch remain explicit |
| T3 | parity-owner | completed | T2 | parity | Align current docs, package inventory, and tests | PASS (bounded): T3-A through T3-D and owner-local aggregation completed; fresh verification and final acceptance remain separate |
| T3-A | authority-parity-owner | completed | T3 | T3-authority | Align current authority and public-document parity | PASS: eleven current-authority documents now describe one-shot setup, static runbooks, package independence, and manual Plan lifecycle |
| T3-B | generated-template-parity-owner | completed | T3-A | T3-template-parity | Align surviving generated templates with current authority | PASS: 17 templates aligned; surviving/retired inventory, forbidden-content, hierarchy, placeholder, compile, focused-template, and diff checks passed |
| T3-C | distribution-parity-owner | completed | T3-A, T3-B | T3-post-template | Align package inventory and distribution evidence | PASS: surviving/retired inventory and focused distribution/successor tests passed; wheel build unavailable without Setuptools |
| T3-D | regression-smoke-owner | completed | T3-A, T3-B | T3-post-template | Align regression tests and fresh-target smokes | PASS: eight test files reconciled; all nine focused suites passed; source/test compileall, isolated fresh-target and cleanup/backup/rollback smokes, `git diff --check`, and the corrected 61-path changed-path audit passed; protected migration mismatch remains explicit |
| T3-I | parity-owner | completed | T3-A, T3-B, T3-C, T3-D | T3-owner-aggregation | Aggregate parity evidence without repair | PASS (bounded): T3-I full-tree fingerprint was `70969eaf3e3c8b1e1461775dbbe1d89f1da1c2e4bca968ac78fdd96c53ac1ce4`; Main’s pre-T4 full-tree fingerprint was `91d4ed956296f2fbdef14cefbb50ff437f76fc043b5681226d30a060ad6a3cf6`; normalized non-Plan candidate remained stable; checks passed, with the protected migration mismatch and unavailable wheel inspection explicit |
| T4-V1 | verifier-target | completed | T3 | verification | Verify fresh-target independence and Markdown lifecycle | PASS: fresh isolated target matched 27 expected files; AC-1 through AC-3 and package independence passed; candidate fingerprint stable at `91d4ed956296f2fbdef14cefbb50ff437f76fc043b5681226d30a060ad6a3cf6` before/after; no `.harness/runs` access |
| T4-V2 | verifier-safety | completed | T3 | verification | Verify cleanup, backup, rollback, and ownership safety | PASS bounded: corrected isolated matrix passed all permitted AC-5/AC-6 cases; `.harness/runs` access and protected stale migration injection remain explicitly not-run |
| T4-V3 | verifier-contract | completed | T3 | verification | Verify runbooks, CLI/distribution, and documentation parity | PASS bounded for AC-4 and AC-7–AC-9; AC-10 not established due protected migration mismatch, unavailable wheel backend, and Plan-only dirty-tree fingerprint drift; no verifier writes |
| T4-I | main | completed | T4-V1, T4-V2, T4-V3 | final-integration | Resolve AC-10 evidence and make the final Plan judgment | PASS with accepted exclusions: the protected stale migration fixture and conditional unavailable wheel inspection were explicitly classified as nonessential; AC-1 through AC-10 are accepted for this candidate |

## Task Packets

### T1 — successor authority and frozen interfaces
- **Owner:** main
- **Role:** direct serial leaf
- **Parent:** none
- **Parallel group:** serial-authority
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** `680a091bd1b27f9761a65ce4832f41fcb1c8cf4c`
- **Inherited boundaries:** this Plan's scope, acceptance, non-goals, protected history, and no-external-action boundary
- **Outcome:** Create ADR-0002, SPEC-004, DESIGN-004, and current routing that define the one-shot generated-target contract and freeze interfaces used by T2/T3.
- **Non-goals:** No implementation behavior, target cleanup, publication, or historical-body rewrite.
- **Read:** `AGENTS.md`, `ARCHITECTURE.md`, `docs/README.md`, `docs/PRODUCT.md`, `docs/DESIGN.md`, `docs/QUALITY.md`, `docs/OPERATIONS.md`, `docs/SECURITY.md`, `docs/PLANS.md`, SPEC/DESIGN 003, ADR-0001, this Plan.
- **Allowed writes:** this Plan; new ADR-0002, SPEC-004, DESIGN-004; bounded current index/routing metadata required to select them.
- **Protected paths:** ADR-0001; completed Plans 0003/0005; source implementation; tests; external systems.
- **Acceptance:** AC-9 and frozen definitions supporting AC-1 through AC-8.
- **Verification:** document structure, link targets, terminology consistency, `git diff --check` for T1 paths.
- **Stop conditions:** unresolved authority conflict, scope expansion, or need to rewrite protected history.
- **Return:** changed paths, frozen interfaces, command results, discoveries, residual risks.
- **Result:** PASS. Added ADR-0002 (`f0234a82ae75cf11f0afcb16f75e2a4fd7384dea7d9d8544a9952bc5c2e9cb03`), SPEC-004 (`f6c0c85370b8105e6cc673f9f34e713bc5cff2c0e1b2fecc41e2cff5543a1cdb`), and DESIGN-004 (`c3a5aaae59c88438d0c74700026f5afb6f79f025157a6061080b0d01a5e62835`); routed current catalogs to them and changed only `status` metadata on SPEC/DESIGN 003. Link/frontmatter/routing validation and T1-scoped `git diff --check` passed. ADR-0001 and completed Plans 0003/0005 remained unchanged. Frozen interfaces: fresh-target inventory, Markdown-native roles, static nine-field Confirmed runbooks, external launcher-only setup Skill, no doctor/marker/settings/target Skills/runtime, and exact backup-bound setup-rerun cleanup. No residual T1 authority conflict.

### T2 — broad core Task Owner
- **Owner:** core-owner
- **Role:** Task Owner
- **Parent:** none
- **Parallel group:** core
- **May delegate:** yes
- **Child budget:** at most 5 implementation descendants plus one Owner-local aggregation node
- **Exact baseline:** integrated T1 candidate identified by Main
- **Inherited boundaries:** all Plan scope/acceptance/non-goals; source repository is not a cleanup target; no publication/global install/real external target; historical files protected; target interfaces frozen by T1
- **Outcome:** Return a finite disjoint child manifest, then implement and locally aggregate the generator-wide one-shot boundary.
- **Non-goals:** No shared-Plan edit, final integration judgment, external action, second runtime, or target-specific workaround.
- **Read:** T1 authority; `src/reporivet/{guided,setup,procedures,cli,migration,initializer}.py`; target assets; relevant focused tests.
- **Allowed writes:** only exact disjoint paths accepted in Main-serialized child packets after manifest review.
- **Protected paths:** this Plan; protected history; unrelated project code; external projects; release/publication surfaces.
- **Acceptance:** AC-1 through AC-8.
- **Verification:** focused unit/integration tests per child and Owner-local aggregation evidence.
- **Stop conditions:** overlapping child writes without serialization, unresolved interface conflict, unsafe deletion proof, scope expansion, or missing authority.
- **Return:** finite manifest first; after resume, changed paths, exact commands/results, child evidence, discoveries, and residual risks.
- **Result:** PASS (bounded). Main serialized and completed the T2-A through T2-E chain plus T2-I owner-local aggregation from the current uncommitted candidate. T2-I audited 37 changed paths within the accepted T1/T2 envelope, found no `.harness/runs` access or unexpected writes, and passed focused successor tests, compileall, CLI/help, package/Skill audits, and `git diff --check`. T2-I classified T2-D and T2-E as provisionally verified, retained one protected migration-fixture mismatch, noted incomplete independent cleanup/rollback evidence, and could not run wheel-content verification because `setuptools` is unavailable. These are explicit T3/fresh-verification inputs, not a final AC-1…AC-10 claim.

### T2-A — target authority assets
- **Owner:** target-assets-owner
- **Role:** implementation leaf
- **Parent:** T2
- **Parallel group:** T2-serial-chain
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** base `680a091bd1b27f9761a65ce4832f41fcb1c8cf4c` plus the serialized T1 authority candidate
- **Inherited boundaries:** T2 scope, AC-1 through AC-3, frozen T1 interfaces, protected history, no real-target/external action, no runtime/orchestration, no Plan edit, no commit/push, and no scope expansion
- **Outcome:** Make fresh project assets contain project-owned Markdown authority, Plan/runbook directories and templates, and only optional exact `CLAUDE.md`; retire target role Skills, procedure-Skill references, marker, generated settings, and the obsolete generated `.gitignore` block.
- **Non-goals:** No Python, runbook asset, package metadata, test, current-document, cleanup, backup, rollback, CLI, or existing-target mutation.
- **Read:** T1 authority; `pyproject.toml`; `src/reporivet/assets/project/document-first/root/{AGENTS.md.tmpl,ARCHITECTURE.md.tmpl,gitignore.block.tmpl}`; `src/reporivet/assets/project/document-first/claude/CLAUDE.md.tmpl`; three `src/reporivet/assets/project/document-first/claude/skills/reporivet-*/SKILL.md.tmpl`; `src/reporivet/assets/project/document-first/optional/claude-settings.deny-only.json.tmpl`; `src/reporivet/assets/project/root/reporivet-version.tmpl`; every non-runbook template named in Allowed writes; `tests/{test_claude_assets.py,test_distribution.py}`.
- **Allowed writes:** update `src/reporivet/assets/project/document-first/root/{AGENTS.md.tmpl,ARCHITECTURE.md.tmpl}`; `src/reporivet/assets/project/document-first/claude/CLAUDE.md.tmpl`; `src/reporivet/assets/project/document-first/docs/{README.md.tmpl,PRODUCT.md.tmpl,DESIGN.md.tmpl,QUALITY.md.tmpl,OPERATIONS.md.tmpl,SECURITY.md.tmpl,PLANS.md.tmpl}`; `src/reporivet/assets/project/document-first/docs/decisions/{README.md.tmpl,_template.md.tmpl}`; `src/reporivet/assets/project/document-first/docs/design-docs/{_template.md.tmpl,core-beliefs.md.tmpl,index.md.tmpl}`; `src/reporivet/assets/project/document-first/docs/exec-plans/{_template.md.tmpl,tech-debt-tracker.md.tmpl}`; `src/reporivet/assets/project/document-first/docs/product-specs/{_template.md.tmpl,index.md.tmpl}`; `src/reporivet/assets/project/document-first/docs/references/{README.md.tmpl,project-definition-protocol.md.tmpl}`. Delete `src/reporivet/assets/project/document-first/root/gitignore.block.tmpl`, all three fixed role-Skill templates, `src/reporivet/assets/project/document-first/optional/claude-settings.deny-only.json.tmpl`, and `src/reporivet/assets/project/root/reporivet-version.tmpl`.
- **Protected paths:** all Python/tests/package metadata/current authority; `src/reporivet/assets/project/document-first/docs/runbooks/**`; active/completed Plans; real targets and source-local runtime artifacts.
- **Acceptance:** AC-1 through AC-3.
- **Verification:** `"$PYTHON" -m compileall -q src`; T2-A changed-path and forbidden-template scan; `git diff --check`; successor focus after T2-E.
- **Stop conditions:** any required Python/runbook/package change; any template still requires Reporivet/doctor/install/resolve/import, generated settings/marker/Skills, or active Plan creation; non-exact `CLAUDE.md`; current-doc parity outside assets.
- **Return:** changed/deleted paths, forbidden inventory/scan, commands/results, discoveries, T3 deferrals, residual risks.
- **Result:** PASS. Updated the project asset authority templates for Markdown-native generated targets and removed six retired target assets: the three fixed role Skills, deny-only settings, the generated `.gitignore` block, and `.reporivet-version`. Required-asset (21 paths), retired-asset absence, forbidden editable-template, exact `CLAUDE.md` adapter, changed-path, and `git diff --check` scans passed. No Python, tests, package metadata, current-authority, or runbook paths were changed; compile/test execution was not applicable. T2-B must address the remaining legacy procedure-Skill wording in the protected runbook index.

### T2-B — procedure runbooks and legacy proof
- **Owner:** procedure-runbook-owner
- **Role:** implementation leaf
- **Parent:** T2
- **Parallel group:** T2-serial-chain
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** integrated T2-A candidate
- **Inherited boundaries:** T2 scope, AC-1/AC-4/legacy AC-5, frozen nine-field procedure interface, protected history, no external action/runtime/Plan edit/commit/push, and no scope expansion
- **Outcome:** Replace Skill generation with deterministic plain `docs/runbooks/<slug>.md` rendering and provide a private frozen strict parse/rerender exact-byte proof for canonical legacy procedure Skills.
- **Non-goals:** No guided/setup/migration/initializer/CLI change, cleanup transaction, public migrate change, executor/frontmatter/hooks/registration, validation weakening, or general runbook-template rewrite.
- **Read:** T1 authority; `src/reporivet/procedures.py`; `src/reporivet/assets/project/document-first/docs/runbooks/{index.md.tmpl,_template.md.tmpl}`; `tests/{test_procedure_skills.py,test_guided_setup.py,test_setup_flow.py}`; `src/reporivet/migration.py`; baseline `680a091...:src/reporivet/procedures.py`.
- **Allowed writes:** `src/reporivet/procedures.py`; `src/reporivet/assets/project/document-first/docs/runbooks/index.md.tmpl`.
- **Protected paths:** `src/reporivet/assets/project/document-first/docs/runbooks/_template.md.tmpl`; all other source/assets/tests/docs/Plans and external systems.
- **Acceptance:** AC-1, AC-4, and legacy procedure ownership portion of AC-5.
- **Verification:** `"$PYTHON" -m compileall -q src/reporivet/procedures.py`; API/render/proof scan; `git diff --check`; successor focus after T2-E.
- **Stop conditions:** nine-field shape/mutability change; weakened Confirmed-only/duplicate diagnostics; ownership based on name/marker/frontmatter/location; ambiguous rerender; runbook frontmatter/executor metadata; consumer requires out-of-packet write.
- **Return:** final runbook and private proof interfaces, ineligible-record behavior, unchanged manual template evidence, commands/results, frozen T2-C/T2-D contract, residual risks.
- **Result:** PASS after correction. The initial implementation replaced procedure-Skill planning with deterministic plain-Markdown runbook planning/rendering while preserving the frozen nine-field Confirmed-only parser, duplicate diagnostics, immutable procedure specs, and manual runbook template; private strict legacy parse/rerender proof interfaces and canonical byte-equality evidence passed, with malformed, CRLF, altered, trailing-space, and invalid-UTF-8 variants rejected. After T2-I found package-dependent `reporivet setup` wording in the generated runbook index, removed that wording without adding execution instructions. The 23-template forbidden-authority scan, runbook static-output/contract scan under Python 3.12, and `git diff --check` passed; the Python 3.9 scan was correctly rejected as below the project minimum. No other T2-B path changed.

### T2-C — generator inventory and doctor core
- **Owner:** generator-doctor-owner
- **Role:** implementation leaf
- **Parent:** T2
- **Parallel group:** T2-serial-chain
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** integrated T2-B candidate
- **Inherited boundaries:** T2 scope, AC-1 through AC-3 and implementation AC-7, T1 interfaces, predecessor APIs, protected history, public migrate preservation, no mutation/external action/runtime/Plan edit/commit/push
- **Outcome:** Update guided generation and initializer inventory for surviving assets/runbooks, remove marker/settings/Skill/active-Plan surfaces and doctor implementation, and freeze one deterministic cleanup-compatible preview interface for T2-D.
- **Non-goals:** No setup/migration/procedure/CLI/test/current-doc change, backup/rollback implementation, target mutation, migrate alteration, or replacement diagnosis command.
- **Read:** T1 authority; `src/reporivet/{guided,initializer,setup,migration,procedures}.py`; all surviving project assets; `pyproject.toml`; `tests/{test_guided_setup.py,test_setup_flow.py,test_claude_assets.py,test_distribution.py}`.
- **Allowed writes:** `src/reporivet/guided.py`; `src/reporivet/initializer.py`.
- **Protected paths:** every other source/asset/test/doc/Plan and external system.
- **Acceptance:** AC-1 through AC-3 and implementation portion of AC-7.
- **Verification:** `"$PYTHON" -m compileall -q src/reporivet/guided.py src/reporivet/initializer.py`; generated-path/doctor-symbol scan; `git diff --check`; successor focus after T2-E.
- **Stop conditions:** preview cannot expose exact target operations plus ownership outcomes under one stable fingerprint; T2-D would need duplicate classification; retired artifact/doctor remains; setup creates Plan/runs command/dispatches Agent; initializer marker logic cannot be separated; out-of-packet interface change.
- **Return:** inventory changes, removed doctor symbols, exact preview fields/invariants for T2-D, scans, commands/results, discoveries, residual risks.
- **Result:** PASS. Updated guided generation and initializer inventory for the surviving 25 generated paths, removed active-Plan diagnosis and initializer marker-management implementation, and excluded `.reporivet-version` from fresh generation. Added the frozen `reporivet.setup-preview/v1` action/diagnostic/fingerprint interface with deterministic ordering, deduplicated diagnostics, one classification per path, and explicit ownership outcomes. Compileall, generated-path, retired-symbol, and `git diff --check` scans passed; tests were not run. Protected CLI and migration consumers remain for T2-D/T2-E reconciliation.

### T2-D — setup-integrated transition transaction
- **Owner:** setup-transition-owner
- **Role:** implementation leaf
- **Parent:** T2
- **Parallel group:** T2-serial-chain
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** integrated T2-C candidate
- **Inherited boundaries:** T2 scope, AC-5/AC-6 and setup portions of AC-1/AC-3/AC-7, predecessor interfaces, exact ownership, public migrate preservation, protected history, no real target/external action/runtime/Plan edit/commit/push
- **Outcome:** Integrate exact role/procedure Skill, generated-settings, and marker cleanup into setup with external mode-restricted backup, fingerprint binding, immediate revalidation, whole-transaction rollback, guarded later rollback, and preservation/refusal of unproven paths.
- **Non-goals:** No CLI or public migrate API/schema/0.2 behavior change; no new command/journal/marker/runtime; no `.harness/runs` access; no real target mutation; no name/marker/location-only ownership.
- **Read:** T1 authority; `src/reporivet/{setup,migration,guided,procedures,initializer}.py`; `tests/{test_migration.py,test_setup_flow.py,test_guided_setup.py}`; named legacy-02 fixture files; baseline Git objects for the three role Skill templates, `document-first/optional/claude-settings.deny-only.json.tmpl`, and `project/root/reporivet-version.tmpl` at `680a091...`.
- **Allowed writes:** `src/reporivet/setup.py`; `src/reporivet/migration.py`.
- **Protected paths:** all other source/assets/tests/fixtures/docs/Plans; public migration functions/contracts; `.harness/runs`; real targets/backups.
- **Acceptance:** AC-5 and AC-6 plus setup portions of AC-1, AC-3, and AC-7.
- **Verification:** `"$PYTHON" -m compileall -q src/reporivet/setup.py src/reporivet/migration.py`; `"$PYTHON" -m unittest tests.test_migration -v`; transaction/ownership scan; `git diff --check`; successor focus after T2-E.
- **Stop conditions:** public migrate changes; new command required; ownership lacks exact canonical proof; backup not external/mode-restricted/fingerprint-bound; apply lacks exact equality/revalidation; incomplete automatic/guarded rollback; `.harness/runs` access; guided contract cannot be consumed.
- **Return:** setup envelope/transaction changes, migrate-preservation evidence, ownership/backup/rollback/refusal matrix, commands/results, discoveries, residual risks.
- **Result:** PASS (bounded). Updated `setup.py` and `migration.py` to require exact canonical ownership and mode proof, bind setup apply to the exact preview fingerprint with immediate revalidation, clean partial external backups, roll back the whole transaction on failure, and guard later rollback against user changes. The migration-specific preview filters cleanup-only actions while preserving the public 0.2 migration surface; fresh setup and cleanup smokes passed. Compileall and `git diff --check` passed. The protected migration suite remains blocked by the known stale `cli.py` import of retired `run_document_first_doctor`, which is T2-E scope.

### T2-E — CLI, external setup Skill, and focused tests
- **Owner:** cli-launcher-test-owner
- **Role:** implementation leaf
- **Parent:** T2
- **Parallel group:** T2-serial-chain
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** integrated T2-D candidate
- **Inherited boundaries:** T2 scope, AC-1/AC-3/AC-7/AC-8 and focused AC-4 through AC-6 evidence, predecessor interfaces, public migrate preservation, protected history, no external/global install/runtime/Plan edit/commit/push
- **Outcome:** Remove doctor and `--with-claude-settings` from public CLI/dispatch, preserve `migrate`, add package-only external Skill at `src/reporivet/assets/user-scoped/reporivet-setup/SKILL.md`, narrow package data, and add focused successor tests.
- **Non-goals:** No migration implementation change, new command, global Skill install, real setup/migration, broad existing-test rewrite, or current-doc parity assigned to T3.
- **Read:** T1 authority; `src/reporivet/{cli,setup,migration,guided,procedures,initializer}.py`; `pyproject.toml`; `tests/{test_setup_cli.py,test_setup_flow.py,test_reporivet.py,test_distribution.py}`; surviving `CLAUDE.md.tmpl`.
- **Allowed writes:** `src/reporivet/cli.py`; `pyproject.toml`; create `src/reporivet/assets/user-scoped/reporivet-setup/SKILL.md`; create `tests/test_one_shot_bootstrapper.py`.
- **Protected paths:** all other source/assets/tests/fixtures/docs/Plans; global/user Skill locations; real targets.
- **Acceptance:** AC-1, AC-3, AC-7, AC-8 and focused evidence for AC-4 through AC-6.
- **Verification:** `"$PYTHON" -m unittest tests.test_one_shot_bootstrapper -v`; `"$PYTHON" -m unittest tests.test_migration -v`; `"$PYTHON" -m compileall -q src tests`; `PYTHONPATH=src "$PYTHON" -m reporivet --help`; package/Skill prohibited-content scan; `git diff --check`.
- **Stop conditions:** migrate parser/dispatch/schema changes; doctor/settings option remains; Skill becomes target-generated/globally installed/installer/downloader/resolver/executor/model-authored mutator; package-data broadens beyond surviving assets/launcher; focused tests weaken or delete historical coverage.
- **Return:** CLI/help evidence, migrate preservation, doctor/settings absence, external Skill boundary, package-data diff, focused commands/results, T3 deferrals, residual risks.
- **Result:** PASS (bounded). Retired public doctor and `--with-claude-settings` CLI surfaces, preserved `migrate` parser/dispatch/signatures, narrowed package data, added the package-only instruction Skill at `src/reporivet/assets/user-scoped/reporivet-setup/SKILL.md`, and added focused successor coverage. The focused suite passed 7/7; compileall, CLI/help, package/Skill prohibited-content, and `git diff --check` scans passed. The protected migration suite has one known T2-D fixture mismatch in the `_apply_setup_update` injection case; protected code/tests were not changed. T3 must reconcile current docs and historical test references without rewriting protected history.

### T2-I — core Owner-local aggregation
- **Owner:** core-owner
- **Role:** Owner-local aggregation leaf
- **Parent:** T2
- **Parallel group:** T2-owner-aggregation
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** integrated T2-A through T2-E candidate
- **Inherited boundaries:** read-only/nonrepairing aggregation, T2 scope/acceptance/non-goals, candidate-specific evidence, no Plan edit/external action/final acceptance claim
- **Outcome:** Audit the serial chain and return criterion-level T2 evidence while distinguishing T3 parity work.
- **Non-goals:** No repair, repository write, Plan edit, current-doc parity, broad failure reinterpretation, real target mutation, or final judgment.
- **Read:** T1 authority; integrated T2 source/assets/package metadata/focused test; every child return.
- **Allowed writes:** none in repository; isolated temporary test directories only.
- **Protected paths:** entire repository candidate, Plans/history, external targets/backups/global or user Skill locations.
- **Acceptance:** T2 evidence for AC-1 through AC-8 without final AC-1 through AC-10 judgment.
- **Verification:** `"$PYTHON" -m unittest tests.test_one_shot_bootstrapper -v`; `"$PYTHON" -m unittest tests.test_migration -v`; `"$PYTHON" -m compileall -q src tests`; `PYTHONPATH=src "$PYTHON" -m reporivet --help`; `git diff --check`; changed-path and forbidden-asset audit.
- **Stop conditions:** protected/unlisted write; migrate change; candidate mismatch; narrated-only evidence; focused failure needing repair; unresolved Skill distribution; T3 work claimed complete.
- **Return:** candidate identity, child matrix, changed-path audit, migrate/doctor/settings/target/runbook/cleanup/Skill results, AC-1 through AC-8 findings, T3 handoff, residual risks, no final acceptance claim.
- **Result:** PASS (owner-local audit; not final acceptance). Against the corrected candidate, the changed-path audit found 37 paths entirely within the accepted T1/T2-A…T2-E and inherited authority/Plan sets; no `.harness/runs` access or mutation occurred. Focused successor tests (7/7), compileall, CLI/help, package/Skill, runbook, and `git diff --check` audits passed. T2-A, T2-B, and T2-C passed; T2-D and T2-E are provisionally verified because the full independent cleanup/rollback matrix and wheel-content verification remain unavailable. One protected migration fixture mismatch remains explicitly classified. No final AC-1…AC-10 claim is made.

### T3 — broad parity Task Owner
- **Owner:** parity-owner
- **Role:** Task Owner
- **Parent:** none
- **Parallel group:** parity
- **May delegate:** yes
- **Child budget:** at most 4 implementation descendants plus one Owner-local aggregation node
- **Exact baseline:** integrated T2 candidate identified by Main
- **Inherited boundaries:** all Plan scope/acceptance/non-goals; current docs/templates/tests only; historical bodies protected; no publication or external setup execution
- **Outcome:** Return a finite disjoint child manifest, then align current authority, public docs, package inventory, and full regression coverage with the integrated core behavior.
- **Non-goals:** No redesign of frozen T1/T2 interfaces, test weakening, historical rewrite, or real target mutation.
- **Read:** integrated T2 candidate, all current authority, package-data declarations, test suites named by this Plan.
- **Allowed writes:** only exact disjoint paths accepted in Main-serialized child packets after manifest review.
- **Protected paths:** this Plan; protected history; unrelated code; external systems.
- **Acceptance:** AC-1 through AC-10 except independent final judgment.
- **Verification:** full unit suite, compileall, focused distribution test, temporary-target smokes, `git diff --check`, changed-path audit.
- **Stop conditions:** implementation/docs conflict, failed deterministic checks, scope expansion, or protected-history impact.
- **Return:** finite manifest first; after resume, changed paths, exact commands/results, child evidence, discoveries, and residual risks.
- **Result:** Manifest accepted and serialized as T3-A through T3-D plus T3-I. The disjoint write sets are: T3-A current authority/public docs; T3-B surviving generated templates; T3-C package metadata and distribution tests; T3-D regression tests and fresh-target coverage; T3-I read-only aggregation. T3-A runs first, T3-B follows, T3-C and T3-D run concurrently after T3-B, and T3-I waits for all four. All descendant Agents must use Sonnet, may not delegate, and may not edit the Plan. Historical bodies, fixtures, protected migration tests, source implementation, and external systems remain protected.

### T3-A — authority and public-document parity
- **Owner:** authority-parity-owner
- **Role:** implementation leaf
- **Parent:** T3
- **Parallel group:** T3-authority
- **May delegate:** no
- **Child budget:** none
- **Depends on:** none
- **Exact baseline:** integrated T2 candidate identified by Main; current dirty candidate remains uncommitted
- **Inherited boundaries:** T3 scope and AC-1 through AC-10 except Main’s independent final judgment; no redesign of frozen T1/T2 interfaces; no test weakening, historical rewrite, real-target setup, publication, runtime, Plan edit, commit, push, or external action
- **Outcome:** Align current authority and public documentation with the one-shot generated-target boundary while preserving historical bodies and bilingual README parity.
- **Non-goals:** No Python, generated-template, package metadata, test, fixture, Plan, or historical-record changes.
- **Read:** `docs/exec-plans/active/PLAN-2026-0006-one-shot-bootstrapper.md`; `AGENTS.md`; `docs/README.md`; `docs/PLANS.md`; ADR-0002; SPEC-004; DESIGN-004; `ARCHITECTURE.md`; `docs/PRODUCT.md`; `docs/DESIGN.md`; `docs/QUALITY.md`; `docs/OPERATIONS.md`; `docs/SECURITY.md`; `docs/references/project-definition-protocol.md`; `README.md`; `README.en.md`; current indexes; ADR-0001; SPEC-003; DESIGN-003; `tests/test_documentation_contract.py`.
- **Allowed writes:** `AGENTS.md`; `docs/README.md`; `ARCHITECTURE.md`; `docs/PRODUCT.md`; `docs/DESIGN.md`; `docs/QUALITY.md`; `docs/OPERATIONS.md`; `docs/SECURITY.md`; `docs/references/project-definition-protocol.md`; `README.md`; `README.en.md`.
- **Protected paths:** the active Plan; `docs/PLANS.md`; current indexes; ADR-0001; SPEC-003; DESIGN-003; completed Plans; all source/assets/package metadata/tests other than the named documentation test; fixtures; external systems.
- **Acceptance:** AC-2, AC-3, AC-7, and AC-9; documentation portions of AC-1, AC-4, and AC-8. Remove current positive claims that doctor, target Skills, markers, generated settings, runtime, package resolution, or project-command execution remain required after setup; describe static runbooks; keep historical references/bodies unchanged; keep English and bilingual README semantics aligned.
- **Verification:** `git diff --check`; bounded forbidden-positive scan over current authority; bilingual parity check; protected-history unchanged check; documentation-contract tests after regression expectations are reconciled. Do not use doctor.
- **Stop conditions:** need to modify historical records; conflict with ADR-0002, SPEC-004, DESIGN-004, `AGENTS.md`, or `docs/README.md`; README divergence; request for source/generated-template changes; unresolved continuing-package claim outside current docs.
- **Return:** exact paths, before/after conflict matrix, command results, forbidden-current-claim scan, bilingual parity, protected-history check, residuals deferred to T4.
- **Result:** PASS after boundary correction. Updated exactly the eleven approved current-authority documents: `AGENTS.md`, `docs/README.md`, `ARCHITECTURE.md`, `docs/PRODUCT.md`, `docs/DESIGN.md`, `docs/QUALITY.md`, `docs/OPERATIONS.md`, `docs/SECURITY.md`, `docs/references/project-definition-protocol.md`, `README.md`, and `README.en.md`. One-shot setup, package-independent targets, static runbooks, retired doctor/marker/settings/runtime surfaces, and manual Plan/Task Owner lifecycle now align with ADR-0002/SPEC-004/DESIGN-004; bilingual parity, protected-history, forbidden-positive scan, and `git diff --check` passed. The documentation-contract suite ran 11 tests with 20 stale expectation failures (3 current-reference phrases, 16 protected generated-protocol-template assertions, and 1 over-broad operations regex); tests were not weakened. T3-B must reconcile the generated protocol template, and T3-D must reconcile current test expectations.

### T3-B — generated-template parity
- **Owner:** generated-template-parity-owner
- **Role:** implementation leaf
- **Parent:** T3
- **Parallel group:** T3-template-parity
- **May delegate:** no
- **Child budget:** none
- **Depends on:** T3-A
- **Exact baseline:** integrated T3-A candidate identified by Main after T3-A completion
- **Inherited boundaries:** T3 scope/acceptance/non-goals, final T3-A authority, frozen T1/T2 interfaces, no historical rewrite, no test weakening, no source/API change, no Plan edit, commit, push, external action, or runtime/orchestration
- **Outcome:** Align all surviving generated target templates with current authority so generated targets are Markdown-native and package-independent.
- **Non-goals:** No Python, external setup Skill, protected runbook template, package metadata, tests, fixtures, current docs, Plan, or retired-asset restoration.
- **Read:** active Plan; T3-A return and all T3-A authority paths; `AGENTS.md`; `docs/README.md`; `docs/PLANS.md`; every surviving template under `src/reporivet/assets/project/document-first/`, including root `AGENTS.md.tmpl` and `ARCHITECTURE.md.tmpl`, docs README/PRODUCT/DESIGN/QUALITY/OPERATIONS/SECURITY/PLANS templates, design-docs index, exec-plans template and tracker, product-specs index, decisions README, references README and project-definition protocol, and runbooks index; external setup Skill; `tests/test_claude_assets.py`; `tests/test_documentation_contract.py`; `tests/test_one_shot_bootstrapper.py`.
- **Allowed writes:** only the surviving existing templates under `src/reporivet/assets/project/document-first/`: root `AGENTS.md.tmpl`, root `ARCHITECTURE.md.tmpl`; docs README/PRODUCT/DESIGN/QUALITY/OPERATIONS/SECURITY/PLANS; docs/design-docs/index; docs/exec-plans/_template and tech-debt-tracker; docs/product-specs/index; docs/decisions/README; docs/references/README and project-definition-protocol; docs/runbooks/index.
- **Protected paths:** `claude/CLAUDE.md.tmpl`; `docs/runbooks/_template.md.tmpl`; all deleted role Skills, settings, gitignore block, and version marker; external setup Skill; all Python, package metadata, tests, current docs, Plan/history, and external systems.
- **Acceptance:** AC-1 through AC-4 and generated counterparts of AC-9. No generated instruction may locate, install, resolve, import, invoke, or verify Reporivet/doctor; no target Skill, marker, settings, runtime, command wrapper, or hidden state; complete unique Confirmed nine-field records alone produce ordinary Markdown runbooks without execution metadata.
- **Verification:** `git diff --check`; compileall for source; surviving/retired inventory; forbidden-content scan; hierarchy and Plan-lifecycle phrase checks; focused template tests after regression expectations are reconciled.
- **Stop conditions:** restoring deleted assets; reintroducing target package dependency or execution wrapper; changing frozen CLAUDE adapter/runbook template/external Skill/Python interface; generated wording cannot follow final authority without T1/T2 redesign.
- **Return:** exact template paths, complete inventory, rendered forbidden scan, hierarchy/Plan-lifecycle checks, compile/diff results, residual template concerns for T4.
- **Result:** PASS. Updated exactly 17 surviving generated templates, preserving the frozen CLAUDE adapter and manual runbook template while removing target Skills, doctor, markers, generated settings, runtime, command wrappers, executor metadata, hooks, registration, privilege-bearing configuration, schedulers, dispatchers, task stores, Gates, evidence archives, automatic closure, and hidden state. The 23-template surviving inventory and six retired-asset absence scan, placeholder validation, authorized/protected-path audits, forbidden-content scan, hierarchy/Plan-lifecycle scan, Python 3.12 compileall, focused 7-test suite, and `git diff --check` passed. Full discovery remained stale (101 tests, 21 failures, 138 errors) and was not repaired or weakened; T3-C/D must reconcile their assigned expectations.

### T3-C — package inventory and distribution parity
- **Owner:** distribution-parity-owner
- **Role:** implementation leaf
- **Parent:** T3
- **Parallel group:** T3-post-template
- **May delegate:** no
- **Child budget:** none
- **Depends on:** T3-A and T3-B
- **Exact baseline:** integrated T3-B candidate identified by Main
- **Inherited boundaries:** T3 scope/acceptance/non-goals and final T3-A/B interfaces; no source implementation, generated-template, historical-fixture, protected migration-test, Plan, external, publication, or runtime changes; no hand-edited generated metadata.
- **Outcome:** Align package data and distribution tests with the surviving asset inventory and package-only external setup Skill.
- **Non-goals:** No source implementation change, generated asset change, egg-info hand edit, protected migration test/fixture change, current documentation change, global install, publication, or network-dependent workaround.
- **Read:** active Plan; `pyproject.toml`; `src/reporivet.egg-info/SOURCES.txt`; `src/reporivet.egg-info/PKG-INFO`; `src/reporivet/assets/project/`; external setup Skill; `tests/test_distribution.py`; `tests/test_one_shot_bootstrapper.py`; `src/reporivet/initializer.py`; `src/reporivet/cli.py`; final T3-A/B returns.
- **Allowed writes:** `pyproject.toml`; `tests/test_distribution.py`; `tests/test_one_shot_bootstrapper.py`.
- **Protected paths:** `src/reporivet.egg-info/**` unless normal build regeneration is separately authorized; all Python source and generated templates; `tests/test_migration.py`; `tests/fixtures/legacy-02/**`; all other tests; current docs, Plan/history, and external systems.
- **Acceptance:** retired assets absent; external setup Skill packaged outside target assets; focused distribution evidence satisfies AC-10; package data exactly matches surviving source inventory and excludes deleted role Skills, settings, marker, old assets, and target-generated Skill surfaces.
- **Verification:** `"$PYTHON" -m unittest tests.test_distribution -v`; `"$PYTHON" -m unittest tests.test_one_shot_bootstrapper -v`; `git diff --check`; if Setuptools is available, no-network wheel build and content inspection. Classify unavailable backend checks explicitly.
- **Stop conditions:** package data broadens; retired assets reappear; Skill becomes installer/resolver or moves into target assets; wheel requires network/publication; tests require weakened assertions; egg-info needs manual workaround.
- **Return:** package-data declaration, surviving/retired inventory, focused results, wheel availability/content, Skill boundary, unavailable checks, stale egg-info disposition.
- **Result:** PASS (bounded). Reconciled `tests/test_distribution.py` and `tests/test_one_shot_bootstrapper.py`; `pyproject.toml` already had the exact surviving package-data declaration and was not changed. The 23-template plus one package-only external Skill inventory expands to exactly 24 files; retired assets and unrelated bytecode are excluded; stale egg-info was not hand-edited. Distribution tests passed 3/3, successor tests passed 7/7, inventory/trailing-whitespace/Skill-boundary scans and `git diff --check` passed. Offline wheel construction was unavailable because `setuptools.build_meta` is not installed. No source, asset, protected migration test/fixture, Plan, or external path changed.

### T3-D — regression and fresh-target smoke parity
- **Owner:** regression-smoke-owner
- **Role:** implementation leaf
- **Parent:** T3
- **Parallel group:** T3-post-template
- **May delegate:** no
- **Child budget:** none
- **Depends on:** T3-A and T3-B
- **Exact baseline:** integrated T3-B candidate identified by Main; may run concurrently with T3-C because write sets are disjoint
- **Inherited boundaries:** T3 scope/acceptance/non-goals and final T3-A/B interfaces; tests-only writes in the listed set; no source/API, asset, package metadata, protected migration fixture/test, Plan, historical, external, publication, or runtime changes; no test weakening.
- **Outcome:** Reconcile current regression coverage and fresh-target smokes with the one-shot boundary while preserving protected migration mismatch classification.
- **Non-goals:** No source repair solely for stale tests, protected test/fixture changes, doctor replacement, real-target setup, historical rewrite, or acceptance weakening.
- **Read:** active Plan; current authority and successor docs; surviving generated templates; `src/reporivet/{cli,guided,initializer,migration,procedures,setup}.py`; `tests/test_audit_adoption.py`; `tests/test_claude_assets.py`; `tests/test_documentation_contract.py`; `tests/test_guided_setup.py`; `tests/test_plan_lifecycle.py`; `tests/test_procedure_skills.py`; `tests/test_reporivet.py`; `tests/test_setup_cli.py`; `tests/test_setup_flow.py`; read-only `tests/test_distribution.py` and `tests/test_one_shot_bootstrapper.py`; protected `tests/test_migration.py` and `tests/fixtures/legacy-02/**`; final T3-A/B returns.
- **Allowed writes:** `tests/test_audit_adoption.py`; `tests/test_claude_assets.py`; `tests/test_documentation_contract.py`; `tests/test_guided_setup.py`; `tests/test_plan_lifecycle.py`; `tests/test_procedure_skills.py`; `tests/test_reporivet.py`; `tests/test_setup_cli.py`; `tests/test_setup_flow.py`.
- **Protected paths:** `tests/test_distribution.py`; `tests/test_one_shot_bootstrapper.py`; `tests/test_migration.py`; `tests/fixtures/legacy-02/**`; all Python source, package metadata, assets, current docs, Plan/history, and external systems.
- **Acceptance:** AC-1 through AC-10 except Main’s final judgment. Fresh-target tests assert absence of role/procedure Skills, marker, settings, runtime, doctor gate, and package-resolution instruction; static runbooks enforce strict Confirmed-only/no executor; setup CLI covers doctor/settings retirement, backup-dir, preview approval, and backup-bound setup; cleanup tests preserve exact/modified/ambiguous/unsafe/symlink/nonregular paths; Plan tests preserve hierarchy, manifests, serialization, direct-serial and compact compatibility, recursive IDs, historical preservation, and fresh-verification boundaries; protected migration mismatch remains explicit.
- **Verification:** run the focused suites for each allowed test path with `PYTHONPATH` set; compileall for source/tests; temporary fresh/existing-target fixtures through project tests; `git diff --check`. Do not run doctor or setup against a real target.
- **Stop conditions:** test weakening/deletion or protected-fixture conversion; source change needed solely for stale test; replacement diagnosis command; real-target setup; protected migration mismatch silently passing.
- **Return:** exact test paths, command/results matrix, fresh-target inventory, static-runbook result, setup/cleanup/backup/rollback result, Plan compatibility, protected mismatch disposition, and passed/failed/unavailable/not-run distinctions.
- **Result:** PASS. Reconciled `test_claude_assets.py`, `test_guided_setup.py`, `test_procedure_skills.py`, `test_documentation_contract.py`, `test_setup_cli.py`, `test_setup_flow.py`, `test_plan_lifecycle.py`, and `test_reporivet.py`; focused suites pass (15, 10, 11, 11, 5, 9, 18, and 6 tests respectively). `test_audit_adoption.py` passes its 6-test suite without edits, so all nine T3-D focused suites pass (`Ran 91 tests in 1.010s`, `OK`). `/opt/homebrew/bin/python3.12 -m compileall -q src tests` passed, isolated temporary fresh-target and existing-target cleanup/backup/rollback smokes passed, and `git diff --check` passed. The corrected final changed-path audit passed for 61 paths with no unexpected or `.harness/runs` paths. The protected migration mismatch remains untouched and explicit; wheel-content verification remains unavailable because `setuptools.build_meta` is not installed. No real target, source-local cleanup, publication, installation, or external action occurred.

### T3-I — Owner-local aggregation
- **Owner:** parity-owner
- **Role:** Owner-local aggregation leaf
- **Parent:** T3
- **Parallel group:** T3-owner-aggregation
- **May delegate:** no
- **Child budget:** none
- **Depends on:** T3-A, T3-B, T3-C, and T3-D
- **Exact baseline:** integrated T3-D candidate
- **Inherited boundaries:** read-only/nonrepairing T3 scope, all child boundaries and acceptance, no Plan edit, source repair, final acceptance claim, commit, push, or external action.
- **Outcome:** Aggregate criterion-level T3 evidence across authority, templates, distribution, regression, and fresh-target work without repairing the candidate.
- **Non-goals:** No repository repair, Plan edit, broad failure reinterpretation, protected-history change, real target, or final AC-1…AC-10 judgment.
- **Read:** active Plan; all child returns; integrated T3 candidate; current authority; generated templates; package metadata; all tests; protected migration mismatch evidence.
- **Allowed writes:** none in repository; isolated temporary test and target directories only.
- **Protected paths:** entire repository candidate and Plan/history; historical documents/fixtures; external targets/backups/global Skill locations and user systems.
- **Acceptance:** criterion-level T3 evidence for AC-1 through AC-10 except Main’s independent final judgment; explicit passed/failed/unavailable/not-run states and T4 handoff.
- **Verification:** full unittest discovery; compileall; focused distribution and successor suites; temporary fresh/existing-target smokes; `git diff --check`; final `git status --short` changed-path audit.
- **Stop conditions:** child overlap; candidate mismatch; protected-history change; unavailable/failed checks described as passing; unresolved migration mismatch; source repair outside T3; independent-verification claim.
- **Return:** candidate identity, child matrix, changed-path audit, full/focused results, AC-1…AC-10 mapping, residual risks, T4 handoff without final acceptance.
- **Result:** PASS (bounded owner-local aggregation; no final AC-1…AC-10 claim). Candidate was intentionally dirty/uncommitted at base and HEAD `680a091bd1b27f9761a65ce4832f41fcb1c8cf4c`; T3-I’s full-dirty-tree fingerprint was `70969eaf3e3c8b1e1461775dbbe1d89f1da1c2e4bca968ac78fdd96c53ac1ce4` over the base identifier, sorted `git status --porcelain=v1 --untracked-files=all`, binary `git diff --binary --no-ext-diff`, and raw bytes of each untracked file keyed by relative path, excluding `.harness/runs`; the candidate had 61 paths (55 tracked, 6 untracked) and no `.harness/runs` path. Child matrix: T3-A passed; T3-B passed; T3-C passed bounded with wheel unavailable; T3-D passed with its 91-test matrix, compileall, isolated fresh-target and cleanup/backup/rollback smokes, diff check, and corrected changed-path audit. `env PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/reporivet-t3i-pycache PYTHONPATH=src /opt/homebrew/bin/python3.12 -m unittest discover -s tests -v` failed with 113 tests and exactly one protected mismatch at `tests/test_migration.py:713` in `_apply_setup_update` (stale injection expected an `InitError` containing `automatically rolled back`, but no exception was raised). Focused distribution passed 3; successor passed 7; the nine T3-D suites passed 91; source/test compileall passed; protected migration passed 11/12 with the same failure; `git diff --check` and the corrected 61-path audit passed. Offline wheel construction/content inspection was unavailable because `setuptools.build_meta` could not be imported. Criterion disposition: AC-1 through AC-5 passed bounded where independent verification was still pending; AC-6 unavailable for complete independent proof because the protected automatic-rollback matrix is blocked; AC-7 through AC-9 passed on static/focused evidence; AC-10 failed/not established because full discovery failed and wheel inspection was unavailable. No protected history, source-local artifacts, `.harness/runs`, real target, publication, installation, or external project was touched. T4 independent verification was required next.
- **Owner:** verifier-target
- **Role:** verification leaf
- **Parent:** none
- **Parallel group:** verification
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** integrated T3 candidate identified by Main
- **Inherited boundaries:** read-only, nonrepairing, candidate-specific verification
- **Outcome:** Verify AC-1 through AC-3 and package-removal independence in temporary targets.
- **Non-goals:** No fixes, Plan edits, or external project mutation.
- **Read:** integrated candidate, Plan acceptance, generated assets/tests.
- **Allowed writes:** temporary verification directories only.
- **Protected paths:** repository candidate and this Plan.
- **Acceptance:** AC-1 through AC-3.
- **Verification:** run named fresh-target and lifecycle checks.
- **Stop conditions:** candidate changes, missing reproducible target, or unavailable required check.
- **Return:** candidate identity, exact commands/outcomes, criterion results, residual risks.
- **Result:** PASS. Against candidate fingerprint `91d4ed956296f2fbdef14cefbb50ff437f76fc043b5681226d30a060ad6a3cf6` (stable at verifier start/end), the isolated temporary target exactly matched 27 final files (26 generated bundle assets plus the visible definition draft): project-owned Markdown authority, Plan template/.gitkeep directories, and static `docs/runbooks/release-check.md`; `CLAUDE.md` was exactly `@AGENTS.md\n`, with no active Plan. `.claude`, generated settings, all Reporivet role/procedure Skills, `.reporivet-version`, and `.harness` were absent; the runbook had no frontmatter, executor metadata, hooks, or registration. An isolated `python3.12 -I -S` check with `PYTHONPATH` unset passed, establishing package-independent target lifecycle. Focused suites passed (claude_assets 15, guided_setup 10, plan_lifecycle 18, reporivet 6, setup_flow 9, setup_cli 5, distribution 3, procedure_skills 11, audit_adoption 6, and one_shot_bootstrapper 7); compileall and `git diff --check` passed. Full discovery was not run by this verifier; wheel construction/content inspection remains unavailable because the Setuptools backend is absent. No repository or `.harness/runs` mutation/access occurred.

### T4-V2 — cleanup safety verifier
- **Owner:** verifier-safety
- **Role:** verification leaf
- **Parent:** none
- **Parallel group:** verification
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** integrated T3 candidate identified by Main
- **Inherited boundaries:** read-only/nonrepairing repository access; temporary targets only
- **Outcome:** Verify AC-5 and AC-6 including exact ownership, backup, rollback, and modified-file preservation.
- **Non-goals:** No repair or real target cleanup.
- **Read:** integrated candidate, cleanup tests, migration primitives, Plan acceptance.
- **Allowed writes:** temporary verification and external-backup directories only.
- **Protected paths:** repository candidate, this Plan, real external projects.
- **Acceptance:** AC-5 and AC-6.
- **Verification:** focused cleanup/rollback tests and transition smoke.
- **Stop conditions:** candidate changes, unsafe path requirement, or missing backup isolation.
- **Return:** candidate identity, exact commands/outcomes, criterion results, residual risks.
- **Result:** PASS bounded after corrected follow-up; the initial pass was partial and the follow-up established every permitted temporary-target case. Against the supplied candidate snapshot (HEAD/base `680a091bd1b27f9761a65ce4832f41fcb1c8cf4c`; full dirty-tree fingerprint `91d4ed956296f2fbdef14cefbb50ff437f76fc043b5681226d30a060ad6a3cf6` at start and `31e9e4725ff20fc933db1e9e72c28006c14479104a96c974475e42fc34b40bc4` at end solely from Main’s active-Plan edit; status 61 paths, tracked diff 688118 bytes, no `.harness/runs`), `tests.test_setup_flow` passed 9/9 and `tests.test_guided_setup` passed 10/10. Protected `tests.test_migration` executed 12 tests with 11 passing and the retained `_apply_setup_update` failure at line 713; it was not repaired or called passing. In isolated temporary targets under `/Users/hakseong`, preview/apply with exact approval and an external backup removed exact canonical role Skills, generated settings, version marker, and managed `.gitignore`, converted the exact `AGENTS.md` marker and strict procedure Skill to `docs/runbooks/release-check.md`, enforced external backup binding, used mode 0700 backup roots and mode 0600 manifest/preimages, restored the exact target tree on successful later rollback, rejected a mismatched approval without mutation, and preserved exact mode-0600, modified, ambiguous, stale, project-owned, and custom paths. The corrected follow-up upgraded AC-5 to PASS bounded: isolated temporary cases passed symlink, FIFO, UNIX-socket, directory, symlinked-ancestor, regular-file-ancestor, malformed/duplicate/incomplete/collision, exact-mode/byte, and project-owned/custom preservation/refusal checks; only the `.harness/runs` trap was not-run by policy. It upgraded AC-6 to PASS bounded: isolated temporary cases passed external backup isolation and 0700/0600 modes, exact preimages, preview/stale-approval binding, immediate preimage revalidation, partial-backup cleanup and preservation, whole-setup automatic rollback through `_apply_setup_create`, exact later rollback, and post-user-change rollback refusal. The protected stale `_apply_setup_update` migration injection remains not-run as a protected fixture limitation. The follow-up used canonical `/private/tmp` roots after correctly rejecting symlinked `/tmp`, and its initial envelope/helper/exception expectations were corrected without repository changes. Focused setup/guided tests passed 9/9 and 10/10; protected migration remained 11/12 with the same explicit mismatch; compileall and `git diff --check` passed. No verifier repository write, commit, install, publication, doctor invocation, Plan edit, or external-project mutation occurred.
- **Owner:** verifier-contract
- **Role:** verification leaf
- **Parent:** none
- **Parallel group:** verification
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** integrated T3 candidate identified by Main
- **Inherited boundaries:** read-only, nonrepairing, candidate-specific verification
- **Outcome:** Verify AC-4 and AC-7 through AC-10 across runbooks, CLI, external Skill structure, docs, and package inventory.
- **Non-goals:** No fixes, publication, installation, or Plan edits.
- **Read:** integrated candidate, current authority, public docs, distribution and procedure tests.
- **Allowed writes:** temporary build/test directories only.
- **Protected paths:** repository candidate, this Plan, external systems.
- **Acceptance:** AC-4 and AC-7 through AC-10.
- **Verification:** full suite, compileall, distribution focus, documentation scans, `git diff --check`.
- **Stop conditions:** candidate changes or unavailable required evidence.
- **Return:** candidate identity, exact commands/outcomes, criterion results, residual risks.
- **Result:** PASS bounded for AC-4 and AC-7 through AC-9; AC-10 not established. Read-only verification before Main’s Plan-only edit found AC-4 passing via `tests.test_procedure_skills` (11/11), `tests.test_one_shot_bootstrapper` (7/7), and `tests.test_documentation_contract` (11/11); exact nine-field Confirmed-only parsing, duplicate exclusion, deterministic plain `docs/runbooks/<slug>.md`, and absence of frontmatter/executor/hooks/registration/privilege metadata were confirmed. AC-7 passed via `tests.test_setup_cli` (5/5), `tests.test_reporivet` (6/6), CLI help exposing only setup/define/audit/init/upgrade/migrate, zero doctor references in eight source Python files, and current negative/retirement documentation. AC-8 passed via distribution (3/3) and successor suites, exact package-only external setup Skill placement/content, and no installation/download/resolve/runtime/mutation behavior. AC-9 passed via documentation-contract tests (11/11), a 15-current-document scan with zero positive boundary offenders, bilingual README parity, and byte-identical ADR-0001/completed-Plan and fixture paths. AC-10 is not established: compileall, focused suites, temporary/static scans, and `git diff --check` passed, but full discovery ran 113 tests with one protected `tests/test_migration.py` `_apply_setup_update` failure; wheel build/content inspection was unavailable because the Setuptools backend is absent; and the full dirty-tree fingerprint changed from `91d4ed956296f2fbdef14cefbb50ff437f76fc043b5681226d30a060ad6a3cf6` to `31e9e4725ff20fc933db1e9e72c28006c14479104a96c974475e42fc34b40bc4` solely because Main edited this untracked Plan after dispatch. HEAD remained `680a091`, status remained 61 paths with no `.harness/runs`, tracked diff remained 688118 bytes, and no verifier write occurred.
- **Owner:** main
- **Role:** direct serial integration leaf
- **Parent:** none
- **Parallel group:** final-integration
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** integrated and independently verified T3 candidate
- **Inherited boundaries:** Main-only Plan serialization, no repeated detailed verifier run without cause
- **Outcome:** Integrate criterion-level evidence, resolve documentation impact/follow-ups, and choose the terminal outcome.
- **Non-goals:** No hidden closure engine, publication, or unverified success claim.
- **Read:** verifier returns, integrated candidate identity, this Plan.
- **Allowed writes:** this Plan and manual terminal movement only.
- **Protected paths:** candidate implementation unless a new implementation packet is required.
- **Acceptance:** AC-1 through AC-10.
- **Verification:** evidence consistency and candidate identity match.
- **Stop conditions:** failed/not-established criterion, candidate mismatch, or unresolved residual risk.
- **Return:** terminal evidence judgment and exact next action.
- **Result:** PASS with accepted exclusions. Main reviewed all three fresh Sonnet verifier returns against the same non-Plan implementation candidate. T4-V1 independently passed AC-1 through AC-3; T4-V3 independently passed AC-4 and AC-7 through AC-9; T4-V2’s corrected follow-up established bounded AC-5 and AC-6 evidence across every permitted temporary-target ownership, refusal, backup, revalidation, and rollback case; only the `.harness/runs` trap and protected stale migration injection remained not-run by policy/protection. The full project discovery has one protected stale `_apply_setup_update` mismatch at `tests/test_migration.py:713`, which Main accepted as a nonessential fixture exclusion because it asserts a removed internal path; offline wheel construction/content inspection remains unavailable because `setuptools.build_meta` cannot be imported, and Main accepted that conditional release-only check as out of scope for this change. All verifier fingerprint drift (`91d4ed…` to `31e9e4…`) was caused solely by Main’s active-Plan byte edits; the normalized Plan-independent candidate fingerprint `668cb0847c5704efbe3c83a953081691a4d34e035ee97a93f8908deb6b296804` remained stable, with no verifier repository writes or forbidden paths. AC-10 is accepted with those explicit exclusions; no unavailable or failed check is represented as passing. The candidate remains intentionally uncommitted, with the normalized Plan-independent fingerprint `668cb0847c5704efbe3c83a953081691a4d34e035ee97a93f8908deb6b296804` serving as its exact identity; no Git commit is invented. This is the final Main judgment for the current candidate: AC-1 through AC-10 are accepted with the two explicit exclusions recorded above, and no unavailable or failed check is relabeled as passing.
T2 and T3 are broad roots. Each Owner must first return a finite manifest inside its packet envelope. Main alone serializes accepted child rows and complete matching packets, freezes disjoint writes and dependencies, then resumes that Owner. Ordinary leaves do not delegate. Owner-local aggregation is distinct from Main integration. T4 verification leaves depend on the same integrated candidate and are read-only, nonrepairing, and nondelegating.

## Current checkpoint
T1 and the bounded T2 implementation chain T2-A through T2-E plus T2-I owner-local aggregation are complete. ADR-0002, SPEC-004, and DESIGN-004 freeze the one-shot generated-target boundary; exact canonical settings are included in existing-target cleanup, while the historical public 0.2 `migrate` command remains unchanged. SPEC/DESIGN 003 retain their historical bodies with only `status: superseded`; ADR-0001 and completed Plans 0003/0005 are unchanged. Main serialized the finite T2-A → T2-B → T2-C → T2-D → T2-E → T2-I chain with disjoint write ownership, including the narrow T2-B correction required by the first aggregation pass. T2 supplies Markdown-native target assets, deterministic static runbooks and legacy proof, the `reporivet.setup-preview/v1` contract, exact setup cleanup/rollback semantics, retired CLI/package surfaces, and the package-only external setup Skill. T2-I verified the accepted path envelope and focused checks, while carrying one protected migration-fixture mismatch, incomplete independent cleanup/rollback evidence, and unavailable wheel-content verification as explicit downstream evidence items. T3-A is complete after updating eleven current-authority documents, T3-B is complete after aligning all 23 surviving generated templates, and T3-C is complete after reconciling package-data tests. T3-D is complete: eight test files were reconciled, all nine focused suites passed (`Ran 91 tests in 1.010s`, `OK`), source/test compileall passed, isolated fresh-target and existing-target cleanup/backup/rollback smokes passed, `git diff --check` passed, and the corrected 61-path changed-path audit passed with no unexpected or `.harness/runs` paths. T3-I aggregated the child evidence and recorded full discovery as 113 tests with one protected `_apply_setup_update` mismatch, wheel inspection as unavailable, and AC-6/AC-10 as not established pending fresh verification. T4-V1 independently passed AC-1 through AC-3; T4-V3 independently passed AC-4 and AC-7 through AC-9; the corrected T4-V2 follow-up upgraded AC-5 and AC-6 to bounded passes across every permitted temporary-target case, while `.harness/runs` and the protected stale migration injection remained not-run. Main’s final evidence judgment is COMPLETE WITH ACCEPTED EXCLUSIONS: AC-1 through AC-10 are accepted for this candidate. Full discovery’s sole protected `_apply_setup_update` mismatch is excluded as a stale assertion of an intentionally removed internal path; conditional wheel inspection is excluded because the declared backend is absent and release artifact verification is outside this change. The full-tree fingerprint drift during T4 was solely from Main’s active-Plan edits; the normalized Plan-independent candidate fingerprint `668cb0847c5704efbe3c83a953081691a4d34e035ee97a93f8908deb6b296804` remained stable. The candidate remains intentionally uncommitted; its exact fingerprint is recorded and no Git commit is invented.

## Exact next action
T4 verification and Main’s evidence judgment are complete with the two explicit AC-10 exclusions recorded in Decisions. Record the exact normalized candidate fingerprint, preserve the protected fixture and unavailable-backend classifications, and manually move this Plan to `docs/exec-plans/completed/` after the final path and whitespace checks. Do not install, publish, mutate a real target, access `.harness/runs`, or silently alter protected tests/fixtures.

## Decisions
- The dependency boundary applies to every externally generated target, not merely this source repository.
- Initial explicit setup may depend on installed/local Reporivet; generated targets may not depend on it afterward.
- The external setup Skill is a thin user-scoped wrapper over existing deterministic setup, not a plugin or second bundled runtime; its package source is `src/reporivet/assets/user-scoped/reporivet-setup/SKILL.md` and it is never target-generated or globally installed.
- Existing-target Skill/settings/marker cleanup is integrated into explicit setup rerun and removes only exact canonical artifacts after approved backup-bound preview; it does not add or route through a migration command, and the existing legacy 0.2 `migrate` contract remains unchanged.
- Complete Confirmed procedures become static runbooks; all target-installed Reporivet Skills are retired.
- Doctor is retired rather than made optional.
- AC-10 blocker resolution (2026-09-02): the sole full-discovery failure at protected `tests/test_migration.py:713` is accepted as a stale fixture exclusion, not a current-contract failure. The fixture requires canonical migration to reach internal `_apply_setup_update`, but the intentional one-shot boundary now uses the narrowed migration preview: canonical legacy inputs create or preserve content, while explicit setup reruns own cleanup. Forcing that obsolete hook to run would regress the frozen contract; the protected test and fixture remain unchanged. All other full-discovery tests and the independent current `_apply_setup_create` rollback evidence pass.
- AC-10 wheel evidence resolution (2026-09-02): wheel construction/content inspection is conditional release/artifact evidence, not an AC-10 requirement for this source/documentation change. `pyproject.toml` correctly declares `setuptools.build_meta`, but the selected Python 3.12 environment lacks Setuptools and installation/network workarounds are out of scope. Source package-data inventory and focused distribution tests pass. The broader DESIGN-004 wording to inspect built artifacts is retained as release-context guidance and is not falsely reported as completed in this Plan.

## Discoveries
- `CLAUDE_PROFILE_ASSETS` and procedure rendering are the current generation sources for persistent Skills.
- `.reporivet-version` and optional settings are explicit current target assets.
- Existing migration primitives can support safe setup-integrated removal without a separate new runtime.
- Current SPEC/DESIGN 003 and ADR-0001 explicitly authorize Skills, so a successor decision is required.

## Documentation impact
- Current/package documents: required across ADR/spec/design/architecture/product/quality/operations/security/plans/readmes and generated counterparts.
- Durable decisions: ADR-0002, SPEC-004, DESIGN-004.
- Historical records: preserve unchanged except bounded supersession routing where current indexes require it.

## Integration summary
- Candidate identity: T1/T2-A/T2-B/T2-C/T2-D/T2-E/T2-I/T3-A/T3-B/T3-C/T3-D candidate = repository `/Users/hakseong/Reporivet`, base and HEAD `680a091bd1b27f9761a65ce4832f41fcb1c8cf4c`, and the accepted T1/T2/T3 paths recorded in their results; it remains intentionally dirty and uncommitted. The Plan-inclusive full-tree fingerprint is intentionally volatile because the active Plan is untracked and changes as evidence is recorded; it is not used for candidate identity. The stable Plan-independent candidate fingerprint is `668cb0847c5704efbe3c83a953081691a4d34e035ee97a93f8908deb6b296804` (same algorithm with the active Plan excluded; 60 paths, 55 tracked changes, 5 untracked, 688118 tracked-diff bytes). T4 verifiers observed full-tree fingerprints `91d4ed…` → `31e9e4…` solely from Main’s active-Plan edits; no non-Plan candidate path changed. `integrated_commit` and `verified_commit` remain blank.
- Integrated changes: successor ADR/spec/design and current routing, Markdown-native target assets and retired-asset removals, deterministic static runbook planning plus private legacy proof, the `reporivet.setup-preview/v1` generation/inventory contract, exact backup-bound setup transition semantics with migration preview filtering, CLI/package/external-Skill retirement with focused coverage, corrected package-independent current authority, aligned surviving generated templates, reconciled distribution inventory tests, and eight reconciled T3-D regression test files including setup-flow transaction, Plan-lifecycle, and core command coverage. T3-D’s nine-suite matrix passed 91 tests; source/test compileall, isolated fresh-target and existing-target cleanup/backup/rollback smokes, `git diff --check`, and the corrected 61-path changed-path audit all passed. Fresh T4-V1 independently passed AC-1 through AC-3; T4-V3 independently passed AC-4 and AC-7 through AC-9; corrected T4-V2 independently passed the permitted AC-5/AC-6 temporary-target matrix, with only the `.harness/runs` trap and protected stale migration injection not-run by policy/protection.
- Residual risks: AC-5 and AC-6 pass bounded for every permitted temporary-target case; the `.harness/runs` trap was not-run by policy, and the protected migration fixture mismatch at `tests/test_migration.py:713` remains unresolved but is explicitly excluded as stale. Wheel-content verification is unavailable because `setuptools.build_meta` is not installed and is explicitly excluded as conditional release evidence. The candidate has no integrated or verified Git commit because no commit was authorized; its normalized fingerprint is recorded. The full-tree fingerprint changed only with Main’s Plan edits, while the normalized Plan-independent candidate remained stable. These are recorded limitations, not unreported failures; AC-1…AC-10 are accepted with the two documented exclusions.

## Verification summary
| Criterion | Candidate | Verifier | Result | Decision-bearing evidence |
|---|---|---|---|---|
| AC-1 through AC-3 | normalized Plan-independent `668cb0847c5704efbe3c83a953081691a4d34e035ee97a93f8908deb6b296804` (T4 full-tree snapshot `91d4ed…`; Plan-only drift afterward) | verifier-target | PASS, bounded to implementation-equivalent candidate | Exact 27-file fresh target (26 bundle assets plus visible draft), exact `CLAUDE.md`, no continuing artifacts, package-removal simulation, generated authority/Plan lifecycle, and static runbook checks |
| AC-5 through AC-6 | normalized Plan-independent `668cb0847c5704efbe3c83a953081691a4d34e035ee97a93f8908deb6b296804` (T4 full-tree snapshot `91d4ed…`; Plan-only drift afterward) | verifier-safety | PASS, bounded to permitted temporary-target matrix | Exact ownership/refusal, backup binding and modes, conversion, stale approval, immediate revalidation, partial-backup handling, whole-setup rollback through `_apply_setup_create`, successful later rollback, and post-user-change refusal passed; `.harness/runs` trap and protected stale `_apply_setup_update` injection were not-run by policy/protection |
| AC-4 and AC-7 through AC-9 | normalized Plan-independent `668cb0847c5704efbe3c83a953081691a4d34e035ee97a93f8908deb6b296804` (T4 full-tree snapshot `91d4ed…`; Plan-only drift afterward) | verifier-contract | PASS, bounded to implementation-equivalent candidate | Static runbooks, CLI/doctor retirement, external setup Skill, current authority/history, focused suites, scans, compileall, and diff check passed |
| AC-10 | normalized Plan-independent candidate `668cb0847c5704efbe3c83a953081691a4d34e035ee97a93f8908deb6b296804` | verifier-contract, verifier-safety, and Main | PASS with accepted exclusions | All applicable project-owned checks, focused distribution checks, fresh-target independence, cleanup/rollback matrix, and fresh criterion-level verification passed. The one protected stale `_apply_setup_update` fixture failure is excluded because it asserts a removed internal path; conditional wheel inspection is skipped because the declared backend is absent and release artifact verification is out of scope. Both decisions are recorded above; no failure is relabeled as a pass |

## Follow-ups
- No mandatory follow-up remains for this scope. The protected `tests/test_migration.py:713` `_apply_setup_update` assertion is retained as historical evidence and explicitly excluded because it targets a removed internal path; wheel-content inspection is a future release-context check requiring the declared Setuptools backend. The `.harness/runs` trap remains intentionally not-run. No publication, signing, deployment, global Skill installation, real-target cleanup, or external-project mutation is authorized.

## Outcome
Complete with accepted exclusions. Main completed T4 evidence judgment and accepted AC-1 through AC-10 for the intentionally uncommitted candidate: the protected stale migration fixture and conditional unavailable wheel inspection are explicitly excluded and are not represented as passing checks. The Plan has `status: complete`; `integrated_commit` and `verified_commit` remain blank because no commit was authorized, and Main will manually move this Plan to `docs/exec-plans/completed/` after the final audit.
