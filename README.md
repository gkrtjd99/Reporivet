# Reporivet

> **Repository-native harness for long-running, agent-driven software development.**

OpenAI의 **Harness Engineering**을 주 기준으로, 저장소 자체를 에이전트가 읽고 수정하고 검증하고 정리할 수 있는 운영 환경으로 만드는 초기화 도구입니다.

이 프로젝트는 에이전트 실행 플랫폼이나 별도 오케스트레이터가 아닙니다. 초기화가 끝난 프로젝트는 저장소 안의 `AGENTS.md`, `docs/`, `dev/`, Git, 선택적 GitHub Actions만으로 운영됩니다. 특정 LLM 플러그인, Skill, Task DB, 장기 실행 컨트롤러가 필요하지 않습니다.

## 핵심 모델

```text
AGENTS.md          짧은 지도와 운영 계약
     ↓
docs/              제품·구조·설계·계획·결정의 기록 시스템
     ↓
ExecPlan           복잡한 작업을 재개할 수 있는 living document
     ↓
Main / Sub         Main이 범위·통합·완료, Sub가 bounded task 수행
     ↓
dev/               결정적인 컨텍스트·검사·검증 인터페이스
     ↓
CI + garden        불변 조건 강제와 장기 드리프트 보고
```

설계 배경은 [`docs/design-docs/DESIGN-REPORIVET-001-initializer-and-runtime.md`](docs/design-docs/DESIGN-REPORIVET-001-initializer-and-runtime.md), 생성 결과는 [`docs/product-specs/SPEC-REPORIVET-001-generated-project.md`](docs/product-specs/SPEC-REPORIVET-001-generated-project.md)에 정리되어 있습니다.

## 보장하는 것

- `AGENTS.md`는 긴 매뉴얼이 아니라 약 140줄 이하의 저장소 지도입니다.
- 제품·설계·아키텍처·품질·보안·신뢰성 문서는 초기 생성 후 프로젝트가 소유합니다.
- 복잡한 작업은 `docs/exec-plans/active/`의 한 ExecPlan과 그 안의 Task Packet으로 관리합니다.
- Main은 계획·문서 생명주기·통합·검증 대상·완료를 소유합니다.
- Sub는 한정된 읽기·쓰기 범위, acceptance, stop condition을 가진 한 작업만 수행합니다.
- `dev/harness.toml`에 커밋된 명령만 완료 게이트에서 실행합니다.
- 설정된 실행 파일이 없으면 검사를 건너뛰지 않고 실패합니다.
- 검증 로그는 `.harness/runs/`에 남고 Git에는 커밋되지 않습니다.
- 생성되는 `.gitignore`는 빌드 결과, 환경파일, 키, 자격증명, IDE 개인설정을 기본 차단합니다.
- `./dev/security-check`는 force-add 등으로 Git에 들어온 민감 경로와 고신뢰 토큰 서명을 완료 게이트에서 거부합니다.
- `garden`은 오래된 계획·문서·경로·참조를 자동 삭제하지 않고 후보로 보고합니다.
- 재초기화와 업그레이드는 프로젝트 소유 문서를 덮어쓰지 않습니다.

## 요구사항

- Python 3.11 이상
- 생성되는 shell entrypoint를 사용할 POSIX 환경
- Git 권장
- 대상 프로젝트 자체의 빌드·테스트 도구

Python 런타임 의존성은 표준 라이브러리뿐입니다.

## 설치

저장소를 복제해 editable 모드로 설치합니다.

```bash
git clone https://github.com/gkrtjd99/Reporivet.git
cd Reporivet
python3 -m pip install -e .
```

설치하지 않고 실행할 수도 있습니다.

```bash
PYTHONPATH=src python3 -m reporivet --help
```

## 초기화

새 경로도 생성할 수 있습니다.

```bash
reporivet init \
  --root /absolute/path/to/project \
  --name "My Project" \
  --summary "사용자가 이 프로젝트로 얻는 가치" \
  --project-kind service \
  --with-ci
```

지원 프로필은 `service`, `web`, `application`, `library`, `cli`, `other`입니다. 서비스·웹·애플리케이션 프로필에는 `docs/RELIABILITY.md`가 추가됩니다.

변경 예정만 확인하려면:

```bash
reporivet init --root ./my-project --name "My Project" --dry-run
```

### 기존 프로젝트

기존 소스나 빌드 파일이 감지되면 다음 계획이 자동 생성됩니다.

```text
docs/exec-plans/active/PLAN-0000-establish-repository-baseline.md
```

기존 프로젝트의 명령 감지는 초안일 뿐입니다. `dev/harness.toml`은 `configuration = "review"`로 시작하므로, 사람이 실제 실행 결과와 lockfile을 확인해 `ready`로 바꾸기 전에는 `check`와 `verify`가 성공하지 않습니다.

### 새 빈 프로젝트

새 프로젝트는 `baseline = "draft"`, `configuration = "ready"`로 시작합니다. 아직 소스가 없으면 문서·계획·구조 검사만으로 `./dev/verify`를 실행할 수 있습니다. 소스가 생기면 canonical command를 설정해야 합니다.

## 생성되는 운영 명령

```bash
./dev/bootstrap                         # lockfile 기반 설치 등
./dev/context --path src/example.py    # 필요한 문서와 active plan 라우팅
./dev/run                               # 애플리케이션 실행
./dev/check                             # 빠른 피드백
./dev/verify                            # canonical completion gate
./dev/smoke                             # 사용자 관찰 가능 경로
./dev/security-check                    # Git 추적 비밀·개인 파일 차단

./dev/docs-index                        # 문서 catalog 갱신
./dev/docs-index --check                # catalog drift 검사
./dev/docs-check                        # 문서 구조·metadata·링크 검사
./dev/plan-check                        # ExecPlan·Task Packet 검사
./dev/architecture-check                # 구조 문서와 기계적 경계 검사
./dev/garden                            # 장기 정리 후보 보고

./dev/new-plan "Account deletion" --area identity
./dev/task PLAN-2026-0001 T2
./dev/close-plan PLAN-2026-0001
```

각 wrapper는 저장소 안의 `dev/harness.py`를 호출합니다. 프로젝트별 명령은 `dev/harness.toml`이 유일한 기준입니다.

## ExecPlan 종료

1. 모든 Task와 문서 영향을 해결합니다.
2. 상태를 `verifying`으로 바꿉니다.
3. `integrated_commit: "HEAD"`로 설정합니다.
4. 후보 변경과 verifying plan을 함께 커밋해 worktree를 깨끗하게 만듭니다.
5. `./dev/close-plan PLAN-...`을 실행합니다.

`close-plan`은 현재 깨끗한 `HEAD`에서 전체 검증을 실행하고, 실제 SHA를 `integrated_commit`과 `verified_commit`에 기록한 다음 계획을 `completed/`로 이동합니다. 이 completion record는 별도 커밋으로 남깁니다.

## 문서 생명주기

| 문서 | 의미 | 관리 방식 |
|---|---|---|
| `PRODUCT.md`, `ARCHITECTURE.md` 등 | 현재 상태 | 구현과 함께 갱신 |
| `product-specs/`, `design-docs/`, `runbooks/` | 장기 공유 지식 | frontmatter와 catalog로 관리 |
| `exec-plans/active/` | 현재 실행 상태 | Main이 계속 갱신 |
| `exec-plans/completed/`, accepted ADR | 역사 기록 | 삭제 대신 supersede |
| `generated/` | 재생성 가능한 사실 | 생성기만 수정 |
| `.harness/runs/` | 원시 실행 로그 | Git ignore, 삭제 가능 |

`docs-index`는 각 index의 명시적 catalog block만 갱신하며, 사람이 작성한 설명을 보존합니다.

## 안전한 업그레이드

```bash
reporivet upgrade --root . --dry-run
reporivet upgrade --root .
reporivet doctor --root .
```

업그레이드 가능한 대상:

- `AGENTS.md`의 `reporivet` managed block
- `.gitignore`의 managed block
- `.reporivet-version`
- `dev/harness.py`와 wrapper 스크립트
- initializer가 생성한 GitHub Actions 파일
- 새 버전에서 추가된 누락 스캐폴드 파일

절대 덮어쓰지 않는 대상:

- `ARCHITECTURE.md`
- `docs/PRODUCT.md`, `DESIGN.md`, `QUALITY.md`, `SECURITY.md`, `RELIABILITY.md`
- `dev/harness.toml`
- product spec, design doc, ExecPlan, ADR, runbook
- 문서 index의 사람 작성 영역

초기화하려는 저장소에 이미 프로젝트 소유의 `dev/check`, `dev/verify` 같은 경로가 있으면 조용히 대체하지 않고 충돌을 보고하며 중단합니다.

## 저장소 위생과 비밀정보

Reporivet은 자신과 생성 대상 프로젝트의 `.gitignore`에 관리 블록을 추가해 다음 항목의 실수성 커밋을 줄입니다.

- `.env` 계열의 실제 환경값, 토큰, 개인키, 인증서·키스토어, 클라우드·Kubernetes 자격증명
- Terraform state와 로컬 deployment state
- IDE·에디터·운영체제의 개인 설정
- 로컬 DB, 원시 로그, 캐시, 가상환경, 의존성 디렉터리, 테스트·coverage·빌드 산출물

반대로 `.env.example`, `*.tfvars.example`, `.vscode/extensions.json`, 소스·migration·문서와 package-manager lockfile은 계속 추적할 수 있습니다. 의도적으로 공개 가능한 테스트 키나 fixture가 ignore 패턴과 겹치면 내용을 검토하고 근거를 남긴 뒤 명시적으로 추가해야 합니다.

`.gitignore`는 보안 경계가 아니며 이미 커밋된 비밀정보를 제거하지 않습니다. 비밀정보가 한 번이라도 Git에 들어갔다면 먼저 폐기·회전한 뒤 필요에 따라 history에서 제거해야 합니다. 취약점 제보 절차는 [`.github/SECURITY.md`](.github/SECURITY.md)를 따릅니다.

## CI

`--with-ci`를 사용하면 두 workflow가 생성됩니다.

- PR과 `main` push에서 `bootstrap`과 `verify`
- 주간 또는 수동 실행으로 `garden` 보고서 업로드

초기화 후 대상 프로젝트의 런타임 설치 단계가 추가로 필요하면 workflow를 프로젝트 요구에 맞게 보강해야 합니다. `dev/harness.toml`과 CI가 서로 다른 검증을 수행하지 않도록 유지하는 것이 핵심입니다.

## 이 저장소 테스트

```bash
python3 -m unittest discover -s tests -v
```

테스트는 초기화, 기존 프로젝트 baseline, 문서 소유권 보존, 안전한 업그레이드, 민감·개인·빌드 산출물 ignore 정책과 example·lockfile 예외, force-added 민감 경로와 고신뢰 credential signature 차단, catalog drift, 미래 ExecPlan 토큰 보존, Task Packet, strict baseline, 누락 도구 실패, dry-run, command 충돌, Git commit-bound plan closure를 검증합니다.

## 비목표

- 여러 Main을 자동 조정하는 오케스트레이터
- Task DB, lease, scheduler, journal, replay
- 무인 PR 병합 봇
- 특정 LLM 제품의 플러그인이나 Skill 설치
- 의미적 판단을 모두 스크립트로 대체하는 것

기계적으로 판정 가능한 규칙은 CI로 강제하고, 단순성·설계 타당성·문서 폐기처럼 의미 판단이 필요한 부분은 Main과 독립 Reviewer의 증거 기반 판단으로 남깁니다.
