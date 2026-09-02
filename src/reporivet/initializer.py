from __future__ import annotations

import json
import os
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

PACKAGE_ROOT = Path(__file__).resolve().parent
ASSETS = PACKAGE_ROOT / "assets" / "project"
# Retained solely for the public legacy migration parser.  Current setup does
# not generate or inventory a managed marker.
MANAGED_MARKER = re.compile(r"# reporivet:managed version=[^\s]+")
AUDIT_STATUSES = frozenset({"confirmed", "inferred", "unknown", "conflict", "skipped"})
AUDIT_COMMAND_GROUPS = ("bootstrap", "run", "check", "verify", "smoke", "architecture")
AUDIT_IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".harness",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "coverage",
        "dist",
        "node_modules",
        "out",
        "target",
        "vendor",
    }
)
AUDIT_MANIFEST_NAMES = frozenset(
    {
        "Cargo.toml",
        "Gemfile",
        "Package.swift",
        "Pipfile",
        "build.gradle",
        "build.gradle.kts",
        "composer.json",
        "go.mod",
        "package.json",
        "pom.xml",
        "pyproject.toml",
        "requirements.txt",
    }
)
AUDIT_LOCKFILE_NAMES = frozenset(
    {
        "Cargo.lock",
        "Gemfile.lock",
        "Package.resolved",
        "Pipfile.lock",
        "bun.lock",
        "bun.lockb",
        "composer.lock",
        "go.sum",
        "gradle.lockfile",
        "package-lock.json",
        "pnpm-lock.yaml",
        "poetry.lock",
        "uv.lock",
        "yarn.lock",
    }
)
AUDIT_RUNTIME_CONFIG_NAMES = frozenset(
    {
        ".node-version",
        ".python-version",
        ".tool-versions",
        "dev/harness.toml",
    }
)
AUDIT_SOURCE_DIRECTORIES = ("src", "app", "lib", "packages", "services")
AUDIT_TEST_DIRECTORIES = ("tests", "test", "spec", "__tests__")


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


@dataclass(frozen=True)
class AuditFinding:
    category: str
    status: str
    path: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        if self.status not in AUDIT_STATUSES:
            raise InitError(f"unsupported audit status: {self.status}")
        return {
            "category": self.category,
            "detail": self.detail,
            "path": self.path,
            "status": self.status,
        }


@dataclass(frozen=True)
class AuditReport:
    findings: tuple[AuditFinding, ...]

    @property
    def conflicts(self) -> tuple[AuditFinding, ...]:
        return tuple(finding for finding in self.findings if finding.status == "conflict")

    def as_dict(self) -> dict[str, object]:
        counts = {
            status: sum(1 for finding in self.findings if finding.status == status)
            for status in sorted(AUDIT_STATUSES)
        }
        return {
            "counts": counts,
            "findings": [finding.as_dict() for finding in self.findings],
            "schema": "reporivet.audit/v1",
        }

    def render(self) -> str:
        return json.dumps(
            self.as_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"


def validate_root(root: Path, *, create: bool = False, dry_run: bool = False) -> Path:
    expanded = root.expanduser()
    absolute = Path(os.path.abspath(expanded))
    component = symlink_component(absolute)
    if component is not None:
        raise InitError(
            f"refusing to use a symlinked project root or parent: {root} "
            f"(via {component})"
        )
    non_directory_parent = next(
        (
            parent
            for parent in absolute.parents
            if parent.exists() and not parent.is_dir()
        ),
        None,
    )
    if non_directory_parent is not None:
        raise InitError(
            f"project root parent is not a directory: {root} "
            f"(via {non_directory_parent})"
        )
    if not absolute.exists():
        if not create:
            raise InitError(f"project root does not exist: {root}")
        if not dry_run:
            absolute.mkdir(parents=True, exist_ok=False)
        return absolute
    if not absolute.is_dir():
        raise InitError(f"project root is not a directory: {root}")
    return absolute


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


def symlink_component(path: Path) -> Path | None:
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            return candidate
    return None


def ensure_safe_write_path(path: Path) -> None:
    component = symlink_component(path)
    if component is not None:
        raise InitError(f"refusing to write through symlink path: {path} (via {component})")


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


def has_python_test_files(root: Path) -> bool:
    tests = root / "tests"
    if not tests.is_dir() or tests.is_symlink():
        return False
    for current_text, directory_names, file_names in os.walk(tests, topdown=True, followlinks=False):
        current = Path(current_text)
        directory_names[:] = [
            name
            for name in sorted(directory_names)
            if not (current / name).is_symlink()
        ]
        if any(name.startswith("test_") and name.endswith(".py") for name in file_names):
            return True
    return False


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
        elif has_python_test_files(root):
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


def validate_audit_root(root: Path) -> Path:
    expanded = root.expanduser()
    absolute = Path(os.path.abspath(expanded))
    component = symlink_component(absolute)
    if component is not None:
        raise InitError(
            f"refusing to audit a symlinked project root or parent: {root} "
            f"(via {component})"
        )
    canonical = absolute.resolve(strict=False)
    if not canonical.exists():
        raise InitError(f"project root does not exist: {root}")
    if not canonical.is_dir():
        raise InitError(f"project root is not a directory: {root}")
    return canonical


def audit_relative(path: Path, root: Path) -> str:
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError:
        return "."
    return relative or "."


def audit_symlink_component(root: Path, path: Path) -> Path | None:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return path
    candidate = root
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            return candidate
    return None


def audit_repository_entries(root: Path) -> tuple[list[Path], list[AuditFinding]]:
    files: list[Path] = []
    skipped: list[AuditFinding] = []

    def record_walk_error(error: OSError) -> None:
        path = Path(error.filename) if error.filename else root
        skipped.append(
            AuditFinding(
                category="skipped-path",
                status="skipped",
                path=audit_relative(path, root),
                detail="path could not be read during inventory",
            )
        )

    for current_text, directory_names, file_names in os.walk(
        root,
        topdown=True,
        followlinks=False,
        onerror=record_walk_error,
    ):
        current = Path(current_text)
        retained_directories: list[str] = []
        for name in sorted(directory_names):
            path = current / name
            relative = audit_relative(path, root)
            if path.is_symlink():
                skipped.append(
                    AuditFinding(
                        category="skipped-path",
                        status="skipped",
                        path=relative,
                        detail="symbolic-link directory was not traversed",
                    )
                )
            elif name in AUDIT_IGNORED_DIRECTORIES:
                skipped.append(
                    AuditFinding(
                        category="skipped-path",
                        status="skipped",
                        path=relative,
                        detail="generated, dependency, or repository state was not inventoried",
                    )
                )
            else:
                retained_directories.append(name)
        directory_names[:] = retained_directories

        for name in sorted(file_names):
            path = current / name
            relative = audit_relative(path, root)
            if path.is_symlink():
                skipped.append(
                    AuditFinding(
                        category="skipped-path",
                        status="skipped",
                        path=relative,
                        detail="symbolic-link file was not read",
                    )
                )
            elif path.is_file():
                files.append(path)
            else:
                skipped.append(
                    AuditFinding(
                        category="skipped-path",
                        status="skipped",
                        path=relative,
                        detail="non-regular filesystem entry was not read",
                    )
                )
    return files, skipped


def audit_file_category(relative: str) -> str | None:
    path = Path(relative)
    name = path.name
    lower = relative.casefold()
    if name in {"AGENTS.md", "CLAUDE.md"} or lower.endswith("copilot-instructions.md"):
        return "instruction"
    if name in AUDIT_MANIFEST_NAMES:
        return "manifest"
    if name in AUDIT_LOCKFILE_NAMES:
        return "lockfile"
    if (
        lower.startswith(".github/workflows/")
        or lower in {".gitlab-ci.yml", "azure-pipelines.yml", "bitbucket-pipelines.yml"}
    ):
        return "ci"
    if relative in AUDIT_RUNTIME_CONFIG_NAMES:
        return "runtime-config"
    if path.parts and path.parts[0] in {"dev", "scripts", "bin"}:
        return "entry-point"
    if name in {"Makefile", "justfile", "Taskfile.yml", "Taskfile.yaml"}:
        return "entry-point"
    if lower.startswith("docs/") or (len(path.parts) == 1 and name.casefold().endswith(".md")):
        return "durable-document"
    return None


def audit_command_detail(command: Sequence[str], *, configured: bool) -> str:
    if configured:
        return f"configured argv command; argc={len(command)}; content=redacted"
    return json.dumps(list(command), ensure_ascii=False, separators=(",", ":"))


def audit_command_findings(root: Path) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    config_path = root / "dev" / "harness.toml"
    config_component = audit_symlink_component(root, config_path)
    if config_component is not None:
        findings.append(
            AuditFinding(
                category="command",
                status="conflict",
                path="dev/harness.toml",
                detail="command configuration is behind a symbolic-link path",
            )
        )
        return findings
    if config_path.exists() and not config_path.is_file():
        findings.append(
            AuditFinding(
                category="command",
                status="conflict",
                path="dev/harness.toml",
                detail="command configuration path is not a regular file",
            )
        )
        return findings

    commands: dict[str, object]
    configuration = "review"
    configured = config_path.is_file()
    if configured:
        try:
            with config_path.open("rb") as handle:
                data = tomllib.load(handle)
        except (OSError, UnicodeError, tomllib.TOMLDecodeError):
            findings.append(
                AuditFinding(
                    category="command",
                    status="conflict",
                    path="dev/harness.toml",
                    detail="command configuration is not valid TOML",
                )
            )
            return findings
        project = data.get("project", {})
        commands = data.get("commands", {})
        if not isinstance(project, dict) or not isinstance(commands, dict):
            findings.append(
                AuditFinding(
                    category="command",
                    status="conflict",
                    path="dev/harness.toml",
                    detail="command configuration tables are malformed",
                )
            )
            return findings
        configuration_value = project.get("configuration", "review")
        if not isinstance(configuration_value, str) or configuration_value.casefold() not in {"ready", "review"}:
            findings.append(
                AuditFinding(
                    category="command",
                    status="conflict",
                    path="dev/harness.toml",
                    detail="project.configuration must be ready or review",
                )
            )
            return findings
        configuration = configuration_value.casefold()
    else:
        command_inputs = (
            "package.json",
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            "bun.lock",
            "bun.lockb",
            "pyproject.toml",
            "requirements.txt",
            "uv.lock",
            "poetry.lock",
            "ruff.toml",
            "mypy.ini",
            "pytest.ini",
            "go.mod",
            "Cargo.toml",
            "Cargo.lock",
            "pom.xml",
            "mvnw",
            "build.gradle",
            "build.gradle.kts",
            "gradlew",
            "tests",
        )
        unsafe = [
            relative
            for relative in command_inputs
            if audit_symlink_component(root, root / relative) is not None
        ]
        nonregular: list[str] = []
        for relative in command_inputs:
            if relative in unsafe:
                continue
            path = root / relative
            if not path.exists():
                continue
            expected_type = path.is_dir() if relative == "tests" else path.is_file()
            if not expected_type:
                nonregular.append(relative)
        if unsafe or nonregular:
            for relative in unsafe:
                findings.append(
                    AuditFinding(
                        category="command",
                        status="conflict",
                        path=relative,
                        detail="command inference input is behind a symbolic-link path",
                    )
                )
            for relative in nonregular:
                findings.append(
                    AuditFinding(
                        category="command",
                        status="conflict",
                        path=relative,
                        detail="command inference input has an unexpected filesystem type",
                    )
                )
            for group in AUDIT_COMMAND_GROUPS:
                findings.append(
                    AuditFinding(
                        category="command",
                        status="unknown",
                        path=f"commands/{group}",
                        detail="command inference was not attempted because an input path is unsafe",
                    )
                )
            return findings
        package_path = root / "package.json"
        if package_path.is_file():
            try:
                package_data = json.loads(package_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                findings.append(
                    AuditFinding(
                        category="command",
                        status="conflict",
                        path="package.json",
                        detail="package manifest could not be parsed for command inference",
                    )
                )
                return findings
            if not isinstance(package_data, dict):
                findings.append(
                    AuditFinding(
                        category="command",
                        status="conflict",
                        path="package.json",
                        detail="package manifest must contain a JSON object",
                    )
                )
                return findings
        pyproject_path = root / "pyproject.toml"
        if pyproject_path.is_file():
            try:
                pyproject_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                findings.append(
                    AuditFinding(
                        category="command",
                        status="conflict",
                        path="pyproject.toml",
                        detail="Python project manifest could not be read for command inference",
                    )
                )
                return findings
        commands = detect_commands(root)

    for group in AUDIT_COMMAND_GROUPS:
        entries = commands.get(group, [])
        if not isinstance(entries, list):
            findings.append(
                AuditFinding(
                    category="command",
                    status="conflict",
                    path=f"commands/{group}",
                    detail="command group must be an array",
                )
            )
            continue
        if not entries:
            findings.append(
                AuditFinding(
                    category="command",
                    status="unknown",
                    path=f"commands/{group}",
                    detail="no command is configured or safely inferred",
                )
            )
            continue
        for index, entry in enumerate(entries, start=1):
            if (
                not isinstance(entry, list)
                or not entry
                or any(not isinstance(argument, str) or not argument for argument in entry)
            ):
                findings.append(
                    AuditFinding(
                        category="command",
                        status="conflict",
                        path=f"commands/{group}/{index}",
                        detail="command must be a non-empty array of non-empty strings",
                    )
                )
                continue
            findings.append(
                AuditFinding(
                    category="command",
                    status=("confirmed" if configured and configuration == "ready" else "inferred"),
                    path=f"commands/{group}/{index}",
                    detail=audit_command_detail(entry, configured=configured),
                )
            )
    return findings


def audit_project(*, root: Path) -> AuditReport:
    root = validate_audit_root(root)
    files, findings = audit_repository_entries(root)
    for path in files:
        relative = audit_relative(path, root)
        category = audit_file_category(relative)
        if category is not None:
            findings.append(
                AuditFinding(
                    category=category,
                    status="confirmed",
                    path=relative,
                    detail="existing repository authority inventoried without execution",
                )
            )

    source_directories = [
        name
        for name in AUDIT_SOURCE_DIRECTORIES
        if (root / name).is_dir() and not (root / name).is_symlink()
    ]
    test_directories = [
        name
        for name in AUDIT_TEST_DIRECTORIES
        if (root / name).is_dir() and not (root / name).is_symlink()
    ]
    if source_directories:
        for relative in source_directories:
            findings.append(
                AuditFinding("source-path", "confirmed", relative, "existing source boundary inventoried")
            )
    else:
        findings.append(
            AuditFinding("source-path", "unknown", "source", "no conventional source boundary was found")
        )
    if test_directories:
        for relative in test_directories:
            findings.append(
                AuditFinding("test-path", "confirmed", relative, "existing test boundary inventoried")
            )
    else:
        findings.append(
            AuditFinding("test-path", "unknown", "tests", "no conventional test boundary was found")
        )

    findings.extend(audit_command_findings(root))
    unique = {
        (finding.category, finding.status, finding.path, finding.detail): finding
        for finding in findings
    }
    ordered = tuple(
        unique[key]
        for key in sorted(unique, key=lambda item: (item[0], item[2], item[1], item[3]))
    )
    return AuditReport(ordered)


def initialize_project(
    *,
    root: Path,
    name: str,
    summary: str,
    dry_run: bool,
) -> ChangeSet:
    from .guided import maintain_document_first_bundle

    return maintain_document_first_bundle(
        root=root,
        name=name,
        summary=summary,
        create=True,
        dry_run=dry_run,
    )


def upgrade_project(*, root: Path, dry_run: bool) -> ChangeSet:
    root = validate_root(root)
    from .migration import legacy_02_upgrade_surfaces_present

    if legacy_02_upgrade_surfaces_present(root):
        raise InitError(
            "ordinary upgrade cannot retire legacy 0.2 runtime surfaces; preview the explicit migration first: "
            f"reporivet migrate --root {root} --from 0.2 --preview --backup-dir <external-path>"
        )
    from .guided import maintain_document_first_bundle

    return maintain_document_first_bundle(
        root=root,
        create=False,
        dry_run=dry_run,
    )
