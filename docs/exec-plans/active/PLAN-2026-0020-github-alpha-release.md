---
id: PLAN-2026-0020
kind: exec-plan
status: active
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
- [ ] 전체 검사·독립 검토·커밋·PR CI·merge commit CI.
- [ ] 정확한 wheel 및 공개 prerelease 생성·원격 검증.

## Validation and Evidence

macOS Python 3.13 전체 검사 76개 통과(비 UTF-8 실파일 테스트 1개는 파일시스템 제한으로 건너뜀). 독립 재현에서 Linux의 비 UTF-8 실파일과 초기화 실패 복구, preview/apply 일치를 확인했다. 계약 투영 검사와 actionlint 통과. 후보 SHA와 실제 CI·artifact·원격 결과는 실행 후 기록한다.
