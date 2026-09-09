# Source ExecPlan Policy

ExecPlans are source-repository documents for complex work. They are manually copied from [`exec-plans/_template.md`](exec-plans/_template.md), version-controlled, and readable without chat history. They are not a generated target schema or an automatic completion system.

## When a plan is required

Create a plan for cross-cutting, risky, long-running, multi-agent, public-contract, persistent-data, authentication, authorization, payment, infrastructure, deployment, or difficult-to-verify changes. Small, local, reversible work may proceed without one until its scope expands.

## Required properties

A plan records purpose, scope, non-goals, acceptance criteria, milestones, exact reads and writes, protected paths, dependencies, execution constraints, verification commands, documentation impact, discoveries, decisions, evidence, and follow-ups. Generated observations are evidence, not authority. Normative choices record reason, scope, prevented failure, existing capabilities, alternatives and rejection reasons, verification, and revisit conditions.

## Operating roles and delegation

Task types remain `support`, `implementation`, or `verification`. Every Task Packet records state, dependencies, outcome, non-goals, exact reads, allowed writes, protected paths, acceptance IDs, required capabilities and tool access, concurrency, retry and time budget, verification commands, stop conditions, and a result.

Main owns intent, scope, non-goals, acceptance, permissions, plan writing and lifecycle, decomposition, delegation, integration order, the exact verification target, final integration, evidence acceptance, and completion approval. Small tasks omit unnecessary hierarchy; delegated work has a maximum depth of Main → Task Lead → leaf.

Main은 Task 간 공유 인터페이스·경로 소유권·의존성·통합 순서를 설계한다.

Only an explicitly designated Task Lead may delegate within the assigned parent packet. Without new approval for each leaf, the Lead may compose and assign bounded leaf packets whose allowed writes are a subset of the parent, whose protected paths, acceptance criteria, and stop conditions are inherited unchanged, and whose execution stays within the parent budget. Lead의 역할은 상위 계약 안의 leaf 분해·경계 설계·packet 구성과 배정, scheduling, repair coordination, consolidating leaf results and status로 제한하며 Main이 같은 ExecPlan에 기록한다. Scope changes return to Main; the Lead cannot change acceptance, permissions, or plan state, edit the durable ExecPlan, perform final integration, or approve completion.

Leaf agents cannot delegate, broaden scope, change acceptance, or approve their own work. Delegation cannot expand authority beyond the parent packet or host execution permissions and must not be used to bypass a denied action. Implementers and Independent Verifiers are leaf roles. An Implementer owns assigned writes and focused verification. An Independent Verifier judges an exact candidate in a separate context without relying on implementer explanation. If the host cannot provide a separate context, record that independent verification was not performed rather than treating self-checks as independent evidence.

Read-only work may run in parallel. Mutable work is sequential unless every parallel write has separate worktrees, disjoint write paths, frozen shared interfaces, Main-owned serialized integration, and fresh verification of the integrated candidate. Focused verification belongs to the bounded task; Main owns final canonical verification of the integrated candidate and the acceptance decision.

공유 계약은 병렬 수행 동안 고정한다. 변경이 필요하면 영향 작업을 멈추고 경계 소유자(Main: Task 간, Lead: parent 내부)가 계약을 조정한 뒤 재배정한다. parent 범위·계약·권한 변경은 Main에게 반환한다. 이 절차는 host/project의 더 제한적인 병렬 정책을 완화하지 않으며, 독립 경계를 만들 수 없으면 순차 수행한다.

Verifier는 반례·실패 경로·회귀를 능동적으로 찾고 테스트 자체의 가정도 의심한다. 수정 후에는 새 exact candidate를 재검증한다.

수선 시 Main 또는 지정 Lead는 확인된 결함과 재현 근거를 하나의 요청으로 취합하고, 가능하면 기존 Implementer를 재개한다. 요청에는 현재 후보, 수정 허용 경로, 실패 근거, 재검증 대상을 포함한다. 원인이 불명확하면 추가 구현 전에 범위를 제한한 진단을 수행한다. 기존 시간·재시도 예산과 같은 접근법 두 번 실패 시 중단 조건은 유지한다. 구현자 재개는 별도 문맥의 독립 검증을 대체하지 않는다.

## Result prose contract

Keep task state, task type, and the Markdown `Result` field. Result prose distinguishes candidate work, independent verification, integration, and acceptance, and includes:

- status and exact integrated candidate: exact target commit SHA, or base commit plus nonignored file hashes, modes, and the deletion list;
- changed paths or read-only scope;
- execution environment and tool access;
- commands run and results;
- verification scope, evidence, and limitations;
- blockers and unresolved issues;
- the verifier's recommendation separately from Main or human approval.

결함에는 위반한 요구사항·trigger·영향과 재현 또는 구체적인 코드 근거를 제시한다. 우려·취향·미검증 영역은 결함과 구분하고 결함 개수를 강제하지 않는다.

결함 보고에는 기존 테스트·검사가 해당 실패 경로를 왜 검출하지 못하는지 설명한다. 관련 검사를 확인하지 못했다면 그 한계를 명시한다.

Verifier는 각 수락 기준을 `PASS`(증거로 충족 확인), `FAIL`(위반 또는 필요한 동작 누락), `UNPROVEN`(확보한 증거로 충족 여부 미확인)으로 판정하고 근거를 연결한다. 의도·추정·다른 검사의 성공만으로 `UNPROVEN`을 `PASS`로 바꾸지 않는다. 필수 수락 기준에 `FAIL` 또는 `UNPROVEN`이 남으면 완료 수락을 추천하지 않는다. 최종 수락 권한은 Main 또는 human reviewer에게 남는다. 기존 Validation and Evidence 표에 기준별 판정과 FAIL/UNPROVEN의 미충족 사항 또는 증거 부족을 기록한다. 실행 전 표의 판정은 `UNPROVEN`이며 Task의 state와 승인 필드를 대체하지 않는다.

### 적용 이유와 재검토 조건

이 보강은 소스 운영 계약과 앞으로 작성하는 ExecPlan에 적용하며 완료된 계획과 생성 target의 schema는 바꾸지 않는다. 기준별 판정은 결함 미발견을 요구 충족으로 오인하는 일을, 검사 사각지대 설명은 이미 검증된 경로의 반복 지적을, 수선 요청 취합과 구현자 재개는 중복·충돌 수정과 문맥 재탐색을 줄이기 위한 것이다.

기존 역할 계약·Result 필드·증거 표·계약 테스트와 동기화 도구를 재사용한다. 변경하지 않는 대안은 증거 부족의 기록 방법과 수선 인계 항목이 불명확하게 남아 제외했다. 별도 에이전트 묶음·고정 검증 3종·추가 상태 시스템은 작은 작업의 비용과 중복을 늘려 제외했다. 외부 패키지나 실행 API를 도입하지 않는다.

기계적 검사는 계약 문구·양식 열·투영 일치를 확인할 뿐 판정의 타당성을 승인하지 않는다. 실제 증거와 별도 문맥 검토를 Main이 수락한다. 판정 중복, 효과 없는 반복 검사, 구현자 재개의 오래된 가정이 관찰되면 Main이 이 정책을 재검토하고 중복 규칙을 축소하거나 대체한다. 이를 위한 자동 계측이나 별도 기록 시스템은 추가하지 않는다.

## Verification and completion

Use actual repository checks and project-owned tools declared by the plan. `PYTHON=python3 ./dev/check` is the source repository check; it is not a target command and does not approve project work. A separate-context verifier reports whether independent verification was performed. Main records the exact candidate, environment, commands, verification scope, evidence, blockers, and approval status. A fingerprint identifies the state; it does not grant approval. A commit is not created merely to satisfy evidence formatting.

There is no automatic Gate, Verification Run, `close-plan` command, run directory, or generated closure record. Main completes a plan manually after acceptance criteria, documentation impact, independent review when required, and follow-ups are resolved. Historical completed plans and accepted decisions remain unchanged; current documents supersede them explicitly.

## Non-goals

ExecPlans do not authorize an external task service, daemon, model judge, backup, archive, deletion, publication, deployment, or old-repository operation unless the plan and human authority explicitly grant that separate action.
