---
id: QUALITY
kind: quality
status: active
area: repository
summary: 기계적 안전성 검사와 실제 agent 탐색 평가의 분리
---

# Quality

품질의 핵심은 새 agent가 프로젝트의 올바른 근거·코드·검사 방법을 찾아 활용하는 것이다. 고정 문서 schema 통과는 그 증거가 아니다. 기계적으로 확인할 수 있는 파일 안전성과 실제 행동 평가는 서로 대체하지 않는다.

## 기계적 검사

`PYTHON=python3 ./dev/check`는 이 소스의 canonical 검사 명령이다. target에는 설치되지 않는다.

- 전체 unittest: 생성 범위, 링크/marker, 기존 bytes/mode 보존, read-only 동작, symlink/nonregular/legacy 거부, preimage 재검사와 rollback, immutable before/after unified diff·no-op·terminal escape preview.
- Source contract sync: provider 바깥 내용 제외와 정확한 bytes 투영. 문서 내용의 의미는 판단하지 않는다.
- Distribution: 네트워크 없이 wheel build/inventory/install/실제 CLI/uninstall을 수행한다. 설치 또는 실행하지 않은 것을 테스트 이름만으로 통과했다고 주장하지 않는다.
- Syntax 및 diff: source compile, `git diff --check`.

빌드용 pip/setuptools가 없는 환경은 실패로 보고하며 테스트를 skip하여 성공처럼 보이게 하지 않는다. 새 환경이 필요하면 고유 임시 경로를 만들며 다른 작업의 venv를 삭제·재생성하지 않는다.

## 실제 agent 탐색

[평가 절차](references/agent-navigation-evaluation.md)를 따른다. 같은 fixture 내용과 작업에 대해 적용 전/후를 별도 fresh session으로 수행한다. 근거 문서와 코드 선택, 실제 검사 명령/exit/output, 과거·제안·현재 구분을 기록한다. PLAN-0007에서 관찰한 이전 template 생성물의 결과는 현재 UX template의 향상 근거로 재사용하지 않는다.

일회성·단일 모델·작은 fixture의 결과는 보편적 성능 보장이 아니다. 적용 전에도 성공했다면 성공률 향상이라고 주장하지 않는다. 자기 보고 경로는 관찰 가능한 명령/결과와 구분한다. 평가 권한은 프롬프트로 제한되며 OS sandbox를 제공했다고 주장하지 않는다.

## 독립 검토

경로/소유권/transaction/packaged asset/CI 변경은 별도 context에서 exact candidate를 반증한다. 수락 기준, trigger, 영향, 재현 근거를 제시하고 수정 후 새 후보를 재검증한다. 테스트의 가정도 검토한다. 독립 검토를 수행하지 않았다면 명시한다.

## 완료와 릴리즈

Main은 대상 base와 변경 fingerprint 또는 commit, 환경, 실제 명령/결과, 독립 검토와 문서 영향을 기록한다. 자체 Gate나 `close-plan`은 사용하지 않는다. 문서 이동은 의미적 승인이나 검사 성공을 대신하지 않는다. CI는 소스 제품 검사를 실행하며 배포하지 않는다. 이 버전의 공개 게시나 이전 release 교체는 별도 권한이다.

## 알려진 한계

대규모/비정형 저장소, 반복 시행, 다중 모델, 실제 코드 수정 작업의 일반적 효과는 별도 근거가 필요하다. 범위 제한 inventory와 기계적 링크 점검은 완전한 Markdown 파서나 semantic judge가 아니다. 초기화 도구가 프로젝트 자체의 테스트/CI/보안 검사를 대신하지 않는다.
