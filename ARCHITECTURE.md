---
id: ARCHITECTURE
kind: architecture
status: active
area: repository
summary: Installed CLI와 runtime 없는 Markdown target의 경계
---

# Architecture

## 제품 경계

```text
installed reporivet CLI
    → 제한된 read-only 경로 관찰
    → AGENTS / 선택적 CLAUDE 관리 블록의 안전한 갱신

target agent
    → 일반 Markdown 탐색
    → 프로젝트의 기존 명세·코드·검사 도구
```

Target에는 Reporivet runtime이나 설정을 설치하지 않는다. agent의 일상 작업이 installed package를 호출해야 하는 역방향 의존성도 없다. 모델·원격 서비스·task database를 추가하지 않는다.

## Source map

| 경로 | 책임 |
|---|---|
| `src/reporivet/cli.py` | init/audit/upgrade/doctor의 인자와 exit code |
| `src/reporivet/initializer.py` | inventory, marker 소유권, preimage/postimage, 생성·갱신·점검 |
| `src/reporivet/assets/project/root/AGENTS.md.tmpl` | 짧은 비권위적 탐색 안내 |
| `tests/` | 제품의 기계적 안전성·생성·배포 회귀 |
| `tests/fixtures/navigation/` | 실제 agent 탐색 대조용 서로 다른 문서 구조 |
| `dev/check` | 이 소스 저장소의 검사 실행; target에 배포하지 않음 |
| `dev/agent_contract_sync.py` | 이 소스의 CLAUDE portable block을 AGENTS에 투영 |
| `docs/` | 이 제품의 현재 요구사항·결정·실험·작업 역사 |

## 읽기와 쓰기

관찰은 깊이·개수가 제한된 실제 경로 목록이며 문서의 의미를 추론하거나 project command를 실행하지 않는다. 파일 이름이 명령이나 Markdown 문법으로 해석되지 않도록 렌더링한다. 관리 블록 밖 프로젝트 지침이 의미적 경로와 소유권을 유지한다. 생성된 안내도 경로 관찰을 authority나 자동 routing으로 바꾸지 않는다.

`init`/`upgrade`의 dry-run은 쓰기 전에 준비한 동일 immutable operation의 before/after bytes로 실제 unified diff를 만든다. 변경이 없으면 명시적인 no-op을 출력한다. 이 diff는 terminal에서 사람이 검토하는 escaped preview일 뿐 그대로 적용하는 patch가 아니다. audit은 반대로 파일 내용을 출력하지 않는 경로 관찰이므로, preview가 instruction 본문을 노출할 수 있는 것과 구분한다. fingerprint는 operation을 식별하는 보조 정보이며 승인 토큰·잠금·다음 실행 결과의 보장이 아니다.

Mutation은 쓰기 대상의 원래 bytes/type/mode/hash를 고정하고 그 이미지로부터 결과를 렌더링한다. 적용 직전 모든 preimage와 개별 write의 preimage를 확인한다. 새 파일은 기존 파일을 덮어쓰지 않는 방식으로 만들고, 기존 파일은 완성된 임시 파일로 교체한다. 중간 실패 시 일치하는 자기 postimage만 복구하고 concurrent 변경은 보존·보고한다. 이것은 OS 수준의 완전한 동시성 격리가 아니다.

## 제품 검증과 source 검사

`doctor`의 기계적 결과와 실제 agent 탐색 품질을 구분한다. source의 `./dev/check`와 CI는 unit/integration/distribution 검사를 실행할 뿐 target의 작업을 승인하지 않는다. [탐색 평가](docs/references/agent-navigation-evaluation.md)는 별도의 새 agent 세션과 통제된 fixture를 사용하며 실행 engine을 제품에 포함하지 않는다.

## 기존 버전과 역사

v0.2의 copied runtime·고정 schema·Gate·closure 계약은 [ADR-0002](docs/decisions/ADR-0002-entrypoint-only-boundary.md)로 supersede한다. 이전 target은 자동 migration하지 않는다. Legacy runtime·marker·CI 의존성의 제거는 target maintainer가 별도 소유하고, 기존 문서·명령·CI 영향과 compatibility를 검토한 뒤 수행한다. [전환 절차](docs/references/entrypoint-migration.md)는 source repository root에서 읽는 안내와 checkout 안에서 실행할 수 있는 migration 문서를 구분한다. 기존 release/tag/assets와 completed 계획은 그대로 보존한다.

## Source-only contract projection

이 소스에서는 `CLAUDE.md`의 `reporivet:portable:start/end` 블록을 작성하고 `./dev/agent-contract-sync`로 AGENTS에 투영한다. `--check`는 bytes drift를 읽기 전용으로 검사한다. 이 helper는 target에 배포되지 않으며 선택적 target CLAUDE는 AGENTS를 가리키는 얇은 연결일 뿐이다. 일반 target에 source의 문서 체계나 agent 역할을 강제하지 않는다.
