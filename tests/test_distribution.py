from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import venv
import zipfile
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]


class DistributionTests(unittest.TestCase):
    def command(self, *command: str | Path, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run([str(item) for item in command], cwd=cwd, env=env, text=True, capture_output=True, check=False, timeout=120)

    def test_wheel_contains_only_entrypoint_assets_and_cli_survives_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "source"
            source.mkdir()
            shutil.copy2(REPOSITORY / "pyproject.toml", source / "pyproject.toml")
            shutil.copy2(REPOSITORY / "README.md", source / "README.md")
            shutil.copytree(REPOSITORY / "src", source / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.egg-info"))
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            env = os.environ.copy()
            for key in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE"):
                env.pop(key, None)
            env.update({"PIP_NO_INDEX": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_CONFIG_FILE": os.devnull})
            built = self.command(sys.executable, "-m", "pip", "wheel", source, "--no-build-isolation", "--no-deps", "--no-index", "--wheel-dir", wheelhouse, env=env)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            wheels = sorted(wheelhouse.glob("*.whl"))
            self.assertEqual(len(wheels), 1)
            with zipfile.ZipFile(wheels[0]) as archive:
                names = archive.namelist()
                self.assertTrue(any(name.endswith("/initializer.py") for name in names))
                self.assertTrue(any(name.endswith("/cli.py") for name in names))
                self.assertTrue(any(name.endswith("AGENTS.md.tmpl") for name in names))
                self.assertFalse(any("assets/project/dev/" in name for name in names))
                self.assertFalse(any("assets/project/docs/" in name for name in names))
                self.assertFalse(any(name.endswith((".pyc", ".pyo")) for name in names))
                metadata = next(archive.read(name).decode() for name in names if name.endswith(".dist-info/METADATA"))
                self.assertIn("Version: 0.3.0.dev1", metadata)

            project = root / "project"
            project.mkdir()
            env_dir = root / "venv"
            venv.EnvBuilder(with_pip=True, clear=True).create(env_dir)
            python = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            installed = self.command(python, "-m", "pip", "install", "--no-index", "--no-deps", wheels[0], env=env)
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            imported = self.command(python, "-I", "-c", "import reporivet; print(reporivet.__file__)", cwd=root, env=env)
            self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
            self.assertTrue(Path(imported.stdout.strip()).resolve().is_relative_to(env_dir))
            cli = env_dir / ("Scripts/reporivet.exe" if os.name == "nt" else "bin/reporivet")
            for command in (("init", "--root", project), ("audit", "--root", project), ("doctor", "--root", project)):
                result = self.command(cli, *command, cwd=root, env=env)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            agents_before = (project / "AGENTS.md").read_bytes()
            removed = self.command(python, "-m", "pip", "uninstall", "-y", "reporivet", env=env)
            self.assertEqual(removed.returncode, 0, removed.stdout + removed.stderr)
            absent = self.command(python, "-I", "-c", "import importlib.util; assert importlib.util.find_spec('reporivet') is None", cwd=root, env=env)
            self.assertEqual(absent.returncode, 0, absent.stdout + absent.stderr)
            self.assertFalse(cli.exists())
            self.assertEqual(agents_before, (project / "AGENTS.md").read_bytes())
            self.assertFalse((project / "dev").exists())


if __name__ == "__main__":
    unittest.main()
