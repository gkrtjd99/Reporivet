---
id: PLAN-2026-0020
kind: exec-plan
status: completed
owner: main
area: release
created: 2026-11-27
updated: 2026-11-27
base_commit: "718021503e161931f0b9bda3155c9da8aed1c314"
---

# 0.3.0a1 GitHub 프리릴리즈

## Current Contract

- 근거: 사용자의 변경 커밋·CI 확인·README 개선·릴리즈 게시 요청, `docs/PRODUCT.md`, `docs/PLANS.md`, `docs/QUALITY.md`, `docs/SECURITY.md`. 현재 미커밋 사용자 변경을 포함하고 다른 PR·기존 v0.2 tag/release는 보호한다.
- 범위: 기존 변경 검토 및 재현된 결함 수정, 실제 배포 가능한 한·영 README, `0.3.0a1` 버전·메타데이터 정합, 새 브랜치/PR CI, main merge 후 exact SHA CI 및 GitHub 프리릴리즈의 wheel/sdist/checksum/검증 정보 게시. PyPI 게시와 기존 target 자동 변환은 포함하지 않는다.
- 수락 기준: source 전체 검사와 위험 파일 변경의 독립 검토가 통과한다. PR의 10개 matrix 검사와 merge commit의 main CI를 실제 확인한다. wheel은 검증된 exact commit에서 만들고 설치·제거·checksum을 검증하며 release tag·assets를 원격에서 재확인한다. README와 release notes에 알파·v0.2 비호환, 검증 범위·알려진 제한을 정확히 표시한다.
- 제약: 기존 release/tag를 이동하거나 덮어쓰지 않는다. 사용자 비밀과 원시 transcript를 게시하지 않는다. 실패나 미실행을 성공으로 보고하지 않는다. 인증 설정·다른 사용자의 변경/PR은 건드리지 않는다. 불가한 외부 조건은 정확히 보고한다.

## Progress

- [x] GitHub 권한, 기존 릴리즈 및 CI 트리거 확인. 현재 main은 base와 일치한다.
- [x] README·버전·보안 안내 정리, 재현된 파일 안전성 결함 수정.
- [x] 전체 검사·독립 검토·커밋·PR CI·merge commit CI.
- [x] 정확한 wheel 및 공개 prerelease 생성·원격 검증.

## Validation and Evidence

- PASS — 후보 `e195e88632b4d73df87dcb4bd3f8e3828ec6bcc1`을 별도 context에서 검토했다. Linux 비루트 Python 3.13 전체 검사 76개 통과(건너뜀 없음). macOS Python 3.13은 76개 중 75개 통과, 비 UTF-8 실파일 1개는 파일시스템 제한으로 건너뜀. 독립 재현에서 초기화 실패 복구, preview/apply 일치와 Linux 비 UTF-8 경로를 확인했고 수정 후 추가 차단 사항은 없었다. 계약 투영 검사와 actionlint도 통과했다.
- PASS — [PR #8](https://github.com/gkrtjd99/Reporivet/pull/8)의 [CI](https://github.com/gkrtjd99/Reporivet/actions/runs/45964271649)와 병합 커밋 `3487498129f1c955386aa3d4ed2054ee5cfdf42e`의 [main CI](https://github.com/gkrtjd99/Reporivet/actions/runs/45964375689)에서 Linux/macOS × Python 3.11–3.15 각 10개 job이 통과했다. 병합 커밋 tree는 검토 후보 tree와 같다.
- PASS — 병합 커밋의 git archive에서 wheel과 sdist를 빌드했다. Python 3.13 격리 환경에서 wheel 설치, version/audit/init/upgrade/doctor, 제거와 기존 파일 보존을 확인했다. 공개 [v0.3.0a1 prerelease](https://github.com/gkrtjd99/Reporivet/releases/tag/v0.3.0a1)의 tag가 병합 커밋을 가리키고, 원격 자산을 다시 내려받은 뒤 양쪽 SHA-256을 확인했다. README의 직접 URL로 별도 venv에 설치해 `0.3.0a1`을 확인했다.
- Artifact SHA-256: wheel `ac94fb8570a1a15da4114f557019a8fcc27c5903f4cf6180c4777a73dd5ee7da`; sdist `652731d353fec8491cb00c9c38d5d1ccd0528f9829ab30bdf66d378584fd864a`.
- UNPROVEN — 실제 프로젝트 전반의 에이전트 작업 성공률·비용 개선은 입증되지 않았다. Windows 지원, 완전한 경합 격리 및 ACL 통제는 제공하지 않으며 v0.2의 자동 이전도 없다. 프리릴리즈는 GitHub에서 배포하며 PyPI에 게시하지 않았다.
