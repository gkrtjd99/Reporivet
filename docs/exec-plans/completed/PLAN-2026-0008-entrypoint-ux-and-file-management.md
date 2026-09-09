---
id: PLAN-2026-0008
kind: exec-plan
status: completed
owner: main
area: entrypoints
created: 2026-09-08
updated: 2026-09-08
base_commit: "226b15af1b8ccf1d82ba410322a214f1f593cc7e"
---

# 진입점 UX와 파일 관리 안내 보수

## Purpose / Big Picture

사용자는 UX·파일 관리 평가를 받은 뒤 “그래 ux문제 보수하고 문서들도 싹 업데이트 하자”라고 지시했다. 기존 PLAN-0007의 로컬 통합 후보를 보존하면서 실제 변경 diff, 실행 환경에서 읽을 수 있는 복구 안내, 관리 블록의 편집·갱신·제거 안내, 읽기 쉬운 Unicode 링크를 제공한다. 현재 문서를 실제 동작과 맞추되 역사 기록은 다시 쓰지 않는다.

## Progress

- [x] 앞선 독립 UX 평가와 Main 재현으로 문제·권한·범위 확인.
- [x] 최소 UX 보수와 회귀 검사 구현.
- [x] 관련 현재 문서·예제·평가 대상 설명 갱신.
- [x] 정확한 통합 후보의 독립 반증과 최종 검사.
- [x] Main 수락과 완료 기록.

## Context and Orientation

기준 HEAD는 위 base이며 작업 트리에는 PLAN-0007의 미커밋 변경이 있다. 제품은 0.3.0.dev1이며 target에 AGENTS/선택적 CLAUDE 블록만 생성한다. initializer.py의 immutable _Operation이 렌더와 쓰기를 결속하고 ChangeSet.print는 현재 경로/fingerprint만 출력한다. _markdown_path가 링크 label과 destination 양쪽에 쓰여 한글 label도 URL encoding된다. Legacy 오류의 source-relative migration 경로는 target/wheel에 없다. 제품 현재 권한은 PRODUCT, SPEC-003, ARCHITECTURE, QUALITY, SECURITY에 있다.

## Scope

- 기존 init/upgrade --dry-run에 실제 before/after unified diff를 추가한다. 새 명령·승인 토큰·저장소 상태는 만들지 않는다.
- Legacy init/upgrade/doctor 오류에서 네트워크 없이도 필요한 조치를 알 수 있는 짧은 절차를 제공하고 공식 저장소의 전환 안내 위치를 명시한다. 미출시 문서 URL이 현재 공개됐다고 주장하지 않는다.
- 생성 블록에 직접 편집할 위치, 재생성 시 내부 편집 대체, 문서 이동 후 갱신과 package 제거 후 독립 사용을 짧게 안내한다.
- Unicode/공백 label은 읽을 수 있게 보존하되 Markdown 특수문자·control 문자는 inert하게 표시한다. URL destination은 기존 안전한 encoding을 유지한다.
- README와 현재 요구사항·구조·품질·보안·전환·참고 index·평가 문서를 갱신한다. 필요하면 기존 파일 안에 사용자 지침 예제와 정확한 marker를 사용한 수동 제거 절차를 넣는다.

## Non-goals

새 runtime/schema/Gate/자동 migration/제거 명령, semantic 분류·라우팅, API/SDK/LLM 서비스, 새 dependency, CI/인프라 변경, 커밋·push·PR·release·PyPI 게시, 과거 completed/accepted 본문 수정, 기존 target/공유 tmp 환경 삭제는 하지 않는다.

## Acceptance Criteria

- **AC-1:** init/upgrade dry-run은 신규/변경 예정 본문과 삭제되는 관리 블록 편집을 unified diff로 보여준다. No-op은 diff가 없음을 명시한다. Target bytes/mode/mtime/디렉터리는 불변이다. Diff는 준비된 동일 immutable operation에서 산출하고 승인/잠금으로 표현하지 않는다. 제어문자가 terminal escape로 실행되지 않도록 출력한다.
- **AC-2:** Legacy 오류는 target에 없는 상대 파일만 안내하지 않는다. init/upgrade/doctor에 일관된 자급적 수동 조치 안내와 공식 source 위치가 있으며 여전히 exit 오류 및 무변경 거부한다. 네트워크 호출을 추가하지 않는다.
- **AC-3:** 생성 블록만 읽어도 수동 지침을 쓸 위치, 내부 편집 대체, upgrade 갱신, installed package의 선택성을 이해할 수 있다. 관리 블록 밖 bytes/mode와 재실행 안정성을 보존한다.
- **AC-4:** 한글·공백 label은 읽을 수 있고 괄호/대괄호/HTML/control/개행/Markdown marker가 링크나 instruction을 주입하지 못한다. doctor는 실제 생성 링크를 검사한다.
- **AC-5:** 현재 문서의 사용 흐름·예제·수동 제거·미리보기의 민감 정보 한계가 실제 구현과 일치한다. 과거 탐색 실험은 이전 생성물의 관찰임을 명시하며 새 생성물에 성공 결과를 전용하지 않는다. source/target 책임 분리를 유지한다.
- **AC-6:** 전체 source unit/integration/distribution 및 기존 안전성 회귀와 독립 반증을 통과한다. 정확한 후보, 명령/환경, 확인된 한계와 Main 수락을 기록한다.

## Milestones

M1 제품 보수 → M2 현재 문서 갱신 → M3 통합 검증·수락. 쓰기는 순차 수행한다.

## Task Packets

### T1 — 제품 UX와 회귀

- State: completed
- Task type: implementation
- Depends on: 앞선 평가 완료
- Outcome: AC-1/2/3/4의 최소 구현과 focused tests.
- Reads: 현재 계약·이 계획, initializer.py, cli.py, AGENTS template, 제품 tests, README/전환 안내.
- Allowed writes: src/reporivet/initializer.py, src/reporivet/cli.py, src/reporivet/assets/project/root/AGENTS.md.tmpl, tests/test_reporivet.py, tests/test_audit_adoption.py, tests/test_distribution.py.
- Protected paths: 그 외 모든 경로, Main 소유 계획/문서, 기존 로컬 변경/환경과 역사.
- Execution constraints: Sonnet leaf, 재위임 금지, 단일 writer. 12분 예산, 같은 접근 2회 실패 시 Main 반환. 고유 /private/tmp fixture만 사용. 기존 Python 3.13 환경 재설치/삭제 금지. 새 코드 주석은 필요한 제약만 한국어로 작성한다.
- Verify: 지원 Python으로 focused unittest 및 가능하면 전체 dev/check. 안전성 acceptance 약화 금지.
- Stop conditions: 쓰기 범위·제품 경계·공유 인터페이스 변경 필요, 예산 초과, 동시 writer 발견.
- Result: Sonnet이 initializer/template/제품 tests 4개 파일 보수와 당시 전체 50 tests 통과를 보고했다. Main이 diff 줄 처리 및 관리 블록 suffix 보존 결함을 추가 회귀로 보수했고 최신 전체 53 tests가 통과했다. 이 결과는 최종 독립 추천이나 Main 수락을 대신하지 않는다.

### T2 — 현재 문서와 통합

- State: completed
- Task type: implementation
- Depends on: T1 writer 종료
- Outcome: AC-5, 코드와 문서 정합.
- Reads: 현재 문서, T1 실제 diff와 검사.
- Allowed writes: README.md, README.en.md, ARCHITECTURE.md, docs/PRODUCT.md, docs/QUALITY.md, docs/SECURITY.md, docs/README.md, docs/product-specs/SPEC-REPORIVET-003-agent-entrypoints.md, docs/references/entrypoint-migration.md, docs/references/agent-navigation-evaluation.md, docs/references/README.md, 이 계획. Main의 필요 보수는 T1 허용 경로 안에서만 수행한다.
- Protected paths: completed/accepted 역사, 기존 .gitignore/환경, CI/인프라, 원격.
- Execution constraints: 단일 writer, 15분 단위 bounded 점검, 같은 접근 2회 실패 시 재설계. Main이 README/통합을 맡고 나머지 열 개 문서만 Sonnet leaf에 bounded 위임했다. Leaf의 원본 쓰기 동안 Main 원본 쓰기는 중단했다. Leaf 재위임·계획 변경·최종 승인 권한 없음. 새 API/서비스 없음.
- Verify: 실제 CLI 예제, 상대 링크 검사, 전체 dev/check.
- Stop conditions: 범위 밖 발견은 기록하고 구현하지 않는다.
- Result: README 및 현재 문서 열 개 갱신. 실제 preview/사용자 지침 위치/수동 제거/privacy/legacy checkout 안내/과거 평가 provenance를 반영했다. 문서 leaf는 git diff --check 통과 뒤 쓰기 종료했다.

### T3 — 정확한 통합 후보 독립 반증

- State: completed
- Task type: verification
- Depends on: T1/T2 종료
- Outcome: AC 전체의 반례와 실제 사용자 흐름 검증.
- Reads: exact candidate, 현재 계약·문서·코드·tests.
- Allowed writes: 자기 고유 임시 fixture/검사 산출물만. 원본 수정 금지.
- Protected paths: 구현·기준·완료 기록·기존 환경 전체.
- Execution constraints: 별도 context Sonnet Independent Verifier, 재위임 금지, 10분, 같은 접근 2회 실패 시 반환. 사용자 파일/경로 주입·dry-run 출력의 전제도 의심한다.
- Verify: 지원 Python 전체 dev/check, Unicode/Markdown/control 입력, 새 문서 이동 후 갱신, no-op, 원본 bytes/mode/mtime, legacy 오류의 standalone 조치, 실제 wheel CLI.
- Stop conditions: exact target drift, 증거 부재, 요구 충돌.
- Result: 별도 Sonnet이 최종 exact candidate의 drift 0건과 확인 결함 0건을 보고하고 통과를 추천했다. Main은 아래 최종 검사·문서·한계를 검토하여 별도로 수락했다.

## Architecture Impact

기존 immutable operation의 표현과 Markdown 렌더만 보수한다. 파일 mutation 경계와 installed CLI → 일반 Markdown 의존성 방향은 바꾸지 않는다. 신규 production dependency는 없다.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| README/README.en | update | 실제 preview·편집·갱신·제거 사용 흐름 | Main | resolved |
| PRODUCT/SPEC-003/ARCHITECTURE | update | 새 관찰 가능한 UX와 기존 소유권 | Main | resolved |
| QUALITY/SECURITY | update | diff 내용 노출·제어문자·회귀 범위 | Main | resolved |
| docs README/references README/migration | update | 실제 접근·사용 예제·수동 제거 | Main | resolved |
| agent-navigation-evaluation | update | 과거 평가 대상과 새 template의 구분 | Main | resolved |
| CLAUDE/AGENTS source 계약 | none | 역할·명령·소스 권한 변화 없음 | Main | resolved |
| completed 계획/accepted ADR/과거 문서 본문 | none | 역사 보존 | Main | resolved |

## Interfaces and Dependencies

Main이 scope/권한/통합 순서를 고정했다. T1 종료 전 다른 원본 writer를 시작하지 않는다. 기존 stdlib difflib와 HTML/URL encoding을 재사용한다. 변경은 미출시 CLI의 사람이 읽는 preview와 생성 Markdown이며 별도 machine schema/승인 API를 만들지 않는다. Raw diff 출력은 파일 내용을 노출할 수 있으므로 audit의 내용 비출력 계약과 구분한다.

## Migration, Rollout, and Recovery

미출시 0.3.0.dev1 내 보수다. 기존 entrypoint는 upgrade로 관리 블록만 갱신하고 사용자 지침은 밖에 보존한다. v0.2 자동 전환 거부는 유지한다. 새 template를 받은 target도 package 부재에서 일반 Markdown을 사용할 수 있다. 수동 제거는 정확한 marker 내부만 검토하여 제거하고 혼합 파일 전체 삭제를 권하지 않는다. 문제 시 이번 변경의 국소 diff만 되돌리며 기존 PLAN-0007 변경을 reset하지 않는다. 공개 게시 권한은 없다.

## Surprises and Discoveries

- 2026-09-08 — 기존 preview는 경로/fingerprint뿐이어서 문서가 요구한 본문 검토가 불가능했다. Legacy 안내는 source에만 있는 상대 문서를 가리켰다.
- 2026-09-08 — API/SDK 작업이 아니다. 모델 중립 Markdown 제품을 유지하며 SDK skill의 모델 전환/API 추가 흐름은 적용하지 않는다.

- 2026-09-08 — Main 반례에서 초기 diff의 splitlines가 vertical tab를 실제 줄로 분리하고 본문 `---`/`+++`를 header로 오인했다. LF-only 줄 분리와 기본 unified header 처리를 사용하도록 수정하고 회귀로 검증했다.
- 2026-09-08 — 실제 upgrade 회귀에서 관리 블록 뒤 사용자 본문이 잘렸다. `_upsert`가 suffix 전체 slice 대신 한 문자 `text[span[1]]`만 취했다. `text[span[1]:]`로 보수하고 양쪽 파일의 CRLF prefix/suffix, end marker EOF, init/upgrade no-op 및 preview bytes/mode/mtime 회귀를 추가했다. 앞선 검사에서 suffix 사례가 빠졌으므로 이전 평가를 안전 보장으로 해석하지 않는다. 결함의 최초 도입 시점은 단정하지 않는다.
- 2026-09-08 — T1이 writer 종료 보고 후 한국어 주석을 추가 수정했다. Main 통합과 쓰기 경계가 겹쳐 즉시 이후 쓰기를 중지시켰고 종료 확인을 받았다. 마지막 주석 보수까지 exact candidate에 포함했다. T2는 동일 문제를 예방하도록 완료 후 추가 쓰기 금지를 명시했다.

## Decision Log

- 2026-09-08 — 사용자 승인에 따라 기존 기능의 UX만 보수한다. No-change는 확인된 문서/실행 불일치를 남겨 기각했다. 새 preview engine/승인 저장소/파일 watcher는 기존 operation+diff와 짧은 안내로 충분하므로 기각했다. 문서의 현재/과거를 자동 분류하는 안은 관찰을 authority로 오인하게 하므로 기각했다. 검증은 실제 diff/파일 보존/독립 반례이며 재검토 조건은 구체적인 사용성·안전성 실패다.

## Concrete Steps

1. 위 scope로 T1 구현과 focused tests.
2. 단일 writer 종료 뒤 Main 문서 갱신·사용 흐름 확인.
3. `PYTHON=/private/tmp/reporivet-py313-venv-EANM2w/bin/python ./dev/check`.
4. Base + nonignored hashes/modes/deletion snapshot으로 후보 고정 후 독립 검증.
5. 보수 시 새 후보 재검증, Main 수락 뒤 수동 completed 이동.

## Validation and Evidence

기준 후보: PLAN-0007 snapshot `db8ae63c3d72be0e6c6d0ae42bc4bb118767eed68ce0a6b3270031e44d9d4d16`. 이전 47 tests를 이번 검증으로 재사용하지 않았다.

- 최종 exact candidate: base `226b15af1b8ccf1d82ba410322a214f1f593cc7e` + `/var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-ux-final-xrbrb75h/files.json`, SHA-256 `45db2fb4ed048ec6d3a9bc9840471a76986c939fd10b7b2560f7cc09d322b7b2`. Nonignored 파일 hash/mode와 deletion 132개이며 이 계획의 기록만 제외했다. 임시 snapshot은 영구 보관 서비스가 아니며 fingerprint 자체도 승인이 아니다.
- 환경: macOS Darwin 25.6.0, Python 3.13.15, setuptools 84.0.0. 기존 공유 venv는 재설치·삭제하지 않았다.
- Main 최종 명령: `PYTHON=/private/tmp/reporivet-py313-venv-EANM2w/bin/python ./dev/check` — 53 tests OK, distribution build/install/uninstall, source contract drift, syntax, git diff --check 통과.
- 별도 Sonnet verifier: 첫 후보 `f1311aea00d40ebd116cb8f4ceb963886a7b15afcfb9d83c0417ff7adf1b2dbe`에서 전체 53 tests, 양쪽 prefix/suffix/EOF·mode·mtime·no-op, Unicode/control/bidi, 세 종류 legacy 거부, 실제 offline wheel CLI init/upgrade preview/legacy 안내를 확인했다. 현재 상대 링크 41개 중 누락 0건.
- 최종 후보 재검증: migration 문서 한 파일만 달라졌음을 확인하고 CLI 흐름/정확한 marker/수동 제거/소유권/privacy 정합을 재검토했다. 후보 mismatch 0건, 확인된 결함 0건, 최종 추천은 통과. 초기 내부 API summary fixture의 no-op 의심은 공개 CLI에서 재현되지 않아 철회했다.
- Main 수락: AC-1~6 및 Documentation Impact를 충족한다고 판단하여 2026-09-08 로컬 후보를 수락했다. 새 탐색 benchmark는 이번 AC 밖의 한계이며 성능 향상을 주장하지 않는다. 커밋·원격 게시·배포는 수행하지 않았다.

## Outcomes and Retrospective

실제 변경 preview, 자급적 legacy 안내, 읽을 수 있는 Unicode label, 생성 블록 수명 주기와 현재 문서 11개를 정리했다. 통합 반례에서 사용자 suffix 손실이라는 실제 파일 보존 결함을 추가로 발견·수정했다. 기존 테스트의 통과를 포괄적 안전 증거로 취급하지 않고 양쪽 사용자 본문/EOF/줄 구분 반례를 회귀로 남겼다. 계획은 Main 수락 뒤 수동으로 completed로 이동하며 target에 종료 runtime이나 상태를 설치하지 않는다.

## Follow-ups

현재 없음. 범위 밖 발견은 Main이 이 계획에 기록하고 완료 전에 처리 방식을 명시한다.
