---
id: PLAN-2026-0002
kind: exec-plan
status: verifying
owner: main
area: harness
created: 2026-08-29
updated: 2026-08-30
base_commit: "9d6d6600c54d29f7bb67dcb65eb5bffed56e337c"
integrated_commit: "HEAD"
verified_commit: ""
traceability: 1
product_spec: SPEC-REPORIVET-002
verification_run: ""
manifest_sha256: ""
gate_verdict: ""
gate_review_reason: ""
---

# Unified project definition, evidence-bound verification, and skill retirement

## Purpose / Big Picture

Reporivet will become the one canonical project for both pre-project definition/adoption and post-project repository operation. A person or Main Agent will be able to start or resume a structured product definition, audit an existing repository without changing it, safely adopt missing harness responsibilities, trace P0 requirements through plans and tasks to commit-bound evidence, and run one deterministic `./dev/verify` that preserves a structured Verification Run and risk-based Gate result.

The installed package remains responsible for initialization and managed upgrades. The copied repository-local Python-standard-library runtime remains independently usable after the package is removed. Valid HarnessEngineeringSkill capabilities are adapted into this architecture; Skill bundles, runtime-specific targets, host bridges, model judges, daemons, external task state, and duplicate gates are not retained.

Observable completion requires all acceptance criteria below, current-state documentation, wheel/package-removal scenarios, a clean integrated candidate, independent verification, and evidence-bound plan closure. The later instruction excluding old-repository backup and deletion supersedes the retirement execution originally requested: this plan includes migration documentation and logical retirement readiness only, with no backup, archive, deprecation write, deletion, or other external repository operation.

## Progress

- [x] Establish current Reporivet behavior, ownership, verification, packaging, and test constraints.
- [x] Inspect HarnessEngineeringSkill at pinned commit and classify migration inputs.
- [x] Deliver definition, audit/adoption, traceability, conditional knowledge, and context routing.
- [x] Deliver one Verification Run, Gate policy, evidence-bound close-plan, and CI evidence.
- [x] Resolve runtime parity, documentation, deterministic regression, and release packaging.
- [x] Integrate and independently verify the clean candidate.
- [x] Prepare evidence-bound closure and resolve all follow-ups without external old-repository actions.

## Context and Orientation

Reporivet currently exposes `init`, `upgrade`, and `doctor` from `src/reporivet/cli.py`. `src/reporivet/initializer.py` owns project detection, managed-file markers, bounded `AGENTS.md` updates, project-owned configuration preservation, and asset rendering. The canonical copied runtime is `src/reporivet/assets/project/dev/harness.py`; `dev/harness.py` is the dogfood rendering. The runtime already implements document catalogs, docs/plan/security/architecture checks, context routing, plan creation/task extraction, close-plan, and gardening, but command groups currently create separate run directories and do not produce a unified manifest or Gate.

`dev/harness.toml` is project-owned. New optional Gate policy must therefore be generated only for new projects; old configs receive in-memory defaults and an advisory. The environment’s default `/usr/bin/python3` is 3.9.6, while Reporivet requires Python 3.11+, so local implementation and verification use `/Users/hakseong/.local/bin/python3.12` through `PYTHON` or an explicit interpreter.

HarnessEngineeringSkill was inspected read-only at commit `dd5989d4f9de5646349b3bceec4e19806262d14d`. Its durable inputs are the fourteen-section definition protocol, resumable evidence states, existing-project scan/adoption concepts, traceability, conditional module knowledge, and deterministic validation. Its five runtime bundles, target synchronization, host prompt/bridge files, and incomplete model evaluation are non-target architecture.

## Scope

- Add explicit package and repository-local definition, audit, and code-map interfaces.
- Preserve Confirmed, Proposed, and Open evidence without semantic promotion.
- Add authority-preserving adoption and deterministic read-only inventory.
- Add stable Journey/P0/Acceptance IDs and opt-in plan/task/evidence validation.
- Add conditional module contracts and a derived code map with context routing.
- Refactor `./dev/verify` into one evidence-producing run with fixed check order.
- Add local Git target evidence, path risk classification, protected-path policy, Gate verdicts, shadow/enforce behavior, and human-readable report.
- Bind `close-plan` to one run, manifest hash, verdict, target SHA, and REVIEW reason.
- Update generated/dogfood CI, managed ownership, current-state docs, tests, wheel contents, and package-removal evidence.
- Prepare a local, release-ready `0.2.0` candidate without publishing it.
- Provide a Reporivet-side migration guide and logical retirement mapping.

## Non-goals

- Backing up, bundling, archiving, changing, deprecating through an external write, or deleting HarnessEngineeringSkill.
- Publishing to PyPI, creating a GitHub release, PR, comment, merge, deployment, or any external write other than the explicitly authorized push of the current working branch.
- Adding an agent execution platform, orchestrator, task database, journal service, daemon, plugin framework, MCP server, LLM API, model SDK, judge, trajectory evaluator, confidence score, or policy DSL.
- Adding production dependencies, network-required checks, runtime targets, Skill bundles, or a required `CLAUDE.md` bridge.
- Rewriting completed ExecPlans or replacing existing project authority documents and CI with generic templates.
- Making generated code maps authoritative, creating contracts for every directory, or adding universal file-size/import rules.
- Mutating existing project-owned `dev/harness.toml` during upgrade.

## Product Trace

| Product spec | Journey | P0 requirement | Acceptance criteria | Implementation tasks | Verification tasks |
|---|---|---|---|---|---|
| `SPEC-REPORIVET-002` | `JRN-001` | `REQ-P0-001` | `AC-1`, `AC-2` | `T2` | `T9` |
| `SPEC-REPORIVET-002` | `JRN-002` | `REQ-P0-002` | `AC-3` | `T3` | `T9` |
| `SPEC-REPORIVET-002` | `JRN-003` | `REQ-P0-003` | `AC-4` | `T4` | `T9` |
| `SPEC-REPORIVET-002` | `JRN-004` | `REQ-P0-004` | `AC-5` | `T5` | `T9` |
| `SPEC-REPORIVET-002` | `JRN-005` | `REQ-P0-005` | `AC-6`, `AC-14` | `T2`, `T8` | `T9` |
| `SPEC-REPORIVET-002` | `JRN-006` | `REQ-P0-006` | `AC-7`, `AC-8`, `AC-9` | `T6` | `T9` |
| `SPEC-REPORIVET-002` | `JRN-007` | `REQ-P0-007` | `AC-10`, `AC-11` | `T7` | `T9` |
| `SPEC-REPORIVET-002` | `JRN-008` | `REQ-P0-008` | `AC-12` | `T7` | `T9` |
| `SPEC-REPORIVET-002` | `JRN-009` | `REQ-P0-009` | `AC-13` | `T8` | `T9` |
| `SPEC-REPORIVET-002` | `JRN-010` | `REQ-P0-010` | `AC-15` | `T1`, `T8` | `T9` |

## Acceptance Criteria

- **AC-1 — Skill-free resumable definition:** A blank repository can start a structured definition, persist partial progress, and resume without repeating confirmed sections using only Reporivet-created repository files.
- **AC-2 — Evidence separation:** Definition artifacts distinguish Confirmed, Proposed, and Open. Strict validation rejects unresolved placeholders, blocking critical items, malformed/duplicate links, contradictions, and proposals represented as current fact.
- **AC-3 — Safe audit and adoption:** Audit is byte-for-byte read-only and deterministic. Adoption inventories instructions, README/docs, manifests, lockfiles, CI, scripts/config, source/tests, commands, inferences, unknowns, conflicts, and skips while preserving existing authority and keeping unverified commands in review.
- **AC-4 — Product traceability:** Every P0 requirement links to a journey and observable AC; the first plan and its implementation/verification tasks reference those IDs; completed traceable plans record criterion-level evidence and a verified commit.
- **AC-5 — Conditional knowledge surfaces:** Module contracts exist only for justified durable boundaries; validated contracts and actual/configured/confirmed-planned paths drive a deterministic non-authoritative code map and `context --path/--area` routing.
- **AC-6 — Repository-native independence:** After uninstalling Reporivet, generated definition, audit, context, planning, checks, verification, close-plan fixtures, and garden commands work through repository-local files without Skill/runtime bundles.
- **AC-7 — Single Verification Run:** One `./dev/verify` creates exactly one top-level run ID/directory shared by every canonical check and external command log.
- **AC-8 — Structured evidence:** Success, candidate failure, and infrastructure error preserve deterministic `manifest.json`, `gate.json`, `report.md`, check summaries, and available logs after run creation.
- **AC-9 — Status semantics:** Checks use only pass/fail/error/skipped/unknown, and required fail/error priority determines deterministic verification status without silently passing missing configured tools.
- **AC-10 — Risk and Gate:** Explicit local base/head evidence and changed paths produce contained/wide/irreversible/unknown risk plus independent protected-path matches and PASS/REVIEW/BLOCK/INCONCLUSIVE using the declared priority.
- **AC-11 — Shadow and enforce:** Shadow returns zero for deterministic PASS/REVIEW and nonzero for deterministic fail/error; enforce returns zero only for Gate PASS.
- **AC-12 — Evidence-bound close-plan:** Closure verifies the clean current HEAD exactly once; PASS closes, REVIEW needs a non-empty explicit human reason, and BLOCK/INCONCLUSIVE cannot be overridden. Run, manifest hash, verdict, SHA, and reason are durable.
- **AC-13 — CI evidence preservation:** PR/push CI passes explicit base/head evidence, verifies the explicit head, preserves full local history needed for diffing, uploads `.harness/runs/` on success/failure, and uses immutable actions with read-only contents permission.
- **AC-14 — Regression and packaging:** Greenfield/resume/ambiguity/audit/adoption/traceability/Gate/upgrade/wheel/install/generated-project/package-removal/dogfood scenarios pass deterministically without network, credentials, or model evaluation.
- **AC-15 — Safe retirement preparation:** Reporivet records the pinned migration source, complete capability disposition, replacement interfaces, discarded surfaces, migration guidance, and remaining limits. No old-repository backup, archive, deprecation write, or deletion is performed.

## Milestones

### M1 — Freeze migration source and ownership boundary

Record the pinned source SHA, migration matrix, no-delete scope, existing ownership model, and target interfaces before behavior changes.

### M2 — Definition, audit, and adoption core

Deliver explicit definition start/status/validate/finalize, deterministic audit, safe adoption, final spec generation, and first vertical-slice plan generation while keeping the copied runtime standalone.

### M3 — Traceability and conditional knowledge

Deliver stable IDs, product/plan/task/evidence links, legacy compatibility, conditional module contracts, code-map generation, and routed context.

### M4 — Evidence-bound verification and Gate

Deliver one Verification Run, status semantics, manifest, local Git evidence, path-risk/protected policy, Gate verdicts, shadow/enforce, report, and failure artifact preservation.

### M5 — Closure, CI, parity, and deterministic coverage

Bind close-plan to evidence, propagate CI targets, preserve artifacts, restore wrapper/runtime parity, and cover all required scenarios.

### M6 — Release-ready integration and migration guidance

Update current-state documentation, prepare version `0.2.0`, build and inspect the wheel, prove isolated/package-removed operation, independently verify a clean candidate, and close this plan with genuine review evidence if required.

## Task Packets

### T1 — Freeze and map the migration source

#### State

complete

#### Task type

support

#### Depends on

none

#### Outcome

Record the exact upstream source and classify every retained or discarded capability against Reporivet ownership and verification.

#### Non-goals

Implementation, cloning, backup, archive, deletion, external writes, or model evaluation.

#### Read

Current Reporivet operating/docs/runtime/initializer/test sources and HarnessEngineeringSkill README, architecture, Skill references/scripts, starter kit, targets, synchronization/tests, and CI at the pinned SHA.

#### Allowed writes

This ExecPlan and `docs/references/harness-engineering-skill-migration.md`.

#### Protected paths

All code, completed plans, and external repositories.

#### Acceptance

AC-15

#### Verify

Source SHA and every matrix row include source, disposition, Reporivet target, verification, retired surface, and residual risk; `git diff --check` remains clean.

#### Stop conditions

Conflicting upstream sources, a capability that requires a prohibited platform/dependency, or any requested external/retirement operation.

#### Result

Pinned commit `dd5989d4f9de5646349b3bceec4e19806262d14d` was inspected read-only. The target architecture is the installed initializer plus independent repository-local runtime. No upstream write, clone, fetch, backup, archive, or deletion occurred.

### T2 — Implement definition bootstrap and repository-local lifecycle

#### State

complete

#### Task type

implementation

#### Depends on

T1

#### Outcome

Deliver explicit definition start/status/validate/finalize with persisted evidence states, final canonical spec, first vertical-slice plan, and standalone operation.

#### Non-goals

Semantic interviewing by the CLI, automatic answers, overwriting `docs/PRODUCT.md`, generic config migration, or implicit draft creation from init/upgrade.

#### Read

`src/reporivet/cli.py`, `src/reporivet/initializer.py`, canonical/dogfood runtime, product/plan templates, docs catalogs, current tests, and this plan.

#### Allowed writes

CLI/initializer/package inventory helper, canonical/dogfood runtime, definition/product/plan assets, managed wrappers, focused tests, and directly corresponding docs.

#### Protected paths

Completed plans, existing project-owned files during generated-project tests, and all unrelated modules.

#### Acceptance

AC-1, AC-2, AC-6, AC-14

#### Verify

Greenfield, idempotent start, partial resume, no repeated confirmed sections, invalid/blocked draft, final spec/first plan, generated-runtime parity, and package-independent fixtures.

#### Stop conditions

Missing semantic decisions, proposal promotion, authority overwrite, unmarked command collision, non-transactional finalization, or generated runtime package import.

#### Result

Implemented explicit package-side `reporivet define --root`, managed `./dev/define`, a project-owned resumable fourteen-section draft, structural status/validation/finalization, canonical spec and first-slice plan rendering, collision refusal, transactional catalog/output rollback, exact managed ownership, repository-local symlink refusal, reciprocal Journey/P0/AC checks, and standalone stdlib-only operation. Focused definition tests passed 25/25 and the full suite passed 40/40 under Python 3.12; in-memory compilation, canonical/dogfood version-token parity, and `git diff --check` passed. A separate read-only verification context reproduced earlier failure cases, verified their corrections and valid-boundary behavior, left repository status unchanged, and returned `T2 verdict: PASS` with no remaining T2 finding. Clean candidate SHA and final Verification Run evidence remain intentionally deferred to T9.

### T3 — Implement deterministic audit and authority-preserving adoption

#### State

complete

#### Task type

implementation

#### Depends on

T2

#### Outcome

Deliver package and repository-local audit plus explicit adoption that adds only missing responsibilities and retains inferred commands in review.

#### Non-goals

Executing discovered commands, network access, timestamps/random output, replacing authority documents, or generating a second audit state database.

#### Read

Initializer detection/ownership functions, runtime config model, managed templates, ignore rules, and audit/adoption tests.

#### Allowed writes

Package inventory/initializer/CLI, canonical/dogfood runtime and wrappers, audit documentation, and focused tests.

#### Protected paths

Existing README, AGENTS outside managed blocks, architecture, CI, manifests, lockfiles, source/tests, and project-owned config in adoption fixtures.

#### Acceptance

AC-3, AC-6, AC-14

#### Verify

Two audits produce identical bytes and an unchanged full-tree snapshot; adoption preserves authority byte snapshots, records conflicts/skips, refuses collisions, and leaves inferred commands in review.

#### Stop conditions

Audit writes anything, executes project code, traverses outside root, contacts the network, leaks absolute paths, or adoption needs a substantial authority rewrite.

#### Result

Implemented package-side `reporivet audit --root` and `reporivet define --root --adopt`, managed `./dev/audit`, and the byte-equivalent standalone runtime audit. Audit emits sorted `reporivet.audit/v1` JSON with the five declared statuses, relative POSIX paths, configured-command redaction, no project-command execution, no symlink traversal, and deterministic package/runtime/wrapper bytes. Adoption audits before writing, blocks on conflicts, preserves existing authority and `dev/harness.toml`, creates missing configuration in review state, updates only bounded standalone-marker blocks, refuses unsafe/colliding/nonregular paths, is idempotent, and rolls back exact target bytes and modes after injected failure.

Edge-case hardening covers symlinked runtime/wrapper roots, invalid UTF-8 and malformed config, directories/FIFOs/unreadable command inputs, incidental inline and fenced marker examples, and CRLF authority bytes through later `docs-index` updates. Focused audit/adoption tests passed 19/19 and the full suite passed 59/59 under Python 3.12; in-memory compilation, canonical/dogfood version-token parity, live package/runtime/wrapper audit parity (21,198 bytes, SHA-256 `0e9fd2a46bfe0447fd7255bb59b0f3deaae4c603e70794b484035f586fe9ce60`), and `git diff --check` passed. The same separate read-only verification context independently reproduced every earlier failure fixture, confirmed CRLF/rollback/idempotence/package independence, left repository status unchanged, and returned `VERDICT: PASS`. Clean candidate SHA and final Verification Run evidence remain deferred to T9.

### T4 — Add opt-in product-to-evidence traceability

#### State

complete

#### Task type

implementation

#### Depends on

T2

#### Outcome

Validate stable Journey/P0/AC links through product specs, Product Trace, Task Packet acceptance, run evidence, and verified commits while preserving legacy plans.

#### Non-goals

Rewriting historical plans, forcing full traceability on small unplanned changes, or adding a generic document/schema engine.

#### Read

Runtime frontmatter/section/task/plan helpers, product/plan templates, current completed plans, and new definition outputs.

#### Allowed writes

Canonical/dogfood validators, product/plan templates, current plan/spec docs, and traceability tests.

#### Protected paths

Completed plans and acceptance criteria.

#### Acceptance

AC-4, AC-14

#### Verify

Valid chain passes; duplicate/unknown/missing IDs, P0 without AC, implementation/verification task without AC, complete plan without evidence/SHA, and REVIEW without reason fail; historical completed plans remain valid unchanged.

#### Stop conditions

Validation requires semantic inference, existing completed history must change, or evidence paths can escape `.harness/runs/`.

#### Result

Implemented opt-in validation for plans with `traceability: 1` only. Referenced active product specs now supply confirmed stable Journey/P0/AC declarations with duplicate, known-link, reciprocity, and shared-journey checks; Product Trace rows bind those IDs to known Task Packets and task acceptance. Traceable implementation and verification tasks require a Task type and known AC, terminal traceable plans reject unresolved placeholders, and complete traceable plans require criterion-level run evidence, manifest SHA-256, verified commit, PASS/REVIEW verdict, and a genuine REVIEW reason when applicable. Evidence paths are structurally confined beneath `.harness/runs/<verification_run>/`; historical completed plans without opt-in metadata remain byte-unchanged and valid.

The generic product-spec and ExecPlan templates plus generated first-slice plans expose the opt-in fields and evidence table, and `SPEC-REPORIVET-002` supplies the current confirmed authority for this plan. Focused traceability tests passed 3/3, the full suite passed 62/62 under Python 3.12, compile, catalog, strict plan, runtime/template parity, `git diff --check`, and `./dev/check` passed. The first `./dev/check` attempt used the configured system `python3` (3.9) and failed because `tomllib` is unavailable; rerunning the unchanged gate with a temporary PATH shim to the required Python 3.12 passed all checks and 62 tests. A separate read-only verification context exercised the declared invalid links, task gaps, completion metadata, REVIEW reason, and literal/Markdown evidence-path escape cases, confirmed unchanged repository state and legacy history, and returned `VERDICT: PASS`. Clean candidate SHA and final Verification Run evidence remain deferred to T9.

### T5 — Add conditional module knowledge and context routing

#### State

complete

#### Task type

implementation

#### Depends on

T2, T4

#### Outcome

Generate contracts only for justified boundaries, derive a deterministic non-authoritative code map, and route relevant context by path/area.

#### Non-goals

A contract for every directory, speculative generic rows, language-specific import enforcement, or making generated output authoritative.

#### Read

Runtime context/catalog/config/path helpers, detected/configured paths, definition confirmed planned paths, and documentation conventions.

#### Allowed writes

Canonical/dogfood runtime, wrapper/assets, module-contract/code-map docs, context docs, and focused tests.

#### Protected paths

Unrelated docs/source and existing project-owned contracts.

#### Acceptance

AC-5, AC-6, AC-14

#### Verify

Actual/configured/confirmed-planned rows appear, inferred-only/generic rows do not, contract metadata validates, drift is detected, and path/area context selects the correct contract/map/spec.

#### Stop conditions

No durable boundary evidence, unknown values would need guessing, or generated rows become a source of truth.

#### Result

Implemented a narrow module-contract schema for stable `MOD-*` identity, lifecycle, area, summary, owner, responsibility, applicable paths, public entry points, dependency rules, organization, and verification commands. Contract scopes must be supported by an existing safe repository path, configured source/test path, or an explicitly confirmed planned path; unresolved placeholders and unsupported scopes fail deterministically, while explicit `unknown` values remain visible rather than inferred. The frontmatter parser now preserves list-valued metadata, enabling existing durable `applies_to` routing as well as contract validation. Reporivet dogfoods exactly one justified contract for the canonical-package-asset/copied-runtime boundary.

Added deterministic, non-authoritative `./dev/code-map` generation and `--check` drift detection. The map emits only configured source/test paths, active contract scopes, and `[confirmed] Planned path:` declarations under an explicit level-three `Confirmed` evidence heading, adding `actual` only when the path exists. `docs-check` validates the same model and rejects stale output. `context --path`, `--area`, and `--plan` now select matching active contracts, map entries, durable documents/specifications, and selected-plan product authority. The initializer packages the module-contract README/template and bootstrap map, owns the managed `dev/code-map` wrapper, generates the map before document checks, and includes code-map assets/checking in doctor; the copied runtime remains standard-library-only and package-independent.

Focused T5 tests passed 4/4 and the full suite passed 66/66 under Python 3.12. Compile, code-map drift, document catalog, strict docs, strict plan, architecture, doctor, canonical/dogfood runtime and template parity, `git diff --check`, and the unchanged `./dev/check` gate all passed; the gate used a temporary PATH shim so configured `python3` resolved to the required Python 3.12. Initial independent read-only verification found that a level-two heading did not clear prior `### Confirmed` state, reproduced a wrong-heading planned row, and returned FAIL. The parser was narrowed to clear state on level-one/two headings, the exact reproducer was added to the focused suite, and focused/full/gate checks passed again. The same independent verifier reproduced the corrected behavior, confirmed proposed, inferred, wrong-heading, and unrelated generic paths are omitted, and returned `VERDICT: PASS`. Clean candidate SHA and final Verification Run evidence remain deferred to T9.

### T6 — Implement one Verification Run and structured evidence

#### State

complete

#### Task type

implementation

#### Depends on

T3, T4, T5

#### Outcome

Make one canonical verify invocation share one run context across the fixed checks and preserve deterministic summaries/logs on pass, fail, or error.

#### Non-goals

A registry, plugin/pipeline framework, second gate, complex exception taxonomy, raw logs in Git, or weakening current checks.

#### Read

`execute_group`, all built-in check commands, config loading, security scanner, run ignore rules, and current failure tests.

#### Allowed writes

Canonical/dogfood runtime, verification docs, and runtime tests.

#### Protected paths

Check acceptance, security rules, project-owned command configuration, and unrelated commands.

#### Acceptance

AC-7, AC-8, AC-9, AC-14

#### Verify

Exactly one top-level run; all seven fixed stages and external logs share it; deterministic UTF-8/newline JSON/Markdown uses relative POSIX paths; missing executables are errors; candidate failures block; optional smoke skips; failures preserve artifacts; recursive verify config is rejected.

#### Stop conditions

More than one top-level run, lost artifacts, silent missing check, raw secret/log commit, or a generated runtime dependency on Reporivet.

#### Result

Implemented one shared Verification Run with seven fixed ordered stages, immediate per-check JSON persistence, shared built-in/external logs, deterministic manifest/Gate/report finalization, candidate-failure versus infrastructure-error semantics, required failure precedence, optional absent-smoke skip, malformed configured-smoke blocking, explicit local Git target evidence without parent inference, structured command redaction, and recursion rejection across architecture, project, and smoke groups. The T6 Gate remains deliberately `UNKNOWN`/`deferred` until T7 policy is applied.

Focused verification tests passed 10/10 and the full suite passed 76/76 under Python 3.12. Strict code-map, document catalog, documentation, plan, security, runtime parity, in-memory compilation, and `git diff --check` passed. Post-fix dogfood run `.harness/runs/20260829T170435788817Z-verify` passed all required stages, skipped only absent optional smoke, and bound manifest SHA-256 `5d3382d727a445f1698b3c1f929726194c295b2fec41f99d0ae634d3c8e463c4`. Independent verification reproduced the architecture/smoke recursion guards and all T6 pass/fail/error/no-Git/explicit-target scenarios, found no remaining defect, and returned `VERDICT: PASS`. Clean final candidate evidence remains deferred to T9.

### T7 — Add Gate policy and evidence-bound close-plan

#### State

complete

#### Task type

implementation

#### Depends on

T6

#### Outcome

Classify explicit local changes, produce the four Gate verdicts with shadow/enforce behavior, and bind plan closure transactionally to one clean-HEAD run.

#### Non-goals

Scores/confidence, auto-merge, network Git evidence, inferred parent commits, overriding BLOCK/INCONCLUSIVE, or a second verification path.

#### Read

Config generation/loading, Git helpers, verify result schema, current close-plan lifecycle, plan template, and close-plan tests.

#### Allowed writes

Initializer config generation/doctor, current dogfood config, canonical/dogfood runtime, plan templates/docs, and Gate/closure tests.

#### Protected paths

Existing configs during upgrade, completed plans, Gate priorities, and acceptance criteria.

#### Acceptance

AC-10, AC-11, AC-12, AC-14

#### Verify

Contained clean PASS; protected/unknown/wide/irreversible/dirty REVIEW; required fail BLOCK; executable/config/target error INCONCLUSIVE; shadow/enforce exits; missing evidence cannot PASS; REVIEW reason required; BLOCK/INCONCLUSIVE never override; close-plan makes one run and rolls back a failed move.

#### Stop conditions

Target mismatch, unavailable required explicit SHA at closure, dirty closing worktree, policy weakening to force PASS, fabricated acceptance, or closure Gate BLOCK/INCONCLUSIVE.

#### Result

Implemented conservative generated `[gate]` policy plus read-only in-memory defaults for existing configs, deterministic doctor advisories, explicit local base/head/target evidence, canonical Git commit resolution, contained/wide/irreversible/unknown risk classification, independent protected-path matching, fixed PASS/REVIEW/BLOCK/INCONCLUSIVE priority, and shadow/enforce exit semantics. Malformed policy or target evidence becomes INCONCLUSIVE; missing evidence cannot PASS; no parent, remote, fetch, or network evidence is inferred.

`close-plan` now invokes the canonical Verification Run exactly once against the plan base and clean current HEAD, validates the persisted manifest/Gate/hash/target binding, accepts PASS directly, requires one safe explicit human reason for REVIEW, rejects BLOCK/INCONCLUSIVE without override, binds traceable criterion rows, and transactionally restores the exact active bytes and mode after a failed move or post-move structural check while retaining verification artifacts. Plan enumeration now refuses symlinked directories/files and FIFO or other nonregular Markdown entries before opening them.

Focused Gate/Verification, close-plan, old-config/doctor, and traceability suites passed 31/31; the complete suite and `./dev/check` passed 89/89 under the required Python 3.12 PATH shim. Compilation, security, code-map/catalog drift, strict documentation/plan/architecture checks, package doctor, canonical/dogfood version-token parity, and `git diff --check` passed. Two independent read-only reviews initially found abbreviated/uppercase explicit SHA mismatch and pre-guard symlink/FIFO plan reads; both defects received focused regressions and the same reviewers independently reproduced the fixes, verified the genuine mismatch and refusal boundaries, and returned PASS with no remaining finding. The exact committed T7 candidate Verification Run remains separate ignored evidence; final plan-bound closure evidence remains deferred to T9.

### T8 — Integrate ownership, CI, documentation, and release packaging

#### State

complete

#### Task type

implementation

#### Depends on

T7

#### Outcome

Restore generated/dogfood parity, propagate CI evidence, document current behavior/migration, and create a release-ready `0.2.0` wheel with complete assets and no forbidden surfaces.

#### Non-goals

Publishing, GitHub writes, changing the old repository, dependencies, model assets, daemons, targets, or broad unrelated documentation rewrites.

#### Read

Managed asset maps/rendering/doctor, wrapper template, generated/dogfood CI, package data, current-state docs/specs/designs, and release tests.

#### Allowed writes

Initializer/assets/wrappers, dogfood config/runtime, CI files, package version/data, current-state and packaged docs, migration references, and distribution tests.

#### Protected paths

Existing generated-project authority/config during upgrade, completed plans, secrets, and external repositories.

#### Acceptance

AC-6, AC-13, AC-14, AC-15

#### Verify

Version-token-only runtime parity; all wrappers honor `PYTHON`; upgrade preserves config bytes; doctor advisory; CI uses immutable actions/read-only permissions/full history/explicit target/one verify/always upload; wheel inventory contains every required asset and no bytecode/Skill/target/model/daemon; isolated and package-removed operation passes.

#### Stop conditions

Unpinned or broader CI action/permission, forbidden wheel asset, production dependency, network-required validation, config rewrite, or any external publication/retirement action.

#### Result

Established `reporivet.__version__` as the single package version source at `0.2.0`, switched project metadata to dynamic attribute lookup, regenerated every dogfood managed marker/runtime/wrapper from canonical assets, and encoded exact generated/dogfood byte parity plus executable and `PYTHON`-aware wrapper checks. `doctor` now requires `dev/audit` and the project-owned project-definition protocol while preserving the existing missing-`[gate]` advisory; init/upgrade create a missing protocol but preserve existing protocol and configuration bytes.

Generated and dogfood CI now use immutable action SHAs, `contents: read`, full history, the explicit PR/push head, explicit base/head/target exports, one bootstrap then one verify, step-summary reporting, and `if: always()` run-artifact upload. An all-zero push base remains unavailable and no parent/fetch/network evidence is invented. Ruby/Psych parsed both workflow files; `actionlint` was not installed locally and was not silently claimed.

Added a complete offline distribution regression that builds `reporivet-0.2.0-py3-none-any.whl` without build isolation, dependencies, index, or network; checks the complete package-asset inventory and absence of bytecode, Skill, target, model, and daemon surfaces; installs into a fresh environment; exercises installed CLI/init/doctor/verify/definition/audit; uninstalls Reporivet; and then proves repository-local definition, audit, context, planning, checks, verification, gardening, and real-Git close-plan operation. The focused initializer/template suite passed 18/18, the distribution suite passed 1/1, and the complete suite passed 94/94 under Python 3.12. The unchanged canonical `./dev/check` passed the same 94 tests with a temporary Python 3.12 `python3` shim. In-memory compilation, security over 109 tracked paths, catalog drift, strict documentation/plan, architecture, package doctor, managed parity, and `git diff --check` passed.

Synchronized current and generated-project documentation for definition, deterministic audit/adoption, traceability, conditional contracts/code map/context, one Verification Run, Gate/closure, explicit CI evidence, package removal, and the local-only release boundary. Added substantive `DESIGN-REPORIVET-002`, the human/Main project-definition protocol, and one generic create-if-missing protocol template without copying Reporivet-specific specs/design/migration artifacts into target projects. Catalogs now include the new design.

The first full post-document suite exposed one ownership-parity omission: package inventory included the new protocol while standalone runtime audit/required-doc lists did not. Both canonical lists were updated, dogfood runtime was regenerated, audit/adoption passed 19/19, and the complete suite passed 94/94 again. Independent read-only review initially found an overstated command allowlist in architecture/security/user docs. The wording now distinguishes project-configured argv from fixed runtime-owned validation and local Git-evidence argv; the same reviewer verified runtime call sites, strict docs/catalogs, bilingual parity, packaging/ownership/CI/migration boundaries, and returned PASS with no remaining T8 finding.

### T9 — Integrate, independently verify, and close the release candidate

#### State

complete

#### Task type

verification

#### Depends on

T1, T2, T3, T4, T5, T6, T7, T8

#### Outcome

Produce criterion-by-criterion evidence for a clean candidate commit, close this plan only under its Gate rules, and retain a release-ready local artifact boundary.

#### Non-goals

Implementer self-approval, weakening policy, a second final verify after history-only closure, publishing, or old-repository actions.

#### Read

This plan, all changed code/tests/docs, the clean candidate diff, wheel inventory, generated-project fixtures, and Verification Run artifacts.

#### Allowed writes

Main-owned plan progress/evidence, temporary ignored verification artifacts, candidate commit, and later completed-plan bookkeeping commit.

#### Protected paths

Acceptance criteria, verified candidate after evidence creation, raw logs, external systems, and old repositories.

#### Acceptance

AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15

#### Verify

Compile, full unittest, security, docs-index, strict docs/plan, architecture, check, one canonical verify, wheel inventory/install, definition/resume/audit/adoption, generated verify/doctor, package removal, Gate/close-plan matrix, and independent review against the exact clean candidate SHA.

#### Stop conditions

Dirty or mismatched target, missing evidence, failed criterion, manifest/head mismatch, Gate BLOCK/INCONCLUSIVE, REVIEW without a user-supplied reason, or any request to publish/delete externally.

#### Result

Preliminary candidate `f5de7ac4e8d42f16ac62f55c5edddb887b11647c` passed the independent Python 3.12 offline suite 94/94 and deterministic repository checks, but exact-commit review correctly returned FAIL for AC-14: package-side `validate_root()` resolved caller input before checking symlink components, so `init` and `define` wrote through a symlinked root. Root validation now checks the absolute unresolved root and every parent before any creation or write, and the focused regression covers both commands through direct root and parent symlinks.

Corrected clean candidate `2d5cce3589800999f823add6d68abc7d15980516` received independent `PASS_FOR_FINAL_GATE` across AC-1 through AC-15. The verifier reproduced all four former root/parent symlink cases with return code 2 and no target writes, ran the focused regression, complete offline suite 95/95, in-memory compile, security over 113 tracked paths, catalogs, strict docs/plan, architecture, package doctor, managed runtime parity, wheel/install/uninstall/package-removal coverage, and `git diff --check`, and found no remaining release-blocking defect. Plan-only terminal candidate `03a161778c504240eb1665f4f02cf1ae96022244` then received `PASS_FINAL_EXACT_SHA`, with source and test trees byte-identical to the corrected candidate.

Before push, the user explicitly requested matching Korean and English README explanations of the generated directory/document structure, ownership model, selective context flow, architectural rationale, conditional surfaces, and the fact that infrastructure configuration is not generated. This documentation-only refinement remains part of the same release candidate and must retain bilingual semantic parity and exact-SHA read-only confirmation. Candidate-tree `./dev/verify` and `close-plan` remain deliberately reserved; the one canonical Verification Run, manifest binding, Gate verdict, verified SHA, criterion rows, and any human REVIEW reason remain exclusively owned by `close-plan`.

## Architecture Impact

The public package CLI gains definition and audit entry points. Package-side inventory remains initializer-only; the generated runtime contains its own standard-library implementation and must not import the package. The canonical runtime gains fixed definition/audit/traceability/code-map functions and small Verification Run/Gate value objects, while retaining one file for package-removal portability. `execute_group` accepts a shared run context rather than creating per-group canonical run roots. Git evidence and Gate rendering are separate narrow helpers, not a framework. `dev/harness.toml` remains project-owned; optional Gate accessors apply in-memory defaults. Tests encode package/runtime schema and managed-file parity.

Dependency direction remains:

```text
installed CLI -> initializer/package inventory -> rendered repository assets
repository wrappers -> repository-local dev/harness.py -> stdlib + project files/commands
```

The reverse edge from generated runtime to installed package remains forbidden.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| `README.md`, `README.en.md`, `AGENTS.md`, `docs/README.md` | update | User commands, generated structure, document ownership, context routing, rationale, artifacts, Gate, and migration entry points | Main | complete |
| `ARCHITECTURE.md` | update | Unified lifecycle, evidence flow, ownership, command boundary, and dependency direction | Main | complete |
| `docs/PRODUCT.md` | update | New product capabilities and routing to detailed specs | Main | complete |
| `docs/DESIGN.md` | update | New design authority and non-goals | Main | complete |
| `docs/QUALITY.md` | update | Check statuses, Verification Run, Gate, traceability quality | Main | complete |
| `docs/SECURITY.md` | update | Audit/draft/evidence handling and no-network/external-write boundary | Main | complete |
| `docs/PLANS.md` | update | Product Trace, task types/acceptance, evidence-bound closure | Main | complete |
| `docs/design-docs/DESIGN-REPORIVET-001-initializer-and-runtime.md` | update | Preserve and extend two-lifetime ownership | Main | complete |
| `docs/design-docs/DESIGN-REPORIVET-002-project-definition-adoption-and-evidence-gate.md` | create | Durable behavior and trade-offs for this feature set | Main | complete |
| `docs/product-specs/SPEC-REPORIVET-001-generated-project.md` | update | Generated-project observable lifecycle | Main | complete |
| `docs/product-specs/SPEC-REPORIVET-002-project-definition-adoption-and-evidence-gate.md` | create | JRN/REQ-P0/AC source of truth for this plan | Main | complete |
| `docs/references/project-definition-protocol.md` | create | Stable human/Main definition protocol | Main | complete |
| `docs/references/harness-engineering-skill-migration.md` | create | Pinned capability migration matrix | Main | complete |
| ExecPlan and product-spec templates | update | Opt-in traceability/task/evidence fields | Main | complete |
| Packaged project docs/CI templates | update/create | Generated projects receive matching current behavior | Main | complete |
| Document catalogs | generate | Keep indexes synchronized after coherent updates | Main | complete |

## Interfaces and Dependencies

- Existing project capabilities reused: ownership markers, managed-block upsert, config preservation, project detection, command inference, durable document catalogs, frontmatter/plan/task parsing, security scanning, subprocess streaming, plan IDs, context routing, close-plan transaction shape, and gardening.
- New production dependency: none.
- Public contract impact: new `reporivet define`, `reporivet audit`, `./dev/define`, `./dev/audit`, `./dev/code-map`, Verification Run schemas, optional `[gate]`, and `close-plan --accept-review`.
- External service impact: none; CI only uploads job-local artifacts through an immutable existing GitHub Action and receives no write permission beyond artifact storage intrinsic to the workflow run.

## Migration, Rollout, and Recovery

New projects receive the new runtime, wrappers, definition templates, and explicit shadow Gate defaults. Existing projects continue to work with missing `[gate]` because defaults are applied in memory; `doctor` advises configuration review. Upgrade refreshes marked managed files and creates missing assets but never edits project-owned config or authority documents. Unmarked canonical path collisions stop before writes.

There is no persisted-data migration, network migration, old repository operation, or compatibility framework. Recovery is a normal Git revert of the candidate or generated-project upgrade commit. Definition finalization and plan closure are transactional. `.harness/runs/` is ignored, disposable local/CI evidence. The release boundary is the clean candidate commit recorded in the manifest; the later completed-plan move is historical bookkeeping.

## Surprises and Discoveries

- 2026-08-29 — The system `python3` is 3.9.6; local deterministic commands require explicit Python 3.12.
- 2026-08-29 — No active umbrella plan existed; this plan was created from the canonical template at base commit `9d6d6600c54d29f7bb67dcb65eb5bffed56e337c`.
- 2026-08-29 — HarnessEngineeringSkill has five byte-equivalent runtime bundles plus an Antigravity prompt; these are deployment duplication, not target architecture.
- 2026-08-29 — The pinned upstream model-evaluation path expects missing/ignored test material and is not suitable for blocking verification.
- 2026-08-29 — Dogfood `dev/security-check` is bespoke and does not honor `PYTHON`, unlike the packaged wrapper ownership map.
- 2026-08-29 — Current canonical/dogfood runtime comparison must normalize the managed harness-version token; parity became a deterministic test.
- 2026-08-29 — T2 independent verification showed that placeholder detection must normalize Unicode/Markdown edge punctuation and that malformed stable-ID detection must distinguish compact ID-like fields from ordinary prose beginning with `AC`, `JRN`, or `REQ`.
- 2026-08-30 — Explicit abbreviated or uppercase Git object IDs must be resolved to their canonical local commit before comparison; raw textual comparison falsely reports a target mismatch.
- 2026-08-30 — Plan discovery must reject symlinked and nonregular entries before reading frontmatter; checking only the selected plan after enumeration permits outside reads and FIFO hangs.
- 2026-08-30 — A new project-owned scaffold must be mirrored in both package inventory and standalone runtime audit/required-document ownership; the full suite exposed the initially omitted protocol path.
- 2026-08-30 — `dev/harness.toml` is the source of project-configured argv, not an exhaustive process allowlist; built-in validation and local Git evidence use fixed runtime-owned argv and must be documented separately.
- 2026-08-30 — Package root validation must inspect the absolute but unresolved caller path before canonicalization; resolving first erases root and parent symlink evidence and permits initialization writes through the link.

## Decision Log

- 2026-08-29 — Extend the existing initializer plus standalone copied runtime; do not introduce another operating system or framework.
- 2026-08-29 — Keep `./dev/verify` as the only completion gate and refactor existing checks into one fixed shared run.
- 2026-08-29 — Keep semantic questions and REVIEW approval human/Main-owned; commands validate persisted structure/evidence only.
- 2026-08-29 — Apply new traceability rules only to plans opting in with `traceability: 1`; preserve historical completed plans unchanged.
- 2026-08-29 — Missing Gate config receives conservative shadow defaults in memory; upgrades do not rewrite project-owned config.
- 2026-08-29 — Use explicit environment or plan base/head evidence only; never infer a parent, remote, or fetch.
- 2026-08-29 — The user’s no-backup/no-delete instruction supersedes old-repository preservation and retirement execution. Reporivet-side migration documentation remains in scope.
- 2026-08-29 — Prepare version `0.2.0` locally but do not publish or perform external GitHub writes.
- 2026-08-30 — Package one generic project-definition protocol as a project-owned create-if-missing scaffold; keep Reporivet-specific specs, designs, and migration records out of generated target projects.
- 2026-08-30 — The user explicitly authorized committing and pushing the current working branch after adding bilingual README explanations of generated structure, document use, context routing, rationale, and non-generated infrastructure; PR, merge, release, publication, deployment, and unrelated external writes remain excluded.

## Concrete Steps

Run commands from the repository root with `PYTHON=/Users/hakseong/.local/bin/python3.12` where wrappers resolve Python.

1. Complete and check T1 migration/reference artifacts.
2. Implement T2–T8 sequentially, keeping the packaged runtime canonical and running focused tests plus `./dev/check` after each integrated slice.
3. Regenerate dogfood runtime/wrappers and document catalogs only after corresponding sources are coherent.
4. Run compile, full unit, strict docs/plan, security, architecture, wheel, isolated install, generated-project, package-removal, Gate, and close-plan scenario tests.
5. Resolve every Documentation Impact row and set all implementation tasks complete.
6. Set this plan to `verifying` and `integrated_commit: "HEAD"`; commit the candidate.
7. Independently verify the clean candidate with explicit base/head evidence and inspect manifest/gate/report against all ACs.
8. If Gate is REVIEW, obtain a genuine non-empty user acceptance reason; never synthesize it.
9. Run `./dev/close-plan PLAN-2026-0002 --accept-review "<user reason>"` only when permitted, then commit the completed-plan record separately without a second canonical verify.

## Validation and Evidence

### Acceptance closure

| Acceptance criterion | Task | Evidence path | Run ID | Manifest SHA-256 | Verified commit | Gate verdict | Review reason |
|---|---|---|---|---|---|---|---|
| AC-1 | T2/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-2 | T2/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-3 | T3/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-4 | T4/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-5 | T5/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-6 | T2/T5/T8/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-7 | T6/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-8 | T6/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-9 | T6/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-10 | T7/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-11 | T7/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-12 | T7/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-13 | T8/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-14 | T2-T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |
| AC-15 | T1/T8/T9 | closure-bound | closure-bound | closure-bound | `HEAD` | closure-bound | required only for REVIEW |

- Integrated target: `HEAD`
- Verified commit: bound by `close-plan`
- Verification Run: reserved for the one `close-plan` invocation
- Manifest SHA-256: bound by `close-plan`
- Gate verdict: bound by `close-plan`
- T8 pre-candidate regression: Python 3.12 full suite 94/94 PASS; focused initializer/template 18/18 PASS; audit/adoption 19/19 PASS after protocol parity correction; offline distribution/package-removal 1/1 PASS.
- T8 repository checks: in-memory compile PASS; `./dev/check` PASS with 94 tests; security PASS over 109 tracked paths; code-map/catalog/strict docs/plan/architecture/package doctor/managed parity/`git diff --check` PASS.
- T8 CI syntax: Ruby/Psych parse PASS for dogfood and packaged workflows; `actionlint` unavailable locally.
- T8 independent review: initial command-boundary documentation finding corrected; same read-only reviewer returned PASS for AC-6, AC-13, AC-14, AC-15, ownership, config preservation, bilingual parity, links/catalogs, CI, and generic-template scope.
- T9 exact reviews: preliminary candidate `f5de7ac4e8d42f16ac62f55c5edddb887b11647c` returned FAIL for the reproduced package root-symlink write; corrected candidate `2d5cce3589800999f823add6d68abc7d15980516` returned `PASS_FOR_FINAL_GATE` for AC-1 through AC-15 after 95/95 and explicit four-case no-write reproduction; plan-only terminal candidate `03a161778c504240eb1665f4f02cf1ae96022244` returned `PASS_FINAL_EXACT_SHA`. The subsequent user-requested bilingual README structure/rationale refinement requires the same deterministic checks and final exact-SHA confirmation before push.
- Raw logs: `.harness/runs/` and not committed

## Outcomes and Retrospective

T1-T9 delivered the requested repository-native lifecycle, deterministic evidence model, current/generated documentation, bilingual generated-structure and context-rationale guidance, local `0.2.0` packaging boundary, corrected root-symlink safety, and exact independent candidate verification without publication, release, deployment, or former-repository operations. The plan is ready for its one canonical Gate-bound `close-plan` transition after the final documentation-only candidate receives exact-SHA confirmation; closure will bind the run, manifest, verdict, verified SHA, criterion rows, and any person-supplied REVIEW reason.

## Follow-ups

Promote unresolved in-scope debt to [`tech-debt-tracker.md`](/docs/exec-plans/tech-debt-tracker.md) before completion. Do not create an external task system.

- none yet
