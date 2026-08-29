from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Sequence

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet.cli import main as cli_main


class VerificationRunTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(list(args))
        return subprocess.CompletedProcess(list(args), returncode, stdout.getvalue(), stderr.getvalue())

    def init(self, root: Path) -> None:
        result = self.run_cli(
            "init",
            "--root",
            str(root),
            "--name",
            "Verification Fixture",
            "--summary",
            "A fixed Verification Run fixture.",
            "--skip-check",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def write_config(
        self,
        root: Path,
        *,
        architecture: Sequence[Sequence[str]] = (),
        verify: Sequence[Sequence[str]] = (),
        smoke: Sequence[Sequence[str]] = (),
        source: bool = True,
    ) -> None:
        def commands(value: Sequence[Sequence[str]]) -> str:
            return json.dumps([list(command) for command in value], ensure_ascii=False)

        (root / "dev/harness.toml").write_text(
            "\n".join(
                (
                    "# Project-owned configuration. The initializer never overwrites this file.",
                    "version = 1",
                    "",
                    "[project]",
                    'name = "Verification Fixture"',
                    'summary = "A fixed Verification Run fixture."',
                    'kind = "cli"',
                    'primary_language = "Python"',
                    'runtime = "Python 3.12"',
                    'baseline = "draft"',
                    'configuration = "ready"',
                    'default_branch = "main"',
                    "",
                    "[commands]",
                    "bootstrap = []",
                    "run = []",
                    "check = []",
                    f"verify = {commands(verify)}",
                    f"smoke = {commands(smoke)}",
                    f"architecture = {commands(architecture)}",
                    "",
                    "[paths]",
                    'source = ["src"]' if source else "source = []",
                    'tests = ["tests"]',
                    'generated_docs = ["docs/generated"]',
                    "",
                    "[policy]",
                    "parallel_writes = false",
                    "agents_max_lines = 140",
                    "stale_plan_days = 21",
                    "security_scan_max_bytes = 2097152",
                    "security_allow_tracked = []",
                    "require_plan_for = []",
                    "",
                )
            ),
            encoding="utf-8",
        )
        if source:
            (root / "src").mkdir(exist_ok=True)
        generated = subprocess.run(
            [sys.executable, "-I", str(root / "dev/harness.py"), "code-map"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(generated.returncode, 0, generated.stdout + generated.stderr)

    def run_harness(
        self,
        root: Path,
        command: str,
        *args: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHON"] = sys.executable
        if environment:
            env.update(environment)
        return subprocess.run(
            [sys.executable, "-I", str(root / "dev/harness.py"), command, *args],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def verification_runs(self, root: Path) -> list[Path]:
        runs = root / ".harness/runs"
        return sorted(path for path in runs.glob("*-verify") if path.is_dir()) if runs.exists() else []

    def load_artifacts(self, run: Path) -> tuple[dict[str, object], dict[str, object]]:
        manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        gate = json.loads((run / "gate.json").read_text(encoding="utf-8"))
        return manifest, gate

    def assert_complete_artifacts(self, root: Path, run: Path) -> None:
        self.assertEqual(run.parent, root / ".harness/runs")
        self.assertTrue((run / "manifest.json").is_file())
        self.assertTrue((run / "gate.json").is_file())
        self.assertTrue((run / "report.md").is_file())
        checks = sorted((run / "checks").glob("*.json"))
        self.assertEqual(
            [path.name for path in checks],
            [
                "01-security.json",
                "02-docs-index.json",
                "03-documentation.json",
                "04-plan.json",
                "05-architecture.json",
                "06-project.json",
                "07-smoke.json",
            ],
        )
        for path in (run / "manifest.json", run / "gate.json", run / "report.md", *checks):
            payload = path.read_bytes()
            self.assertTrue(payload.endswith(b"\n"), path)
            self.assertNotIn(str(root).encode(), payload, path)

    def test_one_shared_run_records_seven_ordered_checks_and_optional_smoke_skip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.init(root)
            secret_argument = "raw-argv-must-not-enter-artifacts"
            self.write_config(
                root,
                architecture=((sys.executable, "-c", "print('architecture-ok')"),),
                verify=((sys.executable, "-c", "print('project-ok')", secret_argument),),
            )

            result = self.run_harness(root, "verify")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            runs = self.verification_runs(root)
            self.assertEqual(len(runs), 1)
            run = runs[0]
            self.assert_complete_artifacts(root, run)
            structured_evidence = b"".join(
                path.read_bytes()
                for path in (run / "manifest.json", run / "gate.json", run / "report.md", *sorted((run / "checks").glob("*.json")))
            )
            self.assertNotIn(secret_argument.encode(), structured_evidence)
            manifest, gate = self.load_artifacts(run)
            checks = manifest["checks"]
            self.assertEqual([check["name"] for check in checks], [
                "security",
                "docs-index",
                "documentation",
                "plan",
                "architecture",
                "project",
                "smoke",
            ])
            self.assertEqual([check["status"] for check in checks], [
                "skipped",
                "pass",
                "pass",
                "pass",
                "pass",
                "pass",
                "skipped",
            ])
            self.assertFalse(checks[-1]["required"])
            self.assertEqual(manifest["status"], "pass")
            self.assertEqual(gate["verdict"], "UNKNOWN")
            self.assertEqual(gate["mode"], "deferred")
            self.assertEqual(gate["reason_codes"], ["GATE_POLICY_DEFERRED"])
            expected_hash = hashlib.sha256((run / "manifest.json").read_bytes()).hexdigest()
            self.assertEqual(gate["manifest_sha256"], expected_hash)
            self.assertEqual(manifest["target_evidence"]["changed_paths_status"], "unknown")
            self.assertIn("no Git parent was inferred", manifest["target_evidence"]["changed_paths_detail"])
            self.assertIn("architecture-ok", (run / "logs/05-architecture-01.log").read_text(encoding="utf-8"))
            self.assertIn("project-ok", (run / "logs/06-project-01.log").read_text(encoding="utf-8"))

    def test_candidate_failure_continues_to_smoke_and_preserves_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.init(root)
            self.write_config(
                root,
                verify=((sys.executable, "-c", "print('candidate-failed'); raise SystemExit(7)"),),
                smoke=((sys.executable, "-c", "print('smoke-still-ran')"),),
            )

            result = self.run_harness(root, "verify")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            run = self.verification_runs(root)[0]
            self.assert_complete_artifacts(root, run)
            manifest, _ = self.load_artifacts(run)
            by_name = {check["name"]: check for check in manifest["checks"]}
            self.assertEqual(manifest["status"], "fail")
            self.assertEqual(by_name["project"]["status"], "fail")
            self.assertEqual(by_name["project"]["returncodes"], [7])
            self.assertEqual(by_name["smoke"]["status"], "pass")
            self.assertTrue(by_name["smoke"]["required"])
            self.assertIn("candidate-failed", (run / "logs/06-project-01.log").read_text(encoding="utf-8"))
            self.assertIn("smoke-still-ran", (run / "logs/07-smoke-01.log").read_text(encoding="utf-8"))

    def test_required_failure_precedes_infrastructure_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.init(root)
            self.write_config(
                root,
                architecture=(("missing-reporivet-architecture-command",),),
                verify=((sys.executable, "-c", "raise SystemExit(3)"),),
            )

            result = self.run_harness(root, "verify")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            run = self.verification_runs(root)[0]
            manifest, _ = self.load_artifacts(run)
            by_name = {check["name"]: check for check in manifest["checks"]}
            self.assertEqual(by_name["architecture"]["status"], "error")
            self.assertEqual(by_name["project"]["status"], "fail")
            self.assertEqual(manifest["status"], "fail")

    def test_missing_executable_is_error_and_all_artifacts_survive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.init(root)
            self.write_config(root, verify=((str(root / "missing-reporivet-project-command"),),))

            result = self.run_harness(root, "verify")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            runs = self.verification_runs(root)
            self.assertEqual(len(runs), 1)
            run = runs[0]
            self.assert_complete_artifacts(root, run)
            manifest, _ = self.load_artifacts(run)
            by_name = {check["name"]: check for check in manifest["checks"]}
            self.assertEqual(manifest["status"], "error")
            self.assertEqual(by_name["project"]["status"], "error")
            self.assertEqual(by_name["project"]["returncodes"], [None])
            self.assertIn("configured executable is unavailable", by_name["project"]["detail"])

    def test_malformed_configuration_is_error_with_complete_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.init(root)
            (root / "dev/harness.toml").write_text("[project\n", encoding="utf-8")

            result = self.run_harness(root, "verify")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            runs = self.verification_runs(root)
            self.assertEqual(len(runs), 1)
            run = runs[0]
            self.assert_complete_artifacts(root, run)
            manifest, gate = self.load_artifacts(run)
            self.assertEqual(manifest["status"], "error")
            self.assertEqual(manifest["detection"]["config_status"], "error")
            self.assertEqual(manifest["hashes"]["policy_sha256"], "")
            self.assertEqual(gate["verdict"], "UNKNOWN")

    def test_malformed_optional_smoke_configuration_is_required_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.init(root)
            self.write_config(
                root,
                verify=((sys.executable, "-c", "print('project-ok')"),),
            )
            config = root / "dev/harness.toml"
            config.write_text(
                config.read_text(encoding="utf-8").replace("smoke = []", 'smoke = "malformed"'),
                encoding="utf-8",
            )

            result = self.run_harness(root, "verify")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            run = self.verification_runs(root)[0]
            self.assert_complete_artifacts(root, run)
            manifest, _ = self.load_artifacts(run)
            smoke = next(check for check in manifest["checks"] if check["name"] == "smoke")
            self.assertEqual(manifest["status"], "error")
            self.assertEqual(smoke["status"], "error")
            self.assertTrue(smoke["required"])

    def test_recursive_verify_configuration_is_rejected_without_nested_run(self) -> None:
        recursive_commands = (
            ("./dev/verify",),
            (sys.executable, "-m", "dev.harness", "verify"),
            ("sh", "-c", "'./dev/verify'"),
        )
        for command in recursive_commands:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                self.init(root)
                self.write_config(root, verify=(command,))

                result = self.run_harness(root, "verify")
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                runs = self.verification_runs(root)
                self.assertEqual(len(runs), 1)
                manifest, _ = self.load_artifacts(runs[0])
                project = next(check for check in manifest["checks"] if check["name"] == "project")
                self.assertEqual(project["status"], "error")
                self.assertIn("recursively invokes", project["detail"])

    def test_architecture_and_smoke_reject_recursive_verify_without_nested_run(self) -> None:
        recursive_command = (
            "sh",
            "-c",
            'if [ -z "$REPORIVET_RECURSION_GUARD" ]; then '
            "REPORIVET_RECURSION_GUARD=1 ./dev/verify; fi",
        )
        for group in ("architecture", "smoke"):
            with self.subTest(group=group), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                self.init(root)
                command_groups = {
                    "verify": ((sys.executable, "-c", "print('project-ok')"),),
                    group: (recursive_command,),
                }
                self.write_config(root, **command_groups)

                result = self.run_harness(root, "verify")
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                runs = self.verification_runs(root)
                self.assertEqual(len(runs), 1)
                manifest, _ = self.load_artifacts(runs[0])
                check = next(item for item in manifest["checks"] if item["name"] == group)
                self.assertEqual(check["status"], "error")
                self.assertTrue(check["required"])
                self.assertIn("recursively invokes", check["detail"])

    def test_project_without_local_git_ignores_enclosing_repository(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git is unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            outer = Path(tmp).resolve()
            subprocess.run(["git", "init", "-b", "main"], cwd=outer, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Verification Fixture"], cwd=outer, check=True)
            subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=outer, check=True)
            (outer / "parent.txt").write_text("parent\n", encoding="utf-8")
            subprocess.run(["git", "add", "parent.txt"], cwd=outer, check=True)
            subprocess.run(["git", "commit", "-m", "parent"], cwd=outer, check=True, capture_output=True)
            root = outer / "project"
            root.mkdir()
            self.init(root)
            self.write_config(
                root,
                verify=((sys.executable, "-c", "print('project-ok')"),),
            )

            result = self.run_harness(root, "verify")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run = self.verification_runs(root)[0]
            manifest, gate = self.load_artifacts(run)
            target = manifest["target_evidence"]
            self.assertEqual(target["git_status"], "unavailable")
            self.assertEqual(target["actual_head_sha"], "")
            self.assertIsNone(target["clean"])
            self.assertEqual(target["changed_paths_status"], "unknown")
            self.assertIn("enclosing repositories were ignored", target["changed_paths_detail"])
            self.assertEqual(gate["target_evidence"], target)

    def test_explicit_local_target_records_changed_paths_without_parent_inference(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git is unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.init(root)
            self.write_config(
                root,
                verify=((sys.executable, "-c", "print('target-ok')"),),
            )
            (root / "src/value.py").write_text("VALUE = 1\n", encoding="utf-8")
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Verification Fixture"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "base"], cwd=root, check=True, capture_output=True)
            base = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True
            ).stdout.strip()
            (root / "src/value.py").write_text("VALUE = 2\n", encoding="utf-8")
            subprocess.run(["git", "add", "src/value.py"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "change value"], cwd=root, check=True, capture_output=True)
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True
            ).stdout.strip()

            result = self.run_harness(
                root,
                "verify",
                environment={
                    "REPORIVET_BASE_SHA": base,
                    "REPORIVET_HEAD_SHA": head,
                    "REPORIVET_TARGET": "local-test",
                },
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run = self.verification_runs(root)[0]
            manifest, gate = self.load_artifacts(run)
            target = manifest["target_evidence"]
            self.assertEqual(target["base_sha"], base)
            self.assertEqual(target["intended_head_sha"], head)
            self.assertEqual(target["actual_head_sha"], head)
            self.assertTrue(target["head_matches_intended"])
            self.assertTrue(target["clean"])
            self.assertEqual(target["changed_paths_status"], "available")
            self.assertEqual(target["changed_paths_method"], "git-diff-explicit-base-to-target")
            self.assertEqual(target["changed_paths"], ["src/value.py"])
            self.assertEqual(gate["target_evidence"], target)


if __name__ == "__main__":
    unittest.main()
