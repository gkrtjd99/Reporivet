from __future__ import annotations

import re
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
START = "<!-- reporivet:portable:start -->"
END = "<!-- reporivet:portable:end -->"


def portable(text: str) -> str:
    match = re.search(r"<!-- reporivet:portable:start -->\n(?P<body>.*?)<!-- reporivet:portable:end -->", text, re.DOTALL)
    if match is None:
        raise AssertionError("missing portable contract")
    return match.group("body")


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return match.group(0).strip()


class AgentOperatingContractTests(unittest.TestCase):
    maxDiff = None

    def read(self, relative: str) -> str:
        return (REPOSITORY / relative).read_text(encoding="utf-8")

    def test_source_contract_projection_and_entrypoint_links(self) -> None:
        source = portable(self.read("CLAUDE.md"))
        agents = self.read("AGENTS.md")
        projected = portable(agents) if START in agents else agents
        self.assertEqual(source, projected)

        # Ensure all Markdown links in the entrypoint point to real files or directories
        links = re.findall(r"\[.*?\]\((.*?)\)", source)
        self.assertGreaterEqual(len(links), 5)
        for link in links:
            target = (REPOSITORY / link).resolve()
            self.assertTrue(target.exists(), f"Link in entrypoint does not exist: {link}")

        normalized = source.casefold()
        for required in (
            "작업에 필요한 근거",
            "문서 사용",
            "결정적 명령",
            "docs/readme.md",
            "docs/product.md",
            "architecture.md",
            "docs/security.md",
            "docs/quality.md",
            "docs/plans.md",
            "agent-contract-sync",
        ):
            self.assertIn(required, normalized)

        # Must not contain agent org chart / hierarchy dogma
        for forbidden in (
            "main → task owner → leaf",
            "task owner",
            "task lead",
            "separate required stronger execution context",
            "repair packet",
            "direct-implementation ratio",
            "call-count quota",
        ):
            self.assertNotIn(forbidden, normalized)

    def test_source_plan_policy_and_template_structure(self) -> None:
        plans = self.read("docs/PLANS.md")
        template = self.read("docs/exec-plans/_template.md")
        normalized_plans = plans.casefold()

        for required in (
            "current contract",
            "progress",
            "stop and escalate before",
            "verification and evidence",
            "recovery and completion",
            "exact candidate",
            "`pass`",
            "`fail`",
            "`unproven`",
            "no automatic gate",
        ):
            self.assertIn(required, normalized_plans)

        for forbidden in (
            "main → task owner → leaf",
            "operating roles and delegation",
            "six restoration points",
            "capability and host boundaries",
            "result prose contract",
            "repair packet",
            "./dev/close-plan",
            ".harness/runs",
        ):
            self.assertNotIn(forbidden, normalized_plans)

        normalized_template = template.casefold()
        for required in (
            "purpose / big picture",
            "current contract",
            "progress",
            "scope",
            "non-goals",
            "acceptance criteria",
            "approach and key changes",
            "architecture impact",
            "documentation impact",
            "validation and evidence",
        ):
            self.assertIn(required, normalized_template)

        for forbidden in (
            "owner design before delegation",
            "owner design checkpoint",
            "task packets",
            'bulk "implement and verify" delegation',
        ):
            self.assertNotIn(forbidden, normalized_template)

    def test_evidence_table_separates_verdict_from_approval(self) -> None:
        evidence = section(self.read("docs/exec-plans/_template.md"), "Validation and Evidence")
        rows = [line for line in evidence.splitlines() if line.startswith("|")]
        cells = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
        self.assertGreaterEqual(len(cells), 2)
        self.assertEqual(cells[0], [
            "Acceptance criterion", "Result", "Evidence path or note",
            "Verified candidate", "Human/reviewer approval",
        ])
        self.assertTrue(all(len(row) == len(cells[0]) for row in cells))
        self.assertTrue(any(row[:2] == ["AC-1", "UNPROVEN"] for row in cells[1:]))

    def test_quality_declares_navigation_and_product_criteria(self) -> None:
        quality = self.read("docs/QUALITY.md").casefold()
        for required in (
            "기계적 검사",
            "문서 탐색 및 제품 품질 평가",
            "문서 탐색",
            "현재·과거 구분",
            "제약 확인",
            "근거의 정직성",
            "불필요한 읽기 방지",
            "실제 agent 탐색 평가",
            "독립 검토",
            "완료와 릴리즈",
            "`pass`",
            "`fail`",
            "`unproven`",
        ):
            self.assertIn(required, quality)

        for forbidden in (
            "최소 수동 행동 평가 6개",
            "main의 상세 구현 격리와 설계 판정",
            "owner 설계 대조와 통짜 위임 금지",
            "어려운 실행의 별도 강한 문맥",
        ):
            self.assertNotIn(forbidden, quality)

    def test_current_documents_route_to_entrypoint_product_and_manual_evidence(self) -> None:
        self.assertIn("entrypoint-migration.md", self.read("README.md"))
        self.assertIn("SPEC-REPORIVET-003", self.read("docs/README.md"))
        self.assertIn("SPEC-REPORIVET-003", self.read("docs/PRODUCT.md"))
        self.assertIn("ADR-0002-entrypoint-only-boundary.md", self.read("ARCHITECTURE.md"))
        self.assertIn("agent-navigation-evaluation.md", self.read("docs/QUALITY.md"))
        self.assertIn("entrypoint-migration.md", self.read("docs/SECURITY.md"))

        for relative in (
            "docs/product-specs/SPEC-REPORIVET-001-generated-project.md",
            "docs/product-specs/SPEC-REPORIVET-002-project-definition-adoption-and-evidence-gate.md",
            "docs/design-docs/DESIGN-REPORIVET-001-initializer-and-runtime.md",
            "docs/design-docs/DESIGN-REPORIVET-002-project-definition-adoption-and-evidence-gate.md",
            "docs/module-contracts/MOD-HARNESS-RUNTIME.md",
            "docs/references/project-definition-protocol.md",
            "docs/references/harness-engineering-skill-migration.md",
        ):
            self.assertIn("status: superseded", self.read(relative), relative)

    def test_source_contract_does_not_force_target_runtime_or_packaged_schema(self) -> None:
        source = self.read("CLAUDE.md").casefold()
        for obsolete in (
            "dev/harness.py",
            "dev/harness.toml",
            "./dev/context",
            "./dev/define",
            "./dev/new-plan",
            "./dev/close-plan",
        ):
            self.assertNotIn(obsolete, source)
        self.assertNotIn("src/reporivet/assets/project/docs", source)
        self.assertFalse((REPOSITORY / "docs/generated/code-map.md").exists())
        self.assertFalse((REPOSITORY / "src/reporivet/assets/project/dev/harness.py").exists())
        self.assertFalse((REPOSITORY / "src/reporivet/assets/project/docs/PLANS.md.tmpl").exists())

        # Target template must not receive source-only contract sync or org policies
        tmpl = self.read("src/reporivet/assets/project/root/AGENTS.md.tmpl").casefold()
        self.assertNotIn("agent-contract-sync", tmpl)
        self.assertNotIn("main → task owner", tmpl)
        self.assertNotIn("execplan", tmpl)


if __name__ == "__main__":
    unittest.main()
