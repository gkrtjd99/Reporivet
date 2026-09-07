from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
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

from reporivet.cli import main as cli_main


class ClosePlanTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(list(args))
        return subprocess.CompletedProcess(list(args), returncode, stdout.getvalue(), stderr.getvalue())

    def run_harness(
        self,
        root: Path,
        command: str,
        *args: str,
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment["PYTHON"] = sys.executable
        return subprocess.run(
            [sys.executable, "-I", str(root / "dev/harness.py"), command, *args],
            cwd=root,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )

    def init(self, root: Path) -> None:
        result = self.run_cli(
            "init",
            "--root",
            str(root),
            "--name",
            "Close Plan Fixture",
            "--summary",
            "An evidence-bound close-plan fixture.",
            "--skip-check",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def activate_fixture(self, root: Path) -> None:
        for relative in (
            "ARCHITECTURE.md",
            "docs/PRODUCT.md",
            "docs/DESIGN.md",
            "docs/QUALITY.md",
            "docs/SECURITY.md",
            "docs/RELIABILITY.md",
        ):
            path = root / relative
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            text = (
                text.replace("status: draft", "status: active")
                .replace("TODO", "Established")
                .replace("- [ ] Observed repository facts reviewed:", "- [x] Observed repository facts reviewed:")
                .replace("- [ ] Baseline questions resolved or tracked:", "- [x] Baseline questions resolved or tracked:")
            )
            path.write_text(text, encoding="utf-8")
        config = root / "dev/harness.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'baseline = "draft"',
                'baseline = "established"',
            ),
            encoding="utf-8",
        )

    def configure_project_check(self, root: Path, command: list[str]) -> None:
        config = root / "dev/harness.toml"
        replacement = "verify = " + json.dumps([command])
        text = config.read_text(encoding="utf-8")
        self.assertIn("verify = []", text)
        config.write_text(text.replace("verify = []", replacement), encoding="utf-8")

    def initialize_git(self, root: Path) -> None:
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Close Plan Fixture"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=root, check=True)

    def commit_all(self, root: Path, message: str) -> str:
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()

    def resolve_plan(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        text = text.replace("status: proposed", "status: verifying")
        text = text.replace('integrated_commit: ""', 'integrated_commit: "HEAD"')
        text = text.replace("TODO", "resolved")
        text = re.sub(r"\bpending\b", "resolved", text, flags=re.IGNORECASE)
        text = text.replace("- [ ]", "- [x]")
        text = re.sub(r"(#### State\n\n)(ready|blocked)", r"\1complete", text)
        path.write_text(text, encoding="utf-8")

    def prepare_candidate(
        self,
        root: Path,
        *,
        project_command: list[str] | None = None,
        protected_change: bool = False,
    ) -> tuple[Path, str, str, str]:
        self.init(root)
        self.activate_fixture(root)
        if project_command is not None:
            self.configure_project_check(root, project_command)
        self.initialize_git(root)
        base = self.commit_all(root, "base")
        created = self.run_harness(root, "new-plan", "Close", "evidence", "--area", "test")
        self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
        plan_path = root / created.stdout.strip()
        self.resolve_plan(plan_path)
        if protected_change:
            security = root / "docs/SECURITY.md"
            security.write_text(
                security.read_text(encoding="utf-8") + "\nReviewed protected-path fixture note.\n",
                encoding="utf-8",
            )
        head = self.commit_all(root, "candidate")
        plan_id = re.search(r"^id:\s*(\S+)", plan_path.read_text(encoding="utf-8"), re.MULTILINE)
        self.assertIsNotNone(plan_id)
        return plan_path, plan_id.group(1), base, head

    def verification_runs(self, root: Path) -> list[Path]:
        runs = root / ".harness/runs"
        return sorted(path for path in runs.glob("*-verify") if path.is_dir()) if runs.exists() else []

    def frontmatter_value(self, text: str, field: str) -> str:
        match = re.search(rf"^{re.escape(field)}:\s*(.*)$", text, re.MULTILINE)
        self.assertIsNotNone(match, field)
        value = match.group(1).strip()
        if value.startswith('"'):
            return str(json.loads(value))
        return value

    def test_pass_closure_binds_one_run_hash_verdict_and_sha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            plan_path, plan_id, base, head = self.prepare_candidate(root)

            close = self.run_harness(root, "close-plan", plan_id)
            self.assertEqual(close.returncode, 0, close.stdout + close.stderr)
            runs = self.verification_runs(root)
            self.assertEqual(len(runs), 1)
            run = runs[0]
            manifest_bytes = (run / "manifest.json").read_bytes()
            manifest = json.loads(manifest_bytes)
            gate = json.loads((run / "gate.json").read_text(encoding="utf-8"))
            manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
            self.assertEqual(gate["verdict"], "PASS")
            self.assertEqual(gate["manifest_sha256"], manifest_hash)
            self.assertEqual(manifest["target_evidence"]["base_sha"], base)
            self.assertEqual(manifest["target_evidence"]["actual_head_sha"], head)
            self.assertEqual(manifest["target_evidence"]["target"], plan_id)

            completed = root / "docs/exec-plans/completed" / plan_path.name
            self.assertFalse(plan_path.exists())
            self.assertTrue(completed.is_file())
            text = completed.read_text(encoding="utf-8")
            self.assertEqual(self.frontmatter_value(text, "status"), "complete")
            self.assertEqual(self.frontmatter_value(text, "integrated_commit"), head)
            self.assertEqual(self.frontmatter_value(text, "verified_commit"), head)
            self.assertEqual(self.frontmatter_value(text, "verification_run"), run.name)
            self.assertEqual(self.frontmatter_value(text, "manifest_sha256"), manifest_hash)
            self.assertEqual(self.frontmatter_value(text, "gate_verdict"), "PASS")
            self.assertEqual(self.frontmatter_value(text, "gate_review_reason"), "")

    def test_review_requires_explicit_reason_and_leaves_plan_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            plan_path, plan_id, _, _ = self.prepare_candidate(root, protected_change=True)
            before = plan_path.read_bytes()
            mode = plan_path.stat().st_mode

            close = self.run_harness(root, "close-plan", plan_id)
            self.assertEqual(close.returncode, 2, close.stdout + close.stderr)
            self.assertIn("requires a genuine non-empty --accept-review reason", close.stderr)
            self.assertEqual(plan_path.read_bytes(), before)
            self.assertEqual(plan_path.stat().st_mode, mode)
            self.assertFalse((root / "docs/exec-plans/completed" / plan_path.name).exists())
            runs = self.verification_runs(root)
            self.assertEqual(len(runs), 1)
            gate = json.loads((runs[0] / "gate.json").read_text(encoding="utf-8"))
            self.assertEqual(gate["verdict"], "REVIEW")
            self.assertIn("PROTECTED_PATH_MATCH", gate["reason_codes"])

    def test_review_reason_is_preserved_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            plan_path, plan_id, _, _ = self.prepare_candidate(root, protected_change=True)
            reason = "보호 경로 변경의 영향과 복구 절차를 검토하고 승인함"

            close = self.run_harness(root, "close-plan", plan_id, "--accept-review", reason)
            self.assertEqual(close.returncode, 0, close.stdout + close.stderr)
            runs = self.verification_runs(root)
            self.assertEqual(len(runs), 1)
            completed = root / "docs/exec-plans/completed" / plan_path.name
            text = completed.read_text(encoding="utf-8")
            self.assertEqual(self.frontmatter_value(text, "gate_verdict"), "REVIEW")
            self.assertEqual(self.frontmatter_value(text, "gate_review_reason"), reason)

    def test_block_and_inconclusive_cannot_be_overridden(self) -> None:
        cases = (
            (
                "BLOCK",
                [sys.executable, "-c", "raise SystemExit(7)"],
                "Gate BLOCK prevents plan closure",
            ),
            (
                "INCONCLUSIVE",
                ["missing-close-plan-verifier"],
                "Gate INCONCLUSIVE prevents plan closure",
            ),
        )
        for verdict, command, expected_error in cases:
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                plan_path, plan_id, _, _ = self.prepare_candidate(root, project_command=command)
                before = plan_path.read_bytes()

                close = self.run_harness(
                    root,
                    "close-plan",
                    plan_id,
                    "--accept-review",
                    "A human reason cannot override this verdict",
                )
                self.assertEqual(close.returncode, 2, close.stdout + close.stderr)
                self.assertIn(expected_error, close.stderr)
                self.assertEqual(plan_path.read_bytes(), before)
                self.assertFalse((root / "docs/exec-plans/completed" / plan_path.name).exists())
                runs = self.verification_runs(root)
                self.assertEqual(len(runs), 1)
                gate = json.loads((runs[0] / "gate.json").read_text(encoding="utf-8"))
                self.assertEqual(gate["verdict"], verdict)

    def test_close_plan_refuses_unsafe_unrelated_plan_entries_before_reading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp).resolve()
            plan_path, plan_id, _, _ = self.prepare_candidate(root)
            original_bytes = plan_path.read_bytes()
            external = Path(outside_tmp).resolve() / "outside.md"
            external.write_bytes(b"\xff\xfeoutside")
            unsafe = root / "docs/exec-plans/active/evil.md"
            unsafe.symlink_to(external)

            close = self.run_harness(root, "close-plan", plan_id, timeout=3)

            self.assertEqual(close.returncode, 2, close.stdout + close.stderr)
            self.assertIn("refusing to read or write through repository symlink", close.stderr)
            self.assertEqual(plan_path.read_bytes(), original_bytes)
            self.assertEqual(self.verification_runs(root), [])

        if not hasattr(os, "mkfifo"):
            return
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            plan_path, plan_id, _, _ = self.prepare_candidate(root)
            original_bytes = plan_path.read_bytes()
            fifo = root / "docs/exec-plans/active/zzz-nonregular.md"
            os.mkfifo(fifo)

            close = self.run_harness(root, "close-plan", plan_id, timeout=3)

            self.assertEqual(close.returncode, 2, close.stdout + close.stderr)
            self.assertIn("plan entry is not a regular file", close.stderr)
            self.assertEqual(plan_path.read_bytes(), original_bytes)
            self.assertEqual(self.verification_runs(root), [])

    def load_runtime_module(self, root: Path):
        module_name = f"fixture_harness_{root.name.replace('-', '_')}"
        spec = importlib.util.spec_from_file_location(module_name, root / "dev/harness.py")
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        self.addCleanup(sys.modules.pop, module_name, None)
        return module

    def test_post_move_failure_restores_exact_active_plan_and_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            plan_path, plan_id, _, _ = self.prepare_candidate(root)
            original_bytes = plan_path.read_bytes()
            original_mode = plan_path.stat().st_mode
            module = self.load_runtime_module(root)
            original_plan_check = module.command_plan_check
            calls = 0

            def fail_after_move(args):
                nonlocal calls
                calls += 1
                if calls == 1:
                    return original_plan_check(args)
                raise module.HarnessError("forced post-move structural failure")

            module.command_plan_check = fail_after_move
            with self.assertRaisesRegex(module.HarnessError, "forced post-move structural failure"):
                module.command_close_plan(
                    module.argparse.Namespace(plan=plan_id, accept_review="")
                )

            self.assertEqual(calls, 2)
            self.assertEqual(plan_path.read_bytes(), original_bytes)
            self.assertEqual(plan_path.stat().st_mode, original_mode)
            self.assertFalse((root / "docs/exec-plans/completed" / plan_path.name).exists())
            self.assertEqual(len(self.verification_runs(root)), 1)

    def test_head_change_during_verification_prevents_closure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            plan_path, plan_id, _, _ = self.prepare_candidate(root)
            original_bytes = plan_path.read_bytes()
            module = self.load_runtime_module(root)
            original_run = module.run_verification

            def change_head_after_run(**kwargs):
                result = original_run(**kwargs)
                (root / "head-change.txt").write_text("changed\n", encoding="utf-8")
                self.commit_all(root, "concurrent head change")
                return result

            module.run_verification = change_head_after_run
            with self.assertRaisesRegex(module.HarnessError, "closing HEAD changed during verification"):
                module.command_close_plan(
                    module.argparse.Namespace(plan=plan_id, accept_review="")
                )

            self.assertEqual(plan_path.read_bytes(), original_bytes)
            self.assertFalse((root / "docs/exec-plans/completed" / plan_path.name).exists())
            self.assertEqual(len(self.verification_runs(root)), 1)


if __name__ == "__main__":
    unittest.main()
