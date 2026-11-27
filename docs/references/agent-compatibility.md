---
id: REF-REPORIVET-006
kind: reference
status: active
owner: main
area: compatibility
updated: 2026-11-27
---

# 에이전트 진입점 호환성

Reporivet은 root `AGENTS.md`의 관리 블록과, `--claude`를 선택한 경우 `AGENTS.md`를 읽으라는 일반 텍스트 포인터가 들어 있는 `CLAUDE.md`를 만든다. 포인터는 `@` import가 아니며 에이전트가 추가 읽기 지시를 따를지는 실행 환경과 모델에 달려 있다. `doctor`는 구조·링크를 확인할 뿐 에이전트의 실제 지침 로딩을 증명하지 않는다. 여기서 공식 문서의 지원과 로컬 실측은 별개다. 공식 문서와 제품 버전은 바뀔 수 있다.

## 표면별 상태 — 2026-11-27 확인

| 에이전트·표면 | 공식 문서상 진입점 | 이번 로컬 관찰 | 유의점 |
|---|---|---|---|
| Codex CLI 0.172.0 | root에서 작업 디렉터리까지의 `AGENTS.md` 등 | 격리된 root와 하위 cwd에서 도구 호출 없이 지침 토큰 반환 | 각 디렉터리의 `AGENTS.override.md` 우선순위와 크기 제한이 있다. [공식 안내](https://developers.openai.com/codex/guides/agents-md/) |
| Claude Code CLI 2.1.332, 일반 모드 | `CLAUDE.md`; 설정·버전에 따라 `AGENTS.md` | AGENTS만 있는 대상은 도구 호출 없이 토큰 반환. `--claude` 포인터 대상은 도구 없는 질의에 UNKNOWN, 별도 Read 허용 세션은 AGENTS를 읽고 토큰 반환 | 이 환경의 기본 fallback은 프로젝트 `CLAUDE.md`가 있으면 AGENTS 대신 CLAUDE를 사용한다. Reporivet의 텍스트 포인터는 지시 이행에 의존한다. [공식 안내](https://code.claude.com/docs/en/memory), [AGENTS 모듈](https://github.com/anthropics/claude-code/blob/main/mods/agents-md/README.md) |
| Claude Code CLI 2.1.332, `--restricted` | 설정·환경에 따라 다름 | AGENTS-only 및 CLAUDE 양성 대조의 도구 없는 질의는 둘 다 UNKNOWN. 별도 Read 허용 세션은 CLAUDE와 AGENTS를 읽고 토큰 반환 | 양성 대조도 실패해 원인을 지침 로딩 자체로 단정할 수 없다. 일반 모드 결과를 이 모드의 보장으로 쓰지 않는다. |
| GitHub Copilot CLI | 공식 문서는 root·작업 디렉터리 등에서 `AGENTS.md`와 `CLAUDE.md` 탐색을 설명 | CLI 미설치로 실측하지 않음 | 다른 Copilot 표면의 지원은 다르며 일부 subagent에는 저장소 지침이 기본 포함되지 않는다. [CLI 안내](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions), [표면별 지원](https://docs.github.com/en/copilot/reference/custom-instructions-support), [subagent](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference) |

Codex 실측의 marker는 Reporivet 생성 블록 **밖의 사용자 지침**에 두었다. 이는 해당 세션에서 그 사용자 지침이 모델 응답에 반영된 관찰이며, 생성된 경로 목록의 의미 이해나 작업 성공을 증명하지 않는다. Claude의 `--claude` 포인터 후속 Read도 같은 한계를 가진다. Codex의 기본 지침 용량 제한(공식 문서의 기본값 32 KiB), 기존 override 파일, 상위·하위 지침과 에이전트별 설정은 실제 로딩에 영향을 줄 수 있다. 목록이 읽혔다는 것과 목록이 유용하다는 것도 다르다.

**Claude의 하위 지침 주의:** 같은 일반 모드에서 유일한 차이가 root CLAUDE 포인터의 존재인 두 fixture를 비교했다. `nested/subject.txt`만 Read한 뒤 하위 지침의 토큰을 묻는 질의에서 AGENTS-only 대상은 토큰을 반환했고, `--claude` 대상은 UNKNOWN을 반환했다. 둘 다 하위 AGENTS를 직접 Read하지 않았다. 이는 해당 기본 fallback 설정에서 root CLAUDE의 존재가 하위 AGENTS 로딩에도 영향을 줄 수 있다는 공식 설명과 부합하는 단일 관찰이다. 여러 버전·설정의 보장은 아니다. 기존 nested AGENTS에 의존한다면 `--claude`를 추가하기 전에 사용 중인 Claude Code의 설정과 실제 로딩을 확인한다.

## 로컬 probe와 한계

고유 임시 디렉터리 `/private/var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-compat-9k3vmoxm`에 현재 작업 트리의 CLI로 `init --name Probe`를 실행하고 `--claude` 대상은 포인터를 그대로 생성했다. AGENTS에는 생성된 관리 블록 외부에 실험용 비밀이 아닌 고유 토큰을 추가했다. Codex 하위 cwd 사례의 nested AGENTS는 프로젝트 소유 테스트 지침이며 Reporivet이 생성한 파일이 아니다. fixture 밖 사용자 설정은 수정하지 않았다.

자동 로딩 probe의 질의는 파일명·토큰을 주지 않고, 이미 문맥에 있는 프로젝트 지침의 토큰을 반환하거나 없으면 UNKNOWN을 답하며 도구를 호출하지 말라고 요청했다. Codex는 `exec --skip-git-repo-check --ephemeral --ignore-user-config --sandbox read-only --json`을 사용했다. Claude 일반 모드는 `--setting-sources project`, hook 비활성화, auto-memory 비활성화, `--strict-mcp-config`, `--no-session-persistence`, `--permission-mode dontAsk`, `--model fable`, `--tools ''`을 사용했다. 포인터 탐색은 별도 fresh 세션에서 Read만 허용하고 지침에 파일 읽기 지시가 있으면 따르도록 요청했다. 모든 표준입력은 `DEVNULL`이었다.

두 도구의 trace에서 결과와 도구 호출을 확인했지만 모델이 본 전체 초기 문맥을 독립적으로 복원한 것은 아니다. 사용자·상위 경로의 주요 instruction 파일은 없거나 비어 있음을 확인했으나 다른 환경 변수·관리 설정까지 보편적으로 배제한 것은 아니다. 각 조건은 단일 세션이며, 다른 버전·IDE·cloud·subagent·다중 모델·보안 경계·성능은 검증하지 않았다. 로그는 고유 임시 경로에만 있고 지속 보관이 보장되지 않는다. Claude 10회 CLI 표시 목록가 합계는 약 `$0.315`이며 실제 청구액은 확인하지 않았다. Codex의 비용은 측정하지 않았다.

`CLAUDE.md` 포인터를 포함한 실제 agent 탐색 사례는 [탐색 평가](agent-navigation-evaluation.md)에 별도로 기록한다. 통합 환경에서 지침이 빠지면 우선 해당 에이전트의 버전, 시작 디렉터리, 설정과 자동 주입 여부를 확인하고 필요한 경우 프로젝트 소유 지침에서 읽기 경로를 명시한다.
