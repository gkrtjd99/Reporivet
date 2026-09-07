from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
SRC = REPOSITORY / "src"
sys.path.insert(0, str(SRC))

from reporivet import __version__, initializer
from reporivet.cli import main as cli_main


class ReporivetTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        previous = Path.cwd()
        try:
            if cwd is not None:
                os.chdir(cwd)
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                returncode = cli_main(list(args))
        finally:
            os.chdir(previous)
        return subprocess.CompletedProcess(list(args), returncode, stdout.getvalue(), stderr.getvalue())

    def init(
        self, root: Path, *extra: str, checked: bool = False
    ) -> subprocess.CompletedProcess[str]:
        options = list(extra)
        if not checked and "--skip-check" not in options:
            options.append("--skip-check")
        return self.run_cli(
            "init",
            "--root",
            str(root),
            "--name",
            "Test Project",
            "--summary",
            "A test project with an agent-readable repository harness.",
            "--project-kind",
            "service",
            *options,
        )

    def init_kind(
        self, root: Path, kind: str, *extra: str
    ) -> subprocess.CompletedProcess[str]:
        options = list(extra)
        if "--skip-check" not in options:
            options.append("--skip-check")
        return self.run_cli(
            "init",
            "--root",
            str(root),
            "--name",
            "Test Project",
            "--summary",
            "A test project with an agent-readable repository harness.",
            "--project-kind",
            kind,
            *options,
        )

    def run_harness(self, root: Path, command: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / "dev" / "harness.py"), command, *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def mutation_fingerprint(self, output: str) -> str:
        match = re.search(r"^Mutation plan fingerprint: ([0-9a-f]{64})$", output, re.MULTILINE)
        self.assertIsNotNone(match, output)
        assert match is not None
        return match.group(1)

    def filesystem_snapshot(self, root: Path) -> tuple[tuple[str, str, int, bytes], ...]:
        entries: list[tuple[str, str, int, bytes]] = []
        if not root.exists():
            return ()
        for path in sorted(root.rglob("*")):
            relative = path.relative_to(root).as_posix()
            mode = stat.S_IMODE(path.lstat().st_mode)
            if path.is_dir():
                entries.append((relative, "directory", mode, b""))
            elif path.is_file():
                entries.append((relative, "file", mode, path.read_bytes()))
        return tuple(entries)

    def test_initializes_repository_local_harness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root, "--with-ci", checked=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            expected = (
                "AGENTS.md",
                "ARCHITECTURE.md",
                ".reporivet-version",
                "dev/harness.toml",
                "dev/harness.py",
                "dev/context",
                "dev/verify",
                "dev/security-check",
                "dev/garden",
                "docs/README.md",
                "docs/PRODUCT.md",
                "docs/QUALITY.md",
                "docs/SECURITY.md",
                "docs/RELIABILITY.md",
                "docs/PLANS.md",
                "docs/exec-plans/_template.md",
                "docs/exec-plans/tech-debt-tracker.md",
                "docs/references/project-definition-protocol.md",
                ".github/workflows/harness-verify.yml",
                ".github/workflows/harness-garden.yml",
            )
            for relative in expected:
                self.assertTrue((root / relative).exists(), relative)

            agents_text = (root / "AGENTS.md").read_text(encoding="utf-8")
            plans_text = (root / "docs/PLANS.md").read_text(encoding="utf-8")
            knowledge_map = (root / "docs/README.md").read_text(encoding="utf-8")
            plan_template = (root / "docs/exec-plans/_template.md").read_text(encoding="utf-8")
            self.assertLessEqual(len(agents_text.splitlines()), 140)
            self.assertIn("## Agent operating roles", agents_text)
            self.assertIn("Main → Task Lead → leaf", agents_text)
            self.assertIn("## Operating roles and delegation", plans_text)
            self.assertIn("## Result prose contract", plans_text)
            self.assertIn("no plan is selected", knowledge_map)
            self.assertIn("#### Execution constraints", plan_template)
            self.assertIn("exact target commit SHA", plan_template)
            self.assertFalse(any(path.name == "SKILL.md" for path in root.rglob("*")))
            config = (root / "dev" / "harness.toml").read_text(encoding="utf-8")
            self.assertIn('baseline = "draft"', config)
            self.assertIn('configuration = "ready"', config)
            self.assertIn("[gate]", config)
            self.assertIn('mode = "shadow"', config)
            self.assertIn('default_risk = "unknown"', config)
            self.assertIn("require_clean = true", config)
            self.assertIn('protected_paths = [".github/workflows/**", "AGENTS.md", "dev/harness.py", "dev/harness.toml", "docs/SECURITY.md"]', config)
            self.assertIn("actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1", (root / ".github/workflows/harness-verify.yml").read_text())
            self.assertIn("actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1", (root / ".github/workflows/harness-garden.yml").read_text())

            verify = self.run_harness(root, "verify")
            self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    def test_service_init_does_not_generate_design_or_frontend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init_kind(root, "service")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((root / "docs/DESIGN.md").exists())
            self.assertFalse((root / "docs/FRONTEND.md").exists())
            self.assertTrue((root / "docs/RELIABILITY.md").exists())

    def test_library_init_does_not_generate_design(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init_kind(root, "library")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((root / "docs/DESIGN.md").exists())

    def test_cli_init_does_not_generate_visual_design(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init_kind(root, "cli")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((root / "docs/DESIGN.md").exists())

    def test_web_init_generates_visual_design_and_frontend_drafts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init_kind(
                root,
                "web",
                "--capability",
                "visual-design",
                "--capability",
                "frontend",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for relative in ("docs/DESIGN.md", "docs/FRONTEND.md"):
                path = root / relative
                self.assertTrue(path.exists(), relative)
                self.assertIn("status: draft", path.read_text(encoding="utf-8"))
            config = tomllib.loads((root / "dev/harness.toml").read_text(encoding="utf-8"))
            self.assertEqual(config["documents"]["schema"], 2)
            self.assertTrue(config["documents"]["visual_design"])
            self.assertTrue(config["documents"]["frontend"])

    def test_visual_design_template_has_only_visual_design_sections(self) -> None:
        template = initializer.read_asset("docs/DESIGN.md.tmpl")
        headings = re.findall(r"^## (.+?)$", template, re.MULTILINE)
        self.assertEqual(
            headings,
            [
                "Overview",
                "Colors",
                "Typography",
                "Layout",
                "Elevation & Depth",
                "Shapes",
                "Components",
                "Do's and Don'ts",
            ],
        )

    def test_design_template_contains_no_agent_role_or_plan_policy(self) -> None:
        template = initializer.read_asset("docs/DESIGN.md.tmpl").casefold()
        self.assertNotIn("agent", template)
        self.assertNotIn("plan", template)
        self.assertNotIn("policy", template)

    def test_frontend_template_contains_implementation_rules_not_visual_tokens(self) -> None:
        template = initializer.read_asset("docs/FRONTEND.md.tmpl").casefold()
        for term in ("routing", "state", "validation", "verification"):
            self.assertIn(term, template)
        for token in ("colors", "typography", "elevation", "shapes", "shadow"):
            self.assertNotIn(token, template)

    def test_quality_score_is_not_generated_without_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init_kind(root, "service")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((root / "docs/QUALITY_SCORE.md").exists())
            self.assertFalse(any(path.name == "QUALITY_SCORE.md" for path in root.rglob("*")))
            self.assertFalse(any(path.name == "SKILL.md" for path in root.rglob("*")))
            config = tomllib.loads((root / "dev/harness.toml").read_text(encoding="utf-8"))
            self.assertFalse(config["documents"]["quality_score"])

    def test_release_version_and_managed_assets_are_in_sync(self) -> None:
        metadata = tomllib.loads((REPOSITORY / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(__version__, "0.2.0")
        self.assertNotIn("version", metadata["project"])
        self.assertEqual(metadata["project"]["dynamic"], ["version"])
        self.assertEqual(
            metadata["tool"]["setuptools"]["dynamic"]["version"],
            {"attr": "reporivet.__version__"},
        )

        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp).resolve()
            result = self.init(generated)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            for destination, asset in initializer.managed_files(False).items():
                values = {"HARNESS_VERSION": __version__}
                if asset == "dev/wrapper.sh.tmpl":
                    values["COMMAND"] = Path(destination).name
                expected = initializer.read_asset(asset, values).rstrip() + "\n"
                for root in (REPOSITORY, generated):
                    path = root / destination
                    self.assertEqual(path.read_text(encoding="utf-8"), expected, str(path))
                    if destination.startswith("dev/"):
                        self.assertTrue(
                            stat.S_IMODE(path.stat().st_mode) & 0o111,
                            f"not executable: {path}",
                        )

        security_wrapper = (REPOSITORY / "dev" / "security-check").read_text(
            encoding="utf-8"
        )
        self.assertIn('PYTHON=${PYTHON:-python3}', security_wrapper)
        self.assertIn('exec "$PYTHON"', security_wrapper)

    def test_ci_workflows_bind_explicit_target_and_preserve_evidence(self) -> None:
        workflows = (
            (REPOSITORY / ".github" / "workflows" / "ci.yml").read_text(
                encoding="utf-8"
            ),
            initializer.read_asset(
                "github/harness-verify.yml.tmpl",
                {"HARNESS_VERSION": __version__},
            ),
        )
        required = (
            "permissions:\n  contents: read",
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
            "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0",
            "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1",
            "fetch-depth: 0",
            "format('refs/pull/{0}/head', github.event.pull_request.number)",
            "github.event.pull_request.base.sha",
            "github.event.pull_request.head.sha",
            "github.event.before",
            "REPORIVET_BASE_SHA=%s",
            "REPORIVET_HEAD_SHA=%s",
            "REPORIVET_TARGET=%s",
            "0000000000000000000000000000000000000000",
            "actual_head=$(git rev-parse HEAD)",
            "cat \"$report\" >> \"$GITHUB_STEP_SUMMARY\"",
            "path: .harness/runs/",
        )
        for workflow in workflows:
            for fragment in required:
                self.assertIn(fragment, workflow)
            self.assertEqual(workflow.count("run: ./dev/verify"), 1)
            self.assertGreaterEqual(workflow.count("if: always()"), 2)
            self.assertLess(
                workflow.index("run: ./dev/bootstrap"),
                workflow.index("run: ./dev/verify"),
            )
            self.assertNotIn("HEAD^", workflow)
            self.assertNotIn("git fetch", workflow)

    def test_doctor_requires_audit_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            (root / "dev" / "audit").unlink()

            doctor = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(doctor.returncode, 2)
            self.assertIn("missing dev/audit", doctor.stderr)

    def test_doctor_requires_definition_protocol(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            protocol = root / "docs" / "references" / "project-definition-protocol.md"
            protocol.unlink()

            doctor = self.run_cli("doctor", "--root", str(root))
            self.assertEqual(doctor.returncode, 2)
            self.assertIn(
                "missing docs/references/project-definition-protocol.md",
                doctor.stderr,
            )

    def test_generated_gitignore_blocks_build_secrets_and_personal_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            second = self.init(root)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            gitignore = (root / ".gitignore").read_text(encoding="utf-8")
            self.assertEqual(gitignore.count("# reporivet:start"), 1)
            self.assertEqual(gitignore.count("# reporivet:end"), 1)
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)

            ignored = (
                ".harness/runs/verify.log",
                ".env",
                ".env.production",
                "secrets.env",
                "credentials.json",
                "service-account-prod.json",
                ".vault-token",
                ".dev.vars",
                ".mcp.json",
                ".cursor/mcp.json",
                ".docker/config.json",
                ".config/gh/hosts.yml",
                ".bundle/config",
                ".cargo/credentials.toml",
                "key.properties",
                "id_ed25519",
                "certificate.p12",
                "terraform.tfstate",
                ".idea/workspace.xml",
                ".vscode/settings.json",
                "dist/reporivet.whl",
                ".venv/bin/python",
                "node_modules/package/index.js",
                "target/debug/app",
                ".vite/deps/chunk.js",
                ".dart_tool/package_config.json",
                ".serverless/state.json",
                ".wrangler/state.json",
                ".supabase/state.json",
                "local.properties",
            )
            for relative in ignored:
                check = subprocess.run(
                    ["git", "check-ignore", "-q", relative],
                    cwd=root,
                    check=False,
                )
                self.assertEqual(check.returncode, 0, f"expected ignored: {relative}")

            allowed_examples = (
                ".env.example",
                ".env.production.example",
                "service-account.example.json",
                "terraform.tfvars.example",
                ".vscode/extensions.json",
                ".reporivet-version",
                "uv.lock",
                "poetry.lock",
                "package-lock.json",
                "pnpm-lock.yaml",
                "Cargo.lock",
                ".docker/Dockerfile",
                ".cursor/rules/project.mdc",
                ".codex/config.toml",
                "Package.resolved",
                "site/index.html",
                "README.md",
            )
            for relative in allowed_examples:
                check = subprocess.run(
                    ["git", "check-ignore", "-q", relative],
                    cwd=root,
                    check=False,
                )
                self.assertEqual(check.returncode, 1, f"expected trackable: {relative}")

    def test_security_check_rejects_force_added_sensitive_material(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)

            secret = root / ".env"
            secret.write_text("API_TOKEN=not-a-real-token\n", encoding="utf-8")
            subprocess.run(["git", "add", "-f", ".env"], cwd=root, check=True)
            path_failure = self.run_harness(root, "security-check")
            self.assertNotEqual(path_failure.returncode, 0)
            self.assertIn("tracked sensitive local configuration", path_failure.stderr)

            config = root / "dev" / "harness.toml"
            config.write_text(
                config.read_text(encoding="utf-8").replace(
                    "security_allow_tracked = []", 'security_allow_tracked = [".env"]'
                ),
                encoding="utf-8",
            )
            allowlisted = self.run_harness(root, "security-check")
            self.assertEqual(allowlisted.returncode, 0, allowlisted.stdout + allowlisted.stderr)

            subprocess.run(["git", "rm", "--cached", "-f", ".env"], cwd=root, check=True, capture_output=True)
            secret.unlink()
            dockerfile = root / ".docker" / "Dockerfile"
            dockerfile.parent.mkdir()
            dockerfile.write_text("FROM scratch\n", encoding="utf-8")
            subprocess.run(["git", "add", ".docker/Dockerfile"], cwd=root, check=True)
            docker_allowed = self.run_harness(root, "security-check")
            self.assertEqual(docker_allowed.returncode, 0, docker_allowed.stdout + docker_allowed.stderr)

            token_file = root / "notes.txt"
            token_file.write_text("temporary=" + "AK" + "IA" + "A" * 16 + "\n", encoding="utf-8")
            subprocess.run(["git", "add", "notes.txt"], cwd=root, check=True)
            content_failure = self.run_harness(root, "security-check")
            self.assertNotEqual(content_failure.returncode, 0)
            self.assertIn("AWS access key signature", content_failure.stderr)

    def test_security_check_rejects_force_added_ignored_build_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)

            artifact = root / "dist" / "reporivet.whl"
            artifact.parent.mkdir()
            artifact.write_bytes(b"not-a-real-wheel")
            subprocess.run(["git", "add", "-f", "dist/reporivet.whl"], cwd=root, check=True)

            failure = self.run_harness(root, "security-check")
            self.assertNotEqual(failure.returncode, 0)
            self.assertIn("tracked path is ignored by a repository .gitignore", failure.stderr)

    def test_existing_implementation_gets_baseline_plan_and_requires_command_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            baseline = root / "docs" / "exec-plans" / "active" / "PLAN-0000-establish-repository-baseline.md"
            self.assertTrue(baseline.exists())
            config = (root / "dev" / "harness.toml").read_text(encoding="utf-8")
            self.assertIn('configuration = "review"', config)
            check = self.run_harness(root, "check")
            self.assertNotEqual(check.returncode, 0)
            self.assertIn("configuration = 'review'", check.stderr)

    def test_project_owned_documents_survive_reinit_and_upgrade(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            first = self.init(root)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

            product = root / "docs" / "PRODUCT.md"
            architecture = root / "ARCHITECTURE.md"
            protocol = root / "docs" / "references" / "project-definition-protocol.md"
            config = root / "dev" / "harness.toml"
            product.write_text("# Project-owned product truth\n", encoding="utf-8")
            architecture.write_text("# Project-owned architecture truth\n", encoding="utf-8")
            protocol.write_text("# Project-owned definition protocol\n", encoding="utf-8")
            config.write_text(config.read_text(encoding="utf-8") + "\n# user-owned\n", encoding="utf-8")

            second = self.init(root, "--skip-check")
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            upgrade = self.run_cli("upgrade", "--root", str(root), "--skip-check")
            self.assertEqual(upgrade.returncode, 0, upgrade.stdout + upgrade.stderr)

            self.assertEqual(product.read_text(encoding="utf-8"), "# Project-owned product truth\n")
            self.assertEqual(architecture.read_text(encoding="utf-8"), "# Project-owned architecture truth\n")
            self.assertEqual(
                protocol.read_text(encoding="utf-8"),
                "# Project-owned definition protocol\n",
            )
            self.assertIn("# user-owned", config.read_text(encoding="utf-8"))

    def test_agents_managed_block_is_idempotent_and_preserves_user_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "AGENTS.md").write_text("# Team note\n\nKeep this section.\n", encoding="utf-8")
            first = self.init(root)
            second = self.init(root)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            text = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("Keep this section.", text)
            self.assertEqual(text.count("<!-- reporivet:start -->"), 1)
            self.assertEqual(text.count("<!-- reporivet:end -->"), 1)

    def test_docs_index_catalogs_new_durable_document_and_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            spec = root / "docs" / "product-specs" / "SPEC-IDENTITY-001-account-deletion.md"
            spec.write_text(
                """---
id: SPEC-IDENTITY-001
kind: product-spec
status: active
area: identity
summary: Account deletion behavior
applies_to:
  - "src/identity/**"
supersedes: []
---

# Account deletion
""",
                encoding="utf-8",
            )
            stale = self.run_harness(root, "docs-index", "--check")
            self.assertNotEqual(stale.returncode, 0)
            update = self.run_harness(root, "docs-index")
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
            self.assertIn("SPEC-IDENTITY-001", (root / "docs" / "README.md").read_text(encoding="utf-8"))
            self.assertIn("SPEC-IDENTITY-001", (root / "docs" / "product-specs" / "index.md").read_text(encoding="utf-8"))
            current = self.run_harness(root, "docs-index", "--check")
            self.assertEqual(current.returncode, 0, current.stdout + current.stderr)

    def test_runtime_plan_tokens_survive_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            template = (root / "docs" / "exec-plans" / "_template.md").read_text(encoding="utf-8")
            runtime = (root / "dev" / "harness.py").read_text(encoding="utf-8")
            self.assertIn("created: {{DATE}}", template)
            self.assertIn('"{{DATE}}": date.today().isoformat()', runtime)
            self.assertNotIn(f'"{date.today().isoformat()}": date.today().isoformat()', runtime)

            new_plan = self.run_harness(root, "new-plan", "Future", "plan", "--area", "test")
            self.assertEqual(new_plan.returncode, 0, new_plan.stdout + new_plan.stderr)
            plan = (root / new_plan.stdout.strip()).read_text(encoding="utf-8")
            self.assertIn(f"created: {date.today().isoformat()}", plan)
            self.assertNotIn("{{DATE}}", plan)

    def test_new_plan_and_task_packet_are_routable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            new_plan = self.run_harness(root, "new-plan", "Login", "lockout", "--area", "identity")
            self.assertEqual(new_plan.returncode, 0, new_plan.stdout + new_plan.stderr)
            relative = new_plan.stdout.strip()
            self.assertTrue((root / relative).exists(), relative)
            self.assertIn("docs/exec-plans/active/", relative)
            plan_id = Path(relative).name.split("-login-lockout.md")[0]
            task = self.run_harness(root, "task", plan_id, "T2")
            self.assertEqual(task.returncode, 0, task.stdout + task.stderr)
            self.assertIn("#### Allowed writes", task.stdout)
            plan_check = self.run_harness(root, "plan-check")
            self.assertEqual(plan_check.returncode, 0, plan_check.stdout + plan_check.stderr)

    def test_established_baseline_rejects_scaffold_markers_and_draft_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            config = root / "dev" / "harness.toml"
            config.write_text(
                config.read_text(encoding="utf-8").replace('baseline = "draft"', 'baseline = "established"'),
                encoding="utf-8",
            )
            strict = self.run_harness(root, "docs-check")
            self.assertNotEqual(strict.returncode, 0)
            self.assertTrue("unresolved TODO" in strict.stderr or "status 'active'" in strict.stderr)

    def test_configured_missing_tool_fails_instead_of_skipping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            config = root / "dev" / "harness.toml"
            text = config.read_text(encoding="utf-8").replace(
                "verify = []", 'verify = [["definitely-not-an-executable"]]'
            )
            config.write_text(text, encoding="utf-8")
            verify = self.run_harness(root, "verify")
            self.assertNotEqual(verify.returncode, 0)
            self.assertIn("configured executable is unavailable", verify.stderr)

    def test_dry_run_does_not_create_or_modify_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp).resolve() / "new-project"
            first_dry_init = self.init(missing, "--dry-run")
            second_dry_init = self.init(missing, "--dry-run")
            self.assertEqual(first_dry_init.returncode, 0, first_dry_init.stdout + first_dry_init.stderr)
            self.assertEqual(second_dry_init.returncode, 0, second_dry_init.stdout + second_dry_init.stderr)
            self.assertFalse(missing.exists())
            self.assertEqual(
                self.mutation_fingerprint(first_dry_init.stdout),
                self.mutation_fingerprint(second_dry_init.stdout),
            )

            root = Path(tmp).resolve() / "existing"
            root.mkdir()
            result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            before = self.filesystem_snapshot(root)
            first_dry_upgrade = self.run_cli("upgrade", "--root", str(root), "--dry-run")
            second_dry_upgrade = self.run_cli("upgrade", "--root", str(root), "--dry-run")
            self.assertEqual(first_dry_upgrade.returncode, 0, first_dry_upgrade.stdout + first_dry_upgrade.stderr)
            self.assertEqual(second_dry_upgrade.returncode, 0, second_dry_upgrade.stdout + second_dry_upgrade.stderr)
            self.assertEqual(before, self.filesystem_snapshot(root))
            self.assertEqual(
                self.mutation_fingerprint(first_dry_upgrade.stdout),
                self.mutation_fingerprint(second_dry_upgrade.stdout),
            )

    def test_mutation_plan_fingerprint_is_canonical_and_path_relative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve() / "project"
            preview = self.init(root, "--dry-run")
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            entry_lines = [
                line.removeprefix("  - ")
                for line in preview.stdout.splitlines()
                if line.startswith("  - {")
            ]
            entries = [json.loads(line) for line in entry_lines]
            self.assertTrue(entries)
            self.assertEqual([entry["path"] for entry in entries], sorted(entry["path"] for entry in entries))
            for entry in entries:
                self.assertFalse(Path(entry["path"]).is_absolute())
                self.assertIn(entry["action"], {"create-directory", "create-file", "update-file"})
                self.assertIn(entry["preimage"]["type"], {"missing", "directory", "file"})
                self.assertIn(entry["postimage"]["type"], {"directory", "file"})
                if entry["postimage"]["type"] == "file":
                    self.assertRegex(entry["postimage"]["sha256"], r"^[0-9a-f]{64}$")
            canonical = json.dumps(entries, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
            self.assertEqual(self.mutation_fingerprint(preview.stdout), hashlib.sha256(canonical).hexdigest())
            self.assertNotIn(str(root), "\n".join(entry_lines))

            applied = self.init(root)
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            self.assertEqual(self.mutation_fingerprint(applied.stdout), self.mutation_fingerprint(preview.stdout))
            by_path = {entry["path"]: entry for entry in entries}
            for relative in ("docs/generated/code-map.md", "docs/README.md"):
                self.assertEqual(
                    hashlib.sha256((root / relative).read_bytes()).hexdigest(),
                    by_path[relative]["postimage"]["sha256"],
                )

    def test_staging_snapshot_excludes_unrelated_concurrent_edit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            notes = root / "notes.txt"
            notes.write_bytes(b"original user bytes\n")
            original = initializer._apply_harness_files

            def render(**kwargs):
                changes = original(**kwargs)
                notes.write_bytes(b"concurrent user bytes\n")
                notes.chmod(0o600)
                return changes

            with mock.patch.object(initializer, "_apply_harness_files", side_effect=render):
                result = self.init(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(notes.read_bytes(), b"concurrent user bytes\n")
            self.assertEqual(stat.S_IMODE(notes.stat().st_mode), 0o600)
            self.assertNotIn('"path":"notes.txt"', result.stdout)

    def test_staging_snapshot_retains_managed_file_initial_preimage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            agents = root / "AGENTS.md"
            agents.write_bytes(b"original authority\n")
            original = initializer._apply_harness_files

            def render(**kwargs):
                changes = original(**kwargs)
                agents.write_bytes(b"concurrent authority\n")
                agents.chmod(0o600)
                return changes

            with mock.patch.object(initializer, "_apply_harness_files", side_effect=render):
                result = self.init(root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("preimage changed before mutation: AGENTS.md", result.stderr)
            self.assertEqual(agents.read_bytes(), b"concurrent authority\n")
            self.assertEqual(stat.S_IMODE(agents.stat().st_mode), 0o600)
            self.assertEqual(list(root.iterdir()), [agents])

    def test_staged_runtime_does_not_import_target_or_environment_modules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp).resolve()
            root = parent / "repo"
            (root / "dev").mkdir(parents=True)
            env_modules = parent / "env-modules"
            env_modules.mkdir()
            marker = parent / "executed"
            malicious = (
                f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
                "raise RuntimeError('untrusted project code executed')\n"
            )
            (root / "dev/json.py").write_text(malicious, encoding="utf-8")
            (env_modules / "json.py").write_text(malicious, encoding="utf-8")
            before = self.filesystem_snapshot(root)
            with mock.patch.dict(os.environ, {"PYTHONPATH": str(env_modules)}):
                result = self.init(root, "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(marker.exists())
            self.assertEqual(self.filesystem_snapshot(root), before)

    def test_completed_temp_write_rechecks_original_before_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            agents = root / "AGENTS.md"
            agents.write_bytes(b"original authority\n")
            original = initializer._write_all
            injected = False

            def edit_during_temp_write(descriptor, content):
                nonlocal injected
                original(descriptor, content)
                if content.startswith(b"original authority"):
                    agents.write_bytes(b"concurrent authority\n")
                    agents.chmod(0o600)
                    injected = True

            with mock.patch.object(initializer, "_write_all", side_effect=edit_during_temp_write):
                result = self.init(root)
            self.assertEqual(result.returncode, 2)
            self.assertTrue(injected)
            self.assertIn("preimage changed before write: AGENTS.md", result.stderr)
            self.assertEqual(agents.read_bytes(), b"concurrent authority\n")
            self.assertEqual(stat.S_IMODE(agents.stat().st_mode), 0o600)
            self.assertEqual(list(root.iterdir()), [agents])

    def test_partial_write_failure_preserves_original_bytes_and_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            agents = root / "AGENTS.md"
            agents.write_bytes(b"original authority\n")
            agents.chmod(0o640)
            before = self.filesystem_snapshot(root)
            original = initializer._write_all

            def fail_partial(descriptor, content):
                if content.startswith(b"original authority"):
                    os.write(descriptor, content[:4])
                    raise OSError("injected short write failure")
                return original(descriptor, content)

            with mock.patch.object(initializer, "_write_all", side_effect=fail_partial):
                result = self.init(root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("injected short write failure", result.stderr)
            self.assertEqual(self.filesystem_snapshot(root), before)

    def test_apply_revalidates_each_preimage_and_rolls_back_prior_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            agents = root / "AGENTS.md"
            agents.write_text("# Original authority\n", encoding="utf-8")
            original_apply = initializer._apply_mutation_entry
            edited = False

            def edit_before_agents(entry: object) -> None:
                nonlocal edited
                if getattr(entry, "relative") == "AGENTS.md" and not edited:
                    agents.write_text("# Concurrent user edit\n", encoding="utf-8")
                    edited = True
                original_apply(entry)

            with mock.patch.object(initializer, "_apply_mutation_entry", side_effect=edit_before_agents):
                result = self.init(root)

            self.assertEqual(result.returncode, 2)
            self.assertTrue(edited)
            self.assertIn("preimage changed before write: AGENTS.md", result.stderr)
            self.assertEqual(agents.read_text(encoding="utf-8"), "# Concurrent user edit\n")
            self.assertEqual([path for path in root.rglob("*") if path != agents], [])

    def test_intermediate_mutation_failure_restores_exact_bytes_modes_and_created_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            agents = root / "AGENTS.md"
            agents.write_text("# Original authority\n", encoding="utf-8")
            agents.chmod(0o640)
            before = self.filesystem_snapshot(root)
            original_apply = initializer._apply_mutation_entry
            calls = 0

            def fail_after_write(entry: object) -> None:
                nonlocal calls
                original_apply(entry)
                calls += 1
                if calls == 5:
                    raise OSError("injected mutation failure")

            with mock.patch.object(initializer, "_apply_mutation_entry", side_effect=fail_after_write):
                result = self.init(root)

            self.assertEqual(result.returncode, 2)
            self.assertIn("injected mutation failure", result.stderr)
            self.assertEqual(self.filesystem_snapshot(root), before)

    def test_rollback_preserves_user_edit_to_transaction_postimage_and_reports_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            original_apply = initializer._apply_mutation_entry
            changed_path: Path | None = None

            def edit_after_write(entry: object) -> None:
                nonlocal changed_path
                original_apply(entry)
                if getattr(entry, "postimage").kind == "file":
                    changed_path = root / getattr(entry, "relative")
                    changed_path.write_text("concurrent user edit\n", encoding="utf-8")
                    raise OSError("injected failure after concurrent edit")

            with mock.patch.object(initializer, "_apply_mutation_entry", side_effect=edit_after_write):
                result = self.init(root)

            self.assertEqual(result.returncode, 2)
            self.assertIsNotNone(changed_path)
            assert changed_path is not None
            self.assertEqual(changed_path.read_text(encoding="utf-8"), "concurrent user edit\n")
            self.assertIn("rollback incomplete", result.stderr)
            self.assertIn(changed_path.relative_to(root).as_posix(), result.stderr)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO support is required")
    def test_init_refuses_fifo_and_directory_type_mismatches_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fifo = root / "AGENTS.md"
            os.mkfifo(fifo)
            result = self.init(root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("not a regular file", result.stderr)
            self.assertEqual(set(root.iterdir()), {fifo})

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            target = root / "dev/harness.py"
            target.mkdir(parents=True)
            result = self.init(root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("filesystem type", result.stderr)
            self.assertTrue(target.is_dir())
            self.assertEqual(set(root.rglob("*")), {root / "dev", target})

    def test_init_refuses_to_replace_existing_project_owned_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "dev").mkdir()
            (root / "dev" / "check").write_text("#!/bin/sh\necho project-owned\n", encoding="utf-8")
            result = self.init(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to replace existing project-owned command paths", result.stderr)
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertIn("project-owned", (root / "dev" / "check").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
