---
id: PLAN-2026-0016
kind: exec-plan
status: completed
owner: main
area: source-operations
created: 2026-11-26
updated: 2026-11-26
base_commit: "718021503e161931f0b9bda3155c9da8aed1c314"
---

# 소스 운영 경량화와 중단된 계획 정리

## Current Contract

- 근거: 사용자 요청과 이 작업 시작 시 `AGENTS.md`, `docs/PLANS.md`, `docs/QUALITY.md`, `docs/SECURITY.md`, `docs/README.md`; 기존 수정사항은 작업 트리에 보존한다.
- 목적·범위: 위험 기반 안전검사·독립 검토를 유지하면서 계획과 기록 부담을 줄이고, 중단된 PLAN-0011/0013을 실제 결과와 일치하게 분리한다. 제품 동작, 파일 안전 테스트와 CI는 변경하지 않는다.
- 수락 기준: 짧은 위험 변경 기록에도 scope/보호 경계, 수락 기준, 정확한 후보, 실제 검사 결과와 독립 검토 및 미검증을 보존한다. 두 계획의 FAIL/UNPROVEN·TD-0001 open·기존 증거 및 재개 조건을 유지한다. 현재 문서 링크와 계약 테스트가 유효하다.
- 보호 경로: 기존 사용자 변경 및 이전 권한 수정, 제품 코드·배포 자산·CI·과거 completed 문서. 필요한 현재 운영 문서, 계약 검사와 대상 계획·현재 링크만 수정한다.
- 절차: 관련 계약의 충돌을 확인하고 독립 검토를 수행하며 실행하지 않은 검사는 명시한다. 검증 후 결과와 추후 과제를 이 계획에 기록한다.

## Progress

- [x] 기존 정책과 대상 계획의 실패 및 보류 상태 확인.
- [x] 운영 정책·양식 경량화 및 계획 상태 정리.
- [x] 독립 검토, 검사와 결과 기록.

## Approach and Documentation Impact

작은 단일 범위 변경에 간결한 계획을 허용하고 복잡한 작업의 상세 계획은 유지한다. 과거 계획은 성공으로 표시하지 않고 중단 상태·이유·재개 조건을 표시한다. 운영 정책, 문서 지도와 해당 테스트의 문구·링크를 일치시킨다.

## Validation and Evidence

- **PASS:** 좁은 범위 변경의 짧은 기록과 중복 증거 제거를 허용하며, 파일 안전 검사와 위험 변경의 독립 검토·기준별 판단을 유지했다. 별도 문맥 검토가 최종 정책 및 대상 계획의 이력과 링크를 대조했다.
- **PASS:** PLAN-0011/0013은 성공으로 표시하지 않고 `paused/`로 이동했다. FAIL/UNPROVEN과 TD-0001의 open 상태 및 과거 이력은 유지했다.
- **PASS:** macOS, Python 3.13.18, setuptools 84.2.1 격리 venv에서 `PYTHON=<venv>/bin/python PYTHONDONTWRITEBYTECODE=1 ./dev/check` exit 0, 64 tests/5.367s/OK. 마지막 paused 조건 문구 조정 후 독립 계약 테스트 6/6 재통과. `agent-contract-sync --check` 및 `git diff --check` 통과; 로컬 Markdown 상대 링크 오류 없음.
- **Candidate:** base `718021503e161931f0b9bda3155c9da8aed1c314`. 아래 SHA-256 대상은 전부 mode `0644`; 이 계획은 검증 기록 자체이므로 목록에서 제외한다. 기존 권한 변경 일곱 파일의 해시는 [PLAN-0015](PLAN-2026-0015-new-file-permissions.md)에 기록된 값과 일치한다.
  - `docs/PLANS.md`: `cefb6060dfb38cc6241bfa3b1f9ff35d84589666764514de5fc4f2aef9cf163a`
  - `docs/README.md`: `08e72f05d2e5d2eac9333bcdf92a9fdac04d7423dc8c1ae0230193d87e698637`
  - `docs/exec-plans/_template.md`: `6322a2a41ac4af38e13d7fe9d2124964fad19bc6e14fc498d82d1c3696c97b45`
  - `docs/exec-plans/tech-debt-tracker.md`: `f8fe50616b056a30ef7259f1469f42aa58f9c6a55ce9ce2b0f16651fd9253cf1`
  - `tests/test_agent_operating_contract.py`: `5743bc46fafac84a65fb64f6b5c7767d1fe325ca4114e129b67079f7d0c36173`
  - `docs/exec-plans/paused/PLAN-2026-0011-task-owner-delegation-probe.md`: `c4ff2bf7b1a828e140afa95ca85740a177f8391f4767fa086a298a96c39f7390`
  - `docs/exec-plans/paused/PLAN-2026-0013-long-context-cost-evaluation.md`: `f045ed1a538ed0b76ac7b93a7e14cf661db4883ec5dc4f06ed6f147a36ed0234`
  - 기존 미커밋 `docs/exec-plans/completed/PLAN-2026-0015-new-file-permissions.md`: `8048eb717733df7baa48bd3c56b2af81b33e0674fccdff52f3ad39adb3986929`
- 삭제된 경로는 `active/PLAN-2026-0011-task-owner-delegation-probe.md`, `active/PLAN-2026-0013-long-context-cost-evaluation.md` 두 이동 전 경로뿐이다. 계획 본문은 paused 경로에 보존했다.

## Migration, Recovery, and Follow-ups

이전 기록과 기술 부채는 보존하며 계획 이동은 Git에서 되돌릴 수 있다. 제품이나 대상 프로젝트에 migration은 없다. TD-0001은 open 상태로 유지하며 본 작업에서 실험을 재개하지 않았다.
