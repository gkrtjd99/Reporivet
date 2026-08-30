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

## Product Traceability

Traceability is opt-in. A plan that declares `traceability: 1` must name exactly one active `product_spec` and carry a Product Trace table that connects known confirmed journey, P0 requirement, and acceptance IDs to implementation and verification tasks.

- Confirmed declarations are the only evidence that can satisfy a trace link. Proposed and Open material remains visible but non-authoritative.
- Implementation and verification Task Packets each declare a task type and at least one known acceptance criterion.
- Product Trace links are reciprocal: each referenced P0 and criterion must agree about its journey and relationship.
- A verifying or complete traceable plan contains no unresolved placeholder in trace, task, or closure evidence.
- Historical plans without traceability metadata remain valid and are not rewritten.

## Task Packet contract

Task types are `support`, `implementation`, or `verification`. Every packet records state, dependencies, outcome, non-goals, exact reads, allowed writes, protected paths, acceptance IDs, verification commands, stop conditions, and a result.

Main owns plan state, acceptance, decomposition, and integration. A Sub Agent receives one bounded packet, cannot broaden its scope or delegate again, and cannot approve its own implementation. Tasks live inside the ExecPlan; do not create another durable task registry or orchestration database.

## Main and Sub write policy

The Main Agent owns the plan file. Sub Agents return structured results; they do not concurrently edit shared plan state. Mutable parallelism requires separate worktrees, disjoint write paths, frozen shared interfaces, and Main-owned serialized integration.

## Documentation impact

Each plan declares `none`, `create`, `update`, `supersede`, `retire`, or `generate` for affected durable documents. Completion is blocked while a declared action is pending.

## Verification evidence

A traceable completed plan records criterion-level evidence beneath `.harness/runs/<verification_run>/` and includes:

- the Verification Run ID;
- SHA-256 of the finalized manifest;
- the clean verified commit;
- the Gate verdict;
- an evidence path for each acceptance criterion; and
- the genuine human reason when the verdict is `REVIEW`.

Evidence paths must stay under the named run directory. Raw logs remain ignored and are not copied into the plan. `BLOCK` and `INCONCLUSIVE` are not completion evidence.

## Closure

Set the plan to `verifying`, resolve all Task Packets and documentation impact, set `integrated_commit: HEAD`, commit the candidate, then run:

```bash
./dev/close-plan PLAN-...
# A REVIEW verdict additionally requires the human rationale:
./dev/close-plan PLAN-... --accept-review "reviewed impact and recovery rationale"
```

The command runs the canonical Verification Run exactly once against the plan base and clean current `HEAD`. `PASS` closes directly; `REVIEW` closes only with a genuine explicit rationale; `BLOCK` and `INCONCLUSIVE` cannot be overridden. Successful closure records the run ID, manifest SHA-256, Gate verdict, verified commit, and applicable criterion evidence before moving the plan into `completed/`. Commit that historical completion record separately; do not run a second canonical verify merely because the plan moved.

## Non-goals

ExecPlans do not authorize an external task service, daemon, model judge, backup, archive, deletion, publication, deployment, or old-repository operation unless the plan and human authority explicitly grant that separate action.
