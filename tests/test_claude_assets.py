from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet import guided
from reporivet.cli import main as cli_main
from reporivet.initializer import read_asset


class ClaudeAssetTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(list(args))
        return returncode, stdout.getvalue(), stderr.getvalue()

    def start(self, root: Path) -> None:
        returncode, stdout, stderr = self.run_cli("define", "start", "--root", str(root))
        self.assertEqual(returncode, 0, stdout + stderr)

    def preview(self, root: Path, *, settings: bool = False) -> dict[str, object]:
        args = ["define", "finalize", "--root", str(root)]
        if settings:
            args.append("--with-claude-settings")
        returncode, stdout, stderr = self.run_cli(*args)
        self.assertEqual(returncode, 0, stdout + stderr)
        return json.loads(stdout)

    def apply(self, root: Path, preview: dict[str, object], *, settings: bool = False) -> tuple[int, str, str]:
        args = [
            "define",
            "finalize",
            "--root",
            str(root),
            "--apply",
            "--approve-preview",
            str(preview["fingerprint"]),
        ]
        if settings:
            args.append("--with-claude-settings")
        return self.run_cli(*args)

    def settings_action(self, preview: dict[str, object]) -> dict[str, str]:
        return next(
            action
            for action in preview["actions"]
            if action["path"] == ".claude/settings.json"
        )

    def assert_settings_conflict(
        self,
        root: Path,
        *,
        settings_opt_in: bool = False,
        secret_marker: str = "",
    ) -> None:
        preview = self.preview(root, settings=settings_opt_in)
        action = self.settings_action(preview)
        self.assertEqual(action["action"], "conflict")
        self.assertEqual(action["content"], "")
        self.assertEqual(action["current_sha256"], "")
        self.assertIn("unsafe", action["reason"])
        if secret_marker:
            self.assertNotIn(secret_marker, json.dumps(preview))

        returncode, stdout, stderr = self.apply(
            root,
            preview,
            settings=settings_opt_in,
        )
        self.assertEqual(returncode, 2, stdout + stderr)
        self.assertIn("unsafe target conflicts", stderr)
        self.assertFalse((root / "AGENTS.md").exists())
        self.assertFalse((root / ".reporivet-version").exists())

    def test_default_profile_is_thin_portable_and_has_no_live_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.start(root)
            preview = self.preview(root)
            paths = {str(action["path"]) for action in preview["actions"]}
            self.assertNotIn(".claude/settings.json", paths)
            returncode, stdout, stderr = self.apply(root, preview)
            self.assertEqual(returncode, 0, stdout + stderr)

            self.assertEqual((root / "CLAUDE.md").read_bytes(), b"@AGENTS.md\n")
            self.assertFalse((root / ".claude/settings.json").exists())
            expected = {
                "reporivet-main",
                "reporivet-implementation",
                "reporivet-verification",
            }
            actual = {path.parent.name for path in (root / ".claude/skills").glob("*/SKILL.md")}
            self.assertEqual(actual, expected)
            for name in expected:
                path = root / ".claude/skills" / name / "SKILL.md"
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                frontmatter = text.split("---\n", 2)[1]
                self.assertRegex(frontmatter, rf"(?m)^name: {re.escape(name)}$")
                description = re.search(r"(?m)^description: (.+)$", frontmatter)
                self.assertIsNotNone(description)
                self.assertIn("Use when", description.group(1))
                self.assertNotRegex(frontmatter, r"(?m)^(allowed-tools|hooks|shell):")

            returncode, doctor_stdout, doctor_stderr = self.run_cli(
                "doctor",
                "--root",
                str(root),
            )
            self.assertEqual(returncode, 0, doctor_stdout + doctor_stderr)
            findings = json.loads(doctor_stdout)["findings"]
            self.assertEqual(
                [finding for finding in findings if finding["severity"] in {"error", "warning"}],
                [],
            )
            self.assertTrue(
                any(
                    finding["path"] == ".claude/settings.json"
                    and "absent by default" in finding["detail"]
                    for finding in findings
                )
            )

    def test_role_skills_encode_native_hierarchical_dispatch_contract(self) -> None:
        main = read_asset(
            "document-first/claude/skills/reporivet-main/SKILL.md.tmpl"
        )
        implementation = read_asset(
            "document-first/claude/skills/reporivet-implementation/SKILL.md.tmpl"
        )
        verification = read_asset(
            "document-first/claude/skills/reporivet-verification/SKILL.md.tmpl"
        )

        formula = (
            "`T<n> (broad milestone) -> T<n>-A/B/C/... (owned child packets, "
            "all ready leaves dispatched concurrently) -> T<n>-I (integration) -> "
            "T<n>-V1/V2/... (parallel fresh verification)`"
        )
        for skill in (main, implementation, verification):
            self.assertIn(formula, skill)
            self.assertIn("common installed-project rule", skill)
            self.assertIn("every milestone classified as broad", skill)
            self.assertIn(
                "does not apply to inherently single or serial milestones",
                skill,
            )
            self.assertIn("If a child is itself broad", skill)
            self.assertIn("`T<n>-A-1`", skill)
            self.assertIn("ordinary leaf Agents do not delegate", skill)

        for phrase in (
            "complete dependency-ready leaf set concurrently",
            "Main owns the overall task tree",
            "Main alone serializes Plan edits",
            "only the host's native Agent execution",
            "no scheduler, task store, lease, lock, or automatic dispatcher",
        ):
            self.assertIn(phrase, main)
        for phrase in (
            "`Role: Task Owner` and `May delegate: yes`",
            "predeclared bounded descendant packets",
            "inherit parent scope, protected paths, and acceptance",
            "cannot broaden",
            "disjoint allowed-write sets",
            "frozen shared interfaces",
            "separate worktrees",
        ):
            self.assertIn(phrase, implementation)
        for phrase in (
            "Read-only verification leaves may run concurrently",
            "depends on the integrated candidate",
            "Default verification leaves do not delegate",
            "candidate changes",
        ):
            self.assertIn(phrase, verification)

    def test_packaged_hierarchy_assets_encode_frozen_native_dispatch_contract(self) -> None:
        asset_paths = {
            "agents": "document-first/root/AGENTS.md.tmpl",
            "plans": "document-first/docs/PLANS.md.tmpl",
            "claude": "document-first/claude/CLAUDE.md.tmpl",
            "main": "document-first/claude/skills/reporivet-main/SKILL.md.tmpl",
            "implementation": "document-first/claude/skills/reporivet-implementation/SKILL.md.tmpl",
            "verification": "document-first/claude/skills/reporivet-verification/SKILL.md.tmpl",
        }
        assets = {name: read_asset(path) for name, path in asset_paths.items()}
        inventory = read_asset("document-first/docs/README.md.tmpl")
        expected_asset_paths = {
            *asset_paths.values(),
            "document-first/docs/README.md.tmpl",
        }

        for path in asset_paths.values():
            self.assertIn(path, expected_asset_paths)
        self.assertIn("document-first/docs/README.md.tmpl", expected_asset_paths)
        self.assertEqual(assets["claude"], "@AGENTS.md\n")

        for name in ("agents", "plans", "main", "implementation", "verification"):
            text = assets[name]
            self.assertIn("For every milestone classified as broad", text)
            self.assertIn("ordinary leaf Agents do not delegate", text)

        main = assets["main"]
        for phrase in (
            "broad",
            "multi-part",
            "root",
            "Role: Task Owner",
            "May delegate: yes",
            "finite",
            "accepted",
            "manifest",
            "checkpoint",
            "serializes",
            "dispatch",
            "declared",
            "host's native Agent execution",
            "final repository integration",
        ):
            self.assertIn(phrase, main)
        self.assertRegex(
            main,
            r"(?is)(?:broad|multi-part).{0,160}roots?.{0,160}Role: Task Owner.{0,100}May delegate: yes",
        )
        self.assertRegex(
            main,
            r"(?is)serializ\w*.{0,120}\bfinite\b.{0,80}\baccepted\b.{0,80}\bmanifest\b.{0,180}resum\w*",
        )
        self.assertRegex(main, r"(?is)\bmanifest\b.{0,160}\bresum\w*\b")
        self.assertRegex(main, r"(?is)\bindependent\b.{0,100}\broot\b.{0,120}\b(?:Task )?Owners?\b")
        self.assertRegex(main, r"(?is)\broot\b.{0,160}\bOwner\w*\b.{0,160}\bconcurr")
        self.assertRegex(
            main,
            r"(?is)\bonly\b.{0,140}\bresum\w*\b.{0,100}\bOwner\b.{0,180}\bdispatch\w*\b.{0,120}\bdeclared\b.{0,120}\bdependency-ready\b.{0,180}\bdescendant",
        )
        self.assertRegex(main, r"(?is)\bMain\b.{0,120}\bfinal integration\b")
        self.assertRegex(main, r"(?is)\b(?:narrow|inherently (?:single or )?serial)\b")
        self.assertRegex(
            main,
            r"(?is)(?:direct(?:ly)?\s+non[- ]delegating\s+leaves?|ordinary\s+leaf\s+Agents?\s+do\s+not\s+delegate)",
        )
        self.assertRegex(
            main,
            r"(?is)(?:\bnarrow\b|\binherently (?:single or )?serial\b).{0,220}\broot\b.{0,180}(?:direct(?:ly)?\s+non[- ]delegating|ordinary\s+leaf)",
        )

        implementation = assets["implementation"]
        for phrase in (
            "Role: Task Owner",
            "May delegate: yes",
            "predeclared bounded descendant packets",
            "inherit parent scope",
            "protected paths",
            "acceptance",
            "cannot broaden",
            "disjoint allowed-write sets",
            "frozen shared interfaces",
            "separate worktrees",
            "exact baseline",
        ):
            self.assertIn(phrase, implementation)
        implementation_lower = implementation.casefold()
        self.assertTrue(
            any(
                phrase in implementation_lower
                for phrase in (
                    "child budget",
                    "child-budget",
                    "descendant budget",
                    "descendant-budget",
                    "budget for child",
                    "budget for descendant",
                )
            )
        )
        self.assertIn("local aggregat", implementation_lower)

        verification = assets["verification"]
        for phrase in (
            "fresh context",
            "Read-only verification leaves may run concurrently",
            "depends on the integrated candidate",
            "Default verification leaves do not delegate",
        ):
            self.assertIn(phrase, verification)
        self.assertRegex(
            verification,
            r"(?is)(?:non[- ]repairing|Do not change the candidate)",
        )

        hierarchy_assets = "\n".join(
            assets[name] for name in ("agents", "plans", "main", "implementation", "verification")
        )
        no_runtime_assets = hierarchy_assets + "\n" + inventory
        for phrase in (
            "no scheduler",
            "no dispatcher",
            "task DB",
            "runner",
            "automatic closure",
        ):
            self.assertIn(phrase, no_runtime_assets)

        inventory_paths = (
            "AGENTS.md",
            "CLAUDE.md",
            "docs/PLANS.md",
            ".claude/skills/reporivet-main/SKILL.md",
            ".claude/skills/reporivet-implementation/SKILL.md",
            ".claude/skills/reporivet-verification/SKILL.md",
        )
        for path in inventory_paths:
            self.assertIn(f"`{path}`", inventory)

    def test_future_assets_define_integrated_setup_and_dynamic_procedure_skill_boundary(self) -> None:
        asset_paths = (
            "document-first/root/AGENTS.md.tmpl",
            "document-first/docs/README.md.tmpl",
            "document-first/docs/OPERATIONS.md.tmpl",
            "document-first/docs/PLANS.md.tmpl",
            "document-first/docs/references/project-definition-protocol.md.tmpl",
            "document-first/docs/runbooks/index.md.tmpl",
            "document-first/claude/skills/reporivet-main/SKILL.md.tmpl",
            "document-first/claude/skills/reporivet-implementation/SKILL.md.tmpl",
            "document-first/claude/skills/reporivet-verification/SKILL.md.tmpl",
        )
        assets = {path: read_asset(path) for path in asset_paths}
        combined = "\\n".join(assets.values())
        for phrase in (
            "reporivet setup",
            "reporivet init",
            "structure-only",
            "lower-level `reporivet define`",
            "Only complete Confirmed structured procedure records can produce",
            ".claude/skills/<slug>/SKILL.md",
            "through resumed",
            "no procedure is inferred or executed",
            "differing, stale, or arbitrary Skill",
            "Main—not package runtime",
            "visible Markdown",
            "pipx-primary",
            "same wheel",
            "Uninstalling Reporivet leaves repository artifacts useful",
            "no scheduler",
            "dispatcher",
            "task DB",
            "runner",
            "generated CI",
            "Gate",
            "evidence archive",
            "deployment engine",
            "automatic closure",
        ):
            self.assertIn(phrase, combined)

        for path in asset_paths[-3:]:
            text = assets[path]
            frontmatter = text.split("---\n", 2)[1]
            self.assertEqual(
                set(re.findall(r"(?m)^([A-Za-z][A-Za-z0-9_-]*):", frontmatter)),
                {"name", "description"},
            )
            self.assertIn("instruction-only", text)
            self.assertIn("least privilege", text)
            self.assertIn("Do not pre-generate a project-specific Skill", text)

    def test_default_preview_reports_existing_settings_without_content_leakage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            settings = root / ".claude/settings.json"
            settings.parent.mkdir(parents=True)
            secret_marker = "project-private-setting-value"
            original = json.dumps(
                {
                    "permissions": {"ask": ["Bash(*)"]},
                    "private": secret_marker,
                }
            ).encode("utf-8") + b"\n"
            settings.write_bytes(original)
            self.start(root)

            preview = self.preview(root)
            actions = {str(action["path"]): action for action in preview["actions"]}
            action = actions[".claude/settings.json"]
            self.assertEqual(action["action"], "preserve")
            self.assertEqual(action["content"], "")
            self.assertEqual(action["current_sha256"], hashlib.sha256(original).hexdigest())
            self.assertIn("never merges or rewrites", action["reason"])
            self.assertNotIn(secret_marker, json.dumps(preview))

            returncode, stdout, stderr = self.apply(root, preview)
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertEqual(settings.read_bytes(), original)

    def test_empty_settings_file_is_project_owned_and_never_artificially_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            settings = root / ".claude/settings.json"
            settings.parent.mkdir(parents=True)
            settings.write_bytes(b"")
            self.start(root)

            for settings_opt_in in (False, True):
                with self.subTest(settings_opt_in=settings_opt_in):
                    preview = self.preview(root, settings=settings_opt_in)
                    action = self.settings_action(preview)
                    self.assertEqual(action["action"], "preserve")
                    self.assertEqual(action["content"], "")
                    self.assertEqual(
                        action["current_sha256"],
                        hashlib.sha256(b"").hexdigest(),
                    )
                    self.assertIn("never merges or rewrites", action["reason"])

            preview = self.preview(root)
            returncode, stdout, stderr = self.apply(root, preview)
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertEqual(settings.read_bytes(), b"")

    def test_settings_symlink_and_dangling_symlink_are_explicit_conflicts_without_reads(self) -> None:
        for dangling in (False, True):
            with self.subTest(dangling=dangling), tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
                root = Path(directory).resolve()
                external_root = Path(external_directory).resolve()
                settings = root / ".claude/settings.json"
                settings.parent.mkdir(parents=True)
                target = external_root / ("missing.json" if dangling else "settings.json")
                secret_marker = "external-settings-secret"
                if not dangling:
                    target.write_text(secret_marker + "\n", encoding="utf-8")
                settings.symlink_to(target)
                self.start(root)

                original_reader = guided._read_regular_file_bytes
                with mock.patch.object(
                    guided,
                    "_read_regular_file_bytes",
                    wraps=original_reader,
                ) as reader:
                    for settings_opt_in in (False, True):
                        self.assert_settings_conflict(
                            root,
                            settings_opt_in=settings_opt_in,
                            secret_marker=secret_marker,
                        )
                self.assertFalse(
                    any(call.args and call.args[0] == settings for call in reader.call_args_list)
                )
                if dangling:
                    self.assertFalse(target.exists())
                else:
                    self.assertEqual(target.read_text(encoding="utf-8"), secret_marker + "\n")

    def test_symlinked_settings_parent_is_an_explicit_conflict_without_external_reads(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
            root = Path(directory).resolve()
            external_root = Path(external_directory).resolve()
            external_settings = external_root / "settings.json"
            secret_marker = "symlinked-parent-secret"
            external_settings.write_text(secret_marker + "\n", encoding="utf-8")
            (root / ".claude").symlink_to(external_root, target_is_directory=True)
            settings = root / ".claude/settings.json"
            self.start(root)

            original_reader = guided._read_regular_file_bytes
            with mock.patch.object(
                guided,
                "_read_regular_file_bytes",
                wraps=original_reader,
            ) as reader:
                for settings_opt_in in (False, True):
                    self.assert_settings_conflict(
                        root,
                        settings_opt_in=settings_opt_in,
                        secret_marker=secret_marker,
                    )
            self.assertFalse(
                any(call.args and call.args[0] == settings for call in reader.call_args_list)
            )
            self.assertEqual(external_settings.read_text(encoding="utf-8"), secret_marker + "\n")
            self.assertEqual(
                sorted(path.name for path in external_root.iterdir()),
                ["settings.json"],
            )

    def test_settings_preview_rejects_parent_replaced_after_initial_validation_without_external_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
            root = Path(directory).resolve()
            external_root = Path(external_directory).resolve()
            local_claude = root / ".claude"
            local_settings = local_claude / "settings.json"
            local_claude.mkdir()
            local_settings.write_bytes(b'{"local":true}\n')
            external_settings = external_root / "settings.json"
            secret_marker = "raced-external-settings-secret"
            external_bytes = (secret_marker + "\n").encode("utf-8")
            external_settings.write_bytes(external_bytes)
            self.start(root)

            original_reader = guided._read_regular_file_bytes
            original_open = guided.os.open
            external_identity = (
                external_settings.stat().st_dev,
                external_settings.stat().st_ino,
            )
            raced = False
            opened_external = False

            def race_parent(path: Path, **kwargs: object) -> bytes:
                nonlocal raced
                if path == local_settings and not raced:
                    raced = True
                    local_claude.rename(root / ".claude-before-race")
                    local_claude.symlink_to(external_root, target_is_directory=True)
                return original_reader(path, **kwargs)

            def track_open(
                path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
                flags: int,
                mode: int = 0o777,
                *,
                dir_fd: int | None = None,
            ) -> int:
                nonlocal opened_external
                descriptor = original_open(
                    path,
                    flags,
                    mode,
                    dir_fd=dir_fd,
                )
                metadata = os.fstat(descriptor)
                if (metadata.st_dev, metadata.st_ino) == external_identity:
                    opened_external = True
                return descriptor

            with mock.patch.object(
                guided,
                "_read_regular_file_bytes",
                side_effect=race_parent,
            ), mock.patch.object(
                guided.os,
                "open",
                side_effect=track_open,
            ):
                preview = self.preview(root, settings=True)

            action = self.settings_action(preview)
            self.assertEqual(action["action"], "conflict")
            self.assertEqual(action["content"], "")
            self.assertEqual(action["current_sha256"], "")
            self.assertNotIn(secret_marker, json.dumps(preview))
            self.assertNotEqual(
                action["current_sha256"],
                hashlib.sha256(external_bytes).hexdigest(),
            )
            self.assertFalse(opened_external)
            self.assertEqual(external_settings.read_bytes(), external_bytes)

    def test_settings_directory_is_an_explicit_conflict_without_a_content_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            settings = root / ".claude/settings.json"
            settings.mkdir(parents=True)
            self.start(root)

            original_reader = guided._read_regular_file_bytes
            with mock.patch.object(
                guided,
                "_read_regular_file_bytes",
                wraps=original_reader,
            ) as reader:
                for settings_opt_in in (False, True):
                    self.assert_settings_conflict(root, settings_opt_in=settings_opt_in)
            self.assertFalse(
                any(call.args and call.args[0] == settings for call in reader.call_args_list)
            )
            self.assertTrue(settings.is_dir())

    def test_settings_fifo_is_an_explicit_conflict_without_a_blocking_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            settings = root / ".claude/settings.json"
            settings.parent.mkdir(parents=True)
            os.mkfifo(settings)
            self.start(root)

            original_reader = guided._read_regular_file_bytes
            with mock.patch.object(
                guided,
                "_read_regular_file_bytes",
                wraps=original_reader,
            ) as reader:
                for settings_opt_in in (False, True):
                    self.assert_settings_conflict(root, settings_opt_in=settings_opt_in)
            self.assertFalse(
                any(call.args and call.args[0] == settings for call in reader.call_args_list)
            )
            self.assertTrue(stat.S_ISFIFO(settings.lstat().st_mode))

    def test_settings_read_error_is_redacted_conflict_and_apply_is_atomic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            settings = root / ".claude/settings.json"
            settings.parent.mkdir(parents=True)
            secret_marker = "unreadable-settings-secret"
            original = (secret_marker + "\n").encode("utf-8")
            settings.write_bytes(original)
            self.start(root)

            original_reader = guided._read_regular_file_bytes

            def fail_settings_read(path: Path, **kwargs: object) -> bytes:
                if path == settings:
                    raise PermissionError("simulated unreadable settings")
                return original_reader(path, **kwargs)

            with mock.patch.object(
                guided,
                "_read_regular_file_bytes",
                side_effect=fail_settings_read,
            ):
                for settings_opt_in in (False, True):
                    self.assert_settings_conflict(
                        root,
                        settings_opt_in=settings_opt_in,
                        secret_marker=secret_marker,
                    )
            self.assertEqual(settings.read_bytes(), original)

    def test_optional_settings_require_matching_preview_and_add_only_denials(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.start(root)
            preview = self.preview(root, settings=True)
            actions = {str(action["path"]): action for action in preview["actions"]}
            settings_action = actions[".claude/settings.json"]
            self.assertEqual(settings_action["action"], "create")
            proposed = json.loads(str(settings_action["content"]))
            self.assertEqual(
                proposed["$schema"],
                "https://json.schemastore.org/claude-code-settings.json",
            )
            self.assertEqual(set(proposed["permissions"]), {"deny"})
            self.assertTrue(proposed["permissions"]["deny"])
            self.assertNotIn("allow", proposed["permissions"])
            self.assertNotIn("ask", proposed["permissions"])
            self.assertNotIn("hooks", proposed)
            self.assertNotIn("mcpServers", proposed)

            returncode, _, stderr = self.apply(root, preview, settings=False)
            self.assertEqual(returncode, 2)
            self.assertIn("does not match", stderr)
            self.assertFalse((root / ".claude/settings.json").exists())

            returncode, stdout, stderr = self.apply(root, preview, settings=True)
            self.assertEqual(returncode, 0, stdout + stderr)
            installed = json.loads((root / ".claude/settings.json").read_text(encoding="utf-8"))
            self.assertEqual(installed, proposed)

    def test_apply_rejects_raced_claude_parent_without_external_mutation_or_rollback_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
            root = Path(directory).resolve()
            external_root = Path(external_directory).resolve()
            external_settings = external_root / "settings.json"
            external_skill = external_root / "skills/reporivet-implementation/SKILL.md"
            external_skill.parent.mkdir(parents=True)
            external_settings.write_bytes(b'{"external":"keep-settings"}\n')
            external_skill.write_bytes(b"keep external skill bytes\n")
            external_before = {
                path.relative_to(external_root).as_posix(): path.read_bytes()
                for path in external_root.rglob("*")
                if path.is_file()
            }
            external_directories_before = {
                path.relative_to(external_root).as_posix()
                for path in external_root.rglob("*")
                if path.is_dir()
            }
            self.start(root)
            preview = self.preview(root, settings=True)

            local_claude = root / ".claude"
            parked_claude = root / ".claude-before-race"
            race_target = local_claude / "skills/reporivet-implementation/SKILL.md"
            original_safe_write = guided.ensure_safe_write_path
            raced = False

            def race_after_path_check(path: Path) -> None:
                nonlocal raced
                original_safe_write(path)
                if path == race_target and not raced:
                    raced = True
                    local_claude.rename(parked_claude)
                    local_claude.symlink_to(external_root, target_is_directory=True)

            with mock.patch.object(
                guided,
                "ensure_safe_write_path",
                side_effect=race_after_path_check,
            ):
                returncode, stdout, stderr = self.apply(
                    root,
                    preview,
                    settings=True,
                )

            self.assertTrue(raced)
            self.assertEqual(returncode, 2, stdout + stderr)
            external_after = {
                path.relative_to(external_root).as_posix(): path.read_bytes()
                for path in external_root.rglob("*")
                if path.is_file()
            }
            external_directories_after = {
                path.relative_to(external_root).as_posix()
                for path in external_root.rglob("*")
                if path.is_dir()
            }
            self.assertEqual(external_after, external_before)
            self.assertEqual(external_directories_after, external_directories_before)
            self.assertFalse((external_root / "skills/reporivet-main").exists())
            self.assertFalse((external_root / "skills/reporivet-verification").exists())

    def test_existing_settings_are_preserved_without_merge_or_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            settings = root / ".claude/settings.json"
            settings.parent.mkdir(parents=True)
            original = b'{"permissions":{"ask":["Bash(*)"]},"custom":true}\n'
            settings.write_bytes(original)
            skill = root / ".claude/skills/reporivet-main/SKILL.md"
            skill.parent.mkdir(parents=True)
            original_skill = b"---\nname: reporivet-main\ndescription: Custom Main process. Use when project policy requires it.\n---\n\nKeep this project-owned procedure.\n"
            skill.write_bytes(original_skill)
            self.start(root)

            preview = self.preview(root, settings=True)
            actions = {str(action["path"]): action for action in preview["actions"]}
            self.assertEqual(actions[".claude/settings.json"]["action"], "preserve")
            self.assertEqual(actions[".claude/skills/reporivet-main/SKILL.md"]["action"], "preserve")
            self.assertIn("never merges or rewrites", actions[".claude/settings.json"]["reason"])
            returncode, stdout, stderr = self.apply(root, preview, settings=True)
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertEqual(settings.read_bytes(), original)
            self.assertEqual(skill.read_bytes(), original_skill)

            second = self.preview(root, settings=True)
            settings.write_bytes(b'{"changed":true}\n')
            returncode, _, stderr = self.apply(root, second, settings=True)
            self.assertEqual(returncode, 2)
            self.assertIn("does not match", stderr)
            self.assertEqual(settings.read_bytes(), b'{"changed":true}\n')


if __name__ == "__main__":
    unittest.main()
