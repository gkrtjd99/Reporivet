---
id: PLAN-2026-0015
kind: exec-plan
status: active
owner: main
area: documentation
created: 2026-09-27
updated: 2026-09-27
base_commit: "718021503e161931f0b9bda3155c9da8aed1c314"
---

# 선택적 문서 기반 작업·모델 라우팅·Jev 안내

## Purpose / Big Picture

기존 플러그인을 이식하지 않고, 사용자가 native Claude Code/ultracode를 유지하면서
모델·effort와 Jev 판단 기준을 필요한 문서에서만 찾아 적용할 수 있게 한다.
문서 추가와 실제 API 연동·성능 검증을 구분한다.

## Current Contract

- 원본: 위 base의 `AGENTS.md`, `CLAUDE.md`, `docs/PLANS.md`, `docs/QUALITY.md`, `docs/SECURITY.md`, `SPEC-REPORIVET-003`, `ADR-0002`.
- 사용자 요청: 기존 플러그인 이식 없이 중요한 Jev·model routing 내용을 Reporivet에 반영하고 PR을 준비한다.
- 범위: `docs/README.md`, `docs/references/README.md`, 새 선택적 가이드 세 개와 이 소스 계획.
- 보호: `src/`, target template, 의존성, `.claude` 설정, CI, 기존 완료 계획·ADR 본문, 작업 상태.
- 금지: 새 runtime/SDK/router/hook/plugin/DB 설치, 실제 모델 호출·청구, 비밀정보 포함, 미검증 성능 주장, main 직접 쓰기·병합.
- 승인 범위는 문서 수정과 PR 생성까지다. merge·release·배포는 포함하지 않는다.

## Progress

- [x] 현재 제품 경계와 원본 파일 revision 확인.
- [x] 공식 TypeSafe/Claude 자료와 대화의 설계 가설을 구분.
- [x] 선택적 가이드와 두 문서 지도 연결을 작성.
- [x] 원본 blob 일치·문서 링크·patch 적용·변경 경계의 제한된 로컬 점검.
- [ ] 전체 checkout에서 `PYTHON=python3 ./dev/check` 실행.
- [ ] 브랜치/PR 생성, 독립 검토와 사용자 수락.

## Context and Orientation

현재 `0.3.0.dev1`은 작은 Markdown 진입점만 만든다. `docs/README.md`는 기존 소스 진입점에서 연결되는 지도다.
새 가이드는 reference이며 생성 대상에 복사되지 않는다. 기존 문서의 이름·작업 체계·권한을 바꾸지 않는다.

## Scope and Non-goals

문서 기반 작업, 필수 계약/선택 자료, 인계·검증·재개, 모델 요청/매핑/관측, 최소 effort의 평가,
Jev 질문·confidence·실패·관찰 평가를 문서화한다.
실행 자동화, SDK 예제의 실호출, 고정 모델 가격표, 보편적 effort 등급, 기존 플러그인 코드는 포함하지 않는다.

## Acceptance Criteria

- **AC-1:** 필요한 경우에만 새 가이드로 이동하며 제품의 entrypoint-only 경계가 유지된다.
- **AC-2:** 라우팅 문서는 요청 모델·effort와 실제 gateway 적용을 구분하고 미확인 값과 가설을 표시한다.
- **AC-3:** Jev 문서는 Noul/Choice/Score·confidence의 의미, 필수 계약·권한의 독립성, 실패·검토·평가 기준을 구분한다.
- **AC-4:** 문서 연결과 patch가 기계적으로 유효하고 canonical 소스 검사가 통과한다.
- **AC-5:** 변경 브랜치의 실제 후보가 PR에서 검토 가능하고 미실행 검증을 성공으로 표시하지 않는다.

## Approach and Key Changes

기존 자동 로딩 문서와 target template는 늘리지 않는다.
`docs/README.md`와 reference 인덱스에 선택적 안내만 추가한다.
외부 제품 기능은 공식 출처와 확인일을 기록하고 운영 정책은 제안으로 표시한다.

## Milestones

M1은 가이드·진입 링크와 기계적 문서 점검이다.
M2는 canonical 검사와 PR 검토이며, 네트워크나 쓰기 권한이 없으면 미완료로 남긴다.

## Architecture Impact

없음. 런타임·의존성·CLI·생성 결과·상태 모델을 변경하지 않는다.

## Documentation Impact

| 문서 | 작업 | 이유 |
|---|---|---|
| `docs/README.md`, `docs/references/README.md` | update | 선택적 탐색 경로 |
| `document-driven-native-work.md` | create | 얇은 문서 기반 작업·인계·검증 |
| `model-effort-routing.md` | create | 기존 host/gateway의 프로필·평가 경계 |
| `jev-decision-guidance.md` | create | 좁은 판단의 의미·한계·실패 처리 |
| 제품 명세·ADR·target template | none | 제품 책임과 생성 동작 유지 |

## Migration, Rollout, and Recovery

설치나 migration이 필요 없다. 채택할 프로젝트는 기존 문서의 소유권 아래 필요한 부분만 검토한다.
rollback은 이 문서 diff를 되돌리는 것으로 충분하며 실제 API 설정·작업 상태를 건드리지 않는다.

## Surprises and Discoveries

- 2026-09-27: connector 조회는 가능하지만 브랜치 생성은 `403 Resource not accessible by integration`으로 거부됐다. 다른 계정이나 main 직접 쓰기로 우회하지 않았다.
- 로컬 환경의 GitHub DNS 접근이 실패해 전체 checkout과 canonical 소스 검사를 수행하지 못했다.

## Decision Log

- 제품 확장 대신 선택적 reference로 작성한다. 실제 Jev·gateway 연결은 기존 프로젝트의 별도 승인·검증 책임으로 남긴다.
- 문서 품질 점검을 모델 성능이나 실환경 라우팅 검증으로 대체하지 않는다.

## Concrete Steps

1. 현재 main과 문서 원본 blob을 재확인한다.
2. 변경 bundle의 diff와 SHA-256을 검토하고 깨끗한 checkout에 `git apply --check` 후 적용한다.
3. `PYTHON=python3 ./dev/check`와 `git diff --check`를 실행한다.
4. 쓰기 권한이 확인된 연결에서 별도 브랜치와 PR을 만들고 실제 후보 SHA·검증 결과를 기록한다.

## Validation and Evidence

제한된 로컬 점검은 원격 base 문서와 일치하는 두 파일을 사용하는 fixture에서 수행했다.
전체 repository clone이나 canonical test 실행이 아니다. 적용 patch와 SHA-256 목록은 전달 bundle에 포함한다.

| 기준 | 결과 | 근거 |
|---|---|---|
| AC-1 | PASS | 변경 대상이 문서 6개뿐이며 source/target 자산은 변경하지 않음 |
| AC-2 | PASS | 요청/매핑/관측, `unknown`, Luna 가설, 평가·fallback 명시; 작성자 문서 검토 |
| AC-3 | PASS | 공식 출력 의미·제한과 운영 제안을 구분; 작성자 문서 검토 |
| AC-4 | UNPROVEN | 제한된 문서·patch 검사는 통과, `./dev/check`는 미실행 |
| AC-5 | UNPROVEN | 원격 브랜치·commit·PR 미생성, 독립 검토 미수행 |

위 PASS는 문서 수락 기준의 작성자 점검이지 독립 검토나 모델 동작 증거가 아니다.
최종 verified candidate는 실제 PR head가 생성되고 검증된 뒤 기록한다.

## Outcomes and Follow-ups

문서 변경은 준비했으나 PR과 canonical 검사가 남아 있으므로 계획을 완료로 이동하지 않는다.
연결의 저장소 쓰기 권한 확인 후 main의 변경 여부를 다시 검토하고, 기존 검사 기준을 유지한 채 PR을 제출한다.
