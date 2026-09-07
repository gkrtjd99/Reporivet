---
id: PLAN-2026-0006
kind: exec-plan
status: verifying
owner: main
area: harness
created: 2026-09-08
updated: 2026-09-08
base_commit: "364a77346d542042307bdcc3f5a84602ec105c08"
integrated_commit: HEAD
verified_commit: ""
traceability: 0
product_spec: ""
verification_run: ""
manifest_sha256: ""
gate_verdict: ""
gate_review_reason: ""
---

# 검증된 0.2.0 GitHub 수동 릴리즈

## Purpose / Big Picture

사용자는 PR#1 merge 후 “응 릴리즈 배포 실행”이라고 명시했다. 검증된 merge commit `364a77346d542042307bdcc3f5a84602ec105c08`의 0.2.0 wheel과 체크섬을 GitHub Release로 제공한다. 기존 local release-ready 절차를 새 자동화 없이 사람이 승인한 수동 게시로 잇는다. Reporivet 제품 자체가 GitHub를 조작하는 기능을 추가하는 것은 아니다.

## Progress

- [x] exact merge 후보·기존 절차·main CI 확인.
- [x] offline wheel 빌드와 Sonnet의 실제 산출물 검증.
- [x] GitHub release 게시 및 원격 tag/download hash 확인.
- [x] 근거·Documentation Impact 정리 및 정식 계획 종료 후보 준비.

## Context and Orientation

제품 버전은 0.2.0이다. 기존 README/QUALITY의 local gate는 외부 게시를 수행하지 않는다. 이번 사용자의 별도 게시 지시가 이 수동 작업의 권한이다. GitHub 인증 경로는 앞선 PR 생성·merge에서 실제 동작했으므로 과거 completed 계획의 읽기 전용 인터페이스 제한을 현재 상태로 재사용하지 않는다. PyPI 인증/게시 workflow 및 기존 tag/release는 없다.

## Scope

- exact merge commit을 source로 offline wheel build, inventory 및 fresh install/uninstall 검증.
- 기존 GitHub 저장소에 `v0.2.0` tag와 release, wheel·SHA256SUMS·검증 요약 게시.
- 이 계획과 release notes에 실제 결과 및 한계를 기록.

## Non-goals

제품 코드·설정·기존 completed 역사 수정, 새 publish workflow, runtime dependency, PyPI/TestPyPI 게시, 서비스 배포, credential 생성·노출, force-push/tag 이동, 기존 release 덮어쓰기.

## Acceptance Criteria

- **AC-1:** merge commit과 main CI가 일치하고 version 0.2.0인 wheel을 네트워크·의존성 해결 없이 빌드한다.
- **AC-2:** 별도 Sonnet이 실제 업로드 후보 wheel의 inventory·설치·generated runtime 동작을 확인하고 source 수정 없이 근거를 반환한다.
- **AC-3:** GitHub `v0.2.0`이 exact merge commit에 결속되고 다운로드한 wheel 및 체크섬이 로컬 후보와 일치한다. PyPI·미실행 플랫폼 성공을 주장하지 않는다.

## Milestones

M1은 exact artifact 검증, M2는 게시 및 read-back 검증이다. 검증 실패 시 게시하지 않는다.

## Task Packets

### T1 — Main exact artifact 준비

#### State

complete

#### Task type

implementation

#### Depends on

none

#### Execution constraints

Main만 계획·Git integration 소유. local archive/build/log 쓰기만. 단일 writer. 동일 접근 두 번 실패 시 중지. 5분.

#### Outcome

exact merge의 offline wheel과 hash를 고정한다.

#### Non-goals

제품 코드 수정, 자동배포 구현, 외부 설치.

#### Read

QUALITY local gate, pyproject, 기존 distribution test 절차.

#### Allowed writes

이 계획, 자기 임시 archive/artifact/log, 로컬 실행 기록 commit.

#### Protected paths

나머지 tracked 파일, 기존 completed 계획, 외부 publication은 T3 전 금지.

#### Acceptance

AC-1

#### Verify

main CI exact head, pip wheel --no-build-isolation --no-deps --no-index, wheel metadata와 hash.

#### Stop conditions

source/버전 불일치, build 실패, 기존 release/tag 충돌.

#### Result

main CI run 34146538306은 merge 364a773에서 Ubuntu/Python3.11.16 전체178 tests PASS, Gate REVIEW(shadow). 기존 제품 후보의 독립 검증 및 Python3.12/3.13 결과는 PLAN-0005 기록에 있다. `/private/tmp/reporivet-release-020-H7ZI4J/source`를 exact merge의 git archive로 생성하고 offline pip wheel rc0을 확인했다. 실제 후보 `dist/reporivet-0.2.0-py3-none-any.whl`, SHA256 `b8fdfee1f2667dc9c8edb2204cb5cabeec753df8682a56ab384735bdff67dc6c`, metadata name/version/Python>=3.11 및 runtime dependency 없음 확인. build.log는 같은 stage에 보존한다.

### T2 — Sonnet actual wheel 검증

#### State

complete

#### Task type

verification

#### Depends on

T1

#### Execution constraints

Sonnet 별도 context, 원본 read-only. 자기 tmp/log만 쓰기. 재위임·게시 금지. 동일 접근 두 번 실패 시 중지. 6분.

#### Outcome

고정 wheel의 배포 적합성을 독립 확인한다.

#### Non-goals

코드 수정, 자기 결과 승인, 외부 설치·게시.

#### Read

T1 exact source/artifact 및 기존 distribution test/QUALITY 요구.

#### Allowed writes

자기 임시 venv/fixture/log만.

#### Protected paths

모든 원본 tracked 파일과 T1 artifact bytes, tag/release 및 외부 저장소.

#### Acceptance

AC-1, AC-2

#### Verify

wheel metadata/inventory, fresh venv no-index install, CLI/init/doctor/generated check, package uninstall 후 copied runtime context/check. exact archive distribution test. hash 변화 없음.

#### Stop conditions

candidate 불일치, 외부 설치 필요, 제품 결함, scope 확장.

#### Result

Sonnet이 실제 wheel hash를 재확인하고 Python3.12.14 fresh venv no-index/no-deps 설치·실제 uninstall을 검증했다. wheel48 entries, source/wheel asset38개 bytes 일치, dependency/cache/bytecode/금지경로0개. CLI help/init/doctor, generated check/verify, uninstall 후 context/check/verify 성공 및 isolated import의 ModuleNotFoundError 확인. Git 없는 fixture Gate REVIEW는 한계로 구분한다. exact source distribution test1개는 기존 Python3.13 build 환경에서 PASS(7.515s). 최초 Python3.12 fresh venv의 source rebuild는 backend 부재로 환경 실패했으며 실제 wheel 실행 성공과 구분했다. /tmp symlink 거부 후 realpath 대조 정상. 로그 `/private/tmp/reporivet-pr3-fixture/logs/`. Main은 추천 PASS를 수락했다. 공개 요약은 artifact의 VERIFICATION.md다.

### T3 — Main 게시 및 read-back

#### State

complete

#### Task type

implementation

#### Depends on

T2

#### Execution constraints

기존 인증 gh와 Git만 사용. release 쓰기는 Main 단독. 동일 접근 두 번 실패 시 중지. 5분.

#### Outcome

검증된 wheel을 공개하고 tag와 다운로드 bytes를 확인한다.

#### Non-goals

PyPI, 자동배포, tag 이동, clobber, 기존 release 삭제.

#### Read

T1/T2 근거, gh release help 및 원격 현재 tag/release 상태.

#### Allowed writes

이 계획, 자기 release notes/checksum/download 디렉터리, origin의 새 v0.2.0 tag 및 해당 release/assets.

#### Protected paths

제품 source/config/history, 다른 tag/release/저장소, 인증 설정.

#### Acceptance

AC-3

#### Verify

원격 tag exact SHA, release 공개 상태, fresh asset download SHA256 일치 및 API assets 목록.

#### Stop conditions

기존 tag/release 충돌, 인증 거부, asset 불일치, 게시 범위 변경 필요.

#### Result

https://github.com/gkrtjd99/Reporivet/releases/tag/v0.2.0 공개 완료. --target으로 merge364a773을 지정했고 git ls-remote의 실제 tag SHA도 일치했다. isDraft=false/isPrerelease=false 및 wheel/SHA256SUMS/VERIFICATION.md uploaded 상태 확인. gh release download로 세 파일을 새 경로에 내려받아 로컬 후보와 bytewise 일치 확인. wheel SHA256 b8fdfee1f2667dc9c8edb2204cb5cabeec753df8682a56ab384735bdff67dc6c, SHA256SUMS b210563fd55a220053e61be73ea7623d98df52f41937503cdca08721fa384ee8, VERIFICATION.md 52c864065ae60a17fbf1282847842a9bdd7d75eabb69dde41f83aa446937644f. Main은 AC-3을 수락했다. PyPI 및 서비스 배포는 수행하지 않았다.

## Architecture Impact

없음. 기존 package 및 copied runtime 경계를 그대로 배포한다. 자동 게시 기능이나 production dependency를 추가하지 않는다.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| 이 계획 | create/update | 사용자 게시 권한·exact artifact·원격 결과 보존 | Main | resolved |
| GitHub release notes | create | 설치 방법·검증·기존 local gate와 수동 게시 구분 | Main | resolved |
| PRODUCT/ARCHITECTURE/QUALITY/README | none | 제품 기능 및 local gate는 여전히 게시하지 않으며 수동 릴리즈는 외부 운영 기록으로 구분 | Main | resolved |

## Interfaces and Dependencies

기존 pip/setuptools build, GitHub CLI release interface 및 stdlib 검증만 사용한다. Main은 build→독립검증→게시의 순서와 artifact 소유권을 고정한다. source 병렬 쓰기 없음.

## Migration, Rollout, and Recovery

새 v0.2.0 tag만 merge SHA에 결속하고 검증한 assets를 한 release로 게시한다. 기존 tag/release가 생기면 덮어쓰지 않고 중지한다. 사용자 문서나 설정 migration 없음. 게시 후 문제는 공개 결과를 보고하고 수정 버전 또는 철회에 대한 별도 판단을 받으며 임의 삭제/태그 이동은 하지 않는다.

## Decision Log

- 사용자 명시 지시에 따라 기존 공개 GitHub에 수동 배포한다. 버전과 일치하는 v0.2.0을 이번 tag로 선택한다. no-change는 게시 요청을 충족하지 못하고 새 workflow/PyPI는 설정·권한과 지속 관리가 필요하므로 이번에는 제외한다. enforcement는 exact SHA/hash와 fresh install/read-back이며 다음 릴리즈에서 자동화 필요성이 생길 때 재검토한다.

## Surprises and Discoveries

기존 release/tag/publish workflow는 없었다. 과거의 GitHub 읽기 전용 제한은 현재 인증 경로에는 해당하지 않으며 PR 생성·merge로 실제 쓰기를 확인했다.

## Concrete Steps

1. exact merge archive에서 offline wheel을 빌드한다.
2. 별도 Sonnet이 고정된 실제 wheel을 fresh venv와 generated fixture로 검증한다.
3. Main이 새 v0.2.0 tag/release/assets를 게시하고 다시 다운로드해 hash를 확인한다.
4. 결과를 기록하고 적용 가능한 계획 검증·종료를 수행한다.

## Validation and Evidence

Main CI: https://github.com/gkrtjd99/Reporivet/actions/runs/34146538306. artifact/독립/원격 결과는 Task Result에 기록한다. 별도 source 코드 변경이 없으므로 기존 제품 근거와 새 실제 asset 검증을 구분한다.

## Outcomes and Retrospective

사용자가 승인한 GitHub 0.2.0 수동 릴리즈를 게시했고 actual wheel의 독립 검증 및 공개 asset 다운로드 일치를 확인했다. 새 코드·workflow·dependency 없이 기존 merge 후보를 배포했다. Main이 AC-1/2/3 근거를 수락한다. PyPI 인증/게시 및 서비스 배포는 수행하지 않았다. 계획 기록은 release tag의 source를 변경하지 않는다.

## Follow-ups

PyPI가 필요하면 maintainer 인증과 프로젝트 소유권 확인이 필요하다. 인증값을 로그나 저장소에 기록하지 않는다.
