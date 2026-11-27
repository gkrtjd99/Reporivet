# Reporivet

**프로젝트의 기존 문서와 코드를, 에이전트가 찾을 수 있도록.**

Reporivet은 저장소를 살펴보고 `AGENTS.md`에 작은 탐색 진입점을 추가하는 CLI입니다. 이미 있는 문서 체계와 도구를 그대로 사용하면서, 새로운 에이전트가 어디서부터 살펴볼지 알려줍니다.

[![CI](https://github.com/gkrtjd99/Reporivet/actions/workflows/ci.yml/badge.svg)](https://github.com/gkrtjd99/Reporivet/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](README.en.md) · [빠른 시작](#빠른-시작) · [명령어](#명령어) · [안전과 한계](#안전과-한계) · [문서](#문서)

> **v0.3.0a1은 프리릴리즈입니다.** 공개된 [v0.2.0](https://github.com/gkrtjd99/Reporivet/releases/tag/v0.2.0)은 이전 runtime형 제품입니다. 기존 프로젝트는 자동으로 전환되지 않으므로 [전환 안내](docs/references/entrypoint-migration.md)를 먼저 확인하세요.

## 왜 Reporivet인가요?

저장소의 요구사항, 설계, 코드와 검사 방법은 여러 경로에 흩어져 있을 수 있습니다. Reporivet은 그 파일들을 복사하거나 새 문서 형식으로 바꾸는 대신, **실제로 관찰한 경로를 가리키는 짧은 목록**을 만듭니다.

```text
AGENTS.md / 선택적인 CLAUDE.md
    → 프로젝트의 기존 문서 · 명세 · 코드 · 검사 방법
    → 에이전트가 필요한 근거를 읽고 기존 도구로 작업
```

- **기존 프로젝트 존중:** 문서 이름, 디렉터리 구조, frontmatter나 작업 절차를 강제하지 않습니다. Spec Kit, OpenSpec, Kiro 또는 자체 문서 체계를 그대로 사용할 수 있습니다.
- **좁은 쓰기 범위:** `AGENTS.md`의 관리 블록과 선택적인 `CLAUDE.md` 연결만 작성합니다. 블록 밖의 기존 내용과 파일 mode는 보존합니다.
- **검토 후 적용:** 파일 내용을 출력하지 않는 `audit`와 실제 변경 내용을 보여 주는 `--dry-run`을 제공합니다.
- **일반 Markdown:** 대상 프로젝트에 런타임, CI, 설정 파일이나 별도의 작업 저장소를 설치하지 않습니다. 패키지를 제거해도 파일은 남습니다.

관찰된 경로는 **현재 요구사항이라는 보증이 아닙니다.** 어떤 문서가 최신 근거인지, 어떤 검사가 적절한지는 프로젝트 소유자와 에이전트가 확인해야 합니다. 진입점이 이미 잘 연결된 저장소에는 Reporivet이 필요하지 않을 수 있습니다.

## 빠른 시작

**요구사항:** Python 3.11 이상, Linux 또는 macOS. Windows는 현재 지원하지 않습니다. CI는 두 OS에서 Python 3.11–3.15를 검사하도록 구성되어 있습니다.

### 설치

[v0.3.0a1 GitHub 프리릴리즈](https://github.com/gkrtjd99/Reporivet/releases/tag/v0.3.0a1)의 wheel을 가상환경에 설치합니다. 이 버전이 PyPI에 게시되었다고 가정하지 않습니다.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install https://github.com/gkrtjd99/Reporivet/releases/download/v0.3.0a1/reporivet-0.3.0a1-py3-none-any.whl
reporivet --version
```

또는 소스 checkout에서 `python -m pip install .`로 설치할 수 있습니다. 가상환경을 만들 때는 지원되는 Python 3.11 이상을 선택하세요.

### 프로젝트 살펴보고 적용하기

아래 경로를 **실제 대상 프로젝트**로 바꾸세요. 먼저 관찰 결과와 변경 미리보기를 검토합니다.

```bash
reporivet audit --root /path/to/project
reporivet init --root /path/to/project --dry-run
reporivet init --root /path/to/project
reporivet doctor --root /path/to/project
```

Claude Code용 연결도 원한다면 미리보기와 적용 **양쪽에** `--claude`를 추가합니다.

```bash
reporivet init --root /path/to/project --claude --dry-run
reporivet init --root /path/to/project --claude
```

`--claude`는 `AGENTS.md`를 읽으라는 일반 텍스트 포인터를 추가합니다. Claude Code 버전·설정에 따라 지침을 불러오는 방식이 다르며, 기존 하위 `AGENTS.md` 사용에 영향을 줄 수 있습니다. [에이전트별 호환성](docs/references/agent-compatibility.md)을 확인하세요.

## 명령어

| 명령 | 하는 일 |
|---|---|
| `init` | 한정된 `AGENTS.md` 관리 블록을 생성하거나 갱신합니다. `--claude`를 선택하면 연결도 작성합니다. |
| `audit` | 실제 경로와 제외 범위를 읽기 전용 JSON으로 보고합니다. 파일 내용이나 추론한 명령은 출력·실행하지 않습니다. 종료 코드 0은 보고서 작성 성공을 뜻합니다. |
| `upgrade` | 관찰 경로와 관리 블록을 다시 생성합니다. CLAUDE 연결도 갱신하려면 다시 `--claude`를 지정합니다. |
| `doctor` | 관리 구조와 로컬 링크 등을 기계적으로 점검합니다. 오류 시 종료 코드 2를 반환하며, 문서의 의미나 작업 완료를 판정하지 않습니다. |

`init`과 `upgrade`는 `--dry-run`을 지원합니다. 상세 옵션은 `reporivet --help`와 각 명령의 `--help`를 확인하세요. 새 프로젝트 경로를 지정할 때는 부모 디렉터리가 먼저 있어야 합니다.

## 프로젝트 지침 관리

Reporivet이 관리하는 부분은 아래 marker 사이입니다. **다음 `init` 또는 `upgrade`에서 이 블록은 다시 생성됩니다.** 보존할 프로젝트 지침은 블록 밖에 작성하세요.

```markdown
<!-- reporivet:entrypoints:start -->
Reporivet이 관리하는 탐색 안내
<!-- reporivet:entrypoints:end -->
```

예를 들어 블록 밖에서 현재 요구사항의 위치, 과거 문서 구분, 실제 검사 명령을 직접 안내할 수 있습니다. 파일을 추가·이동·삭제한 뒤에는 `upgrade --dry-run`으로 차이를 확인하고, 같은 옵션으로 적용한 다음 `doctor`를 실행하세요.

패키지 삭제와 안내 블록 삭제는 별개입니다. 자동 제거 명령은 없으며, 사용자 내용이 섞인 파일 전체를 삭제하지 말고 [수동 제거 절차](docs/references/entrypoint-migration.md)를 따르세요.

## 안전과 한계

- `audit`는 파일 내용을 출력하지 않지만, **경로 이름 자체에는 민감한 정보가 들어갈 수 있습니다.**
- `--dry-run`은 실제 before/after의 사람 검토용 diff이며 적용 가능한 patch가 아닙니다. 기존 지침과 주변 문맥이 포함될 수 있으므로 공유 전에 확인하세요. Fingerprint는 승인·잠금·다음 실행 결과를 보장하지 않습니다.
- 관찰은 최대 512개 항목과 깊이 제한 안에서 이루어지고, 결과는 최대 80개 파일입니다. 문서형과 그 외 경로에 각각 최대 40개를 먼저 배정하고 남는 자리를 재배분하지만, 특정 문서나 검사 파일이 포함된다는 보장은 없습니다. 파일명은 문서의 중요도나 현재성을 판정하지 않습니다.
- 새 파일의 권한에는 OS의 생성 정책과 일반적으로 호출자의 umask가 적용됩니다. 기본 ACL 동작은 OS·파일시스템마다 다릅니다. 파일 보호는 OS 수준의 완전한 동시성 격리나 sandbox가 아닙니다. 다른 사용자가 동시에 디렉터리 항목을 교체할 수 없는 위치에서 실행하세요. 자세한 내용은 [보안과 한계](docs/SECURITY.md)를 참고하세요.

## 실제 효과는 검증됐나요?

[탐색 평가](docs/references/agent-navigation-evaluation.md)는 적용 전후의 fresh 에이전트 세션과 관찰 결과를 기록합니다. 현재의 작은 합성 사례에서는 적용 전부터 에이전트가 올바르게 진단했으므로 **작업 성공률이나 비용의 개선은 입증되지 않았습니다.** 더 큰 실제 저장소와 다양한 모델에서의 결과는 아직 확인이 필요합니다.

## 개발과 기여

이 저장소를 수정할 때는 소스 checkout에서 다음 검사를 실행합니다. 배포 검사는 wheel 빌드가 가능한 pip/setuptools 환경을 필요로 합니다.

```bash
PYTHON=python3 ./dev/check
```

버그와 개선 제안은 [GitHub Issues](https://github.com/gkrtjd99/Reporivet/issues)에 남겨 주세요. 취약점이나 비밀정보는 공개 이슈에 게시하지 말고 [보안 정책](.github/SECURITY.md)을 따릅니다.

## 문서

- [문서 지도](docs/README.md) · [제품 요구사항](docs/PRODUCT.md) · [아키텍처](ARCHITECTURE.md)
- [에이전트별 호환성](docs/references/agent-compatibility.md) · [실제 탐색 평가](docs/references/agent-navigation-evaluation.md)
- [v0.2 전환 및 블록 제거](docs/references/entrypoint-migration.md) · [품질 기준](docs/QUALITY.md) · [보안과 한계](docs/SECURITY.md)

## 라이선스

[MIT License](LICENSE)
