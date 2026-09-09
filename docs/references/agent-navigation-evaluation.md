---
id: REF-REPORIVET-005
kind: reference
status: active
owner: main
area: evaluation
---

# 실제 agent 탐색 평가

## 목적과 한계

Fresh agent가 진입점에서 현재 근거·구현·실제 검사 명령을 찾는지 관찰한다. 문서 schema 검사, semantic router, 모델 benchmark, 완료 Gate가 아니다. 제품에 runner·LLM 서비스·transcript 저장소를 추가하지 않는다.

**평가 provenance:** 아래 기록은 PLAN-0007 당시의 entrypoint template와 그 계획의 최종 후보를 대상으로 수행한 역사적 관찰이다. PLAN-0008에서 보수한 현재 UX template의 향상·효과를 검증한 결과가 아니며, 아래 성공·읽은 순서·hash·실험값을 현재 template의 근거로 재사용하지 않는다. 오래된 실험 값과 절차는 재현 가능한 역사로 보존한다.

## 재현 입력과 절차

[fixture-inputs.json](../../tests/fixtures/navigation/fixture-inputs.json)은 문서 배치가 서로 다른 Atlas와 Birch의 정확한 원본이다. 각 fixture에는 의도적으로 과거 값이 남은 코드와 실패하는 검사가 있다. 테스트 실패를 숨기거나 성공하도록 고치지 않는다.

소스 root에서 다음처럼 별도의 before/after 사본을 만든다. 이 명령은 평가 설명일 뿐 제품 실행 engine이 아니다.

```sh
python3 - <<'PY'
import json, pathlib, tempfile
data = json.loads(pathlib.Path("tests/fixtures/navigation/fixture-inputs.json").read_text(encoding="utf-8"))
root = pathlib.Path(tempfile.mkdtemp(prefix="reporivet-navigation-")).resolve()
for name, files in data.items():
    for phase in ("before", "after"):
        for relative, content in files.items():
            path = root / f"{name}-{phase}" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode("utf-8"))
print(root)
PY
```

1. Before에는 Reporivet을 적용하지 않는다. After에만 `init --name Atlas` 또는 `init --name Birch --claude`를 적용한다. 각 root를 명시하고 원본 bytes 보존을 확인한다.
2. 각 조건마다 별도의 fresh session을 배정한다. 같은 agent의 기억을 재사용하지 않는다. 해당 fixture만 읽고, 상위/다른 fixture/제품 소스/이전 결과는 보지 못하도록 지시한다.
3. 과제는 “만료 동작의 버그를 조사하고 현재 요구·구현·과거 근거·문서화된 로컬 검사와 실제 결과를 보고하라”다. 정답 값이나 올바른 문서 경로를 미리 주지 않는다.
4. AGENTS/CLAUDE가 있으면 거기서 시작하고, 없으면 README부터 읽도록 한다. 쓰기·설치·네트워크·재위임은 금지하며 문서에 명시된 통제 fixture 검사만 허용한다. 이것은 prompt 권한 제한이며 OS sandbox 제공을 뜻하지 않는다.
5. 읽은 순서, 짧은 인용, 요구값과 코드값, 실제 명령/cwd/exit/output을 기록한다. 선택 경로는 agent 자기 보고이며 Main의 bytes/명령 재확인과 구분한다.
6. 같은 진단 목표·원본·권한·모델 조건을 유지하되 prompt 문구의 byte-identical 통제, 속도/토큰 통제, 보편적 향상을 주장하지 않는다.

## 2026-09-08 PLAN-0007 역사 관찰

모델 배정은 네 세션 모두 Sonnet, 각 시간 예산은 4분이다. 검사 interpreter는 `/private/tmp/reporivet-py313-venv-EANM2w/bin/python -B`(Python 3.13.15)다. 이 interpreter의 isolated import에서 Reporivet은 설치되지 않은 것으로 확인됐다. 원본 JSON SHA-256은 `fb2f092a56663bd4c56f6b5e4e6f37ca98734ee0de15604fa7f256a16d2b3977`이다. Before/after target은 PLAN-0007 당시 template로 생성했다.

| Fixture | 현재 요구값 | 코드값 | 실제 검사 결과 |
|---|---|---|---|
| Atlas | 30분 | 45분 | exit 1, `session_minutes: expected=30 actual=45` |
| Birch | 120초 | 300초 | exit 1, `request_timeout_seconds: expected=120 actual=300` |

이 값은 프로젝트의 만료값이지 agent 세션의 제한 시간이 아니다. 네 세션 모두 현재와 과거 근거를 구분하고 같은 불일치를 올바르게 진단했다.

읽기 순서(각 fixture root 기준):

- Atlas before: `README.md` → `handbook/start.md` → `policies/session-rules.md` → `components/session.py` → `quality/check_session.py` → `archive/session-rules.md`.
- Atlas after: `AGENTS.md` → `README.md` → `policies/session-rules.md` → `components/session.py` → `quality/check_session.py` → `archive/session-rules.md` → `handbook/start.md`.
- Birch before: `README.md` → `engineering/knowledge/current.md` → `decisions/request-timeout.md` → `server/timeouts.py` → `notes/old-timeout.md` → `bin/verify_timeout.py`.
- Birch after: `AGENTS.md` → `CLAUDE.md` → `README.md` → `engineering/knowledge/current.md` → `decisions/request-timeout.md` → `server/timeouts.py` → `notes/old-timeout.md` → `bin/verify_timeout.py`.

각 cwd는 `/private/tmp/reporivet-navigation-ignda9rj/{atlas,birch}-{before,after}`이며 실행 명령은 위 interpreter 뒤에 Atlas의 `quality/check_session.py`, Birch의 `bin/verify_timeout.py`를 붙인 것이다. Main도 원본 bytes와 실제 실패 출력을 독립적으로 확인했다.

PLAN-0007의 최종 후보에 맞춘 생성물은 `/private/tmp/reporivet-final-navigation-ckx_w9i5`에 새로 생성했다. 기존 PLAN-0007 실험의 생성 bytes와 정확히 일치하고 doctor 검사를 통과했다. 이 일치는 당시 candidate의 재현성만 확인하며 PLAN-0008 현재 UX template의 결과나 향상을 입증하지 않는다.

- Atlas AGENTS SHA-256: `f8b36ae4de2da453e19ca43a6a529abb19886943b03b2daf299ffc54ffd96462`.
- Birch AGENTS SHA-256: `c6feca017f49eca36cd7f6ede5af748147fc75bbcd76e189ebce8311329ed625`.
- Birch CLAUDE SHA-256: `0b206945aeb4fb2a8880553ffa072d57fca98d50b4be6ed987148024cf20007b`.

## 결론

이 PLAN-0007의 작은 역사 실험은 당시 template 진입점에서 필요한 근거를 찾아 진단하는 동작을 관찰했다. **Before부터 두 fixture 모두 성공했으므로 추가 효과나 성공률 향상을 입증하지 않았다.** After는 오히려 읽은 파일이 각각 하나/둘 늘었다. 이 결과는 현재 UX template에 대한 성능·향상 주장이 아니다. 시간·토큰 효율 비교나 실제 코드 수정 성공은 평가하지 않았다. Atlas의 재인증 요구는 검사 범위 밖이며, Birch는 AGENTS를 먼저 읽었으므로 CLAUDE-only 시작의 성공도 별도로 입증하지 않았다.

이미 잘 연결된 저장소에는 추가하지 않는 것이 합리적이다. 여러 저장소·모델·반복 시행에서 구체적인 탐색 문제가 확인되기 전에는 이 관찰을 근거로 평가 서비스나 더 큰 실행 체계를 추가하지 않는다.
