---
id: PLAN-2026-0003
kind: exec-plan
status: complete
owner: main
area: harness
created: 2026-08-31
updated: 2026-09-01
supersedes: PLAN-2026-0002
superseded_by: ""
base_commit: "5df73f7038f5f36aebeed19f5ab50a920f0e5424"
integrated_commit: ""
verified_commit: ""
product_spec: SPEC-REPORIVET-003
---

# Replace the repository runtime with a document-first Agent harness

## Purpose / Big Picture

Replace Reporivet's copied repository-local execution, Gate, evidence, CI, and maintenance runtime with an understandable bundle of canonical authority documents, Claude Code adapters/Skills, and durable Markdown Plans. A fresh installation must create no Reporivet `dev/`, `.harness/runs`, runtime configuration, generated CI, or completion engine. Existing 0.2 installations must migrate only through an explicit previewed, ownership-aware, reversible package command.

A person can confirm the outcome by inspecting the generated tree from `docs/README.md`, resuming Main from one active Plan, dispatching implementation and verification Subs against project-owned commands, and completing fresh-install, migration, rollback, wheel, and package-removal tests without any copied Reporivet executor.

## Progress

- [x] Establish the approved product boundary and durable replacement Plan.
- [x] Add the superseding product specification, design, and ADR.
- [x] Implement the document/Plan/Claude bundle and guided setup.
- [x] Implement explicit 0.2 preview, backup, migration, and rollback.
- [x] Flip fresh initialization and retire generated runtime surfaces.
- [x] Synchronize current authority and public documentation.
- [x] Independently verify the integrated candidate.
- [x] Productize integrated setup, confirmed procedure Skills, and first-Plan handoff.
- [x] Verify one exact wheel through pipx and pip installation and removal.

**Current checkpoint:** Complete. T6-V1/V2/V3/V4 accept AC-13 through AC-20 for source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4`. T7-A/B/C2 prove the exact read-only wheel `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` through complete inventory plus isolated pipx and pip install/use/uninstall lifecycles. The initial T7-C node remains discarded as a verifier-protocol failure. Fresh read-only T7-V1 independently rehashed and inspected the source, wheel, accepted manifests, retained repositories, removal state, and authority boundary; it passed AC-21 and found AC-1 through AC-21 sufficiently bound to the unchanged candidate with no blocker. No commit, publication, push, release, signing, or deployment occurred or is authorized.

**Exact next action:** None for this Plan. Preserve it under `docs/exec-plans/completed/`; any package publication, release, signing, tag, push, or deployment requires separate explicit authorization.

## Context and Orientation

The current package entry is `src/reporivet/cli.py`; safe root validation, audit, managed ownership, rendering, and rollback facilities live in `src/reporivet/initializer.py`. The copied runtime is `src/reporivet/assets/project/dev/harness.py`, with dogfood output in `dev/harness.py`, wrappers and `dev/harness.toml`, generated workflows, and `.harness/runs` evidence.

Current authority is routed from `AGENTS.md` and `docs/README.md`. This Plan supersedes [`PLAN-2026-0002`](../completed/PLAN-2026-0002-integrate-definition-and-retire-skill.md), whose implementation/evidence remains historical while its copied-runtime, Gate, generated-CI, code-map/context, and Skill-exclusion decisions are retired.

Read as applicable:

- `AGENTS.md`, `docs/README.md`, `docs/PRODUCT.md`, `ARCHITECTURE.md`
- `docs/DESIGN.md`, `docs/QUALITY.md`, `docs/SECURITY.md`, `docs/PLANS.md`
- `docs/product-specs/SPEC-REPORIVET-003-document-first-harness.md`
- `docs/design-docs/DESIGN-REPORIVET-003-document-first-harness.md`
- `docs/decisions/ADR-0001-document-first-product-boundary.md`
- `docs/references/project-definition-protocol.md`
- task-specific package, asset, test, and legacy contract paths named below

## Scope

- Package-side audit, guided definition, initialization/upgrade, migration/rollback, and read-only doctor.
- Canonical authority templates, compact future Plan lifecycle, Claude Code role/procedure Skills, and optional settings.
- Explicit retirement of generated runtime, wrappers, configuration, CI, evidence, Gate, context/code-map, and garden surfaces.
- Ownership-safe 0.2 migration and comprehensive fresh/legacy/distribution tests.
- Reporivet's own current docs and dogfood tree migration.
- Integrated guided `setup`, structure-only `init`, and exact machine-readable onboarding state.
- Complete user-confirmed project procedure Skills managed through resumed setup.
- Main Skill first-Plan handoff without a package-side Plan runtime.
- Genuine pipx and pip lifecycle verification from one exact wheel.

## Non-goals

- Agent scheduler, process supervisor, task database, journal, plugin runtime, MCP bridge, model judge, command runner, CI platform, deployment engine, secret scanner, or evidence archive.
- LLM-backed setup or automatic semantic promotion of repository inference.
- Compatibility wrappers for retired `./dev/*` commands.
- Automatic deletion of customized files, project-owned CI/docs, or `.harness/runs`.
- Non-Claude host adapters in this Plan.
- Publication, release, push, deployment, or other external action.

## Acceptance Criteria

- **AC-1 — Understandable generated tree:** `docs/README.md` explains every generated path, including optional hidden Claude paths, ownership, purpose, and removal boundary.
- **AC-2 — Canonical entry and routing:** `AGENTS.md` plus `docs/README.md` is sufficient for Main, implementation Sub, and Verification Sub routing; `CLAUDE.md` is only a thin adapter.
- **AC-3 — Evidence-safe guided setup:** scan/interview output preserves Confirmed, Proposed, Open, and Sources; no inference becomes Confirmed and users never choose document filenames.
- **AC-4 — Durable minimal Plans:** one substantive goal maps to one active Plan with goal, acceptance, task state, checkpoint, exact next action, decisions, discoveries, and compact integration/verification evidence. Main owns mutations and terminal Plans move to `completed/` with explicit outcome status.
- **AC-5 — Sub-Agent-first parallel execution:** the installed operating documents define one common rule for every broad milestone `T<n>`: decompose it into hierarchically named, individually owned child packets `T<n>-A`, `T<n>-B`, and so on; dispatch the complete dependency-ready leaf set concurrently rather than serially; recurse as `T<n>-A-1` only through an explicitly designated Task Owner; converge through `T<n>-I`; then run fresh `T<n>-V*` verification leaves in parallel. Ordinary leaf Agents do not delegate. Parallel mutable leaves use disjoint write sets or isolated worktrees with frozen shared interfaces. Main owns intent, the overall tree, serialized Plan updates, integration decisions, and evidence judgment. This is a generated project operating contract, not a requirement to restructure this implementation Plan's already completed T0–T3 history.
- **AC-6 — Project-owned execution:** Reporivet generates no command wrappers, CI, deployment, secret scanner, Verification Run, Gate, evidence archive, or automatic Plan closure.
- **AC-7 — Safe Claude profile:** Claude Skills/settings are optional adapters, catalogued, explicitly previewed, ownership-safe, instruction-only/least-privilege, and never silently merged into existing settings.
- **AC-8 — Operations authority:** `docs/OPERATIONS.md` is the single current run/release/observe/backup/rollback/recovery authority; fresh projects do not also receive `RELIABILITY.md`.
- **AC-9 — Explicit legacy migration:** ordinary upgrade refuses 0.2 retirement. Migration requires an unchanged preview fingerprint and explicit external backup, preserves ambiguous/project-owned content, and supports exact automatic and post-success rollback.
- **AC-10 — Historical readability:** completed/superseded Plans and legacy Gate fields remain readable; `.harness/runs` is preserved and no new code writes it.
- **AC-11 — Package boundary:** fresh init and wheel contents contain no copied runtime, wrapper, generated workflow, runtime config, code-map/context executor, Gate, or run writer. Package removal leaves documents, Skills, Plans, Git, and project commands useful, but no Reporivet maintenance command is promised.
- **AC-12 — Current authority parity:** public/current docs, templates, specs, designs, and ADRs agree on the new boundary; contradictory 0.2 contracts are explicitly superseded rather than silently rewritten.
- **AC-13 — Integrated setup CLI:** `reporivet setup` coordinates audit, visible guided definition, actual Open-state reporting, exact preview, and approved apply while lower-level `define` remains compatible and `init` remains structure-only.
- **AC-14 — Machine-readable setup result:** setup emits one canonical `reporivet.setup/v1` JSON envelope containing root, mode/state, audit, all seven evidence-state topics, draft state, exact nested preview/fingerprint, apply eligibility, input mode, changes, and next action without mixed stdout prose.
- **AC-15 — Guided safety and resumability:** setup audits once, never prompts in non-TTY or dry-run mode, keeps Open items visible and nonblocking, writes only the visible draft before approval, and preserves exact stale-preview, no-follow, conflict, settings, and rollback guarantees.
- **AC-16 — Confirmed procedure Skills:** only complete structured Confirmed procedure records generate deterministic instruction-only `.claude/skills/<slug>/SKILL.md` files; incomplete, generic, Proposed, Open, and Sources records generate none. Existing files are preserved, unsafe targets conflict, old Skills are never auto-deleted, and no command or permission grant executes.
- **AC-17 — Main-owned first Plan handoff:** setup creates no Plan. The Main Skill searches active/completed history, resumes one matching active Plan, stops on ambiguity, otherwise selects the lowest unused current-year ID and creates ordinary Markdown from `_template.md` without overwrite, hidden state, Plan CLI, or automatic closure.
- **AC-18 — Authority and history parity:** current/public/package authority agrees on setup, structure-only init, procedure Skills, Main Plan handoff, ownership, and exclusions; SPEC/DESIGN 003 distinguish implemented source behavior from artifact readiness; retired generated code-map/module-contract material is retained but visibly historical/superseded.
- **AC-19 — Distribution/removal contract:** public guidance is pipx-primary with pip support from the same wheel, source-checkout guidance remains contributor-only, uninstall leaves generated Markdown/Plans/Skills useful, and no unsupported publication/signing/deployment claim or runtime dependency is added.
- **AC-20 — Boundary regression:** focused and full checks pass without adding a scheduler, dispatcher, copied runner, generated CI, Gate, evidence archive, deployment engine, semantic LLM rewrite, settings merge, setup-created Plan, or automatic closure; init/define/upgrade/migration/settings/history behavior remains green.
- **AC-21 — Genuine artifact lifecycle:** one exact wheel is inspected and exercised through isolated pipx and pip setup/init/doctor/install/uninstall lifecycles, proving console/import removal and persistent repository usefulness without any retired runtime surface.

## Milestones

### M1 — Freeze the new authority boundary

Create the replacement Plan/spec/design/ADR while keeping the existing implementation runnable.

### M2 — Deliver package-side document setup and migration

Implement guided setup, compact templates, Claude assets, read-only doctor, and tested 0.2 migration before enabling deletion.

### M3 — Flip the generated tree and retire the runtime

Make document-first initialization the only default, remove proven-owned runtime assets, and replace runtime-bound tests.

### M4 — Reconcile authority and independently verify

Update current/public docs, exercise fresh and legacy paths, and obtain criterion-level evidence from a fresh Verification Sub.

## Task Packets

### T0 — Establish decision boundary

#### State

complete

#### Task type

support

#### Depends on

none

#### Outcome

Create this Plan, explicitly supersede terminal `PLAN-2026-0002`, and add SPEC-003, DESIGN-003, and ADR-0001 without changing runtime behavior.

#### Non-goals

Package/runtime changes, broad current-document rewrites, release, or external action.

#### Read

The old Plan; SPEC/DESIGN 001-002; decision template; approved implementation plan.

#### Allowed writes

This Plan; old Plan terminal metadata/location/link only; new SPEC/DESIGN/ADR records; supersession-only frontmatter/notices in SPEC/DESIGN 001-002; directly broken current references and managed document catalog blocks required to keep current checks coherent.

#### Protected paths

Old Plan task results/evidence body; source, tests, current-state documents, and other completed historical Plans.

#### Acceptance

AC-12; the new records state the retained/retired boundary and migration requirement, and old history remains readable.

#### Verify

Inspect links/frontmatter, run strict current Plan validation, and run `git diff --check`.

#### Stop conditions

A contradictory user decision, unknown next IDs, or a need to rewrite old historical results.

#### Result

Complete. Main created `PLAN-2026-0003`, archived `PLAN-2026-0002` as superseded without changing its task/criterion evidence, disabled only its now-obsolete live traceability opt-in, and repaired its direct current reference. A bounded documentation Sub created SPEC-003, DESIGN-003, and ADR-0001; Main reviewed them, marked SPEC/DESIGN 001-002 superseded, refreshed four managed catalogs, and confirmed strict Plan, documentation, catalog, routed-context, and patch-format checks.

### T1 — Build document, Plan, and Claude bundle

#### State

complete

#### Task type

implementation

#### Depends on

T0

#### Outcome

Implement compact templates, guided setup, Claude role/procedure Skills, an explicitly reviewed opt-in settings path, and read-only doctor using existing safe package facilities. The default Claude profile creates only a missing root `CLAUDE.md` containing `@AGENTS.md` and standard-compliant project Skills under `.claude/skills/`; it does not create live settings.

#### Non-goals

Migration deletion, runtime compatibility additions, project command execution, or generated CI.

#### Read

This Plan and SPEC/DESIGN/ADR-003; `src/reporivet/initializer.py`; CLI; current assets; audit/definition/ownership tests; current Claude Code settings and Skill documentation before finalizing settings syntax.

#### Allowed writes

Initializer/CLI and cohesive package helpers; root/docs/Claude assets; Plan template/policy; focused audit/definition/guided/Claude/Plan tests.

#### Protected paths

Legacy runtime/CI deletion, project-owned fixture content, and unrelated current documents.

#### Acceptance

AC-1, AC-2, AC-3, AC-4, AC-5, AC-7, AC-8.

#### Verify

Focused tests prove read-only scan/dry-run/doctor, resumable visible draft, evidence-state separation, create-if-missing preservation, compact Plan structure, root `CLAUDE.md` import semantics, standard-compliant Skill assets, live settings absent by default, and previewed create-if-missing settings opt-in without merge or privilege grants.

#### Stop conditions

Semantic inference is required, existing settings must be merged, ownership cannot be proven, or a new framework/dependency appears necessary.

#### Result

Complete. The candidate provides package-side guided definition, exact preview/apply, document-first authority assets, portable Claude role Skills, opt-in deny-only settings, compact Plan assets, and structural doctor. Three bounded repair rounds addressed the findings from three fresh verifiers. A fourth fresh Verification Sub kept candidate `0dc3e74e677e8ea772e411ed72d41cc1979cc8608dee6ac5fe0d4a7faaccad36` unchanged and passed AC-1, AC-2, AC-3, AC-4, AC-5, AC-7, and AC-8. Exact ancestry-race, Outcome, and retired-authority regressions pass; focused tests pass 31/31, relevant existing tests pass 63/63, compilation and patch hygiene pass, and all referenced document-first assets are package-covered. No applicable T1 defect remained within the requested scope.

### T2 — Add explicit 0.2 migration

#### State

complete

#### Task type

implementation

#### Depends on

T1

#### Outcome

Implement deterministic preview/fingerprint, ownership classification, explicit external backup, transactional apply, and manifest rollback while ordinary upgrade refuses legacy retirement.

#### Non-goals

Executing old runtime/config, deleting ambiguous files or `.harness/runs`, or automatically changing Plan status.

#### Read

This Plan and SPEC/DESIGN/ADR-003; safe path/ownership/snapshot helpers; canonical 0.2 assets; active/completed Plan formats; CI templates; migration tests.

#### Allowed writes

`src/reporivet/migration.py`, CLI dispatch, minimal shared safe helpers, migration tests/fixtures, and directly corresponding package docs.

#### Protected paths

Actual dogfood legacy assets until T3; customized/project-owned fixture bytes; completed Plans.

#### Acceptance

AC-9 and AC-10.

#### Verify

Stable preview, changed-preview refusal, symlink/nonregular refusal, canonical/custom mixed trees, active Plan blockers, retained evidence, failure-injection rollback, successful migration rollback, and post-migration-change refusal.

#### Stop conditions

A marker alone would authorize deletion, backup cannot be exact and visible, or rollback would overwrite new user changes.

#### Result

Complete. The candidate implements deterministic 0.2 preview/fingerprint, explicit external backup, ownership-aware apply, automatic failure restoration, post-success manifest rollback, legacy Plan blockers, retained completed history and `.harness/runs`, and ordinary-upgrade refusal. A fresh Verification Sub kept candidate `dd146b662167131c3f8e05f67c904059b8d47c6b174e6bf139af020eb9b234ae` unchanged and passed AC-9 and AC-10. All 12 migration, 4 directly affected upgrade, and 50 retained T1 tests passed, together with the packet's named independent preview, ownership, backup, rollback, blocker, history, `.harness/runs`, and upgrade-refusal reproductions.

### T3 — Flip initialization and retire runtime

#### State

complete

#### Task type

implementation

#### Depends on

T2

#### Outcome

Make the document-first tree the only fresh-install output and remove copied runtime/wrapper/config/workflow/code-map/Gate assets and runtime-only tests atomically.

#### Non-goals

Compatibility shims, replacement executors, current-document full rewrite, or publication.

#### Read

This Plan; completed T1/T2 results; initializer managed inventory; package data; runtime/wrapper/workflow assets; distribution/runtime tests; dogfood `dev/` ownership.

#### Allowed writes

Package initializer/CLI/inventory/assets; proven-owned dogfood runtime paths; runtime/distribution tests.

#### Protected paths

Project-owned `dev/` content or CI, `.harness/runs`, completed Plans, and unrelated code.

#### Acceptance

AC-6 and AC-11, while retaining all T1/T2 criteria.

#### Verify

Fresh init contains only the declared tree; the wheel has no retired assets; package removal leaves documents/Skills/Plans usable; no forwarding or fallback path remains.

#### Stop conditions

Ambiguous ownership, migration tests are not green, or removal leaves the repository/package unrunnable.

#### Result

Complete. The candidate makes document-first init/upgrade/doctor the only production package surface, removes retired runtime code/options/assets and 19 proven canonical dogfood runtime/wrappers, preserves project-owned `dev/harness.toml`, `.github/workflows/ci.yml`, `.harness/runs`, history, and migration, and retains guided definition coverage. A fresh narrow verifier kept candidate `e34084b93fa515a2cc6aa4b932fabfbadd9123433a111a647e6607e968e8cb5b` unchanged and passed T3, AC-6, and AC-11 after the ownership repair; prior full T3 evidence passed all 58 retained tests and static package boundaries.

### T4 — Synchronize current authority

#### State

complete

#### Task type

implementation

#### Depends on

T3

#### Outcome

Align Korean/English README, current authority, templates, protocol, operations, supersession notices, and knowledge maps with implemented behavior, including hierarchical owned task trees and concurrent dispatch of every dependency-ready leaf.

#### Non-goals

Rewriting historical Plan bodies, generic placeholder expansion, or unsupported operational claims.

#### Read

Exact integrated behavior/tests plus all current authority and public documents named by Documentation Impact.

#### Allowed writes

Current/public documents, active SPEC/DESIGN-003 wording, current and packaged `AGENTS.md`/`PLANS.md`/compact Plan/role Skill templates, supersession frontmatter/notices, catalogs, new `docs/OPERATIONS.md`; retire current `docs/RELIABILITY.md` authority; minimal Plan task-ID parsing and focused lifecycle/asset tests only if required for hierarchical IDs.

#### Protected paths

Implementation/tests except the minimal hierarchical task-ID parser and focused tests named above; completed Plan results/evidence; unrelated package behavior; and user-owned target fixtures.

#### Acceptance

AC-1, AC-2, AC-5, AC-8, and AC-12.

#### Verify

Current documents contain no live `./dev/*`, Gate/run/close-plan/generated-CI authority; bilingual semantics and package templates agree; links resolve; hierarchical IDs such as `T1-A` and `T1-A-1` map exactly to owned packets; all dependency-ready leaves are documented for concurrent dispatch; only explicit Task Owners may fan out children; mutable siblings require disjoint writes or isolated worktrees; `git diff --check` passes.

#### Stop conditions

Implementation and documentation disagree or a project-specific operational fact would need guessing.

#### Result

Complete. Current/public/package authority agrees with implemented T1–T3 behavior and the generic installed-project broad-milestone rule. A fresh Verification Sub kept candidate manifest `90e8ef2e7a91e0aaae188516adf9ab673635afcc6d28d8f5a6cf5533fd919f7d` unchanged and passed T4, AC-1, AC-2, AC-5, AC-8, and AC-12. The rule applies to every broad `T<n>` milestone, exempts inherently serial work, and covers owned descendants, complete ready-leaf parallel dispatch, explicit Task Owner-only fan-out, inherited boundaries, isolated writes, integration, and parallel fresh verification without adding runtime orchestration. Focused tests pass 27/27 and the full suite passes 63/63; doctor, links, CLI/bilingual parity, generated-surface coverage, template/policy parity, retired-reference scan, and patch hygiene pass.

### T5 — Independently verify integrated candidate

#### State

complete

#### Task type

verification

#### Depends on

T4

#### Outcome

Judge the exact integrated candidate criterion by criterion without relying on implementer summaries.

#### Non-goals

Redesign, repair, acceptance changes, publication, or external actions.

#### Read

This Plan, SPEC/DESIGN/ADR-003, current authority, the full diff, package/assets/tests, and migration fixtures.

#### Allowed writes

Verifier return only; Main alone updates this Plan after judgment.

#### Protected paths

Candidate, acceptance criteria, historical evidence, and external systems.

#### Acceptance

AC-1 through AC-12.

#### Verify

Python 3.11+ full unit/compile/diff checks; wheel inventory/isolated install/uninstall; fresh init; guided setup; Plan resume; migration preview/apply/rollback; ownership/path/settings adversarial cases; deletion and documentation parity review.

#### Stop conditions

The candidate changes during verification, any criterion lacks evidence, or the environment prevents a required check.

#### Result

Complete through combined fresh evidence. The first fresh T5 node remains invalid because it emitted a protected `.harness/runs` descendant. Its protocol-valid replacement passed AC-1 through AC-10 and AC-12 for the then-integrated candidate but correctly left AC-11 unknown because genuine wheel tooling was unavailable. T6 fresh verification bound all subsequent source productization to replacement candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4`; T7-A/B/C2 and fresh T7-V1 then supplied the missing exact wheel/package-removal evidence, passed AC-11 and AC-21, and kept that final source identity unchanged. No T5 acceptance criterion remains failed or unknown.

## Productization scope extension — 2026-09-01

The confirmed product is the balanced document-first operating-contract manager. Default onboarding is an integrated `setup`; `init` remains the structure-only fast path; `define` remains the lower-level resumable interface. Main Skill owns ordinary Markdown Plan creation/resume. Complete Confirmed procedure records may generate instruction-only project Skills through resumed setup. Public installation is pipx-primary with pip support from the same wheel. Host-native execution remains responsible for Agent dispatch and project commands.

Frozen dependency direction:

```text
procedures.py <- guided.py <- setup.py <- cli.py
```

`setup.py` owns `SetupEnvelope` and `coordinate_setup(...)`. Envelope keys are `schema`, `root`, `mode`, `state`, `audit`, `definition`, `preview`, `eligible_for_apply`, `changes`, `input`, and `next_action`. `procedures.py` owns `ProcedureSpec`, validation, canonical serialization, Skill paths, and instruction-only rendering. Existing public `define` output and private helpers consumed by migration remain compatible.

### Productization task state

| Task | Owner | State | Depends on | Parallel group | Outcome | Result |
|---|---|---|---|---|---|---|
| T6-A | setup-owner | complete | interface freeze | G6.1 | Integrated setup coordinator and quiet guided core | 42/42 focused pass |
| T6-B | procedure-owner | complete | interface freeze | G6.1 | Structured procedures and Skill renderer | 32/32 focused/regression pass |
| T6-C | cli-owner | complete | interface freeze | G6.1 | Public setup parser and JSON output | 67/67 lane suite pass |
| T6-D | authority-owner | complete | scope freeze | G6.1 | Current/public/history parity | 69/69 lane suite and links pass |
| T6-E | asset-owner | complete | scope freeze | G6.1 | Installed templates and Main handoff | 31/31 focused pass |
| T6-I | main | complete | T6-A, T6-B, T6-C, T6-D, T6-E | integration | Integrate and freeze source candidate | product `f8f59363d8c0a2587cb3868187414a173dbc96437e484ff05ddaf576a8b4c140`; 95/95 pass |
| T6-V1 | verification-behavior | complete | T6-I | G6.V | Verify AC-13 through AC-17 and AC-20 | AC-13/15/17/20 pass; AC-14/16 fail with two confirmed defects |
| T6-V2 | verification-authority | complete | T6-I | G6.V | Verify AC-17 through AC-20 | AC-17 through AC-20 pass within source/document scope |
| T6-R1 | tty-output-repair | complete | T6-V1 | G6.R | Keep interactive prompt prose off stdout | 96/96 full pass; exact 2-file delta |
| T6-R2 | procedure-authority-repair | complete | T6-V1 | G6.R | Align current/package authority to frozen nine fields | 95/95 full pass; exact 3-file delta |
| T6-RI | main | complete | T6-R1, T6-R2 | integration | Integrate repairs and freeze replacement candidate | product `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4`; 96/96 pass |
| T6-V3 | verification-tty | complete | T6-RI | G6.RV | Reverify AC-14 and affected regressions | AC-14 and affected AC-13/15/20 pass; identity stable |
| T6-V4 | verification-procedure | complete | T6-RI | G6.RV | Reverify AC-16/18 and affected regressions | AC-16/18 and affected AC-20 pass; identity stable |
| T7-A | distribution-builder | complete | T6-V3, T6-V4 | build | Build and freeze one wheel | wheel `512e304c...10ae4`; 43-member inventory and metadata pass |
| T7-B | verification-pipx | complete | T7-A | G7.install | Verify pipx lifecycle | pipx portion accepted; evidence `e6e422...8e93` |
| T7-C | verification-pip | invalidated | T7-A | G7.install | Verify pip lifecycle and package removal | verifier-protocol failure; evidence discarded, no product judgment |
| T7-C2 | verification-pip | complete | T7-A | G7.install replacement | Replace invalid T7-C with fresh pip verification | pip portion accepted; evidence `2c74c0...5192` |
| T7-I | main | complete | T7-B, T7-C2 | integration | Integrate artifact evidence | exact identities accepted; invalid T7-C excluded |
| T7-V1 | verification-artifact | complete | T7-I | verification | Judge AC-21 and full candidate | AC-21 pass; AC-1 through AC-21 bound; no blocker |

### T6-A — Integrated setup coordinator

- **Role:** leaf
- **Parent:** T6
- **Parallel group:** G6.1
- **May delegate:** no
- **Owner:** setup-owner
- **Outcome:** add `src/reporivet/setup.py`, expose bounded non-printing guided helpers, report actual evidence values and Open items, and preserve exact preview/apply safety.
- **Read:** frozen interface above; `src/reporivet/cli.py`, `guided.py`, `initializer.py`; focused guided/audit tests.
- **Allowed writes:** `src/reporivet/setup.py`, bounded setup/non-printing hooks in `src/reporivet/guided.py`, `tests/test_setup_flow.py`.
- **Protected paths:** sibling writes, migration and fixtures, current/public/package docs, settings, history, project-owned files, `.harness/runs` descendants.
- **Acceptance:** AC-13, AC-14, AC-15.
- **Verification:** TTY/non-TTY/answers/dry-run, actual Open values, one audit, exact preview/apply/stale handling, unchanged lower-level define behavior.
- **Stop conditions:** migration helper breakage, second traversal/writer, LLM semantics, or required interface change.
- **Return:** lane paths and hashes relative to the seeded baseline, focused results, integration hook, residual risks.
- **Result:** Complete. Added the frozen setup envelope/coordinator and quiet guided hooks; 42/42 focused and related regressions passed. Procedure targets were intentionally left for T6-I.

### T6-B — Confirmed procedure Skills

- **Role:** leaf
- **Parent:** T6
- **Parallel group:** G6.1
- **May delegate:** no
- **Owner:** procedure-owner
- **Outcome:** implement `ProcedureSpec`, strict complete-record validation, canonical draft record serialization, deterministic Skill path/content rendering, and focused tests without modifying guided integration concurrently.
- **Read:** procedure topic/schema, role Skills, Skill doctor rules, runbook/operations guidance, safe target semantics.
- **Allowed writes:** `src/reporivet/procedures.py`, `tests/test_procedure_skills.py`.
- **Protected paths:** `guided.py`, CLI/setup, settings, role Skill templates, migration, arbitrary project Skills, sibling writes, `.harness/runs` descendants.
- **Acceptance:** AC-16 and applicable AC-20 boundary clauses.
- **Verification:** invalid/duplicate/reserved slugs; incomplete/generic/Proposed/Open exclusion; deterministic rendering; instruction-only content; no execution.
- **Stop conditions:** hidden state, privilege-bearing frontmatter, automatic deletion, settings mutation, or need to claim arbitrary project Skills.
- **Return:** lane paths/hashes, frozen integration functions, focused results, residual risks.
- **Result:** Complete. Added strict immutable procedure records, canonical compact JSON, deterministic instruction-only Skill targets, and diagnostics; 10/10 direct plus 22/22 related regressions passed.

### T6-C — Setup CLI

- **Role:** leaf
- **Parent:** T6
- **Parallel group:** G6.1
- **May delegate:** no
- **Owner:** cli-owner
- **Outcome:** add the frozen `setup` parser/mode matrix and print exactly one `SetupEnvelope.render()` result.
- **Read:** frozen coordinator signature and current parser/compatibility tests.
- **Allowed writes:** `src/reporivet/cli.py`, `tests/test_setup_cli.py`.
- **Protected paths:** setup/guided implementation, docs/assets, migration, sibling writes, `.harness/runs` descendants.
- **Acceptance:** AC-13, AC-14.
- **Verification:** valid/invalid flag combinations, exact one-document stdout, preserved define/init/upgrade/migrate/doctor grammar.
- **Stop conditions:** implicit bare-command setup, compatibility break, duplicate setup logic, or interface change.
- **Return:** lane paths/hashes and focused parser results.
- **Result:** Complete. Added the exact setup grammar, local coordinator import, mode validation, and one-document output; 4/4 focused, 34/34 compatibility, and 67/67 lane suite passed.

### T6-D — Current authority and historical classification

- **Role:** leaf
- **Parent:** T6
- **Parallel group:** G6.1
- **May delegate:** no
- **Owner:** authority-owner
- **Outcome:** align Korean/English current authority with setup/init/procedure/pipx/pip behavior, repair SPEC/DESIGN implementation-status wording, and classify retired generated/module-contract material as historical without deleting history.
- **Read:** implemented behavior and current/public/spec/design/history surfaces.
- **Allowed writes:** `README.md`, `README.en.md`, `AGENTS.md`, `ARCHITECTURE.md`, applicable current `docs/*.md`, SPEC/DESIGN 003, definition/Skill references, `docs/generated/**`, `docs/module-contracts/**`, `tests/test_documentation_contract.py`.
- **Protected paths:** package code/assets, completed Plans and their evidence bodies, sibling writes, project CI, `.harness/runs` descendants.
- **Acceptance:** AC-18, AC-19, AC-20 documentation boundary.
- **Verification:** bilingual commands, current/template handoff contract supplied to T6-E, links, no live retired routing, no unsupported publication claim.
- **Stop conditions:** rewriting historical evidence, inventing project facts, or requiring runtime behavior changes.
- **Return:** lane paths/hashes, documentation test results, residual historical classifications.
- **Result:** Complete. Current/public/spec/design authority now distinguishes implemented source behavior from pending artifact readiness; retired generated/module-contract material is retained as historical. Six focused and 69 full lane tests plus 161 scoped links passed.

### T6-E — Installed assets and Main Plan handoff

- **Role:** leaf
- **Parent:** T6
- **Parallel group:** G6.1
- **May delegate:** no
- **Owner:** asset-owner
- **Outcome:** update document-first templates and Main Skill for setup/init/procedure ownership and exact first-Plan ID/no-duplicate handoff.
- **Read:** frozen product wording, current templates, Plan policy/template, role Skills, asset/package tests.
- **Allowed writes:** applicable paths under `src/reporivet/assets/project/document-first/**`; focused changes in `tests/test_plan_lifecycle.py`, `tests/test_claude_assets.py`, and `tests/test_distribution.py`.
- **Protected paths:** package Python code, current/public docs, migration, arbitrary project Skills/settings, sibling writes, `.harness/runs` descendants.
- **Acceptance:** AC-16, AC-17, AC-18, AC-19.
- **Verification:** generated-tree catalog, role Skill portability, Main first-ID/no-duplicate text, procedure path family, package-data boundary.
- **Stop conditions:** adding Plan CLI/runtime, privileged Skill frontmatter, settings merge, or package data outside the frozen boundary.
- **Return:** lane paths/hashes and focused asset results.
- **Result:** Complete after one watchdog resume of the same Agent/context. Installed templates and role Skills now cover setup, procedures, pipx/pip, and exact Main first-Plan handoff; 31/31 focused tests passed. The reported pre-seeded `tests/test_distribution.py` change was correctly excluded from the actual lane delta.

### T6-I — Source integration

- **Role:** integration
- **Parent:** T6
- **Parallel group:** integration
- **May delegate:** no
- **Owner:** main
- **Depends on:** T6-A through T6-E
- **Outcome:** reject out-of-scope lane paths, integrate exact bytes/modes serially, wire procedure parsing/targets/doctor into the guided core, resolve only frozen-interface conflicts, run shared checks, and freeze a source fingerprint.
- **Allowed writes:** lane-owned paths, required shared regression assertions, and this active Plan only.
- **Acceptance:** AC-13 through AC-20.
- **Stop conditions:** lane baseline mismatch, protected-path reference, unapproved public API change, failing migration/settings/history regression, or scope expansion.
- **Result:** Complete. Every seed-relative delta stayed in its allowed write set; Main integrated 39 lane files, added only the shared procedure preview/doctor wiring and regressions, and preserved migration/settings interfaces. Focused integration checks passed 59/59, full tests 95/95, compile and patch hygiene passed, and doctor reported no errors. Frozen product candidate: `f8f59363d8c0a2587cb3868187414a173dbc96437e484ff05ddaf576a8b4c140`.

### T6-V1 / T6-V2 — Parallel fresh verification

- **Role:** verification leaves
- **Parent:** T6
- **Parallel group:** G6.V
- **May delegate:** no
- **Depends on:** T6-I
- **Allowed writes:** verifier return only; temporary external fixtures may be used.
- **Protected paths:** candidate and `.harness/runs` descendants.
- **Acceptance:** T6-V1 judges behavioral/safety AC-13 through AC-17 and AC-20; T6-V2 judges authority/history/distribution-contract AC-17 through AC-20.
- **Result:** Complete. Both leaves preserved exact product identity `f8f59363d8c0a2587cb3868187414a173dbc96437e484ff05ddaf576a8b4c140`. T6-V2 accepted AC-17 through AC-20. T6-V1 accepted AC-13, AC-15, AC-17, and AC-20, but independently reproduced two defects: real TTY prompting contaminates stdout before the otherwise valid setup envelope, and current procedure protocol text requires concepts rejected by the frozen exact nine-field implementation. Full tests still passed 95/95; these are missing real-path/authority-parity regressions, not broad runtime failures.

### T6-R1 / T6-R2 — Parallel verification repairs

- **Role:** implementation leaves
- **Parent:** T6
- **Parallel group:** G6.R
- **May delegate:** no
- **Depends on:** T6-V1
- **T6-R1 owner/outcome:** `tty-output-repair`; preserve the frozen coordinator signature and setup grammar while routing the interactive question/prompt to stderr so stdout contains only one parseable `reporivet.setup/v1` document.
- **T6-R1 allowed writes:** `src/reporivet/cli.py`, `tests/test_setup_cli.py`.
- **T6-R2 owner/outcome:** `procedure-authority-repair`; preserve the frozen `ProcedureSpec` schema and align current/package procedure protocol wording and contract tests to exact required fields `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, and `rollback`.
- **T6-R2 allowed writes:** `docs/references/project-definition-protocol.md`, `src/reporivet/assets/project/document-first/docs/references/project-definition-protocol.md.tmpl`, `tests/test_documentation_contract.py`.
- **Protected paths:** sibling writes, all other public APIs and authority, migration/history/settings, arbitrary project Skills, project-owned files, `.harness/runs` descendants, external systems.
- **Acceptance:** R1 proves real interactive input leaves stdout directly JSON-parseable and keeps the prompt visible on stderr. R2 proves current/package parity and rejects any schema expansion, owner inference, hidden permission semantics, or implementation change. Both preserve all unaffected T6 behavior.
- **Stop conditions:** coordinator/public schema change, new procedure fields, prompt suppression rather than stderr routing, broad documentation rewrite, dependency addition, or any out-of-scope path.
- **Return:** exact seed-relative paths/hashes, focused results, and residual risks.
- **Result:** Complete. T6-R1 changed only CLI plus its focused test, routes coordinator stdout to stderr while rendering the envelope afterward, and passed 96/96 full tests. T6-R2 changed only current/package protocol plus its contract test, retained the exact implementation schema unchanged, and passed 95/95 full tests. Neither lane committed, delegated, installed dependencies, or touched protected paths.

### T6-RI / T6-V3 / T6-V4 — Repair integration and fresh re-verification

Main verifies the primary candidate still matches the frozen repair seed, integrates only the two disjoint repair deltas, runs shared checks, and freezes a replacement product fingerprint as T6-RI. Fresh read-only T6-V3 then judges AC-14 plus affected AC-13/15/20 behavior through a real TTY path, while T6-V4 judges AC-16/18 plus affected AC-20 authority/package parity. Both must preserve replacement identity; prior accepted criteria remain bound to the unchanged portions of the integrated candidate.

- **T6-RI result:** Complete. A resumable seed-only baseline proved R1 and R2 changed exactly their five allowed files; Main integrated exact returned bytes/modes. Replacement candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` has patch SHA-256 `be6f73dc9e0d54da2e3c098c092e7ca72d9c748f9e3392a533009405f90127de`, 91 tracked changes, and 50 untracked regular files. Focused tests pass 21/21, full tests 96/96, compile/doctor/diff pass, and post-check identity matches `/tmp/reporivet-t6-repaired-candidate-f2nsyu7a/manifest.json`.
- **T6-V3/V4 result:** Complete. Both fresh nodes kept the replacement identity unchanged. V3 accepted AC-14 and affected AC-13/15/20 after an OS-backed PTY proved JSON-only stdout and prompt-only stderr. V4 accepted AC-16/18 and affected AC-20 after independently rejecting all missing, empty, and formerly demanded extra fields while proving exact current/package parity. No T6 criterion remains unknown or failed.

### T7 — Genuine wheel lifecycle

The user authorized network installation of `setuptools>=68`, pipx, and required build/verification tooling only inside disposable temporary virtual environments. No repository/global installation, publication, signing, tag, push, release, or deployment is authorized. Every node protects real `.harness/runs` descendants from enumeration, read, copy, hash, archive, write, deletion, or emitted metadata.

#### T7-A — Build and freeze one wheel

- **Role:** implementation/evidence leaf
- **May delegate:** no
- **Owner:** distribution-builder
- **Depends on:** T6-V3 and T6-V4
- **Outcome:** build exactly one wheel from an exact disposable seed of candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4`, then freeze its path, SHA-256, size, metadata, and complete archive inventory.
- **Allowed writes:** disposable worktree, virtual environment, build cache, artifact directory, and evidence manifest under `/tmp` only.
- **Protected paths:** primary repository bytes/refs, global/user environments, credentials, active/completed Plans, project-owned CI, external services, publication state, and protected run evidence.
- **Acceptance:** source seed matches the replacement product manifest before build; only authorized tooling is installed into the disposable venv; exactly one `.whl` is produced; archive paths/types/modes and METADATA/WHEEL/entry points are inspected; Python `>=3.11`, zero runtime dependencies, console entry point, package version, and complete document-first package data are present; retired runtime/wrapper/workflow/Gate/evidence surfaces are absent; primary candidate identity remains unchanged.
- **Stop conditions:** source seed mismatch, more than one wheel, repository/global install, unexpected build dependency, retired surface, metadata mismatch, protected-path access, or publication attempt.
- **Return:** wheel path/hash/size, tooling versions and build command, complete inventory manifest, candidate identity before/after, and residual risks.
- **Result:** Complete. T7-A built exactly one wheel with Python 3.13.15, setuptools 84.0.0, and build 1.6.0 inside `/tmp`. Wheel `reporivet-0.2.0-py3-none-any.whl` is read-only, 91,541 bytes, SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4`. Canonical evidence `/tmp/reporivet-t7-a-artifacts-sXzFhW/t7-a-evidence.json` is read-only, SHA-256 `9b89486bd07504f032f122aa4a346c3b7516b2119d59d90e804f15a223f37663`. All 43 ZIP/RECORD members verify; metadata and complete package-data coverage pass; no retired package surface appears. The only residual is nonblocking setuptools license metadata deprecation guidance.

#### T7-B / T7-C — Parallel install and removal verification

- **Role:** verification leaves
- **May delegate:** no
- **Depends on:** T7-A
- **Parallel group:** G7.install
- **Shared input:** the exact immutable T7-A wheel path and SHA-256; each node rehashes it before and after.
- **T7-B owner/outcome:** `verification-pipx`; install only into disposable `PIPX_HOME`/`PIPX_BIN_DIR`, exercise help, setup preview/apply with one exact Confirmed procedure, structure-only init, doctor, uninstall, console/app-registration removal, and retained generated repository usefulness.
- **T7-C owner/outcome:** `verification-pip`; install with `--no-deps` into a disposable venv, exercise the same package behavior, prove import/distribution/console presence before uninstall and absence afterward, and preserve generated Markdown/Plans/role+procedure Skills/Git/project-command usability.
- **Allowed writes:** disjoint `/tmp` tool environments, target repositories, caches, and evidence manifests only.
- **Acceptance:** both channels use the same wheel hash; setup creates no Plan/runtime and generates only the valid procedure Skill; init remains structure-only; doctor succeeds; uninstall removes only package-side Python/console/app state; generated project-owned files remain exact and usable; no retired surface or external action appears.
- **Return:** channel manifest with commands, paths, hashes, criterion-level results, uninstall proof, and residual risks.
- **Result:** T7-B complete. Its read-only manifest `/tmp/reporivet-t7-b-jjq7f0nt/t7-b-evidence.json`, SHA-256 `e6e4223466d38385a534581f27d81f227ee13188c0473eebf4e8cac52a688e93`, accepts the pipx portion after exact wheel installation, setup preview/apply, one procedure Skill, structure-only init, doctor, uninstall/app removal, and byte/mode-identical target durability. The initial T7-C lifecycle narration is unusable because that verifier ran three source Git status operations without the mandatory exclusions; Main discards the entire node as a protocol failure and records no product defect from it. Fresh replacement T7-C2 complete. Its read-only manifest `/tmp/reporivet-t7-c2-bHXiGp/t7-c2-evidence.json`, SHA-256 `2c74c03a01ceb09020f4f630e37ad4b140bc9b5f4f7f7f2a5a67ed044d4a5192`, accepts the pip portion after local-only `--no-index --no-deps` installation, the same package behavior, exact import/distribution/console removal, and byte/mode-identical target durability. Both accepted channels preserve the exact wheel, source, T7-A evidence, generated documents/Plans/Skills/Git, and project commands.

#### T7-I / T7-V1 — Artifact evidence integration and final verification

Main checks both channel manifests against the frozen wheel and source identities without rerunning their detailed lifecycle, records criterion-level evidence, and freezes T7-I. Fresh read-only T7-V1 then independently inspects the candidate, wheel, complete inventory, both install/uninstall results, persistent target trees, and unsupported-claim boundary before judging AC-21 and final Plan completion.

- **T7-I result:** Complete. Main rehashed the sole wheel (`512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4`, 91,541 bytes, mode `0444`), T7-A evidence (`9b89486bd07504f032f122aa4a346c3b7516b2119d59d90e804f15a223f37663`), T7-B evidence (`e6e4223466d38385a534581f27d81f227ee13188c0473eebf4e8cac52a688e93`), and T7-C2 evidence (`2c74c03a01ceb09020f4f630e37ad4b140bc9b5f4f7f7f2a5a67ed044d4a5192`). The accepted channel manifests are regular read-only files, report `completed`, accept their assigned pipx/pip portions, preserve source fingerprint `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and patch SHA-256 `be6f73dc9e0d54da2e3c098c092e7ca72d9c748f9e3392a533009405f90127de`, and require only fresh T7-V1 for overall AC-21. Main did not rerun either detailed lifecycle and did not consume the invalid initial T7-C evidence.
- **T7-V1 result:** Complete and PASS. A fresh read-only Verification Sub preserved source HEAD `5df73f7038f5f36aebeed19f5ab50a920f0e5424`, fingerprint `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4`, and patch SHA-256 `be6f73dc9e0d54da2e3c098c092e7ca72d9c748f9e3392a533009405f90127de` before and after. It independently rehashed all four accepted inputs, verified the sole 43-member wheel and every RECORD hash/size, matched all 37 non-cache source package files byte-for-byte, confirmed exact metadata/entry point/zero dependencies and retired-surface absence, and validated both channel manifests, referenced uninstall state, retained target snapshots, Git/project-command usefulness, and current authority boundary. The invalid initial T7-C root was not accessed or incorporated. AC-21 passes; prior AC-1 through AC-20 remain bound to the unchanged candidate; no completion blocker was established.

### Uncommitted candidate worktree protocol

No commit is authorized. Main freezes Plan bytes, obtains explicit tracked/untracked changed paths with Git exclusions for `.harness/runs` and descendants, and creates a mode-restricted seed bundle under `/tmp`: full-index tracked patch, exact bytes/modes for explicitly listed untracked regular files, deletion tombstones, and a canonical manifest/fingerprint. Nonregular untracked entries are rejected.

Each isolated worktree starts from exact HEAD, receives that seed, and must match its fingerprint before a mutable leaf starts. Each lane returns only its allowed paths relative to the seed. Main verifies the primary path still matches the frozen baseline and copies exact resulting bytes/modes serially. No lane commit, cherry-pick, stash commit, whole-tree copy, or raw-HEAD reconstruction is used. If exact seeding cannot be proven, mutable work is serialized rather than weakening isolation.

## Architecture Impact

The dependency direction changes from a two-lifetime package-plus-copied-runtime design to:

```text
installed Reporivet CLI -> package-side audit/render/migrate/doctor -> repository documents and optional Claude adapters
Agent host -> AGENTS.md -> docs/README.md -> active Plan -> task-relevant authority/Skills -> project-owned commands
```

No generated repository code imports the package, because no Reporivet executor is generated. The package remains standard-library-only unless a concrete blocker is approved.

## Documentation Impact

| Surface | Action | Status |
|---|---|---|
| `README.md`, `README.en.md` | rewrite public boundary and generated tree | complete; later artifact-status wording follow-up recorded |
| `AGENTS.md`, `CLAUDE.md`, `docs/README.md` | replace runtime routing with authority/Plan/Skill routing | complete |
| `docs/PRODUCT.md`, `ARCHITECTURE.md`, `docs/DESIGN.md` | replace two-lifetime runtime architecture | complete; later artifact-status wording follow-up recorded |
| `docs/QUALITY.md`, `docs/SECURITY.md`, `docs/PLANS.md` | remove Gate/run closure and define project-owned evidence | complete |
| `docs/OPERATIONS.md`, `docs/RELIABILITY.md` | establish one operations authority and retire duplicate current authority | complete |
| specs/designs/ADR | add 003 records and supersede contradictory 001/002 contracts | complete |
| definition and Skill migration references | align guided setup and project-owned procedural Skills | complete |
| package templates/assets | match all current authority | complete |

## Interfaces and Dependencies

- Existing capabilities to reuse: `validate_root`, `ChangeSet`, `AuditFinding`, `AuditReport`, `read_asset`, `render`, `ensure_safe_write_path`, managed-block helpers, create-if-missing behavior, command detection, and snapshot/restore utilities in `src/reporivet/initializer.py`.
- New package module: one bounded `src/reporivet/migration.py` for explicit 0.2 preview/apply/rollback.
- New production dependency: none planned.
- Public contract impact: Reporivet maintenance remains package-side; generated `./dev/*`, Gate/evidence schemas, and generated CI are removed.
- Host contract: `AGENTS.md` is canonical; Claude files are optional adapters and not security boundaries.

## Migration, Rollout, and Recovery

Ordinary `upgrade` must detect 0.2 runtime surfaces and refuse destructive conversion. `migrate --preview` is target-read-only and emits a deterministic manifest/fingerprint. Apply requires that exact fingerprint and an explicit backup directory outside the generated target tree.

Deletion requires expected path, regular non-symlink type, known ownership marker where applicable, and exact canonical 0.2 bytes/hash. Ambiguous/custom/project-owned files and `.harness/runs` are preserved. Apply snapshots every affected path, rolls back automatically on failure, and writes a transparent manifest supporting post-success rollback unless later user changes make overwrite unsafe.

The current repository changes are staged so old behavior remains runnable until migration and replacement tests pass. The runtime and generated assets are removed atomically only in T3; no compatibility wrapper remains afterward.

## Surprises and Discoveries

- 2026-08-31 — The existing strict Plan checker requires the Gate-era expanded Plan schema and crashed on compact Task Packet bullets. This active Plan temporarily uses the current expanded headings so the repository remains runnable; T1 changes the future template/doctor contract to the approved compact format.
- 2026-08-31 — The system `python3` can be older than the package requirement; checks use an explicit Python 3.11+ interpreter when needed.
- 2026-08-31 — Current Claude Code guidance confirms project Skills at `.claude/skills/<name>/SKILL.md`, root-relative `@AGENTS.md` imports from root `CLAUDE.md`, and shared project settings at `.claude/settings.json`. Bash permission patterns are command-text filters rather than a semantic policy or OS sandbox, so a deny list is not safe to install as Reporivet's default protection.
- 2026-08-31 — T1's first fresh verification found that create-if-missing safety is insufficient unless the normal preview also reports an already-existing optional settings path, and that structural doctor must inspect minimum authority structure plus the complete transitional 0.2 wrapper/routing inventory rather than only file existence and a few headline legacy paths.
- 2026-08-31 — The local Python 3.13 interpreter can run all source/focused tests but lacks `setuptools.build_meta`; static package-data coverage passes while wheel/install/uninstall evidence remains explicitly unknown until an authorized environment already containing the required backend is available.
- 2026-08-31 — The first T1 repair passed its named regressions but was not generalized across the full settings path-state matrix or Plan grammar. The next approach uses explicit state tables and a compact-schema version marker rather than inferring ownership/history from proposed empty content or incidental Gate/run prose.
- 2026-08-31 — Retired-contract diagnosis must evaluate each match within its local clause: a negated first mention cannot suppress a later live mention, and a trailing negation such as “does not apply” must not be reported as live authority.
- 2026-08-31 — A no-follow flag on the final settings file is insufficient: an attacker or concurrent process can replace `.claude` after ancestry validation, so safe preview and mutation require stable directory-descriptor traversal and final opens relative to the verified parent.
- 2026-08-31 — Compact terminal Outcome validation must parse one exact normalized status value; finding a terminal word anywhere in prose incorrectly accepts negated or qualified values such as `not complete`.
- 2026-08-31 — Clause-local retired-reference matching also needs conservative comma and coordinating-conjunction segmentation; semicolon/sentence/adversative boundaries alone still let an earlier negation suppress a later live instruction.
- 2026-08-31 — Dogfood `dev/harness.toml` is not a generated-default retirement target: it declares project ownership, contains project-specific commands, and the migration classifier correctly preserves it. T3 may remove the 19 canonical runtime/wrapper files but must restore and retain this configuration.
- 2026-09-01 — The first T5 verifier invalidated its own node by listing `.harness/runs/.gitkeep`, then stopped before mandatory behavioral checks and final identity capture. This is a verification-protocol failure, not a confirmed candidate defect; replacement verification must exclude the protected tree from all enumerations and fingerprint inputs.
- 2026-09-01 — A large uncommitted candidate can still support safe parallel mutation without a commit: an exact HEAD-relative binary patch plus validated regular untracked files seeded five worktrees to fingerprint `899db1b6ee7632d415699789e6a8f19f2756d80a08b51f6ff04de4e98677644e`; all returned deltas were then compared to that seed rather than to HEAD.
- 2026-09-01 — Seed-relative comparison matters: T6-E correctly reported that `tests/test_distribution.py` differed from HEAD but had not changed in its lane, so Main excluded it instead of integrating a false delta.
- 2026-09-01 — T6-V1's real PTY probe found a test gap: `input(prompt)` writes the interactive question to stdout before the canonical setup envelope. The repair belongs at the CLI stream boundary so the frozen coordinator and guided interfaces remain unchanged.
- 2026-09-01 — T6-V1 also found authority drift rather than a missing feature: current/package procedure protocol prose had broadened “complete” beyond the explicitly frozen nine-field `ProcedureSpec`. Scope control requires repairing that prose and its contract test, not adding unapproved fields or semantics.
- 2026-09-01 — Serial integration of disjoint repair lanes must compare every lane to the immutable seed baseline, not to a primary tree already containing an earlier sibling. The first resumable integration attempt correctly stopped after R1 when this assumption failed; a seed-only baseline then proved the partial state and completed R2 without recopying or weakening validation.
- 2026-09-01 — T7-A emitted only nonblocking setuptools license metadata/classifier deprecation guidance, including a future 2027-02-18 deadline. This does not block the frozen wheel criterion and is not expanded into metadata cleanup under the current scope.
- 2026-09-01 — The initial T7-C verifier completed the intended lifecycle but invalidated its node by issuing three source Git inventory commands without mandatory pathspec exclusions. No protected descendant was emitted, but the entire node is discarded by protocol; fresh T7-C2 replaces it and accepts the pip portion without using that evidence.

## Decision Log

- 2026-08-31 — Adopt rich content and thin execution: authority documents, Skills, settings, and Plans remain; repository runtime orchestration is retired.
- 2026-08-31 — `AGENTS.md` is canonical; Claude Code receives the first optional host profile.
- 2026-08-31 — `docs/OPERATIONS.md` replaces split operations/reliability authority for fresh installations.
- 2026-08-31 — Existing 0.2 installations use an explicit one-shot migration with preview, external backup, ownership-aware apply, and rollback; ordinary upgrade does not delete runtime assets.
- 2026-08-31 — Main remains a long-lived coordinator; implementation and detailed verification are Sub-Agent work, with compact evidence returned to Main.
- 2026-08-31 — Plan execution is a dependency tree, not a serial checklist: each child such as `T1-A` has its own owner and packet, Main dispatches the complete ready leaf set concurrently, and only packets explicitly designated as Task Owners may fan out bounded descendants. Parallel mutable siblings require disjoint writes or isolated worktrees; integration and fresh verification are explicit downstream nodes.
- 2026-08-31 — Terminal `complete`, `cancelled`, and `superseded` Plans live under `completed/`; status records the actual outcome.
- 2026-08-31 — The default Claude Code adapter is a root `CLAUDE.md` containing only `@AGENTS.md` plus portable project Skills whose `name` matches the parent directory and whose `description` states purpose and trigger. Reporivet does not create live `.claude/settings.json` by default; any deny-only settings template is outside automatic discovery and can be installed only through an exact preview and explicit create-if-missing opt-in. Existing settings are never merged or rewritten, and permission rules are documented as defense in depth rather than a sandbox.
- 2026-09-01 — Productization uses integrated `setup` by default, retains structure-only `init` and lower-level `define`, delegates first-Plan creation to Main Skill, and supports pipx-primary plus pip from one wheel without adding a Plan or Skill CLI.
- 2026-09-01 — A complete Confirmed procedure is represented as one compact canonical JSON object in the visible draft. Only valid unique records generate instruction-only targets; diagnostics remain visible but nonblocking, and stale or differing project Skills remain untouched.
- 2026-09-01 — T6 product identity excludes the protected `.harness/runs` tree and the Main-owned active Plan only. This preserves a stable product fingerprint while Main appends evidence; verifiers still read and judge the Plan separately.
- 2026-09-01 — The approved procedure interface remains the exact nine-field `ProcedureSpec`; the T6-V1 authority mismatch is repaired by narrowing protocol prose to that decision rather than expanding product scope.

## Concrete Steps

1. Complete T0 decision records and current structural checks.
2. Implement and independently review T1 using focused tests before migration work.
3. Implement T2 migration and prove rollback before authorizing deletion.
4. Complete T3 boundary flip and remove all runtime compatibility surfaces.
5. Complete T4 documentation parity against integrated behavior.
6. Dispatch T5 to a fresh Verification Sub and record criterion-level evidence.
7. Complete T6 parallel productization leaves, Main integration, and parallel fresh verification.
8. Build one exact wheel and verify pipx/pip installation, operation, uninstall, and retained repository usefulness through T7.
9. Move this Plan to `completed/` only after Main accepts complete evidence.

## Validation and Evidence

| Criterion | Evidence | Verifier | Candidate | Result |
|---|---|---|---|---|
| AC-1, AC-2, AC-3, AC-4, AC-5, AC-7, AC-8 | 31/31 focused tests; 63/63 relevant existing tests; exact ancestry-race, Outcome, and retired-authority probes; compile, patch hygiene, and static package-data coverage | fourth fresh Verification Sub | `0dc3e74e677e8ea772e411ed72d41cc1979cc8608dee6ac5fe0d4a7faaccad36` | pass |
| AC-9, AC-10 | 12/12 migration tests; 4/4 upgrade tests; 50/50 retained T1 tests; named independent preview, ownership, backup, rollback, blocker, history, and retained-evidence reproductions | fresh T2 Verification Sub | `dd146b662167131c3f8e05f67c904059b8d47c6b174e6bf139af020eb9b234ae` | pass |
| AC-6, AC-11 | 58/58 retained tests; focused init/upgrade/doctor/CLI probes; static 29-asset production inventory with zero retired matches; 19 canonical dogfood removals; project-owned `dev/harness.toml` preservation | fresh T3 Verification Subs | `e34084b93fa515a2cc6aa4b932fabfbadd9123433a111a647e6607e968e8cb5b` | pass |
| AC-1, AC-2, AC-5, AC-8, AC-12 | 27/27 focused and 63/63 full tests; generic `T<n>` policy on 13/13 surfaces; doctor 0 errors; 167/167 links; CLI/bilingual/template/generated-surface/retired-reference parity | fresh T4 Verification Sub | `90e8ef2e7a91e0aaae188516adf9ab673635afcc6d28d8f5a6cf5533fd919f7d` | pass |
| AC-1 through AC-10, AC-12 | Protocol-valid protected-path handling; stable initial/final identity; 63/63 full tests; compile/diff; fresh init/upgrade/doctor; guided definition; Plan/Claude/migration probes; 183/183 links; parity and static 29-asset boundary | replacement fresh T5 Verification Sub | `f793567262ca66f11016aa198ddc46ec207eb23fbe91b234bf72a91348344293` | pass |
| AC-11 distribution evidence | Fresh/static/package-removal tests pass, but genuine wheel build/inspection and isolated install/uninstall could not run because Python 3.12/3.13 lack `setuptools.build_meta` and installation/network were not authorized | replacement fresh T5 Verification Sub | `f793567262ca66f11016aa198ddc46ec207eb23fbe91b234bf72a91348344293` | historical unknown; resolved by T7-A/B/C2/V1 |
| AC-13 through AC-20 implementation integration | Five exact seeded leaves; 39 validated lane files; shared procedure target/doctor wiring; 59/59 focused integration and 95/95 full tests; compile, doctor, and patch hygiene | Main integration | `f8f59363d8c0a2587cb3868187414a173dbc96437e484ff05ddaf576a8b4c140` | implementation complete |
| AC-13, AC-15, AC-17, AC-20 | Real non-TTY/TTY/dry-run/apply/safety probes; 89/89 focused, 95/95 full, compile/distribution/diff/doctor; stable candidate identity | fresh T6-V1 | `f8f59363d8c0a2587cb3868187414a173dbc96437e484ff05ddaf576a8b4c140` | pass |
| AC-17 through AC-20 | 37/37 focused authority/asset/Plan/distribution tests; 95/95 full; 175 current links and 16 package-template links; dependency/boundary inventory; stable identity | fresh T6-V2 | `f8f59363d8c0a2587cb3868187414a173dbc96437e484ff05ddaf576a8b4c140` | pass within source/document scope |
| AC-14 | Envelope structure passed, but a real PTY invocation emitted the question and prompt before JSON so direct stdout parsing failed | fresh T6-V1 | `f8f59363d8c0a2587cb3868187414a173dbc96437e484ff05ddaf576a8b4c140` | historical fail; repaired by T6-R1 and passed by T6-V3 |
| AC-16 | Procedure behavior passed, but current protocol required owner/authority/input/protected-path concepts rejected by the frozen nine-field schema | fresh T6-V1 | `f8f59363d8c0a2587cb3868187414a173dbc96437e484ff05ddaf576a8b4c140` | historical fail; repaired by T6-R2 and passed by T6-V4 |
| AC-14/16 repair integration | Exact two-lane seed-relative five-file delta; real input regression; current/package exact-nine-field regression; 21/21 focused and 96/96 full; compile/doctor/diff; stable post-check identity | Main integration | `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` | implementation complete |
| AC-14 and affected AC-13/15/20 | 10 subprocess probes including OS-backed PTY; JSON-only stdout, prompt-only stderr, exact one-answer/Open state; 24/24 focused and 96/96 full; compile/doctor/diff; stable identity | fresh T6-V3 | `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` | pass |
| AC-16/18 and affected AC-20 | Exact nine-field current/package/implementation parity; 9/9 missing, 9/9 empty, and 10/10 extra-field rejection; deterministic target and preservation probes; 29/29 focused; 168/168 links; stable identity | fresh T6-V4 | `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` | pass |
| AC-21 artifact build/inventory | Exact seeded source; one read-only wheel `512e304c...10ae4`; 43/43 RECORD members; metadata/entry point/Python/dependency/package-data/retired-surface checks; source and primary identity stable | T7-A distribution builder | `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` | pass for build/inventory portion |
| AC-21 pipx lifecycle | Exact wheel install; help/setup/apply/procedure/init/doctor; pipx uninstall and app/console removal; 78-entry target remains byte/mode exact and project command usable | fresh T7-B | wheel `512e304c...10ae4`; evidence `e6e422...8e93` | pipx portion pass |
| AC-21 initial pip lifecycle | Verifier used unexcluded source Git inventory commands; entire node discarded despite otherwise successful narration | initial T7-C | invalid evidence, not incorporated | invalid verifier protocol; no product judgment |
| AC-21 pip lifecycle | Local-only `--no-index --no-deps` install; import/distribution/console presence then exact removal; setup/init/doctor; 78-entry target remains byte/mode exact and usable | fresh replacement T7-C2 | wheel `512e304c...10ae4`; evidence `2c74c0...5192` | pip portion pass |
| AC-21 artifact integration | Rehash accepted T7-A/B/C2 manifests and sole wheel; exact source fingerprint/patch unchanged; invalid T7-C excluded; detailed channel lifecycles not rerun | Main T7-I | `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` | integrated |
| AC-21 final artifact lifecycle and AC-1 through AC-21 binding | Stable source before/after; all accepted hashes/modes/schemas; independent 43-member ZIP/RECORD and 37-file source parity; both uninstall states and retained snapshots; Git/project commands; current authority/non-goal boundary; invalid T7-C untouched | fresh T7-V1 | source `c1f8c72d...`; wheel `512e304c...10ae4` | pass; no blocker |

- Frozen source candidate: `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4`; protected `.harness/runs` descendants and Main-only Plan evidence updates are excluded from product identity
- AC-1 through AC-20 pass through combined fresh source and authority verification; full source checks pass 96/96 with compile, doctor, and patch hygiene
- AC-21 passes through one exact wheel plus accepted T7-A/B/C2 and fresh T7-V1 evidence; all AC-1 through AC-21 are bound to the unchanged candidate and no criterion remains failed or unknown
- Residual risks: artifact/evidence files are ephemeral `/tmp` records rather than a product evidence archive; lifecycle proof is environment-specific to the recorded macOS/Python 3.13 tooling; the wheel is unsigned because signing/publication are out of scope; historical module-contract prose depends on its superseded header; setuptools license metadata/classifier deprecations become time-relevant by 2027-02-18; conservative pre-verification readiness wording remains a documentation follow-up

## Outcomes and Retrospective

Complete. Reporivet now productizes an understandable document-first repository operating contract: canonical authority, integrated guided setup, structure-only init, resumable definition, Main-owned durable Plans, instruction-only role and Confirmed-procedure Skills, explicit reversible 0.2 migration, and project-owned execution boundaries. Copied runners, generated CI, Gate/evidence/closure machinery, automatic dispatch, and hidden runtime state are absent. Source verification passes AC-1 through AC-20, and one exact wheel passes complete inventory plus isolated pipx and pip install/use/uninstall evidence under AC-21. Because no commit was requested, terminal verification is bound to reproducible dirty-tree fingerprint `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` rather than an invented integrated or verified commit. No publication, release, signing, tag, push, or deployment occurred.

## Follow-ups

- Future documentation owner: when artifact-readiness or release documentation is next intentionally edited, replace conservative pre-verification “artifact readiness pending” status wording with this Plan's verified wheel result; do not reopen the completed candidate solely for that wording.
- Future release maintainer: before 2027-02-18, review the nonblocking setuptools license metadata/classifier deprecation guidance as a separately scoped packaging-metadata change.

## Outcome

complete
