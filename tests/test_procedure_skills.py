from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from reporivet.procedures import (
    PROCEDURE_FIELDS,
    ProcedureSpec,
    ProcedureValidationError,
    build_procedure_skill_plan,
    parse_confirmed_procedures,
    parse_procedure_record,
    procedure_skill_path,
    render_procedure_skill,
    serialize_procedure_spec,
)


class ProcedureSkillTests(unittest.TestCase):
    def spec(self, **overrides: object) -> ProcedureSpec:
        values: dict[str, object] = {
            "slug": "release-check",
            "title": "Release check",
            "trigger": "A release candidate is ready for review",
            "reads": ("docs/QUALITY.md", "docs/OPERATIONS.md"),
            "actions": ("Run the project-owned release checks", "Review the output"),
            "stop_conditions": ("A required check fails", "A project owner is unavailable"),
            "evidence": ("Record command output in the active Plan",),
            "permissions": ("Use only project-owned commands",),
            "rollback": ("Restore the prior release state using the documented procedure",),
        }
        values.update(overrides)
        return ProcedureSpec(**values)

    def test_spec_is_immutable_and_normalizes_to_tuples(self) -> None:
        spec = self.spec(
            title="  Release check  ",
            reads=[" docs/QUALITY.md "],
        )
        self.assertEqual(spec.title, "Release check")
        self.assertEqual(spec.reads, ("docs/QUALITY.md",))
        with self.assertRaises((AttributeError, TypeError)):
            spec.reads += ("docs/OPERATIONS.md",)  # type: ignore[misc]
        with self.assertRaises((AttributeError, TypeError)):
            spec.title = "Changed"  # type: ignore[misc]

    def test_slug_validation_rejects_invalid_reserved_and_long_values(self) -> None:
        invalid = (
            "",
            "Upper-case",
            "two--words",
            "-leading",
            "trailing-",
            "not_a_slug",
            "a" * 65,
            "reporivet-main",
            "reporivet-implementation",
            "reporivet-verification",
        )
        for slug in invalid:
            with self.subTest(slug=slug), self.assertRaises(ProcedureValidationError):
                self.spec(slug=slug)

    def test_required_scalars_and_items_must_be_nonempty(self) -> None:
        for field in ("title", "trigger"):
            with self.subTest(field=field), self.assertRaises(ProcedureValidationError):
                self.spec(**{field: "  "})
        for field in PROCEDURE_FIELDS[3:]:
            with self.subTest(field=field), self.assertRaises(ProcedureValidationError):
                self.spec(**{field: ()})
            with self.subTest(field=f"{field}-item"), self.assertRaises(ProcedureValidationError):
                self.spec(**{field: ("valid", "  ")})
        with self.assertRaises(ProcedureValidationError):
            self.spec(trigger="line one\nline two")

    def test_canonical_record_is_compact_exact_and_round_trips(self) -> None:
        spec = self.spec()
        record = serialize_procedure_spec(spec)
        self.assertEqual(record, spec.canonical_record())
        self.assertNotIn(", ", record)
        self.assertNotIn(": ", record)
        self.assertEqual(set(json.loads(record)), set(PROCEDURE_FIELDS))
        self.assertEqual(parse_procedure_record(record), spec)
        self.assertEqual(record, spec.to_record())

    def test_parser_rejects_noncanonical_json_shapes_with_diagnostics(self) -> None:
        valid = self.spec().canonical_record()
        values = (
            "plain confirmed evidence",
            "{not-json}",
            "[]",
            json.dumps({"slug": "release-check"}),
            valid.replace('"title":"Release check"', '"title":""'),
            '{"slug":"release-check","slug":"other","title":"T","trigger":"T","reads":["r"],"actions":["a"],"stop_conditions":["s"],"evidence":["e"],"permissions":["p"],"rollback":["r"]}',
        )
        collection = parse_confirmed_procedures(values)
        self.assertEqual(collection.procedures, ())
        self.assertEqual(len(collection.diagnostics), len(values))
        self.assertEqual([item.index for item in collection.diagnostics], list(range(len(values))))
        self.assertEqual(collection.diagnostics[0].code, "generic")
        self.assertTrue(all(item.path.startswith("procedures.confirmed[") for item in collection.diagnostics))

    def test_only_complete_confirmed_records_are_eligible_and_duplicates_are_excluded(self) -> None:
        first = self.spec().canonical_record()
        second = self.spec(title="Another release check").canonical_record()
        collection = parse_confirmed_procedures((first, "generic evidence", second))
        self.assertEqual(collection.procedures, ())
        self.assertEqual(
            [(diagnostic.index, diagnostic.code) for diagnostic in collection.diagnostics],
            [(0, "duplicate-slug"), (1, "generic"), (2, "duplicate-slug")],
        )

        unique = parse_confirmed_procedures((first, self.spec(slug="backup-check").canonical_record()))
        self.assertEqual([item.slug for item in unique.eligible], ["release-check", "backup-check"])
        self.assertTrue(unique.valid)

    def test_skill_path_and_render_are_deterministic_instruction_only_content(self) -> None:
        spec = self.spec()
        expected_path = ".claude/skills/release-check/SKILL.md"
        self.assertEqual(procedure_skill_path(spec).as_posix(), expected_path)
        self.assertEqual(procedure_skill_path("release-check").as_posix(), expected_path)

        rendered = render_procedure_skill(spec)
        self.assertEqual(rendered, render_procedure_skill(spec))
        self.assertEqual(rendered.count("---\n"), 2)
        frontmatter = rendered.split("---\n", 2)[1]
        self.assertEqual(
            [line.split(":", 1)[0] for line in frontmatter.splitlines()],
            ["name", "description"],
        )
        self.assertRegex(frontmatter, r"(?m)^name: release-check$")
        self.assertIn("description: Release check. Use when A release candidate is ready for review.", frontmatter)
        for heading in (
            "## Trigger",
            "## Required reads",
            "## Actions",
            "## Stop conditions",
            "## Evidence",
            "## Permissions",
            "## Rollback",
        ):
            self.assertIn(heading, rendered)
        self.assertNotRegex(frontmatter, r"(?m)^(allowed-tools|hooks|shell):")
        self.assertNotIn("settings.json", rendered)
        self.assertNotIn("subprocess", rendered)
        self.assertTrue(rendered.endswith("\n"))

    def test_evidence_mapping_reads_only_confirmed_values(self) -> None:
        valid = self.spec().canonical_record()
        plan = build_procedure_skill_plan(
            {
                "confirmed": [valid],
                "proposed": [self.spec(slug="proposed-check").canonical_record()],
                "open": [self.spec(slug="open-check").canonical_record()],
                "sources": [self.spec(slug="source-check").canonical_record()],
            }
        )
        self.assertEqual([target.slug for target in plan.targets], ["release-check"])
        self.assertEqual(plan.diagnostics, ())

    def test_plan_exposes_targets_and_diagnostics_without_io_or_execution(self) -> None:
        valid = self.spec().canonical_record()
        plan = build_procedure_skill_plan(("generic evidence", valid))
        self.assertEqual(len(plan.targets), 1)
        self.assertEqual(plan.targets[0].path, ".claude/skills/release-check/SKILL.md")
        self.assertEqual(plan.targets[0].content, render_procedure_skill(self.spec()))
        self.assertEqual(len(plan.diagnostics), 1)
        self.assertEqual(plan.diagnostics[0].code, "generic")
        self.assertEqual(plan.procedures, (self.spec(),))

    def test_frontmatter_quotes_yaml_sensitive_values_without_extra_fields(self) -> None:
        spec = self.spec(title="Release: production", trigger="When #approved is set")
        rendered = render_procedure_skill(spec)
        frontmatter = rendered.split("---\n", 2)[1]
        self.assertEqual([line.split(":", 1)[0] for line in frontmatter.splitlines()], ["name", "description"])
        self.assertIn('description: "Release: production. Use when When #approved is set."', frontmatter)


if __name__ == "__main__":
    unittest.main()
