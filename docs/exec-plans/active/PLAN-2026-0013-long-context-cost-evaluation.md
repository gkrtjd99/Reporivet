---
id: PLAN-2026-0013
kind: exec-plan
status: active
owner: main
area: source-operating-contract-evaluation
created: 2026-09-09
updated: 2026-09-09
base_commit: "f382e8d3c6173c0cd22df2e41ed0d32fb379ee71"
---

# TD-0001 — 반복 작업의 문맥·사용량 및 실제 compact 평가

## Purpose / Big Picture

이전 평가에서 중단된 안전성 검증과 실제 실행을 다시 수행하고, 운영 계약 변경의 효과를 관찰 가능한 범위에서 판단한다. 절감 성공을 목표값으로 강제하지 않는다. 효과 없음·비용 증가·실행 실패도 유효한 결과이며 실제 Main 전체 문맥이나 청구 비용을 대리지표로 바꾸지 않는다.

## Current Contract

- Revision E3. 2026-09-09 사용자의 “그래서 안하겠다고?”를 실제 검증 재개 요청으로 받아 진행한다. 이전 실패·초과·소진된 접근은 유지하며 E2를 성공으로 바꾸지 않는다. 재개23:07부터30분을 배정하고 반복 수선 대신 동일 조건의 최소 실제 비교를 우선한다. 현재는 읽기 전용 제한 진단만 배정했고, 새 고유 tmp의 구현/실험 packet은 Main이 아래에 확정한다. 새 모델/agent로 기존 retry를 초기화하지 않는다. E1/E2의 목적·금지·AC·보호 경로는 유지한다.
- E2 이력: E1의 목적·금지·AC·권한은 유지한다. Main은 준비 지연과 미완성 수선을 반영해 2026-09-09 22:20에 자체 시간 배정을 한 차례 조정했다. 최초 요청 21:42:31부터 원래45분 경계는22:27:31이며 이를 초기화하지 않는다. 전체60분(22:42:31 종료) 안에서 마지막 수선180초, 비교 한 쌍, compact 한 번, 독립 검토로 축소한다. 추가 사용자 승인을 받았다는 뜻이 아니며 호출 수·가격·경로·수락 기준을 확대하지 않는다. 출처는 2026-09-09 사용자의 “다음 작업은 TD-0001에 남긴 장기 문맥 보호·비용 절감 효과 검증입니다. 해와”와 현행 CLAUDE/PLANS/QUALITY, TD-0001이다. 이는 원인 진단과 새 제한 평가 예산의 승인이지 과거 실패·시간·retry 기록의 삭제나 source/host 변경 승인이 아니다.
- Main은 목적·비목표·AC·권한·전역 비교 조건·통합·최종 수락을 관리한다. 지정 Task Owner는 실제 실행 설계·검증 방법·중요 변경/결정 증거 대조를 직접 책임진다. 상세 구현과 로그 분석은 별도 문맥에 두며 Main은 bounded 근거만 읽는다.
- 사용자 원문 금지 유지: “사용자 변경을 덮어쓰지 마라.” “기존 최대 위임 깊이와 더 제한적인 host 정책을 유지한다.” “가짜 transcript, 임의의 토큰 절감률, 자기 보고만으로 효과를 입증하지 마라.” “실제 위험한 작업이나 외부 부작용을 발생시켜 시험하지 마라.” “실패한 검사를 숨기거나, 통과시키기 위해 수락 기준을 약화하지 마라.”
- “계층을 없애고 Main이 직접 구현하도록 되돌리는 것.” 및 Owner 코딩량/직접 구현 비율 강제 금지. 기존/현재 비교에서 역할·과제·도구까지 바꾸지 않는다. Main→Owner→leaf보다 깊은 평가Main 계층을 추가하지 않는다.
- “사용자 홈의 전역 설정, 외부 서비스, 자격증명, 배포 환경을 임의로 변경하지 마라.” guard 환경변수 삭제·permission 우회·새 의존성/설정/runtime/task DB/packet 저장소/자동 완료 서비스 추가 금지. tmp의 일회성 시험은 제품 runtime으로 배포하지 않는다.
- 같은 실패 접근 두 번이면 중단한다. 과거 sleep 기반 handler 준비 시험의 2회 실패는 소진된 상태다. 새 시험은 readiness handshake로 사전조건을 실제 확인하는 다른 방법이며 sleep 시간을 늘려 재시도하지 않는다. 원인 불명 상태에서는 영향 구현을 보류한다.
- 시작·재개·압축 후·새 지시/환경 관찰·계약 변경·수락 전에 관련 권위 본문을 실제 읽는다. 경로/revision만 전달한 것은 읽기 증거가 아니다. stale 결과는 재대조 전 수락하지 않는다.
- Main만 이 계획과 기존 tracker를 기록한다. 이전 completed PLAN-0012와 기존 probe/driver/fixture는 읽기 전용이다. 구현/실험자는 새 고유 tmp만 쓸 수 있다. 저장소 쓰기와 mutable 준비·실험은 순차 수행한다. 읽기 전용 조사는 병렬 가능하다.
- 전체 추가 작업 예산 45분을 출발점으로 하고 실제 초과는 숨기지 않는다. 지원 조사나 모델/agent 교체로 예산을 초기화하지 않는다. 실제 평가 CLI는 최대 4개 비교 세션과 control/compact 각 1개, 요청마다 확인된 목록가격 상한과 wall-clock 종료를 적용한다. 목록가격 상한은 실제 청구 상한이 아니다. 각 단계의 구체적 상한은 아래 packet에서 더 좁힌다.

## Owner Design Before Delegation

- 관찰: 동일 fixture/정책 snapshot·요청 alias·도구·작업 순서·예산에서 이전/현재 계약의 반복 작업 결과를 비교한다. 성공률·금지 위반·Owner 직접 증거 대조·보고 payload·CLI usage·실패와 시간 기록을 보존한다.
- 불변: Main 최종 수락, 단일 허용 구현 경로, 보호 파일, 고정 검사, 위임 깊이, 실제/추정/미측정 구별을 유지한다.
- 기존 기능: native CLI stream-json, 실제 /compact 요청, 기존 tmp fixture/manifest/검사 방법을 재사용한다. 웹/설치 탐색은 이미 확인된 기능의 재조사에 사용하지 않는다.
- 초기 진단: 시험용 자식의 signal handler 설치를 handshake로 확인하고, 부모 종료·자식 생존·KILL·그룹 소멸의 결정적 분기를 검증한다. 일반 CLI가 READY를 출력해야 한다는 요구는 추가하지 않는다.
- compact: 기존 driver와 이벤트에서 입력 flush/계속 읽기/turn 처리를 먼저 확인한다. 필요한 경우 동일 driver의 평범한 후속 turn과 /compact를 비교하여 driver 정지와 compact 처리 지연을 구별한다. padding이나 timeout 증대만으로 성공을 만들지 않는다.
- 비교 방향: Owner 단독 대 Owner+leaf는 정책 효과 비교가 아니므로 제외한다. 이전 base 732b2e826da6de37a670686218bcf487d39b3e9e와 현재 base의 정책만 바꾸고 나머지는 고정한다. 최대 두 쌍을 반대 순서로 실행해 순서 영향을 드러낸다.
- 측정: root usage에 child가 포함되는지 확인 전 합산하지 않는다. 마지막 누적 result와 turn별 값을 중복 합산하지 않는다. 최종 보고 bytes는 Main 경계의 대리지표이며 실제 Main 전체 context/token이 아니다. CLI 추정 가격과 실제 청구는 분리한다.
- 가정/중단: 안전한 종료·native leaf 지원·stream driver·usage 포함 관계는 초기 UNPROVEN이다. 해당 불확실성만 bounded 진단에 배정한다. 지원/권한/안전성 실패는 원인과 함께 반환한다.

## Progress

- [x] 새 사용자 요청, 현재 base와 기존 보호 파일을 확인했다.
- [x] 이전 실패의 시험 준비 경쟁과 비교 조건 오염 위험을 진단했다.
- [x] 시험용 자식의 READY를 관찰한 종료 분기 시험이 두 번째 시도에서 PASS했다. 첫 시도의 newline framing 실패와 준비 약720초(8분 초과)를 보존한다.
- [x] 공통 최초 frame 연결·bounded 수신·PGID 정리·정책 mode를 수선하고 남은 결함을 분리했다.
- [x] E3 단일 Read-only 진단 한 쌍을 실제 완료하고 독립 대조했다.
- [ ] 반복 비교: E1/E2는 미실행, E3 after의3개진단은완료했으나종료EPERM후before는보류했다.
- [ ] compact 성공/복원: E3빈문맥거절과실제과제문맥의compacting4개는관측했으나boundary/복원은미확인이다.
- [x] 동결 후보 독립 검토와 canonical60tests는 수행했고 TD-0001은 open으로 유지했다.
- [ ] 최종 기록 후보의 독립 재대조 및 전체 수락: 시간 소진과 필수 미충족으로 보류.

## Context and Orientation

소스는 PR #5로 main에 merge됐다. PLAN-0012는 소스 AC를 수락했지만 효과를 수락하지 않았다. TD-0001은 실패한 paired 준비, compact timeout, 예산 초과와 미입증 지표를 추적한다. 현재 branch main/base f382e8d이며 기존 untracked PLAN-0011만 사용자 변경이다. 시작 전 PLAN-0011 hash는 fd965cfdb306265c6a3588f683baf8677811aee626f890e6ebd6e68061d9dc7c, mode0644, inode28009031, ctime_ns1788943209873243842다.

## Scope

새 고유 tmp의 일회성 진단·안전성 시험·정책/fixture snapshot·실제 CLI 평가와 증거, Main의 이 계획/기존 tracker 기록만 허용한다. 원래 source 계약·제품 코드·배포 자산은 변경하지 않는다.

## Non-goals

실제 청구 자료 없는 현금 절감 주장, 소형 반복 시험의 보편적 장기 효과 주장, 대규모 padding, 새 benchmark/runtime/오케스트레이션 제품, 전역 설정/의존성 변경, 기존 실패 기록 삭제, 무조건 고급 모델·agent 수 증가.

## Acceptance Criteria

- **AC-1:** 이전 실패와 새 시험의 차이가 근거로 설명되고, 실제 모델 실행 전에 결정적 종료 분기를 검증한다. 해당 안전성이 FAIL/UNPROVEN이면 영향 실행을 하지 않는다.
- **AC-2:** 동일 과제·도구·alias·허용 경로·예산에서 이전/현재 계약을 실제 별도 문맥으로 비교한다. 반복 수·순서·실패·부분 실행을 숨기지 않는다. 성공 여부는 기준이 아니며 관찰된 부정적 결과도 허용한다.
- **AC-3:** 실제 /compact의 입력/이벤트/종료와 post-boundary 계약 Read를 구분한다. 실패하면 driver/protocol/처리 대기의 확보된 원인과 미확인 영역을 명시한다. 실제 성공은 boundary가 있을 때만 인정한다.
- **AC-4:** 역할/turn별 사용량의 포함 관계와 집계 방법을 검증하고 Main 보고량·전체 사용량·CLI 추정·실제 청구를 분리한다. 미측정 효과를 PASS로 바꾸지 않는다.
- **AC-5:** 정확한 fixture/소스 후보·보호 경로·실제 검사·별도 문맥 검토가 있으며 기록과 tracker가 실제 결과를 반영한다. 필수 미충족이면 전체 수락을 보류한다.

## Milestones

M1: 원인과 실행 안전성 확정. M2: 최소 실제 비교/compact 및 계측. M3: 반증 검토와 결과 수락 또는 구체적 blocker 기록.

## Task Packets

### T5 — E3 최소 실제 관찰

- Main 승인:23:10. 이전/현재 모두 같은 Read-only Owner 과제로 고정한다. Owner 단독과 Owner+leaf를 서로 비교하지 않으며 Main이 구현을 가져오지도 않는다. 이 축소 관찰은 기존 leaf·장기 반복 시나리오 전체의 PASS를 대신하지 않는다.
- 지정 Owner가 새 고유 tmp에만 준비한다. 기존 종료 함수와 snapshot을 재사용하되 네이티브 leaf 완료 추정과 six-turn gate는 사용하지 않는다. single-shot CLI의 stdin을 닫고 stdout/stderr를 종료까지 회수하는 방법으로 실제 첫 A/B 한 쌍을 우선 관찰한다. 도구는Read뿐, 동일alias/과제/fixture/정책 외조건/240초/CLI추정$1.50. 합성 검사는 실제host증거가 아니다.
- 준비3분, 한 번의 구문/정리 경계 확인 후 즉시 Main에 명령을 반환한다. Main이 직접 두 CLI Owner를 순차 실행한다. 준비 Owner가 CLI Owner를 호출해 계층을 더하지 않는다. Agent/쓰기 도구 없는 과제라 leaf 완료 여부는 측정 대상 밖이며 전체 계층 효과를 주장하지 않는다.
- compact-first 한 세션은 준비 turn에 막힌 이전 방법과 다른 protocol control로만 사용한다. 첫 입력이 `/compact`이며 fresh context의 거절/no-op 가능성을 기록한다. 의미 있는 문맥 복원의 증거로 자동 대체하지 않는다. boundary가 실제 있을 때만 post-boundary Read, 전체180초/$0.50. 호출을 보내는 것과 성공은 구별한다.
- 기존 source/모든 이전tmp/설정/자격증명/사용자파일은 보호한다. 읽기·쓰기 권한을 바꾸는 우회는 금지한다. 최초 한 쌍 결과 후에만 Main이 남은 예산 안에서 추가 관찰을 판단한다. 기존 AC는 유지하고 확보된 부분 결과와 미입증을 구분한다.
- State/Result: 실제 첫 A/B 완료. 새 root `reporivet-td0001-e3-dr56una_`; single-before와single-after 모두root terminal1개/exit0/timeout없음/drain완료/파일변경없음. 두 조건 모두숫자정렬결함과거짓PASS를정확히거부했다. before59.776초/994bytes/input6773/cache-read14720/output1451/CLI표시$0.077500, after56.184초/1027bytes/input8097/cache-read10368/output1449/$0.081894. costBasis=unknown이므로청구액이아니며이한쌍만의인과효과를주장하지않는다. compact-first도실제전송했고0.215초/num_turns0/usage0/result success/boundary없음으로끝났다. 이는빈문맥control이며복원성공은아니다. 원래 E1/E2 이력은보존한다.

### T6 — E3 반복 문맥과 의미 있는 compact

- 첫 실제 결과를 바탕으로 Main이 추가 두세션을 승인한다. 총비교CLI는최대4개로유지하고추가준비probe는없다. 같은Read-only Owner구조를before/after에고정하며, 순서는after→before로첫한쌍과반대로한다. 단일과제와반복과제는서로다른과제이므로동일표본인것처럼합산하지않는다.
- 새고유tmp만쓰기,기존source/tmp/설정은보호. 준비3분. 기존bounded수신/검증한정리함수를재사용하고Agent완료gate는없다. 각각전체300초/CLI추정$1.50, 요청마다동일조건. 기존240초single-shot과다른다단계과제로별도배정하는것이지이전실패timeout만늘리는재시도가아니다. 전체E3종료23:37은유지한다.
- 단계: 같은초기진단→Main driver가C2내림차순요구·실제검사로갱신후현재평가→새비권위PASS 상태에대한평가→실제`/compact`→boundary가있는경우현재평가. 각Owner root result를받은뒤에만다음단계로전환한다. /compact전용상한120초와전체300초를함께적용한다. 종료시stdout도회수한다.
- compact-first는대화0인no-op이었으므로이번에는실제수행한과제문맥을대상으로한다. padding·가짜transcript·가상완료event는쓰지않는다. boundary가없으면실패/미입증을남기고새수선을반복하지않는다. terminal usage는모두원형보존하고누적/포함관계확인전합산하지않는다.
- Main이CLI Owner를직접순차실행한다. 준비Owner는구현/중요경계대조만하고모델을호출하지않는다. 독립검토는새고유증거경로만허용하며이전경로위반을반복하지않는다. 기존AC전체를축소관찰의PASS로바꾸지않는다.
- State/Result: after만실행, before는권한오류이후보류. 최종driver SHA256 `640f42d7235a083970f548653c68edb9a7ecdddeeaaaf9a6db2c328af184cd70`, root `reporivet-td0001-e3-repeat-eh9_i5mk`. 초기PROMPT에양쪽동일한CLAUDE.md/docs/PLANS.md Read와정확fixture경로를명시했다. Main이T5의5회Read오류를동일Start-here경로로추정했으나Owner실제대조로서로다른STATUS/README/package.json추측경로였음을확인해그추정을철회했고문서를복사하지않았다.
- 실제관측: repeat-after raw111484bytes/48행, 정상Read13회(정책2파일포함), root success3개. 초기숫자오름차순결함, C2내림차순의새반례, 비권위PASS/쓰기허용주장을모두정확히판정하고거부했다. 두실제check는exit1이다. root별usage input7992/11155/11733, cache8576/16128/19840, output1195/1012/460이며합계가마지막modelUsage input30880/cache44544/output2667과일치한다. 따라서관측된세turn에서usage는turn별,modelUsage와CLI표시가격은누적이다. 마지막$0.243347은compact이전누적표시값이며costBasis=unknown/최종청구아님.
- 실제compact 처리진입은compacting4개로관측했다. 저장된raw에boundary/compact terminal/post-boundary Read는없다. 종료중kill_group의os.killpg(pgid,0)가EPERM으로실패하여driver exit1, 이후drain/최종manifest/summary저장을막았다. 따라서미회수출력과최종비용은미확인이며PGID소멸도UNPROVEN이다.23:33:24에고유mcpconfig경로를가진CLI는ps에서관측되지않았지만이를그룹소멸증명으로대체하지않는다. 추가신호/권한우회/수선/모델실행은하지않는다. AST동일성과이전종료시험은이환경의EPERM분기를입증하지못했다.
- T5한쌍은독립대조됐고두조건최종반환994/1027bytes,CLI표시가격0.077500/0.081894였다. 차이는+3.32%/+5.67%이지만작은한쌍·cache/순서변수·정책명시Read미관측때문에정책의인과효과나일반적절감률로해석하지않는다. T6는정책실제Read와반복판정의부분근거만추가하며비교쌍이아니다.

### T7 — E3 최종 기록 후보 대조

- 별도Verifier가현재기록과T5/T6보존증거를대조하고canonical을수행한다. 새고유검증tmp만쓰기허용,기존모든tmp(venv사용만예외)/source는읽기전용,모델실행/수선/권한우회금지. 기록반영이끝난후후보를동결하며Main은이후source를수정하지않는다. 정확후보와검사결과는별도검증증거및최종응답에서식별한다. 남은효과AC와EPERM경계는소스검사성공으로PASS로바꾸지않는다.

### T1 — 제한 진단과 설계

- State/type/dependencies: completed / support / none.
- Outcome: 이전 준비 시험과 compact driver의 실제 원인을 분리하고 최소 실행 설계를 확정한다.
- Execution constraints: 지정 Owner, 읽기 전용, 재위임 없음. 최초4분/6도구, 권한 명확화 후 compact driver 추가 읽기2분/3도구. Bash의 파일 목록·Python JSON 추출은 허용하되 모델 CLI/API/실험 프로세스·쓰기 금지.
- Read: TD-0001, PLANS, 이전 run_eval.py와 compact result-summary/실제 driver/이벤트 type·시간만.
- Allowed writes: 없음. Protected: 모든 source/기존 tmp/설정/자격증명.
- Acceptance/Verify: AC-1/3/4의 사전 진단, 실제 파일 근거와 반례.
- Stop: 근거 부재·민감 정보·새 지원 조사·원인 미확정. 실행 가능한 부분과 불확실성을 반환한다.
- Result: sleep 기반 준비 추정은 handler 설치를 증명하지 못함. handshake는 시험 자식에만 적용한다. Owner 단독/Owner+leaf 제안은 Main이 비교 오염으로 거부하고 정책만 다른 동일 구조로 교정했다. 기존 compact의120초는 process 시작부터의 전체 deadline이며 앞선 진단 약53.8초를 포함한다. 실제 compact 자체의 대기120초였다고 해석할 수 없다. 기본 framing/flush 이후 compacting 진입은 있었지만 내부 처리 지연 원인은 미확인이다.

### T2 — 고유 tmp 준비와 결정적 사전검증

- State/type/dependencies: stopped / implementation / T1 completed; 비교 driver는 미수락.
- Outcome: 기존 기능을 재사용한 최소 일회성 driver와 동일 fixture를 준비하고 종료·stream·계측 사전조건을 검증한다.
- Execution constraints: 지정 Owner가 설계/중요 diff를 직접 대조한다. 단일 작성자, 재위임 필요 시 parent 하위 leaf만. 8분, 새 접근 최대2회 실패 중단. Main 계획 쓰기와 순차 수행한다.
- Read: E1/T1, 지정 기존 helper와 새 고유 tmp.
- Allowed writes: Main이 확인한 새 고유 tmp만. Protected: 저장소 전체·기존 증거/fixture·홈/설정/외부서비스.
- Acceptance/Verify: AC-1. 실제 READY→TERM→부모 종료/자식 생존→KILL→그룹 소멸을 기록하고 중요한 driver 경계를 직접 대조한다. 필요한 native leaf no-op은 별도 Main 승인 후만 가능하다.
- Stop: 안전성 미확인·공유 계약/허용 경로 변경·동일 접근2회 실패·시간 만료.
- Result: 새 tmp `/var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-td0001-t2-582kb2cm`에 준비했다. handshake-result.json은 READY(child80508/pgid80507)→TERM→부모exit-15/자식생존→TERM_SEEN→KILL→group소멸,1.059초 PASS를 기록한다. 첫 시도는 literal newline framing 실패였고 두 번째가 통과했다. 새 handshake 접근 예산도 모두 사용했으며 재시험하지 않는다. 네 Python 파일 구문 검사와 snapshot의 정책5파일만 차이 확인은 PASS. 실제 CLI/API는 아직 미실행이다. common-prompt.txt가 실제 초기 입력에 연결되지 않은 결함을 Owner가 반환했으므로 실행을 보류했다. Main은 이 원인이 확인된 한 지점만 1회/90초 수선을 배정하며 종료함수·fixture·조건·예산은 바꾸지 않는다. 이전 720초 준비 초과는 초기화하지 않는다. 공통 packet의 실제 최초 frame 연결은 byte 일치 검사로 PASS했고 수선은 약107초로90초를 초과했다. Main의 제한 대조에서 후속 prompt들이 새 정책의 직접 Read/대조 의무를 양쪽에 명령하는 비교 오염과 select 뒤 blocking readline의 deadline 사각지대를 확인했다. 이 두 지점만 두 번째 bounded 수선(90초)에 배정했다. 결과는 부분 적용이었다: bounded_line과 nonblocking FD만 추가됐고 기존 readline 연결·후속 prompt·compact driver 수선 및 검증은 미완료다. 실행을 금지한다. E2에서 동일 접근의 마지막 수선180초를 배정한다. 새 기능·handshake 재시도는 금지하고 다시 실패하면 중단한다. 원래90초 경계에 대한 Owner의 초과 보고와 host duration87.925초를 함께 남기며 서로 다른 시간 측정 범위를 같다고 단정하지 않는다. 다음180초 수신 수선은163.055초에 완료되어 부분행 timeout 검사가 PASS했다. 이후 generic tool_result 완료 오인과 compact의 약한 종료 함수가 확인되어 별도150초 경계 수선 및30초 mode 정규화를 배정했다. 이 단계 host273.241초로 초과했다. 최종 run_eval.py SHA256 `743dda90dd2b72d58d2414b4821ee28ebe3f6eaf43fec445d8bb8b251c7635dc`, run_compact.py `83ca2af28dc3fcd9c13bd05c560a4a13a6d9e390fc2c20a20831bd672302d2ec`. before 정책5파일0664→0644 정규화는 bytes를 유지했으며 fixture는 원래부터 양쪽0644다. Git blob provenance는 독립 확인됐지만 공통 prompt의 행동 유도·단일 AB 순서라는 비교 한계도 남는다. terminal gate의 합성 검사는 실제 host 지원 증거가 아니다. 최종 비교 classifier 결함은 T3에 기록하며 수선을 더 반복하지 않는다.

### T3 — 실제 비교와 compact

- State/type/dependencies: stopped / verification / 비교 보류; 독립된 Read-only 세션만 실행.
- Outcome: 같은 조건의 실제 반복 작업 및 compact를 실행하고 raw 증거를 Main 문맥 밖에 보존한다.
- Execution constraints: Main이 준비된 명령으로 CLI Owner를 직접 배정한다. CLI의 leaf만 bounded 구현, 깊이 Main→Owner→leaf, 각 비교 세션에서 leaf 최대1개(필요 시 같은 문맥 재개). E2에서 한 쌍만 순차 실행하며 조건별 wall-clock240초/CLI 추정$1.50. control 추가 세션은 생략한다. compact 한 세션은 준비 turn별30초, compact 전용120초, 전체180초/$0.50로 구분한다. 전체 실행 단계20분 안, 전체 E2 종료 경계도 준수한다. 시작 전에 실제 옵션과 조건을 고정한다.
- Read: 각 snapshot의 권위 계약/fixture/검사 결과. 이전/현재 공통 prompt에 새 Owner 의무를 추가하지 않는다.
- Allowed writes: 새 tmp의 지정 fixture 구현 파일과 driver 증거만. Protected: 모든 나머지 경로·원본/기존fixture/설정.
- Acceptance/Verify: AC-2/3/4. 중복없는 실제 이벤트·검사 exit·hash/mode·시간과 usage 포함 관계. 실제 compact와 수동 재주입/재시작은 분리한다.
- Stop: 준비 안전성 실패, guard/권한 거절, 보호 경로 변경, budget/timeout, 동일 접근2회 실패. 실패를 없던 run으로 처리하지 않는다.
- Result: 비교 실행은 보류한다. 최종 run_eval.py SHA743dda90…의123행은 parent_tool_use_id를 구분하지 않고 모든 result를 Owner turn 종료로 취급한다. 같은 파일의 terminal gate는 child result를 완료 근거로 삼으므로, 그 이벤트가 오면 child 종료가 Owner 종료로 오인되어 후속 turn/계측이 앞당겨질 수 있다. native 형태는 미관측이며 이 결함을 숨긴 채 효과 비교를 실행하지 않는다. 마지막 수선 이후 추가 수선·재시도는 하지 않는다. compact는 Agent가 없는 Read-only 세션이라 이 blocker와 독립적이다. 두 driver의 PGID 정리 함수 AST 동일성과 compact finally의 무조건 호출을 Main이 확인했으며, standalone 종료 분기 근거·bounded 수신 검사와 함께 compact 한 번만 실행 승인한다. 준비 turn30초씩/compact120초/전체180초, CLI추정$0.50, 모든 실패를 보존한다.
- 실제 명령: `python3 -B /var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-td0001-t2-582kb2cm/run_compact.py`. `compact-run/summary.json`은 총35.263초, 준비 turn1 약30.025초 deadline, inputs1개, result0개, boundary없음, exit0, group_gone=true를 기록했다. `/compact`와 두 번째 준비 turn 및 post-boundary 요청은 미전송이다. 따라서 이는 실제 CLI 준비 단계 중단이지 compact 완료 실패나 성공의 새 근거가 아니다. 수신 중단 뒤 프로세스 종료까지의 출력은 drain하지 않아 최종 result/usage가 발생했는지도 미확인이다. Root/leaf 합계·Main 전체 context·청구·절감률은 계산하지 않는다. Owner 직접 대조에서 raw14796bytes/JSONL11행(system1/assistant6/user4), Read4회와 대응결과4개, 최종 text/result0개를 확인했다. 반복된 assistant usage1436 및2201은 누적 범위가 미확인이라 합산하지 않는다. stderr의 unrecognized_model 진단2개는 backend 정체나 청구 모델을 증명하지 않는다. 마지막90초 읽기 전용 대조도 host131.723초로 초과했다.

### T4 — 독립 검토와 최종 통합

- State/type/dependencies: stopped / verification / 동결 후보 검토 완료, 최종 기록 후보 재검토는 시간 소진으로 미실행.
- Outcome: 구현/Owner 결론에 의존하지 않고 exact 후보·raw 증거를 반증하고 기준별 결과를 판정한다.
- Execution constraints: 별도 문맥, 읽기 전용, source 변경/새 실험/재위임 없음, 5분. Main은 검증 중 source 기록을 동결한다.
- Read: E1/결과, 지정 tmp 증거, 현재 source/보호 파일, 기존 검사.
- Allowed writes: 고유 검증 증거와 원래 검사 산출물만. 기존 승인 venv를 프로세스 PATH에만 사용하며 새 설치 없음.
- Acceptance/Verify: AC-1~5, `PYTHON=python3 ./dev/check`, drift/diff, 정확 후보 hash/mode/삭제 목록, 지표/인과 주장 반증. source 테스트 성공을 효과 입증으로 바꾸지 않는다.
- Stop: 후보 변경·근거/권한 부족·예산 만료. 원래 기준을 낮추지 않는다.
- Result: 별도 문맥이 동결 후보의 driver 결함·실제 Read4회·compact 미전송·usage 미확인을 독립 확인했다. 승인된 venv PATH의 `PYTHON=python3 ./dev/check`는 exit0,60tests/6.550s/OK였다. nonignored73항목/삭제0의 검사 전후 manifest가 동일하며 SHA256 `f8c3c6b73a2f20a9ad72358d2d3c9a2b0d0efab7de9a6b0118d783c66acfbcfc`다. 사용자 PLAN0011의 hash/mode/inode/ctime, completed PLAN0012 및 source 정책은 보존됐다. Verifier 판정은 AC1 PASS, AC2~5 UNPROVEN, 전체 수락 안 함이다. 이 결과를 반영한 현재 기록 파일은 이전 동결 후보와 다르며, 그 PASS를 자동 승계하지 않는다. 마지막 독립 재대조는 미실행이다.
- 증거 및 경계 위반: Verifier가 새 고유 검증 tmp 대신 읽기 전용으로 배정된 기존 `reporivet-independent-verify-tf1q8jwj`에 `dev-check.log`, `manifest-before.json`, `manifest-after.json`, `candidate-comparison.json`을 생성했다. Main은22:43:43에 이4파일의 birth/mtime이22:38~22:40임을 확인했다. 새 파일 생성 정황이지 기존 모든 증거가 덮어써지지 않았다는 완전한 증명은 아니며, 이 허용 경로 위반을 숨기거나 산출물을 삭제하지 않는다. 증거 위치가 유용하다는 이유로 경계 위반을 수락하지 않는다.
- 종료: T4 host342.786초는5분을 초과했고 반환 확인 시 E2전체60분(22:42:31)도 지났다. 추가 평가·수선·검증 배정은 중단하고 실패·종료 기록만 반영한다. 이 기록 반영 뒤의 후보는 독립 검토 미완료로 유지한다. Main은 효과 검증 완료를 승인하지 않는다.

## Architecture Impact

없음. source/runtime/배포 인터페이스 변경 없이 기존 host와 고유 tmp 시험만 사용한다.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| 이 계획 | create | 새 사용자 요청·진단/실행 실패·수락 보류 기록 | Main | 기록 반영, 최종 독립 재대조 미완료 |
| tech-debt-tracker.md | update | TD-0001의 실제 결과/잔여 blocker | Main | resolved; 독립 대조 대상 |
| CLAUDE/AGENTS/PLANS/QUALITY/제품 문서 | none | 정책·제품 변경은 요청 범위 밖 | Main | resolved |
| completed PLAN-0012/사용자 PLAN-0011 | none | 역사·사용자 변경 보존 | Main | resolved |

## Interfaces and Dependencies

Main이 정책 비교 조건과 실행 순서·허용 경로를 고정한다. Owner는 실제 driver 설계와 안전성·증거 대조를 책임진다. mutable 준비/CLI 실행/기록은 순차, 읽기 전용 진단은 병렬 가능하다. 준비자가 CLI 실행까지 맡아 중간 평가Main 계층을 만들지 않는다. 공유 계약 변경은 Main에 반환한다.

## Migration, Rollout, and Recovery

배포/migration 없음. 기존 시험을 덮어쓰거나 재실행하지 않는다. 새 고유 tmp만 사용하고 실패 증거를 남긴다. 기록을 위해 commit/push/PR을 만들지 않는다. 같은 실패 접근을 모델/agent 변경으로 재시작하지 않는다.

## Surprises and Discoveries

- 초기 Owner가 read-only 파일 목록 조회까지 CLI 실행 금지로 해석했다. Main은 허용된 Bash 파일 읽기와 금지한 모델/API 실행을 구분해 명확히 했다.

## Decision Log

- no-change/절차 재기록만으로는 사용자 요청을 충족하지 못하므로 실제 실행을 우선한다. 기존 sleep 시험 반복과 timeout만 늘리는 접근은 원인 증거가 없어 제외한다. 새 runtime/범용 orchestration은 필요 없으며 기존 CLI·fixture·증거 체계를 재사용한다.

## Concrete Steps

1. 권위·기준·보호 파일과 과거 실패를 확인한다.
2. Owner가 진단 근거로 설계를 확정하고 새 tmp에서 결정적 사전검증한다.
3. 고정 조건의 실제 비교 및 compact를 실행한다.
4. 독립 검토·source 검사 후 Main이 결과와 tracker를 갱신한다.

## Validation and Evidence

| Acceptance criterion | Task | Result | Evidence | Verified candidate | Reviewer recommendation | Main approval |
|---|---|---|---|---|---|---|
| AC-1 | T1/T2/T6 | UNPROVEN | 기존READY분기PASS는유지하나E3실제EPERM/그룹소멸미확인 | repeat640f42d7… | 이전PASS의범위를한정 | 새환경전체안전성수락안함 |
| AC-2 | T5/T6 | UNPROVEN | 단일진단한쌍완료,반복after만부분완료 | T5/T6의고유root/hash | T5제한관측확인 | 전체효과수락안함 |
| AC-3 | T5/T6 | UNPROVEN | 빈문맥거절및유의미문맥compacting4개, boundary/복원없음 | T6보존raw | 최종대조대상 | 수락안함 |
| AC-4 | T5/T6 | UNPROVEN | single원형/반복3turn누적관계확인,전체계층/Main문맥/청구미측정 | T5/T6 terminal원형 | T5제한관측확인 | 전체효과수락안함 |
| AC-5 | T7 | UNPROVEN | 최종기록동결후소스대조; T6최종manifest/회수부재유지 | T7의별도최종candidate증거 | 최종대조결과별도 | 전체수락보류 |

원시 transcript/로그는 commit하지 않는다. 이 계획에 명령·판정·실패·지표 의미와 증거 위치를 durable 요약으로 남긴다. 실제 청구/장기 Main 전체 문맥이 미측정이면 미입증으로 유지한다.

## Outcomes and Retrospective

E3에서는동일한읽기전용단일진단한쌍을실제로완료했고둘다정확한결함판정을반환했다. 현재조건의반환bytes와CLI표시가격은각각3.32%/5.67%높았으나한쌍의제한된관측이며정책인과효과/청구절감으로해석하지않는다. 의미있는대화문맥에서는정책Read·C2전환·거짓PASS거부3개판정을관측했지만반대조건은권한오류로보류했다. 실제compact처리진입은있었으나boundary와복원은입증하지못했다. 단일·반복실험을합산하지않으며장기Main전체문맥·전체계층비용·실제청구효과는여전히미측정이다. TD-0001은open,전체수락은보류한다. E3종료기록이후추가실행/신호재시도/권한우회는하지않는다.

### E1/E2 이력

효과 검증 목표는 충족하지 못했다. 준비 수선이 반복되고 원래45분 및 여러 단계 예산을 초과했으며, 새 paired 실행0회와 compact 미전송 상태다. 이는 절감이 없다는 실험 결과가 아니라 효과를 측정하지 못한 결과다. 실제 Read-only 세션의 파일 읽기와 정상 종료·그룹 소멸만 관측했다. 전체 수락은 보류하며 계획을 active에 둔다. Source 정책/제품/배포 자산·completed PLAN-0012·사용자 PLAN-0011은 수정하지 않는다. TD-0001을 닫지 않고 남은 classifier, drain, 실제 compact와 사용량 포함 관계를 기록한다. 추가 수선/모델 호출·commit/push/PR은 이번 E2에서 하지 않는다. 독립 최종 대조와 source 검사 결과는 T4 및 증거 표에 별도로 기록한다.

## Follow-ups

기존 TD-0001을 재사용하며 실제 결과에 따라 갱신한다. 새 task registry는 만들지 않는다.
