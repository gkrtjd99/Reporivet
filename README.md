# Reporivet

Reporivet은 코딩 에이전트를 위한 저장소 로컬의 문서 우선 운영 계약을 만들고 안전하게 유지하는 Python 3.11+ 패키지입니다.

기본 온보딩 명령은 감사, 보이는 안내형 정의, 정확한 미리보기, 승인된 문서/어댑터 변경을 조정하는 통합 `reporivet setup` 흐름입니다. `reporivet init`은 구조만 만드는 비덮어쓰기 create-if-missing 경로로 유지되고, 재개 가능한 정의 작업을 위한 하위 수준 `reporivet define`도 유지됩니다. 사용자가 확인한 완전한 구조화 절차만 재개된 setup을 통해 선택적 지침 전용 프로젝트 Skill을 만들 수 있습니다. Reporivet은 대상 저장소에 복사된 실행기를 남기지 않으며 명령, 테스트, CI, 배포, 운영, 비밀 정보, 증거는 프로젝트가 소유합니다.

English: [`README.en.md`](README.en.md)

## 제품 경계

```text
에이전트 호스트
    -> AGENTS.md
    -> docs/README.md
    -> 일치하는 활성 Plan 하나
    -> 작업 관련 권위 문서
    -> 프로젝트 소유 명령과 증거

Reporivet 패키지
    -> setup / init / define / audit / doctor / migrate
    -> 문서, 메타데이터, 선택 가능한 얇은 어댑터
```

패키지를 제거해도 생성된 Markdown, Plan, Skill, Git, 프로젝트 명령을 계속 유용하게 사용할 수 있어야 합니다. Reporivet 자체는 Plan이나 대상 런타임을 만들지 않으며, 프로젝트에 Plan이 필요할 때 첫 번째 일반 Markdown Plan을 만들거나 재개하는 일은 Main Skill이 담당합니다.

Reporivet은 프로젝트 명령 래퍼, CI 워크플로, 작업 데이터베이스, 저널, 증거 보관소, 백그라운드 서비스, 자동 Plan 완료 메커니즘을 생성하지 않습니다. Agent를 spawn/dispatch하지 않고 프로젝트 명령을 실행하지 않으며 CI/배포, scheduler, Gate, 숨겨진 상태 저장소도 제공하지 않습니다.

## 현재 생성 트리

문서 우선 설정은 누락된 경로만 만들고 기존 프로젝트 소유 또는 모호한 콘텐츠를 보존합니다.

```text
AGENTS.md
ARCHITECTURE.md
.reporivet-version
.gitignore                                      한정된 관리 블록

docs/
  README.md
  PRODUCT.md
  DESIGN.md
  QUALITY.md
  OPERATIONS.md
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

CLAUDE.md                                      Claude 프로필의 얇은 import
.claude/skills/reporivet-main/SKILL.md         지침 전용 역할 어댑터
.claude/skills/reporivet-implementation/SKILL.md
.claude/skills/reporivet-verification/SKILL.md
.claude/settings.json                          명시적으로 선택하는 deny 전용 설정
```

`project-definition.draft.md`는 안내형 정의를 시작한 뒤에만 나타나며 유지관리자가 명시적으로 제거할 때까지 보이는 재개 상태로 남습니다. `.gitkeep` 파일은 빈 Plan 디렉터리만 보존하므로 추적된 Plan이 생기면 제거할 수 있습니다. Reporivet은 `.gitignore`의 한정된 관리 블록만 바꾸고 그 밖의 ignore 규칙을 보존합니다.

`CLAUDE.md`와 세 Skill은 호스트별 구성 요소이며 정식 권위를 바꾸지 않고 제거할 수 있습니다. `.claude/settings.json`은 기본으로 존재하지 않고 정확한 미리보기 승인이 있어야 생성되며 기존 파일과 병합하거나 기존 파일을 덮어쓰지 않습니다.

새 문서 우선 대상에는 `dev/` 실행 표면과 `.harness/` 상태 트리가 모두 생성되지 않습니다. 이 도그푸드 저장소는 `dev/harness.toml`을 비활성 프로젝트 소유 레거시 설정으로만 보존합니다. 이 파일은 현재 실행 권위가 아니며 새 대상에 생성되지 않습니다. 보존된 `.harness/runs`는 폐기된 과거의 민감 상태입니다. 현재 코드는 그 내용을 읽거나, 쓰거나, 삭제하지 않으며 현재 증거나 작업 저장소로 사용해서는 안 됩니다.

경로별 소유권, 선택 가능성, 제거 경계는 [`docs/README.md`](docs/README.md)를 참고하십시오.

## 사용자 설치

공개 설치 안내는 pipx를 우선합니다.

```bash
pipx install reporivet
```

동일한 wheel에서 pip도 지원합니다.

```bash
python -m pip install reporivet
```

두 형식은 하나의 wheel을 설치하며 pipx는 격리된 CLI 환경을 위한 권장 방식입니다. 완료된 PLAN-2026-0003은 source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4`와 exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4`가 기록된 격리된 pipx 및 pip 설치/사용/제거 수명주기를 통과했다고 기록합니다. 검증 산출물은 임시 자료이며 영구적이거나 다운로드 가능한 증거 보관소가 아닙니다. 게시, 서명, 릴리스, 배포, CI 수리/준비성은 여전히 확립되지 않았고 범위 밖입니다.

## 기여자 전용: 소스 체크아웃

기여자는 Python 3.11 이상 인터프리터를 명시적으로 선택하여 체크아웃에서 패키지를 직접 실행할 수 있습니다. 다음은 공개 설치 경로가 아닙니다.

```bash
PYTHON=/absolute/path/to/python3.11-or-newer
"$PYTHON" --version

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/reporivet-pycache" \
PYTHONPATH=src \
"$PYTHON" -m reporivet --help
```

## 기본 온보딩

절대 대상 경로를 선택하고 설치된 Reporivet에서 통합 setup 명령을 사용합니다.

```bash
ROOT=/absolute/path/to/target
reporivet setup --root "$ROOT"
```

`setup`은 읽기 전용 감사, 보이는 안내형 정의, 답변 재개, 정확한 미리보기와 명시적으로 승인된 적용을 조정합니다. 실제 Open 항목을 포함한 일곱 개 증거 주제를 모두 보고하며 프로젝트 명령을 실행하거나 Plan을 만들지 않습니다. 완전하고 사용자가 확인한 구조화 절차 레코드만 재개된 setup을 통해 지침 전용 프로젝트 Skill을 추가할 수 있고, 불완전하거나 추론된 일반 절차, Proposed/Open/Sources 레코드는 추가하지 않습니다.

`reporivet init --root "$ROOT"`은 구조만 만드는 비덮어쓰기 create-if-missing 경로입니다. 안내형 인터뷰를 수행하거나 Plan을 만들지 않습니다. Main Skill이 활성/완료 이력을 살펴 일치하는 활성 Plan을 재개하고, 없으면 사용하지 않은 현재 연도의 가장 낮은 ID를 선택해 첫 일반 Markdown Plan을 만듭니다. Reporivet 자체는 Plan이나 런타임을 만들지 않습니다.

## 하위 수준 정의 인터페이스

유지관리자가 보이는 재개 가능한 정의 흐름을 직접 사용해야 할 때에도 `define`은 유지됩니다.

```bash
reporivet define start --root "$ROOT"
reporivet define resume --root "$ROOT"
reporivet define resume --root "$ROOT" --answers /absolute/path/to/answers.json
reporivet define status --root "$ROOT"
reporivet define finalize --root "$ROOT"
```

보이는 Markdown 초안이 유일한 재개 상태입니다. 일곱 개 주제 각각에서 **Confirmed**, **Proposed**, **Open**, **Sources**를 분리합니다. 명시적 답변은 공백 정규화만 거쳐 Confirmed에 들어가고, 스캐너 관찰은 Proposed에 남으며, 빈 답변은 Open에 남습니다. LLM은 답변을 다시 쓰거나 권위를 선택하거나 추론을 사실로 승격하지 않습니다. Deny 전용 Claude 설정을 명시적으로 선택하려면 최종 미리보기와 승인된 적용에 모두 `--with-claude-settings`를 포함합니다. 기존 설정은 항상 보존됩니다.

## 패키지 CLI

| 명령 | 목적 | 변경 경계 |
| --- | --- | --- |
| `reporivet setup` | 기본 통합 감사, 안내형 정의, 정확한 미리보기와 승인된 설정. | 명시적 승인과 안전한 재검증 뒤에만 쓰며 Plan을 만들거나 프로젝트 명령을 실행하지 않습니다. |
| `reporivet init` | 구조만 만드는 비덮어쓰기 create-if-missing 번들. | 기존 프로젝트 소유 콘텐츠를 보존하며 안내형 설정이나 Plan을 만들지 않습니다. |
| `reporivet define start/resume/status/finalize` | 하위 수준의 보이는 안내형 정의와 정확한 미리보기/적용. | 문서화된 초안 단계와 승인된 적용만 한정된 정의/설정 경로에 씁니다. |
| `reporivet audit` | 결정론적 저장소 인벤토리. | 읽기 전용이며 프로젝트 명령을 실행하지 않습니다. |
| `reporivet upgrade` | 누락된 현재 번들 경로 유지. | 인식된 레거시 0.2 표면을 거부하고 명시적 마이그레이션을 요구합니다. |
| `reporivet migrate` | 0.2 마이그레이션 트랜잭션 미리보기, 적용, 롤백. | 적용에는 외부 백업과 정확한 승인이 필요합니다. |
| `reporivet doctor` | 문서 우선 구조 진단. | 읽기 전용입니다. |

일반 프로젝트 사용에는 설치된 `reporivet <command>`를 사용합니다. `PYTHONPATH=src "$PYTHON" -m reporivet <command>`는 기여자 전용 소스 체크아웃 형식입니다.

## Main / 구현 Sub / 검증 Sub

- **Main**은 의도, 범위, 비목표, 인수 조건, 전체 작업 트리, 통합, 결정, 후보 식별자, 증거 판단, 직렬화된 모든 Plan 편집을 소유합니다. Main Skill 지침은 프로젝트 워크플로를 위해 호스트 네이티브 Agent 디스패치를 설명할 수 있지만 Reporivet이 Agent를 spawn하거나 dispatch하지는 않습니다.
- **Task Owner**는 모든 broad 또는 multi-part root의 기본 역할이며 `May delegate: yes`를 가집니다. Owner는 먼저 승인된 범위 안에서 finite child manifest(유한한 child manifest)를 반환하고, Main은 승인된 child row와 완전한 matching packet을 Plan에 직렬화한 뒤 직렬화된 Owner를 재개합니다. 재개된 Task Owner만 호스트 네이티브 Agent 실행으로 자신에게 선언된 dependency-ready descendant를 dispatch합니다.
- **구현 Sub**는 정확한 읽기 경로, 허용된 쓰기 경로, 보호 경로, 인수 조건, 프로젝트 소유 검사, 중지 조건, 반환 증거를 담은 한정된 Task Packet 하나를 받습니다. narrow 또는 본질적으로 single/serial인 root는 direct nondelegating leaf(직접적인 nondelegating leaf)로 남고, ordinary leaf Agents never delegate(일반 leaf Agent는 절대 위임하지 않으며) 범위를 넓히거나 자신의 작업을 승인하지 않습니다. Descendant는 부모의 범위, 보호 경로, 인수 조건, 비목표, child budget, 고정된 인터페이스를 상속합니다.
- **검증 Sub**는 새로운 컨텍스트에서 시작하고 통합 후보를 식별하며 적용 가능한 프로젝트 소유 검사를 실행한 뒤 인수 조건별 결과와 잔여 위험을 반환합니다. 읽기 전용(read-only) 검증 leaf는 병렬로 실행할 수 있고 위임하지 않으며 통합 후보에 의존합니다. Main이 별도 구현 작업을 dispatch하지 않는 한 후보를 수정하지 않습니다. 프로젝트 명령 실행은 프로젝트와 호스트 워크플로의 책임이며 Reporivet의 책임이 아닙니다.

broad 또는 multi-part root에는 다음과 같은 공통 installed-project 규칙을 적용합니다.

`T<n> (broad root Owner) -> T<n>-A/B/C/... (declared child packets, all ready leaves dispatched concurrently) -> T<n>-I (Owner-local aggregation) -> T<n>-V1/V2/... (parallel fresh verification)`

Main은 independent root Owners(독립적인 root Owner)를 동시에 dispatch합니다. 이 규칙은 narrow 또는 본질적으로 single/serial인 root에는 적용되지 않으며, 이러한 root는 direct nondelegating leaves(직접적인 nondelegating leaf)로 남습니다. 각 child 작업은 자체 owner, state, dependency, outcome, result와 일치하는 한정 packet을 유지합니다. 변경 가능한 형제 작업을 병렬 실행하려면 disjoint allowed-write sets(허용된 쓰기 집합이 겹치지 않음), 고정된 공유 인터페이스, separate exact-baseline worktrees(정확한 baseline의 별도 worktree)가 필요합니다. Owner-local aggregation(Owner-local aggregation is distinct from Main's final repository integration)은 Main의 최종 저장소 통합과 구별되며, 새 검증은 통합 후보에 대해 read-only(읽기 전용), nonrepairing(비수정), nondelegating(비위임)으로 수행됩니다.

Main만 Plan 편집을 직렬화하고 Owner-local aggregation과 최종 통합을 구분해 기록하며 종료 Plan을 `completed/`로 수동 이동합니다. 어떤 명령도 완료를 결정하지 않습니다. 이것은 호스트/프로젝트 운영 계약이지 Reporivet 런타임이 아닙니다. Reporivet은 Agent spawn/dispatch 메커니즘, 프로젝트 명령 실행기, CI/배포 시스템, scheduler, dispatcher, task store, lease, lock, Gate, 증거 보관소, 숨겨진 상태, 자동 closure 또는 이 워크플로를 위한 런타임을 설치하지 않습니다.

## 명시적 0.2 마이그레이션과 롤백

일반 설정은 인식된 레거시 표면을 암묵적으로 제거하지 않습니다. 대상 밖의 절대 백업 디렉터리를 선택하고 전체 트랜잭션을 미리 봅니다.

```bash
ROOT=/absolute/path/to/target
BACKUP_DIR=/absolute/path/outside/target/reporivet-backup

PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --root "$ROOT" \
  --from 0.2 \
  --preview \
  --backup-dir "$BACKUP_DIR"
```

모든 동작을 검토한 뒤 정확한 지문을 적용합니다.

```bash
MIGRATION_PREVIEW_SHA256='paste-the-emitted-sha256'

PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --root "$ROOT" \
  --from 0.2 \
  --apply \
  --approve-preview "$MIGRATION_PREVIEW_SHA256" \
  --backup-dir "$BACKUP_DIR"
```

적용은 승인된 미리보기를 다시 검증하고 권한이 제한된 외부 백업과 manifest를 생성하며 프로젝트 소유 또는 모호한 경로를 보존합니다. 적용 실패 시 안전한 경우 자동 복원을 시도합니다. 이 백업은 마이그레이션 소유 경로만 포함하며 일반 저장소 또는 프로덕션 백업이 아닙니다.

정확히 출력된 manifest로 롤백합니다.

```bash
PYTHONPATH=src "$PYTHON" -m reporivet migrate \
  --rollback /absolute/path/to/external-backup/manifest.json
```

이후 사용자 변경을 덮어쓰게 된다면 롤백은 거부됩니다. 마이그레이션된 후보가 프로젝트 소유 검사를 통과하고 유지관리자가 수락할 때까지 외부 백업을 보존합니다. 복구와 사고 경계는 [`docs/OPERATIONS.md`](docs/OPERATIONS.md)를 참고하십시오.

## 프로젝트 검사

위와 같이 인터프리터와 외부 바이트코드 캐시를 선택한 뒤 실행합니다.

```bash
PYTHONPATH=src "$PYTHON" -m unittest discover -s tests -v
PYTHONPATH=src "$PYTHON" -m compileall -q src tests
PYTHONPATH=src "$PYTHON" -m reporivet doctor --root .
git diff --check
```

산출물 빌드와 릴리스 검사는 환경 의존적이며 이 소스 명령으로 입증되지 않습니다. 증거 권위는 [`docs/QUALITY.md`](docs/QUALITY.md), 실행과 릴리스 경계 권위는 [`docs/OPERATIONS.md`](docs/OPERATIONS.md)입니다.

## 비목표

Reporivet은 다음이 아닙니다.

- 범용 오케스트레이션 플랫폼, 스케줄러, 작업 서비스, 숨겨진 상태 저장소
- 프로젝트 빌드, 테스트, CI, 릴리스, 배포, 관찰, 백업, 복구, 사고 시스템의 대체물
- 복사된 다중 호스트 프롬프트, 실행기, 모델, 판정기 번들
- 프로젝트 사실을 추론하거나 스캐너 관찰을 승인된 요구사항으로 바꾸는 권위
- 호스트 deny 규칙이 샌드박스를 이룬다는 보장
- 직접 검증되지 않은 릴리스, 설치, 산출물, 게시, 배포의 증거
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
