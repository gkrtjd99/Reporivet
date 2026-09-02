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

- **AC-6:** The declared Task Owner hierarchy is recorded for host-native execution.

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

Resume the declared strict graph workflow through host-native Agent execution.

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
        lowered = packaged.lower()
        for phrase in (
            "active and completed history",
            "resumes exactly one matching active ordinary markdown plan",
            "stops on ambiguity",
            "lowest unused current-year id",
            "without overwriting an existing file",
            "main and the host/project own plan edits",
            "every shared plan mutation and manual movement between plan directories",
            "no scheduler, dispatcher, task store, lease, lock, command runner, gate, evidence archive, automatic closure, hidden state",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lowered)
        self.assertIn("task_graph: 1", lowered)
        self.assertIn("unmarked compact plans retain structural validation", lowered)
        self.assertNotIn("reporivet-main", lowered)

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

    def test_strict_hierarchy_and_direct_serial_fixtures_serialize_current_plan_contract(self) -> None:
        cases = (
            ("nested hierarchy", strict_hierarchy_plan(), STRICT_HIERARCHY_TASKS),
            ("root integration", strict_root_integration_plan(), STRICT_ROOT_INTEGRATION_TASKS),
            (
                "direct serial leaf",
                strict_direct_serial_plan(),
                (("T2",),),
            ),
            ("childless Task Owner", strict_childless_owner_plan(), (("T3",),)),
            (
                "blocked dependency",
                strict_dependency_plan(blocked=True),
                (("T4",), ("T4-A",), ("T4-B",)),
            ),
        )
        for label, plan, tasks in cases:
            with self.subTest(label=label):
                self.assertRegex(plan, r"(?m)^format: 2$")
                self.assertIn("## Task state", plan)
                self.assertIn("## Task Packets", plan)
                self.assertIn("## Current checkpoint", plan)
                self.assertTrue(plan.endswith("\n"))
                for task in tasks:
                    task_id = task[0]
                    self.assertIn(f"| {task_id} |", plan)
                    self.assertIn(f"### {task_id} —", plan)

        hierarchy = strict_hierarchy_plan()
        self.assertIn("task_graph: 1", hierarchy)
        self.assertIn("- **Role:** Task Owner", hierarchy)
        self.assertIn("- **May delegate:** yes", hierarchy)
        serial = strict_direct_serial_plan()
        self.assertIn("- **Role:** leaf", serial)
        self.assertIn("- **May delegate:** no", serial)

    def test_task_graph_marker_is_opt_in_and_compatibility_is_documented(self) -> None:
        marked = strict_hierarchy_plan()
        unmarked = strict_hierarchy_plan(task_graph=None)
        self.assertIn("task_graph: 1", marked)
        self.assertNotIn("task_graph:", unmarked)
        self.assertEqual(unmarked, marked.replace("task_graph: 1\n", "", 1))

        alternate_marker = strict_hierarchy_plan(task_graph="2")
        self.assertIn("task_graph: 2", alternate_marker)
        self.assertIn("## Task state", alternate_marker)
        self.assertIn("## Task Packets", alternate_marker)

        policy = (REPOSITORY / "docs/PLANS.md").read_text(encoding="utf-8")
        for phrase in (
            "`task_graph: 1` marker opts a compact `format: 2` Plan into strict hierarchy checks",
            "unmarked compact Plans retain structural validation",
            "historical expanded or completed Plans remain untouched",
            "recursive task IDs remain valid",
            "direct serial Plans remain supported",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, policy)

    def test_hierarchy_rows_preserve_the_frozen_columns_and_serialized_values(self) -> None:
        plan = strict_hierarchy_plan()
        columns = tuple(
            cell.strip() for cell in STRICT_TASK_HEADER.strip("|").split("|")
        )
        self.assertEqual(columns, STRICT_ROW_FIELDS)
        self.assertIn(STRICT_TASK_HEADER, plan)
        self.assertIn(STRICT_TASK_SEPARATOR, plan)
        for task in STRICT_HIERARCHY_TASKS:
            with self.subTest(task=task[0]):
                self.assertEqual(plan.count(strict_task_row(task)), 1)

        changed = replace_strict_row_cell(plan, "T1-B", "Outcome", "updated prose")
        self.assertIn(
            "| T1-B | owner-b | complete | T1-B-1 | T1-leaves | updated prose | complete |",
            changed,
        )
        self.assertNotIn(strict_task_row(STRICT_HIERARCHY_TASKS[2]), changed)

    def test_hierarchy_packets_preserve_bounded_fields_and_owner_metadata(self) -> None:
        plan = strict_hierarchy_plan()
        for task in STRICT_HIERARCHY_TASKS:
            task_id = task[0]
            with self.subTest(task=task_id):
                self.assertEqual(plan.count(f"### {task_id} —"), 1)
                packet = strict_task_packet(task)
                self.assertIn(packet, plan)
                for field in STRICT_PACKET_FIELDS:
                    self.assertIn(f"- **{field}:**", packet)

        self.assertIn("- **Role:** Task Owner", plan)
        self.assertIn("- **Role:** integration", plan)
        self.assertIn("- **Role:** verification", plan)
        self.assertIn("- **Parent:** T1-B", plan)
        self.assertIn("- **May delegate:** yes", plan)
        self.assertIn("- **May delegate:** no", plan)
        self.assertIn("- **Inherited boundaries:**", plan)
        self.assertIn("- **Return:** decision-bearing evidence", plan)

    def test_dependency_and_fresh_verification_edges_are_serialized_explicitly(self) -> None:
        plan = strict_hierarchy_plan()
        for edge in (
            "| T1-B | owner-b | complete | T1-B-1 |",
            "| T1-B-I | integrator-b | complete | T1-B-1 |",
            "| T1-I | integrator-root | complete | T1-A, T1-B, T1-B-I |",
            "| T1-V | verifier | complete | T1-I |",
        ):
            self.assertIn(edge, plan)
        self.assertIn("### T1-V —", plan)
        self.assertIn("- **Role:** verification", plan)
        self.assertIn("- **Parent:** T1", plan)
        self.assertIn("- **Parallel group:** verification", plan)
        self.assertIn("- **May delegate:** no", plan)

        policy = (REPOSITORY / "docs/PLANS.md").read_text(encoding="utf-8")
        for phrase in (
            "Fresh verification nodes that depend on that integrated candidate",
            "read-only, nonrepairing, and nondelegating",
            "Main manually moves the terminal Plan to",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, policy)

    def test_plan_states_results_and_terminal_movement_remain_manual(self) -> None:
        active = compact_plan(status="in-progress")
        self.assertIn("status: in-progress", active)
        self.assertIn("## Outcome\n\nPending until terminal transition.", active)
        self.assertIn("## Verification summary\n\n- Pending until verification.", active)

        for status in ("complete", "cancelled", "superseded"):
            with self.subTest(status=status):
                terminal = compact_plan(status=status)
                self.assertIn(f"status: {status}", terminal)
                self.assertIn(f"## Outcome\n\n{status}", terminal)
                self.assertIn("## Documentation impact\n\n- None.", terminal)
                self.assertIn("Candidate identity: commit abc123", terminal)
                self.assertIn("## Verification summary\n\n| Criterion |", terminal)
                self.assertIn("## Follow-ups\n\n- None.", terminal)

        policy = (REPOSITORY / "docs/PLANS.md").read_text(encoding="utf-8")
        self.assertIn("No command decides completion or moves a Plan automatically", policy)
        self.assertIn("Main manually moves the terminal Plan", policy)
        self.assertIn("Main owns terminal movement and evidence judgment", policy)

    def test_direct_serial_and_compact_plan_forms_remain_supported(self) -> None:
        serial = strict_direct_serial_plan(task_graph=None)
        self.assertRegex(serial, r"(?m)^format: 2$")
        self.assertNotIn("task_graph:", serial)
        self.assertIn(
            "| T2 | serial-owner | complete | none | none | Perform serial work | complete |",
            serial,
        )
        self.assertIn("- **Role:** leaf", serial)
        self.assertIn("- **Parent:** none", serial)
        self.assertIn("- **May delegate:** no", serial)

        compact = compact_plan()
        self.assertRegex(compact, r"(?m)^format: 2$")
        self.assertIn("| Task | Owner | State | Depends on | Outcome | Result |", compact)
        self.assertNotIn("Parallel group", compact)
        self.assertIn("### T1 — Implement", compact)

        recursive = hierarchical_compact_plan()
        self.assertRegex(recursive, r"(?m)^format: 2$")
        self.assertNotIn("task_graph:", recursive)
        for task_id in ("T1", "T1-A", "T1-A-1"):
            self.assertIn(f"| {task_id} |", recursive)
            self.assertIn(f"### {task_id} —", recursive)

        policy = (REPOSITORY / "docs/PLANS.md").read_text(encoding="utf-8")
        self.assertIn("unmarked compact Plans retain structural validation", policy)
        self.assertIn("direct serial Plans remain supported", policy)

    def test_recursive_task_ids_keep_exact_packet_mapping_and_owners(self) -> None:
        plan = hierarchical_compact_plan()
        rows = (
            "| T1 | task-owner | complete | none | Decompose | complete |",
            "| T1-A | task-owner-a | complete | T1 | Own branch | complete |",
            "| T1-A-1 | implementation-a1 | complete | T1-A | Implement leaf | complete |",
        )
        for row in rows:
            with self.subTest(row=row):
                self.assertEqual(plan.count(row), 1)

        for task_id, owner in (
            ("T1", "task-owner"),
            ("T1-A", "task-owner-a"),
            ("T1-A-1", "implementation-a1"),
        ):
            with self.subTest(task=task_id):
                self.assertEqual(plan.count(f"### {task_id} — Implement"), 1)
                self.assertIn(f"- **Owner:** {owner}", plan)
                self.assertIn("- **Outcome:** Implement the example.", plan)

        self.assertIn("| T1-A-1 | implementation-a1 | complete | T1-A |", plan)
        self.assertIn("recursive task IDs remain valid", (REPOSITORY / "docs/PLANS.md").read_text(encoding="utf-8"))

    def test_setup_preserves_active_and_historical_plan_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            active = root / "docs/exec-plans/active/PLAN-2026-0001-example.md"
            completed = root / "docs/exec-plans/completed/PLAN-2025-0001-history.md"
            active.parent.mkdir(parents=True)
            completed.parent.mkdir(parents=True)
            active_text = compact_plan(plan_id="PLAN-2026-0001", status="in-progress")
            completed_text = EXPANDED_LEGACY_PLAN.format(
                plan_id="PLAN-2025-0001",
                status="complete",
            ) + "\nHistorical bytes remain readable.\n"
            active.write_text(active_text, encoding="utf-8")
            completed.write_text(completed_text, encoding="utf-8")
            before = {active: active.read_bytes(), completed: completed.read_bytes()}

            self.install_bundle(root)

            self.assertEqual({active: active.read_bytes(), completed: completed.read_bytes()}, before)
            self.assertIn("## Purpose / Big Picture", completed.read_text(encoding="utf-8"))
            self.assertIn("Historical bytes remain readable.", completed.read_text(encoding="utf-8"))

    def test_terminal_plan_template_leaves_evidence_and_movement_to_main(self) -> None:
        template = read_asset("document-first/docs/exec-plans/_template.md.tmpl")
        terminal = template.replace("status: proposed", "status: complete", 1)
        for heading in (
            "## Documentation impact",
            "## Integration summary",
            "## Verification summary",
            "## Follow-ups",
            "## Outcome",
        ):
            self.assertIn(heading, terminal)
        self.assertIn("- **Owner:** TODO", terminal)
        self.assertIn("manually moves the terminal Plan to", terminal)
        self.assertIn("Main records `complete`, `cancelled`, or `superseded` only after fresh evidence", terminal)
        self.assertIn("automatic closure", terminal.casefold())

    def test_terminal_compact_plans_encode_each_manual_outcome(self) -> None:
        for status in ("complete", "cancelled", "superseded"):
            with self.subTest(status=status):
                plan = compact_plan(status=status)
                self.assertIn(f"status: {status}", plan)
                self.assertIn(f"## Outcome\n\n{status}", plan)
                self.assertIn("## Integration summary", plan)
                self.assertIn("## Verification summary", plan)
                self.assertIn("## Follow-ups\n\n- None.", plan)

    def test_compact_format_and_historical_plan_forms_remain_distinguishable(self) -> None:
        compact = compact_plan()
        self.assertRegex(compact, r"(?m)^format: 2$")
        self.assertNotIn("## Purpose / Big Picture", compact)

        historical = EXPANDED_LEGACY_PLAN.format(
            plan_id="PLAN-2025-0001",
            status="complete",
        )
        self.assertNotRegex(historical, r"(?m)^format:")
        self.assertNotIn("task_graph:", historical)
        self.assertIn("## Purpose / Big Picture", historical)
        self.assertIn("## Validation and Evidence", historical)
        self.assertIn("Historical acceptance was met.", historical)

        policy = (REPOSITORY / "docs/PLANS.md").read_text(encoding="utf-8")
        self.assertIn("historical expanded or completed Plans remain untouched", policy)
        self.assertIn("Use [`exec-plans/_template.md`](exec-plans/_template.md) with `format: 2`", policy)

    def test_duplicate_plan_ids_remain_visible_for_manual_ambiguity_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            active = root / "docs/exec-plans/active/PLAN-2026-0009-active.md"
            completed = root / "docs/exec-plans/completed/PLAN-2026-0009-history.md"
            active.parent.mkdir(parents=True)
            completed.parent.mkdir(parents=True)
            active.write_text(
                compact_plan(plan_id="PLAN-2026-0009", status="in-progress"),
                encoding="utf-8",
            )
            completed.write_text(
                EXPANDED_LEGACY_PLAN.format(
                    plan_id="PLAN-2026-0009",
                    status="complete",
                ),
                encoding="utf-8",
            )
            before = {active: active.read_bytes(), completed: completed.read_bytes()}

            self.install_bundle(root)

            self.assertEqual({active: active.read_bytes(), completed: completed.read_bytes()}, before)
            policy = (root / "docs/PLANS.md").read_text(encoding="utf-8")
            self.assertIn("stops on ambiguity", policy.lower())
            self.assertIn("active and completed history", policy.lower())

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
            self.assertIn("active ordinary Markdown Plan", policy)
            self.assertIn("Terminal states are:", policy)
            self.assertIn(
                "For every broad or multi-part root, the default packet is `Role: Task Owner` with `May delegate: yes`",
                policy,
            )
            self.assertIn("Narrow or inherently serial roots remain direct nondelegating leaves", policy)
            self.assertIn("Main dispatches independent root Owners concurrently", policy)
            self.assertIn("Each Owner first returns a finite child manifest", policy)
            self.assertIn(
                "Only the resumed serialized Task Owner dispatches its own declared dependency-ready descendants",
                policy,
            )
            self.assertNotIn("complete dependency-ready leaf set concurrently", policy)
            self.assertNotIn("./dev/", policy)
            self.assertNotIn(".harness/runs", policy)
            self.assertNotIn("Gate verdict", policy)


if __name__ == "__main__":
    unittest.main()
