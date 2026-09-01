from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet.cli import build_parser, main as cli_main
from reporivet.guided import DEFINITION_TOPICS


class _FakeEnvelope:
    def __init__(self, document: str = '{"schema":"reporivet.setup/v1"}\n') -> None:
        self.document = document
        self.render_calls = 0

    def render(self) -> str:
        self.render_calls += 1
        return self.document


class _FakeStdin:
    def __init__(self, is_tty: bool) -> None:
        self._is_tty = is_tty

    def isatty(self) -> bool:
        return self._is_tty


class _TtyInput(io.StringIO):
    def isatty(self) -> bool:
        return True


class SetupCliTests(unittest.TestCase):
    def invoke_with_fake_setup(
        self,
        arguments: list[str],
        *,
        is_tty: bool,
    ) -> tuple[int, str, str, list[dict[str, object]], _FakeEnvelope]:
        calls: list[dict[str, object]] = []
        envelope = _FakeEnvelope("setup-envelope\n")
        module = types.ModuleType("reporivet.setup")

        def coordinate_setup(**kwargs: object) -> _FakeEnvelope:
            calls.append(kwargs)
            return envelope

        module.coordinate_setup = coordinate_setup  # type: ignore[attr-defined]
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.dict(sys.modules, {"reporivet.setup": module}):
            with patch.object(sys, "stdin", _FakeStdin(is_tty)):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    returncode = cli_main(arguments)
        return returncode, stdout.getvalue(), stderr.getvalue(), calls, envelope

    def invoke(self, arguments: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(arguments)
        return returncode, stdout.getvalue(), stderr.getvalue()

    def test_setup_parser_has_only_the_frozen_surface_and_requires_root(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "setup",
                "--root",
                "/tmp/project",
                "--answers",
                "/tmp/answers.json",
                "--with-claude-settings",
                "--dry-run",
                "--apply",
                "--approve-preview",
                "preview-hash",
            ]
        )
        self.assertEqual(parsed.command, "setup")
        self.assertEqual(parsed.root, Path("/tmp/project"))
        self.assertEqual(parsed.answers, Path("/tmp/answers.json"))
        self.assertTrue(parsed.with_claude_settings)
        self.assertTrue(parsed.dry_run)
        self.assertTrue(parsed.apply)
        self.assertEqual(parsed.approve_preview, "preview-hash")

        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(["setup"])
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args([])

    def test_preview_passes_all_inputs_and_renders_exactly_one_document(self) -> None:
        arguments = [
            "setup",
            "--root",
            "/tmp/project",
            "--answers",
            "/tmp/answers.json",
            "--with-claude-settings",
            "--dry-run",
        ]
        returncode, stdout, stderr, calls, envelope = self.invoke_with_fake_setup(
            arguments,
            is_tty=True,
        )

        self.assertEqual(returncode, 0)
        self.assertEqual(stdout, "setup-envelope\n")
        self.assertEqual(stderr, "")
        self.assertEqual(envelope.render_calls, 1)
        self.assertEqual(
            calls,
            [
                {
                    "root": Path("/tmp/project"),
                    "answers": Path("/tmp/answers.json"),
                    "with_claude_settings": True,
                    "dry_run": True,
                    "apply": False,
                    "approve_preview": "",
                    "stdin_is_tty": True,
                }
            ],
        )

    def test_apply_passes_approval_and_settings_without_answers_or_dry_run(self) -> None:
        returncode, stdout, stderr, calls, envelope = self.invoke_with_fake_setup(
            [
                "setup",
                "--root",
                "/tmp/project",
                "--with-claude-settings",
                "--apply",
                "--approve-preview",
                "preview-hash",
            ],
            is_tty=False,
        )

        self.assertEqual(returncode, 0)
        self.assertEqual(stdout, "setup-envelope\n")
        self.assertEqual(stderr, "")
        self.assertEqual(envelope.render_calls, 1)
        self.assertEqual(
            calls,
            [
                {
                    "root": Path("/tmp/project"),
                    "answers": None,
                    "with_claude_settings": True,
                    "dry_run": False,
                    "apply": True,
                    "approve_preview": "preview-hash",
                    "stdin_is_tty": False,
                }
            ],
        )

    def test_real_tty_setup_routes_prompt_to_stderr_and_emits_one_json_document(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            stdout = io.StringIO()
            stderr = io.StringIO()
            stdin = _TtyInput("Recorded product answer\n")
            with patch.object(sys, "stdin", stdin):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    returncode = cli_main(["setup", "--root", str(root)])

            stdout_text = stdout.getvalue()
            stderr_text = stderr.getvalue()
            self.assertEqual(returncode, 0)
            self.assertTrue(stdout_text.startswith("{"))
            payload = json.loads(stdout_text)
            self.assertEqual(payload["schema"], "reporivet.setup/v1")
            self.assertEqual(
                stdout_text[json.JSONDecoder().raw_decode(stdout_text)[1] :],
                "\n",
            )

            prompt = f"{DEFINITION_TOPICS[0].question}\n> "
            self.assertNotIn(prompt, stdout_text)
            self.assertEqual(stderr_text, prompt)

            self.assertEqual(
                payload["input"],
                {"mode": "tty", "prompted": True, "recorded": True},
            )
            topics = payload["definition"]["topics"]
            confirmed: list[object] = []
            for topic in topics.values():
                confirmed.extend(topic["confirmed"])
            self.assertEqual(confirmed, ["Recorded product answer"])

    def test_invalid_setup_mode_combinations_write_only_an_error_to_stderr(self) -> None:
        cases = (
            (
                ["setup", "--root", "/tmp/project", "--apply"],
                "setup --apply requires --approve-preview HASH",
            ),
            (
                ["setup", "--root", "/tmp/project", "--approve-preview", "preview-hash"],
                "--approve-preview requires setup --apply",
            ),
            (
                [
                    "setup",
                    "--root",
                    "/tmp/project",
                    "--apply",
                    "--approve-preview",
                    "preview-hash",
                    "--answers",
                    "/tmp/answers.json",
                ],
                "setup --apply does not accept --answers",
            ),
            (
                [
                    "setup",
                    "--root",
                    "/tmp/project",
                    "--apply",
                    "--approve-preview",
                    "preview-hash",
                    "--dry-run",
                ],
                "setup --apply cannot be combined with --dry-run",
            ),
        )
        for arguments, expected_error in cases:
            with self.subTest(arguments=arguments):
                returncode, stdout, stderr = self.invoke(arguments)
                self.assertEqual(returncode, 2)
                self.assertEqual(stdout, "")
                self.assertIn(expected_error, stderr)


if __name__ == "__main__":
    unittest.main()
