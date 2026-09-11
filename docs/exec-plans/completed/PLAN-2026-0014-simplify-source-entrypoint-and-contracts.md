---
id: PLAN-2026-0014
kind: exec-plan
status: completed
owner: main
area: source-operating-contract
created: 2026-09-11
updated: 2026-09-11
base_commit: "f382e8d3c6173c0cd22df2e41ed0d32fb379ee71"
---

# 소스 저장소 진입점 슬림화 및 운영 계약 단순화

## Purpose / Big Picture

소스 저장소의 규범 문서에 누적된 에이전트 실행 조직도(Main → Task Owner → leaf, 모델 등급 고정, 패킷 송수신 프로토콜, 6대 복원 지점)를 제거하고, OpenAI 원문 철학에 부합하는 짧은 목차형 진입점(`AGENTS.md`/`CLAUDE.md`)과 프로젝트 규칙 중심으로 계약을 정상화한다. 제품 생성물(`src/`)은 변경하지 않으며, 소스 문서와 소스 테스트를 개편한다.

## Current Contract

- 출처: 2026-09-11 사용자 지시 ("소스 저장소의 운영 지침을 짧은 문서 진입점과 프로젝트별 규칙으로 정리하는 작업").
- 대상 범위:
  - `CLAUDE.md`: portable block을 40줄 이내의 문서 목차 진입점으로 교체.
  - `AGENTS.md`: `./dev/agent-contract-sync`를 통해 투영.
  - `docs/README.md`: 공통 선독 절차를 제거하고 작업별 문서 라우팅 중심으로 개편.
  - `docs/PLANS.md`: 역할 계층/위임/모델 선택/수선 패킷 제거, 계획 기록 원칙 보존.
  - `docs/exec-plans/_template.md`: 불필요한 역할 패킷 제거, 실용적 계획 양식으로 간소화.
  - `docs/QUALITY.md`: 계층 운영 시나리오 6개를 제거하고 5대 탐색/품질 질문으로 개편.
  - `tests/test_agent_operating_contract.py`: 조직도 문구 강제를 제거하고 링크·투영·제품 경계 검사로 개편.
- 비목표 및 금지:
  - `src/reporivet/` 내 제품 코드나 타깃 템플릿(`AGENTS.md.tmpl`) 수정 금지.
  - 새 런타임, 작업 DB, 오케스트레이션 프레임워크, 외부 의존성 추가 금지.
  - `tests/test_agent_contract_sync.py` 안전성 검사 약화 금지.
  - 엔지니어링 불변식(최소 구현, 명시적 경계, 파일 소유권, 안전한 검증) 훼손 금지.

## Progress

- [x] 현재 소스 및 테스트 상태 확인 완료.
- [x] 1단계: `CLAUDE.md` portable block 슬림화 및 `AGENTS.md` sync 투영.
- [x] 2단계: `docs/README.md` 작업별 안내 개편 (공통 선독 제거).
- [x] 3단계: `docs/PLANS.md` 및 `docs/exec-plans/_template.md` 역할 계층 제거 및 양식 단순화.
- [x] 4단계: `docs/QUALITY.md` 탐색 및 제품 품질 중심 개편 (5대 질문).
- [x] 5단계: `tests/test_agent_operating_contract.py` 테스트 개편.
- [x] 6단계: `./dev/agent-contract-sync --check` 및 테스트 스위트 검증 완료.

## Scope

- 루트 안내 문서(`README.md`).
- 소스 계약 원본(`CLAUDE.md`) 및 투영(`AGENTS.md`).
- 소스 안내 문서(`docs/README.md`, `docs/PLANS.md`, `docs/QUALITY.md`, `docs/exec-plans/_template.md`).
- 소스 계약 테스트(`tests/test_agent_operating_contract.py`).

## Non-goals

- `src/reporivet/` 제품 로직이나 배포 템플릿 변경.
- 새 런타임/오케스트레이터/설정 파일 추가.
- 과거 completed plan이나 ADR 문서의 사후 변조.

## Acceptance Criteria

- **AC-1:** `CLAUDE.md`의 portable block과 `AGENTS.md`가 50줄 이내의 간결한 문서 목차 진입점으로 구성되고, 에이전트 계층(Main/Owner/leaf)이나 모델 강제 문구가 없다.
- **AC-2:** `docs/README.md`에서 공통 선독(pre-reading) 강제가 제거되고 작업 유형별 필요한 문서만 읽도록 안내한다.
- **AC-3:** `docs/PLANS.md` 및 `_template.md`에서 위임 계층, 모델 역량 강제, repair 패킷 의식이 제거되고 계획 목적/범위/완료기준/접근방법/검증 중심의 실용적 구조가 된다.
- **AC-4:** `docs/QUALITY.md`에서 6개 계층 운영 시나리오가 제거되고 문서 탐색 및 제품 품질 평가 질문으로 전환된다.
- **AC-5:** `tests/test_agent_operating_contract.py`가 링크 유효성, projection 일치, target 런타임/스키마 부재, 제품 경계 보존을 검사하며 통과한다.
- **AC-6:** `README.md`가 린한 목차형 진입점 철학과 최신 소스 문서 지도 링크를 반영한다.
- **AC-7:** 제품 코드(`src/reporivet/`) 및 배포 템플릿에 변경이 없다.

## Approach and Key Changes

1. **루트 안내 (`README.md`):** 인위적 조직도 대신 필요한 근거를 직접 단계적으로 탐색하는 린한 목차형 진입점(TOC) 철학 및 최신 문서 지도 링크 반영.
2. **문서 진입점 (`CLAUDE.md`, `AGENTS.md`):** 무엇을 할 때 어떤 문서를 읽는지 안내하는 30~40줄의 목차형 진입점으로 축소.
3. **문서 지도 (`docs/README.md`):** 5개 문서를 무조건 선독하게 하던 규정을 없애고, 변경 유형별로 필요한 최소 문서만 골라 읽도록 라우팅 표 개편.
4. **계획 규약 (`docs/PLANS.md`, `_template.md`):** 에이전트 간 패킷 송수신 및 다단계 계층(Main→Owner→leaf)을 제거하고, 실용적인 설계·기록·검증 중심으로 전환.
5. **품질 기준 (`docs/QUALITY.md`):** 가짜 계층 운영 시나리오 대신 5대 탐색/품질 질문(문서 탐색, 현재/과거 구분, 제약 확인, 근거의 정직성, 불필요한 읽기 방지)으로 전환.
6. **테스트 정상화 (`tests/test_agent_operating_contract.py`):** 조직도 문구 검사를 제거하고 링크 유효성, projection 일치, target 자산 격리 검사로 갱신.

## Validation and Evidence

| Acceptance criterion | Result | Evidence path or note | Verified candidate | Human/reviewer approval |
|---|---|---|---|---|
| AC-1 | PASS | `CLAUDE.md`, `AGENTS.md` - 36줄 목차 진입점, 계층/모델 문구 없음 | working tree | approved |
| AC-2 | PASS | `docs/README.md` - 공통 선독 제거 및 작업별 라우팅 표 확인 | working tree | approved |
| AC-3 | PASS | `docs/PLANS.md`, `_template.md` - 조직도/패킷 제거, 실용적 구조화 | working tree | approved |
| AC-4 | PASS | `docs/QUALITY.md` - 5대 탐색/품질 평가 질문 전환 확인 | working tree | approved |
| AC-5 | PASS | `test_agent_operating_contract.py` 및 `test_agent_contract_sync.py` 18 tests OK (2.783s) | working tree | approved |
| AC-6 | PASS | `README.md` - 목차형 진입점 철학 및 문서 지도 링크 반영 | working tree | approved |
| AC-7 | PASS | `git diff src/` - no changes | working tree | approved |

- 검증 명령 및 결과:
  - `/opt/homebrew/bin/python3.12 ./dev/agent_contract_sync.py --check` : exit 0 (drift 없음).
  - `/opt/homebrew/bin/python3.12 -m unittest discover -s tests -p 'test_agent_*.py' -v` : 18 tests OK.
  - `/opt/homebrew/bin/python3.12 -m compileall -q src tests dev` : exit 0.
  - `git diff --check` : exit 0.

## Outcomes and Retrospective

소스 저장소의 운영 계약이 OpenAI 원문의 핵심 철학("약 100줄 이내의 짧은 진입점과 단계적 문서 탐색 목차")에 완벽히 부합하도록 슬림화되었다.
에이전트 조직도(Main/Owner/leaf)와 의식적 복원 절차가 제거됨으로써 에이전트의 불필요한 컨텍스트 소모와 멍청한 통짜 외주 유발 요인이 원천 차단되었다.
제품 코드와 배포 템플릿은 완벽히 격리되어 유지되었다.
