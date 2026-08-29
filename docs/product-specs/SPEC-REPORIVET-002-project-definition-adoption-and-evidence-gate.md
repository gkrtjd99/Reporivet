---
id: SPEC-REPORIVET-002
kind: product-spec
status: active
area: harness
summary: Repository-native definition, adoption, traceability, verification, Gate, and migration behavior
applies_to:
  - "src/reporivet/**"
  - "dev/**"
  - "docs/**"
supersedes: []
---

# Project definition, adoption, and evidence Gate

## Confirmed traceability

### Confirmed

- [confirmed] JRN-001 | A maintainer starts or resumes project definition from persisted repository evidence.
- [confirmed] JRN-002 | A maintainer audits and adopts an existing repository without replacing its authority.
- [confirmed] JRN-003 | A maintainer follows a requirement from product intent through criterion-level verification evidence.
- [confirmed] JRN-004 | An agent loads only the durable module and path context needed for its bounded task.
- [confirmed] JRN-005 | A maintainer uses the generated repository harness after removing the installed Reporivet package.
- [confirmed] JRN-006 | A maintainer runs one canonical verification and inspects its preserved structured evidence.
- [confirmed] JRN-007 | A maintainer evaluates changed-path risk and receives a conservative Gate verdict.
- [confirmed] JRN-008 | A maintainer closes a plan only against evidence bound to the verified commit.
- [confirmed] JRN-009 | CI verifies an explicit candidate and preserves its evidence on success or failure.
- [confirmed] JRN-010 | A maintainer migrates durable HarnessEngineeringSkill capabilities into Reporivet without external retirement actions.

- [confirmed] REQ-P0-001 | Journey: JRN-001 | Acceptance: AC-1, AC-2 | Provide explicit, resumable project definition with separated evidence states.
- [confirmed] REQ-P0-002 | Journey: JRN-002 | Acceptance: AC-3 | Provide deterministic read-only audit and authority-preserving adoption.
- [confirmed] REQ-P0-003 | Journey: JRN-003 | Acceptance: AC-4 | Preserve stable product-to-plan-to-task-to-evidence traceability.
- [confirmed] REQ-P0-004 | Journey: JRN-004 | Acceptance: AC-5 | Route context through justified module contracts and an actual-path code map.
- [confirmed] REQ-P0-005 | Journey: JRN-005 | Acceptance: AC-6, AC-14 | Keep generated runtime behavior independent and regression-tested.
- [confirmed] REQ-P0-006 | Journey: JRN-006 | Acceptance: AC-7, AC-8, AC-9 | Produce one Verification Run with deterministic status and artifacts.
- [confirmed] REQ-P0-007 | Journey: JRN-007 | Acceptance: AC-10, AC-11 | Produce conservative risk verdicts with shadow and enforce behavior.
- [confirmed] REQ-P0-008 | Journey: JRN-008 | Acceptance: AC-12 | Bind plan closure to one verified clean commit and its Gate evidence.
- [confirmed] REQ-P0-009 | Journey: JRN-009 | Acceptance: AC-13 | Preserve explicit target evidence and run artifacts in CI.
- [confirmed] REQ-P0-010 | Journey: JRN-010 | Acceptance: AC-15 | Record migration and logical retirement readiness without external writes.

- [confirmed] AC-1 | P0: REQ-P0-001 | Journey: JRN-001 | A blank repository can start, persist, and resume structured definition without repeating confirmed sections.
- [confirmed] AC-2 | P0: REQ-P0-001 | Journey: JRN-001 | Strict definition validation separates Confirmed, Proposed, and Open evidence and rejects unresolved or contradictory input.
- [confirmed] AC-3 | P0: REQ-P0-002 | Journey: JRN-002 | Audit is deterministic and read-only, and adoption preserves existing authority while leaving unverified commands in review.
- [confirmed] AC-4 | P0: REQ-P0-003 | Journey: JRN-003 | Confirmed P0 requirements, journeys, acceptance criteria, plan tasks, evidence paths, and verified commits form a validated chain.
- [confirmed] AC-5 | P0: REQ-P0-004 | Journey: JRN-004 | Only justified module contracts and actual, configured, or confirmed planned paths drive deterministic context routing.
- [confirmed] AC-6 | P0: REQ-P0-005 | Journey: JRN-005 | Repository-local definition, audit, context, planning, checks, verification, closure, and gardening work without the installed package.
- [confirmed] AC-7 | P0: REQ-P0-006 | Journey: JRN-006 | One canonical verify invocation creates exactly one shared Verification Run directory.
- [confirmed] AC-8 | P0: REQ-P0-006 | Journey: JRN-006 | Success, candidate failure, and infrastructure error preserve deterministic manifest, Gate, report, check, and available log artifacts.
- [confirmed] AC-9 | P0: REQ-P0-006 | Journey: JRN-006 | Checks use the declared statuses and required failure or error determines verification status without silent skips.
- [confirmed] AC-10 | P0: REQ-P0-007 | Journey: JRN-007 | Explicit local target and changed-path evidence produce conservative risk, protected-path matches, and Gate verdicts.
- [confirmed] AC-11 | P0: REQ-P0-007 | Journey: JRN-007 | Shadow and enforce modes apply the declared exit semantics without overriding BLOCK or INCONCLUSIVE.
- [confirmed] AC-12 | P0: REQ-P0-008 | Journey: JRN-008 | Plan closure records one run, manifest hash, verdict, verified SHA, criterion evidence, and an explicit REVIEW reason when required.
- [confirmed] AC-13 | P0: REQ-P0-009 | Journey: JRN-009 | CI verifies the explicit head with explicit base evidence and always preserves the resulting run artifacts.
- [confirmed] AC-14 | P0: REQ-P0-005 | Journey: JRN-005 | Greenfield, adoption, traceability, Gate, packaging, generated-project, and package-removal scenarios pass deterministically without network or model evaluation.
- [confirmed] AC-15 | P0: REQ-P0-010 | Journey: JRN-010 | Reporivet records the pinned migration source, capability disposition, replacement interfaces, discarded surfaces, and remaining limits without backup, archive, deprecation write, or deletion.

### Proposed

- None.

### Open

- None.

## Non-goals

- External repository writes, backup, archive, or deletion.
- Model-based judging, agent execution infrastructure, plugins, daemons, or production dependencies.
- Rewriting completed plans or project-owned authority during adoption or upgrade.
