from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet.cli import main as cli_main


SECTIONS = (
    "Project Identity",
    "Problem and Current Alternative",
    "Target Users",
    "Value Proposition and Solution",
    "MVP Capabilities and Priority",
    "User Journeys",
    "Scope Boundaries",
    "Success Signals",
    "Non-Functional Requirements",
    "Stack and Architecture Constraints",
    "Agent Operating Model",
    "Repository Boundaries and Context",
    "Verification and Handoff",
    "First Milestone, Dependencies, and Risks",
)

CONFIRMED = {
    1: [
        "Project name: Sample Project",
        "Project purpose: Provide one repository-native sample capability.",
    ],
    2: [
        "Problem: Maintainers cannot verify the first project behavior from repository evidence.",
        "Current alternative: Repeat untracked manual setup and inspection.",
    ],
    3: ["Primary user: A maintainer starting a repository-native project."],
    4: [
        "Value proposition: Make the first useful behavior observable and repeatable.",
        "Solution boundary: Deliver only the confirmed first slice.",
    ],
    5: [
        "REQ-P0-001 | Journey: JRN-001 | Acceptance: AC-001 | Provide one observable greeting command."
    ],
    6: ["JRN-001 | A maintainer runs the greeting command and observes its output."],
    7: [
        "In scope: One local greeting command and its deterministic test.",
        "Out of scope: Network services, accounts, and deployment.",
    ],
    8: ["Success signal: The command exits zero and prints the confirmed greeting."],
    9: ["Reliability constraint: The first slice is deterministic and local-only."],
    10: ["Architecture constraint: The runtime uses only the Python standard library."],
    11: ["Agent checkpoint: Main reviews the bounded diff before independent verification."],
    12: [
        "Read context: AGENTS.md, docs, and the existing source and test layout.",
        "Allowed writes: src/greeting.py and tests/test_greeting.py.",
        "Protected paths: docs/PRODUCT.md and unrelated source files.",
    ],
    13: [
        "AC-001 | P0: REQ-P0-001 | Journey: JRN-001 | The greeting command exits zero and prints the confirmed greeting.",
        "Completion evidence: python -m unittest discover -s tests -v.",
    ],
    14: [
        "First verifiable slice: Create one observable greeting command | P0: REQ-P0-001 | Journey: JRN-001 | Acceptance: AC-001",
        "Dependency: The repository has a runnable Python interpreter.",
        "Risk: The command path may conflict with existing project authority.",
    ],
}


class DefinitionTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(list(args))
        return subprocess.CompletedProcess(list(args), returncode, stdout.getvalue(), stderr.getvalue())

    def init(self, root: Path) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "init",
            "--root",
            str(root),
            "--name",
            "Sample Project",
            "--summary",
            "A sample project.",
            "--skip-check",
        )

    def define(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return self.run_cli("define", "--root", str(root), *extra)

    def run_harness(self, root: Path, *args: str, isolated: bool = False) -> subprocess.CompletedProcess[str]:
        command = [sys.executable]
        if isolated:
            command.append("-I")
        command.extend((str(root / "dev" / "harness.py"), *args))
        return subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)

    def load_runtime_module(self, root: Path):
        module_name = f"definition_harness_{root.name.replace('-', '_')}"
        spec = importlib.util.spec_from_file_location(module_name, root / "dev/harness.py")
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        self.addCleanup(sys.modules.pop, module_name, None)
        return module

    def run_define_wrapper(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHON"] = sys.executable
        return subprocess.run(
            [str(root / "dev" / "define"), *args],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def draft_text(self, confirmed_count: int = 14) -> str:
        lines = [
            "---",
            "kind: project-definition-draft",
            "format: 1",
            "created: 2026-08-29",
            "updated: 2026-08-29",
            'progress: "0/14"',
            'next: "1. Project Identity"',
            'continuation: "Resume from persisted evidence."',
            "---",
            "",
            "# Project Definition Draft",
            "",
            "Human and Main Agent evidence only.",
        ]
        for number, title in enumerate(SECTIONS, start=1):
            is_confirmed = number <= confirmed_count
            lines.extend(("", f"## {number}. {title}", "", "### Confirmed", ""))
            if is_confirmed:
                lines.extend(f"- [confirmed] {item}" for item in CONFIRMED[number])
            else:
                lines.append("- None.")
            lines.extend(("", "### Proposed", ""))
            if is_confirmed and number == 4:
                lines.append("- [proposed] A graphical dashboard may be explored after the first slice.")
            else:
                lines.append("- None.")
            lines.extend(("", "### Open", ""))
            if not is_confirmed:
                lines.append(f"- [blocking] Confirm section {number} evidence.")
            elif number == 10:
                lines.append("- [non-blocking] Evaluate optional packaging after the first slice.")
            else:
                lines.append("- None.")
            lines.extend(("", "### Sources", "", "- [source] Human confirmation recorded in this draft."))
        return "\n".join(lines).rstrip() + "\n"

    def write_draft(self, root: Path, text: str | None = None) -> Path:
        path = root / "docs" / "product-specs" / "project-definition.draft.md"
        path.write_text(text if text is not None else self.draft_text(), encoding="utf-8")
        return path

    def replace_evidence(self, text: str, section_number: int, heading: str, lines: list[str]) -> str:
        title = re.escape(SECTIONS[section_number - 1])
        section_pattern = re.compile(
            rf"(^## {section_number}\. {title}\s*$)(.*?)(?=^## |\Z)",
            re.MULTILINE | re.DOTALL,
        )
        section_match = section_pattern.search(text)
        self.assertIsNotNone(section_match)
        assert section_match is not None
        section_block = section_match.group(0)
        evidence_pattern = re.compile(
            rf"(^### {re.escape(heading)}\s*$)(.*?)(?=^### |\Z)",
            re.MULTILINE | re.DOTALL,
        )
        replacement = rf"\1\n\n" + "\n".join(lines) + "\n\n"
        updated_block, count = evidence_pattern.subn(replacement, section_block, count=1)
        self.assertEqual(count, 1)
        return text[: section_match.start()] + updated_block.rstrip() + "\n\n" + text[section_match.end() :].lstrip("\n")

    def snapshot(self, root: Path) -> dict[Path, bytes]:
        return {
            path.relative_to(root): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file()
        }

    def test_definition_start_is_explicit_and_dry_run_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            initialized = base / "initialized"
            initialized.mkdir()
            init = self.init(initialized)
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            self.assertFalse((initialized / "docs/product-specs/project-definition.draft.md").exists())
            self.assertTrue((initialized / "dev/define").exists())
            config_before = (initialized / "dev/harness.toml").read_bytes()
            upgrade = self.run_cli("upgrade", "--root", str(initialized), "--skip-check")
            self.assertEqual(upgrade.returncode, 0, upgrade.stdout + upgrade.stderr)
            self.assertFalse((initialized / "docs/product-specs/project-definition.draft.md").exists())
            self.assertEqual((initialized / "dev/harness.toml").read_bytes(), config_before)

            dry_root = base / "dry"
            dry = self.define(dry_root, "--dry-run")
            self.assertEqual(dry.returncode, 0, dry.stdout + dry.stderr)
            self.assertFalse(dry_root.exists())

            explicit = base / "explicit"
            started = self.define(explicit)
            self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
            self.assertTrue((explicit / "AGENTS.md").exists())
            self.assertTrue((explicit / "dev/harness.py").exists())
            self.assertTrue((explicit / "dev/define").exists())
            self.assertTrue((explicit / "docs/product-specs/project-definition.draft.md").exists())
            index = (explicit / "docs/product-specs/index.md").read_text(encoding="utf-8")
            self.assertNotIn("project-definition.draft.md", index)
            docs_check = self.run_harness(explicit, "docs-check")
            self.assertEqual(docs_check.returncode, 0, docs_check.stdout + docs_check.stderr)

    def test_definition_start_refreshes_older_managed_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            initialized = self.init(root)
            self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
            config = root / "dev/harness.toml"
            config.write_text(config.read_text(encoding="utf-8") + "\n# project-owned-byte-sentinel\n", encoding="utf-8")
            config_before = config.read_bytes()
            runtime = root / "dev/harness.py"
            runtime.write_text(
                "#!/usr/bin/env python3\n"
                "# reporivet:managed version=0.0.0\n"
                "raise SystemExit(73)\n",
                encoding="utf-8",
            )
            wrapper = root / "dev/define"
            wrapper.unlink()

            started = self.define(root)
            self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
            self.assertNotIn("raise SystemExit(73)", runtime.read_text(encoding="utf-8"))
            self.assertIn("reporivet:managed", wrapper.read_text(encoding="utf-8"))
            self.assertEqual(config.read_bytes(), config_before)
            status = self.run_define_wrapper(root, "status")
            self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
            self.assertIn("Progress: 0/14 sections confirmed", status.stdout)

    def test_definition_start_rejects_incidental_managed_markers_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            for relative in ("dev/define", "dev/harness.py", "dev/docs-index"):
                with self.subTest(relative=relative):
                    root = base / relative.replace("/", "-")
                    path = root / relative
                    path.parent.mkdir(parents=True)
                    content = (
                        "#!/usr/bin/env sh\n"
                        "# mention reporivet:managed, but this command is project-owned\n"
                        "printf '%s\\n' project-owned\n"
                    )
                    path.write_text(content, encoding="utf-8")
                    before = self.snapshot(root)

                    result = self.define(root)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("refusing to replace existing project-owned command paths", result.stderr)
                    self.assertEqual(self.snapshot(root), before)
                    self.assertEqual(path.read_text(encoding="utf-8"), content)
                    self.assertFalse((root / "AGENTS.md").exists())

    @unittest.skipIf(os.name == "nt", "symlink ownership checks require POSIX semantics")
    def test_init_and_definition_refuse_symlinked_roots_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            outside = base / "outside"
            outside.mkdir()

            for command, operation in (("init", self.init), ("define", self.define)):
                with self.subTest(command=command, path="root"):
                    target = outside / f"{command}-root"
                    target.mkdir()
                    root_link = base / f"{command}-root-link"
                    root_link.symlink_to(target, target_is_directory=True)

                    result = operation(root_link)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("symlinked project root or parent", result.stderr)
                    self.assertTrue(root_link.is_symlink())
                    self.assertEqual(list(target.iterdir()), [])

                with self.subTest(command=command, path="parent"):
                    parent_target = outside / f"{command}-parent"
                    parent_target.mkdir()
                    parent_link = base / f"{command}-parent-link"
                    parent_link.symlink_to(parent_target, target_is_directory=True)
                    requested_root = parent_link / "project"

                    result = operation(requested_root)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("symlinked project root or parent", result.stderr)
                    self.assertTrue(parent_link.is_symlink())
                    self.assertFalse((parent_target / "project").exists())

    @unittest.skipIf(os.name == "nt", "symlink ownership checks require POSIX semantics")
    def test_definition_start_refuses_symlink_write_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            outside = base / "outside"
            outside.mkdir()

            broken_root = base / "broken"
            (broken_root / "dev").mkdir(parents=True)
            external_command = outside / "created-command"
            broken_link = broken_root / "dev/define"
            broken_link.symlink_to(external_command)
            broken = self.define(broken_root)
            self.assertNotEqual(broken.returncode, 0)
            self.assertIn("symlink", broken.stderr)
            self.assertTrue(broken_link.is_symlink())
            self.assertFalse(external_command.exists())
            self.assertFalse((broken_root / "AGENTS.md").exists())

            managed_root = base / "managed"
            (managed_root / "dev").mkdir(parents=True)
            external_runtime = outside / "managed-runtime.py"
            external_runtime.write_text(
                "#!/usr/bin/env python3\n# reporivet:managed version=0.0.0\nraise SystemExit(73)\n",
                encoding="utf-8",
            )
            runtime_before = external_runtime.read_bytes()
            runtime_link = managed_root / "dev/harness.py"
            runtime_link.symlink_to(external_runtime)
            managed = self.define(managed_root)
            self.assertNotEqual(managed.returncode, 0)
            self.assertIn("symlink", managed.stderr)
            self.assertEqual(external_runtime.read_bytes(), runtime_before)
            self.assertFalse((managed_root / "AGENTS.md").exists())

            parent_root = base / "parent"
            parent_root.mkdir()
            external_dev = outside / "dev"
            external_dev.mkdir()
            (parent_root / "dev").symlink_to(external_dev, target_is_directory=True)
            parent = self.define(parent_root)
            self.assertNotEqual(parent.returncode, 0)
            self.assertIn("symlink", parent.stderr)
            self.assertEqual(list(external_dev.iterdir()), [])
            self.assertFalse((parent_root / "AGENTS.md").exists())

    def test_repeated_definition_start_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            first = self.define(root)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            before = self.snapshot(root)
            second = self.define(root)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(self.snapshot(root), before)

    def test_status_resumes_after_confirmed_sections_without_repeating_them_as_next(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            started = self.define(root)
            self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
            draft = self.write_draft(root, self.draft_text(confirmed_count=2))
            status = self.run_define_wrapper(root, "status")
            self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
            self.assertIn("Progress: 2/14 sections confirmed", status.stdout)
            self.assertEqual(status.stdout.count("1. Project Identity"), 1)
            self.assertEqual(status.stdout.count("2. Problem and Current Alternative"), 1)
            self.assertIn("Next unresolved section: 3. Target Users", status.stdout)
            self.assertNotIn("Next unresolved section: 1.", status.stdout)
            self.assertNotIn("Next unresolved section: 2.", status.stdout)
            persisted = draft.read_text(encoding="utf-8")
            self.assertIn('progress: "2/14"', persisted)
            self.assertIn('next: "3. Target Users"', persisted)
            second = self.run_define_wrapper(root, "status")
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(second.stdout, status.stdout)
            self.assertEqual(draft.read_text(encoding="utf-8"), persisted)

    def test_validate_accepts_complete_structural_definition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            self.write_draft(root)
            valid = self.run_harness(root, "define", "validate", isolated=True)
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            self.assertIn("14 confirmed sections", valid.stdout)

    def test_validate_rejects_section_heading_and_status_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            cases = {
                "missing section": self.draft_text().replace(
                    "\n## 14. First Milestone, Dependencies, and Risks", "\n## 15. First Milestone, Dependencies, and Risks"
                ),
                "duplicate section": self.draft_text()
                + "\n## 1. Project Identity\n\n### Confirmed\n\n- [confirmed] Duplicate.\n\n### Proposed\n\n- None.\n\n### Open\n\n- None.\n\n### Sources\n\n- None.\n",
                "out of order": self.draft_text()
                .replace("## 1. Project Identity", "## X. Project Identity", 1)
                .replace("## 2. Problem and Current Alternative", "## 1. Project Identity", 1)
                .replace("## X. Project Identity", "## 2. Problem and Current Alternative", 1),
                "unknown evidence heading": self.draft_text().replace("### Proposed", "### Accepted", 1),
                "unknown evidence status": self.draft_text().replace("[confirmed] Project name", "[accepted] Project name", 1),
                "duplicate none sentinel": self.draft_text().replace("- None.", "- None.\n- None.", 1),
            }
            for name, text in cases.items():
                with self.subTest(name=name):
                    self.write_draft(root, text)
                    result = self.run_harness(root, "define", "validate")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("ERROR:", result.stderr)

    def test_validate_rejects_malformed_duplicate_and_contradictory_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            malformed = self.draft_text().replace("REQ-P0-001", "REQ-P0-one")
            duplicate_line = CONFIRMED[5][0]
            duplicate = self.replace_evidence(
                self.draft_text(),
                5,
                "Confirmed",
                [f"- [confirmed] {duplicate_line}", f"- [confirmed] {duplicate_line}"],
            )
            contradictory = self.replace_evidence(
                self.draft_text(),
                5,
                "Proposed",
                [
                    "- [proposed] REQ-P0-001 | Journey: JRN-001 | Acceptance: AC-001 | Deliver a contradictory capability."
                ],
            )
            cases = {
                "malformed stable identifier": (malformed, "malformed stable identifier"),
                "duplicate identifier": (duplicate, "duplicate identifier"),
                "contradictory duplicate evidence": (contradictory, "contradictory duplicate evidence"),
            }
            for name, (text, expected) in cases.items():
                with self.subTest(name=name):
                    self.write_draft(root, text)
                    result = self.run_harness(root, "define", "validate")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_validate_rejects_blocking_open_and_proposal_as_confirmed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            blocked = self.replace_evidence(
                self.draft_text(), 1, "Open", ["- [blocking] Resolve the project identity authority."]
            )
            proposal_duplicate = self.replace_evidence(
                self.draft_text(),
                4,
                "Proposed",
                [f"- [proposed] {CONFIRMED[4][0]}"],
            )
            for name, text, expected in (
                ("blocking Open", blocked, "blocking Open item"),
                ("proposal as confirmed", proposal_duplicate, "proposal is also represented as confirmed"),
            ):
                with self.subTest(name=name):
                    self.write_draft(root, text)
                    result = self.run_harness(root, "define", "validate")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_validate_rejects_placeholders_and_broken_trace_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            cases = {
                "placeholder": (
                    self.draft_text().replace(
                        "Project purpose: Provide one repository-native sample capability.",
                        "Project purpose: TBD",
                    ),
                    "unresolved TODO or TBD",
                ),
                "template token": (
                    self.draft_text().replace(
                        "Project purpose: Provide one repository-native sample capability.",
                        "Project purpose: {{VALUE}}",
                    ),
                    "unresolved template token",
                ),
                "P0 unknown journey": (
                    self.draft_text().replace(
                        "REQ-P0-001 | Journey: JRN-001",
                        "REQ-P0-001 | Journey: JRN-999",
                        1,
                    ),
                    "references unknown journey JRN-999",
                ),
                "AC unknown P0": (
                    self.draft_text().replace(
                        "AC-001 | P0: REQ-P0-001",
                        "AC-001 | P0: REQ-P0-999",
                        1,
                    ),
                    "references unknown P0 REQ-P0-999",
                ),
                "duplicate first-slice journey field": (
                    self.draft_text().replace(
                        CONFIRMED[14][0],
                        CONFIRMED[14][0].replace(
                            "| Acceptance: AC-001",
                            "| Journey: JRN-999 | Acceptance: AC-001",
                        ),
                    ),
                    "duplicate 'Journey:' link field",
                ),
                "reordered P0 declaration fields": (
                    self.draft_text().replace(
                        CONFIRMED[5][0],
                        "REQ-P0-001 | Acceptance: AC-001 | Journey: JRN-001 | Provide one observable greeting command.",
                    ),
                    "declaration must use",
                ),
                "space-separated journey links": (
                    self.draft_text().replace(
                        "REQ-P0-001 | Journey: JRN-001",
                        "REQ-P0-001 | Journey: JRN-001 JRN-002",
                        1,
                    ),
                    "malformed 'Journey:' links; use comma-separated",
                ),
                "reordered first-slice fields": (
                    self.draft_text().replace(
                        CONFIRMED[14][0],
                        "First verifiable slice: Create one observable greeting command | Journey: JRN-001 | P0: REQ-P0-001 | Acceptance: AC-001",
                    ),
                    "first slice must use",
                ),
            }
            for name, (text, expected) in cases.items():
                with self.subTest(name=name):
                    self.write_draft(root, text)
                    result = self.run_harness(root, "define", "validate")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_validate_rejects_conflicting_singular_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            conflicting_confirmed = self.replace_evidence(
                self.draft_text(),
                1,
                "Confirmed",
                [
                    f"- [confirmed] {CONFIRMED[1][0]}",
                    "- [confirmed] Project name: Conflicting Project",
                    f"- [confirmed] {CONFIRMED[1][1]}",
                ],
            )
            conflicting_proposal = self.replace_evidence(
                self.draft_text(),
                4,
                "Proposed",
                ["- [proposed] Solution boundary: Deliver an unrelated alternative instead."],
            )
            duplicate_inline_label = self.replace_evidence(
                self.draft_text(),
                1,
                "Confirmed",
                [
                    "- [confirmed] Project name: Sample Project | Project name: Other Project",
                    f"- [confirmed] {CONFIRMED[1][1]}",
                ],
            )
            cases = (
                (
                    "multiple confirmed scalar values",
                    conflicting_confirmed,
                    "multiple confirmed values for singular project name",
                ),
                (
                    "proposed scalar alternative",
                    conflicting_proposal,
                    "proposed alternative conflicts with confirmed singular solution boundary",
                ),
                (
                    "duplicate scalar label in one item",
                    duplicate_inline_label,
                    "duplicate singular 'Project name:' label",
                ),
            )
            for name, text, expected in cases:
                with self.subTest(name=name):
                    self.write_draft(root, text)
                    result = self.run_harness(root, "define", "validate")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_validate_rejects_non_concrete_values_and_empty_slice_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            cases = {
                "punctuated none": (
                    self.draft_text().replace(
                        "Problem: Maintainers cannot verify the first project behavior from repository evidence.",
                        "Problem: None.",
                    ),
                    "missing concrete confirmed problem",
                ),
                "punctuated unknown": (
                    self.draft_text().replace(
                        "Project name: Sample Project",
                        "Project name: Unknown.",
                    ),
                    "missing concrete confirmed project name",
                ),
                "Markdown-wrapped unknown": (
                    self.draft_text().replace(
                        "Project name: Sample Project",
                        "Project name: **Unknown.**",
                    ),
                    "missing concrete confirmed project name",
                ),
                "Unicode ellipsis unknown": (
                    self.draft_text().replace(
                        "Project name: Sample Project",
                        "Project name: Unknown…",
                    ),
                    "missing concrete confirmed project name",
                ),
                "Unicode full-stop unknown": (
                    self.draft_text().replace(
                        "Project name: Sample Project",
                        "Project name: Unknown。",
                    ),
                    "missing concrete confirmed project name",
                ),
                "punctuated not established": (
                    self.draft_text().replace(
                        "Solution boundary: Deliver only the confirmed first slice.",
                        "Solution boundary: Not established.",
                    ),
                    "missing concrete confirmed solution boundary",
                ),
                "generic punctuated placeholder": (
                    self.draft_text().replace(
                        "Reliability constraint: The first slice is deterministic and local-only.",
                        "Unknown.",
                    ),
                    "confirmed evidence must contain a concrete value",
                ),
                "labeled generic punctuated placeholder": (
                    self.draft_text().replace(
                        "Reliability constraint: The first slice is deterministic and local-only.",
                        "Reliability constraint: Unknown.",
                    ),
                    "confirmed evidence must contain a concrete value",
                ),
                "empty first-slice description": (
                    self.draft_text().replace(
                        CONFIRMED[14][0],
                        "First verifiable slice: | P0: REQ-P0-001 | Journey: JRN-001 | Acceptance: AC-001",
                    ),
                    "first slice is missing a concrete description",
                ),
            }
            for name, (text, expected) in cases.items():
                with self.subTest(name=name):
                    self.write_draft(root, text)
                    result = self.run_harness(root, "define", "validate")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

            self.write_draft(
                root,
                self.draft_text().replace(
                    "Project name: Sample Project",
                    "Project name: **Unknown.**",
                ),
            )
            final = self.run_harness(root, "define", "finalize")
            self.assertNotEqual(final.returncode, 0)
            self.assertFalse(
                (root / "docs/product-specs/SPEC-PROJECT-001-product-definition.md").exists()
            )
            self.assertEqual(
                list((root / "docs/exec-plans/active").glob("*.md")),
                [],
            )

    def test_validate_rejects_declaration_shaped_mistyped_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            identifiers = (
                "REQ-P00-001",
                "REQ-P1-001",
                "REQ/P0/002",
                "REQ:P0:002",
                "REQ P0 002",
                "REQ／P0／002",
                "JRN/002",
                "AC/002",
            )
            for identifier in identifiers:
                with self.subTest(identifier=identifier):
                    text = self.replace_evidence(
                        self.draft_text(),
                        5,
                        "Proposed",
                        [
                            f"- [proposed] {identifier} | A malformed proposed declaration."
                        ],
                    )
                    self.write_draft(root, text)
                    result = self.run_harness(root, "define", "validate")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        f"malformed stable declaration identifier '{identifier}'",
                        result.stderr,
                    )

            ordinary_items = (
                "AC adapter compatibility remains optional | Only hardware deployment contexts would use it.",
                "AC/DC compatibility remains optional | This is ordinary prose, not an ID declaration.",
                "JRN files remain repository-local notes | This is ordinary prose, not an ID declaration.",
                "REQ review remains human-owned | This is ordinary prose, not an ID declaration.",
            )
            for item in ordinary_items:
                with self.subTest(ordinary=item):
                    text = self.replace_evidence(
                        self.draft_text(),
                        10,
                        "Proposed",
                        [f"- [proposed] {item}"],
                    )
                    self.write_draft(root, text)
                    result = self.run_harness(root, "define", "validate")
                    self.assertEqual(
                        result.returncode,
                        0,
                        result.stdout + result.stderr,
                    )

            final_text = self.replace_evidence(
                self.draft_text(),
                10,
                "Proposed",
                [f"- [proposed] {ordinary_items[0]}"],
            )
            self.write_draft(root, final_text)
            final = self.run_harness(root, "define", "finalize")
            self.assertEqual(final.returncode, 0, final.stdout + final.stderr)
            spec = root / "docs/product-specs/SPEC-PROJECT-001-product-definition.md"
            self.assertIn(ordinary_items[0], spec.read_text(encoding="utf-8"))

    def test_validate_rejects_placeholder_non_blocking_open_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            concrete = "[non-blocking] Evaluate optional packaging after the first slice."
            for placeholder in (
                "Unknown.",
                "None.",
                "To be determined.",
                "**Unknown.**",
                "Unknown…",
            ):
                with self.subTest(placeholder=placeholder):
                    text = self.draft_text().replace(concrete, f"[non-blocking] {placeholder}")
                    self.write_draft(root, text)
                    result = self.run_harness(root, "define", "validate")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        "non-blocking Open item must contain a concrete unresolved question or follow-up",
                        result.stderr,
                    )

            self.write_draft(root)
            valid = self.run_harness(root, "define", "validate")
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

    def test_validate_requires_ac_to_p0_reciprocity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            text = self.draft_text().replace(
                CONFIRMED[5][0],
                "REQ-P0-001 | Journey: JRN-001 | Acceptance: AC-002 | Provide one observable greeting command.",
            )
            text = self.replace_evidence(
                text,
                13,
                "Confirmed",
                [
                    f"- [confirmed] {CONFIRMED[13][0]}",
                    "- [confirmed] AC-002 | P0: REQ-P0-001 | Journey: JRN-001 | The alternate criterion observes the greeting command.",
                    f"- [confirmed] {CONFIRMED[13][1]}",
                ],
            )
            text = text.replace("Acceptance: AC-001", "Acceptance: AC-002", 1)
            self.write_draft(root, text)

            result = self.run_harness(root, "define", "validate")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("AC-001 and REQ-P0-001 links are not reciprocal", result.stderr)

    def test_validate_rejects_cross_section_and_separated_scalar_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            cross_section = self.replace_evidence(
                self.draft_text(),
                2,
                "Confirmed",
                [
                    f"- [confirmed] {CONFIRMED[2][0]}",
                    f"- [confirmed] {CONFIRMED[2][1]}",
                    "- [confirmed] Project name: Cross-section alternative",
                ],
            )
            cases = (
                (
                    "cross-section scalar",
                    cross_section,
                    "'Project name:' evidence belongs in section 1",
                ),
                (
                    "semicolon-separated duplicate",
                    self.draft_text().replace(
                        "Project name: Sample Project",
                        "Project name: Sample Project; Project name: Other Project",
                    ),
                    "duplicate singular 'Project name:' label",
                ),
                (
                    "comma-separated duplicate",
                    self.draft_text().replace(
                        "Project name: Sample Project",
                        "Project name: Sample Project, Project name: Other Project",
                    ),
                    "duplicate singular 'Project name:' label",
                ),
            )
            for name, text, expected in cases:
                with self.subTest(name=name):
                    self.write_draft(root, text)
                    result = self.run_harness(root, "define", "validate")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_validate_rejects_unrelated_first_slice_trace_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            text = self.replace_evidence(
                self.draft_text(),
                5,
                "Confirmed",
                [
                    f"- [confirmed] {CONFIRMED[5][0]}",
                    "- [confirmed] REQ-P0-002 | Journey: JRN-002 | Acceptance: AC-002 | Provide a second observable command.",
                ],
            )
            text = self.replace_evidence(
                text,
                6,
                "Confirmed",
                [
                    f"- [confirmed] {CONFIRMED[6][0]}",
                    "- [confirmed] JRN-002 | A maintainer runs the second command and observes its output.",
                ],
            )
            text = self.replace_evidence(
                text,
                13,
                "Confirmed",
                [
                    f"- [confirmed] {CONFIRMED[13][0]}",
                    "- [confirmed] AC-002 | P0: REQ-P0-002 | Journey: JRN-002 | The second command exits zero and prints its output.",
                    f"- [confirmed] {CONFIRMED[13][1]}",
                ],
            )
            text = text.replace(
                CONFIRMED[14][0],
                "First verifiable slice: Create one observable greeting command | P0: REQ-P0-001 | Journey: JRN-002 | Acceptance: AC-002",
            )
            self.write_draft(root, text)

            result = self.run_harness(root, "define", "validate")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "first slice P0 REQ-P0-001 does not reference selected journey JRN-002",
                result.stderr,
            )
            self.assertIn(
                "first slice P0 REQ-P0-001 does not reference selected acceptance AC-002",
                result.stderr,
            )
            self.assertIn(
                "first slice acceptance AC-002 does not reference selected P0 REQ-P0-001",
                result.stderr,
            )

    def test_validate_requires_concrete_definition_and_handoff_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            required_labels = (
                ("Project name:", "missing concrete confirmed project name"),
                ("Project purpose:", "missing concrete confirmed project purpose"),
                ("Problem:", "missing concrete confirmed problem"),
                ("Current alternative:", "missing concrete confirmed current alternative"),
                ("Primary user:", "missing concrete confirmed primary user"),
                ("Value proposition:", "missing concrete confirmed value proposition"),
                ("Solution boundary:", "missing concrete confirmed solution boundary"),
                ("In scope:", "missing concrete confirmed in-scope boundary"),
                ("Out of scope:", "missing concrete confirmed out-of-scope boundary"),
                ("Success signal:", "missing concrete confirmed success signal"),
                ("Agent checkpoint:", "missing concrete confirmed agent checkpoint"),
                ("Completion evidence:", "missing concrete confirmed completion evidence"),
                ("First verifiable slice:", "missing concrete confirmed first verifiable slice"),
                ("Dependency:", "missing concrete confirmed first-slice dependency"),
                ("Risk:", "missing concrete confirmed first-slice risk"),
            )
            for label, expected in required_labels:
                with self.subTest(label=label):
                    self.write_draft(root, self.draft_text().replace(label, "Unlabeled evidence:", 1))
                    result = self.run_harness(root, "define", "validate")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_finalize_creates_spec_catalog_and_one_traceable_first_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            self.write_draft(root)
            product = root / "docs/PRODUCT.md"
            product_before = product.read_bytes()
            final = self.run_define_wrapper(root, "finalize")
            self.assertEqual(final.returncode, 0, final.stdout + final.stderr)
            spec = root / "docs/product-specs/SPEC-PROJECT-001-product-definition.md"
            self.assertTrue(spec.exists())
            self.assertEqual(product.read_bytes(), product_before)
            self.assertTrue((root / "docs/product-specs/project-definition.draft.md").exists())
            plans = list((root / "docs/exec-plans/active").glob("*.md"))
            self.assertEqual(len(plans), 1)
            spec_text = spec.read_text(encoding="utf-8")
            self.assertIn("### Confirmed", spec_text)
            self.assertIn("[confirmed] Problem:", spec_text)
            self.assertIn("### Proposed", spec_text)
            self.assertIn("[proposed] A graphical dashboard", spec_text)
            self.assertIn("### Open", spec_text)
            self.assertIn("[non-blocking] Evaluate optional packaging", spec_text)
            plan_text = plans[0].read_text(encoding="utf-8")
            self.assertIn("## Product Trace", plan_text)
            self.assertIn("`SPEC-PROJECT-001`", plan_text)
            self.assertIn("`JRN-001`", plan_text)
            self.assertIn("`REQ-P0-001`", plan_text)
            self.assertIn("`AC-001`", plan_text)
            task_acceptance = re.findall(r"#### Acceptance\s+\n\s*(.*?)\n", plan_text)
            self.assertEqual(task_acceptance, ["AC-001", "AC-001"])
            self.assertIn("Task type\n\nimplementation", plan_text)
            self.assertIn("Task type\n\nverification", plan_text)
            plan_id_match = re.search(r"^id: (PLAN-[0-9-]+)$", plan_text, re.MULTILINE)
            self.assertIsNotNone(plan_id_match)
            assert plan_id_match is not None
            for task_id in ("T1", "T2"):
                task = self.run_harness(root, "task", plan_id_match.group(1), task_id)
                self.assertEqual(task.returncode, 0, task.stdout + task.stderr)
                self.assertIn("#### Acceptance", task.stdout)
                self.assertIn("AC-001", task.stdout)
            index = (root / "docs/product-specs/index.md").read_text(encoding="utf-8")
            self.assertIn("SPEC-PROJECT-001", index)
            self.assertNotIn("project-definition.draft.md", index)
            catalog_check = self.run_harness(root, "docs-index", "--check")
            self.assertEqual(catalog_check.returncode, 0, catalog_check.stdout + catalog_check.stderr)
            plan_check = self.run_harness(root, "plan-check")
            self.assertEqual(plan_check.returncode, 0, plan_check.stdout + plan_check.stderr)

            second = self.run_harness(root, "define", "finalize")
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("refusing to overwrite existing final specification", second.stderr)
            self.assertEqual(len(list((root / "docs/exec-plans/active").glob("*.md"))), 1)

    def test_finalize_refuses_existing_target_plan_without_writing_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            self.write_draft(root)
            existing = root / "docs/exec-plans/active/PLAN-2026-0042-existing-first-slice.md"
            existing.write_text(
                "---\nid: PLAN-2026-0042\nkind: exec-plan\nstatus: proposed\nproduct_spec: SPEC-PROJECT-001\n---\n\n# Existing\n",
                encoding="utf-8",
            )
            before = existing.read_bytes()
            result = self.run_harness(root, "define", "finalize")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("existing target plan", result.stderr)
            self.assertFalse((root / "docs/product-specs/SPEC-PROJECT-001-product-definition.md").exists())
            self.assertEqual(existing.read_bytes(), before)
            self.assertEqual(list((root / "docs/exec-plans/active").glob("*.md")), [existing])

    def test_finalize_rolls_back_created_files_and_catalog_changes_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            self.write_draft(root)
            docs_readme = root / "docs/README.md"
            product_index = root / "docs/product-specs/index.md"
            product_index.write_text("# Broken catalog without managed markers\n", encoding="utf-8")
            docs_before = docs_readme.read_bytes()
            index_before = product_index.read_bytes()
            result = self.run_harness(root, "define", "finalize")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "docs/product-specs/SPEC-PROJECT-001-product-definition.md").exists())
            self.assertEqual(list((root / "docs/exec-plans/active").glob("*.md")), [])
            self.assertEqual(docs_readme.read_bytes(), docs_before)
            self.assertEqual(product_index.read_bytes(), index_before)

    def test_finalize_rollback_preserves_concurrent_catalog_edit_and_reports_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            self.write_draft(root)
            module = self.load_runtime_module(root)
            original_docs_index = module.command_docs_index
            catalog = root / "docs/README.md"
            user_bytes = b"concurrent catalog edit\n"

            def edit_catalog_after_index(args):
                original_docs_index(args)
                catalog.write_bytes(user_bytes)
                raise module.HarnessError("forced failure after catalog edit")

            module.command_docs_index = edit_catalog_after_index
            with self.assertRaisesRegex(module.HarnessError, "rollback incomplete") as caught:
                module.command_define_finalize(module.argparse.Namespace())

            self.assertEqual(catalog.read_bytes(), user_bytes)
            self.assertIn("docs/README.md", str(caught.exception))
            self.assertFalse((root / "docs/product-specs/SPEC-PROJECT-001-product-definition.md").exists())
            self.assertEqual(list((root / "docs/exec-plans/active").glob("*.md")), [])

    def test_finalize_rollback_preserves_concurrent_spec_or_plan_edit(self) -> None:
        for target_kind in ("spec", "plan"):
            with self.subTest(target_kind=target_kind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                self.assertEqual(self.define(root).returncode, 0)
                self.write_draft(root)
                module = self.load_runtime_module(root)
                user_bytes = f"concurrent {target_kind} edit\n".encode("utf-8")
                edited_path: Path | None = None

                def edit_created_path(_args):
                    nonlocal edited_path
                    if target_kind == "spec":
                        edited_path = root / "docs/product-specs/SPEC-PROJECT-001-product-definition.md"
                    else:
                        plans = list((root / "docs/exec-plans/active").glob("*.md"))
                        self.assertEqual(len(plans), 1)
                        edited_path = plans[0]
                    edited_path.write_bytes(user_bytes)
                    raise module.HarnessError(f"forced {target_kind} edit")

                module.command_docs_index = edit_created_path
                with self.assertRaisesRegex(module.HarnessError, "rollback incomplete") as caught:
                    module.command_define_finalize(module.argparse.Namespace())

                self.assertIsNotNone(edited_path)
                assert edited_path is not None
                self.assertEqual(edited_path.read_bytes(), user_bytes)
                self.assertIn(edited_path.relative_to(root).as_posix(), str(caught.exception))
                if target_kind == "spec":
                    self.assertEqual(list((root / "docs/exec-plans/active").glob("*.md")), [])
                else:
                    self.assertFalse(
                        (root / "docs/product-specs/SPEC-PROJECT-001-product-definition.md").exists()
                    )

    @unittest.skipIf(os.name == "nt", "symlink ownership checks require POSIX semantics")
    def test_repository_definition_commands_refuse_symlink_paths_without_external_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            outside = base / "outside"
            outside.mkdir()

            draft_root = base / "draft"
            self.assertEqual(self.define(draft_root).returncode, 0)
            external_draft = outside / "definition.md"
            external_draft.write_text(self.draft_text(confirmed_count=2), encoding="utf-8")
            external_draft_before = external_draft.read_bytes()
            draft = draft_root / "docs/product-specs/project-definition.draft.md"
            draft.unlink()
            draft.symlink_to(external_draft)
            status = self.run_harness(draft_root, "define", "status")
            self.assertNotEqual(status.returncode, 0)
            self.assertIn("repository symlink", status.stderr)
            self.assertEqual(external_draft.read_bytes(), external_draft_before)

            spec_root = base / "spec"
            self.assertEqual(self.define(spec_root).returncode, 0)
            self.write_draft(spec_root)
            external_spec = outside / "created-spec.md"
            spec_link = spec_root / "docs/product-specs/SPEC-PROJECT-001-product-definition.md"
            spec_link.symlink_to(external_spec)
            spec_result = self.run_harness(spec_root, "define", "finalize")
            self.assertNotEqual(spec_result.returncode, 0)
            self.assertIn("repository symlink", spec_result.stderr)
            self.assertTrue(spec_link.is_symlink())
            self.assertFalse(external_spec.exists())
            self.assertEqual(list((spec_root / "docs/exec-plans/active").glob("*.md")), [])

            plan_root = base / "plan"
            self.assertEqual(self.define(plan_root).returncode, 0)
            self.write_draft(plan_root)
            external_plans = outside / "plans"
            external_plans.mkdir()
            active_plans = plan_root / "docs/exec-plans/active"
            (active_plans / ".gitkeep").unlink()
            active_plans.rmdir()
            active_plans.symlink_to(external_plans, target_is_directory=True)
            plan_result = self.run_harness(plan_root, "define", "finalize")
            self.assertNotEqual(plan_result.returncode, 0)
            self.assertIn("repository symlink", plan_result.stderr)
            self.assertFalse((plan_root / "docs/product-specs/SPEC-PROJECT-001-product-definition.md").exists())
            self.assertEqual(list(external_plans.iterdir()), [])

            catalog_root = base / "catalog"
            self.assertEqual(self.define(catalog_root).returncode, 0)
            self.write_draft(catalog_root)
            external_catalog = outside / "catalog.md"
            external_catalog.write_text("external catalog sentinel\n", encoding="utf-8")
            catalog_before = external_catalog.read_bytes()
            catalog = catalog_root / "docs/README.md"
            catalog.unlink()
            catalog.symlink_to(external_catalog)
            catalog_result = self.run_harness(catalog_root, "define", "finalize")
            self.assertNotEqual(catalog_result.returncode, 0)
            self.assertIn("repository symlink", catalog_result.stderr)
            self.assertEqual(external_catalog.read_bytes(), catalog_before)
            self.assertFalse((catalog_root / "docs/product-specs/SPEC-PROJECT-001-product-definition.md").exists())
            self.assertEqual(list((catalog_root / "docs/exec-plans/active").glob("*.md")), [])

    def test_generated_runtime_is_package_independent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self.assertEqual(self.define(root).returncode, 0)
            self.write_draft(root, self.draft_text(confirmed_count=2))
            runtime = (root / "dev/harness.py").read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"^\s*(?:from|import)\s+reporivet\b", runtime, re.MULTILINE))
            isolated = self.run_harness(root, "define", "status", isolated=True)
            self.assertEqual(isolated.returncode, 0, isolated.stdout + isolated.stderr)
            self.assertIn("Next unresolved section: 3. Target Users", isolated.stdout)

    def test_define_wrapper_collision_and_upgrade_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            collision = base / "collision"
            (collision / "dev").mkdir(parents=True)
            unmarked = collision / "dev/define"
            unmarked.write_text("#!/bin/sh\nprintf project-owned\\n\n", encoding="utf-8")
            refused = self.define(collision)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("refusing to replace existing project-owned command paths", refused.stderr)
            self.assertFalse((collision / "AGENTS.md").exists())
            self.assertIn("project-owned", unmarked.read_text(encoding="utf-8"))

            upgrade_root = base / "upgrade"
            upgrade_root.mkdir()
            initialized = self.init(upgrade_root)
            self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
            config = upgrade_root / "dev/harness.toml"
            config.write_text(config.read_text(encoding="utf-8") + "\n# project-owned-byte-sentinel\n", encoding="utf-8")
            config_before = config.read_bytes()
            wrapper = upgrade_root / "dev/define"
            wrapper.unlink()
            upgraded = self.run_cli("upgrade", "--root", str(upgrade_root), "--skip-check")
            self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
            self.assertIn("reporivet:managed", wrapper.read_text(encoding="utf-8"))
            self.assertEqual(config.read_bytes(), config_before)
            self.assertFalse((upgrade_root / "docs/product-specs/project-definition.draft.md").exists())

            project_wrapper = "#!/bin/sh\nprintf preserved-project-command\\n\n"
            wrapper.write_text(project_wrapper, encoding="utf-8")
            preserved = self.run_cli("upgrade", "--root", str(upgrade_root), "--skip-check")
            self.assertEqual(preserved.returncode, 0, preserved.stdout + preserved.stderr)
            self.assertEqual(wrapper.read_text(encoding="utf-8"), project_wrapper)
            self.assertEqual(config.read_bytes(), config_before)


if __name__ == "__main__":
    unittest.main()
