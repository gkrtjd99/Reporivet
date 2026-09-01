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

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet.cli import main as cli_main


class AuditTests(unittest.TestCase):
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

    def tree_snapshot(self, root: Path) -> tuple[tuple[str, str, int, bytes | str | None], ...]:
        entries: list[tuple[str, str, int, bytes | str | None]] = [
            (".", "directory", stat.S_IMODE(root.lstat().st_mode), None)
        ]
        for current_text, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
            current = Path(current_text)
            for name in sorted(directory_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                mode = stat.S_IMODE(path.lstat().st_mode)
                entries.append(
                    (relative, "symlink" if path.is_symlink() else "directory", mode, os.readlink(path) if path.is_symlink() else None)
                )
            for name in sorted(file_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                mode = stat.S_IMODE(path.lstat().st_mode)
                entries.append(
                    (relative, "symlink" if path.is_symlink() else "file", mode, os.readlink(path) if path.is_symlink() else path.read_bytes())
                )
        return tuple(sorted(entries))

    def test_package_audit_is_byte_stable_read_only_and_does_not_execute_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
            root = Path(directory).resolve()
            external = Path(external_directory).resolve()
            self.write_existing_repository(root)
            (root / ".git").mkdir()
            (root / ".git/config").write_text("repository metadata\n", encoding="utf-8")
            (root / "node_modules/dependency").mkdir(parents=True)
            (root / "node_modules/dependency/index.js").write_text("dependency\n", encoding="utf-8")
            secret = external / "outside.txt"
            secret.write_text("DO_NOT_REPORT_EXTERNAL_CONTENT\n", encoding="utf-8")
            (root / "linked-outside.txt").symlink_to(secret)
            sentinel = root / "audit-must-not-run-project-command"
            (root / "package.json").write_text(
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

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first.stdout.encode("utf-8"), second.stdout.encode("utf-8"))
            self.assertEqual(before, self.tree_snapshot(root))
            self.assertFalse(sentinel.exists())
            self.assertEqual(secret.read_bytes(), b"DO_NOT_REPORT_EXTERNAL_CONTENT\n")
            self.assertNotIn("DO_NOT_REPORT_EXTERNAL_CONTENT", first.stdout)
            self.assertNotIn(str(root), first.stdout)
            self.assertNotIn(str(external), first.stdout)

            report = json.loads(first.stdout)
            self.assertEqual(report["schema"], "reporivet.audit/v1")
            findings = report["findings"]
            self.assertEqual(
                findings,
                sorted(
                    findings,
                    key=lambda item: (
                        item["category"],
                        item["path"],
                        item["status"],
                        item["detail"],
                    ),
                ),
            )
            by_path = {
                (finding["category"], finding["path"], finding["status"])
                for finding in findings
            }
            for expected in (
                ("instruction", "AGENTS.md", "confirmed"),
                ("durable-document", "README.md", "confirmed"),
                ("manifest", "package.json", "confirmed"),
                ("lockfile", "package-lock.json", "confirmed"),
                ("ci", ".github/workflows/ci.yml", "confirmed"),
                ("source-path", "src", "confirmed"),
                ("test-path", "tests", "confirmed"),
                ("skipped-path", ".git", "skipped"),
                ("skipped-path", "node_modules", "skipped"),
                ("skipped-path", "linked-outside.txt", "skipped"),
            ):
                self.assertIn(expected, by_path)

    def test_configured_commands_are_redacted_without_reproducing_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            config = root / "dev/harness.toml"
            config.parent.mkdir()
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

            audit = self.run_cli("audit", "--root", str(root))

            self.assertEqual(audit.returncode, 0, audit.stderr)
            for sentinel in ("/Users/hakseong/ABSOLUTE_SENTINEL", "TOPSECRET_SENTINEL"):
                self.assertNotIn(sentinel, audit.stdout)
            command_details = [
                finding["detail"]
                for finding in json.loads(audit.stdout)["findings"]
                if finding["category"] == "command" and finding["path"].count("/") == 2
            ]
            self.assertTrue(command_details)
            self.assertTrue(
                all(
                    detail.startswith("configured argv command; argc=")
                    and detail.endswith("; content=redacted")
                    for detail in command_details
                )
            )

    def test_invalid_configuration_is_reported_as_conflict_json(self) -> None:
        payloads = (
            b"\xff\xfe\x00",
            b'version = 1\n[project]\nconfiguration = ["ready"]\n[commands]\n',
        )
        for payload in payloads:
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                config = root / "dev/harness.toml"
                config.parent.mkdir()
                config.write_bytes(payload)

                audit = self.run_cli("audit", "--root", str(root))

                self.assertEqual(audit.returncode, 0, audit.stderr)
                self.assertNotIn("Traceback", audit.stderr)
                self.assertTrue(
                    any(
                        finding["path"] == "dev/harness.toml"
                        and finding["status"] == "conflict"
                        and finding["category"] == "command"
                        for finding in json.loads(audit.stdout)["findings"]
                    )
                )

    def test_nonregular_command_inputs_are_conflicts_without_tracebacks(self) -> None:
        for relative in ("dev/harness.toml", "package.json", "pyproject.toml"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                (root / relative).mkdir(parents=True)

                audit = self.run_cli("audit", "--root", str(root))

                self.assertEqual(audit.returncode, 0, audit.stderr)
                self.assertNotIn("Traceback", audit.stderr)
                self.assertTrue(
                    any(
                        finding["path"] == relative
                        and finding["status"] == "conflict"
                        and finding["category"] == "command"
                        for finding in json.loads(audit.stdout)["findings"]
                    )
                )

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO support is required")
    def test_fifo_command_input_is_not_opened(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            os.mkfifo(root / "package.json")
            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment["PYTHONPYCACHEPREFIX"] = str(root.parent / "external-pycache")
            environment["PYTHONPATH"] = str(SRC)

            audit = subprocess.run(
                [sys.executable, "-m", "reporivet", "audit", "--root", str(root)],
                cwd=REPOSITORY,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )

            self.assertEqual(audit.returncode, 0, audit.stderr)
            self.assertTrue(
                any(
                    finding["path"] == "package.json"
                    and finding["status"] == "conflict"
                    and finding["category"] == "command"
                    for finding in json.loads(audit.stdout)["findings"]
                )
            )

    def test_audit_refuses_symlinked_root_or_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
            parent = Path(directory).resolve()
            external = Path(external_directory).resolve()
            repository = external / "repository"
            repository.mkdir()
            sentinel = repository / "EXTERNAL-SENTINEL.md"
            sentinel.write_text("external authority\n", encoding="utf-8")
            linked_parent = parent / "linked-parent"
            linked_parent.symlink_to(external, target_is_directory=True)
            before = self.tree_snapshot(repository)

            below_parent = self.run_cli(
                "audit",
                "--root",
                str(linked_parent / "repository"),
            )
            root_alias = parent / "repository-link"
            root_alias.symlink_to(repository, target_is_directory=True)
            direct = self.run_cli("audit", "--root", str(root_alias))

            for result in (below_parent, direct):
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("symlinked project root", result.stderr)
                self.assertNotIn("EXTERNAL-SENTINEL.md", result.stderr)
            self.assertEqual(before, self.tree_snapshot(repository))


if __name__ == "__main__":
    unittest.main()
