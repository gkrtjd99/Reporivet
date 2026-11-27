# Source ExecPlan Policy

ExecPlans are version-controlled source records for work that needs a durable plan; they are not a target-project schema or an automatic completion system. The [template](exec-plans/_template.md) is a starting point, not a required collection of headings.

## When a plan is required

Use a plan for cross-cutting, risky, long-running, public-contract, persistent-data, authentication, authorization, payment, infrastructure, deployment, or difficult-to-verify changes. Small, local, reversible work may proceed without a durable plan until its scope expands.

A narrow change that still needs a plan may use a short record. Record only the context needed to do and review that work; combine related items and omit inapplicable sections rather than filling them with `N/A`. Larger or uncertain work can add detail as needed. Keep a single record of each fact or link to existing evidence rather than copying it into multiple places.

## Current contract and progress

Before implementation, record the purpose, relevant authority, scope and protected paths, constraints, acceptance criteria, and planned verification. Keep this **Current Contract** distinct from **Progress**: progress records the candidate, decisions, changes, and unresolved work without silently changing the contract. Recheck the contract when work resumes or the instructions change; resolve conflicts and scope changes explicitly.

## Stop and escalate before

Check that the user has authorized public API or persisted-data changes, authentication, authorization, payments, infrastructure or production deployment, and new or replacement production dependencies. Existing user instructions may already provide that authorization. Do not weaken a test merely to pass it, write outside the authorized scope, or broadly rewrite unrelated files. Investigate repeated failures before choosing another approach.

## Verification and evidence

Record the exact candidate using an immutable Git commit or tree ID, or the base revision plus changed-file hashes and modes and a deletion list. In the same plan or linked review, record the environment, commands and results, relevant documentation impact, independent review when required, and unresolved limits. Avoid copying the same evidence between the plan and review. File safety checks and independent review for risky changes remain required by [`QUALITY.md`](QUALITY.md) and [`SECURITY.md`](SECURITY.md).

Distinguish `PASS` (verified), `FAIL` (violated), and `UNPROVEN` (insufficient evidence). Never treat intent or unrelated passing tests as proof. Do not recommend acceptance with required criteria at FAIL or UNPROVEN. The user or reviewer retains acceptance authority. Record material defects and their re-verification, and leave unresolved work with an owner and next step.

## Recovery and completion

Use the project's real checks and retain the recovery information needed for the change. There is no automatic Gate, Verification Run, `close-plan` command, run directory, or generated closure record. Complete a plan manually when its criteria, review, documentation impact, and follow-ups are resolved. Completed plans and accepted decisions are historical records; supersede them rather than rewriting their bodies. A completion claim alone is not evidence.

When work is no longer being actively pursued, mark it paused and move it to [`exec-plans/paused/`](exec-plans/paused/). Retain failed or unproven results and unresolved follow-ups; do not present incomplete criteria as successful or the work as completed. Before resuming, review the prior results, permissions and budget against the current instructions and obtain any separately required authorization. An old plan does not itself authorize a new run.

Plans do not themselves authorize external services, deployment, deletion, or unrelated changes.
