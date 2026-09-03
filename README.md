# Reporivet

Reporivet은 코딩 에이전트를 위한 저장소 로컬의 문서 우선 운영 계약을 명시적인 설정 과정에서 만드는 Python 3.11+ 패키지입니다. 기본 온보딩 명령은 감사, 보이는 안내형 정의, 정확한 미리보기, 승인된 일회성 패키지 측 트랜잭션을 조정하는 통합 `reporivet setup` 흐름입니다. `reporivet init`은 구조만 만드는 create-if-missing 경로로 유지되고, 재개 가능한 정의 작업을 위한 하위 수준 `reporivet define`도 유지됩니다. Reporivet은 대상에 복사된 실행기, 대상 Skill, 마커, 생성된 설정 또는 런타임을 남기지 않으며 명령, 테스트, CI, 배포, 운영, 비밀 정보, Git과 증거는 프로젝트가 소유합니다.

English: [`README.en.md`](README.en.md)

## 제품 경계

```text
호스트/프로젝트 워크플로
    -> AGENTS.md
    -> docs/README.md
    -> 일치하는 활성 Markdown Plan 하나
    -> 작업 관련 권위 문서
    -> 프로젝트 소유 명령과 증거

Reporivet 패키지 (setup 또는 transition을 호출하는 동안에만)
    -> setup / init / define / audit / migrate
    -> 보이는 초안, 정확한 미리보기, 승인된 트랜잭션
```

설정은 한정된 일회성 패키지 측 트랜잭션입니다. 설치된 패키지 또는 명시적으로 선택한 로컬 소스는 사용자가 setup이나 레거시 transition을 호출하는 동안에만 사용할 수 있으며, 인계 후에는 패키지를 제거해도 일반적인 대상 작업이 줄어들지 않습니다. 대상은 자체 Markdown, Plan, 정적 runbook, Git, 프로젝트 명령과 호스트 네이티브 Agent로 계속 유용합니다. Reporivet은 프로젝트 명령을 실행하거나 Agent를 spawn/dispatch하거나 Plan을 만들지 않으며, 계속 실행되는 대상 런타임이나 진단 명령을 제공하지 않습니다.

선택 가능한 외부 사용자 범위 `/reporivet-setup` wrapper는 지침 전용(instruction-only)이며 대상 밖에 있습니다. 결정론적인 미리보기/적용 흐름만 전달하고, Reporivet을 설치·resolve·다운로드·import하지 않으며, 대상 파일을 직접 편집하지 않습니다.

## 현재 생성 트리

일회성 setup은 누락된 프로젝트 소유 경로만 만들고 기존 프로젝트 소유 또는 모호한 콘텐츠를 보존합니다.

```text
AGENTS.md
ARCHITECTURE.md

docs/
  README.md
  PRODUCT.md
  DESIGN.md                                      모든 프로젝트에 생성되는 universal 설계 문서
  FRONTEND.md                                    `web_ui=yes`가 Confirmed일 때만 생성
  QUALITY.md
  OPERATIONS.md
  RELIABILITY.md                                 `deployed_runtime=yes`가 Confirmed일 때만 생성
  SECURITY.md
  PLANS.md
  product-specs/
    index.md
    _template.md
    project-definition.draft.md                 안내형 정의 중에만 존재
  design-docs/
    index.md
    _template.md
    core-beliefs.md
  decisions/
    README.md
    _template.md
  exec-plans/
    _template.md
    active/.gitkeep
    completed/.gitkeep
    tech-debt-tracker.md
  references/
    README.md
    project-definition-protocol.md
  runbooks/
    index.md
    _template.md
    <slug>.md                                   정적 절차 문서

CLAUDE.md                                      선택 가능한 정확한 adapter: @AGENTS.md
```

초안은 안내형 정의를 재개해야 하는 동안에만 나타납니다. Setup은 필요할 때 빈 Plan 디렉터리를 만들 수 있지만 활성 Plan 파일은 절대 만들지 않습니다. 호스트/프로젝트의 Main 절차가 활성 및 완료 이력을 검색하고, 일치하는 활성 Plan 하나를 재개하거나, 없을 때 사용하지 않은 현재 연도의 가장 낮은 ID로 첫 번째 일반 Markdown Plan을 만듭니다.

## Capability별 문서

`reporivet setup`은 두 capability 질문을 visible definition에 추가합니다. `web_ui`가 정확히 **Confirmed** 상태의 `yes`이면 `docs/FRONTEND.md`를 만들고, `deployed_runtime`이 정확히 **Confirmed** 상태의 `yes`이면 `docs/RELIABILITY.md`를 만듭니다. 두 질문은 서로 독립적이므로 둘 다 확인될 수 있습니다. `no`, Proposed, Open, Sources-only, 추론값, 감사 관찰만으로는 선택 문서가 생성되지 않습니다.

`DESIGN.md`는 모든 프로젝트의 시각·상호작용·접근성 권위 문서입니다. `FRONTEND.md`는 frontend 구현과 client-side loading/error/retry 상태를 다루며 service reliability를 소유하지 않습니다. `RELIABILITY.md`는 service/runtime failure mode, SLI/SLO, observability, deployment/rollback, recovery, incident 경계를 다루는 보조 문서이고, universal 운영 권위인 `OPERATIONS.md`를 대체하거나 상위에 두지 않습니다. 두 문서 모두 프로젝트 소유자, 출처와 provenance, 적용 candidate/environment, 프로젝트 소유 검사를 기록하며 확인되지 않은 topology·telemetry·SLO·recovery 주장을 만들어내지 않습니다.

새 대상에는 Reporivet 역할 또는 절차 Skill, `.reporivet-version`, 생성된 `.claude/settings.json`, 복사된 모듈/런타임, doctor gate, registry 또는 package-resolution 지침, 명령 래퍼, scheduler, dispatcher, task store, Gate, 증거 보관소, 숨겨진 상태가 포함되지 않습니다. 기존 레거시 경로는 정확한 정식 소유권 증거가 있는 명시적인 setup 재실행 중에만 검토할 수 있으며, 이름·마커·frontmatter·위치만으로 삭제를 승인하지 않습니다.

## 정적 절차 runbook

완전하고 고유하며 사용자가 확인한 strict structured procedure record 하나만 자격을 가집니다. 정확히 다음 아홉 필드를 가져야 합니다: `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, `rollback`. 결정론적 출력은 `docs/runbooks/<slug>.md`의 일반 Markdown이며 frontmatter, executor metadata, hooks, command registration, privilege-bearing configuration이 없습니다. 불완전하거나 잘못되었거나 일반적이거나 추론되었거나 Proposed, Open, Sources-only 또는 중복인 레코드는 runbook을 만들지 않습니다. Runbook은 검토하는 프로젝트 문서이지 실행기가 아닙니다.

## 설정 시점 사용자를 위한 설치

공개 설치 안내는 setup 또는 명시적인 패키지 측 transition을 호출할 때 사용합니다.

```bash
pipx install reporivet
```

동일한 wheel에서 pip도 지원합니다.

```bash
python -m pip install reporivet
```

이는 하나의 setup 시점 패키지를 설치하는 두 가지 방법입니다. 생성된 대상에 패키지 의존성이 계속 생기는 것은 아닙니다. 완료된 PLAN-2026-0003은 source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4`와 exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4`가 기록된 격리된 pipx 및 pip 설치/사용/제거 수명주기를 통과했다고 기록합니다. 검증 산출물은 임시 자료이며 영구적이거나 다운로드 가능한 증거 보관소가 아닙니다. 게시, 서명, 릴리스, 배포, CI 수리/준비성은 여전히 확립되지 않았고 범위 밖입니다.

## 기여자 전용: 소스 체크아웃

기여자는 Python 3.11 이상 인터프리터를 명시적으로 선택해 체크아웃에서 패키지 측 명령을 직접 실행할 수 있습니다. 이는 공개 설치 경로가 아니며 setup 이후 생성된 대상이 실행해야 하는 명령도 아닙니다.

```bash
PYTHON=/absolute/path/to/python3.11-or-newer
"$PYTHON" --version

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/reporivet-pycache" \
PYTHONPATH=src \
"$PYTHON" -m reporivet --help
```

## 기본 온보딩

절대 대상 경로를 선택하고 Reporivet을 setup에 사용할 수 있는 동안 통합 setup 명령을 사용합니다.

```bash
ROOT=/absolute/path/to/target
reporivet setup --root "$ROOT"
```

`setup`은 읽기 전용 감사, 보이는 안내형 정의, 답변 재개, 정확한 미리보기와 명시적으로 승인된 적용을 조정합니다. 실제 Open 항목을 보고하고 변경 직전에 대상을 다시 검증합니다. 프로젝트 명령을 실행하거나 Plan을 만들거나 Agent를 spawn/dispatch하거나 대상 런타임 또는 package-resolution 의존성을 남기지 않습니다.

새 대상에는 Markdown 권위 문서, Plan 템플릿/디렉터리, 자격을 갖춘 레코드의 결정론적인 정적 runbook과 정확한 루트 `CLAUDE.md`(선택 시 `@AGENTS.md`와 끝 개행 하나만 포함)가 제공됩니다. 위에서 폐기한 Reporivet 대상 산출물은 제공되지 않습니다. Setup 뒤 패키지가 없는 것은 예상된 상태이며 `UNKNOWN`, blocking 또는 잔여 위험이 아닙니다.

`reporivet init --root "$ROOT"`은 구조만 만드는 비덮어쓰기 create-if-missing 경로입니다. 안내형 인터뷰를 수행하거나 Plan을 만들지 않습니다. 첫 번째 일반 Markdown Plan을 만들거나 재개하는 주체는 Reporivet이 아니라 호스트/프로젝트의 Main 절차입니다.

## 하위 수준 정의 인터페이스

유지관리자가 보이는 재개 가능한 정의 흐름을 직접 사용해야 할 때에도 `define`은 유지됩니다.

```bash
reporivet define start --root "$ROOT"
reporivet define resume --root "$ROOT"
reporivet define resume --root "$ROOT" --answers /absolute/path/to/answers.json
reporivet define status --root "$ROOT"
reporivet define finalize --root "$ROOT"
```

보이는 Markdown 초안이 유일한 재개 상태입니다. 각 주제에서 **Confirmed**, **Proposed**, **Open**, **Sources**를 분리합니다. 답변을 추론하거나 권위 문서로 다시 쓰지 않습니다. Finalize는 승인된 문서와 정적 runbook 미리보기만 만들며 대상 Skill을 생성하거나 절차를 실행하지 않습니다.

## 패키지 CLI

| 명령 | 목적 | 변경 경계 |
| --- | --- | --- |
| `reporivet setup` | 기본 통합 감사, 안내형 정의, 정확한 미리보기와 승인된 일회성 setup. | 명시적 승인과 안전한 재검증 뒤에만 쓰며 Plan을 만들거나 프로젝트 명령을 실행하지 않습니다. |
| `reporivet init` | 구조만 만드는 비덮어쓰기 create-if-missing 번들. | 기존 프로젝트 소유 콘텐츠를 보존하며 안내형 설정이나 Plan을 만들지 않습니다. |
| `reporivet define start/resume/status/finalize` | 하위 수준의 보이는 안내형 정의와 정확한 미리보기/적용. | 문서화된 초안 단계와 승인된 한정 setup 경로만 씁니다. |
| `reporivet audit` | 패키지 측 결정론적 저장소 인벤토리. | 읽기 전용이며 프로젝트 명령을 실행하지 않습니다. |
| `reporivet upgrade` | 패키지 측 유지관리 중 누락된 현재 번들 경로 유지. | 소유권을 추측하지 않고 인식된 레거시 0.2 표면을 거부합니다. |
| `reporivet migrate` | 인식된 레거시 0.2 트랜잭션의 미리보기, 적용 또는 롤백. | 파괴적 적용에는 정확한 승인과 외부 백업이 필요합니다. |

`reporivet doctor`는 폐기되었으며 계속되는 Reporivet 진단 계약은 없습니다. 대상 검증에는 프로젝트 소유 검사를 사용합니다. 설치된 `reporivet <command>`와 `PYTHONPATH=src "$PYTHON" -m reporivet <command>` 형식은 setup 시점 또는 기여자 전용 패키지 작업이며 setup 이후 대상의 요구사항이 아닙니다.

## Main / Task Owner / 구현 Sub / 검증 Sub

- **Main**은 의도, 범위, 비목표, 인수 조건, 전체 작업 트리, 통합, 결정, 후보 식별자, 증거 판단과 직렬화된 모든 Plan 편집을 소유합니다. Main은 호스트 네이티브 Agent dispatch를 사용하며 Reporivet은 Agent를 spawn/dispatch하지 않습니다.
- **Task Owner**는 모든 broad 또는 multi-part root의 기본 역할이며 `May delegate: yes`를 가집니다. Owner는 먼저 승인된 범위 안에서 finite child manifest를 반환하고, Main은 승인된 child row와 완전한 matching packet을 Plan에 직렬화한 뒤 직렬화된 Owner를 재개합니다. 재개된 serialized Task Owner만 호스트 네이티브 Agent 실행으로 선언된 dependency-ready descendant를 dispatch합니다.
- **구현 Sub**는 정확한 읽기 경로, 허용된 쓰기 경로, 보호 경로, 프로젝트 소유 검사, 인수 조건과 중지 조건을 담은 한정 Task Packet 하나를 받습니다. Narrow 또는 본질적으로 serial인 root는 direct nondelegating leaf로 남으며 ordinary leaf Agents never delegate(일반 leaf Agent는 절대 위임하지 않고) 범위를 넓히거나 자신의 작업을 승인하지 않습니다.
- **검증 Sub**는 새로운 컨텍스트에서 시작해 통합 후보를 식별하고 프로젝트 소유 검사를 실행한 뒤 인수 조건별 결과와 잔여 위험을 반환합니다. 읽기 전용 검증 leaf는 병렬로 실행할 수 있고, 위임하지 않으며, 통합 후보에 의존합니다. 별도 구현 작업이 없으면 후보를 수정하지 않습니다.

For every broad or multi-part root, this is a common host/project rule:

`T<n> (broad root Owner) -> T<n>-A/B/C/... (declared child packets, all ready leaves dispatched concurrently) -> T<n>-I (Owner-local aggregation) -> T<n>-V1/V2/... (parallel fresh verification)`

Main은 독립적인 root Owner를 동시에 dispatch합니다. 모든 child 작업은 owner, state, dependency, outcome, result와 일치하는 한정 packet을 유지합니다. 변경 가능한 형제 작업을 병렬 실행하려면 disjoint allowed-write sets, 고정된 공유 인터페이스와 separate exact-baseline worktrees가 필요합니다. Owner-local aggregation은 Main의 최종 저장소 통합과 구별되며, 새 검증은 통합 후보에 대해 read-only, nonrepairing, nondelegating으로 수행됩니다. Main만 Plan 편집을 직렬화하고 종료 Plan을 `completed/`로 수동 이동하며 어떤 명령도 완료를 결정하지 않습니다.

이것은 호스트/프로젝트 운영 계약이지 Reporivet 런타임이 아닙니다. Reporivet은 Agent spawn/dispatch 메커니즘, 프로젝트 명령 실행기, CI/배포 시스템, scheduler, dispatcher, task store, lease, lock, Gate, 증거 보관소, 숨겨진 상태 또는 자동 closure를 설치하지 않습니다.

## 명시적 레거시 transition, 백업 및 롤백

일반적인 새 setup은 레거시 산출물을 암묵적으로 제거하지 않습니다. 유지관리자는 기존 대상에 대해 setup을 명시적으로 재실행할 수 있습니다. 정리 또는 변환은 정확한 Reporivet 소유 바이트 또는 정확한 strict parse-and-rerender 일치로 증명된 경로에만 허용됩니다. 수정된 경로, 프로젝트 소유 경로, 모호하거나 알려지지 않은 경로, 안전하지 않은 경로, 심볼릭 링크와 비정규 경로는 보존하거나 거부합니다.

파괴적 동작에는 완전한 가시적 미리보기, 명시적 승인, 미리보기 지문에 결합된 대상 밖 절대 외부 백업, 즉시 preimage 재검증과 안전한 실패 뒤 트랜잭션 롤백이 필요합니다. 이후 롤백은 외부 manifest를 사용하며 성공 postimage가 변경되었으면 거부합니다. `.claude`를 재귀 삭제하지 않으며, 트랜잭션이 비어 있음을 증명한 하위 디렉터리만 제거할 수 있습니다.

역사적 `migrate --from 0.2` 인터페이스는 인식된 레거시 표면을 위한 별도의 패키지 측 transition으로 유지됩니다.

```bash
BACKUP_DIR=/absolute/path/outside/target/reporivet-backup

PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --root "$ROOT" \
  --from 0.2 \
  --preview \
  --backup-dir "$BACKUP_DIR"
```

모든 동작을 검토하고 출력된 지문만 승인합니다.

```bash
MIGRATION_PREVIEW_SHA256='paste-the-emitted-sha256'

PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --root "$ROOT" \
  --from 0.2 \
  --apply \
  --approve-preview "$MIGRATION_PREVIEW_SHA256" \
  --backup-dir "$BACKUP_DIR"
```

롤백은 정확한 외부 manifest를 받습니다.

```bash
PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --rollback /absolute/path/to/external-backup/manifest.json
```

## 프로젝트 검사

위에서 설명한 인터프리터와 외부 바이트코드 캐시를 선택한 뒤 프로젝트 소유 검사를 실행합니다.

```bash
PYTHONPATH=src "$PYTHON" -m unittest discover -s tests -v
PYTHONPATH=src "$PYTHON" -m compileall -q src tests
git diff --check
```

이 검사는 기여자/소스 체크아웃 명령입니다. 새 Verification Sub가 하나의 식별 가능한 통합 후보에 대해 적용 가능한 프로젝트 소유 검사를 실행하며, Reporivet은 이를 실행하지 않습니다. 산출물 빌드와 릴리스 검사는 환경 의존적이며 이 소스 명령으로 입증되지 않습니다. 증거 권위는 [`docs/QUALITY.md`](docs/QUALITY.md), 실행과 릴리스 경계 권위는 [`docs/OPERATIONS.md`](docs/OPERATIONS.md)입니다.

## 비목표

Reporivet은 다음이 아닙니다.

- 범용 오케스트레이션 플랫폼, scheduler, task service 또는 숨겨진 상태 저장소
- 프로젝트 빌드, 테스트, CI, 릴리스, 배포, 관찰, 백업, 복구 또는 사고 시스템의 대체물
- 복사된 다중 호스트 프롬프트, 실행기, 모델, 판정기 또는 대상 Skill 번들
- 프로젝트 사실을 추론하거나 스캐너 관찰을 승인된 요구사항으로 바꾸는 권위
- 호스트 deny 규칙이 샌드박스를 이룬다는 보장
- 직접 검증되지 않은 릴리스, 설치, 산출물, 게시 또는 배포의 증거
- 패키지 측 게시, 서명 또는 릴리스 자동화

## 현재 권위

- 지식 및 생성 표면: [`docs/README.md`](docs/README.md)
- 제품: [`docs/PRODUCT.md`](docs/PRODUCT.md)
- 아키텍처: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- 설계: [`docs/DESIGN.md`](docs/DESIGN.md)
- 품질: [`docs/QUALITY.md`](docs/QUALITY.md)
- 운영: [`docs/OPERATIONS.md`](docs/OPERATIONS.md)
- 보안: [`docs/SECURITY.md`](docs/SECURITY.md)
- Plan: [`docs/PLANS.md`](docs/PLANS.md)
- 현재 decision/specification/design: ADR-0002, SPEC-REPORIVET-004 및 DESIGN-REPORIVET-004
