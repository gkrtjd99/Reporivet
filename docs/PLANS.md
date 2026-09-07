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
- Durable normative choices record their scope, reason, protected condition or prevented failure, existing repository and dependency/framework capabilities reviewed, official primary sources when an external technical choice is involved, no-change and practical alternatives, rejection reasons, verification or enforcement, and revisit or retirement condition.

Generated repository facts are evidence, not authority. Plans and reviews must preserve observed facts and candidates separately and must not promote a scanner candidate to a normative choice without explicit project-owned review.

## Product Traceability

Traceability is opt-in. A plan that declares `traceability: 1` must name exactly one active `product_spec` and carry a Product Trace table that connects known confirmed journey, P0 requirement, and acceptance IDs to implementation and verification tasks.

- Confirmed declarations are the only evidence that can satisfy a trace link. Proposed and Open material remains visible but non-authoritative.
- Implementation and verification Task Packets each declare a task type and at least one known acceptance criterion.
- Product Trace links are reciprocal: each referenced P0 and criterion must agree about its journey and relationship.
- A verifying or complete traceable plan contains no unresolved placeholder in trace, task, or closure evidence.
- Historical plans without traceability metadata remain valid and are not rewritten.

## Operating roles and delegation

Task types remain `support`, `implementation`, or `verification`. Every Task Packet records state, dependencies, outcome, non-goals, exact reads, allowed writes, protected paths, acceptance IDs, required capabilities and tool access, concurrency, retry and time budget, verification commands, stop conditions, and a result.

Main owns intent, scope, non-goals, acceptance, permissions, plan writing and lifecycle, decomposition, delegation, integration order, the exact verification target, final integration, evidence acceptance, and completion approval. Small tasks omit unnecessary hierarchy; delegated work has a maximum depth of Main → Task Lead → leaf.

Main은 Task 간 공유 인터페이스·경로 소유권·의존성·통합 순서를 설계한다.

Only an explicitly designated Task Lead may delegate within the assigned parent packet. Without new approval for each leaf, the Lead may compose and assign bounded leaf packets whose allowed writes are a subset of the parent, whose protected paths, acceptance criteria, and stop conditions are inherited unchanged, and whose execution stays within the parent budget. Lead의 역할은 상위 계약 안의 leaf 분해·경계 설계·packet 구성과 배정, scheduling, repair coordination, consolidating leaf results and status로 제한하며 Main이 같은 ExecPlan에 기록한다. Scope changes return to Main; the Lead cannot change acceptance, permissions, or plan state, edit the durable ExecPlan, perform final integration, or approve completion.

Leaf agents cannot delegate, broaden scope, change acceptance, or approve their own work. Delegation cannot expand authority beyond the parent packet or host execution permissions and must not be used to bypass a denied action. Implementers and Independent Verifiers are leaf roles. An Implementer owns assigned writes and focused verification. An Independent Verifier judges an exact candidate in a separate context without relying on implementer explanation. If the host cannot provide a separate context, record that independent verification was not performed rather than treating self-checks as independent evidence.

Read-only work may run in parallel. Mutable work is sequential unless every parallel write has separate worktrees, disjoint write paths, frozen shared interfaces, Main-owned serialized integration, and fresh verification of the integrated commit. Focused verification belongs to the bounded task; Main owns final canonical verification of the integrated candidate and the acceptance decision.

공유 계약은 병렬 수행 동안 고정한다. 변경이 필요하면 영향 작업을 멈추고 경계 소유자(Main: Task 간, Lead: parent 내부)가 계약을 조정한 뒤 재배정한다. parent 범위·계약·권한 변경은 Main에게 반환한다. 이 절차는 host/project의 더 제한적인 병렬 정책을 완화하지 않으며, 독립 경계를 만들 수 없으면 순차 수행한다.

Verifier는 반례·실패 경로·회귀를 능동적으로 찾고 테스트 자체의 가정도 의심한다. 수정 후에는 새 exact candidate를 재검증한다.

Tasks live inside the ExecPlan; do not create another durable task registry or orchestration database. Main owns the plan file, and delegated agents return concise results instead of concurrently editing shared plan state.

## Result prose contract

Keep the existing task states, task types, and Markdown `Result` field. Write Result prose that distinguishes candidate work, independent verification, integration, and acceptance, and includes:

- status and exact target commit SHA;
- changed paths or read-only scope;
- execution environment, including relevant capabilities and tool access;
- commands run and their results;
- verification scope, results, and evidence locations;
- blockers, unresolved issues, and residual limitations;
- the verifier's recommendation separately from Main or human approval.

결함에는 위반한 요구사항·trigger·영향과 재현 또는 구체적인 코드 근거를 제시한다. 우려·취향·미검증 영역은 결함과 구분하고 결함 개수를 강제하지 않는다.

When an independent context is unavailable, state that independent verification was not performed and identify the focused checks that were performed. Raw transcripts and polling history are not Result evidence.

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
