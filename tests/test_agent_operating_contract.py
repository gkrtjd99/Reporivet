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

    def test_source_contract_projection_and_owner_roles(self) -> None:
        source = portable(self.read("CLAUDE.md"))
        agents = self.read("AGENTS.md")
        projected = portable(agents) if START in agents else agents
        self.assertEqual(source, projected)

        normalized = source.casefold()
        for required in (
            "main → task owner → leaf",
            "only an explicitly designated task owner",
            "task owner",
            "must not be delegated wholesale",
            "directly owns executable design",
            "no coding share",
            "direct-implementation ratio",
            "call-count quota",
            "every leaf receives one bounded",
            "assigned acceptance criteria",
            "packet may permit local implementation, investigation, and check choices",
            "core design, scope, permissions, acceptance criteria, and prohibitions",
            "more restrictive host/project policy",
            "plan lifecycle",
            "global design",
            "reads only bounded code/evidence needed for judgment",
            "separate required stronger execution context",
            "integration execution may be delegated",
            "retains order, exact candidate, final integration",
            "completion approval",
            "current requirements and execution environment",
            "owner comparison is not independent verification",
            "separate context",
            "frozen shared interfaces",
            "memory is auxiliary",
            "spec-reporivet-003-agent-entrypoints.md",
            "agent-contract-sync",
        ):
            self.assertIn(required, normalized)
        self.assertNotIn("task lead", normalized)
        self.assertIn("docs/plans.md", normalized)
        self.assertNotIn("결함 보고에는", normalized)
        self.assertNotIn("수선 시 main", normalized)

    def test_source_plan_policy_preserves_owner_and_manual_boundary(self) -> None:
        plans = self.read("docs/PLANS.md")
        template = self.read("docs/exec-plans/_template.md")
        normalized = plans.casefold()
        for required in (
            "main → task owner → leaf",
            "only an explicitly designated task owner",
            "leaf receives one bounded packet",
            "task owner owns the executable design",
            "direct comparison of important diffs",
            "repair-cause judgment",
            "no required coding share",
            "call-count quota",
            "current contract",
            "progress",
            "six restoration points",
            "only a path or revision",
            "stale task must stop",
            "acceptance is held",
            "legitimate new user instruction",
            "default assignment observed on the current host",
            "failure cost",
            "not fixed to the cheapest grade",
            "agent or model changes",
            "prompt or task packet",
            "host permissions",
            "post-checks",
            "shell path may bypass",
            "semantic rule is not proved",
            "exact target commit sha",
            "retained negative evidence",
            "task owner's direct design/evidence judgment",
            "detailed evidence locations",
            "current requirements and execution environment",
            "owner comparison is necessary",
            "separate context",
            "without explicit authority and packet scope",
            "retain any stricter prohibition",
            "no automatic gate",
        ):
            self.assertIn(required, normalized)
        self.assertNotIn("task lead", normalized)

        roles_normalized = section(plans, "Operating roles and delegation").casefold()
        for required in (
            "when an implementation-affecting cause or core design assumption is unconfirmed",
            "assign only that uncertainty to a bounded investigation or experiment",
            "hold the affected implementation until the owner confirms a resolving design from the evidence",
            "do not require diagnosis for every minor assumption",
        ):
            self.assertIn(required, roles_normalized)

        template_normalized = template.casefold()
        for required in (
            "current contract",
            "owner design before delegation",
            "observable behavior",
            "invariants and prohibited actions",
            "evidence-backed implementation direction",
            "failure paths",
            "write protections",
            "assumptions",
            "packet-permitted local implementation",
            "core design, scope, permissions, acceptance criteria, and prohibitions",
            'bulk "implement and verify" delegation',
            "applied contract",
            "per-criterion pass/fail/unproven",
            "protected-path/prohibition checks",
            "retained negative evidence",
            "design deviations",
            "task owner judgment",
            "detailed evidence locations",
            "design/evidence comparison",
            "current requirements",
            "manual reinjection",
            "actual source or project-owned checks",
        ):
            self.assertIn(required, template_normalized)
        self.assertNotIn("task lead", template_normalized)

        owner_design = section(template, "Owner Design Before Delegation").casefold()
        for required in (
            "when an implementation-affecting cause or core design assumption is unconfirmed",
            "assign only that uncertainty to a bounded investigation or experiment",
            "hold the affected implementation until the owner confirms a resolving design from the evidence",
            "minor assumptions do not require diagnosis",
        ):
            self.assertIn(required, owner_design)

        checkpoint_match = re.search(
            r"^#### Owner design checkpoint\n(?P<body>.*?)(?=^#### |\Z)",
            template,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(checkpoint_match)
        checkpoint = checkpoint_match.group(0).casefold()
        for required in (
            "implementation-affecting cause or core design assumption is unconfirmed",
            "bounded investigation or experiment",
            "hold the affected implementation until the owner confirms a resolving design from the evidence",
            "minor assumptions do not require diagnosis",
        ):
            self.assertIn(required, checkpoint)

        self.assertNotIn("./dev/close-plan", plans)
        self.assertNotIn(".harness/runs", plans)
        self.assertNotIn("./dev/docs-index", template)

    def test_verification_and_repair_contract_is_connected(self) -> None:
        detailed = ("docs/PLANS.md", "docs/exec-plans/_template.md")
        for relative in detailed:
            text = self.read(relative)
            normalized = text.casefold()
            with self.subTest(path=relative):
                for required in (
                    "`pass`(증거로 충족 확인)",
                    "`fail`(위반 또는 필요한 동작 누락)",
                    "`unproven`(확보한 증거로 충족 여부 미확인)",
                    "근거를 연결한다",
                    "의도·추정·다른 검사의 성공만으로 `unproven`을 `pass`로 바꾸지 않는다",
                    "필수 수락 기준에 `fail` 또는 `unproven`이 남으면 완료 수락을 추천하지 않는다",
                    "최종 수락 권한은 main 또는 human reviewer에게 남는다",
                    "기존 테스트·검사가 해당 실패 경로를 왜 검출하지 못했는지",
                    "관련 검사를 확인하지 못했다면 그 한계를 명시한다",
                ):
                    self.assertIn(required, normalized)
                self.assertTrue(
                    "designated owner" in normalized
                    or "지정 owner" in normalized
                    or "지정 task owner" in normalized
                )
                self.assertIn("evidence", normalized)
                self.assertTrue("current candidate" in normalized or "현재 후보" in normalized)
                self.assertTrue("re-verification" in normalized or "재검증" in normalized)

        source = self.read("CLAUDE.md").casefold()
        self.assertIn("docs/plans.md", source)
        self.assertIn("required acceptance criterion left `fail` or `unproven`", source)
        self.assertNotIn("기존 테스트·검사가", source)
        self.assertNotIn("bounded repair request", source)

    def test_evidence_table_separates_verdict_from_approval(self) -> None:
        evidence = section(self.read("docs/exec-plans/_template.md"), "Validation and Evidence")
        rows = [line for line in evidence.splitlines() if line.startswith("|")]
        cells = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
        self.assertGreaterEqual(len(cells), 2)
        self.assertEqual(cells[0], [
            "Acceptance criterion", "Task", "Result", "Evidence path or note",
            "Verified candidate", "Reviewer recommendation", "Main/human approval",
        ])
        self.assertTrue(all(len(row) == len(cells[0]) for row in cells))
        self.assertTrue(any(row[:3] == ["AC-1", "T2/T3", "UNPROVEN"] for row in cells[1:]))
        self.assertIn("FAIL/UNPROVEN이면 Evidence에 미충족 사항 또는 증거 부족", evidence)
        self.assertIn("판정은 Task state나 Main/human approval을 대체하지 않는다", evidence)

    def test_quality_declares_six_behavior_scenarios_and_limits(self) -> None:
        quality = self.read("docs/QUALITY.md").casefold()
        for required in (
            "최소 수동 행동 평가 6개",
            "main의 상세 구현 격리와 설계 판정",
            "owner 설계 대조와 통짜 위임 금지",
            "압축 후 재개 시 계약 재확보",
            "진행 중 추가 제약 적용",
            "모순된 pass 수락 거부",
            "어려운 실행의 별도 강한 문맥",
            "실제 compact가 가능한 환경에서는",
            "통제된 수동 재주입임을 명시",
            "실행/미실행과 효과 미입증 경계",
            "문서에 적은 평가 절차",
            "기존 fresh-context 평가는 재사용할 때",
            "필수 기준에 fail 또는 unproven",
        ):
            self.assertIn(required, quality)
        self.assertNotIn("수선/lifecycle", quality)
        self.assertNotIn("이번 변경에서 실제 행동을 실행했다고 쓰지 않는다", quality)
        self.assertNotIn("이번 개선의 여섯 시나리오", quality)

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


if __name__ == "__main__":
    unittest.main()
