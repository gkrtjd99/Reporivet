# Source contract authoring

This source repository authors its portable operating contract in the block below.
Edit this block, then run `./dev/agent-contract-sync`; do not edit `AGENTS.md` directly.
`./dev/agent-contract-sync --check` detects drift without writes. Provider-specific
instructions outside the block are not projected. Generated target repositories
keep AGENTS canonical and do not receive this source-only tool or CLAUDE file.

<!-- reporivet:portable:start -->
<!-- reporivet:start -->
# Reporivet 작업 진입점

Reporivet은 프로젝트의 기존 문서·코드·검사 방법으로 연결되는
작은 진입점을 만드는 도구다.

## 작업에 필요한 근거

- 문서 지도와 현재/과거 구분: [`docs/README.md`](docs/README.md)
- 제품 목적과 요구사항: [`docs/PRODUCT.md`](docs/PRODUCT.md), [`docs/product-specs/SPEC-REPORIVET-003-agent-entrypoints.md`](docs/product-specs/SPEC-REPORIVET-003-agent-entrypoints.md)
- 구조와 모듈 경계: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- 설계 근거: [설계 문서 인덱스](docs/design-docs/index.md)
- 구현 원칙: [`docs/design-docs/core-beliefs.md`](docs/design-docs/core-beliefs.md)
- 파일 변경·소유권·보안 제약: [`docs/SECURITY.md`](docs/SECURITY.md)
- 검사 방법·검토·완료 기준: [`docs/QUALITY.md`](docs/QUALITY.md)
- 복잡하거나 위험한 변경의 계획: [`docs/PLANS.md`](docs/PLANS.md), [`docs/exec-plans/active/`](docs/exec-plans/active/)

## 문서 사용

- 현재 작업에 해당하는 문서와 연결된 근거만 읽는다.
- 상세 규칙은 여기 복제하지 않고 연결된 문서를 원본으로 삼는다.
- 과거 기록을 현재 요구사항으로 간주하지 않는다.
- 적용되는 근거가 충돌하면 충돌을 알리고 임의로 선택하지 않는다.

## 결정적 명령

- 소스 검사: `PYTHON=python3 ./dev/check`
- 휴대용 계약 투영: `./dev/agent-contract-sync` (소스 저장소 전용)
- 휴대용 계약 불일치 검사: `./dev/agent-contract-sync --check` (읽기 전용)
<!-- reporivet:end -->
<!-- reporivet:portable:end -->
