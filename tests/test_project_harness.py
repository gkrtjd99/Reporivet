from __future__ import annotations

import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from project_harness.cli import main as cli_main


class ProjectHarnessTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        previous = Path.cwd()
        try:
            if cwd is not None:
                os.chdir(cwd)
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                returncode = cli_main(list(args))
        finally:
            os.chdir(previous)
        return subprocess.CompletedProcess(list(args), returncode, stdout.getvalue(), stderr.getvalue())

    def init(
        self, root: Path, *extra: str, checked: bool = False
    ) -> subprocess.CompletedProcess[str]:
        options = list(extra)
        if not checked and "--skip-check" not in options:
            options.append("--skip-check")
        return self.run_cli(
            "init",
            "--root",
            str(root),
            "--name",
            "Test Project",
            "--summary",
            "A test project with an agent-readable repository harness.",
            "--project-kind",
            "service",
            *options,
        )

    def run_harness(self, root: Path, command: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / "dev" / "harness.py"), command, *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_initializes_repository_local_harness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.init(root, "--with-ci", checked=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            expected = (
                "AGENTS.md",
                "ARCHITECTURE.md",
                ".harness-version",
                "dev/harness.toml",
                "dev/harness.py",
                "dev/context",
                "dev/verify",
                "dev/garden",
                "docs/README.md",
                "docs/PRODUCT.md",
                "docs/DESIGN.md",
                "docs/QUALITY.md",
                "docs/SECURITY.md",
                "docs/RELIABILITY.md",
                "docs/PLANS.md",
                "docs/exec-plans/_template.md",
                "docs/exec-plans/tech-debt-tracker.md",
                ".github/workflows/harness-verify.yml",
                ".github/workflows/harness-garden.yml",
            )
            for relative in expected:
                self.assertTrue((root / relative).exists(), relative)

            self.assertLessEqual(len((root / "AGENTS.md").read_text(encoding="utf-8").splitlines()), 140)
            self.assertFalse(any(path.name == "SKILL.md" for path in root.rglob("*")))
            config = (root / "dev" / "harness.toml").read_text(encoding="utf-8")
            self.assertIn('baseline = "draft"', config)
            self.assertIn('configuration = "ready"', config)
            self.assertIn("actions/checkout@v6", (root / ".github/workflows/harness-verify.yml").read_text())
            self.assertIn("actions/upload-artifact@v7", (root / ".github/workflows/harness-garden.yml").read_text())

            verify = self.run_harness(root, "verify")
            self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    def test_existing_implementation_gets_baseline_plan_and_requires_command_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            baseline = root / "docs" / "exec-plans" / "active" / "PLAN-0000-establish-repository-baseline.md"
            self.assertTrue(baseline.exists())
            config = (root / "dev" / "harness.toml").read_text(encoding="utf-8")
            self.assertIn('configuration = "review"', config)
            check = self.run_harness(root, "check")
            self.assertNotEqual(check.returncode, 0)
            self.assertIn("configuration = 'review'", check.stderr)

    def test_project_owned_documents_survive_reinit_and_upgrade(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self.init(root)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

            product = root / "docs" / "PRODUCT.md"
            architecture = root / "ARCHITECTURE.md"
            config = root / "dev" / "harness.toml"
            product.write_text("# Project-owned product truth\n", encoding="utf-8")
            architecture.write_text("# Project-owned architecture truth\n", encoding="utf-8")
            config.write_text(config.read_text(encoding="utf-8") + "\n# user-owned\n", encoding="utf-8")

            second = self.init(root, "--skip-check")
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            upgrade = self.run_cli("upgrade", "--root", str(root), "--skip-check")
            self.assertEqual(upgrade.returncode, 0, upgrade.stdout + upgrade.stderr)

            self.assertEqual(product.read_text(encoding="utf-8"), "# Project-owned product truth\n")
            self.assertEqual(architecture.read_text(encoding="utf-8"), "# Project-owned architecture truth\n")
            self.assertIn("# user-owned", config.read_text(encoding="utf-8"))

    def test_agents_managed_block_is_idempotent_and_preserves_user_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# Team note\n\nKeep this section.\n", encoding="utf-8")
            first = self.init(root)
            second = self.init(root)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            text = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("Keep this section.", text)
            self.assertEqual(text.count("<!-- project-harness:start -->"), 1)
            self.assertEqual(text.count("<!-- project-harness:end -->"), 1)

    def test_docs_index_catalogs_new_durable_document_and_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            spec = root / "docs" / "product-specs" / "SPEC-IDENTITY-001-account-deletion.md"
            spec.write_text(
                """---
id: SPEC-IDENTITY-001
kind: product-spec
status: active
area: identity
summary: Account deletion behavior
applies_to:
  - "src/identity/**"
supersedes: []
---

# Account deletion
""",
                encoding="utf-8",
            )
            stale = self.run_harness(root, "docs-index", "--check")
            self.assertNotEqual(stale.returncode, 0)
            update = self.run_harness(root, "docs-index")
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
            self.assertIn("SPEC-IDENTITY-001", (root / "docs" / "README.md").read_text(encoding="utf-8"))
            self.assertIn("SPEC-IDENTITY-001", (root / "docs" / "product-specs" / "index.md").read_text(encoding="utf-8"))
            current = self.run_harness(root, "docs-index", "--check")
            self.assertEqual(current.returncode, 0, current.stdout + current.stderr)

    def test_new_plan_and_task_packet_are_routable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            new_plan = self.run_harness(root, "new-plan", "Login", "lockout", "--area", "identity")
            self.assertEqual(new_plan.returncode, 0, new_plan.stdout + new_plan.stderr)
            relative = new_plan.stdout.strip()
            self.assertTrue((root / relative).exists(), relative)
            self.assertIn("docs/exec-plans/active/", relative)
            plan_id = Path(relative).name.split("-login-lockout.md")[0]
            task = self.run_harness(root, "task", plan_id, "T2")
            self.assertEqual(task.returncode, 0, task.stdout + task.stderr)
            self.assertIn("#### Allowed writes", task.stdout)
            plan_check = self.run_harness(root, "plan-check")
            self.assertEqual(plan_check.returncode, 0, plan_check.stdout + plan_check.stderr)

    def test_established_baseline_rejects_scaffold_markers_and_draft_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            config = root / "dev" / "harness.toml"
            config.write_text(
                config.read_text(encoding="utf-8").replace('baseline = "draft"', 'baseline = "established"'),
                encoding="utf-8",
            )
            strict = self.run_harness(root, "docs-check")
            self.assertNotEqual(strict.returncode, 0)
            self.assertTrue("unresolved TODO" in strict.stderr or "status 'active'" in strict.stderr)

    def test_configured_missing_tool_fails_instead_of_skipping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            config = root / "dev" / "harness.toml"
            text = config.read_text(encoding="utf-8").replace(
                "verify = []", 'verify = [["definitely-not-an-executable"]]'
            )
            config.write_text(text, encoding="utf-8")
            verify = self.run_harness(root, "verify")
            self.assertNotEqual(verify.returncode, 0)
            self.assertIn("configured executable is unavailable", verify.stderr)

    def test_dry_run_does_not_create_or_modify_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "new-project"
            dry_init = self.init(missing, "--dry-run")
            self.assertEqual(dry_init.returncode, 0, dry_init.stdout + dry_init.stderr)
            self.assertFalse(missing.exists())

            root = Path(tmp) / "existing"
            root.mkdir()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            before = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            dry_upgrade = self.run_cli("upgrade", "--root", str(root), "--dry-run")
            self.assertEqual(dry_upgrade.returncode, 0, dry_upgrade.stdout + dry_upgrade.stderr)
            after = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(before, after)

    def test_init_refuses_to_replace_existing_project_owned_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "dev").mkdir()
            (root / "dev" / "check").write_text("#!/bin/sh\necho project-owned\n", encoding="utf-8")
            result = self.init(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to replace existing project-owned command paths", result.stderr)
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertIn("project-owned", (root / "dev" / "check").read_text(encoding="utf-8"))

    def test_close_plan_binds_verification_to_clean_git_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            new_plan = self.run_harness(root, "new-plan", "Close", "test", "--area", "test")
            self.assertEqual(new_plan.returncode, 0, new_plan.stdout + new_plan.stderr)
            plan_path = root / new_plan.stdout.strip()

            for relative in (
                "ARCHITECTURE.md",
                "docs/PRODUCT.md",
                "docs/DESIGN.md",
                "docs/QUALITY.md",
                "docs/SECURITY.md",
                "docs/RELIABILITY.md",
            ):
                path = root / relative
                text = path.read_text(encoding="utf-8")
                text = text.replace("status: draft", "status: active").replace("TODO", "Established")
                path.write_text(text, encoding="utf-8")

            plan = plan_path.read_text(encoding="utf-8")
            plan = plan.replace("status: proposed", "status: verifying")
            plan = plan.replace('integrated_commit: ""', 'integrated_commit: "HEAD"')
            plan = plan.replace("TODO", "resolved")
            plan = plan.replace("pending", "resolved")
            plan = plan.replace("- [ ]", "- [x]")
            plan = re.sub(r"(#### State\n\n)(ready|blocked)", r"\1complete", plan)
            plan_path.write_text(plan, encoding="utf-8")

            config = root / "dev" / "harness.toml"
            config.write_text(
                config.read_text(encoding="utf-8").replace('baseline = "draft"', 'baseline = "established"'),
                encoding="utf-8",
            )

            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "candidate"], cwd=root, check=True, capture_output=True)
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True
            ).stdout.strip()

            plan_id = plan_path.name.split("-close-test.md")[0]
            close = self.run_harness(root, "close-plan", plan_id)
            self.assertEqual(close.returncode, 0, close.stdout + close.stderr)
            completed = root / "docs" / "exec-plans" / "completed" / plan_path.name
            self.assertTrue(completed.exists())
            completed_text = completed.read_text(encoding="utf-8")
            self.assertIn("status: complete", completed_text)
            self.assertIn(f"integrated_commit: {head}", completed_text)
            self.assertIn(f"verified_commit: {head}", completed_text)


if __name__ == "__main__":
    unittest.main()
