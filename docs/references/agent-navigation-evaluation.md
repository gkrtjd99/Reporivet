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

**평가 provenance:** 2026-09-08 PLAN-0007 항목은 당시의 entrypoint template와 최종 후보를 대상으로 한 역사적 관찰이다. PLAN-0008에서 보수한 현재 UX template의 효과를 검증한 결과가 아니며 그 성공·읽은 순서·hash·실험값을 현재 template의 근거로 재사용하지 않는다. 2026-11-27 현재 template 실험은 아래에 별도로 기록한다.

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

## 2026-11-27 현재 UX template 전후 관찰

**결과:** 현재 template 적용 전후 모두 Atlas와 Birch의 현재 요구·과거 근거·구현 불일치 및 문서화된 검사의 실패를 정확히 보고했다. 이 두 작은 사례에서 추가 효과는 관찰되지 않았다. 적용 후 명시적 `Read` 호출은 각각 1회와 2회 늘었지만 검색 호출 수가 달랐고 단일 시행이므로 전체 비용이나 일반적 성능의 차이라고 결론짓지 않는다.

### 입력과 방법

- 입력 `tests/fixtures/navigation/fixture-inputs.json` SHA-256: `fb2f092a56663bd4c56f6b5e4e6f37ca98734ee0de15604fa7f256a16d2b3977`. 현재 작업 트리의 `AGENTS.md.tmpl` SHA-256: `d9b160c59feef1d8b687c49d99bcf4bd017ade32aeea6de61e4e5b9c14302aa5`. 템플릿과 미커밋 CLI 후보로 생성했으며 base commit만으로 그 전체 후보를 대신하지 않는다.
- 새 임시 root `/private/var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-current-eval-clean-r0kweuvj`의 별도 네 사본에 동일 원본을 작성했다. Atlas after에 `init --name Atlas`, Birch after에 `init --name Birch --claude`만 적용했다. 실행 전후 원본 6개씩 bytes와 파일 목록, 생성물 hashes 보존을 확인했다. Atlas AGENTS: `34aded12a5f594c4072ed1fcc93ddd519394bdf61accc9059a3a844f80aea940`; Birch AGENTS: `04b54c1ebb313ac62f38fa683dc4bf5baafdd38b267d28c3a8775a41cb2c47e0`; Birch CLAUDE: `0b206945aeb4fb2a8880553ffa072d57fca98d50b4be6ed987148024cf20007b`.
- 각 사본에서 Claude Code 2.1.332, `claude-fable-5-2`, Python 3.15.2로 별도 세션을 병렬 실행했다. 동일 프롬프트를 `claude -p` 인자로 전달하고 표준입력은 `DEVNULL`로 닫았다. 파일의 프롬프트 bytes SHA-256은 `e8bdf2f26d83486c20cc284ce18224bd13cfb5e315563ddac206fe7d5f37113a`이며 그 파일의 마지막 LF는 인자에 포함하지 않았다. CLI trace는 초기 사용자 메시지를 기록하지 않으므로 인자 밖 입력이 없었다는 사실을 trace만으로 독립 증명하지는 못한다.
- 세션은 `--restricted --strict-mcp-config --no-chrome --no-session-persistence --tools Read,Glob,Grep,Bash --permission-mode dontAsk --model fable --max-budget-usd 2 --output-format stream-json --verbose`를 사용했다. 해당 fixture의 `python3 -B` 검사 명령만 `--allowedTools`로 추가했다. 네 세션의 `sandbox_enabled`는 false다. 동일한 권한 설정으로 각각 대상 사본 root에서 시작했지만, prompt 제한이나 restricted 도구를 OS sandbox라고 주장하지 않는다. 사용자·프로젝트 설정을 무시하는 제한 모드이므로 일상적인 모든 에이전트 환경과 같지 않다.
- 최초 별도 네 세션은 최종 보고에서 실행용 Python 스크립트와 다른 fixture 이름을 입력으로 봤다고 밝혔다. 스크립트에 검사 경로가 포함되어 네 결과는 비교에서 **제외**했다. 실행기 표준입력 상속이 가능한 원인이나 최초 사용자 메시지 trace가 없어 단정하지 않는다. 위 재실행은 새 사본과 새 세션에서 `DEVNULL`을 사용했으며 최종 보고에 해당 스크립트 단서는 다시 나타나지 않았다. 제외한 첫 실행도 비용에 포함한다.

네 세션의 인자로 동일하게 전달하도록 구성한 프롬프트:

```text
이 저장소의 만료 동작 버그를 조사해 주세요. 현재 요구사항, 실제 구현, 과거 근거와 구분, 문서화된 로컬 검사 및 실행 결과를 보고하세요.
AGENTS.md 또는 CLAUDE.md가 있으면 거기서 시작하고, 둘 다 없으면 README.md에서 시작하세요. 해당 저장소 밖의 파일, 다른 실험, 제품 소스 및 이전 결과는 보지 마세요.
파일 수정·설치·네트워크·재위임은 하지 마세요. 문서에 명시된 이 저장소의 로컬 검사 명령을 실행할 권한은 있습니다. 다른 셸 명령은 사용하지 마세요.
읽은 파일 순서를 기록하고, 검사 명령·작업 디렉터리·종료 코드·출력을 실제 관찰대로 보고하세요. 실행하지 않은 것은 미실행이라고 표시하세요.
```

### 실제 관찰

| Fixture | 조건 | 정확한 진단·과거 구분 | 명시적 Read | Glob | 문서 검사 실제 결과 |
|---|---|---|---:|---:|---|
| Atlas | 적용 전 | 현재 30분 / 구현·과거 45분 | 6 | 2 | `python3 -B quality/check_session.py`, exit 1, `session_minutes: expected=30 actual=45` |
| Atlas | 적용 후 | 현재 30분 / 구현·과거 45분 | 7 | 1 | 동일 명령·exit·출력 |
| Birch | 적용 전 | 현재 120초 / 구현·과거 300초 | 6 | 1 | `python3 -B bin/verify_timeout.py`, exit 1, `request_timeout_seconds: expected=120 actual=300` |
| Birch | 적용 후 | 현재 120초 / 구현·과거 300초 | 8 | 2 | 동일 명령·exit·출력 |

Read 횟수는 trace의 명시적 호출이며 자동 주입되는 지침 읽기는 포함하지 않는다. 각 session은 우선 검사 뒤에 `echo`와 `pwd`를 덧붙인 복합 Bash 명령을 시도했으나 권한 설정이 거부했다. 그 후 정확한 문서 명령을 실행해 위 exit/output을 얻었다. Main도 각 fixture root에서 같은 검사와 결과를 별도 재확인했다. 네 trace에서 허용되지 않은 Bash 실행, 파일 쓰기 또는 재위임 호출은 관측되지 않았다. 이는 해당 trace의 범위에 대한 관찰이다.

호출 순서상 Atlas before는 README → handbook → 현재 규칙 → 과거 기록 → 구현 → 검사, after는 AGENTS → README → handbook → 현재 규칙 → 과거 기록 → 구현 → 검사였다. Birch before는 README → 현재 지식 → 승인 결정 → 과거 기록 → 구현 → 검사, after는 AGENTS → CLAUDE → README → 현재 지식 → 승인 결정 → 과거 기록 → 구현 → 검사였다. 여러 `Read`는 병렬 호출로 보고됐으므로 나열 순서는 실제 완료 순서가 아니다. Birch의 CLAUDE만으로 시작하는 흐름은 별도 실험하지 않았다.

Claude CLI가 표시한 목록가 기준 비용은 유효 네 실행 합계 약 `$0.854`, 제외한 최초 네 실행까지 약 `$1.737`이다. 이는 실제 청구액이 아니며 cache·동시 실행·단일 시행을 통제하지 않아 전후 절감이나 인과효과로 해석하지 않는다. 원시 trace는 위 고유 임시 root에만 있고 저장소에는 포함하지 않는다.

**한계:** 두 fixture는 작고 명시적 Glob 탐색으로 파일 전체를 찾을 수 있어 실제 대형 저장소나 코드 수정 성공을 대표하지 않는다. 각 조건 한 번, 한 모델만 평가했다. 더 복잡한 실제 업무·반복·다중 모델 및 시간/비용의 통제 비교는 미실행이다. 개선이 입증되지 않은 결과와 개선이 없다고 일반화하는 결론은 다르다.

## 2026-11-27 관찰 목록 균형 변경 평가

**결과:** 루트의 일반 파일 90개로 목록이 포화된 두 합성 fixture에서 기존 목록은 `docs/README.md`를 누락했고, 개선된 목록은 두 경우 모두 포함했다. 다만 새 에이전트 여섯 세션은 목록이 없거나 문서가 목록에 없는 경우에도 별도 탐색으로 이 문서를 읽었고 모두 같은 버그를 정확히 진단했다. 이 시험은 **목록 누락의 기계적 완화는 확인했지만 실제 진단 향상은 관측하지 못했다.**

### 입력과 조건

- 위 Atlas/Birch 원본 JSON(SHA-256 `fb2f092a56663bd4c56f6b5e4e6f37ca98734ee0de15604fa7f256a16d2b3977`)의 각 사본에 루트 파일 `bundle-000.txt`부터 `bundle-089.txt`까지 추가했다. 각 내용은 `Inventory item NNN; generated fixture filler.\n`이며 `NNN`은 3자리 숫자다.
- 각 사본의 `docs/README.md`는 `# 문서 안내\n\n프로젝트 문서의 시작점은 [유지보수 안내](LINK)입니다. 과거 내용의 적용 여부는 원문을 확인하세요.\n`이다. `LINK`는 Atlas에서 `../handbook/start.md`, Birch에서 `../engineering/knowledge/current.md`다. 두 fixture는 각각 원본 97개 파일이며 모든 조건에서 상대 경로·내용·mode가 같다. 이들은 실제 프로젝트가 아닌 합성 fixture다.
- 세 조건은 `no`(진입점 미생성), `old`(변경 전 관찰 구현), `new`(변경된 관찰 구현)다. 기존 initializer SHA-256 `33905f61d5f07cccbf17b8dec38b24777185b9d16c04c1b304a4c1250e48baf8`, 개선 후보 `56d149234988d0480486d3791555a5f273da7c2d81fc342d3ae6ea31c46d3dae`. 둘 다 동일한 template SHA-256 `d9b160c59feef1d8b687c49d99bcf4bd017ade32aeea6de61e4e5b9c14302aa5`를 사용했다. Atlas는 AGENTS만, Birch는 `--claude`로 두 진입점을 생성했다.
- 각 조건에서 생성 전후 원본 파일의 상대 경로·mode·내용 hash로 만든 inventory hash는 Atlas `0a2d11e687fc5a4ef785a91852057dd7bc3fec70b301ee1268bb864195a8dfd6`, Birch `2dacc046de3001ab2e6c6cad4e7b4bb05448236f92a5eb304a8f5fce836cc893`로 동일했다. 실행 후에도 Main이 대조하고 각 fixture의 검사 결과를 독립 재실행했다.
- old/new 모두 생성 목록은 80개였다. old는 두 경우 `docs/README.md` 미포함, new는 포함했다. AGENTS SHA-256은 Atlas old `03b735840cdd1b16246adaf105f09769a081daa339c981540e6c9edf2ba37dea`, new `0c76f45829607a4a6ac4c6c599df290ebcfcd5f762b97c7c36fdae1761d1067f`; Birch old `07638f31810c850f8e997d48b4b0a6e7eb68faf074da69a1c250ed501f9231d6`, new `e249ace10202320ab714d37b01b8f90d44dce519371f8a26749d18a98d9aeb5f`다.
- 여섯 fresh 세션에 위 2026-11-27 평가와 같은 prompt(`prompt.txt` SHA-256 `e8bdf2f26d83486c20cc284ce18224bd13cfb5e315563ddac206fe7d5f37113a`, 마지막 LF 제외)를 인자로 주도록 구성하고 `stdin=DEVNULL`로 실행했다. 각 대상 root에서 Claude Code 2.1.332와 `claude-fable-5-2`, 동일한 restricted 도구·permission 설정·해당 fixture 검사 명령 allowlist를 사용했다. 시작 순서는 `birch-no`, `birch-new`, `atlas-old`, `atlas-new`, `birch-old`, `atlas-no`이며 병렬 실행했다. 각 `sandbox_enabled`는 false이고 초기 user 메시지는 trace에 없으므로 OS sandbox나 prompt의 전체 바이트가 독립 증명된 것으로 주장하지 않는다.
- 평가 root 및 원시 trace: `/private/var/folders/5w/7w1hw08s7gv4k7j8f57dslnw0000gn/T/reporivet-observe-eval-q7qft57l`. 보존된 CLI 기준 코드와 개선 후보, 세션별 JSONL 및 fixture manifest가 이 고유 임시 경로에 있다. 임시 파일은 지속 보관을 보장하지 않으며 제품에 포함하지 않는다.

### 실제 탐색 결과

| Fixture | 조건 | docs/README 목록 포함 | docs/README 실제 Read | 정확한 진단·검사 | Read / Glob / Grep 호출 |
|---|---|---|---|---|---:|
| Atlas | no | 해당 없음 | 예 | 예 | 8 / 2 / 0 |
| Atlas | old | 아니요 | 예 | 예 | 9 / 2 / 1 |
| Atlas | new | 예 | 예 | 예 | 8 / 2 / 2 |
| Birch | no | 해당 없음 | 예 | 예 | 8 / 2 / 1 |
| Birch | old | 아니요 | 예 | 예 | 10 / 2 / 2 |
| Birch | new | 예 | 예 | 예 | 10 / 2 / 1 |

모두 현재 요구와 폐기된 과거 근거를 구분해 Atlas는 현재 30분과 구현 45분, Birch는 현재 120초와 구현 300초의 불일치를 보고했다. Atlas의 문서화된 `python3 -B quality/check_session.py`는 exit 1과 `session_minutes: expected=30 actual=45`, Birch의 `python3 -B bin/verify_timeout.py`는 exit 1과 `request_timeout_seconds: expected=120 actual=300`을 실제 반환했다. 여섯 세션 모두 먼저 검사에 `echo` 또는 `pwd`를 덧붙여 허용되지 않은 Bash를 시도했고 거부된 후 문서 명령만 실행했다. 금지된 Bash 실행·파일 쓰기·재위임은 trace에서 관측되지 않았다.

Read는 명시적 도구 호출 수이며 지침 자동 주입과 `Grep`의 읽기는 포함하지 않는다. 이전 목록에서 빠진 문서를 모든 세션이 실제로 읽었으므로, 링크 포함 자체를 탐색 성공 향상으로 해석하지 않는다. 병렬 Read의 나열 순서 역시 실제 완료 순서는 아니다. 여섯 실행의 CLI 목록가 기준 비용은 합계 `$1.767475`이며 실제 청구액이 아니다. 병렬 실행·cache 및 조건별 각 한 번의 실행을 통제하지 않아 비용·시간 차이의 원인을 단정하지 않는다.

**한계:** 일반 파일 90개와 문서 진입점은 의도적으로 만든 사례다. 각 3조건은 한 번씩, 한 모델만 사용했고 실제 수정 작업은 평가하지 않았다. 개선 후 Birch 목록에도 `bin/verify_timeout.py`는 포함되지 않았다. 에이전트는 문서를 통해 이 검사 경로를 찾아 실행했지만, 문서 유사 경로와 그 외 경로 모두에서 특정 파일의 포함은 보장되지 않는다. 문서 유사 범주가 포화되거나 별도의 512개 방문·깊이 한도에 먼저 도달하면 중요한 문서도 여전히 빠질 수 있다. 실제 저장소·모델 전반의 탐색 성공이나 비용 개선은 미입증이다.
