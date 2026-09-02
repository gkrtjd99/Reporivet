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
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet import migration
from reporivet.guided import DEFINITION_DRAFT_PATH, DEFINITION_TOPICS
from reporivet.initializer import InitError, audit_project
from reporivet.procedures import ProcedureSpec, render_procedure_runbook
from reporivet.setup import SetupEnvelope, coordinate_setup


class SetupFlowTests(unittest.TestCase):
    maxDiff = None

    def coordinate(self, root: Path, **overrides: object) -> SetupEnvelope:
        arguments: dict[str, object] = {
            "root": root,
            "answers": None,
            "with_claude_settings": False,
            "dry_run": False,
            "apply": False,
            "approve_preview": "",
            "stdin_is_tty": False,
            "input_fn": lambda _prompt: self.fail("input_fn must not be called"),
            "backup_dir": None,
        }
        arguments.update(overrides)
        return coordinate_setup(**arguments)  # type: ignore[arg-type]

    def procedure(self, slug: str = "release-check") -> ProcedureSpec:
        return ProcedureSpec(
            slug=slug,
            title=f"{slug.replace('-', ' ').title()} procedure",
            trigger="a maintainer explicitly requests the confirmed procedure",
            reads=("docs/OPERATIONS.md",),
            actions=("Run the project-owned documented command.",),
            stop_conditions=("Stop if the documented prerequisite is missing.",),
            evidence=("Record the project-owned command result.",),
            permissions=("Use only permissions already granted by the project owner.",),
            rollback=("Follow the rollback steps in docs/OPERATIONS.md.",),
        )

    def snapshot(self, root: Path) -> tuple[tuple[str, str, int, bytes | str | None], ...]:
        entries: list[tuple[str, str, int, bytes | str | None]] = []
        for current_text, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
            current = Path(current_text)
            for name in sorted(directory_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                mode = stat.S_IMODE(path.lstat().st_mode)
                entries.append(
                    (
                        relative,
                        "symlink" if path.is_symlink() else "directory",
                        mode,
                        os.readlink(path) if path.is_symlink() else None,
                    )
                )
            for name in sorted(file_names):
                path = current / name
                relative = path.relative_to(root).as_posix()
                mode = stat.S_IMODE(path.lstat().st_mode)
                entries.append(
                    (
                        relative,
                        "symlink" if path.is_symlink() else "file",
                        mode,
                        os.readlink(path) if path.is_symlink() else path.read_bytes(),
                    )
                )
        return tuple(sorted(entries))

    def test_non_tty_setup_audits_once_creates_only_visible_draft_and_reports_actual_topics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "pyproject.toml").write_text("[project]\nname = 'fixture'\n", encoding="utf-8")
            stdout = io.StringIO()
            with mock.patch("reporivet.setup.audit_project", wraps=audit_project) as audited:
                with contextlib.redirect_stdout(stdout):
                    envelope = self.coordinate(root)

            audited.assert_called_once_with(root=root)
            self.assertEqual(stdout.getvalue(), "")
            payload = envelope.as_dict()
            self.assertEqual(
                set(payload),
                {
                    "schema",
                    "root",
                    "mode",
                    "state",
                    "audit",
                    "definition",
                    "preview",
                    "eligible_for_apply",
                    "changes",
                    "input",
                    "next_action",
                    "backup",
                },
            )
            self.assertEqual(payload["schema"], "reporivet.setup/v1")
            self.assertEqual(payload["root"], str(root))
            self.assertEqual(payload["mode"], "preview")
            self.assertEqual(payload["state"], "awaiting-approval")
            self.assertTrue(payload["eligible_for_apply"])
            self.assertEqual(payload["input"], {"mode": "non-tty", "prompted": False, "recorded": False})
            self.assertEqual(
                payload["changes"],
                {"created": [DEFINITION_DRAFT_PATH.as_posix()], "updated": [], "skipped": []},
            )

            definition = payload["definition"]
            self.assertIsInstance(definition, dict)
            assert isinstance(definition, dict)
            self.assertEqual(
                definition["draft"],
                {"path": DEFINITION_DRAFT_PATH.as_posix(), "state": "created"},
            )
            topics = definition["topics"]
            self.assertIsInstance(topics, dict)
            assert isinstance(topics, dict)
            self.assertEqual(set(topics), {topic.key for topic in DEFINITION_TOPICS})
            for topic in DEFINITION_TOPICS:
                actual = topics[topic.key]
                self.assertIsInstance(actual, dict)
                assert isinstance(actual, dict)
                self.assertEqual(actual["title"], topic.title)
                self.assertEqual(actual["question"], topic.question)
                for evidence_state in ("confirmed", "proposed", "open", "sources"):
                    self.assertIsInstance(actual[evidence_state], list)
                self.assertEqual(actual["open"], [topic.question])

            self.assertTrue((root / DEFINITION_DRAFT_PATH).is_file())
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertFalse((root / "docs/PRODUCT.md").exists())
            preview = payload["preview"]
            self.assertIsInstance(preview, dict)
            assert isinstance(preview, dict)
            self.assertEqual(preview["schema"], "reporivet.setup-preview/v1")
            self.assertEqual(len(str(preview["fingerprint"])), 64)
            self.assertNotIn(
                ".claude/settings.json",
                {action["path"] for action in preview["actions"]},
            )
            self.assertEqual(json.loads(envelope.render()), payload)

    def test_answers_are_deterministic_and_open_items_are_visible_but_nonblocking(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as answer_directory:
            root = Path(directory).resolve()
            answers = Path(answer_directory).resolve() / "answers.json"
            answers.write_text(
                json.dumps(
                    {
                        "product": "For maintainers; success is a reviewable setup preview.",
                        "design": {
                            "confirmed": "Keyboard operation is required.",
                            "proposed": "Review reduced-motion behavior.",
                            "open": "Which locales must be supported?",
                            "sources": "Owner answer.",
                        },
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            first = self.coordinate(root, answers=answers)
            second = self.coordinate(root, answers=answers)

            first_payload = first.as_dict()
            second_payload = second.as_dict()
            self.assertEqual(
                first_payload["preview"]["fingerprint"],  # type: ignore[index]
                second_payload["preview"]["fingerprint"],  # type: ignore[index]
            )
            topics = first_payload["definition"]["topics"]  # type: ignore[index]
            self.assertEqual(
                topics["product"]["confirmed"],
                ["For maintainers; success is a reviewable setup preview."],
            )
            self.assertEqual(topics["product"]["open"], [])
            self.assertEqual(topics["design"]["confirmed"], ["Keyboard operation is required."])
            self.assertEqual(topics["design"]["proposed"], ["Review reduced-motion behavior."])
            self.assertEqual(topics["design"]["open"], ["Which locales must be supported?"])
            self.assertEqual(topics["design"]["sources"], ["Owner answer."])
            self.assertTrue(first_payload["eligible_for_apply"])
            self.assertEqual(first_payload["state"], "awaiting-approval")
            self.assertEqual(first_payload["input"], {"mode": "answers-file", "prompted": False, "recorded": True})
            self.assertEqual(second_payload["changes"]["skipped"], [DEFINITION_DRAFT_PATH.as_posix()])  # type: ignore[index]

    def test_tty_records_at_most_one_answer_per_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            prompts: list[str] = []
            answers = iter(("Product answer", "Design answer"))

            def answer(prompt: str) -> str:
                prompts.append(prompt)
                return next(answers)

            first = self.coordinate(root, stdin_is_tty=True, input_fn=answer)
            self.assertEqual(len(prompts), 1)
            self.assertIn(DEFINITION_TOPICS[0].question, prompts[0])
            first_topics = first.as_dict()["definition"]["topics"]  # type: ignore[index]
            self.assertEqual(first_topics["product"]["confirmed"], ["Product answer"])
            self.assertEqual(first_topics["design"]["confirmed"], [])
            self.assertEqual(first.as_dict()["input"], {"mode": "tty", "prompted": True, "recorded": True})

            second = self.coordinate(root, stdin_is_tty=True, input_fn=answer)
            self.assertEqual(len(prompts), 2)
            self.assertIn(DEFINITION_TOPICS[1].question, prompts[1])
            second_topics = second.as_dict()["definition"]["topics"]  # type: ignore[index]
            self.assertEqual(second_topics["product"]["confirmed"], ["Product answer"])
            self.assertEqual(second_topics["design"]["confirmed"], ["Design answer"])

    def test_dry_run_never_prompts_or_writes_and_can_preview_answer_file_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as answer_directory:
            root = Path(directory).resolve()
            sentinel = root / "project-owned.txt"
            sentinel.write_bytes(b"keep exact bytes\n")
            answers = Path(answer_directory).resolve() / "answers.json"
            answers.write_text(json.dumps({"quality": "Run python -m unittest."}), encoding="utf-8")
            before = self.snapshot(root)

            envelope = self.coordinate(
                root,
                answers=answers,
                dry_run=True,
                stdin_is_tty=True,
                input_fn=lambda _prompt: self.fail("dry-run must never prompt"),
            )

            self.assertEqual(self.snapshot(root), before)
            payload = envelope.as_dict()
            self.assertEqual(payload["mode"], "dry-run")
            self.assertEqual(payload["state"], "dry-run")
            self.assertFalse(payload["eligible_for_apply"])
            self.assertEqual(payload["definition"]["draft"]["state"], "planned-create")  # type: ignore[index]
            self.assertEqual(
                payload["definition"]["topics"]["quality"]["confirmed"],  # type: ignore[index]
                ["Run python -m unittest."],
            )
            self.assertEqual(payload["input"], {"mode": "answers-file", "prompted": False, "recorded": True})
            self.assertFalse((root / DEFINITION_DRAFT_PATH).exists())

            no_answers = self.coordinate(
                root,
                dry_run=True,
                stdin_is_tty=True,
                input_fn=lambda _prompt: self.fail("dry-run must never prompt"),
            )
            self.assertEqual(no_answers.as_dict()["input"], {"mode": "disabled-dry-run", "prompted": False, "recorded": False})
            self.assertEqual(self.snapshot(root), before)

    def test_apply_mode_matrix_missing_draft_stale_preview_and_approval_binding(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as answer_directory:
            missing_root = Path(directory).resolve() / "missing-draft"
            missing_root.mkdir()
            with self.assertRaisesRegex(InitError, "definition draft is missing"):
                self.coordinate(
                    missing_root,
                    apply=True,
                    approve_preview="0" * 64,
                )
            self.assertFalse((missing_root / DEFINITION_DRAFT_PATH).exists())

            root = Path(directory).resolve() / "project"
            root.mkdir()
            backup = Path(directory).resolve() / "external-backup"
            preview_envelope = self.coordinate(
                root,
                with_claude_settings=True,
                backup_dir=backup,
            )
            preview = preview_envelope.as_dict()["preview"]
            fingerprint = str(preview["fingerprint"])  # type: ignore[index]
            actions = {action["path"]: action for action in preview["actions"]}  # type: ignore[index]
            self.assertNotIn(".claude/settings.json", actions)
            self.assertFalse((root / ".claude/settings.json").exists())
            self.assertEqual(
                preview_envelope.as_dict()["backup"],
                {
                    "directory": str(backup),
                    "manifest": None,
                    "required": False,
                    "status": "available",
                },
            )

            without_compatibility_flag = self.coordinate(
                root,
                with_claude_settings=False,
                backup_dir=backup,
            )
            self.assertEqual(
                without_compatibility_flag.as_dict()["preview"]["fingerprint"],  # type: ignore[index]
                fingerprint,
            )

            answer_path = Path(answer_directory).resolve() / "answers.json"
            answer_path.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(InitError, "does not accept --answers"):
                self.coordinate(
                    root,
                    answers=answer_path,
                    apply=True,
                    approve_preview=fingerprint,
                )
            with self.assertRaisesRegex(InitError, "cannot be combined"):
                self.coordinate(
                    root,
                    dry_run=True,
                    apply=True,
                    approve_preview=fingerprint,
                )
            with self.assertRaisesRegex(InitError, "nonempty"):
                self.coordinate(root, apply=True, approve_preview="")
            with self.assertRaisesRegex(InitError, "requires setup --apply"):
                self.coordinate(root, approve_preview=fingerprint)

            (root / "AGENTS.md").write_text("# Changed after preview\n", encoding="utf-8")
            before_stale = self.snapshot(root)
            with self.assertRaisesRegex(InitError, "does not match"):
                self.coordinate(
                    root,
                    apply=True,
                    approve_preview=fingerprint,
                    with_claude_settings=False,
                    backup_dir=backup,
                )
            self.assertEqual(self.snapshot(root), before_stale)
            self.assertFalse(backup.exists())

            refreshed = self.coordinate(
                root,
                with_claude_settings=True,
                backup_dir=backup,
            )
            refreshed_fingerprint = str(refreshed.as_dict()["preview"]["fingerprint"])  # type: ignore[index]
            stdout = io.StringIO()
            with mock.patch("reporivet.setup.audit_project", wraps=audit_project) as audited:
                with contextlib.redirect_stdout(stdout):
                    applied = self.coordinate(
                        root,
                        apply=True,
                        approve_preview=refreshed_fingerprint,
                        with_claude_settings=True,
                        backup_dir=backup,
                        stdin_is_tty=True,
                        input_fn=lambda _prompt: self.fail("apply must never prompt"),
                    )
            audited.assert_called_once_with(root=root)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(applied.as_dict()["state"], "applied")
            self.assertEqual(applied.as_dict()["mode"], "apply")
            self.assertFalse(applied.as_dict()["eligible_for_apply"])
            self.assertEqual(applied.as_dict()["input"], {"mode": "none", "prompted": False, "recorded": False})
            self.assertFalse((root / ".claude/settings.json").exists())
            self.assertEqual(
                applied.as_dict()["backup"],
                {
                    "directory": str(backup),
                    "manifest": str(backup / "manifest.json"),
                    "required": False,
                    "status": "applied",
                },
            )
            self.assertTrue((backup / "manifest.json").is_file())

    def test_conflict_is_ineligible_and_apply_preserves_external_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
            root = Path(directory).resolve()
            external = Path(external_directory).resolve() / "PRODUCT.md"
            external.write_bytes(b"external exact bytes\n")
            (root / "docs").mkdir()
            (root / "docs/PRODUCT.md").symlink_to(external)

            envelope = self.coordinate(root)
            payload = envelope.as_dict()
            self.assertEqual(payload["state"], "conflict")
            self.assertFalse(payload["eligible_for_apply"])
            actions = {action["path"]: action for action in payload["preview"]["actions"]}  # type: ignore[index]
            self.assertEqual(actions["docs/PRODUCT.md"]["action"], "conflict")
            before = self.snapshot(root)
            external_before = external.read_bytes()

            with self.assertRaisesRegex(InitError, "unsafe target conflicts"):
                self.coordinate(
                    root,
                    apply=True,
                    approve_preview=str(payload["preview"]["fingerprint"]),  # type: ignore[index]
                )

            self.assertEqual(self.snapshot(root), before)
            self.assertEqual(external.read_bytes(), external_before)

    def test_confirmed_procedure_preview_is_deterministic_and_generates_only_valid_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as answer_directory:
            root = Path(directory).resolve()
            valid = self.procedure()
            proposed = self.procedure("proposed-only")
            opened = self.procedure("open-only")
            sourced = self.procedure("source-only")
            answers = Path(answer_directory).resolve() / "answers.json"
            answers.write_text(
                json.dumps(
                    {
                        "procedures": {
                            "confirmed": [
                                valid.canonical_record(),
                                "Generic confirmed procedure evidence.",
                                '{"slug":"incomplete"}',
                            ],
                            "proposed": [proposed.canonical_record()],
                            "open": [opened.canonical_record()],
                            "sources": [sourced.canonical_record()],
                        }
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            first = self.coordinate(root, answers=answers)
            second = self.coordinate(root, answers=answers)
            first_payload = first.as_dict()
            second_payload = second.as_dict()
            preview = first_payload["preview"]
            self.assertIsInstance(preview, dict)
            assert isinstance(preview, dict)
            actions = {action["path"]: action for action in preview["actions"]}
            target = "docs/runbooks/release-check.md"
            self.assertEqual(actions[target]["action"], "create")
            self.assertEqual(actions[target]["content"], render_procedure_runbook(valid))
            for excluded in ("proposed-only", "open-only", "source-only", "incomplete"):
                self.assertNotIn(
                    f"docs/runbooks/{excluded}.md",
                    actions,
                )
            self.assertEqual(
                [(item["index"], item["code"], item["path"]) for item in preview["diagnostics"]],
                [
                    (1, "generic", "procedures.confirmed[1]"),
                    (2, "incomplete-record", "procedures.confirmed[2]"),
                ],
            )
            self.assertTrue(first_payload["eligible_for_apply"])
            self.assertEqual(
                preview["fingerprint"],
                second_payload["preview"]["fingerprint"],  # type: ignore[index]
            )

            applied = self.coordinate(
                root,
                apply=True,
                approve_preview=str(preview["fingerprint"]),
            )
            self.assertEqual(
                (root / target).read_text(encoding="utf-8"),
                render_procedure_runbook(valid),
            )
            self.assertEqual(
                applied.as_dict()["preview"]["diagnostics"],  # type: ignore[index]
                preview["diagnostics"],
            )

    def test_legacy_procedure_skills_preserve_existing_and_stale_files_and_refuse_symlinks(self) -> None:
        valid = self.procedure()
        with tempfile.TemporaryDirectory() as answer_directory:
            answers = Path(answer_directory).resolve() / "answers.json"
            answers.write_text(
                json.dumps(
                    {"procedures": {"confirmed": [valid.canonical_record()]}},
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                target = root / ".claude/skills/release-check/SKILL.md"
                target.parent.mkdir(parents=True)
                project_owned = b"project-owned procedure Skill\n"
                target.write_bytes(project_owned)
                stale = root / ".claude/skills/old-name/SKILL.md"
                stale.parent.mkdir(parents=True)
                stale_content = b"stale but retained Skill\n"
                stale.write_bytes(stale_content)

                envelope = self.coordinate(root, answers=answers)
                preview = envelope.as_dict()["preview"]
                actions = {action["path"]: action for action in preview["actions"]}  # type: ignore[index]
                self.assertEqual(actions[".claude/skills/release-check/SKILL.md"]["action"], "preserve")
                self.assertEqual(
                    actions[".claude/skills/old-name/SKILL.md"]["action"],
                    "preserve",
                )
                applied = self.coordinate(
                    root,
                    apply=True,
                    approve_preview=str(preview["fingerprint"]),  # type: ignore[index]
                )
                self.assertEqual(applied.as_dict()["state"], "applied")
                self.assertEqual(target.read_bytes(), project_owned)
                self.assertEqual(stale.read_bytes(), stale_content)

            with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external_directory:
                root = Path(directory).resolve()
                external = Path(external_directory).resolve() / "external-skill.md"
                external_content = b"external procedure content\n"
                external.write_bytes(external_content)
                target = root / ".claude/skills/release-check/SKILL.md"
                target.parent.mkdir(parents=True)
                target.symlink_to(external)

                envelope = self.coordinate(root, answers=answers)
                payload = envelope.as_dict()
                preview = payload["preview"]
                actions = {action["path"]: action for action in preview["actions"]}  # type: ignore[index]
                self.assertEqual(actions[".claude/skills/release-check/SKILL.md"]["action"], "conflict")
                self.assertFalse(payload["eligible_for_apply"])
                with self.assertRaisesRegex(InitError, "unsafe target conflicts"):
                    self.coordinate(
                        root,
                        apply=True,
                        approve_preview=str(preview["fingerprint"]),  # type: ignore[index]
                    )
                self.assertTrue(target.is_symlink())
                self.assertEqual(external.read_bytes(), external_content)

    def test_apply_failure_rolls_back_all_bundle_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            preview = self.coordinate(root)
            fingerprint = str(preview.as_dict()["preview"]["fingerprint"])  # type: ignore[index]
            before = self.snapshot(root)
            original_create = migration._apply_setup_create
            calls = 0

            def fail_second_create(*args: object, **kwargs: object) -> object:
                nonlocal calls
                calls += 1
                result = original_create(*args, **kwargs)
                if calls == 2:
                    raise OSError("injected setup failure")
                return result

            with mock.patch.object(migration, "_apply_setup_create", side_effect=fail_second_create):
                with self.assertRaisesRegex(InitError, "rolled back"):
                    self.coordinate(
                        root,
                        apply=True,
                        approve_preview=fingerprint,
                    )

            self.assertGreaterEqual(calls, 2)
            self.assertEqual(self.snapshot(root), before)


if __name__ == "__main__":
    unittest.main()
