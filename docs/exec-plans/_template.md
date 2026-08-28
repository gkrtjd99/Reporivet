---
id: {{PLAN_ID}}
kind: exec-plan
status: proposed
owner: main
area: {{AREA}}
created: {{DATE}}
updated: {{DATE}}
base_commit: "{{BASE_COMMIT}}"
integrated_commit: ""
verified_commit: ""
---

# {{PLAN_TITLE}}

## Purpose / Big Picture

TODO: explain what becomes observably possible and how a person or agent can confirm it.

## Progress

- [ ] Establish current behavior and constraints.
- [ ] Deliver the smallest working milestone.
- [ ] Integrate and independently verify the candidate.
- [ ] Resolve documentation impact and follow-ups.

## Context and Orientation

TODO: explain relevant repository paths, modules, terms, current behavior, and authoritative documents for a reader with no chat history.

## Scope

- TODO

## Non-goals

- TODO

## Acceptance Criteria

- **AC-1:** TODO

## Milestones

### M1 — Smallest observable slice

TODO: state the working behavior, implementation outline, and verification. Later milestones build on a repository that already works.

## Task Packets

### T1 — Explore and establish the change boundary

#### State

ready

#### Depends on

none

#### Outcome

TODO

#### Non-goals

TODO

#### Read

TODO: exact documents and paths.

#### Allowed writes

Plan result only; no implementation writes unless Main expands this packet.

#### Protected paths

Everything not explicitly allowed.

#### Acceptance

AC-1

#### Verify

`./dev/context --plan {{PLAN_ID}}` and task-specific read-only checks.

#### Stop conditions

Conflicting sources, public-contract or data-migration impact, missing authority, or scope expansion.

#### Result

TODO: status, findings, evidence, proposed boundary, risks, and exact follow-ups.

### T2 — Implement the smallest working slice

#### State

blocked

#### Depends on

T1

#### Outcome

TODO

#### Non-goals

TODO

#### Read

TODO

#### Allowed writes

TODO

#### Protected paths

All paths outside Allowed writes.

#### Acceptance

AC-1

#### Verify

`./dev/check` and task-specific tests.

#### Stop conditions

Allowed writes are insufficient, acceptance must change, a protected contract changes, or the same approach fails twice.

#### Result

TODO: status, changed files, commit, acceptance results, commands and results, risks, and documentation proposal.

### T3 — Independently verify the integrated candidate

#### State

blocked

#### Depends on

T2

#### Outcome

Judge the integrated candidate against observable acceptance without relying on implementer explanation.

#### Non-goals

Redesign or unrelated cleanup.

#### Read

This plan, changed code, tests, and current-state documents.

#### Allowed writes

Verifier evidence only unless Main assigns a repair.

#### Protected paths

Implementation and acceptance criteria.

#### Acceptance

All criteria in this plan.

#### Verify

`./dev/verify` plus declared smoke or reproduction commands.

#### Stop conditions

The candidate commit differs from the integrated target, evidence is unavailable, or requirements conflict.

#### Result

TODO: verified target, criterion-by-criterion pass/fail, commands, observable evidence, residual risks, and recommendation.

## Architecture Impact

TODO: affected modules, dependency edges, invariants, and required machine checks; write `none` with a reason when there is no impact.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| `docs/PRODUCT.md` | TODO: none/create/update/supersede/retire/generate | TODO | Main | pending |
| `ARCHITECTURE.md` | TODO | TODO | Main | pending |

## Interfaces and Dependencies

- Existing project capability inspected: TODO
- New production dependency: none / TODO
- Public or cross-repository contract impact: none / TODO

## Migration, Rollout, and Recovery

TODO: record data migration, compatibility, rollout, rollback, retry, idempotency, and cleanup requirements; write `not applicable` with a reason where appropriate.

## Surprises and Discoveries

- {{DATE}} — Plan created; no discoveries recorded yet.

## Decision Log

- {{DATE}} — Initial scope proposed by Main; approval pending.

## Concrete Steps

Run commands from the repository root. Keep this section current and copy only durable summaries into Validation and Evidence.

1. `./dev/context --plan {{PLAN_ID}}`
2. TODO
3. `./dev/check`
4. `./dev/verify`

## Validation and Evidence

- Integrated target: pending
- Verified commit: pending
- Acceptance results: pending
- Commands and durable summaries: pending
- Raw logs: `.harness/runs/` and not committed

## Outcomes and Retrospective

TODO: summarize delivered behavior, remaining limits, and what should become a reusable rule, test, tool, or document.

## Follow-ups

Promote unresolved items to [`tech-debt-tracker.md`](/docs/exec-plans/tech-debt-tracker.md) or the declared external backlog before completion.

- none yet
