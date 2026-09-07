---
id: PLAN-2026-0003
kind: exec-plan
status: in-progress
owner: main
area: harness
created: 2026-09-07
updated: 2026-09-07
base_commit: "16e6a477eaefc41ca374fd77f35f9ec61a3191a0"
integrated_commit: "7ad0c9c247759016660616fa6d876d7044375261"
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
- [x] PR3: 관찰 facts, baseline questions, authority drafts와 context lifecycle 구현 및 독립 검증.
- [x] PR4: 현행 계약에 필요한 file-safety 보수 및 exact 후보의 독립 재검증, Main bounded acceptance.
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

complete

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

구현 후보 `21c50b5e26fcc9a796551d6d612f72789f32918b` 통합. 구현자 보고: PR3 13 tests, 전체 123 tests, distribution/package-removal, runtime parity 통과. Main도 `/tmp/reporivet-pr3-venv`의 Python 3.12로 `./dev/check`를 별도 실행하여 exit 0을 확인했다(`/tmp/reporivet-pr3-main-check.log`). 독립 정확성 review의 focused 13개 및 adjacent 12개 테스트는 통과했지만 다음 보수 항목이 재현되어 완료 승인 전이다: `--plan` 선택 밖의 active plan 노출, `ruff.toml` command 후보의 잘못된 evidence 경로, context에서 불완전 accepted ADR 검증 누락, frontmatter 없는 legacy 문서의 warning이 hard error로 바뀌는 회귀. 추가 독립 review는 core context 문서를 읽기 전 safe-path 검사가 누락되어 외부 symlink PRODUCT가 authority로 노출되는 문제도 재현했다. 이 다섯 항목을 보수하며 initializer/runtime의 병렬 수정을 피하기 위해 PR4 후보 통합 후 순차 진행한다. 구현자의 canonical run `20260907T021205136834Z-verify`는 pass지만 Main 계획 편집으로 dirty target이었다. clean candidate 검증을 대신하지 않는다.

보수 packet: `tests/test_authority_lifecycle.py`에 선택한 active plan만 출력하는 fixture, `ruff.toml` 후보의 정확한 근거 경로 fixture, 불완전 accepted ADR의 context 거부, frontmatter 없는 legacy notes의 warning/비권위 처리, core authority symlink 및 nonregular 입력 거부를 먼저 추가한다. 허용 구현은 initializer의 observed-facts renderer와 canonical/dogfood runtime의 같은 renderer 및 context 관련 함수다. PR4 transaction API·Gate·baseline 정책·기존 project-owned bytes는 변경하지 않는다. focused/adjacent 테스트와 runtime parity를 통과한 뒤 별도 context에서 재검증한다. Main 계약 해석: 원문 PR3의 `ExecPlan: 선택된 active plan만`을 그대로 적용하므로 명시적으로 선택하지 않은 plan은 기본 authority 목록에 넣지 않는다. accepted ADR을 normative context에 싣기 전에는 docs-check와 동일한 기존 구조 검증을 적용한다. frontmatter 자체가 없는 legacy notes는 warning과 함께 authority에서 제외하되, authority를 명시한 malformed metadata·충돌·unsafe path의 fail-closed 처리는 유지한다. 이는 과거 동작 전체를 복원하거나 의미 판정 규칙을 추가하는 변경이 아니다.

보수 후보 `e69ecebc89846a5add8448e7b0b1006ddf2a5453` 완료. 구현자 검증: authority 18 tests, adjacent 14 tests, 전체 138 tests 및 runtime parity/diff check 통과. 로그는 `.harness/runs/20260907T025617187810Z-check`다. 독립 reviewer가 이 정확한 SHA를 `/tmp/reporivet-pr3-reverify-MPUbBq`에 archive로 분리해 재검증했다. authority 18/18, adjacent 14/14, 추가 ruff/legacy/malformed/symlink fixture 및 runtime parity 모두 통과했고 새 verified finding은 없다. Main은 이 증거로 PR3의 bounded acceptance를 승인한다. archive에는 `.git`이 없어 최종 Git-bound canonical verification은 T5에서 별도 수행한다.

범위 결정: 문서 scope overlap만으로 충돌이라고 판정하지 않으며 duplicate ID와 명시적 supersession 불일치만 기계적으로 거부한다. baseline evidence guard는 새 provenance가 있는 초안에 적용하고 legacy authority를 변경하지 않는다. 새 schema/command 없이 기존 문서의 evidence review를 사용하며 verify와 baseline 사이 순환 의존을 만들지 않는다.

### T3 — PR4 구현

#### State

complete

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

2026-09-07 PR4 읽기 전용 조사로 범위를 확정했다. initializer apply_harness의 렌더/쓰기 interleave를 mutation plan과 작은 transaction으로 분리하고, adoption snapshot rollback과 copied runtime definition finalize/close-plan rollback에 postimage 보호를 적용한다. PR3 독립 review와 별개 후보에서 구현하고 Main이 순차 통합한다. 후보 `63ee936796b6c3def2b976d332f20f26a3c001e4`는 11개 허용 경로만 변경했으며 Main `dcd8a90`으로 통합했다. 구현자 환경의 전체 133 tests, distribution 및 runtime parity가 통과했지만 독립 안전성 review가 진행 중이며 3개 결함이 재현되어 acceptance는 미승인이다: staging 후 사용자 bytes/mode 변경을 늦은 live preimage 채취로 덮는 문제, staged runtime import가 target `dev/json.py`를 dry-run 중 실행하는 문제, finalize missing preimage 이후 생성된 spec을 덮는 문제. 최종 독립 보고는 추가로 finalize가 write 직후 사용자 편집을 transaction postimage로 잘못 채택해 rollback 중 삭제하는 문제, initializer의 in-place partial write 오류가 원본을 손상한 채 남기는 문제까지 총 5건을 재현했다. 재현 스크립트는 `/tmp/pr4-independent-repro.py`의 stage-edit/unsafe-import/finalize-preimage/finalize-postimage/partial-write이며 기존 focused 95 tests 및 guard 4 tests/13 scenarios는 통과했다. PR3 보수 다음 순서로 PR4를 보수한다.

PR4 보수 계약: staging 초기 bytes/mode와 렌더 후의 차이만 mutation으로 계획하고 최초 preimage를 보존한다. staged runtime은 isolated Python으로 호출해 target 모듈을 import하지 않는다. finalize는 전체 및 각 write 직전 preimage 검증, missing 경로의 exclusive creation, 렌더 결과와 예정 mode에서 구성한 postimage를 사용한다. write 뒤 임의 live 파일을 postimage로 인정하지 않는다. initializer 기존 파일을 in-place truncate하지 않고 완성된 임시 bytes/mode를 준비해 preimage 재검증 후 교체한다. 사용자 divergence를 무조건 rollback해서는 안 되며, 이 변경도 OS-level 완전 동시성 isolation을 주장하지 않는다. 다섯 reproducer를 회귀 테스트로 포함하고 독립 verifier가 수정 후 다시 실행한다. 보수 구현 전 6개 회귀 테스트(다섯 결함 및 managed-preimage 변형)가 모두 실패함을 `/tmp/pr4-repair-before.log`로 확인했다. finalize의 catalog write는 기존 command_docs_index 안에서 이루어지므로 해당 쓰기 접점에만 명시적인 optional 내부 transaction 인자를 허용한다. 새 CLI/Namespace 정책 설정이나 무관한 catalog 재설계는 금지한다. 독립 reviewer는 clean 원본 worktree의 정확한 후보 SHA를 읽으며 Main tree에서는 PR3 보수를 순차 진행한다.

Main 계약: 기존 init/upgrade --dry-run은 canonical 상대경로/action/preimage type·mode·hash/예정 content hash의 deterministic fingerprint를 제공한다. apply는 자체 동일 계획을 구성하고 mutation 전 전체 preimage를 다시 검증한다. 별도 실행한 dry-run을 승인 토큰으로 강제하는 기능은 추가하지 않으며 그러한 보장을 주장하지 않는다. 모든 target의 안전한 type과 부모 경로를 먼저 검사하고 mutation 직전 다시 검사한다. transaction이 실제 만든 postimage와 현재 파일이 같을 때만 rollback하며 다르면 사용자 변경을 보존하고 rollback conflict를 명시한다. 파일 bytes/mode와 새로 만든 빈 directory를 보존·복원하되 무관한 파일은 건드리지 않는다. 동시 수정의 완전한 OS-level isolation을 주장하지 않는다.

허용 경로: src/reporivet/initializer.py, 기존 CLI 출력의 fingerprint 연결만 src/reporivet/cli.py, canonical/dogfood dev/harness.py의 definition finalize/close-plan rollback, 관련 tests 및 직접 영향 security/design/spec 문서. runtime 전반의 unrelated mutation이나 Gate 정책은 확장하지 않는다. 새로운 approval CLI, persisted backup registry, production dependency는 금지한다.

2026-09-07 재개 및 보수 후 독립 검증: 보수 commit `1d064217da738ebc3ed593ce4aeccf365fb0cd16`은 이미 통합되어 있었다. 독립 verifier는 exact `24a98fc658a015f5b143a92881a0f0ba8cd5be76`를 archive `/tmp/pr4-24a98fc-verifier-kqgWD5`로 분리하고 Git blob과 핵심 코드 bytes를 비교했다. Darwin arm64/Python 3.12.14의 `/tmp/reporivet-pr3-venv` 환경에서 전체 155 tests/73.927초 PASS (distribution/offline wheel install-uninstall/copied runtime 및 service/web/library/CLI 포함). 과거 reproducer를 현행 hook과 안전 기대값에 맞춘 임시 사본으로 5 scenarios 전부 재실행했고 추가 독립 4 tests/5 scenarios (chmod/replace 실패, staging mode-only, finalize mode-only divergence, catalog partial temp write)도 PASS했다. 로그는 `/tmp/pr4-24a98fc-verifier-suite.log`, `/tmp/pr4-24a98fc-repro.log`, `/tmp/pr4-24a98fc-adversarial.log`다. 새로 재현된 결함 없음, AC-4/해당 AC-6 PASS recommendation. Main은 이를 bounded PR4 acceptance로 수락한다. archive 독립 검증은 T5의 Git-bound canonical 검증을 대체하지 않는다. 기존 OS isolation/partial-error rollback-incomplete 한계를 유지하며 운영 계약 PLAN-0004 변경을 복구 범위로 재구현하지 않는다.

### T4 — PR5 migration

#### State

in-progress

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

정확한 구현 허용 경로: CLAUDE.md, AGENTS.md, 신규 dev/agent-contract-sync, 신규 dev/agent_contract_sync.py, docs/DESIGN.md(아래 내용 보존 후 retire), ARCHITECTURE.md, docs/design-docs/core-beliefs.md, docs/PRODUCT.md, docs/PLANS.md, docs/README.md, docs/design-docs/index.md, README.md, README.en.md, src/reporivet/assets/project/root/AGENTS.md.tmpl, 신규 tests/test_agent_contract_sync.py, tests/test_agent_operating_contract.py, docs/design-docs/_template.md, docs/decisions/_template.md. Main만 이 계획을 편집한다. source design/ADR template은 이미 조사 항목을 갖춘 packaged template과 맞추는 범위만 허용한다. 초기 18개 허용 경로 밖 발견은 구현하지 말고 Main에 보고한다.

#### Protected paths

completed plans, archive, target project-owned authority, external repositories.

#### Acceptance

AC-5, AC-6

#### Verify

contract sync/check/idempotence, 링크 검사, matrix/distribution/package 제거, full check.

#### Stop conditions

기존 내용 손실, 동기화 범위 충돌, 외부 publish 필요.

#### Result

읽기 전용 migration 조사 완료, 구현은 공유 테스트를 수정 중인 PR4 및 PR3 보수 이후 순차 수행한다. DESIGN의 durable operating 원칙과 최소 구현 관례는 core-beliefs로, ownership/technical 계약과 Gate 설명은 기존 ARCHITECTURE의 적절한 절로 통합한다. knowledge lifecycle은 README/PLANS, Main/Sub 및 공통 조사 의무는 CLAUDE portable block과 PLANS, command UX/UTF-8 및 제품 non-goals는 PRODUCT의 해당 절로 분리한다. 현재 docs/README.md·design-docs/index.md·portable contract의 live DESIGN 링크를 함께 수정하되 completed/history는 보존한다. Main이 README.md의 주변 문맥을 확인한 결과 DESIGN 언급은 source 링크가 아니라 generated-target 안내였으므로 지우지 않고 conditional visual taxonomy로 정정한다. README.en.md에도 동일한 stale 생성 트리가 있으므로 양쪽 generated tree/관련 lifecycle 설명의 최소 정정을 허용하며, target project-owned DESIGN 보존 보장은 그대로 유지한다.

2026-09-07 재개한 정확한 migration 경계: PLAN-0004의 Main/Lead/leaf·분해·반증 문구는 source/target 역할 절에 그대로 보존한다. DESIGN의 repository-centric 원칙과 최소 구현 관례는 core-beliefs, ownership·fail-closed·argv 실행·Gate/closure 기술 설명은 ARCHITECTURE, lifecycle은 README/PLANS, CLI/UTF-8 observable 계약과 비목표는 PRODUCT에 대응시킨다. 이미 동등하게 존재하는 문장은 중복 복사하지 말고 Result의 mapping으로 보존을 입증한다. current live DESIGN 링크는 AGENTS/README/design-docs index에서 교체하고 target optional visual DESIGN 및 관련 fixtures/runtime/constants와 completed history는 보존한다. source PLANS Required properties 및 source design/ADR templates의 누락된 공통 조사 구조는 이미 갖춰진 target 계약에 맞춘다. 새 조사 의무는 Engineering invariants에 두어 기존 역할 절을 재작성하지 않는다.

실행 제약: 구현 leaf 한 명, 재위임 금지, 쓰기는 순차. 파일 편집/local candidate commit 및 Python 3.12 focused/check 도구 허용, 예산 최대 25분, 같은 접근 두 번 실패 시 중지. 별도 read-only verifier가 exact 후보의 source sync/path/migration/target parity를 반증하며 최대 15분. 추가 의존성/CLI target/CI/Gate/config 변경 금지. source sync는 root/parent 및 CLAUDE/AGENTS의 unsafe symlink·nonregular를 검증하고 marker malformed/fenced/duplicate/reversed와 invalid UTF-8을 쓰기 전 거부한다. payload bytes는 정규화하지 않으며 --check는 파일·mode·mtime을 변경하지 않는다. drift sync는 같은 directory의 완성된 temporary file 교체 및 기존 mode 보존, preimage divergence 시 중지, idempotent 동작이다. OS-level 완전 동시성 isolation이나 외부 approval-token binding은 주장하지 않는다. helper/wrapper는 package asset/target에 포함하지 않는다.

source-only sync의 최소 계약: CLAUDE의 유일한 paired portable block을 AGENTS 전체 portable 내용으로 deterministic projection한다. 잘못된/중복 marker와 unsafe path는 쓰기 전에 거부하고 block 밖 provider-specific 내용은 AGENTS에 복사하지 않는다. `--check`는 읽기 전용이며 drift 때 비정상 종료한다. 새 unittest가 source command `--check`를 실행하여 기존 check/verify 경로에서 drift를 검출한다. marker spelling은 `<!-- reporivet:portable:start -->`와 `<!-- reporivet:portable:end -->`로 고정하고, 각 marker 사이의 UTF-8 line bytes를 정규화 없이 그대로 projection한다. 새 source wrapper는 기존 PYTHON 환경변수 관례를 따르고 helper는 `dev/agent_contract_sync.py` 하나로 제한한다. 임의 target CLI 옵션은 추가하지 않는다. CI/Gate/config 정책이나 target package 자산에 이 도구를 연결하지 않는다. source AGENTS와 target template의 종전 전체 동일성 assertion만 source-only 차이에 맞춰 분리하고 target AGENTS 독립성 및 runtime parity 검사는 유지한다.

원문 PR3의 공통 조사 의무도 함께 반영한다: normative rule/decision의 reason·scope·방어할 실패, 기존 repo/dependency capability, 외부 선택의 공식 자료, no-change와 실질적 대안/거부 이유, verification/enforcement, revisit/retirement. 의미 판정 validator나 새로운 정책 runtime을 만들지는 않는다.

2026-09-07 구현 후보 `17a684fff07d834ae0dcb30f25e8d63d3975e072` (base `31fe5ebf8e7c73f22862ce773f8522b90f27e264`): 정확한 18개 허용 경로만 변경, clean local commit. PLAN-0004 역할/분해/반증 및 PLANS delegation/result 절은 시작 후보와 byte-for-byte 보존했다. source DESIGN 의도/최소 구현→core-beliefs, ownership/argv/fail-closed/markers/Gate→ARCHITECTURE, lifecycle→README/PLANS, CLI UX/Unicode/non-goals→PRODUCT, agent 역할→기존 AGENTS/PLANS로 매핑하고 live source 링크를 교체한 뒤 retire했다. target optional visual DESIGN과 runtime/Gate/config/initializer/history는 변경하지 않았다. source CLAUDE portable payload→AGENTS exact-byte sync와 source wrapper/helper, 조사 의무·source template 정합성을 구현했다. catalog는 이미 current라 수동/자동 쓰기가 불필요했다.

구현자 검증 환경: Darwin/Python 3.12.14 `/tmp/reporivet-pr3-venv`, 신규 테스트 first-red, focused 18/18 PASS, 최종 staged bytes의 `./dev/check` 166 tests/74.894초 PASS(distribution/offline install-uninstall/copied runtime 포함). sync --check/docs-index --check/docs-check/plan-check/diff-check 통과, commit 후 sync check PASS. run `.harness/runs/20260907T092143952903Z-check`, `/tmp/pr5-implementer-focused.log`, `/tmp/pr5-implementer-check-final.log`. 초기 Main canonical은 clean `278e9d0cc70708b6ffb6f8669c0cd18b45b118ed`에서 `20260907T092719288373Z-verify`, 166 tests/82.460초 pass 및 Gate REVIEW였다. 그러나 독립 verifier가 helper `abspath`의 symlink/.. lexical collapse에 의한 deterministic wrong-root AGENTS write를 재현했다. `/tmp/pr5-independent-path-repro.py`는 fixture의 link→other/child 뒤 `link/../source/dev/agent-contract-sync` 실행 시 실제 B helper가 A AGENTS를 변경하는 것을 검출한다. focused/distribution/matrix 55 tests와 추가 43 failure scenarios는 통과했고 문서 내용 보존/기존 역할 byte parity도 확인했지만 AC-5 path 계약 위반으로 이 후보는 미수락이다.

보수 packet: dev/agent_contract_sync.py와 tests/test_agent_contract_sync.py만 수정한다. unsafe ancestor evidence를 잃는 abspath/lexical normalization 전에 원래 실행·root 경로의 prefix를 검사하고 symlink/..를 쓰기 전 거부한다. direct helper sync(root) 및 wrapper 실제 invocation 모두에 재현 회귀를 먼저 추가해 A/B의 bytes/mode/mtime이 보존되는지 확인한다. 안전한 일반 상대경로·다른 cwd/PYTHON override·no-op 및 기존 path/marker/partial-write 검사는 유지한다. 새 CLI/config/target support/일반 filesystem abstraction 금지. 구현 leaf 최대 10분·재위임 금지, 동일 접근 두 번 실패 중지. 보수 후보 `7ad0c9c247759016660616fa6d876d7044375261`에서 helper와 tests 두 경로만 변경했다. abspath 선행 정규화를 제거하고 상대 root는 cwd와 연결하되 원래 .. prefix를 보존하여 검사한다. 독립 repro 및 신규 direct/wrapper 각각 first-red 확인(`/tmp/pr5-path-repair-first-red.log`) 뒤 focused sync/operating 20/20 PASS(`/tmp/pr5-path-repair-focused.log`). 원 repro는 unsafe symlink를 exit 1로 거부하고 A/B 원본 bytes/mode/mtime 보존을 확인했다. 정상 relative/.. 및 wrapper no-op도 통과했다. Main은 이 diff가 허용 경계 안인지 확인했다. 보수 후 독립 verifier가 새 exact 후보로 원 reproducer와 adjacent 검사를 재실행 중이며 Main이 canonical을 다시 실행한다.

### T5 — 독립 통합 검증과 종료

#### State

in-progress

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

PR3와 PR4 bounded acceptance 완료, PR5 exact 구현 후보 `17a684fff07d834ae0dcb30f25e8d63d3975e072`의 별도 context 독립 검토 진행 중이다. Main은 이 후보와 계획 기록만 포함한 clean Git 대상에 계획 base를 지정해 canonical 검증한다. PLAN-0002의 현행 blocked/T9 및 빈 closure evidence를 확인했으며 기존 기록이 미종료 상태를 정확히 표현하므로 완료로 바꾸지 않는다. PLAN-0004에 받은 REVIEW 종료 승인을 다른 계획으로 확대하지 않는다.

## Architecture Impact

initializer와 copied stdlib runtime의 두 수명을 유지한다. 관찰 artifact는 generated non-authority이며 plan이 유일한 작업 기록이다. source-only contract projection은 generated target에 배포하지 않는다.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| 현재 product/spec/design 문서와 packaged templates | update | authority lifecycle과 file-safety 계약 | Main | resolved |
| docs/DESIGN.md와 관련 현재 문서 | retire/update | 비시각 내용을 적절한 source로 이동 | Main | resolved |
| CLAUDE.md, AGENTS.md | update/generate | source portable contract projection | Main | resolved |
| docs/README.md 및 catalogs | update | 현재 링크와 lifecycle 일치; catalog는 이미 current | Main | resolved |
| PLAN-2026-0002 | update | 기존 blocked/T9 정정이 미종료 현실을 정확히 표현함을 확인 | Main | resolved |

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
