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

    def preview(self, root: Path) -> dict[str, object]:
        returncode, stdout, stderr = self.run_cli(
            "define", "finalize", "--root", str(root)
        )
        self.assertEqual(returncode, 0, stdout + stderr)
        return json.loads(stdout)

    def apply(self, root: Path, preview: dict[str, object]) -> tuple[int, str, str]:
        return self.run_cli(
            "define",
            "finalize",
            "--root",
            str(root),
            "--apply",
            "--approve-preview",
            str(preview["fingerprint"]),
        )

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
        secret_marker: str = "",
    ) -> None:
        preview = self.preview(root)
        action = self.settings_action(preview)
        self.assertEqual(action["action"], "conflict")
        self.assertEqual(action["content"], "")
        self.assertEqual(action["current_sha256"], "")
        self.assertIn("unsafe", action["reason"])
        if secret_marker:
            self.assertNotIn(secret_marker, json.dumps(preview))

        returncode, stdout, stderr = self.apply(root, preview)
        self.assertEqual(returncode, 2, stdout + stderr)
        self.assertIn("unsafe target conflicts", stderr)
        self.assertFalse((root / "AGENTS.md").exists())
        self.assertFalse((root / ".reporivet-version").exists())

    def test_default_profile_is_thin_portable_and_has_only_project_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.start(root)
            preview = self.preview(root)
            paths = {str(action["path"]) for action in preview["actions"]}
            self.assertNotIn(".claude/settings.json", paths)
            returncode, stdout, stderr = self.apply(root, preview)
            self.assertEqual(returncode, 0, stdout + stderr)

            self.assertEqual((root / "CLAUDE.md").read_bytes(), b"@AGENTS.md\n")
            self.assertFalse((root / ".claude").exists())
            for retired in (
                ".reporivet-version",
                ".gitignore",
                ".harness",
                ".claude/settings.json",
                ".claude/skills",
            ):
                self.assertFalse((root / retired).exists(), retired)
            self.assertEqual(
                list((root / "docs/exec-plans/active").glob("*.md")), []
            )
            self.assertEqual(
                list((root / "docs/exec-plans/completed").glob("*.md")), []
            )
            self.assertTrue((root / "docs/runbooks/index.md").is_file())

    def test_project_documents_encode_native_hierarchical_dispatch_contract(self) -> None:
        agents = read_asset("document-first/root/AGENTS.md.tmpl")
        plans = read_asset("document-first/docs/PLANS.md.tmpl")
        inventory = read_asset("document-first/docs/README.md.tmpl")
        formula = (
            "`T<n> (broad root Owner) -> T<n>-A/B/C/... (declared child packets, "
            "all ready leaves dispatched concurrently) -> T<n>-I (Owner-local aggregation) -> "
            "T<n>-V1/V2/... (parallel fresh verification)`"
        )
        for text in (agents, plans):
            self.assertIn(formula, text)
            self.assertIn("broad or multi-part", text)
            self.assertIn("Role: Task Owner", text)
            self.assertIn("May delegate: yes", text)
            self.assertIn("Ordinary leaf Agents", text)
            self.assertIn("never delegate", text)
            self.assertIn("integrated candidate", text)
        self.assertIn(formula, inventory)
        self.assertIn("Role: Task Owner", inventory)
        self.assertIn("May delegate: yes", inventory)
        self.assertIn("nondelegating", inventory)
        self.assertIn("integrated candidate", inventory)

        for phrase in (
            "finite child manifest",
            "Main alone serializes Plan edits",
            "host-native Agent execution",
            "no scheduler",
            "dispatcher",
            "Owner-local aggregation",
            "separate exact-baseline worktrees",
        ):
            self.assertIn(phrase, agents)
        for phrase in (
            "Setup handoff creates no Plan",
            "project commands and CI remain project/host-owned",
            "Reporivet installs no scheduler",
        ):
            self.assertIn(phrase, plans)
        self.assertIn("static runbooks", inventory)
        self.assertIn("No generated target requires a package", agents)

    def test_packaged_project_assets_encode_frozen_native_dispatch_contract(self) -> None:
        asset_paths = {
            "agents": "document-first/root/AGENTS.md.tmpl",
            "plans": "document-first/docs/PLANS.md.tmpl",
            "claude": "document-first/claude/CLAUDE.md.tmpl",
            "inventory": "document-first/docs/README.md.tmpl",
            "runbooks": "document-first/docs/runbooks/index.md.tmpl",
        }
        assets = {name: read_asset(path) for name, path in asset_paths.items()}
        self.assertEqual(assets["claude"], "@AGENTS.md\n")

        formula = (
            "`T<n> (broad root Owner) -> T<n>-A/B/C/... (declared child packets, "
            "all ready leaves dispatched concurrently) -> T<n>-I (Owner-local aggregation) -> "
            "T<n>-V1/V2/... (parallel fresh verification)`"
        )
        for name in ("agents", "plans"):
            text = assets[name]
            self.assertIn(formula, text)
            self.assertIn("Role: Task Owner", text)
            self.assertIn("May delegate: yes", text)
            self.assertIn("Ordinary leaf Agents", text)
            self.assertIn("never delegate", text)
            self.assertIn("integrated candidate", text)
        self.assertIn(formula, assets["inventory"])
        self.assertIn("Role: Task Owner", assets["inventory"])
        self.assertIn("May delegate: yes", assets["inventory"])
        self.assertIn("nondelegating", assets["inventory"])
        self.assertIn("integrated candidate", assets["inventory"])

        agents = assets["agents"]
        for phrase in (
            "finite child manifest",
            "Main alone serializes Plan edits",
            "host-native Agent execution",
            "disjoint allowed-write sets",
            "separate exact-baseline worktrees",
            "Owner-local aggregation",
            "no scheduler",
            "dispatcher",
        ):
            self.assertIn(phrase, agents)
        plans = assets["plans"]
        for phrase in (
            "Setup handoff creates no Plan",
            "searches active and completed history",
            "Reporivet installs no scheduler",
            "direct serial Plans remain supported",
        ):
            self.assertIn(phrase, plans)

        inventory = assets["inventory"]
        for path in (
            "AGENTS.md",
            "CLAUDE.md",
            "docs/PLANS.md",
            "docs/runbooks/index.md",
            "docs/runbooks/_template.md",
        ):
            self.assertIn(f"`{path}`", inventory)
        for retired in (
            ".claude/skills/reporivet-main/SKILL.md",
            ".claude/skills/reporivet-implementation/SKILL.md",
            ".claude/skills/reporivet-verification/SKILL.md",
        ):
            self.assertNotIn(f"`{retired}`", inventory)

        runbooks = assets["runbooks"]
        self.assertIn("ordinary Markdown", runbooks)
        self.assertIn("no frontmatter", runbooks)
        self.assertIn("not an executor", runbooks)

    def test_project_assets_define_integrated_setup_and_static_runbook_boundary(self) -> None:
        asset_paths = (
            "document-first/root/AGENTS.md.tmpl",
            "document-first/docs/README.md.tmpl",
            "document-first/docs/OPERATIONS.md.tmpl",
            "document-first/docs/PLANS.md.tmpl",
            "document-first/docs/references/project-definition-protocol.md.tmpl",
            "document-first/docs/runbooks/index.md.tmpl",
        )
        assets = {path: read_asset(path) for path in asset_paths}
        combined = "\\n".join(assets.values())
        for phrase in (
            "one-shot",
            "package-side only",
            "Setup handoff does not create a Plan",
            "complete, unique, user-confirmed strict",
            "docs/runbooks/<slug>.md",
            "during resumed setup",
            "no procedure is inferred or executed",
            "differing, stale, arbitrary",
            "ordinary Markdown",
            "Package absence after setup is expected",
            "no scheduler",
            "dispatcher",
            "task database",
            "command runner",
            "Gate",
            "evidence archive",
            "automatic closure",
        ):
            self.assertIn(phrase, combined)
        self.assertNotIn(".claude/skills/<slug>/SKILL.md", combined)
        self.assertNotIn("allowed-tools:", combined)
        self.assertNotIn("hooks:", combined)
        self.assertNotIn("executor:", combined)
        protocol = assets["document-first/docs/references/project-definition-protocol.md.tmpl"]
        self.assertIn("exactly these nine fields", protocol)
        self.assertIn("no additional fields or aliases are accepted", protocol)
        self.assertIn("does not execute project commands", protocol)
        self.assertIn("dispatch Agents, create a Plan", protocol)


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
            self.assertIn("preserve project-owned bytes", action["reason"])
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

            preview = self.preview(root)
            action = self.settings_action(preview)
            self.assertEqual(action["action"], "preserve")
            self.assertEqual(action["content"], "")
            self.assertEqual(
                action["current_sha256"],
                hashlib.sha256(b"").hexdigest(),
            )
            self.assertIn("preserve project-owned bytes", action["reason"])

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
                    self.assert_settings_conflict(
                        root,
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
                self.assert_settings_conflict(
                    root,
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
                preview = self.preview(root)

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
                self.assert_settings_conflict(root)
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
                self.assert_settings_conflict(root)
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
                self.assert_settings_conflict(
                    root,
                    secret_marker=secret_marker,
                )
            self.assertEqual(settings.read_bytes(), original)

    def test_fresh_setup_never_generates_optional_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.start(root)
            preview = self.preview(root)
            paths = {str(action["path"]) for action in preview["actions"]}
            self.assertNotIn(".claude/settings.json", paths)
            self.assertNotIn(".claude/settings.json", json.dumps(preview))

            returncode, stdout, stderr = self.apply(root, preview)
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertFalse((root / ".claude").exists())
            self.assertFalse((root / ".claude/settings.json").exists())

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
            preview = self.preview(root)

            local_documents = root / "docs"
            parked_documents = root / "docs-before-race"
            race_target = local_documents / "QUALITY.md"
            original_safe_write = guided.ensure_safe_write_path
            raced = False

            def race_after_path_check(path: Path) -> None:
                nonlocal raced
                original_safe_write(path)
                if path == race_target and not raced:
                    raced = True
                    local_documents.rename(parked_documents)
                    local_documents.symlink_to(external_root, target_is_directory=True)

            with mock.patch.object(
                guided,
                "ensure_safe_write_path",
                side_effect=race_after_path_check,
            ):
                returncode, stdout, stderr = self.apply(
                    root,
                    preview,
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

            preview = self.preview(root)
            actions = {str(action["path"]): action for action in preview["actions"]}
            self.assertEqual(actions[".claude/settings.json"]["action"], "preserve")
            self.assertEqual(actions[".claude/skills/reporivet-main/SKILL.md"]["action"], "preserve")
            self.assertIn("preserve project-owned bytes", actions[".claude/settings.json"]["reason"])
            returncode, stdout, stderr = self.apply(root, preview)
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertEqual(settings.read_bytes(), original)
            self.assertEqual(skill.read_bytes(), original_skill)

            second = self.preview(root)
            settings.write_bytes(b'{"changed":true}\n')
            returncode, _, stderr = self.apply(root, second)
            self.assertEqual(returncode, 2)
            self.assertIn("does not match", stderr)
            self.assertEqual(settings.read_bytes(), b'{"changed":true}\n')


if __name__ == "__main__":
    unittest.main()
