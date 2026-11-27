---
id: PLAN-2026-0018
kind: exec-plan
status: completed
owner: main
area: navigation-and-evaluation
created: 2026-11-27
updated: 2026-11-27
base_commit: "718021503e161931f0b9bda3155c9da8aed1c314"
---

# 제한된 관찰에서 문서 누락 완화와 탐색 평가

## Current Contract

- 근거: 사용자 요청, `docs/PRODUCT.md`, `SPEC-REPORIVET-003`, `docs/SECURITY.md`, `docs/QUALITY.md`, `docs/references/agent-navigation-evaluation.md`. 기존 미커밋 사용자 변경은 보존한다.
- 범위: 한정된 관찰 목록의 파일 분포를 개선하고 동일한 원본에 이전/개선된 목록을 적용해 fresh-agent 탐색을 비교한다. 실제 경로만 표시하며 이름이나 위치로 권위·현재 요구·명령을 추론하지 않는다. 대상 문서·코드·검사는 실제 근거에 맞게만 수정한다.
- 수락 기준: 일반 파일이 파일 출력 한도를 채워 방문한 문서를 모두 밀어내는 사례가 완화된다. 관찰 깊이·항목·방문 작업 상한과 제외 보고, read-only audit, 실제 경로 및 marker·안전성 계약을 유지한다. 기존 회귀·배포 검사 및 exact candidate의 독립 검토를 수행한다. 동일 fixture, 조건별 새 세션, 실제 도구 trace·검사/진단을 기록하고 효과가 없거나 미입증이어도 보고한다.
- 보호: 기존 target 범위·사용자 파일·권한 수정·과거 결과를 덮어쓰지 않는다. 평가 fixture는 고유 임시 경로만 사용하고 agent는 fixture 밖 읽기, 쓰기, 설치, 네트워크, 재위임을 하지 않는다. 원시 transcript·실행 engine은 제품에 포함하지 않는다.
- 계획 기준점: 현재 미커밋 권한 수정 포함 기준 initializer SHA-256 `33905f61d5f07cccbf17b8dec38b24777185b9d16c04c1b304a4c1250e48baf8`를 별도 임시 경로에 동결한다. 실험의 stdin은 `DEVNULL`; 시작 prompt 전체를 trace로 독립 증명하지 못하면 한계를 적는다.

## Progress

- [x] 기존 기준 코드 동결과 품질·평가 계약 확인.
- [x] 관찰 목록 개선과 기계적 회귀 검증.
- [x] 독립 새 세션으로 미적용/이전/개선 목록 탐색 비교 및 결과 기록.
- [x] 독립 검토와 최종 소스 검사.

## Validation and Evidence

- **PASS — 경로 선택:** 루트 일반 파일 90개로 기존 80개 목록에서 빠진 `docs/README.md`가 수정 후 두 fixture의 audit/진입점에 표시된다. 방문한 파일 중 문서 유사·기타를 우선 각 40개까지 선택하고 빈 자리를 재분배한다. 512 방문·80 출력과 깊이·제외 및 비권위 경계는 유지된다.
- **PASS — 검증 및 실제 탐색 관찰:** 합성 fixture 2개 × 미적용/이전/개선 각 fresh 세션에서 현재 요구·구현·과거·실제 검사 결과를 확인했다. 여섯 세션 모두 성공했으므로 진단 향상은 관찰되지 않았다. 정확한 입력·trace·첫 명령 거부·결과와 제한은 [평가 기록](../../references/agent-navigation-evaluation.md)에 보존했다. 독립 검토가 제품 변경·두 source 사본·생성물·fixture 보존·6 trace 및 평가 문서를 대조했다.
- **UNPROVEN:** 이 한 모델·단일 시행·합성 사례를 넘어선 실제 업무의 진단·비용 향상. 문서 범주 포화, 방문 512개 및 깊이 한도에서 중요 문서의 포함을 보장하지 않으며 다른 범주의 중요한 경로도 빠질 수 있다. Birch 개선 목록에서 검사 경로가 빠진 사례를 평가 기록에 명시했다.
- **검사:** macOS/Python 3.13.18 격리 venv의 `PYTHON=<venv>/bin/python PYTHONDONTWRITEBYTECODE=1 ./dev/check` exit 0, 67 tests / 10.343s / OK. 평가 문서에 Birch 검사 경로 누락 한계 문장만 검사 후 추가했으며 독립 재대조·`git diff --check`를 수행했다. 별도 초기 검토에서 30개 대상 테스트도 통과했다.
- **Candidate:** base `718021503e161931f0b9bda3155c9da8aed1c314`와 [PLAN-0017](../completed/PLAN-2026-0017-current-template-navigation-evaluation.md)의 기존 미커밋 후보. 그 계획 파일 SHA-256 `ae99037f5382b1a46158b5dda57b8bbd16a5e5468ba8691d3130b29bbde2dd4b`. 이 계획은 자체 증거이므로 다음 목록에서 제외한다. 다음 각 파일 mode는 `0644`이며 이전 후보에서 이번 작업으로 바뀐 파일이다.
  - `src/reporivet/initializer.py`: `56d149234988d0480486d3791555a5f273da7c2d81fc342d3ae6ea31c46d3dae`
  - `tests/test_audit_adoption.py`: `6c9ee53498682830ff6fe081d116dbedbea876814ab0ac7adbfe1104cb293900`
  - `README.md`: `6aa2ca867ff9e3d8b26c750626f6cfe080d68ccaa3de3cebbb184401f35723be`
  - `README.en.md`: `f3c1ba15f305bd9dcdbabdf694d4e95989f150a3be8e9e4a1fb69df06a701015`
  - `ARCHITECTURE.md`: `27d431205cf1d52f12cbb9cf4c102ded23be7b6b71391cc86f2ea4c8fcc04b43`
  - `docs/references/agent-navigation-evaluation.md`: `d294ed74820cf72794d5f6e74fc50877e3c30bbebabd273dc7916b769fa1c926`
- 기존 미커밋 파일과 기존 계획 이동의 삭제 목록은 PLAN-0017 및 그가 참조하는 PLAN-0016/0015를 따른다. 이번 작업에 삭제된 경로는 없다. 진입점 템플릿 SHA-256은 전후 동일 `d9b160c59feef1d8b687c49d99bcf4bd017ade32aeea6de61e4e5b9c14302aa5`다.
