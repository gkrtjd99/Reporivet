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
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet.cli import main as cli_main
from reporivet.guided import (
    LEGACY_MANAGED_FILES,
    LEGACY_RUNTIME_PATHS,
    parse_definition_draft,
)
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

    def test_doctor_validates_authority_structure_utf8_and_retired_vocabulary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_bundle(root)
            product = root / "docs/PRODUCT.md"
            original_product = product.read_text(encoding="utf-8")

            product.write_text(
                "# Product\n\nThe generated Gate is current.\n",
                encoding="utf-8",
            )
            returncode, stdout, stderr = self.run_cli(
                "doctor", "--root", str(root)
            )
            self.assertEqual(returncode, 2, stdout + stderr)
            product_findings = [
                finding
                for finding in json.loads(stdout)["findings"]
                if finding["path"] == "docs/PRODUCT.md"
            ]
            self.assertTrue(
                any("missing required structure" in finding["detail"] for finding in product_findings)
            )
            self.assertTrue(
                any("singular Gate" in finding["detail"] for finding in product_findings)
            )

            product.write_text(
                original_product
                + "\nThe Reporivet runtime is current.\n"
                + "Automatic Plan closure is current.\n"
                + "The generated gate is current.\n",
                encoding="utf-8",
            )
            returncode, stdout, stderr = self.run_cli(
                "doctor", "--root", str(root)
            )
            self.assertEqual(returncode, 0, stdout + stderr)
            details = [
                finding["detail"]
                for finding in json.loads(stdout)["findings"]
                if finding["path"] == "docs/PRODUCT.md"
            ]
            self.assertTrue(any("singular Gate" in detail for detail in details))
            self.assertTrue(any("Reporivet runtime" in detail for detail in details))
            self.assertTrue(any("automatic Plan closure" in detail for detail in details))

            product.write_text(original_product, encoding="utf-8")
            quality = root / "docs/QUALITY.md"
            quality.write_bytes(b"# Quality\n\xff\n")
            returncode, stdout, stderr = self.run_cli(
                "doctor", "--root", str(root)
            )
            self.assertEqual(returncode, 2, stdout + stderr)
            self.assertTrue(
                any(
                    finding["path"] == "docs/QUALITY.md"
                    and "UTF-8" in finding["detail"]
                    for finding in json.loads(stdout)["findings"]
                )
            )

    def test_retired_contract_detection_is_clause_local_and_checks_every_match(self) -> None:
        cases = (
            (
                "Do not use Gate; Gate is current",
                {"singular Gate": 1, "automatic Plan closure": 0, "Reporivet runtime": 0},
            ),
            (
                "Automatic Plan closure does not apply.",
                {"singular Gate": 0, "automatic Plan closure": 0, "Reporivet runtime": 0},
            ),
            (
                "Gate is current; do not use Gate. The Reporivet runtime is retired; Automatic Plan closure is current.",
                {"singular Gate": 1, "automatic Plan closure": 1, "Reporivet runtime": 0},
            ),
            (
                "Do not use Gate, and Gate is current",
                {"singular Gate": 1, "automatic Plan closure": 0, "Reporivet runtime": 0},
            ),
            (
                "Gate is retired, Gate is current",
                {"singular Gate": 1, "automatic Plan closure": 0, "Reporivet runtime": 0},
            ),
            (
                "Gate is current and Automatic Plan closure does not apply.",
                {"singular Gate": 1, "automatic Plan closure": 0, "Reporivet runtime": 0},
            ),
            (
                "Do not use Gate, Automatic Plan closure, or the Reporivet runtime.",
                {"singular Gate": 0, "automatic Plan closure": 0, "Reporivet runtime": 0},
            ),
        )
        for guidance, expected_counts in cases:
            with self.subTest(guidance=guidance), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                self.install_bundle(root)
                product = root / "docs/PRODUCT.md"
                product.write_text(
                    product.read_text(encoding="utf-8") + "\n" + guidance + "\n",
                    encoding="utf-8",
                )

                returncode, stdout, stderr = self.run_cli(
                    "doctor", "--root", str(root)
                )
                self.assertEqual(returncode, 0, stdout + stderr)
                details = [
                    finding["detail"]
                    for finding in json.loads(stdout)["findings"]
                    if finding["path"] == "docs/PRODUCT.md"
                    and finding["severity"] == "warning"
                ]
                for marker, expected_count in expected_counts.items():
                    self.assertEqual(
                        sum(marker in detail for detail in details),
                        expected_count,
                        details,
                    )

    def test_doctor_derives_confirmed_procedure_skills_without_scanning_stale_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
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
            stale.write_text("not a valid Skill, but project-owned\n", encoding="utf-8")
            target_relative = ".claude/skills/release-check/SKILL.md"

            returncode, stdout, stderr = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(returncode, 0, stdout + stderr)
            findings = json.loads(stdout)["findings"]
            self.assertTrue(
                any(
                    finding["path"] == target_relative
                    and finding["severity"] == "warning"
                    and "not installed" in finding["detail"]
                    for finding in findings
                )
            )
            self.assertEqual(
                {
                    finding["path"]
                    for finding in findings
                    if finding["path"].startswith("procedures.confirmed[")
                },
                {"procedures.confirmed[1]", "procedures.confirmed[2]"},
            )
            self.assertNotIn(
                ".claude/skills/old-name/SKILL.md",
                {finding["path"] for finding in findings},
            )

            preview = self.preview(root)
            returncode, stdout, stderr = self.apply_preview(root, preview)
            self.assertEqual(returncode, 0, stdout + stderr)
            target = root / target_relative
            self.assertTrue(target.is_file())

            returncode, stdout, stderr = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(returncode, 0, stdout + stderr)
            installed_findings = json.loads(stdout)["findings"]
            self.assertFalse(
                any(
                    finding["path"] == target_relative
                    and "not installed" in finding["detail"]
                    for finding in installed_findings
                )
            )
            self.assertNotIn(
                ".claude/skills/old-name/SKILL.md",
                {finding["path"] for finding in installed_findings},
            )

            fixed = root / ".claude/skills/reporivet-main/SKILL.md"
            fixed_content = fixed.read_bytes()
            fixed.write_text(
                "---\nname: wrong-name\ndescription: missing trigger\nallowed-tools: Bash\n---\n",
                encoding="utf-8",
            )
            returncode, stdout, stderr = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(returncode, 2, stdout + stderr)
            fixed_findings = [
                finding
                for finding in json.loads(stdout)["findings"]
                if finding["path"] == ".claude/skills/reporivet-main/SKILL.md"
            ]
            self.assertTrue(
                any("match its parent" in finding["detail"] for finding in fixed_findings)
            )
            self.assertTrue(
                any("allowed-tools" in finding["detail"] for finding in fixed_findings)
            )
            fixed.write_bytes(fixed_content)

            external = Path(external_directory).resolve() / "external-skill.md"
            external_content = b"external sensitive Skill content\n"
            external.write_bytes(external_content)
            target.unlink()
            target.symlink_to(external)
            returncode, stdout, stderr = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(returncode, 2, stdout + stderr)
            self.assertTrue(
                any(
                    finding["path"] == target_relative
                    and finding["severity"] == "error"
                    and "unsafe" in finding["detail"]
                    for finding in json.loads(stdout)["findings"]
                )
            )
            self.assertEqual(external.read_bytes(), external_content)

    def test_doctor_inventory_reports_only_managed_legacy_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_bundle(root)
            project_owned = root / "dev/verify"
            project_owned.parent.mkdir(parents=True)
            project_owned.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            (root / "dev/custom-tool").write_text("project owned\n", encoding="utf-8")

            returncode, stdout, stderr = self.run_cli(
                "doctor", "--root", str(root)
            )
            self.assertEqual(returncode, 0, stdout + stderr)
            initial_paths = {
                finding["path"] for finding in json.loads(stdout)["findings"]
            }
            self.assertNotIn("dev/verify", initial_paths)
            self.assertNotIn("dev/custom-tool", initial_paths)

            managed = "# reporivet:managed version=0.2.0\n"
            for relative in LEGACY_MANAGED_FILES:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(managed, encoding="utf-8")
            (root / "dev/harness.toml").write_text(
                "version = 1\n\n[project]\nname = \"fixture\"\n\n[commands]\n\n[paths]\n",
                encoding="utf-8",
            )
            for relative in LEGACY_RUNTIME_PATHS:
                (root / relative).mkdir(parents=True, exist_ok=True)
            retained = root / ".harness/runs/private.log"
            retained.write_bytes(b"sensitive retained evidence\n")

            returncode, stdout, stderr = self.run_cli(
                "doctor", "--root", str(root)
            )
            self.assertEqual(returncode, 0, stdout + stderr)
            findings = json.loads(stdout)["findings"]
            warning_paths = {
                finding["path"]
                for finding in findings
                if finding["severity"] == "warning"
            }
            expected = set(LEGACY_MANAGED_FILES) | set(LEGACY_RUNTIME_PATHS) | {
                "dev/harness.toml"
            }
            self.assertTrue(expected.issubset(warning_paths), sorted(expected - warning_paths))
            self.assertNotIn("dev/custom-tool", warning_paths)
            self.assertEqual(retained.read_bytes(), b"sensitive retained evidence\n")

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
            sentinel = root / "doctor-command-ran"
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
            self.assertIn("`.claude/settings.json`", inventory)
            self.assertIn("`.claude/settings.local.json`", inventory)

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
            self.assertTrue(agents.startswith("# Project instructions\n\nKeep this exact.  \n"))
            self.assertEqual(agents.count("<!-- reporivet:start -->"), 1)
            self.assertTrue((root / "docs/OPERATIONS.md").is_file())
            self.assertFalse((root / "docs/RELIABILITY.md").exists())
            self.assertFalse((root / "dev").exists())
            self.assertFalse((root / ".harness").exists())
            self.assertFalse((root / ".github/workflows/harness-verify.yml").exists())

            before_doctor = self.snapshot(root)
            returncode, doctor_stdout, doctor_stderr = self.run_cli(
                "doctor",
                "--root",
                str(root),
            )
            self.assertEqual(returncode, 2, doctor_stdout + doctor_stderr)
            self.assertEqual(self.snapshot(root), before_doctor)
            self.assertFalse(sentinel.exists())
            findings = json.loads(doctor_stdout)["findings"]
            self.assertTrue(
                any(
                    finding["severity"] == "error"
                    and finding["path"] == "docs/PRODUCT.md"
                    and "missing required structure" in finding["detail"]
                    for finding in findings
                )
            )


if __name__ == "__main__":
    unittest.main()
