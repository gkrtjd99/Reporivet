---
id: PLAN-2026-0017
kind: exec-plan
status: completed
owner: main
area: product-evaluation
created: 2026-11-27
updated: 2026-11-27
base_commit: "718021503e161931f0b9bda3155c9da8aed1c314"
---

# 현재 진입점 템플릿의 적용 전후 탐색 평가

## Current Contract

- 근거: 사용자의 실제 전후 비교 요청, `docs/PRODUCT.md`, `docs/QUALITY.md`, `docs/references/agent-navigation-evaluation.md`, `SPEC-REPORIVET-003`. 기존 미커밋 변경과 역사 기록은 보호한다.
- 범위: 동일한 Atlas/Birch fixture의 before/after 각 독립 fresh agent 진단. after에만 현재 작업 트리의 CLI와 템플릿을 적용한다. 모델·작업·권한·검사 조건을 맞추고 원본과 생성 파일의 hash를 기록한다.
- 수락 기준: 각 조건의 현재/과거 근거·구현·실제 검사 명령과 exit/output, 읽은 경로 및 차이를 관찰한다. 원본 bytes 보존과 독립 재실행을 확인하고 도구 trace·자기 보고를 구분한다. 결과가 같거나 악화되어도 보존하고 이전 템플릿 관측과 섞지 않는다. 동일 fixture 각각 단일 실행은 일반적 효과의 증거가 아니다.
- 보호: fixture 생성은 새 고유 임시 경로에서만. agent에게 수정·설치·네트워크·재위임·다른 fixture와 상위 경로 읽기 금지. 문서에 명시된 해당 fixture 검사만 허용하며 prompt 제한과 OS sandbox를 혼동하지 않는다. 제품 코드·타 작업 파일·원시 transcript를 저장소에 추가하지 않는다.
- 평가 기록은 현재 `docs/references/agent-navigation-evaluation.md`에 과거 관찰과 구분해 추가한다. 실패·미실행·기록 누락은 그대로 보고한다. 별도 문맥에서 결과와 한계를 독립 검토한다.

## Progress

- [x] 현재 제품 요구·역사 평가 및 fixture의 원본/기대 결과 확인.
- [x] fixture 생성·현재 템플릿 고정·fresh 세션 실행. 최초 오염된 4회는 제외하고 새로운 조건에서 4회 재실행.
- [x] trace, 결과, 검사 독립 재확인 및 독립 검토.

## Validation and Evidence

- **PASS:** 현재 template로 생성한 두 fixture의 적용 전후에서 현재/과거/구현 진단 및 실제 검사 결과를 각각 관측했다. 원본 bytes·생성물·trace와 결과를 독립 대조했다. 두 before도 성공했으므로 추가 효과는 관찰되지 않았다. 평가의 한계와 제외된 최초 실행은 [평가 기록](../../references/agent-navigation-evaluation.md)에 있다.
- **UNPROVEN:** 더 큰 실제 저장소와 반복·다중 모델·코드 수정 성공, 시간이나 비용에 대한 일반적 효과. 위 기준은 이 제한적 평가의 완료 기준이 아니라 후속 평가 대상이다.
- 별도 문맥 검토에서 최종 평가 문서 SHA-256 `352f668b1ab9d93005a52750fc449e53423e42c1cb05ee2999ea0dff573a64a7`, 실제 trace·생성물·과거 기록 보존을 확인했다. 최초 오염 원인은 미확정이며 두 번째 실행의 초기 메시지 전체는 trace로 직접 입증되지 않는다.
- macOS / Python 3.13.18 격리 venv에서 `PYTHON=<venv>/bin/python PYTHONDONTWRITEBYTECODE=1 ./dev/check` exit 0, 64 tests / 5.755s / OK. 문서의 마지막 cwd·prompt 표현 2곳은 실행 후 독립 검토에서 더 정확히 정정했다. `git diff --check` exit 0.
- Candidate base `718021503e161931f0b9bda3155c9da8aed1c314`; 앞선 미커밋 파일의 hash/mode·이동 전 삭제 목록은 [PLAN-0016](../completed/PLAN-2026-0016-lighten-source-operations.md)에 기록된 후보와 동일하고, 그 계획 파일 자체 SHA-256은 `3f073e3eb0f9ea4cde4b487500521d173801f83adbdf7584119b043dde9aa020`이다. 이번 평가 문서 mode `0644`, SHA는 위와 같다. 이 계획 자체는 증거 기록이므로 후보 hash에서 제외한다.
