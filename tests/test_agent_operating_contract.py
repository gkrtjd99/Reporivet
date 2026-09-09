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

    def test_source_contract_projection_and_roles(self) -> None:
        source = portable(self.read("CLAUDE.md"))
        projected = portable(self.read("AGENTS.md")) if START in self.read("AGENTS.md") else self.read("AGENTS.md")
        self.assertEqual(source, projected)

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
            "spec-reporivet-003-agent-entrypoints.md",
            "agent-contract-sync",
        ):
            self.assertIn(required, normalized)
        for provider_name in ("claude", "anthropic", "openai", "chatgpt", "gemini"):
            self.assertNotIn(provider_name, normalized)

    def test_source_plan_policy_preserves_roles_and_manual_boundary(self) -> None:
        plans = self.read("docs/PLANS.md")
        template = self.read("docs/exec-plans/_template.md")
        normalized = plans.casefold()
        for required in (
            "main → task lead → leaf",
            "only an explicitly designated task lead",
            "leaf agents cannot delegate",
            "scheduling",
            "repair coordination",
            "consolidating leaf results",
            "allowed writes are a subset of the parent",
            "inherited unchanged",
            "scope changes return to main",
            "execution stays within the parent budget",
            "must not be used to bypass a denied action",
            "focused verification",
            "independent verifier",
            "separate context",
            "independent verification was not performed",
            "exact target commit sha",
            "verification scope",
            "main or human approval",
            "no automatic gate",
        ):
            self.assertIn(required, normalized)
        template_normalized = template.casefold()
        for required in ("independently review", "separate context", "independent verification was not performed", "exact target commit sha", "verification scope", "main or human approval", "manual", "actual source or project-owned checks"):
            self.assertIn(required, template_normalized)
        self.assertNotIn("./dev/close-plan", plans)
        self.assertNotIn(".harness/runs", plans)
        self.assertNotIn("./dev/docs-index", template)

    def test_verification_and_repair_contract_in_source_policy_and_template(self) -> None:
        for relative in ("CLAUDE.md", "docs/PLANS.md", "docs/exec-plans/_template.md"):
            text = self.read(relative)
            with self.subTest(path=relative):
                for required in (
                    "`PASS`(증거로 충족 확인)",
                    "`FAIL`(위반 또는 필요한 동작 누락)",
                    "`UNPROVEN`(확보한 증거로 충족 여부 미확인)",
                    "근거를 연결한다",
                    "의도·추정·다른 검사의 성공만으로 `UNPROVEN`을 `PASS`로 바꾸지 않는다",
                    "필수 수락 기준에 `FAIL` 또는 `UNPROVEN`이 남으면 완료 수락을 추천하지 않는다",
                    "최종 수락 권한은 Main 또는 human reviewer에게 남는다",
                    "기존 테스트·검사가 해당 실패 경로를 왜 검출하지 못하는지",
                    "관련 검사를 확인하지 못했다면 그 한계를 명시한다",
                    "Main 또는 지정 Lead는 확인된 결함과 재현 근거를 하나의 요청으로 취합",
                    "가능하면 기존 Implementer를 재개",
                    "현재 후보, 수정 허용 경로, 실패 근거, 재검증 대상",
                    "원인이 불명확하면 추가 구현 전에 범위를 제한한 진단",
                    "기존 시간·재시도 예산과 같은 접근법 두 번 실패 시 중단 조건은 유지",
                ):
                    self.assertIn(required, text)

    def test_evidence_table_separates_verdict_from_approval(self) -> None:
        evidence = section(self.read("docs/exec-plans/_template.md"), "Validation and Evidence")
        rows = [line for line in evidence.splitlines() if line.startswith("|")]
        cells = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
        self.assertEqual(cells[0], [
            "Acceptance criterion", "Task", "Result", "Evidence path or note",
            "Verified candidate", "Reviewer recommendation", "Main/human approval",
        ])
        self.assertEqual(len(cells), 3)
        self.assertTrue(all(len(row) == len(cells[0]) for row in cells))
        self.assertEqual(cells[2], ["AC-1", "T2/T3", "UNPROVEN", "pending", "pending", "pending", "pending"])
        self.assertIn("FAIL/UNPROVEN이면 Evidence에 미충족 사항 또는 증거 부족", evidence)
        self.assertIn("판정은 Task state나 Main/human approval을 대체하지 않는다", evidence)

    def test_current_documents_route_to_entrypoint_product_and_manual_evidence(self) -> None:
        self.assertIn("entrypoint-migration.md", self.read("README.md"))
        self.assertIn("SPEC-REPORIVET-003", self.read("docs/README.md"))
        self.assertIn("SPEC-REPORIVET-003", self.read("docs/PRODUCT.md"))
        self.assertIn("ADR-0002-entrypoint-only-boundary.md", self.read("ARCHITECTURE.md"))
        self.assertIn("agent-navigation-evaluation.md", self.read("docs/QUALITY.md"))
        self.assertIn("entrypoint-migration.md", self.read("docs/SECURITY.md"))

        for relative in ("docs/product-specs/SPEC-REPORIVET-001-generated-project.md",
                         "docs/product-specs/SPEC-REPORIVET-002-project-definition-adoption-and-evidence-gate.md",
                         "docs/design-docs/DESIGN-REPORIVET-001-initializer-and-runtime.md",
                         "docs/design-docs/DESIGN-REPORIVET-002-project-definition-adoption-and-evidence-gate.md",
                         "docs/module-contracts/MOD-HARNESS-RUNTIME.md",
                         "docs/references/project-definition-protocol.md",
                         "docs/references/harness-engineering-skill-migration.md"):
            self.assertIn("status: superseded", self.read(relative), relative)

    def test_source_contract_does_not_force_target_runtime_or_packaged_schema(self) -> None:
        source = self.read("CLAUDE.md").casefold()
        for obsolete in ("dev/harness.py", "dev/harness.toml", "./dev/context", "./dev/define", "./dev/new-plan", "./dev/close-plan"):
            self.assertNotIn(obsolete, source)
        self.assertNotIn("src/reporivet/assets/project/docs", source)
        self.assertFalse((REPOSITORY / "docs/generated/code-map.md").exists())
        self.assertFalse((REPOSITORY / "src/reporivet/assets/project/dev/harness.py").exists())
        self.assertFalse((REPOSITORY / "src/reporivet/assets/project/docs/PLANS.md.tmpl").exists())


if __name__ == "__main__":
    unittest.main()
