---
id: PLAN-2026-0019
kind: exec-plan
status: completed
owner: main
area: compatibility-and-ci
created: 2026-11-27
updated: 2026-11-27
base_commit: "718021503e161931f0b9bda3155c9da8aed1c314"
---

# 에이전트 호환성과 지원 환경 CI 확대

## Current Contract

- 근거: 사용자 요청, `docs/PRODUCT.md`, `docs/QUALITY.md`, `docs/SECURITY.md`, `docs/PLANS.md`, `pyproject.toml`, 현재 source 및 공식 에이전트 문서. 기존 미커밋 변경을 보호한다.
- 범위: Codex·Claude Code·Copilot의 진입점 사용을 제품 버전·실행 표면별로 조사하고 실제 검증과 공식 문서를 구분해 기록한다. Python 지원 선언 및 POSIX 의존성과 일치하는 CI matrix를 구성한다. target에 설정·runtime·CI를 생성하거나 배포하지 않는다.
- 수락 기준: 테스트한 환경과 미검증·설정별 차이를 정직하게 기록하고 링크를 유효하게 유지한다. CI의 검증 대상 HEAD 결속, action SHA pin, 최소 권한, 실제 `dev/check` 및 실패 보고를 유지한다. 설치 가능한 Python 버전을 불필요하게 제한하지 않고 OS 지원을 근거 없이 확장하지 않는다.
- 보호: 이전 작업 트리·타 계획·사용자 설정·인증/비밀·release 보존. 외부 게시/원격 CI 실행은 하지 않는다. 실제 probe는 고유 임시 경로, 최소 권한, 민감 데이터 없는 fixture만 사용한다.
- 검증: 가능한 로컬 interpreter로 실제 전체 검사, workflow 정적 검증과 별도 context 독립 검토. 원격 runner와 미설치 에이전트는 실행하지 않은 것을 PASS로 바꾸지 않는다.

## Progress

- [x] 시작 트리와 현 Python·CI 선언 확인.
- [x] 실행 환경 조사·호환성 근거 기록 및 CI 확장.
- [x] 정확한 후보의 독립 검토·검사·한계 기록.

## Validation and Evidence

- **PASS — 호환성 조사:** 공식 문서와 Codex CLI 0.172.0, Claude Code 2.1.332의 격리된 fresh-session 실측을 [호환성 기록](../../references/agent-compatibility.md)에 구분했다. `--claude`의 일반 텍스트 포인터 및 Claude 하위 지침의 관찰된 조건 차이를 기록했다. Copilot은 공식 문서 확인만 했고 실행하지 않았다.
- **PASS — CI 구성과 검토:** Linux·macOS × Python 3.11–3.15의 10개 조합을 설정했다. SHA-pinned actions, `contents: read`, 명시적 HEAD 확인, 선택된 Python으로 고정 build tools 설치와 `dev/check`를 유지한다. `actionlint .github/workflows/ci.yml`, `git diff --check`, `./dev/agent-contract-sync --check` exit 0. 독립 검토가 workflow·호환성 문서와 trace를 대조했다.
- **PASS — 로컬 검사:** macOS에서 격리 venv로 `PYTHON=<venv>/bin/python PYTHONDONTWRITEBYTECODE=1 ./dev/check`: Python 3.12.16 67 tests/5.758s/OK, 3.13.18 67/7.476s/OK, 3.15.2 67/7.626s/OK. 일부 문서·CI 변경 전 실행이며 해당 변경은 제품 소스·테스트 로직을 바꾸지 않았다. Python 3.15에서는 metadata 변경 뒤 배포 테스트도 통과했다.
- **PASS — Linux 독립 검사:** Docker official Python 이미지, Linux aarch64 및 UID/GID 65534에서 작업 트리를 read-only mount해 고유 `/tmp`에 복사하고 setuptools 84.2.1·wheel 0.48.0을 설치한 뒤 `PYTHON=<venv>/bin/python PYTHONDONTWRITEBYTECODE=1 ./dev/check`를 실행했다. Python 3.11.18/3.12.16/3.13.18/3.14.10/3.15.2 각각 67 tests 및 Docker exit 0. Linux amd64 에뮬레이션에서도 비root Python 3.13.18 67 tests/21.329s/Docker exit 0. 주요 제품·테스트·메타데이터·README·CI·호환성 문서 12개 파일 hash는 최종 작업 트리와 일치하나, 모든 파일의 fingerprint를 의미하지는 않는다. 원시 로그는 고유 임시 경로 `reporivet-linux-final2-{FihtOU,A7kvgO,xk7y3d,2WTRMf,BEkegK,vfEnnU}/result.log`에 있다. 앞선 zsh wrapper의 읽기 전용 변수 오류 6회는 종료코드 미확인으로 PASS에 포함하지 않았다.
- **UNPROVEN:** GitHub-hosted Actions의 실제 10개 job, macOS Python 3.11/3.14, Windows 및 Copilot CLI 실제 동작. 로컬 컨테이너 검사는 호스팅 runner 실행을 대체하지 않는다. Windows는 현재 POSIX 파일 연산 때문에 지원하지 않는다. 3.15 이후 버전은 `requires-python >=3.11`이 허용하지만 이 matrix에서 검증하지 않았다.
- Candidate base `718021503e161931f0b9bda3155c9da8aed1c314` 및 [PLAN-0018](../completed/PLAN-2026-0018-observed-path-coverage.md)의 기존 미커밋 후보; 그 계획 SHA-256 `8d9cc0eb337111cdcfd2d253108ab86d09000a84797d344266a6c68b983c729e`. 아래는 이번 작업의 변경 파일로 전부 mode `0644`; 이 계획 자체는 증거 기록이므로 목록에서 제외한다.
  - `.github/workflows/ci.yml`: `e2237db1f8c4ba89ee4783913317f2ae8ce795bddb65ae8d469ec055bf4912bd`
  - `pyproject.toml`: `ec8686260a2f88f586c86437324a4d99ded2266180d8e88177c3296ecf2fc22d`
  - `README.md`: `0c0d21d27d4abb556f3d6b516e083c13d602b88787c618658abfbe3b4617e94c`
  - `README.en.md`: `5afb046802c113fb9fe8abb70c9b55179f524902cc93a11fbff87e8657ceafca`
  - `docs/README.md`: `b221e70c5f5477cba2abdd5cc833efa301c8ce3652f7dda366b1ebe84ce694c6`
  - `docs/references/agent-compatibility.md`: `a24505d9bc0869994f58b605c1ba6b11771a9c372369cfe55d7c8b0626aa89f2`
- 이번 작업의 삭제 경로는 없다. 이전 미커밋 파일과 계획 이동의 삭제 목록은 PLAN-0018 및 그가 참조하는 이전 계획에 기록돼 있다. 배포·push·원격 CI 실행은 수행하지 않았다.
