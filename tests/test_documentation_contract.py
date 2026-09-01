from __future__ import annotations

import re
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]

BILINGUAL_READMES = (REPOSITORY / "README.en.md", REPOSITORY / "README.md")
CURRENT_DOCUMENTS = (
    REPOSITORY / "README.en.md",
    REPOSITORY / "README.md",
    REPOSITORY / "AGENTS.md",
    REPOSITORY / "ARCHITECTURE.md",
    REPOSITORY / "docs/README.md",
    REPOSITORY / "docs/PRODUCT.md",
    REPOSITORY / "docs/DESIGN.md",
    REPOSITORY / "docs/QUALITY.md",
    REPOSITORY / "docs/OPERATIONS.md",
    REPOSITORY / "docs/SECURITY.md",
    REPOSITORY / "docs/PLANS.md",
    REPOSITORY / "docs/references/project-definition-protocol.md",
    REPOSITORY / "docs/references/harness-engineering-skill-migration.md",
    REPOSITORY / "docs/product-specs/SPEC-REPORIVET-003-document-first-harness.md",
    REPOSITORY / "docs/design-docs/DESIGN-REPORIVET-003-document-first-harness.md",
)

HISTORICAL_DOCUMENTS = (
    REPOSITORY / "docs/generated/README.md",
    REPOSITORY / "docs/generated/code-map.md",
    REPOSITORY / "docs/module-contracts/README.md",
    REPOSITORY / "docs/module-contracts/_template.md",
    REPOSITORY / "docs/module-contracts/MOD-HARNESS-RUNTIME.md",
)

SPEC = REPOSITORY / "docs/product-specs/SPEC-REPORIVET-003-document-first-harness.md"
DESIGN = REPOSITORY / "docs/design-docs/DESIGN-REPORIVET-003-document-first-harness.md"
PROTOCOL = REPOSITORY / "docs/references/project-definition-protocol.md"
PACKAGE_PROTOCOL = REPOSITORY / "src/reporivet/assets/project/document-first/docs/references/project-definition-protocol.md.tmpl"
PLANS = REPOSITORY / "docs/PLANS.md"
ARTIFACT_READINESS_DOCUMENTS = (
    REPOSITORY / "ARCHITECTURE.md",
    REPOSITORY / "docs/DESIGN.md",
    REPOSITORY / "docs/QUALITY.md",
    REPOSITORY / "docs/OPERATIONS.md",
    REPOSITORY / "docs/references/harness-engineering-skill-migration.md",
)
ARTIFACT_CANDIDATE = "c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4"
ARTIFACT_WHEEL = "512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4"
ARTIFACT_LIFECYCLE = "passed the recorded isolated pipx and pip install/use/uninstall lifecycle"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class DocumentationContractTests(unittest.TestCase):
    maxDiff = None

    def test_bilingual_readmes_expose_the_same_public_command_surface(self) -> None:
        english, korean = (read(path) for path in BILINGUAL_READMES)
        commands = (
            "reporivet setup",
            "reporivet setup --root \"$ROOT\"",
            "reporivet init --root \"$ROOT\"",
            "pipx install reporivet",
            "python -m pip install reporivet",
            "reporivet define start --root \"$ROOT\"",
            "reporivet define resume --root \"$ROOT\"",
            "reporivet define status --root \"$ROOT\"",
            "reporivet define finalize --root \"$ROOT\"",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertIn(command, english)
                self.assertIn(command, korean)

        self.assertIn("instruction-only", english)
        self.assertIn("지침 전용", korean)
        candidate = "c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4"
        wheel = "512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4"
        for document in (english, korean):
            self.assertIn("setup", document)
            self.assertIn("init", document)
            self.assertIn("define", document)
            self.assertIn("pipx", document)
            self.assertIn("pip", document)
            self.assertIn("Plan", document)
            self.assertIn("PLAN-2026-0003", document)
            self.assertIn(candidate, document)
            self.assertIn(wheel, document)
        self.assertIn("passed the recorded isolated pipx and pip install/use/uninstall lifecycle", english)
        self.assertIn("기록된 격리된 pipx 및 pip 설치/사용/제거 수명주기를 통과", korean)

    def test_current_documents_define_integrated_setup_and_plan_boundaries(self) -> None:
        for path in CURRENT_DOCUMENTS:
            text = read(path)
            with self.subTest(path=path):
                self.assertNotIn("./dev/", text)

        readme = read(REPOSITORY / "docs/README.md")
        self.assertIn("default onboarding entry point is integrated `reporivet setup`", readme)
        self.assertIn("`reporivet init` is structure-only", readme)
        self.assertIn("`reporivet define` remains the lower-level resumable definition interface", readme)
        self.assertIn("Setup creates no Plan or runtime", readme)
        self.assertIn("does not spawn or dispatch Agents", readme)
        self.assertIn("Main Skill creates or resumes the first ordinary Markdown Plan", readme)

        plans = read(PLANS)
        self.assertIn("Setup and first-Plan handoff", plans)
        self.assertIn("searches active and completed history", plans)
        self.assertIn("resumes exactly one matching active ordinary Markdown Plan", plans)
        self.assertIn("lowest unused current-year ID", plans)
        self.assertIn("Reporivet does not create or close Plans automatically", plans)

    def test_historical_generated_surfaces_are_classified_and_not_live_routing(self) -> None:
        for path in HISTORICAL_DOCUMENTS:
            text = read(path)
            with self.subTest(path=path):
                self.assertRegex(text, r"(?i)historical/superseded")
                self.assertTrue(
                    "not current routing" in text
                    or "not a current setup or routing requirement" in text,
                    text,
                )
                self.assertNotIn("./dev/", text)

        module_contract = read(REPOSITORY / "docs/module-contracts/MOD-HARNESS-RUNTIME.md")
        self.assertIn("status: superseded", module_contract)
        self.assertIn("old runtime commands are not to be run", module_contract)

        code_map = read(REPOSITORY / "docs/generated/code-map.md")
        self.assertIn("retired repository-local process", code_map)
        self.assertNotIn("Generated by `./dev/code-map`", code_map)

    def test_complete_procedure_records_are_the_only_project_skill_input(self) -> None:
        required_fields = (
            "slug",
            "title",
            "trigger",
            "reads",
            "actions",
            "stop_conditions",
            "evidence",
            "permissions",
            "rollback",
        )
        rejected_schema_fields = (
            "owner",
            "canonical_authority",
            "canonical-authority",
            "inputs",
            "protected_paths",
            "protected-paths",
            "scope",
            "prerequisites",
            "authorization",
            "escalation",
        )
        shared_contract = (
            "complete",
            "user-confirmed",
            "strict structured record",
            "exactly these nine fields",
            "no additional fields or aliases are accepted",
            "no values or defaults are inferred",
            "resumed setup",
            "Generic",
            "inferred",
            "incomplete",
            "Proposed",
            "Open",
            "Sources-only",
            "instruction-only",
            "no procedure is inferred or executed",
            "no command execution",
            "Agent spawn/dispatch",
            "privilege-bearing frontmatter",
            "preserved and never deleted",
            "reporivet setup",
            "reporivet init",
            "reporivet define",
            "Setup and init create no Plan or runtime",
            "do not spawn or dispatch Agents",
            "Main Skill creates or resumes the first ordinary Markdown Plan",
        )

        for path in (PROTOCOL, PACKAGE_PROTOCOL):
            protocol = read(path)
            with self.subTest(path=path):
                for field in required_fields:
                    with self.subTest(field=field):
                        self.assertIn(f"`{field}`", protocol)
                for field in rejected_schema_fields:
                    with self.subTest(rejected_field=field):
                        self.assertNotIn(f"`{field}`", protocol)
                for phrase in shared_contract:
                    with self.subTest(phrase=phrase):
                        self.assertIn(phrase, protocol)

    def test_spec_and_design_record_verified_source_and_artifact_lifecycle_boundary(self) -> None:
        historical_candidate = "f793567262ca66f11016aa198ddc46ec207eb23fbe91b234bf72a91348344293"
        candidate = "c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4"
        wheel = "512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4"
        for path in (SPEC, DESIGN):
            text = read(path)
            with self.subTest(path=path):
                self.assertIn("Source behavior through the previously verified document-first implementation exists", text)
                self.assertIn(historical_candidate, text)
                self.assertIn("passed AC-1 through AC-10 and AC-12", text)
                self.assertIn("AC-11 wheel/install evidence remained unknown", text)
                self.assertIn(candidate, text)
                self.assertIn(wheel, text)
                self.assertIn("passed the recorded isolated pipx and pip install/use/uninstall lifecycle", text)
                self.assertIn("temporary and are not a durable or downloadable evidence archive", text)
                self.assertIn("../exec-plans/completed/PLAN-2026-0003-document-first-harness.md", text)
                self.assertNotIn("../exec-plans/active/PLAN-2026-0003", text)
                self.assertRegex(
                    text,
                    r"(?i)publication, signing, release, deployment, and ci repair/readiness remain unestablished and outside scope",
                )

    def test_current_authority_records_completed_artifact_lifecycle(self) -> None:
        stale_status = re.compile(
            r"(?i)\b(?:pending|open|unknown|unverified)\b|remain(?:s)? subject to (?:its|their) own verification"
        )
        lifecycle_terms = re.compile(r"(?i)\b(?:wheel|artifact|pipx|pip|install|uninstall|lifecycle)\b")

        for path in ARTIFACT_READINESS_DOCUMENTS:
            text = read(path)
            with self.subTest(path=path):
                self.assertIn(ARTIFACT_CANDIDATE, text)
                self.assertIn(ARTIFACT_WHEEL, text)
                self.assertIn(ARTIFACT_LIFECYCLE, text)
                for line_number, line in enumerate(text.splitlines(), start=1):
                    if lifecycle_terms.search(line):
                        with self.subTest(line=line_number):
                            self.assertIsNone(stale_status.search(line), line)

        for path in (REPOSITORY / "docs/QUALITY.md", REPOSITORY / "docs/OPERATIONS.md"):
            text = read(path)
            open_section = text.split("### Open", 1)[1].split("### Sources", 1)[0]
            with self.subTest(path=path):
                self.assertNotIn(ARTIFACT_CANDIDATE, open_section)
                self.assertNotIn(ARTIFACT_WHEEL, open_section)
                self.assertNotIn("pip install/use/uninstall lifecycle", open_section)

    def test_current_docs_do_not_make_positive_release_or_execution_claims(self) -> None:
        positive_patterns = (
            re.compile(r"(?i)\bready for release\b"),
            re.compile(r"(?i)\b(?:is|are|now|fully) release-ready\b"),
            re.compile(r"(?i)\b(?:reporivet|the package)\s+(?:publishes|signs|releases|deploys)\b"),
            re.compile(r"(?i)\b(?:reporivet|the package)\s+(?:spawns|dispatches)\s+Agents\b"),
            re.compile(r"(?i)\bReporivet\s+executes\s+project commands\b"),
        )
        negative_markers = re.compile(
            r"(?i)\b(?:no|not|never|does not|do not|without|pending|unknown|excluded|remains?)\b"
        )
        for path in CURRENT_DOCUMENTS:
            for line_number, line in enumerate(read(path).splitlines(), start=1):
                if negative_markers.search(line):
                    continue
                for pattern in positive_patterns:
                    with self.subTest(path=path, line=line_number, pattern=pattern.pattern):
                        self.assertIsNone(pattern.search(line), line)

        english = read(REPOSITORY / "README.en.md")
        candidate = "c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4"
        wheel = "512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4"
        self.assertIn(candidate, english)
        self.assertIn(wheel, english)
        self.assertIn("passed the recorded isolated pipx and pip install/use/uninstall lifecycle", english)
        self.assertIn("temporary and are not a durable or downloadable evidence archive", english)
        self.assertIn("Publication, signing, release, deployment, and CI repair/readiness remain unestablished and outside scope", english)


if __name__ == "__main__":
    unittest.main()
