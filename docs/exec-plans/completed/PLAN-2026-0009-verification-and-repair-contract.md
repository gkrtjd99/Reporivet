---
id: PLAN-2026-0009
kind: exec-plan
status: completed
owner: main
area: source-contract
created: 2026-09-09
updated: 2026-09-09
base_commit: "226b15af1b8ccf1d82ba410322a214f1f593cc7e"
---

# 검증 판정과 수선 인계 계약 보강

## Purpose / Big Picture

사용자가 승인한 세 항목만 소스 운영 계약과 ExecPlan 양식에 반영한다. 수락 기준의 증거 부족을 실패와 구분하고, 결함 보고에 기존 검사의 사각지대를 설명하며, 수선 요청을 취합해 기존 구현자 문맥을 활용한다.

## Progress

- [x] 현재 계약·계획 양식·계약 테스트와 ZIP 원문을 확인했다.
- [x] 세 항목과 회귀 검사 2개를 반영하고 계약을 동기화했다.
- [x] 통합 후보의 canonical 검사 55개를 통과하고 별도 문맥에서 직접 검토했다.
- [x] 문서 영향과 증거를 확정하고 Main이 AC-1부터 AC-4까지 수락했다.

## Context and Orientation

`CLAUDE.md`의 portable block이 소스이며 `./dev/agent-contract-sync`가 `AGENTS.md`에 투영한다. `docs/PLANS.md`와 `docs/exec-plans/_template.md`는 소스 계획의 정책과 양식이다. `tests/test_agent_operating_contract.py`는 계약의 기계적 회귀를 검사한다. 기존 작업 트리에 대규모 미커밋 변경이 있으며 이를 보존한다. 이번 대상의 수정 전 사본은 세션의 고유 임시 디렉터리에 보관했다.

## Scope

위 다섯 파일과 이 계획만 수정한다. AGENTS는 동기화 도구로만 갱신한다.

## Non-goals

제품 CLI·배포 target·의존성·모델 설정·에이전트 정의·고정 검증 계층·자동 Gate를 바꾸거나 추가하지 않는다. 기존 승인 주체, 독립 검증, 시간·재시도 예산과 중단 조건을 바꾸지 않는다.

## Acceptance Criteria

- **AC-1:** 기준별 PASS/FAIL/UNPROVEN의 의미와 증거, 필수 기준의 FAIL/UNPROVEN이 남을 때 완료 추천 금지, Main/human 승인 소유권이 명시된다.
- **AC-2:** 결함 보고에 기존 검사가 실패 경로를 놓치는 이유 또는 검사 미확인 한계가 포함된다.
- **AC-3:** Main/지정 Lead가 수선 요청을 취합하고 가능한 경우 기존 Implementer를 재개하며, 현재 후보·허용 경로·실패 근거·재검증 대상을 전달한다. 불명확한 원인은 제한된 진단으로 확인하고 기존 예산·두 번 실패 중단 조건을 유지한다.
- **AC-4:** 양식에서 판정을 실제 기록할 수 있고, 동기화와 canonical 검사 및 별도 문맥 검토를 통과한다. 제품 target과 기존 무관한 변경은 보존한다.

## Milestones

### M1 — 기존 계약과 양식의 최소 보강

세 규칙, 판정 표 열, 정책의 이유·대안·재검토 조건, 계약 회귀 검사만 추가한다.

## Task Packets

### T1 — Main의 순차 구현 및 검증

- State: completed
- Task type: implementation
- Depends on: none
- Execution constraints: Markdown/Python 편집과 로컬 검사 능력; Read/Edit/Write/Bash; 순차 쓰기; 같은 접근법 두 번 실패 시 중단; 작업 예산 20분.
- Outcome: AC-1부터 AC-4까지 반영한 후보.
- Non-goals: 위 Non-goals와 동일.
- Read: 위 Context의 다섯 파일과 현재 제품·품질·보안 문서.
- Allowed writes: CLAUDE.md, AGENTS.md(동기화만), docs/PLANS.md, docs/exec-plans/_template.md, tests/test_agent_operating_contract.py, 이 계획.
- Protected paths: 나머지 모든 경로와 기존 무관한 변경.
- Acceptance: AC-1, AC-2, AC-3, AC-4.
- Verify: `./dev/agent-contract-sync`, `PYTHON=python3 ./dev/check`.
- Stop conditions: 승인 범위 초과, 요구 충돌, 같은 접근법 두 번 실패.
- Result: 완료. 대상 다섯 파일의 최소 추가분과 이 계획만 작성했다. AGENTS는 동기화했다. 아래 정확 후보에서 Python 3.13 임시 환경의 canonical 검사 55개와 투영·compileall·diff 검사가 통과했다. Main이 증거를 수락했다.

### T2 — 별도 문맥의 통합 후보 검토

- State: completed
- Task type: verification
- Depends on: T1
- Execution constraints: 문서 계약과 테스트를 반증하는 능력; 읽기 전용 도구; 쓰기·재위임 금지; 검토 1회와 필요 시 수정 후보 재검토; 5분.
- Outcome: exact candidate에 대한 독립 검토 추천. Main이 별도 수락한다.
- Non-goals: 제품 동작 및 기존 변경 전체 리뷰.
- Read: T1 대상, 이 계획, 수정 전 사본과 후보 fingerprint.
- Allowed writes: 없음.
- Protected paths: 모든 파일.
- Acceptance: AC-1부터 AC-4까지.
- Verify: 이번 diff와 현재 계약, 테스트 가정, 판정 및 승인 경계 확인.
- Stop conditions: 후보 변경, 권한·범위 충돌, 근거 부족.
- Result: 별도 문맥의 직접 검토에서 구체 결함 없음. 검토 시작·종료의 다섯 파일 hashes 일치와 전체 manifest 일치를 확인했고 55개 unittest, sync check, diff check, 메모리 내 compile이 통과했다. AC-1/2/3은 PASS, AC-4는 canonical 자체 실행과 범위 밖 수정 전 사본 부재 때문에 UNPROVEN으로 반환하여 완료 추천을 보류했다. Main은 자신이 실행한 동일 후보의 canonical 성공 결과와 실제 쓰기 이력·대상별 수정 전후 diff로 AC-4를 별도 확인하고 수락했다. 검토자의 보류를 PASS 추천으로 바꾸어 기록하지 않는다.

## Architecture Impact

없음. 소스의 문서 운영 계약만 보강하고 installed CLI와 target 경계를 유지한다.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| CLAUDE.md / AGENTS.md | update / sync | 세 운영 규칙 | Main | resolved |
| docs/PLANS.md | update | 계획의 판정·수선 정책과 이유 | Main | resolved |
| docs/exec-plans/_template.md | update | 규칙을 적용할 양식 | Main | resolved |
| docs/PRODUCT.md / ARCHITECTURE.md / docs/QUALITY.md / docs/SECURITY.md | none | 제품·구조·기존 품질 및 보안 경계 불변 | Main | resolved |

## Interfaces and Dependencies

Main이 순차 통합한다. 외부 의존성과 신규 인터페이스는 없다. 기존 계약 테스트와 동기화 도구를 재사용한다.

## Migration, Rollout, and Recovery

공개 API·영속 데이터 migration은 없다. 기존 완료 계획은 수정하지 않는다. 복구가 필요하면 이번 추가분만 되돌리고 기존 미커밋 변경은 보존한다.

## Surprises and Discoveries

- 2026-09-09 — 기존 작업 트리 변경을 발견했고 이번 대상의 수정 전 bytes를 고유 임시 경로에 보존했다.

## Decision Log

- 2026-09-09 — 사용자가 세 항목의 반영을 승인했다. ZIP 전체 설치·고정 역할 추가 대신 기존 계약과 양식을 보강한다. 정책 이유·대안·재검토 조건은 docs/PLANS.md에 둔다.

## Concrete Steps

1. 기존 파일에 세 규칙과 양식 판정 열을 추가한다.
2. 계약 회귀 검사를 추가하고 동기화한다.
3. canonical 검사를 수행하고 후보 fingerprint를 기록한다.
4. 독립 검토 후 증거와 문서 영향을 확정한다.

## Validation and Evidence

| Acceptance criterion | Task | Result | Evidence path or note | Verified candidate | Reviewer recommendation | Main/human approval |
|---|---|---|---|---|---|---|
| AC-1 | T1/T2 | PASS | 계약·정책·양식의 판정 정의와 완료 추천 금지, 회귀 검사 | 아래 후보 | PASS | Main 수락 |
| AC-2 | T1/T2 | PASS | 세 문서의 검사 사각지대/미확인 한계 문구, 회귀 검사 | 아래 후보 | PASS | Main 수락 |
| AC-3 | T1/T2 | PASS | 수선 인계·예산·진단·독립 검증 유지, 회귀 검사 | 아래 후보 | PASS | Main 수락 |
| AC-4 | T1/T2 | PASS | 표 구조 검사, canonical 55개 성공, 쓰기 이력과 이번 diff 확인 | 아래 후보 | UNPROVEN 반환; T2 한계 참조 | Main이 부족 증거를 별도 확인하고 수락 |

### 정확 후보

Base는 frontmatter의 SHA다. 아래 구현·문서 다섯 파일의 mode는 모두 `0644`이고 이번 작업으로 삭제한 기존 파일은 없다. 이 계획의 완료 기록·이동은 검토 후의 증거 정리이며 검토 대상 다섯 파일을 변경하지 않는다.

| Path | SHA-256 |
|---|---|
| CLAUDE.md | `3de67f22ee59b3f5c539ae45862193c954f4f836d9ce121778a21e9945cc914c` |
| AGENTS.md | `d3c0c411fbf75111e57fa5099733e05026103b395e8c9c0a749a3a6511c67602` |
| docs/PLANS.md | `091f7f5d73c4353fa9207b950a924cff8899344a521bb78d09ffb4784ad684e6` |
| docs/exec-plans/_template.md | `692c0898895490f8a6cc6841f9334584c2023a229f859c31cb7d02055d4613e8` |
| tests/test_agent_operating_contract.py | `38b138f098d6802f53aea225b35efacf02148daee54034588228204062eb736b` |

전체 nonignored 69개 파일의 hashes/modes 및 기존 삭제 목록을 포함한 검토 시점 manifest의 SHA-256은 `8e134c2dcbd7dc9be41c103b3dd79da7772160d7487ef1bc7946ec8b4e40aab1`이다. 세션 임시 사본 디렉터리 `/var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-verification-contract-ky0u8ke2`의 `candidate.json`에 저장했고 독립 검토자가 전체 일치를 확인했다. 임시 사본은 영구 배포 자산이 아니다. fingerprint는 승인 자체가 아니다.

### 명령과 환경

- `./dev/agent-contract-sync` 및 `./dev/agent-contract-sync --check`: 성공.
- `PYTHON=python3 ./dev/check`: 기본 Python 3.9.6이 최소 3.11 미만이어서 실행 전 실패.
- `PYTHON=/opt/homebrew/bin/python3.13 ./dev/check`: 55개 중 distribution 검사 1개 실패. 원인은 환경의 `setuptools.build_meta` 부재이며 테스트를 skip하거나 약화하지 않았다.
- 새 고유 임시 venv에 빌드 도구를 설치했다. Python 3.13.15, pip 26.2, setuptools 84.0.0, wheel 0.48.0, packaging 26.3. 프로젝트의 의존성 파일과 전역 Python은 수정하지 않았다.
- `PYTHON=/tmp/reporivet-contract-check-BnWc7p/bin/python ./dev/check`: exit 0, 55개 tests PASS, contract drift·compileall·git diff --check PASS. 완료 기록·이동 후에도 검토한 다섯 파일의 hashes 일치를 확인하고 같은 명령을 재실행하여 exit 0, 55개 PASS를 확인했다.
- 독립 검토자는 같은 Python으로 unittest 55개, sync check, diff check, 메모리 compile을 별도 수행했고 모두 성공했다. canonical 전체 실행과는 구분한다.

### 범위와 검토 한계

Main의 실제 편집은 허용된 다섯 파일과 이 계획뿐이며 제품·설정·기존 무관한 변경을 수정한 명령은 실행하지 않았다. 다섯 파일의 수정 전 사본 대비 diff는 세 규칙과 관련 검사에 한정된다. 검토자는 범위 밖의 구현 전 사본을 받지 않았으므로 범위 보존을 독립적으로 입증했다고 주장하지 않는다.

검토자가 스킬 호출 과정에서 의도치 않은 배경 검토 에이전트를 생성했다가 즉시 중단했고 결과를 사용하지 않았다고 보고했다. 재위임 금지의 절차 이탈은 기록하되, 실제 근거는 그 검토자 자신의 별도 문맥 직접 검토·명령·후보 일치 확인만 수락한다. 쓰기나 하위 결과 의존이 없고 후보가 유지되었으므로 Main은 추가 검토를 요구하지 않았다.

## Outcomes and Retrospective

세 항목을 기존 계약·정책·양식에 반영하고 회귀 검사 2개를 추가했다. 독립 검토에서 구체 결함은 없었으며 Main이 검사와 범위 증거를 보완하여 모든 수락 기준을 승인했다. 기계적 테스트는 실제 agent의 판정 품질이나 토큰·시간 효율 향상을 증명하지 않는다. 별도 에이전트 묶음과 제품 target 변경은 없다.

## Follow-ups

없음.
