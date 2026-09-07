from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet.cli import main as cli_main


class AuthorityLifecycleTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(list(args))
        return subprocess.CompletedProcess(list(args), returncode, stdout.getvalue(), stderr.getvalue())

    def init(self, root: Path, *, summary: str = "A target-specific fixture.") -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "init",
            "--root",
            str(root),
            "--name",
            "Authority Fixture",
            "--summary",
            summary,
            "--project-kind",
            "service",
            "--skip-check",
        )

    def run_harness(self, root: Path, command: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / "dev/harness.py"), command, *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def write_decision(
        self,
        root: Path,
        *,
        filename: str,
        decision_id: str,
        status: str,
        scope: str = "src/shared/**",
        body: str | None = None,
        supersedes: tuple[str, ...] = (),
        superseded_by: str = "",
    ) -> Path:
        supersedes_lines = "\n".join(f'  - "{item}"' for item in supersedes)
        if not supersedes_lines:
            supersedes_lines = "[]"
        if body is None:
            body = """## Context

The repository needs one explicit choice for this fixture scope.

## Decision

Keep the fixture behavior deterministic.

## Consequences

- The choice is inspectable.

## Alternatives considered

- No change: rejected because the ambiguity would remain.
- Use a second explicit implementation: rejected because it duplicates the boundary.

## Verification and retirement

- Run `./dev/docs-check`; revisit when the scoped implementation is retired.
"""
        path = root / "docs" / "decisions" / filename
        path.write_text(
            f"""---
id: {decision_id}
kind: decision
status: {status}
area: fixture
summary: Fixture authority decision
applies_to:
  - "{scope}"
supersedes: {supersedes_lines if supersedes_lines == '[]' else chr(10) + supersedes_lines}
superseded_by: {superseded_by}
---

# Fixture authority decision

{body}""",
            encoding="utf-8",
        )
        return path

    def test_init_generates_observed_facts_with_evidence_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "src").mkdir()
            (root / "src/main.ts").write_text("export const value = 1;\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests/main.test.ts").write_text("// fixture\n", encoding="utf-8")
            (root / ".github/workflows").mkdir(parents=True)
            (root / ".github/workflows/ci.yml").write_text("name: ci\n", encoding="utf-8")
            (root / "package.json").write_text(
                json.dumps({"scripts": {"check": "test-runner"}}),
                encoding="utf-8",
            )
            (root / "package-lock.json").write_text("{}\n", encoding="utf-8")

            result = self.init(root, summary="Invented product mission that must not enter observed facts.")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            facts = (root / "docs/generated/repository-facts.md").read_text(encoding="utf-8")
            questions = (root / "docs/generated/baseline-questions.md").read_text(encoding="utf-8")

            for evidence in (
                "`package.json`",
                "`package-lock.json`",
                "`src`",
                "`tests`",
                "`.github/workflows/ci.yml`",
            ):
                self.assertIn(evidence, facts)
            self.assertIn("Observed", facts)
            self.assertIn("Candidate", facts)
            self.assertIn("Evidence path", facts)
            self.assertNotIn("Invented product mission", facts)
            for invented_authority in ("target users are", "SLO is", "owned by", "design token"):
                self.assertNotIn(invented_authority, facts.casefold())
            self.assertIn("product purpose", questions.casefold())
            self.assertIn("ownership", questions.casefold())
            self.assertIn("SLO", questions)

    def test_init_keeps_design_docs_to_index_and_template_without_removing_existing_core_beliefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            generated = sorted(path.name for path in (root / "docs/design-docs").glob("*.md"))
            self.assertEqual(generated, ["_template.md", "index.md"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            core = root / "docs/design-docs/core-beliefs.md"
            core.parent.mkdir(parents=True)
            original = """---
id: DESIGN-CORE-001
kind: design-doc
status: active
area: repository
summary: Existing target core beliefs
applies_to:
  - "**"
supersedes: []
---

# Existing target core beliefs
"""
            core.write_text(original, encoding="utf-8")
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(core.read_text(encoding="utf-8"), original)

    def test_legacy_configuration_upgrade_preserves_authority_and_adds_new_generated_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            product = root / "docs/PRODUCT.md"
            architecture = root / "ARCHITECTURE.md"
            product_text = """---
id: PRODUCT
kind: product
status: active
area: product
summary: Legacy product authority
applies_to:
  - "src/**"
---

# Legacy product

Established product authority.
"""
            architecture_text = """---
id: ARCHITECTURE
kind: architecture
status: active
area: repository
summary: Legacy architecture authority
applies_to:
  - "**"
---

# Legacy architecture

Established architecture authority.
"""
            product.write_text(product_text, encoding="utf-8")
            architecture.write_text(architecture_text, encoding="utf-8")
            for relative in ("docs/QUALITY.md", "docs/SECURITY.md", "docs/RELIABILITY.md"):
                path = root / relative
                text = path.read_text(encoding="utf-8")
                path.write_text(
                    text.replace("status: draft", "status: active").replace("TODO", "Established"),
                    encoding="utf-8",
                )
            config = root / "dev/harness.toml"
            config_text = config.read_text(encoding="utf-8")
            documents_start = config_text.index("[documents]")
            commands_start = config_text.index("[commands]")
            config_text = (
                config_text[:documents_start]
                + config_text[commands_start:]
            ).replace('baseline = "draft"', 'baseline = "established"')
            config.write_text(config_text, encoding="utf-8")
            for relative in (
                "docs/generated/repository-facts.md",
                "docs/generated/baseline-questions.md",
            ):
                (root / relative).unlink()
            agents = root / "AGENTS.md"
            agents.write_text(
                "\n".join(
                    line
                    for line in agents.read_text(encoding="utf-8").splitlines()
                    if "docs/generated/repository-facts.md" not in line
                    and "docs/generated/baseline-questions.md" not in line
                )
                + "\n",
                encoding="utf-8",
            )

            legacy_check = self.run_harness(root, "docs-check")
            self.assertEqual(legacy_check.returncode, 0, legacy_check.stdout + legacy_check.stderr)
            upgrade = self.run_cli("upgrade", "--root", str(root), "--skip-check")
            self.assertEqual(upgrade.returncode, 0, upgrade.stdout + upgrade.stderr)
            self.assertEqual(product.read_text(encoding="utf-8"), product_text)
            self.assertEqual(architecture.read_text(encoding="utf-8"), architecture_text)
            self.assertEqual(config.read_text(encoding="utf-8"), config_text)
            self.assertTrue((root / "docs/generated/repository-facts.md").is_file())
            self.assertTrue((root / "docs/generated/baseline-questions.md").is_file())

    def test_product_template_describes_target_not_reporivet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root, summary="Coordinate field inspections for bridge teams.")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            product = (root / "docs/PRODUCT.md").read_text(encoding="utf-8")
            self.assertIn("Coordinate field inspections for bridge teams.", product)
            self.assertIn("## Users and jobs", product)
            self.assertNotIn("repository-local agent harness", product.casefold())
            self.assertEqual(product.count("Reporivet"), 1)
            self.assertIn("provenance", product.casefold())

    def test_architecture_template_describes_target_not_harness_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "src").mkdir()
            (root / "src/service.py").write_text("VALUE = 1\n", encoding="utf-8")
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            architecture = (root / "ARCHITECTURE.md").read_text(encoding="utf-8")
            self.assertIn("`src`", architecture)
            self.assertIn("## Repository map", architecture)
            self.assertNotIn("Main Agent", architecture)
            self.assertNotIn("Task Packet", architecture)
            self.assertNotIn("repository-local runtime", architecture.casefold())
            self.assertEqual(architecture.count("Reporivet"), 1)

    def test_draft_documents_are_excluded_from_default_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            default = self.run_harness(root, "context")
            self.assertEqual(default.returncode, 0, default.stdout + default.stderr)
            self.assertNotIn("`ARCHITECTURE.md`", default.stdout)
            self.assertNotIn("`docs/PRODUCT.md`", default.stdout)

            drafts = self.run_harness(root, "context", "--include-drafts")
            self.assertEqual(drafts.returncode, 0, drafts.stdout + drafts.stderr)
            self.assertIn("`ARCHITECTURE.md`", drafts.stdout)
            self.assertIn("`docs/PRODUCT.md`", drafts.stdout)

    def test_accepted_decision_is_included_in_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            decision = self.write_decision(
                root,
                filename="ADR-0042-fixture.md",
                decision_id="ADR-0042",
                status="accepted",
            )
            self.assertEqual(self.run_harness(root, "docs-index").returncode, 0)

            context = self.run_harness(root, "context")
            self.assertEqual(context.returncode, 0, context.stdout + context.stderr)
            self.assertIn(str(decision.relative_to(root)), context.stdout)
            self.assertIn("ADR-0042 [accepted]", context.stdout)

    def test_superseded_decision_is_excluded_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            old = self.write_decision(
                root,
                filename="ADR-0041-old.md",
                decision_id="ADR-0041",
                status="superseded",
                superseded_by="ADR-0042",
            )
            self.write_decision(
                root,
                filename="ADR-0042-new.md",
                decision_id="ADR-0042",
                status="accepted",
                supersedes=("ADR-0041",),
            )
            self.assertEqual(self.run_harness(root, "docs-index").returncode, 0)

            default = self.run_harness(root, "context")
            self.assertEqual(default.returncode, 0, default.stdout + default.stderr)
            self.assertNotIn(str(old.relative_to(root)), default.stdout)
            history = self.run_harness(root, "context", "--include-history")
            self.assertEqual(history.returncode, 0, history.stdout + history.stderr)
            self.assertIn(str(old.relative_to(root)), history.stdout)

    def test_conflicting_active_authority_fails_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            first = root / "docs/product-specs/SPEC-FIXTURE-001-first.md"
            second = root / "docs/product-specs/SPEC-FIXTURE-001-second.md"
            document = """---
id: SPEC-FIXTURE-001
kind: product-spec
status: active
area: fixture
summary: Explicit duplicate authority fixture
applies_to:
  - "src/shared/**"
supersedes: []
---

# Fixture authority
"""
            first.write_text(document, encoding="utf-8")
            second.write_text(document, encoding="utf-8")

            context = self.run_harness(root, "context")
            self.assertNotEqual(context.returncode, 0)
            self.assertIn("duplicate authority id 'SPEC-FIXTURE-001'", context.stderr)

    def test_different_active_authorities_may_share_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for index in (1, 2):
                (root / f"docs/product-specs/SPEC-FIXTURE-00{index}.md").write_text(
                    f"""---
id: SPEC-FIXTURE-00{index}
kind: product-spec
status: active
area: fixture
summary: Compatible authority {index}
applies_to:
  - "src/shared/**"
supersedes: []
---

# Compatible authority {index}
""",
                    encoding="utf-8",
                )

            context = self.run_harness(root, "context", "--path", "src/shared/value.py")
            self.assertEqual(context.returncode, 0, context.stdout + context.stderr)
            self.assertIn("SPEC-FIXTURE-001", context.stdout)
            self.assertIn("SPEC-FIXTURE-002", context.stdout)

    def test_explicit_supersession_mismatch_fails_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.write_decision(
                root,
                filename="ADR-0041-still-current.md",
                decision_id="ADR-0041",
                status="accepted",
            )
            self.write_decision(
                root,
                filename="ADR-0042-replacement.md",
                decision_id="ADR-0042",
                status="accepted",
                supersedes=("ADR-0041",),
            )

            context = self.run_harness(root, "context")
            self.assertNotEqual(context.returncode, 0)
            self.assertIn("supersession mismatch", context.stderr)

    def test_baseline_cannot_be_established_by_status_edit_alone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for relative in (
                "ARCHITECTURE.md",
                "docs/PRODUCT.md",
                "docs/QUALITY.md",
                "docs/SECURITY.md",
                "docs/RELIABILITY.md",
            ):
                path = root / relative
                if path.exists():
                    path.write_text(
                        path.read_text(encoding="utf-8").replace("status: draft", "status: active"),
                        encoding="utf-8",
                    )
            config = root / "dev/harness.toml"
            config.write_text(
                config.read_text(encoding="utf-8").replace('baseline = "draft"', 'baseline = "established"'),
                encoding="utf-8",
            )

            check = self.run_harness(root, "docs-check")
            self.assertNotEqual(check.returncode, 0)
            self.assertIn("baseline evidence review", check.stderr)

    def test_durable_decision_requires_reason_and_alternatives(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.write_decision(
                root,
                filename="ADR-0042-incomplete.md",
                decision_id="ADR-0042",
                status="accepted",
                body="""## Decision

Use the fixture implementation.
""",
            )
            self.assertEqual(self.run_harness(root, "docs-index").returncode, 0)

            check = self.run_harness(root, "docs-check")
            self.assertNotEqual(check.returncode, 0)
            self.assertIn("accepted decision requires a concrete reason", check.stderr)
            self.assertIn("accepted decision requires at least two substantive alternatives", check.stderr)
            self.assertIn("accepted decision requires concrete verification or enforcement", check.stderr)


if __name__ == "__main__":
    unittest.main()
