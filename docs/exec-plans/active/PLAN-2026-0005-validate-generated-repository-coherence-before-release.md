---
id: PLAN-2026-0005
kind: exec-plan
status: in-progress
owner: main
area: harness
created: 2026-09-07
updated: 2026-09-07
base_commit: "58665a897b891b0abc721e159593725c0b71af6d"
integrated_commit: "58665a897b891b0abc721e159593725c0b71af6d"
verified_commit: ""
traceability: 0
product_spec: ""
verification_run: ""
manifest_sha256: ""
gate_verdict: ""
gate_review_reason: ""
---

# 생성 저장소의 배포 전 논리 정합성 검증

## Purpose / Big Picture

사용자는 배포 전에 생성되는 저장소가 논리적으로 타당하고 문제를 일으킬 지점이 없는지 검증을 요청했다. 현재 코드 후보를 실제 생성 결과와 독립 반증으로 평가하고 배포 판단에 필요한 확인된 결함·제약·미검증 영역을 보고한다. 이 계획은 검증 기록이며 제품 수정이나 배포 승인이 아니다.

## Progress

- [x] clean 코드 후보와 제품 요구사항 및 검증 범위 고정.
- [x] 생성 문서·설정·명령의 의미 정합성 검토.
- [x] 초기화·정의·adoption·upgrade의 bounded 실패 경로 반증. 추가 raw-path 후보는 시간 한도로 미확정.
- [x] 실제 배포 wheel과 package 제거 후 생성 저장소 실행.
- [x] Main의 확인된 세 결함 재현·증거 수락 및 배포 보류 권고 확정.
- [ ] 공식 종료: 별도 canonical evidence-bound closure는 실행하지 않았다. 평가 완료와 배포 승인·결함 보수 완료를 구분한다.

## Context and Orientation

코드 대상은 `58665a897b891b0abc721e159593725c0b71af6d`다. PLAN-0002/0003/0004는 공식 종료됐다. PLAN-0002/0003 종료 검증은 각각 168 tests, PLAN-0004는 당시 155 tests 및 필수 검사를 통과했다. 이 검토는 이전 통과를 되풀이하는 대신 테스트가 놓친 생성 결과의 의미·운영 실패를 찾는다. 권위는 docs/PRODUCT.md, SPEC-REPORIVET-001/002, QUALITY/SECURITY, ADR-0001이다. generated target은 AGENTS canonical이며 source-only CLAUDE/helper가 포함되지 않는다. runtime은 package 제거 후 standalone stdlib로 동작해야 한다.

## Scope

- 여섯 project kind 및 explicit document capabilities의 생성 결과.
- AGENTS/knowledge map/초안/계획/optional 문서/설정/실제 runtime의 모순 및 막힌 운영 흐름.
- empty/기존 구현 초기화, define start/resume/finalize, audit/adoption, repeat init/upgrade, 사용자 bytes 보존.
- wheel offline build/install/uninstall, 생성 target의 명령과 Git-bound Gate 흐름.
- 구체적인 재현 및 코드 근거가 있는 결함과 단순 한계·취향을 구분.

## Non-goals

- 코드·테스트·템플릿·설정·CI 수정, 결함 자동 보수, acceptance 완화.
- push/release/publication/deployment, 외부 저장소 작업, 새 dependency.
- 모델 실행 성능 평가, 실제 사용자 product 의도 발명, OS-level 완전 동시성 안전 주장.
- 완료된 계획 재작성, 새 task registry 또는 orchestration infrastructure.

## 승인된 보수 단계 — 2026-09-07

사용자가 평가 보고 후 “배포전에 보수, 재검증할거 처리해”라고 요청했다. 이후 단계 T5/T6에서는 위 검증 전용 Scope/Non-goals 중 제품 보수 금지를 해제하고 아래 명시 경로의 보수·회귀·독립 검증을 허용한다. T1–T4 결과는 보수 이전의 역사적 평가다. 배포·push·dependency·새 public API·persisted schema 변경 금지는 유지한다. Main은 단일 구현 leaf 이후 후보를 검토·통합·local commit하고 새 exact 후보에 독립 검증과 explicit-target canonical verify를 수행한다. REVIEW는 사용자 수락을 발명하지 않고 그대로 보고한다.

현재 제약은 기존 metadata/config authority와 managed block 바깥 bytes 보존, source-bearing empty verification 거부를 복원하는 것이다. 기존 preserving updater와 source detection 시설을 먼저 재사용한다. no-change는 확인된 결함을 남기므로 기각하고 새 범용 scanner·설정/schema·dependency 추가는 현 요구에 불필요하므로 기각한다. source detection은 실행 명령 추론이나 authority 승격을 하지 않는다. 회귀 테스트가 enforcement이며 향후 소유권·source 계약이 명시 변경될 때만 재검토한다. 새 외부 기술 선택은 없다.

문서 영향: Main이 이 계획의 결과/근거를 갱신한다. runtime의 현행 의미를 설명하는 문서 수정이 실제 필요하면 Main이 해당 현행 문서만 검토 후 갱신한다. completed 문서는 변경하지 않는다. 기본 보수는 기존 계약 복원이므로 migration/schema 변환은 없으며 source/package runtime 동기화와 신규 생성·upgrade 경로를 검증한다. rollback은 이 bounded 변경의 정상 revert이며 사용자 문서·설정 변환을 요구하지 않는다.

## Acceptance Criteria

- **AC-1:** 생성 문서의 논리 정합성을 실제 산출물과 canonical 요구사항/명령에 대조한다.
- **AC-2:** 핵심 lifecycle과 사용자 authority 보존의 정상·실패 경로를 직접 확인한다.
- **AC-3:** 실제 wheel 및 package 제거 후 동작과 기존 suite 범위·한계를 기록한다.
- **AC-4:** 모든 결함에는 exact target, trigger, 요구 위반, 영향, 재현 명령 또는 구체 코드 근거를 기록하고 Main이 수락 여부를 판단한다.

- **AC-5:** ordinary define와 재초기화/upgrade는 기존 config의 name/summary를 존중하고 AGENTS/.gitignore 관리 블록 밖 bytes를 보존한다. 관련 실패 회귀와 반복 실행 대조군이 통과한다.
- **AC-6:** root-level 구현이 있는 프로젝트에서 빈 check/verify 명령은 명시적으로 실패하고, 실제 빈 프로젝트와 명시된 정상/실패 명령의 기존 동작을 유지한다. source detection은 문서·config authority를 변경하지 않는다.
- **AC-7:** raw symlink/.. 후보를 확정/기각하고 확인된 경로 계약 위반은 거부 회귀로 보수한다. 신규 후보의 전체 suite, 독립 검토, actual wheel/standalone 및 Main canonical 결과를 기록한다. 미실행 플랫폼/외부 CI/배포는 통과로 주장하지 않는다.

## Milestones

### M1 — 독립 읽기 전용 반증

세 leaf가 고정 코드 후보를 각자 임시 fixture에서 검증한다. source tracked 쓰기는 없으며 Main만 이 계획을 편집한다.

### M2 — 근거 수락과 보고

Main이 finding을 재현하거나 별도 반증하여 결함과 한계를 구분하고 배포 전 판단을 보고한다. 수정은 사용자의 별도 요청 이후 작업이다.

## Task Packets

### T1 — 생성 운영 계약의 의미 정합성

#### State

complete

#### Task type

verification

#### Depends on

none

#### Execution constraints

- Required capabilities: 문서·제품 계약과 Python CLI를 비교하는 독립 반증.
- Tool access: read/Git/Python, 임시 fixture만 쓰기.
- Concurrency: T2/T3와 읽기 전용 병렬, shared source 변경 금지.
- Retry budget: 동일 접근 두 번 실패 시 중지.
- Time budget: 12분.

#### Outcome

생성 문서를 따라 작업할 때의 모순, 잘못된 authority 승격, 막힌 계획/문서 흐름을 재현한다.

#### Non-goals

코드 수정, 단순 문체·취향 finding, 재위임.

#### Read

이 계획, PRODUCT/SPEC-001/002, packaged AGENTS/docs/templates, initializer의 관련 렌더 지점, 실제 generated 결과.

#### Allowed writes

자신의 임시 fixture와 로그만. Main이 결과를 이 계획에 기록한다.

#### Protected paths

모든 tracked 파일과 다른 task fixture.

#### Acceptance

AC-1, AC-4

#### Verify

service/web/library/CLI 등 실제 생성 결과의 config/docs/context/계획을 대조하고 문서가 지시하는 경로를 실행한다. 테스트 자체의 가정도 의심하며 finding 수를 강제하지 않는다.

#### Stop conditions

exact target 불일치, 외부 접근/수정 필요, 범위 확장 또는 제품 authority 충돌.

#### Result

exact `58665a897b891b0abc721e159593725c0b71af6d`의 독립 archive에서 fixture 8개(기본 six-kind, 기존 구현 CLI, explicit 4 capabilities library)를 생성하고 repository-local 명령 43회를 실행했다. optional taxonomy/config 일치, source-only CLAUDE 미포함, dangling core-beliefs 참조 없음, draft의 기본 authority 제외, explicit definition→active SPEC/첫 proposed plan→context/문서/계획 검사 정상. synthetic 제품 정의는 기존 test fixture를 복사하지 않았고 validator의 필드 오류 안내를 따라 수정 후 finalize했다. 새로운 confirmed semantic blocker는 없다는 recommendation을 Main이 검토 범위에서 수락한다. greenfield config의 PLAN-0000 완료 안내와 해당 계획 미생성 불일치는 문서 안내 공백으로 기록하지만 실제 dead end는 미확정이다. 초기 parent 미존재 오류는 별도 운영제약으로 분리한다. 환경 Darwin/Python 3.12, tracked 쓰기 없음. 근거: `/private/tmp/reporivet-t1-8rqa4B/experiment.py`, `experiments.json`, `definition-corrected.json`. 실제 구현 완료→baseline established→장기간 문서 retirement는 이 task에서 실행하지 않았다.

### T2 — lifecycle과 authority 보존 반증

#### State

complete

#### Task type

verification

#### Depends on

none

#### Execution constraints

- Required capabilities: Python filesystem/lifecycle 실패 재현 및 ownership 분석.
- Tool access: read/Git/Python, 임시 fixture만 쓰기.
- Concurrency: T1/T3와 읽기 전용 병렬.
- Retry budget: 동일 접근 두 번 실패 시 중지.
- Time budget: 12분.

#### Outcome

init/define/adopt/upgrade의 현실적인 상태 전이에서 데이터 손실·잘못된 authority·사용 불가 상태를 찾는다.

#### Non-goals

구현·보수, OS-level arbitrary race 보장, 재위임.

#### Read

이 계획, initializer/CLI/canonical runtime의 관련 ownership/lifecycle, tests/definition/audit/authority/upgrade fixtures, SECURITY/SPEC-001/002.

#### Allowed writes

자신의 임시 fixture와 로그만.

#### Protected paths

모든 tracked 파일과 다른 task fixture.

#### Acceptance

AC-2, AC-4

#### Verify

재실행·legacy upgrade·custom authority/config·explicit capability 전이·definition handoff를 반증한다. 기존 guard 통과를 안전성 전체로 확대하지 않는다.

#### Stop conditions

exact target 불일치, 실제 사용자 파일 쓰기 필요, 미승인 외부 작업.

#### Result

독립 verifier가 전달한 metadata reset 및 managed block 밖 bytes 변경 두 finding을 Main이 exact archive `/private/tmp/reporivet-release-main-qzNM3B`와 `/tmp/reporivet-t2-58665a/probe.py`로 재현해 수락했다. Main 결과는 `/private/var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-t2-probe-_ckev1ku/results.json`에 있다. ordinary define은 exit 0/config bytes 보존에도 AGENTS name/purpose를 기본값으로 되돌렸다. init/upgrade는 AGENTS/.gitignore의 사용자 CRLF prefix/suffix bytes를 바꿨고 define --adopt 대조군은 보존했다. capability 활성화 후 upgrade는 선택 문서를 생성하며 config를 보존했고, 비활성화 후에도 사용자 문서를 보존했다.

추가로 `initializer.py:360–377`의 abspath 선행 정규화가 symlink/.. 검사를 우회하는지 최대 3분의 bounded 실험을 요청했으나 최종 재현 결과가 반환되지 않았다. Main은 시간 한도 종료로 leaf를 중단했다. 해당 후보는 실제 wrong-root 쓰기가 확인되지 않았으므로 결함 수에 포함하지 않는다. T2 complete는 확보된 근거의 평가 종료이며, 전체 filesystem 안전성이나 미완료 추가 실험의 통과를 뜻하지 않는다. 최종 leaf 보고는 수신하지 못했고 중간 두 finding과 Main 재현만 수락했다.

### T3 — 배포 산출물과 standalone 실행

#### State

complete

#### Task type

verification

#### Depends on

none

#### Execution constraints

- Required capabilities: offline Python packaging 및 실제 generated CLI/Git fixture 검증.
- Tool access: read/Git/Python/local wheel build/install/uninstall, 전용 임시 환경만 쓰기.
- Concurrency: T1/T2와 읽기 전용 병렬.
- Retry budget: 동일 접근 두 번 실패 시 중지.
- Time budget: 12분.

#### Outcome

실제 wheel 설치로 생성한 target의 required docs/명령·package 제거·plan/Gate 흐름과 배포 제한을 확인한다.

#### Non-goals

네트워크 설치/외부 CI/배포, system environment 변경, 재위임.

#### Read

이 계획, pyproject, tests/test_distribution.py와 관련 matrix, packaged assets/wrappers/CI, QUALITY의 release gate.

#### Allowed writes

자신의 임시 archive/build/venv/fixture/log만.

#### Protected paths

모든 tracked 파일과 다른 task fixture, 시스템 Python 환경.

#### Acceptance

AC-3, AC-4

#### Verify

exact archive에서 전체 suite를 실행하고 offline wheel build/install/uninstall 및 실제 target 명령을 추가로 검증한다. baseline suite와 독립 추가 실험을 구분한다.

#### Stop conditions

필수 tool 부재, 네트워크/새 dependency 필요, target 불일치.

#### Result

exact archive `/private/tmp/reporivet-t3-zNDaPm/archive`, Darwin arm64/Python 3.12.14에서 `python -m unittest discover -s tests -v` 신규 실행: 168 tests OK/71.687초. offline `pip wheel --no-build-isolation --no-deps --no-index`와 새 venv 설치, packaged assets 38개 inventory 통과. 추가 10개 시나리오군: 4-kind wheel 생성, root-level/src 구현 전이, 실패/성공 configured command, 기존 Python inference review→실제 unittest, explicit define/audit, package uninstall/import 불가 확인 뒤 standalone verify/audit/context/garden/define, Git-bound plan/task/close-plan PASS, generated CI shell의 explicit HEAD 성공 및 mismatch exit 2. 초기 orchestration의 /tmp symlink와 init 직후 definition draft가 있다는 잘못된 fixture 가정 두 건은 제품 결함이 아니며 같은 script 재시도는 중지했다.

finding: 빈 CLI 생성 뒤 root main.py를 추가해도 check/verify exit 0이고 project skipped다. Gate는 REVIEW이지 PASS가 아니다. source=[src] 경로 존재만 검사해 empty command guard가 누락된다. Main은 별도 exact archive와 자체 script로 syntax-invalid main.py, clean explicit Git target에서도 동일 결과를 확인했다. configured src/main.py와 code-map 갱신 대조군은 빈 check command를 exit 2로 거부했다. 명시적 source/command 설정은 운영자 의무지만 현재 SPEC-001:139의 일반적인 source-bearing empty verification 거부 보장은 이 경로에서 성립하지 않는다. Main은 P2 검증 누락 finding을 수락한다.

로그/재현: `/private/tmp/reporivet-t3-zNDaPm/unittest.log`, `direct.py`, `direct.log`, `operations/direct-logs/`, `reproduce-root-source.sh`, `reproduce-root-source.log`; Main `/private/tmp/reporivet-release-main-qzNM3B-source-guard-probe.py`, fixture `/private/var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-main-source-guard-_9azyz2w/cli`. 실제 source canonical·외부 Actions·release를 실행한 것으로 주장하지 않는다.

### T4 — Main 증거 수락과 배포 전 평가

#### State

complete

#### Task type

verification

#### Depends on

T1, T2, T3

#### Execution constraints

- Required capabilities: 범위 조정, finding 재현, 증거 통합 및 위험 평가.
- Tool access: read/Git/Python/임시 fixture, 이 계획만 편집.
- Concurrency: source 쓰기는 Main의 계획 기록만 순차.
- Retry budget: 같은 재현 접근 두 번 실패 시 미확인으로 구분.
- Time budget: 15분.

#### Outcome

확인된 결함·비결함·잔여 한계를 구분한 최종 평가를 보고한다.

#### Non-goals

수정 또는 배포, 테스트 통과만으로 의미적 정확성 승인.

#### Read

각 task 결과와 특정 finding 코드/fixture, 이 계획.

#### Allowed writes

이 계획과 Main 전용 임시 fixture/log.

#### Protected paths

코드·테스트·templates·config·CI·completed history·외부 저장소.

#### Acceptance

AC-1, AC-2, AC-3, AC-4

#### Verify

원 reproducer 또는 별도 최소 fixture를 실행하고 exact source 근거를 대조한다. canonical 검증을 실행하지 않은 경우 이전 run을 신규 실행처럼 보고하지 않는다.

#### Stop conditions

사용자 의미 판단 필요, 범위 확장, 실제 수정 필요.

#### Result

Main은 독립 T1/T3 결과와 T2 중간 findings를 검토하고 세 P2를 exact candidate의 별도 fixture에서 재현했다. generated taxonomy/authority 분리/definition handoff/standalone 운영은 검증 범위에서 정합하지만, 정상 명령에서의 agent contract metadata 불일치, 사용자 소유 bytes 변경, source-bearing empty verification 누락이 남는다. 따라서 현재 후보의 배포 보류를 권고한다. 이는 공식 Gate BLOCK 판정이나 외부 배포 승인 철회가 아니라 검증자의 제품 준비도 평가다. 낮은 우선순위 두 사항과 미확정 raw-path 후보를 결함과 분리했다. 제품 코드는 수정하지 않았다. 신규 source canonical 검증 및 formal close-plan은 실행하지 않았으므로 계획은 blocked로 남긴다.

### T5 — 배포 전 보수와 회귀 테스트

#### State

in-progress

#### Task type

implementation

#### Depends on

T4

#### Execution constraints

- Required capabilities: Python initializer/runtime의 파일 소유권·검증 보수와 실패 테스트 작성.
- Tool access: read/edit/local Git diff/Python tests, 외부 접근 없음.
- Concurrency: 단일 Implementer의 순차 쓰기. Main은 구현 중 tracked 파일을 쓰지 않는다.
- Retry budget: 같은 접근 두 번 실패 시 Main에게 반환.
- Time budget: 35분.

#### Outcome

확인된 세 결함을 failing regression으로 고정하고 최소 보수한다. raw symlink/.. 후보를 임시 fixture로 확인하고 실제 거부 계약 위반이면 같은 파일 안전 경계 안에서 회귀·보수한다. nested root와 PLAN-0000 안내는 기존 기능으로 해결되는 최소 국소 보수만 허용한다.

#### Non-goals

새 public API/설정/schema/dependency/CI 변경, 광범위 리팩터링, 외부 배포, 재위임, 계획 편집, commit.

#### Read

이 계획, PRODUCT/SPEC-001/002, SECURITY/QUALITY, module contract, initializer/runtime 및 관련 tests. source runtime은 packaged asset과 일치해야 한다.

#### Allowed writes

`src/reporivet/initializer.py`, `src/reporivet/assets/project/dev/harness.py`, `dev/harness.py`, `tests/test_reporivet.py`, `tests/test_definition.py`, `tests/test_audit_adoption.py`, `tests/test_verification_run.py`, `tests/test_distribution.py`. 추가 경로가 필요하면 쓰지 않고 Main에게 반환한다.

#### Protected paths

위 목록 외 모든 tracked 파일, 사용자 데이터, completed 계획, 외부 저장소, 설정·CI·AGENTS/CLAUDE.

#### Acceptance

AC-5, AC-6, AC-7

#### Verify

각 보수 전 실패와 보수 후 성공을 기록한다. define/re-init/upgrade의 config metadata/사용자 bytes 보존, empty/source-bearing/configured command 대조군, raw-path 거부/일반 경로 성공을 확인한다. focused tests 및 전체 suite를 실행한다.

#### Stop conditions

새 public contract/권한 변경 필요, 확인하지 못한 원인에 대한 보수, protected path 쓰기 필요, 같은 접근 두 번 실패.

#### Result

보수 진행 중. Implementer 결과는 후보이며 수락이 아니다.

### T6 — 독립 후보 반증과 배포 산출물 재검증

#### State

blocked

#### Task type

verification

#### Depends on

T5

#### Execution constraints

- Required capabilities: 독립 filesystem/CLI 반증, offline wheel 검증.
- Tool access: exact Git archive 읽기, 전용 임시 fixture/venv/log만 쓰기.
- Concurrency: 구현 종료 후 실행. Main 최종 canonical과 읽기 전용 병렬 허용.
- Retry budget: 같은 접근 두 번 실패 시 보고.
- Time budget: 25분.

#### Outcome

Main이 지정한 exact commit에서 요구사항과 실제 사용 경로를 독립 검증하고 결함과 한계를 구분한다.

#### Non-goals

구현 설명에 의존한 승인, source 쓰기, 재위임, 외부 서비스, 배포 승인.

#### Read

exact candidate, AC-5/6/7, 현행 요구사항, 실제 wheel/fixture. 구현자의 설명 대신 코드와 실험을 근거로 판단한다.

#### Allowed writes

자신의 임시 archive/venv/fixture/log만.

#### Protected paths

모든 source tracked 파일 및 다른 task fixture.

#### Acceptance

AC-5, AC-6, AC-7

#### Verify

세 결함의 반례 및 경로 거부 대조군, actual offline wheel build/install/uninstall, package 없는 runtime 실행과 전체 suite 범위를 확인한다. Main이 exact target과 recommendation을 수락한다.

#### Stop conditions

exact target 불일치, 외부 설치 필요, 허용 경계 변경 필요.

#### Result

후보 고정 대기.

## Architecture Impact

없음. 현행 계약과 산출물을 읽기 전용 검증하며 구현·의존성은 변경하지 않는다.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| 이 ExecPlan | create/update | 고정 후보·검증 범위·재현 근거·후속 보수 판단 보존 | Main | resolved |
| 제품·설계·template·completed 계획 | none | 검증만 요청받았으므로 수정하지 않음 | Main | resolved |

## Interfaces and Dependencies

Main은 세 읽기 전용 task의 관심사를 분리하고 결과 중복을 제거한다. 공유 계약과 exact 후보는 고정한다. leaf 재위임 금지. 별도 임시 fixture 외 병렬 쓰기 없음. 기존 scanner/runtime/test/build facilities를 재사용하며 production dependency 추가 없음.

## Migration, Rollout, and Recovery

해당 없음. 실제 repo/사용자 데이터/배포를 변경하지 않는다. 실패 실험은 전용 임시 디렉터리에만 한정한다.

## Surprises and Discoveries

- 기존 168 tests와 실제 wheel/package-removal은 통과했지만 추가 정상 사용 경로에서 아래 결함을 발견했다. suite 통과를 생성 결과 전체의 의미적 타당성으로 확대하지 않는다.
- P2 — 기존 init의 name/summary를 ordinary define이 AGENTS에서 root.name/목적 입력용 placeholder로 되돌린다. config는 보존돼 두 운영 안내가 서로 달라진다. `initializer.py:2621–2634`, `2420–2434`, `2450–2459`. Main의 별도 exact fixture에서도 define exit 0 및 config preserved true, AGENTS default reset을 확인했다.
- P2 — 일반 init/upgrade의 AGENTS/.gitignore 갱신이 managed block 밖 CRLF·말단 whitespace를 바꾼다. `initializer.py:589–619`, `626–638`, `2452–2463`. 경계 밖 bytes 보존 계약 위반이며 adopt 대조군은 원본을 보존한다. Main도 재현했다.
- P2 — root main.py가 생겨도 source=[src]만 검사해 빈 project verification이 skipped/exit 0이 된다. `initializer.py:741–743`, packaged runtime `4771–4772`, `4949–4962`. Main의 clean explicit-target 재현은 Gate REVIEW였으며 PASS 또는 테스트 실행으로 과장하지 않는다.
- 낮은 우선순위 운영제약 — 부모 directory가 없는 nested --root는 init exit 2/mutation rolled back이며 부모를 만든 뒤 같은 명령은 성공했다. Main fixture `/private/var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-main-nested-root-wndm3ogr`. 데이터 손실은 관찰하지 않았다.
- 문서 안내 공백 — greenfield config는 PLAN-0000 완료를 지시하지만 빈 프로젝트에는 해당 계획이 생성되지 않는다. `initializer.py:1157`, `2523`. 실제 운영 불가능한 dead end는 미확정이다.

## Decision Log

- 2026-09-07 — 사용자 요청은 배포 전 검증이다. no-change 평가를 기본으로 하며 자동 보수·새 infrastructure·배포는 제외한다. 이유는 문제 확인과 변경 승인을 분리하고 검증 대상 bytes를 고정하기 위함이다.

## Concrete Steps

1. 고정 exact 후보와 사용자 요청을 각 bounded leaf에 전달한다.
2. 실제 generated fixtures와 wheel 기반 검증을 실행한다.
3. Main이 finding을 재현하고 결과/한계를 이 계획에 기록한다.
4. 구현 수정 없이 배포 전 평가를 보고한다.

## Validation and Evidence

- Exact product target: `58665a897b891b0abc721e159593725c0b71af6d`.
- 환경: Darwin arm64, Python 3.12.14 `/tmp/reporivet-pr3-venv`.
- 이전 canonical 168 tests 통과는 기존 근거이며 이번 신규 실험과 구분한다.
- 신규 명령/fixture/검증 결과는 각 Task Result에 기록한다.

## Outcomes and Retrospective

배포 전 bounded 평가는 완료했다. 기본 생성 구조, authority 분리, 실제 wheel와 package 없는 runtime은 검사 범위에서 정상이다. 그러나 Main 재현이 있는 세 P2 때문에 현재 후보의 배포는 보류하는 편이 타당하다. 전체 168 tests 통과는 이 세 실패 경로를 배제하지 못했다. 이 판단은 release readiness recommendation이며 공식 Gate 또는 사람의 배포 승인이 아니다.

검증 한계: Darwin arm64/Python 3.12.14의 local offline 환경만 신규 확인했다. Linux/Windows-native/다른 Python 조합, 외부 CI, 실제 publication/deployment, 장기간 authority retirement는 이번에 검증하지 않았다. 추가 raw-path 후보는 미확정이다. 검증 평가와 공식 계획 종료는 다르므로 canonical closure 증거 없이 completed로 이동하지 않는다.

## Follow-ups

- Main 소유: 별도 보수 요청 시 세 confirmed P2에 대한 failing regression부터 고정하고 보수 후 새 exact candidate를 독립 검증한다. 현재 자동 보수는 수행하지 않는다.
- Main 소유: 추가 initializer symlink/.. 후보는 후속 보안 검증에서 실제 쓰기/거부 대조군으로 확정하거나 기각한다. 현재 confirmed defect로 취급하지 않는다.
- Main 소유: nested root 부모 생성 제약 및 greenfield PLAN-0000 안내는 보수 범위 결정 때 검토한다. 실제 데이터 손실이나 dead end를 확인했다고 주장하지 않는다.
- 공식 종료 blocker: 이번 검증 기록에는 신규 source canonical run/manifest와 evidence-bound close-plan이 없다. 이전 계획의 REVIEW 수락을 이 계획으로 재사용하지 않는다.
