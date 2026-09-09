from __future__ import annotations

import contextlib
import io
import json
import os
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

            def fail_second(operation: object) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected write failure")
                original(operation)

            with mock.patch.object(initializer, "_atomic_write", side_effect=fail_second):
                code, output, error = self.run_cli("init", "--root", str(root), "--claude")
            self.assertEqual(code, 2)
            self.assertIn("rolled back", error)
            self.assertEqual(before, agents.read_bytes())
            self.assertFalse(claude.exists())

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
