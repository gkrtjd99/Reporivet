from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet.cli import main as cli_main
from reporivet.guided import LEGACY_RUNTIME_PATHS, parse_definition_draft
from reporivet.initializer import read_asset
from reporivet.procedures import ProcedureSpec


class GuidedSetupTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(list(args))
        return returncode, stdout.getvalue(), stderr.getvalue()

    def define(self, root: Path, action: str, *extra: str) -> tuple[int, str, str]:
        return self.run_cli("define", action, "--root", str(root), *extra)

    def procedure(self, slug: str = "release-check") -> ProcedureSpec:
        return ProcedureSpec(
            slug=slug,
            title="Release check procedure",
            trigger="a maintainer explicitly requests the confirmed procedure",
            reads=("docs/OPERATIONS.md",),
            actions=("Run the project-owned documented command.",),
            stop_conditions=("Stop if a documented prerequisite is missing.",),
            evidence=("Record the project-owned command result.",),
            permissions=("Use only permissions granted by the project owner.",),
            rollback=("Follow docs/OPERATIONS.md rollback guidance.",),
        )

    def snapshot(self, root: Path) -> tuple[tuple[str, str, int, bytes | str | None], ...]:
        entries: list[tuple[str, str, int, bytes | str | None]] = []
        for current_text, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
            current = Path(current_text)
            for name in sorted(directory_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                mode = stat.S_IMODE(path.lstat().st_mode)
                if path.is_symlink():
                    entries.append((relative, "symlink", mode, os.readlink(path)))
                else:
                    entries.append((relative, "directory", mode, None))
            for name in sorted(file_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                mode = stat.S_IMODE(path.lstat().st_mode)
                if path.is_symlink():
                    entries.append((relative, "symlink", mode, os.readlink(path)))
                else:
                    entries.append((relative, "file", mode, path.read_bytes()))
        return tuple(sorted(entries))

    def preview(self, root: Path, *extra: str) -> dict[str, object]:
        returncode, stdout, stderr = self.define(root, "finalize", *extra)
        self.assertEqual(returncode, 0, stdout + stderr)
        return json.loads(stdout)

    def apply_preview(self, root: Path, preview: dict[str, object], *extra: str) -> tuple[int, str, str]:
        return self.define(
            root,
            "finalize",
            "--apply",
            "--approve-preview",
            str(preview["fingerprint"]),
            *extra,
        )

    def install_bundle(self, root: Path) -> None:
        returncode, stdout, stderr = self.define(root, "start")
        self.assertEqual(returncode, 0, stdout + stderr)
        preview = self.preview(root)
        returncode, stdout, stderr = self.apply_preview(root, preview)
        self.assertEqual(returncode, 0, stdout + stderr)

    def test_scan_and_dry_run_are_read_only_and_keep_inference_proposed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            sentinel = root / "project-command-ran"
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "scripts": {
                            "test": f"python -c 'from pathlib import Path; Path({str(sentinel)!r}).write_text(\"ran\")'",
                            "build": "tsc",
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            before = self.snapshot(root)

            returncode, stdout, stderr = self.define(root, "start", "--dry-run")
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertEqual(self.snapshot(root), before)
            self.assertFalse(sentinel.exists())
            self.assertFalse((root / "docs/product-specs/project-definition.draft.md").exists())

            returncode, stdout, stderr = self.define(root, "start")
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertFalse(sentinel.exists())
            draft_path = root / "docs/product-specs/project-definition.draft.md"
            text = draft_path.read_text(encoding="utf-8")
            draft = parse_definition_draft(text)
            quality = draft.evidence["quality"]
            self.assertEqual(quality.confirmed, [])
            self.assertTrue(any("commands/" in item for item in quality.proposed))
            self.assertTrue(any("without execution" in item for item in quality.sources))
            self.assertEqual(
                [text.index(f"### {heading}") for heading in ("Confirmed", "Proposed", "Open", "Sources")],
                sorted(text.index(f"### {heading}") for heading in ("Confirmed", "Proposed", "Open", "Sources")),
            )

            status_code, status_stdout, status_stderr = self.define(root, "status")
            self.assertEqual(status_code, 0, status_stdout + status_stderr)
            status = json.loads(status_stdout)
            self.assertEqual(status["confirmed_topics"], 0)
            self.assertEqual(status["next"], "product")

    def test_resume_uses_only_the_visible_draft_and_preserves_evidence_states(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.assertEqual(self.define(root, "start")[0], 0)
            answers = root / "answers.json"
            answers.write_text(
                json.dumps(
                    {
                        "product": "For one maintainer; {{DESIGN_EVIDENCE}} is literal and success is observable.",
                        "design": {
                            "confirmed": ["Keyboard access and visible focus are required."],
                            "proposed": ["Review reduced-motion behavior."],
                            "open": ["Which locales are supported?"],
                            "sources": ["Owner interview on 2026-08-31."],
                        },
                    }
                ),
                encoding="utf-8",
            )

            returncode, stdout, stderr = self.define(root, "resume", "--answers", str(answers))
            self.assertEqual(returncode, 0, stdout + stderr)
            draft_path = root / "docs/product-specs/project-definition.draft.md"
            text = draft_path.read_text(encoding="utf-8")
            draft = parse_definition_draft(text)
            self.assertEqual(
                draft.evidence["product"].confirmed,
                ["For one maintainer; {{DESIGN_EVIDENCE}} is literal and success is observable."],
            )
            self.assertEqual(draft.evidence["product"].open, [])
            self.assertEqual(
                draft.evidence["design"].confirmed,
                ["Keyboard access and visible focus are required."],
            )
            self.assertEqual(draft.evidence["design"].proposed, ["Review reduced-motion behavior."])
            self.assertEqual(draft.evidence["design"].open, ["Which locales are supported?"])
            self.assertEqual(draft.evidence["design"].sources, ["Owner interview on 2026-08-31."])
            self.assertIn('progress: "2/7"', text)
            self.assertIn('next: "3. Quality and project commands"', text)
            preview = self.preview(root)
            product_action = next(
                action for action in preview["actions"] if action["path"] == "docs/PRODUCT.md"
            )
            self.assertIn("{{DESIGN_EVIDENCE}} is literal", product_action["content"])
            self.assertEqual(product_action["content"].count("Keyboard access and visible focus"), 0)

            answers.write_text(json.dumps({"quality": "Run the repository-owned unit test command."}), encoding="utf-8")
            before = self.snapshot(root)
            returncode, stdout, stderr = self.define(
                root,
                "resume",
                "--answers",
                str(answers),
                "--dry-run",
            )
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertEqual(self.snapshot(root), before)
            self.assertEqual(parse_definition_draft(draft_path.read_text(encoding="utf-8")).confirmed_count, 2)

            invalid = root / "invalid.json"
            invalid.write_text(json.dumps({"quality": "line one\nline two"}), encoding="utf-8")
            returncode, _, stderr = self.define(root, "resume", "--answers", str(invalid))
            self.assertEqual(returncode, 2)
            self.assertIn("one Markdown bullet per string", stderr)

    def test_document_first_templates_keep_sources_and_project_owned_evidence_language(self) -> None:
        product_spec = read_asset(
            "document-first/docs/product-specs/_template.md.tmpl"
        )
        positions = [
            product_spec.index(f"### {heading}")
            for heading in ("Confirmed", "Proposed", "Open", "Sources")
        ]
        self.assertEqual(positions, sorted(positions))

        core_beliefs = read_asset(
            "document-first/docs/design-docs/core-beliefs.md.tmpl"
        )
        self.assertIn("project-owned checks with inspectable evidence", core_beliefs)
        self.assertNotIn("feedback gate", core_beliefs.casefold())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.assertEqual(self.define(root, "start")[0], 0)
            actions = {
                str(action["path"]): action
                for action in self.preview(root)["actions"]
            }
            self.assertIn(
                "### Sources",
                actions["docs/product-specs/_template.md"]["content"],
            )
            self.assertIn(
                "project-owned checks with inspectable evidence",
                actions["docs/design-docs/core-beliefs.md"]["content"],
            )

    def test_setup_bundle_uses_markdown_authority_without_a_diagnostic_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_bundle(root)

            inventory = (root / "docs/README.md").read_text(encoding="utf-8")
            plans = (root / "docs/PLANS.md").read_text(encoding="utf-8")
            runbooks = (root / "docs/runbooks/index.md").read_text(encoding="utf-8")
            self.assertIn("ordinary Markdown", inventory)
            self.assertIn("Package absence after setup is expected", inventory)
            self.assertIn("Setup handoff does not create a Plan", inventory)
            self.assertIn("Setup handoff creates no Plan", plans)
            self.assertIn("static runbook", runbooks)
            self.assertNotIn(".claude/skills/<slug>/SKILL.md", inventory)
            self.assertFalse((root / ".claude/settings.json").exists())
            self.assertFalse((root / ".reporivet-version").exists())

            quality = root / "docs/QUALITY.md"
            quality.write_bytes(b"# Quality\n\xff\n")
            preview = self.preview(root)
            actions = {str(action["path"]): action for action in preview["actions"]}
            self.assertEqual(actions["docs/QUALITY.md"]["action"], "preserve")
            returncode, stdout, stderr = self.apply_preview(root, preview)
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertEqual(quality.read_bytes(), b"# Quality\n\xff\n")

    def test_markdown_authority_preserves_retired_vocabulary_without_rewriting(self) -> None:
        cases = (
            "Do not use Gate; Gate is current",
            "Automatic Plan closure does not apply.",
            "Gate is current; do not use Gate. The Reporivet runtime is retired; Automatic Plan closure is current.",
            "Do not use Gate, and Gate is current",
            "Gate is retired, Gate is current",
            "Gate is current and Automatic Plan closure does not apply.",
            "Do not use Gate, Automatic Plan closure, or the Reporivet runtime.",
        )
        for guidance in cases:
            with self.subTest(guidance=guidance), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                self.install_bundle(root)
                product = root / "docs/PRODUCT.md"
                original = product.read_bytes()
                product.write_bytes(original + ("\n" + guidance + "\n").encode("utf-8"))

                preview = self.preview(root)
                action = next(
                    action
                    for action in preview["actions"]
                    if action["path"] == "docs/PRODUCT.md"
                )
                self.assertEqual(action["action"], "preserve")
                self.assertEqual(
                    action["current_sha256"],
                    hashlib.sha256(product.read_bytes()).hexdigest(),
                )
                returncode, stdout, stderr = self.apply_preview(root, preview)
                self.assertEqual(returncode, 0, stdout + stderr)
                self.assertEqual(
                    product.read_bytes(),
                    original + ("\n" + guidance + "\n").encode("utf-8"),
                )

    def test_confirmed_procedures_render_static_runbooks_and_preserve_stale_skills(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_bundle(root)
            spec = self.procedure()
            answers = root / "answers.json"
            answers.write_text(
                json.dumps(
                    {
                        "procedures": {
                            "confirmed": [
                                spec.canonical_record(),
                                "Generic procedure evidence.",
                                '{"slug":"incomplete"}',
                            ]
                        }
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            returncode, stdout, stderr = self.define(
                root,
                "resume",
                "--answers",
                str(answers),
            )
            self.assertEqual(returncode, 0, stdout + stderr)

            stale = root / ".claude/skills/old-name/SKILL.md"
            stale.parent.mkdir(parents=True)
            stale_bytes = b"not a valid Skill, but project-owned\n"
            stale.write_bytes(stale_bytes)

            preview = self.preview(root)
            actions = {str(action["path"]): action for action in preview["actions"]}
            runbook_relative = "docs/runbooks/release-check.md"
            self.assertEqual(actions[runbook_relative]["action"], "create")
            self.assertEqual(actions[stale.as_posix().replace(root.as_posix() + "/", "")]["action"], "preserve")
            self.assertIn("Generic procedure evidence", json.dumps(preview))
            self.assertIn("incomplete", json.dumps(preview))
            self.assertNotIn(".claude/skills/release-check/SKILL.md", actions)

            returncode, stdout, stderr = self.apply_preview(root, preview)
            self.assertEqual(returncode, 0, stdout + stderr)
            runbook = root / runbook_relative
            self.assertTrue(runbook.is_file())
            content = runbook.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("# Release check procedure\n"))
            self.assertNotIn("---\n", content)
            self.assertEqual(stale.read_bytes(), stale_bytes)
            self.assertFalse((root / ".claude/settings.json").exists())

    def test_setup_preserves_historical_runtime_without_inventory_or_access(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.assertEqual(self.define(root, "start")[0], 0)
            project_owned = root / "dev/verify"
            project_owned.parent.mkdir(parents=True)
            project_owned.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            (root / "dev/custom-tool").write_text("project owned\n", encoding="utf-8")
            for relative in LEGACY_RUNTIME_PATHS:
                (root / relative).mkdir(parents=True, exist_ok=True)
            retained = root / ".harness/runs/private.log"
            retained_bytes = b"sensitive retained evidence\n"
            retained.write_bytes(retained_bytes)
            runtime_before = self.snapshot(root)

            from reporivet import guided

            original_path_state = guided._path_state

            def reject_runtime_access(path: Path, relative: str):
                if relative == ".harness" or relative.startswith(".harness/"):
                    raise AssertionError(f"setup accessed retained runtime: {relative}")
                return original_path_state(path, relative)

            with mock.patch.object(
                guided,
                "_path_state",
                side_effect=reject_runtime_access,
            ):
                preview = self.preview(root)
                returncode, stdout, stderr = self.apply_preview(root, preview)
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertEqual(retained.read_bytes(), retained_bytes)
            self.assertTrue((root / "dev/verify").is_file())
            self.assertEqual(
                {
                    entry for entry in self.snapshot(root) if entry[0].startswith(".harness/")
                },
                {
                    entry for entry in runtime_before if entry[0].startswith(".harness/")
                },
            )

    def test_start_rejects_a_non_directory_parent_without_a_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            blocker = base / "blocking-file"
            blocker.write_text("not a directory\n", encoding="utf-8")
            root = blocker / "project"

            returncode, stdout, stderr = self.define(root, "start")

            self.assertEqual(returncode, 2, stdout + stderr)
            self.assertEqual(stdout, "")
            self.assertIn("project root parent is not a directory", stderr)
            self.assertNotIn("Traceback", stderr)
            self.assertEqual(blocker.read_text(encoding="utf-8"), "not a directory\n")

    def test_preview_reports_symlink_conflicts_and_apply_does_not_write_external_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
            root = Path(directory).resolve()
            external = Path(external_directory).resolve() / "PRODUCT.md"
            external.write_bytes(b"# External product\n")
            (root / "docs").mkdir()
            (root / "docs/PRODUCT.md").symlink_to(external)
            self.assertEqual(self.define(root, "start")[0], 0)

            preview = self.preview(root)
            actions = {str(action["path"]): action for action in preview["actions"]}
            self.assertEqual(actions["docs/PRODUCT.md"]["action"], "conflict")
            before_external = external.read_bytes()
            returncode, _, stderr = self.apply_preview(root, preview)
            self.assertEqual(returncode, 2)
            self.assertIn("unsafe target conflicts", stderr)
            self.assertEqual(external.read_bytes(), before_external)
            self.assertFalse((root / "AGENTS.md").exists())

    def test_preview_apply_preserves_project_files_and_rejects_stale_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            sentinel = root / "project-command-ran"
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "scripts": {
                            "test": f"python -c 'from pathlib import Path; Path({str(sentinel)!r}).write_text(\"ran\")'"
                        }
                    }
                ),
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_bytes(b"# Project instructions\n\nKeep this exact.  \n")
            (root / "docs").mkdir()
            product = root / "docs/PRODUCT.md"
            product.write_bytes(b"# Existing product\n\nDo not rewrite.  ")
            claude = root / "CLAUDE.md"
            claude.write_bytes(b"# Existing host instructions\n")
            self.assertEqual(self.define(root, "start")[0], 0)

            first = self.preview(root)
            actions = {str(action["path"]): action for action in first["actions"]}
            self.assertEqual(actions["docs/PRODUCT.md"]["action"], "preserve")
            self.assertEqual(actions["CLAUDE.md"]["action"], "preserve")
            self.assertNotIn(".claude/settings.json", actions)
            self.assertTrue(all("content" in action for action in first["actions"]))
            inventory = actions["docs/README.md"]["content"]
            for path in actions:
                self.assertIn(f"`{path}`", inventory, path)
            self.assertNotIn("`.claude/settings.json`", inventory)
            self.assertNotIn("`.claude/settings.local.json`", inventory)

            product.write_bytes(b"# Existing product\n\nChanged after preview.\n")
            before_stale_apply = self.snapshot(root)
            returncode, _, stderr = self.apply_preview(root, first)
            self.assertEqual(returncode, 2)
            self.assertIn("does not match", stderr)
            self.assertEqual(self.snapshot(root), before_stale_apply)

            current = self.preview(root)
            expected_product = product.read_bytes()
            expected_claude = claude.read_bytes()
            returncode, stdout, stderr = self.apply_preview(root, current)
            self.assertEqual(returncode, 0, stdout + stderr)
            self.assertEqual(product.read_bytes(), expected_product)
            self.assertEqual(claude.read_bytes(), expected_claude)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents, "# Project instructions\n\nKeep this exact.  \n")
            self.assertTrue((root / "docs/OPERATIONS.md").is_file())
            self.assertFalse((root / "docs/RELIABILITY.md").exists())
            self.assertFalse((root / "dev").exists())
            self.assertFalse((root / ".harness").exists())
            self.assertFalse((root / ".github/workflows/harness-verify.yml").exists())

            self.assertFalse(sentinel.exists())
            self.assertFalse((root / ".claude/settings.json").exists())
            self.assertFalse((root / ".reporivet-version").exists())
            self.assertFalse((root / ".harness").exists())
            self.assertNotIn("doctor", inventory.casefold())


if __name__ == "__main__":
    unittest.main()
