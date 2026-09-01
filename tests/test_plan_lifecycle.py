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


STRICT_TASK_HEADER = "| Task | Owner | State | Depends on | Parallel group | Outcome | Result |"
STRICT_TASK_SEPARATOR = "|---|---|---|---|---|---|---|"
STRICT_ROW_FIELDS = (
    "Task",
    "Owner",
    "State",
    "Depends on",
    "Parallel group",
    "Outcome",
    "Result",
)
STRICT_PACKET_FIELDS = (
    "Owner",
    "Role",
    "Parent",
    "Parallel group",
    "May delegate",
    "Inherited boundaries",
    "Outcome",
    "Non-goals",
    "Read",
    "Allowed writes",
    "Protected paths",
    "Acceptance",
    "Verification",
    "Stop conditions",
    "Return",
    "Result",
)

# task id, row owner, state, dependencies, row group, row outcome, row result,
# packet role, packet parent, packet group, packet delegation
STRICT_HIERARCHY_TASKS = (
    ("T1", "owner-root", "complete", "none", "root-owners", "Own subtree", "complete", "Task Owner", "none", "root-owners", "yes"),
    ("T1-A", "impl-a", "complete", "none", "T1-leaves", "Implement A", "complete", "leaf", "T1", "T1-leaves", "no"),
    ("T1-B", "owner-b", "complete", "T1-B-1", "T1-leaves", "Own nested subtree", "complete", "Task Owner", "T1", "T1-leaves", "yes"),
    ("T1-B-1", "impl-b1", "complete", "none", "T1-B-leaves", "Implement nested leaf", "complete", "leaf", "T1-B", "T1-B-leaves", "no"),
    ("T1-B-I", "integrator-b", "complete", "T1-B-1", "T1-B-integration", "Integrate nested leaf", "complete", "integration", "T1-B", "T1-B-integration", "no"),
    ("T1-I", "integrator-root", "complete", "T1-A, T1-B, T1-B-I", "T1-integration", "Integrate subtree", "complete", "integration", "T1", "T1-integration", "no"),
    ("T1-V", "verifier", "complete", "T1-I", "verification", "Verify subtree", "complete", "verification", "T1", "verification", "no"),
)

STRICT_ROOT_INTEGRATION_TASKS = (
    ("T5", "owner-root", "complete", "none", "root-owners", "Own root subtree", "complete", "Task Owner", "none", "root-owners", "yes"),
    ("T5-A", "impl-a", "complete", "none", "implementation", "Implement A", "complete", "leaf", "T5", "implementation", "no"),
    ("T5-I", "integrator", "complete", "T5-A, T5-B", "integration", "Integrate candidate", "complete", "integration", "T5", "integration", "no"),
    ("T5-B", "impl-b", "complete", "none", "implementation", "Later unrelated leaf", "complete", "leaf", "T5", "implementation", "no"),
    ("T5-V", "verifier", "complete", "T5-I", "verification", "Verify candidate", "complete", "verification", "T5", "verification", "no"),
)


def strict_task_row(task: tuple[str, ...]) -> str:
    task_id, owner, state, depends_on, group, outcome, result, *_ = task
    return f"| {task_id} | {owner} | {state} | {depends_on} | {group} | {outcome} | {result} |"


def strict_task_packet(task: tuple[str, ...]) -> str:
    task_id, owner, _state, _depends_on, _group, _outcome, _result, role, parent, packet_group, may_delegate = task
    return f"""### {task_id} — Strict task {task_id}

- **Owner:** {owner}
- **Role:** {role}
- **Parent:** {parent}
- **Parallel group:** {packet_group}
- **May delegate:** {may_delegate}
- **Inherited boundaries:** frozen strict graph contract and inherited task boundaries.
- **Outcome:** Packet-specific bounded work for {task_id}.
- **Non-goals:** No unrelated work.
- **Read:** current authority
- **Allowed writes:** bounded task paths
- **Protected paths:** unrelated paths
- **Acceptance:** AC-6
- **Verification:** project-owned checks
- **Stop conditions:** scope conflict
- **Return:** decision-bearing evidence
- **Result:** Packet evidence intentionally differs from the row result.
"""


def strict_plan(
    tasks: tuple[tuple[str, ...], ...],
    *,
    plan_id: str = "PLAN-2026-0010",
    task_graph: str | None = "1",
) -> str:
    marker = "" if task_graph is None else f"task_graph: {task_graph}\n"
    rows = "\n".join(strict_task_row(task) for task in tasks)
    packets = "\n".join(strict_task_packet(task) for task in tasks)
    return f"""---
id: {plan_id}
kind: exec-plan
format: 2
{marker}status: in-progress
owner: main
area: strict-graph
created: 2026-09-01
updated: 2026-09-01
---

# Strict graph test Plan

## Original goal

Exercise the strict task graph contract.

## Observable outcome and acceptance

- **AC-6:** Doctor validates strict task graph semantics.

## Scope

- Validate the declared task graph.

## Non-goals

- No unrelated work.

## Task state

{STRICT_TASK_HEADER}
{STRICT_TASK_SEPARATOR}
{rows}

## Task Packets

{packets}
## Current checkpoint

The strict graph candidate is recorded for validation.

## Exact next action

Run the focused strict graph doctor checks.

## Decisions

- Use the frozen strict task graph contract.

## Discoveries

- None.

## Documentation impact

- None.

## Integration summary

- Pending until integration.

## Verification summary

- Pending until verification.

## Follow-ups

- Pending until terminal transition.

## Outcome

Pending until terminal transition.
"""


def strict_hierarchy_plan(*, task_graph: str | None = "1") -> str:
    return strict_plan(STRICT_HIERARCHY_TASKS, task_graph=task_graph)


def strict_direct_serial_plan(*, task_graph: str | None = "1") -> str:
    return strict_plan(
        (
            ("T2", "serial-owner", "complete", "none", "none", "Perform serial work", "complete", "leaf", "none", "none", "no"),
        ),
        plan_id="PLAN-2026-0011",
        task_graph=task_graph,
    )


def strict_childless_owner_plan() -> str:
    return strict_plan(
        (
            ("T3", "owner-only", "complete", "none", "none", "Own one bounded task", "complete", "Task Owner", "none", "none", "yes"),
        ),
        plan_id="PLAN-2026-0012",
    )


def strict_dependency_plan(*, blocked: bool = True) -> str:
    dependent_state = "blocked" if blocked else "ready"
    return strict_plan(
        (
            ("T4", "owner-root", "complete", "none", "root-owners", "Own dependency subtree", "complete", "Task Owner", "none", "root-owners", "yes"),
            ("T4-A", "impl-a", "in-progress", "none", "serial", "Implement prerequisite", "pending", "leaf", "T4", "serial", "no"),
            ("T4-B", "impl-b", dependent_state, "T4-A", "serial", "Implement dependent", "pending", "leaf", "T4", "serial", "no"),
        ),
        plan_id="PLAN-2026-0013",
    )


def strict_root_integration_plan() -> str:
    return strict_plan(STRICT_ROOT_INTEGRATION_TASKS, plan_id="PLAN-2026-0014")


def replace_strict_row_cell(text: str, task_id: str, field: str, value: str) -> str:
    lines = text.splitlines()
    try:
        index = lines.index(STRICT_TASK_HEADER)
    except ValueError as exc:
        raise AssertionError("strict task header not found") from exc
    columns = [cell.strip() for cell in STRICT_TASK_HEADER.strip("|").split("|")]
    field_index = columns.index(field)
    for row_index in range(index + 2, len(lines)):
        row = lines[row_index]
        if row.startswith(f"| {task_id} |"):
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            cells[field_index] = value
            lines[row_index] = "| " + " | ".join(cells) + " |"
            return "\n".join(lines) + "\n"
    raise AssertionError(f"strict task row not found: {task_id}")


def replace_strict_packet_field(text: str, task_id: str, field: str, value: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if line.startswith(f"### {task_id} —")
        ),
        None,
    )
    if start is None:
        raise AssertionError(f"strict packet not found: {task_id}")
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("### ")
            or lines[index].startswith("## Current checkpoint")
        ),
        len(lines),
    )
    matches = [
        index
        for index in range(start + 1, end)
        if lines[index].startswith(f"- **{field}:**")
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected one {field} field in {task_id}, found {len(matches)}")
    lines[matches[0]] = f"- **{field}:** {value}\n"
    return "".join(lines)


def remove_strict_packet_field(text: str, task_id: str, field: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if line.startswith(f"### {task_id} —")
        ),
        None,
    )
    if start is None:
        raise AssertionError(f"strict packet not found: {task_id}")
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("### ")
            or lines[index].startswith("## Current checkpoint")
        ),
        len(lines),
    )
    matches = [
        index
        for index in range(start + 1, end)
        if lines[index].startswith(f"- **{field}:")
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected one {field} field in {task_id}, found {len(matches)}")
    del lines[matches[0]]
    return "".join(lines)


def duplicate_strict_packet_field(text: str, task_id: str, field: str, value: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if line.startswith(f"### {task_id} —")
        ),
        None,
    )
    if start is None:
        raise AssertionError(f"strict packet not found: {task_id}")
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("### ")
            or lines[index].startswith("## Current checkpoint")
        ),
        len(lines),
    )
    matches = [
        index
        for index in range(start + 1, end)
        if lines[index].startswith(f"- **{field}:**")
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected one {field} field in {task_id}, found {len(matches)}")
    lines.insert(matches[0] + 1, f"- **{field}:** {value}\n")
    return "".join(lines)


def add_strict_task(text: str, task: tuple[str, ...]) -> str:
    row_marker = f"{STRICT_TASK_SEPARATOR}\n"
    if row_marker not in text:
        raise AssertionError("strict row separator not found")
    text = text.replace(row_marker, row_marker + strict_task_row(task) + "\n", 1)
    checkpoint = "## Current checkpoint"
    packet = strict_task_packet(task)
    if checkpoint not in text:
        raise AssertionError("strict checkpoint not found")
    return text.replace(checkpoint, packet + "\n" + checkpoint, 1)


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

    def assert_strict_plan_is_valid(self, text: str) -> None:
        returncode, findings = self.doctor_plan_findings(text)
        self.assertEqual(returncode, 0, findings)
        self.assertFalse(
            any(finding["severity"] == "error" for finding in findings),
            findings,
        )
        self.assertTrue(
            all(
                finding["path"] == "docs/exec-plans/active/PLAN-2026-0001-example.md"
                for finding in findings
            ),
            findings,
        )

    def assert_strict_plan_has_error(
        self,
        text: str,
        *expected_fragments: str,
    ) -> list[dict[str, str]]:
        returncode, findings = self.doctor_plan_findings(text)
        self.assertEqual(returncode, 2, findings)
        self.assertTrue(
            any(
                all(fragment in finding["detail"] for fragment in expected_fragments)
                for finding in findings
            ),
            findings,
        )
        self.assertTrue(findings)
        self.assertTrue(
            all(
                finding["path"] == "docs/exec-plans/active/PLAN-2026-0001-example.md"
                for finding in findings
            ),
            findings,
        )
        return findings

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
        self.assertIn("task_graph: 1", current_policy)
        self.assertIn("`T<n> (broad root Owner)", current_policy)

        for template in (current, packaged):
            self.assertRegex(template, r"(?m)^format: 2$")
            self.assertRegex(template, r"(?m)^task_graph: 1$")
            self.assertTrue(
                "`T<n> (broad root Owner)" in template
                or "Broad or multi-part roots default to `Role: Task Owner`"
                in template,
                template,
            )
            self.assertTrue(
                "declared child packets" in template
                or "every row requires one matching bounded packet" in template
                or "every child row requires one matching bounded packet" in template,
                template,
            )
            self.assertTrue(
                "Owner-local aggregation" in template
                or "Owner locally aggregates descendant results" in template,
                template,
            )
            self.assertTrue(
                "finite child manifest" in template
                or "finite accepted manifest" in template,
                template,
            )
            self.assertTrue(
                "dependency-ready descendants" in template,
                template,
            )
            for field in (
                "- **Role:**",
                "- **Parent:**",
                "- **Parallel group:**",
                "- **May delegate:**",
                "- **Inherited boundaries:**",
                "- **Return:**",
            ):
                self.assertIn(field, template)

        for task_id in ("T1-A", "T1-B", "T1-I", "T1-V1", "T1-V2"):
            self.assertIn(f"| {task_id} |", packaged)
        self.assertIn("`T<n>-A-1`", packaged)
        self.assertIn("ordinary leaf Agents do not delegate", packaged)
        self.assertLess(len(packaged.splitlines()), 120)

    def test_strict_hierarchy_and_direct_serial_fixtures_are_valid(self) -> None:
        for label, plan in (
            ("nested hierarchy", strict_hierarchy_plan()),
            ("root integration with unrelated later leaf", strict_root_integration_plan()),
            ("direct serial leaf", strict_direct_serial_plan()),
            ("childless Task Owner", strict_childless_owner_plan()),
            ("blocked dependency", strict_dependency_plan(blocked=True)),
        ):
            with self.subTest(label=label):
                self.assert_strict_plan_is_valid(plan)

    def test_strict_task_graph_marker_is_opt_in_and_invalid_marker_suppresses_graph_checks(self) -> None:
        unmarked = strict_hierarchy_plan(task_graph=None)
        self.assert_strict_plan_is_valid(unmarked)
        unmarked_semantically_malformed = replace_strict_packet_field(
            unmarked, "T1-A", "Role", "review"
        )
        self.assert_strict_plan_is_valid(unmarked_semantically_malformed)

        quoted = strict_hierarchy_plan(task_graph='"1"')
        self.assert_strict_plan_is_valid(quoted)

        malformed = strict_hierarchy_plan(task_graph="2")
        returncode, findings = self.doctor_plan_findings(malformed)
        self.assertEqual(returncode, 2, findings)
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("task_graph", findings[0]["detail"])
        self.assertEqual(
            findings[0]["path"],
            "docs/exec-plans/active/PLAN-2026-0001-example.md",
        )

    def test_strict_rows_require_every_frozen_column(self) -> None:
        base = strict_hierarchy_plan()
        for field in STRICT_ROW_FIELDS:
            with self.subTest(field=field):
                header = "| " + " | ".join(
                    column for column in STRICT_ROW_FIELDS if column != field
                ) + " |"
                malformed = base.replace(STRICT_TASK_HEADER, header, 1)
                self.assert_strict_plan_has_error(malformed, field)

    def test_strict_packets_require_every_bounded_and_hierarchy_field(self) -> None:
        base = strict_hierarchy_plan()
        for field in STRICT_PACKET_FIELDS:
            with self.subTest(field=field):
                malformed = (
                    replace_strict_packet_field(base, "T1-B", field, "")
                    if field == "Owner"
                    else remove_strict_packet_field(base, "T1-B", field)
                )
                expected = "owners disagree" if field == "Owner" else field
                self.assert_strict_plan_has_error(malformed, "T1-B", expected)

    def test_strict_packet_hierarchy_fields_must_be_unique(self) -> None:
        base = strict_hierarchy_plan()
        values = {
            "Role": "leaf",
            "Parent": "none",
            "Parallel group": "other-group",
            "May delegate": "no",
        }
        for field, duplicate in values.items():
            with self.subTest(field=field):
                malformed = duplicate_strict_packet_field(
                    base, "T1-B", field, duplicate
                )
                self.assert_strict_plan_has_error(malformed, "T1-B", field)

    def test_strict_roles_and_delegation_are_canonical_and_bounded(self) -> None:
        canonical_case = replace_strict_packet_field(
            replace_strict_packet_field(
                replace_strict_packet_field(
                    replace_strict_packet_field(
                        strict_hierarchy_plan(),
                        "T1-A",
                        "Role",
                        "LEAF",
                    ),
                    "T1-A",
                    "May delegate",
                    "NO",
                ),
                "T1-B",
                "Role",
                "TASK OWNER",
            ),
            "T1-B",
            "May delegate",
            "YES",
        )
        self.assert_strict_plan_is_valid(canonical_case)

        cases = (
            ("invalid role", "T1-A", "Role", "review", "Role"),
            ("leaf may delegate", "T1-A", "May delegate", "yes", "May delegate"),
            ("integration may delegate", "T1-B-I", "May delegate", "yes", "May delegate"),
            ("verification may delegate", "T1-V", "May delegate", "yes", "May delegate"),
            ("owner may not delegate", "T1-B", "May delegate", "no", "May delegate"),
        )
        for label, task_id, field, value, expected in cases:
            with self.subTest(label=label):
                malformed = replace_strict_packet_field(
                    strict_hierarchy_plan(), task_id, field, value
                )
                self.assert_strict_plan_has_error(malformed, task_id, expected)

        self.assert_strict_plan_is_valid(strict_childless_owner_plan())

    def test_strict_parent_must_be_none_at_root_and_exact_immediate_prefix_elsewhere(self) -> None:
        cases = (
            ("root has parent", "T1", "T1-A"),
            ("missing parent", "T1-B-1", "T1-MISSING"),
            ("non-immediate existing parent", "T1-B-1", "T1"),
            ("wrong lexical branch", "T1-B-1", "T1-A"),
            ("case-sensitive parent", "T1-B-1", "t1-b"),
            ("non-sentinel empty value", "T1-A", "-"),
        )
        for label, task_id, parent in cases:
            with self.subTest(label=label):
                malformed = replace_strict_packet_field(
                    strict_hierarchy_plan(), task_id, "Parent", parent
                )
                self.assert_strict_plan_has_error(malformed, task_id, "Parent")

        empty_group = replace_strict_packet_field(
            strict_direct_serial_plan(), "T2", "Parallel group", "-"
        )
        self.assert_strict_plan_has_error(empty_group, "T2", "group")

    def test_strict_owner_and_parallel_group_parity_is_exact_but_prose_need_not_match(self) -> None:
        # The fixture deliberately gives packets different Outcome and Result prose.
        self.assert_strict_plan_is_valid(strict_hierarchy_plan())

        owner_mismatch = replace_strict_packet_field(
            strict_hierarchy_plan(), "T1-B", "Owner", "other-owner"
        )
        findings = self.assert_strict_plan_has_error(
            owner_mismatch,
            "task T1-B row and Task Packet owners disagree",
        )
        self.assertEqual(
            sum(
                finding["detail"] == "compact Plan task T1-B row and Task Packet owners disagree"
                for finding in findings
            ),
            1,
            findings,
        )

        group_mismatch = replace_strict_packet_field(
            strict_hierarchy_plan(), "T1-B", "Parallel group", "other-group"
        )
        self.assert_strict_plan_has_error(group_mismatch, "T1-B", "group")

    def test_strict_dependencies_reject_blank_malformed_mixed_none_duplicate_missing_self_and_case_aliases(self) -> None:
        cases = (
            ("blank dependency", "T1-B-I", "T1-B-1,,T1-A", "T1-B-I", "dep"),
            ("mixed none", "T1-B-I", "none,T1-B-1", "T1-B-I", "none"),
            (
                "malformed delimiter",
                "T1-I",
                "T1-A;T1-B;T1-B-I",
                "T1-I",
                "Depends on contains malformed Task ID 'T1-A;T1-B;T1-B-I'",
            ),
            ("duplicate dependency", "T1-I", "T1-A, T1-A, T1-B, T1-B-I", "T1-I", "duplicate"),
            ("missing dependency", "T1-I", "T1-A, T1-MISSING, T1-B, T1-B-I", "T1-I", "T1-MISSING"),
            ("self dependency", "T1-B-I", "T1-B-I", "T1-B-I", "self"),
            ("case-sensitive id", "T1-I", "t1-a, T1-B, T1-B-I", "T1-I", "t1-a"),
            ("empty dependency", "T1-B-I", "", "T1-B-I", "dep"),
            (
                "non-sentinel empty value",
                "T1-B-I",
                "-",
                "T1-B-I",
                "Depends on contains malformed Task ID '-'",
            ),
        )
        for label, task_id, depends_on, expected_task, expected in cases:
            with self.subTest(label=label):
                malformed = replace_strict_row_cell(
                    strict_hierarchy_plan(), task_id, "Depends on", depends_on
                )
                self.assert_strict_plan_has_error(malformed, expected_task, expected)

    def test_strict_dependency_cycles_are_reported_without_rewriting_parent_edges(self) -> None:
        malformed = replace_strict_row_cell(
            strict_hierarchy_plan(), "T1-B-1", "Depends on", "T1-B-I"
        )
        self.assert_strict_plan_has_error(malformed, "T1-B-1", "cycle")

        # Parent remains the declared lexical hierarchy even when dependencies cycle.
        self.assertIn(
            "- **Parent:** T1-B\n",
            replace_strict_packet_field(malformed, "T1-B-1", "Result", "cycle evidence"),
        )

    def test_strict_state_and_result_mapping_is_enforced(self) -> None:
        for state, result in (
            ("ready", "pending"),
            ("in-progress", "pending"),
            ("complete", "complete"),
            ("cancelled", "cancelled"),
            ("superseded", "superseded"),
        ):
            with self.subTest(valid_state=state, valid_result=result):
                valid = replace_strict_row_cell(
                    replace_strict_row_cell(
                        strict_direct_serial_plan(), "T2", "State", state
                    ),
                    "T2",
                    "Result",
                    result,
                )
                self.assert_strict_plan_is_valid(valid)

        self.assert_strict_plan_is_valid(strict_dependency_plan(blocked=True))

        for state, result in (
            ("ready", "complete"),
            ("in-progress", "complete"),
            ("complete", "pending"),
            ("cancelled", "complete"),
            ("superseded", "pending"),
            ("blocked", "complete"),
        ):
            with self.subTest(state=state, result=result):
                malformed = replace_strict_row_cell(
                    replace_strict_row_cell(
                        strict_direct_serial_plan(), "T2", "State", state
                    ),
                    "T2",
                    "Result",
                    result,
                )
                self.assert_strict_plan_has_error(malformed, "T2", "Result")

        invalid_state = replace_strict_row_cell(
            strict_direct_serial_plan(), "T2", "State", "queued"
        )
        self.assert_strict_plan_has_error(invalid_state, "T2", "State")

        invalid_result = replace_strict_row_cell(
            strict_direct_serial_plan(), "T2", "Result", "waiting"
        )
        self.assert_strict_plan_has_error(invalid_result, "T2", "Result")

        verifying_leaf = replace_strict_row_cell(
            replace_strict_row_cell(
                strict_hierarchy_plan(), "T1-A", "State", "verifying"
            ),
            "T1-A",
            "Result",
            "pending",
        )
        self.assert_strict_plan_has_error(verifying_leaf, "T1-A", "verifying")

        verifying_task = replace_strict_row_cell(
            replace_strict_row_cell(
                strict_hierarchy_plan(), "T1-V", "State", "verifying"
            ),
            "T1-V",
            "Result",
            "pending",
        )
        self.assert_strict_plan_is_valid(verifying_task)

    def test_strict_runnable_and_complete_tasks_require_complete_dependencies(self) -> None:
        self.assert_strict_plan_is_valid(strict_dependency_plan(blocked=True))

        runnable_with_pending_dependency = strict_dependency_plan(blocked=False)
        self.assert_strict_plan_has_error(
            runnable_with_pending_dependency, "T4-B", "blocked"
        )

        in_progress_with_pending_dependency = replace_strict_row_cell(
            strict_dependency_plan(blocked=True), "T4-B", "State", "in-progress"
        )
        self.assert_strict_plan_has_error(
            in_progress_with_pending_dependency, "T4-B", "blocked"
        )

        blocked_with_complete_dependency = replace_strict_row_cell(
            replace_strict_row_cell(
                strict_dependency_plan(blocked=True), "T4-A", "State", "complete"
            ),
            "T4-A",
            "Result",
            "complete",
        )
        # The frozen contract does not require promoting an already blocked task.
        self.assert_strict_plan_is_valid(blocked_with_complete_dependency)

        complete_with_pending_dependency = replace_strict_row_cell(
            replace_strict_row_cell(
                strict_dependency_plan(blocked=True), "T4-B", "State", "complete"
            ),
            "T4-B",
            "Result",
            "complete",
        )
        self.assert_strict_plan_has_error(
            complete_with_pending_dependency,
            "T4-B",
            "must remain blocked until dependencies complete",
        )

    def test_strict_integration_ordering_and_descendant_rules_are_enforced(self) -> None:
        self.assert_strict_plan_is_valid(strict_hierarchy_plan())
        self.assert_strict_plan_is_valid(strict_root_integration_plan())

        local_sibling_missing = replace_strict_row_cell(
            strict_hierarchy_plan(), "T1-B-I", "Depends on", "T1-A"
        )
        self.assert_strict_plan_has_error(
            local_sibling_missing, "T1-B-I", "T1-B-1"
        )

        no_implementation_dependency = replace_strict_row_cell(
            strict_hierarchy_plan(), "T1-B-I", "Depends on", "none"
        )
        self.assert_strict_plan_has_error(
            no_implementation_dependency, "T1-B-I", "implementation"
        )

        verification_dependency = replace_strict_row_cell(
            strict_hierarchy_plan(), "T1-B-I", "Depends on", "T1-V"
        )
        self.assert_strict_plan_has_error(
            verification_dependency, "T1-B-I", "verification"
        )

        integration_with_descendant = add_strict_task(
            strict_hierarchy_plan(),
            (
                "T1-B-I-A",
                "impl-extra",
                "complete",
                "none",
                "T1-B-I-leaves",
                "Invalid integration child",
                "complete",
                "leaf",
                "T1-B-I",
                "T1-B-I-leaves",
                "no",
            ),
        )
        self.assert_strict_plan_has_error(
            integration_with_descendant, "T1-B-I", "descendant"
        )

        integration_delegation = replace_strict_packet_field(
            strict_hierarchy_plan(), "T1-B-I", "May delegate", "yes"
        )
        self.assert_strict_plan_has_error(
            integration_delegation, "T1-B-I", "May delegate"
        )

    def test_strict_verification_ordering_state_and_descendant_rules_are_enforced(self) -> None:
        self.assert_strict_plan_is_valid(strict_root_integration_plan())

        direct_leaf_dependency = replace_strict_row_cell(
            strict_hierarchy_plan(), "T1-V", "Depends on", "T1-A"
        )
        self.assert_strict_plan_has_error(
            direct_leaf_dependency, "T1-V", "integration"
        )

        no_integration_dependency = replace_strict_row_cell(
            strict_hierarchy_plan(), "T1-V", "Depends on", "none"
        )
        self.assert_strict_plan_has_error(
            no_integration_dependency, "T1-V", "integration"
        )

        verification_delegation = replace_strict_packet_field(
            strict_hierarchy_plan(), "T1-V", "May delegate", "yes"
        )
        self.assert_strict_plan_has_error(
            verification_delegation, "T1-V", "May delegate"
        )

        verification_with_descendant = add_strict_task(
            strict_hierarchy_plan(),
            (
                "T1-V-A",
                "impl-extra",
                "complete",
                "none",
                "verification-child",
                "Invalid verification child",
                "complete",
                "leaf",
                "T1-V",
                "verification-child",
                "no",
            ),
        )
        self.assert_strict_plan_has_error(
            verification_with_descendant, "T1-V", "descendant"
        )

        verification_before_integration = replace_strict_row_cell(
            replace_strict_row_cell(
                replace_strict_row_cell(
                    strict_hierarchy_plan(), "T1-I", "State", "in-progress"
                ),
                "T1-I",
                "Result",
                "pending",
            ),
            "T1-V",
            "State",
            "ready",
        )
        verification_before_integration = replace_strict_row_cell(
            verification_before_integration, "T1-V", "Result", "pending"
        )
        self.assert_strict_plan_has_error(
            verification_before_integration, "T1-V", "blocked"
        )

        complete_verification_before_integration = replace_strict_row_cell(
            replace_strict_row_cell(
                replace_strict_row_cell(
                    strict_hierarchy_plan(), "T1-I", "State", "in-progress"
                ),
                "T1-I",
                "Result",
                "pending",
            ),
            "T1-V",
            "State",
            "complete",
        )
        self.assert_strict_plan_has_error(
            complete_verification_before_integration, "T1-V", "dep"
        )

    def test_non_task_owner_packets_cannot_have_descendants(self) -> None:
        for role in ("leaf", "integration", "verification"):
            with self.subTest(role=role):
                malformed = replace_strict_packet_field(
                    replace_strict_packet_field(
                        strict_hierarchy_plan(), "T1-B", "Role", role
                    ),
                    "T1-B",
                    "May delegate",
                    "no",
                )
                self.assert_strict_plan_has_error(
                    malformed, "T1-B", "May delegate"
                )

    def test_strict_findings_are_plan_relative_task_specific_and_suppress_prerequisite_cascades(self) -> None:
        malformed = replace_strict_row_cell(
            strict_hierarchy_plan(), "T1-A", "Depends on", "T1-MISSING"
        )
        findings = self.assert_strict_plan_has_error(
            malformed, "T1-A", "T1-MISSING"
        )
        details = [finding["detail"] for finding in findings]
        self.assertFalse(any("T1-I" in detail for detail in details), details)
        self.assertFalse(any("cycle" in detail.casefold() for detail in details), details)

    def test_strict_direct_serial_and_unmarked_recursive_compatibility_remain_supported(self) -> None:
        self.assert_strict_plan_is_valid(strict_direct_serial_plan(task_graph=None))
        returncode, findings = self.doctor_plan_findings(hierarchical_compact_plan())
        self.assertEqual(returncode, 0, findings)
        self.assertFalse(
            any(finding["severity"] == "error" for finding in findings),
            findings,
        )

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
            "disjoint allowed-write sets",
            "integrated candidate",
        )
        for current, packaged in pairs:
            for policy in (current, packaged):
                policy_lower = policy.casefold()
                self.assertTrue(
                    "`t<n> (broad root owner)" in policy_lower
                    or "broad or multi-part roots default to `role: task owner`"
                    in policy_lower,
                    policy,
                )
                self.assertTrue(
                    "`role: task owner` and `may delegate: yes`" in policy_lower
                    or "`role: task owner` with `may delegate: yes`" in policy_lower,
                    policy,
                )
                self.assertTrue(
                    "frozen shared interfaces" in policy_lower
                    or "frozen interfaces" in policy_lower,
                    policy,
                )
                self.assertTrue(
                    "separate worktrees" in policy_lower
                    or "separate exact-baseline worktrees" in policy_lower,
                    policy,
                )
                self.assertTrue(
                    "no scheduler, task store, lease, lock, or automatic dispatcher"
                    in policy_lower
                    or "no scheduler, dispatcher, task store, lease, lock" in policy_lower,
                    policy,
                )
                self.assertTrue(
                    "declared child packets" in policy_lower
                    or "every child row retains an explicit owner and matching bounded packet"
                    in policy_lower,
                    policy,
                )
                self.assertTrue(
                    "owner-local aggregation" in policy_lower
                    or "local aggregation of descendant results" in policy_lower,
                    policy,
                )
                self.assertTrue(
                    "finite child manifest" in policy_lower
                    or "finite accepted manifest" in policy_lower,
                    policy,
                )
                self.assertTrue(
                    "main alone serializes" in policy_lower
                    or "main serializes" in policy_lower,
                    policy,
                )
                self.assertTrue(
                    "resumes that serialized owner" in policy_lower
                    or "resuming an owner" in policy_lower,
                    policy,
                )
                self.assertTrue(
                    "declared dependency-ready descendants" in policy_lower
                    or "complete dependency-ready descendants" in policy_lower,
                    policy,
                )
                self.assertTrue(
                    "ordinary leaf agents never delegate" in policy_lower
                    or "ordinary leaf agents do not delegate" in policy_lower,
                    policy,
                )
                for phrase in required:
                    self.assertIn(phrase, policy)
            for policy in (current, packaged):
                self.assertTrue(
                    "using only the host's native Agent execution" in policy
                    or "through host-native Agent execution" in policy,
                    policy,
                )
            self.assertTrue(
                "Descendants inherit the parent's scope, acceptance, non-goals, protected paths"
                in current
                or "Descendants inherit parent scope, protected paths, acceptance"
                in current,
                current,
            )
            self.assertTrue(
                "Descendants inherit the parent's scope, acceptance, non-goals, protected paths"
                in packaged
                or "Descendants inherit parent scope, protected paths, acceptance"
                in packaged,
                packaged,
            )

    def test_generated_plan_policy_keeps_main_as_serialized_owner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.install_bundle(root)
            policy = (root / "docs/PLANS.md").read_text(encoding="utf-8")
            self.assertIn("Main alone serializes Plan edits", policy)
            self.assertIn("active Markdown Plan", policy)
            self.assertIn("complete`, `cancelled`, or `superseded", policy)
            self.assertIn(
                "Broad or multi-part roots default to `Role: Task Owner` and `May delegate: yes`",
                policy,
            )
            self.assertIn("common installed-project rule", policy)
            self.assertIn("every milestone classified as broad", policy)
            self.assertIn("does not apply to inherently single or serial milestones", policy)
            self.assertIn(
                "Main dispatches the complete dependency-ready root set concurrently",
                policy,
            )
            self.assertIn(
                "A resumed Owner dispatches its complete dependency-ready descendants",
                policy,
            )
            self.assertNotIn("complete dependency-ready leaf set concurrently", policy)
            self.assertNotIn("./dev/", policy)
            self.assertNotIn(".harness/runs", policy)
            self.assertNotIn("Gate verdict", policy)


if __name__ == "__main__":
    unittest.main()
