from __future__ import annotations

import contextlib
import io
import inspect
import json
import re
import sys
import tomllib
import types
import unittest
from pathlib import Path
from unittest.mock import patch

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
PACKAGE_ROOT = SRC / "reporivet"
PROJECT_ASSETS = PACKAGE_ROOT / "assets" / "project"
USER_SCOPED_ASSETS = PACKAGE_ROOT / "assets" / "user-scoped"
SETUP_SKILL = USER_SCOPED_ASSETS / "reporivet-setup" / "SKILL.md"
sys.path.insert(0, str(SRC))

from reporivet import cli, migration
from reporivet.procedures import build_procedure_runbook_plan


class _Rendered:
    def __init__(self, text: str) -> None:
        self.text = text

    def render(self) -> str:
        return self.text


class _FakeStdin:
    def isatty(self) -> bool:
        return False


class OneShotBootstrapperTests(unittest.TestCase):
    maxDiff = None

    def capture_main(self, arguments: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli.main(arguments)
        return returncode, stdout.getvalue(), stderr.getvalue()

    def test_help_and_parser_expose_only_successor_cli_surfaces(self) -> None:
        parser = cli.build_parser()
        help_text = parser.format_help()
        self.assertIn("setup", help_text)
        self.assertIn("migrate", help_text)
        self.assertNotIn("doctor", help_text.casefold())
        self.assertNotIn("--with-claude-settings", help_text)
        self.assertEqual(
            [name for name in vars(cli) if "doctor" in name.casefold()],
            [],
        )

        subparsers = next(
            action
            for action in parser._actions
            if getattr(action, "choices", None) is not None
        )
        setup_parser = subparsers.choices["setup"]
        migrate_parser = subparsers.choices["migrate"]
        self.assertIn("--backup-dir", setup_parser.format_help())
        self.assertIn("--preview", migrate_parser.format_help())
        self.assertIn("--apply", migrate_parser.format_help())
        self.assertIn("--rollback", migrate_parser.format_help())

        rejected = (
            ["doctor"],
            ["setup", "--root", "/tmp/project", "--with-claude-settings"],
            ["define", "finalize", "--with-claude-settings"],
        )
        for arguments in rejected:
            with self.subTest(arguments=arguments):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        parser.parse_args(arguments)

    def test_setup_launcher_dispatch_forwards_only_internal_false_settings_and_backup(self) -> None:
        calls: list[dict[str, object]] = []
        setup_module = types.ModuleType("reporivet.setup")

        def coordinate_setup(**kwargs: object) -> _Rendered:
            calls.append(kwargs)
            return _Rendered('{"schema":"reporivet.setup/v1"}\n')

        setup_module.coordinate_setup = coordinate_setup  # type: ignore[attr-defined]
        with patch.dict(sys.modules, {"reporivet.setup": setup_module}), patch.object(
            sys,
            "stdin",
            _FakeStdin(),
        ):
            returncode, stdout, stderr = self.capture_main(
                [
                    "setup",
                    "--root",
                    "/tmp/project",
                    "--backup-dir",
                    "/tmp/external-backup",
                    "--dry-run",
                ]
            )

        self.assertEqual(returncode, 0)
        self.assertEqual(stdout, '{"schema":"reporivet.setup/v1"}\n')
        self.assertEqual(stderr, "")
        self.assertEqual(
            calls,
            [
                {
                    "root": Path("/tmp/project"),
                    "answers": None,
                    "with_claude_settings": False,
                    "dry_run": True,
                    "apply": False,
                    "approve_preview": "",
                    "stdin_is_tty": False,
                    "backup_dir": Path("/tmp/external-backup"),
                }
            ],
        )

    def test_define_dispatch_keeps_settings_internal_only(self) -> None:
        preview_calls: list[dict[str, object]] = []
        with patch.object(
            cli,
            "preview_guided_setup",
            side_effect=lambda **kwargs: (
                preview_calls.append(kwargs) or _Rendered("preview\n")
            ),
        ):
            returncode, stdout, stderr = self.capture_main(
                ["define", "finalize", "--root", "/tmp/project"]
            )

        self.assertEqual(returncode, 0)
        self.assertEqual(stdout, "preview\n")
        self.assertEqual(stderr, "")
        self.assertEqual(
            preview_calls,
            [{"root": Path("/tmp/project"), "with_claude_settings": False}],
        )

    def test_public_migrate_parser_dispatch_and_contract_remain_unchanged(self) -> None:
        parser = cli.build_parser()
        preview_args = parser.parse_args(
            [
                "migrate",
                "--root",
                "/tmp/project",
                "--from",
                "0.2",
                "--preview",
                "--backup-dir",
                "/tmp/external-backup",
            ]
        )
        self.assertEqual(preview_args.command, "migrate")
        self.assertEqual(preview_args.from_version, "0.2")
        self.assertTrue(preview_args.preview)
        self.assertFalse(preview_args.apply)
        self.assertIsNone(preview_args.rollback)

        with patch.object(
            cli,
            "preview_migration",
            return_value=_Rendered('{"schema":"reporivet.migration-preview/v1"}\n'),
        ) as preview_migration, patch.object(
            cli,
            "apply_migration",
            return_value=_Rendered('{"schema":"reporivet.migration-result/v1"}\n'),
        ) as apply_migration, patch.object(
            cli,
            "rollback_migration",
            return_value=_Rendered('{"schema":"reporivet.migration-result/v1"}\n'),
        ) as rollback_migration:
            code, stdout, stderr = self.capture_main(
                [
                    "migrate",
                    "--root",
                    "/tmp/project",
                    "--from",
                    "0.2",
                    "--preview",
                    "--backup-dir",
                    "/tmp/external-backup",
                ]
            )
            self.assertEqual(code, 0)
            self.assertEqual(stdout, '{"schema":"reporivet.migration-preview/v1"}\n')
            self.assertEqual(stderr, "")
            preview_migration.assert_called_once_with(
                root=Path("/tmp/project"),
                from_version="0.2",
                backup_dir=Path("/tmp/external-backup"),
            )

            code, stdout, stderr = self.capture_main(
                [
                    "migrate",
                    "--root",
                    "/tmp/project",
                    "--from",
                    "0.2",
                    "--apply",
                    "--approve-preview",
                    "a" * 64,
                    "--backup-dir",
                    "/tmp/external-backup",
                ]
            )
            self.assertEqual(code, 0)
            self.assertEqual(stdout, '{"schema":"reporivet.migration-result/v1"}\n')
            self.assertEqual(stderr, "")
            apply_migration.assert_called_once_with(
                root=Path("/tmp/project"),
                from_version="0.2",
                approve_preview="a" * 64,
                backup_dir=Path("/tmp/external-backup"),
            )

            code, stdout, stderr = self.capture_main(
                ["migrate", "--rollback", "/tmp/external-backup/manifest.json"]
            )
            self.assertEqual(code, 0)
            self.assertEqual(stdout, '{"schema":"reporivet.migration-result/v1"}\n')
            self.assertEqual(stderr, "")
            rollback_migration.assert_called_once_with(
                manifest=Path("/tmp/external-backup/manifest.json")
            )

        self.assertEqual(
            tuple(inspect.signature(migration.preview_migration).parameters),
            ("root", "from_version", "backup_dir"),
        )
        self.assertEqual(
            tuple(inspect.signature(migration.apply_migration).parameters),
            ("root", "from_version", "approve_preview", "backup_dir"),
        )
        self.assertEqual(
            tuple(inspect.signature(migration.rollback_migration).parameters),
            ("manifest",),
        )

    def test_static_confirmed_procedure_runbooks_have_no_skill_or_executor_surface(self) -> None:
        record = json.dumps(
            {
                "slug": "release-check",
                "title": "Release check",
                "trigger": "a release candidate is ready",
                "reads": ["docs/QUALITY.md"],
                "actions": ["review project-owned evidence"],
                "stop_conditions": ["required evidence is missing"],
                "evidence": ["record the review result"],
                "permissions": ["maintainer approval"],
                "rollback": ["return to the prior candidate"],
            },
            separators=(",", ":"),
        )
        plan = build_procedure_runbook_plan([record, "a generic procedure note"])
        self.assertEqual([target.path for target in plan.targets], ["docs/runbooks/release-check.md"])
        content = plan.targets[0].content
        self.assertTrue(content.startswith("# Release check\n"))
        self.assertNotIn("---\n", content)
        self.assertNotIn("allowed-tools", content)
        self.assertNotIn("hooks", content)
        self.assertNotIn("executor", content)
        self.assertEqual(plan.diagnostics[0].code, "generic")

    def test_package_data_matches_surviving_assets_and_external_skill(self) -> None:
        metadata = tomllib.loads(
            (REPOSITORY / "pyproject.toml").read_text(encoding="utf-8")
        )
        setuptools = metadata["tool"]["setuptools"]
        package_data = setuptools["package-data"]["reporivet"]
        self.assertEqual(
            package_data,
            [
                "assets/project/document-first/root/*.tmpl",
                "assets/project/document-first/docs/*.tmpl",
                "assets/project/document-first/docs/*/*.tmpl",
                "assets/project/document-first/claude/*.tmpl",
                "assets/user-scoped/reporivet-setup/SKILL.md",
            ],
        )
        self.assertFalse(setuptools["include-package-data"])
        self.assertNotIn("exclude-package-data", setuptools)

        expected_assets = {
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
        actual_assets = {
            path.relative_to(PROJECT_ASSETS).as_posix()
            for path in PROJECT_ASSETS.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}
        }
        self.assertEqual(actual_assets, expected_assets)
        self.assertEqual(
            {
                path.relative_to(USER_SCOPED_ASSETS).as_posix()
                for path in USER_SCOPED_ASSETS.rglob("*")
                if path.is_file()
            },
            {"reporivet-setup/SKILL.md"},
        )
        self.assertTrue(SETUP_SKILL.is_file())
        self.assertNotIn(PROJECT_ASSETS, SETUP_SKILL.parents)

        declared_files = {
            path.relative_to(PACKAGE_ROOT).as_posix()
            for pattern in package_data
            for path in PACKAGE_ROOT.glob(pattern)
            if path.is_file()
        }
        expected_declared_files = {
            *(f"assets/project/{relative}" for relative in expected_assets),
            "assets/user-scoped/reporivet-setup/SKILL.md",
        }
        self.assertEqual(declared_files, expected_declared_files)
        for retired in (
            "skills",
            "optional",
            "reporivet-version",
            "gitignore",
            "doctor",
            "runtime",
        ):
            self.assertNotIn(retired, " ".join(actual_assets).casefold())

    def test_external_setup_skill_is_instruction_only_and_not_an_installer(self) -> None:
        content = SETUP_SKILL.read_text(encoding="utf-8")
        self.assertRegex(content, r"\A---\nname: reporivet-setup\ndescription: .+\n---\n")
        frontmatter = content.split("---\n", 2)[1]
        self.assertEqual(
            set(re.findall(r"(?m)^([A-Za-z][A-Za-z0-9_-]*):", frontmatter)),
            {"name", "description"},
        )
        self.assertIn("reporivet setup --root", content)
        self.assertIn("--apply --approve-preview", content)
        self.assertIn("external backup", content)
        self.assertIn("instruction-only", content)
        for phrase in (
            "install, download, resolve, or reproduce Reporivet",
            "does not itself write target files",
        ):
            self.assertIn(phrase, content)
        self.assertRegex(content, r"execute\s+project commands")
        self.assertRegex(content, r"perform model-authored\s+filesystem mutation")
        for phrase in (
            "allowed-tools:",
            "tools:",
            "permissions:",
            "hooks:",
            "shell:",
            "pip install",
            "python -m pip",
            "npm install",
            "curl ",
            "wget ",
            "git clone",
        ):
            self.assertNotIn(phrase, content.casefold())
        self.assertNotIn("--with-claude-settings", content)
        self.assertNotIn("doctor", content.casefold())


if __name__ == "__main__":
    unittest.main()
