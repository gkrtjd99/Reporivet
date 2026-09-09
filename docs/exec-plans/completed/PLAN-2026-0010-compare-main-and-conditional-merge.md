---
id: PLAN-2026-0010
kind: exec-plan
status: completed
owner: main
area: comparative-validation
created: 2026-09-09
updated: 2026-09-09
base_commit: "226b15af1b8ccf1d82ba410322a214f1f593cc7e"
---

# 원격 main 대비 비교 검증과 조건부 PR merge

## Purpose / Big Picture

처음 사용자는 기존 main보다 훨씬 좋다고 검증된 경우에만 PR merge까지 승인했다. 그 조건에 따른 비교와 게시 보류는 아래에 역사적으로 보존한다. 이후 사용자는 pilot의 한계를 설명받고, 현재 제품 요구 충족·안전성·관찰된 토큰 절감을 근거로 merge할 만하다는 추천에 “ㄱㄱ”라고 명시 승인했다. 새 게시 판단은 아래 M4/T5 계약을 따른다. 기존 AC-3의 UNPROVEN을 PASS로 바꾸지 않으며 보편적인 우위나 제거 기능의 상위호환을 주장하지 않는다.

## Progress

- [x] GitHub 인증과 원격 main SHA, PR 부재를 확인했다.
- [x] 정확한 두 후보를 고정하고 canonical 및 안전성 반례를 비교했다.
- [x] 독립 검토에서 사용자 본문 손실 결함을 찾았고 Main이 양쪽 CLI에서 재현했다.
- [x] C1 안전성 blocker로 중단했던 비교를 사용자 수선 승인 후 재개했다.
- [x] B1/B2 수선 후보 C2의 canonical 59 tests와 독립 안전성 재검증을 통과했다.
- [x] 동일 조건의 실제 개발 pilot 4개와 Main의 외부 oracle 검증을 완료했다.
- [x] 비용 기준에 미달한 pilot을 반올림해 통과시키지 않고 효용 우위를 UNPROVEN으로 유지했다.
- [x] C2 보고 시점에는 조건 미충족으로 PR 생성·push·merge를 하지 않았다.
- [x] 후속 사용자 명시 승인에 따라 별도 게시 검토·정확 후보 CI 후 PR #3을 merge했다.
- [x] Merge 후 main CI와 로컬 tree 일치·clean을 확인하고 M4 근거를 수락했다.

## Context and Orientation

로컬 main과 원격 main은 모두 base_commit과 같고 현재 작업 트리에 v0.3 entrypoint-only 전환 및 후속 보강이 미커밋 상태로 있다. 현재 열린 PR은 없다. v0.2는 copied runtime·고정 문서·Gate를 제공하고 v0.3은 이를 제거하므로 동일 기능 전체의 상위호환으로 간주할 수 없다. 현재 ADR-0002, SPEC-003, migration 문서가 제품 전환을 정의한다.

## Scope

Main은 이 계획과 필요할 경우 비교 결과 문서만 작성한다. 고유 임시 디렉터리에 원격 main과 현재 nonignored 파일의 frozen 사본, 평가 fixture와 로그를 만든다. 평가용 구현 쓰기는 프로젝트 본체가 아닌 별도 Git worktree의 명시된 fixture 경로만 허용한다. 2026-09-09 후속 사용자 승인으로 B1/B2 수선에 한해 `src/reporivet/initializer.py`, `tests/test_audit_adoption.py`, `tests/test_reporivet.py`의 구현·회귀 검사 수정을 허용한다. 원본 제품의 다른 동작이나 수락 기준을 통과시키기 위해 약화하지 않는다. 기존 C1 비교 결과는 역사적 관찰로 보존하며 수선 후보 C2와 구분한다. 조건 충족 후의 PR 대상은 고정한 현재 전체 변경과 검증 기록이며, 게시 전 비밀·임시 산출물·의도하지 않은 파일 포함 여부를 확인한다.

## Non-goals

성능 우위를 만들기 위한 테스트 약화·편향된 작업 선택·자동 migration·과거 release 변경·배포·패키지 공개·권한 설정 변경·force push·보호 규칙 우회·기존 작업 reset은 금지한다. 새 runtime·평가 서비스·작업 데이터베이스를 제품에 추가하지 않는다.

## Acceptance Criteria

- **AC-1 — 후보 고정:** 원격 main SHA와 candidate의 base/nonignored hashes/modes/삭제 목록, 환경, 명령, 결과를 기록한다. 비교 중 후보를 바꾸지 않는다.
- **AC-2 — 기능·안전성:** candidate canonical 검사를 통과하고 공통 시나리오의 사용자 파일 훼손·권한/경계 위반·중요 회귀가 없어야 한다. baseline 실패는 같은 환경에서 재현·원인을 구분하고 기능 제거를 테스트 통과 향상으로 세지 않는다.
- **AC-3 — 실제 개발 효용:** 동일 fixture·작업·모델·권한·예산에서 실제 코드 변경의 성공과 테스트를 비교한다. 적어도 두 종류의 작업에서 쌍대 관찰을 수행한다. 성공률 비열등만으로 훨씬 좋다고 하지 않는다. 성공 개선 또는 동등 성공과 두 작업 모두에서 반복 확인되는 유의미한 비용 절감이 필요하다. 비용 기준은 완료된 성공 trial의 관찰 가능한 실행 시간 또는 토큰이 비교쌍마다 20% 이상 줄어드는 것; 한 지표를 사후 선택하지 않고 두 지표를 모두 기록한다. 서로 반대 방향이면 우위를 보류한다. trial 시간·토큰은 host 관찰치이며 호출/대기 잡음과 표본 한계를 공개한다. 한 번의 pilot 우위는 확증이 아니므로 우위가 보이면 새 fresh context로 반복해 확인한다. pilot 동률·악화·비교 불가능이면 반복 없이 미입증으로 종료할 수 있다.
- **AC-4 — 타당성·독립 검토:** source와 target 계약의 차이, 제거 기능·호환성·migration, 평가 oracle과 비용 측정의 가정을 독립 검토한다. 유지보수 코드량 감소만으로 AC-3을 대체하지 않는다. 구체 결함과 UNPROVEN을 구분한다.
- **AC-5 — 조건부 공개:** AC-1부터 AC-4까지 증거가 충분하고 Main이 훨씬 낫다는 결론을 수락한 경우에만 브랜치 commit/push·PR 생성·필수 CI/검토·merge를 수행한다. remote base가 변하면 통합 후보를 재검증한다. merge SHA와 CI 결과를 확인한다. 미충족이면 PR·merge를 실행하지 않는다.

## Milestones

### M1 — 고정 후보와 결정적 비교

두 source 사본과 동일 환경으로 canonical 및 공통 CLI 동작·생성 범위·파일 보존을 확인한다.

### M2 — 실제 개발 pilot와 독립 판단

공통으로 수행 가능한 기능 변경과 버그 수정 fixture를 고정해 같은 조건으로 fresh agent를 실행한다. host가 비교 가능한 격리·모델·관찰치를 제공하지 못하면 그 한계를 기록하고 AC-3을 UNPROVEN으로 남긴다.

### M3 — 조건부 PR merge 또는 미입증 보고

조건을 사후 완화하지 않는다.

## Task Packets

### T1 — Main의 후보 준비와 비교 통합

- State: completed
- Task type: support
- Depends on: none
- Execution constraints: Git/Python/CLI/평가 설계; 로컬 도구 및 GitHub 읽기; 쓰기는 순차 또는 격리된 worktree; 같은 접근법 두 번 실패 시 중단; 30분.
- Outcome: exact candidates와 직접 비교 증거.
- Non-goals: 위 Non-goals와 동일.
- Read: 현재 제품·품질·보안·계획 정책, 원격 main CLI와 문서, 필요한 코드·검사.
- Allowed writes: 이 계획, 필요 시 docs/references의 비교 결과 1개, 고유 임시 평가 영역. 조건 충족 전 GitHub 쓰기 없음.
- Protected paths: 기존 제품·테스트·기존 문서 본문 및 다른 작업의 환경.
- Acceptance: AC-1, AC-2, AC-3.
- Verify: 같은 Python의 두 후보 검사, 동일 fixture 결과 비교, 후보 hash 유지.
- Stop conditions: 실제 근거 부족, 조건 위반, 원본 작업 손실 가능성, 같은 접근법 두 번 실패.
- Result: 비교 실행과 통합 증거 수집은 완료했다. C1에서는 canonical 성공과 별개로 본문 손실을 재현하여 중단했다. 사용자 승인 후 C2의 AC-1/2 PASS를 수락하고 실제 pilot까지 검증했다. AC-3은 비용 기준 미충족으로 UNPROVEN이며 원격 쓰기는 실행하지 않았다. Task 실행 완료는 우수성·계획 완료·merge 승인이 아니다.

### T2 — 독립 비교 검토

- State: completed
- Task type: verification
- Depends on: T1 후보 준비; 최종 증거는 T1 이후.
- Execution constraints: 코드·제품 경계와 평가 반증 능력; 읽기 전용; 재위임/Skill 호출 금지; 5분과 필요 시 후속 증거 검토 1회.
- Outcome: AC-2/3/4의 판단 추천; Main이 최종 수락한다.
- Non-goals: 구현 수정, 자동 승인.
- Read: 고정 후보의 관련 구현·문서·검사, 이 계획과 결과.
- Allowed writes: 없음.
- Protected paths: 전부.
- Acceptance: AC-2, AC-3, AC-4.
- Verify: 경계/회귀/비교가능성/측정의 반례를 찾아 구체 trigger와 근거 제시.
- Stop conditions: 후보 변경, 근거 부족, 권한/범위 이탈.
- Result: C1에서는 두 독립 검토가 안전성 결함·평가 한계로 merge 보류를 추천했다. C2 후속 안전성 검토는 exact candidate 대조, focused 40 tests와 225 CLI 반례 후 AC-2 수락을 추천했다. 최종 비교 검토는 준비 inputs·prompt hashes·postimage hashes/modes·네 구현 diff를 확인하고 oracle과 unittest를 독립 재실행했다. 비용 계산도 재확인하여 AC-3 UNPROVEN, AC-4 PASS(담당 독립 검토 범위), PR·merge 미실행을 추천했다. Main은 이 추천과 직접 검증을 합쳐 수선 근거는 수락하되 우수성·merge 승인은 보류한다.

### T3 — 고정 fixture의 개발 trial

- State: completed
- Task type: implementation
- Depends on: T1의 fixture 및 공유 평가 계약 고정.
- Execution constraints: 같은 모델과 fresh context, 같은 tool access, 5분, 재위임/Skill/네트워크/전역설치 금지. 병렬 쓰기는 각각 별도 Git worktree·겹치지 않는 절대경로·동일 고정 요구로만 수행한다.
- Outcome: 승인된 fixture 코드 수정과 실제 테스트 결과. 완료 승인은 Main만 수행한다.
- Non-goals: 다른 비교 조건 읽기, 원본 레포 수정, 테스트 약화, 평가 oracle 열람.
- Read: 개별 packet에 지정한 자기 fixture의 진입점·요구·코드·테스트.
- Allowed writes: 개별 packet의 fixture 구현 및 필요한 테스트. 생성된 기존 검증 명령이 관리하는 ignored evidence와 `docs/generated/code-map.md`, `docs/generated/docs-index.md`의 파생 갱신은 허용한다. 제품 동작·요구·설정·진입점·기존 수락 검사는 변경하지 않는다. 두 조건에 같은 권한을 제공하며 없는 runtime을 새로 설치하지 않는다.
- Protected paths: 나머지 전부. Main이 외부 oracle을 소유한다.
- Acceptance: AC-3.
- Verify: fixture 자체 검사와 Main의 고정 oracle.
- Stop conditions: 권한 부족, 불명확한 요구 충돌, 시간 초과, 같은 접근법 두 번 실패.
- Result: C1에서는 미실행했다. C2 안전성 통과 후 네 fresh agent가 자기 worktree에서 실제 구현·회귀 검사를 완료했다. Main의 고정 oracle은 lease 양쪽 17/17, queue 양쪽 20/20 PASS였다. 기존 test method AST·보호 파일·mode·HEAD가 유지되고 각 작업은 허용된 구현과 테스트 두 파일만 변경했다. 시간·token 관찰치를 모두 기록했다. 성공은 동등하지만 queue의 두 비용 지표 모두 20% 미만 감소여서 AC-3은 UNPROVEN이다. 판정 기준을 바꾸거나 반복으로 유리한 결과를 찾지 않았다.

### T4 — 승인된 marker 경계와 preview 경고 수선

- State: completed
- Task type: implementation
- Depends on: C1의 B1/B2 재현 및 2026-09-09 사용자 수선 승인.
- Execution constraints: Python/Markdown 파일 소유권·CLI 회귀 검사 능력; Read/Edit/Write/Bash; 원본 제품 쓰기는 이 작업만 수행, Main의 병행 준비는 별도 fixture worktree에 한정; 재위임/Skill 호출 금지; 10분; 같은 접근법 두 번 실패 시 중단.
- Outcome: B1/B2를 제거한 C2, 새 후보의 독립 검토는 T2 후속으로 수행.
- Non-goals: baseline 수정, 공개 API·marker 이름·허용 파일 범위 변경, 테스트 약화, 불필요한 parser/의존성 추가.
- Read: CLAUDE 및 docs 현재 제품·보안·품질, initializer, 관련 두 테스트, 이 계획 B1/B2.
- Allowed writes: src/reporivet/initializer.py, tests/test_audit_adoption.py, tests/test_reporivet.py.
- Protected paths: 그 외 전부, 이 계획 포함. 기존 무관한 변경 보존.
- Acceptance: AC-2 및 B1/B2 Follow-ups의 제거 기준. LF/CR/CRLF의 기존 정상 marker·fence와 UTF-8 bytes 보존. U+2028/VT 외 Python-only separator도 소유권을 만들면 안 된다. 위험 입력은 원문 보존 또는 쓰기 전 거부해야 한다. preview는 human-only escaped/non-applyable 성격을 실제 출력에서 경고한다.
- Verify: 기존 결함에 대해 먼저 실패하는 focused 회귀 검사와 수선 후 성공; 같은 지원 Python 사용. Main이 canonical·exact candidate·독립 수락을 소유한다.
- Stop conditions: 범위 확대, 공유 계약 변경, 같은 접근법 두 번 실패.
- Result: 세 허용 파일만 수선했다. 기존 결함에 실패하는 focused 회귀 검사를 확인한 뒤 수선 후 관련 40 tests를 통과했다. Main이 주석을 한국어로 정리한 정확 C2를 고정했고 canonical 59 tests와 별도 문맥의 225 CLI 반례 검증을 통과했다. 안전성 Verifier의 AC-2 수락 추천과 Main의 동일 후보 canonical 결과를 합쳐 B1/B2 제거를 수락했다. 제품 경계·의존성·marker 계약 변경은 없다.

## Architecture Impact

현재 승인된 제품 수선은 기존 initializer 내부 marker 행 처리와 preview 안내에 한정한다. runtime·설정·의존성은 추가하지 않는다. C1 비교는 제품 변경 없이 수행한 역사적 결과다.

## Documentation Impact

이 계획에 조건·근거·결과를 기록한다. 기존 현재 제품 문서와 완료 계획은 변경하지 않는다. 미입증 결론을 향상 주장으로 바꾸지 않는다.

## Interfaces and Dependencies

기존 Python 표준 라이브러리·Git·gh·검증용 임시 Python 환경을 재사용한다. source를 frozen 복사하여 다른 작업 변경과 분리한다. agent 평가에 쓰기 병렬성이 필요하면 fixture repo의 별도 worktree를 사용한다. 공유 요구·oracle·모델·예산은 Main이 고정한다.

## Migration, Rollout, and Recovery

기존 v0.2 release와 target은 보존한다. source main의 제품 경계 전환과 기존 target migration은 별개다. PR merge 승인 조건 충족 전 원격에 쓰지 않는다. PR 후 실패 시 merge하지 않고 근거를 보고한다. 로컬 사용자 변경을 reset하거나 discard하지 않는다.

## Surprises and Discoveries

- 2026-09-09 — 원격 main=로컬 HEAD=226b15af1b8ccf1d82ba410322a214f1f593cc7e, main 보호 설정 false, 열린 PR 없음. 보호가 없더라도 검증을 생략하지 않는다.

## Decision Log

- 2026-09-09 — 사용자의 조건부 merge 요청에 따라 성능·성공·안전성 기준을 실행 전에 고정했다. no-change/미merge는 조건 미충족 시 정상 결과다. 코드량 감소만 보는 대안은 기능 제거와 효용을 혼동하므로 제외했다. 사전 한계로 공정한 비교가 불가능하면 그 결과를 공개하고 중단한다.

## Concrete Steps

1. 후보 사본과 manifest를 만든다.
2. 같은 환경에서 결정적 검사·공통 동작을 비교한다.
3. 공통 업무 pilot 및 독립 검토를 수행한다.
4. 조건 충족 시에만 PR·CI·merge; 그렇지 않으면 결과 기록.

### 2026-09-09 수선 재개

사용자의 “응 ㄱㄱ”를 B1/B2 수선·재검증과 조건부 비교 재개 승인으로 해석한다. main보다 훨씬 좋다는 검증 전 PR·merge 금지는 유지한다. T4에 제품 수정 경로를 명시적으로 배정했다. C1의 기존 결과는 수정하지 않고 C2 결과를 추가한다.

## Validation and Evidence

| Acceptance criterion | Task | Result | Evidence path or note | Verified candidate | Reviewer recommendation | Main/human approval |
|---|---|---|---|---|---|---|
| AC-1 | T1 | PASS | 원격 SHA·사본·전체 manifest 및 시작/종료 일치 | 아래 C1 | 확인 | Main 수락 |
| AC-2 | T1/T2 | FAIL | 일반 검사 성공과 별개로 사용자 본문 손실 재현 | C1 / main | 수락 보류 | Main FAIL 확인 |
| AC-3 | T1/T3 | UNPROVEN | 안전성 실패로 실제 개발 pilot 미실행 | C1 | 효용 미입증 | 미승인 |
| AC-4 | T2 | UNPROVEN | 독립 검토 수행, 안전성 및 효용 수락 불가 | C1 / main | merge 보류 | 미승인 |
| AC-5 | Main | UNPROVEN | 선행 조건 실패. PR·push·merge·release 미실행 | C1 | merge 보류 | 조건 미충족 |

### 정확 후보 C1과 환경

- Baseline: 원격 main `226b15af1b8ccf1d82ba410322a214f1f593cc7e`. 로컬 HEAD와 동일, 네트워크 `git ls-remote` 및 GitHub branch API로 확인했다.
- Candidate: 같은 base + nonignored 70개 파일의 SHA-256/modes + 기존 삭제 65개 목록. manifest SHA-256 `dc20c048343d89035e84530f3b525ba8c35789d043cf2bc1065fe838d20bdd78`.
- 고유 임시 LAB: `/private/var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-main-comparison-jsnfaj2d`. `candidate-manifest.json`, `baseline/`, `candidate/`에 고정 사본과 전체 식별 자료를 두었다. 두 source 사본은 각각 별도 detached Git worktree다. `/var` 표기는 같은 위치의 symlink 경유 경로이며 baseline 실행에는 실제 `/private/var` 경로를 사용했다.
- 검증 Python: `/private/tmp/reporivet-contract-check-BnWc7p/bin/python`, Python 3.13.15; pip 26.2, setuptools 84.0.0, wheel 0.48.0, packaging 26.3. baseline 하위 명령까지 동일 Python을 쓰도록 해당 bin을 PATH 앞에 두었다.
- 제품 코드·기존 문서·테스트의 원본과 C1 hashes는 결과 기록 직전에도 일치했다. 이 계획의 이후 증거 갱신은 C1의 제품 변경이 아니다. Baseline 검사 후 tracked diff도 없었다.

### Canonical 결과와 제외한 잘못된 비교

- Candidate: `PYTHON=<venv>/bin/python <LAB>/candidate/dev/check` — exit 0, 55 tests PASS, drift·compileall·diff check PASS. 로그 `candidate-check.log`.
- Baseline 최종: 실제 경로에서 cwd=`<LAB>/baseline`, `PATH=<venv>/bin:$PATH`, `PYTHON=<venv>/bin/python`, `./dev/check` — exit 0, 178 tests PASS 및 원래 runtime의 source 검사 PASS. 로그 `baseline-check-supported-python.log`.
- Baseline 초기 실행 1회는 `/var` symlink parent 거부로 exit 2. 실제 경로 재실행은 harness 내부의 `python3`가 시스템 3.9를 선택하여 tomllib 부재 등으로 실패했다. 원인을 확인해 PATH까지 고정한 뒤 성공했으며, 이 환경 실패를 candidate의 성능·정확성 우위로 세지 않았다.
- 178개와 55개는 서로 다른 기능 범위의 검사다. 소요시간 73.977초와 5.433초는 각각의 테스트 실행 관찰값일 뿐 같은 개발 업무의 속도 비교가 아니며, 성능 우위 근거로 사용하지 않는다.

### B1 — 사용자 본문 손실: 확인된 merge blocker

- Candidate 위치: `src/reporivet/initializer.py:322`의 `str.splitlines(keepends=True)`와 `:359–360`의 관리 블록 교체.
- Baseline 대응 위치: `src/reporivet/initializer.py:542`, `managed_block_span()`.
- Markdown 행 종료는 LF/CR/CRLF인데 Python splitlines는 U+2028, VT 등도 행 구분으로 처리한다. 그래서 사용자 텍스트 뒤의 inline marker를 standalone 관리 marker로 오인한다.
- 위반: SPEC-003 REQ-ENTRY-001/006, AC-1/3의 사용자 bytes 보존과 잘못된 marker 안전 처리, 이 계획 AC-2.

UTF-8 AGENTS.md 입력(Python 문자열 표기):

```python
"User-owned inline example <!-- reporivet:entrypoints:start -->\nMUST_KEEP_USER_BODY\n<!-- reporivet:entrypoints:end -->\n"
```

실제 재현에서는 ` `을 해당 Unicode 문자로, `\n`을 LF로 기록한다. ` ` 대신 `\x0b`를 기록해도 동일하다. Baseline은 marker 이름만 `<!-- reporivet:start -->`와 `<!-- reporivet:end -->`로 바꾼 동등 입력을 사용했다.

각 고유 tempfile root에서 동일 Python과 각 source의 절대 PYTHONPATH로 다음을 실행했다.

```sh
python -m reporivet init --root <fresh-target>
```

| Version | Separator | CLI exit | 사용자 prefix 보존 | MUST_KEEP_USER_BODY 보존 |
|---|---|---|---|---|
| Candidate | U+2028 | 0 | yes | **no** |
| Candidate | VT U+000B | 0 | yes | **no** |
| Baseline | U+2028 | 0 | yes | **no** |
| Baseline | VT U+000B | 0 | yes | **no** |

Main이 독립 검토 이후 직접 CLI에서 네 경우를 재현했다. 따라서 신규 회귀가 아닌 양쪽에 남아 있는 안전성 결함으로 분류한다. 일반 tests가 모두 통과해도 AC-2는 FAIL이다. 기존 테스트는 일반 inline/fenced/partial marker를 검사하지만 Markdown과 Python의 행 경계 차이를 다루지 않는다.

재현 script와 입력/출력 hashes 및 결과 JSON은 LAB의 `reproduce_marker_loss.py`, `marker-loss-results.json`에 있다. 스크립트는 고유 임시 target만 변경했으며 source 파일은 수정하지 않았다. 비공개 사용자 입력은 포함하지 않는다.

### B2 — preview 경고 요구 불충족

Candidate `src/reporivet/initializer.py:82–90`과 실제 `init --dry-run` 출력을 확인했다. unified diff와 fingerprint는 출력하지만 escaped human preview이며 적용 가능한 patch가 아니라는 경고를 출력하지 않는다. SPEC-003 AC-2는 preview의 경고를 요구한다. 문서 설명은 존재하나 CLI 출력과 요구의 불일치는 남는다. B1과 같은 데이터 손실 심각도로 취급하지 않는다. 출력은 LAB `preview-warning.log`에 기록했다.

### 실제 개발 pilot의 미실행 범위

표준 라이브러리만 쓰는 lease 만료 버그수정과 pending pagination 기능 추가의 공통 fixture 원본을 준비했다. Golden 요구·동일 원본을 고정하기 위한 fixture 전용 로컬 commit만 만들었다. Reporivet source commit은 만들지 않았다. trial 초기화 스크립트는 작성했지만 실행하지 않았고, 구현 agent를 실행하지 않았다. 시간·토큰·코드 수정 성공률은 측정하지 않았다.

독립 제품 검토에 따라 baseline의 `configuration=review` 준비 비용과 실제 개발 효용을 구분해야 하며, 작은 공통 oracle은 기존 전체 Gate의 대체 품질을 입증하지 못한다. 이 한계까지 해소하지 않은 채 훨씬 낫다고 하지 않는다.

### C2 — 승인된 수선과 독립 안전성 재검증

- C2는 같은 base의 nonignored 70파일·65삭제 목록으로 고정했다. LAB의 `candidate2/`와 `candidate2-manifest.json`, manifest SHA-256 `bd2c3badd52b3790cf1c8d96b56c74e939d73d072968da72102d1d3be034f147`가 정확 후보다. C1 이후 변경은 initializer·관련 테스트 두 파일·이 계획뿐이다.
- `_managed_span()`은 LF/CR/CRLF만 행 경계로 인식한다. Fence 종료의 뒤쪽 공백도 `[ \t]`만 허용하여 Unicode separator가 fenced 예시의 소유권을 바꾸지 못하게 했다. Preview에는 escaped human-only/non-applyable 경고와 fingerprint의 비승인·비잠금 성격을 실제 출력한다. 공개 marker/API·의존성·설치 범위는 그대로다.
- Implementer는 기존 코드에 새 focused 검사를 실행하여 실패를 먼저 확인했다. 수선 후 focused 6 methods와 관련 두 모듈의 40 tests가 통과했다. Main은 추가된 행 경계 설명 주석만 한국어로 바꾼 후 C2를 고정했다.
- Main canonical: cwd=`<LAB>/candidate2`, `PATH=<venv>/bin:$PATH`, `PYTHON=<venv>/bin/python`, `./dev/check` — exit 0, **59 tests PASS**, unittest 5.640초, distribution·source projection drift·compileall·diff check 포함. `candidate2-check.log`에 기록했다. 이 시간은 main과의 개발 속도 비교로 사용하지 않는다.
- 별도 문맥의 안전성 Verifier는 C2 전체 hashes/modes/삭제목록을 시작·종료 확인하고 C1/C2 실제 diff를 검토했다. 기존 U+2028/VT payload에서 C1은 본문 삭제·exit 0, C2는 bytes 완전 보존·exit 2였다. 관련 40 tests와 별도 **225개 CLI 반례**가 통과했다. 추가 반례는 두 marker 모두 inline인 경우, 8종 separator와 LF/CR/CRLF, 추가 Unicode 공백과 양쪽 fence, AGENTS/CLAUDE, init/upgrade, preview/apply 및 bytes/mode/mtime 보존을 포함한다.
- Verifier는 담당 범위의 AC-2 수락을 추천했으나 canonical·효용·merge 승인으로 확장하지 않았다. Main은 동일 후보 canonical과 합쳐 B1/B2 수선 및 C2 안전성 근거를 수락한다. 이 결과만으로 AC-3 또는 merge를 승인하지 않는다.
- 구현 파일 SHA-256: `src/reporivet/initializer.py` = `e72b0c49b9f00d3ca7bbb888d8d8202e5f84193a1c1d99cf8816fc68cc48795f`, `tests/test_audit_adoption.py` = `7cc5254ecf9600f39ffcb8c329970f9f92385286752ddbb3a82b8f4f95b7265f`, `tests/test_reporivet.py` = `51f650cbcd47b2c95794de175cb79ca06f8cba89cc96df40cec486ecbc293620`; 모두 mode 0644. 원본 전체 파일과도 대조했으며 Main의 이후 계획 기록만 C2와 다르다.

### 실제 개발 pilot — 실행 전 고정 계약과 준비

- stdlib-only Dispatch Ledger fixture의 동일 원본에서 별도 Git worktree 4개를 만들었다. Lease 만료 버그수정은 trial-1=main, trial-2=C2, queue cursor pagination 기능추가는 trial-3=C2, trial-4=main이다. Agent에게 조건 이름이나 형제 작업·oracle을 보여주지 않았다.
- 두 버전에 동일 기본 `python -m reporivet init --root <trial> --name dispatch-ledger-fixture`를 사용했다. `--claude`, baseline-only skip 옵션은 쓰지 않았다. Main의 초기화 관찰에서 main은 50파일/343471 bytes를 생성하고 기존 `.gitignore`를 의도대로 관리했으며, C2는 AGENTS.md 1파일/2377 bytes만 생성하고 원본 파일을 변경하지 않았다. 이는 설치 표면의 차이이며 개발 성공 또는 비용 우위와 별개다.
- Main은 baseline의 `configuration=review`를 실제 확인 후 `ready`로 바꾸고, stdlib fixture에 맞게 bootstrap 설치 명령을 없애고 source 경로를 `dispatch`로 지정했다. 처음 code-map stale을 발견해 기존 생성 명령으로 갱신했다. 생성 파일을 Git index에 포함한 후 `./dev/docs-index`, `./dev/code-map`, `./dev/check`가 두 baseline fixture에서 모두 성공했다. 양쪽 모두 준비 상태를 fixture 전용 로컬 commit으로 고정했다. Baseline의 `baseline=draft`는 그대로이며 전체 Gate/baseline 확립을 주장하지 않는다. Source commit은 만들지 않았다.
- `prepared-trial-manifests.json`은 초기 파일 hashes와 fixture commit을, `baseline-trial-setup.json`과 `candidate2-trial-setup.json`은 초기화 변경 범위를 기록한다. 준비·구성 검토 비용은 개발 agent 비용과 분리한다.
- 공통 요구는 `handbook/requirements.md`다. Lease는 strict expiry, 실제 시각 비교, aware datetime 및 positive non-bool integer TTL 검증을 요구한다. Queue는 keyword-only exclusive cursor, status/cursor 선필터 후 정렬·limit, 입력 검증과 비변경을 요구한다. 폐기된 `notes/archive.md`는 현재 요구가 아니다.
- Main의 외부 oracle `evaluate_trial.py` SHA-256은 `bba3d0af7b856652f169ef9a4e541446246dc2420936380145be298f95b37b71`이다. 원본은 기존 tests 3개가 통과하지만 lease oracle 3/17, queue oracle 4/20에 그쳤다. 결과를 본 뒤 oracle·우위 기준을 바꾸지 않는다. 작은 oracle은 전체 runtime Gate나 모든 timezone 상태를 대체하지 않는다.
- 네 fresh `general-purpose` agent에 동일 `model=sonnet`, 도구·권한·5분 예산, 재위임/Skill/네트워크/설치 금지, 자기 root 제한을 적용했다. 실제 모델 ID는 host가 별도로 노출하지 않으므로 요청한 alias 이상으로 단정하지 않는다. `trial-prompt-template.txt`, `frozen-trial-prompts.json`에 실행 전에 입력을 고정했다. 같은 작업의 prompt는 root만 다르다. 각 agent는 자기 AGENTS부터 읽고 코드와 회귀 검사를 실제 수정한다.
- Source 운영의 새 세 규칙과 target AGENTS template은 별개다. 이 비교는 각 제품이 설치한 진입점 아래의 개발 작업을 비교하며, 세 source 규칙만의 인과 효과를 분리한 실험이 아니다. 공통 host 정책·병렬 호출·캐시·호출 대기의 영향을 배제하지 못한다. Host 시간과 subagent token 관찰값을 그대로 공개하며 실제 과금이나 장기 생산성으로 환산하지 않는다.

### 실제 개발 pilot — 관찰 결과와 Main 판정

각 구현자가 아니라 Main이 고정 외부 oracle과 전체 fixture tests를 다시 실행했다. 네 trial 모두 성공했다. `verify_trials.py`는 보호 파일 hashes, 파일 mode, fixture HEAD, 기존 test method AST 보존과 diff check도 확인했다. 구현자들이 추가한 테스트 개수가 다르므로 그 개수를 정확성 우위로 세지 않았다.

| 작업 | 조건 | 외부 oracle | Host 시간 | Host tokens | Tool uses |
|---|---|---|---|---|---|
| Lease 버그수정 | main / trial-1 | 17/17 PASS | 200762 ms | 33782 | 31 |
| Lease 버그수정 | C2 / trial-2 | 17/17 PASS | 189658 ms | 24277 | 30 |
| Queue 기능추가 | main / trial-4 | 20/20 PASS | 139622 ms | 31342 | 23 |
| Queue 기능추가 | C2 / trial-3 | 20/20 PASS | 131170 ms | 25131 | 19 |

- 비용은 fresh agent 완료 알림의 `usage.duration_ms`, `usage.subagent_tokens`, `usage.tool_uses`에서 가져왔다. 구현자 추정치나 재개 agent의 누적치를 사용하지 않았다. `pilot-host-metrics.json`에 원시 관찰값, `pilot-cost-comparison.json`에 계산값이 있다.
- Lease는 시간 5.530927167491856%, token 28.136285595879464% 감소했다. 이 한 쌍은 pilot 비용 문턱을 넘었지만 반복 확증은 아니다.
- Queue는 시간 6.053487272779361%, token **19.81685916661349%** 감소했다. 두 비용 지표 모두 사전에 고정한 20%에 미달했다. 소수점 반올림으로 통과시키지 않는다.
- 성공은 양쪽 모두 2/2이며 네 trial은 허용된 두 파일만 변경했다. 동등 성공과 절감 방향의 pilot 신호는 확인했지만 두 작업 모두의 유의미 비용 절감·반복 확인은 성립하지 않는다. **AC-3은 UNPROVEN**이다. 후보가 나쁘거나 실용 가치가 없다는 반증도 아니다.
- 사전 종료 규칙에 따라 pilot 기준 미달로 반복 확증을 시작하지 않는다. 좋은 값이 나올 때까지 반복하거나 oracle·20% 기준을 사후 조정하지 않는다. 토큰·시간 관찰치의 작은 표본과 host 잡음 때문에 이 숫자를 보편적 생산성 추정치로 일반화하지 않는다.
- 증거: `pilot-verification-results.json`, `trial-*-oracle.json`, `trial-*-main-tests.log`, `trial-*-diff.patch`, `prepared-trial-manifests.json`. Initial oracle hash는 실행 전후 그대로다. 평가 fixture·scripts·logs는 임시 LAB에만 있고 제품이나 target에 추가하지 않았다.

## C1 시점의 Outcomes and Retrospective

조건부 merge 판단은 **보류**다. 사용자 본문 손실이라는 필수 안전성 실패가 있고 개발 효용도 UNPROVEN이다. 기존 main에도 같은 결함이 있음을 확인했지만, 양쪽이 동일하게 실패한다는 이유로 candidate를 승인하지 않는다. 원격 branch·PR·release를 만들거나 수정하지 않았고 source commit/push/merge도 하지 않았다. 제품 수정은 이번 비교 범위에 포함하지 않아 적용하지 않았다.

## C1 시점의 Follow-ups

- **B1, owner Main:** Markdown 행 경계를 정확히 처리하도록 marker 소유권 판정을 수선하고 U+2028/VT 및 다른 비Markdown separator 회귀 검사를 추가해야 한다. 제거 조건은 사용자 본문 보존 또는 안전 거부, 기존 marker/fence 동작 유지, 전체 검사와 새 exact candidate의 독립 검토 통과다. 이 계획을 재개할 때 별도 구현 범위를 승인·배정한다.
- **B2, owner Main:** preview 출력에 요구된 non-applyable/escaped human preview 경고를 명시하고 회귀 검사한다. 완료 기준은 실제 CLI 출력과 SPEC AC-2 일치다.
- 안전성 수선 후에도 실제 개발 효용 비교가 통과하기 전에는 조건부 merge 권한을 사용하지 않는다.

## C2 최종 독립 검토와 수락 경계

최종 비교 Verifier는 각 비교쌍의 기존 입력 hashes와 root 이외 동일 prompt를 확인하고 네 구현 diff를 읽었다. 기존 assertion 약화나 oracle 응답만을 겨냥한 구현은 발견하지 않았다. 모든 trial postimage의 hashes/modes가 일치했고, Python 3.13.15로 oracle·unittest를 독립 재실행하여 lease 양쪽 17/17, queue 양쪽 20/20 및 fixture tests 각각 8/7/9/9 성공을 확인했다. 비용 감소율도 원시 기록에서 재계산했다. 추천은 **AC-3 UNPROVEN, AC-4 PASS(담당 검토 범위), PR·merge 미실행**이다. Main은 이를 수락한다.

Verifier가 확인한 한계도 유지한다. Oracle의 17/20 사례는 독립적인 agent 성공 표본 수가 아니다. DST/fold·극단 입력 등 전체 입력 공간을 증명하지 않는다. 기존 test method AST 검사만으로 setup·import 우회를 일반적으로 배제할 수 없으나 이번에는 실제 diff 검토를 추가했다. Nonignored 파일 검사는 모든 ignored 파일·세션 접근 준수까지 증명하지 않는다. Alias 이상의 backend 모델 ID, 순수 추론 시간·실제 과금, 초기화 비용, 전체 Gate, source 운영 규칙의 개별 효과, 장기 유지보수·migration 효용은 측정하지 않았다.

| Acceptance criterion | Task | Result | Evidence path or note | Verified candidate | Reviewer recommendation | Main/human approval |
|---|---|---|---|---|---|---|
| AC-1 | T1 | PASS | C2 manifest, 원본과 frozen 파일·mode·삭제목록 대조, 환경·명령 기록 | C2 / 고정 main | 동일 후보 확인 | Main 수락 |
| AC-2 | T1/T2/T4 | PASS | C2 canonical 59 tests, 독립 40 tests와 225 CLI 사례, B1/B2 해소 | C2 | 안전성 담당 범위 수락 추천 | Main 수선·안전성 수락 |
| AC-3 | T1/T3 | UNPROVEN | 양쪽 개발 성공 2/2. Queue 시간·token 절감 모두 20% 미달, 반복 확증 없음 | 고정 main/C2에서 준비한 네 fixture postimages | 효용 우위 미입증 | 우수성 미승인 |
| AC-4 | T2 | PASS | 경계·제거 기능·준비 공정성·oracle·계산 독립 검토 및 재실행 | C2 / 네 fixture postimages | 담당 검토 범위 PASS | Main 검토 근거 수락; 제품 우위 아님 |
| AC-5 | Main | UNPROVEN | 게시 전제 미충족으로 source commit/push·PR·merge 미실행 | C2 | 미게시 추천 | merge 미승인; 조건부 권한 경계 준수 |

## Outcomes and Retrospective — C2 보고 시점

B1/B2 수선과 검증, 실제 개발 pilot 및 독립 비교 검토를 마쳤다. 그러나 사용자 조건인 **“기존 main보다 훨씬 좋음”은 입증하지 못했으므로 PR·merge하지 않는다.** 개선 방향의 관찰치를 없던 것으로 취급하지도, 문턱 미달을 반올림·평균·다른 지표로 바꿔 통과시키지도 않는다. 비교 실행 완료와 제품 우수성·게시 수락은 별개다.

필수 우수성 기준이 UNPROVEN이므로 이 계획을 완료 수락하거나 completed로 옮기지 않고 `blocked`로 둔다. 기존 미커밋 사용자 변경과 이번 로컬 수선은 보존하며 source commit·push·PR·merge·release는 수행하지 않았다. 최종 문서 영향은 이 계획에서 해소했다. 제품은 이미 요구된 marker 안전성·preview 경고를 충족하도록 수선했으므로 제품 스펙·architecture·migration 또는 생성 template에 추가 변경이 필요하지 않다.

최종 원본 후보는 C2와 같은 제품·기존 문서·테스트에 이 계획의 결과 기록만 더한 상태다. LAB의 `final-source-manifest.json`은 base + 전체 nonignored 파일 hashes/modes + 삭제목록으로 이를 식별한다. 자기 hash를 자기 문서 안에 넣는 대신 외부 manifest로 식별하며 fingerprint는 승인 자체가 아니다. 최종 원본 검사 기록은 `final-source-check.log`이고 Main의 마지막 확인에 사용한다.

## Follow-ups — C2 보고 시점

- **B1/B2, owner Main: 해결.** C2의 전체 검사·독립 재검증·Main 수락으로 제거 조건을 충족했다. 과거 main과 기존 target을 소급 수정하거나 migration하지 않았다.
- **AC-3, owner Main: UNPROVEN.** 동일 예산의 이번 pilot 기준 미달로 추가 반복·게시를 중단했다. 향후 평가를 재개하려면 목적·표본·환경·비용 지표를 관찰 전에 다시 명시한 범위가 필요하다. 이번 수치를 유리하게 해석하려고 기존 기준을 소급 변경하지 않는다.
- C2 보고 시점에는 조건부 merge를 승인하지 않았다. 아래 후속 사용자 결정이 게시 권한을 새로 부여했으며 기존 실험 결과를 변경하지 않는다.

## M4 — 후속 사용자 승인에 따른 PR 통합

사용자는 토큰 감소의 실질적 가치와 merge 적합성을 질문했다. Main은 두 작업에서 동등 성공과 낮은 비용을 관찰했고 현재 entrypoint-only 목적에서는 merge를 추천하되, 원래 20%·반복 확증 기준과 보편적 우위는 미입증임을 설명했다. 이에 사용자가 “ㄱㄱ”로 실행을 승인했다. 이는 통계적 판정을 바꾼 것이 아니라 제한된 근거와 제품 전환을 이해한 뒤의 별도 제품 수락 결정이다. 이전 게시 보류 문장·AC-5는 당시 권한을 기록한 것으로, 이번 공개에는 아래 수락 기준을 적용한다.

- **M4-AC1:** 이전 검토 후보와 변경 경계를 대조하고 제품 변경은 추가하지 않는다. 비밀·임시 실험·의도하지 않은 파일을 게시하지 않는다.
- **M4-AC2:** 정확한 PR 후보의 canonical과 게시 전 독립 검토를 통과한다. 기존 안전성·테스트·제품 요구를 약화하지 않는다.
- **M4-AC3:** 별도 branch/PR로 게시하고 현재 원격 base 및 필수 CI를 확인한 뒤 정상 merge한다. 보호 우회·force push·release·패키지 배포·기존 target migration은 하지 않는다. 원격 base가 변경되면 통합 후보를 재검증한다.
- **M4-AC4:** 최종 merge SHA와 CI 결과, 로컬 상태를 확인하고 결과를 보고한다. AC-3의 UNPROVEN 및 pilot 한계는 PR에도 명시한다.

### T5 — Main의 게시 및 독립 검토 통합

- State: completed
- Task type: support
- Depends on: T1–T4 및 후속 사용자 승인.
- Execution constraints: Git/GitHub/검증 능력; Main만 source 계획·index·branch·commit·원격 PR/merge를 변경; 별도 읽기 전용 Verifier는 10분, 재위임/Skill/설치/원격 쓰기 금지. Main 게시 예산 30분, 같은 접근법 두 번 실패 시 중단.
- Outcome: 명시 승인된 현재 전체 entrypoint-only 후보의 PR 및 merge 증거.
- Allowed writes: 이 계획과 수락 후 completed 경로 이동, 빈 active 디렉터리 보존용 `.gitkeep`, 현재 고정 후보 전체의 의도적 staging/commit/push, 해당 PR 본문·merge와 실제 merge 결과를 기록하는 문서-only 후속 PR. 임시 검증 증거는 기존 LAB만 사용.
- Protected paths: 새 제품 변경, 관련 없는 사용자 파일·설정, 기존 release/target 및 권한 정책.
- Non-goals: 위 공통 Non-goals, 성능 실험 재채점·확증 주장.
- Acceptance: M4-AC1–4. 원래 AC-3은 게시의 필수 확증 조건에서 분리하지만 판정은 UNPROVEN으로 보존한다.
- Verify: source canonical, 독립 전체 변경 검토, staged tree 대조, 원격 CI·merge SHA·로컬 clean 확인.
- Stop conditions: 새 결함·예상하지 않은 후보 변경·CI 실패·원격 통합 충돌·권한 부족.
- Result: 게시 전 M4-AC1/2 근거를 수락했다. 이전 최종 후보와의 차이는 Main의 이 계획 기록뿐이다. Python 3.13.15 canonical 59 tests가 통과했다. 별도 문맥의 전체 변경 검토는 새 blocker를 발견하지 않았고 58 tests, offline wheel/sdist build·inventory, 계약 drift·diff를 확인했다. 검토 시작/종료의 계획 제외 fingerprint는 `39f30156bdc760254c0e01c592b4d51ba89ecdd74d69cc2ccf17b4715dec527b`로 동일했다. 설치/네트워크 금지인 Verifier가 미실행한 distribution install/uninstall은 Main canonical에서 통과했다. 이후 실제 Linux/Python 3.11 PR CI가 성공했고, 같은 exact head를 정상 merge했다. Merge 후 main CI도 성공했으며 로컬 main을 fast-forward한 뒤 tree 일치·clean을 확인했다. 아래 M4 최종 근거를 Main이 수락하여 T5를 완료한다.

### M4 결정의 이유와 경계

기존 영구 source 정책·Git·gh·dev/check를 그대로 사용한다. 변경하지 않는 대안도 안전하지만 사용자는 현재 제품 목표에 맞는 개선을 수락했다. 19.8169%를 20%로 반올림하거나 작업 평균으로 확증을 주장하는 대안은 증거 왜곡이므로 제외했다. 게시 자체를 승인한 사용자 결정과 실험 판정을 분리해, 유용한 변경을 통합하면서 검증 한계를 숨기는 실패를 방지한다. 새로운 보안/기능 결함이나 CI 실패가 생기면 merge를 중단하며, 장기 효용은 새 사전 설계 실험이 있을 때만 재평가한다.

## M4 최종 수락과 완료 근거

- 제품 PR: [#3](https://github.com/gkrtjd99/Reporivet/pull/3), `MERGED`, 2026-09-09T04:53:15Z.
- Exact PR head: `f1402802c939119389fbe99eae7cf3a0b014c245`; base: `226b15af1b8ccf1d82ba410322a214f1f593cc7e`.
- [PR CI](https://github.com/gkrtjd99/Reporivet/actions/runs/34312645799): Linux/Python 3.11 `verify` SUCCESS. 로컬 canonical도 Python 3.13.15에서 59 tests PASS.
- Merge SHA: `e4aa3b9fcf794eef834273d8fecda10271e6f1b3`.
- [Merge 후 main CI](https://github.com/gkrtjd99/Reporivet/actions/runs/34312711299): SUCCESS.
- Main은 `git diff --exit-code f1402802c939119389fbe99eae7cf3a0b014c245 HEAD`로 merge tree와 검토 후보의 완전 일치를 확인했다. 로컬 main은 원격 main으로 fast-forward했고 작업 트리는 clean이었다.
- Merge에는 `--match-head-commit`을 사용했고, 보호 우회·force push·release·패키지 배포·기존 target migration은 하지 않았다. 원격 base는 검토한 SHA 그대로였다.

| Acceptance criterion | Result | Evidence | Reviewer recommendation | Main/human approval |
|---|---|---|---|---|
| M4-AC1 | PASS | 이전 후보 대조·명시적 staging·게시 파일 독립 검토 | 담당 범위 PASS | Main 수락 |
| M4-AC2 | PASS | 별도 게시 검토, 로컬 59 tests와 exact PR CI | CI 확인 전 조건부 추천; 실제 CI로 미검증 부분 해소 | Main 수락 |
| M4-AC3 | PASS | PR #3 MERGED, exact head/base·정상 merge·CI | 새 blocker 없음 | 후속 사용자 승인 + Main 실행 수락 |
| M4-AC4 | PASS | merge SHA·main CI·tree 일치·로컬 clean 확인 | 원격 실행 확인은 Main 담당 | Main 확인·수락 |

원래 AC-3의 **UNPROVEN**은 그대로다. 완료는 보편적 성능 우위의 인증이 아니라, 후속 사용자 승인에 따른 제품 통합과 근거 확인의 완료를 의미한다. M4 수락 후 이 계획을 completed로 이동한다. 이 문서 이동·실제 merge 근거 기록은 작은 문서-only 후속 PR로 남겨 제품 merge 전에 미래 결과를 완료했다고 기록하지 않는다. 빈 active 디렉터리는 `.gitkeep`으로 보존한다. 제품·테스트·CI를 추가 변경하지 않으므로 이 기록을 위해 제품 작업을 재개하지 않는다.
