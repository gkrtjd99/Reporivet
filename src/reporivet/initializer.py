from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable, Sequence

from . import __version__

PACKAGE_ROOT = Path(__file__).resolve().parent
ASSETS = PACKAGE_ROOT / "assets" / "project"
AGENTS_START = "<!-- reporivet:start -->"
AGENTS_END = "<!-- reporivet:end -->"
GITIGNORE_START = "# reporivet:start"
GITIGNORE_END = "# reporivet:end"
MANAGED_MARKER = "reporivet:managed"
SOURCE_MARKERS = (
    "src",
    "app",
    "lib",
    "packages",
    "services",
    "package.json",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
)


class InitError(RuntimeError):
    """Raised when initialization cannot complete safely."""


@dataclass
class ChangeSet:
    created: list[Path] = field(default_factory=list)
    updated: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)

    def record(self, action: str, path: Path) -> None:
        getattr(self, action).append(path)

    def print(self, root: Path, *, dry_run: bool = False) -> None:
        prefix = "Planned" if dry_run else "Applied"
        print(f"\n{prefix} Reporivet changes")
        for label, paths in (("created", self.created), ("updated", self.updated), ("skipped", self.skipped)):
            print(f"\n{label}:")
            if not paths:
                print("  - none")
            for path in paths:
                try:
                    display = path.relative_to(root)
                except ValueError:
                    display = path
                print(f"  - {display}")


def validate_root(root: Path, *, create: bool = False, dry_run: bool = False) -> Path:
    root = root.expanduser().resolve(strict=False)
    if not root.exists():
        if not create:
            raise InitError(f"project root does not exist: {root}")
        if not dry_run:
            root.mkdir(parents=True, exist_ok=False)
        return root
    if not root.is_dir():
        raise InitError(f"project root is not a directory: {root}")
    return root


def render(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def read_asset(relative: str, values: dict[str, str] | None = None) -> str:
    path = ASSETS / relative
    if not path.exists():
        raise InitError(f"missing packaged asset: {relative}")
    text = path.read_text(encoding="utf-8")
    return render(text, values or {})


def extract_block(text: str, start: str, end: str) -> str:
    start_at = text.find(start)
    end_at = text.find(end)
    if start_at == -1 or end_at == -1 or end_at < start_at:
        raise InitError(f"template is missing managed markers: {start} / {end}")
    return text[start_at : end_at + len(end)]


def upsert_block_text(original: str, block: str, start: str, end: str) -> str:
    start_at = original.find(start)
    end_at = original.find(end)
    if (start_at == -1) != (end_at == -1) or (start_at != -1 and end_at < start_at):
        raise InitError(f"existing file has malformed managed markers: {start} / {end}")
    if start_at != -1:
        end_at += len(end)
        before = original[:start_at].rstrip()
        after = original[end_at:].lstrip("\n")
        pieces = [piece for piece in (before, block.rstrip(), after.rstrip()) if piece]
        return "\n\n".join(pieces) + "\n"
    if not original.strip():
        return block.rstrip() + "\n"
    return original.rstrip() + "\n\n" + block.rstrip() + "\n"


def _write(path: Path, content: str, changes: ChangeSet, *, dry_run: bool, allow_update: bool) -> None:
    normalized = content.rstrip() + "\n"
    if not path.exists():
        changes.created.append(path)
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(normalized, encoding="utf-8")
        return
    original = path.read_text(encoding="utf-8")
    if original == normalized:
        changes.skipped.append(path)
        return
    if not allow_update:
        changes.skipped.append(path)
        return
    changes.updated.append(path)
    if not dry_run:
        path.write_text(normalized, encoding="utf-8")


def write_if_missing(path: Path, content: str, changes: ChangeSet, *, dry_run: bool) -> None:
    _write(path, content, changes, dry_run=dry_run, allow_update=False)


def upsert_block(
    path: Path,
    block: str,
    changes: ChangeSet,
    *,
    start: str,
    end: str,
    dry_run: bool,
) -> None:
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    updated = upsert_block_text(original, block, start, end)
    _write(path, updated, changes, dry_run=dry_run, allow_update=True)


def write_managed(path: Path, content: str, changes: ChangeSet, *, mode: str, dry_run: bool) -> None:
    if mode == "init":
        _write(path, content, changes, dry_run=dry_run, allow_update=False)
        return
    if not path.exists():
        _write(path, content, changes, dry_run=dry_run, allow_update=False)
        return
    head = "\n".join(path.read_text(encoding="utf-8", errors="ignore").splitlines()[:8])
    if MANAGED_MARKER not in head:
        changes.skipped.append(path)
        return
    _write(path, content, changes, dry_run=dry_run, allow_update=True)


def set_executable(paths: Iterable[Path], *, dry_run: bool) -> None:
    if dry_run or os.name == "nt":
        return
    for path in paths:
        if path.exists():
            path.chmod(path.stat().st_mode | 0o111)


def infer_language(root: Path, supplied: str) -> str:
    if supplied.strip():
        return supplied.strip()
    mapping = (
        ("package.json", "TypeScript/JavaScript"),
        ("pyproject.toml", "Python"),
        ("requirements.txt", "Python"),
        ("go.mod", "Go"),
        ("Cargo.toml", "Rust"),
        ("pom.xml", "Java"),
        ("build.gradle", "Java/Kotlin"),
        ("build.gradle.kts", "Kotlin/Java"),
    )
    for filename, language in mapping:
        if (root / filename).exists():
            return language
    return "Not established"


def infer_runtime(root: Path, supplied: str, language: str) -> str:
    if supplied.strip():
        return supplied.strip()
    if (root / "package.json").exists():
        return "Node.js"
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        return "Python"
    if (root / "go.mod").exists():
        return "Go"
    if (root / "Cargo.toml").exists():
        return "Rust"
    if (root / "pom.xml").exists() or (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        return "JVM"
    return language


def has_existing_implementation(root: Path) -> bool:
    return any((root / marker).exists() for marker in SOURCE_MARKERS)


def source_paths(root: Path) -> list[str]:
    paths = [name for name in ("src", "app", "lib", "packages", "services") if (root / name).exists()]
    return paths or ["src"]


def test_paths(root: Path) -> list[str]:
    paths = [name for name in ("tests", "test", "spec", "__tests__") if (root / name).exists()]
    return paths or ["tests"]


def load_package_scripts(root: Path) -> tuple[str, dict[str, str]]:
    package_path = root / "package.json"
    if not package_path.exists():
        return "npm", {}
    try:
        data = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "npm", {}
    manager = "npm"
    if (root / "pnpm-lock.yaml").exists():
        manager = "pnpm"
    elif (root / "yarn.lock").exists():
        manager = "yarn"
    elif (root / "bun.lockb").exists() or (root / "bun.lock").exists():
        manager = "bun"
    scripts = data.get("scripts", {})
    return manager, scripts if isinstance(scripts, dict) else {}


def node_run(manager: str, script: str) -> list[str]:
    return ["npm", "run", script] if manager == "npm" else [manager, "run", script]


def detect_commands(root: Path) -> dict[str, list[list[str]]]:
    commands: dict[str, list[list[str]]] = {
        "bootstrap": [],
        "run": [],
        "check": [],
        "verify": [],
        "smoke": [],
        "architecture": [],
    }

    if (root / "package.json").exists():
        manager, scripts = load_package_scripts(root)
        if manager == "pnpm":
            commands["bootstrap"].append(["pnpm", "install", "--frozen-lockfile"])
        elif manager == "yarn":
            commands["bootstrap"].append(["yarn", "install", "--immutable"])
        elif manager == "bun":
            commands["bootstrap"].append(["bun", "install", "--frozen-lockfile"])
        elif (root / "package-lock.json").exists():
            commands["bootstrap"].append(["npm", "ci"])
        else:
            commands["bootstrap"].append(["npm", "install"])
        for candidate in ("dev", "start"):
            if candidate in scripts:
                commands["run"].append(node_run(manager, candidate))
                break
        if "check" in scripts:
            commands["check"].append(node_run(manager, "check"))
        else:
            for name in ("lint", "typecheck", "test"):
                if name in scripts:
                    commands["check"].append(node_run(manager, name))
        if "verify" in scripts:
            commands["verify"].append(node_run(manager, "verify"))
        else:
            commands["verify"].extend(commands["check"])
            if "build" in scripts:
                commands["verify"].append(node_run(manager, "build"))
        for candidate in ("test:smoke", "smoke", "test:e2e"):
            if candidate in scripts:
                commands["smoke"].append(node_run(manager, candidate))
                break

    pyproject_text = ""
    if (root / "pyproject.toml").exists():
        pyproject_text = (root / "pyproject.toml").read_text(encoding="utf-8", errors="ignore").lower()
        if (root / "uv.lock").exists():
            commands["bootstrap"].append(["uv", "sync", "--frozen"])
        elif (root / "poetry.lock").exists():
            commands["bootstrap"].append(["poetry", "install", "--sync"])
        else:
            commands["bootstrap"].append(["python", "-m", "pip", "install", "-e", "."])
    elif (root / "requirements.txt").exists():
        commands["bootstrap"].append(["python", "-m", "pip", "install", "-r", "requirements.txt"])

    python_checks: list[list[str]] = []
    if "ruff" in pyproject_text or (root / "ruff.toml").exists():
        python_checks.append(["python", "-m", "ruff", "check", "."])
    if "mypy" in pyproject_text or (root / "mypy.ini").exists():
        python_checks.append(["python", "-m", "mypy", "."])
    if (root / "tests").is_dir():
        if "pytest" in pyproject_text or (root / "pytest.ini").exists():
            python_checks.append(["python", "-m", "pytest"])
        elif any((root / "tests").rglob("test_*.py")):
            python_checks.append(["python", "-m", "unittest", "discover", "-s", "tests", "-v"])
    commands["check"].extend(command for command in python_checks if command not in commands["check"])
    commands["verify"].extend(command for command in python_checks if command not in commands["verify"])

    if (root / "go.mod").exists():
        commands["bootstrap"].append(["go", "mod", "download"])
        commands["check"].append(["go", "test", "./..."])
        commands["verify"].extend((["go", "test", "./..."], ["go", "vet", "./..."]))
    if (root / "Cargo.toml").exists():
        commands["bootstrap"].append(["cargo", "fetch", "--locked"] if (root / "Cargo.lock").exists() else ["cargo", "fetch"])
        commands["check"].append(["cargo", "test"])
        commands["verify"].extend(
            (
                ["cargo", "fmt", "--check"],
                ["cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings"],
                ["cargo", "test", "--all-features"],
            )
        )
    if (root / "mvnw").exists():
        commands["bootstrap"].append(["./mvnw", "dependency:go-offline"])
        commands["check"].append(["./mvnw", "test"])
        commands["verify"].append(["./mvnw", "verify"])
    elif (root / "pom.xml").exists():
        commands["bootstrap"].append(["mvn", "dependency:go-offline"])
        commands["check"].append(["mvn", "test"])
        commands["verify"].append(["mvn", "verify"])
    if (root / "gradlew").exists():
        commands["bootstrap"].append(["./gradlew", "dependencies"])
        commands["check"].append(["./gradlew", "test"])
        commands["verify"].append(["./gradlew", "check"])
    elif (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        commands["bootstrap"].append(["gradle", "dependencies"])
        commands["check"].append(["gradle", "test"])
        commands["verify"].append(["gradle", "check"])

    for key, entries in commands.items():
        unique: list[list[str]] = []
        seen: set[tuple[str, ...]] = set()
        for entry in entries:
            marker = tuple(entry)
            if marker not in seen:
                unique.append(entry)
                seen.add(marker)
        commands[key] = unique
    return commands


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_array(values: Sequence[str]) -> str:
    return "[" + ", ".join(toml_string(value) for value in values) + "]"


def toml_command_array(commands: Sequence[Sequence[str]]) -> str:
    if not commands:
        return "[]"
    rows = ["  " + toml_array(list(command)) for command in commands]
    return "[\n" + ",\n".join(rows) + ",\n]"


def build_config(
    *,
    name: str,
    summary: str,
    kind: str,
    language: str,
    runtime: str,
    root: Path,
) -> str:
    commands = detect_commands(root)
    existing = has_existing_implementation(root)
    configuration = "review" if existing else "ready"
    lines = [
        "# Project-owned configuration. The initializer never overwrites this file.",
        "# Review detected commands against the repository before setting configuration = \"ready\".",
        "version = 1",
        "",
        "[project]",
        f"name = {toml_string(name)}",
        f"summary = {toml_string(summary)}",
        f"kind = {toml_string(kind)}",
        f"primary_language = {toml_string(language)}",
        f"runtime = {toml_string(runtime)}",
        'baseline = "draft" # change to "established" after PLAN-0000 is complete',
        f'configuration = "{configuration}"',
        'default_branch = "main"',
        "",
        "[commands]",
    ]
    for key in ("bootstrap", "run", "check", "verify", "smoke", "architecture"):
        lines.append(f"{key} = {toml_command_array(commands[key])}")
    lines.extend(
        (
            "",
            "[paths]",
            f"source = {toml_array(source_paths(root))}",
            f"tests = {toml_array(test_paths(root))}",
            'generated_docs = ["docs/generated"]',
            "",
            "[policy]",
            "parallel_writes = false",
            "agents_max_lines = 140",
            "stale_plan_days = 21",
            "security_scan_max_bytes = 2097152",
            "security_allow_tracked = []",
            "require_plan_for = [",
            '  "public-api",',
            '  "persistent-data",',
            '  "authentication",',
            '  "authorization",',
            '  "payments",',
            '  "infrastructure",',
            '  "deployment",',
            "]",
        )
    )
    return "\n".join(lines) + "\n"


def config_values(
    *,
    root: Path,
    name: str,
    summary: str,
    kind: str,
    primary_language: str,
    runtime: str,
) -> dict[str, str]:
    language = infer_language(root, primary_language)
    inferred_runtime = infer_runtime(root, runtime, language)
    architecture_start = (
        "This repository already contains implementation. Establish the baseline from code, tests, build files, and runtime behavior; do not infer missing facts."
        if has_existing_implementation(root)
        else "No implementation architecture exists yet. Record only structure that has actually been introduced; proposals belong in an active ExecPlan."
    )
    return {
        "PROJECT_NAME": name,
        "PROJECT_SUMMARY": summary,
        "PROJECT_KIND": kind,
        "PRIMARY_LANGUAGE": language,
        "RUNTIME": inferred_runtime,
        "DATE": date.today().isoformat(),
        "ARCHITECTURE_START": architecture_start,
        "HARNESS_VERSION": __version__,
    }


def project_documents(kind: str) -> dict[str, str]:
    documents = {
        "ARCHITECTURE.md": "root/ARCHITECTURE.md.tmpl",
        "docs/README.md": "docs/README.md.tmpl",
        "docs/PRODUCT.md": "docs/PRODUCT.md.tmpl",
        "docs/DESIGN.md": "docs/DESIGN.md.tmpl",
        "docs/QUALITY.md": "docs/QUALITY.md.tmpl",
        "docs/SECURITY.md": "docs/SECURITY.md.tmpl",
        "docs/PLANS.md": "docs/PLANS.md.tmpl",
        "docs/product-specs/index.md": "docs/product-specs/index.md.tmpl",
        "docs/product-specs/_template.md": "docs/product-specs/_template.md.tmpl",
        "docs/design-docs/index.md": "docs/design-docs/index.md.tmpl",
        "docs/design-docs/core-beliefs.md": "docs/design-docs/core-beliefs.md.tmpl",
        "docs/design-docs/_template.md": "docs/design-docs/_template.md.tmpl",
        "docs/exec-plans/_template.md": "docs/exec-plans/_template.md.tmpl",
        "docs/exec-plans/tech-debt-tracker.md": "docs/exec-plans/tech-debt-tracker.md.tmpl",
        "docs/decisions/README.md": "docs/decisions/README.md.tmpl",
        "docs/decisions/_template.md": "docs/decisions/_template.md.tmpl",
        "docs/generated/README.md": "docs/generated/README.md.tmpl",
        "docs/references/README.md": "docs/references/README.md.tmpl",
        "docs/runbooks/index.md": "docs/runbooks/index.md.tmpl",
        "docs/runbooks/_template.md": "docs/runbooks/_template.md.tmpl",
    }
    if kind.lower() in {"service", "web", "application", "app"}:
        documents["docs/RELIABILITY.md"] = "docs/RELIABILITY.md.tmpl"
    return documents


def managed_files(with_ci: bool) -> dict[str, str]:
    files = {
        ".reporivet-version": "root/reporivet-version.tmpl",
        "dev/harness.py": "dev/harness.py",
        "dev/bootstrap": "dev/wrapper.sh.tmpl",
        "dev/context": "dev/wrapper.sh.tmpl",
        "dev/run": "dev/wrapper.sh.tmpl",
        "dev/check": "dev/wrapper.sh.tmpl",
        "dev/verify": "dev/wrapper.sh.tmpl",
        "dev/smoke": "dev/wrapper.sh.tmpl",
        "dev/security-check": "dev/wrapper.sh.tmpl",
        "dev/docs-index": "dev/wrapper.sh.tmpl",
        "dev/docs-check": "dev/wrapper.sh.tmpl",
        "dev/plan-check": "dev/wrapper.sh.tmpl",
        "dev/architecture-check": "dev/wrapper.sh.tmpl",
        "dev/new-plan": "dev/wrapper.sh.tmpl",
        "dev/task": "dev/wrapper.sh.tmpl",
        "dev/close-plan": "dev/wrapper.sh.tmpl",
        "dev/garden": "dev/wrapper.sh.tmpl",
    }
    if with_ci:
        files.update(
            {
                ".github/workflows/harness-verify.yml": "github/harness-verify.yml.tmpl",
                ".github/workflows/harness-garden.yml": "github/harness-garden.yml.tmpl",
            }
        )
    return files


def preflight_managed_conflicts(root: Path, *, with_ci: bool, mode: str) -> None:
    if mode != "init":
        return
    conflicts: list[str] = []
    for relative in managed_files(with_ci):
        path = root / relative
        if not path.exists():
            continue
        if not path.is_file():
            conflicts.append(relative)
            continue
        head = "\n".join(path.read_text(encoding="utf-8", errors="ignore").splitlines()[:8])
        if MANAGED_MARKER not in head:
            conflicts.append(relative)
    if conflicts:
        formatted = ", ".join(conflicts)
        raise InitError(
            "refusing to replace existing project-owned command paths: " + formatted +
            "; move or rename them before initialization"
        )


def ensure_directories(root: Path, *, dry_run: bool) -> None:
    if dry_run:
        return
    for relative in (
        "docs/exec-plans/active",
        "docs/exec-plans/completed",
        "docs/product-specs",
        "docs/design-docs",
        "docs/decisions",
        "docs/generated",
        "docs/references",
        ".harness/runs",
        "dev",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)
    for relative in ("docs/exec-plans/active/.gitkeep", "docs/exec-plans/completed/.gitkeep", ".harness/runs/.gitkeep"):
        path = root / relative
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")


def create_baseline_plan(root: Path, values: dict[str, str], changes: ChangeSet, *, dry_run: bool) -> None:
    active = root / "docs" / "exec-plans" / "active"
    if any(active.glob("*.md")):
        return
    destination = active / "PLAN-0000-establish-repository-baseline.md"
    content = read_asset("docs/exec-plans/baseline.md.tmpl", values)
    write_if_missing(destination, content, changes, dry_run=dry_run)


def run_generated(root: Path, command: str, *args: str) -> int:
    harness = root / "dev" / "harness.py"
    if not harness.exists():
        raise InitError("generated dev/harness.py is missing")
    completed = subprocess.run([sys.executable, str(harness), command, *args], cwd=root, check=False)
    return completed.returncode


def apply_harness(
    *,
    root: Path,
    mode: str,
    name: str,
    summary: str,
    kind: str,
    primary_language: str,
    runtime: str,
    with_ci: bool,
    baseline: bool,
    dry_run: bool,
    skip_check: bool,
) -> ChangeSet:
    root = validate_root(root, create=mode == "init", dry_run=dry_run)
    values = config_values(
        root=root,
        name=name.strip() or root.name,
        summary=summary.strip() or "TODO: define the project purpose during baseline establishment.",
        kind=kind.strip() or "other",
        primary_language=primary_language,
        runtime=runtime,
    )
    preflight_managed_conflicts(root, with_ci=with_ci, mode=mode)
    changes = ChangeSet()
    ensure_directories(root, dry_run=dry_run)

    agents_template = read_asset("root/AGENTS.md.tmpl", values)
    agents_block = extract_block(agents_template, AGENTS_START, AGENTS_END)
    upsert_block(
        root / "AGENTS.md",
        agents_block,
        changes,
        start=AGENTS_START,
        end=AGENTS_END,
        dry_run=dry_run,
    )

    gitignore_block = read_asset("root/gitignore.block.tmpl", values).strip()
    upsert_block(
        root / ".gitignore",
        gitignore_block,
        changes,
        start=GITIGNORE_START,
        end=GITIGNORE_END,
        dry_run=dry_run,
    )

    for destination, asset in project_documents(values["PROJECT_KIND"]).items():
        # Keep runtime plan tokens intact. They are resolved by the copied
        # repository-local harness when a future plan is created, not by the
        # initializer that installs the template.
        asset_values = {} if destination == "docs/exec-plans/_template.md" else values
        write_if_missing(root / destination, read_asset(asset, asset_values), changes, dry_run=dry_run)

    config_path = root / "dev" / "harness.toml"
    if not config_path.exists():
        config = build_config(
            name=values["PROJECT_NAME"],
            summary=values["PROJECT_SUMMARY"],
            kind=values["PROJECT_KIND"],
            language=values["PRIMARY_LANGUAGE"],
            runtime=values["RUNTIME"],
            root=root,
        )
        write_if_missing(config_path, config, changes, dry_run=dry_run)
    else:
        changes.skipped.append(config_path)

    for destination, asset in managed_files(with_ci).items():
        # Managed code may itself contain tokens for future repository-local
        # operations. Render only the values owned by this managed artifact so
        # project metadata such as DATE cannot accidentally rewrite source.
        local_values = {"HARNESS_VERSION": __version__}
        if asset == "dev/wrapper.sh.tmpl":
            local_values["COMMAND"] = Path(destination).name
        write_managed(root / destination, read_asset(asset, local_values), changes, mode=mode, dry_run=dry_run)

    executable = [root / path for path in managed_files(with_ci) if path.startswith("dev/")]
    set_executable(executable, dry_run=dry_run)

    if baseline and has_existing_implementation(root):
        create_baseline_plan(root, values, changes, dry_run=dry_run)

    changes.print(root, dry_run=dry_run)
    if dry_run:
        return changes

    if run_generated(root, "docs-index") != 0:
        raise InitError("docs-index failed after initialization")
    if skip_check:
        return changes
    if run_generated(root, "docs-check") != 0:
        raise InitError("docs-check failed after initialization")
    return changes


def read_existing_config(root: Path) -> dict[str, object]:
    config_path = root / "dev" / "harness.toml"
    if not config_path.exists():
        return {}
    try:
        with config_path.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise InitError(f"cannot read {config_path}: {exc}") from exc


def upgrade_project(
    *, root: Path, with_ci: bool, dry_run: bool, skip_check: bool
) -> ChangeSet:
    root = validate_root(root)
    config = read_existing_config(root)
    project = config.get("project", {}) if isinstance(config, dict) else {}
    if not isinstance(project, dict):
        project = {}
    return apply_harness(
        root=root,
        mode="upgrade",
        name=str(project.get("name", root.name)),
        summary=str(project.get("summary", "Repository-local agent harness.")),
        kind=str(project.get("kind", "other")),
        primary_language=str(project.get("primary_language", "")),
        runtime=str(project.get("runtime", "")),
        with_ci=with_ci or (root / ".github" / "workflows" / "harness-verify.yml").exists(),
        baseline=False,
        dry_run=dry_run,
        skip_check=skip_check,
    )


def doctor_project(root: Path) -> int:
    root = validate_root(root)
    errors: list[str] = []
    warnings: list[str] = []
    required = (
        "AGENTS.md",
        "ARCHITECTURE.md",
        ".reporivet-version",
        "docs/README.md",
        "docs/PRODUCT.md",
        "docs/DESIGN.md",
        "docs/QUALITY.md",
        "docs/SECURITY.md",
        "docs/PLANS.md",
        "docs/exec-plans/_template.md",
        "docs/exec-plans/tech-debt-tracker.md",
        "dev/harness.py",
        "dev/harness.toml",
        "dev/bootstrap",
        "dev/context",
        "dev/run",
        "dev/check",
        "dev/verify",
        "dev/smoke",
        "dev/security-check",
        "dev/docs-index",
        "dev/docs-check",
        "dev/plan-check",
        "dev/architecture-check",
        "dev/new-plan",
        "dev/task",
        "dev/close-plan",
        "dev/garden",
    )
    for relative in required:
        if not (root / relative).exists():
            errors.append(f"missing {relative}")
    for relative in required:
        path = root / relative
        if relative.startswith("dev/") and relative != "dev/harness.toml" and path.exists() and os.name != "nt":
            if not os.access(path, os.X_OK):
                errors.append(f"not executable: {relative}")

    harness = root / "dev" / "harness.py"
    if harness.exists():
        head = "\n".join(harness.read_text(encoding="utf-8", errors="ignore").splitlines()[:8])
        if MANAGED_MARKER not in head:
            warnings.append("dev/harness.py is not marked as managed; upgrades will preserve it")
        if f"version={__version__}" not in head:
            warnings.append(f"dev/harness.py is not at initializer version {__version__}; run reporivet upgrade --dry-run")
    if not (root / ".git").exists():
        warnings.append("no .git directory detected; plans and decisions are not yet versioned")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 2
    if harness.exists():
        for command, args in (("docs-index", ("--check",)), ("docs-check", ()), ("plan-check", ())):
            if run_generated(root, command, *args) != 0:
                return 2
    return 0

