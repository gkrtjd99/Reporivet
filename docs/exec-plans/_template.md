---
id: {{PLAN_ID}}
kind: exec-plan
status: proposed
owner: {{OWNER}}
area: {{AREA}}
created: {{DATE}}
updated: {{DATE}}
base_commit: "{{BASE_COMMIT}}"
---

# {{PLAN_TITLE}}

Copy this template manually for a source plan; it is not generated target output.

## Purpose / Big Picture

TODO: explain what becomes observably possible and how a person or agent can confirm it.

## Current Contract

Record the authoritative contract before implementation:
- Authoritative source and revision.
- Scope and non-goals.
- Acceptance criteria.
- Allowed writes and protected paths.
- Constraints and prohibitions.

Keep this section authoritative and separate from the changing Progress summary. When resuming work, after context compression, or when instructions change, recheck this section.

## Progress

- [ ] Establish current behavior and constraints.
- [ ] Deliver the smallest working milestone.
- [ ] Run verification and resolve issues.
- [ ] Resolve documentation impact and follow-ups.

## Context and Orientation

TODO: explain relevant repository paths, modules, terms, current behavior, and authoritative documents for a reader with no prior context.

## Scope

- TODO

## Non-goals

- TODO

## Acceptance Criteria

- **AC-1:** TODO observable behavior or evidence.

## Approach and Key Changes

TODO: outline the design direction, invariants, failure paths, and specific files to modify.

## Milestones

### M1 — Smallest observable slice

TODO: state the working behavior, implementation outline, and verification.

## Architecture Impact

TODO: affected modules, dependency edges, invariants, and required machine checks; write `none` with a reason when there is no impact.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| `docs/PRODUCT.md` | TODO: none/create/update/supersede/retire | TODO | TODO | pending |
| `ARCHITECTURE.md` | TODO | TODO | TODO | pending |

## Migration, Rollout, and Recovery

TODO: record compatibility, rollout, rollback, retry, idempotency, and cleanup requirements; write `not applicable` with a reason where appropriate.

## Surprises and Discoveries

- {{DATE}} — Plan created; no discoveries recorded yet.

## Decision Log

- {{DATE}} — Initial scope proposed; approval pending.

## Concrete Steps

1. Read current sources and the matching active plan.
2. TODO implementation step.
3. Run verification commands.

## Validation and Evidence

Criteria are judged as `PASS`, `FAIL`, or `UNPROVEN`. Before execution, all are `UNPROVEN`.

| Acceptance criterion | Result | Evidence path or note | Verified candidate | Human/reviewer approval |
|---|---|---|---|---|
| AC-1 | UNPROVEN | pending | pending | pending |

- Verified candidate: pending (commit SHA or base commit + hashes/modes)
- Commands and results: pending

## Outcomes and Retrospective

TODO: summarize delivered behavior, remaining limits, and lessons learned.

## Follow-ups

Promote unresolved items to [`tech-debt-tracker.md`](tech-debt-tracker.md) or the declared external backlog before completion.

- none yet
