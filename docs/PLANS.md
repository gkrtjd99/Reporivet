---
owner: main
status: active
last_reviewed: 2026-08-31
---

# Plans

## Purpose

A Plan is the single durable Markdown record for one substantive goal. It carries scope, acceptance, task ownership, decisions, checkpoint state, integration, independent verification, documentation impact, follow-ups, and outcome without requiring another task system.

Use [`exec-plans/_template.md`](exec-plans/_template.md) with `format: 2`.

## Conditional capability documents

A Plan records work on optional capability documents without becoming their authority. When `web_ui=yes` is explicitly Confirmed, `docs/FRONTEND.md` is the project-owned route for frontend implementation and client-side loading/error/retry guidance. When `deployed_runtime=yes` is explicitly Confirmed, `docs/RELIABILITY.md` is supplemental reliability guidance subordinate to `docs/OPERATIONS.md`; the latter remains universal operational authority.

Capability answers are visible setup/define evidence, audit output is attributable observation, and Plan status is work state. These vocabularies remain distinct: missing, Proposed, Open, Sources-only, inferred, or unverified capability values do not activate an artifact or establish acceptance. A Plan's Documentation Impact names any changed optional artifact, its owner and sources, and the exact project-owned checks or operational evidence used by a fresh Verification Sub.

## Setup and first-Plan handoff

The default onboarding command is integrated `reporivet setup`; `reporivet init` is structure-only and `reporivet define` remains the lower-level resumable definition interface. Setup and init create no Plan, Plan runtime, scheduler, or hidden state. The Main Skill owns the handoff: it searches active and completed history, resumes exactly one matching active ordinary Markdown Plan, stops on ambiguity, or creates a new Plan from `_template.md` using the lowest unused current-year ID without overwriting an existing file. Reporivet does not create or close Plans automatically.

## When to use a Plan

Create or resume a matching Plan for cross-cutting, long-running, risky, public-contract, persistent-data, security, infrastructure, deployment, or multi-context work. A small, local, reversible edit may proceed without one when acceptance and evidence are obvious.

Before creating a Plan, inspect [`exec-plans/active/`](exec-plans/active/) and reuse the one substantive goal that already matches. Do not split one goal across multiple active records or use Plans as a backlog.

## Ownership and lifecycle

### Main

Main owns:

- original intent, observable outcome, scope, non-goals, and acceptance criteria;
- decomposition, task ordering, Task Packets, host-native dispatch instructions, and integration; Reporivet does not spawn or dispatch Agents;
- candidate identity and verification target;
- decisions, discoveries, documentation impact, follow-ups, and outcome;
- every shared Plan mutation and manual movement between Plan directories.

Main serializes Plan edits. Sub agents return evidence to Main rather than concurrently editing the shared Plan unless an unusually narrow packet grants one disjoint Plan section and Main still controls integration.

### Implementation Sub

An implementation Sub receives exactly one bounded Task Packet. It may read and write only the named scope, must preserve protected paths, runs the named project-owned checks, stops at stated conditions, and returns changed paths, evidence, discoveries, and residual risks. A default leaf may not broaden scope, change acceptance, delegate, move the Plan, or approve its own candidate. The only delegation exception is the explicitly bounded Task Owner role below.

### Verification Sub

A Verification Sub starts from a fresh context after integration. It identifies the integrated candidate, maps checks to acceptance criteria, runs applicable project-owned commands, inspects non-goals and protected paths, and returns accepted, failed, or not-established results plus residual risks. A default verification leaf does not delegate. It does not repair the candidate unless Main creates a separate implementation packet.

### Broad-milestone native-Agent dispatch

For every broad or multi-part root, the default packet is `Role: Task Owner` with `May delegate: yes`. Narrow or inherently serial roots remain direct nondelegating leaves. This is a host/project operating rule, not a Reporivet runtime:

`T<n> (broad root Owner) -> T<n>-A/B/C/... (declared child packets, all ready leaves dispatched concurrently) -> T<n>-I (Owner-local aggregation) -> T<n>-V1/V2/... (parallel fresh verification)`

Main dispatches independent root Owners concurrently. Each Owner first returns a finite child manifest within its approved envelope; Main alone serializes accepted child rows and complete matching packets into the Plan, freezes their boundaries, and resumes that serialized Owner. Only the resumed serialized Task Owner dispatches its own declared dependency-ready descendants through host-native Agent execution. Ordinary leaf Agents never delegate. A narrow or inherently serial root follows its declared direct, nondelegating path instead.

Every child row retains an explicit owner and matching bounded packet. Descendants inherit the parent's scope, acceptance, non-goals, protected paths, child budget, and frozen interfaces and cannot broaden them. Parallel mutable siblings require disjoint allowed-write sets and separate exact-baseline worktrees. Owner-local aggregation is distinct from Main's final repository integration; fresh verification nodes depend on the integrated candidate and are read-only, nonrepairing, and nondelegating.

Reporivet installs no scheduler, dispatcher, task store, lease, lock, command runner, Gate, evidence archive, automatic closure, hidden state, or other runtime for this workflow. It installs no Agent spawn/dispatch mechanism or project command execution engine; project commands and CI remain project/host-owned. The `task_graph: 1` marker opts a compact `format: 2` Plan into strict hierarchy checks; unmarked compact Plans retain structural validation, historical expanded or completed Plans remain untouched, recursive task IDs remain valid, and direct serial Plans remain supported.

## Minimum active Plan content

Each Plan has:

- frontmatter with identity, status, owner, area, dates, supersession links, and candidate hashes;
- one original goal and one observable outcome;
- explicit scope and non-goals;
- one task-state table;
- one matching Task Packet per task;
- one current checkpoint and one exact next action;
- concise decisions and discoveries;
- documentation impact;
- integration and verification summaries;
- bounded follow-ups;
- one terminal outcome.

Task state belongs in the single table. Every row retains `Task`, `Owner`, `State`, `Depends on`, `Outcome`, and `Result`; a visible `Parallel group` column may record concurrent siblings. Detailed work instructions belong in the matching packet. Do not add a second registry, packet directory, journal, event log, evidence archive, or hidden coordination state.

## Task Packet minimum

Every implementation or verification packet states:

- outcome;
- non-goals;
- exact reads;
- allowed writes;
- protected paths;
- acceptance criteria;
- project-owned verification commands;
- stop conditions;
- return evidence.

Packets should be self-contained enough for a fresh context but no broader than the assigned task. When broad-milestone decomposition exists, each packet also records `Role`, `Parent`, `Parallel group`, `May delegate`, inherited boundaries and write isolation, and its compact `Return`. An inherently single or serial milestone may omit those hierarchy-only fields.

## Ablation checkpoint

For each design or implementation change, Main or the applicable Task Owner follows the [`Ablation`](design-docs/core-beliefs.md#ablation) guidance and records the outcome and rechecked requirements and invariants in the active Plan before integration and fresh verification.

## States and lifecycle

Active states are:

- `proposed`
- `approved`
- `in-progress`
- `verifying`
- `blocked`

Terminal states are:

- `complete`
- `cancelled`
- `superseded`

Lifecycle:

1. Main Skill searches existing history and either resumes one matching active Plan or creates the first ordinary Markdown Plan in `docs/exec-plans/active/` with the lowest unused current-year ID; setup itself never creates it.
2. Main approves scope and acceptance before mutable work.
3. For each broad or multi-part root, Main dispatches independent root Owners concurrently. Each Owner returns a finite child manifest; Main serializes accepted child rows and complete matching packets into the Plan, then resumes the serialized Owner to dispatch its declared dependency-ready descendants. An inherently single or serial root remains a direct nondelegating leaf and follows its declared linear dependency order.
4. Owner-local child results converge on their declared aggregation node; Main separately integrates the accepted candidate and records `integrated_commit` or another exact identifier.
5. Fresh verification nodes that depend on that integrated candidate may run in parallel when their packets are read-only, nonrepairing, and nondelegating, and return criterion-level evidence.
6. Main records `verified_commit` when commit-based verification applies, resolves documentation impact and follow-ups, chooses the terminal outcome, and edits the status.
7. Main manually moves the terminal Plan to `docs/exec-plans/completed/`.

No command decides completion or moves a Plan automatically. A terminal state is justified only by accepted evidence, not by an agent's assertion.

## Completion

- `base_commit` identifies the comparison point when Git is used.
- `integrated_commit` identifies the exact implementation candidate presented for verification.
- `verified_commit` identifies the exact commit actually checked; it must match the accepted integrated candidate for commit-based completion.
- When verification occurs in an intentionally dirty tree, record another exact reproducible fingerprint and explain the limitation instead of inventing a commit.
- Record exact commands, results, criterion mapping, and residual risks in the verification summary.
- Mark unavailable or unrun evidence explicitly; never report it as passing.
- Main normally relies on the fresh verifier's detailed execution evidence rather than rerunning the same checks without cause.

## Parallel work

For every broad or multi-part root, Main dispatches independent root Owners together. Only a resumed serialized Task Owner dispatches its own complete dependency-ready descendant set. Inherently single or serial roots follow their declared linear order as direct nondelegating leaves. Read-only exploration, review, and verification lanes may run concurrently. Mutable siblings are dependency-ready for concurrent dispatch only when their packets have disjoint allowed-write sets, frozen shared interfaces, and separate exact-baseline worktrees; otherwise dependencies must serialize them. The Plan remains Main-serialized, Owner-local aggregation remains distinct from Main integration, and fresh verification depends on the integrated candidate.

## Documentation and history

Every Plan resolves Documentation Impact as changed, no change required, or follow-up with an owner and trigger. Completed Plans preserve what happened; do not rewrite their bodies to match later policy. Supersession metadata may point readers to the current successor without erasing history.

Out-of-scope discoveries go in [`exec-plans/tech-debt-tracker.md`](exec-plans/tech-debt-tracker.md) only when they are concrete and useful. That tracker is not an implementation queue and does not authorize work.

### Confirmed

- Current package checks recognize the compact `format: 2` headings and active/terminal state sets above.
- Plan files are ordinary Markdown and remain useful without the package installed.
- Main owns terminal movement and evidence judgment.

### Proposed

- None.

### Open

- None.

### Sources

- [`exec-plans/_template.md`](exec-plans/_template.md)
- [`product-specs/SPEC-REPORIVET-003-document-first-harness.md`](product-specs/SPEC-REPORIVET-003-document-first-harness.md)
- [`design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](design-docs/DESIGN-REPORIVET-003-document-first-harness.md)
