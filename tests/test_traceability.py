from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet.cli import main as cli_main


COMMIT = "b" * 40
MANIFEST_SHA = "a" * 64


class TraceabilityTests(unittest.TestCase):
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
            "Traceability Project",
            "--summary",
            "A traceability validation fixture.",
            "--skip-check",
        )

    def run_plan_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / "dev/harness.py"), "plan-check"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def run_harness(self, root: Path, command: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", str(root / "dev/harness.py"), command, *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def spec_text(self) -> str:
        return """---
id: SPEC-TEST-001
kind: product-spec
status: active
area: test
summary: Traceability test authority
applies_to: []
supersedes: []
---

# Traceability test authority

## Confirmed traceability

### Confirmed

- [confirmed] JRN-001 | A maintainer observes one bounded behavior.
- [confirmed] REQ-P0-001 | Journey: JRN-001 | Acceptance: AC-1 | Provide the bounded behavior.
- [confirmed] AC-1 | P0: REQ-P0-001 | Journey: JRN-001 | The bounded behavior is observable.

### Proposed

- None.

### Open

- None.
"""

    def plan_text(self, *, status: str = "approved") -> str:
        task_state = "complete" if status == "complete" else "ready"
        return f"""---
id: PLAN-2026-0099
kind: exec-plan
status: {status}
owner: main
area: test
created: 2026-08-30
updated: 2026-08-30
base_commit: "{COMMIT}"
integrated_commit: "{COMMIT}"
verified_commit: "{COMMIT}"
traceability: 1
product_spec: SPEC-TEST-001
verification_run: run-001
manifest_sha256: "{MANIFEST_SHA}"
gate_verdict: PASS
gate_review_reason: ""
---

# Traceability validation fixture

## Purpose / Big Picture

Deliver one bounded, observable behavior.

## Progress

- [x] Deliver and verify the behavior.

## Context and Orientation

Use the referenced product specification and this plan only.

## Scope

- One bounded behavior.

## Non-goals

- Unrelated work.

## Product Trace

| Product spec | Journey | P0 requirement | Acceptance criteria | Implementation tasks | Verification tasks |
|---|---|---|---|---|---|
| `SPEC-TEST-001` | `JRN-001` | `REQ-P0-001` | `AC-1` | `T1` | `T2` |

## Acceptance Criteria

- **AC-1:** The bounded behavior is observable.

## Milestones

### M1 — Bounded behavior

Deliver and verify the behavior.

## Task Packets

### T1 — Implement the behavior

#### State

{task_state}

#### Task type

implementation

#### Depends on

none

#### Outcome

The bounded behavior is implemented.

#### Non-goals

Unrelated changes.

#### Read

The product specification and this plan.

#### Allowed writes

The bounded fixture implementation.

#### Protected paths

Everything else.

#### Acceptance

AC-1

#### Verify

Run the focused test.

#### Stop conditions

The acceptance criterion or scope must change.

#### Result

The implementation result is recorded.

### T2 — Verify the behavior

#### State

{task_state}

#### Task type

verification

#### Depends on

T1

#### Outcome

The bounded behavior is independently verified.

#### Non-goals

Implementation or redesign.

#### Read

The product specification, plan, implementation, and evidence.

#### Allowed writes

Verification evidence only.

#### Protected paths

Implementation and acceptance criteria.

#### Acceptance

AC-1

#### Verify

Inspect the criterion-level evidence.

#### Stop conditions

The target or evidence differs.

#### Result

The verification result is recorded.

## Architecture Impact

None; this is a validation fixture.

## Documentation Impact

| Document | Action | Reason | Owner | Status |
|---|---|---|---|---|
| Product specification | none | Authority is current | Main | resolved |

## Interfaces and Dependencies

- No production dependency.

## Migration, Rollout, and Recovery

Not applicable to this fixture.

## Surprises and Discoveries

- No discoveries.

## Decision Log

- The bounded trace is accepted for this fixture.

## Concrete Steps

1. Run the focused check.

## Validation and Evidence

### Acceptance closure

| Acceptance criterion | Task | Evidence path | Run ID | Manifest SHA-256 | Verified commit | Gate verdict | Review reason |
|---|---|---|---|---|---|---|---|
| `AC-1` | `T1/T2` | `.harness/runs/run-001/report.md#AC-1` | `run-001` | `{MANIFEST_SHA}` | `{COMMIT}` | `PASS` | not applicable |

- Integrated target: {COMMIT}
- Verified commit: {COMMIT}
- Verification Run: run-001
- Manifest SHA-256: {MANIFEST_SHA}
- Gate verdict: PASS
- Raw logs remain uncommitted.

## Outcomes and Retrospective

The bounded behavior and evidence chain are recorded.

## Follow-ups

- none
"""

    def install_traceable_plan(self, root: Path, *, status: str = "approved") -> tuple[Path, Path]:
        spec = root / "docs/product-specs/SPEC-TEST-001-traceability.md"
        spec.write_text(self.spec_text(), encoding="utf-8")
        directory = "completed" if status == "complete" else "active"
        plan = root / f"docs/exec-plans/{directory}/PLAN-2026-0099-traceability.md"
        plan.write_text(self.plan_text(status=status), encoding="utf-8")
        return spec, plan

    def test_valid_traceable_plan_passes_and_legacy_completed_plan_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.install_traceable_plan(root)

            legacy_source = (
                REPOSITORY
                / "docs/exec-plans/completed/PLAN-2026-0001-rename-to-reporivet-and-prepare-public-release.md"
            )
            legacy = root / "docs/exec-plans/completed" / legacy_source.name
            shutil.copyfile(legacy_source, legacy)
            legacy_before = legacy.read_bytes()

            check = self.run_plan_check(root)

            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertEqual(legacy.read_bytes(), legacy_before)

    def test_plan_check_rejects_invalid_spec_trace_and_task_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            spec, plan = self.install_traceable_plan(root)
            valid_spec = self.spec_text()
            valid_plan = self.plan_text()
            cases = (
                (
                    "missing product spec",
                    valid_spec,
                    valid_plan.replace("product_spec: SPEC-TEST-001", 'product_spec: ""'),
                    "traceability plan is missing product_spec",
                ),
                (
                    "duplicate declaration",
                    valid_spec.replace(
                        "- [confirmed] JRN-001 | A maintainer observes one bounded behavior.\n",
                        "- [confirmed] JRN-001 | A maintainer observes one bounded behavior.\n"
                        "- [proposed] JRN-001 | A duplicate proposed journey.\n",
                    ),
                    valid_plan,
                    "duplicate identifier JRN-001",
                ),
                (
                    "unknown declaration link",
                    valid_spec.replace("Acceptance: AC-1", "Acceptance: AC-999", 1),
                    valid_plan,
                    "references unknown or unconfirmed acceptance AC-999",
                ),
                (
                    "P0 without acceptance",
                    valid_spec.replace(
                        "REQ-P0-001 | Journey: JRN-001 | Acceptance: AC-1 | Provide the bounded behavior.",
                        "REQ-P0-001 | Journey: JRN-001 | Provide the bounded behavior.",
                    ),
                    valid_plan,
                    "missing 'Acceptance:' link field",
                ),
                (
                    "proposed criterion cannot satisfy confirmed trace",
                    valid_spec.replace("- [confirmed] AC-1 |", "- [proposed] AC-1 |"),
                    valid_plan,
                    "references unknown or unconfirmed acceptance AC-1",
                ),
                (
                    "unknown Product Trace criterion",
                    valid_spec,
                    valid_plan.replace("| `AC-1` | `T1` |", "| `AC-999` | `T1` |"),
                    "unknown acceptance criterion AC-999",
                ),
                (
                    "missing task type",
                    valid_spec,
                    valid_plan.replace("#### Task type\n\nimplementation\n\n", "", 1),
                    "traceability task is missing 'Task type' field",
                ),
                (
                    "implementation task without criterion",
                    valid_spec,
                    valid_plan.replace(
                        "#### Acceptance\n\nAC-1\n\n#### Verify\n\nRun the focused test.",
                        "#### Acceptance\n\nall criteria\n\n#### Verify\n\nRun the focused test.",
                    ),
                    "missing known acceptance criterion",
                ),
                (
                    "verification task without criterion",
                    valid_spec,
                    valid_plan.replace(
                        "#### Acceptance\n\nAC-1\n\n#### Verify\n\nInspect the criterion-level evidence.",
                        "#### Acceptance\n\nall criteria\n\n#### Verify\n\nInspect the criterion-level evidence.",
                    ),
                    "missing known acceptance criterion",
                ),
            )
            for name, spec_text, plan_text, expected in cases:
                with self.subTest(name=name):
                    spec.write_text(spec_text, encoding="utf-8")
                    plan.write_text(plan_text, encoding="utf-8")
                    check = self.run_plan_check(root)
                    self.assertNotEqual(check.returncode, 0)
                    self.assertIn(expected, check.stderr)

    def test_complete_traceable_plan_requires_bound_evidence_and_review_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            _, plan = self.install_traceable_plan(root, status="complete")
            valid = self.plan_text(status="complete")

            check = self.run_plan_check(root)
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

            cases = (
                (
                    "missing manifest SHA",
                    valid.replace(f'manifest_sha256: "{MANIFEST_SHA}"', 'manifest_sha256: ""'),
                    "manifest_sha256 must be a 64-character SHA-256",
                ),
                (
                    "evidence path escape",
                    valid.replace(
                        ".harness/runs/run-001/report.md#AC-1",
                        ".harness/runs/run-001/../outside.json",
                    ),
                    "evidence path must stay beneath .harness/runs/run-001/",
                ),
                (
                    "REVIEW without reason",
                    valid.replace("gate_verdict: PASS", "gate_verdict: REVIEW", 1).replace(
                        "| `PASS` | not applicable |", "| `REVIEW` | not applicable |"
                    ),
                    "REVIEW gate verdict requires gate_review_reason",
                ),
                (
                    "missing criterion evidence",
                    valid.replace(
                        f"| `AC-1` | `T1/T2` | `.harness/runs/run-001/report.md#AC-1` | `run-001` | `{MANIFEST_SHA}` | `{COMMIT}` | `PASS` | not applicable |\n",
                        "",
                    ),
                    "complete traceable plan has no evidence row for AC-1",
                ),
                (
                    "terminal placeholder",
                    valid.replace(
                        "The bounded behavior and evidence chain are recorded.",
                        "The bounded behavior is recorded; evidence remains pending.",
                    ),
                    "complete traceable plan contains an unresolved placeholder",
                ),
            )
            for name, plan_text, expected in cases:
                with self.subTest(name=name):
                    plan.write_text(plan_text, encoding="utf-8")
                    check = self.run_plan_check(root)
                    self.assertNotEqual(check.returncode, 0)
                    self.assertIn(expected, check.stderr)

    def test_close_plan_binds_traceable_criterion_evidence_to_final_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for relative in (
                "ARCHITECTURE.md",
                "docs/PRODUCT.md",
                "docs/DESIGN.md",
                "docs/QUALITY.md",
                "docs/SECURITY.md",
                "docs/RELIABILITY.md",
            ):
                path = root / relative
                if not path.exists():
                    continue
                text = path.read_text(encoding="utf-8")
                path.write_text(
                    text.replace("status: draft", "status: active").replace("TODO", "Established"),
                    encoding="utf-8",
                )
            config = root / "dev/harness.toml"
            config.write_text(
                config.read_text(encoding="utf-8").replace(
                    'baseline = "draft"',
                    'baseline = "established"',
                ),
                encoding="utf-8",
            )
            spec = root / "docs/product-specs/SPEC-TEST-001-traceability.md"
            spec.write_text(self.spec_text(), encoding="utf-8")
            catalog = self.run_harness(root, "docs-index")
            self.assertEqual(catalog.returncode, 0, catalog.stdout + catalog.stderr)

            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Traceability Fixture"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "base"], cwd=root, check=True, capture_output=True)
            base = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()

            plan = root / "docs/exec-plans/active/PLAN-2026-0099-traceability.md"
            plan_text = self.plan_text(status="complete")
            plan_text = plan_text.replace("status: complete", "status: verifying", 1)
            plan_text = plan_text.replace(f'base_commit: "{COMMIT}"', f'base_commit: "{base}"')
            plan_text = plan_text.replace(f'integrated_commit: "{COMMIT}"', 'integrated_commit: "HEAD"')
            plan_text = plan_text.replace(f'verified_commit: "{COMMIT}"', 'verified_commit: ""')
            plan.write_text(plan_text, encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "candidate"], cwd=root, check=True, capture_output=True)
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()

            close = self.run_harness(root, "close-plan", "PLAN-2026-0099")
            self.assertEqual(close.returncode, 0, close.stdout + close.stderr)
            runs = sorted((root / ".harness/runs").glob("*-verify"))
            self.assertEqual(len(runs), 1)
            run = runs[0]
            manifest_hash = hashlib.sha256((run / "manifest.json").read_bytes()).hexdigest()
            gate = json.loads((run / "gate.json").read_text(encoding="utf-8"))
            self.assertEqual(gate["verdict"], "PASS")

            completed = root / "docs/exec-plans/completed" / plan.name
            self.assertFalse(plan.exists())
            text = completed.read_text(encoding="utf-8")
            expected_row = (
                f"| `AC-1` | `T1/T2` | `.harness/runs/{run.name}/manifest.json` | "
                f"`{run.name}` | `{manifest_hash}` | `{head}` | `PASS` | none |"
            )
            self.assertIn(expected_row, text)
            final_check = self.run_plan_check(root)
            self.assertEqual(final_check.returncode, 0, final_check.stdout + final_check.stderr)


if __name__ == "__main__":
    unittest.main()
