# Reporivet

[한국어](README.md) | [English](README.en.md)

> **Repository-native harness for long-running, agent-driven software development.**

OpenAI의 [**Harness engineering: leveraging Codex in an agent-first world**](https://openai.com/ko-KR/index/harness-engineering/)를 주 기준으로, 저장소 자체를 에이전트가 읽고 수정하고 검증하고 정리할 수 있는 운영 환경으로 만드는 초기화 도구입니다.

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

### 에이전트 진입점

- `AGENTS.md`가 모든 에이전트가 따라야 할 저장소 운영 계약과 문서 진입점입니다.
- 이 source 저장소에서만 `CLAUDE.md`의 portable block을 작성하고 `./dev/agent-contract-sync`로 정확한 bytes를 `AGENTS.md` 전체에 투영합니다. 투영 파일을 직접 수정하지 않습니다. `./dev/agent-contract-sync --check`는 쓰기 없이 drift를 검사하며 block 밖 provider 설명은 복사하지 않습니다.
- 생성 대상 프로젝트에는 이 source-only sync 도구, 도구별 `CLAUDE.md`, `.claude/`, 중첩 `AGENTS.md`를 자동 추가하지 않습니다. 사용하는 도구가 별도 진입점을 요구하면 같은 `AGENTS.md`를 가리키는 얇은 연결 파일만 프로젝트가 선택적으로 둡니다.
- 생성 대상에서는 도구별 진입점이 있더라도 `AGENTS.md`를 정본으로 유지합니다.

두 수명 구조는 [`DESIGN-REPORIVET-001`](docs/design-docs/DESIGN-REPORIVET-001-initializer-and-runtime.md), 정의·adoption·evidence Gate 설계는 [`DESIGN-REPORIVET-002`](docs/design-docs/DESIGN-REPORIVET-002-project-definition-adoption-and-evidence-gate.md), 생성 결과는 [`SPEC-REPORIVET-001`](docs/product-specs/SPEC-REPORIVET-001-generated-project.md), 상세 요구사항은 [`SPEC-REPORIVET-002`](docs/product-specs/SPEC-REPORIVET-002-project-definition-adoption-and-evidence-gate.md)에 정리되어 있습니다.

## 초기화 후 생성 구조

일반적인 초기화는 애플리케이션 코드나 인프라를 추측해서 만드는 대신, 프로젝트가 스스로 운영될 수 있는 문서·명령·검증 표면을 만듭니다.

```text
project/
├── AGENTS.md                    짧은 운영 계약과 문서 라우터
├── ARCHITECTURE.md              현재 구현 구조의 정본
├── .gitignore                   프로젝트 내용 + Reporivet 관리 보안 블록
├── .reporivet-version           관리 asset 버전
├── dev/
│   ├── harness.py               package 제거 후에도 동작하는 로컬 runtime
│   ├── harness.toml             프로젝트별 명령·경로·정책의 정본
│   └── bootstrap, define, audit, code-map, context, check, verify, ...
├── docs/
│   ├── README.md                지식 지도와 읽기 순서
│   ├── PRODUCT.md               현재 제품 목적·사용자·요구·비목표
│   ├── DESIGN.md                visual-design capability일 때만 시각 디자인
│   ├── FRONTEND.md              frontend capability일 때만 프론트엔드 구현
│   ├── PRODUCT_SENSE.md         product-sense capability일 때만 제품 판단
│   ├── QUALITY.md               테스트·Verification Run·Gate 기준
│   ├── SECURITY.md              신뢰 경계·secret·명령 실행·review 기준
│   ├── PLANS.md                 ExecPlan·Task Packet·closure 정책
│   ├── RELIABILITY.md           reliability capability일 때만 생성
│   ├── product-specs/           장기 제품 동작 명세
│   ├── design-docs/             장기 설계와 trade-off 기록
│   ├── exec-plans/              active 작업과 completed 역사
│   ├── module-contracts/        근거가 있는 다중 파일 경계만 기록
│   ├── decisions/               supersede 가능한 중요 결정 기록
│   ├── runbooks/                실행·증거·rollback이 있는 운영 절차
│   ├── references/              선별된 참고자료와 정의 프로토콜
│   └── generated/code-map.md    실제·설정·confirmed path에서 파생된 비정본 지도
├── .harness/runs/               Git-ignored 로컬 검증 evidence와 raw log
└── .github/workflows/           --with-ci일 때만 생성
```

기존 구현이 감지되면 `docs/exec-plans/active/PLAN-0000-establish-repository-baseline.md`가 추가될 수 있고, 추론된 명령은 사람이 확인할 때까지 `configuration = "review"`입니다. 프로젝트 정의 draft는 `init`이나 `upgrade`가 암묵적으로 만들지 않으며, `reporivet define --root .`을 명시적으로 실행할 때만 생성됩니다.

### 왜 표면을 나누는가

| 표면 | 책임 | 분리한 이유 |
|---|---|---|
| `AGENTS.md` | 시작 순서, 범위 제한, Main/Sub 책임, 중단 조건 | 긴 지식을 preload하지 않고 정본 위치만 알려 주기 위해 |
| 현재 상태 문서 | 지금 사실인 제품·구조·설계·품질·보안 | 계획이나 과거 기록을 현재 사실로 오해하지 않게 하기 위해 |
| durable 문서 | 장기 spec, design, decision, runbook | 대화가 끊겨도 결정 근거와 계약을 Git에 남기기 위해 |
| ExecPlan | 복잡한 작업의 범위, 비목표, Task, acceptance, evidence | 별도 Task DB 없이 작업을 재개하고 범위 확장을 통제하기 위해 |
| `dev/` | 모든 agent와 CI가 공유하는 결정적 명령 | 설명이 아니라 같은 명령의 실제 결과를 evidence로 사용하기 위해 |
| `.harness/runs/` | manifest, Gate, report, check JSON, 가능한 log | 검증 대상 commit과 결과를 묶되 raw output을 durable 문서와 분리하기 위해 |

### 에이전트가 읽는 순서와 컨텍스트

문서가 디스크에 존재한다고 모델 컨텍스트에 자동으로 들어가지는 않습니다. 에이전트는 먼저 `AGENTS.md`를 읽고, 가능한 한 좁은 입력으로 다음 명령을 실행합니다.

```bash
./dev/context --path src/example.py
./dev/context --area identity
./dev/context --plan PLAN-2026-0001
```

`context`는 모든 문서 본문을 출력하지 않고 일치하는 module contract, code-map entry, durable 문서, product spec, active plan의 경로와 한 줄 summary만 반환합니다. 에이전트는 그중 현재 Task에 필요한 파일만 읽습니다. `AGENTS.md`는 문서 전체, dependency, generated output, completed plan, cache, raw log를 미리 읽는 것을 금지합니다. 작은 로컬 변경은 큰 ExecPlan을 읽거나 만들지 않고 진행할 수 있고, Sub Agent는 Task Packet에 적힌 정확한 읽기·쓰기 범위만 받습니다.

이 방식은 컨텍스트 사용을 줄이지만 OS 수준의 read sandbox는 아닙니다. metadata의 `area`와 `applies_to`를 구체적으로 유지하고 `code-map`, catalog, docs 검사를 통과시켜 라우팅 drift를 줄이며, 최종 범위 판단은 Main과 사람에게 남깁니다.

### 생성하지 않는 것

Reporivet은 프로젝트 권위를 추측하지 않으므로 기본 초기화에서 `README.md`, source/test 코드, `Dockerfile`, Docker Compose, Kubernetes manifest, Helm chart, Terraform, deployment 설정을 만들지 않습니다. `.gitignore`나 `SECURITY.md`에 cloud·Kubernetes·Terraform 관련 항목이 보이더라도 실제 인프라 설정이 아니라 credential과 local state의 실수성 커밋을 막는 일반 보안 기준입니다. 기존 인프라 파일은 audit/adoption이 inventory하고 보존할 수 있지만 새로 만들지 않습니다.

## 보장하는 것

- `AGENTS.md`는 긴 매뉴얼이 아니라 약 140줄 이하의 저장소 지도입니다.
- 제품·설계·아키텍처·품질·보안·신뢰성 문서는 초기 생성 후 프로젝트가 소유합니다.
- 복잡한 작업은 `docs/exec-plans/active/`의 한 ExecPlan과 그 안의 Task Packet으로 관리합니다.
- Main은 계획·문서 생명주기·통합·검증 대상·완료를 소유합니다.
- Sub는 한정된 읽기·쓰기 범위, acceptance, stop condition을 가진 한 작업만 수행합니다.
- 명시적 `define` 흐름은 Confirmed, Proposed, Open, Sources를 분리하고 `JRN-* -> REQ-P0-* -> AC-*` 관계를 검증합니다.
- `audit`은 결정론적 read-only inventory이며, `define --adopt`는 기존 권위를 보존하고 충돌 시 쓰기 전에 중단합니다.
- opt-in ExecPlan traceability는 제품 기준을 Task와 criterion-level evidence 및 verified commit까지 연결합니다.
- 프로젝트별 configured command는 `dev/harness.toml`에 커밋된 argv array만 실행하며, runtime의 built-in validation과 로컬 Git evidence는 고정 argv를 사용합니다. 설정된 실행 파일이 없으면 건너뛰지 않고 실패합니다.
- 한 번의 `./dev/verify`는 고정된 검사 순서와 하나의 `.harness/runs/<run>-verify/` 아래 manifest, Gate, report, check JSON, 가능한 로그를 남깁니다.
- Gate는 명시적 로컬 base/head/target과 changed path만 사용해 `PASS`, `REVIEW`, `BLOCK`, `INCONCLUSIVE`를 판정합니다.
- 생성되는 `.gitignore`는 빌드 결과, 환경파일, 키, 자격증명, IDE 개인설정을 기본 차단합니다.
- `./dev/security-check`는 force-add 등으로 Git에 들어온 민감 경로와 고신뢰 토큰 서명을 완료 게이트에서 거부합니다.
- `garden`은 오래된 계획·문서·경로·참조를 자동 삭제하지 않고 후보로 보고합니다.
- 재초기화와 업그레이드는 프로젝트 소유 문서와 기존 `dev/harness.toml` bytes를 덮어쓰지 않습니다.
- 생성된 runtime은 설치 package를 import하지 않으므로 Reporivet 제거 후에도 repository-local 명령이 동작합니다.

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

지원 프로필은 `service`, `web`, `application`, `library`, `cli`, `other`입니다. 기본적으로 `web`은 visual-design과 frontend 문서를, `service`·`web`·`application`은 reliability를 활성화하며 product-sense는 opt-in입니다. 선택된 document capability에 따라 시각 전용 `DESIGN.md`, `FRONTEND.md`, `PRODUCT_SENSE.md`, `RELIABILITY.md`를 생성하며, 기존 프로젝트 소유 문서는 upgrade 중에도 보존합니다.

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

## 프로젝트 정의와 기존 저장소 adoption

프로젝트 정의는 `init`이나 `upgrade`가 암묵적으로 시작하지 않습니다. 사람이 명시적으로 시작하고 repository-owned draft를 편집합니다.

```bash
reporivet define --root .
./dev/define status
./dev/define validate
./dev/define finalize
```

14개 section은 Confirmed, Proposed, Open, Sources를 분리합니다. `finalize`는 blocking Open, placeholder, contradiction, 잘못된 stable ID/link를 거부하고, 검증된 evidence에서 final product spec과 첫 vertical-slice ExecPlan 하나를 transactionally 생성합니다. 자세한 절차는 [Project Definition Protocol](docs/references/project-definition-protocol.md)을 따릅니다.

기존 저장소는 먼저 쓰기 없는 audit으로 authority와 명령 후보를 확인한 뒤 adoption합니다.

```bash
reporivet audit --root .
reporivet define --root . --adopt
./dev/audit
```

Adoption은 기존 README, `AGENTS.md`의 사용자 영역, architecture, CI, catalog, configuration을 보존합니다. inferred command는 사람이 확인하기 전까지 `configuration = "review"`입니다.

## 생성되는 운영 명령

```bash
./dev/bootstrap                         # lockfile 기반 설치 등
./dev/define status                     # definition progress와 다음 section
./dev/define validate                   # evidence 구조와 trace link 검증
./dev/define finalize                   # final spec과 첫 ExecPlan 생성
./dev/audit                             # 쓰기·명령 실행 없는 repository inventory
./dev/code-map                          # evidence-backed code map 갱신
./dev/context --path src/example.py    # 필요한 문서·contract·active plan 라우팅
./dev/run                               # 애플리케이션 실행
./dev/check                             # 빠른 피드백
./dev/verify                            # 유일한 canonical completion gate와 evidence run
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

`close-plan`은 plan의 명시적 base와 현재 깨끗한 `HEAD`를 대상으로 canonical Verification Run을 정확히 한 번 실행합니다. `PASS`는 바로 닫고, `REVIEW`는 사람이 직접 작성한 `--accept-review "..."` 사유가 있어야 닫습니다. `BLOCK`과 `INCONCLUSIVE`는 override할 수 없습니다. 성공 시 run ID, finalized manifest SHA-256, Gate verdict, verified SHA, criterion evidence와 해당 REVIEW 사유를 기록하고 계획을 `completed/`로 이동합니다. 이 역사 기록은 별도 커밋으로 남기되 두 번째 `./dev/verify`는 실행하지 않습니다.

## 문서 생명주기

| 문서 | 의미 | 관리 방식 |
|---|---|---|
| `PRODUCT.md`, `ARCHITECTURE.md` 등 | 현재 상태 | 구현과 함께 갱신 |
| `product-specs/`, `design-docs/`, `runbooks/` | 장기 공유 지식 | frontmatter와 catalog로 관리 |
| `exec-plans/active/` | 현재 실행 상태 | Main이 계속 갱신 |
| `exec-plans/completed/`, accepted ADR | 역사 기록 | 삭제 대신 supersede |
| `generated/` | 재생성 가능한 사실 | 생성기만 수정 |
| `.harness/runs/` | local Verification Run evidence와 원시 로그 | Git ignore, 공유 전 검토, 삭제 가능 |

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

- PR과 `main` push에서 explicit base/head/target을 bind하고 `bootstrap` 다음 `verify`를 정확히 한 번 실행
- success/failure와 무관하게 report를 step summary에 추가하고 `.harness/runs/` evidence 업로드
- 주간 또는 수동 실행으로 `garden` 보고서 업로드

Workflow action은 immutable SHA로 고정되고 `contents: read`, full checkout history를 사용합니다. push base가 all-zero이면 parent를 추론하지 않고 unavailable로 유지합니다. 초기화 후 대상 프로젝트의 런타임 설치 단계가 추가로 필요하면 workflow를 프로젝트 요구에 맞게 보강하되, `dev/harness.toml`과 CI가 서로 다른 검증을 수행하지 않도록 유지해야 합니다.

## 이 저장소 테스트

```bash
python3 -m unittest discover -s tests -v
```

테스트는 definition/resume/finalization, deterministic audit/adoption, traceability, conditional contract/code map/context, Verification Run status/artifact, Gate/closure, initialization/upgrade ownership, CI structure, security, wheel inventory, isolated install, package uninstall 후 repository-local 동작을 검증합니다.

현재 `0.2.0` 목표는 로컬 release-ready boundary입니다. network 없이 wheel을 build·inspect·install·uninstall하고 generated project를 검증하지만 PyPI 게시나 GitHub Release 생성은 하지 않습니다.

## 비목표

- 여러 Main을 자동 조정하는 오케스트레이터
- Task DB, lease, scheduler, journal, replay, daemon, plugin, MCP bridge
- 무인 PR 생성·병합, package publication, deployment 같은 외부 write
- 특정 LLM 제품의 Skill/runtime target bundle이나 model judge
- 의미적 product 판단, conflict resolution, REVIEW acceptance를 스크립트가 대신하는 것
- 이전 저장소의 backup, archive, deprecation write, 삭제 또는 다른 운영

기계적으로 판정 가능한 규칙은 CI로 강제하고, 단순성·설계 타당성·문서 폐기처럼 의미 판단이 필요한 부분은 Main과 독립 Reviewer의 증거 기반 판단으로 남깁니다.
