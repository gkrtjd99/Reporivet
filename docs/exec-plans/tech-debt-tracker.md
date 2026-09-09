# Technical Debt and Follow-up Tracker

This is the canonical in-repository backlog for unresolved work that must survive completion of an ExecPlan when no external issue tracker is declared.

Do not copy every idea here. Add an item only when it has evidence, impact, an owner or owning area, and a trigger for reconsideration.

## Open

### TD-0001 — 장기 문맥 보호·비용 효과의 실행 근거

- Source: [PLAN-2026-0012](completed/PLAN-2026-0012-main-context-owner-judgment.md), T5.
- Area / Priority / Owner: source-operating-contract / medium / Main.
- Evidence: paired fixture는 준비됐지만 timeout 자식 정리의 결정적 시험이 2회 실패해 실제 비교를 중단했다. 단일 `/compact` 요청도 120초 안에 boundary/result 없이 종료됐으며 진단·준비·수선·실행의 시간 예산 초과가 관찰됐다. no-op과 compact 직전 부분 계측은 총비용 또는 절감률의 근거가 아니다.
- Impact: 현재 소스 계약의 완료 수락과 별개로 장기 Main 문맥 보호·실제 compact 후 복원·총토큰/청구 비용 감소·예산 강제의 효과를 주장할 수 없다.
- Trigger: 해당 효과를 제품/운영 근거로 주장하려 하거나, 중단된 시험에 대한 원인 진단과 새 실행 예산이 명시적으로 승인될 때 재검토한다. 현재 실패·재시도 예산을 agent/model 변경으로 초기화하지 않는다.
- Exit criteria: 안전한 종료 경계 검증 후 동일 조건의 실제 전후 실행 및 실제 compact 이벤트를 확보한다. Main 반환량·전체 사용량·청구 비용을 분리하고 준비/검토 오버헤드와 실패도 보존한다. 시간 예산 준수는 host 제한과 prompt 정책을 구분해 검증한다. 절감이 관찰되지 않으면 그 부정적 결과로 종결할 수 있으며, 새 runtime·자동 계측 시스템은 별도 승인 없이 추가하지 않는다.

## Resolved

- None.
