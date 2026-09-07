---
id: PLAN-2026-0003
kind: exec-plan
status: in-progress
owner: main
area: harness
created: 2026-09-07
updated: 2026-09-07
base_commit: "16e6a477eaefc41ca374fd77f35f9ec61a3191a0"
integrated_commit: ""
verified_commit: ""
traceability: 0
product_spec: ""
verification_run: ""
manifest_sha256: ""
gate_verdict: ""
gate_review_reason: ""
---

# Authority taxonomy 복구 PR3–PR5 완료

## Purpose / Big Picture

대상 프로젝트의 관찰 사실과 초안, 현재 authority를 구분하고 repository-local runtime을 유지하면서 안전한 변경과 자체 문서 migration을 완료한다. 사용자는 2026-09-07 남은 복구 작업 전체 실행을 승인했다. 이 승인은 release 게시, 외부 저장소 변경 또는 사람이 작성해야 하는 Gate REVIEW 사유를 대신하지 않는다.

## Progress

- [x] 복구 원문과 현재 HEAD, 기존 계획의 종료 요건 확인.
- [ ] PR3: 관찰 facts, baseline questions, authority drafts와 context lifecycle 구현 및 독립 검증.
- [ ] PR4: 현행 계약에 필요한 file-safety만 테스트부터 선별 이식 및 독립 검증.
- [ ] PR5: 자체 문서 migration, portable contract projection, release fixture 검증.
- [ ] 통합 후보의 canonical verification과 두 계획의 종료 상태 정리.

## Context and Orientation

기준은 `16e6a477eaefc41ca374fd77f35f9ec61a3191a0`이다. PR1/PR2 구현 및 회귀 검증은 완료되었으며 PR2는 protected runtime 변경으로 shadow Gate REVIEW를 받았다. 이전 `PLAN-2026-0002`는 정의·audit·Gate 기능 구현의 별도 계획이다. 해당 계획의 T9 complete 표시는 종료 증거가 비어 있는 현실과 불일치하며 공식 종료를 의미하지 않는다. PR3–PR5는 그 과거 계획의 원래 구현 범위와 구분하여 이 계획에서 추적한다.

입력 원문은 `/Users/hakseong/Downloads/Reporivet_Current_State_Recovery_Plan_ko.md`이다. 저장소 경계는 accepted ADR-0001을 유지한다. 설치 package는 생성·upgrade를, copied `dev/harness.py`는 package 없는 저장소 작업을 담당한다.

## Scope

- 관찰 가능한 repository facts와 baseline questions를 evidence path와 함께 생성한다.
- PRODUCT/ARCHITECTURE 초안을 대상 프로젝트 중심으로 유지한다.
- 기본 context에 active 문서와 accepted ADR만 포함하고 draft/history는 명시적 옵션으로 노출한다.
- baseline의 단순 status 편집 및 충돌하는 authority가 검증을 통과하지 않게 한다.
- durable decision의 이유·scope·대안·조사·검증·재검토 조건을 구조적으로 표현하고 검증한다.
- preview fingerprint, preimage 재검증, rollback과 사용자 변경 보존을 기존 소유권 경계에서 구현한다.
- Reporivet 자체 비시각 DESIGN 내용을 적절한 현재 문서로 옮긴 후 기존 파일을 제거한다.
- source repository 전용 CLAUDE portable contract block에서 AGENTS 전체 portable 내용을 deterministic projection한다. 대상 프로젝트는 AGENTS canonical을 유지한다.

## Non-goals

- one-shot 커밋 전체 cherry-pick, runtime 제거, provider별 target asset, daemon, scheduler, task database, 모델 판정, 새 production dependency.
- archive/history 수정, 외부 저장소 변경, push/PR/merge/release/deployment.
- 기존 target의 project-owned 문서·설정 덮어쓰기, scanner 추론 자동 승격.
- 사람의 REVIEW 사유 조작 또는 Gate 정책 완화.

## Acceptance Criteria

- **AC-1:** generated repository-facts와 baseline-questions는 실제 관찰 경로를 제시하고 제품 의도·ownership·SLO·visual token을 발명하지 않는다.
- **AC-2:** 대상 authority 초안은 draft이며 기본 context에서 제외된다. active 문서/accepted ADR만 기본 선택되고 명시적 draft/history 옵션과 충돌 검사가 동작한다.
- **AC-3:** baseline은 status 편집만으로 성립하지 않으며 durable decision은 이유·실질적 대안·verification을 요구한다.
- **AC-4:** root/parent symlink, nonregular/FIFO, 읽기 전용 audit, preview/preimage, rollback/user-edit 보존, evidence-state 비승격을 재현 테스트로 입증한다.
- **AC-5:** 자체 DESIGN 내용이 손실 없이 이동되고 현재 링크가 유효하다. source contract sync/check는 deterministic하며 generated targets에 provider 의존성을 만들지 않는다.
- **AC-6:** service/web/library/CLI fixture, distribution, package 제거 후 runtime, 전체 check/verify 및 독립 exact-target 검증이 통과한다. 완료 승인은 Gate 판정과 구분해 기록한다.

## Milestones

### M1 — PR3 authority lifecycle

기존 scanner와 doc parser를 재사용한다. 의미 추론 대신 명시적 evidence와 구조 검증을 사용한다. 관련 회귀 테스트를 먼저 추가하고 독립 검증 후 통합한다.

### M2 — PR4 bounded safety

기존 generic 안전 함수와 역사적 구현을 비교하고 부족한 기능만 수동 이식한다. 새 public 또는 persisted 계약에 필요한 세부 결정은 구현 전에 Main이 이 계획에 고정한다.

### M3 — PR5 source migration

현재 문서 내용을 읽고 의미별 이동과 링크·catalog 변경을 원자적으로 수행한다. contract sync는 source 전용이며 package target runtime에 포함하지 않는다.

## Task Packets

### T1 — 현행 구현과 누락 조사

#### State

complete

#### Task type

support

#### Depends on

none

#### Outcome

요구별 구현 유무, 변경 지점과 최소 계약 결정을 반환한다.

#### Non-goals

구현 및 위임.

#### Read

복구 원문 PR3–PR5, ADR-0001, docs/PLANS.md, initializer/runtime/templates와 관련 테스트.

#### Allowed writes

없음. 결과는 Main이 이 계획에 기록한다.

#### Protected paths

모든 저장소 파일.

#### Acceptance

AC-1, AC-2, AC-3, AC-4, AC-5, AC-6

#### Verify

Python 3.12로 `./dev/context --area harness`, 관련 소스와 테스트 읽기.

#### Stop conditions

현재 authority 충돌, 필수 사용자 결정 또는 범위 확장.

#### Result

2026-09-07 읽기 전용 조사 완료. 기존 capability 생성, path symlink guard, audit, definition evidence parser 및 일부 rollback을 재사용한다. PR3 누락은 generated facts/questions, context lifecycle 필터, baseline review 검증과 durable decision 구조다. PR4는 기존 init/upgrade dry-run 및 transaction 경계에 fingerprint/preimage/postimage를 보강하며 one-shot CLI는 가져오지 않는다. PR5의 자체 DESIGN 이동 및 CLAUDE portable block projection은 사용자가 승인한 복구 원문의 명시적 migration이다.

### T2 — PR3 구현

#### State

in-progress

#### Task type

implementation

#### Depends on

T1

#### Outcome

관찰 facts와 baseline 질문, authority lifecycle 및 decision 계약 구현.

#### Non-goals

PR4 transaction 확장, PR5 source 문서 migration.

#### Read

이 계획과 T1에서 고정할 관련 initializer/runtime/template/test 경로.

#### Allowed writes

src/reporivet/initializer.py, src/reporivet/cli.py, src/reporivet/assets/project/**, dev/harness.py, 해당 회귀 tests, 직접 영향 spec/design 문서. 실제 dispatch에서 더 좁힌다.

#### Protected paths

계획 파일, archive/history, project-owned target fixture의 원본, Gate/CI 정책 및 다른 모든 경로.

#### Acceptance

AC-1, AC-2, AC-3, AC-6

#### Verify

원문 PR3의 9개 필수 테스트, 기존 회귀 suite, package/runtime parity, `./dev/check`.

#### Stop conditions

승인되지 않은 계약 확대, authority 충돌, 같은 접근 두 번 실패, acceptance 완화 필요.

#### Result

구현 후보 `21c50b5e26fcc9a796551d6d612f72789f32918b` 통합. 구현자 보고: PR3 13 tests, 전체 123 tests, distribution/package-removal, runtime parity 통과. Main도 `/tmp/reporivet-pr3-venv`의 Python 3.12로 `./dev/check`를 별도 실행하여 exit 0을 확인했다(`/tmp/reporivet-pr3-main-check.log`). 독립 정확성 review의 focused 13개 및 adjacent 12개 테스트는 통과했지만 다음 보수 항목이 재현되어 완료 승인 전이다: `--plan` 선택 밖의 active plan 노출, `ruff.toml` command 후보의 잘못된 evidence 경로, context에서 불완전 accepted ADR 검증 누락, frontmatter 없는 legacy 문서의 warning이 hard error로 바뀌는 회귀. 추가 code review 결과와 함께 보수하며 initializer/runtime의 병렬 수정을 피하기 위해 PR4 후보 통합 후 순차 진행한다. 구현자의 canonical run `20260907T021205136834Z-verify`는 pass지만 Main 계획 편집으로 dirty target이었다. clean candidate 검증을 대신하지 않는다.

범위 결정: 문서 scope overlap만으로 충돌이라고 판정하지 않으며 duplicate ID와 명시적 supersession 불일치만 기계적으로 거부한다. baseline evidence guard는 새 provenance가 있는 초안에 적용하고 legacy authority를 변경하지 않는다. 새 schema/command 없이 기존 문서의 evidence review를 사용하며 verify와 baseline 사이 순환 의존을 만들지 않는다.

### T3 — PR4 구현

#### State

in-progress

#### Task type

implementation

#### Depends on

T2

#### Outcome

기존 소유권을 유지하는 preview/preimage/rollback 및 evidence parser 안전성.

#### Non-goals

one-shot 경계 이식, 추가 runtime 또는 임의 config migration.

#### Read

이 계획, 관련 initializer/runtime safety와 tests, 역사적 안전 함수만.

#### Allowed writes

Main이 M2 계약과 정확한 경로를 고정한 뒤 해당 코드·회귀 테스트만.

#### Protected paths

archive/history, Gate/CI 정책, unrelated paths.

#### Acceptance

AC-4, AC-6

#### Verify

안전성별 실패 주입 테스트와 snapshot 비교, full check, package independence.

#### Stop conditions

계약 미확정, source conflict, 사용자 변경 손실, 범위 확대.

#### Result

2026-09-07 PR4 읽기 전용 조사로 범위를 확정했다. initializer apply_harness의 렌더/쓰기 interleave를 mutation plan과 작은 transaction으로 분리하고, adoption snapshot rollback과 copied runtime definition finalize/close-plan rollback에 postimage 보호를 적용한다. PR3 독립 review와 별개 후보에서 구현하고 Main이 순차 통합한다.

Main 계약: 기존 init/upgrade --dry-run은 canonical 상대경로/action/preimage type·mode·hash/예정 content hash의 deterministic fingerprint를 제공한다. apply는 자체 동일 계획을 구성하고 mutation 전 전체 preimage를 다시 검증한다. 별도 실행한 dry-run을 승인 토큰으로 강제하는 기능은 추가하지 않으며 그러한 보장을 주장하지 않는다. 모든 target의 안전한 type과 부모 경로를 먼저 검사하고 mutation 직전 다시 검사한다. transaction이 실제 만든 postimage와 현재 파일이 같을 때만 rollback하며 다르면 사용자 변경을 보존하고 rollback conflict를 명시한다. 파일 bytes/mode와 새로 만든 빈 directory를 보존·복원하되 무관한 파일은 건드리지 않는다. 동시 수정의 완전한 OS-level isolation을 주장하지 않는다.

허용 경로: src/reporivet/initializer.py, 기존 CLI 출력의 fingerprint 연결만 src/reporivet/cli.py, canonical/dogfood dev/harness.py의 definition finalize/close-plan rollback, 관련 tests 및 직접 영향 security/design/spec 문서. runtime 전반의 unrelated mutation이나 Gate 정책은 확장하지 않는다. 새로운 approval CLI, persisted backup registry, production dependency는 금지한다.

### T4 — PR5 migration

#### State

blocked

#### Task type

implementation

#### Depends on

T3

#### Outcome

자체 문서 migration과 source-only portable contract projection.

#### Non-goals

release publication, generated target provider 의존성.

#### Read

docs/DESIGN.md, AGENTS.md, CLAUDE.md, ARCHITECTURE.md, core-beliefs, PLANS와 직접 참조 경로.

#### Allowed writes

Main이 확인한 이동 대상 현재 문서, source-only dev/agent-contract-sync와 대응 검사/테스트, 문서 catalogs.

#### Protected paths

completed plans, archive, target project-owned authority, external repositories.

#### Acceptance

AC-5, AC-6

#### Verify

contract sync/check/idempotence, 링크 검사, matrix/distribution/package 제거, full check.

#### Stop conditions

기존 내용 손실, 동기화 범위 충돌, 외부 publish 필요.

#### Result

M2 검증 대기.

### T5 — 독립 통합 검증과 종료

#### State

blocked

#### Task type

verification

#### Depends on

T2, T3, T4

#### Outcome

정확한 clean SHA에 acceptance를 검증하고 종료 증거 또는 정확한 blocker를 기록한다.

#### Non-goals

구현자 자기 승인, 사람 REVIEW 사유 조작, 정책 완화.

#### Read

이 계획과 PLAN-2026-0002, 전체 변경 diff와 현재 문서, Verification Run.

#### Allowed writes

Main 소유 계획 evidence만. 독립 verifier는 읽기 전용.

#### Protected paths

구현·acceptance·archive/history.

#### Acceptance

AC-1, AC-2, AC-3, AC-4, AC-5, AC-6

#### Verify

정확한 commit의 full suite, distribution, matrix, docs/plan/security/architecture 및 canonical verify. close-plan은 실제 REVIEW 사유가 있을 때만 수행한다.

#### Stop conditions

HEAD 불일치, 누락 evidence, BLOCK/INCONCLUSIVE 또는 사람 사유 없는 REVIEW 종료.

#### Result

구현 완료 대기.

## Architecture Impact

initializer와 copied stdlib runtime의 두 수명을 유지한다. 관찰 artifact는 generated non-authority이며 plan이 유일한 작업 기록이다. source-only contract projection은 generated target에 배포하지 않는다.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| 현재 product/spec/design 문서와 packaged templates | update | authority lifecycle과 file-safety 계약 | Main | pending |
| docs/DESIGN.md와 관련 현재 문서 | retire/update | 비시각 내용을 적절한 source로 이동 | Main | pending |
| CLAUDE.md, AGENTS.md | update/generate | source portable contract projection | Main | pending |
| docs/README.md 및 catalogs | generate/update | 현재 링크와 lifecycle 일치 | Main | pending |
| PLAN-2026-0002 | update | 과거 complete 표시와 미종료 현실 구분 | Main | pending |

## Interfaces and Dependencies

- 기존 시설: scanner/audit, schema parser, context routing, ownership, snapshot/rollback, deterministic wrappers.
- production dependency 추가 없음.
- 승인된 public 확장: context draft/history 옵션과 source contract sync. 추가 preview 관련 계약은 M2 전에 명시한다.

## Migration, Rollout, and Recovery

각 milestone을 별도 local commit으로 통합하고 새 회귀 검증을 수행한다. target project-owned bytes는 보존한다. 기존 accepted/history 문서는 rewrite하지 않는다. source DESIGN 제거는 내용 이동과 링크 수정 후에만 수행한다. 오류 시 해당 local 변경을 작은 수정으로 복구하며 history rewrite를 하지 않는다.

## Surprises and Discoveries

- 2026-09-07 — PLAN-2026-0002의 T9 complete는 빈 closure metadata와 불일치한다. PR3–PR5 완료를 과거 계획 완료로 자동 간주하지 않는다.

## Decision Log

- 2026-09-07 — 사용자의 남은 작업 전체 실행 지시에 따라 PR3–PR5를 이 ExecPlan에서 순차 수행한다.
- 2026-09-07 — 이전 답변의 PR1 완료는 baseline 검사 완료만 의미한다. 원문 PR1의 계획 종료/blocked 조건은 아직 정리되지 않았다.
- 2026-09-07 — 사람 REVIEW 사유는 구현 승인과 별개이며 임의로 만들어 종료하지 않는다.

## Concrete Steps

1. T1 조사로 PR3 의미와 정확한 변경 지점을 고정한다.
2. PR3/PR4/PR5 각각 테스트 우선 구현, 독립 review, 순차 통합.
3. 현재 문서와 이전 계획 상태를 실제 evidence에 맞게 갱신한다.
4. Python 3.12 격리 환경에서 `./dev/check`, 명시적 base/head의 `./dev/verify`를 실행한다.
5. 승인 요건을 충족하면 close-plan, 아니면 blocked 상태와 실제 근거를 남긴다.

## Validation and Evidence

- 기준 SHA: `16e6a477eaefc41ca374fd77f35f9ec61a3191a0`.
- 이전 PR2: 직접 110 tests 및 canonical verify pass, protected dev/harness.py로 REVIEW. 독립 exact-target 110 tests 및 6-kind matrix pass.
- 이 계획의 새 구현/검증 evidence: 아직 없음.
- raw logs는 `.harness/runs/`에 유지하며 commit하지 않는다.

## Outcomes and Retrospective

진행 중. 구현 완료와 Gate-bound 종료를 구분한다.

## Follow-ups

- PLAN-2026-0002의 빈 closure evidence 및 사람 REVIEW 사유 요건은 최종 종료 시 별도로 확인한다.
