# Reporivet

**프로젝트의 기존 근거를 agent가 찾아 쓰도록 돕는 작은 진입점 도구입니다.**

현재 소스는 미출시 **0.3.0.dev1**입니다. 공개된 [v0.2.0](https://github.com/gkrtjd99/Reporivet/releases/tag/v0.2.0)은 이전 runtime형 제품이며 tag와 배포 파일은 그대로입니다. 기존 사용자는 [전환·파일 관리 안내](docs/references/entrypoint-migration.md)를 먼저 읽으세요. 새 패키지를 설치한다고 기존 target이 자동 전환되지는 않습니다.

## 하는 일과 하지 않는 일

```text
AGENTS.md 또는 선택한 실행 환경의 진입 문서
    → 프로젝트가 이미 가진 문서·명세·코드·검사 방법
    → agent가 근거를 읽고 기존 도구로 작업
```

Reporivet은 문서 이름·디렉터리·frontmatter를 강제하지 않습니다. `handbook/`, `openspec/`, `specs/`, README 등 기존 경로를 제한된 범위에서 관찰해 안내를 추가합니다. **경로가 존재한다는 사실은 현재 요구사항이라는 뜻이 아닙니다.** 현재 근거와 읽기 순서는 프로젝트 소유자가 관리 블록 밖에 기록합니다.

이미 진입점이 잘 연결돼 있다면 추가하지 않아도 됩니다. Spec Kit·OpenSpec·Kiro 등의 명세·작업 절차를 대체하거나 같은 상태를 두 번 관리하지 않습니다.

```text
project/
├── AGENTS.md                  # 한정된 관리 블록; 밖의 기존 본문 보존
├── CLAUDE.md                  # --claude 선택 시 AGENTS로 연결
└── 기존 문서·코드·설정·CI       # 이름·배치·내용 그대로 유지
```

Target runtime·wrapper·harness.toml·버전 marker·고정 docs 문서군·ExecPlan schema·Gate·작업 상태·CI·`.gitignore`는 생성하지 않습니다. 패키지를 제거해도 일반 Markdown과 프로젝트 자체 도구로 사용할 수 있습니다.

## 처음 사용하기

Python 3.11 이상이 필요합니다. 다음은 **이 소스 checkout의 root에서** 실행하는 방법입니다. 미출시 버전이 package index에 있다고 가정하지 않습니다.

```bash
PYTHONPATH=src python3 -m reporivet --help
PYTHONPATH=src python3 -m reporivet audit --root /absolute/path/to/project
PYTHONPATH=src python3 -m reporivet init --root /absolute/path/to/project --dry-run
PYTHONPATH=src python3 -m reporivet init --root /absolute/path/to/project
PYTHONPATH=src python3 -m reporivet doctor --root /absolute/path/to/project
```

설치한 CLI에서는 `reporivet`을 사용합니다. preview와 적용에는 같은 옵션을 사용하세요.

```bash
reporivet init --root ./project --name "Project" --claude --dry-run
reporivet init --root ./project --name "Project" --claude
reporivet doctor --root ./project
```

- `init`: AGENTS 관리 블록을 생성·갱신합니다. 새 root의 부모 디렉터리는 먼저 있어야 하며 경로의 symlink는 거부합니다.
- `--claude`: CLAUDE 관리 블록도 생성·갱신합니다. 기존 두 파일의 의미적 충돌까지 해결하지는 않습니다.
- `audit`: 실제 경로와 제외 범위를 JSON으로 출력하는 읽기 전용 관찰입니다. 파일 내용이나 추론한 명령을 출력·실행하지 않습니다. Exit 0은 보고서 작성 성공이지 conflict 부재나 프로젝트 품질 통과가 아닙니다.
- `doctor`: 생성된 로컬 링크·관리 구조 등을 기계적으로 점검합니다. 오류는 exit 2이며, 의미·작업 완료를 판정하지 않습니다.
- `upgrade`: 경로 목록과 관리 블록을 다시 생성합니다. CLAUDE도 갱신하려면 `--claude`를 명시합니다. v0.2 자동 migration은 하지 않습니다.

## 미리보기에서 확인할 것

`init`과 `upgrade`의 `--dry-run`은 target 파일·디렉터리를 변경하지 않고 생성/갱신/변경 없음 목록, **실제 예정 본문의 unified diff**, fingerprint를 보여줍니다. `-`는 없어질 줄, `+`는 새 줄입니다. 변경이 없으면 `No changes (no-op).`와 `(no changes)`를 표시합니다.

관리 블록 안의 수동 편집이 대체되는지도 diff에 드러납니다. CRLF의 `\r`, terminal 제어 문자, 방향 제어 문자는 실행되지 않는 문자열로 표시하고 마지막 줄바꿈이 없으면 `No newline at end of file` 표시를 붙입니다. 이는 사람의 검토용 출력이며 그대로 적용할 patch로 보장하지 않습니다.

**Preview에는 기존 instruction 본문과 주변 문맥이 포함될 수 있습니다.** 비밀값이 있는지 확인하기 전 외부에 공유하지 마세요. 파일 내용을 출력하지 않는 `audit`와 다릅니다. Fingerprint는 승인·잠금·다음 실행 결과의 보장이 아니므로 입력이나 문서가 바뀌면 preview부터 다시 확인합니다.

## 직접 쓸 지침과 자동 갱신할 목록 구분하기

AGENTS의 `reporivet:entrypoints:start/end` 사이만 Reporivet 관리 영역입니다. **그 안의 편집은 다음 init/upgrade에서 대체됩니다.** 보존할 프로젝트 지침은 블록 앞이나 뒤에 작성하세요. 기존 파일의 양쪽 본문 bytes와 mode는 보존합니다.

다음은 관리 블록 밖에 쓸 수 있는 예시입니다. 경로와 명령은 예시이므로 자기 프로젝트의 실제 근거로 바꾸세요. 문서를 새 schema에 맞추거나 존재하지 않는 파일을 만들 필요는 없습니다.

```markdown
## 이 프로젝트의 읽기 순서

- 현재 요구사항은 handbook/current.md를 읽는다.
- archive/의 문서는 과거 기록이며 현재 정책을 대체하지 않는다.
- 관련 구현은 src/에서 찾고, 검사 방법은 CONTRIBUTING.md에서 확인한다.
- 문서끼리 충돌하면 근거를 보고하고 임의로 선택하지 않는다.
```

관찰 목록은 완전한 inventory가 아닙니다. 한글·공백 파일명은 읽을 수 있는 label로 표시하고 링크 주소는 URL encoding합니다. 이름만 보고 현재/과거 authority를 자동 분류하지 않습니다.

## 문서를 옮기거나 안내를 제거할 때

문서를 추가·이동·삭제해도 AGENTS 목록은 자동 갱신되지 않습니다. 설치된 CLI가 있다면 다음처럼 갱신합니다.

```bash
reporivet upgrade --root ./project --claude --dry-run
reporivet upgrade --root ./project --claude
reporivet doctor --root ./project
```

패키지가 없으면 일반 Markdown으로 직접 관리할 수 있습니다. 나중에 다시 Reporivet을 사용할 생각이라면 보존할 지침은 관리 블록 밖에 두세요. 설치나 명령 예시 자체가 agent에게 실행 권한을 부여하지는 않습니다.

패키지 제거와 문서 제거는 별개입니다. 더 이상 관리 블록을 쓰지 않으려면 [정확한 marker와 수동 제거 절차](docs/references/entrypoint-migration.md)를 따라 CLAUDE 연결과 AGENTS 블록만 검토해 제거합니다. **사용자 본문이 섞인 AGENTS/CLAUDE 전체를 삭제하지 마세요.** 자동 제거 명령은 없습니다.

## 실제로 잘 찾아가는가?

[실제 agent 탐색 평가](docs/references/agent-navigation-evaluation.md)는 서로 다른 작은 저장소에서 적용 전후를 fresh 세션으로 관찰한 기록입니다. 기존 실험은 적용 전부터 성공했으므로 개선 효과를 입증하지 않았습니다. 그때의 생성물과 이번 UX 보수 생성물도 구분해 기록합니다. 기계적 검사와 문구 개선만으로 새 agent의 업무 성능이 좋아졌다고 주장하지 않습니다.

## 소스 개발 및 검증

```bash
PYTHON=python3 ./dev/check
```

이 명령은 **Reporivet 소스 저장소의** unit/integration/distribution 검사이며 target에 설치되지 않습니다. 지원 Python과 offline wheel build가 가능한 pip/setuptools 환경이 필요합니다. 빌드 도구가 없으면 실패를 숨기거나 skip하지 않습니다.

이 소스에서만 CLAUDE portable block을 편집하고 `./dev/agent-contract-sync`로 AGENTS에 투영합니다. Target에는 source 전용 sync helper나 이 소스의 문서 구조를 배포하지 않습니다.

- [현재 요구사항](docs/PRODUCT.md) · [상세 명세](docs/product-specs/SPEC-REPORIVET-003-agent-entrypoints.md)
- [구조와 소유권](ARCHITECTURE.md) · [품질](docs/QUALITY.md) · [보안과 한계](docs/SECURITY.md)
- [전환·파일 관리](docs/references/entrypoint-migration.md) · [탐색 평가](docs/references/agent-navigation-evaluation.md)
- [현재 제품 경계 결정](docs/decisions/ADR-0002-entrypoint-only-boundary.md)

파일 보호는 OS 수준의 완전한 동시성 격리나 sandbox가 아닙니다. Reporivet은 프로젝트 명령 실행·agent 감독·모델 호출·배포·게시를 수행하지 않습니다.
