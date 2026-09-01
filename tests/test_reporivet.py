from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet import __version__
from reporivet.cli import build_parser, main as cli_main


EXPECTED_FRESH_FILES = {
    ".claude/skills/reporivet-implementation/SKILL.md",
    ".claude/skills/reporivet-main/SKILL.md",
    ".claude/skills/reporivet-verification/SKILL.md",
    ".gitignore",
    ".reporivet-version",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "CLAUDE.md",
    "docs/DESIGN.md",
    "docs/OPERATIONS.md",
    "docs/PLANS.md",
    "docs/PRODUCT.md",
    "docs/QUALITY.md",
    "docs/README.md",
    "docs/SECURITY.md",
    "docs/decisions/README.md",
    "docs/decisions/_template.md",
    "docs/design-docs/_template.md",
    "docs/design-docs/core-beliefs.md",
    "docs/design-docs/index.md",
    "docs/exec-plans/_template.md",
    "docs/exec-plans/active/.gitkeep",
    "docs/exec-plans/completed/.gitkeep",
    "docs/exec-plans/tech-debt-tracker.md",
    "docs/product-specs/_template.md",
    "docs/product-specs/index.md",
    "docs/references/README.md",
    "docs/references/project-definition-protocol.md",
    "docs/runbooks/_template.md",
    "docs/runbooks/index.md",
}

EXPECTED_FRESH_DIRECTORIES = {
    parent.as_posix()
    for relative in EXPECTED_FRESH_FILES
    for parent in Path(relative).parents
    if parent.as_posix() != "."
}

RETIRED_FRESH_PATHS = {
    ".github",
    ".harness",
    "dev",
    "docs/RELIABILITY.md",
    "docs/generated",
    "docs/module-contracts",
}


class ReporivetTests(unittest.TestCase):
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

    def init(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "init",
            "--root",
            str(root),
            "--name",
            "Test Project",
            "--summary",
            "A document-first repository fixture.",
            *extra,
        )

    def snapshot(self, root: Path) -> tuple[tuple[str, str, bytes | None], ...]:
        entries: list[tuple[str, str, bytes | None]] = []
        for current_text, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
            current = Path(current_text)
            for name in sorted(directory_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                entries.append((relative, "symlink" if path.is_symlink() else "directory", None))
            for name in sorted(file_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                entries.append(
                    (
                        relative,
                        "symlink" if path.is_symlink() else "file",
                        None if path.is_symlink() else path.read_bytes(),
                    )
                )
        return tuple(sorted(entries))

    def test_initializes_exact_document_first_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            files = {
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
                if path.is_file()
            }
            directories = {
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
                if path.is_dir()
            }
            self.assertEqual(files, EXPECTED_FRESH_FILES)
            self.assertEqual(directories, EXPECTED_FRESH_DIRECTORIES)
            for relative in RETIRED_FRESH_PATHS:
                self.assertFalse((root / relative).exists(), relative)

            self.assertEqual((root / "CLAUDE.md").read_bytes(), b"@AGENTS.md\n")
            self.assertEqual(
                (root / ".reporivet-version").read_text(encoding="utf-8"),
                "# reporivet:managed version=0.2.0\n0.2.0\n",
            )
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count("<!-- reporivet:start -->"), 1)
            self.assertEqual(agents.count("<!-- reporivet:end -->"), 1)
            self.assertNotIn("./dev/", agents)
            self.assertNotIn(".harness/runs", agents)

    def test_release_version_and_version_marker_are_in_sync(self) -> None:
        metadata = tomllib.loads((REPOSITORY / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(__version__, "0.2.0")
        self.assertNotIn("version", metadata["project"])
        self.assertEqual(metadata["project"]["dynamic"], ["version"])
        self.assertEqual(
            metadata["tool"]["setuptools"]["dynamic"]["version"],
            {"attr": "reporivet.__version__"},
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            marker = (root / ".reporivet-version").read_text(encoding="utf-8")
            self.assertEqual(marker.count(__version__), 2)

    def test_init_dry_run_is_read_only_for_missing_and_existing_roots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            missing = base / "missing"
            dry_missing = self.init(missing, "--dry-run")
            self.assertEqual(dry_missing.returncode, 0, dry_missing.stdout + dry_missing.stderr)
            self.assertFalse(missing.exists())

            existing = base / "existing"
            existing.mkdir()
            sentinel = existing / "project-owned.txt"
            sentinel.write_bytes(b"keep exact bytes  \n")
            before = self.snapshot(existing)
            dry_existing = self.init(existing, "--dry-run")
            self.assertEqual(dry_existing.returncode, 0, dry_existing.stdout + dry_existing.stderr)
            self.assertEqual(self.snapshot(existing), before)

    def test_nonlegacy_upgrade_maintains_only_document_first_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            initialized = self.init(root)
            self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)

            product = root / "docs/PRODUCT.md"
            product.write_bytes(b"# Project-owned product authority\n")
            missing_skill = root / ".claude/skills/reporivet-verification/SKILL.md"
            missing_skill.unlink()
            before_dry_run = self.snapshot(root)

            dry_run = self.run_cli("upgrade", "--root", str(root), "--dry-run")
            self.assertEqual(dry_run.returncode, 0, dry_run.stdout + dry_run.stderr)
            self.assertEqual(self.snapshot(root), before_dry_run)
            self.assertFalse(missing_skill.exists())

            upgraded = self.run_cli("upgrade", "--root", str(root))
            self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
            self.assertEqual(product.read_bytes(), b"# Project-owned product authority\n")
            self.assertTrue(missing_skill.is_file())
            for relative in RETIRED_FRESH_PATHS:
                self.assertFalse((root / relative).exists(), relative)

    def test_init_and_upgrade_preserve_project_owned_authority_and_host_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "docs").mkdir()
            agents_original = b"# Team instructions\n\nKeep this exact.  \n"
            product_original = b"# Existing product\n\nDo not rewrite.  "
            claude_original = b"# Existing host instructions\n"
            (root / "AGENTS.md").write_bytes(agents_original)
            (root / "docs/PRODUCT.md").write_bytes(product_original)
            (root / "CLAUDE.md").write_bytes(claude_original)

            initialized = self.init(root)
            self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
            self.assertTrue((root / "AGENTS.md").read_bytes().startswith(agents_original))
            self.assertEqual((root / "docs/PRODUCT.md").read_bytes(), product_original)
            self.assertEqual((root / "CLAUDE.md").read_bytes(), claude_original)

            upgraded = self.run_cli("upgrade", "--root", str(root))
            self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
            self.assertTrue((root / "AGENTS.md").read_bytes().startswith(agents_original))
            self.assertEqual((root / "docs/PRODUCT.md").read_bytes(), product_original)
            self.assertEqual((root / "CLAUDE.md").read_bytes(), claude_original)

    def test_doctor_root_directly_runs_structural_document_first_doctor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            initialized = self.init(root)
            self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)

            healthy = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(healthy.returncode, 0, healthy.stdout + healthy.stderr)
            self.assertEqual(json.loads(healthy.stdout)["schema"], "reporivet.doctor/v2")

            (root / "docs/OPERATIONS.md").unlink()
            broken = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(broken.returncode, 2, broken.stdout + broken.stderr)
            self.assertTrue(
                any(
                    finding["path"] == "docs/OPERATIONS.md"
                    and finding["severity"] == "error"
                    for finding in json.loads(broken.stdout)["findings"]
                )
            )

    def test_runtime_only_and_transitional_cli_paths_are_absent(self) -> None:
        parser = build_parser()
        rejected = (
            ("init", "--with-ci"),
            ("init", "--skip-check"),
            ("init", "--no-baseline-plan"),
            ("init", "--project-kind", "service"),
            ("init", "--primary-language", "Python"),
            ("init", "--runtime", "Python 3.13"),
            ("upgrade", "--with-ci"),
            ("upgrade", "--skip-check"),
            ("doctor", "--document-first"),
            ("define", "--adopt"),
        )
        for arguments in rejected:
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    parser.parse_args(list(arguments))

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["define", "--root", "."])


if __name__ == "__main__":
    unittest.main()
