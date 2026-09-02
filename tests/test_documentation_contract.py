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
HIERARCHY_DOCUMENTS = (
    REPOSITORY / "AGENTS.md",
    REPOSITORY / "README.en.md",
    REPOSITORY / "README.md",
    REPOSITORY / "docs/PRODUCT.md",
    REPOSITORY / "docs/DESIGN.md",
    REPOSITORY / "docs/PLANS.md",
    REPOSITORY / "docs/product-specs/SPEC-REPORIVET-003-document-first-harness.md",
    REPOSITORY / "docs/design-docs/DESIGN-REPORIVET-003-document-first-harness.md",
    REPOSITORY / "docs/exec-plans/_template.md",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return " ".join(read(path).split())


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

    def test_complete_procedure_records_are_the_only_static_runbook_input(self) -> None:
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
        )
        path_specific_contract = {
            PROTOCOL: (
                "during explicit package-side setup",
                "reporivet setup",
                "reporivet init",
                "reporivet define",
                "ordinary Markdown at `docs/runbooks/<slug>.md` through resumed setup",
                "The output has no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration",
                "It is descriptive project documentation, not an executor",
                "does not generate a target role or procedure Skill",
                "Existing, differing, stale, or arbitrary project Skills are preserved and never deleted by procedure rendering",
                "Setup and init create no Plan or runtime",
                "execute no project commands",
                "do not spawn or dispatch Agents",
                "Main Skill creates or resumes the first ordinary Markdown Plan",
                "No generated target artifact locates, installs, resolves, imports, invokes, or verifies Reporivet",
                "package absence afterward is expected",
            ),
            PACKAGE_PROTOCOL: (
                "ordinary project-owned Markdown",
                "without a package or continuing runtime",
                "does not execute project commands, dispatch Agents, create a Plan",
                "No generated target artifact directs an Agent to locate, install, resolve, import, invoke, or verify Reporivet",
                "No target role or procedure Skill",
                "ordinary Markdown file at `docs/runbooks/<slug>.md` during resumed setup only",
                "ordinary target work does not depend on package-side context",
                "The file is descriptive and instruction-only project documentation, not an executor",
                "no command execution, Agent spawn/dispatch, privilege-bearing frontmatter",
                "Existing differing, stale, arbitrary, unsafe, symlinked, or nonregular runbooks remain preserved and are never deleted by rendering",
                "A filename, marker, frontmatter block, or location alone never proves ownership",
                "package absence is expected",
            ),
        }

        for path, path_contract in path_specific_contract.items():
            protocol = read(path)
            with self.subTest(path=path):
                for field in required_fields:
                    with self.subTest(field=field):
                        self.assertIn(f"`{field}`", protocol)
                for field in rejected_schema_fields:
                    with self.subTest(rejected_field=field):
                        self.assertNotIn(f"`{field}`", protocol)
                for phrase in (*shared_contract, *path_contract):
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
            r"(?i)\b(?:pending|unknown|unverified)\b|"
            r"\bopen\b(?!\s+items\b)|"
            r"remain(?:s)? subject to (?:its|their) own verification"
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

    def test_broad_roots_default_to_task_owners_and_serial_roots_remain_leaves(self) -> None:
        authority = " ".join(normalized(path) for path in HIERARCHY_DOCUMENTS)
        self.assertRegex(
            authority,
            r"(?i)\b(?:broad|multi-part)\b.{0,180}\b(?:root|milestone)s?\b"
            r".{0,180}\bdefault(?:s|ed|ing)?\b.{0,180}"
            r"\bRole:\s*Task Owner\b.{0,120}\bMay delegate:\s*yes\b",
        )
        self.assertIn("Role: Task Owner", authority)
        self.assertIn("May delegate: yes", authority)
        self.assertRegex(
            authority,
            r"(?i)\b(?:narrow|inherently serial)\b.{0,180}"
            r"\b(?:direct|nondelegating)\b.{0,80}\bleaves?\b",
        )
        topology = (
            "T<n> (broad root Owner) -> T<n>-A/B/C/... "
            "(declared child packets, all ready leaves dispatched concurrently) "
            "-> T<n>-I (Owner-local aggregation) -> T<n>-V1/V2/... "
            "(parallel fresh verification)"
        )
        self.assertIn(topology, authority)

        for path in BILINGUAL_READMES:
            text = read(path)
            with self.subTest(path=path):
                self.assertIn("Task Owner", text)
                self.assertIn("May delegate: yes", text)
                self.assertIn(topology, text)

    def test_owner_checkpoint_nested_dispatch_and_isolation_contract(self) -> None:
        authority = " ".join(normalized(path) for path in HIERARCHY_DOCUMENTS)
        self.assertRegex(
            authority,
            r"(?i)(?:\bOwner\b.{0,120}\bfinite(?:\s+\w+){0,4}\s+manifest\b|"
            r"\bfinite(?:\s+\w+){0,4}\s+manifest\b.{0,120}\bOwner\b)",
        )
        self.assertRegex(
            authority,
            r"(?i)\bMain\b[^.]{0,180}\balone\b[^.]{0,80}\bserializ\w*\b"
            r"[^.]{0,220}\b(?:child\s+rows?|matching\s+packets?)\b"
            r"[^.]{0,180}\bresum\w*\b[^.]{0,80}\b(?:serialized\s+)?Owner\b",
        )
        self.assertRegex(
            authority,
            r"(?i)\bMain\b.{0,400}\bdispatch\w*\b.{0,220}"
            r"\bindependent root Owners\b.{0,160}\b(?:concurr|parallel)\w*\b",
        )
        self.assertRegex(
            authority,
            r"(?i)\bonly\b[^.]{0,100}\bresum\w*\b[^.]{0,60}\bserializ\w*\b"
            r"[^.]{0,80}\b(?:Task Owner|Owner)\b[^.]{0,120}\bdispatch\w*\b"
            r"[^.]{0,100}\bdeclared\b[^.]{0,80}\bdescendants?\b",
        )
        self.assertRegex(
            authority,
            r"(?i)\bordinary leaf(?: Agents?)?.{0,80}\b(?:do not|never)\s+delegate\b",
        )
        self.assertRegex(
            authority,
            r"(?i)\binherit\w*[^.]{0,160}\bscope\b[^.]{0,100}"
            r"\bprotected paths\b[^.]{0,100}\bacceptance\b[^.]{0,100}"
            r"\bcannot broaden\b",
        )
        self.assertIn("disjoint allowed-write sets", authority)
        self.assertIn("separate exact-baseline worktrees", authority)
        self.assertRegex(
            authority,
            r"(?i)(?:Owner[- ]local aggregation.{0,180}"
            r"(?:distinct|separate).{0,180}Main(?:'s)?(?: repository)? integration|"
            r"Main(?:'s)?(?: repository)? integration.{0,180}"
            r"(?:distinct|separate).{0,180}Owner[- ]local aggregation)",
        )

    def test_fresh_verification_and_plan_compatibility_are_documented(self) -> None:
        authority = " ".join(
            normalized(path) for path in (*HIERARCHY_DOCUMENTS, REPOSITORY / "docs/QUALITY.md")
        )
        self.assertRegex(authority, r"(?i)\bfresh(?:[- ]context)?[^.]{0,180}\bverification\b")
        self.assertRegex(
            authority,
            r"(?i)\bread-only\b[^.]{0,180}\bverification\b[^.]{0,180}"
            r"(?:nondelegating|do not delegate|cannot delegate)",
        )
        self.assertRegex(
            authority,
            r"(?i)\bverification\w*[^.]{0,240}\bdepend\w*\b[^.]{0,100}"
            r"\bintegrated candidate\b",
        )
        self.assertRegex(
            authority,
            r"(?i)\bcandidate mutation\b[^.]{0,100}\binvalidat\w*\b"
            r"[^.]{0,100}\bverification evidence\b",
        )

        compatibility = (
            (
                "unmarked compact Plans",
                r"(?i)\bunmarked compact Plans?\b.{0,120}"
                r"\b(?:retain|remain|continue|supported|valid)\w*\b",
            ),
            (
                "historical/expanded Plans",
                r"(?i)\bhistorical\s+expanded\s+or\s+completed\s+Plans?\b"
                r".{0,40}\bremain(?:s)?\s+untouched\b",
            ),
            (
                "recursive task IDs",
                r"(?i)\brecursive(?:\s+task)?\s+IDs?\b.{0,120}"
                r"\b(?:remain|valid|supported|preserved)\w*\b",
            ),
            (
                "direct serial Plans",
                r"(?i)\bdirect serial Plans?\b.{0,120}"
                r"\b(?:remain|supported|valid|preserved)\w*\b",
            ),
        )
        for label, pattern in compatibility:
            with self.subTest(compatibility=label):
                self.assertRegex(authority, pattern)

    def test_current_docs_explicitly_reject_runtime_and_orchestration_boundaries(self) -> None:
        negative_markers = re.compile(
            r"(?i)\b(?:no|not|never|does not|do not|without|excluded|unestablished)\b"
        )
        boundary_terms = (
            ("scheduler", r"\bscheduler\b"),
            ("dispatcher", r"\bdispatcher\b"),
            ("runtime", r"\bruntime\b"),
            ("task database", r"\btask database\b"),
            ("task store", r"\btask store\b"),
            ("command runner", r"\bcommand runner\b"),
            ("Gate", r"\bGate\b"),
            ("evidence archive", r"\bevidence archive\b"),
            ("automatic closure", r"\bautomatic closure\b"),
        )
        text = read(SPEC)
        for label, term in boundary_terms:
            with self.subTest(boundary=label):
                self.assertTrue(
                    any(
                        re.search(term, line) and negative_markers.search(line)
                        for line in text.splitlines()
                    ),
                    f"{label} lacks an explicit negative boundary in {SPEC}",
                )

    def test_current_docs_do_not_make_positive_release_or_execution_claims(self) -> None:
        positive_patterns = (
            re.compile(r"(?i)\bready for release\b"),
            re.compile(r"(?i)\b(?:is|are|now|fully) release-ready\b"),
            re.compile(r"(?i)\b(?:reporivet|the package)\s+(?:publishes|signs|releases|deploys)\b"),
            re.compile(r"(?i)\b(?:reporivet|the package)\s+(?:spawns|dispatches)\s+Agents\b"),
            re.compile(r"(?i)\bReporivet\s+executes\s+project commands\b"),
        )
        hierarchy_positive_patterns = (
            re.compile(
                r"(?i)\b(?:reporivet|the package)\b[^.\n]*\b"
                r"(?:scheduler|dispatcher|runtime|task\s+(?:database|store)|"
                r"command\s+runner|gate|evidence\s+(?:archive|store)|"
                r"automatic\s+(?:plan[- ]?closure|closure))\b"
            ),
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

        for path in HIERARCHY_DOCUMENTS:
            for line_number, line in enumerate(read(path).splitlines(), start=1):
                if negative_markers.search(line):
                    continue
                for pattern in hierarchy_positive_patterns:
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
