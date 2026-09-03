from __future__ import annotations

import contextlib
import hashlib
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

from reporivet import guided, migration
from reporivet.cli import main as cli_main
from reporivet.initializer import InitError

FIXTURES = REPOSITORY / "tests" / "fixtures" / "legacy-02"
LEGACY_WRAPPERS = (
    "bootstrap",
    "context",
    "define",
    "audit",
    "code-map",
    "run",
    "check",
    "verify",
    "smoke",
    "security-check",
    "docs-index",
    "docs-check",
    "plan-check",
    "architecture-check",
    "new-plan",
    "task",
    "close-plan",
    "garden",
)


class MigrationTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(list(args))
        return subprocess.CompletedProcess(list(args), returncode, stdout.getvalue(), stderr.getvalue())

    def legacy_fixture(self, relative: str, values: dict[str, str] | None = None) -> bytes:
        text = (FIXTURES / relative).read_text(encoding="utf-8")
        for key, value in (values or {}).items():
            text = text.replace("{{" + key + "}}", value)
        return (text.rstrip() + "\n").encode("utf-8")

    def install_canonical_02(self, root: Path) -> None:
        (root / "AGENTS.md").write_bytes(b"# Existing 0.2 instructions\n")
        (root / ".gitignore").write_bytes(b"# Existing project ignores\n")
        (root / "docs/exec-plans/active").mkdir(parents=True, exist_ok=True)
        (root / "docs/exec-plans/completed").mkdir(parents=True, exist_ok=True)
        (root / "dev").mkdir(parents=True, exist_ok=True)
        harness = root / "dev/harness.py"
        harness.write_bytes(
            self.legacy_fixture(
                "dev/harness.py.tmpl",
                {"HARNESS_VERSION": "0.2.0"},
            )
        )
        harness.chmod(0o755)
        for command in LEGACY_WRAPPERS:
            wrapper = root / "dev" / command
            wrapper.write_bytes(
                self.legacy_fixture(
                    "dev/wrapper.sh.tmpl",
                    {
                        "COMMAND": command,
                        "HARNESS_VERSION": "0.2.0",
                    },
                )
            )
            wrapper.chmod(0o755)
        (root / "dev/harness.toml").write_bytes(
            (FIXTURES / "dev/harness.toml").read_bytes()
        )

        workflows = root / ".github/workflows"
        workflows.mkdir(parents=True, exist_ok=True)
        for name in ("harness-verify.yml", "harness-garden.yml"):
            workflows.joinpath(name).write_bytes(
                self.legacy_fixture(
                    f"github/{name}.tmpl",
                    {"HARNESS_VERSION": "0.2.0"},
                )
            )

        for relative in (".harness/runs", ".harness/tmp", ".harness/worktrees"):
            directory = root / relative
            directory.mkdir(parents=True, exist_ok=True)
            (directory / ".gitkeep").write_bytes(b"")

    def preview_cli(self, root: Path, backup: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = self.run_cli(
            "migrate",
            "--root",
            str(root),
            "--from",
            "0.2",
            "--preview",
            "--backup-dir",
            str(backup),
        )
        payload = json.loads(result.stdout) if result.stdout else {}
        return result, payload

    def apply_cli(
        self,
        root: Path,
        backup: Path,
        fingerprint: str,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = self.run_cli(
            "migrate",
            "--root",
            str(root),
            "--from",
            "0.2",
            "--apply",
            "--approve-preview",
            fingerprint,
            "--backup-dir",
            str(backup),
        )
        payload = json.loads(result.stdout) if result.stdout else {}
        return result, payload

    def tree_snapshot(self, root: Path) -> tuple[tuple[str, str, int, bytes | str | None], ...]:
        entries: list[tuple[str, str, int, bytes | str | None]] = [
            (".", "directory", stat.S_IMODE(root.lstat().st_mode), None)
        ]
        for current_text, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
            current = Path(current_text)
            for name in sorted(directory_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                metadata = path.lstat()
                mode = stat.S_IMODE(metadata.st_mode)
                if stat.S_ISLNK(metadata.st_mode):
                    entries.append((relative, "symlink", mode, os.readlink(path)))
                else:
                    entries.append((relative, "directory", mode, None))
            for name in sorted(file_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                metadata = path.lstat()
                mode = stat.S_IMODE(metadata.st_mode)
                if stat.S_ISLNK(metadata.st_mode):
                    entries.append((relative, "symlink", mode, os.readlink(path)))
                elif stat.S_ISREG(metadata.st_mode):
                    entries.append((relative, "regular", mode, path.read_bytes()))
                elif stat.S_ISFIFO(metadata.st_mode):
                    entries.append((relative, "fifo", mode, None))
                else:
                    entries.append((relative, "nonregular", mode, None))
        return tuple(sorted(entries))

    @staticmethod
    def inventory_by_path(payload: dict[str, object]) -> dict[str, dict[str, object]]:
        return {
            str(entry["path"]): entry
            for entry in payload["legacy_inventory"]  # type: ignore[index]
        }

    def test_preview_is_repeatable_byte_stable_read_only_and_inventories_exact_canonical_02(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root = base / "repository"
            backup = base / "visible-backup"
            root.mkdir()
            self.install_canonical_02(root)
            project_command_sentinel = root / "project-command-ran"
            (root / "project-command").write_text(
                f"would create {project_command_sentinel}\n",
                encoding="utf-8",
            )
            before = self.tree_snapshot(root)

            with mock.patch.object(
                subprocess,
                "run",
                side_effect=AssertionError("migration preview must not execute project commands"),
            ):
                first, first_payload = self.preview_cli(root, backup)
                second, second_payload = self.preview_cli(root, backup)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first.stdout.encode("utf-8"), second.stdout.encode("utf-8"))
            self.assertEqual(first_payload, second_payload)
            self.assertEqual(first_payload["schema"], "reporivet.migration-preview/v1")
            self.assertRegex(str(first_payload["fingerprint"]), r"^[0-9a-f]{64}$")
            self.assertEqual(before, self.tree_snapshot(root))
            self.assertFalse(backup.exists())
            self.assertFalse(project_command_sentinel.exists())

            inventory = self.inventory_by_path(first_payload)
            expected = {
                "dev/harness.py",
                "dev/bootstrap",
                "dev/context",
                "dev/define",
                "dev/audit",
                "dev/code-map",
                "dev/run",
                "dev/check",
                "dev/verify",
                "dev/smoke",
                "dev/security-check",
                "dev/docs-index",
                "dev/docs-check",
                "dev/plan-check",
                "dev/architecture-check",
                "dev/new-plan",
                "dev/task",
                "dev/close-plan",
                "dev/garden",
                "dev/harness.toml",
                "dev",
                ".github/workflows/harness-verify.yml",
                ".github/workflows/harness-garden.yml",
                ".harness/runs",
                ".harness/tmp",
                ".harness/worktrees",
            }
            self.assertEqual(set(inventory), expected)
            for relative, entry in inventory.items():
                self.assertEqual(entry["path"], relative)
                self.assertIn("lstat_type", entry)
                self.assertIn("current_sha256", entry)
                self.assertIn("ownership", entry)
                self.assertIn("action", entry)
                self.assertIn("reason", entry)
                self.assertIn("reversible", entry)
                self.assertIn("review_required", entry)
                self.assertIn("backup_destination", entry)
            removable = expected - {".harness/runs", ".harness/tmp", ".harness/worktrees"}
            for relative in removable:
                self.assertEqual(inventory[relative]["action"], "remove", relative)
                if relative != "dev":
                    self.assertEqual(inventory[relative]["ownership"], "reporivet-canonical-0.2")
            self.assertEqual(inventory[".harness/runs"]["action"], "retain")
            self.assertEqual(inventory[".harness/runs"]["current_sha256"], "")
            self.assertIsNone(inventory[".harness/runs"]["current_mode"])

            other_backup = base / "different-backup"
            before_wrong_backup = self.tree_snapshot(root)
            with self.assertRaisesRegex(InitError, "approval does not match"):
                migration.apply_migration(
                    root=root,
                    from_version="0.2",
                    approve_preview=str(first_payload["fingerprint"]),
                    backup_dir=other_backup,
                )
            self.assertEqual(before_wrong_backup, self.tree_snapshot(root))
            self.assertFalse(other_backup.exists())

    def test_customized_marker_files_and_mixed_project_dev_content_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root = base / "repository"
            backup = base / "backup"
            root.mkdir()
            self.install_canonical_02(root)
            customized = root / "dev/check"
            customized.write_bytes(customized.read_bytes() + b"# customized but still marker-bearing\n")
            customized_before = customized.read_bytes()
            project_tool = root / "dev/project-tool"
            project_tool.write_bytes(b"#!/bin/sh\nprintf project-owned\\n\n")
            project_tool.chmod(0o751)
            project_tool_before = project_tool.read_bytes()

            preview = migration.preview_migration(
                root=root,
                from_version="0.2",
                backup_dir=backup,
            )
            inventory = {entry.path: entry for entry in preview.legacy_inventory}
            self.assertEqual(inventory["dev/check"].ownership, "reporivet-customized")
            self.assertEqual(inventory["dev/check"].action, "preserve")
            self.assertTrue(inventory["dev/check"].review_required)
            self.assertEqual(inventory["dev"].action, "preserve")
            self.assertIn("project-owned or preserved content", inventory["dev"].reason)

            result = migration.apply_migration(
                root=root,
                from_version="0.2",
                approve_preview=preview.fingerprint,
                backup_dir=backup,
            )

            self.assertEqual(result.status, "applied")
            self.assertEqual(customized.read_bytes(), customized_before)
            self.assertEqual(project_tool.read_bytes(), project_tool_before)
            self.assertEqual(stat.S_IMODE(project_tool.stat().st_mode), 0o751)
            self.assertTrue((root / "dev").is_dir())
            self.assertFalse((root / "dev/harness.py").exists())
            self.assertFalse((root / "dev/verify").exists())

    def test_canonical_and_custom_harness_config_are_classified_conservatively(self) -> None:
        for customized in (False, True):
            with self.subTest(customized=customized), tempfile.TemporaryDirectory() as directory:
                base = Path(directory).resolve()
                root = base / "repository"
                backup = base / "backup"
                root.mkdir()
                self.install_canonical_02(root)
                config = root / "dev/harness.toml"
                if customized:
                    config.write_bytes(config.read_bytes() + b"\n# project customization\n")
                before = config.read_bytes()

                preview = migration.preview_migration(
                    root=root,
                    from_version="0.2",
                    backup_dir=backup,
                )
                entry = {item.path: item for item in preview.legacy_inventory}[
                    "dev/harness.toml"
                ]
                self.assertEqual(entry.action, "preserve" if customized else "remove")
                self.assertEqual(
                    entry.ownership,
                    "project-owned" if customized else "reporivet-canonical-0.2",
                )
                migration.apply_migration(
                    root=root,
                    from_version="0.2",
                    approve_preview=preview.fingerprint,
                    backup_dir=backup,
                )
                if customized:
                    self.assertEqual(config.read_bytes(), before)
                else:
                    self.assertFalse(config.exists())

    def test_canonical_customized_and_project_owned_workflows_obey_exact_ownership(self) -> None:
        cases = ("canonical", "customized-marker", "project-owned")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                base = Path(directory).resolve()
                root = base / "repository"
                backup = base / "backup"
                root.mkdir()
                self.install_canonical_02(root)
                target = root / ".github/workflows/harness-verify.yml"
                unrelated = root / ".github/workflows/ci.yml"
                unrelated.write_bytes(b"name: project-ci\n")
                if case == "customized-marker":
                    target.write_bytes(target.read_bytes() + b"\n# customized\n")
                elif case == "project-owned":
                    target.write_bytes(b"name: project-owned-at-canonical-path\n")
                target_before = target.read_bytes()

                preview = migration.preview_migration(
                    root=root,
                    from_version="0.2",
                    backup_dir=backup,
                )
                entry = {item.path: item for item in preview.legacy_inventory}[
                    ".github/workflows/harness-verify.yml"
                ]
                expected_action = "remove" if case == "canonical" else "preserve"
                expected_owner = {
                    "canonical": "reporivet-canonical-0.2",
                    "customized-marker": "reporivet-customized",
                    "project-owned": "project-owned",
                }[case]
                self.assertEqual(entry.action, expected_action)
                self.assertEqual(entry.ownership, expected_owner)
                self.assertNotIn(
                    ".github/workflows/ci.yml",
                    {item.path for item in preview.legacy_inventory},
                )

                migration.apply_migration(
                    root=root,
                    from_version="0.2",
                    approve_preview=preview.fingerprint,
                    backup_dir=backup,
                )
                self.assertEqual(unrelated.read_bytes(), b"name: project-ci\n")
                if case == "canonical":
                    self.assertFalse(target.exists())
                else:
                    self.assertEqual(target.read_bytes(), target_before)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO support is required")
    def test_symlink_fifo_and_changed_candidate_refuse_without_following_or_writing(self) -> None:
        for kind in ("symlink", "fifo"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                base = Path(directory).resolve()
                root = base / "repository"
                backup = base / "backup"
                external = base / "external"
                root.mkdir()
                self.install_canonical_02(root)
                target = root / "dev/check"
                target.unlink()
                if kind == "symlink":
                    external.write_bytes(b"external bytes must remain unread and unchanged\n")
                    target.symlink_to(external)
                else:
                    os.mkfifo(target)

                preview = migration.preview_migration(
                    root=root,
                    from_version="0.2",
                    backup_dir=backup,
                )
                entry = {item.path: item for item in preview.legacy_inventory}[
                    "dev/check"
                ]
                self.assertEqual(entry.lstat_type, kind)
                self.assertEqual(entry.current_sha256, "")
                self.assertEqual(entry.action, "refuse")
                before_external = external.read_bytes() if external.exists() else b""
                with self.assertRaisesRegex(InitError, "blocker"):
                    migration.apply_migration(
                        root=root,
                        from_version="0.2",
                        approve_preview=preview.fingerprint,
                        backup_dir=backup,
                    )
                self.assertFalse(backup.exists())
                if external.exists():
                    self.assertEqual(external.read_bytes(), before_external)

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root = base / "repository"
            backup = base / "backup"
            root.mkdir()
            self.install_canonical_02(root)
            preview = migration.preview_migration(
                root=root,
                from_version="0.2",
                backup_dir=backup,
            )
            (root / "dev/check").write_bytes(
                (root / "dev/check").read_bytes() + b"# changed after preview\n"
            )
            before = self.tree_snapshot(root)
            with self.assertRaisesRegex(InitError, "approval does not match"):
                migration.apply_migration(
                    root=root,
                    from_version="0.2",
                    approve_preview=preview.fingerprint,
                    backup_dir=backup,
                )
            self.assertEqual(before, self.tree_snapshot(root))
            self.assertFalse(backup.exists())

    def test_active_legacy_plan_fields_block_apply_while_completed_history_is_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root = base / "repository"
            backup = base / "backup"
            root.mkdir()
            self.install_canonical_02(root)
            active = root / "docs/exec-plans/active/PLAN-0001-active.md"
            active.write_text(
                """---
id: PLAN-0001
kind: exec-plan
status: verifying
owner: main
verification_run: ""
manifest_sha256: ""
gate_verdict: ""
---

# Active legacy plan
""",
                encoding="utf-8",
            )
            completed = root / "docs/exec-plans/completed/PLAN-0000-history.md"
            completed.write_text(
                """---
id: PLAN-0000
kind: exec-plan
status: complete
owner: main
verification_run: RUN-old
manifest_sha256: old
gate_verdict: pass
---

# Historical Gate plan
""",
                encoding="utf-8",
            )
            completed_before = completed.read_bytes()

            preview = migration.preview_migration(
                root=root,
                from_version="0.2",
                backup_dir=backup,
            )
            self.assertEqual(len(preview.plan_blockers), 1)
            self.assertEqual(preview.plan_blockers[0]["path"], active.relative_to(root).as_posix())
            self.assertEqual(
                preview.plan_blockers[0]["fields"],
                ["gate_verdict", "manifest_sha256", "verification_run"],
            )
            with self.assertRaisesRegex(InitError, "active Plan"):
                migration.apply_migration(
                    root=root,
                    from_version="0.2",
                    approve_preview=preview.fingerprint,
                    backup_dir=backup,
                )
            self.assertFalse(backup.exists())
            self.assertEqual(completed.read_bytes(), completed_before)

            active.write_text(
                """---
id: PLAN-0001
kind: exec-plan
format: 2
status: verifying
owner: main
---

# Active document-first plan
""",
                encoding="utf-8",
            )
            current = migration.preview_migration(
                root=root,
                from_version="0.2",
                backup_dir=backup,
            )
            migration.apply_migration(
                root=root,
                from_version="0.2",
                approve_preview=current.fingerprint,
                backup_dir=backup,
            )
            self.assertEqual(completed.read_bytes(), completed_before)
            self.assertIn("status: verifying", active.read_text(encoding="utf-8"))

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO support is required")
    def test_retained_runs_trap_proves_contents_are_not_listed_read_or_backed_up(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root = base / "repository"
            backup = base / "backup"
            root.mkdir()
            self.install_canonical_02(root)
            runs = root / ".harness/runs"
            (runs / ".gitkeep").unlink()
            trap = runs / "DO-NOT-OPEN-OR-LIST-THIS-FIFO"
            os.mkfifo(trap)
            secret = runs / "private-evidence.txt"
            secret.write_bytes(b"PRIVATE-RUN-CONTENT-MUST-NOT-APPEAR\n")
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(SRC)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment["PYTHONPYCACHEPREFIX"] = str(base / "external-pycache")
            real_listdir = os.listdir
            runs_identity = (runs.stat().st_dev, runs.stat().st_ino)

            def refuse_runs_listing(path: object) -> list[str]:
                metadata = os.fstat(path) if isinstance(path, int) else os.stat(path)  # type: ignore[arg-type]
                if (metadata.st_dev, metadata.st_ino) == runs_identity:
                    raise AssertionError(".harness/runs contents must not be listed")
                return real_listdir(path)  # type: ignore[arg-type]

            with mock.patch.object(migration.os, "listdir", side_effect=refuse_runs_listing):
                preview = migration.preview_migration(
                    root=root,
                    from_version="0.2",
                    backup_dir=backup,
                )
            self.assertEqual(
                {entry.path: entry for entry in preview.legacy_inventory}[".harness/runs"].lstat_type,
                "directory",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reporivet",
                    "migrate",
                    "--root",
                    str(root),
                    "--from",
                    "0.2",
                    "--preview",
                    "--backup-dir",
                    str(backup),
                ],
                cwd=REPOSITORY,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn(trap.name, result.stdout)
            self.assertNotIn(secret.name, result.stdout)
            self.assertNotIn("PRIVATE-RUN-CONTENT", result.stdout)
            payload = json.loads(result.stdout)
            runs_entry = self.inventory_by_path(payload)[".harness/runs"]
            self.assertEqual(runs_entry["lstat_type"], "directory")
            self.assertEqual(runs_entry["action"], "retain")
            self.assertEqual(runs_entry["current_sha256"], "")
            self.assertFalse(backup.exists())

    @unittest.skipIf(os.name == "nt", "POSIX mode evidence is required")
    def test_external_backup_manifest_records_exact_bytes_modes_and_excludes_runs_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root = base / "repository"
            backup = base / "visible-backup"
            root.mkdir()
            self.install_canonical_02(root)
            checked = root / "dev/check"
            checked.chmod(0o751)
            checked_before = checked.read_bytes()
            runs_secret = root / ".harness/runs/private-evidence.txt"
            runs_secret.write_bytes(b"retained evidence not copied\n")

            preview = migration.preview_migration(
                root=root,
                from_version="0.2",
                backup_dir=backup,
            )
            applied, payload = self.apply_cli(root, backup, preview.fingerprint)

            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertEqual(payload["status"], "applied")
            manifest_path = Path(str(payload["manifest"]))
            self.assertEqual(manifest_path, backup / "manifest.json")
            self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(manifest_path.stat().st_mode), 0o600)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema"], "reporivet.migration-backup/v1")
            self.assertEqual(manifest["status"], "successful")
            self.assertEqual(manifest["preview_fingerprint"], preview.fingerprint)
            entries = {entry["path"]: entry for entry in manifest["entries"]}
            check_entry = entries["dev/check"]
            self.assertEqual(check_entry["preimage"]["type"], "regular")
            self.assertTrue(check_entry["preimage"]["prior_existence"])
            self.assertEqual(check_entry["preimage"]["mode"], 0o751)
            self.assertEqual(
                check_entry["preimage"]["sha256"],
                hashlib.sha256(checked_before).hexdigest(),
            )
            backup_copy = backup / check_entry["preimage"]["backup_path"]
            self.assertEqual(backup_copy.read_bytes(), checked_before)
            self.assertEqual(stat.S_IMODE(backup_copy.stat().st_mode), 0o600)
            self.assertEqual(check_entry["postimage"]["type"], "missing")
            self.assertFalse(checked.exists())
            self.assertTrue(runs_secret.is_file())
            self.assertFalse(
                any(str(entry["path"]).startswith(".harness/runs/") for entry in manifest["entries"])
            )
            self.assertNotIn(runs_secret.name, manifest_path.read_text(encoding="utf-8"))
            self.assertNotIn("retained evidence not copied", manifest_path.read_text(encoding="utf-8"))

    def test_each_repository_mutation_phase_failure_automatically_restores_exact_tree(self) -> None:
        phases = (
            "_apply_setup_create",
            "_apply_setup_update",
            "_apply_remove_file",
            "_apply_remove_directory",
        )
        for phase in phases:
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as directory:
                base = Path(directory).resolve()
                root = base / "repository"
                backup = base / "backup"
                root.mkdir()
                self.install_canonical_02(root)
                if phase == "_apply_setup_update":
                    # The public migration preview intentionally excludes legacy
                    # marker cleanup.  Use the explicit guided setup preview for
                    # this subcase so the exact generated marker produces a real
                    # convert -> setup-update transaction operation.
                    draft = guided._initial_definition(root, None)
                    values = guided._bundle_values(root, draft)
                    legacy_agents = guided._legacy_marker_expected("AGENTS.md", values)
                    (root / "AGENTS.md").write_text(legacy_agents + "\n", encoding="utf-8")
                    raw_preview = guided._build_guided_setup_preview(
                        root=root,
                        with_claude_settings=False,
                        draft=draft,
                    )
                    preview = migration._bind_setup_preview(
                        raw_preview,
                        root=root,
                        backup_dir=backup,
                    )
                    agents_action = next(
                        action for action in preview.actions if action.path == "AGENTS.md"
                    )
                    self.assertEqual(agents_action.action, "convert")
                    update_specs = migration._setup_mutation_specs(root=root, preview=preview)
                    self.assertEqual(
                        next(spec.operation for spec in update_specs if spec.path == "AGENTS.md"),
                        "setup-update",
                    )
                    preview_factory = lambda: guided._build_guided_setup_preview(
                        root=root,
                        with_claude_settings=False,
                        draft=draft,
                    )
                else:
                    preview = migration.preview_migration(
                        root=root,
                        from_version="0.2",
                        backup_dir=backup,
                    )
                    preview_factory = None
                before = self.tree_snapshot(root)
                original = getattr(migration, phase)
                calls = 0

                def fail_after_mutation(*args: object, **kwargs: object) -> object:
                    nonlocal calls
                    result = original(*args, **kwargs)
                    calls += 1
                    if calls == 1:
                        raise OSError(f"injected {phase} failure")
                    return result

                with mock.patch.object(migration, phase, side_effect=fail_after_mutation):
                    with self.assertRaisesRegex(InitError, "automatically rolled back"):
                        if preview_factory is None:
                            migration.apply_migration(
                                root=root,
                                from_version="0.2",
                                approve_preview=preview.fingerprint,
                                backup_dir=backup,
                            )
                        else:
                            migration._apply_setup_transition(
                                root=root,
                                preview=preview,
                                backup_dir=backup,
                                preview_factory=preview_factory,
                            )

                self.assertEqual(calls, 1)
                self.assertEqual(before, self.tree_snapshot(root))
                self.assertTrue((backup / "manifest.json").is_file())
                manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["status"], "rolled-back-after-failure")
                self.assertEqual(manifest["unrecovered"], [])

    def test_successful_migration_then_manifest_rollback_restores_exact_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root = base / "repository"
            backup = base / "backup"
            root.mkdir()
            self.install_canonical_02(root)
            (root / "dev/check").chmod(0o751)
            before = self.tree_snapshot(root)
            preview = migration.preview_migration(
                root=root,
                from_version="0.2",
                backup_dir=backup,
            )
            applied = migration.apply_migration(
                root=root,
                from_version="0.2",
                approve_preview=preview.fingerprint,
                backup_dir=backup,
            )
            self.assertNotEqual(before, self.tree_snapshot(root))

            rollback = self.run_cli("migrate", "--rollback", str(applied.manifest))
            rolled_back = json.loads(rollback.stdout) if rollback.stdout else {}

            self.assertEqual(rollback.returncode, 0, rollback.stderr)
            self.assertEqual(rolled_back["status"], "rolled-back")
            self.assertEqual(before, self.tree_snapshot(root))
            manifest = json.loads(applied.manifest.read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "rolled-back")

    def test_post_migration_user_change_causes_safe_rollback_refusal_without_partial_restore(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root = base / "repository"
            backup = base / "backup"
            root.mkdir()
            self.install_canonical_02(root)
            preview = migration.preview_migration(
                root=root,
                from_version="0.2",
                backup_dir=backup,
            )
            applied = migration.apply_migration(
                root=root,
                from_version="0.2",
                approve_preview=preview.fingerprint,
                backup_dir=backup,
            )
            claude = root / "CLAUDE.md"
            claude.write_bytes(claude.read_bytes() + b"\n# user change after migration\n")
            after_user_change = self.tree_snapshot(root)

            with self.assertRaisesRegex(InitError, "post-migration user change"):
                migration.rollback_migration(manifest=applied.manifest)

            self.assertEqual(after_user_change, self.tree_snapshot(root))
            self.assertFalse((root / "dev/harness.py").exists())

    def test_ordinary_upgrade_refuses_legacy_02_without_deleting_or_replacing_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root = base / "repository"
            root.mkdir()
            self.install_canonical_02(root)
            before = self.tree_snapshot(root)

            for extra in ((), ("--dry-run",)):
                with self.subTest(extra=extra):
                    result = self.run_cli(
                        "upgrade",
                        "--root",
                        str(root),
                        *extra,
                    )
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("migrate", result.stderr)
                    self.assertIn("--preview", result.stderr)
                    self.assertEqual(before, self.tree_snapshot(root))


if __name__ == "__main__":
    unittest.main()
