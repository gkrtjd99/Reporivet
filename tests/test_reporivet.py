from __future__ import annotations

import contextlib
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from reporivet import __version__
from reporivet.cli import main as cli_main


class ReporivetTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli_main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_version_and_runtime_free_init(self) -> None:
        self.assertEqual(__version__, "0.3.0.dev1")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            code, output, error = self.run_cli("init", "--root", str(root), "--name", "Fixture")
            self.assertEqual(code, 0, output + error)
            self.assertTrue((root / "AGENTS.md").is_file())
            self.assertFalse((root / "dev").exists())
            self.assertFalse((root / ".reporivet-version").exists())
            generated = (root / "AGENTS.md").read_text()
            self.assertNotIn("fixed document schema", generated)
            self.assertIn("## 수명 주기 안내", generated)
            self.assertIn("reporivet upgrade --root .", generated)
            self.assertIn("필요하면 `--claude`", generated)
            self.assertIn("package가 없어도", generated)
            self.assertIn("자동 권한", generated)

    def test_claude_is_bounded_optional_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "CLAUDE.md").write_bytes(b"# User instructions\r\n\r\nKeep exact.  \r\n")
            original = (root / "CLAUDE.md").read_bytes()
            code, output, error = self.run_cli("init", "--root", str(root), "--claude")
            self.assertEqual(code, 0, output + error)
            self.assertTrue((root / "CLAUDE.md").read_bytes().startswith(original))
            self.assertIn("AGENTS.md", (root / "CLAUDE.md").read_text())
            self.assertFalse((root / "CLAUDE.md").is_symlink())

    def test_existing_user_agents_bytes_are_preserved_outside_managed_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            original = b"# User rules\r\n\r\nKeep exact trailing bytes.  \r\n"
            (root / "AGENTS.md").write_bytes(original)
            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 0, output + error)
            self.assertTrue((root / "AGENTS.md").read_bytes().startswith(original))
            second = (root / "AGENTS.md").read_bytes()
            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 0, output + error)
            self.assertEqual(second, (root / "AGENTS.md").read_bytes())

    def test_dry_run_has_no_side_effect_and_stable_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "new"
            first = self.run_cli("init", "--root", str(root), "--dry-run")
            second = self.run_cli("init", "--root", str(root), "--dry-run")
            self.assertEqual(first[0], 0, first[2])
            self.assertEqual(second[0], 0, second[2])
            self.assertFalse(root.exists())
            def fp(value: str) -> str:
                return next(line.rsplit(" ", 1)[-1] for line in value.splitlines() if line.startswith("Mutation plan fingerprint:"))
            self.assertEqual(fp(first[1]), fp(second[1]))

    def test_dry_run_prints_real_diff_and_explicit_noop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            code, output, error = self.run_cli("init", "--root", str(root), "--dry-run")
            self.assertEqual(code, 0, output + error)
            self.assertIn("Unified diff:", output)
            self.assertIn("사람이 검토하는 이스케이프된 미리보기", output)
            self.assertIn("적용 가능한 patch가 아닙니다", output)
            self.assertIn("fingerprint는 승인·잠금·다음 실행 결과를 보장하지 않습니다", output)
            self.assertIn("--- AGENTS.md", output)
            self.assertIn("+++ AGENTS.md", output)
            self.assertIn("+<!-- reporivet:entrypoints:start -->", output)
            self.assertFalse((root / "AGENTS.md").exists())
            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 0, output + error)
            code, output, error = self.run_cli("init", "--root", str(root), "--dry-run")
            self.assertEqual(code, 0, output + error)
            self.assertIn("No changes (no-op).", output)
            self.assertIn("(no changes)", output)
            self.assertIn("사람이 검토하는 이스케이프된 미리보기", output)
            self.assertIn("적용 가능한 patch가 아닙니다", output)

    def test_dry_run_preserves_newline_facts_and_escapes_terminal_controls(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "AGENTS.md").write_bytes(b"# User\r\n\x1b[31munsafe\x1b[0m")
            code, output, error = self.run_cli("init", "--root", str(root), "--name", "Changed", "--dry-run")
            self.assertEqual(code, 0, output + error)
            self.assertIn("\\ No newline at end of file", output)
            self.assertNotIn("\x1b", output)
            self.assertIn("\\x1b", output)
            self.assertIn("\\r", output)

    def test_upgrade_preview_shows_replaced_content_and_preserves_both_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.assertEqual(self.run_cli("init", "--root", str(root), "--claude")[0], 0)
            agents, claude = root / "AGENTS.md", root / "CLAUDE.md"
            agents.write_bytes(b"user prefix\r\n" + agents.read_bytes().replace(
                b"## Observed entry paths", b"USER-EDITED\n## Observed entry paths"
            ) + b"user suffix\r\n")
            agents.chmod(0o640)
            claude.chmod(0o600)
            before = {p: (p.read_bytes(), p.stat().st_mode, p.stat().st_mtime_ns) for p in (agents, claude)}
            code, output, error = self.run_cli("upgrade", "--root", str(root), "--claude", "--dry-run")
            self.assertEqual(code, 0, output + error)
            self.assertIn("-USER-EDITED", output)
            self.assertIn("사람이 검토하는 이스케이프된 미리보기", output)
            self.assertIn("적용 가능한 patch가 아닙니다", output)
            self.assertIn("fingerprint는 승인·잠금·다음 실행 결과를 보장하지 않습니다", output)
            self.assertNotIn("--- CLAUDE.md", output)
            for path, image in before.items():
                self.assertEqual((path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns), image)
            self.assertEqual(self.run_cli("upgrade", "--root", str(root), "--claude")[0], 0)
            self.assertNotIn(b"USER-EDITED", agents.read_bytes())
            self.assertTrue(agents.read_bytes().startswith(b"user prefix\r\n"))
            self.assertTrue(agents.read_bytes().endswith(b"user suffix\r\n"))
            self.assertEqual(stat.S_IMODE(agents.stat().st_mode), 0o640)

    def test_both_managed_blocks_preserve_suffixes_and_markers_at_eof(self) -> None:
        from reporivet import initializer

        for suffix in (b"\r\n\r\nuser suffix\r\n", b""):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                prefix = b"user prefix\r\n\r\n"
                bodies = {
                    "AGENTS.md": initializer._agent_block(root, "Fixture", ""),
                    "CLAUDE.md": initializer._claude_block(),
                }
                for name, body in bodies.items():
                    (root / name).write_bytes(prefix + body.encode() + suffix)
                before = {name: (root / name).read_bytes() for name in bodies}
                for command in ("init", "upgrade"):
                    code, output, error = self.run_cli(command, "--root", str(root), "--claude")
                    self.assertEqual(code, 0, output + error)
                    for name, content in before.items():
                        self.assertEqual((root / name).read_bytes(), content)

    def test_preview_keeps_content_prefixes_and_control_characters_on_their_lines(self) -> None:
        from reporivet import initializer

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            before = b"--old\nleft\vright\n"
            after = b"++new\nleft\tright\n"
            (root / "AGENTS.md").write_bytes(before)
            operation = initializer._operation(root, "AGENTS.md", after)
            preview = initializer._operations_diff((operation,))
            self.assertIn("---old\n", preview)
            self.assertIn("+++new\n", preview)
            self.assertIn("-left\\vright\n", preview)
            self.assertIn("+left\\tright\n", preview)
            self.assertNotIn("No newline at end of file", preview)
            self.assertNotIn("\n\n", preview)

    def test_audit_is_read_only_bounded_and_hides_contents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "src").mkdir()
            (root / "src/main.py").write_text("SECRET_CONTENT_SENTINEL\n")
            (root / "package.json").write_text('{"scripts":{"test":"rm -f SHOULD_NOT_RUN"}}\n')
            before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))
            first = self.run_cli("audit", "--root", str(root))
            second = self.run_cli("audit", "--root", str(root))
            self.assertEqual(first[0], 0, first[2])
            self.assertEqual(first[1], second[1])
            self.assertEqual(before, sorted(p.relative_to(root).as_posix() for p in root.rglob("*")))
            self.assertNotIn("SECRET_CONTENT_SENTINEL", first[1])
            self.assertNotIn("rm -f", first[1])
            report = json.loads(first[1])
            self.assertEqual(report["schema"], "reporivet.audit/v2")
            self.assertTrue(any(item["category"] == "source-root" for item in report["findings"]))

    def test_legacy_v02_is_rejected_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / ".reporivet-version").write_text("0.2.0\n")
            before = (root / ".reporivet-version").read_bytes()
            for command in ("init", "upgrade"):
                code, output, error = self.run_cli(command, "--root", str(root))
                self.assertEqual(code, 2)
                self.assertIn("0.2", error)
                self.assertIn("https://github.com/gkrtjd99/Reporivet", error)
                self.assertIn("docs/references/entrypoint-migration.md", error)
                self.assertNotIn("/blob/main/docs/", error)
                self.assertIn("old Reporivet-owned markers, runtime, and CI dependencies", error)
                self.assertEqual(before, (root / ".reporivet-version").read_bytes())
            code, output, error = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(code, 2)
            self.assertIn("entrypoint-migration.md", error)
            self.assertIn("https://github.com/gkrtjd99/Reporivet", error)
            self.assertNotIn("/blob/main/docs/", error)

    def test_doctor_requires_agents_and_checks_claude_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            code, output, error = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(code, 2)
            self.assertIn("AGENTS.md is missing", error)
            (root / "AGENTS.md").write_text("<!-- reporivet:entrypoints:start -->\n<!-- reporivet:entrypoints:end -->\n")
            (root / "CLAUDE.md").write_text("<!-- reporivet:entrypoints:claude:start -->\nwrong\n<!-- reporivet:entrypoints:claude:end -->\n")
            code, output, error = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(code, 2)
            self.assertIn("does not reference AGENTS.md", error)

    def test_symlink_and_fifo_targets_are_rejected_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory).resolve()
            linked = Path(outside).resolve() / "AGENTS.md"
            linked.write_text("outside\n")
            (root / "AGENTS.md").symlink_to(linked)
            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 2)
            self.assertIn("symlink", error)
            self.assertEqual(linked.read_text(), "outside\n")

            (root / "AGENTS.md").unlink()
            if hasattr(os, "mkfifo"):
                os.mkfifo(root / "AGENTS.md")
                code, output, error = self.run_cli("init", "--root", str(root))
                self.assertEqual(code, 2)
                self.assertIn("regular file", error)

    def test_marker_with_indent_is_not_claimed_as_managed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            agents = root / "AGENTS.md"
            agents.write_text("  <!-- reporivet:entrypoints:start -->\n  <!-- reporivet:entrypoints:end -->\n")
            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 2)
            self.assertIn("malformed managed markers", error)

    def test_reserved_symlink_is_visible_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory).resolve()
            target = Path(outside) / "version"
            target.write_text("0.2.0\n")
            (root / ".reporivet-version").symlink_to(target)
            code, output, error = self.run_cli("init", "--root", str(root))
            self.assertEqual(code, 2)
            self.assertIn("reserved", error)
            self.assertFalse((root / "AGENTS.md").exists())

    def test_asset_substitution_is_single_pass(self) -> None:
        from reporivet.initializer import read_asset
        rendered = read_asset("root/AGENTS.md.tmpl", {
            "PROJECT_NAME": "{{OBSERVED_PATH_ROWS}}",
            "PROJECT_SUMMARY": "summary",
            "OBSERVED_PATH_ROWS": "ROW",
            "OBSERVED_EXCLUSIONS": "none",
        })
        self.assertIn("# {{OBSERVED_PATH_ROWS}} agent entrypoints", rendered)
        self.assertNotIn("# ROW agent entrypoints", rendered)

    def test_doctor_checks_managed_links_but_not_user_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "AGENTS.md").write_text(
                "user [outside](https://example.invalid/missing)\n\n"
                "<!-- reporivet:entrypoints:start -->\n"
                "# Fixture agent entrypoints\n\n"
                "- [missing.md](./missing.md)\n"
                "<!-- reporivet:entrypoints:end -->\n"
            )
            code, output, error = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(code, 2)
            self.assertIn("target is missing", error)
            (root / "missing.md").write_text("ok\n")
            code, output, error = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(code, 0, output + error)


if __name__ == "__main__":
    unittest.main()
