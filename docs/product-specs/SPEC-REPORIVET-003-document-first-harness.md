---
id: SPEC-REPORIVET-003
kind: product-spec
status: superseded
area: harness
summary: Document-first host-neutral Agent harness and reversible 0.2 migration
applies_to:
  - "src/reporivet/**"
  - "src/reporivet/assets/project/**"
  - "AGENTS.md"
  - "CLAUDE.md"
  - ".claude/**"
  - "docs/**"
supersedes:
  - SPEC-REPORIVET-001
  - SPEC-REPORIVET-002
---

# Document-first Agent harness

## Contract status and boundary

This is the current approved product contract for the document-first Reporivet boundary. Source behavior through the previously verified document-first implementation exists. The historical candidate identified by `f793567262ca66f11016aa198ddc46ec207eb23fbe91b234bf72a91348344293` passed AC-1 through AC-10 and AC-12; AC-11 wheel/install evidence remained unknown, and that historical result is not evidence for a later integrated product candidate. Completed [`PLAN-2026-0003`](../exec-plans/completed/PLAN-2026-0003-document-first-harness.md) records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive. Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside scope. The corresponding design is [`DESIGN-REPORIVET-003`](../design-docs/DESIGN-REPORIVET-003-document-first-harness.md), and the architectural decision is [`ADR-0001`](../decisions/ADR-0001-document-first-product-boundary.md).

The default onboarding command is integrated `reporivet setup`. `reporivet init` remains structure-only, and lower-level `reporivet define` remains available. Setup coordinates package-side audit, visible guided definition, exact preview, and approved apply; it does not create a Plan or target runtime, spawn or dispatch Agents, execute project commands, or operate CI/deployment. Durable authority is readable Markdown and project-owned Git history. The Main Skill creates or resumes the first ordinary Markdown Plan. A complete user-confirmed structured procedure may create an instruction-only project Skill through resumed setup; incomplete, inferred, generic, Proposed, Open, and Sources-only records create none. Reporivet does not promise a maintenance command after the package is removed.

## Canonical entry and optional host adapters

- `AGENTS.md` is the canonical, host-neutral entry point. It tells Main, implementation Sub-Agents, and Verification Sub-Agents which authority documents to read, how to resume the active Plan, and where project-owned commands and CI live.
- `docs/README.md` is the generated knowledge map. It explains every generated path, its owner, purpose, optionality, and removal boundary without becoming a second operating authority.
- `CLAUDE.md` is an optional thin Claude Code adapter that points to `AGENTS.md`; it must not duplicate or override the canonical instructions.
- Claude is the first supported host profile. Optional Claude Skills and settings route Claude to the same documents and role procedures. They are not required for the repository to remain useful, are instruction-only/least-privilege, and must be explicitly previewed and ownership-safe.
- No host adapter may create a competing authority, silently enable privileged behavior, or make the installed Reporivet package a runtime dependency.
- The default onboarding route is integrated `reporivet setup`; `reporivet init` is structure-only and `reporivet define` is the lower-level resumable interface. Setup creates no Plan or runtime; the Main Skill owns first-Plan creation/resume.

## Authority documents and operations

A fresh project receives a rich, navigable authority set appropriate to its profile. It includes the knowledge map and the project-owned product, design, quality, security, planning, decision, reference, and execution-plan surfaces. The exact generated bundle is documented by `docs/README.md` rather than hidden in an executor.

`docs/OPERATIONS.md` is the single current operations authority. It covers the project's run, release, observe, backup, rollback, and recovery procedures. A fresh project does not receive a second current `RELIABILITY.md` authority. Existing project-owned operations or reliability documents are not silently overwritten or deleted during adoption or migration; any retirement is explicit and ownership-aware.

## Guided definition and evidence states

The default `reporivet setup` flow is guided, deterministic, and evidence-preserving; lower-level `reporivet define` remains compatible for direct draft work:

1. A read-only scan inventories relevant instructions, authority documents, manifests, commands, CI, source/test signals, and possible conflicts without executing project commands or following symlinks.
2. An interview presents the consequential questions and records provenance. It does not ask the user to choose canonical document filenames.
3. A visible draft is resumed across the seven topics and reports actual Open items; a complete structured procedure is eligible for a Skill only after user confirmation.
4. A preview identifies proposed additions, ownership classifications, unresolved decisions, and any procedure Skill targets before writing.
5. After explicit approval, canonical documents, optional adapters, and only eligible instruction-only procedure Skills are created where ownership permits. Setup creates no Plan; the Main Skill performs first-Plan handoff.

Every definition section keeps these states visibly separate and in this order:

- **Confirmed** — evidence or a user decision accepted as current; only this state can satisfy a product traceability link.
- **Proposed** — a visible hypothesis for review; it never becomes Confirmed by inference or by generation.
- **Open** — unresolved work or a question, including whether it blocks handoff; it remains visible until resolved.
- **Sources** — provenance for the preceding content; a source does not itself imply confirmation.

Adoption preserves existing authority and adds only missing responsibilities. Inferred commands remain review-state until a project owner confirms them. Ambiguous, customized, unmarked, symlinked, or nonregular paths are preserved or refused rather than silently replaced.

## Durable minimal Plans and Agent responsibilities

One substantive goal maps to one active ordinary Markdown Plan. Setup and init create no Plan. The Main Skill searches active and completed history, resumes one matching active Plan, stops on ambiguity, or creates the first Plan with the lowest unused current-year ID from the project template. A Plan contains, at minimum, the goal, observable acceptance criteria, task state and dependencies, current checkpoint, exact next action, decisions, discoveries, and compact integration/verification evidence. For every broad or multi-part root, the default packet is `Role: Task Owner` with `May delegate: yes`; narrow or inherently serial roots remain direct nondelegating leaves:

`T<n> (broad root Owner) -> T<n>-A/B/C/... (declared child packets, all ready leaves dispatched concurrently) -> T<n>-I (Owner-local aggregation) -> T<n>-V1/V2/... (parallel fresh verification)`

Main dispatches independent root Owners concurrently. Each Owner first returns a finite child manifest within its approved envelope; Main alone serializes accepted child rows and complete matching packets into the Plan and resumes that serialized Owner. Only the resumed serialized Task Owner dispatches its own declared dependency-ready descendants using the host's native Agent execution; ordinary leaf Agents never delegate. Every child row retains Owner, State, Depends on, Outcome, and Result and has one matching owner-bearing packet. The active Plan is the durable resume point; terminal Plans move to `completed/` with an explicit outcome such as complete, cancelled, or superseded. Main owns the overall tree and alone serializes Plan mutations. The `task_graph: 1` marker opts a compact `format: 2` Plan into strict hierarchy checks; unmarked compact Plans retain structural validation, historical expanded or completed Plans remain untouched, recursive task IDs remain valid, and direct serial Plans remain supported.

Execution is Sub-Agent-first and uses only the host's native Agent execution:

- **Main** owns intent, scope, acceptance, decomposition, root-owner dispatch, integration order, Plan updates, and the judgment that returned evidence satisfies the contract.
- **Task Owners and implementation leaves** receive bounded Task Packets, change only assigned project/package paths, and run the smallest applicable project-owned commands. Descendants inherit the parent's scope, protected paths, acceptance, non-goals, child budget, and frozen interfaces and cannot broaden them.
- **Verification leaves** use a fresh context, independently inspect the integrated candidate, run applicable project-owned verification or CI-equivalent commands, and return criterion-level evidence and residual risks. Read-only verification leaves may run in parallel, never delegate, and depend on the integrated candidate; they do not repair it.

Concurrent mutable siblings require disjoint allowed-write sets, frozen shared interfaces, and separate exact-baseline worktrees. Owner-local aggregation is distinct from Main's final repository integration; fresh verification follows that integrated candidate. Reporivet installs no scheduler, dispatcher, task store, lease, lock, command runner, automatic dispatcher, copied executor, Gate, evidence archive, hidden state, or automatic Plan-closure process for this lifecycle.

## Project-owned commands and CI

The project owns its command definitions, test/verification tools, CI workflows, deployment procedures, secret handling, and operational policies. Reporivet may describe these surfaces during setup and preserve them during adoption, but it does not execute project commands, spawn or dispatch Agents, generate command wrappers, a `dev` configuration, a replacement command runner, or generated CI as part of the document-first target. Project CI may invoke project-owned commands and may be retained or deliberately changed by the project; it is not Reporivet-owned.

After package removal, generated Markdown, ordinary Plans, Skills if installed, Git, and project commands remain useful. Only package-side maintenance capability disappears. No package-independent Reporivet command, copied runtime, command runner, CI/deployment engine, Gate, evidence archive, hidden state, or automatic close-plan mechanism is promised.

## Retained and retired boundary

The document-first contract retains:

- deterministic, read-only audit and safe ownership classification during package-side setup and migration preview;
- Confirmed, Proposed, Open, and Sources evidence states with visible provenance;
- rich authority documents, decisions, references, and durable Markdown Plans;
- explicit project-owned commands, CI, and operations authority; and
- historical plans and legacy evidence as readable project history, including existing `.harness/runs/`, without creating new run artifacts.

It retires from newly generated repositories:

- the copied repository-local runtime and `harness.py`;
- shell wrappers, `dev/harness.toml`, and package-independent Reporivet command groups;
- Verification Runs, Gate policy, evidence archives, and automatic evidence-bound Plan closure;
- generated CI and Reporivet-owned command configuration;
- `context`, generated `code-map`, and `garden` execution surfaces; and
- any copied executor that continues operating after the installed package is removed.

Retirement of these generated surfaces does not authorize deletion of project-owned files or historical evidence. Legacy material is retained for readability unless the explicit migration authorizes a proven-owned retirement action.

## Installation channel and artifact boundary

Public installation guidance is pipx-primary, with pip supported from the same wheel:

```bash
pipx install reporivet
python -m pip install reporivet
```

These commands describe the supported user channels, not standalone lifecycle evidence. Completed [`PLAN-2026-0003`](../exec-plans/completed/PLAN-2026-0003-document-first-harness.md) records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive. Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside scope. Reporivet does not publish, sign, or release packages.

## Explicit reversible 0.2 migration

Ordinary upgrade refuses to perform the 0.2 retirement. A separate migration must:

1. produce a deterministic preview with an input fingerprint, ownership classification, proposed writes/removals, preserved paths, conflicts, and unresolved blockers;
2. require a human to inspect and approve that preview while the target fingerprint is unchanged;
3. create an external, visible backup before any destructive action, with a manifest and checksums that identify its location and contents;
4. preserve project-owned, customized, ambiguous, historical, symlinked, and nonregular paths, and modify or remove only proven Reporivet-managed legacy surfaces;
5. record ownership and backup information so a failed apply can automatically restore the exact pre-migration state when safe; and
6. provide an explicit post-success rollback that refuses to overwrite changes made after migration and otherwise restores the backed-up state.

The migration must preserve existing Plans and `.harness/runs/` as history, must not treat a marker alone as permission to delete, and must expose refusal reasons rather than guessing. Preview, approval, external backup, ownership preservation, and rollback are product requirements, not optional implementation details.

## Observable acceptance

A conforming implementation lets a person:

- inspect `AGENTS.md` and `docs/README.md` and route Main, implementation, and verification work without a hidden runtime;
- use integrated `reporivet setup` as the default onboarding path, retain structure-only `init`, and use lower-level `define` when needed;
- distinguish current authority, optional Claude adapters, complete-procedure Skills/settings, project commands/CI, and durable Plans by ownership;
- complete guided setup while seeing Confirmed, Proposed, Open, and Sources separately and actual Open items;
- generate a procedure Skill only from a complete user-confirmed structured record through resumed setup, with no execution;
- have the Main Skill resume or create the first ordinary Markdown Plan while setup itself creates no Plan;
- resume one active Plan and obtain independent Sub-Agent implementation and verification evidence through the host/project workflow;
- remove the installed package without losing generated Markdown, Plans, Skills, Git, or project-command usefulness; and
- preview, approve, back up, apply, and roll back a 0.2 migration without deleting ambiguous or project-owned content.

Fresh-install, package-removal, guided-setup, ownership, migration, rollback, productization, and distribution verification are implemented and recorded by completed [`PLAN-2026-0003`](../exec-plans/completed/PLAN-2026-0003-document-first-harness.md). Historical verification of the prior document-first candidate passed AC-1 through AC-10 and AC-12, but that result is not evidence for the integrated product candidate or its wheel. The current candidate and exact-wheel lifecycle are recorded above; the verification artifacts are temporary and are not a durable or downloadable evidence archive. Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside scope.

## Non-goals

This boundary does not add Agent spawn/dispatch, a scheduler, daemon, task database, plugin runtime, MCP bridge, model judge, project command runner, CI platform, deployment engine, secret scanner, Gate, evidence archive, hidden state, automatic closure, publication, signing, release automation, or compatibility wrappers for retired command paths. It does not make semantic product decisions from repository inference, and it does not include non-Claude host adapters in the current scope.
