---
id: PLAN-2026-0004
kind: exec-plan
status: in-progress
owner: main
area: harness
created: 2026-09-07
updated: 2026-09-07
base_commit: "1d064217da738ebc3ed593ce4aeccf365fb0cd16"
integrated_commit: "72ce34901e8473139691a73f42b919709adaafa0"
verified_commit: ""
traceability: 0
product_spec: ""
verification_run: ""
manifest_sha256: ""
gate_verdict: ""
gate_review_reason: ""
---

# 모델 중립적인 agent 운영 계약 정리

## Purpose / Big Picture

2026-09-07 사용자가 운영 검토 후 업데이트를 승인했다. 현재 계약과 오래된 메모리의 충돌을 제거하고, 모델명 대신 책임·위임 한도·검증 증거로 agent 작업을 운영한다. 선택한 plan만 노출하는 context 정책은 유지하면서 선택 없음과 활성 작업 없음의 표현을 구분한다.

## Progress

- [x] 현행 운영 계약·메모리·실제 실행의 충돌 확인.
- [x] source 및 generated-target 운영 계약과 회귀 테스트 업데이트.
- [x] 잘못된 메모리를 제거하고 사용자 선호를 모델 중립적으로 정리.
- [x] 독립 검토와 clean exact-target canonical verification.
- [ ] T4 추가 승인: Main·Lead 분해 책임과 Verifier의 적극적인 반증 의무 보강 및 새 후보 검증.
- [ ] 공식 close-plan: 이번 추가 요청은 구현 승인이다. 이전 REVIEW 승인이나 공식 closure로 자동 처리하지 않는다.

## Context and Orientation

기준 HEAD는 `1d064217da738ebc3ed593ce4aeccf365fb0cd16`이다. PLAN-2026-0003은 PR4 독립 재검증 및 PR5 migration이 남은 별도 작업이다. 해당 계획의 기존 미커밋 Main 기록을 보존한다. 이번 변경을 PR3–PR5 전체 완료로 보고하지 않는다.

현재 AGENTS/PLANS는 Sub 재위임을 금지하지만 사용자 메모리는 지정된 Task Owner 재위임을 허용한다. 또 과거 제품 메모리는 현재 ADR-0001과 반대되는 runtime 폐기 경계를 기록한다. Root CLAUDE는 현재 AGENTS import adapter이며, source-only portable projection은 PLAN-0003의 별도 미완료 작업이다.

## Scope

- Main, 명시적으로 지정된 Task Lead, Implementer, Independent Verifier의 모델 중립적 책임.
- 최대 Main → Task Lead → leaf 깊이. leaf 재위임 금지. 작은 작업은 불필요한 계층 생략.
- Task Lead는 승인된 parent packet의 권한·예산 안에서 bounded leaf packet 구성·배정·보수 조정·결과 취합을 수행한다. leaf마다 새 승인을 의무화하지 않으며 allowed writes는 parent의 부분집합이고 protected paths/acceptance/stop 조건을 상속한다. 범위/acceptance/권한/최종 통합·승인과 durable plan 편집은 Main 소유.
- 읽기 전용 병렬 작업과 쓰기 병렬 조건을 구분. disjoint paths AND worktrees AND frozen interfaces AND Main 통합/통합 후 검증.
- 실행 환경의 모델·도구·동시성·재시도 예산과 portable 계약 분리. 별도 context 미지원 시 독립 검증을 수행했다고 주장하지 않음.
- 같은 ExecPlan Result 안에서 후보/검증/통합/acceptance/closure 상태와 SHA·범위·명령·환경·근거·blocker를 구분. 새 schema/상태 enum/registry는 만들지 않음.
- Task별 focused 검증과 통합 후보의 canonical 검증 소유권 구분, 짧은 결과 반환, raw transcript/불필요한 대기 polling 금지 안내.
- 메모리는 현행 source of truth와 상위 지시를 덮지 않는 보조 정보로 제한.
- context가 plan 미선택을 설명하고 기존 active 디렉터리 및 `--plan` 사용을 안내. 자동 plan 선택·본문 목록 출력은 추가하지 않음.

## Non-goals

- PLAN-0003의 PR4 transaction 보수나 PR5 DESIGN retirement/source sync 구현.
- provider/model 고정, 새 모델 router·scheduler·task DB·설정 파일·production dependency.
- Gate/CI/approval 정책 완화, REVIEW 이유 조작, 모든 PASS에 사람 승인 추가.
- completed plans/legacy fixtures 수정, 기존 target project-owned 문서 덮어쓰기.
- 새 CLI 옵션, task discovery command, persisted plan schema 변경, push/release.

## Acceptance Criteria

- **AC-1:** source/target 계약이 지정된 Task Lead의 제한된 위임만 허용하고 leaf 재위임·자기 승인·범위 확대를 금지한다. 모델명이 portable 계약에 없다.
- **AC-2:** 병렬 쓰기는 모든 안전 조건을 요구한다. 실행 환경 미지원과 독립 검증 미수행을 명시하고 현재 Gate 승인 경계를 보존한다.
- **AC-3:** Result 및 새 계획 template에 target SHA/검증 범위/환경과 명령/evidence/미해결 사항/승인 구분이 표현되며 기존 계획 parser 및 legacy 계획을 깨지 않는다.
- **AC-4:** plan 미선택 출력은 선택 없음과 작업 없음의 혼동을 제거한다. 선택 밖 plan은 노출하지 않고 명시적 선택/history 동작은 유지한다.
- **AC-5:** 오래된 제품 메모리는 현행 계약을 거스르지 않도록 정리하고, 위임 선호는 모델 중립적이며 새로운 repo 계약을 중복 저장하지 않는다.
- **AC-6:** focused tests, source/template/runtime parity, full check와 exact-target verify가 통과하고 독립 검토 결과가 기록된다.

## Milestones

M1은 운영 계약·선택 안내·메모리의 제한된 업데이트다. M2는 별도 context의 독립 검토와 clean 통합 후보의 canonical 검증이다.

## Task Packets

### T1 — 운영 계약 및 context 안내 구현

#### State

complete

#### Task type

implementation

#### Depends on

none

#### Outcome

AC-1부터 AC-4까지 최소 구현과 회귀 테스트.

#### Non-goals

재위임, 메모리/계획 편집, PR4/PR5, 새 runtime orchestration 또는 schema.

#### Read

이 계획, AGENTS.md, docs/PLANS.md, docs/README.md, docs/DESIGN.md의 Main/Sub 절, source/asset ExecPlan template, packaged AGENTS/PLANS/README template, canonical/dogfood command_context와 관련 tests.

#### Allowed writes

AGENTS.md; docs/PLANS.md; docs/README.md; docs/DESIGN.md의 Main/Sub 참조 문장만; docs/exec-plans/_template.md; src/reporivet/assets/project/root/AGENTS.md.tmpl; src/reporivet/assets/project/docs/PLANS.md.tmpl; src/reporivet/assets/project/docs/README.md.tmpl; src/reporivet/assets/project/docs/exec-plans/_template.md.tmpl; canonical/dogfood dev/harness.py의 plan 안내 출력만; tests/test_authority_lifecycle.py 및 새 tests/test_agent_operating_contract.py; 직접 필요한 test_reporivet.py assertion만.

#### Protected paths

CLAUDE.md, 모든 active/completed 계획, memory, PR4 safety/authority 필터/initializer/Gate/CI/config, PR5 migration, 그 밖의 모든 경로.

#### Acceptance

AC-1, AC-2, AC-3, AC-4, AC-6

#### Verify

`PATH=/tmp/reporivet-pr3-venv/bin:$PATH PYTHON=/tmp/reporivet-pr3-venv/bin/python`에서 focused authority/operating-contract tests, runtime/template parity, `./dev/check`, `git diff --check`.

#### Stop conditions

현재 지시 충돌의 승인된 해소 범위 밖 변경, acceptance 완화, 새 권한/API/schema 필요, 같은 접근 두 번 실패.

#### Result

상태: complete. Main은 독립 검토의 AC-1–AC-4 PASS recommendation과 T3의 clean canonical 검증을 근거로 bounded 구현 acceptance를 승인했다. 이는 human REVIEW 승인이나 공식 closure가 아니다. 후보 SHA: `3e65279becf6ec531176f33a047e14a71c1abefd`, parent `c684de7e006924f3789c9f530530fbd6e105c966`. 14개 허용 경로만 변경했다. 구현자 결과: focused authority/contract/plan/parity 31 tests 및 full check 152 tests 통과, diff check 통과. 환경은 지정한 Python 3.12.14 venv이며 run은 `.harness/runs/20260907T060143037297Z-check`다. 역할 절의 source/target 의미 동일성, leaf 권한 상속, 최대 위임 깊이, 결과 prose, 계획 선택 안내를 업데이트했다. 새 schema/CLI/config 또는 PR4/PR5 변경은 없다. 별도 구현자 보고를 최종 승인으로 취급하지 않는다.

### T2 — 메모리 정리

#### State

complete

#### Task type

support

#### Depends on

none

#### Outcome

현재 계약과 충돌하는 메모리를 제거하고 사용자 선호만 유지.

#### Non-goals

repo 제품 계약의 메모리 복제, 승인되지 않은 사용자 선호 추가.

#### Read

memory/MEMORY.md, subagent-first-main-orchestration.md, productization-scope-balanced.md, avoid-scope-expansion.md 및 현행 ADR-0001.

#### Allowed writes

Main만 기존 memory의 해당 파일과 index를 수정/제거.

#### Protected paths

다른 사용자 메모리·외부 저장소·제품 구현.

#### Acceptance

AC-5

#### Verify

변경 diff 및 memory index target 확인. 모델별 구체 배정은 저장하지 않음.

#### Stop conditions

출처 불명 사용자 선호 또는 현재 요구와의 실제 충돌.

#### Result

상태: complete. Main이 기존 subagent-first 메모리에서 특정 모델 배정·의무적 하위 분해/병렬화·중복 운영 규칙을 제거하고 모델 중립적 역할 선호와 현재 계약 참조만 남겼다. runtime 폐기 등 현재 요구와 충돌하는 productization-scope-balanced 메모리는 읽은 내용과 일치함을 검사한 뒤 삭제했고 MEMORY.md index에서도 제거했다. avoid-scope-expansion 선호는 보존했다. 이 메모리는 Git 외부의 사용자 설정이며 repository 제품 계약을 복제하지 않는다.

### T3 — 독립 검토 및 통합 검증

#### State

complete

#### Task type

verification

#### Depends on

T1, T2

#### Outcome

정확한 후보 commit의 구현·운영 계약 일관성과 non-goals를 검증.

#### Non-goals

구현 수정·자기 승인·Gate 결과를 사람 승인으로 대체.

#### Read

이 계획과 후보 diff/관련 tests/current contracts. memory는 Main이 별도 검사.

#### Allowed writes

독립 verifier는 tracked 쓰기 없음. 임시 fixture/log만. Main만 계획 증거 기록.

#### Protected paths

모든 구현/acceptance/계획.

#### Acceptance

AC-1, AC-2, AC-3, AC-4, AC-5, AC-6

#### Verify

독립 context에서 exact SHA 확인, focused regression 및 계약 검토. Main은 clean 통합 SHA에 explicit base/head로 canonical `./dev/verify` 실행.

#### Stop conditions

target 불일치, 실제 결함, evidence 누락, 사람 이유 없는 REVIEW closure.

#### Result

상태: 검증 complete, 공식 closure는 blocked. 독립 read-only verifier는 exact 구현 후보 `3e65279becf6ec531176f33a047e14a71c1abefd`를 검사하여 AC-1–AC-4 및 focused AC-6 PASS를 권고했고 새 결함은 찾지 못했다. 실행 증거: authority+contract 23, reporivet 36, distribution 1, traceability 4, definition 32 tests 통과. source/template 의미 동일성과 runtime version marker 외 parity도 확인했다. AC-5는 Main의 메모리 검증으로 별도 충족했다.

Main의 canonical run `20260907T060621364377Z-verify`는 base `1d064217da738ebc3ed593ce4aeccf365fb0cd16`에서 clean HEAD `6f80627a388c9a29cb4e0219f4be376d9b299cb8`을 검증했다. 실제/의도 HEAD 일치, clean=true, TARGET_CONFIRMED. 보안·catalog·문서·계획·architecture·project 필수 검사 모두 통과했으며 project는 152 tests/70.038초였다. optional smoke는 미설정으로 skipped. Gate는 shadow REVIEW이며 이유는 RISK_WIDE 및 보호 경로 AGENTS.md/dev/harness.py 변경이다. Main은 구현/검증 evidence를 수락했지만 genuine human REVIEW 사유는 없으므로 close-plan을 실행하지 않았다. 이후 commit은 이 증거의 문서 기록만이며 검증된 코드 후보를 변경하지 않는다.

### T4 — 분해 책임 및 적극적인 반증 검증 보강

#### State

in-progress

#### Task type

implementation

#### Depends on

T3

#### Outcome

2026-09-07 사용자의 추가 승인에 따라 Main의 Task 간 인터페이스·경로 소유권·의존성·통합 순서 설계 책임과 Lead의 parent 내부 leaf 분해 책임을 명시한다. 공유 계약 변경 시 영향 작업 중지·계약 조정·재배정, 상위 경계 변경 시 Main 반환을 명시한다. Verifier는 반례·실패 경로·회귀 및 테스트의 잘못된 가정을 적극 검토하며 결함은 재현 또는 구체적인 코드 근거로 입증한다. 추측·취향·미검증 영역을 결함과 구분하고 finding 개수를 강제하지 않는다. AC-1, AC-2, AC-3, AC-6의 추가 구체화이며 기존 권한을 확대하지 않는다.

#### Non-goals

runtime/Gate/CI/schema 변경, PR4/PR5, 메모리 중복 기록, push 및 공식 closure.

#### Read

AGENTS.md, docs/PLANS.md, source/packaged ExecPlan templates, 대응 AGENTS/PLANS templates, tests/test_agent_operating_contract.py, 이 계획.

#### Allowed writes

AGENTS.md; docs/PLANS.md; docs/exec-plans/_template.md; src/reporivet/assets/project/root/AGENTS.md.tmpl; src/reporivet/assets/project/docs/PLANS.md.tmpl; src/reporivet/assets/project/docs/exec-plans/_template.md.tmpl; tests/test_agent_operating_contract.py. Main만 이 계획을 수정한다.

#### Protected paths

위 허용 경로 외 전체. 구현자는 계획 수정·재위임·최종 승인 금지.

#### Acceptance

AC-1, AC-2, AC-3, AC-6. source/target 의미 일치, 기존 leaf·Main 통합·권한 경계 보존, 분해 책임과 증거 기반 반증 의무의 회귀 검사.

#### Verify

Python 3.12 venv `/tmp/reporivet-pr3-venv`에서 focused contract tests 및 diff check. 별도 context read-only verifier가 정확한 commit과 focused tests로 독립 평가한다. Main은 clean 통합 후보에 canonical verify를 실행한다. 구현·검토는 순차이며 각각 최대 15분, 같은 접근 실패 두 번이면 중지한다. 구현자는 파일 읽기/편집 및 테스트·local candidate commit 도구만 사용한다. verifier는 tracked 쓰기 없이 읽기·테스트만 수행한다.

#### Stop conditions

상위 권한 확대, protected paths 변경 필요, 요구사항 충돌, 같은 접근 두 번 실패. 검증 불가 영역은 명시하며 성공으로 간주하지 않는다.

#### Result

구현 후보: `72ce34901e8473139691a73f42b919709adaafa0` (base `7b018cfceaec7598d7221ef4b6d14f463101c4b4`). 허용된 7개 경로만 변경했다. Python 3.12.14 venv에서 operating-contract focused 6 tests와 diff check 통과. Main은 변경 경로와 diff를 확인했고 별도 context의 read-only verifier에 exact 후보를 전달했다. 독립 평가 및 canonical 결과는 대기 중이며 후보 통합을 acceptance로 간주하지 않는다. 기존 Gate/closure 회귀 9 tests 및 계획 형식 검사도 통과했다. 이전 T1–T3의 증거는 이전 후보에만 적용되며 이번 추가 변경의 검증을 대신하지 않는다.

## Architecture Impact

역할은 문서상 책임이며 실행 engine이 아니다. package/copied runtime 경계, stdlib-only 독립성, Gate를 유지한다.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| AGENTS/PLANS 및 packaged 대응 template | update | 모델 중립적 위임·승인 계약 및 T4 분해·반증 책임 | Main | resolved |
| README/context 및 계획 template | update | 선택 안내·결과 인수인계 | Main | resolved |
| docs/DESIGN Main/Sub 문장 | update | 이번 변경과 상충하는 문구 방지; retirement 아님 | Main | resolved |
| memory 및 index | retire/update | 오래된 제품 경계 제거·선호만 보존 | Main | resolved |

## Interfaces and Dependencies

기존 Task Packet·Markdown Result·context 출력·tests를 재사용한다. 새 dependency/config/public flag/persisted schema 없음. source CLAUDE의 현재 AGENTS import 방향과 target canonical AGENTS를 유지한다.

## Migration, Rollout, and Recovery

기존 계획 metadata 및 historical records를 migration하지 않는다. 신규 init/managed contract update 경로를 사용하고 project-owned 보존 규칙을 바꾸지 않는다. 기존 PLAN-0003 dirty 기록을 별도 보존하고 local commit만 사용한다. memory는 검토된 기존 파일만 정리한다.

## Decision Log

- 2026-09-07 — 사용자 업데이트 승인 범위를 운영 계약·메모리·선택 안내에 한정한다. PR4/PR5 전체 완료를 묵시적으로 포함하지 않는다.
- 2026-09-07 — Main이 직접 bounded 구현과 검증을 위임한다. 아직 적용 전인 Task Lead 규칙으로 먼저 재위임하지 않는다.
- 2026-09-07 — Task Lead는 선택적 역할이고 Main → Lead → leaf만 허용한다. source of truth와 실행 환경의 상위 권한은 구분한다.

## Surprises and Discoveries

- 과거 메모리의 runtime 폐기 및 재위임 규칙이 현행 저장소 계약과 충돌했다.
- 기본 Python은 3.11 미만이므로 검증에 확인된 Python 3.12 venv를 명시한다.

## Concrete Steps

1. `./dev/context --plan PLAN-2026-0004`로 승인 범위를 읽고 T1의 focused 테스트부터 업데이트한다.
2. Main은 T2의 메모리와 index만 정리한다.
3. 구현 후보를 commit한 뒤 독립 검토하고 필요하면 bounded 보수한다.
4. 검증 전 계획 기록을 commit하고 정확한 base/head를 지정해 `./dev/verify`를 실행한다.
5. 승인 조건과 실제 Gate를 기록하며 사람 REVIEW 이유가 없으면 closure는 blocked로 남긴다.

## Validation and Evidence

- 기준 SHA: `1d064217da738ebc3ed593ce4aeccf365fb0cd16`.
- 구현 후보: `3e65279becf6ec531176f33a047e14a71c1abefd`, 독립 검토 완료, 새 결함 없음.
- clean 통합 검증 SHA: `6f80627a388c9a29cb4e0219f4be376d9b299cb8`.
- 보고서: `.harness/runs/20260907T060621364377Z-verify/report.md`.
- Gate: `.harness/runs/20260907T060621364377Z-verify/gate.json`, shadow REVIEW.
- manifest SHA-256: `54209ff1e14266923c3e5e30f45fa1fbee1f2147f049c9e364434cff4cd44da5`.
- 메모리 index 2개 경로 존재, 폐기 메모리 제거, 특정 모델 이름 미포함 검사 통과.
- run artifact는 `.harness/runs/`에 유지하고 raw log는 commit하지 않는다.

## Outcomes and Retrospective

T1–T3의 운영 계약·메모리·context 선택 안내 업데이트와 독립/canonical 검증은 완료했고 Main이 해당 후보의 evidence를 수락했다. 사용자 추가 승인으로 T4를 재개하여 분해 책임과 적극적 반증 의무를 구현했다. 현재 추가 후보의 독립/canonical 검증은 진행 중이며 이전 검증 metadata를 재사용하지 않는다. 기존 parser/schema·Gate·target 소유권·PR4/PR5 경계와 공식 closure 구분을 유지한다.

## Follow-ups

- PLAN-0003의 미완료 PR4 독립 재검증 및 PR5는 별도 작업으로 유지한다.
