---
id: REF-REPORIVET-004
kind: reference
status: active
owner: main
area: migration
---

# 진입점 전환과 파일 관리

## 제품 경계

미출시 `0.3.0.dev1`은 v0.2 관리 runtime·버전 marker·운영 블록을 발견하면 쓰기 전에 거부합니다. 기존 target을 삭제·변환·재실행하거나 호환 fallback을 제공하지 않습니다. 공개된 v0.2.0과 기존 target을 그대로 계속 사용할 수도 있습니다.

새 패키지 설치는 기존 target의 migration이 아닙니다. 전환은 target 관리자가 소유하는 별도 검토 변경입니다. 패키지 제거와 문서 제거도 별개입니다. Reporivet을 uninstall해도 target 파일은 남으며, 진입점 안내를 제거한다고 프로젝트의 다른 도구를 제거할 필요는 없습니다.

## 공식 저장소와 checkout 문서 구분

공식 source root는 [github.com/gkrtjd99/Reporivet](https://github.com/gkrtjd99/Reporivet)입니다. Legacy 오류는 이 위치와 수동 조치를 안내하며, 미출시 문서가 remote default branch에 이미 있다고 주장하지 않습니다. 이 문서는 **source checkout 안의** `docs/references/entrypoint-migration.md`이며 target이나 wheel에는 설치되지 않습니다.

## v0.3 관리 블록 수동 제거

자동 제거 명령은 없습니다. 먼저 두 파일의 실제 본문과 연결을 읽고 소유권을 확인하세요. 다음 정확한 standalone marker 쌍과 그 내부만 검토해 제거합니다.

- AGENTS.md: `<!-- reporivet:entrypoints:start -->`부터 `<!-- reporivet:entrypoints:end -->`까지.
- CLAUDE.md: `<!-- reporivet:entrypoints:claude:start -->`부터 `<!-- reporivet:entrypoints:claude:end -->`까지.

블록 앞뒤의 사용자 bytes와 지침을 보존합니다. 사용자 내용이 섞인 파일 전체를 삭제하지 마세요. AGENTS 안내와 선택적 CLAUDE 연결은 같은 변경에서 검토하여 끊어진 연결을 남기지 않고, 사용자 소유 CLAUDE 본문은 유지합니다. 잘못되거나 중복된 marker, 들여쓰기·fence 안의 예시·부분 marker를 실제 소유 영역으로 추측하여 삭제하지 마세요. 소유 범위가 불명확하면 수동 검토로 먼저 해결합니다. 제거 후에는 target 자체의 관련 검사를 수행합니다.

## v0.2 target의 별도 전환 절차

1. Target의 기존 도구로 현재 파일 소유권과 CI·명령 의존성을 확인합니다. 이름이 같다는 이유로 Reporivet 소유라고 가정하지 않습니다. Runtime·wrapper·CI 제거에는 target 관리자의 별도 호환성 검토가 필요합니다.
2. 기존 문서 구조와 진입점을 유지하고 필요한 안내만 수정합니다. Reporivet 소스의 계획이나 runtime을 복사하지 않습니다.
3. 기존 marker·runtime·wrapper·버전 marker·설정의 제거 변경에 별도 명시적 권한을 받고, 사용자 내용과 CI 의존성을 보존·정리한 뒤 검증합니다. 이 작업을 패키지 설치나 자동 초기화에 끼워 넣지 않습니다. Legacy 흔적이 남으면 새 CLI는 계속 거부합니다.
4. 검토된 전환 이후 새 블록의 preview를 확인하고 적용합니다. 다음 명령은 설치된 새 CLI를 사용하는 예시입니다. CLAUDE를 원할 때는 양쪽 명령에 `--claude`를 명시합니다.

   ```sh
   reporivet init --root ./target --claude --dry-run
   reporivet init --root ./target --claude
   reporivet doctor --root ./target
   ```

5. Fresh agent가 결과 진입점에서 실제 target 작업을 수행하게 하고 선택한 근거와 프로젝트 자체 검사 결과를 기록합니다. 경로 존재를 authority로 취급하지 않습니다.
6. 문제 발생 시 검토한 전환 commit을 되돌리거나 국소 수정합니다. 무관한 사용자 작업을 버리는 reset은 사용하지 않습니다.

## v0.3 문서를 옮긴 뒤 갱신

관찰 목록은 자동 갱신되지 않습니다. 사용자 지침은 marker 밖에 두고, 설치된 CLI로 다음 순서로 확인합니다.

```sh
reporivet upgrade --root ./target --claude --dry-run
reporivet upgrade --root ./target --claude
reporivet doctor --root ./target
```

`--claude`를 생략하면 CLAUDE 블록은 생성·갱신하지 않습니다. 관리 블록 안의 직접 편집은 재생성 때 대체됩니다. 패키지가 없어도 일반 Markdown으로 수동 관리할 수 있습니다.

Preview는 실제 예정 본문을 보여주지만 제어문자를 escape한 **사람 검토용 diff**이며 적용 가능한 patch로 보장하지 않습니다. 기존 instruction 내용과 주변 문맥이 포함될 수 있으므로 공유 전에 비밀값을 확인하세요. 파일 내용을 출력하지 않는 `audit`와는 다릅니다. Fingerprint는 승인이나 잠금이 아니며 입력이 바뀌면 preview부터 다시 확인해야 합니다.

## 제거된 CLI 옵션

공개된 **v0.2.0 CLI**와 비교해 다음을 제거했습니다.

- `define` 및 해당 명령의 `--adopt`, `--dry-run`
- `init --summary`, `--project-kind`, `--capability`, `--primary-language`, `--runtime`
- `init --with-ci`, `--no-baseline-plan`, `--skip-check`
- `upgrade --with-ci`, `--skip-check`

남은 명령은 `init`, `audit`, `upgrade`, `doctor`입니다. 정확한 옵션은 각 명령의 `--help`에서 확인합니다.

## 복구 한계

Initializer의 파일 보호와 rollback은 자기 관리 영역의 한정된 쓰기에만 적용됩니다. 사용자 파일 삭제를 허가하거나 백업 저장소를 제공하지 않으며 무관한 동시 변경의 복구를 보장하지 않습니다. 수락 전에 정확한 대상·target diff·사용자 소유 CI를 함께 검토하세요.
