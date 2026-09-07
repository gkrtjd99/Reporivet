from __future__ import annotations

import contextlib
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


class CodeMapTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = cli_main(list(args))
        return subprocess.CompletedProcess(list(args), returncode, stdout.getvalue(), stderr.getvalue())

    def init(self, root: Path, *, checked: bool = False) -> subprocess.CompletedProcess[str]:
        args = [
            "init",
            "--root",
            str(root),
            "--name",
            "Code Map Project",
            "--summary",
            "An evidence-backed code-map fixture.",
        ]
        if not checked:
            args.append("--skip-check")
        return self.run_cli(*args)

    def run_harness(self, root: Path, command: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / "dev/harness.py"), command, *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def product_spec(self) -> str:
        return """---
id: SPEC-MAP-001
kind: product-spec
status: active
area: domain
summary: Domain routing evidence
applies_to:
  - "src/domain/**"
supersedes: []
---

# Domain routing evidence

## Path evidence

### Confirmed

- [confirmed] Planned path: future/worker.py
- [inferred] Planned path: future/inferred.py
- Generic path: generic/unreferenced

## Other path list

- [confirmed] Planned path: future/wrong-level-two.py

### Proposed

- [proposed] Planned path: future/proposed.py
- [confirmed] Planned path: future/wrong-heading.py

### Open

- None.
"""

    def module_contract(
        self,
        *,
        owner: str | None = "Domain maintainers",
        scope: str = "src/domain",
        status: str = "active",
    ) -> str:
        owner_line = f"owner: {owner}\n" if owner is not None else ""
        return f"""---
id: MOD-DOMAIN
kind: module-contract
status: {status}
area: domain
summary: Domain implementation boundary
{owner_line}responsibility: Keep domain entry points and dependency direction explicit.
applies_to:
  - "{scope}"
public_entry_points:
  - "src/domain/service.py"
dependency_rules:
  - "Domain code does not depend on generated documentation."
organization: Domain implementation and tests remain in their configured source roots.
verification:
  - "python -m unittest discover -s tests -v"
---

# Domain implementation boundary
"""

    def prepare_evidence_fixture(self, root: Path) -> None:
        (root / "src/domain").mkdir(parents=True)
        (root / "src/domain/service.py").write_text("VALUE = 1\n", encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests/test_sample.py").write_text("# fixture\n", encoding="utf-8")
        (root / "generic/unreferenced").mkdir(parents=True)

        config = root / "dev/harness.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'source = ["src"]',
                'source = ["src", "configured-only"]',
            ),
            encoding="utf-8",
        )
        (root / "docs/product-specs/SPEC-MAP-001-domain.md").write_text(
            self.product_spec(),
            encoding="utf-8",
        )
        (root / "docs/module-contracts/MOD-DOMAIN.md").write_text(
            self.module_contract(),
            encoding="utf-8",
        )

    def test_code_map_uses_only_actual_configured_contract_and_confirmed_planned_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.prepare_evidence_fixture(root)

            catalog = self.run_harness(root, "docs-index")
            self.assertEqual(catalog.returncode, 0, catalog.stdout + catalog.stderr)
            generated = self.run_harness(root, "code-map")
            self.assertEqual(generated.returncode, 0, generated.stdout + generated.stderr)
            first = (root / "docs/generated/code-map.md").read_bytes()

            text = first.decode("utf-8")
            self.assertIn("| `src` | actual, configured |", text)
            self.assertIn("| `configured-only` | configured |", text)
            self.assertIn("| `src/domain` | actual, configured, contract | domain | `MOD-DOMAIN` |", text)
            self.assertIn("| `future/worker.py` | confirmed-planned | domain | `SPEC-MAP-001` |", text)
            self.assertNotIn("generic/unreferenced", text)
            self.assertNotIn("future/inferred.py", text)
            self.assertNotIn("future/wrong-level-two.py", text)
            self.assertNotIn("future/proposed.py", text)
            self.assertNotIn("future/wrong-heading.py", text)

            second = self.run_harness(root, "code-map")
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual((root / "docs/generated/code-map.md").read_bytes(), first)
            current = self.run_harness(root, "code-map", "--check")
            self.assertEqual(current.returncode, 0, current.stdout + current.stderr)
            docs = self.run_harness(root, "docs-check")
            self.assertEqual(docs.returncode, 0, docs.stdout + docs.stderr)

    def test_contract_metadata_and_scope_are_validated_without_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            contract = root / "docs/module-contracts/MOD-DOMAIN.md"

            contract.write_text(self.module_contract(owner=None), encoding="utf-8")
            missing = self.run_harness(root, "code-map")
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("missing frontmatter field 'owner'", missing.stderr)

            contract.write_text(self.module_contract(scope="future/unconfirmed"), encoding="utf-8")
            unsupported = self.run_harness(root, "code-map")
            self.assertNotEqual(unsupported.returncode, 0)
            self.assertIn("lacks actual, configured, or confirmed-planned evidence", unsupported.stderr)

            contract.write_text(
                self.module_contract(owner="unknown", scope="src", status="draft")
                .replace('  - "src/domain/service.py"', '  - "unknown"')
                .replace('  - "Domain code does not depend on generated documentation."', '  - "unknown"')
                .replace("organization: Domain implementation and tests remain in their configured source roots.", "organization: unknown")
                .replace('  - "python -m unittest discover -s tests -v"', '  - "unknown"'),
                encoding="utf-8",
            )
            explicit_unknown = self.run_harness(root, "code-map")
            self.assertEqual(explicit_unknown.returncode, 0, explicit_unknown.stdout + explicit_unknown.stderr)
            self.assertNotIn("MOD-DOMAIN", (root / "docs/generated/code-map.md").read_text(encoding="utf-8"))

    def test_drift_and_path_area_spec_routing_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.prepare_evidence_fixture(root)
            self.assertEqual(self.run_harness(root, "docs-index").returncode, 0)
            self.assertEqual(self.run_harness(root, "code-map").returncode, 0)

            new_plan = self.run_harness(root, "new-plan", "Map", "context", "--area", "domain")
            self.assertEqual(new_plan.returncode, 0, new_plan.stdout + new_plan.stderr)
            plan_path = root / new_plan.stdout.strip()
            plan_text = plan_path.read_text(encoding="utf-8").replace(
                'product_spec: ""',
                "product_spec: SPEC-MAP-001",
            )
            plan_path.write_text(plan_text, encoding="utf-8")
            plan_id_match = re.search(r"^id:\s*(\S+)", plan_text, re.MULTILINE)
            self.assertIsNotNone(plan_id_match)
            plan_id = plan_id_match.group(1)

            by_path = self.run_harness(
                root,
                "context",
                "--path",
                "src/domain/service.py",
                "--plan",
                plan_id,
            )
            self.assertEqual(by_path.returncode, 0, by_path.stdout + by_path.stderr)
            self.assertIn("MOD-DOMAIN", by_path.stdout)
            self.assertIn("`src/domain` — evidence: actual, configured, contract", by_path.stdout)
            self.assertIn("docs/product-specs/SPEC-MAP-001-domain.md", by_path.stdout)
            self.assertIn("Product authority:", by_path.stdout)

            by_area = self.run_harness(root, "context", "--area", "domain")
            self.assertEqual(by_area.returncode, 0, by_area.stdout + by_area.stderr)
            self.assertIn("MOD-DOMAIN", by_area.stdout)
            self.assertIn("`future/worker.py` — evidence: confirmed-planned", by_area.stdout)
            self.assertIn("SPEC-MAP-001", by_area.stdout)
            self.assertNotIn("configured-only` — evidence", by_area.stdout)

            code_map = root / "docs/generated/code-map.md"
            code_map.write_text(code_map.read_text(encoding="utf-8") + "manual drift\n", encoding="utf-8")
            map_check = self.run_harness(root, "code-map", "--check")
            self.assertNotEqual(map_check.returncode, 0)
            self.assertIn("is stale; run ./dev/code-map", map_check.stderr)
            docs_check = self.run_harness(root, "docs-check")
            self.assertNotEqual(docs_check.returncode, 0)
            self.assertIn("docs/generated/code-map.md is stale; run ./dev/code-map", docs_check.stderr)

    def test_packaged_assets_and_wrapper_work_without_package_imports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root, checked=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for relative in (
                "dev/code-map",
                "docs/module-contracts/README.md",
                "docs/module-contracts/_template.md",
                "docs/generated/code-map.md",
            ):
                self.assertTrue((root / relative).is_file(), relative)
            self.assertNotIn("import reporivet", (root / "dev/harness.py").read_text(encoding="utf-8"))

            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            environment["PYTHON"] = sys.executable
            wrapper = subprocess.run(
                [str(root / "dev/code-map"), "--check"],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(wrapper.returncode, 0, wrapper.stdout + wrapper.stderr)
            isolated = subprocess.run(
                [sys.executable, "-I", str(root / "dev/harness.py"), "code-map", "--check"],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(isolated.returncode, 0, isolated.stdout + isolated.stderr)

            doctor = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)

    def test_old_config_uses_gate_defaults_and_doctor_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            config = root / "dev/harness.toml"
            old_text = config.read_text(encoding="utf-8").split("\n[gate]\n", 1)[0] + "\n"
            config.write_text(old_text, encoding="utf-8")
            before = config.read_bytes()

            doctor = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)
            self.assertIn("conservative shadow defaults apply in memory", doctor.stdout)
            self.assertEqual(config.read_bytes(), before)

            verify = self.run_harness(root, "verify")
            self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
            self.assertIn("Gate REVIEW (shadow)", verify.stdout)
            self.assertEqual(config.read_bytes(), before)

    def test_doctor_reports_malformed_config_without_mutating_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            config = root / "dev/harness.toml"
            config.write_bytes(b"[project\n")
            before = config.read_bytes()

            doctor = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(doctor.returncode, 2, doctor.stdout + doctor.stderr)
            self.assertIn("cannot read", doctor.stderr)
            self.assertEqual(config.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
