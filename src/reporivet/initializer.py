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
CATALOG_START = "<!-- reporivet:catalog:start -->"
CATALOG_END = "<!-- reporivet:catalog:end -->"
MANAGED_MARKER = re.compile(r"# reporivet:managed version=[^\s]+")
DEFINITION_DRAFT_PATH = Path("docs/product-specs/project-definition.draft.md")
AUDIT_STATUSES = frozenset({"confirmed", "inferred", "unknown", "conflict", "skipped"})
AUDIT_COMMAND_GROUPS = ("bootstrap", "run", "check", "verify", "smoke", "architecture")
DOCUMENT_CAPABILITIES = ("visual-design", "frontend", "product-sense", "reliability")
DOCUMENT_CAPABILITY_KEYS = {
    "visual-design": "visual_design",
    "frontend": "frontend",
    "product-sense": "product_sense",
    "reliability": "reliability",
}
PROJECT_KIND_DOCUMENT_DEFAULTS = {
    "service": frozenset({"reliability"}),
    "web": frozenset({"visual-design", "frontend", "reliability"}),
    "application": frozenset({"reliability"}),
    "app": frozenset({"reliability"}),
    "library": frozenset(),
    "cli": frozenset(),
    "other": frozenset(),
}
PROJECT_CONFIG_KINDS = tuple(PROJECT_KIND_DOCUMENT_DEFAULTS)
OPTIONAL_DOCUMENT_ASSETS = {
    "visual-design": ("docs/DESIGN.md", "docs/DESIGN.md.tmpl"),
    "frontend": ("docs/FRONTEND.md", "docs/FRONTEND.md.tmpl"),
    "product-sense": ("docs/PRODUCT_SENSE.md", "docs/PRODUCT_SENSE.md.tmpl"),
    "reliability": ("docs/RELIABILITY.md", "docs/RELIABILITY.md.tmpl"),
}
GATE_PROTECTED_PATHS = (
    ".github/workflows/**",
    "AGENTS.md",
    "dev/harness.py",
    "dev/harness.toml",
    "docs/SECURITY.md",
)
GATE_CONTAINED_PATHS = ("docs/**", "src/**", "tests/**")
GATE_WIDE_PATHS = (
    ".github/**",
    "ARCHITECTURE.md",
    "Cargo.toml",
    "build.gradle",
    "build.gradle.kts",
    "dev/**",
    "go.mod",
    "package.json",
    "pom.xml",
    "pyproject.toml",
)
GATE_IRREVERSIBLE_PATHS = (
    "db/migrations/**",
    "infrastructure/**",
    "migrations/**",
    "schema/migrations/**",
    "terraform/**",
)
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
        ".reporivet-version",
        ".tool-versions",
        "dev/harness.toml",
    }
)
AUDIT_SOURCE_DIRECTORIES = ("src", "app", "lib", "packages", "services")
AUDIT_TEST_DIRECTORIES = ("tests", "test", "spec", "__tests__")
AUDIT_CATALOG_PATHS = frozenset(
    {
        "docs/README.md",
        "docs/product-specs/index.md",
        "docs/design-docs/index.md",
        "docs/decisions/README.md",
        "docs/runbooks/index.md",
    }
)
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
COMMAND_INFERENCE_INPUTS = (
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
HARNESS_DIRECTORY_PATHS = frozenset(
    {
        ".",
        ".github",
        ".github/workflows",
        ".harness",
        ".harness/runs",
        "dev",
        "docs",
        "docs/decisions",
        "docs/design-docs",
        "docs/exec-plans",
        "docs/exec-plans/active",
        "docs/exec-plans/completed",
        "docs/generated",
        "docs/module-contracts",
        "docs/product-specs",
        "docs/references",
        "docs/runbooks",
    }
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


@dataclass(frozen=True)
class MutationImage:
    kind: str
    mode: int | None
    sha256: str | None
    content: bytes | None = field(default=None, repr=False, compare=False)

    def as_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "sha256": self.sha256,
            "type": self.kind,
        }


@dataclass(frozen=True)
class MutationEntry:
    root: Path = field(repr=False, compare=False)
    relative: str
    action: str
    preimage: MutationImage
    postimage: MutationImage

    @property
    def path(self) -> Path:
        return self.root if self.relative == "." else self.root / self.relative

    def as_dict(self) -> dict[str, object]:
        return {
            "action": self.action,
            "path": self.relative,
            "postimage": self.postimage.as_dict(),
            "preimage": self.preimage.as_dict(),
        }


@dataclass(frozen=True)
class MutationPlan:
    root: Path = field(repr=False, compare=False)
    entries: tuple[MutationEntry, ...]

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(
            [entry.as_dict() for entry in self.entries],
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def print(self) -> None:
        print(f"Mutation plan fingerprint: {self.fingerprint}")
        print("Mutation plan entries:")
        if not self.entries:
            print("  - none")
            return
        for entry in self.entries:
            print(
                "  - "
                + json.dumps(
                    entry.as_dict(),
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )
            )


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


def mutation_relative(path: Path, root: Path) -> str:
    if path == root:
        return "."
    try:
        return path.relative_to(root).as_posix()
    except ValueError as exc:
        raise InitError(f"mutation path is outside the project root: {path}") from exc


def capture_mutation_image(path: Path, *, root: Path) -> MutationImage:
    relative = mutation_relative(path, root)
    ensure_safe_write_path(path)
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return MutationImage("missing", None, None)
    except OSError as exc:
        raise InitError(f"cannot inspect mutation path {relative}: {exc}") from exc
    mode = stat.S_IMODE(metadata.st_mode)
    if stat.S_ISDIR(metadata.st_mode):
        return MutationImage("directory", mode, None)
    if not stat.S_ISREG(metadata.st_mode):
        raise InitError(f"mutation target is not a regular file or directory: {relative}")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode):
                raise InitError(f"mutation target changed filesystem type while reading: {relative}")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
        finally:
            os.close(descriptor)
    except InitError:
        raise
    except OSError as exc:
        raise InitError(f"cannot read mutation target {relative}: {exc}") from exc
    content = b"".join(chunks)
    return MutationImage(
        "file",
        stat.S_IMODE(opened.st_mode),
        hashlib.sha256(content).hexdigest(),
        content,
    )


def mutation_image_matches(path: Path, image: MutationImage, *, root: Path) -> bool:
    try:
        current = capture_mutation_image(path, root=root)
    except InitError:
        return False
    return (
        current.kind == image.kind
        and current.mode == image.mode
        and current.sha256 == image.sha256
    )


def preflight_mutation_target_types(
    root: Path,
    *,
    kind: str,
    capabilities: Iterable[str] | None,
    with_ci: bool,
    include_definition_draft: bool,
) -> None:
    for relative in harness_target_relative_paths(
        kind=kind,
        capabilities=capabilities,
        with_ci=with_ci,
        include_definition_draft=include_definition_draft,
    ):
        path = root / relative
        ensure_safe_write_path(path)
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise InitError(f"cannot inspect mutation target {relative}: {exc}") from exc
        expected_directory = relative in HARNESS_DIRECTORY_PATHS
        actual_directory = stat.S_ISDIR(metadata.st_mode)
        actual_file = stat.S_ISREG(metadata.st_mode)
        if expected_directory and not actual_directory:
            raise InitError(f"mutation target has an unexpected filesystem type; expected directory: {relative}")
        if not expected_directory and not actual_file:
            raise InitError(
                f"mutation target has an unexpected filesystem type and is not a regular file: {relative}"
            )


def preflight_command_inference_inputs(root: Path) -> None:
    for relative in COMMAND_INFERENCE_INPUTS:
        path = root / relative
        ensure_safe_write_path(path)
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise InitError(f"cannot inspect command inference input {relative}: {exc}") from exc
        expected_directory = relative == "tests"
        if expected_directory and not stat.S_ISDIR(metadata.st_mode):
            raise InitError(f"command inference input has an unexpected filesystem type: {relative}")
        if not expected_directory and not stat.S_ISREG(metadata.st_mode):
            raise InitError(f"command inference input is not a regular file: {relative}")


def is_managed_file(path: Path) -> bool:
    if symlink_component(path) is not None or not path.is_file():
        return False
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:3]
    except OSError:
        return False
    return any(MANAGED_MARKER.fullmatch(line) is not None for line in lines)


def marker_line_spans(text: str, marker: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    markdown_marker = marker.startswith("<!--")
    fence_character = ""
    fence_length = 0
    offset = 0
    for line in text.splitlines(keepends=True):
        content = line[:-1] if line.endswith("\n") else line
        probe = content[:-1] if content.endswith("\r") else content
        stripped = probe.lstrip(" \t")
        indentation = len(probe) - len(stripped)
        consider_marker = True
        if markdown_marker and fence_character:
            closing = re.match(
                rf"{re.escape(fence_character)}{{{fence_length},}}",
                stripped,
            )
            if closing is not None and not stripped[closing.end() :].strip():
                fence_character = ""
                fence_length = 0
            consider_marker = False
        elif markdown_marker and indentation <= 3:
            opening = re.match(r"`{3,}|~{3,}", stripped)
            if opening is not None:
                fence_character = opening.group(0)[0]
                fence_length = len(opening.group(0))
                consider_marker = False
        if (
            consider_marker
            and probe.strip(" \t") == marker
            and (not markdown_marker or indentation <= 3)
        ):
            spans.append((offset, offset + len(content)))
        offset += len(line)
    return spans


def managed_block_span(text: str, start: str, end: str) -> tuple[int, int] | None:
    starts = marker_line_spans(text, start)
    ends = marker_line_spans(text, end)
    if not starts and not ends:
        return None
    if len(starts) != 1 or len(ends) != 1 or ends[0][0] < starts[0][1]:
        raise InitError(f"existing file has malformed managed markers: {start} / {end}")
    return starts[0][0], ends[0][1]


def extract_block(text: str, start: str, end: str) -> str:
    try:
        span = managed_block_span(text, start, end)
    except InitError as exc:
        raise InitError(f"template has malformed managed markers: {start} / {end}") from exc
    if span is None:
        raise InitError(f"template is missing managed markers: {start} / {end}")
    return text[span[0] : span[1]]


def upsert_block_text(original: str, block: str, start: str, end: str) -> str:
    span = managed_block_span(original, start, end)
    if span is not None:
        before = original[: span[0]].rstrip()
        after = original[span[1] :].lstrip("\n")
        pieces = [piece for piece in (before, block.rstrip(), after.rstrip()) if piece]
        return "\n\n".join(pieces) + "\n"
    if not original.strip():
        return block.rstrip() + "\n"
    return original.rstrip() + "\n\n" + block.rstrip() + "\n"


def _write(path: Path, content: str, changes: ChangeSet, *, dry_run: bool, allow_update: bool) -> None:
    ensure_safe_write_path(path)
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
    ensure_safe_write_path(path)
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    updated = upsert_block_text(original, block, start, end)
    _write(path, updated, changes, dry_run=dry_run, allow_update=True)


def upsert_block_text_preserving(original: str, block: str, start: str, end: str) -> str:
    span = managed_block_span(original, start, end)
    replacement = block.rstrip()
    if span is not None:
        return original[: span[0]] + replacement + original[span[1] :]
    if not original:
        return replacement + "\n"
    separator = "" if original.endswith("\n\n") else ("\n" if original.endswith("\n") else "\n\n")
    return original + separator + replacement + "\n"


def upsert_block_preserving(
    path: Path,
    block: str,
    changes: ChangeSet,
    *,
    start: str,
    end: str,
    dry_run: bool,
) -> None:
    ensure_safe_write_path(path)
    existed = path.exists()
    original_bytes = path.read_bytes() if existed else b""
    original = original_bytes.decode("utf-8")
    updated = upsert_block_text_preserving(original, block, start, end)
    updated_bytes = updated.encode("utf-8")
    if original_bytes == updated_bytes:
        changes.skipped.append(path)
        return
    if existed:
        changes.updated.append(path)
    else:
        changes.created.append(path)
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(updated_bytes)


def write_managed(path: Path, content: str, changes: ChangeSet, *, mode: str, dry_run: bool) -> None:
    ensure_safe_write_path(path)
    if mode == "init":
        _write(path, content, changes, dry_run=dry_run, allow_update=False)
        return
    if not path.exists():
        _write(path, content, changes, dry_run=dry_run, allow_update=False)
        return
    if not is_managed_file(path):
        changes.skipped.append(path)
        return
    _write(path, content, changes, dry_run=dry_run, allow_update=True)


def set_executable(paths: Iterable[Path], *, dry_run: bool) -> None:
    if dry_run or os.name == "nt":
        return
    for path in paths:
        ensure_safe_write_path(path)
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


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def command_evidence_path(root: Path, command: Sequence[str]) -> str | None:
    executable = command[0] if command else ""
    candidates: tuple[str, ...]
    if executable in {"npm", "pnpm", "yarn", "bun"}:
        candidates = (
            "package.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            "bun.lock",
            "bun.lockb",
            "package-lock.json",
        )
    elif executable in {"python", "python3", "uv", "poetry"}:
        candidates = ("pyproject.toml", "requirements.txt", "uv.lock", "poetry.lock", "tests")
    elif executable == "go":
        candidates = ("go.mod",)
    elif executable == "cargo":
        candidates = ("Cargo.toml", "Cargo.lock")
    elif executable in {"mvn", "./mvnw"}:
        candidates = ("mvnw", "pom.xml")
    elif executable in {"gradle", "./gradlew"}:
        candidates = ("gradlew", "build.gradle", "build.gradle.kts")
    else:
        candidates = ("Makefile", "justfile", "Taskfile.yml", "Taskfile.yaml")
    return next((relative for relative in candidates if (root / relative).exists()), None)


def repository_fact_values(root: Path) -> dict[str, str]:
    files, _ = audit_repository_entries(root)
    observed: set[tuple[str, str]] = set()
    for path in files:
        relative = audit_relative(path, root)
        category = audit_file_category(relative)
        if category in {"manifest", "lockfile", "ci", "runtime-config", "entry-point"}:
            observed.add((category, relative))
    for relative in AUDIT_SOURCE_DIRECTORIES:
        path = root / relative
        if path.is_dir() and not path.is_symlink():
            observed.add(("source-root", relative))
    for relative in AUDIT_TEST_DIRECTORIES:
        path = root / relative
        if path.is_dir() and not path.is_symlink():
            observed.add(("test-root", relative))

    observed_rows = [
        f"| {markdown_cell(category)} | `{markdown_cell(relative)}` exists | `{markdown_cell(relative)}` |"
        for category, relative in sorted(observed, key=lambda item: (item[0], item[1]))
    ]
    if not observed_rows:
        observed_rows.append("| none | No supported repository evidence was observed. | `.` |")

    candidates: set[tuple[str, str, str]] = set()
    language_runtime_evidence = (
        ("package.json", "TypeScript/JavaScript", "Node.js"),
        ("pyproject.toml", "Python", "Python"),
        ("requirements.txt", "Python", "Python"),
        ("go.mod", "Go", "Go"),
        ("Cargo.toml", "Rust", "Rust"),
        ("pom.xml", "Java", "JVM"),
        ("build.gradle", "Java/Kotlin", "JVM"),
        ("build.gradle.kts", "Kotlin/Java", "JVM"),
    )
    for evidence, language, runtime in language_runtime_evidence:
        if (root / evidence).is_file() and not (root / evidence).is_symlink():
            candidates.add(("language", language, evidence))
            candidates.add(("runtime", runtime, evidence))
    for group, commands in detect_commands(root).items():
        for command in commands:
            evidence = command_evidence_path(root, command)
            if evidence is None:
                continue
            candidates.add(
                (
                    f"{group} command",
                    json.dumps(command, ensure_ascii=False, separators=(",", ":")),
                    evidence,
                )
            )
    candidate_rows = [
        f"| {markdown_cell(kind)} | `{markdown_cell(candidate)}` | `{markdown_cell(evidence)}` |"
        for kind, candidate, evidence in sorted(candidates, key=lambda item: (item[0], item[1], item[2]))
    ]
    if not candidate_rows:
        candidate_rows.append("| none | No supported language, runtime, or command candidate was derived. | `.` |")

    architecture_paths = sorted(
        (relative, category)
        for category, relative in observed
        if category in {"source-root", "test-root"}
    )
    architecture_rows = [
        f"| `{markdown_cell(relative)}` | Observed {markdown_cell(category)}; responsibility remains open. | `{markdown_cell(relative)}` |"
        for relative, category in architecture_paths
    ]
    if not architecture_rows:
        architecture_rows.append("| `TODO` | No conventional source or test root was observed; establish paths from evidence. | `.` |")
    return {
        "OBSERVED_FACT_ROWS": "\n".join(observed_rows),
        "CANDIDATE_FACT_ROWS": "\n".join(candidate_rows),
        "ARCHITECTURE_PATH_ROWS": "\n".join(architecture_rows),
    }


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_array(values: Sequence[str]) -> str:
    return "[" + ", ".join(toml_string(value) for value in values) + "]"


def toml_command_array(commands: Sequence[Sequence[str]]) -> str:
    if not commands:
        return "[]"
    rows = ["  " + toml_array(list(command)) for command in commands]
    return "[\n" + ",\n".join(rows) + ",\n]"


def default_document_capabilities(kind: str) -> frozenset[str]:
    return PROJECT_KIND_DOCUMENT_DEFAULTS.get(kind.strip().lower(), frozenset())


def validate_config_version(config: dict[str, object]) -> None:
    if config.get("version") != 1:
        raise InitError("unsupported dev/harness.toml version; expected version = 1")


def configured_project_kind(config: dict[str, object]) -> str:
    project = config.get("project", {})
    if not isinstance(project, dict):
        raise InitError("dev/harness.toml [project] must be a table")
    raw_kind = project.get("kind", "other")
    if not isinstance(raw_kind, str):
        raise InitError("dev/harness.toml [project].kind must be a string")
    kind = raw_kind.strip().lower()
    if kind not in PROJECT_KIND_DOCUMENT_DEFAULTS:
        choices = ", ".join(PROJECT_CONFIG_KINDS)
        raise InitError(
            f"dev/harness.toml [project].kind must be one of: {choices}"
        )
    return kind


def normalize_document_capabilities(capabilities: Iterable[str]) -> frozenset[str]:
    normalized: set[str] = set()
    for value in capabilities:
        capability = value.strip().lower()
        if capability not in DOCUMENT_CAPABILITIES:
            choices = ", ".join(DOCUMENT_CAPABILITIES)
            raise InitError(f"unsupported document capability '{value}'; expected one of: {choices}")
        normalized.add(capability)
    return frozenset(normalized)


def configured_document_capabilities(config: dict[str, object]) -> frozenset[str] | None:
    raw = config.get("documents")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise InitError("dev/harness.toml [documents] must be a table")
    if raw.get("schema") != 2:
        raise InitError("dev/harness.toml [documents].schema must be 2")
    capabilities: set[str] = set()
    for capability, key in DOCUMENT_CAPABILITY_KEYS.items():
        value = raw.get(key, False)
        if not isinstance(value, bool):
            raise InitError(f"dev/harness.toml [documents].{key} must be true or false")
        if value:
            capabilities.add(capability)
    quality_score = raw.get("quality_score", False)
    if not isinstance(quality_score, bool):
        raise InitError("dev/harness.toml [documents].quality_score must be true or false")
    if quality_score:
        raise InitError("dev/harness.toml [documents].quality_score must remain false")
    return frozenset(capabilities)


def selected_document_capabilities(config: dict[str, object]) -> frozenset[str]:
    validate_config_version(config)
    kind = configured_project_kind(config)
    configured = configured_document_capabilities(config)
    return configured if configured is not None else default_document_capabilities(kind)


def effective_document_capabilities(
    *,
    kind: str,
    requested: Iterable[str] | None,
    existing_config: dict[str, object] | None = None,
) -> frozenset[str]:
    requested_capabilities = normalize_document_capabilities(requested or ())
    if existing_config is not None:
        validate_config_version(existing_config)
        existing_kind = configured_project_kind(existing_config)
        configured = configured_document_capabilities(existing_config)
        if configured is not None:
            return configured
        unenforced = requested_capabilities - default_document_capabilities(existing_kind)
        if unenforced:
            formatted = ", ".join(sorted(unenforced))
            raise InitError(
                "cannot persist explicit document capabilities in the existing "
                "project-owned dev/harness.toml because it has no [documents] table: "
                f"{formatted}; update that configuration explicitly before retrying"
            )
        return default_document_capabilities(existing_kind)
    return default_document_capabilities(kind) | requested_capabilities


def build_config(
    *,
    name: str,
    summary: str,
    kind: str,
    language: str,
    runtime: str,
    root: Path,
    capabilities: Iterable[str] | None = None,
    force_review: bool = False,
) -> str:
    commands = detect_commands(root)
    existing = has_existing_implementation(root)
    configuration = "review" if force_review or existing else "ready"
    enabled = default_document_capabilities(kind) | normalize_document_capabilities(capabilities or ())
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
        "[documents]",
        "schema = 2",
        f"visual_design = {'true' if 'visual-design' in enabled else 'false'}",
        f"frontend = {'true' if 'frontend' in enabled else 'false'}",
        f"product_sense = {'true' if 'product-sense' in enabled else 'false'}",
        f"reliability = {'true' if 'reliability' in enabled else 'false'}",
        "quality_score = false",
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
            "",
            "[gate]",
            'mode = "shadow"',
            'default_risk = "unknown"',
            "require_clean = true",
            f"protected_paths = {toml_array(GATE_PROTECTED_PATHS)}",
            f"contained_paths = {toml_array(GATE_CONTAINED_PATHS)}",
            f"wide_paths = {toml_array(GATE_WIDE_PATHS)}",
            f"irreversible_paths = {toml_array(GATE_IRREVERSIBLE_PATHS)}",
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
        **repository_fact_values(root),
    }


def project_documents(
    kind: str,
    capabilities: Iterable[str] | None = None,
) -> dict[str, str]:
    enabled = (
        default_document_capabilities(kind)
        if capabilities is None
        else normalize_document_capabilities(capabilities)
    )
    documents = {
        "ARCHITECTURE.md": "root/ARCHITECTURE.md.tmpl",
        "docs/README.md": "docs/README.md.tmpl",
        "docs/PRODUCT.md": "docs/PRODUCT.md.tmpl",
        "docs/QUALITY.md": "docs/QUALITY.md.tmpl",
        "docs/SECURITY.md": "docs/SECURITY.md.tmpl",
        "docs/PLANS.md": "docs/PLANS.md.tmpl",
        "docs/product-specs/index.md": "docs/product-specs/index.md.tmpl",
        "docs/product-specs/_template.md": "docs/product-specs/_template.md.tmpl",
        "docs/design-docs/index.md": "docs/design-docs/index.md.tmpl",
        "docs/design-docs/_template.md": "docs/design-docs/_template.md.tmpl",
        "docs/exec-plans/_template.md": "docs/exec-plans/_template.md.tmpl",
        "docs/exec-plans/tech-debt-tracker.md": "docs/exec-plans/tech-debt-tracker.md.tmpl",
        "docs/module-contracts/README.md": "docs/module-contracts/README.md.tmpl",
        "docs/module-contracts/_template.md": "docs/module-contracts/_template.md.tmpl",
        "docs/decisions/README.md": "docs/decisions/README.md.tmpl",
        "docs/decisions/_template.md": "docs/decisions/_template.md.tmpl",
        "docs/generated/README.md": "docs/generated/README.md.tmpl",
        "docs/generated/code-map.md": "docs/generated/code-map.md.tmpl",
        "docs/generated/repository-facts.md": "docs/generated/repository-facts.md.tmpl",
        "docs/generated/baseline-questions.md": "docs/generated/baseline-questions.md.tmpl",
        "docs/references/README.md": "docs/references/README.md.tmpl",
        "docs/references/project-definition-protocol.md": "docs/references/project-definition-protocol.md.tmpl",
        "docs/runbooks/index.md": "docs/runbooks/index.md.tmpl",
        "docs/runbooks/_template.md": "docs/runbooks/_template.md.tmpl",
    }
    for capability in ("visual-design", "frontend", "product-sense", "reliability"):
        if capability in enabled:
            destination, asset = OPTIONAL_DOCUMENT_ASSETS[capability]
            documents[destination] = asset
    return documents


def managed_files(with_ci: bool) -> dict[str, str]:
    files = {
        ".reporivet-version": "root/reporivet-version.tmpl",
        "dev/harness.py": "dev/harness.py",
        "dev/bootstrap": "dev/wrapper.sh.tmpl",
        "dev/context": "dev/wrapper.sh.tmpl",
        "dev/define": "dev/wrapper.sh.tmpl",
        "dev/audit": "dev/wrapper.sh.tmpl",
        "dev/code-map": "dev/wrapper.sh.tmpl",
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


def audit_managed_block_state(text: str, start: str, end: str) -> str:
    try:
        span = managed_block_span(text, start, end)
    except InitError:
        return "malformed"
    return "absent" if span is None else "present"


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
        command_inputs = COMMAND_INFERENCE_INPUTS
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


def audit_project_document_paths(
    root: Path,
) -> tuple[tuple[str, ...], list[AuditFinding]]:
    base_paths = tuple(sorted(project_documents("other")))
    config_path = root / "dev" / "harness.toml"
    if audit_symlink_component(root, config_path) is not None:
        return base_paths, []
    if config_path.exists() and not config_path.is_file():
        return base_paths, []
    if not config_path.is_file():
        return base_paths, []
    try:
        with config_path.open("rb") as handle:
            config = tomllib.load(handle)
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return base_paths, []
    try:
        capabilities = selected_document_capabilities(config)
        kind = configured_project_kind(config)
    except InitError as exc:
        return base_paths, [
            AuditFinding(
                category="document-configuration",
                status="conflict",
                path="dev/harness.toml",
                detail=str(exc),
            )
        ]
    return tuple(sorted(project_documents(kind, capabilities))), []


def audit_adoption_findings(root: Path) -> list[AuditFinding]:
    project_document_paths, findings = audit_project_document_paths(root)
    shared_targets = (
        ("AGENTS.md", AGENTS_START, AGENTS_END, "agent operating contract"),
        (".gitignore", GITIGNORE_START, GITIGNORE_END, "generated evidence exclusions"),
    )
    for relative, start, end, responsibility in shared_targets:
        path = root / relative
        if audit_symlink_component(root, path) is not None:
            findings.append(
                AuditFinding(
                    category="proposed-addition",
                    status="conflict",
                    path=relative,
                    detail=f"cannot add {responsibility} through a symbolic-link path",
                )
            )
        elif path.exists() and not path.is_file():
            findings.append(
                AuditFinding(
                    category="proposed-addition",
                    status="conflict",
                    path=relative,
                    detail=f"cannot add {responsibility} because the path is not a regular file",
                )
            )
        elif path.is_file():
            try:
                state = audit_managed_block_state(path.read_bytes().decode("utf-8"), start, end)
            except (OSError, UnicodeError):
                state = "malformed"
            status = "confirmed" if state == "present" else "inferred"
            detail = (
                f"{responsibility} is present"
                if state == "present"
                else f"adoption will append a bounded {responsibility} block"
            )
            if state == "malformed":
                status = "conflict"
                detail = f"existing {responsibility} markers are malformed"
            findings.append(AuditFinding("proposed-addition", status, relative, detail))
        else:
            findings.append(
                AuditFinding(
                    category="proposed-addition",
                    status="inferred",
                    path=relative,
                    detail=f"adoption will create the missing {responsibility}",
                )
            )

    for relative in project_document_paths:
        path = root / relative
        if audit_symlink_component(root, path) is not None:
            findings.append(
                AuditFinding(
                    category="proposed-addition",
                    status="conflict",
                    path=relative,
                    detail="cannot preserve or extend documentation through a symbolic-link path",
                )
            )
        elif path.exists() and not path.is_file():
            findings.append(
                AuditFinding(
                    category="proposed-addition",
                    status="conflict",
                    path=relative,
                    detail="documentation target is not a regular file",
                )
            )
        elif path.is_file() and relative in AUDIT_CATALOG_PATHS:
            try:
                state = audit_managed_block_state(
                    path.read_bytes().decode("utf-8"),
                    CATALOG_START,
                    CATALOG_END,
                )
            except (OSError, UnicodeError):
                state = "malformed"
            if state == "present":
                findings.append(
                    AuditFinding(
                        category="proposed-addition",
                        status="confirmed",
                        path=relative,
                        detail="Reporivet catalog responsibility is present",
                    )
                )
            elif state == "absent":
                findings.append(
                    AuditFinding(
                        category="proposed-addition",
                        status="inferred",
                        path=relative,
                        detail="adoption will append a bounded Reporivet catalog block and preserve existing text",
                    )
                )
            else:
                findings.append(
                    AuditFinding(
                        category="proposed-addition",
                        status="conflict",
                        path=relative,
                        detail="existing Reporivet catalog markers are malformed",
                    )
                )
        elif path.is_file():
            findings.append(
                AuditFinding(
                    category="authority",
                    status="skipped",
                    path=relative,
                    detail="existing project-owned documentation will be preserved byte-for-byte",
                )
            )
        else:
            findings.append(
                AuditFinding(
                    category="proposed-addition",
                    status="inferred",
                    path=relative,
                    detail="adoption will create this missing project-owned document",
                )
            )

    config_path = root / "dev" / "harness.toml"
    if config_path.is_file() and audit_symlink_component(root, config_path) is None:
        findings.append(
            AuditFinding(
                category="authority",
                status="skipped",
                path="dev/harness.toml",
                detail="existing project-owned command configuration will be preserved byte-for-byte",
            )
        )
    elif not config_path.exists() and not config_path.is_symlink():
        findings.append(
            AuditFinding(
                category="proposed-addition",
                status="inferred",
                path="dev/harness.toml",
                detail="adoption will create review-state command configuration",
            )
        )

    draft_path = root / DEFINITION_DRAFT_PATH
    if draft_path.is_file() and audit_symlink_component(root, draft_path) is None:
        findings.append(
            AuditFinding(
                category="authority",
                status="skipped",
                path=DEFINITION_DRAFT_PATH.as_posix(),
                detail="existing project-owned definition draft will be preserved byte-for-byte",
            )
        )
    elif not draft_path.exists() and not draft_path.is_symlink():
        findings.append(
            AuditFinding(
                category="proposed-addition",
                status="inferred",
                path=DEFINITION_DRAFT_PATH.as_posix(),
                detail="adoption will create a resumable project-definition draft",
            )
        )

    for relative in sorted(managed_files(False)):
        path = root / relative
        if audit_symlink_component(root, path) is not None:
            findings.append(
                AuditFinding(
                    category="proposed-addition",
                    status="conflict",
                    path=relative,
                    detail="canonical managed path is symbolic-linked",
                )
            )
        elif path.exists() and not path.is_file():
            findings.append(
                AuditFinding(
                    category="proposed-addition",
                    status="conflict",
                    path=relative,
                    detail="canonical managed path is not a regular file",
                )
            )
        elif path.is_file() and is_managed_file(path):
            findings.append(
                AuditFinding(
                    category="proposed-addition",
                    status="confirmed",
                    path=relative,
                    detail="Reporivet-managed runtime responsibility is present",
                )
            )
        elif path.is_file():
            findings.append(
                AuditFinding(
                    category="proposed-addition",
                    status="conflict",
                    path=relative,
                    detail="canonical command path is project-owned and unmarked",
                )
            )
        else:
            findings.append(
                AuditFinding(
                    category="proposed-addition",
                    status="inferred",
                    path=relative,
                    detail="adoption will install the missing Reporivet-managed runtime responsibility",
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
    findings.extend(audit_adoption_findings(root))
    unique = {
        (finding.category, finding.status, finding.path, finding.detail): finding
        for finding in findings
    }
    ordered = tuple(
        unique[key]
        for key in sorted(unique, key=lambda item: (item[0], item[2], item[1], item[3]))
    )
    return AuditReport(ordered)


def preflight_managed_conflicts(root: Path, *, with_ci: bool, mode: str) -> None:
    if mode not in {"init", "define", "adopt"}:
        return
    conflicts: list[str] = []
    for relative in managed_files(with_ci):
        path = root / relative
        if symlink_component(path) is not None:
            conflicts.append(f"{relative} (symlink path)")
            continue
        if not path.exists():
            continue
        if not is_managed_file(path):
            conflicts.append(relative)
    if conflicts:
        formatted = ", ".join(conflicts)
        raise InitError(
            "refusing to replace existing project-owned command paths: " + formatted +
            "; move or rename them before initialization"
        )


def harness_target_relative_paths(
    *,
    kind: str,
    capabilities: Iterable[str] | None = None,
    with_ci: bool,
    include_definition_draft: bool,
) -> tuple[str, ...]:
    relative_paths = {
        "AGENTS.md",
        ".gitignore",
        "dev/harness.toml",
        "docs/exec-plans/active",
        "docs/exec-plans/completed",
        "docs/product-specs",
        "docs/design-docs",
        "docs/decisions",
        "docs/module-contracts",
        "docs/generated",
        "docs/references",
        ".harness/runs",
        "dev",
        "docs/exec-plans/active/.gitkeep",
        "docs/exec-plans/completed/.gitkeep",
        ".harness/runs/.gitkeep",
        "docs/exec-plans/active/PLAN-0000-establish-repository-baseline.md",
        *project_documents(kind, capabilities),
        *managed_files(with_ci),
    }
    if include_definition_draft:
        relative_paths.add(DEFINITION_DRAFT_PATH.as_posix())
    expanded = set(relative_paths)
    for relative in tuple(relative_paths):
        for parent in Path(relative).parents:
            if parent != Path("."):
                expanded.add(parent.as_posix())
    return tuple(sorted(expanded))


def preflight_safe_write_paths(
    root: Path,
    *,
    kind: str,
    capabilities: Iterable[str] | None = None,
    with_ci: bool,
    include_definition_draft: bool,
) -> None:
    for relative in harness_target_relative_paths(
        kind=kind,
        capabilities=capabilities,
        with_ci=with_ci,
        include_definition_draft=include_definition_draft,
    ):
        ensure_safe_write_path(root / relative)


def preflight_optional_document_targets(
    root: Path,
    capabilities: Iterable[str],
) -> None:
    for capability in sorted(normalize_document_capabilities(capabilities)):
        relative, _ = OPTIONAL_DOCUMENT_ASSETS[capability]
        path = root / relative
        ensure_safe_write_path(path)
        if not path.exists():
            continue
        if not path.is_file():
            raise InitError(f"optional document target is not a regular file: {relative}")
        try:
            path.read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise InitError(f"cannot read optional document target as UTF-8: {relative}") from exc


def ensure_directories(root: Path, *, dry_run: bool) -> None:
    if dry_run:
        return
    for relative in (
        "docs/exec-plans/active",
        "docs/exec-plans/completed",
        "docs/product-specs",
        "docs/design-docs",
        "docs/decisions",
        "docs/module-contracts",
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


def create_definition_draft(root: Path, values: dict[str, str], changes: ChangeSet, *, dry_run: bool) -> None:
    content = read_asset(
        "docs/product-specs/project-definition.draft.md.tmpl",
        {"DATE": values["DATE"]},
    )
    write_if_missing(root / DEFINITION_DRAFT_PATH, content, changes, dry_run=dry_run)


def run_generated(root: Path, command: str, *args: str, quiet: bool = False) -> int:
    harness = root / "dev" / "harness.py"
    if not harness.exists():
        raise InitError("generated dev/harness.py is missing")
    completed = subprocess.run(
        [sys.executable, str(harness), command, *args],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None,
    )
    return completed.returncode


def preflight_adoption_blocks(
    root: Path,
    values: dict[str, str],
    capabilities: Iterable[str] | None = None,
) -> None:
    targets = [
        (
            root / "AGENTS.md",
            extract_block(read_asset("root/AGENTS.md.tmpl", values), AGENTS_START, AGENTS_END),
            AGENTS_START,
            AGENTS_END,
        ),
        (
            root / ".gitignore",
            read_asset("root/gitignore.block.tmpl", values).strip(),
            GITIGNORE_START,
            GITIGNORE_END,
        ),
    ]
    for relative, asset in project_documents(
        values["PROJECT_KIND"], capabilities
    ).items():
        if relative not in AUDIT_CATALOG_PATHS:
            continue
        targets.append(
            (
                root / relative,
                extract_block(read_asset(asset, values), CATALOG_START, CATALOG_END),
                CATALOG_START,
                CATALOG_END,
            )
        )
    for path, block, start, end in targets:
        if not path.exists():
            continue
        if not path.is_file():
            raise InitError(f"adoption target is not a regular file: {path.relative_to(root)}")
        try:
            original = path.read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise InitError(f"cannot read adoption target: {path.relative_to(root)}") from exc
        upsert_block_text_preserving(original, block, start, end)


def _copy_repository_for_plan(source: Path, destination: Path) -> None:
    destination.mkdir(mode=stat.S_IMODE(source.lstat().st_mode), parents=True)

    def copy_directory(current_source: Path, current_destination: Path) -> None:
        try:
            entries = sorted(os.scandir(current_source), key=lambda entry: entry.name)
        except OSError as exc:
            raise InitError(f"cannot stage repository path {current_source}: {exc}") from exc
        for directory_entry in entries:
            source_path = Path(directory_entry.path)
            destination_path = current_destination / directory_entry.name
            relative = source_path.relative_to(source).as_posix()
            if relative in {".git", ".harness"}:
                continue
            try:
                metadata = source_path.lstat()
            except OSError as exc:
                raise InitError(f"cannot inspect repository path while planning: {relative}: {exc}") from exc
            mode = stat.S_IMODE(metadata.st_mode)
            if stat.S_ISLNK(metadata.st_mode):
                os.symlink(os.readlink(source_path), destination_path)
            elif stat.S_ISDIR(metadata.st_mode):
                destination_path.mkdir(mode=mode)
                if directory_entry.name not in AUDIT_IGNORED_DIRECTORIES:
                    copy_directory(source_path, destination_path)
                os.chmod(destination_path, mode)
            elif stat.S_ISREG(metadata.st_mode):
                image = capture_mutation_image(source_path, root=source)
                destination_path.write_bytes(image.content or b"")
                os.chmod(destination_path, mode)
            elif stat.S_ISFIFO(metadata.st_mode) and hasattr(os, "mkfifo"):
                os.mkfifo(destination_path, mode)
            else:
                raise InitError(
                    f"cannot safely render a mutation plan with non-regular repository entry: {relative}"
                )

    copy_directory(source, destination)
    os.chmod(destination, stat.S_IMODE(source.lstat().st_mode))


def _remap_changes(changes: ChangeSet, source_root: Path, target_root: Path) -> ChangeSet:
    remapped = ChangeSet()
    for label in ("created", "updated", "skipped"):
        values = [
            target_root / path.relative_to(source_root)
            for path in getattr(changes, label)
        ]
        setattr(remapped, label, values)
    return remapped


def _mutation_plan_from_stage(root: Path, staged_root: Path) -> MutationPlan:
    entries: list[MutationEntry] = []
    candidates = [staged_root]
    candidates.extend(sorted(staged_root.rglob("*"), key=lambda path: path.relative_to(staged_root).as_posix()))
    for staged_path in candidates:
        relative = mutation_relative(staged_path, staged_root)
        try:
            metadata = staged_path.lstat()
        except OSError as exc:
            raise InitError(f"cannot inspect staged mutation path {relative}: {exc}") from exc
        if stat.S_ISLNK(metadata.st_mode) or not (
            stat.S_ISDIR(metadata.st_mode) or stat.S_ISREG(metadata.st_mode)
        ):
            continue
        target_path = root if relative == "." else root / relative
        preimage = capture_mutation_image(target_path, root=root)
        postimage = capture_mutation_image(staged_path, root=staged_root)
        if (
            preimage.kind == postimage.kind
            and preimage.mode == postimage.mode
            and preimage.sha256 == postimage.sha256
        ):
            continue
        if postimage.kind == "directory":
            if preimage.kind != "missing":
                raise InitError(f"mutation target has an unexpected filesystem type: {relative}")
            action = "create-directory"
        elif postimage.kind == "file":
            if preimage.kind not in {"missing", "file"}:
                raise InitError(f"mutation target has an unexpected filesystem type: {relative}")
            action = "create-file" if preimage.kind == "missing" else "update-file"
        else:
            raise InitError(f"unsupported staged mutation type: {relative}")
        entries.append(
            MutationEntry(
                root=root,
                relative=relative,
                action=action,
                preimage=preimage,
                postimage=postimage,
            )
        )
    entries.sort(key=lambda entry: entry.relative)
    return MutationPlan(root=root, entries=tuple(entries))


def _read_descriptor_image(descriptor: int) -> MutationImage:
    metadata = os.fstat(descriptor)
    if not stat.S_ISREG(metadata.st_mode):
        return MutationImage("nonregular", stat.S_IMODE(metadata.st_mode), None)
    os.lseek(descriptor, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while True:
        chunk = os.read(descriptor, 1024 * 1024)
        if not chunk:
            break
        chunks.append(chunk)
    content = b"".join(chunks)
    return MutationImage(
        "file",
        stat.S_IMODE(metadata.st_mode),
        hashlib.sha256(content).hexdigest(),
        content,
    )


def _write_all(descriptor: int, content: bytes) -> None:
    view = memoryview(content)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("short write while applying mutation")
        view = view[written:]


def _chmod_open_file(descriptor: int, path: Path, mode: int) -> None:
    if hasattr(os, "fchmod"):
        os.fchmod(descriptor, mode)
    else:
        os.chmod(path, mode)


def _write_file_image(entry: MutationEntry) -> None:
    path = entry.path
    content = entry.postimage.content
    mode = entry.postimage.mode
    if content is None or mode is None:
        raise InitError(f"mutation file postimage is incomplete: {entry.relative}")
    flags = os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if entry.preimage.kind == "missing":
        flags |= os.O_CREAT | os.O_EXCL
        descriptor = os.open(path, flags, mode)
    else:
        descriptor = os.open(path, flags)
    try:
        if entry.preimage.kind == "file":
            current = _read_descriptor_image(descriptor)
            if (
                current.kind != entry.preimage.kind
                or current.mode != entry.preimage.mode
                or current.sha256 != entry.preimage.sha256
            ):
                raise InitError(f"preimage changed before write: {entry.relative}")
        os.ftruncate(descriptor, 0)
        os.lseek(descriptor, 0, os.SEEK_SET)
        _write_all(descriptor, content)
        _chmod_open_file(descriptor, path, mode)
    finally:
        os.close(descriptor)


def _apply_mutation_entry(entry: MutationEntry) -> None:
    path = entry.path
    ensure_safe_write_path(path)
    if not mutation_image_matches(path, entry.preimage, root=entry.root):
        raise InitError(f"preimage changed before write: {entry.relative}")
    if entry.action == "create-directory":
        if entry.postimage.mode is None:
            raise InitError(f"mutation directory postimage is incomplete: {entry.relative}")
        path.mkdir(mode=entry.postimage.mode)
        os.chmod(path, entry.postimage.mode)
        return
    if entry.action in {"create-file", "update-file"}:
        if not path.parent.is_dir():
            raise InitError(f"mutation parent directory is unavailable: {entry.relative}")
        _write_file_image(entry)
        return
    raise InitError(f"unsupported mutation action for {entry.relative}: {entry.action}")


def _restore_file_preimage(entry: MutationEntry) -> None:
    content = entry.preimage.content
    mode = entry.preimage.mode
    if content is None or mode is None:
        raise InitError(f"file preimage is incomplete: {entry.relative}")
    flags = os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(entry.path, flags)
    try:
        current = _read_descriptor_image(descriptor)
        if (
            current.kind != entry.postimage.kind
            or current.mode != entry.postimage.mode
            or current.sha256 != entry.postimage.sha256
        ):
            raise InitError(f"postimage changed before rollback: {entry.relative}")
        os.ftruncate(descriptor, 0)
        os.lseek(descriptor, 0, os.SEEK_SET)
        _write_all(descriptor, content)
        _chmod_open_file(descriptor, entry.path, mode)
    finally:
        os.close(descriptor)


def _rollback_mutation_entries(entries: Sequence[MutationEntry]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    preserved: list[str] = []
    for entry in reversed(entries):
        path = entry.path
        if mutation_image_matches(path, entry.preimage, root=entry.root):
            continue
        if not mutation_image_matches(path, entry.postimage, root=entry.root):
            preserved.append(entry.relative)
            continue
        try:
            if entry.preimage.kind == "missing":
                if entry.postimage.kind == "file":
                    path.unlink()
                elif entry.postimage.kind == "directory":
                    path.rmdir()
            elif entry.preimage.kind == "file":
                _restore_file_preimage(entry)
            else:
                raise InitError(f"unsupported rollback preimage: {entry.relative}")
        except (OSError, InitError) as exc:
            preserved.append(entry.relative)
            errors.append(f"{entry.relative}: {exc}")
    return sorted(set(preserved)), errors


def _apply_mutation_plan(plan: MutationPlan) -> None:
    for entry in plan.entries:
        if not mutation_image_matches(entry.path, entry.preimage, root=plan.root):
            raise InitError(f"preimage changed before mutation: {entry.relative}")
    touched: list[MutationEntry] = []
    try:
        for entry in plan.entries:
            touched.append(entry)
            _apply_mutation_entry(entry)
    except BaseException as exc:
        preserved, rollback_errors = _rollback_mutation_entries(touched)
        if preserved or rollback_errors:
            detail = f"mutation failed ({exc}); rollback incomplete"
            if preserved:
                detail += "; preserved path(s): " + ", ".join(preserved)
            if rollback_errors:
                detail += "; rollback error(s): " + "; ".join(rollback_errors)
            raise InitError(detail) from exc
        raise InitError(f"mutation failed and was rolled back: {exc}") from exc


def _apply_harness_files(
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
    capabilities: Sequence[str] | None = None,
    include_definition_draft: bool = False,
    quiet_generated: bool = False,
) -> ChangeSet:
    root = validate_root(root, create=mode in {"init", "define"}, dry_run=dry_run)
    kind_value = kind.strip() or "other"
    config_path = root / "dev" / "harness.toml"
    existing_config: dict[str, object] | None = None
    if config_path.is_file() and symlink_component(config_path) is None:
        existing_config = read_existing_config(root)
        kind_value = configured_project_kind(existing_config)
    enabled_capabilities = effective_document_capabilities(
        kind=kind_value,
        requested=capabilities,
        existing_config=existing_config,
    )
    values = config_values(
        root=root,
        name=name.strip() or root.name,
        summary=summary.strip() or "TODO: define the project purpose during baseline establishment.",
        kind=kind_value,
        primary_language=primary_language,
        runtime=runtime,
    )
    preflight_managed_conflicts(root, with_ci=with_ci, mode=mode)
    preflight_safe_write_paths(
        root,
        kind=values["PROJECT_KIND"],
        capabilities=enabled_capabilities,
        with_ci=with_ci,
        include_definition_draft=include_definition_draft,
    )
    preflight_optional_document_targets(root, enabled_capabilities)
    if mode == "adopt":
        preflight_adoption_blocks(root, values, enabled_capabilities)
    changes = ChangeSet()
    ensure_directories(root, dry_run=dry_run)

    agents_template = read_asset("root/AGENTS.md.tmpl", values)
    agents_block = extract_block(agents_template, AGENTS_START, AGENTS_END)
    agents_upsert = upsert_block_preserving if mode == "adopt" else upsert_block
    agents_upsert(
        root / "AGENTS.md",
        agents_block,
        changes,
        start=AGENTS_START,
        end=AGENTS_END,
        dry_run=dry_run,
    )

    gitignore_block = read_asset("root/gitignore.block.tmpl", values).strip()
    gitignore_upsert = upsert_block_preserving if mode == "adopt" else upsert_block
    gitignore_upsert(
        root / ".gitignore",
        gitignore_block,
        changes,
        start=GITIGNORE_START,
        end=GITIGNORE_END,
        dry_run=dry_run,
    )

    for destination, asset in project_documents(
        values["PROJECT_KIND"], enabled_capabilities
    ).items():
        # Keep runtime plan tokens intact. They are resolved by the copied
        # repository-local harness when a future plan is created, not by the
        # initializer that installs the template.
        asset_values = {} if destination == "docs/exec-plans/_template.md" else values
        content = read_asset(asset, asset_values)
        if mode == "adopt" and destination in AUDIT_CATALOG_PATHS:
            upsert_block_preserving(
                root / destination,
                extract_block(content, CATALOG_START, CATALOG_END),
                changes,
                start=CATALOG_START,
                end=CATALOG_END,
                dry_run=dry_run,
            )
        else:
            write_if_missing(root / destination, content, changes, dry_run=dry_run)

    if include_definition_draft:
        create_definition_draft(root, values, changes, dry_run=dry_run)

    if not config_path.exists():
        config = build_config(
            name=values["PROJECT_NAME"],
            summary=values["PROJECT_SUMMARY"],
            kind=values["PROJECT_KIND"],
            language=values["PRIMARY_LANGUAGE"],
            runtime=values["RUNTIME"],
            root=root,
            capabilities=enabled_capabilities,
            force_review=mode == "adopt",
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
    if dry_run or mode == "adopt":
        return changes

    if run_generated(root, "code-map", quiet=quiet_generated) != 0:
        raise InitError("code-map failed after initialization")
    if run_generated(root, "docs-index", quiet=quiet_generated) != 0:
        raise InitError("docs-index failed after initialization")
    if skip_check:
        return changes
    if run_generated(root, "docs-check", quiet=quiet_generated) != 0:
        raise InitError("docs-check failed after initialization")
    return changes


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
    capabilities: Sequence[str] | None = None,
    include_definition_draft: bool = False,
) -> ChangeSet:
    root = validate_root(
        root,
        create=mode in {"init", "define"},
        dry_run=True,
    )
    preflight_command_inference_inputs(root) if root.exists() else None
    kind_value = kind.strip() or "other"
    config_path = root / "dev" / "harness.toml"
    existing_config: dict[str, object] | None = None
    if config_path.is_file() and symlink_component(config_path) is None:
        existing_config = read_existing_config(root)
        kind_value = configured_project_kind(existing_config)
    enabled_capabilities = effective_document_capabilities(
        kind=kind_value,
        requested=capabilities,
        existing_config=existing_config,
    )
    preflight_mutation_target_types(
        root,
        kind=kind_value,
        capabilities=enabled_capabilities,
        with_ci=with_ci,
        include_definition_draft=include_definition_draft,
    )

    with tempfile.TemporaryDirectory(prefix="reporivet-plan-") as temporary:
        staged_parent = Path(temporary).resolve()
        staged_root = staged_parent / (root.name or "project")
        if root.exists():
            _copy_repository_for_plan(root, staged_root)
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                staged_changes = _apply_harness_files(
                    root=staged_root,
                    mode=mode,
                    name=name,
                    summary=summary,
                    kind=kind_value,
                    primary_language=primary_language,
                    runtime=runtime,
                    with_ci=with_ci,
                    baseline=baseline,
                    dry_run=False,
                    skip_check=skip_check,
                    capabilities=tuple(sorted(enabled_capabilities)),
                    include_definition_draft=include_definition_draft,
                    quiet_generated=True,
                )
        except BaseException as exc:
            if isinstance(exc, InitError):
                raise
            raise InitError(f"cannot render mutation plan: {exc}") from exc
        changes = _remap_changes(staged_changes, staged_root, root)
        plan = _mutation_plan_from_stage(root, staged_root)

    changes.print(root, dry_run=dry_run)
    plan.print()
    if dry_run:
        return changes
    _apply_mutation_plan(plan)
    return changes


def define_project(*, root: Path, dry_run: bool) -> ChangeSet:
    return apply_harness(
        root=root,
        mode="define",
        name="",
        summary="",
        kind="other",
        primary_language="",
        runtime="",
        with_ci=False,
        baseline=True,
        dry_run=dry_run,
        skip_check=False,
        include_definition_draft=True,
    )


def adopt_project(*, root: Path, dry_run: bool) -> ChangeSet:
    root = validate_audit_root(root)
    report = audit_project(root=root)
    print(report.render(), end="")
    if report.conflicts:
        paths = ", ".join(sorted({finding.path for finding in report.conflicts}))
        raise InitError(f"adoption audit found conflicts; no files were written: {paths}")

    config_path = root / "dev" / "harness.toml"
    existing_config = (
        read_existing_config(root)
        if config_path.is_file() and symlink_component(config_path) is None
        else None
    )
    project_kind = (
        configured_project_kind(existing_config)
        if existing_config is not None
        else "other"
    )
    capabilities = effective_document_capabilities(
        kind=project_kind,
        requested=None,
        existing_config=existing_config,
    )
    preflight_optional_document_targets(root, capabilities)
    try:
        return apply_harness(
            root=root,
            mode="adopt",
            name="",
            summary="",
            kind=project_kind,
            primary_language="",
            runtime="",
            with_ci=False,
            baseline=True,
            dry_run=dry_run,
            skip_check=False,
            capabilities=tuple(sorted(capabilities)),
            include_definition_draft=True,
        )
    except Exception as exc:
        detail = str(exc)
        if "rollback incomplete" in detail:
            raise InitError(f"adoption failed; {detail}") from exc
        raise InitError(f"adoption failed and was rolled back: {detail}") from exc


def read_existing_config(root: Path) -> dict[str, object]:
    config_path = root / "dev" / "harness.toml"
    if not config_path.exists():
        return {}
    try:
        with config_path.open("rb") as handle:
            config = tomllib.load(handle)
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise InitError(f"cannot read dev/harness.toml: {exc}") from exc
    validate_config_version(config)
    return config


def gate_config_advisory(config: dict[str, object]) -> str:
    if "gate" not in config:
        return "dev/harness.toml has no [gate] table; conservative shadow defaults apply in memory"
    gate = config["gate"]
    if not isinstance(gate, dict):
        return "dev/harness.toml [gate] value is not a table; verification will be inconclusive"
    mode = gate.get("mode", "shadow")
    default_risk = gate.get("default_risk", "unknown")
    require_clean = gate.get("require_clean", True)
    if mode not in {"shadow", "enforce"}:
        return "dev/harness.toml [gate].mode must be shadow or enforce"
    if default_risk not in {"contained", "wide", "irreversible", "unknown"}:
        return "dev/harness.toml [gate].default_risk is invalid"
    if not isinstance(require_clean, bool):
        return "dev/harness.toml [gate].require_clean must be true or false"
    for field in ("protected_paths", "contained_paths", "wide_paths", "irreversible_paths"):
        value = gate.get(field, [])
        if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
            return f"dev/harness.toml [gate].{field} must be an array of non-empty strings"
        for pattern in value:
            pure = Path(pattern)
            if pure.is_absolute() or "\\" in pattern or ".." in pure.parts:
                return f"dev/harness.toml [gate].{field} contains an unsafe pattern"
    return ""


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
        "docs/QUALITY.md",
        "docs/SECURITY.md",
        "docs/PLANS.md",
        "docs/exec-plans/_template.md",
        "docs/exec-plans/tech-debt-tracker.md",
        "docs/module-contracts/README.md",
        "docs/module-contracts/_template.md",
        "docs/generated/code-map.md",
        "docs/references/project-definition-protocol.md",
        "dev/harness.py",
        "dev/harness.toml",
        "dev/bootstrap",
        "dev/context",
        "dev/define",
        "dev/audit",
        "dev/code-map",
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
    provenance_marker = "Provenance: initialized by Reporivet"
    if any(
        (root / relative).is_file()
        and provenance_marker in (root / relative).read_text(encoding="utf-8", errors="ignore")
        for relative in ("ARCHITECTURE.md", "docs/PRODUCT.md")
    ):
        required += (
            "docs/generated/repository-facts.md",
            "docs/generated/baseline-questions.md",
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
    if symlink_component(harness) is not None:
        errors.append("unsafe symlink path: dev/harness.py")
    elif harness.exists():
        head = "\n".join(harness.read_text(encoding="utf-8", errors="ignore").splitlines()[:3])
        if not is_managed_file(harness):
            warnings.append("dev/harness.py is not marked as managed; upgrades will preserve it")
        if f"version={__version__}" not in head:
            warnings.append(f"dev/harness.py is not at initializer version {__version__}; run reporivet upgrade --dry-run")
    if not (root / ".git").exists():
        warnings.append("no .git directory detected; plans and decisions are not yet versioned")

    config_path = root / "dev" / "harness.toml"
    if config_path.exists():
        try:
            config = read_existing_config(root)
            enabled = selected_document_capabilities(config)
        except InitError as exc:
            errors.append(str(exc))
        else:
            advisory = gate_config_advisory(config)
            if advisory:
                warnings.append(advisory)
            for capability, (relative, _) in OPTIONAL_DOCUMENT_ASSETS.items():
                if capability in enabled and not (root / relative).exists():
                    errors.append(f"missing {relative}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 2
    if harness.exists() and symlink_component(harness) is None:
        for command, args in (
            ("code-map", ("--check",)),
            ("docs-index", ("--check",)),
            ("docs-check", ()),
            ("plan-check", ()),
        ):
            if run_generated(root, command, *args) != 0:
                return 2
    return 0

