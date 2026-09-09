---
id: SECURITY
kind: security
status: active
area: security
summary: 진입점 갱신의 파일 소유권과 읽기·쓰기 경계
---

# Security

## 신뢰 경계

호출자가 대상 root와 운영체제 권한을 선택한다. 기존 경로·instruction bytes·파일 이름은 신뢰하지 않는다. installed package는 로컬 산출물이며 프로젝트 명령, Python 모듈, 원격 콘텐츠를 실행하지 않는다. Audit은 파일 내용/자격증명을 출력하지 않는 제한된 경로 관찰이다. 경로명 자체에도 민감한 정보가 있을 수 있으므로 결과를 공유하기 전 검토한다.

## 보호 대상

- Target 쓰기는 AGENTS와 명시적으로 선택한 CLAUDE 관리 블록으로 제한한다.
- 관리 블록 밖의 bytes와 기존 파일 mode를 보존한다. 기존 README/SDD 문서/설정/CI/dev 경로는 수정하지 않는다.
- 경로 정규화 전에 symlink component를 검사한다. root/parent/대상 파일의 symlink, nonregular/FIFO, 잘못된 marker와 invalid UTF-8은 안전하게 거부한다.
- fenced marker 예시는 소유권을 부여하지 않는다. 실제 malformed/partial marker는 조용히 수선하거나 본문을 지우지 않는다.
- 렌더 전에 immutable preimage를 고정한다. user edit 이후 이미지를 새 preimage로 채택해 덮어쓰지 않는다.
- 원래 파일을 truncate하지 않고 완성된 임시 bytes/mode로 교체하며, 새 파일은 존재하면 실패하는 방식으로 생성한다.
- 실패 시 자기 postimage와 일치하는 대상만 되돌린다. concurrent 변경은 보존하고 복구 불완전을 명시한다.
- 경로와 project name을 Markdown으로 렌더링할 때 control/marker/링크 주입을 막는다. 임의 파일명을 shell command로 만들지 않는다.

## 기존 버전 전환

실제 v0.2 version/managed runtime/operating block을 확인하면 init/upgrade는 write 전 거부한다. 자동 삭제, runtime 재실행, 설정 변환, release 교체를 하지 않는다. [전환 안내](references/entrypoint-migration.md)를 따른다. 평범한 프로젝트의 동명 dev 설정만으로 Reporivet 소유권을 주장하지 않는다. v0.3 entrypoint 제거가 필요하면 정확한 두 managed marker pair(`<!-- reporivet:entrypoints:start -->` / `<!-- reporivet:entrypoints:end -->`, `<!-- reporivet:entrypoints:claude:start -->` / `<!-- reporivet:entrypoints:claude:end -->`)만 별도 검토로 제거하고, 혼합 파일의 사용자 본문과 AGENTS↔CLAUDE 연결은 함께 보존·정리한다.

## 미리보기와 기밀성

`init`/`upgrade --dry-run`은 immutable before/after에서 만든 실제 unified diff를 terminal escape와 함께 사람이 읽을 수 있게 출력한다. 이는 실행 가능한 patch가 아니며, fingerprint도 승인·잠금·재실행 결과를 보장하지 않는다. Preview에는 관리 블록의 기존 instruction 본문과 주변 문맥이 포함될 수 있으므로 외부 공유 전 비밀·개인정보를 검토한다. `audit`은 반대로 파일 내용을 출력하지 않는 제한된 경로 관찰이다. 두 출력의 content privacy와 audit 계약을 혼동하지 않는다.

## 기계적 점검과 의미적 승인

Doctor는 경로/관리 구조의 오류를 알릴 뿐 agent 능력이나 보안·제품 의미를 승인하지 않는다. 현재와 과거 문서의 구분, 충돌 해결, 명령 실행 권한과 작업 완료 판단은 사용자/agent의 실제 근거 검토에 남는다. 자동 Gate·승인 대체 점수는 없다.

## Source 운영

소스 CI의 action pin과 `contents: read`를 유지한다. 테스트는 자기 고유 임시 경로만 쓰며 기존 다른 작업의 환경을 삭제·재생성하지 않는다. 경로·소유권·file replacement·packaging·CI 변경에는 회귀와 독립 검토가 필요하다. 실제 agent 평가는 통제된 fixture와 최소 권한으로 수행하고 원시 transcript에 비밀값이 없는지 확인한다.

## 한계와 보고

파일 검사/preimage guard는 OS-level 완전한 race/process sandbox가 아니다. Git 상태나 preview fingerprint는 권한 부여가 아니다. 이 제품은 secret scanner나 프로젝트 CI를 설치하지 않는다. 기존 ignore/보안 도구는 프로젝트가 유지하며 비밀이 노출됐다면 폐기·회전한다. 이 소스의 과거 `.harness` 로그와 임시환경은 삭제하지 않고 기존 `.gitignore`를 보존한다. 이는 과거 raw log의 우발적인 추적·공개를 막기 위한 것으로, 새 run 상태나 runtime을 생성한다는 뜻이 아니다.

제보는 [보안 정책](../.github/SECURITY.md)을 따른다. 자격증명·비공개 저장소 내용·원시 로그를 공개 issue에 게시하지 않는다.
