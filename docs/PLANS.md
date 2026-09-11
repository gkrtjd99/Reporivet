# Source ExecPlan Policy

ExecPlans are source-repository documents for complex work. They are manually copied from [`exec-plans/_template.md`](exec-plans/_template.md), version-controlled, and readable without chat history. They are not a generated target schema or an automatic completion system.

## When a plan is required

Create a plan for cross-cutting, risky, long-running, public-contract, persistent-data, authentication, authorization, payment, infrastructure, deployment, or difficult-to-verify changes. Small, local, reversible work may proceed without a durable plan until its scope expands.

## Required properties

A plan records purpose, scope, non-goals, acceptance criteria, current authority, approach, progress, discoveries, decisions, verification commands and results, documentation impact, recovery, and follow-ups.

## Current contract and progress

The plan must keep a **Current Contract** separate from **Progress**:
- **Current Contract** contains the authoritative source and revision, scope, non-goals, acceptance criteria, protected paths, and constraints.
- **Progress** records transient state, candidate, completed steps, and unresolved work. A status summary never replaces the current contract.

When resuming paused work, after context compression, or when instructions or requirements change, recheck the authoritative contract and plan before proceeding. If requirements conflict or scope expands, stop and resolve the conflict rather than proceeding silently.

## Stop and escalate before

- changing public APIs, persisted data, authentication, authorization, payments, infrastructure, or production deployment;
- adding or replacing a production dependency;
- writing outside the assigned scope or protected paths;
- weakening an acceptance test merely to make an implementation pass;
- rewriting unrelated code or formatting the repository broadly;
- continuing after the same approach has failed twice.

## Verification and evidence

Verification records the exact candidate (commit SHA or base commit with nonignored file hashes/modes and deletion list), commands run, exit status, and relevant output.

Criteria are judged using three states:
- `PASS`: verified by evidence.
- `FAIL`: violated or required behavior missing.
- `UNPROVEN`: insufficient evidence to confirm.

Do not convert `UNPROVEN` to `PASS` based on intent, assumption, or passing unrelated checks. If a required acceptance criterion is `FAIL` or `UNPROVEN`, completion cannot be approved. Final acceptance authority remains with the user or reviewer.

When defects are found, record the root cause, failing evidence, affected criteria, fix, and re-verification result.

## Recovery and completion

- Use actual repository and project-owned checks.
- There is no automatic Gate, Verification Run, `close-plan` command, run directory, or generated closure record. A plan is completed manually after acceptance criteria, documentation impact, verification, and follow-ups are resolved.
- Historical completed plans and accepted decisions remain unchanged; current documents supersede them explicitly.
- An agent saying “done” is not completion evidence.

## Non-goals

ExecPlans do not authorize an external task service, daemon, model judge, backup, archive, deletion, publication, deployment, or old-repository operation unless explicitly granted.
