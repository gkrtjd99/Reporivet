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

CLAUDE.md                                      정확한 `@AGENTS.md` adapter (없을 때 생성)
```

Visible draft는 안내형 정의를 재개하는 동안의 프로젝트 소유 resume 상태입니다. 승인된 setup 뒤에도 resume 또는 provenance 필요가 없을 때까지 프로젝트가 의도적으로 제거할 수 있으며, setup이 이를 자동으로 숨기거나 제거하지는 않습니다. Setup은 필요할 때 빈 Plan 디렉터리를 만들 수 있지만 활성 Plan 파일은 절대 만들지 않습니다. 호스트/프로젝트의 Main 절차가 활성 및 완료 이력을 검색하고, 일치하는 활성 Plan 하나를 재개하거나, 없을 때 사용하지 않은 현재 연도의 가장 낮은 ID로 첫 번째 일반 Markdown Plan을 만듭니다.

## Capability별 문서

`reporivet setup`은 두 capability 질문을 visible definition에 추가합니다. `web_ui`가 정확히 **Confirmed** 상태의 `yes`이면 `docs/FRONTEND.md`를 만들고, `deployed_runtime`이 정확히 **Confirmed** 상태의 `yes`이면 `docs/RELIABILITY.md`를 만듭니다. 두 질문은 서로 독립적이므로 둘 다 확인될 수 있습니다. `no`, Proposed, Open, Sources-only, 추론값, 감사 관찰만으로는 선택 문서가 생성되지 않습니다.

`DESIGN.md`는 모든 프로젝트의 시각·상호작용·접근성 권위 문서입니다. `FRONTEND.md`는 frontend 구현과 client-side loading/error/retry 상태를 다루며 service reliability를 소유하지 않습니다. `RELIABILITY.md`는 service/runtime failure mode, SLI/SLO, observability, deployment/rollback, recovery, incident 경계를 다루는 보조 문서이고, universal 운영 권위인 `OPERATIONS.md`를 대체하거나 상위에 두지 않습니다. 두 문서 모두 프로젝트 소유자, 출처와 provenance, 적용 candidate/environment, 프로젝트 소유 검사를 기록하며 확인되지 않은 topology·telemetry·SLO·recovery 주장을 만들어내지 않습니다.

새 대상에는 Reporivet 역할 또는 절차 Skill, `.reporivet-version`, 생성된 `.claude/settings.json`, 복사된 모듈/런타임, doctor gate, registry 또는 package-resolution 지침, 명령 래퍼, scheduler, dispatcher, task store, Gate, 증거 보관소, 숨겨진 상태가 포함되지 않습니다. 기존 레거시 경로는 정확한 정식 소유권 증거가 있는 명시적인 setup 재실행 중에만 검토할 수 있으며, 이름·마커·frontmatter·위치만으로 삭제를 승인하지 않습니다.

## Reporivet setup과 Harness 설치의 구분

위 tree가 현재 Reporivet setup의 경계입니다. 호스트 측 Harness 또는 plugin 설치는 별도 작업이며 `.claude/skills/**`, `.claude/settings.json`, `.worktreeinclude`, `docs/templates/**`, `rules/**`, editor/lint 설정 같은 호스트 파일을 복사할 수 있습니다. 현재 `reporivet setup`은 이런 경로를 만들지 않으며, 해당 경로가 존재한다는 사실만으로 setup이 만들었다고 볼 수 없습니다. 변경하거나 제거하기 전에 소유권을 확인해야 합니다. Reporivet은 대상에 계속 사용하는 Harness/plugin runtime을 설치하거나 주입하지 않습니다. 위에서 설명한 외부 `/reporivet-setup` wrapper도 지침만 전달하며 그런 설치를 수행하지 않습니다.

## 정적 절차 runbook

완전하고 고유하며 사용자가 확인한 strict structured procedure record 하나만 자격을 가집니다. 정확히 다음 아홉 필드를 가져야 합니다: `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, `rollback`. 결정론적 출력은 `docs/runbooks/<slug>.md`의 일반 Markdown이며 frontmatter, executor metadata, hooks, command registration, privilege-bearing configuration이 없습니다. 불완전하거나 잘못되었거나 일반적이거나 추론되었거나 Proposed, Open, Sources-only 또는 중복인 레코드는 runbook을 만들지 않습니다. Runbook은 검토하는 프로젝트 문서이지 실행기가 아닙니다.

## 설정 시점 사용자를 위한 설치

공개 설치 안내는 setup 또는 명시적인 패키지 측 transition을 호출할 때만 필요합니다. Setup이 끝나면 대상 프로젝트는 패키지 없이도 자체 Markdown, Plan, runbook, Git, 프로젝트 명령과 호스트 네이티브 Agent로 계속 동작합니다.

```bash
pipx install reporivet
```

동일한 wheel에서 pip도 지원합니다.

```bash
python -m pip install reporivet
```

이는 하나의 setup 시점 패키지를 설치하는 두 가지 방법입니다. 생성된 대상에 Reporivet 패키지 의존성이 계속 생기는 것은 아닙니다. 완료된 PLAN-2026-0003은 source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4`와 exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4`가 기록된 격리된 pipx 및 pip 설치/사용/제거 수명주기를 통과했다고 기록합니다. 검증 산출물은 임시 자료이며 영구적이거나 다운로드 가능한 증거 보관소가 아닙니다. 게시, 서명, 릴리스, 배포, CI 수리/준비성은 여전히 확립되지 않았고 범위 밖입니다. 현재 공개 인덱스 상태도 이 저장소의 품질 근거로 확립되어 있지 않습니다.

### 소스에서 wheel을 빌드해 다른 프로젝트에 사용하기

소스 체크아웃에서 wheel을 만들려면 Python 3.11 이상과 `pyproject.toml`에 선언된 `setuptools>=77` build backend가 필요합니다. 아래 명령은 Reporivet 소스 루트에서 실행하며, 네트워크 게시나 릴리스를 수행하지 않고 임시 디렉터리에 wheel을 만듭니다.

```bash
PYTHON=/absolute/path/to/python3.11-or-newer
"$PYTHON" --version

WHEEL_DIR="$(mktemp -d)"
"$PYTHON" -m pip wheel . \
  --no-build-isolation \
  --no-deps \
  --no-index \
  --wheel-dir "$WHEEL_DIR"
```

생성된 local wheel을 setup 시점 환경에 설치한 뒤 대상 프로젝트를 지정합니다. `pipx` 또는 pip 중 하나만 선택하면 됩니다.

```bash
"$PYTHON" -m pip install "$WHEEL_DIR"/reporivet-*.whl
# 또는
pipx install "$WHEEL_DIR"/reporivet-*.whl

ROOT=/absolute/path/to/target
```

성공적인 wheel 빌드는 설치, 게시, 서명, 릴리스 또는 배포를 증명하지 않습니다. 이 수명주기의 프로젝트 소유 검사와 제한은 [`docs/QUALITY.md`](docs/QUALITY.md)와 [`docs/OPERATIONS.md`](docs/OPERATIONS.md)를 따릅니다.

wheel을 설치하지 않고 선택한 source checkout을 의도적으로 직접 사용하려면 해당 checkout에서 패키지 측 명령을 실행합니다.

```bash
REPORIVET_CHECKOUT=/absolute/path/to/Reporivet
ROOT=/absolute/path/to/target
cd "$REPORIVET_CHECKOUT"

PYTHONPATH=src "$PYTHON" -m reporivet setup \
  --root "$ROOT"
```

출력된 `preview.fingerprint`를 `SETUP_PREVIEW_SHA256`에 복사한 뒤에만 같은 source-checkout 형식에 `--apply --approve-preview "$SETUP_PREVIEW_SHA256"`를 붙여 사용합니다. 이것도 setup 시점의 패키지 작업이며 checkout이나 runtime을 대상에 복사하지 않습니다.

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

## 기본 온보딩: 다른 프로젝트에 적용

`setup`은 이미 존재하는 안전한 대상 디렉터리를 받습니다. 없는 디렉터리를 먼저 만들고 구조만 준비하려면 `reporivet init --root "$ROOT"`을 사용할 수 있습니다. Reporivet은 대상 디렉터리나 그 안의 프로젝트 소유 파일을 임의로 만들거나 덮어쓰지 않습니다.

첫 번째 setup 호출은 감사, 보이는 안내형 정의, 답변 재개와 정확한 preview를 수행합니다.

```bash
ROOT=/absolute/path/to/target
reporivet setup --root "$ROOT"
```

유효한 answers 파일이 이미 있으면 이 preview/definition 단계에서 함께 지정할 수 있습니다.

```bash
reporivet setup \
  --root "$ROOT" \
  --answers /absolute/path/to/answers.json
```

이 호출은 JSON envelope를 출력합니다. `state`는 보통 `awaiting-approval`이며, `backup-required`, `conflict` 또는 `dry-run`을 출력할 수도 있고 그 경우 해당 다음 단계를 따라야 합니다. `definition`, `changes`, `preview.actions`, `preview.diagnostics`를 모두 검토하고 `preview.fingerprint`의 exact SHA-256을 복사합니다. 대상 bundle은 아직 적용되지 않습니다. 일반 setup에서는 보이는 `docs/product-specs/project-definition.draft.md`를 만들거나 갱신할 수 있으며, 이는 프로젝트 소유의 resume 상태입니다. Setup은 이 상태를 자동으로 숨기거나 제거하지 않습니다.

별도의 `setup --preview` flag는 없습니다. `--apply`가 없는 호출이 setup preview 단계입니다. 검토한 대상과 동일한 root, draft, backup 경로를 유지한 채 exact fingerprint를 승인하여 적용합니다.

```bash
PREVIEW_SHA256='paste-the-preview-fingerprint-from-the-json-output'

reporivet setup \
  --root "$ROOT" \
  --apply \
  --approve-preview "$PREVIEW_SHA256"
```

`--apply`는 현재 대상과 보이는 draft를 다시 읽어 preview를 재계산한 뒤 fingerprint가 정확히 일치할 때만 적용합니다. 대상, draft, answers 또는 backup 경로를 바꿨다면 이전 fingerprint를 재사용하지 말고 preview를 다시 실행해야 합니다. `setup --apply`에는 `--answers`와 `--dry-run`을 함께 사용할 수 없습니다.

Preview에 legacy cleanup이나 기타 파괴적 동작이 포함되면 대상 밖의 절대 외부 backup 디렉터리를 preview와 apply 양쪽에 지정해야 합니다. 새 대상의 create-only setup에는 보통 필요하지 않습니다.

```bash
BACKUP_DIR=/absolute/path/outside/target/reporivet-backup

reporivet setup \
  --root "$ROOT" \
  --backup-dir "$BACKUP_DIR"

# JSON output의 fingerprint를 검토한 뒤 같은 backup 경로로 적용합니다.
reporivet setup \
  --root "$ROOT" \
  --backup-dir "$BACKUP_DIR" \
  --apply \
  --approve-preview "$PREVIEW_SHA256"
```

### Preview와 승인이 필요한 경우

모든 Reporivet 명령이 preview를 필요로 하는 것은 아닙니다. Preview fingerprint는 setup bundle 또는 legacy transition을 실제로 적용할 때의 승인 경계입니다.

| 명령 또는 상황 | 동작 | Preview와 승인 |
| --- | --- | --- |
| `reporivet setup --root "$ROOT"` | 감사, guided definition, 보이는 draft 처리와 target preview를 수행합니다. | JSON preview와 fingerprint를 검토하지만 이 호출만으로 target bundle을 적용하지 않습니다. |
| `reporivet setup --root "$ROOT" --apply` | 현재 draft를 기준으로 setup bundle을 적용합니다. | `--approve-preview <HASH>`가 반드시 필요하며 exact fingerprint가 아니면 거부됩니다. |
| `reporivet setup --root "$ROOT" --dry-run` | 답변과 예상 action을 계산하지만 파일을 쓰지 않습니다. | 승인이 필요하지 않으며 `--apply`와 함께 사용할 수 없습니다. |
| `reporivet define finalize --root "$ROOT"` | lower-level visible definition의 target preview를 출력합니다. | 적용할 때 `define finalize --root "$ROOT" --apply --approve-preview <HASH>`를 사용합니다. |
| `reporivet audit --root "$ROOT"`, `reporivet define status --root "$ROOT"` | package-side read-only inventory 또는 draft 상태를 출력합니다. | setup preview나 approval이 필요하지 않습니다. |
| `reporivet init --root "$ROOT"` | 누락된 구조를 create-if-missing 방식으로 준비합니다. | setup fingerprint gate는 없으며, 쓰기 없이 확인하려면 `--dry-run`을 사용합니다. |
| `reporivet migrate --root "$ROOT" --from 0.2 --preview --backup-dir "$BACKUP_DIR"` | 별도의 legacy transition preview입니다. | 항상 명시적 `--preview` 후 exact `--approve-preview`와 외부 backup으로 적용합니다. 자세한 명령은 아래 transition 절을 따릅니다. |

### Answers 파일

`--answers`는 topic key를 최상위 키로 갖는 JSON object입니다. 값은 Confirmed shorthand 문자열이거나 `confirmed`, `proposed`, `open`, `sources`만 포함하는 object이며, 각 값은 문자열 하나 또는 문자열 배열입니다. 누락된 topic은 Open으로 남습니다. `setup --apply`에서는 새 answers 파일을 받지 않고, preview 전에 저장된 visible draft를 사용합니다.

```json
{
  "product": "Maintainers need a reviewable repository setup.",
  "design": {
    "confirmed": "Keyboard operation is required.",
    "proposed": ["Review reduced-motion behavior."],
    "open": ["Which locales must be supported?"],
    "sources": ["Project owner answer."]
  },
  "web_ui": "no",
  "deployed_runtime": "no",
  "procedures": {
    "confirmed": [
      "{\"slug\":\"release-check\",\"title\":\"Release check\",\"trigger\":\"Before release\",\"reads\":[\"QUALITY.md\"],\"actions\":[\"Run project checks\"],\"stop_conditions\":[\"A required check fails\"],\"evidence\":[\"Check output\"],\"permissions\":[\"Maintainer approval\"],\"rollback\":[\"Follow the project rollback procedure\"]}"
    ]
  }
}
```

`procedures.confirmed`의 각 항목은 위처럼 strict nine-field JSON record를 담은 문자열이어야 합니다. 정확히 `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, `rollback`을 모두 갖춘 고유한 Confirmed record만 `docs/runbooks/<slug>.md`를 만들 수 있습니다. Generic, incomplete, duplicate, Proposed, Open 또는 Sources-only record는 runbook을 만들지 않습니다.

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
| `reporivet setup` | 기본 통합 감사, 안내형 정의, 정확한 미리보기와 승인된 일회성 setup. | 최종 target bundle은 exact preview fingerprint의 명시적 승인과 안전한 재검증 뒤에만 적용하며, 일반 setup은 승인 전에 visible draft를 만들거나 갱신할 수 있습니다. Plan을 만들거나 프로젝트 명령을 실행하지 않습니다. |
| `reporivet init` | 구조만 만드는 비덮어쓰기 create-if-missing 번들. | 기존 프로젝트 소유 콘텐츠를 보존하며 안내형 설정이나 Plan을 만들지 않습니다. |
| `reporivet define start/resume/status/finalize` | 하위 수준의 보이는 안내형 정의와 정확한 미리보기/적용. | 문서화된 초안 단계와 승인된 한정 setup 경로만 씁니다. |
| `reporivet audit` | 패키지 측 결정론적 저장소 인벤토리. | 읽기 전용이며 프로젝트 명령을 실행하지 않습니다. |
| `reporivet upgrade` | 패키지 측 유지관리 중 누락된 현재 번들 경로 유지. | 소유권을 추측하지 않고 인식된 레거시 0.2 표면을 거부합니다. |
| `reporivet migrate` | 별도의 역사적 레거시 0.2 트랜잭션을 미리보기, 적용 또는 롤백. | 파괴적 적용에는 정확한 승인과 외부 백업이 필요합니다. |

`reporivet doctor`는 폐기되었으며 계속되는 Reporivet 진단 계약은 없습니다. 대상 검증에는 프로젝트 소유 검사를 사용합니다. 설치된 `reporivet <command>`와 `PYTHONPATH=src "$PYTHON" -m reporivet <command>` 형식은 setup 시점 또는 기여자 전용 패키지 작업이며 setup 이후 대상의 요구사항이 아닙니다.

## 호스트/프로젝트 workflow (Reporivet runtime이 아님)

다음 Main, Plan 및 Agent 역할은 `AGENTS.md`, 일반 Markdown Plan, 프로젝트 명령과 호스트의 Agent 기능으로 표현되는 호스트 네이티브/프로젝트 소유 운영 계약입니다. 이 계약은 handoff 이후 적용되며 Reporivet이 제공하거나 실행하지 않습니다.

- **Main**은 의도, 범위, 비목표, 인수 조건, 전체 작업 트리, 통합, 결정, 후보 식별자, 증거 판단과 직렬화된 모든 Plan 편집을 소유합니다. Main은 호스트 네이티브 Agent dispatch를 사용하며 Reporivet은 Agent를 spawn/dispatch하지 않습니다.
- **Task Owner**는 모든 broad 또는 multi-part root의 기본 역할이며 `May delegate: yes`를 가집니다. Owner는 먼저 승인된 범위 안에서 finite child manifest를 반환하고, Main은 승인된 child row와 완전한 matching packet을 Plan에 직렬화한 뒤 직렬화된 Owner를 재개합니다. 재개된 serialized Task Owner만 호스트 네이티브 Agent 실행으로 선언된 dependency-ready descendant를 dispatch합니다.
- **구현 Sub**는 정확한 읽기 경로, 허용된 쓰기 경로, 보호 경로, 프로젝트 소유 검사, 인수 조건과 중지 조건을 담은 한정 Task Packet 하나를 받습니다. Narrow 또는 본질적으로 serial인 root는 direct nondelegating leaf로 남으며 ordinary leaf Agents never delegate(일반 leaf Agent는 절대 위임하지 않고) 범위를 넓히거나 자신의 작업을 승인하지 않습니다.
- **검증 Sub**는 새로운 컨텍스트에서 시작해 통합 후보를 식별하고 프로젝트 소유 검사를 실행한 뒤 인수 조건별 결과와 잔여 위험을 반환합니다. 읽기 전용 검증 leaf는 병렬로 실행할 수 있고, 위임하지 않으며, 통합 후보에 의존합니다. 별도 구현 작업이 없으면 후보를 수정하지 않습니다.

For every broad or multi-part root, this is a common host/project rule:

`T<n> (broad root Owner) -> T<n>-A/B/C/... (declared child packets, all ready leaves dispatched concurrently) -> T<n>-I (Owner-local aggregation) -> T<n>-V1/V2/... (parallel fresh verification)`

Main은 독립적인 root Owner를 동시에 dispatch합니다. 모든 child 작업은 owner, state, dependency, outcome, result와 일치하는 한정 packet을 유지합니다. 변경 가능한 형제 작업을 병렬 실행하려면 disjoint allowed-write sets, 고정된 공유 인터페이스와 separate exact-baseline worktrees가 필요합니다. Owner-local aggregation은 Main의 최종 저장소 통합과 구별되며, 새 검증은 통합 후보에 대해 read-only, nonrepairing, nondelegating으로 수행됩니다. Main만 Plan 편집을 직렬화하고 종료 Plan을 `completed/`로 수동 이동하며 어떤 명령도 완료를 결정하지 않습니다.

이것은 호스트/프로젝트 운영 계약이지 Reporivet 런타임이 아닙니다. Reporivet은 Agent spawn/dispatch 메커니즘, 프로젝트 명령 실행기, CI/배포 시스템, scheduler, dispatcher, task store, lease, lock, Gate, 증거 보관소, 숨겨진 상태 또는 자동 closure를 설치하지 않습니다.

## 역사적 Reporivet 0.2 migration (현재 setup과 별도)

이 절은 일반적인 새 프로젝트 setup 경로가 아닙니다. 인식된 legacy 0.2 표면에만 적용됩니다. `dev/`, `.harness/runs`, 복사된 runtime, 이전 Skills, 생성된 settings 및 관련 명령 표면 같은 예전 Harness 시대 산출물은 역사적 transition 후보일 뿐이며, 새 setup의 출력이 아니고 현재 setup이 Harness나 지속 runtime을 설치한다는 뜻도 아닙니다.

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
- Guided definition protocol: [`project-definition-protocol.md`](docs/references/project-definition-protocol.md)
- 현재 one-shot setup specification: [`SPEC-REPORIVET-004-one-shot-bootstrapper.md`](docs/product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md)
- 현재 one-shot setup design: [`DESIGN-REPORIVET-004-one-shot-setup.md`](docs/design-docs/DESIGN-REPORIVET-004-one-shot-setup.md)
- 현재 one-shot setup decision: [`ADR-0002-one-shot-bootstrapper-boundary.md`](docs/decisions/ADR-0002-one-shot-bootstrapper-boundary.md)

이 SPEC-004, DESIGN-004 및 ADR-0002 문서가 현재 setup 동작의 권위입니다. 이전 Harness 시대의 참조 문서는 역사적 배경일 뿐이며 현재 generated tree 또는 one-shot 경계 주장을 덮어쓰지 않습니다.
