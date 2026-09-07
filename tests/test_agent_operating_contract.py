from __future__ import annotations

import re
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return match.group(0).strip()


def task_blocks(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^### (T[0-9A-Za-z_-]+) — .+$", text, re.MULTILINE))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[match.group(1)] = text[match.start() : end]
    return blocks


class AgentOperatingContractTests(unittest.TestCase):
    maxDiff = None

    def read(self, relative: str) -> str:
        return (REPOSITORY / relative).read_text(encoding="utf-8")

    def test_source_and_packaged_agent_role_contracts_match(self) -> None:
        source = section(self.read("AGENTS.md"), "Agent operating roles")
        packaged = section(
            self.read("src/reporivet/assets/project/root/AGENTS.md.tmpl"),
            "Agent operating roles",
        )
        self.assertEqual(source, packaged)

        normalized = source.casefold()
        for required in (
            "main → task lead → leaf",
            "explicitly designated task lead",
            "must not delegate",
            "implementer",
            "independent verifier",
            "scope, non-goals, acceptance criteria, permissions",
            "plan writing and lifecycle",
            "final integration",
            "completion approval",
            "required capabilities, tool access, concurrency, retry, and time budget",
            "allowed writes are a subset of the parent",
            "inherited unchanged",
            "without further approval for each leaf",
            "execution stays within the parent budget",
            "must not be used to bypass a denied action",
            "lead의 역할은 상위 계약 안의 leaf 분해·경계 설계·packet 구성과 배정",
            "scheduling leaf work, coordinating repairs, consolidating results로 제한한다",
            "lead cannot change permissions or plan state",
            "edit the durable execplan, perform final integration, or approve acceptance",
            "memory is auxiliary",
        ):
            self.assertIn(required, normalized)
        for provider_name in ("claude", "anthropic", "openai", "chatgpt", "gemini"):
            self.assertNotIn(provider_name, normalized)

    def test_source_and_packaged_plan_role_and_result_contracts_match(self) -> None:
        source = self.read("docs/PLANS.md")
        packaged = self.read("src/reporivet/assets/project/docs/PLANS.md.tmpl")
        for heading in ("Operating roles and delegation", "Result prose contract"):
            self.assertEqual(section(source, heading), section(packaged, heading))

        roles = section(source, "Operating roles and delegation").casefold()
        for required in (
            "main → task lead → leaf",
            "only an explicitly designated task lead",
            "leaf agents cannot delegate",
            "scheduling",
            "repair coordination",
            "consolidating leaf results",
            "without new approval for each leaf",
            "allowed writes are a subset of the parent",
            "inherited unchanged",
            "scope changes return to main",
            "execution stays within the parent budget",
            "must not be used to bypass a denied action",
            "lead의 역할은 상위 계약 안의 leaf 분해·경계 설계·packet 구성과 배정",
            "consolidating leaf results and status로 제한",
            "lead cannot change acceptance, permissions, or plan state",
            "edit the durable execplan, perform final integration, or approve completion",
            "focused verification",
            "canonical verification",
            "separate worktrees",
            "disjoint write paths",
            "frozen shared interfaces",
            "fresh verification",
        ):
            self.assertIn(required, roles)

        result = section(source, "Result prose contract").casefold()
        for required in (
            "exact target commit sha",
            "execution environment",
            "commands run",
            "verification scope",
            "result",
            "evidence",
            "blockers",
            "approval",
            "independent verification was not performed",
        ):
            self.assertIn(required, result)

    def test_execplan_templates_capture_execution_constraints_and_result_evidence(self) -> None:
        paths = (
            "docs/exec-plans/_template.md",
            "src/reporivet/assets/project/docs/exec-plans/_template.md.tmpl",
        )
        texts = [self.read(path) for path in paths]
        self.assertEqual(texts[0], texts[1])

        blocks = task_blocks(texts[0])
        self.assertEqual(set(blocks), {"T1", "T2", "T3"})
        for task_id, block in blocks.items():
            with self.subTest(task=task_id):
                self.assertIn("#### Execution constraints", block)
                constraints = block.split("#### Execution constraints", 1)[1].split("####", 1)[0]
                for field in (
                    "Required capabilities",
                    "Tool access",
                    "Concurrency",
                    "Retry budget",
                    "Time budget",
                ):
                    self.assertIn(field, constraints)
                self.assertNotRegex(
                    constraints.casefold(),
                    r"\b(?:claude|anthropic|openai|chatgpt|gemini)\b",
                )

                result = block.split("#### Result", 1)[1].split("\n## ", 1)[0].casefold()
                for field in (
                    "status",
                    "exact target commit sha",
                    "changed paths",
                    "execution environment",
                    "commands run",
                    "verification scope",
                    "results and evidence",
                    "blockers",
                    "approval",
                ):
                    self.assertIn(field, result)

        verifier = blocks["T3"].casefold()
        self.assertIn("independent context", verifier)
        self.assertIn("not performed", verifier)

    def test_decomposition_ownership_and_shared_contract_change_protocol(self) -> None:
        contracts = {
            "agents": section(self.read("AGENTS.md"), "Agent operating roles"),
            "plans": section(self.read("docs/PLANS.md"), "Operating roles and delegation"),
            "template": section(
                self.read("docs/exec-plans/_template.md"), "Interfaces and Dependencies"
            ),
        }
        for name, contract in contracts.items():
            with self.subTest(contract=name):
                for required in (
                    "Main은 Task 간 공유 인터페이스·경로 소유권·의존성·통합 순서를 설계한다",
                    "상위 계약 안의 leaf 분해·경계 설계",
                    "공유 계약은 병렬 수행 동안 고정한다",
                    "변경이 필요하면 영향 작업을 멈추고",
                    "경계 소유자(Main: Task 간, Lead: parent 내부)가 계약을 조정한 뒤 재배정한다",
                    "parent 범위·계약·권한 변경은 Main에게 반환한다",
                    "host/project의 더 제한적인 병렬 정책을 완화하지 않으며",
                    "독립 경계를 만들 수 없으면 순차 수행한다",
                ):
                    self.assertIn(required, contract)
                self.assertNotIn("Beyond composing those packets", contract)

    def test_retired_source_design_routes_to_preserved_authorities(self) -> None:
        self.assertFalse((REPOSITORY / "docs/DESIGN.md").exists())
        for path in ("AGENTS.md", "CLAUDE.md", "docs/README.md", "docs/design-docs/index.md"):
            text = self.read(path)
            self.assertNotRegex(text, r"\]\([^)]*(?:/|\b)DESIGN\.md\)")
            self.assertIn("core-beliefs.md", text)
        roles = section(self.read("AGENTS.md"), "Agent operating roles")
        self.assertIn("상위 계약 안의 leaf 분해·경계 설계", roles)
        self.assertIn("edit the durable ExecPlan, perform final integration, or approve acceptance", roles)
        self.assertIn("Repository as operating environment", self.read("docs/design-docs/core-beliefs.md"))
        self.assertIn("UTF-8", self.read("docs/PRODUCT.md"))
        self.assertIn("Required failure takes precedence", self.read("ARCHITECTURE.md"))

    def test_investigation_invariants_and_source_templates_match_targets(self) -> None:
        for source, target, heading in (
            ("AGENTS.md", "src/reporivet/assets/project/root/AGENTS.md.tmpl", "Engineering invariants"),
            ("docs/PLANS.md", "src/reporivet/assets/project/docs/PLANS.md.tmpl", "Required properties"),
        ):
            self.assertEqual(section(self.read(source), heading), section(self.read(target), heading))
        invariants = section(self.read("AGENTS.md"), "Engineering invariants")
        for required in ("normative", "reason", "scope", "prevented failure", "repository and dependency capabilities",
                         "official primary sources", "no-change", "practical alternatives", "rejection reasons",
                         "verification/enforcement", "revisit/retirement"):
            self.assertIn(required, invariants)
        for relative in ("design-docs/_template.md", "decisions/_template.md"):
            self.assertEqual(self.read("docs/" + relative),
                             self.read("src/reporivet/assets/project/docs/" + relative + ".tmpl"))

    def test_verifier_falsification_and_evidence_based_findings(self) -> None:
        plans = self.read("docs/PLANS.md")
        verifier = task_blocks(self.read("docs/exec-plans/_template.md"))["T3"]
        contracts = {
            "agents": (section(self.read("AGENTS.md"), "Agent operating roles"),) * 2,
            "plans": (
                section(plans, "Operating roles and delegation"),
                section(plans, "Result prose contract"),
            ),
            "template": (
                verifier.split("#### Verify", 1)[1].split("#### Stop conditions", 1)[0],
                verifier.split("#### Result", 1)[1].split("\n## ", 1)[0],
            ),
        }
        for name, (verification, result) in contracts.items():
            with self.subTest(contract=name):
                self.assertIn("반례·실패 경로·회귀를 능동적으로 찾고", verification)
                self.assertIn("테스트 자체의 가정도 의심한다", verification)
                self.assertIn("수정 후에는 새 exact candidate를 재검증한다", verification)
                self.assertIn("위반한 요구사항·trigger·영향", result)
                self.assertIn("재현 또는 구체적인 코드 근거를 제시한다", result)
                self.assertIn("우려·취향·미검증 영역은 결함과 구분", result)
                self.assertIn("결함 개수를 강제하지 않는다", result)

    def test_knowledge_maps_explain_explicit_plan_selection_without_changing_taxonomy(self) -> None:
        source = self.read("docs/README.md")
        packaged = self.read("src/reporivet/assets/project/docs/README.md.tmpl")
        guidance = (
            "With no `--plan`, context reports that no plan is selected; inspect "
            "[`exec-plans/active/`](exec-plans/active/) and rerun with `--plan PLAN-...` "
            "when a matching plan exists. It does not select or reveal an active plan automatically."
        )
        self.assertIn(guidance, source)
        self.assertIn(guidance, packaged)
        self.assertIn("Product outcome and trade-off principles", packaged)
        self.assertNotIn("Product outcome and trade-off principles", source)


if __name__ == "__main__":
    unittest.main()
