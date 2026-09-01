---
id: PLAN-2026-0005
kind: exec-plan
format: 2
task_graph: 1
status: complete
owner: main
area: native-task-owner-hierarchy
created: 2026-09-01
updated: 2026-09-01
supersedes: ""
superseded_by: ""
base_commit: "8245f672fbdf4030d38dda34e6fc23ea0ea8d006"
integrated_commit: "59f537630f9f68434258e2f2bd9dfb33b17eb4edb3fc9a1579a12ac26e753341"
verified_commit: "59f537630f9f68434258e2f2bd9dfb33b17eb4edb3fc9a1579a12ac26e753341"
---

# Make broad tasks default to bounded Task Owner subtrees

## Original goal

For task-based work, create an Owner Agent for each `T<n>`; let each Owner split its work into smaller independent implementation, review, test, verification, and documentation jobs, dispatch those jobs in parallel, inspect and aggregate the subtree, and report one compact result to Main so multiple tasks can progress quickly without filling Main's long-lived context. Use Sonnet Agents and keep Reporivet document-first rather than adding an orchestration runtime.

## Observable outcome and acceptance

- **AC-1 — Broad Owner default:** current and packaged authority state that broad or multi-part roots default to `Role: Task Owner` and `May delegate: yes`, while narrow or inherently serial roots remain direct nondelegating leaves.
- **AC-2 — Durable decomposition checkpoint:** an Owner returns a finite child manifest within its approved envelope; Main alone serializes accepted child rows and complete packets into this Plan before resuming the Owner to dispatch them.
- **AC-3 — Native nested parallelism:** Main may dispatch independent root Owners concurrently and each Owner may dispatch its complete dependency-ready child set through host-native Agent execution; Reporivet provides no scheduler or dispatcher runtime.
- **AC-4 — Bounded ownership and isolation:** Owners inherit and cannot broaden scope, acceptance, non-goals, protected paths, child budget, or frozen interfaces; mutable siblings have disjoint writes and separate exact-baseline worktrees; Owner aggregation is local and Main owns final repository integration.
- **AC-5 — Independent verification:** implementation/Owner tests do not self-approve; fresh candidate-specific Verification Agents are read-only, nonrepairing, nondelegating, and invalidated by later mutation.
- **AC-6 — Semantic Plan checks:** `doctor` validates `task_graph: 1` roles, immediate parents, delegation, row/packet parity, exact dependencies, missing/self/cyclic edges, integration ordering, and verification dependency/state rules with task-specific findings.
- **AC-7 — Compatibility:** unmarked compact Plans retain structural validation, historical expanded/completed Plans remain untouched, recursive task IDs remain valid, and direct serial Plans remain supported.
- **AC-8 — Current/package parity:** current authority, bilingual READMEs, package templates, and role Skills agree on the contract and preserve create-if-missing assets and the no-runtime boundary.
- **AC-9 — Regression:** focused and full tests, compile, doctor, package inventory/parity, link checks, candidate identity, protected-path hygiene, and `git diff --check` pass on one integrated candidate.

## Scope

- Current repository authority and public product/design/quality wording that directly governs Main, Task Owner, leaf, integration, and verification behavior.
- Packaged document-first AGENTS/PLANS/Plan and role Skill templates for future installs.
- Strict opt-in semantic validation for `format: 2` Plans marked `task_graph: 1`.
- Focused lifecycle, asset, and documentation contract tests.
- One Main-owned active Plan, exact-baseline isolated implementation, serial Main integration, and fresh parallel verification.

## Non-goals

- No scheduler, task database, dispatcher, Agent API wrapper, command runner, lease/lock, hidden child registry, evidence archive, generated workflow, or automatic Plan closure.
- No public command/API changes, production dependencies, CI changes, deployment, release, publication, signing, push, tag, or commit.
- No migration or rewrite of existing Plans or installed project-owned files.
- No edits to completed/superseded history, generated records, module contracts, legacy runtime surfaces, or `.harness/runs/**`.

## Task state

| Task | Owner | State | Depends on | Parallel group | Outcome | Result |
|---|---|---|---|---|---|---|
| T1 | current-authority-owner | complete | none | root-owners | Produce bounded current-authority subtree | complete |
| T1-A | current-authority-wording-leaf | complete | none | T1-current-authority-leaves | Update current and public hierarchy wording | complete |
| T1-B | documentation-contract-test-leaf | complete | none | T1-current-authority-leaves | Extend documentation contract coverage | complete |
| T1-R1 | documentation-contract-repair | complete | T1-A, T1-B | T1-repair | Align focused assertions to the frozen contract | complete |
| T1-I | current-authority-owner | complete | T1-A, T1-B, T1-R1 | T1-owner-aggregation | Aggregate and review T1 child outputs | complete |
| T2 | packaged-assets-owner | complete | none | root-owners | Produce bounded packaged-assets subtree | complete |
| T2-A | packaged-contract-assets | complete | none | T2-package-leaves | Update packaged authority and Plan templates | complete |
| T2-B | packaged-role-skills | complete | none | T2-package-leaves | Update packaged role Skill templates | complete |
| T2-C | packaged-asset-contract-tests | complete | none | T2-package-leaves | Extend packaged asset contract assertions | complete |
| T2-I | packaged-assets-owner | complete | T2-A, T2-B, T2-C | T2-package-integration | Aggregate and review T2 child outputs | complete |
| T3 | semantic-validator-owner | complete | none | root-owners | Produce bounded semantic-validator subtree | complete |
| T3-A | semantic-parser-implementation | complete | none | T3-leaves | Implement strict task graph parser and findings | complete |
| T3-B | semantic-lifecycle-tests | complete | none | T3-leaves | Add strict semantic lifecycle fixtures and tests | complete |
| T3-R1 | semantic-lifecycle-repair | complete | T3-A, T3-B | T3-repair | Align strict fixtures and finding assertions | complete |
| T3-I | semantic-validator-owner | complete | T3-A, T3-B, T3-R1 | T3-integration | Aggregate and review T3 child outputs | complete |
| T4 | main | complete | T1, T2, T3, T9, T10 | integration | Integrate exact accepted subtree outputs | complete |
| T9 | integration-test-repair | complete | T1, T2, T3 | integration-repair | Align lifecycle assertions with integrated contract | complete |
| T10 | compact-template-repair | complete | T1, T2, T3 | integration-repair | Restore compact current and packaged Plan templates | complete |
| T5 | semantic-verification | complete | T4 | verification | Verify strict graph semantics and compatibility | complete |
| T6 | authority-verification | complete | T4 | verification | Verify current/package/Skill contract parity | complete |
| T7 | regression-verification | complete | T4 | verification | Verify full regression and patch hygiene | complete |
| T8 | main | complete | T5, T6, T7 | terminal | Judge evidence and transition the Plan | complete |

## Task Packets

### T1 — Current authority Task Owner

- **Owner:** current-authority-owner
- **Role:** Task Owner
- **Parent:** none
- **Parallel group:** root-owners
- **May delegate:** yes
- **Inherited boundaries:** AC-1 through AC-5 and AC-7 through AC-9; current/public authority only; Main retains Plan edits and final integration; child Agents use Sonnet, finite declared packets, disjoint writes, and exact-baseline worktrees.
- **Outcome:** Return a finite child manifest, then after Main serialization dispatch and aggregate current/public authority and focused documentation-contract work.
- **Non-goals:** No packaged asset, production Python, lifecycle-test, runtime, completed-history, generated, module-contract, operations, security, release, or external-system changes.
- **Read:** `AGENTS.md`, `README.md`, `README.en.md`, `docs/README.md`, `docs/PRODUCT.md`, `docs/DESIGN.md`, `docs/PLANS.md`, `docs/QUALITY.md`, current SPEC/DESIGN 003, the current harness migration reference, `docs/exec-plans/_template.md`, and `tests/test_documentation_contract.py`.
- **Allowed writes:** current authority/public files proven to contain the old leaf-dispatch contract, `docs/exec-plans/_template.md`, and `tests/test_documentation_contract.py`, partitioned into disjoint child packets after Main approval.
- **Protected paths:** this Plan; `ARCHITECTURE.md`, `docs/OPERATIONS.md`, `docs/SECURITY.md` unless an exact current contradiction is returned before work; packaged assets; production Python; other tests; completed/superseded/generated/module-contract history; `.harness/runs/**`; `dev/harness.toml`; build outputs.
- **Acceptance:** AC-1 through AC-5 and AC-7 through AC-9.
- **Verification:** targeted documentation contract tests, current-document literal/parity checks, links, exact seed-relative diff, and no positive Reporivet-dispatch/runtime claim.
- **Stop conditions:** non-finite manifest, scope expansion, overlapping child writes, unfrozen wording, need to edit the Plan/protected paths, or inability to prove exact baseline.
- **Return:** first a finite manifest of at most two mutable leaves plus one local aggregation node; after resume, exact changed paths/hashes/modes, child and aggregation results, commands/results, acceptance mapping, discoveries, and residual risks.
- **Result:** complete.

### T1-A — Current and public hierarchy wording

- **Owner:** current-authority-wording-leaf
- **Role:** leaf
- **Parent:** T1
- **Parallel group:** T1-current-authority-leaves
- **May delegate:** no
- **Inherited boundaries:** T1 scope and frozen clauses; exact baseline `8245f672fbdf4030d38dda34e6fc23ea0ea8d006`; disjoint current-document writes; Main owns the Plan and final integration.
- **Outcome:** Replace the old Main-dispatches-every-leaf default with broad Task Owner subtrees across current/public authority while preserving direct serial leaves and the no-runtime boundary.
- **Non-goals:** No package, production Python, test, runtime, operations, security, architecture, historical, release, or external change.
- **Read:** `AGENTS.md`, bilingual READMEs, `docs/{README,PRODUCT,DESIGN,PLANS,QUALITY}.md`, current SPEC/DESIGN 003, current harness migration and project-definition references, `docs/exec-plans/_template.md`, and `tests/test_documentation_contract.py` read-only.
- **Allowed writes:** `AGENTS.md`, `README.md`, `README.en.md`, `docs/PRODUCT.md`, `docs/DESIGN.md`, `docs/PLANS.md`, `docs/QUALITY.md`, current SPEC/DESIGN 003, `docs/references/harness-engineering-skill-migration.md`, and `docs/exec-plans/_template.md` only where old hierarchy wording is present or the new marker/example is required.
- **Protected paths:** this Plan; `docs/README.md`; project-definition protocol; `ARCHITECTURE.md`; OPERATIONS; SECURITY; package assets; production Python; tests; completed/superseded/generated/module-contract history; runtime/build paths; `.harness/runs/**`; external systems.
- **Acceptance:** AC-1 through AC-5 and AC-7 through AC-9; exact-nine-field ProcedureSpec remains canonical and the migration reference must conform to it.
- **Verification:** exact allowed-path diff, `git diff --check`, stale leaf-dispatch/no-runtime review, bilingual semantic parity, and no command/API/history changes; focused docs test runs at T1-I.
- **Stop conditions:** need for any protected/unlisted path, contradictory frozen clause, scope broadening, delegation, runtime claim, baseline uncertainty, or protected traversal.
- **Return:** exact changed paths/hashes/modes, per-file clause mapping, commands/results, discoveries, and residual risks.
- **Result:** complete.

### T1-B — Documentation contract regression tests

- **Owner:** documentation-contract-test-leaf
- **Role:** leaf
- **Parent:** T1
- **Parallel group:** T1-current-authority-leaves
- **May delegate:** no
- **Inherited boundaries:** T1 scope and frozen clauses; exact baseline; one test-file write; Main owns the Plan and final integration.
- **Outcome:** Extend existing documentation-contract assertions for broad Owner defaults, the manifest checkpoint, nested native dispatch, inherited isolation, Owner-local aggregation, fresh verification, compatibility, and no runtime.
- **Non-goals:** No document/package/source/other-test/runtime/history/external changes and no weakened existing assertion.
- **Read:** `tests/test_documentation_contract.py` and every current/public authority path in T1-A as read-only clause sources.
- **Allowed writes:** `tests/test_documentation_contract.py` only.
- **Protected paths:** this Plan; all docs/assets/source/other tests; completed/superseded/generated/module-contract history; runtime/build paths; `.harness/runs/**`; external systems.
- **Acceptance:** AC-1 through AC-5 and AC-7 through AC-9 without weakening setup/init/define, bilingual, historical, artifact, or no-positive-execution assertions.
- **Verification:** compile the single test with external cache, inspect assertion inventory, and `git diff --check`; execute the focused test only on T1-I's aggregate.
- **Stop conditions:** unfrozen wording, need for another path, weakened acceptance, runtime assumption, delegation, or protected traversal.
- **Return:** exact test hash/mode, assertion-to-clause mapping, compile/diff results, discoveries, and residual risks.
- **Result:** complete.

### T1-R1 — Documentation contract assertion repair

- **Owner:** documentation-contract-repair
- **Role:** leaf
- **Parent:** T1
- **Parallel group:** T1-repair
- **May delegate:** no
- **Inherited boundaries:** exact accepted T1-A/T1-B aggregate and frozen canonical clauses; sequential repair supersedes only T1-B's test-file content; Main owns the Plan and final integration.
- **Outcome:** Correct the four focused assertion mismatches without changing current documents or weakening pre-existing documentation coverage.
- **Non-goals:** No document/package/source/other-test/history/runtime/external change, no rollback to the obsolete Main-dispatches-all-leaves contract, and no broadened protected-document scan.
- **Read:** the exact T1-I failed aggregate, T1-A/T1-B evidence, focused failure output, this Plan, and `tests/test_documentation_contract.py` history/diff.
- **Allowed writes:** `tests/test_documentation_contract.py` only in the isolated repair worktree; the worktree is preseeded with the exact failed twelve-path T1 aggregate.
- **Protected paths:** this Plan; all documents/assets/source/other tests; completed/superseded/generated/module-contract history; runtime/build paths; `.harness/runs/**`; external systems.
- **Acceptance:** retain all old assertions; assert the new broad-root/Owner-local topology instead of the obsolete literal; keep no-runtime scanning from falsely failing unchanged protected ARCHITECTURE; match documented historical compatibility and serialization/resume clauses semantically; all focused documentation tests pass.
- **Verification:** run `tests.test_documentation_contract -v` with Python 3.13/external cache on the repaired aggregate; inspect assertion diff for no weakening; explicit-path `git diff --check`; confirm only the test file differs from the failed aggregate.
- **Stop conditions:** a document or other path must change, an old assertion must be removed/weakened, frozen semantics cannot be asserted, repair expands scan scope, delegation, or protected-path uncertainty.
- **Return:** exact repaired test hash/mode/diff, four-failure disposition, focused command result, assertion inventory, discoveries, and residual risks.
- **Result:** complete.

### T1-I — Owner-local current-authority aggregation

- **Owner:** current-authority-owner
- **Role:** integration
- **Parent:** T1
- **Parallel group:** T1-owner-aggregation
- **May delegate:** no
- **Inherited boundaries:** exact accepted T1-A/T1-B union; owner-local worktree only; Main retains primary integration, Plan edits, and final evidence judgment.
- **Outcome:** Aggregate accepted child outputs, review current/public consistency, run focused documentation tests, and return one exact T1 candidate to Main.
- **Non-goals:** No new repair scope, primary/Plan/sibling mutation, package/source/other-test change, self-approval, or fresh-verification claim.
- **Read:** exact T1 child paths/results plus `docs/README.md` and the project-definition protocol read-only.
- **Allowed writes:** only the accepted union of T1-A document/template paths and `tests/test_documentation_contract.py` in the separate T1-I worktree.
- **Protected paths:** primary worktree, this Plan, sibling worktrees except read-only evidence, every path outside the child union, `.harness/runs/**`, external systems.
- **Acceptance:** both children are exact-baseline/disjoint; nine-field ProcedureSpec is preserved; focused documentation tests and diff hygiene pass; bilingual/current clauses align; no runtime or positive Reporivet dispatch claim appears.
- **Verification:** compare child and aggregate path/hash/mode sets; run focused documentation-contract tests and explicit-path `git diff --check`; record aggregate fingerprint.
- **Stop conditions:** missing/overlapping/unexpected child result, baseline mismatch, out-of-union repair, focused failure, Plan/primary mutation, or protected traversal.
- **Return:** aggregate path/hash/mode set, child/command results, criterion mapping, discoveries, residual risks, and explicit Main-integration requirement.
- **Result:** complete.

### T2 — Packaged assets Task Owner

- **Owner:** packaged-assets-owner
- **Role:** Task Owner
- **Parent:** none
- **Parallel group:** root-owners
- **May delegate:** yes
- **Inherited boundaries:** AC-1 through AC-5 and AC-7 through AC-9; packaged document-first assets only; preserve create-if-missing behavior; Main retains Plan edits and final integration; child Agents use Sonnet, finite declared packets, disjoint writes, and exact-baseline worktrees.
- **Outcome:** Return a finite child manifest, then after Main serialization dispatch and aggregate packaged templates, role Skills, and focused asset assertions.
- **Non-goals:** No current authority, production Python, public API, asset inventory/path change unless strictly required, existing-target rewrite, runtime, release, or external action.
- **Read:** packaged root AGENTS, docs PLANS and Plan templates, the three role Skill templates, `tests/test_claude_assets.py`, focused package inventory assertions, and current authority as read-only frozen interface.
- **Allowed writes:** the packaged AGENTS/PLANS/Plan templates, three packaged role Skill templates, `tests/test_claude_assets.py`, and only directly necessary existing package-inventory assertions, partitioned into disjoint child packets after Main approval.
- **Protected paths:** this Plan; current authority/public docs; production Python; lifecycle/documentation tests; package asset inventory and paths unless a concrete requirement is returned; completed/superseded/generated history; `.harness/runs/**`; build outputs.
- **Acceptance:** AC-1 through AC-5 and AC-7 through AC-9.
- **Verification:** focused Claude asset/package tests, current/package clause parity, create-if-missing preservation, exact seed-relative diff, and absence of runtime/dispatch implementation claims.
- **Stop conditions:** non-finite manifest, scope expansion, overlapping child writes, unfrozen current interface, need to edit the Plan/protected paths, asset-path/inventory change, or inability to prove exact baseline.
- **Return:** first a finite manifest of at most three mutable leaves plus one local aggregation node; after resume, exact changed paths/hashes/modes, child and aggregation results, commands/results, acceptance mapping, discoveries, and residual risks.
- **Result:** complete.

### T2-A — Packaged authority and Plan templates

- **Owner:** packaged-contract-assets
- **Role:** leaf
- **Parent:** T2
- **Parallel group:** T2-package-leaves
- **May delegate:** no
- **Inherited boundaries:** T2 scope and frozen current interface; exact baseline; three packaged template writes only; Main owns the Plan and final integration.
- **Outcome:** Align packaged AGENTS, PLANS, and Plan templates with broad Owner defaults, finite Main serialization, Owner child dispatch, local aggregation, fresh verification, compatibility, and no runtime.
- **Non-goals:** No current docs, Skills, tests, production code, inventory/path, runtime, history, or external change.
- **Read:** current AGENTS/PLANS/Plan guidance read-only; packaged root AGENTS, docs PLANS, Plan and README templates; `tests/test_claude_assets.py` and `tests/test_distribution.py` read-only.
- **Allowed writes:** packaged `root/AGENTS.md.tmpl`, `docs/PLANS.md.tmpl`, and `docs/exec-plans/_template.md.tmpl` only.
- **Protected paths:** this Plan; current authority; packaged Skills and all other assets; all tests/source/history/runtime/build paths; `.harness/runs/**`; external systems.
- **Acceptance:** AC-1 through AC-5 and AC-7 through AC-9; preserve `format: 2`, add default `task_graph: 1` example, create-if-missing/content preservation, asset inventory, and no-runtime boundary.
- **Verification:** focused packaged-asset test where individually applicable, clause matrix, unchanged inventory, explicit-path `git diff --check`, and exact diff.
- **Stop conditions:** unfrozen root/nested distinction, need for sibling/current/source/test/inventory path, asset rename, runtime metadata, delegation, or baseline/protected-path uncertainty.
- **Return:** exact changed paths/hashes/modes, clause mapping, commands/results, inventory confirmation, discoveries, and residual risks.
- **Result:** complete.

### T2-B — Packaged role Skill templates

- **Owner:** packaged-role-skills
- **Role:** leaf
- **Parent:** T2
- **Parallel group:** T2-package-leaves
- **May delegate:** no
- **Inherited boundaries:** T2 scope and frozen current/package interface; exact baseline; three Skill writes only; Main owns the Plan and final integration.
- **Outcome:** Align Main, Implementation, and Verification Skills with root Owner dispatch, manifest serialization/resume, bounded ordinary leaves, Owner-local aggregation, and fresh nondelegating verification.
- **Non-goals:** No current docs, packaged authority templates, tests, production code, frontmatter/tool/runtime metadata, inventory/path, history, or external change.
- **Read:** current and packaged AGENTS/PLANS/Plan guidance; the three role Skills; `tests/test_claude_assets.py` and distribution inventory read-only.
- **Allowed writes:** packaged `reporivet-main`, `reporivet-implementation`, and `reporivet-verification` `SKILL.md.tmpl` files only.
- **Protected paths:** this Plan; current docs; T2-A/T2-C paths; all other assets/source/tests/history/runtime/build paths; `.harness/runs/**`; external systems.
- **Acceptance:** AC-1 through AC-5 and AC-7 through AC-9; Skills remain instruction-only, least privilege, and frontmatter remains only `name`/`description`.
- **Verification:** focused role-Skill test where individually applicable, frontmatter/clause parity, unchanged inventory, explicit-path `git diff --check`, and exact diff.
- **Stop conditions:** need for runtime metadata/tool grant, sibling/current/source/test/inventory path, unfrozen contract, delegation, or protected-path uncertainty.
- **Return:** exact Skill hashes/modes, frontmatter/clause evidence, commands/results, discoveries, and residual risks.
- **Result:** complete.

### T2-C — Packaged asset contract assertions

- **Owner:** packaged-asset-contract-tests
- **Role:** leaf
- **Parent:** T2
- **Parallel group:** T2-package-leaves
- **May delegate:** no
- **Inherited boundaries:** T2 scope and frozen clause matrix; exact baseline; one test-file write; Main owns the Plan and final integration.
- **Outcome:** Extend packaged asset assertions for Owner defaults, finite checkpoint, root/nested dispatch, inherited boundaries, fresh verification, and no runtime while preserving inventory and existing coverage.
- **Non-goals:** No asset/source/current/lifecycle/documentation/distribution/runtime/history/external changes and no weakened assertion.
- **Read:** all six T2 asset targets, packaged README inventory reference, `tests/test_claude_assets.py`, and `tests/test_distribution.py` read-only.
- **Allowed writes:** `tests/test_claude_assets.py` only.
- **Protected paths:** this Plan; all docs/assets/source/other tests, especially `tests/test_distribution.py`; history/runtime/build paths; `.harness/runs/**`; external systems.
- **Acceptance:** AC-1 through AC-5 and AC-7 through AC-9; preserve dynamic-procedure, create-if-missing, existing-content, Skill-frontmatter, and exact asset inventory assertions.
- **Verification:** compile the single test with external cache, inspect assertion scope, and explicit-path `git diff --check`; run focused tests on T2-I aggregate.
- **Stop conditions:** test needs inventory/asset/other-test/source change, phrase is unfrozen, assertion weakens coverage, delegation, or protected-path uncertainty.
- **Return:** exact test hash/mode, assertion mapping, compile/diff results, inventory confirmation, discoveries, and residual risks.
- **Result:** complete.

### T2-I — Owner-local packaged parity aggregation

- **Owner:** packaged-assets-owner
- **Role:** integration
- **Parent:** T2
- **Parallel group:** T2-package-integration
- **May delegate:** no
- **Inherited boundaries:** accepted T2-A/T2-B/T2-C union; owner-local worktree only; Main retains primary integration, Plan edits, and final evidence judgment.
- **Outcome:** Aggregate child outputs, verify package/Skill/current parity and unchanged inventory, run focused asset/distribution tests, and return one exact T2 candidate.
- **Non-goals:** No new repair scope, primary/Plan/sibling mutation, current/source/other-test/asset-inventory change, self-approval, or fresh-verification claim.
- **Read:** exact child paths/results, frozen current clauses, packaged README inventory reference, and `tests/test_distribution.py` read-only.
- **Allowed writes:** only the accepted seven-path T2 child union in the separate T2-I worktree.
- **Protected paths:** primary worktree, this Plan, sibling worktrees except read-only evidence, current docs, every path outside the union, `.harness/runs/**`, external systems.
- **Acceptance:** exact disjoint child union; current/package/Skill clause parity; unchanged asset inventory; focused Claude asset/distribution tests and diff hygiene pass; no package runtime/dispatcher claim.
- **Verification:** compare child/aggregate paths/hashes/modes; run `tests.test_claude_assets` and `tests.test_distribution`; explicit-union `git diff --check`; record aggregate fingerprint.
- **Stop conditions:** missing/overlapping/unexpected child result, baseline/inventory mismatch, out-of-union repair, focused failure, current mismatch, Plan/primary mutation, or protected traversal.
- **Return:** aggregate path/hash/mode set, child/command results, parity/inventory matrix, criterion mapping, discoveries, residual risks, and explicit Main-integration requirement.
- **Result:** complete.

### T3 — Semantic Plan validation Task Owner

- **Owner:** semantic-validator-owner
- **Role:** Task Owner
- **Parent:** none
- **Parallel group:** root-owners
- **May delegate:** yes
- **Inherited boundaries:** AC-2 and AC-6 through AC-9; private in-memory structural validation only; no runtime orchestration or public API; Main retains Plan edits and final integration; child Agents use Sonnet, finite declared packets, disjoint writes, and exact-baseline worktrees.
- **Outcome:** Return a finite child manifest, then after Main serialization dispatch and aggregate strict `task_graph: 1` parser/findings and lifecycle test work.
- **Non-goals:** No command/API change, file writer, subprocess, Agent integration, hidden state, dependency, current/package prose edit, or migration of old Plans.
- **Read:** `src/reporivet/guided.py`, `tests/test_plan_lifecycle.py`, current/package Plan templates, `docs/PLANS.md`, `docs/QUALITY.md`, and existing doctor/lifecycle helpers.
- **Allowed writes:** `src/reporivet/guided.py` and `tests/test_plan_lifecycle.py`, one path per mutable child after Main approves the frozen parser/semantic contract.
- **Protected paths:** this Plan; every other production/test/doc/asset path; completed/superseded/generated history; `.harness/runs/**`; build outputs.
- **Acceptance:** AC-2, AC-6, AC-7, and AC-9.
- **Verification:** focused lifecycle tests covering valid strict hierarchy, malformed marker, role/delegation/parent/dependency/cycle/integration/verification defects, unmarked compatibility, recursive IDs, exact findings, doctor, compile, and exact seed-relative diff.
- **Stop conditions:** non-finite manifest, parser contract conflict, need for public/runtime/state changes, test requiring weakened old behavior, need to edit the Plan/protected paths, or inability to prove exact baseline.
- **Return:** first a finite manifest of two mutable leaves plus one local aggregation node and the frozen row/packet semantic contract; after resume, exact changed paths/hashes/modes, child and aggregation results, commands/results, acceptance mapping, discoveries, and residual risks.
- **Result:** complete.

### T3-A — Strict task graph parser and findings

- **Owner:** semantic-parser-implementation
- **Role:** leaf
- **Parent:** T3
- **Parallel group:** T3-leaves
- **May delegate:** no
- **Inherited boundaries:** T3 scope and the frozen strict graph contract below; exact baseline; one private production-file write; Main owns the Plan and final integration.
- **Outcome:** Add private in-memory parsing and task-specific `DoctorFinding` generation for strict `task_graph: 1` compact Plans while preserving current structural and historical behavior.
- **Non-goals:** No public API, writer, subprocess, Agent integration, hidden state, dependency, migration, docs/assets/tests, or runtime change.
- **Read:** `src/reporivet/guided.py`, `tests/test_plan_lifecycle.py` read-only, this Plan, current/package Plan templates and PLANS guidance, and QUALITY.
- **Allowed writes:** `src/reporivet/guided.py` only.
- **Protected paths:** this Plan; tests/docs/assets and all other source; completed/superseded/generated/module-contract history; runtime/build paths; `.harness/runs/**`; external systems.
- **Acceptance:** AC-2, AC-6, AC-7, and applicable AC-9; reuse existing compact/frontmatter/section/task-ID/finding helpers; no behavioral change for unmarked or historical Plans.
- **Verification:** pre-existing lifecycle tests, compile, doctor, exact-path diff/status, and `git diff --check`; new strict tests run after T3-I aggregation.
- **Stop conditions:** frozen contract conflict, need for public/runtime/state/I/O/dependency/doc/test change, unmarked behavior change, delegation, or baseline/protected-path uncertainty.
- **Return:** exact path/hash/mode, private model/normalization/finding catalog, commands/results, criterion mapping, discoveries, and residual risks.
- **Result:** complete.

### T3-B — Strict semantic lifecycle tests

- **Owner:** semantic-lifecycle-tests
- **Role:** leaf
- **Parent:** T3
- **Parallel group:** T3-leaves
- **May delegate:** no
- **Inherited boundaries:** T3 scope and the frozen strict graph contract below; exact baseline; one test-file write; Main owns the Plan and final integration.
- **Outcome:** Add valid strict hierarchy/direct-leaf fixtures plus targeted marker, field, parity, role/delegation, parent, dependency/cycle, integration, verification, state, and compatibility tests.
- **Non-goals:** No production/docs/assets/other-test/runtime/history change and no weakened existing structural/recursive/historical coverage.
- **Read:** `tests/test_plan_lifecycle.py`, `src/reporivet/guided.py` read-only, this Plan, current/package Plan templates and PLANS guidance, and QUALITY.
- **Allowed writes:** `tests/test_plan_lifecycle.py` only.
- **Protected paths:** this Plan; production/docs/assets/other tests; completed/superseded/generated/module-contract history; runtime/build paths; `.harness/runs/**`; external systems.
- **Acceptance:** AC-2, AC-6, AC-7, and applicable AC-9; exact severity/path/task-specific details; preserve existing tests and compatibility; do not require a missing marker to fail.
- **Verification:** compile the test, inspect fixture matrix and diff; execute focused lifecycle/doctor checks after T3-I aggregation.
- **Stop conditions:** frozen contract changes, weakened old behavior, need for another path, implementation-specific phrase coupling, delegation, or baseline/protected-path uncertainty.
- **Return:** exact path/hash/mode, fixture/test matrix, deferred combined checks, criterion mapping, discoveries, and residual risks.
- **Result:** complete.

### T3-R1 — Strict lifecycle fixture and assertion repair

- **Owner:** semantic-lifecycle-repair
- **Role:** leaf
- **Parent:** T3
- **Parallel group:** T3-repair
- **May delegate:** no
- **Inherited boundaries:** exact accepted T3-A/T3-B aggregate and frozen strict graph contract; sequential repair supersedes only T3-B's test-file content; Main owns the Plan and final integration.
- **Outcome:** Correct fixture parent relationships and assertion expectations that conflict with the frozen contract and existing structural finding behavior.
- **Non-goals:** No `guided.py`, docs/assets/other-test/runtime/history/external change; no weakening strict semantics; no new outcome/result prose parity.
- **Read:** exact T3-I failed aggregate, lifecycle failure log, T3-A/T3-B evidence, this Plan, and `tests/test_plan_lifecycle.py` diff/history.
- **Allowed writes:** `tests/test_plan_lifecycle.py` only in the isolated repair worktree; the worktree is preseeded with the exact failed two-path T3 aggregate.
- **Protected paths:** this Plan; `src/reporivet/guided.py`; docs/assets/source/other tests; completed/superseded/generated/module-contract history; runtime/build paths; `.harness/runs/**`; external systems.
- **Acceptance:** valid recursive fixtures declare and serialize immediate lexical parents; malformed dependency delimiters assert the actionable malformed-ID finding; non-owner descendants assert the existing Role/delegation violation; empty Owner cases assert the existing structural owner/parity findings; all strict and compatibility lifecycle tests pass without weakening coverage.
- **Verification:** run `tests.test_plan_lifecycle -v`, compile, doctor, and explicit two-path diff hygiene on the repaired aggregate; inspect test-only repair diff and exact failure disposition.
- **Stop conditions:** `guided.py` or another path must change, frozen semantics would weaken/broaden, an existing passing test is removed, delegation, or protected-path uncertainty.
- **Return:** repaired test hash/mode/diff, four-pattern/24-failure disposition, commands/results, fixture matrix, discoveries, and residual risks.
- **Result:** complete.

### T3-I — Owner-local semantic candidate aggregation

- **Owner:** semantic-validator-owner
- **Role:** integration
- **Parent:** T3
- **Parallel group:** T3-integration
- **May delegate:** no
- **Inherited boundaries:** accepted T3-A/T3-B union and frozen strict contract; owner-local worktree only; Main retains primary integration, Plan edits, and final evidence judgment.
- **Outcome:** Aggregate the two exact leaves, review scope, run focused lifecycle/compile/doctor/diff checks, and return one exact semantic candidate.
- **Non-goals:** No new repair scope, primary/Plan/sibling mutation, doc/asset/other-path change, self-approval, or fresh-verification claim.
- **Read:** exact child paths/results, this Plan and current/package Plan guidance read-only.
- **Allowed writes:** only `src/reporivet/guided.py` and `tests/test_plan_lifecycle.py` in the separate T3-I worktree.
- **Protected paths:** primary worktree, this Plan, sibling worktrees except read-only evidence, every path outside the two-file union, `.harness/runs/**`, external systems.
- **Acceptance:** exact disjoint child union; frozen strict contract and compatibility; focused lifecycle, compile, doctor, and diff hygiene pass; no public/runtime/state/I/O additions.
- **Verification:** compare child/aggregate paths/hashes/modes; run focused lifecycle, compile, doctor, and `git diff --check`; record aggregate fingerprint.
- **Stop conditions:** missing/overlapping/unexpected child result, baseline mismatch, out-of-union repair, mandatory failure, Plan/primary mutation, or protected traversal.
- **Return:** aggregate path/hash/mode set, child/command results, criterion mapping, discoveries, residual risks, and explicit Main-integration requirement.
- **Result:** complete.

### Frozen strict graph contract

- Strict semantics run only for compact `format: 2` Plans whose parsed frontmatter has `task_graph: 1`; quoted `"1"` normalizes identically. A present non-`1` value is one error and suppresses cascading graph checks. A missing marker keeps existing structural validation only; historical expanded/completed Plans remain grandfathered and are never migrated.
- Reuse `_parse_frontmatter`, `_markdown_section`, `TASK_ID_PATTERN`, `_compact_plan_structure_findings`, `_plan_findings`, and `DoctorFinding`. Add private immutable row/packet/graph models only.
- Strict rows require `Task`, `Owner`, `State`, `Depends on`, `Parallel group`, `Outcome`, and `Result`. Strict packets require the existing bounded packet fields plus unique `Role`, `Parent`, `Parallel group`, `May delegate`, and `Inherited boundaries` fields.
- Normalize surrounding whitespace; IDs remain exact and case-sensitive. Roles and yes/no are case-insensitive canonical values. `none` is the sole empty sentinel. Dependencies are ordered comma-separated exact IDs; reject blanks, malformed/mixed-none/duplicate/missing/self edges and cycles without silently repairing.
- Accepted roles are `Task Owner`, `leaf`, `integration`, and `verification`. A packet with descendants and every Task Owner use `May delegate: yes`; leaves/integrations/verifiers use `no`; a childless Owner is valid at the manifest checkpoint. Recursive packet Parent must be the exact immediate lexical ID prefix and exist; root Parent is `none`.
- Require row/packet Owner and Parallel group equality. Do not add Outcome or Result prose-parity checks and do not infer containment from natural-language write/acceptance fields.
- Strict row states are `ready`, `blocked`, `in-progress`, `verifying`, `complete`, `cancelled`, and `superseded`; row Result is `pending`, `complete`, `cancelled`, or `superseded` with the corresponding nonterminal/terminal mapping. Runnable or complete tasks require declared dependencies complete; otherwise they remain blocked. `verifying` applies only to verification.
- Dependency edges are separate from Parent edges. Reject missing targets, self edges, duplicates, and deterministic cycles; row order need not be topological.
- Integrations have no descendants, depend on at least one implementation leaf or Task Owner, and never depend on verification. A non-root parent-local integration must depend on every direct same-parent leaf/Task Owner sibling. Root integration is not forced to depend on unrelated later root leaves.
- Verification has no descendants, `May delegate: no`, and directly depends only on at least one integration candidate rather than implementation leaves/Owners. It cannot be ready/in-progress/verifying/complete until integration dependencies complete.
- Findings are read-only, task-specific errors on the exact Plan-relative path. Missing prerequisite structure suppresses dependent checks rather than raising or fabricating cascades. Preserve existing finding text and final deduplication for current checks.

### T4 — Main integration

- **Owner:** main
- **Role:** integration
- **Parent:** none
- **Parallel group:** integration
- **May delegate:** no
- **Inherited boundaries:** all acceptance and non-goals; integrate only exact accepted T1/T2/T3 outputs; Main alone edits this Plan and the primary worktree.
- **Outcome:** Verify exact seed-relative subtree outputs, integrate accepted paths serially, update current/package/semantic consistency, run deterministic focused checks, and freeze one candidate identity.
- **Non-goals:** No repair outside serialized packets, no commit, and no acceptance judgment before fresh verification.
- **Read:** T1/T2/T3 packets and evidence, all changed paths, current authority, project-owned quality guidance, Git object/mode/status data.
- **Allowed writes:** exact accepted T1/T2/T3 paths and this Plan.
- **Protected paths:** all unapproved paths, especially completed/superseded/generated/module-contract history, `.harness/runs/**`, legacy runtime surfaces, build outputs, and external systems.
- **Acceptance:** AC-1 through AC-9 except terminal fresh-verification judgment.
- **Verification:** exact seed-relative path/hash/mode checks, focused tests, doctor, compile where applicable, current/package parity, and `git diff --check` with protected exclusions.
- **Stop conditions:** unexpected or overlapping path, baseline mismatch, missing evidence, failing mandatory check, hidden state, scope expansion, or candidate mutation during verification.
- **Return:** integrated candidate identity, exact path set, focused results, unresolved failures, and residual risks.
- **Result:** complete.

### T9 — Integrated lifecycle assertion repair

- **Owner:** integration-test-repair
- **Role:** leaf
- **Parent:** none
- **Parallel group:** integration-repair
- **May delegate:** no
- **Inherited boundaries:** exact 21-path T1/T2/T3 integrated candidate `9498674bb62a1650aed70510792454d4056c0de46150d158cd0a6a63608d053a`; test-only correction; Main owns the Plan and integration.
- **Outcome:** Replace three obsolete hierarchy/template literal expectations with assertions for the integrated broad-root Owner contract while preserving the established compact-template limit.
- **Non-goals:** No source/doc/asset/other-test change, no assertion weakening, no template-line-limit increase, no runtime/history/external change.
- **Read:** integrated current/package authority, Skills, Plan templates, focused failure log, `tests/test_plan_lifecycle.py`, and this Plan.
- **Allowed writes:** `tests/test_plan_lifecycle.py` only in its isolated integrated-candidate worktree.
- **Protected paths:** this Plan; all docs/assets/source/other tests; completed/superseded/generated/module-contract history; runtime/build paths; `.harness/runs/**`; external systems.
- **Acceptance:** current/package policy test expects the new broad-root/Owner-local topology and serialization/resume clauses; optional-hierarchy test expects `task_graph: 1` and new root wording; generated-policy test distinguishes root Owner dispatch from resumed Owner descendant dispatch; compact limit remains `<120`.
- **Verification:** run the targeted failed lifecycle tests, full `tests.test_plan_lifecycle`, compile, and explicit-path diff hygiene on the integrated candidate.
- **Stop conditions:** a non-test path must change, compact limit would weaken, frozen contract conflicts, old coverage is removed, delegation, or protected-path uncertainty.
- **Return:** exact test hash/mode/diff, three failure dispositions, command results, discoveries, and residual risks.
- **Result:** complete.

### T10 — Compact current/package Plan template repair

- **Owner:** compact-template-repair
- **Role:** leaf
- **Parent:** none
- **Parallel group:** integration-repair
- **May delegate:** no
- **Inherited boundaries:** exact 21-path integrated candidate `9498674bb62a1650aed70510792454d4056c0de46150d158cd0a6a63608d053a`; two counterpart template writes only; Main owns the Plan and integration.
- **Outcome:** Reduce current and packaged Plan templates below 120 lines while retaining every strict graph field, broad Owner checkpoint, direct serial compatibility, checkpoint/restart content, verification summary, and terminal lifecycle section.
- **Non-goals:** No test/source/other-doc/Skill/inventory/path/runtime/history/external change and no removal of required compact headings or strict semantics.
- **Read:** both integrated Plan templates, current/package PLANS and AGENTS guidance, relevant template/lifecycle/asset/documentation tests, and this Plan.
- **Allowed writes:** `docs/exec-plans/_template.md` and packaged `docs/exec-plans/_template.md.tmpl` only in its isolated integrated-candidate worktree.
- **Protected paths:** this Plan; all other docs/assets/source/tests; package inventory/paths; completed/superseded/generated/module-contract history; runtime/build paths; `.harness/runs/**`; external systems.
- **Acceptance:** both templates remain semantically aligned, retain `format: 2` and `task_graph: 1`, required headings/table/packet fields, one broad Task Owner and one narrow serial example, Main serialization/Owner resume/local aggregation/fresh verification guidance, and each has fewer than 120 lines.
- **Verification:** targeted compact/template/asset/documentation tests, explicit line counts, package inventory confirmation, compile where relevant, and exact two-path diff hygiene.
- **Stop conditions:** required contract cannot fit without weakening, another path/test must change, templates diverge semantically, inventory/path change, delegation, or protected-path uncertainty.
- **Return:** exact two hashes/modes/line counts, clause checklist, command results, discoveries, and residual risks.
- **Result:** complete.

### T5 — Fresh semantic verification

- **Owner:** semantic-verification
- **Role:** verification
- **Parent:** none
- **Parallel group:** verification
- **May delegate:** no
- **Inherited boundaries:** AC-2, AC-6, AC-7, and AC-9; fresh read-only context; exact T4 candidate; implementation narration is unverified.
- **Outcome:** Independently verify strict graph semantics, backward compatibility, actionable findings, recursive IDs, and absence of runtime/state additions.
- **Non-goals:** No candidate repair, writes, delegation, Plan edits, or reinterpretation of acceptance.
- **Read:** exact T4 candidate, `src/reporivet/guided.py`, lifecycle tests, current/package Plan guidance, and project-owned quality commands.
- **Allowed writes:** none.
- **Protected paths:** entire candidate, this Plan, `.harness/runs/**`, external systems.
- **Acceptance:** AC-2, AC-6, AC-7, and relevant AC-9 checks.
- **Verification:** focused lifecycle/doctor/compile checks plus adversarial malformed graphs and candidate identity before/after.
- **Stop conditions:** candidate mutation, protected-path access, missing candidate identity, inability to run required checks, or repair temptation.
- **Return:** criterion-level pass/fail/unknown, exact commands/results, candidate identity before/after, residual risks, and no repair.
- **Result:** complete.

### T6 — Fresh authority and package verification

- **Owner:** authority-verification
- **Role:** verification
- **Parent:** none
- **Parallel group:** verification
- **May delegate:** no
- **Inherited boundaries:** AC-1 through AC-5, AC-7, AC-8, and AC-9; fresh read-only context; exact T4 candidate; implementation narration is unverified.
- **Outcome:** Independently verify current/package/Skill/README parity, bounded Owner checkpoint and nested native-Agent behavior, Main authority, independent verification, compatibility, and no runtime claim.
- **Non-goals:** No candidate repair, writes, delegation, Plan edits, protected history, or external action.
- **Read:** exact T4 candidate, current and packaged authority/Skills/templates, focused documentation/asset tests, and project-owned quality guidance.
- **Allowed writes:** none.
- **Protected paths:** entire candidate, this Plan, `.harness/runs/**`, external systems.
- **Acceptance:** AC-1 through AC-5, AC-7, AC-8, and relevant AC-9 checks.
- **Verification:** focused documentation/Claude asset/package tests, clause and path parity, no-runtime negative assertions, links, and candidate identity before/after.
- **Stop conditions:** candidate mutation, protected-path access, missing candidate identity, inability to run required checks, or repair temptation.
- **Return:** criterion-level pass/fail/unknown, exact commands/results, candidate identity before/after, residual risks, and no repair.
- **Result:** complete.

### T7 — Fresh regression verification

- **Owner:** regression-verification
- **Role:** verification
- **Parent:** none
- **Parallel group:** verification
- **May delegate:** no
- **Inherited boundaries:** AC-9 and regression coverage for all criteria; fresh read-only context; exact T4 candidate; implementation narration is unverified.
- **Outcome:** Independently verify the full project-owned regression, compile, doctor, package inventory, link/parity, source/path hygiene, and clean candidate identity.
- **Non-goals:** No candidate repair, writes, delegation, Plan edits, release, build publication, or external action.
- **Read:** exact T4 candidate, current quality/operations commands, tests and changed paths; exclude `.harness/runs/**` from all traversal and pathspecs.
- **Allowed writes:** none except disposable external `/tmp` interpreter cache/test artifacts.
- **Protected paths:** repository candidate, this Plan, `.harness/runs/**`, external systems.
- **Acceptance:** AC-9 and regression protection for AC-1 through AC-8.
- **Verification:** full unittest discovery, compileall with external cache, doctor, package data/inventory/link/parity checks, `git diff --check`, exact status/path/mode review, and candidate identity before/after.
- **Stop conditions:** candidate mutation, protected-path access, missing identity, test artifact in repository, inability to run required checks, or repair temptation.
- **Return:** criterion-level pass/fail/unknown, exact commands/results, candidate identity before/after, residual risks, and no repair.
- **Result:** complete.

### T8 — Main terminal judgment

- **Owner:** main
- **Role:** leaf
- **Parent:** none
- **Parallel group:** terminal
- **May delegate:** no
- **Inherited boundaries:** all acceptance and non-goals; Main alone judges evidence and moves the Plan.
- **Outcome:** Bind fresh evidence to the unchanged candidate, record criterion-level results and follow-ups, and move this Plan to completed only if every acceptance criterion passes.
- **Non-goals:** No detailed verifier rerun, self-approval, commit, release, publication, or external action.
- **Read:** T4 candidate identity and T5/T6/T7 evidence.
- **Allowed writes:** this Plan and its terminal move only.
- **Protected paths:** all implementation paths, completed history other than this Plan's terminal destination, `.harness/runs/**`, external systems.
- **Acceptance:** AC-1 through AC-9.
- **Verification:** candidate identity equality across T4/T5/T6/T7, complete criterion mapping, terminal status/outcome consistency, and exact Plan move.
- **Stop conditions:** failed/unknown criterion, candidate mismatch or mutation, incomplete evidence, or unresolved scope conflict.
- **Return:** final outcome, evidence summary, residual risks, follow-ups, and working-tree status.
- **Result:** complete.

## Broad-milestone decomposition

T1, T2, and T3 are broad Task Owner roots. Each first proposes a finite child manifest inside the exact packet above. Main reviews and serializes every accepted child row and matching packet here, freezes shared interfaces and exact worktrees, then resumes that Owner. Only the resumed Owner dispatches its dependency-ready children. A newly discovered child or changed boundary returns to Main for another serialization checkpoint before execution.

Independent root Owners run concurrently. Mutable siblings require disjoint allowed-write sets, one immutable seed, separate sibling worktrees, and an explicit parent-local aggregation node. Owner-local tests/review do not satisfy independent acceptance; T5, T6, and T7 begin only after Main freezes T4's integrated candidate.

## Current checkpoint

PLAN-2026-0005 is complete at baseline `8245f672fbdf4030d38dda34e6fc23ea0ea8d006`. T4 integrated all accepted Owner outputs and bounded repairs into exact dirty-tree candidate `59f537630f9f68434258e2f2bd9dfb33b17eb4edb3fc9a1579a12ac26e753341`; T5, T6, and T7 independently verified that unchanged candidate, and T8 bound their criterion-level evidence. No candidate mutation occurred during verification.

## Exact next action

None for this Plan. Preserve the uncommitted candidate; commit, push, release, or publication requires separate user authority.

## Decisions

- Use `task_graph: 1` as an explicit strict semantic-validation marker while preserving unmarked compact and historical Plan compatibility.
- Make the Owner manifest → Main serialization → Owner resume sequence the visible substitute for hidden dynamic task creation.
- Keep Owner-local aggregation separate from Main repository integration and fresh independent verification.
- Use no package-side concurrency cap or execution runtime; host/project capacity governs ready native-Agent dispatch.
- Preserve the exact nine-field ProcedureSpec (`slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, `rollback`) as canonical; normalize the current harness migration reference rather than broadening the schema.
- Freeze the root/nested distinction: Main dispatches independent root Owners; only a resumed serialized Task Owner dispatches its own declared descendants; ordinary leaves never delegate.
- Keep strict state/dependency ordering, but exclude unrequested row/packet Outcome or Result prose-parity checks.

## Discoveries

- Existing recursive task IDs and row/packet structural checks are reusable, but current validation does not enforce role, parent, delegation, dependency, cycle, integration, or verification semantics.
- Existing current and packaged hierarchy guidance already has Task Owner fields, but treats Owner delegation as an exception and assigns complete leaf dispatch to Main.
- The harness migration reference used aliases rejected by the current exact-nine-field ProcedureSpec; T1-A may correct only that stale reference wording under the canonical schema.
- Root integration needs different sibling coverage from owner-local integration: only a non-root parent-local integration is required to depend on every mutable sibling, avoiding a false dependency on later root terminal tasks.

## Documentation impact

- Current-state authority, bilingual READMEs, product/design/quality guidance, SPEC/DESIGN 003, the migration reference, and the current Plan template now express the bounded Task Owner hierarchy.
- Packaged AGENTS/PLANS/Plan and role Skill templates now carry the same contract for future installs while preserving create-if-missing ownership.
- Durable decisions are captured by this completed Plan; no separate ADR or follow-up is required.

## Integration summary

- Candidate identity: dirty-tree 21-path content/mode fingerprint `59f537630f9f68434258e2f2bd9dfb33b17eb4edb3fc9a1579a12ac26e753341`; binary patch SHA-256 `078a992d8e4fc401b709138e8db6038ce79d78c129010edad758c6de01ff80ff`; baseline `8245f672fbdf4030d38dda34e6fc23ea0ea8d006`.
- Integrated changes: exact 12-path T1 authority candidate, seven-path T2 package candidate, two-path T3 semantic candidate, test-only T9 repair, and two-template T10 repair; the final tracked path set remains exactly 21 paths and both Plan templates are byte-identical 119-line files.
- Focused integration evidence: 61/61 lifecycle/asset/documentation/distribution tests passed; compile passed; doctor returned no new errors after the Main-owned Plan structure correction; `git diff --check` passed.
- Residual risks: no acceptance-blocking risk remains. The candidate is intentionally uncommitted and is identified by reproducible content/mode and patch hashes; existing doctor warnings are pre-existing operational notices outside this change.

## Verification summary

| Criterion | Candidate | Verifier | Result | Decision-bearing evidence |
|---|---|---|---|---|
| AC-1 through AC-5 | `59f537630f9f68434258e2f2bd9dfb33b17eb4edb3fc9a1579a12ac26e753341` | T6 fresh authority/package verifier | PASS | 29 authority/package/distribution tests plus three hierarchy-policy tests passed; direct clause review confirmed broad Owner defaults, durable manifest serialization/resume, host-native nested dispatch, inherited isolation, Main-only integration, and fresh nondelegating verification. |
| AC-6 and AC-7 | `59f537630f9f68434258e2f2bd9dfb33b17eb4edb3fc9a1579a12ac26e753341` | T5 fresh semantic verifier | PASS | 32 lifecycle tests and 14 adversarial probes passed; compile and doctor passed with zero errors; private marker-gated graph checks cover roles, parents, dependencies, cycles, state ordering, integration, verification, and compatibility without runtime/state additions. |
| AC-8 | `59f537630f9f68434258e2f2bd9dfb33b17eb4edb3fc9a1579a12ac26e753341` | T6 fresh authority/package verifier | PASS | Current/package/Skill and bilingual README semantics align; ProcedureSpec remains the exact nine fields; both Plan templates are byte-identical 119-line files; the 29-asset inventory and seven package-data patterns remain unchanged. |
| AC-9 | `59f537630f9f68434258e2f2bd9dfb33b17eb4edb3fc9a1579a12ac26e753341` | T5/T6/T7 fresh verifiers | PASS | T7 full discovery passed 120 tests; compileall, doctor with zero errors, and `git diff --check` passed; exact 21-path/mode inventory and artifact hygiene passed; all final identity checks matched fingerprint `59f53763…3341` and patch SHA-256 `078a992d…80ff`. |

## Follow-ups

- None.

## Outcome

complete
