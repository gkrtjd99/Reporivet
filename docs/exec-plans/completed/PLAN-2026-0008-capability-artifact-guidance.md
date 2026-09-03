---
id: PLAN-2026-0008
kind: exec-plan
format: 2
task_graph: 1
status: completed
owner: main
area: guided-artifact-generation
created: 2026-09-03
updated: 2026-09-03
supersedes: ""
superseded_by: ""
base_commit: "ce2c36c"
integrated_commit: ""
verified_commit: ""
---

# Add question-driven capability artifact guidance

## Original goal

Make generated artifact documents self-guiding and capability-aware: ask visible, constrained setup questions; preserve the distinction between Confirmed, Proposed, Open, and Sources; generate conditional ordinary Markdown artifacts only from explicit confirmation; and state each artifact's purpose, ownership, evidence, verification, and non-goals clearly.

## Observable outcome and acceptance

- **AC-1 — Explicit capability selection:** The visible definition flow appends typed, constrained `web_ui` and `deployed_runtime` confirmations (canonical `yes`/`no` values). Scanner/audit observations remain Proposed and never activate optional artifacts; legacy seven-topic drafts remain readable with optional capabilities defaulting to Open.
- **AC-2 — Conditional artifact bundle:** The existing universal bundle remains unchanged for an unconfirmed generic project. Confirmed `web_ui: yes` adds `docs/FRONTEND.md`; confirmed `deployed_runtime: yes` adds `docs/RELIABILITY.md`; `docs/DESIGN.md` remains the universal canonical visual/design artifact. No optional artifact is created for Proposed, Open, Sources-only, `no`, or inferred evidence.
- **AC-3 — Artifact guidance:** Current and generated canonical documents, plus applicable authoring templates, state their purpose/scope, ownership and authority route, constraints/non-goals, evidence/provenance expectations, and project-owned verification boundary. `DESIGN.md` stays visual/interaction-focused; `FRONTEND.md` covers implementation and client-side reliability; `RELIABILITY.md` covers service/runtime SLI/SLO, failure modes, observability, deployment/rollback, and recovery without inventing claims. Unfinished placeholders are not labeled Confirmed.
- **AC-4 — Safe deterministic setup:** Optional files use the existing preview fingerprint, exact approval, conflict/preservation, immediate preimage validation, backup/rollback, and transactional write mechanisms. Existing project-owned files, symlinks, nonregular paths, unsafe paths, and unreadable targets retain current preservation/refusal behavior.
- **AC-5 — Package-independent boundary:** No `/dev`, runtime, scheduler, dispatcher, task store, command wrapper, doctor command, generated settings, marker, hidden state, automatic Plan, target Skill, or project-command execution is introduced. The target remains useful after package removal; `init`, `upgrade`, and legacy migration semantics remain bounded and compatible.
- **AC-6 — Verification and distribution:** Focused behavior, template-contract, package-data/distribution, documentation-contract, migration-compatibility, compile, and patch-hygiene checks pass; generic projects continue to omit conditional reliability/frontend files as appropriate.

## Scope

- Visible definition/evidence model and conditional asset selection in `src/reporivet/guided.py`, reusing existing draft parsing/rendering, asset rendering, preview, fingerprint, conflict, preimage, and transaction utilities.
- New packaged templates `docs/FRONTEND.md.tmpl` and `docs/RELIABILITY.md.tmpl` under the document-first asset tree.
- Document-first canonical and authoring templates that define artifact responsibilities, including root routing, the document map, core documents, and nested design/decision/specification/runbook/Plan scaffolds. Keep status vocabularies distinct and preserve the strict nine-field runbook contract.
- Current authority/document-map wording required to keep the repository's own contract and packaged templates aligned, including the supplemental relation of runtime reliability guidance to `OPERATIONS.md`.
- Focused and regression tests for explicit confirmation, inference non-activation, conditional inventories, content/role constraints, preservation/conflict/fingerprint/rollback, package independence, distribution inventory, and legacy migration.

## Non-goals

- No generated `/dev` surface, command runner, doctor, wrapper, runtime, scheduler, dispatcher, task database, journal, evidence archive, automatic Plan creation/closure, target Skill, settings file, marker, or hidden state.
- No automatic capability inference from filenames, manifests, source paths, scripts, CI, or deployment files; no free-text substring activation.
- No overwrite or rewrite of differing project-owned documents; no destructive cleanup beyond existing exact, preview-bound legacy ownership rules.
- No project command execution, deployment, release, publication, authentication/authorization, persisted-data, or public API change outside the bounded visible definition answer contract.
- No new `PRODUCT_SENSE.md` or `QUALITY_SCORE.md` generation without a separate trigger and evidence contract; no invented scores, SLOs, topology, telemetry, release, or recovery claims.
- No modification of `temp.md`, completed historical Plan bodies, or retained historical runtime fixtures.

## Task state

| Task | Owner | State | Depends on | Parallel group | Outcome | Result |
|---|---|---|---|---|---|---|
| T1 | main | completed | none | serial | Coordinate bounded capability-aware artifact implementation, integration, and fresh verification | Integrated, independently verified, and ready for manual terminal transition. |
| T1-A | implementation-sub | completed | T1 | serial | Add backward-compatible explicit capability evidence and conditional setup bundle selection | Implemented in `src/reporivet/guided.py`; generic setup, init, upgrade, and migration boundaries preserved. |
| T1-B | implementation-sub | completed | T1-A | serial | Add optional artifact templates and reconcile current/generated guidance and authority routing | Added conditional frontend/runtime templates and reconciled current/generated authority guidance without runtime surfaces. |
| T1-C | implementation-sub | completed | T1-B | serial | Add focused regression, distribution, documentation-contract, and migration-boundary tests | Added coverage for capability selection, safety, distribution, documentation contracts, and migration compatibility; full suite passes. |
| T1-I | main | completed | T1-C | serial | Aggregate child evidence and integrate the candidate | Reviewed changed paths, added optional rollback coverage, and recorded the dirty-tree candidate fingerprint. |
| T1-V | verification-sub | completed | T1-I | fresh | Verify the integrated candidate read-only against AC-1 through AC-6 | Fresh verifier matched the candidate and accepted AC-1 through AC-6; no in-scope residual risk. |

## Task Packets

### T1 — broad implementation Owner

- **Owner:** main-assigned Task Owner
- **Role:** Task Owner
- **Parent:** none
- **Parallel group:** serial until the child manifest is accepted
- **May delegate:** yes
- **Child budget:** up to four bounded children, with disjoint write sets and exact-baseline isolation
- **Exact baseline:** `ce2c36c`
- **Inherited boundaries:** AC-1 through AC-6; preserve one-shot package-side setup and all non-goals; do not touch `temp.md`, completed historical bodies, retained runtime fixtures, or external systems.
- **Outcome:** Return a finite child manifest within this envelope. After Main serializes accepted child rows and complete matching packets into this Plan, coordinate implementation and owner-local aggregation, then return Plan-ready evidence. Main separately integrates and judges final evidence.
- **Non-goals:** Scope expansion, runtime/orchestration features, unbounded document redesign, public API changes beyond the approved visible capability input, destructive cleanup, and self-approval.
- **Read:** `AGENTS.md`, `docs/README.md`, `ARCHITECTURE.md`, `docs/PRODUCT.md`, `docs/PLANS.md`, `docs/QUALITY.md`, `docs/SECURITY.md`, `docs/OPERATIONS.md`, `src/reporivet/guided.py`, `src/reporivet/initializer.py`, `src/reporivet/setup.py`, `src/reporivet/migration.py`, relevant assets and tests named by accepted child packets.
- **Allowed writes:** Only paths explicitly assigned by Main in accepted child packets; expected areas are guided implementation, document-first templates/current documentation, and tests/package-contract fixtures. The Task Owner must not edit this shared Plan concurrently.
- **Protected paths:** `temp.md`, `.harness/runs/**`, completed historical Plan bodies, unrelated source behavior, external targets, credentials, and all paths not assigned in a child packet.
- **Acceptance:** AC-1 through AC-6, with criterion-level evidence returned for each.
- **Verification:** Use project-owned commands in `docs/QUALITY.md`; run focused setup/document/distribution tests, compile checks, `git diff --check`, and the applicable full regression suite in a fresh verification context after Main integration.
- **Stop conditions:** Conflicting current authority, need for an unlisted public surface or production dependency, inability to preserve old drafts/migration behavior, unsafe target mutation, failed required checks, or an acceptance criterion requiring unsupported evidence.
- **Return:** finite child manifest first; after resumed execution, changed paths, child results, exact candidate identity, commands/results, criterion mapping, discoveries, residual risks, and recommended integration action.

## Broad-milestone decomposition

The first Task Owner dispatch did not return a manifest within the execution window. Main therefore accepted this bounded fallback manifest without broadening the approved envelope. Children are strictly serial because the definition schema and generated-document contracts are shared interfaces and repository commits are not authorized for this request.

### T1-A — guided capability and bundle implementation

- **Owner:** implementation-sub
- **Role:** leaf
- **Parent:** T1
- **Parallel group:** serial
- **May delegate:** no
- **Depends on:** none
- **Exact baseline:** `ce2c36c`
- **Outcome:** Add backward-compatible visible `web_ui` and `deployed_runtime` yes/no evidence, select optional assets only from exact Confirmed `yes`, and preserve generic init/upgrade/migration behavior through the existing preview/apply transaction.
- **Read:** `AGENTS.md`, `docs/README.md`, `docs/PLANS.md`, `src/reporivet/guided.py`, `src/reporivet/setup.py`, `src/reporivet/initializer.py`, `src/reporivet/migration.py`, and relevant guided/setup tests.
- **Allowed writes:** `src/reporivet/guided.py`, `src/reporivet/setup.py`, `src/reporivet/migration.py` only when required to keep migration explicitly generic; no tests or assets.
- **Protected paths:** all templates and docs, all tests, `temp.md`, `.harness/runs/**`, completed Plans, package metadata, and unrelated source.
- **Acceptance:** AC-1, AC-2, AC-4, AC-5; old seven-topic drafts parse, no inferred capability activates output, exact Confirmed yes selects the intended files, and preview/apply/rollback invariants remain intact.
- **Verification:** `python -m unittest tests.test_guided_setup tests.test_setup_flow tests.test_migration` (record any expected contract-test updates for T1-C), `python -m compileall -q src tests`, and `git diff --check`.
- **Stop conditions:** need for a new public CLI flag, incompatible draft migration, implicit inference, mutation outside current helpers, or any runtime/doctor/wrapper/hidden-state feature.
- **Return:** changed paths, interface notes for T1-B/C, command results, and residual risks.

### T1-B — artifact templates and authority guidance

- **Owner:** implementation-sub
- **Role:** leaf
- **Parent:** T1
- **Parallel group:** serial
- **May delegate:** no
- **Depends on:** T1-A
- **Exact baseline:** candidate returned by T1-A
- **Outcome:** Add ordinary Markdown `FRONTEND` and `RELIABILITY` templates and make current/generated artifact guidance explicit about purpose, scope, ownership, evidence/provenance, verification, constraints, and non-goals; reconcile optional reliability as supplemental to `OPERATIONS.md`.
- **Read:** `AGENTS.md`, `docs/README.md`, `ARCHITECTURE.md`, `docs/PRODUCT.md`, `docs/DESIGN.md`, `docs/QUALITY.md`, `docs/OPERATIONS.md`, `docs/SECURITY.md`, `docs/PLANS.md`, current product/design authority, and all document-first templates touched.
- **Allowed writes:** new `src/reporivet/assets/project/document-first/docs/FRONTEND.md.tmpl` and `RELIABILITY.md.tmpl`; matching document-first root/core/nested templates; current authority/document-map files required for parity. Do not edit Python or tests.
- **Protected paths:** all Python, tests, `temp.md`, `.harness/runs/**`, completed Plans, package metadata unless T1-C identifies a pure inventory correction, and unrelated docs/history.
- **Acceptance:** AC-3 and AC-5; `DESIGN` remains visual, `FRONTEND` covers frontend implementation/client reliability, `RELIABILITY` covers runtime reliability without invented claims, evidence sections remain distinct, TODO placeholders are not Confirmed, and no generated runtime surface is described or added.
- **Verification:** `git diff --check`; static link/heading/forbidden-boundary checks available in the existing documentation tests (T1-C reruns the complete set); compare current/template responsibility wording.
- **Stop conditions:** an authority conflict that cannot be reconciled without changing product scope, a need to add a new taxonomy family, or any instruction that introduces package/runtime dependence.
- **Return:** changed paths, template/content contract, current-authority reconciliation, and residual risks.

### T1-C — focused regression and distribution coverage

- **Owner:** implementation-sub
- **Role:** leaf
- **Parent:** T1
- **Parallel group:** serial
- **May delegate:** no
- **Depends on:** T1-B
- **Exact baseline:** candidate returned by T1-B
- **Outcome:** Encode the conditional capability, legacy compatibility, safety, package-data, documentation, migration-neutrality, and no-runtime acceptance contract in tests without weakening existing assertions.
- **Read:** T1-A/B changed paths; `docs/QUALITY.md`; `tests/test_guided_setup.py`; `tests/test_setup_flow.py`; `tests/test_setup_cli.py`; `tests/test_reporivet.py`; `tests/test_distribution.py`; `tests/test_claude_assets.py`; `tests/test_documentation_contract.py`; `tests/test_migration.py`; `tests/test_one_shot_bootstrapper.py`; `tests/test_plan_lifecycle.py`; `tests/test_audit_adoption.py`.
- **Allowed writes:** only the named test files and other existing test files required by the same acceptance contract; no source, assets, current docs, Plan, or user files.
- **Protected paths:** all production code/assets/docs, `temp.md`, `.harness/runs/**`, completed Plans, and external systems.
- **Acceptance:** AC-1 through AC-6 are represented by focused tests for explicit yes/no, Proposed/Open/Sources-only and inference non-activation, old drafts, selected previews/fingerprints/stale approval, preservation/conflict/rollback, generic init/upgrade/migration, package inventory, ordinary Markdown/no runtime, and existing Plan/runbook/audit boundaries.
- **Verification:** `python -m unittest discover -s tests -p 'test_*.py'`, `python -m compileall -q src tests`, `git diff --check`, and the distribution test's package-data assertions.
- **Stop conditions:** a failing test reveals an unapproved behavior change, tests require weakening an existing boundary, or package-data cannot be verified without unrelated build changes.
- **Return:** changed test paths, exact commands/results, criterion mapping, and residual risks.

### T1-I — Main integration and owner aggregation

- **Owner:** main
- **Role:** integration
- **Parent:** T1
- **Depends on:** T1-C
- **Allowed writes:** this active Plan only; repository integration uses the already shared working tree and does not commit or push.
- **Outcome:** Review child evidence, inspect changed paths, reconcile any bounded issues, record the integrated candidate identity, and prepare fresh verification packets.
- **Verification:** exact changed-path review, `git status --short`, `git diff --check`, and the project-owned checks named by T1-C.
- **Return:** integrated candidate fingerprint/commit if available, criterion mapping, documentation impact, and residual risks.

### T1-V — fresh read-only verification

- **Owner:** verification-sub
- **Role:** Verification Sub
- **Parent:** T1
- **Depends on:** T1-I
- **May delegate:** no
- **Allowed writes:** none.
- **Protected paths:** entire repository and external systems; verification is read-only and nonrepairing.
- **Outcome:** Identify the integrated candidate from a fresh context and verify AC-1 through AC-6 independently.
- **Read:** active Plan, changed paths, current authority, and project-owned quality/operations instructions.
- **Verification:** full applicable test suite, compile checks, `git diff --check`, exact generic and explicit-capability generated-tree checks, package-independent handoff checks, and forbidden-surface checks.
- **Stop conditions:** candidate identity is ambiguous, required checks fail, or evidence is missing; do not repair.
- **Return:** criterion-level accepted/failed/not-established results, exact commands, candidate identity, and residual risks.

## Current checkpoint

T1-A, T1-B, and T1-C are integrated in the shared working tree. The implementation appends constrained visible `web_ui` and `deployed_runtime` topics, treats missing legacy fields as Open, selects optional files only from exact Confirmed `yes`, and keeps `init`, `upgrade`, and 0.2 migration generic. Current and generated documents distinguish DESIGN, FRONTEND, and supplemental RELIABILITY responsibilities, preserve evidence-state separation, and reject invented operational claims. Focused rollback coverage now exercises removal of a newly created optional file after a later mutation failure.

The reproducible dirty-tree candidate identity is `aeed7d452575931a9d8a7110ed18c941ef453d769de5a510e3eafedaef0e40b1`. It hashes the sorted current changed/untracked paths, their regular-file bytes or symlink targets, and permission modes, excluding the lifecycle copy of this Plan (`docs/exec-plans/active/PLAN-2026-0008-capability-artifact-guidance.md` or its completed destination) and protected `temp.md`; no commit was created or authorized.

## Exact next action

Main records the completed fresh-verification evidence, changes this Plan status to `completed`, and moves it manually to `docs/exec-plans/completed/`. No commit, push, publication, deployment, or other external action is authorized by this Plan.

## Decisions

- Keep `docs/DESIGN.md` in the universal bundle; do not create a second design artifact path.
- Confirm web UI and deployed runtime separately: `FRONTEND.md` covers frontend implementation/client reliability, while `RELIABILITY.md` is an optional supplemental runtime document subordinate to `OPERATIONS.md`.
- Use explicit constrained capability evidence rather than matching arbitrary free text or activating from scanner findings.
- Reuse the existing visible Markdown definition as the only resume state and existing exact preview/apply transaction as the only mutation mechanism.
- Treat Plans, audit statuses, setup states, preview actions, and document evidence states as distinct namespaces.

## Discoveries

- Existing generic-target tests intentionally require `docs/RELIABILITY.md` and forbidden runtime surfaces to be absent; conditional tests must preserve this baseline.
- Existing distribution tests include a retired-name assertion for reliability assets and require a deliberate update when the supported template is added.
- The product-specification scaffold risks treating literal `TODO` placeholders as Confirmed; in-scope template correction must move placeholders to Open/Proposed or a clearly non-authoritative scaffold section.
- Historical profile behavior that generated reliability documents is coupled to retired runtime/doctor/wrapper behavior and is not a source for the new conditional bundle.

## Documentation impact

- Changed current and generated artifact maps and authority guidance so DESIGN is universal, FRONTEND is conditional on `web_ui=yes`, and RELIABILITY is conditional on `deployed_runtime=yes` and subordinate to OPERATIONS.
- Added artifact-specific purpose, ownership, evidence/provenance, verification, constraints, and non-goals across core and authoring templates; moved unfinished scaffold material out of Confirmed sections.
- Follow-up: broader taxonomy families such as Product Sense and Quality Score, and historical/source-project document migration, remain out of scope.

## Integration summary

- Candidate identity: dirty-tree fingerprint `aeed7d452575931a9d8a7110ed18c941ef453d769de5a510e3eafedaef0e40b1`, computed from 42 changed/untracked paths with file bytes or symlink targets and permission modes, excluding the lifecycle copy of this Plan and `temp.md`; no commit was created.
- Integrated changes: `src/reporivet/guided.py` now validates and applies the two explicit capability topics through the existing preview/apply transaction. Added `docs/FRONTEND.md.tmpl` and `docs/RELIABILITY.md.tmpl`; updated current/generated guidance and the named regression/distribution/documentation/migration tests. Added an optional-file rollback assertion without changing production transaction code.
- Main checks: `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/reporivet-pycache" PYTHONPATH=src /opt/homebrew/bin/python3.13 -m unittest tests.test_setup_flow -v` — 12 passed; `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/reporivet-pycache" PYTHONPATH=src /opt/homebrew/bin/python3.13 -m unittest discover -s tests -p 'test_*.py'` — 122 passed; `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/reporivet-pycache" PYTHONPATH=src /opt/homebrew/bin/python3.13 -m compileall -q src tests` — passed; `git diff --check` — passed.
- Fresh verification: the independent Verification Sub recomputed the same fingerprint; its focused command covering guided setup, setup flow, migration, distribution, documentation, one-shot, repository, Claude assets, Plan lifecycle, and audit tests passed 106 tests. Static capability/forbidden-surface checks and exact temporary-target inventories passed: generic 26 files, web UI 27, deployed runtime 27, both 28; every package-free handoff remained usable and `CLAUDE.md` was exactly `@AGENTS.md\n`.
- Residual risks: none within AC-1 through AC-6. Wheel publication, deployment, CI repair/readiness, and external release evidence remain outside scope.

## Verification summary

| Criterion | Candidate | Verifier | Result | Decision-bearing evidence |
|---|---|---|---|---|
| AC-1 | `aeed7d452575931a9d8a7110ed18c941ef453d769de5a510e3eafedaef0e40b1` | fresh Verification Sub | accepted | Exact yes/no validation, legacy seven-topic compatibility, and non-confirming/inference tests passed. |
| AC-2 | `aeed7d452575931a9d8a7110ed18c941ef453d769de5a510e3eafedaef0e40b1` | fresh Verification Sub | accepted | Generic, independent, and combined temporary-target inventories matched the conditional bundle contract. |
| AC-3 | `aeed7d452575931a9d8a7110ed18c941ef453d769de5a510e3eafedaef0e40b1` | fresh Verification Sub | accepted | Current/generated document contracts and ordinary-Markdown/authority-boundary checks passed. |
| AC-4 | `aeed7d452575931a9d8a7110ed18c941ef453d769de5a510e3eafedaef0e40b1` | fresh Verification Sub | accepted | Fingerprint, stale approval, preservation/conflict, preimage, transaction, guarded rollback, and optional-file rollback checks passed. |
| AC-5 | `aeed7d452575931a9d8a7110ed18c941ef453d769de5a510e3eafedaef0e40b1` | fresh Verification Sub | accepted | Package-free handoff and forbidden-surface checks passed; no runtime/orchestration surface was introduced. |
| AC-6 | `aeed7d452575931a9d8a7110ed18c941ef453d769de5a510e3eafedaef0e40b1` | fresh Verification Sub | accepted | Full 122-test suite, focused 106-test suite, compileall, distribution, documentation, migration, and diff hygiene checks passed.

## Follow-ups

- None; broader taxonomy and release/publication work remain explicitly out of scope.

## Outcome

Complete. Fresh Verification Sub evidence accepted AC-1 through AC-6 for the recorded dirty-tree candidate. Main is performing the manual terminal transition to `docs/exec-plans/completed/`; no commit or external release action is implied.
