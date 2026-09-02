from __future__ import annotations

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
PACKAGE_ROOT = SRC / "reporivet"
ASSETS = PACKAGE_ROOT / "assets" / "project"
USER_SCOPED_ASSETS = PACKAGE_ROOT / "assets" / "user-scoped"
SETUP_SKILL = USER_SCOPED_ASSETS / "reporivet-setup" / "SKILL.md"
sys.path.insert(0, str(SRC))

from reporivet.cli import main as cli_main


EXPECTED_PACKAGE_DATA = [
    "assets/project/document-first/root/*.tmpl",
    "assets/project/document-first/docs/*.tmpl",
    "assets/project/document-first/docs/*/*.tmpl",
    "assets/project/document-first/claude/*.tmpl",
    "assets/user-scoped/reporivet-setup/SKILL.md",
]

EXPECTED_ASSETS = {
    "document-first/claude/CLAUDE.md.tmpl",
    "document-first/docs/DESIGN.md.tmpl",
    "document-first/docs/OPERATIONS.md.tmpl",
    "document-first/docs/PLANS.md.tmpl",
    "document-first/docs/PRODUCT.md.tmpl",
    "document-first/docs/QUALITY.md.tmpl",
    "document-first/docs/README.md.tmpl",
    "document-first/docs/SECURITY.md.tmpl",
    "document-first/docs/decisions/README.md.tmpl",
    "document-first/docs/decisions/_template.md.tmpl",
    "document-first/docs/design-docs/_template.md.tmpl",
    "document-first/docs/design-docs/core-beliefs.md.tmpl",
    "document-first/docs/design-docs/index.md.tmpl",
    "document-first/docs/exec-plans/_template.md.tmpl",
    "document-first/docs/exec-plans/tech-debt-tracker.md.tmpl",
    "document-first/docs/product-specs/_template.md.tmpl",
    "document-first/docs/product-specs/index.md.tmpl",
    "document-first/docs/references/README.md.tmpl",
    "document-first/docs/references/project-definition-protocol.md.tmpl",
    "document-first/docs/runbooks/_template.md.tmpl",
    "document-first/docs/runbooks/index.md.tmpl",
    "document-first/root/AGENTS.md.tmpl",
    "document-first/root/ARCHITECTURE.md.tmpl",
}

EXPECTED_EXTERNAL_ASSETS = {"reporivet-setup/SKILL.md"}

RETIRED_ASSET_PATHS = {
    "document-first/claude/skills/reporivet-implementation/SKILL.md.tmpl",
    "document-first/claude/skills/reporivet-main/SKILL.md.tmpl",
    "document-first/claude/skills/reporivet-verification/SKILL.md.tmpl",
    "document-first/optional/claude-settings.deny-only.json.tmpl",
    "document-first/root/gitignore.block.tmpl",
    "root/reporivet-version.tmpl",
}

RETIRED_ASSET_PARTS = {
    "dev",
    "github",
    "generated",
    "module-contracts",
}


class DistributionTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(list(args))
        return subprocess.CompletedProcess(list(args), returncode, stdout.getvalue(), stderr.getvalue())

    def run_command(
        self,
        *command: str | Path,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(part) for part in command],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )

    def test_project_metadata_uses_spdx_license_and_explicit_license_file(self) -> None:
        metadata = tomllib.loads((REPOSITORY / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(metadata["build-system"]["requires"], ["setuptools>=77"])
        project = metadata["project"]
        self.assertEqual(project["license"], "MIT")
        self.assertEqual(project["license-files"], ["LICENSE"])
        self.assertNotIn("License :: OSI Approved :: MIT License", project["classifiers"])

    def test_static_package_data_inventory_contains_only_surviving_assets_and_external_skill(self) -> None:
        metadata = tomllib.loads((REPOSITORY / "pyproject.toml").read_text(encoding="utf-8"))
        setuptools = metadata["tool"]["setuptools"]
        package_data = setuptools["package-data"]["reporivet"]
        self.assertEqual(package_data, EXPECTED_PACKAGE_DATA)
        self.assertFalse(setuptools["include-package-data"])
        self.assertNotIn("exclude-package-data", setuptools)

        actual = {
            path.relative_to(ASSETS).as_posix()
            for path in ASSETS.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix not in {".pyc", ".pyo"}
        }
        self.assertEqual(actual, EXPECTED_ASSETS)
        self.assertEqual(
            {
                path.relative_to(USER_SCOPED_ASSETS).as_posix()
                for path in USER_SCOPED_ASSETS.rglob("*")
                if path.is_file()
            },
            EXPECTED_EXTERNAL_ASSETS,
        )
        self.assertTrue(SETUP_SKILL.is_file())
        self.assertNotIn(ASSETS, SETUP_SKILL.parents)

        declared_files = {
            path.relative_to(PACKAGE_ROOT).as_posix()
            for pattern in package_data
            for path in PACKAGE_ROOT.glob(pattern)
            if path.is_file()
        }
        expected_declared_files = {
            *(f"assets/project/{relative}" for relative in EXPECTED_ASSETS),
            *(f"assets/user-scoped/{relative}" for relative in EXPECTED_EXTERNAL_ASSETS),
        }
        self.assertEqual(declared_files, expected_declared_files)

        for relative in RETIRED_ASSET_PATHS:
            self.assertFalse((ASSETS / relative).exists(), relative)
        for relative in actual:
            parts = set(Path(relative).parts)
            self.assertTrue(parts.isdisjoint(RETIRED_ASSET_PARTS), relative)
            self.assertNotIn("harness", Path(relative).name.casefold(), relative)
            self.assertNotIn("code-map", Path(relative).name.casefold(), relative)
            self.assertNotIn("reliability", Path(relative).name.casefold(), relative)

    def test_document_first_repository_remains_useful_without_package_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            project_command = root / "project-check.py"
            project_command.write_text(
                "from pathlib import Path\n"
                "assert Path('docs/PRODUCT.md').is_file()\n"
                "assert Path('docs/exec-plans/_template.md').is_file()\n"
                "print('project-check-ok')\n",
                encoding="utf-8",
            )
            initialized = self.run_cli(
                "init",
                "--root",
                str(root),
                "--name",
                "Distribution Fixture",
                "--summary",
                "A document-first repository that survives package removal.",
            )
            self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
            self.assertFalse((root / "dev").exists())
            self.assertFalse((root / ".harness").exists())

            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            command = self.run_command(
                sys.executable,
                "-I",
                project_command,
                cwd=root,
                env=environment,
            )
            self.assertEqual(command.returncode, 0, command.stdout + command.stderr)
            self.assertEqual(command.stdout, "project-check-ok\n")

            independent = self.run_command(
                sys.executable,
                "-I",
                "-c",
                (
                    "from pathlib import Path; "
                    "root=Path('.'); "
                    "assert '<!-- reporivet:start -->' not in (root/'AGENTS.md').read_text(); "
                    "assert (root/'CLAUDE.md').read_text() == '@AGENTS.md\\n'; "
                    "assert not (root/'.claude').exists(); "
                    "assert not (root/'.reporivet-version').exists(); "
                    "assert not (root/'.gitignore').exists(); "
                    "assert not (root/'reporivet').exists(); "
                    "assert not list((root/'docs/exec-plans/active').glob('PLAN-*.md')); "
                    "template=(root/'docs/exec-plans/_template.md').read_text(); "
                    "assert 'format: 2' in template and '## Task Packets' in template; "
                    "target=root/'docs/exec-plans/active/PLAN-2099-0001-package-free.md'; "
                    "target.write_text(template.replace('PLAN-YYYY-NNNN','PLAN-2099-0001',1)); "
                    "assert target.is_file()"
                ),
                cwd=root,
                env=environment,
            )
            self.assertEqual(independent.returncode, 0, independent.stdout + independent.stderr)

            if shutil.which("git") is not None:
                initialized_git = self.run_command("git", "init", "-b", "main", cwd=root)
                self.assertEqual(
                    initialized_git.returncode,
                    0,
                    initialized_git.stdout + initialized_git.stderr,
                )
                status = self.run_command("git", "status", "--short", cwd=root)
                self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
                self.assertIn("AGENTS.md", status.stdout)


if __name__ == "__main__":
    unittest.main()
