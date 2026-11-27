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
sys.path.insert(0, str(REPOSITORY / "src"))

from reporivet import initializer
from reporivet.cli import main as cli_main


class AuditAdoptionTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str, str]:
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = cli_main(list(args))
        return code, output.getvalue(), error.getvalue()

    def test_audit_is_stable_read_only_and_never_executes_manifest_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "src").mkdir()
            (root / "src/main.py").write_text("not output\n")
            sentinel = root / "ran"
            (root / "package.json").write_text(json.dumps({"scripts": {"test": f"touch {sentinel}"}}))
            before = tuple(sorted(path.relative_to(root).as_posix() for path in root.rglob("*")))
            first = self.run_cli("audit", "--root", str(root))
            second = self.run_cli("audit", "--root", str(root))
            self.assertEqual(first[0], 0, first[2])
            self.assertEqual(first[1], second[1])
            self.assertEqual(before, tuple(sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))))
            self.assertFalse(sentinel.exists())
            self.assertNotIn("touch", first[1])
            report = json.loads(first[1])
            self.assertEqual(report["schema"], "reporivet.audit/v2")
            self.assertTrue(any(item["category"] == "source-root" for item in report["findings"]))

    def test_audit_marks_legacy_runtime_but_does_not_modify_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            runtime = root / "dev/harness.py"
            runtime.parent.mkdir()
            runtime.write_text("#!/usr/bin/env python3\n# reporivet:managed version=0.2.0\n")
            original = runtime.read_bytes()
            code, output, error = self.run_cli("audit", "--root", str(root))
            self.assertEqual(code, 0, error)
            self.assertIn("legacy", output)
            self.assertEqual(original, runtime.read_bytes())

    def test_init_and_upgrade_preserve_user_bytes_and_only_write_entrypoints(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "README.md").write_bytes(b"# Existing\r\nKeep exact.  \r\n")
            code, output, error = self.run_cli("init", "--root", str(root), "--name", "Fixture")
            self.assertEqual(code, 0, output + error)
            self.assertEqual((root / "README.md").read_bytes(), b"# Existing\r\nKeep exact.  \r\n")
            self.assertFalse((root / "dev").exists())
            self.assertFalse((root / "docs").exists())
            agents = (root / "AGENTS.md").read_bytes()
            code, output, error = self.run_cli("upgrade", "--root", str(root))
            self.assertEqual(code, 0, output + error)
            self.assertTrue((root / "AGENTS.md").read_bytes().startswith(agents[:agents.index(b"<!-- reporivet:entrypoints:start -->")]))

    def test_unreadable_utf8_agents_refuses_without_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            agents = root / "AGENTS.md"
            agents.write_bytes(b"\xff\xfe")
            before = agents.read_bytes()
            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 2)
            self.assertIn("UTF-8", error)
            self.assertEqual(before, agents.read_bytes())

    def test_malformed_managed_markers_refuse_without_partial_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            agents = root / "AGENTS.md"
            agents.write_text("prefix\n<!-- reporivet:entrypoints:start -->\nmissing end\n")
            before = agents.read_bytes()
            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 2)
            self.assertIn("malformed managed markers", error)
            self.assertEqual(before, agents.read_bytes())
            self.assertFalse((root / "CLAUDE.md").exists())

    def test_atomic_transaction_rolls_back_prior_write_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            agents = root / "AGENTS.md"
            claude = root / "CLAUDE.md"
            agents.write_text("user\n")
            before = agents.read_bytes()
            original = initializer._atomic_write
            calls = 0

            def fail_second(operation: object, **kwargs: object) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected write failure")
                original(operation, **kwargs)

            with mock.patch.object(initializer, "_atomic_write", side_effect=fail_second):
                code, output, error = self.run_cli("init", "--root", str(root), "--claude")
            self.assertEqual(code, 2)
            self.assertIn("rolled back", error)
            self.assertEqual(before, agents.read_bytes())
            self.assertFalse(claude.exists())

    def test_new_file_postimages_are_rolled_back_or_preserved_after_divergence(self) -> None:
        for divergence in (False, True):
            with self.subTest(divergence=divergence), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                agents, claude = root / "AGENTS.md", root / "CLAUDE.md"
                real_rmdir = os.rmdir
                calls = 0

                def cleanup_then_fail(path: object, *args: object, **kwargs: object) -> None:
                    nonlocal calls
                    real_rmdir(path, *args, **kwargs)
                    if not Path(path).name.startswith(".reporivet-write-"):
                        return
                    calls += 1
                    if calls == 2:
                        if divergence:
                            agents.chmod(stat.S_IMODE(agents.stat().st_mode) ^ stat.S_IXUSR)
                        raise OSError("failure after publishing and cleanup")

                with mock.patch.object(initializer.os, "rmdir", side_effect=cleanup_then_fail):
                    code, output, error = self.run_cli("init", "--root", str(root), "--claude")
                self.assertEqual(code, 2, output + error)
                self.assertFalse(claude.exists())
                self.assertEqual(agents.exists(), divergence)
                self.assertIn("rollback incomplete" if divergence else "rolled back", error)
                self.assertFalse(any(p.name.startswith(".reporivet-write-") for p in root.iterdir()))

    def test_concurrent_identical_creation_is_not_rolled_back(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            agents = root / "AGENTS.md"

            def competing_creation(src: object, dst: object, *, src_dir_fd: int, follow_symlinks: bool) -> None:
                descriptor = os.open(src, os.O_RDONLY, dir_fd=src_dir_fd)
                try:
                    mode = stat.S_IMODE(os.fstat(descriptor).st_mode)
                    content = os.read(descriptor, 65536)
                finally:
                    os.close(descriptor)
                target = Path(dst)
                target.write_bytes(content)
                target.chmod(mode)
                raise FileExistsError("concurrent creation")

            with mock.patch.object(initializer.os, "link", side_effect=competing_creation):
                code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 2, output + error)
            self.assertTrue(agents.exists())
            self.assertIn("rollback incomplete", error)
            self.assertFalse(any(p.name.startswith(".reporivet-write-") for p in root.iterdir()))

    def test_replaced_staging_directory_cannot_change_symlink_target_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            root, victim = parent / "project", parent / "victim"
            root.mkdir()
            victim.mkdir(mode=0o755)
            victim.chmod(0o755)
            real_open = os.open
            replacement = None

            def replace_before_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
                nonlocal replacement
                if isinstance(path, (str, Path)) and Path(path).name.startswith(".reporivet-write-"):
                    replacement = Path(path)
                    replacement.rmdir()
                    replacement.symlink_to(victim, target_is_directory=True)
                return real_open(path, flags, *args, **kwargs)

            with mock.patch.object(initializer.os, "open", side_effect=replace_before_open):
                code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 2, output + error)
            self.assertEqual(stat.S_IMODE(victim.stat().st_mode), 0o755)
            self.assertFalse((root / "AGENTS.md").exists())
            if replacement is not None and replacement.is_symlink():
                replacement.unlink()

    def test_replaced_staging_directory_is_never_recursively_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            root, victim = parent / "project", parent / "victim"
            root.mkdir()
            victim.mkdir()
            (victim / "valuable.txt").write_text("keep")
            real_open = os.open
            replacement = None

            def replace_before_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
                nonlocal replacement
                if isinstance(path, (str, Path)) and Path(path).name.startswith(".reporivet-write-"):
                    replacement = Path(path)
                    replacement.rmdir()
                    victim.rename(replacement)
                return real_open(path, flags, *args, **kwargs)

            with mock.patch.object(initializer.os, "open", side_effect=replace_before_open):
                code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 2, output + error)
            self.assertIsNotNone(replacement)
            self.assertEqual((replacement / "valuable.txt").read_text(), "keep")
            self.assertFalse((root / "AGENTS.md").exists())
            replacement.rename(victim)

    def test_fenced_and_inline_markers_are_not_managed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            agents = root / "AGENTS.md"
            original = "```markdown\n<!-- reporivet:entrypoints:start -->\nexample\n<!-- reporivet:entrypoints:end -->\n```\ninline <!-- reporivet:entrypoints:start -->\n"
            agents.write_text(original)
            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 0, output + error)
            result = agents.read_text()
            self.assertIn(original, result)
            self.assertEqual(result.count("<!-- reporivet:entrypoints:start -->"), 3)

    def test_non_markdown_separators_cannot_create_marker_ownership(self) -> None:
        separators = "\v\f\x1c\x1d\x1e\x85\N{LINE SEPARATOR}\N{PARAGRAPH SEPARATOR}"
        for separator in separators:
            for name, start, end in (
                ("AGENTS.md", initializer.AGENTS_START, initializer.AGENTS_END),
                ("CLAUDE.md", initializer.CLAUDE_START, initializer.CLAUDE_END),
            ):
                for inline_marker in ("start", "end"):
                    for command in ("init", "upgrade"):
                        with self.subTest(separator=repr(separator), name=name, inline=inline_marker, command=command), tempfile.TemporaryDirectory() as directory:
                            root = Path(directory).resolve()
                            self.assertEqual(self.run_cli("init", "--root", str(root), "--claude")[0], 0)
                            opening = "User-owned inline example" + separator + start if inline_marker == "start" else start
                            closing = "User-owned inline example" + separator + end if inline_marker == "end" else end
                            (root / name).write_bytes(f"{opening}\nMUST_KEEP_USER_BODY\n{closing}\n".encode())
                            before = {p: (p.read_bytes(), p.stat().st_mode) for p in (root / "AGENTS.md", root / "CLAUDE.md")}
                            code, output, error = self.run_cli(command, "--root", str(root), "--claude")
                            self.assertEqual(code, 2, output + error)
                            self.assertIn("malformed managed markers", error)
                            for path, image in before.items():
                                self.assertEqual((path.read_bytes(), path.stat().st_mode), image)

    def test_non_markdown_separators_cannot_close_example_fences(self) -> None:
        for separator in "\v\f\x1c\x1d\x1e\x85\N{LINE SEPARATOR}\N{PARAGRAPH SEPARATOR}":
            for fence in ("```", "~~~"):
                for spoof in ("example" + separator + fence, fence + separator):
                    for name, start, end in (
                        ("AGENTS.md", initializer.AGENTS_START, initializer.AGENTS_END),
                        ("CLAUDE.md", initializer.CLAUDE_START, initializer.CLAUDE_END),
                    ):
                        with self.subTest(separator=repr(separator), spoof=repr(spoof), name=name), tempfile.TemporaryDirectory() as directory:
                            root = Path(directory).resolve()
                            original = f"{fence}\n{spoof}\n{start}\nMUST_KEEP_USER_BODY\n{end}\n{fence}\n".encode()
                            (root / name).write_bytes(original)
                            code, output, error = self.run_cli("init", "--root", str(root), "--claude")
                            self.assertEqual(code, 0, output + error)
                            self.assertTrue((root / name).read_bytes().startswith(original))
                            before = {p: p.read_bytes() for p in (root / "AGENTS.md", root / "CLAUDE.md")}
                            code, output, error = self.run_cli("upgrade", "--root", str(root), "--claude")
                            self.assertEqual(code, 0, output + error)
                            for path, content in before.items():
                                self.assertEqual(path.read_bytes(), content)

    def test_inline_fence_openers_do_not_hide_root_markers(self) -> None:
        for separator in "\v\f\x1c\x1d\x1e\x85\N{LINE SEPARATOR}\N{PARAGRAPH SEPARATOR}":
            for fence in ("```", "~~~"):
                with self.subTest(separator=repr(separator), fence=fence):
                    prefix = "User example" + separator + fence + "\n"
                    block = initializer.AGENTS_START + "\nold\n" + initializer.AGENTS_END
                    self.assertEqual(
                        initializer._managed_span(prefix + block, initializer.AGENTS_START, initializer.AGENTS_END),
                        (len(prefix), len(prefix + block)),
                    )

    def test_markdown_line_endings_preserve_exact_managed_span_and_suffix(self) -> None:
        for newline in ("\n", "\r", "\r\n"):
            for start, end in ((initializer.AGENTS_START, initializer.AGENTS_END), (initializer.CLAUDE_START, initializer.CLAUDE_END)):
                for suffix in ("", newline + "user suffix  " + newline):
                    with self.subTest(newline=repr(newline), start=start, suffix=repr(suffix)):
                        prefix = newline.join(("user prefix", "```", start, "example", end, "``` \t", ""))
                        block = newline.join((start, "old", end))
                        original = prefix + block + suffix
                        self.assertEqual(initializer._managed_span(original, start, end), (len(prefix), len(prefix + block)))
                        replacement = start + "\nnew\n" + end
                        self.assertEqual(initializer._upsert(original.encode(), replacement, start, end), (prefix + replacement + suffix).encode())

    def test_fence_info_may_contain_the_other_fence_character(self) -> None:
        for fence, info in (("~~~", "info`x`"), ("```", "info~x~")):
            with self.subTest(fence=fence), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                agents = root / "AGENTS.md"
                original = (f"{fence} {info}\n{initializer.AGENTS_START}\nexample\n{initializer.AGENTS_END}\n{fence}\n").encode()
                agents.write_bytes(original)
                code, output, error = self.run_cli("init", "--root", str(root))
                self.assertEqual(code, 0, output + error)
                before = agents.read_bytes()
                self.assertTrue(before.startswith(original))
                self.assertEqual(self.run_cli("doctor", "--root", str(root))[0], 0)
                self.assertEqual(self.run_cli("upgrade", "--root", str(root))[0], 0)
                self.assertEqual(before, agents.read_bytes())

    def test_reinit_and_upgrade_are_noop_for_same_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            code, output, error = self.run_cli("init", "--root", str(root), "--name", "Stable")
            self.assertEqual(code, 0, output + error)
            before_agents = (root / "AGENTS.md").stat().st_mtime_ns
            before = (root / "AGENTS.md").read_bytes()
            code, output, error = self.run_cli("init", "--root", str(root), "--name", "Stable")
            self.assertEqual(code, 0, output + error)
            self.assertEqual(before, (root / "AGENTS.md").read_bytes())
            self.assertEqual(before_agents, (root / "AGENTS.md").stat().st_mtime_ns)
            code, output, error = self.run_cli("upgrade", "--root", str(root))
            self.assertEqual(code, 0, output + error)
            self.assertEqual(before, (root / "AGENTS.md").read_bytes())
            self.assertEqual(before_agents, (root / "AGENTS.md").stat().st_mtime_ns)

    def test_dry_run_and_preview_do_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            code, output, error = self.run_cli("init", "--root", str(root), "--dry-run")
            self.assertEqual(code, 0, output + error)
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertIn("Mutation plan fingerprint:", output)

    def test_missing_root_preview_matches_apply(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "new"
            args = ("init", "--root", str(root), "--name", "Fixture", "--claude")
            code, preview, error = self.run_cli(*args, "--dry-run")
            self.assertEqual(code, 0, error)
            self.assertFalse(root.exists())
            self.assertNotIn("directory unreadable", preview)
            code, applied, error = self.run_cli(*args)
            self.assertEqual(code, 0, error)
            fingerprint = lambda output: next(line for line in output.splitlines() if line.startswith("Mutation plan fingerprint:"))
            self.assertEqual(fingerprint(preview), fingerprint(applied))
            for filename in ("AGENTS.md", "CLAUDE.md"):
                expected = "\n".join("+" + line for line in (root / filename).read_text(encoding="utf-8").splitlines())
                self.assertIn(expected, preview)

    def test_missing_root_preview_refuses_if_root_appears(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "new"
            original = initializer._prepare

            def appear(*args: object, **kwargs: object) -> object:
                result = original(*args, **kwargs)
                root.mkdir()
                (root / "user.txt").write_text("preserve")
                return result

            with mock.patch.object(initializer, "_prepare", side_effect=appear):
                code, output, error = self.run_cli("init", "--root", str(root), "--dry-run")
            self.assertEqual(code, 2, output + error)
            self.assertIn("appeared during preview", error)
            self.assertEqual((root / "user.txt").read_text(), "preserve")
            self.assertFalse((root / "AGENTS.md").exists())

    @unittest.skipUnless(os.name == "posix", "POSIX umask semantics")
    def test_failed_init_removes_new_mode_zero_root(self) -> None:
        script = (
            "import os, sys; os.umask(0o777); "
            "sys.path.insert(0, sys.argv[1]); "
            "from reporivet.cli import main; sys.exit(main(sys.argv[2:]))"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "new"
            result = subprocess.run([sys.executable, "-c", script, str(REPOSITORY / "src"), "init", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertFalse(root.exists())

    def test_failed_init_preserves_new_root_if_user_populates_or_replaces_it(self) -> None:
        for scenario in ("populated", "replaced"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve() / "new"
                def fail(*args: object, **kwargs: object) -> None:
                    if scenario == "replaced":
                        root.rename(root.with_name("original"))
                        root.mkdir()
                    else:
                        (root / "user.txt").write_text("preserve")
                    raise initializer.InitError("injected failure")
                with mock.patch.object(initializer, "_prepare", side_effect=fail):
                    code, output, error = self.run_cli("init", "--root", str(root))
                self.assertEqual(code, 2, output + error)
                self.assertTrue(root.is_dir())
                if scenario == "populated":
                    self.assertEqual((root / "user.txt").read_text(), "preserve")

    def test_root_creation_permission_error_is_reported_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "new"
            with mock.patch.object(Path, "mkdir", side_effect=PermissionError("permission denied")):
                code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 2, output + error)
            self.assertIn("cannot create project root", error)
            self.assertIn("permission denied", error)
            self.assertNotIn("Traceback", output + error)
            self.assertFalse(root.exists())

    @unittest.skipUnless(os.name == "posix", "POSIX permissions")
    def test_unwritable_parent_reports_root_creation_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve() / "locked"
            parent.mkdir()
            parent.chmod(0o555)
            try:
                root = parent / "new"
                env = dict(os.environ, PYTHONPATH=str(REPOSITORY / "src"), PYTHONDONTWRITEBYTECODE="1")
                result = subprocess.run([sys.executable, "-B", "-m", "reporivet", "init", "--root", str(root)], env=env, capture_output=True, text=True)
                if result.returncode == 0:
                    self.skipTest("process can write to a mode-0555 directory")
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("cannot create project root", result.stderr)
                self.assertNotIn("Traceback", result.stdout + result.stderr)
                self.assertFalse(root.exists())
            finally:
                parent.chmod(0o755)

    @unittest.skipUnless(os.name == "posix", "requires POSIX raw-byte filenames")
    def test_non_utf8_names_are_safely_omitted_from_audit_and_preview(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            raw_path = os.fsencode(root) + b"/invalid-\xff.txt"
            try:
                fd = os.open(raw_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except (OSError, UnicodeError) as exc:
                self.skipTest(f"filesystem does not support non-UTF-8 names: {exc}")
            with os.fdopen(fd, "wb") as file:
                file.write(b"private file content")
            (root / "README.md").write_text("valid content")
            env = dict(os.environ, PYTHONPATH=str(REPOSITORY / "src"), PYTHONIOENCODING="utf-8:strict", PYTHONDONTWRITEBYTECODE="1")
            for command in (("audit",), ("init", "--dry-run")):
                result = subprocess.run([sys.executable, "-B", "-m", "reporivet", *command, "--root", str(root)], env=env, capture_output=True)
                stdout = result.stdout.decode("utf-8", "strict")
                stderr = result.stderr.decode("utf-8", "strict")
                self.assertEqual(result.returncode, 0, stdout + stderr)
                self.assertIn("non-UTF-8 path omitted", stdout)
                self.assertNotIn("invalid-", stdout + stderr)
                self.assertNotIn("private file content", stdout + stderr)
                self.assertFalse((root / "AGENTS.md").exists())
            with open(raw_path, "rb") as file:
                self.assertEqual(file.read(), b"private file content")

    def test_surrogate_entry_is_omitted_before_path_access(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            entry = mock.Mock()
            entry.name = "private-\udcff.txt"
            scan = mock.MagicMock()
            scan.__enter__.return_value = iter([entry])
            with mock.patch.object(initializer.os, "scandir", return_value=scan):
                paths, exclusions = initializer._observed_paths(root)
            self.assertEqual(paths, [])
            self.assertEqual(exclusions, [". (non-UTF-8 path omitted)"])
            entry.is_symlink.assert_not_called()

    @unittest.skipUnless(os.name == "posix", "POSIX surrogate-escaped command arguments")
    def test_non_utf8_root_path_is_refused_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = str(Path(directory).resolve() / "private-\udcff")
            env = dict(os.environ, PYTHONPATH=str(REPOSITORY / "src"), PYTHONIOENCODING="utf-8:strict", PYTHONDONTWRITEBYTECODE="1")
            for command in (("audit",), ("init", "--dry-run"), ("init",)):
                result = subprocess.run([sys.executable, "-B", "-m", "reporivet", *command, "--root", root], env=env, capture_output=True)
                stdout = result.stdout.decode("utf-8", "strict")
                stderr = result.stderr.decode("utf-8", "strict")
                self.assertEqual(result.returncode, 2, stdout + stderr)
                self.assertIn("project root path is not valid UTF-8", stderr)
                self.assertNotIn("private-", stdout + stderr)
                self.assertNotIn("Traceback", stdout + stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_audit_stops_at_entry_budget_and_reports_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for index in range(600):
                (root / f"entry-{index:04d}.txt").write_text("x\n")
            report = initializer.audit_project(root=root).as_dict()
            observed = [item for item in report["findings"] if item["status"] == "confirmed" and item["category"] == "observed-path"]
            exclusions = [item for item in report["findings"] if item["category"] == "exclusion"]
            self.assertLessEqual(len(observed), initializer.MAX_OBSERVED_PATHS)
            self.assertTrue(any("work/exclusion budget reached" in item["detail"] for item in exclusions))
            self.assertLessEqual(len(exclusions), initializer.MAX_EXCLUSIONS + 1)

    def test_document_paths_are_not_crowded_out_by_ordinary_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            docs = root / "docs"
            docs.mkdir()
            (docs / "README.md").write_text("private document contents\n")
            for index in range(90):
                (root / f"item-{index:03d}.txt").write_text("ordinary content\n")

            before = tuple(sorted(path.relative_to(root).as_posix() for path in root.rglob("*")))
            code, output, error = self.run_cli("audit", "--root", str(root))
            self.assertEqual(code, 0, error)
            self.assertEqual(before, tuple(sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))))
            self.assertNotIn("private document contents", output)
            findings = json.loads(output)["findings"]
            self.assertTrue(any(item["path"] == "docs/README.md" and item["category"] == "document" and item["status"] == "confirmed" for item in findings))
            self.assertTrue(any("file observation limit reached" in item["detail"] for item in findings))

            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 0, output + error)
            agents = (root / "AGENTS.md").read_text()
            self.assertIn("[docs/README.md](./docs/README.md) (observed path; not authority)", agents)
            self.assertNotIn("private document contents", agents)
            observed, exclusions = initializer._observed_paths(root, include_instructions=False)
            self.assertEqual(len(observed), initializer.MAX_OBSERVED_PATHS)
            self.assertTrue(any(path.startswith("item-") for path in observed))
            self.assertTrue(any("file observation limit reached" in item for item in exclusions))

    def test_observation_balances_and_reallocates_category_quotas(self) -> None:
        for document_count, other_count in ((60, 90), (3, 90), (90, 3)):
            with self.subTest(documents=document_count, others=other_count), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                docs = root / "docs"
                docs.mkdir()
                for index in range(document_count):
                    (docs / f"doc-{index:03d}.rst").touch()
                for index in range(other_count):
                    (root / f"item-{index:03d}.txt").touch()
                observed, exclusions = initializer._observed_paths(root)
                self.assertEqual(len(observed), min(initializer.MAX_OBSERVED_PATHS, document_count + other_count))
                docs_seen = sum(path.startswith("docs/") for path in observed)
                expected_documents = min(document_count, max(initializer.MAX_OBSERVED_PATHS // 2, initializer.MAX_OBSERVED_PATHS - other_count))
                self.assertEqual(docs_seen, expected_documents)
                self.assertTrue(all((root / path).is_file() for path in observed))
                self.assertTrue(any("file observation limit reached" in item for item in exclusions))
                self.assertEqual((observed, exclusions), initializer._observed_paths(root))

    def test_document_heuristic_includes_non_docs_directory_formats(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "handbook").mkdir()
            expected = ("README", "guide.rst", "handbook/start.mdx", "handbook/README.txt")
            for relative in expected:
                (root / relative).touch()
            for index in range(90):
                (root / f"item-{index:03d}.txt").touch()
            observed, _ = initializer._observed_paths(root)
            self.assertTrue(set(expected).issubset(observed))

    def test_partial_markers_and_unclosed_fences_fail_without_writes(self) -> None:
        start, end = initializer.AGENTS_START, initializer.AGENTS_END
        samples = (
            start + " trailing\nold\n" + end + " trailing\n",
            start[:-4] + "\nold\n" + end[:-4] + "\n",
            "   " + start + "\nold\n   " + end + "\n",
            "```markdown\nunfinished example\n",
        )
        for text in samples:
            with self.subTest(text=text), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                agents = root / "AGENTS.md"
                agents.write_bytes(text.encode())
                code, output, error = self.run_cli("init", "--root", str(root), "--claude")
                self.assertEqual(code, 2, output + error)
                self.assertEqual(agents.read_bytes(), text.encode())
                self.assertFalse((root / "CLAUDE.md").exists())
                self.assertNotIn("Applied", output)

    def test_post_replace_cleanup_failure_restores_current_and_prior_operations(self) -> None:
        for divergence in (False, True):
            with self.subTest(divergence=divergence), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                agents, claude = root / "AGENTS.md", root / "CLAUDE.md"
                agents.write_bytes(b"agent user\r\n")
                claude.write_bytes(b"provider user\r\n")
                agents.chmod(0o640)
                claude.chmod(0o600)
                before = {p: (p.read_bytes(), p.stat().st_mode) for p in (agents, claude)}
                real_unlink = Path.unlink
                cleanups = 0

                def cleanup(path: Path, *args: object, **kwargs: object) -> None:
                    nonlocal cleanups
                    real_unlink(path, *args, **kwargs)
                    if path.name.startswith(".reporivet-write-"):
                        cleanups += 1
                        if cleanups == 2:
                            if divergence:
                                claude.write_bytes(b"concurrent user edit\n")
                            raise OSError("post-replacement cleanup failure")

                with mock.patch.object(Path, "unlink", cleanup):
                    code, output, error = self.run_cli("init", "--root", str(root), "--claude")
                self.assertEqual(code, 2)
                self.assertNotIn("Applied", output)
                self.assertEqual((agents.read_bytes(), agents.stat().st_mode), before[agents])
                if divergence:
                    self.assertEqual(claude.read_bytes(), b"concurrent user edit\n")
                    self.assertIn("rollback incomplete", error)
                    self.assertIn("CLAUDE.md", error)
                else:
                    self.assertEqual((claude.read_bytes(), claude.stat().st_mode), before[claude])
                    self.assertIn("rolled back", error)

    def test_rendering_cannot_adopt_a_later_user_preimage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            agents = root / "AGENTS.md"
            agents.write_bytes(b"original user\n")
            real_asset = initializer.read_asset

            def concurrent_render(*args: object, **kwargs: object) -> str:
                result = real_asset(*args, **kwargs)
                agents.write_bytes(b"concurrent user\n")
                return result

            with mock.patch.object(initializer, "read_asset", side_effect=concurrent_render):
                code, output, error = self.run_cli("init", "--root", str(root), "--claude")
            self.assertEqual(code, 2)
            self.assertIn("preimage changed", error)
            self.assertEqual(agents.read_bytes(), b"concurrent user\n")
            self.assertFalse((root / "CLAUDE.md").exists())

    def test_observation_budget_limits_actual_directory_iteration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for index in range(initializer.MAX_VISITED_ENTRIES + 30):
                (root / f"item-{index}").touch()
            real_scandir = os.scandir
            visited = 0

            @contextlib.contextmanager
            def counted(path: Path):
                nonlocal visited
                with real_scandir(path) as scan:
                    def entries():
                        nonlocal visited
                        for entry in scan:
                            visited += 1
                            yield entry
                    yield entries()

            with mock.patch.object(initializer.os, "scandir", counted):
                initializer.audit_project(root=root)
            self.assertLessEqual(visited, initializer.MAX_VISITED_ENTRIES)

    def test_generated_names_remain_inert_and_stable(self) -> None:
        for name in ("{{OBSERVED_PATH_ROWS}}", "[name](https://example.invalid)", "한글 & <name>"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                (root / "README.md").write_text("existing\n")
                code, output, error = self.run_cli("init", "--root", str(root), "--name", name)
                self.assertEqual(code, 0, output + error)
                before = (root / "AGENTS.md").read_bytes()
                self.assertEqual(self.run_cli("doctor", "--root", str(root))[0], 0)
                self.assertEqual(self.run_cli("upgrade", "--root", str(root))[0], 0)
                self.assertEqual(before, (root / "AGENTS.md").read_bytes())

    def test_unusual_root_name_does_not_inject_managed_markers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / ("name\n" + initializer.AGENTS_END)
            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 0, output + error)
            self.assertEqual(self.run_cli("doctor", "--root", str(root))[0], 0)
            before = (root / "AGENTS.md").read_bytes()
            self.assertEqual(self.run_cli("upgrade", "--root", str(root))[0], 0)
            self.assertEqual(before, (root / "AGENTS.md").read_bytes())

    def test_generated_unicode_labels_remain_readable_and_doctor_checks_them(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            filename = "한 글 [x]!<tag>\\\\`"
            (root / filename).write_text("ok\n")
            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 0, output + error)
            generated = (root / "AGENTS.md").read_text()
            self.assertIn("한 글", generated)
            self.assertIn("%ED%95%9C%20%EA%B8%80", generated)
            self.assertNotIn("[x]", generated)
            (root / filename).unlink()
            code, output, error = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(code, 2)
            self.assertIn("target is missing", error)

    def test_malformed_link_is_a_diagnostic_error_not_a_traceback(self) -> None:
        for link in ("http://[bad", "./bad%00name"):
            with self.subTest(link=link), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                (root / "AGENTS.md").write_text(initializer.AGENTS_START + "\n[bad](" + link + ")\n" + initializer.AGENTS_END)
                code, output, error = self.run_cli("doctor", "--root", str(root))
                self.assertEqual(code, 2, output + error)
                self.assertIn("ERROR", error)


if __name__ == "__main__":
    unittest.main()
