---
id: PLAN-2026-0015
kind: exec-plan
status: completed
owner: main
area: file-safety
created: 2026-11-26
updated: 2026-11-26
base_commit: "718021503e161931f0b9bda3155c9da8aed1c314"
---

# 신규 진입점 파일의 권한 보호

## Purpose / Big Picture

새 AGENTS/CLAUDE 파일이 호출자의 제한적인 파일 생성 권한을 우회하지 않게 하고, 기존 파일 보존 및 안전한 쓰기 계약을 유지한다.

## Current Contract

- Authority: base revision의 `docs/PRODUCT.md`, `docs/product-specs/SPEC-REPORIVET-003-agent-entrypoints.md`, `docs/SECURITY.md`, `docs/QUALITY.md`.
- Scope: 신규 진입점의 mode 및 이에 직접 필요한 planning, 쓰기, rollback, 회귀 검사와 문서. 대상은 `src/reporivet/initializer.py`, 관련 `tests/`, 현재 문서와 이 계획이다.
- Non-goals: target의 다른 파일, 실행 기능, 별도 runtime, CI 설정, 무관한 소스 운영 계약 변경.
- AC-1: 신규 파일은 호출자의 제한적인 생성 권한을 무시해 접근을 넓히지 않는다. AGENTS와 선택적 CLAUDE 모두 검증한다.
- AC-2: 기존 파일의 bytes/mode 보존, preview의 대상 무쓰기, immutable operation과 fingerprint 의미, 충돌·rollback 보호를 유지한다.
- AC-3: 적합한 자동 검사와 exact candidate의 독립 검토를 수행하고 실행 환경 및 미검증을 기록한다.
- Constraints: 프로세스 전역 umask의 일시적 완화로 다른 스레드의 파일 생성을 노출하지 않는다. 대상 프로젝트의 명령이나 원격 콘텐츠를 실행하지 않는다. 기존 공개 release와 무관한 파일은 수정하지 않는다.

## Progress

- [x] 기존 권한 결함과 보안·계획 계약 확인.
- [x] 구현과 회귀 검사.
- [x] 독립 검토와 검증 결과 기록.
- [x] 문서 영향 및 후속 작업 정리.

## Context and Orientation

`initializer.py`의 신규 파일 postimage는 기존에 0644로 고정되며 `_atomic_write`에서 적용된다. postimage mode는 fingerprint와 자기 변경만 되돌리는 rollback 판정에도 사용된다. Preview는 target에 쓰지 않는다.

## Approach and Key Changes

신규 파일 생성 정책은 OS가 0666에 권한 정책을 적용하는 것으로 계획에 표시하고, 실제 mode는 staging 중 확인해 게시 성공 후 rollback postimage로 기록한다. 기존 파일의 mode는 보존한다. 모호한 게시 결과와 사용자 변경은 보수적으로 보존한다. 재귀 삭제를 피하고 fd 기반 staging과 제한적인 정리를 사용한다.

## Architecture Impact

기존 파일 mutation 내부 구현에 한정한다. 새 dependency나 target runtime은 추가하지 않는다.

## Documentation Impact

`README.md`, `README.en.md`, `ARCHITECTURE.md`, `docs/SECURITY.md`에 권한 정책, preview fingerprint 및 ACL·경쟁 한계를 반영했다. 기존 제품 요구의 추가 변경은 없다.

## Migration, Rollout, and Recovery

기존 파일 mode는 변경하지 않는다. 과거에 생성된 파일의 권한은 자동 변경하지 않는다. 문제 시 해당 변경을 되돌리며 사용자 target의 파일은 건드리지 않는다.

## Surprises and Discoveries

- 2026-11-26: 현재 `python3` 3.15.2 환경에는 setuptools가 없어 배포 검사가 기존 상태에서도 실패한다.
- 2026-11-26: 독립 검토에서 동시 생성 파일 삭제, 임시 symlink의 권한 변경 및 교체된 디렉터리의 재귀 삭제 위험을 발견해 각각 수정했다. 공유 쓰기 가능한 상위 디렉터리에서 staging 직후 최초 identity 확인 전의 좁은 rename race는 남는다. `docs/SECURITY.md`에 명시했다.

## Decision Log

- 2026-11-26: 범위를 사용자 요청인 신규 파일 권한과 그 검증으로 한정한다.
- 2026-11-26: 프로세스 전체 umask 변경을 피하고 실제 생성 정책을 OS에 위임한다. 사유 staging 또는 owner-read를 보장할 수 없을 때는 실패한다. 불명확한 게시 결과는 파일을 삭제하지 않는다.

## Validation and Evidence

- AC-1: PASS — umask 002/022/077, 제한적 umask 400/777, 신규 두 파일과 preview 무쓰기를 테스트했다. 기본 ACL은 별도 OS·파일시스템 검증이 필요하다.
- AC-2: PASS — 기존 mode, rollback, 동시 chmod/생성, staging 경로 교체 및 preview 회귀를 실행했다. OS 수준 완전 격리는 제공하지 않으며 위 경쟁 한계가 남는다.
- AC-3: PASS — 별도 문맥에서 구현과 테스트를 반증 검토했다. macOS에서 아래 전체 검사가 모두 exit 0; Linux/Windows와 ACL 환경은 검증하지 않았다.
- Base: `718021503e161931f0b9bda3155c9da8aed1c314`. Candidate SHA-256: `src/reporivet/initializer.py` 33905f61d5f07cccbf17b8dec38b24777185b9d16c04c1b304a4c1250e48baf8; `tests/test_reporivet.py` c2bc85cc9d6c8f2b084be625af59259ebe1f972548478bd99a20f92197118849; `tests/test_audit_adoption.py` d30a78c78d92ba5c0f49bf42bb72101b7f7ee004076bb9c72358ce461a594118; `README.md` bf2e5363ad9ac0168aa3d4248a81af598da61f5d524e82ebd67f062c452acb1d; `README.en.md` 9312a11bf0ffe11aea5e0620c7606fd0ec70888fed3fb58fd3989df4e3dae7e2; `ARCHITECTURE.md` e44f128e8f4b99323e40223e0a33c60417136070015acf472c4ab65de16c8db2; `docs/SECURITY.md` 3af894fc1c47ce835c5c078b27147923df6cbb81201aa250ccb6e1f9d3a653c6. 이 계획은 증거 기록 자체로 별도 해시에서 제외했다. 대상 삭제 없음; 변경 파일 mode 0644.
- `PYTHON=<unique-venv>/bin/python PYTHONDONTWRITEBYTECODE=1 ./dev/check`: Python 3.15.2, setuptools 84.2.1, 64 tests / 6.635s / OK, exit 0; Python 3.13.18, 동일 setuptools, 64 tests / 5.700s / OK, exit 0. 각 격리 venv는 `/private/var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-check-iURr7P/` 아래에서 준비했다.
- 전체 검사 및 독립 검토 이후 구현 파일의 staging 설명 주석과 보안 문서의 한계 설명만 수정했다. 실행 코드와 검사 파일은 바뀌지 않았다.
- 앞선 Python 3.15 전체 검사는 `PYTHONPYCACHEPREFIX` 강제 시 제거 후 namespace가 남아 배포 테스트가 실패했다. 그 설정 없이 배포 테스트 및 위 전체 검사가 통과했다. 기본 시스템 Python의 setuptools 부재는 변경하지 않았다.

## Outcomes and Retrospective

새 파일은 일반 umask를 따르고, 기존 파일 mode는 바꾸지 않는다. 독립 검토에서 찾은 경쟁 경로를 보수적으로 처리했으며, 완전 격리와 ACL 이식성은 주장하지 않는다. 검토 및 관련 검사는 통과했다.

## Follow-ups

기존 기술 부채 범위의 Python/OS CI matrix 및 실제 환경 ACL 검증을 별도 작업으로 고려한다.
