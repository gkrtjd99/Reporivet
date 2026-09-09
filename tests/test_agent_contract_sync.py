from __future__ import annotations

import importlib.util
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[1]
START = b"<!-- reporivet:portable:start -->"
END = b"<!-- reporivet:portable:end -->"


class AgentContractSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve() / "source"
        (self.root / "dev").mkdir(parents=True)
        for name in ("agent-contract-sync", "agent_contract_sync.py"):
            shutil.copy2(REPOSITORY / "dev" / name, self.root / "dev" / name)
        self.source = self.root / "CLAUDE.md"
        self.target = self.root / "AGENTS.md"
        self.payload = b"# Portable contract\n\nKeep all bytes.\n"
        self.source.write_bytes(self.document(self.payload))
        self.target.write_bytes(b"old contract\n")

    def document(self, payload: bytes) -> bytes:
        return b"Provider-only instructions\n" + START + b"\n" + payload + END + b"\nProvider-only footer\n"

    def run_sync(self, *args: str, root: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str((root or self.root) / "dev/agent-contract-sync"), *args],
            cwd=self.root.parent,
            env={**os.environ, "PYTHON": sys.executable},
            capture_output=True, text=True, timeout=10,
        )

    def snapshot(self, path: Path) -> tuple[bytes, int, int]:
        info = path.stat()
        return path.read_bytes(), stat.S_IMODE(info.st_mode), info.st_mtime_ns

    def load_helper(self):
        spec = importlib.util.spec_from_file_location("contract_sync", self.root / "dev/agent_contract_sync.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_exact_projection_and_committed_check(self) -> None:
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.read_bytes(), self.payload)
        committed = (REPOSITORY / "CLAUDE.md").read_bytes()
        expected = committed.split(START + b"\n")[1].split(END)[0]
        self.assertEqual((REPOSITORY / "AGENTS.md").read_bytes(), expected)
        result = self.run_sync("--check", root=REPOSITORY)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_is_readonly_and_sync_preserves_mode_and_is_idempotent(self) -> None:
        self.target.chmod(0o640)
        before = [self.snapshot(path) for path in (self.source, self.target)]
        result = self.run_sync("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, [self.snapshot(path) for path in (self.source, self.target)])
        self.assertEqual(self.run_sync().returncode, 0)
        self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o640)
        synced = self.snapshot(self.target)
        self.assertEqual(self.run_sync().returncode, 0)
        self.assertEqual(self.run_sync("--check").returncode, 0)
        self.assertEqual(self.snapshot(self.target), synced)

    def test_unicode_crlf_trailing_spaces_and_empty_payload(self) -> None:
        for payload in ("한글 é 😀  \r\n\r\n끝 \t\r\n".encode(), b"", b" \n\n",
                        b"a\vb\fc\rd\n```python\nprint('portable')\n```\n"):
            with self.subTest(payload=payload):
                self.source.write_bytes(self.document(payload).replace(START + b"\n", START + b"\r\n"))
                self.assertEqual(self.run_sync().returncode, 0)
                self.assertEqual(self.target.read_bytes(), payload)

    def test_unsafe_markers_and_invalid_utf8_refuse_without_writes(self) -> None:
        valid = self.document(self.payload)
        cases = [
            b"no markers\n", valid.replace(END, b""), valid + START + b"\n",
            END + b"\n" + START + b"\n", valid + valid,
            valid.replace(START, b"prefix " + START),
            valid.replace(END, END + b" trailing"),
            valid.replace(START, b" <!-- reporivet:portable:start -->"),
            valid.replace(START, b"<!-- reporivet:portable:START -->"),
            b"```markdown\n" + valid + b"```\n",
            b"~~~\n" + valid + b"~~~\n",
            valid + b"```\n" + START + b"\n```\n",
            valid.replace(self.payload, b"\xff\n"), valid + b"\xff",
        ]
        for document in cases:
            with self.subTest(document=document):
                self.source.write_bytes(document)
                before = self.snapshot(self.target)
                self.assertNotEqual(self.run_sync().returncode, 0)
                self.assertEqual(self.snapshot(self.target), before)
                self.assertEqual(list(self.root.glob(".AGENTS.md.*")), [])
        self.source.write_bytes(valid)
        self.target.write_bytes(b"\xff")
        before = self.snapshot(self.target)
        self.assertNotEqual(self.run_sync().returncode, 0)
        self.assertEqual(self.snapshot(self.target), before)

    def test_file_symlinks_directories_and_fifos_are_rejected_before_read(self) -> None:
        for path in (self.source, self.target):
            original = path.read_bytes()
            for kind in ("symlink", "directory", "fifo"):
                with self.subTest(path=path.name, kind=kind):
                    path.unlink()
                    outside = self.root.parent / "outside"
                    outside.write_bytes(original)
                    if kind == "symlink":
                        path.symlink_to(outside)
                    elif kind == "directory":
                        path.mkdir()
                    else:
                        os.mkfifo(path)
                    self.assertNotEqual(self.run_sync().returncode, 0)
                    self.assertEqual(outside.read_bytes(), original)
                    if kind == "directory":
                        path.rmdir()
                    else:
                        path.unlink()
                    path.write_bytes(original)

    def test_root_and_parent_symlinks_are_rejected(self) -> None:
        alias = self.root.parent / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        before = self.snapshot(self.target)
        self.assertNotEqual(self.run_sync(root=alias).returncode, 0)
        parent_alias = self.root.parent / "parent-alias"
        parent_alias.symlink_to(self.root.parent, target_is_directory=True)
        self.assertNotEqual(self.run_sync(root=parent_alias / "source").returncode, 0)
        self.assertEqual(self.snapshot(self.target), before)
        helper = self.load_helper()
        for invalid_root in (self.target, self.root / "missing"):
            with self.assertRaises((ValueError, OSError)):
                helper.sync(invalid_root, check=False)

    def test_symlink_dotdot_rejects_direct_and_wrapper_without_touching_either_root(self) -> None:
        other = self.root.parent / "other"
        (other / "child").mkdir(parents=True)
        physical = other / "source"
        shutil.copytree(self.root, physical)
        (physical / "CLAUDE.md").write_bytes(self.document(b"physical new\n"))
        (physical / "AGENTS.md").write_bytes(b"physical old\n")
        link = self.root.parent / "link"
        link.symlink_to(other / "child", target_is_directory=True)
        unsafe = link / ".." / "source"
        paths = [root / name for root in (self.root, physical) for name in ("CLAUDE.md", "AGENTS.md")]
        before = [self.snapshot(path) for path in paths]
        helper = self.load_helper()
        for entry in ("direct", "wrapper"):
            with self.subTest(entry=entry):
                if entry == "direct":
                    with self.assertRaisesRegex(ValueError, "unsafe directory"):
                        helper.sync(unsafe, check=False)
                else:
                    result = self.run_sync(root=unsafe)
                    self.assertNotEqual(result.returncode, 0, result.stderr)
                self.assertEqual([self.snapshot(path) for path in paths], before)

    def test_safe_relative_paths_and_dotdot_remain_supported(self) -> None:
        helper = self.load_helper()
        with mock.patch.object(helper.Path, "cwd", return_value=self.root.parent):
            self.assertTrue(helper.sync(Path("source/dev/.."), check=False))
        before = self.snapshot(self.target)
        result = subprocess.run(
            ["./source/dev/../dev/agent-contract-sync"], cwd=self.root.parent,
            env={**os.environ, "PYTHON": sys.executable}, capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.snapshot(self.target), before)

    def test_preimage_divergence_preserves_user_edit(self) -> None:
        helper = self.load_helper()
        original = helper.tempfile.mkstemp
        for path in (self.source, self.target):
            for mode_only in (False, True):
                with self.subTest(path=path.name, mode_only=mode_only):
                    self.source.write_bytes(self.document(self.payload))
                    self.target.write_bytes(b"old\n")
                    def diverge(*args, **kwargs):
                        result = original(*args, **kwargs)
                        if mode_only:
                            path.chmod(stat.S_IMODE(path.stat().st_mode) ^ 0o100)
                        else:
                            path.write_bytes(b"user edit\n")
                        return result
                    with mock.patch.object(helper.tempfile, "mkstemp", side_effect=diverge):
                        with self.assertRaisesRegex(ValueError, "changed"):
                            helper.sync(self.root, check=False)
                    if not mode_only:
                        self.assertEqual(path.read_bytes(), b"user edit\n")
                    self.assertEqual(list(self.root.glob(".AGENTS.md.*")), [])

    def test_atomic_replace_failure_preserves_original(self) -> None:
        helper = self.load_helper()
        before = self.snapshot(self.target)
        with mock.patch.object(helper.os, "replace", side_effect=OSError("injected replace failure")):
            with self.assertRaises(OSError):
                helper.sync(self.root, check=False)
        self.assertEqual(self.snapshot(self.target), before)
        self.assertEqual(list(self.root.glob(".AGENTS.md.*")), [])

    def test_wrapper_honors_python_override_from_another_cwd(self) -> None:
        python = self.root.parent / "chosen python"
        marker = self.root.parent / "python-used"
        python.write_text(f'#!/bin/sh\nprintf used > "{marker}"\nexec "{sys.executable}" "$@"\n')
        python.chmod(0o755)
        result = subprocess.run([str(self.root / "dev/agent-contract-sync")], cwd=self.root.parent,
                                env={**os.environ, "PYTHON": str(python)}, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(marker.exists())
        self.assertEqual(self.target.read_bytes(), self.payload)

    def test_source_only_tools_are_not_assets_or_generated_targets(self) -> None:
        assets = REPOSITORY / "src/reporivet/assets/project"
        forbidden = {"CLAUDE.md", "agent-contract-sync", "agent_contract_sync.py"}
        self.assertFalse(forbidden & {path.name for path in assets.rglob("*")})
        target = self.root.parent / "generated"
        result = subprocess.run(
            [sys.executable, "-m", "reporivet", "init", "--root", str(target), "--name", "Fixture"],
            env={**os.environ, "PYTHONPATH": str(REPOSITORY / "src"), "PYTHON": sys.executable},
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(forbidden & {path.name for path in target.rglob("*")})
        self.assertNotIn("reporivet:portable", (target / "AGENTS.md").read_text())


if __name__ == "__main__":
    unittest.main()
