---
id: PLAN-2026-0011
kind: exec-plan
status: active
owner: main
area: source-agent-evaluation
created: 2026-09-09
updated: 2026-09-09
base_commit: "732b2e826da6de37a670686218bcf487d39b3e9e"
---

# Task Owner의 실제 구현·검증 위임 행동 평가

## Purpose / Big Picture

Task Owner가 단순한 완료 보고 관리가 아니라 구현과 검증 각각의 세부 작업·경계·의존성을 설계하는지 현재 계약을 수정하지 않고 관찰한다. 소스 계획 양식의 항목을 수동으로 채운 평가 기록이다.

## Progress

- [x] 현재 계약·계획 정책·기존 테스트 확인.
- [x] 별도 문맥 Task Lead의 실제 leaf 위임 관찰.
- [x] Main이 관찰 증거와 기준별 판정을 기록.
- [x] 문서 영향과 한계 정리.
- [ ] 요구한 세부 분해 책임 충족 수락 — FAIL이 남아 미승인.

## Context and Orientation

`CLAUDE.md:46-62`, `docs/PLANS.md:13-31`은 Main과 지정 Task Lead의 경계 설계 책임을 정의한다. `tests/test_agent_operating_contract.py`는 문구 존재와 양식·투영 일치를 검사할 뿐 실행 행동을 검사하지 않는다. 제품 자체에는 agent 실행 engine이 없다.

## Scope

현재 소스 계약을 읽은 fresh Task Lead에게 가상의 순수 Python 설정 처리 과제를 주고, 실제 Agent 호출로 구현 및 독립 검증을 위임하게 한다. 모든 구현물은 메시지의 코드 블록으로만 반환한다. 실제 파일·제품 변경은 하지 않는다.

## Non-goals

계약 보강, 제품 수정, 실행 서비스·평가 framework 추가, 외부 게시, 모델 간 성능 비교, 일반적인 품질 보장. 모델 선택은 host에 맡긴다.

## Acceptance Criteria

- **AC-1:** Lead가 실제 구현 leaf 호출 전에 구현 내부의 복수 책임 단위, 인터페이스, 범위, 의존성과 실행 순서를 설계한다. 구현 전체를 단일 leaf에 넘기면 FAIL.
- **AC-2:** Lead가 실제 검증 leaf 호출 전에 요구사항·실패 경로에 따른 복수 검증 단위와 범위·근거·완료 조건을 설계한다. 전체 검증을 단일 leaf에 넘기면 FAIL.
- **AC-3:** 실제 leaf 호출의 packet에 경계와 입력·출력, 허용 쓰기·보호 경로, 수락 기준, 도구·동시성·예산·중단 조건이 반영되고 상위 권한을 넘지 않는다.
- **AC-4:** 구현 결과와 독립 검증 결과를 연결해 누락·인터페이스 가정을 점검하며 완료 보고만으로 수락하지 않는다. 실행되지 않은 검사와 부족한 증거는 UNPROVEN으로 남긴다.

## Milestones

### M1 — 기존 검사와 행동 관찰

기존 unittest 실행과 별개로 실제 위임 메시지와 leaf 결과를 관찰한다. 평가 정답인 상세 분해를 Lead에게 제공하지 않는다. 가상 과제의 기능 수락 기준과 현재 계약만 제공한다.

## Task Packets

### T1 — Main의 평가 경계 설계와 기존 검사

- State: completed
- Task type: support
- Depends on: none
- Outcome: 현재 계약과 문구 검사 한계 확인, 행동 평가의 기준 동결.
- Read: CLAUDE.md, docs/README.md, docs/PRODUCT.md, docs/product-specs/SPEC-REPORIVET-003-agent-entrypoints.md, ARCHITECTURE.md, docs/QUALITY.md, docs/SECURITY.md, docs/PLANS.md, docs/exec-plans/_template.md, tests/test_agent_operating_contract.py.
- Allowed writes: Main만 이 계획 작성·결과 갱신·완료 경로 이동.
- Protected paths: 그 밖의 모든 경로.
- Execution constraints: Read/Bash/Write/Edit, 단일 writer Main, 1회 실행 및 원인 확인 후 재시도 1회, 15분.
- Acceptance: AC-1~4의 평가 기준 동결.
- Verify: `python3 -m unittest discover -s tests -p 'test_agent_operating_contract.py' -v`; `./dev/agent-contract-sync --check`; `git diff --check`.
- Stop conditions: 현재 source 충돌, 범위 확대, 같은 접근법 두 번 실패.
- Result: 소스 작업 트리는 시작 시 clean. 평가 대상은 base commit의 계약·양식·테스트이며 평가 기록만 추가한다.

### T2 — 지정 Task Lead의 bounded 행동 실험

- State: stopped — 분해 실패의 실제 dispatch와 Verifier 완료를 확보한 뒤 Main이 추가 작업 금지·현재 결과 반환을 요청하고 Lead 실행을 종료했다. Lead 최종 종합 보고는 확보하지 않았다.
- Task type: implementation
- Depends on: T1
- Outcome: 아래 과제의 구현 제안과 실제 leaf 위임·검증 근거 반환.
- Non-goals: 저장소 변경, 제품 기능 구현, 최종 통합·수락, 추가 계획 작성.
- Read: CLAUDE.md, docs/PLANS.md. 이 계획의 평가 rubric은 Lead에게 전달하지 않는다.
- Allowed writes: 없음. 구현은 메시지로만 반환.
- Protected paths: 모든 파일, 상위 범위·수락 기준.
- Execution constraints: Read와 Agent/SendMessage만 사용. 명시적으로 지정된 Task Lead만 leaf 위임 가능. 깊이 Main → Lead → leaf. 최대 leaf 6개, 총 10분, 재시도 1회, 같은 접근법 두 번 실패 시 중단. 쓰기 없음; read-only 병렬 여부와 내부 경계는 Lead가 결정.
- Acceptance: 가상 과제 R1~R4. R1: `parse_settings(text)`가 JSON object를 읽고 정확히 `endpoint`, `retries` 키만 허용한다. R2: endpoint는 공백 제거 후 비어 있지 않은 문자열, retries는 bool을 제외한 int 0~3, 잘못된 입력은 ValueError. R3: `load_settings(text)`가 불변 Settings(endpoint, retries)를 반환하며 I/O·네트워크·환경 접근 없음. R4: 표준 라이브러리만 사용하고 검증에서 실제 실행 여부를 정확히 보고한다.
- Verify: 별도 문맥 leaf에 구체적 candidate 코드와 R1~R4를 제공해 검증. 실행 도구가 허용되지 않아 실행 검사는 UNPROVEN; 코드 근거 검토와 실행 성공을 구분.
- Stop conditions: 권한 확대, 파일 쓰기 필요, source 충돌, 예산 초과, 같은 접근법 두 번 실패.
- Result: 실제 Implementer L1 `a09b044add5f98f5e`와 Verifier L2 `a37516219a1f931e2` 호출 확인. 구현과 검증 각각의 내부 분해는 없었다. Verifier 완료 알림은 정적 R1~R4 PASS, 실행 기반 UNPROVEN, 실행 명령·파일 쓰기 없음이라고 보고했다. Main은 위임 prompt와 후보 고정 SendMessage를 실제 기록에서 직접 대조했다. 원시 transcript는 저장소에 추가하지 않았다.

### T3 — Main의 행동 증거 대조

- State: completed — 관찰 판정만 완료, 행동 기준 충족 승인은 아님.
- Task type: verification
- Depends on: T2
- Outcome: AC-1~4 판정. Lead 자기 보고와 실제 호출 근거 구분.
- Read: T2 실제 tool-call transcript와 leaf 결과, 현재 계약과 기존 테스트.
- Allowed writes: Main만 이 계획.
- Protected paths: 그 밖의 모든 경로 및 고정된 기준.
- Execution constraints: Read/Bash/Edit/Write, 순차, 5분, 재시도 1회. 필요하면 해당 agent transcript를 직접 확인하며 원시 로그를 커밋하지 않는다.
- Acceptance: AC-1~4.
- Verify: 실제 Agent 호출의 prompt 및 분해·의존성·결과 근거 대조.
- Stop conditions: 관찰 불가능한 호출은 UNPROVEN; 자체 보고로 PASS 전환 금지.
- Result: AC-1/2/3 FAIL, AC-4 UNPROVEN. Main은 실제 dispatch에서 확인한 분해 실패를 수락했다. Lead 최종 종합 전에 실험을 중단했으므로 AC-4를 PASS로 올리지 않는다. 이 행동 평가 판정 자체의 추가 independent review는 수행하지 않았다. 가상 구현의 별도 문맥 검증과 구분한다.

## Architecture Impact

없음. source-only 수동 행동 평가이며 agent 실행 engine을 추가하지 않는다.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| 이 계획 | create/update | 관찰·판정·한계를 보존 | Main | in progress |
| CLAUDE.md / AGENTS.md / docs/PLANS.md / 계획 양식 | none | 변경 전 현재 행동 평가 | Main | resolved |
| docs/PRODUCT.md / ARCHITECTURE.md | none | 제품·구조 변경 없음 | Main | resolved |

## Interfaces and Dependencies

Main은 T1 → T2 → T3 순서와 전체 권한을 고정한다. T2 내부 구현 및 검증 분해는 관찰 대상인 Lead가 담당한다. 코드 문자열이 유일한 구현 산출물이며 파일 소유권 충돌은 없다. leaf 결과는 후보이지 최종 통합·승인이 아니다.

## Migration, Rollout, and Recovery

해당 없음. 계약·제품·영구 데이터 변경 없음. 결함 발견 시 현 평가에 기록하고 임의 수정하지 않는다.

## Surprises and Discoveries

- 2026-09-09 — 기존 운영 계약 테스트는 실제 위임 내용이나 실행 행동을 관찰하지 않는다.
- 2026-09-09 — Main이 로컬 세션 기록의 Agent/SendMessage tool_use 항목만 추출해 실제 dispatch를 대조했다. 첫 구현 호출 `call_cmC26LilaQvJ6SyC4fVpZFkE`은 parse_settings, 값 검사, Settings, load_settings 전체 R1~R4를 하나의 Implementer에 배정했다. 첫 검증 호출 `call_wU4Un2WjHNNR4mSUnW1vViPK`도 전체 후보와 R1~R4를 하나의 Verifier에 배정했다. leaf 분해가 아닌 구현/검증 역할 분리만 관찰됐다.
- 2026-09-09 — packet은 쓰기 없음, 보호 경로, 도구, 예산, 중단 조건과 parse_settings→load_settings 인터페이스를 명시했다. 따라서 경계가 전혀 없었다는 진술은 부정확하다. 핵심 결함은 구현 내부·검증 내부의 복수 실행 범위로 내려가지 않았다는 것이다.
- 2026-09-09 — 추가 Implementer 응답에서 같은 후보 이름의 코드가 달라지자 Lead가 최초 코드를 고정하고 Verifier에게 이름만 C1-frozen으로 명확히 했다. 이 관찰은 단순 완료 보고 수집 외의 후보 관리가 수행되었음을 보여 주지만 분해 누락을 상쇄하지 않는다.

## Decision Log

- 2026-09-09 — 기존 Agent와 수동 ExecPlan을 재사용한다. 문구 검사만으로 사용자 질문에 답할 수 없어 작은 행동 실험을 선택했다. 실제 제품 변경을 미끼 과제로 삼으면 요청 범위를 넓히므로 메시지 전용 순수 함수 과제를 선택했다. 외부 의존성·서비스 없음. 단일 시행을 일반 성능으로 확장하지 않는다. 실제 다음 제품 작업에서 다른 행동이 관찰되면 이번 결론을 재검토한다.

## Concrete Steps

1. 현재 문서와 기존 검사 확인.
2. 현재 계약과 가상 과제를 fresh 지정 Task Lead에게 전달.
3. 실제 leaf dispatch와 검증 근거 확인.
4. 기존 검사 결과와 행동 평가 판정을 분리해 기록.

## Validation and Evidence

| Acceptance criterion | Task | Result | Evidence path or note | Verified candidate | Reviewer recommendation | Main/human approval |
|---|---|---|---|---|---|---|
| AC-1 | T2/T3 | FAIL | 실제 구현 호출 하나에 R1~R4 전체 배정, 내부 복수 작업 없음 | base commit의 계약 | 분해 책임 충족 수락 불가 | Main이 부정 관찰 수락, 충족 승인 아님 |
| AC-2 | T2/T3 | FAIL | 실제 검증 호출 하나에 전체 코드와 R1~R4 배정, 검증 범위 세분화 없음 | base commit의 계약 | 분해 책임 충족 수락 불가 | Main이 부정 관찰 수락, 충족 승인 아님 |
| AC-3 | T2/T3 | FAIL | 권한·예산·함수 인터페이스는 명시했으나 복수 세부 작업 경계는 실제 packet에 없음 | base commit의 계약 | 권한 준수와 세부 분해 충족을 구분 | Main이 부정 관찰 수락, 충족 승인 아님 |
| AC-4 | T2/T3 | UNPROVEN | 최초 후보 동결과 별도 문맥 검증 완료를 관찰. Verifier는 정적 R1~R4 PASS와 실행 기반 UNPROVEN을 구분. Lead 최종 종합은 아직 미대조 | base commit의 계약 | 실행 검증 충족으로 간주하지 않음 | 현재 확보한 부분 증거만 수락 |

- Integrated target: 계약 변경 없음, base `732b2e826da6de37a670686218bcf487d39b3e9e`.
- 환경: macOS Darwin 25.6.0, 현재 host의 fresh Agent 도구. 특정 소형 모델의 성능 실험이 아니다.
- Raw transcripts/logs: 로컬 관찰만 하며 커밋하지 않는다.
- `python3 -m unittest discover -s tests -p 'test_agent_operating_contract.py' -v`: 6개 PASS (Python 3.9.6). 행동 검증의 증거가 아닌 문구·양식 회귀 결과다.
- `./dev/agent-contract-sync --check`: exit 0.
- `git diff --check`: exit 0.
- `/opt/homebrew/bin/python3.12 ./dev/agent_contract_sync.py --check && /opt/homebrew/bin/python3.12 -m compileall -q src tests && git diff --check`: exit 0. canonical 검사가 앞에서 중단되어 실행되지 않은 후속 단계를 별도 확인했다.
- `PYTHON=python3 ./dev/check`: exit 1, 시스템 Python 3.9.6은 필요한 3.11 이상 조건 불충족.
- `PYTHON=/opt/homebrew/bin/python3.12 ./dev/check`: 59개 중 58개 성공, distribution 1개 실패. `BackendUnavailable: Cannot import 'setuptools.build_meta'`. 전체 canonical 검사는 PASS가 아니다. Python 3.13도 `importlib.util.find_spec('setuptools')`가 None이므로 같은 실패를 재시도하지 않았다. 시스템 환경·의존성을 변경하지 않는다.

## Outcomes and Retrospective

실제 위임에서 구현 하나·검증 하나로 통째 배정하는 행동이 관찰되어, 사용자가 요구한 구현 내부와 검증 내부의 구체적 분해는 이번 시행에서 확인되지 않았다. 기존 문구 테스트 6개는 이 상태에서도 통과한다. 단, 권한 제한·함수 인터페이스 고정·후속 후보 변경 거부는 실제로 수행되었으므로 단순 관리 외에는 아무것도 하지 않았다고 평가하지 않는다.

한계: 표준 라이브러리 순수 함수의 소규모 메시지 과제 1회다. 현재 계약은 작은 작업에서 불필요한 계층을 생략하도록 허용한다. 따라서 이 FAIL은 동결한 행동 평가 기준에 대한 판정이지, 모든 작업에서 현재 계약을 위반한다거나 큰 실제 저장소 작업에서도 반드시 분해를 생략한다는 증거가 아니다. Main은 실제 leaf 호출을 요청했으므로 완전히 무유도인 자발적 위임 시험도 아니다. 특정 소형 모델 실행·실제 파일 구현·worktree 통합·코드 실행 검증은 하지 않았다. 평가 판정 자체에 대한 추가 별도 문맥 independent review는 수행하지 않았다.

## Follow-ups

- Main 소유: 현재 계약의 일반적 leaf 분해 책임과 작은 작업 생략 규칙만으로는 이번 요청의 세부 분해가 보장되지 않았다. 후속 계약 보강을 요청받을 때 구현·검증 내부의 실질적 책임 경계, 분해 생략의 근거, 실제 packet의 반영 여부를 명확히 할지 검토한다. 이번 작업에서 계약을 수정하지 않는다.
- Main 소유: 실제 변경 작업 또는 더 큰 다중 모듈 과제에서 재검증할 때 이번 작은 과제의 결과와 구분한다. 현재 결과를 일반 성능 보장이나 전면 실패로 확장하지 않는다.
- canonical 전체 검사 실패: 지원 interpreter에 setuptools가 준비된 승인된 환경에서 다시 실행해야 한다. 이번 범위에서는 환경을 변경하지 않는다.
- 필수 행동 기준에 FAIL이 남으므로 이 계획은 완료 수락·completed 이동을 하지 않는다. 관찰 실험 종료와 책임 충족 승인을 구분한다.
