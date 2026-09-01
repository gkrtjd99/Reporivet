---
id: DESIGN-REPORIVET-003
kind: design-doc
status: active
area: harness
summary: Ownership and routing design for the document-first Agent harness
applies_to:
  - "src/reporivet/**"
  - "src/reporivet/assets/project/**"
  - "AGENTS.md"
  - "CLAUDE.md"
  - ".claude/**"
  - "docs/**"
supersedes:
  - DESIGN-REPORIVET-001
  - DESIGN-REPORIVET-002
---

# Document-first Agent harness

## Design status and governing records

This design is the current implementation authority for the approved boundary in [`SPEC-REPORIVET-003`](../product-specs/SPEC-REPORIVET-003-document-first-harness.md). Source behavior through the previously verified document-first implementation exists. Its historical candidate `f793567262ca66f11016aa198ddc46ec207eb23fbe91b234bf72a91348344293` passed AC-1 through AC-10 and AC-12; AC-11 wheel/install evidence remained unknown. Completed [`PLAN-2026-0003`](../exec-plans/completed/PLAN-2026-0003-document-first-harness.md) records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive. Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside scope. [`ADR-0001`](../decisions/ADR-0001-document-first-product-boundary.md) records why the prior repository-local runtime boundary is being retired.

The default onboarding design is integrated `reporivet setup`; `reporivet init` remains structure-only and lower-level `reporivet define` remains available. Setup creates no Plan or target runtime, does not spawn or dispatch Agents, and does not execute project commands. The Main Skill creates or resumes the first ordinary Markdown Plan. Complete user-confirmed structured procedures may create deterministic instruction-only project Skills only through resumed setup.

## System boundary and ownership

The design has a short-lived installed-package lifetime and a durable generated-repository lifetime, but no copied target runtime:

```text
installed Reporivet package
    └─ inventory, guided setup, optional adapters, explicit migration
         └─ project-owned documents, Plans, optional Claude assets
              └─ project-owned commands, CI, Git, and operations
```

The installed package owns only the temporary operations needed to inspect and prepare a target:

- deterministic read-only inventory and audit;
- integrated `setup` coordination, with lower-level `define` retained and structure-only `init` available;
- guided definition and setup preview;
- ownership classification and collision/refusal decisions;
- rendering of canonical document assets, explicitly requested Claude adapters, and complete user-confirmed procedure Skills;
- explicit 0.2 migration preview, external backup, apply, and rollback; and
- read-only diagnosis of the resulting package/document boundary.

Setup does not create a Plan or runtime, execute project commands, or spawn/dispatch Agents. The Main Skill owns first-Plan creation or resume.

The generated repository owns the durable result:

- `AGENTS.md`, the authority documents, decisions, references, and Markdown Plans;
- optional, catalogued Claude Skills and settings that a project has approved;
- project commands, test tools, CI, deployment configuration, and operational procedures; and
- Git history and any project-owned evidence or logs.

Generated authority documents become project-owned. Optional adapters may be managed only through a visible ownership marker or bounded managed block after explicit opt-in. Existing unmarked, customized, symlinked, or nonregular paths are not silently replaced. Existing historical Plans and `.harness/runs/` remain readable project history; the new design does not write new run artifacts there.

The target contains no copied `harness.py`, executor, shell wrapper, `dev/harness.toml`, Gate, Verification Run writer, generated CI workflow, context/code-map executor, garden command, or package-independent Reporivet command. Removing the installed package therefore removes setup capability, not the project's document, Plan, Git, command, or CI foundation.

## Document, Skill, and Plan routing

Routing is explicit and inspectable rather than implemented by a repository daemon or generated index:

1. `AGENTS.md` is the host-neutral entry. It identifies the canonical authority and tells an agent how to resume the active Plan.
2. `docs/README.md` maps authority documents, optional assets, Plan locations, ownership, and removal boundaries. It is a map, not a competing policy.
3. The relevant current authority document supplies product, design, quality, security, operations, or planning context. `docs/OPERATIONS.md` is the one current run/release/observe/backup/rollback/recovery authority.
4. One active Markdown Plan supplies the goal, acceptance, checkpoint, exact next action, decisions, discoveries, and compact evidence for the work.
5. A Claude Skill, when installed, supplies a role or procedure for reading those documents and returning bounded work. It does not become product authority or store hidden state.
6. The agent uses project-owned commands and CI for implementation and verification. Their definitions and results remain the project's responsibility.

`CLAUDE.md`, when present, is only a thin pointer from Claude Code to `AGENTS.md`. Skills and settings are optional adapters to this same route. There is no generated `context` or `code-map` command to infer a route, and no garden command to maintain one.

## Main, implementation Sub-Agent, and Verifier responsibilities

The operating model is deliberately Sub-Agent-first while keeping coordination durable. For every broad or multi-part root, the default packet is `Role: Task Owner` with `May delegate: yes`; narrow or inherently serial roots remain direct nondelegating leaves. The common installed-project rule is:

`T<n> (broad root Owner) -> T<n>-A/B/C/... (declared child packets, all ready leaves dispatched concurrently) -> T<n>-I (Owner-local aggregation) -> T<n>-V1/V2/... (parallel fresh verification)`

Main dispatches independent root Owners concurrently. Each Owner first returns a finite child manifest within its approved envelope. Main alone serializes accepted child rows and complete matching packets into the Plan, freezes their boundaries, and resumes that serialized Owner. Only the resumed serialized Task Owner dispatches its own declared dependency-ready descendants through host-native Agent execution; ordinary leaf Agents never delegate. Owner-local aggregation is distinct from Main's final repository integration, and fresh verification follows the integrated candidate.

- **Main** owns product intent, scope, non-goals, acceptance criteria, the overall hierarchical task tree, dependency state, root-owner dispatch, integration, Plan mutations, and the judgment that evidence is sufficient. Main Skill owns first-Plan creation/resume; Reporivet itself does not spawn or dispatch Agents.
- **Task Owner and implementation leaf** packets contain exact reads, allowed writes, protected paths, acceptance criteria, verification commands, stop conditions, and a return schema. Descendants inherit parent scope, protected paths, acceptance, non-goals, child budget, and frozen interfaces without broadening them. Only the resumed serialized Task Owner may dispatch its predeclared descendants; ordinary leaves do not delegate.
- **Verification leaf** receives a fresh context and independently inspects the integrated candidate. Read-only verification leaves may run in parallel, do not delegate, and depend on the integrated candidate. Each runs applicable project-owned tests or CI-equivalent commands, checks non-goals and ownership boundaries, maps results to acceptance criteria, and returns findings and residual risks without repairing the candidate.

Concurrent mutable siblings are allowed only with disjoint allowed-write sets, frozen shared interfaces, and separate exact-baseline worktrees. Their results converge on an Owner-local aggregation node distinct from Main's final integration; fresh verification nodes follow that integrated candidate, and any candidate mutation invalidates prior verification evidence. Main records concise returned evidence rather than repeating detailed verification by default. Reporivet installs no Agent spawn/dispatch mechanism, project command runner, CI/deployment engine, scheduler, dispatcher, task store, lease, lock, Gate, evidence archive, hidden state, automatic closure, or other runtime to dispatch, resume, or record this workflow; the Plan and host's native Agent execution carry the procedure.

## Authority-document layout

The generated document bundle is intentionally rich enough to be useful without a package:

- `AGENTS.md` and `docs/README.md` provide entry and map behavior;
- `docs/PRODUCT.md`, `docs/DESIGN.md`, `docs/QUALITY.md`, `docs/SECURITY.md`, `docs/OPERATIONS.md`, and `docs/PLANS.md` provide current authority;
- `docs/product-specs/`, `docs/design-docs/`, `docs/exec-plans/{active,completed}/`, `docs/decisions/`, and `docs/references/` provide durable detail and history; and
- optional `.claude/` role Skills/settings and complete-procedure project Skills provide removable instruction adapters without moving authority into hidden configuration; setup creates only eligible procedure Skills and never a Plan.

`docs/OPERATIONS.md` replaces a split fresh-project operations/reliability authority. This does not grant migration permission to erase an existing project-owned `RELIABILITY.md` or other operational record; preservation and explicit ownership review remain mandatory.

## Guided setup and evidence handling

The default `setup` proceeds as scan, guided questions, preview, explicit approval, and write; lower-level `define` exposes the same visible definition stages directly, while `init` only creates structure. The scan is deterministic and read-only: it does not execute detected project commands, follow symlinks, or turn environmental inference into a decision. The user answers consequential questions, while the bundle chooses canonical filenames and stable locations. Setup reports actual Open items, creates no Plan/runtime, and may render a procedure Skill only when its complete structured record is user-confirmed.

Each definition section presents four non-interchangeable evidence areas:

- **Confirmed** contains accepted current evidence or a user decision and is the only state eligible for traceability.
- **Proposed** contains a labeled hypothesis that requires review.
- **Open** contains unresolved questions and their blocking status.
- **Sources** records where the information came from without promoting it to a decision.

Adoption audits before writing, preserves existing authority, adds only missing responsibilities, and leaves inferred commands in review. A collision, ambiguous ownership result, or unsafe path stops the operation before mutation. A failed write restores the captured pre-write state.

## Plan lifecycle

A substantive goal has one active Plan, not a parallel task database or journal. The minimal durable schema contains:

- goal and observable acceptance criteria;
- task rows with hierarchical ID when decomposed, Owner, State, Depends on, Outcome, Result, and optional Parallel group;
- one matching packet per row, with Role, Parent, May delegate, inherited boundaries/write isolation, and Return when decomposed;
- current checkpoint and exact next action;
- decisions and discoveries; and
- integration and verification evidence, including candidate identity when available.

For broad or multi-part roots, the packet defaults to `Role: Task Owner` and `May delegate: yes`; narrow or inherently serial roots remain direct nondelegating leaves. Main dispatches independent root Owners concurrently. An Owner returns a finite child manifest first; Main alone serializes accepted child rows and complete packets into the Plan, then resumes that Owner to dispatch its declared dependency-ready descendants. Ordinary leaves never delegate. Owner-local aggregation remains distinct from Main's final integration, and fresh verification nodes are read-only, nonrepairing, nondelegating, and candidate-specific.

Main Skill creates or resumes the Plan: it searches active and completed history, resumes one matching active Plan, stops on ambiguity, or creates the first ordinary Markdown Plan with the lowest unused current-year ID from the template. Setup and init never create the Plan. Main records each serialization checkpoint, owner-local aggregation, final integration, and fresh verification, and moves a terminal Plan from `active/` to `completed/` with an explicit outcome (`complete`, `cancelled`, or `superseded`). Integration nodes depend on their implementation leaves or Task Owners; fresh verification nodes depend on the integrated candidate. The `task_graph: 1` marker opts a compact `format: 2` Plan into strict hierarchy checks; unmarked compact Plans retain structural validation, historical expanded or completed Plans remain untouched, recursive task IDs remain valid, and direct serial Plans remain supported. There is no automatic closure, Gate verdict, run directory, scheduler, dispatcher, task store, command runner, evidence archive, or second verification engine. Historical Plans remain readable even if they contain retired Gate or evidence fields.

## Claude Skills and settings safety

Claude is the first optional host profile, not a new authority layer.

- Skills are catalogued instruction assets with a declared role, scope, inputs, outputs, and least-privilege tool expectations. They may route an agent to documents and project commands but may not hide state, make semantic product decisions, or introduce a copied executor.
- Settings are optional and minimal. They are previewed as a concrete diff, never silently merged into an existing settings file, and never used to smuggle secrets, broad permissions, or unrelated hooks into a project.
- Creation is limited to missing paths or proven Reporivet-owned blocks. Existing project-owned bytes, unmarked files, symlinks, and nonregular paths are preserved or cause a refusal.
- Removing a Skill or settings adapter must not remove the canonical documents or make the Plan lifecycle unusable.

## Installation and artifact boundary

Public users are guided to install with pipx first (`pipx install reporivet`); pip is supported from the same wheel (`python -m pip install reporivet`). Source-checkout commands are contributor-only. Completed [`PLAN-2026-0003`](../exec-plans/completed/PLAN-2026-0003-document-first-harness.md) records the exact source candidate and wheel lifecycle above. The verification artifacts are temporary and are not a durable or downloadable evidence archive; publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside scope. Reporivet does not publish, sign, or release packages.

## Explicit 0.2 migration transaction

The package owns migration orchestration because it is the only phase allowed to retire old generated assets. Ordinary upgrade does not perform this retirement. Migration follows this transaction:

1. **Preview.** Scan the target without mutation and emit a stable fingerprint, ownership classification, proposed additions/removals, preserved paths, conflicts, and blockers.
2. **Approval gate.** Require explicit human approval of that preview. Reject approval if the target fingerprint changed or if a blocker remains.
3. **External backup.** Before destructive work, create an external, visible backup selected and reported to the user, with a manifest, modes, and checksums. The backup is not hidden inside the target and is not replaced by `.harness/runs/`.
4. **Apply.** Write the new documents and optional adapters only where allowed. Remove or replace only proven Reporivet-managed 0.2 runtime, wrapper, configuration, generated CI, context/code-map, Gate/evidence, and garden surfaces. Preserve project-owned/customized/ambiguous files, existing Plans, and `.harness/runs/`.
5. **Failure rollback.** If apply fails, automatically restore the exact captured state when the ownership and backup preconditions still hold; otherwise stop without overwriting user changes and report the recovery action.
6. **Post-success rollback.** Offer an explicit rollback using the external backup. Refuse when post-migration edits would be overwritten; if the target is unchanged, restore the exact backed-up bytes and metadata.

A legacy marker is evidence for classification, never by itself authorization for deletion. Every refusal is visible and actionable. Migration ownership, backup location, fingerprint, preserved paths, and rollback result are part of the user-visible record.

## Accepted trade-offs

- Setup and legacy migration still require the installed package, but ordinary repository work does not; this trades post-install convenience for a clean package boundary.
- Without a copied executor or Gate, verification and CI vary by project and require stronger project-owned commands and human/Main judgment; in return there is no duplicate runtime, stale generated policy, or false portable guarantee.
- Rich Markdown and one active Plan require disciplined maintenance, but they remain inspectable by any host and recoverable from Git without a state service.
- Claude-first Skills/settings improve one host's ergonomics while preserving host neutrality; non-Claude adapters are deliberately outside this scope.
- Removing generated context/code-map/garden surfaces avoids stale derived machinery but makes routing depend on clear documents and Plan links rather than automatic indexing.
- Preserving historical `.harness/runs/` and legacy Plan fields costs some cleanup, but keeps superseded work readable and avoids destructive history rewriting.
- Preview, external backup, and rollback make 0.2 migration slower and more explicit, which is accepted because retirement is destructive and ownership cannot be guessed.

## Verification conditions

The previously verified document-first source implementation established the source-side boundary through AC-1–AC-10 and AC-12 on its historical candidate. Completed [`PLAN-2026-0003`](../exec-plans/completed/PLAN-2026-0003-document-first-harness.md) records that the current source candidate and exact wheel passed the isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive. This record is not evidence of publication, signing, release, deployment, or CI repair/readiness; those remain unestablished and outside scope.
