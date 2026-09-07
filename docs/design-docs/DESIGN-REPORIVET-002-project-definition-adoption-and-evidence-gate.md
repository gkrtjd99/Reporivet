---
id: DESIGN-REPORIVET-002
kind: design-doc
status: active
area: harness
summary: Design of project definition, adoption, traceability, Verification Run, Gate, and evidence-bound closure
applies_to:
  - "src/reporivet/cli.py"
  - "src/reporivet/initializer.py"
  - "src/reporivet/assets/project/dev/harness.py"
  - "src/reporivet/assets/project/docs/**"
  - ".github/workflows/**"
supersedes: []
---

# Project definition, adoption, and evidence Gate

## Context and goals

Reporivet needed one repository-native lifecycle from uncertain product intent to a verified commit:

```text
Problem -> Journey -> P0 Requirement -> Acceptance Criterion
        -> ExecPlan -> Task -> Verification Evidence -> verified commit
```

The design must preserve uncertainty rather than hide it, adopt existing repositories without replacing their authority, keep the generated runtime independent after package removal, and retain `./dev/verify` as the only completion gate.

Observable product authority is [`SPEC-REPORIVET-002`](../product-specs/SPEC-REPORIVET-002-project-definition-adoption-and-evidence-gate.md). The human/Main operating procedure is the [project-definition protocol](../references/project-definition-protocol.md).

## Two-lifetime ownership

The installed package owns only package-side inventory, rendering, collision preflight, and ownership-aware writes. It exposes `define`, `audit`, `init`, `upgrade`, and `doctor`.

The copied runtime owns definition status/validation/finalization, repeatable audit, context routing, checks, one Verification Run, Gate, and closure. It imports no package code and uses only the standard library, repository files, local Git, and committed project commands.

Project intent, definition evidence, final specifications, current-state documents, plans, and `dev/harness.toml` remain project-owned. Managed runtime/wrapper/workflow files carry an explicit marker; shared authority receives only bounded blocks.

## Definition evidence and resumability

Definition is explicit: `reporivet define --root <path>` creates a project-owned fourteen-section draft. `init` and `upgrade` do not start it.

Each section contains Confirmed, Proposed, Open, and Sources in fixed order:

- Confirmed is current evidence and the only state that can satisfy traceability.
- Proposed remains a visible hypothesis and cannot silently become fact.
- Open records unresolved items; blocking Open items prevent finalization, while non-blocking items remain explicitly labeled.
- Sources record provenance without implying confirmation.

Stable `JRN-*`, `REQ-P0-*`, and `AC-*` identifiers make relationships searchable and restartable. Progress and the next consequential section are computed from the persisted draft, so a new process does not repeat confirmed work.

`status` reports progress without mutation. `validate` checks structure, stable IDs, evidence states, contradictions, completeness, and reciprocal journey/P0/criterion links. `finalize` validates again, writes a final specification and exactly one first vertical-slice ExecPlan transactionally, and refuses existing targets. Commands never interview, answer, or resolve semantic questions.

## Audit and authority-preserving adoption

Package and repository-local audit share observable semantics but remain independent implementations for their two lifetimes. Audit:

- walks only the selected root without following symlinks;
- ignores generated, dependency, cache, and repository-state directories;
- inventories instructions, durable docs, manifests, lockfiles, CI, runtime/configuration, source/test paths, commands, conflicts, additions, and skipped paths;
- emits sorted repository-relative paths and `confirmed`, `inferred`, `unknown`, `conflict`, or `skipped` status; and
- performs no writes, command execution, timestamps, random IDs, or machine-specific path emission.

`define --adopt` runs audit first and refuses any conflict before mutation. Existing README, instructions, architecture, CI, catalogs outside managed blocks, and configuration bytes are preserved. Missing responsibilities are added; inferred commands remain `configuration = "review"`. A failed write restores the exact captured tree.

## Traceability, contracts, and context routing

Traceability applies only when a plan opts in with `traceability: 1` and one active `product_spec`. Narrow parsers validate known confirmed IDs, reciprocal Product Trace links, task types, task acceptance IDs, and criterion-level closure evidence. Historical plans without the metadata remain valid.

Module contracts are conditional, not universal. A contract exists only for an actual, configured, or confirmed planned durable boundary. `./dev/code-map` derives non-authoritative rows from those same evidence classes and never invents generic modules.

Initialization uses the same evidence discipline for `repository-facts.md`: directly observed manifests, lockfiles, source/test roots, CI, runtime configuration, and entry points are separated from mechanically derived language, runtime, and command candidates, and every row carries an evidence path. `baseline-questions.md` exposes the product, ownership, security, reliability/SLO, and visual decisions that scanning cannot answer. Target-centered `PRODUCT.md` and `ARCHITECTURE.md` remain drafts until their structural evidence-review records are completed with concrete review evidence; status edits do not satisfy that check, and the review record does not require a verification result that would create a verify/evidence cycle.

`./dev/context --path|--area|--plan` routes matching specifications, contracts, map entries, durable documents, and active plans. Default authority is lifecycle-bounded to active current-state/product/design/runbook documents and accepted decisions. `--include-drafts` and `--include-history` opt into draft/proposed and deprecated/superseded/rejected/completed material. Context rejects duplicate IDs and inconsistent explicit supersession links but allows different authority IDs to cover the same scope; it performs no natural-language conflict interpretation or model judgment.

Accepted decision validation requires concrete reason/context, at least two substantive alternatives with rejection rationale, and verification/enforcement. The technical design and decision templates additionally make scope, the protected condition or prevented failure, repository/dependency capability research, applicable official primary sources, no-change and practical alternatives, and revisit/retirement conditions explicit.

## One Verification Run

One top-level `./dev/verify` creates exactly one `.harness/runs/<utc-run-id>-verify/` and executes fixed stages:

1. security;
2. docs-index drift;
3. documentation;
4. plans and traceability;
5. architecture;
6. configured project verification; and
7. optional smoke.

Check status is `pass`, `fail`, `error`, `skipped`, or `unknown`. Required candidate failure takes precedence over required infrastructure error. Optional unconfigured smoke is skipped; malformed configured smoke is an error. Direct and shell-hidden recursive verification is rejected.

The run preserves:

- `checks/*.json` with sanitized command metadata;
- `logs/` for available raw output;
- `manifest.json` with timing, detection, hashes, checks, and target evidence;
- `gate.json` with policy, risk, matches, verdict, reasons, and finalized manifest hash; and
- `report.md` with a concise human-readable summary and artifact links.

Failure and error paths finalize these artifacts as far as possible. Raw argv and logs are not copied into structured evidence.

## Explicit target evidence and Gate

Gate considers only caller-provided `REPORIVET_BASE_SHA`, `REPORIVET_HEAD_SHA`, `REPORIVET_TARGET`, a closing plan's base, observed local HEAD, worktree state, and the explicit base-to-target local diff. Valid abbreviated or uppercase object IDs are resolved to the canonical local commit before comparison. No parent, remote branch, fetch, or network evidence is inferred.

Risk is `contained`, `wide`, `irreversible`, or `unknown`. Verdict priority is:

1. required failure -> `BLOCK`;
2. required error/unknown, malformed policy, or target mismatch/error -> `INCONCLUSIVE`;
3. protected path, unknown/wide/irreversible risk, or required dirty state -> `REVIEW`;
4. clean confirmed contained target with all required checks passing -> `PASS`.

New configurations receive explicit shadow defaults. Existing project-owned configuration is never rewritten; equivalent conservative defaults apply in memory and doctor advises review. In shadow mode PASS/REVIEW may return zero while preserving the verdict; BLOCK returns one and INCONCLUSIVE two. In enforce mode only PASS returns zero.

## Evidence-bound close-plan

`close-plan` requires one active plan, a clean current HEAD, and an explicit plan base. It invokes the canonical verification implementation exactly once. PASS closes directly. REVIEW requires a genuine safe one-line reason supplied by a person. BLOCK and INCONCLUSIVE cannot be overridden.

Closure records the run ID, finalized manifest SHA-256, Gate verdict, verified commit, criterion evidence, and REVIEW reason when applicable. The plan then moves to `completed/` and only structural post-move checks run. A post-move failure restores the exact active plan bytes and mode while retaining run artifacts. The later historical bookkeeping commit is not reverified by a second canonical run.

## CI, package removal, and local release boundary

Generated and dogfood CI use immutable actions, `contents: read`, full checkout history, an explicit PR/push head, explicit base/head/target environment, one verify invocation, step-summary report, and `if: always()` artifact upload. An all-zero push base remains unavailable.

The local `0.2.0` boundary verifies one authoritative version, managed marker/wrapper/runtime parity, complete wheel assets, no bytecode/Skill/target/model/daemon surface, isolated installation, generated verify/doctor, package uninstall, and repository-local operation afterward. It does not publish a package or release.

## Migration and discarded surfaces

The pinned capability disposition is recorded in the [HarnessEngineeringSkill migration matrix](../references/harness-engineering-skill-migration.md). Reporivet absorbs durable definition, evidence, traceability, context, and validation responsibilities but discards Skill installation, runtime-specific target bundles, target synchronization, model judges, daemons, external task state, duplicate gates, and all old-repository backup/archive/delete/deprecation execution.

## Alternatives and trade-offs

- A generic schema framework was rejected in favor of narrow Markdown/frontmatter/table parsers because the contract is fixed and agent-legible.
- A plugin registry or policy DSL was rejected in favor of a fixed stage order and small value objects.
- Automatic semantic interviewing was rejected because commands cannot own human product decisions.
- Parent/remote inference was rejected because locally reproducible explicit evidence is safer than environmental guesses.
- Updating old configurations with `[gate]` was rejected because configuration is project-owned.
- A confidence score was rejected because deterministic verdict reasons are more inspectable and do not imply semantic certainty.

## Residual risks and verification

Structural validation cannot prove that a product decision is wise or that project commands cover every real failure mode. Human/Main still owns semantic completeness, conflict resolution, protected-change review, and smoke selection.

Regression coverage includes definition/resume/finalization, audit/adoption rollback and path safety, traceability, contracts/maps/routing, run status/artifact/error paths, Gate matrix, closure transaction, CI structure, managed parity, wheel inventory, isolated install, uninstall, and repository-local closure. Final release evidence additionally binds one clean candidate through the canonical Verification Run and independent review.
