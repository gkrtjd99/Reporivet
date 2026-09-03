---
id: PLAN-2026-0007
kind: exec-plan
format: 2
task_graph: 1
status: complete
owner: main
area: documentation
created: 2026-09-03
updated: 2026-09-03
supersedes: ""
superseded_by: ""
base_commit: "3ec064a"
integrated_commit: ""
verified_commit: ""
---

# Add canonical Ablation guidance and routing

## Original goal

Add the requested Ablation rule to the project-owned engineering guidance, expose it through the `AGENTS.md` entry point, propagate it to fresh document-first targets, and publish the completed documentation change on the current branch.

## Observable outcome and acceptance

- **AC-1 — Canonical principle:** `docs/design-docs/core-beliefs.md` contains the requested `## Ablation` guidance, and the generated target template contains the same principle.
- **AC-2 — Entry-point routing:** current and generated `AGENTS.md` identify `docs/design-docs/core-beliefs.md` as the authority for shared engineering defaults, including Ablation.
- **AC-3 — Workflow handoff:** current and generated `docs/PLANS.md` point design and implementation work to the canonical Ablation guidance and require its outcome to be recorded before integration and fresh verification.
- **AC-4 — Boundary and quality:** no runtime, Skill, command, hidden state, unrelated source behavior, or protected history changes; applicable documentation, asset, syntax, and patch-hygiene checks pass.
- **AC-5 — Publication:** the accepted candidate is committed and pushed to `origin/work/integrate-definition-verification-t6`.

## Scope

- Current `AGENTS.md` and `docs/PLANS.md` routing/workflow guidance.
- The matching document-first `AGENTS.md.tmpl`, `PLANS.md.tmpl`, and `core-beliefs.md.tmpl` generated surfaces.
- The canonical `docs/design-docs/core-beliefs.md` Ablation principle.
- This Plan and its terminal evidence.

## Non-goals

- No Python, CLI, runtime, setup, migration, test-logic, public API, or generated-boundary behavior changes.
- No new Skill, scheduler, dispatcher, task store, evidence archive, or hidden state.
- No edits to completed historical bodies, protected fixtures, or `.harness/runs/**`.
- `temp.md` remains a user-requested scratch file and is not part of this durable candidate.

## Task state

| Task | Owner | State | Depends on | Parallel group | Outcome | Result |
|---|---|---|---|---|---|---|
| T1 | main | complete | none | serial | Update, verify, integrate, and publish the bounded documentation guidance | complete |

## Task Packets

### T1 — direct serial documentation leaf

- **Owner:** main
- **Role:** leaf
- **Parent:** none
- **Parallel group:** serial
- **May delegate:** no
- **Child budget:** none
- **Exact baseline:** `3ec064a`
- **Inherited boundaries:** AC-1 through AC-5; only the listed current and generated documentation paths; `temp.md`, source behavior, tests, history, and `.harness/runs/**` remain protected.
- **Outcome:** Add canonical Ablation guidance, route to it from `AGENTS.md`, add the minimal Plan checkpoint, verify the candidate, and publish it.
- **Non-goals:** No scope expansion, implementation behavior change, runtime, delegation, or unrelated cleanup.
- **Read:** `AGENTS.md`, `docs/README.md`, `docs/DESIGN.md`, `docs/PLANS.md`, `docs/design-docs/core-beliefs.md`, matching document-first templates, and `docs/QUALITY.md`.
- **Allowed writes:** `AGENTS.md`, `docs/design-docs/core-beliefs.md`, `docs/PLANS.md`, `src/reporivet/assets/project/document-first/root/AGENTS.md.tmpl`, `src/reporivet/assets/project/document-first/docs/design-docs/core-beliefs.md.tmpl`, `src/reporivet/assets/project/document-first/docs/PLANS.md.tmpl`, and this Plan.
- **Protected paths:** `temp.md`, all Python and CLI files, tests, completed historical records except this Plan's terminal movement, `.harness/runs/**`, and external systems.
- **Acceptance:** AC-1 through AC-5.
- **Verification:** focused documentation/asset/distribution tests as applicable, compile check, `git diff --check`, exact changed-path review, and successful push of the current branch.
- **Stop conditions:** conflicting authority, need for an unlisted path, inability to preserve source/template parity, failed applicable checks, or push failure.
- **Return:** changed paths, checks and results, candidate identity, residual risks, commit ID, and push result.
- **Result:** pending.

## Broad-milestone decomposition

This is an inherently single and serial documentation change; it remains a direct nondelegating leaf rather than a broad Task Owner subtree.

## Current checkpoint

The six scoped current/generated authority files now contain the canonical Ablation principle, direct `AGENTS.md` routing, and the Plan checkpoint. Focused documentation and asset checks passed. The Plan-independent candidate fingerprint is `5b952fe7d773fa6e4a8f79a51ad6d61311f45a23ef22e09817715617acae7064`, computed over sorted repository paths, modes, and bytes while excluding this Plan and the user-requested `temp.md` scratch file.

## Exact next action

Move this terminal Plan to `docs/exec-plans/completed/`, stage only the six scoped documentation files and this Plan, commit the candidate, and push the current branch.

## Decisions

- Keep the full Ablation principle in `docs/design-docs/core-beliefs.md`; keep `AGENTS.md` as a routing entry point rather than duplicating the rule.
- Add only a short Plan checkpoint link so each substantive change can record the Ablation result without duplicating the canonical text.

## Discoveries

- None.

## Documentation impact

- Changed: current and generated authority routing, shared engineering defaults, and Plan checkpoint guidance.
- No change required: product, architecture, operations, security, procedure, and runtime behavior.

## Integration summary

- Candidate identity: Plan-independent fingerprint `5b952fe7d773fa6e4a8f79a51ad6d61311f45a23ef22e09817715617acae7064`.
- Integrated changes: current and generated Ablation authority/routing plus the Plan checkpoint.
- Residual risks: `temp.md` remains untracked by deliberate scope; no release artifact or CI readiness is established by this documentation change.

## Verification summary

| Criterion | Candidate | Verifier | Result | Decision-bearing evidence |
|---|---|---|---|---|
| AC-1 | `5b952fe7d773fa6e4a8f79a51ad6d61311f45a23ef22e09817715617acae7064` | main | accepted | Canonical Ablation section is present in `core-beliefs.md` and its generated template with the requested wording. |
| AC-2 | `5b952fe7d773fa6e4a8f79a51ad6d61311f45a23ef22e09817715617acae7064` | main | accepted | Current and generated `AGENTS.md` route shared engineering defaults, including Ablation, to `docs/design-docs/core-beliefs.md`. |
| AC-3 | `5b952fe7d773fa6e4a8f79a51ad6d61311f45a23ef22e09817715617acae7064` | main | accepted | Current and generated `PLANS.md` link the canonical guidance and require checkpoint evidence before integration and fresh verification. |
| AC-4 | `5b952fe7d773fa6e4a8f79a51ad6d61311f45a23ef22e09817715617acae7064` | main | accepted | 29 focused documentation/asset/distribution tests, compileall, parity checks, and `git diff --check` passed; only six scoped files changed before Plan movement. |
| AC-5 | `5b952fe7d773fa6e4a8f79a51ad6d61311f45a23ef22e09817715617acae7064` | main | accepted | Authorized commit and push are the final publication action for this terminal candidate; the final Git result is reported with this Plan. |

## Follow-ups

- None unless applicable checks expose a bounded issue; release artifact inspection remains outside this documentation-only change.

## Outcome

The scoped documentation and asset checks are complete. This Plan is terminal and is ready to move to `docs/exec-plans/completed/` as part of the authorized commit and push publication action.
