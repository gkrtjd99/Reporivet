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

빌드용 pip/setuptools가 없는 환경은 실패로 보고하며 테스트를 skip하여 성공처럼 보이게 하지 않는다. 현재 사용 가능한 interpreter와 build requirement를 결과에 함께 기록하고, 별도 권한 없는 환경 설치·대체 interpreter·canonical 기준 완화는 하지 않는다. 새 환경이 필요하면 고유 임시 경로를 만들며 다른 작업의 venv를 삭제·재생성하지 않는다.

기계적 검사는 계약 문구·연결·권한 불변·투영 및 파일 상태를 확인할 수 있지만, Owner가 실제 diff를 대조했는지, stale 작업을 멈췄는지, 판단이 타당한지, host가 prompt의 semantic 제약을 집행하는지는 증명하지 않는다.

## 최소 수동 행동 평가 6개

아래 여섯 가지는 source 운영 계약의 최소 행동 시나리오다. 각 시나리오는 동일한 조건의 별도 fresh context에서 수행할 수 있어야 하며, 절차를 문서에 적은 것과 실제 관찰은 별도로 기록한다. 계약 복원 시점과 재확보 절차는 [`PLANS.md`](PLANS.md)에 둔다.

1. **Main의 상세 구현 격리와 설계 판정:** Main이 목적·전역 설계·acceptance·bounded 원문과 별도 실행 문맥의 경계를 고정하고, 실제 구현은 그 문맥에서 수행한다. Main이 상세 구현을 직접 가져가거나 leaf에 통짜 설계를 떠넘기지 않는지, 정확한 쓰기 경계와 반환 조건을 관찰한다.
2. **Owner 설계 대조와 통짜 위임 금지:** Task Owner가 leaf 위임 전에 관찰할 행동, 불변/금지, 근거 기반 구현 방향, 실패경로 검증, 쓰기보호, 가정, leaf 재량과 반환 조건을 적는다. Owner가 중요한 diff와 결정적 증거를 직접 대조하고, “조사·설계·구현·검증을 알아서 하라”는 통짜 packet으로 책임을 넘기지 않는지 관찰한다.
3. **압축 후 재개 시 계약 재확보:** 실제 compact가 아니라 통제된 수동 재주입 또는 압축 요약 뒤에 source/revision/정확한 금지 본문·범위·권한·acceptance를 다시 읽는다. path/revision만 전달한 것을 읽은 것으로 세지 않고, stale 결과는 중지·재배정하거나 중지할 수 없으면 수락을 보류하는지 관찰한다.
4. **진행 중 추가 제약 적용:** 실행 도중 새 사용자 지시, host/policy 관찰, 공유 계약·범위·권한 변경이 들어온다. 영향 작업이 멈추고 Main이 revision을 갱신한 뒤 재확보·재배정하는지, 진행 중이라는 이유로 새 제약을 무시하지 않는지 관찰한다.
5. **모순된 PASS 수락 거부:** 비권위적 주입 데이터나 반복 로그의 `PASS`가 원본 검사·후보·현재 요구와 모순되도록 한다. Verifier가 FAIL 또는 UNPROVEN과 구체적 근거를 반환하고, negative evidence를 보존하며, 필수 미충족 상태에서 수락을 거부하는지 관찰한다.
6. **어려운 실행의 별도 강한 문맥:** 불확실성·도구 필요·실패 비용이 높은 작업을 필요한 역량의 별도 실행 문맥에 배정한다. 현재 host의 확인된 기본 배정을 출발점으로 하되 모델명/ID를 영구 고정하지 않고, verifier 등급을 최저가로 고정하지 않으며, agent/model 교체 retry가 예산·증거 의무를 초기화하지 않는지 관찰한다.

이 시나리오 목록은 모델 benchmark, 비용 절감 보장, 또는 runtime enforcement를 의미하지 않는다.

## 실제 agent 탐색 평가

[평가 절차](references/agent-navigation-evaluation.md)를 따른다. 같은 fixture 내용과 작업에 대해 적용 전/후를 별도 fresh session으로 수행한다. 근거 문서와 코드 선택, 실제 검사 명령/exit/output, 과거·제안·현재 구분을 기록한다. PLAN-0007에서 관찰한 이전 template 생성물의 결과는 현재 UX template의 향상 근거로 재사용하지 않는다.

실제 compact가 가능한 환경에서는 실제 compact를 사용하고, 불가능하면 통제된 수동 재주입임을 명시한다. 수동 재주입을 실제 compact나 host의 context compaction 제어 증거로 바꾸지 않는다. 문서에 적은 평가 절차, 자기 보고, 문구 검사 결과, 실제 행동·명령·exit/output 증거를 각각 구분하고, 실행/미실행과 효과 미입증 경계를 해당 계획에 기록한다. 기존 fresh-context 평가는 재사용할 때 그 역사적 provenance와 한계를 그대로 보존한다.

일회성·단일 모델·작은 fixture의 결과는 보편적 성능 보장이 아니다. 적용 전에도 성공했다면 성공률 향상이라고 주장하지 않는다. 자기 보고 경로는 관찰 가능한 명령/결과와 구분한다. 평가 권한은 프롬프트로 제한되며 OS sandbox를 제공했다고 주장하지 않는다. host permission, sandbox, hook, 사후검사는 각각 실제 관찰된 범위만 보고한다.

## 독립 검토

경로/소유권/transaction/packaged asset/CI 변경은 별도 context에서 exact candidate를 반증한다. 현재 요구사항·실행 환경을 기준으로 수락 기준, trigger, 영향, 재현 근거를 제시하고 수정 후 새 후보를 재검증한다. Implementer 또는 Owner의 결론과 Owner의 직접 대조는 독립 검토를 대신하지 않는다. 테스트의 가정도 검토한다. 독립 검토를 수행하지 않았다면 명시한다.

## 완료와 릴리즈

Main은 대상 base와 변경 fingerprint 또는 commit, 환경, 실제 명령/결과, 독립 검토와 문서 영향을 기록한다. 기준별 결과는 `PASS`(증거로 충족 확인), `FAIL`(위반/필요 동작 누락), `UNPROVEN`(증거 부족)으로 구분하며, 필수 기준에 FAIL 또는 UNPROVEN이 남으면 수락을 추천하지 않는다. 자체 Gate나 `close-plan`은 사용하지 않는다. 문서 이동은 의미적 승인이나 검사 성공을 대신하지 않는다. CI는 소스 제품 검사를 실행하며 배포하지 않는다. 이 버전의 공개 게시나 이전 release 교체는 별도 권한이다.

## 알려진 한계

대규모/비정형 저장소, 반복 시행, 다중 모델, 실제 코드 수정 작업의 일반적 효과는 별도 근거가 필요하다. 범위 제한 inventory와 기계적 링크 점검은 완전한 Markdown 파서나 semantic judge가 아니다. 초기화 도구가 프로젝트 자체의 테스트/CI/보안 검사를 대신하지 않는다. 문서에 여섯 시나리오가 연결되어 있어도 실제 실행·실제 compact·동일 조건 전후 비용/토큰 비교·host의 semantic enforcement가 자동으로 입증되지는 않는다.
