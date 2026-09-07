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
            "lead role is limited to scheduling leaf work",
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
            "lead role is limited to scheduling",
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
