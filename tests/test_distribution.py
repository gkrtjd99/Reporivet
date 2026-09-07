from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
ASSETS = REPOSITORY / "src" / "reporivet" / "assets" / "project"


@unittest.skipIf(os.name == "nt", "generated repository commands are POSIX shell wrappers")
class DistributionTests(unittest.TestCase):
    maxDiff = None

    def run_command(
        self,
        *command: str | Path,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [str(part) for part in command],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
        )
        return result

    def assert_success(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def isolated_environment(self, python: Path) -> dict[str, str]:
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment.update(
            {
                "PIP_DISABLE_PIP_VERSION_CHECK": "1",
                "PIP_NO_INDEX": "1",
                "PYTHON": str(python),
            }
        )
        return environment

    def copy_build_source(self, destination: Path) -> None:
        shutil.copy2(REPOSITORY / "pyproject.toml", destination / "pyproject.toml")
        shutil.copy2(REPOSITORY / "README.md", destination / "README.md")
        shutil.copytree(
            REPOSITORY / "src",
            destination / "src",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "*.egg-info"),
        )

    def expected_asset_names(self) -> set[str]:
        names: set[str] = set()
        for path in ASSETS.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(REPOSITORY / "src").as_posix()
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            names.add(relative)
        return names

    def activate_fixture(self, root: Path) -> None:
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
                text.replace("status: draft", "status: active")
                .replace("TODO", "Established")
                .replace("- [ ] Observed repository facts reviewed:", "- [x] Observed repository facts reviewed:")
                .replace("- [ ] Baseline questions resolved or tracked:", "- [x] Baseline questions resolved or tracked:"),
                encoding="utf-8",
            )
        config = root / "dev" / "harness.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'baseline = "draft"',
                'baseline = "established"',
            ),
            encoding="utf-8",
        )

    def initialize_git(self, root: Path) -> None:
        self.assert_success(self.run_command("git", "init", "-b", "main", cwd=root))
        self.assert_success(
            self.run_command("git", "config", "user.name", "Distribution Fixture", cwd=root)
        )
        self.assert_success(
            self.run_command(
                "git",
                "config",
                "user.email",
                "distribution@example.invalid",
                cwd=root,
            )
        )

    def commit_all(self, root: Path, message: str) -> str:
        self.assert_success(self.run_command("git", "add", ".", cwd=root))
        self.assert_success(self.run_command("git", "commit", "-m", message, cwd=root))
        result = self.run_command("git", "rev-parse", "HEAD", cwd=root)
        self.assert_success(result)
        return result.stdout.strip()

    def resolve_plan(self, path: Path) -> str:
        text = path.read_text(encoding="utf-8")
        text = text.replace("status: proposed", "status: verifying")
        text = text.replace('integrated_commit: ""', 'integrated_commit: "HEAD"')
        text = text.replace("TODO", "resolved")
        text = re.sub(r"\bpending\b", "resolved", text, flags=re.IGNORECASE)
        text = text.replace("- [ ]", "- [x]")
        text = re.sub(r"(#### State\n\n)(ready|blocked)", r"\1complete", text)
        path.write_text(text, encoding="utf-8")
        match = re.search(r"^id:\s*(\S+)", text, re.MULTILINE)
        self.assertIsNotNone(match)
        return match.group(1)

    def test_wheel_install_and_repository_operation_after_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp).resolve()
            source = temporary / "source"
            source.mkdir()
            self.copy_build_source(source)
            wheel_directory = temporary / "wheelhouse"
            wheel_directory.mkdir()
            build_environment = self.isolated_environment(Path(sys.executable))

            built = self.run_command(
                sys.executable,
                "-m",
                "pip",
                "wheel",
                source,
                "--no-build-isolation",
                "--no-deps",
                "--no-index",
                "--wheel-dir",
                wheel_directory,
                env=build_environment,
            )
            self.assert_success(built)
            wheels = sorted(wheel_directory.glob("*.whl"))
            self.assertEqual([path.name for path in wheels], ["reporivet-0.2.0-py3-none-any.whl"])
            wheel = wheels[0]

            with zipfile.ZipFile(wheel) as archive:
                names = set(archive.namelist())
                packaged_assets = {
                    name for name in names if name.startswith("reporivet/assets/project/")
                }
                self.assertEqual(packaged_assets, self.expected_asset_names())
                for name in names:
                    parts = tuple(part.lower() for part in Path(name).parts)
                    self.assertNotIn("__pycache__", parts)
                    self.assertFalse(name.endswith((".pyc", ".pyo")), name)
                    self.assertNotEqual(Path(name).name.lower(), "skill.md")
                    self.assertTrue(
                        set(parts).isdisjoint(
                            {"target", "targets", "model", "models", "daemon", "daemons"}
                        ),
                        name,
                    )
                metadata_name = next(
                    name for name in names if name.endswith(".dist-info/METADATA")
                )
                metadata = archive.read(metadata_name).decode("utf-8")
                self.assertIn("\nVersion: 0.2.0\n", metadata)
                self.assertNotIn("\nRequires-Dist:", metadata)

            virtualenv = temporary / "venv"
            self.assert_success(self.run_command(sys.executable, "-m", "venv", virtualenv))
            bin_directory = virtualenv / "bin"
            python = bin_directory / "python"
            reporivet = bin_directory / "reporivet"
            environment = self.isolated_environment(python)
            installed = self.run_command(
                python,
                "-m",
                "pip",
                "install",
                "--no-index",
                "--no-deps",
                wheel,
                env=environment,
            )
            self.assert_success(installed)
            self.assert_success(self.run_command(reporivet, "--help", env=environment))

            project = temporary / "project"
            initialized = self.run_command(
                reporivet,
                "init",
                "--root",
                project,
                "--name",
                "Distribution Fixture",
                "--summary",
                "A generated repository that survives package removal.",
                "--project-kind",
                "service",
                "--with-ci",
                "--skip-check",
                env=environment,
            )
            self.assert_success(initialized)
            self.assertNotIn(
                "import reporivet",
                (project / "dev" / "harness.py").read_text(encoding="utf-8"),
            )
            self.assertTrue((project / "docs/generated/repository-facts.md").is_file())
            self.assertTrue((project / "docs/generated/baseline-questions.md").is_file())
            self.assert_success(self.run_command(reporivet, "doctor", "--root", project, env=environment))
            self.assert_success(
                self.run_command(project / "dev" / "verify", cwd=project, env=environment)
            )

            definition = temporary / "definition"
            self.assert_success(
                self.run_command(reporivet, "define", "--root", definition, env=environment)
            )
            self.assert_success(
                self.run_command(reporivet, "audit", "--root", definition, env=environment)
            )

            uninstalled = self.run_command(
                python,
                "-m",
                "pip",
                "uninstall",
                "-y",
                "reporivet",
                env=environment,
            )
            self.assert_success(uninstalled)
            missing_package = self.run_command(
                python,
                "-I",
                "-c",
                "import reporivet",
                env=environment,
            )
            self.assertNotEqual(missing_package.returncode, 0)

            for command in (
                (project / "dev" / "audit",),
                (project / "dev" / "context",),
                (project / "dev" / "check",),
                (project / "dev" / "verify",),
                (project / "dev" / "garden",),
                (definition / "dev" / "define", "status"),
                (definition / "dev" / "audit",),
                (
                    definition / "dev" / "context",
                    "--path",
                    "docs/product-specs/project-definition.draft.md",
                    "--include-drafts",
                ),
            ):
                self.assert_success(self.run_command(*command, cwd=command[0].parents[1], env=environment))

            self.activate_fixture(project)
            self.initialize_git(project)
            self.commit_all(project, "base")
            created = self.run_command(
                project / "dev" / "new-plan",
                "Distribution",
                "closure",
                "--area",
                "test",
                cwd=project,
                env=environment,
            )
            self.assert_success(created)
            plan_path = project / created.stdout.strip()
            plan_id = self.resolve_plan(plan_path)
            task = self.run_command(
                project / "dev" / "task",
                plan_id,
                "T1",
                cwd=project,
                env=environment,
            )
            self.assert_success(task)
            candidate = self.commit_all(project, "candidate")
            closed = self.run_command(
                project / "dev" / "close-plan",
                plan_id,
                cwd=project,
                env=environment,
            )
            self.assert_success(closed)
            completed = project / "docs" / "exec-plans" / "completed" / plan_path.name
            self.assertTrue(completed.is_file())
            text = completed.read_text(encoding="utf-8")
            self.assertRegex(
                text,
                re.compile(
                    rf'^verified_commit:\s*"?{re.escape(candidate)}"?$',
                    re.MULTILINE,
                ),
            )
            self.assertRegex(
                text,
                re.compile(r'^gate_verdict:\s*"?PASS"?$', re.MULTILINE),
            )
            gates = sorted((project / ".harness" / "runs").glob("*-verify/gate.json"))
            gate = json.loads(gates[-1].read_text(encoding="utf-8"))
            self.assertEqual(gate["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
