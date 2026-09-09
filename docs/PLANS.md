# Source ExecPlan Policy

ExecPlans are source-repository documents for complex work. They are manually copied from [`exec-plans/_template.md`](exec-plans/_template.md), version-controlled, and readable without chat history. They are not a generated target schema or an automatic completion system. Tasks and their results live in the plan; do not add a second task registry, state database, packet directory, or orchestration layer.

## When a plan is required

Create a plan for cross-cutting, risky, long-running, multi-agent, public-contract, persistent-data, authentication, authorization, payment, infrastructure, deployment, or difficult-to-verify changes. Small, local, reversible work may proceed without one until its scope expands.

## Required properties

A plan records purpose, scope, non-goals, acceptance criteria, milestones, exact reads and writes, protected paths, dependencies, execution constraints, verification commands, documentation impact, discoveries, decisions, evidence, and follow-ups. Generated observations are evidence, not authority. Normative choices record reason, scope, prevented failure, existing capabilities, practical alternatives and rejection reasons, verification, and revisit conditions.

## Current contract and progress

The plan must keep a **Current Contract** separate from **Progress**. Current Contract contains the source and revision, the exact prohibition text that applies, scope and non-goals, acceptance criteria, interfaces, allowed-write and protected-path authority, and who may change each item. Progress records transient state, candidate, completed steps, and unresolved work; a status or compressed summary never replaces the current contract.

At each of these six restoration points, the responsible agent rereads the authoritative contract and the relevant plan sections, then rechecks source, revision, exact prohibitions, scope, allowed writes, protected paths, acceptance criteria, and stop conditions:

1. before starting a task or assigning a packet;
2. before resuming paused or handed-back work;
3. after context compression, summarization, or manual reinjection;
4. after a new user instruction or host/policy observation that may affect the work;
5. after a shared-contract, scope, permission, or revision change; and
6. before integration, independent review, or acceptance.

Sending only a path or revision is not evidence that the recipient read the contract. The recipient must inspect the authoritative text and preserve applicable negative evidence. A stale task must stop; Main or the designated Task Owner reassigns it only after the current contract is re-established. If stale work cannot be stopped or its state cannot be established, acceptance is held rather than inferred.

Durable, always-applicable policy belongs in the portable contract and this policy. A task-specific user instruction, environment observation, candidate, and approval state belong in the active plan and do not silently become permanent policy. A legitimate new user instruction may change the current contract only through Main's recorded scope/revision decision; affected work stops and is rechecked first.

## Operating roles and delegation

Task types remain `support`, `implementation`, or `verification`. Every Task Packet records state, dependencies, outcome, non-goals, exact reads, allowed writes, protected paths, acceptance IDs, required capabilities and tool access, concurrency, retry and time budget, verification commands, stop conditions, and a result.

Main owns purpose, scope, non-goals, acceptance, permissions, plan writing and lifecycle, decomposition, delegation, integration order, the exact verification target, final integration, evidence acceptance, and completion approval. Main owns global design and each task's bounded authoritative source and separate execution-context boundary, and designs Task-to-Task interfaces, path ownership, dependencies, and integration order. Main reads only bounded code and evidence needed for judgment; it does not accumulate broad exploration, repeated implementation, raw-log analysis, or long debugging in its session. If reading expands, isolate it as a separate bounded task. Difficult work uses a separate required stronger execution context, not a Main implementation session. Integration execution may be delegated, but Main retains sequence, exact candidate, final integration, and acceptance. Main does not replace an Owner's executable design judgment by implementing a delegated task directly.

Small tasks omit unnecessary hierarchy. When delegation is useful, the maximum depth is Main → Task Owner → leaf; a more restrictive host or project policy always wins. Only an explicitly designated Task Owner may delegate within its assigned parent packet. Without new approval for each leaf, the Owner composes bounded leaf packets whose allowed writes are a subset of the parent, whose protected paths, acceptance criteria, and stop conditions are inherited unchanged, and whose execution stays within the parent budget.

The Task Owner owns the executable design, the observation and behavior that will demonstrate it, the verification method, direct comparison of important diffs and decisive evidence, and repair-cause judgment (judgment of a repair's cause). The Owner must not delegate those judgments wholesale. The Owner may schedule bounded leaf work, coordinate repairs, and consolidate results, but cannot change parent scope, permissions, acceptance, or the shared contract, edit the durable plan or plan state, perform final integration, or approve acceptance. There is no required coding share, direct-implementation percentage, or call-count quota; responsibility is not measured by activity volume.

When an implementation-affecting cause or core design assumption is unconfirmed, assign only that uncertainty to a bounded investigation or experiment. Hold the affected implementation until the Owner confirms a resolving design from the evidence. Do not require diagnosis for every minor assumption.

Every leaf receives one bounded packet with its assigned acceptance criteria. A leaf must not delegate, broaden scope, change acceptance, write outside allowed paths, create durable work systems, or approve its own work. The packet may permit local implementation, investigation, and check choices; core design, scope, permissions, acceptance criteria, and prohibitions cannot be changed and return to the Owner or Main. Delegation cannot expand authority or bypass a denied action.

Read-only exploration, review, test analysis, and log analysis may run in parallel. Mutable work is sequential unless every parallel write has disjoint write paths, separate Git worktrees, frozen shared interfaces, Main-owned serialized integration, and fresh verification of the integrated candidate. If an independent boundary cannot be made, run sequentially.

공유 계약은 병렬 수행 동안 고정한다. 변경이 필요하면 영향 작업을 멈추고 경계 소유자(Main: Task 간, Owner: parent 내부)가 계약을 조정한 뒤 재배정한다. parent 범위·계약·권한 변경은 Main에게 반환한다. 이 절차는 host/project의 더 제한적인 병렬 정책을 완화하지 않는다.

## Capability and host boundaries

Role and model grade are separate decisions. Use the default assignment observed on the current host as the starting point, without treating an alias as backend identity. Select the required capability and execution context from task clarity, uncertainty, tool needs, and failure cost: clear low-cost work may use a lower-cost available assignment, while uncertain or costly work receives the capability and, when needed, a separate stronger execution context. Do not hard-code a model name, model ID, provider, or a new configuration key. An Independent Verifier is not fixed to the cheapest grade; its grade follows the judgment required. A retry changes neither the accumulated retry/time budget nor the evidence obligation, even when the agent or model changes.

A prompt or Task Packet communicates responsibility, scope, and intended tool access; it is not host enforcement. Host permissions, sandbox boundaries, and hooks may constrain execution only when their behavior is actually observed. Post-checks such as hashes, modes, diffs, command results, and exact-candidate comparison provide evidence after execution. A shell path may bypass a prompt-level semantic or path restriction when host permissions allow it, and a semantic rule is not proved by a command guard. Do not add a hook, setting key, model ID, runtime, or configuration file to imply enforcement; do not modify home settings, credentials, external services, or deployment environments without explicit authority and packet scope, and retain any stricter prohibition imposed by the current contract. Unobserved host features and backend identity remain `UNPROVEN`.

## Result prose contract

Keep task state, task type, the Markdown `Result` field, and the existing Validation and Evidence table. Result prose distinguishes candidate work, independent verification, integration, and acceptance, and includes:

- applied contract source and revision, including the exact prohibitions and authority used;
- status and exact candidate: an exact target commit SHA, or base commit plus nonignored file hashes, modes, and deletion list;
- changed paths or read-only scope, execution environment, and tool access;
- commands run, exit status, relevant output, and verification scope;
- every acceptance criterion as `PASS`, `FAIL`, or `UNPROVEN`, with the evidence path and the missing requirement or evidence gap;
- checks of protected paths and prohibitions, retained negative evidence and limitations (including its retention when repetitive logs are compressed);
- design deviations, their reason, and whether they were returned to Main;
- the Task Owner's direct design/evidence judgment and unresolved decisions;
- independent verifier findings and recommendation separately from the Main decision/approval or human approval, with detailed evidence locations.

결함에는 위반한 요구사항·trigger·영향과 재현 또는 구체적인 코드 근거를 제시한다. 우려·취향·미검증 영역은 결함과 구분하고 결함 개수를 강제하지 않는다. 결함 보고에는 기존 테스트·검사가 해당 실패 경로를 왜 검출하지 못했는지 설명하며, 관련 검사를 확인하지 못했다면 그 한계를 명시한다.

An Independent Verifier judges the exact candidate in a separate context against the current requirements and execution environment without relying on the Implementer's or Owner's conclusion. Owner comparison is necessary design accountability but does not substitute for independent verification. If a separate context is unavailable, state that independent verification was not performed. The verifier actively seeks counterexamples, failure paths, regressions, and assumptions in the tests; after repair, it reviews a new exact candidate.

Verifier는 각 수락 기준을 `PASS`(증거로 충족 확인), `FAIL`(위반 또는 필요한 동작 누락), `UNPROVEN`(확보한 증거로 충족 여부 미확인)으로 판정하고 근거를 연결한다. 의도·추정·다른 검사의 성공만으로 `UNPROVEN`을 `PASS`로 바꾸지 않는다. 필수 수락 기준에 `FAIL` 또는 `UNPROVEN`이 남으면 완료 수락을 추천하지 않는다. 최종 수락 권한은 Main 또는 human reviewer에게 남는다. 실행 전 표의 판정은 `UNPROVEN`이며 Task state와 승인 필드를 대체하지 않는다.

## Repair, recovery, and completion

For a confirmed defect, Main or the designated Owner sends one bounded repair request containing the current candidate, permitted write paths, failure reproduction/evidence, affected acceptance criteria, and re-verification target. Diagnose within a limited scope before implementing when the cause is unclear. Resume the existing Implementer when possible, but do not reset the existing time or retry budget by changing agent or model. A repair does not change acceptance or protected paths, and a new exact candidate must receive independent review when required.

Use actual repository and project-owned checks named by the plan. `PYTHON=python3 ./dev/check` is the source repository check; it is not a target command and does not approve project work. If the available interpreter lacks a declared build requirement, record the real command failure and use only an explicitly authorized isolated environment for follow-up; do not skip, weaken, or reclassify the canonical check. A separate-context verifier reports whether independent verification was performed. Main records the exact candidate, environment, commands, verification scope, evidence, blockers, documentation impact, and approval status.

There is no automatic Gate, Verification Run, `close-plan` command, run directory, or generated closure record. Main completes a plan manually after acceptance criteria, documentation impact, independent review when required, and follow-ups are resolved. Historical completed plans and accepted decisions remain unchanged; current documents supersede them explicitly. A fingerprint identifies the reviewed state; it does not grant approval. Do not create a commit merely to satisfy evidence formatting.

## Non-goals

ExecPlans do not authorize an external task service, daemon, model judge, backup, archive, deletion, publication, deployment, or old-repository operation unless the plan and human authority explicitly grant that separate action.
