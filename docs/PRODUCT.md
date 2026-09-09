---
id: PRODUCT
kind: product
status: active
area: product
summary: 기존 프로젝트 근거를 찾도록 돕는 runtime 없는 agent 진입점
---

# Product

## Purpose

Reporivet은 프로젝트의 기존 문서·코드·검사 방법을 agent가 찾아 쓰도록 짧은 진입점을 안전하게 구성한다. 다음 미출시 버전은 0.3.0.dev1이다. 공개 v0.2.0의 고정 문서 schema·copied runtime·Gate·계획 종료 모델은 [ADR-0002](decisions/ADR-0002-entrypoint-only-boundary.md)로 대체한다.

## Users and jobs

- 문서가 다양한 경로에 흩어진 저장소의 maintainer는 기존 지식을 복제하지 않고 진입점을 정리한다.
- 새 agent는 AGENTS 또는 실행 환경의 연결 문서에서 시작해 실제 근거·코드·검사 명령을 찾는다.
- 이미 Spec Kit/OpenSpec/Kiro 또는 자체 문서 체계가 있으면 그것을 그대로 사용한다. 이미 잘 연결되어 있으면 Reporivet을 추가하지 않아도 된다.

## Product boundary

Installed CLI는 `init`, `audit`, `upgrade`, `doctor`만 제공한다. target에는 AGENTS의 한정된 관리 블록과 선택적인 CLAUDE 연결만 작성한다. 프로젝트 문서군·설정·명령·CI·작업 상태를 생성하거나 대체하지 않는다. 패키지 제거 후에도 일반 Markdown과 프로젝트 자체 도구로 운영할 수 있다.

관찰된 파일 경로는 비권위적 참고 자료다. 어떤 문서가 현재 요구사항인지, 어떤 제안이 승인됐는지, 어떤 검사가 충분한지는 사용자와 agent가 근거를 읽어 판단한다. 생성된 경로 목록은 사용자를 별도 경로로 자동 routing하지 않는다. 관리 블록 밖의 사용자 지침은 프로젝트 소유이며 그곳에 의미적 routing을 직접 기록할 수 있다.

## Requirements

- **REQ-ENTRY:** 기존 파일 이름·배치·내용을 유지하면서 실제 경로로 연결한다. 문서 이름, frontmatter, ExecPlan schema를 강제하지 않는다.
- **REQ-OWN:** target 쓰기는 명시적인 AGENTS/선택적 CLAUDE 관리 블록으로 제한한다. 사용자 본문 bytes와 기존 mode를 보존한다. `upgrade`에서 CLAUDE 연결을 preview/apply하려면 두 실행 모두 `--claude`를 명시한다.
- **REQ-SAFE:** symlink/nonregular/잘못된 marker/동시 변경을 보수적으로 처리한다. 렌더링은 immutable preimage에 결속하고 rollback은 자기 postimage만 복원한다.
- **REQ-READ:** audit/doctor/preview는 target에 쓰지 않고 프로젝트 명령·파일 내용을 실행하지 않는다. 관찰 범위와 제외를 명시한다. audit은 내용 비출력이고 preview는 검토를 위해 본문이 포함될 수 있다.
- **REQ-PREVIEW:** init/upgrade dry-run은 immutable operation의 실제 before/after unified diff와 no-op을 표시한다. terminal 제어·방향 문자는 escaped human preview로 표시하며 출력은 적용 가능한 patch가 아니다. fingerprint는 승인·잠금·다음 실행 결과를 보장하지 않는다.
- **REQ-CHECK:** doctor는 기계적 경로·소유권 점검이다. 의미적 문서 정확성·agent 능력·작업 완료를 판정하지 않는다.
- **REQ-EVAL:** 진입점 품질은 실제 fresh agent의 근거 선택·작업 결과로 확인한다. 적용 전후 대조와 한계를 기록하고 향상이 없으면 그대로 보고한다. 이전 평가의 template 대상과 현재 UX template의 근거를 섞지 않는다.
- **REQ-MIGRATE:** 이전 runtime형 target은 자동 삭제/변환 없이 쓰기 전 거부한다. 기존 v0.2 release와 사용자 문서를 보존한다.

세부 수락 조건은 [SPEC-REPORIVET-003](product-specs/SPEC-REPORIVET-003-agent-entrypoints.md)에 있다.

## Non-goals

고정 문서 생성, 제품 정의 인터뷰/명세 작성 자동화, Task 분해·추적성 schema, Gate·완료 승인, copied runtime, command 실행 engine, secret scanner, CI 생성, agent 실행/감독 서비스, 모델 평가 API, telemetry, 원격 게시·배포는 제품 책임이 아니다. 프로젝트의 기존 도구와 운영 책임을 존중한다.

## Language and limits

파일은 UTF-8로 다루고 경로와 사용자 입력이 Markdown 구조를 깨지 않도록 처리한다. 제한된 inventory는 임의 구조의 완전한 의미적 이해가 아니다. 실험 fixture의 성공은 다른 모델·대규모 저장소·실제 업무 성능을 보장하지 않는다.
