---
id: PLAN-2026-0007
kind: exec-plan
status: completed
owner: main
area: harness
created: 2026-09-08
updated: 2026-09-08
base_commit: "226b15af1b8ccf1d82ba410322a214f1f593cc7e"
---

# Agent 진입점과 실제 탐색 중심으로 제품 책임 전환

## Purpose / Big Picture

사용자는 고정 문서 schema·복사 runtime·Gate·계획 종료 체계의 필요성을 문제 삼고, 프로젝트마다 다른 문서를 AGENTS.md/실행 환경의 진입점에서 실제로 찾아 활용할 수 있는지를 제품의 핵심으로 바꾸자는 설명에 “ㅇㅇ그렇게 변경해줘”라고 지시했다. 이 요청은 아래 범위의 기존 제품 계약 변경 권한이다. 이전 v0.2.0의 runtime 유지 요구를 이번 전환의 승인으로 오인하지 않으며, 반대로 이전 요구로 새 요청을 무효화하지 않는다.

완료 결과는 기존 문서·명령을 보존하는 작은 entrypoint initializer와, 서로 다른 문서 구조에서 새 agent가 근거·검사 명령·충돌을 찾는 실제 탐색 평가다. 문서 내용의 의미·완료 승인·프로젝트 테스트를 Reporivet 자체 Gate가 대신하지 않는다.

## Progress

- [x] 사용자 변경 의도, 현재 main/clean 상태와 기존 계약 확인.
- [x] 재사용 가능한 파일 안전성 구현과 제거 경계 조사.
- [x] runtime 없는 target 생성·점검·명시적 전환 경계 구현.
- [x] source 문서·계약·검사·배포 inventory 정합화.
- [x] 다른 구조의 fixture에서 실제 새 agent 탐색 수행.
- [x] 독립 반증, 통합 검사, 근거 및 완료 기록.

## Context and Orientation

기준 커밋은 226b15af1b8ccf1d82ba410322a214f1f593cc7e이며 공개 v0.2.0 tag는 364a77346d542042307bdcc3f5a84602ec105c08이다. src/reporivet/initializer.py는 파일 안전성과 생성 정책을 함께 갖고 있고 packaged dev/harness.py는 고정 schema·계획·Gate를 target으로 복사한다. 소스 dev/도 이를 사용한다. 기존 PRODUCT/ARCHITECTURE/SPEC-001/SPEC-002의 runtime 필수 계약은 이번 요청과 충돌하므로 새 제품 경계로 명시적으로 대체한다. completed 계획과 공개 release는 역사로 보존한다.

## Scope

- 다음 미출시 버전에서 installed CLI와 generated 문서의 책임을 entrypoint 작성·read-only 관찰·기계적 경로 점검으로 제한한다.
- target에 dev runtime/wrappers, harness.toml, Gate, runs, 계획 schema, CI workflow, 고정 PRODUCT/ARCHITECTURE 파일군을 더 생성하지 않는다.
- 기존 문서 이름과 배치를 유지하고 관찰된 경로와 사용자 확정 근거를 구분한다. 프로젝트 명령을 추론해 실행하거나 관찰을 authority로 자동 승격하지 않는다.
- AGENTS의 한정된 관리 블록과 선택적인 CLAUDE 진입 연결을 제공한다. 사용자 본문/기존 파일 bytes는 보존한다.
- 패키지의 기존 경로 안전·소유권·preimage/postimage·rollback 구현을 검토하고 가능한 부분을 재사용한다.
- 기존 공개 runtime형 target은 자동 삭제/변환하지 않는다. 변경 전 감지하여 무변경으로 거부하고 사람이 검토할 전환 절차를 문서화한다.
- source의 사용하지 않는 runtime/검사 정책을 함께 정리한다. 보안·파일 보존 회귀는 유지하거나 동등 이상의 새 경계 테스트로 이전한다.
- 원본과 별개의 통제된 fixture에서 fresh agent의 실제 수행 결과를 비교한다. 새로운 LLM 서비스나 평가 실행 엔진은 만들지 않는다.

## Non-goals

- GitHub push/PR/merge/release, v0.2.0 tag/asset 변경, PyPI 게시.
- 사용자 저장소의 기존 runtime·문서·설정 삭제나 자동 migration.
- app/DB/API 구현, 자율 agent 실행 서비스, 모델 의존성·telemetry·새 task database.
- 구조 검사를 의미적 품질의 통과 근거로 사용하거나 제한된 agent 실험을 보편적 성능 보장으로 포장하기.
- completed 계획 및 accepted 결정의 본문을 소급 재작성하기.

## Acceptance Criteria

- **AC-1:** 빈 target과 문서 배치가 다른 기존 target에서 entrypoint를 생성한다. runtime·고정 문서 schema·Gate·작업 상태 파일·workflow를 생성하지 않는다.
- **AC-2:** 기존 문서·설정·명령·CI·관리 블록 밖 instruction bytes를 보존한다. 재실행은 안정적이고 audit/doctor/preview는 읽기 전용이다. 경로 탈출·symlink/nonregular·잘못된 marker·중간 실패 회귀를 검사한다.
- **AC-3:** doctor는 파일 존재·경로/관리 구조 등 기계적 범위만 판단하며 의미적 탐색/완료 PASS를 주장하지 않는다. 어떤 명령도 프로젝트 명령이나 원격 내용을 실행하지 않는다.
- **AC-4:** v0.2 target은 어떤 write 전에도 명확히 거부되며 공개 release와 기존 source 역사/사용자 파일은 불변이다. 새 미출시 버전, CLI 제거 항목, 수동 migration/rollback 경계를 문서화한다.
- **AC-5:** 별도 context의 agent가 서로 다른 문서 구조의 fixture에서 같은 작업 조건으로 올바른 근거·실제 검사 명령·과거/충돌 문서를 식별한다. 적용 전후 대조, 작업 결과, 환경/모델/한계를 기록한다. 실패를 숨기지 않는다.
- **AC-6:** 설치 wheel의 asset inventory와 실제 init/audit/doctor를 확인하고 uninstall 뒤에도 일반 Markdown 진입점이 유효함을 확인한다. 현재 문서·source 실행 명령·테스트가 새 제품 경계와 일치하고 독립 리뷰와 전체 검사가 완료된다.

## Task Packets

### T1 — 기존 재사용 경계 조사

- Task type: support
- State: completed
- Outcome: initializer의 파일 안전성 재사용 경계와 runtime 결합, 유지할 회귀를 확인한다.
- Reads: src/reporivet/initializer.py, cli.py, tests.
- Allowed writes: 없음. Main만 이 계획 기록.
- Protected paths: 모든 원본과 기존 임시환경.
- Acceptance: AC-1/2/3/4.
- Execution constraints: Sonnet read-only leaf, 재위임 금지, 7분, 같은 접근 실패 2회 시 중지.
- Result: Sonnet read-only 조사 완료. 기존 파일 소유권·경로·transaction 보호와 runtime 결합을 식별했고 Main이 T2의 재사용·제거 경계로 수락했다. 원본 쓰기는 없었다.

### T2 — 제품 코드·테스트 전환

- Task type: implementation
- State: completed
- Depends on: T1.
- Outcome: scope에 명시한 최소 entrypoint initializer를 구현하고 기존 안전성 회귀를 새 제품 계약으로 이전한다.
- Allowed writes: src/reporivet/{initializer.py,cli.py,__init__.py}, src/reporivet/assets/project/**, pyproject.toml, tests/test_reporivet.py, tests/test_audit_adoption.py, tests/test_distribution.py. 제거 대상은 직접 읽은 obsolete package assets와 tests/test_{definition,authority_lifecycle,code_map,traceability,verification_run,gate_close_plan}.py다. Source contract tests 두 개는 Main 소유로 보존한다. Code agent가 유일한 writer이며 Main도 이 구간에 계획/문서를 병렬 편집하지 않는다.
- Protected paths: completed 역사, 외부 저장소/release, 기존 임시환경, Main 소유 문서·계획·계약.
- Acceptance: AC-1/2/3/4/6.
- Execution constraints: 단일 writer, 새 고유 mktemp 경로만, 재위임/자기 승인 금지, focused checks, 같은 접근 실패 2회 시 반환.
- Result: Sonnet 구현과 fresh Sonnet T2-R 보수 후 Main이 추가 회귀·배포 격리·fence 보수를 통합했다. 첫 두 후보는 미수락했으며 최종 db8ae63 후보만 아래 근거로 수락했다. init/audit/upgrade/doctor 및 단일 AGENTS template만 남기고 target runtime/schema/Gate assets를 제거했다. 최종 전체 47 tests가 통과했고 확인된 잔여 결함은 없다.

### T3 — Main 통합 및 문서·source 정책 전환

- Task type: implementation
- State: completed
- Depends on: T2.
- Outcome: 현재 문서를 구현과 일치시키고 오래된 계약을 명시적으로 supersede한다.
- Allowed writes: README.md/README.en.md, CLAUDE.md portable block와 sync 결과 AGENTS.md, ARCHITECTURE.md, docs의 현재 문서·새 ADR·평가 절차/fixture 기록, dev source 도구, .github/workflows/ci.yml, 이 계획.
- Protected paths: completed 계획 본문, accepted ADR 본문, release/tag/remote, unrelated 사용자 파일.
- Acceptance: AC-4/5/6.
- Execution constraints: Main이 정책·경계·통합·계획을 소유하며, 정해진 T3 변경은 Sonnet Implementer에게 단일 writer로 배정한다. 코드 T2 writer 종료 후 순차 수행한다. 정책 변경은 사용자 승인 범위 안에서만, dependency·외부 서비스 추가 없음. T3의 추가 allowed writes는 source의 .reporivet-version 및 확인된 빈 .harness/runs/.gitkeep 제거(기존 logs/tmp와 .gitignore는 보존), tests/test_agent_contract_sync.py 및 tests/test_agent_operating_contract.py의 obsolete target-schema 기대 정리, tests/fixtures/navigation/**의 평가 원본이다. Implementer는 이 계획이나 completed/accepted 역사 본문을 변경하지 않는다.
- Result: Sonnet의 순차 source/docs 구현 후 Main이 현재 계약·수동 완료 정책·평가 기록을 정합화했다. CLAUDE portable block은 helper로 AGENTS에 투영했고 source dev/check와 CI를 새 제품 책임에 맞췄다. SPEC-003/ADR-0002/migration/평가 기록을 작성했다. 기존 completed/accepted 역사, .gitignore, 과거 raw logs, 공유 환경과 공개 release는 보존했다. 최종 db8ae63 후보의 독립 검토와 Main 수락을 완료했다.

### T4 — 실제 agent 탐색과 독립 반증

- Task type: verification
- State: completed
- Depends on: T2/T3.
- Outcome: 정확한 candidate를 별도 context에서 반증하고 실제 탐색 task의 성공/실패를 관찰한다.
- Allowed writes: 각 agent의 새 고유 임시 fixture/근거만. Main이 결과를 이 계획과 평가 기록에 통합.
- Protected paths: 원본 구현·수락 기준·기존 임시환경·다른 agent fixture.
- Acceptance: 전체.
- Execution constraints: read-only 검토는 병렬 가능, fresh agent에는 해당 fixture와 작업만 전달, 재위임 금지, 실패를 임의 수정하지 않음. scope 변경/target mismatch 시 Main 반환.
- Result: 서로 다른 두 fixture에서 네 fresh Sonnet 세션이 현재 근거·코드 불일치·과거 문서·실제 실패 검사를 정확히 식별했다. Before부터 성공했으므로 향상은 입증하지 않았다. 별도 context의 Sonnet Independent Verifier a5a19f9ce6dafe7f9는 최종 db8ae63 후보 131개 항목의 일치, 전체 47 tests 및 직접 반례 검사를 확인하고 잔여 확인 결함 없이 PASS recommendation을 보고했다. Main은 아래에서 별도로 최종 수락했다.

## Architecture Impact

Target의 wrapper → copied runtime 의존성을 없애고 installed CLI → 안전한 Markdown entrypoint 생성 경계만 남긴다. Target 읽기와 개발은 일반 파일 탐색 및 기존 project 도구로 수행한다. source repository의 tests/CI는 제품 개발용이지 target에 강제되는 완료 시스템이 아니다.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| PRODUCT/ARCHITECTURE/README들 | update | 새 제품 책임과 실제 CLI | Main | resolved |
| CLAUDE portable block/AGENTS | update/generate | source의 실제 진입점·검사 정책 | Main | resolved |
| QUALITY/SECURITY/PLANS/docs README | update | 기계적 검사와 행동 평가·계획 정책 분리 | Main | resolved |
| SPEC-001/002, DESIGN-001/002, MOD-HARNESS-RUNTIME | supersede | runtime형 과거 경계 표시 | Main | resolved |
| 새 제품 명세/설계 결정/migration/평가 절차 | create | 이유·대안·수락·전환·실험 근거 | Main | resolved |
| completed 계획 및 accepted ADR 본문 | none | 역사 보존 | Main | resolved |

## Interfaces and Dependencies

생산 dependency는 추가하지 않는다. 읽기 전용 조사는 위임하되 실제 쓰기는 순차 수행한다. CLI 및 marker/ownership 경계는 T1 이후 Main이 고정하고 구현 packet에 전달한다. 새로운 runtime fallback이나 v0.2 호환 실행 경로는 추가하지 않는다.

## Migration, Rollout, and Recovery

공개 v0.2.0은 그대로 유지하고 다음 미출시 버전에 breaking change를 명시한다. 기존 runtime형 target 자동 migration은 하지 않으며 old marker/version/managed runtime을 발견하면 write 전 거부한다. 사용자는 기존 버전을 계속 쓰거나 별도 검토된 변경에서 자신의 문서·instruction·CI 의존성을 옮긴다. 실패한 init/upgrade는 preimage/postimage guard로 복구하되 concurrent 사용자 변경을 덮어쓰지 않는다. 소스 변경은 로컬 diff로 유지하며 원격 publication은 이번 권한에 없다.

## Surprises and Discoveries

- 2026-09-08 — 현재 기본 Python에는 tomllib이 없으므로 기존 지원 Python 3.13 환경을 명시한다. 기존 환경 삭제·재생성·패키지 설치를 수행하지 않는다.
- 2026-09-08 — 과거 Gate 기반 완료 규칙은 이번 제거 대상이다. 이를 조용히 우회하지 않고 source 정책 전환을 기록하며 전체 테스트·독립 검증·명시적 근거 수락은 유지한다.

## Decision Log

- 2026-09-08 — 사용자 최신 변경 지시를 위 범위의 제품 경계 전환 승인으로 적용한다. 단순 설명 수정/no-change는 요청을 충족하지 못한다. runtime을 기본 비활성 옵션으로 남기는 안은 두 제품 모델과 maintenance를 남겨 기각한다. 기존 파일 자동 삭제/변환은 사용자 지식을 손상할 수 있어 기각한다. 완전히 새 framework는 기존 안전성 구현 재사용을 검토하기 전 도입하지 않는다. 재검토 조건은 실제 여러 저장소의 탐색 결과 또는 구체적인 안전성 결함이다.

## Concrete Steps

1. 현재 source 계약과 read-only 조사로 경계 고정.
2. regression 및 작은 installed CLI와 entrypoint asset 전환.
3. source 문서/정책/CI 정합화.
4. fresh agent fixture 대조와 독립 반증.
5. 전체 unit/integration/distribution 검사, exact candidate/diff와 근거 기록.

## Validation and Evidence

기준: base 226b15a, 시작 작업 트리 clean. 기존 178 tests 결과는 새 전환의 통과 근거로 사용하지 않는다.

- T1 Sonnet 조사 완료. 기존 transaction/marker/path guard 재사용, runtime/template/검사 결합 제거 필요 확인.
- T2 첫 후보: focused 15 tests OK, 전체 35 tests 중 3 failures/3 errors(29 pass). source 계약의 과거 기대치가 남아 있다. distribution test는 wheel build/inventory만 수행했으며 이름과 달리 install/uninstall을 수행하지 않았다. Main은 이 후보를 수락하지 않았다.
- Main 코드 확인에서 immutable preimage를 렌더 뒤 재수집하는 오류, fenced/malformed marker 보호 퇴행, 실제 legacy version 형식 누락, doctor missing/symlink 검사 누락, 미사용 template/링크 없는 encoded 경로, 최초 재실행·mtime·이름 안정성, install/uninstall 누락, 무시되는 legacy keyword 인자를 발견했다. 보수 및 새 회귀 전 완료 주장 금지.
- 첫 T2 writer는 명시적으로 원본 쓰기/테스트를 중지했다. Main 일부 문서 정리 → T2 두 번째 후보 → T3 source 전환 순으로 단일 writer를 유지했다. 두 번째 후보도 독립 검토에서 post-replacement 예외의 현재 operation rollback 누락, doctor local-link 검사 누락, reserved legacy 판별 fail-open이 확인되어 미수락이다. Main 추가 반례는 partial marker 수용, fenced legacy false positive, placeholder 재치환, 무제한 제외 목록/탐색이다.
- 같은 부분 수정 접근을 반복하지 않고 fresh Sonnet T2-R Implementer에게 regression-first 보수를 배정한다. Allowed writes는 initializer.py, cli.py, AGENTS.md.tmpl 및 세 제품 test 파일만이며 기존 T2의 보호 경계를 상속한다. 방문 entry/출력 budget에서 실제 탐색을 중단하고, 판별 불가능한 reserved legacy marker는 목적지를 읽지 않고 write 전 거부한다. Main이 최종 통합·수락하며 수정 후보는 다시 독립 검증한다.
- T3 source/doc writer 종료. Source contract sync, syntax, diff 검사 성공 보고; 전체 검사에서 distribution 실패 보고가 있으므로 Main이 지원 Python 환경에서 원인을 확인한다. 완료로 수락하지 않았다.
- 적용 후 fresh Sonnet 두 건도 current/code 불일치와 과거 구분, 실제 검사 exit1을 정확히 보고했다. 적용 전후 성공률 향상이나 byte-identical prompt 통제는 입증하지 않았다. 최종 후보의 생성 bytes와 실험 target 일치 확인이 남았다.
- 적용 전 fresh Sonnet 대조 두 개: Atlas는 현재 30분/코드45, Birch는 현재120초/코드300 및 과거 근거 supersession을 정확히 찾고 실제 검사 exit1을 보고했다. 적용 전부터 성공했으므로 개선효과를 아직 주장하지 않는다. 고유 fixture는 /private/tmp/reporivet-navigation-ignda9rj, 원본 변경 없음.

### 최종 통합 검증 — 2026-09-08

- 정확한 대상: base `226b15af1b8ccf1d82ba410322a214f1f593cc7e` 위의 로컬 통합 후보. `/private/tmp/reporivet-reviewed-fix-jmfs_9va/files.json` SHA-256은 `db8ae63c3d72be0e6c6d0ae42bc4bb118767eed68ce0a6b3270031e44d9d4d16`이다. Tracked 및 nonignored untracked 경로의 bytes SHA-256·mode와 삭제(null) 131개 항목을 포함한다. 이 계획의 완료 기록만 basename으로 제외했으며, 이는 검토 대상 코드·현재 문서를 바꾸지 않고 검토 후 수락을 기록하기 위한 예외다. 임시 snapshot은 후보 식별 자료이며 제품의 새 manifest/Gate가 아니다.
- Main과 Independent Verifier가 각각 `PYTHON=/private/tmp/reporivet-py313-venv-EANM2w/bin/python ./dev/check`를 실행했다. Python 3.13.15/setuptools 84.0.0에서 전체 **47 tests OK**, portable contract sync, compileall, git diff 검사 통과. 기본 Python 3.9.6/setuptools 58.0.4는 지원 범위 밖이었고 앞선 distribution 실패는 이 환경에서 발생했다. dev/check는 이제 Python 3.11 미만을 시작 시 명확히 거부한다. 지원 환경을 삭제·재설치하지 않았고 검사를 skip하지 않았다.
- 실제 wheel을 offline build하고 고유 venv에 설치했다. PYTHONPATH/PYTHONHOME/PYTHONUSERBASE를 제거한 임시 cwd에서 isolated import가 설치 venv 내부를 가리키는지 확인하고 실제 console script로 init/audit/doctor를 실행했다. Uninstall 후 import 부재와 console script 삭제, target AGENTS bytes 보존, copied runtime 부재를 확인했다. 단순 source import나 wheel inventory만의 검사가 아니다.
- Main의 추가 회귀는 malformed/partial marker와 unclosed fence, 실제 replacement 뒤 cleanup 실패 시 현재/이전 operation 복구, concurrent 사용자 변경 보존, 렌더 전 immutable preimage, 실제 scandir iteration 512개 상한, inert 이름과 single-pass 치환, malformed URL/NUL 진단을 포함한다. 마지막 valid Markdown fence info의 opposite character 두 사례는 수정 전 실패를 재현하고 opener parser 보수 후 통과했다.
- Independent Verifier `a5a19f9ce6dafe7f9`는 구현 쓰기에 참여하지 않은 별도 Sonnet context에서 최종 후보의 131개 hash/mode/deletion 일치와 전체 검사를 확인했다. Fence info·unclosed/short closer, rollback·doctor links/empty block·legacy fail-closed·concurrent edit·탐색 budget·symlink·hostile name·격리된 console install/uninstall을 직접 재검증했다. 확인된 잔여 결함 없이 **PASS recommendation**을 보고했다. 이는 Main이나 사람의 승인이 아니다.
- Main은 완료 기록 전 후보 SHA-256과 131개 항목의 drift 없음, HEAD와 v0.2.0 tag 불변을 다시 확인했다. 초기 후보의 실패와 중간 대기 기록은 위에 역사로 남겼으며 현재 상태는 이 최종 근거가 대체한다.
- 실제 탐색 평가의 원본·절차·읽은 순서·실패 출력과 한계는 `docs/references/agent-navigation-evaluation.md`에 기록했다. 최종 생성 bytes는 실제 after 실험의 Atlas AGENTS 및 Birch AGENTS/CLAUDE와 동일하고 doctor를 통과했다. 최종 fence 보수 뒤에도 동일성을 재확인했다. 네 세션 모두 진단에 성공했지만 before부터 성공했고 after 읽기는 각각 하나/둘 늘었다. 시간·토큰·실제 코드 수정·CLAUDE-only 출발의 향상을 입증하지 않았다.
- 원격 CI 실행, 커밋, push, PR, merge, release 및 PyPI 게시는 수행하지 않았다. 로컬 후보는 `0.3.0.dev1`이며 공개 v0.2.0 tag/assets를 교체하지 않았다.

## Outcomes and Retrospective

Main은 2026-09-08에 위 exact candidate와 독립 검증 recommendation을 별도로 검토하여 **AC-1부터 AC-6까지 수락하고 이 계획을 완료한다**. Documentation Impact는 모두 resolved이며 확인된 미해결 결함이나 완료 blocker는 없다. 이 수락은 로컬 구현 완료에 한정되며 릴리즈 승인이나 사용자 저장소의 자동 전환 권한이 아니다. 수동 계획 정책에 따라 이 기록을 active에서 completed로 이동한다.

Target은 AGENTS의 한정된 관리 블록과 opt-in CLAUDE 연결만 받는다. 기존 문서 구조·코드·명령·설정·CI는 유지하고 runtime/schema/Gate/작업 상태를 생성하지 않는다. 기계 검사는 파일·경로·소유권·복구만 보장하며 현재 근거의 의미와 작업 완료를 대신 판단하지 않는다. 실제 탐색 실험은 사용자의 질문을 검증하는 작은 근거이지 제품 추가 효과의 증명은 아니다.

## Follow-ups

현재 범위의 미해결 작업은 없다. 더 넓은 저장소·모델·반복 시행에서 구체적인 탐색 문제가 확인될 때 평가나 제품 필요성을 재검토한다. 이미 잘 연결된 저장소에는 추가하지 않는 것도 합리적인 결과다. 커밋·외부 게시와 기존 v0.2 target의 수동 전환은 별도 권한과 검토가 필요한 작업이며 이번 완료 범위에 포함하지 않는다.
