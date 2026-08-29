from __future__ import annotations

import contextlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet import initializer
from reporivet.cli import main as cli_main
from reporivet.initializer import InitError, adopt_project


class AuditAdoptionTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(list(args))
        return subprocess.CompletedProcess(list(args), returncode, stdout.getvalue(), stderr.getvalue())

    def write_existing_repository(self, root: Path) -> dict[str, bytes]:
        files = {
            "README.md": b"# Existing product\n",
            "AGENTS.md": b"# Existing instructions\n\nKeep this exact.  \n",
            "ARCHITECTURE.md": b"# Existing architecture\n",
            "docs/README.md": b"# Existing docs\n\nCustom ending.  ",
            ".github/workflows/ci.yml": b"name: existing\n",
            "package.json": b'{"scripts":{"test":"node test.js"}}\n',
            "package-lock.json": b'{"lockfileVersion":3}\n',
            "src/main.js": b'console.log("ok")\n',
            "tests/test.js": b"// test\n",
        }
        for relative, payload in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        return files

    def install_runtime_only(self, root: Path) -> None:
        harness = root / "dev/harness.py"
        harness.parent.mkdir(parents=True, exist_ok=True)
        harness.write_text(
            initializer.read_asset(
                "dev/harness.py",
                {"HARNESS_VERSION": initializer.__version__},
            ),
            encoding="utf-8",
        )
        harness.chmod(harness.stat().st_mode | 0o111)
        audit = root / "dev/audit"
        audit.write_text(
            initializer.read_asset(
                "dev/wrapper.sh.tmpl",
                {
                    "HARNESS_VERSION": initializer.__version__,
                    "COMMAND": "audit",
                },
            ),
            encoding="utf-8",
        )
        audit.chmod(audit.stat().st_mode | 0o111)

    def tree_snapshot(self, root: Path) -> tuple[tuple[str, str, int, bytes | str | None], ...]:
        entries: list[tuple[str, str, int, bytes | str | None]] = []
        root_mode = stat.S_IMODE(root.lstat().st_mode)
        entries.append((".", "directory", root_mode, None))
        for current_text, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
            current = Path(current_text)
            for name in sorted(directory_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                mode = stat.S_IMODE(path.lstat().st_mode)
                if path.is_symlink():
                    entries.append((relative, "symlink", mode, os.readlink(path)))
                else:
                    entries.append((relative, "directory", mode, None))
            for name in sorted(file_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                mode = stat.S_IMODE(path.lstat().st_mode)
                if path.is_symlink():
                    entries.append((relative, "symlink", mode, os.readlink(path)))
                else:
                    entries.append((relative, "file", mode, path.read_bytes()))
        return tuple(sorted(entries))

    def test_package_audit_is_byte_stable_read_only_and_does_not_execute_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
            root = Path(directory).resolve()
            external = Path(external_directory).resolve()
            self.write_existing_repository(root)
            (root / ".git").mkdir()
            (root / ".git" / "config").write_text("repository metadata\n", encoding="utf-8")
            (root / "node_modules" / "dependency").mkdir(parents=True)
            (root / "node_modules" / "dependency" / "index.js").write_text("dependency\n", encoding="utf-8")
            secret = external / "outside.txt"
            secret.write_text("DO_NOT_REPORT_EXTERNAL_CONTENT\n", encoding="utf-8")
            (root / "linked-outside.txt").symlink_to(secret)
            sentinel = root / "audit-must-not-run-project-command"
            package = root / "package.json"
            package.write_text(
                json.dumps(
                    {
                        "scripts": {
                            "test": f"python -c 'from pathlib import Path; Path({str(sentinel)!r}).write_text(\"ran\")'"
                        }
                    },
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )

            before = self.tree_snapshot(root)
            first = self.run_cli("audit", "--root", str(root))
            second = self.run_cli("audit", "--root", str(root))
            after = self.tree_snapshot(root)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first.stdout.encode("utf-8"), second.stdout.encode("utf-8"))
            self.assertEqual(before, after)
            self.assertFalse(sentinel.exists())
            self.assertEqual(secret.read_bytes(), b"DO_NOT_REPORT_EXTERNAL_CONTENT\n")
            self.assertNotIn("DO_NOT_REPORT_EXTERNAL_CONTENT", first.stdout)
            self.assertNotIn(str(root), first.stdout)
            self.assertNotIn(str(external), first.stdout)
            self.assertNotRegex(first.stdout, r'"(?:generated_at|timestamp|run_id)"')

            report = json.loads(first.stdout)
            self.assertEqual(report["schema"], "reporivet.audit/v1")
            findings = report["findings"]
            self.assertEqual(
                findings,
                sorted(findings, key=lambda item: (item["category"], item["path"], item["status"], item["detail"])),
            )
            statuses = {finding["status"] for finding in findings}
            self.assertLessEqual(statuses, {"confirmed", "inferred", "unknown", "conflict", "skipped"})
            by_path = {(finding["category"], finding["path"], finding["status"]) for finding in findings}
            self.assertIn(("instruction", "AGENTS.md", "confirmed"), by_path)
            self.assertIn(("durable-document", "README.md", "confirmed"), by_path)
            self.assertIn(("manifest", "package.json", "confirmed"), by_path)
            self.assertIn(("lockfile", "package-lock.json", "confirmed"), by_path)
            self.assertIn(("ci", ".github/workflows/ci.yml", "confirmed"), by_path)
            self.assertIn(("source-path", "src", "confirmed"), by_path)
            self.assertIn(("test-path", "tests", "confirmed"), by_path)
            self.assertIn(("skipped-path", ".git", "skipped"), by_path)
            self.assertIn(("skipped-path", "node_modules", "skipped"), by_path)
            self.assertIn(("skipped-path", "linked-outside.txt", "skipped"), by_path)

    def test_adoption_preserves_authority_is_idempotent_and_runtime_audit_matches_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            originals = self.write_existing_repository(root)

            result = self.run_cli("define", "--root", str(root), "--adopt")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((root / "README.md").read_bytes(), originals["README.md"])
            self.assertEqual((root / "ARCHITECTURE.md").read_bytes(), originals["ARCHITECTURE.md"])
            self.assertEqual(
                (root / ".github/workflows/ci.yml").read_bytes(),
                originals[".github/workflows/ci.yml"],
            )
            self.assertEqual((root / "package.json").read_bytes(), originals["package.json"])
            self.assertEqual((root / "package-lock.json").read_bytes(), originals["package-lock.json"])
            self.assertTrue((root / "AGENTS.md").read_bytes().startswith(originals["AGENTS.md"]))
            self.assertTrue((root / "docs/README.md").read_bytes().startswith(originals["docs/README.md"]))
            config = (root / "dev/harness.toml").read_text(encoding="utf-8")
            self.assertIn('configuration = "review"', config)
            self.assertTrue((root / "docs/product-specs/project-definition.draft.md").is_file())
            self.assertTrue((root / "dev/audit").is_file())

            before_second_adoption = self.tree_snapshot(root)
            second = self.run_cli("define", "--root", str(root), "--adopt")
            after_second_adoption = self.tree_snapshot(root)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(before_second_adoption, after_second_adoption)

            package_audit = self.run_cli("audit", "--root", str(root))
            self.assertEqual(package_audit.returncode, 0, package_audit.stderr)
            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            runtime_audit = subprocess.run(
                [sys.executable, "-I", str(root / "dev/harness.py"), "audit"],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(runtime_audit.returncode, 0, runtime_audit.stderr)
            self.assertEqual(package_audit.stdout.encode("utf-8"), runtime_audit.stdout.encode("utf-8"))

    def test_configured_commands_are_redacted_without_reproducing_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_runtime_only(root)
            config = root / "dev/harness.toml"
            config.write_text(
                """version = 1

[project]
configuration = "ready"

[commands]
bootstrap = [["sh", "-c", "true;/Users/hakseong/ABSOLUTE_SENTINEL"]]
run = [["curl", "--token", "TOPSECRET_SENTINEL"]]
check = []
verify = []
smoke = []
architecture = []
""",
                encoding="utf-8",
            )

            package_audit = self.run_cli("audit", "--root", str(root))
            runtime_audit = subprocess.run(
                [sys.executable, "-I", str(root / "dev/harness.py"), "audit"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(package_audit.returncode, 0, package_audit.stderr)
            self.assertEqual(runtime_audit.returncode, 0, runtime_audit.stderr)
            self.assertEqual(package_audit.stdout, runtime_audit.stdout)
            for sentinel in ("/Users/hakseong/ABSOLUTE_SENTINEL", "TOPSECRET_SENTINEL"):
                self.assertNotIn(sentinel, package_audit.stdout)
            command_details = [
                finding["detail"]
                for finding in json.loads(package_audit.stdout)["findings"]
                if finding["category"] == "command" and finding["path"].count("/") == 2
            ]
            self.assertTrue(command_details)
            self.assertTrue(
                all(
                    detail.startswith("configured argv command; argc=") and detail.endswith("; content=redacted")
                    for detail in command_details
                )
            )

    def test_invalid_configuration_type_is_reported_as_conflict_json_by_package_and_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_runtime_only(root)
            (root / "dev/harness.toml").write_text(
                """version = 1

[project]
configuration = ["ready"]

[commands]
bootstrap = []
run = []
check = []
verify = []
smoke = []
architecture = []
""",
                encoding="utf-8",
            )

            package_audit = self.run_cli("audit", "--root", str(root))
            runtime_audit = subprocess.run(
                [sys.executable, "-I", str(root / "dev/harness.py"), "audit"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(package_audit.returncode, 0, package_audit.stderr)
            self.assertEqual(runtime_audit.returncode, 0, runtime_audit.stderr)
            self.assertEqual(package_audit.stdout, runtime_audit.stdout)
            self.assertNotIn("Traceback", runtime_audit.stderr)
            report = json.loads(package_audit.stdout)
            self.assertTrue(
                any(
                    finding["path"] == "dev/harness.toml"
                    and finding["status"] == "conflict"
                    and finding["category"] == "command"
                    for finding in report["findings"]
                )
            )

    def test_invalid_utf8_configuration_is_conflict_json_across_audit_entry_points(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_runtime_only(root)
            (root / "dev/harness.toml").write_bytes(b"\xff\xfe\x00")
            environment = os.environ.copy()
            environment["PYTHON"] = sys.executable

            package_audit = self.run_cli("audit", "--root", str(root))
            runtime_audit = subprocess.run(
                [sys.executable, "-I", str(root / "dev/harness.py"), "audit"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            wrapper_audit = subprocess.run(
                [str(root / "dev/audit")],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

            for result in (package_audit, runtime_audit, wrapper_audit):
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(package_audit.stdout, runtime_audit.stdout)
            self.assertEqual(package_audit.stdout, wrapper_audit.stdout)
            report = json.loads(package_audit.stdout)
            self.assertTrue(
                any(
                    finding["path"] == "dev/harness.toml"
                    and finding["status"] == "conflict"
                    and finding["category"] == "command"
                    for finding in report["findings"]
                )
            )

    def test_nonregular_configuration_blocks_adoption_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_runtime_only(root)
            config = root / "dev/harness.toml"
            config.mkdir()
            before = self.tree_snapshot(root)

            audit = self.run_cli("audit", "--root", str(root))
            runtime_audit = subprocess.run(
                [sys.executable, "-I", str(root / "dev/harness.py"), "audit"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            adoption = self.run_cli("define", "--root", str(root), "--adopt")

            self.assertEqual(audit.returncode, 0, audit.stderr)
            self.assertEqual(runtime_audit.returncode, 0, runtime_audit.stderr)
            self.assertEqual(audit.stdout, runtime_audit.stdout)
            self.assertEqual(adoption.returncode, 2)
            self.assertEqual(before, self.tree_snapshot(root))
            self.assertFalse((root / "docs/product-specs/project-definition.draft.md").exists())
            report = json.loads(audit.stdout)
            self.assertTrue(
                any(
                    finding["path"] == "dev/harness.toml"
                    and finding["status"] == "conflict"
                    and finding["category"] == "command"
                    for finding in report["findings"]
                )
            )

    def test_nonregular_command_inputs_are_conflicts_without_tracebacks(self) -> None:
        for relative in ("package.json", "pyproject.toml"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                self.install_runtime_only(root)
                (root / relative).mkdir()

                package_audit = self.run_cli("audit", "--root", str(root))
                runtime_audit = subprocess.run(
                    [sys.executable, "-I", str(root / "dev/harness.py"), "audit"],
                    cwd=root,
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(package_audit.returncode, 0, package_audit.stderr)
                self.assertEqual(runtime_audit.returncode, 0, runtime_audit.stderr)
                self.assertNotIn("Traceback", runtime_audit.stderr)
                self.assertEqual(package_audit.stdout, runtime_audit.stdout)
                report = json.loads(package_audit.stdout)
                self.assertTrue(
                    any(
                        finding["path"] == relative
                        and finding["status"] == "conflict"
                        and finding["category"] == "command"
                        for finding in report["findings"]
                    )
                )

    @unittest.skipIf(os.name == "nt", "POSIX permissions are required")
    def test_unreadable_command_inputs_are_conflicts_without_tracebacks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_runtime_only(root)
            pyproject = root / "pyproject.toml"
            managed = root / "dev/check"
            pyproject.write_text("[project]\nname = 'fixture'\n", encoding="utf-8")
            managed.write_text("#!/bin/sh\n", encoding="utf-8")
            pyproject.chmod(0)
            managed.chmod(0)
            try:
                package_audit = self.run_cli("audit", "--root", str(root))
                runtime_audit = subprocess.run(
                    [sys.executable, "-I", str(root / "dev/harness.py"), "audit"],
                    cwd=root,
                    text=True,
                    capture_output=True,
                    check=False,
                )
            finally:
                pyproject.chmod(0o600)
                managed.chmod(0o600)

            self.assertEqual(package_audit.returncode, 0, package_audit.stderr)
            self.assertEqual(runtime_audit.returncode, 0, runtime_audit.stderr)
            self.assertNotIn("Traceback", runtime_audit.stderr)
            self.assertEqual(package_audit.stdout, runtime_audit.stdout)
            conflicts = {
                finding["path"]
                for finding in json.loads(package_audit.stdout)["findings"]
                if finding["status"] == "conflict"
            }
            self.assertIn("pyproject.toml", conflicts)
            self.assertIn("dev/check", conflicts)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO support is required")
    def test_fifo_command_input_is_not_opened(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_runtime_only(root)
            os.mkfifo(root / "package.json")
            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment["PYTHONPATH"] = str(SRC)

            package_audit = subprocess.run(
                [sys.executable, "-m", "reporivet", "audit", "--root", str(root)],
                cwd=REPOSITORY,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )
            runtime_audit = subprocess.run(
                [sys.executable, "-I", str(root / "dev/harness.py"), "audit"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )

            self.assertEqual(package_audit.returncode, 0, package_audit.stderr)
            self.assertEqual(runtime_audit.returncode, 0, runtime_audit.stderr)
            self.assertEqual(package_audit.stdout, runtime_audit.stdout)
            report = json.loads(package_audit.stdout)
            self.assertTrue(
                any(
                    finding["path"] == "package.json"
                    and finding["status"] == "conflict"
                    and finding["category"] == "command"
                    for finding in report["findings"]
                )
            )

    def test_docs_only_adoption_creates_review_state_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            readme = root / "README.md"
            readme.write_text("# Existing documentation-only repository\n", encoding="utf-8")
            original = readme.read_bytes()

            result = self.run_cli("define", "--root", str(root), "--adopt")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(readme.read_bytes(), original)
            self.assertIn(
                'configuration = "review"',
                (root / "dev/harness.toml").read_text(encoding="utf-8"),
            )

    def test_incidental_marker_prose_is_preserved_and_receives_separate_managed_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "src").mkdir()
            (root / "src/main.py").write_text("print('existing')\n", encoding="utf-8")
            agents_original = (
                "# Existing instructions\n\n"
                "Document the literals `<!-- reporivet:start -->` and `<!-- reporivet:end -->` here.\n"
            ).encode("utf-8")
            catalog_original = (
                "# Existing docs\n\n"
                "Document `<!-- reporivet:catalog:start -->` and `<!-- reporivet:catalog:end -->` inline.\n"
            ).encode("utf-8")
            (root / "AGENTS.md").write_bytes(agents_original)
            (root / "docs").mkdir()
            (root / "docs/README.md").write_bytes(catalog_original)

            before = self.run_cli("audit", "--root", str(root))
            result = self.run_cli("define", "--root", str(root), "--adopt")

            self.assertEqual(before.returncode, 0, before.stderr)
            before_findings = json.loads(before.stdout)["findings"]
            self.assertTrue(
                any(
                    finding["path"] == "AGENTS.md"
                    and finding["category"] == "proposed-addition"
                    and finding["status"] == "inferred"
                    for finding in before_findings
                )
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            agents = (root / "AGENTS.md").read_bytes()
            catalog = (root / "docs/README.md").read_bytes()
            self.assertTrue(agents.startswith(agents_original))
            self.assertTrue(catalog.startswith(catalog_original))
            self.assertEqual(
                (root / "AGENTS.md").read_text(encoding="utf-8").splitlines().count("<!-- reporivet:start -->"),
                1,
            )
            self.assertEqual(
                (root / "docs/README.md")
                .read_text(encoding="utf-8")
                .splitlines()
                .count("<!-- reporivet:catalog:start -->"),
                1,
            )

    def test_fenced_marker_examples_are_preserved_and_do_not_claim_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "src").mkdir()
            (root / "src/main.py").write_text("print('existing')\n", encoding="utf-8")
            originals = {
                "AGENTS.md": (
                    "# Existing instructions\n\n"
                    "```markdown\n"
                    "<!-- reporivet:start -->\n"
                    "example agent block\n"
                    "<!-- reporivet:end -->\n"
                    "```\n"
                ).encode("utf-8"),
                "docs/README.md": (
                    "# Existing docs\n\n"
                    "~~~markdown\n"
                    "<!-- reporivet:catalog:start -->\n"
                    "example catalog block\n"
                    "<!-- reporivet:catalog:end -->\n"
                    "~~~\n"
                ).encode("utf-8"),
            }
            for relative, payload in originals.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)

            before = self.run_cli("audit", "--root", str(root))
            adoption = self.run_cli("define", "--root", str(root), "--adopt")

            self.assertEqual(before.returncode, 0, before.stderr)
            self.assertEqual(adoption.returncode, 0, adoption.stdout + adoption.stderr)
            findings = json.loads(before.stdout)["findings"]
            for relative in originals:
                self.assertTrue(
                    any(
                        finding["path"] == relative
                        and finding["category"] == "proposed-addition"
                        and finding["status"] == "inferred"
                        for finding in findings
                    ),
                    relative,
                )
                self.assertTrue((root / relative).read_bytes().startswith(originals[relative]))
            self.assertIn("example agent block", (root / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertIn(
                "example catalog block",
                (root / "docs/README.md").read_text(encoding="utf-8"),
            )

            docs_index = subprocess.run(
                [sys.executable, "-I", str(root / "dev/harness.py"), "docs-index"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            docs_check = subprocess.run(
                [sys.executable, "-I", str(root / "dev/harness.py"), "docs-index", "--check"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(docs_index.returncode, 0, docs_index.stdout + docs_index.stderr)
            self.assertEqual(docs_check.returncode, 0, docs_check.stdout + docs_check.stderr)
            for relative, payload in originals.items():
                self.assertTrue((root / relative).read_bytes().startswith(payload), relative)

    def test_adoption_and_docs_index_preserve_crlf_authority_outside_managed_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "src").mkdir()
            (root / "src/main.py").write_text("print('existing')\n", encoding="utf-8")
            originals = {
                "AGENTS.md": b"# Existing instructions\r\n\r\nKeep exact.  \r\n",
                ".gitignore": b"# Existing ignores\r\ncustom-output/\r\n",
                "docs/README.md": b"# Existing docs\r\n\r\nKeep catalog preface exact.  \r\n",
            }
            for relative, payload in originals.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)

            adoption = self.run_cli("define", "--root", str(root), "--adopt")

            self.assertEqual(adoption.returncode, 0, adoption.stdout + adoption.stderr)
            for relative, payload in originals.items():
                self.assertTrue((root / relative).read_bytes().startswith(payload), relative)

            docs_index = subprocess.run(
                [sys.executable, "-I", str(root / "dev/harness.py"), "docs-index"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            docs_check = subprocess.run(
                [sys.executable, "-I", str(root / "dev/harness.py"), "docs-index", "--check"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(docs_index.returncode, 0, docs_index.stdout + docs_index.stderr)
            self.assertEqual(docs_check.returncode, 0, docs_check.stdout + docs_check.stderr)
            for relative, payload in originals.items():
                self.assertTrue((root / relative).read_bytes().startswith(payload), relative)

    def test_adoption_refuses_unmarked_canonical_command_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "src").mkdir()
            (root / "src/main.py").write_text("print('existing')\n", encoding="utf-8")
            (root / "dev").mkdir()
            (root / "dev/check").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            before = self.tree_snapshot(root)

            result = self.run_cli("define", "--root", str(root), "--adopt")

            self.assertEqual(result.returncode, 2)
            self.assertIn("adoption audit found conflicts", result.stderr)
            self.assertIn("dev/check", result.stderr)
            self.assertEqual(before, self.tree_snapshot(root))
            report = json.loads(result.stdout)
            self.assertTrue(
                any(
                    finding["path"] == "dev/check" and finding["status"] == "conflict"
                    for finding in report["findings"]
                )
            )

    def test_adoption_refuses_malformed_shared_or_catalog_blocks_without_partial_output(self) -> None:
        cases = {
            "agents": ("AGENTS.md", "prefix\n<!-- reporivet:start -->\nmissing end\n"),
            "catalog": ("docs/README.md", "# Docs\n<!-- reporivet:catalog:start -->\nmissing end\n"),
        }
        for label, (relative, content) in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                (root / "src").mkdir()
                (root / "src/main.py").write_text("print('existing')\n", encoding="utf-8")
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
                before = self.tree_snapshot(root)

                result = self.run_cli("define", "--root", str(root), "--adopt")

                self.assertEqual(result.returncode, 2)
                self.assertIn("adoption audit found conflicts", result.stderr)
                self.assertEqual(before, self.tree_snapshot(root))
                self.assertFalse((root / "dev/harness.py").exists())
                self.assertFalse((root / "docs/product-specs/project-definition.draft.md").exists())

    def test_adoption_refuses_repository_symlinks_without_reading_or_writing_external_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
            root = Path(directory).resolve()
            external = Path(external_directory).resolve()
            (root / "src").mkdir()
            (root / "src/main.py").write_text("print('existing')\n", encoding="utf-8")
            (root / "docs").mkdir()
            external_specs = external / "product-specs"
            external_specs.mkdir()
            outside = external_specs / "outside.md"
            outside.write_text("outside authority\n", encoding="utf-8")
            (root / "docs/product-specs").symlink_to(external_specs, target_is_directory=True)
            before = self.tree_snapshot(root)
            external_before = self.tree_snapshot(external)

            audit = self.run_cli("audit", "--root", str(root))
            adoption = self.run_cli("define", "--root", str(root), "--adopt")

            self.assertEqual(audit.returncode, 0, audit.stderr)
            self.assertNotIn("outside authority", audit.stdout)
            self.assertEqual(adoption.returncode, 2)
            self.assertIn("docs/product-specs", adoption.stderr)
            self.assertEqual(before, self.tree_snapshot(root))
            self.assertEqual(external_before, self.tree_snapshot(external))

    def test_adoption_rolls_back_exact_tree_after_a_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.write_existing_repository(root)
            before = self.tree_snapshot(root)
            original_write_managed = initializer.write_managed
            calls = 0

            def fail_after_first_managed_write(*args: object, **kwargs: object) -> None:
                nonlocal calls
                original_write_managed(*args, **kwargs)
                calls += 1
                if calls == 1:
                    raise OSError("injected adoption write failure")

            with mock.patch.object(initializer, "write_managed", side_effect=fail_after_first_managed_write):
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaisesRegex(InitError, "adoption failed and was rolled back"):
                        adopt_project(root=root, dry_run=False)

            self.assertEqual(calls, 1)
            self.assertEqual(before, self.tree_snapshot(root))

    def test_audit_and_adoption_refuse_a_root_below_a_symlinked_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
            parent = Path(directory).resolve()
            external = Path(external_directory).resolve()
            repository = external / "repository"
            repository.mkdir()
            self.install_runtime_only(repository)
            sentinel = repository / "EXTERNAL-SENTINEL.md"
            sentinel.write_text("external authority\n", encoding="utf-8")
            linked_parent = parent / "linked-parent"
            linked_parent.symlink_to(external, target_is_directory=True)
            requested_root = linked_parent / "repository"
            before = self.tree_snapshot(repository)
            environment = os.environ.copy()
            environment["PYTHON"] = sys.executable

            audit = self.run_cli("audit", "--root", str(requested_root))
            adoption = self.run_cli("define", "--root", str(requested_root), "--adopt")
            runtime_audit = subprocess.run(
                [sys.executable, "-I", str(requested_root / "dev/harness.py"), "audit"],
                cwd=parent,
                text=True,
                capture_output=True,
                check=False,
            )
            wrapper_audit = subprocess.run(
                [str(requested_root / "dev/audit")],
                cwd=parent,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

            for result in (audit, adoption, runtime_audit, wrapper_audit):
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("symlinked project root or parent", result.stderr)
                self.assertNotIn("EXTERNAL-SENTINEL.md", result.stderr)
            self.assertEqual(before, self.tree_snapshot(repository))

    def test_audit_refuses_a_symlinked_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            root = parent / "repository"
            root.mkdir()
            (root / "README.md").write_text("# Existing\n", encoding="utf-8")
            alias = parent / "repository-link"
            alias.symlink_to(root, target_is_directory=True)

            result = self.run_cli("audit", "--root", str(alias))

            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("symlinked project root", result.stderr)
            self.assertEqual((root / "README.md").read_text(encoding="utf-8"), "# Existing\n")


if __name__ == "__main__":
    unittest.main()
