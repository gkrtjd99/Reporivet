# Technical Debt and Follow-up Tracker

This is the canonical in-repository backlog for unresolved work that must survive completion of an ExecPlan when no external issue tracker is declared.

Do not copy every idea here. Add an item only when it has evidence, impact, an owner or owning area, and a trigger for reconsideration.

## Open

### TD-0001 — 장기 문맥 보호·비용 효과의 실행 근거

- Source: [PLAN-2026-0012](completed/PLAN-2026-0012-main-context-owner-judgment.md), T5; [PLAN-2026-0013](active/PLAN-2026-0013-long-context-cost-evaluation.md), E2 제한 재평가.
- Area / Priority / Owner: source-operating-contract / medium / Main.
- Evidence: PLAN-0012의 paired 준비는 timeout 자식 정리 시험2회 실패로 중단됐다. 이전 `/compact` 실행은 앞선 진단을 포함한 전체 약121초 후 boundary 없이 끝났으며 compact 전용120초 대기였다는 근거는 없다. PLAN-0013의 E1/E2에서는 READY 기반 종료 분기와 부분행 timeout 검사, 정책 Git blob/mode 대조를 수행했지만, 최종 비교 driver가 child result를 Owner turn 종료로 오인할 수 있어 실제 전후 비교는 미실행이다. 별도 Read-only CLI 세션1회는 첫 준비 turn30초 제한으로 중단됐고 총35.263초/exit0/group_gone=true였다. 이 세션에는 `/compact`가 전송되지 않았고 result/usage도 확보되지 않았다. 원래45분 및 여러 준비·수선 예산 초과를 보존한다. CLI 부분 메시지·no-op·과거 부분 계측은 총비용 또는 절감률의 근거가 아니다.
- E3 evidence: 동일 Read-only 단일 진단 한 쌍은 실제 완료했고 둘 다 숫자정렬 결함과 모순된 PASS를 정확히 거부했다. before/after 반환994/1027bytes, CLI표시$0.077500/$0.081894로 관측됐으나 costBasis=unknown, 정책 명시Read 미관측, 단일쌍·cache/순서 한계 때문에 인과효과/실제청구로 해석하지 않는다. 별도 after 반복 세션은 정책 실제Read, C2 변경과 거짓PASS 거부의3개 정상판정을 기록했고 usage turn별합계와 마지막modelUsage가 일치했다. 그후compacting4개가 있었지만 종료확인의EPERM이drain/summary/최종manifest보존을 막아boundary/복원/최종총비용은미확인이다. before반복은재실행하지않았다. 신호권한을우회하지않았으며관측CLI부재를그룹소멸증명으로대체하지않는다. 단일과반복과제를동일표본으로합산하지않는다.
- Review: PLAN-0013의 E1/E2 동결 후보는 별도 문맥에서60tests/6.550s/OK 및 보호 파일 보존을 확인했지만 효과 기준은 UNPROVEN이다. 최종 기록 반영 뒤 독립 재대조는 시간 소진으로 수행하지 않았다. Verifier가 새 고유 경로 대신 읽기 전용 기존 검증 tmp에 증거4파일을 생성한 경계 위반도 남겼다. 최초45분뿐 아니라 E2전체60분과 최종 검토 예산도 초과했다.
- Impact: 현재 소스 계약의 완료 수락과 별개로 장기 Main 문맥 보호·실제 compact 후 복원·총토큰/청구 비용 감소·예산 강제의 효과를 주장할 수 없다.
- Trigger: 해당 효과를 제품/운영 근거로 주장하려 하거나, 중단된 시험에 대한 원인 진단과 새 실행 예산이 명시적으로 승인될 때 재검토한다. 현재 실패·재시도 예산을 agent/model 변경으로 초기화하지 않는다.
- Exit criteria: 안전한 종료 경계 검증 후 동일 조건의 실제 전후 실행 및 실제 compact 이벤트를 확보한다. Main 반환량·전체 사용량·청구 비용을 분리하고 준비/검토 오버헤드와 실패도 보존한다. 시간 예산 준수는 host 제한과 prompt 정책을 구분해 검증한다. 절감이 관찰되지 않으면 그 부정적 결과로 종결할 수 있으며, 새 runtime·자동 계측 시스템은 별도 승인 없이 추가하지 않는다.

## Resolved

- None.
