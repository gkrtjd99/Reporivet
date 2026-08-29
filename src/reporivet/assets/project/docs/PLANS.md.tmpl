# ExecPlan Policy

ExecPlans are self-contained, version-controlled, living documents for complex work. A new Main Agent must be able to resume from the plan and repository without chat history.

## When a plan is required

Create a plan for cross-cutting, risky, long-running, multi-agent, public-contract, persistent-data, authentication, authorization, payment, infrastructure, deployment, or difficult-to-verify changes.

Small, local, reversible work may proceed without a durable plan until its scope expands.

## Lifecycle

```text
proposed -> approved -> in-progress -> verifying -> complete
                     \-> blocked
proposed/approved/in-progress -> cancelled or superseded
```

Active plans live in [`exec-plans/active/`](exec-plans/active/). Completed, cancelled, and superseded plans live in [`exec-plans/completed/`](exec-plans/completed/).

## Required properties

- Self-contained context and orientation for a reader with no chat history.
- Observable purpose, acceptance criteria, milestones, and concrete verification.
- Task Packets with exact read/write boundaries and stop conditions.
- Continuously updated progress, discoveries, decisions, documentation impact, and evidence.
- Idempotent or recoverable steps where possible.
- An integrated Git target and independent verification before closure.

## Main and Sub write policy

The Main Agent owns the plan file. Sub Agents return structured results; they do not concurrently edit shared plan state. Mutable parallelism requires separate worktrees, disjoint write paths, and Main-owned serialized integration.

## Documentation impact

Each plan declares `none`, `create`, `update`, `supersede`, `retire`, or `generate` for affected durable documents. Completion is blocked while a declared action is pending.

## Closure

Set the plan to `verifying`, resolve all Task Packets and documentation impact, set `integrated_commit: HEAD`, commit the candidate, then run:

```bash
./dev/close-plan PLAN-...
```

The command verifies the clean current `HEAD`, records the actual commit SHA, and moves the plan into `completed/`. Commit that historical completion record separately.
