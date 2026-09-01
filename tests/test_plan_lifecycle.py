from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet.cli import main as cli_main
from reporivet.initializer import read_asset


TASK_PACKET = """### T1 — Implement

- **Owner:** implementation
- **Outcome:** Implement the example.
- **Non-goals:** No unrelated work.
- **Read:** current authority
- **Allowed writes:** example paths
- **Protected paths:** unrelated paths
- **Acceptance:** AC-1
- **Verification:** project-owned checks
- **Stop conditions:** scope conflict
- **Return:** decision-bearing evidence
- **Result:** complete
"""


def compact_plan(*, plan_id: str = "PLAN-2026-0001", status: str = "in-progress") -> str:
    terminal = status in {"complete", "cancelled", "superseded"}
    documentation = "- None." if terminal else "- Pending until integration."
    integration = (
        "- Candidate identity: commit abc123\n- Integrated changes: T1 implementation"
        if terminal
        else "- Pending until integration."
    )
    verification = (
        "| Criterion | Candidate | Verifier | Result | Decision-bearing evidence |\n"
        "|---|---|---|---|---|\n"
        "| AC-1 | abc123 | independent | pass | focused checks passed |"
        if terminal
        else "- Pending until verification."
    )
    followups = "- None." if terminal else "- Pending until terminal transition."
    outcome = status if terminal else "Pending until terminal transition."
    return f"""---
id: {plan_id}
kind: exec-plan
format: 2
status: {status}
owner: main
area: example
created: 2026-08-31
updated: 2026-08-31
---

# Example goal

## Original goal

Deliver the example.

## Observable outcome and acceptance

- **AC-1:** The example is observable.

## Scope

- Implement the example.

## Non-goals

- No unrelated work.

## Task state

| Task | Owner | State | Depends on | Outcome | Result |
|---|---|---|---|---|---|
| T1 | implementation | complete | none | Implement | complete |

## Task Packets

{TASK_PACKET}
## Current checkpoint

T1 is integrated and the durable state is recorded.

## Exact next action

Dispatch independent verification for AC-1.

## Decisions

- Use the compact Plan schema.

## Discoveries

- None.

## Documentation impact

{documentation}

## Integration summary

{integration}

## Verification summary

{verification}

## Follow-ups

{followups}

## Outcome

{outcome}
"""


def hierarchical_compact_plan() -> str:
    rows = """| T1 | task-owner | complete | none | Decompose | complete |
| T1-A | task-owner-a | complete | T1 | Own branch | complete |
| T1-A-1 | implementation-a1 | complete | T1-A | Implement leaf | complete |"""
    packets = []
    for task_id, owner in (
        ("T1", "task-owner"),
        ("T1-A", "task-owner-a"),
        ("T1-A-1", "implementation-a1"),
    ):
        packets.append(
            TASK_PACKET.replace("### T1", f"### {task_id}").replace(
                "- **Owner:** implementation",
                f"- **Owner:** {owner}",
            )
        )
    return compact_plan().replace(
        "| T1 | implementation | complete | none | Implement | complete |",
        rows,
    ).replace(TASK_PACKET, "\n".join(packets))


EXPANDED_LEGACY_PLAN = """---
id: {plan_id}
kind: exec-plan
status: {status}
owner: main
area: example
created: 2025-01-01
updated: 2025-01-02
---

# Historical expanded Plan

## Purpose / Big Picture

Preserve the historical result without rewriting it.

## Progress

- [x] Complete the historical work.

## Acceptance Criteria

- Historical acceptance was met.

## Task Packets

### T1 — Historical implementation

#### State

complete

#### Outcome

The work shipped.

#### Result

Complete.

## Validation and Evidence

The project-owned checks passed.

## Outcomes and Retrospective

The historical goal was achieved.
"""


class PlanLifecycleTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(list(args))
        return returncode, stdout.getvalue(), stderr.getvalue()

    def install_bundle(self, root: Path) -> None:
        start_code, start_stdout, start_stderr = self.run_cli(
            "define", "start", "--root", str(root)
        )
        self.assertEqual(start_code, 0, start_stdout + start_stderr)
        preview_code, preview_stdout, preview_stderr = self.run_cli(
            "define", "finalize", "--root", str(root)
        )
        self.assertEqual(preview_code, 0, preview_stdout + preview_stderr)
        preview = json.loads(preview_stdout)
        apply_code, apply_stdout, apply_stderr = self.run_cli(
            "define",
            "finalize",
            "--root",
            str(root),
            "--apply",
            "--approve-preview",
            preview["fingerprint"],
        )
        self.assertEqual(apply_code, 0, apply_stdout + apply_stderr)

    def doctor_plan_findings(
        self,
        text: str,
        *,
        completed: bool = False,
        filename: str = "PLAN-2026-0001-example.md",
    ) -> tuple[int, list[dict[str, str]]]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_bundle(root)
            plan_directory = "completed" if completed else "active"
            path = root / f"docs/exec-plans/{plan_directory}/{filename}"
            path.write_text(text, encoding="utf-8")
            returncode, stdout, stderr = self.run_cli(
                "doctor", "--root", str(root)
            )
            self.assertTrue(stdout, stderr)
            findings = [
                finding
                for finding in json.loads(stdout)["findings"]
                if finding["path"].endswith(filename)
            ]
            return returncode, findings

    def test_document_first_plan_template_is_compact(self) -> None:
        compact = read_asset("document-first/docs/exec-plans/_template.md.tmpl")
        required = (
            "## Original goal",
            "## Observable outcome and acceptance",
            "## Task state",
            "## Task Packets",
            "## Current checkpoint",
            "## Exact next action",
            "## Decisions",
            "## Discoveries",
            "## Documentation impact",
            "## Integration summary",
            "## Verification summary",
            "## Follow-ups",
            "## Outcome",
        )
        for heading in required:
            self.assertIn(heading, compact)
        self.assertRegex(compact, r"(?m)^format: 2$")
        self.assertIn("| Task | Owner |", compact)
        self.assertIn("- **Owner:**", compact)
        for retired in (
            "verification_run:",
            "manifest_sha256:",
            "gate_verdict:",
            "Gate verdict",
            ".harness/runs",
            "./dev/",
        ):
            self.assertNotIn(retired, compact)
        self.assertLess(len(compact.splitlines()), 120)

    def test_packaged_plan_policy_defines_first_plan_handoff_without_runtime_state(self) -> None:
        packaged = read_asset("document-first/docs/PLANS.md.tmpl")
        main = read_asset("document-first/claude/skills/reporivet-main/SKILL.md.tmpl")
        for text in (packaged, main):
            lowered = text.lower()
            for phrase in (
                "active",
                "completed",
                "ordinary markdown plans",
                "resume exactly one matching active plan",
                "stop if multiple active plans match",
                "lowest unused current-year numeric id across both directories",
                "copy `_template.md`",
                "never overwrite/reuse an id",
                "visible markdown",
                "main—not package runtime—creates",
                "plan cli/hidden state/automatic dispatcher/closure",
            ):
                self.assertIn(phrase, lowered)
            self.assertRegex(lowered, r"search(?:es)? both .*active.*completed")

    def test_current_and_packaged_plan_templates_support_optional_hierarchy(self) -> None:
        packaged = read_asset("document-first/docs/exec-plans/_template.md.tmpl")
        current = (REPOSITORY / "docs/exec-plans/_template.md").read_text(
            encoding="utf-8"
        )
        current_policy = (REPOSITORY / "docs/PLANS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "| Task | Owner | State | Depends on | Parallel group | Outcome | Result |",
            packaged,
        )
        for phrase in (
            "## Broad-milestone native-Agent dispatch",
            "`T<n> (broad milestone)",
        ):
            self.assertIn(phrase, current_policy)
        for task_id in ("T1-A", "T1-B", "T1-I", "T1-V1", "T1-V2"):
            self.assertIn(f"| {task_id} |", packaged)
        for field in (
            "- **Role:**",
            "- **Parent:**",
            "- **Parallel group:**",
            "- **May delegate:**",
            "- **Inherited boundaries:**",
            "- **Return:**",
        ):
            self.assertIn(field, packaged)
        formula = (
            "`T<n> (broad milestone) -> T<n>-A/B/C/... (owned child packets, "
            "all ready leaves dispatched concurrently) -> T<n>-I (integration) -> "
            "T<n>-V1/V2/... (parallel fresh verification)`"
        )
        self.assertIn(formula, packaged)
        self.assertIn("common installed-project rule", packaged)
        self.assertIn("every milestone classified as broad", packaged)
        self.assertIn("does not apply to inherently single or serial milestones", packaged)
        self.assertIn("`T<n>-A-1`", packaged)
        self.assertIn("ordinary leaf Agents do not delegate", packaged)
        self.assertLess(len(packaged.splitlines()), 120)

    def test_doctor_accepts_simple_and_recursive_task_ids(self) -> None:
        for label, plan in (
            ("simple", compact_plan()),
            ("recursive", hierarchical_compact_plan()),
        ):
            with self.subTest(label=label):
                returncode, findings = self.doctor_plan_findings(plan)
                self.assertEqual(returncode, 0, findings)
                self.assertFalse(
                    any(finding["severity"] == "error" for finding in findings),
                    findings,
                )

    def test_recursive_task_ids_keep_exact_packet_mapping_and_owners(self) -> None:
        base = hierarchical_compact_plan()
        recursive_packet = next(
            packet
            for packet in base.split("### ")
            if packet.startswith("T1-A-1 ")
        )
        recursive_packet = "### " + recursive_packet.split("## Current checkpoint", 1)[0]
        cases = (
            (
                "duplicate recursive task row",
                base.replace(
                    "| T1-A-1 | implementation-a1 | complete | T1-A | Implement leaf | complete |",
                    "| T1-A-1 | implementation-a1 | complete | T1-A | Implement leaf | complete |\n"
                    "| T1-A-1 | implementation-a1 | complete | T1-A | Duplicate | complete |",
                ),
                "duplicate task row id T1-A-1",
            ),
            (
                "duplicate recursive Task Packet",
                base.replace(
                    recursive_packet,
                    recursive_packet + "\n" + recursive_packet,
                ),
                "duplicate Task Packet id T1-A-1",
            ),
            (
                "missing recursive Task Packet",
                base.replace(recursive_packet, ""),
                "task T1-A-1 is missing a Task Packet",
            ),
            (
                "unexpected recursive Task Packet",
                base.replace(
                    recursive_packet,
                    recursive_packet
                    + "\n"
                    + recursive_packet.replace("T1-A-1", "T1-A-2"),
                ),
                "unexpected Task Packet T1-A-2",
            ),
            (
                "missing recursive row owner",
                base.replace(
                    "| T1-A-1 | implementation-a1 | complete | T1-A | Implement leaf | complete |",
                    "| T1-A-1 |  | complete | T1-A | Implement leaf | complete |",
                ),
                "task T1-A-1 is missing an explicit Owner",
            ),
            (
                "missing recursive packet owner",
                base.replace("- **Owner:** implementation-a1\n", "", 1),
                "Task Packet T1-A-1 is missing an explicit Owner",
            ),
            (
                "recursive row and packet owner mismatch",
                base.replace(
                    "- **Owner:** implementation-a1",
                    "- **Owner:** verification-a1",
                    1,
                ),
                "task T1-A-1 row and Task Packet owners disagree",
            ),
        )
        for label, malformed, expected in cases:
            with self.subTest(label=label):
                returncode, findings = self.doctor_plan_findings(malformed)
                self.assertEqual(returncode, 2, findings)
                self.assertTrue(
                    any(expected in finding["detail"] for finding in findings),
                    findings,
                )

    def test_doctor_accepts_compact_active_and_historical_completed_plans_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_bundle(root)
            active = root / "docs/exec-plans/active/PLAN-2026-0001-example.md"
            active.write_text(
                """---
id: PLAN-2026-0001
kind: exec-plan
format: 2
status: in-progress
owner: main
area: example
created: 2026-08-31
updated: 2026-08-31
---

# Example goal

## Original goal

Deliver the example.

## Observable outcome and acceptance

- **AC-1:** The example is observable.

## Scope

- Implement the example.

## Non-goals

- No unrelated work.

## Task state

| Task | Owner | State | Depends on | Outcome | Result |
|---|---|---|---|---|---|
| T1 | implementation | ready | none | Implement | pending |

## Task Packets

### T1 — Implement

- **Owner:** implementation
- **Outcome:** Implement the example.
- **Non-goals:** No unrelated work.
- **Read:** current authority
- **Allowed writes:** example paths
- **Protected paths:** unrelated paths
- **Acceptance:** AC-1
- **Verification:** project-owned checks
- **Stop conditions:** scope conflict
- **Return:** decision-bearing evidence
- **Result:** pending

## Current checkpoint

The goal and boundary are recorded.

## Exact next action

Dispatch T1.

## Decisions

- None.

## Discoveries

- None.

## Documentation impact

- None.

## Integration summary

- pending

## Verification summary

- pending

## Follow-ups

- Pending until terminal transition.

## Outcome

Pending.
""",
                encoding="utf-8",
            )
            completed = root / "docs/exec-plans/completed/PLAN-2025-0001-history.md"
            completed.write_text(
                """---
id: PLAN-2025-0001
kind: exec-plan
status: complete
owner: main
verification_run: RUN-old
manifest_sha256: old
 gate_verdict: pass
---

# Historical Gate-era Plan

Historical fields remain readable and are not rewritten.
""",
                encoding="utf-8",
            )
            before = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }

            returncode, stdout, stderr = self.run_cli(
                "doctor", "--root", str(root)
            )
            self.assertEqual(returncode, 0, stdout + stderr)
            findings = json.loads(stdout)["findings"]
            self.assertFalse(any(finding["severity"] == "error" for finding in findings))
            after = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(after, before)

            active.write_text(active.read_text(encoding="utf-8").replace("status: in-progress", "status: complete"), encoding="utf-8")
            returncode, stdout, stderr = self.run_cli(
                "doctor", "--root", str(root)
            )
            self.assertEqual(returncode, 2, stdout + stderr)
            self.assertTrue(
                any(
                    finding["path"].endswith("PLAN-2026-0001-example.md")
                    and "invalid for this directory" in finding["detail"]
                    for finding in json.loads(stdout)["findings"]
                )
            )

    def test_doctor_rejects_unowned_and_unresolved_new_terminal_plans(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_bundle(root)
            template = read_asset("document-first/docs/exec-plans/_template.md.tmpl")
            terminal = (
                template.replace("id: PLAN-YYYY-NNNN", "id: PLAN-2026-0002")
                .replace("status: proposed", "status: complete")
            )
            path = root / "docs/exec-plans/completed/PLAN-2026-0002-malformed.md"
            path.write_text(terminal, encoding="utf-8")

            returncode, stdout, stderr = self.run_cli(
                "doctor", "--root", str(root)
            )

            self.assertEqual(returncode, 2, stdout + stderr)
            details = [
                finding["detail"]
                for finding in json.loads(stdout)["findings"]
                if finding["path"].endswith(path.name)
            ]
            self.assertTrue(any("missing an explicit Owner" in detail for detail in details))
            self.assertTrue(any("resolve Documentation impact" in detail for detail in details))
            self.assertTrue(any("resolve Follow-ups" in detail for detail in details))

    def test_strict_compact_plan_rejects_owner_resume_and_task_packet_defects(self) -> None:
        base = compact_plan()
        extra_packet = TASK_PACKET.replace("T1", "T2")
        cases = (
            (
                "missing Plan owner",
                base.replace("owner: main\n", "", 1),
                "missing an explicit Plan owner",
            ),
            (
                "placeholder Plan owner",
                base.replace("owner: main", "owner: TODO", 1),
                "missing an explicit Plan owner",
            ),
            (
                "placeholder checkpoint",
                base.replace(
                    "T1 is integrated and the durable state is recorded.",
                    "TODO: record the checkpoint.",
                ),
                "Current checkpoint is missing or placeholder",
            ),
            (
                "placeholder next action",
                base.replace(
                    "Dispatch independent verification for AC-1.",
                    "Pending.",
                ),
                "Exact next action is missing or placeholder",
            ),
            (
                "duplicate task row",
                base.replace(
                    "| T1 | implementation | complete | none | Implement | complete |",
                    "| T1 | implementation | complete | none | Implement | complete |\n"
                    "| T1 | implementation | complete | none | Duplicate | complete |",
                ),
                "duplicate task row id T1",
            ),
            (
                "duplicate Task Packet",
                base.replace(TASK_PACKET, TASK_PACKET + "\n" + TASK_PACKET),
                "duplicate Task Packet id T1",
            ),
            (
                "missing Task Packet",
                base.replace(TASK_PACKET, ""),
                "task T1 is missing a Task Packet",
            ),
            (
                "unexpected Task Packet",
                base.replace(TASK_PACKET, TASK_PACKET + "\n" + extra_packet),
                "unexpected Task Packet T2",
            ),
            (
                "missing task row owner",
                base.replace(
                    "| T1 | implementation | complete | none | Implement | complete |",
                    "| T1 |  | complete | none | Implement | complete |",
                ),
                "task T1 is missing an explicit Owner",
            ),
            (
                "placeholder task row owner",
                base.replace(
                    "| T1 | implementation | complete | none | Implement | complete |",
                    "| T1 | TODO | complete | none | Implement | complete |",
                ),
                "task T1 is missing an explicit Owner",
            ),
            (
                "missing packet owner",
                base.replace("- **Owner:** implementation\n", "", 1),
                "Task Packet T1 is missing an explicit Owner",
            ),
            (
                "placeholder packet owner",
                base.replace("- **Owner:** implementation", "- **Owner:** pending", 1),
                "Task Packet T1 is missing an explicit Owner",
            ),
            (
                "row and packet owner mismatch",
                base.replace("- **Owner:** implementation", "- **Owner:** verification", 1),
                "owners disagree",
            ),
        )
        for label, malformed, expected in cases:
            with self.subTest(label=label):
                returncode, findings = self.doctor_plan_findings(malformed)
                self.assertEqual(returncode, 2, findings)
                details = [finding["detail"] for finding in findings]
                self.assertTrue(
                    any(expected in detail for detail in details),
                    details,
                )

    def test_terminal_compact_plan_rejects_each_unresolved_summary(self) -> None:
        base = compact_plan(status="complete")
        verification = (
            "| Criterion | Candidate | Verifier | Result | Decision-bearing evidence |\n"
            "|---|---|---|---|---|\n"
            "| AC-1 | abc123 | independent | pass | focused checks passed |"
        )
        cases = (
            (
                "Documentation impact",
                base.replace("## Documentation impact\n\n- None.", "## Documentation impact\n\n- pending"),
            ),
            (
                "Integration summary",
                base.replace(
                    "- Candidate identity: commit abc123\n- Integrated changes: T1 implementation",
                    "- unresolved",
                ),
            ),
            (
                "Verification summary",
                base.replace(verification, "- TODO"),
            ),
            (
                "Follow-ups",
                base.replace("## Follow-ups\n\n- None.", "## Follow-ups\n\n- pending"),
            ),
            (
                "Outcome",
                base.replace("## Outcome\n\ncomplete", "## Outcome\n\nPending."),
            ),
        )
        for heading, malformed in cases:
            with self.subTest(heading=heading):
                returncode, findings = self.doctor_plan_findings(
                    malformed,
                    completed=True,
                )
                self.assertEqual(returncode, 2, findings)
                details = [finding["detail"] for finding in findings]
                self.assertTrue(
                    any(
                        f"terminal compact Plan must resolve {heading}" in detail
                        for detail in details
                    ),
                    details,
                )

    def test_terminal_outcome_must_match_each_terminal_status(self) -> None:
        for status in ("complete", "cancelled", "superseded"):
            with self.subTest(status=status, valid=True):
                returncode, findings = self.doctor_plan_findings(
                    compact_plan(status=status),
                    completed=True,
                )
                self.assertEqual(returncode, 0, findings)
                self.assertFalse(
                    any(finding["severity"] == "error" for finding in findings),
                    findings,
                )

            other = "cancelled" if status != "cancelled" else "superseded"
            malformed = compact_plan(status=status).replace(
                f"## Outcome\n\n{status}",
                f"## Outcome\n\n{other}",
            )
            with self.subTest(status=status, valid=False):
                returncode, findings = self.doctor_plan_findings(
                    malformed,
                    completed=True,
                )
                self.assertEqual(returncode, 2, findings)
                details = [finding["detail"] for finding in findings]
                self.assertTrue(
                    any(
                        f"Outcome must agree with terminal status '{status}'" in detail
                        for detail in details
                    ),
                    details,
                )

    def test_terminal_outcome_rejects_negated_qualified_multiple_and_prose_values(self) -> None:
        cases = (
            ("complete", "not complete"),
            ("complete", "complete later"),
            ("complete", "complete and cancelled"),
            ("complete", "The work is complete"),
            ("cancelled", "cancelled pending cleanup"),
            ("superseded", "superseded by a later Plan"),
            ("superseded", "superseded\n\ncomplete"),
        )
        for status, outcome in cases:
            with self.subTest(status=status, outcome=outcome):
                malformed = compact_plan(status=status).replace(
                    f"## Outcome\n\n{status}",
                    f"## Outcome\n\n{outcome}",
                )
                returncode, findings = self.doctor_plan_findings(
                    malformed,
                    completed=True,
                )
                self.assertEqual(returncode, 2, findings)
                self.assertTrue(
                    any(
                        f"Outcome must agree with terminal status '{status}'"
                        in finding["detail"]
                        for finding in findings
                    ),
                    findings,
                )

    def test_compact_format_marker_is_required_and_expanded_history_is_grandfathered_structurally(self) -> None:
        compact = compact_plan()
        marker_cases = (
            (
                compact.replace("format: 2\n", "", 1),
                "compact Plan is missing required format: 2",
            ),
            (
                compact.replace("format: 2", "format: 1", 1),
                "compact Plan format '1' is invalid; expected 2",
            ),
        )
        for malformed, expected in marker_cases:
            with self.subTest(expected=expected):
                returncode, findings = self.doctor_plan_findings(malformed)
                self.assertEqual(returncode, 2, findings)
                self.assertTrue(
                    any(expected in finding["detail"] for finding in findings),
                    findings,
                )

        for incidental in ("", "\nHistorical Gate and .harness/runs evidence remains readable.\n"):
            with self.subTest(incidental=bool(incidental)):
                legacy = EXPANDED_LEGACY_PLAN.format(
                    plan_id="PLAN-2025-0001",
                    status="complete",
                ) + incidental
                returncode, findings = self.doctor_plan_findings(
                    legacy,
                    completed=True,
                    filename="PLAN-2025-0001-expanded.md",
                )
                self.assertEqual(returncode, 0, findings)
                self.assertFalse(
                    any(finding["severity"] == "error" for finding in findings),
                    findings,
                )
                warnings = [
                    finding for finding in findings if finding["severity"] == "warning"
                ]
                self.assertLessEqual(len(warnings), 1, warnings)
                self.assertTrue(
                    any("grandfathered expanded Plan" in finding["detail"] for finding in warnings),
                    warnings,
                )

        active_legacy = EXPANDED_LEGACY_PLAN.format(
            plan_id="PLAN-2026-0003",
            status="in-progress",
        )
        returncode, findings = self.doctor_plan_findings(
            active_legacy,
            filename="PLAN-2026-0003-expanded.md",
        )
        self.assertEqual(returncode, 0, findings)
        self.assertFalse(
            any(finding["severity"] == "error" for finding in findings),
            findings,
        )
        self.assertTrue(
            any("reconcile it to format: 2" in finding["detail"] for finding in findings),
            findings,
        )

    def test_duplicate_plan_ids_remain_errors_across_plan_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_bundle(root)
            plan_id = "PLAN-2026-0009"
            (root / "docs/exec-plans/active/PLAN-2026-0009-active.md").write_text(
                compact_plan(plan_id=plan_id),
                encoding="utf-8",
            )
            (root / "docs/exec-plans/completed/PLAN-2026-0009-history.md").write_text(
                EXPANDED_LEGACY_PLAN.format(plan_id=plan_id, status="complete"),
                encoding="utf-8",
            )

            returncode, stdout, stderr = self.run_cli(
                "doctor", "--root", str(root)
            )
            self.assertEqual(returncode, 2, stdout + stderr)
            self.assertTrue(
                any(
                    "duplicate Plan id" in finding["detail"]
                    for finding in json.loads(stdout)["findings"]
                )
            )

    def test_current_and_packaged_agent_policy_agree_on_hierarchical_dispatch(self) -> None:
        pairs = (
            (
                (REPOSITORY / "AGENTS.md").read_text(encoding="utf-8"),
                read_asset("document-first/root/AGENTS.md.tmpl"),
            ),
            (
                (REPOSITORY / "docs/PLANS.md").read_text(encoding="utf-8"),
                read_asset("document-first/docs/PLANS.md.tmpl"),
            ),
        )
        required = (
            "`T<n> (broad milestone) -> T<n>-A/B/C/... (owned child packets, "
            "all ready leaves dispatched concurrently) -> T<n>-I (integration) -> "
            "T<n>-V1/V2/... (parallel fresh verification)`",
            "common installed-project rule",
            "every milestone classified as broad",
            "does not apply to inherently single or serial milestones",
            "If a child is itself broad",
            "`T<n>-A-1`",
            "ordinary leaf Agents do not delegate",
            "complete dependency-ready leaf set concurrently",
            "`Role: Task Owner` and `May delegate: yes`",
            "predeclared bounded descendant packets",
            "inherit parent scope, protected paths, and acceptance",
            "disjoint allowed-write sets",
            "frozen shared interfaces",
            "separate worktrees",
            "explicit integration node",
            "integrated candidate",
            "using only the host's native Agent execution",
            "no scheduler, task store, lease, lock, or automatic dispatcher",
        )
        for current, packaged in pairs:
            for phrase in required:
                self.assertIn(phrase, current)
                self.assertIn(phrase, packaged)

    def test_generated_plan_policy_keeps_main_as_serialized_owner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_bundle(root)
            policy = (root / "docs/PLANS.md").read_text(encoding="utf-8")
            self.assertIn("Main alone serializes Plan edits", policy)
            self.assertIn("active Markdown Plan", policy)
            self.assertIn("complete`, `cancelled`, or `superseded", policy)
            self.assertIn("T<n> (broad milestone)", policy)
            self.assertIn("common installed-project rule", policy)
            self.assertIn("every milestone classified as broad", policy)
            self.assertIn("does not apply to inherently single or serial milestones", policy)
            self.assertIn("complete dependency-ready leaf set concurrently", policy)
            self.assertIn("`Role: Task Owner` and `May delegate: yes`", policy)
            self.assertNotIn("./dev/", policy)
            self.assertNotIn(".harness/runs", policy)
            self.assertNotIn("Gate verdict", policy)


if __name__ == "__main__":
    unittest.main()
