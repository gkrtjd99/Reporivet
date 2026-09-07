#!/usr/bin/env python3
# reporivet:managed version=0.2.0
"""Repository-local entrypoints for agent-readable context, plans, checks, and verification."""

from __future__ import annotations

import argparse
import contextlib
import fnmatch
import hashlib
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Sequence


def runtime_root() -> tuple[Path, bool]:
    script = Path(os.path.abspath(__file__))
    if any(candidate.is_symlink() for candidate in (script, *script.parents)):
        return script.parent.parent, True
    return script.parent.parent.resolve(strict=False), False


ROOT, RUNTIME_ROOT_IS_SYMLINKED = runtime_root()
CONFIG_PATH = ROOT / "dev" / "harness.toml"
CATALOG_START = "<!-- reporivet:catalog:start -->"
CATALOG_END = "<!-- reporivet:catalog:end -->"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
TITLE_LINE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
TASK_HEADING = re.compile(r"^###\s+(T[0-9A-Za-z_-]+)\s*(?:—|-)\s*(.+)$", re.MULTILINE)
PLAN_ID_PATTERN = re.compile(r"PLAN-(?:\d{4}-)?(\d{4})")
PLACEHOLDER = "TODO"
DEFINITION_DRAFT = Path("docs/product-specs/project-definition.draft.md")
DEFINITION_SPEC = Path("docs/product-specs/SPEC-PROJECT-001-product-definition.md")
MODULE_CONTRACTS_DIR = Path("docs/module-contracts")
CODE_MAP_PATH = Path("docs/generated/code-map.md")
MODULE_CONTRACT_ID = re.compile(r"MOD-[A-Z0-9]+(?:-[A-Z0-9]+)*")
CONFIRMED_PLANNED_PATH = re.compile(
    r"^\s*-\s+\[confirmed\]\s+Planned path:\s+(.+?)\s*$",
    re.IGNORECASE,
)
VERIFICATION_CHECKS = (
    "security",
    "docs-index",
    "documentation",
    "plan",
    "architecture",
    "project",
    "smoke",
)
CHECK_STATUSES = frozenset({"pass", "fail", "error", "skipped", "unknown"})
GATE_MODES = frozenset({"shadow", "enforce"})
GATE_RISKS = frozenset({"contained", "wide", "irreversible", "unknown"})
GATE_VERDICTS = frozenset({"PASS", "REVIEW", "BLOCK", "INCONCLUSIVE"})
DEFAULT_GATE_POLICY: dict[str, object] = {
    "mode": "shadow",
    "default_risk": "unknown",
    "require_clean": True,
    "protected_paths": (
        ".github/workflows/**",
        "AGENTS.md",
        "dev/harness.py",
        "dev/harness.toml",
        "docs/SECURITY.md",
    ),
    "contained_paths": (
        "docs/**",
        "src/**",
        "tests/**",
    ),
    "wide_paths": (
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
    ),
    "irreversible_paths": (
        "db/migrations/**",
        "infrastructure/**",
        "migrations/**",
        "schema/migrations/**",
        "terraform/**",
    ),
}
DEFINITION_SECTIONS = (
    "Project Identity",
    "Problem and Current Alternative",
    "Target Users",
    "Value Proposition and Solution",
    "MVP Capabilities and Priority",
    "User Journeys",
    "Scope Boundaries",
    "Success Signals",
    "Non-Functional Requirements",
    "Stack and Architecture Constraints",
    "Agent Operating Model",
    "Repository Boundaries and Context",
    "Verification and Handoff",
    "First Milestone, Dependencies, and Risks",
)
DEFINITION_EVIDENCE_HEADINGS = ("Confirmed", "Proposed", "Open", "Sources")
AGENTS_START = "<!-- reporivet:start -->"
AGENTS_END = "<!-- reporivet:end -->"
GITIGNORE_START = "# reporivet:start"
GITIGNORE_END = "# reporivet:end"
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
AUDIT_PROJECT_DOCUMENT_PATHS = (
    "ARCHITECTURE.md",
    "docs/README.md",
    "docs/PRODUCT.md",
    "docs/QUALITY.md",
    "docs/SECURITY.md",
    "docs/PLANS.md",
    "docs/product-specs/index.md",
    "docs/product-specs/_template.md",
    "docs/design-docs/index.md",
    "docs/design-docs/_template.md",
    "docs/exec-plans/_template.md",
    "docs/exec-plans/tech-debt-tracker.md",
    "docs/module-contracts/README.md",
    "docs/module-contracts/_template.md",
    "docs/generated/code-map.md",
    "docs/generated/repository-facts.md",
    "docs/generated/baseline-questions.md",
    "docs/decisions/README.md",
    "docs/decisions/_template.md",
    "docs/generated/README.md",
    "docs/references/README.md",
    "docs/references/project-definition-protocol.md",
    "docs/runbooks/index.md",
    "docs/runbooks/_template.md",
)
AUDIT_MANAGED_RUNTIME_PATHS = (
    ".reporivet-version",
    "dev/harness.py",
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
DEFINITION_ITEM_STATUSES = {
    "Confirmed": {"confirmed"},
    "Proposed": {"proposed"},
    "Open": {"blocking", "non-blocking"},
    "Sources": {"source"},
}
DEFINITION_ID_PATTERNS = {
    "journey": re.compile(r"JRN-[0-9]+"),
    "p0": re.compile(r"REQ-P0-[0-9]+"),
    "acceptance": re.compile(r"AC-[0-9]+"),
}
DEFINITION_NUMBERED_HEADING = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$", re.MULTILINE)
DEFINITION_EVIDENCE_HEADING = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
DEFINITION_TEMPLATE_TOKEN = re.compile(r"\{\{[^{}\n]+\}\}|\$\{[^{}\n]+\}|<<[^<>\n]+>>")
DEFINITION_ID_CANDIDATE = re.compile(
    r"(?<![A-Za-z0-9])(?:JRN(?:[-_][A-Za-z0-9_-]+|[0-9]+)|REQ(?:[-_]P0(?:[-_][A-Za-z0-9_-]+)?|P0[-_]?[A-Za-z0-9_-]*)|AC(?:[-_][A-Za-z0-9_-]+|[0-9]+))(?![A-Za-z0-9])"
)
DEFINITION_DECLARATION_ID_CANDIDATE = re.compile(
    r"(?:"
    r"(?:JRN|AC)(?:$|[-_][A-Za-z0-9_-]+|[0-9][A-Za-z0-9_-]*|[/:.][A-Za-z0-9_-]+|[ \t]+[0-9][A-Za-z0-9_-]*)"
    r"|REQ(?:$|[-_][A-Za-z0-9_-]+|[0-9][A-Za-z0-9_-]*|[/:.]P[A-Za-z0-9]*[/:.][A-Za-z0-9_-]+|[ \t]+P[A-Za-z0-9]*[ \t]+[A-Za-z0-9_-]+)"
    r")",
    re.IGNORECASE,
)
REQUIRED_DOCS = (
    Path("AGENTS.md"),
    Path("ARCHITECTURE.md"),
    Path("docs/README.md"),
    Path("docs/PRODUCT.md"),
    Path("docs/QUALITY.md"),
    Path("docs/SECURITY.md"),
    Path("docs/PLANS.md"),
    Path("docs/product-specs/index.md"),
    Path("docs/product-specs/_template.md"),
    Path("docs/design-docs/index.md"),
    Path("docs/design-docs/_template.md"),
    Path("docs/exec-plans/_template.md"),
    Path("docs/exec-plans/tech-debt-tracker.md"),
    Path("docs/module-contracts/README.md"),
    Path("docs/module-contracts/_template.md"),
    CODE_MAP_PATH,
    Path("docs/decisions/README.md"),
    Path("docs/decisions/_template.md"),
    Path("docs/runbooks/index.md"),
    Path("docs/runbooks/_template.md"),
    Path("docs/generated/README.md"),
    Path("docs/references/README.md"),
    Path("docs/references/project-definition-protocol.md"),
    Path("dev/harness.toml"),
)
CATALOG_AREAS = {
    "product-specs": "product-spec",
    "design-docs": "design-doc",
    "decisions": "decision",
    "runbooks": "runbook",
}
VALID_STATUSES = {
    "product-spec": {"draft", "active", "deprecated", "superseded"},
    "design-doc": {"draft", "active", "deprecated", "superseded"},
    "decision": {"proposed", "accepted", "rejected", "superseded"},
    "runbook": {"draft", "active", "deprecated"},
}
CONTEXT_CORE_DOCUMENTS = (
    Path("ARCHITECTURE.md"),
    Path("docs/PRODUCT.md"),
    Path("docs/QUALITY.md"),
    Path("docs/SECURITY.md"),
    Path("docs/DESIGN.md"),
    Path("docs/FRONTEND.md"),
    Path("docs/PRODUCT_SENSE.md"),
    Path("docs/RELIABILITY.md"),
)
DEFAULT_AUTHORITY_STATUSES = frozenset({"active", "accepted"})
DRAFT_AUTHORITY_STATUSES = frozenset({"draft", "proposed"})
HISTORICAL_AUTHORITY_STATUSES = frozenset({"deprecated", "superseded", "rejected"})
ACTIVE_PLAN_STATES = {"proposed", "approved", "in-progress", "verifying", "blocked"}
COMPLETED_PLAN_STATES = {"complete", "cancelled", "superseded"}
PLAN_REQUIRED_HEADINGS = (
    "Purpose / Big Picture",
    "Progress",
    "Context and Orientation",
    "Scope",
    "Non-goals",
    "Acceptance Criteria",
    "Milestones",
    "Task Packets",
    "Architecture Impact",
    "Documentation Impact",
    "Interfaces and Dependencies",
    "Migration, Rollout, and Recovery",
    "Surprises and Discoveries",
    "Decision Log",
    "Concrete Steps",
    "Validation and Evidence",
    "Outcomes and Retrospective",
    "Follow-ups",
)
TASK_REQUIRED_LABELS = (
    "State",
    "Depends on",
    "Outcome",
    "Non-goals",
    "Read",
    "Allowed writes",
    "Protected paths",
    "Acceptance",
    "Verify",
    "Stop conditions",
    "Result",
)
PRODUCT_TRACE_HEADERS = (
    "Product spec",
    "Journey",
    "P0 requirement",
    "Acceptance criteria",
    "Implementation tasks",
    "Verification tasks",
)
ACCEPTANCE_EVIDENCE_HEADERS = (
    "Acceptance criterion",
    "Task",
    "Evidence path",
    "Run ID",
    "Manifest SHA-256",
    "Verified commit",
    "Gate verdict",
    "Review reason",
)
TRACE_TERMINAL_PLACEHOLDER = re.compile(
    r"\b(?:TODO|TBD|pending)\b|\{\{[^{}\n]+\}\}|\$\{[^{}\n]+\}|<<[^<>\n]+>>",
    re.IGNORECASE,
)
DOCUMENT_SCHEMA = 2
DOCUMENT_CAPABILITY_KEYS = {
    "visual_design": Path("docs/DESIGN.md"),
    "frontend": Path("docs/FRONTEND.md"),
    "product_sense": Path("docs/PRODUCT_SENSE.md"),
    "reliability": Path("docs/RELIABILITY.md"),
}
PROJECT_KIND_DOCUMENT_DEFAULTS = {
    "service": frozenset({"reliability"}),
    "web": frozenset({"visual_design", "frontend", "reliability"}),
    "application": frozenset({"reliability"}),
    "app": frozenset({"reliability"}),
    "library": frozenset(),
    "cli": frozenset(),
    "other": frozenset(),
}
PROJECT_CONFIG_KINDS = tuple(PROJECT_KIND_DOCUMENT_DEFAULTS)


SENSITIVE_DIRECTORY_NAMES = frozenset(
    {
        ".aws",
        ".azure",
        ".credentials",
        ".gcloud",
        ".gnupg",
        ".kube",
        ".secrets",
        ".ssh",
    }
)
SENSITIVE_BASENAMES = frozenset(
    {
        ".env",
        ".envrc",
        ".git-credentials",
        ".netrc",
        ".npmrc",
        ".pypirc",
        ".terraformrc",
        ".vault-token",
        "application_default_credentials.json",
        "auth.json",
        "credentials.json",
        "secret.json",
        "secret.yaml",
        "secret.yml",
        "secrets.json",
        "secrets.yaml",
        "secrets.yml",
        "key.properties",
        "keystore.properties",
        "kubeconfig",
        "local.properties",
        "terraform.rc",
    }
)
SENSITIVE_PATH_PREFIXES = (
    ".config/gcloud/",
    ".config/gh/",
    ".config/op/",
)
SENSITIVE_PATH_SUFFIXES = frozenset(
    {
        ".bundle/config",
        ".cargo/credentials",
        ".cargo/credentials.toml",
        ".config/pip/pip.conf",
        ".docker/config.json",
        ".gem/credentials",
    }
)
SENSITIVE_SUFFIXES = frozenset(
    {
        ".db",
        ".jks",
        ".kdbx",
        ".key",
        ".keystore",
        ".mobileprovision",
        ".ovpn",
        ".p12",
        ".p8",
        ".pem",
        ".pfx",
        ".ppk",
        ".sqlite",
        ".sqlite3",
        ".secret",
        ".token",
        ".tfstate",
        ".tfvars",
    }
)
SENSITIVE_CONTENT_PATTERNS = (
    (
        "private key",
        re.compile(
            rb"-----" + rb"BEGIN (?:(?:RSA|DSA|EC|OPENSSH|ENCRYPTED) )?" + rb"PRIVATE KEY-----"
            + rb"|-----" + rb"BEGIN PGP " + rb"PRIVATE KEY BLOCK-----"
        ),
    ),
    (
        "AWS access key",
        re.compile(rb"(?<![A-Z0-9])(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Z0-9])"),
    ),
    (
        "GitHub token",
        re.compile(rb"(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})"),
    ),
    (
        "OpenAI-like API key",
        re.compile(rb"(?<![A-Za-z0-9_-])sk-(?:(?:proj|svcacct)-)?[A-Za-z0-9_-]{24,}"),
    ),
    (
        "Stripe live secret",
        re.compile(rb"(?<![A-Za-z0-9_])sk_live_[A-Za-z0-9]{16,}"),
    ),
    (
        "Google API key",
        re.compile(rb"(?<![A-Za-z0-9_-])AIza[A-Za-z0-9_-]{35}(?![A-Za-z0-9_-])"),
    ),
    (
        "GitLab personal access token",
        re.compile(rb"(?<![A-Za-z0-9_-])glpat-[A-Za-z0-9_-]{20,}"),
    ),
    (
        "npm access token",
        re.compile(rb"(?<![A-Za-z0-9_])npm_[A-Za-z0-9]{36,}"),
    ),
    (
        "Slack token",
        re.compile(rb"(?<![A-Za-z0-9_-])xox[baprs]-[A-Za-z0-9-]{20,}"),
    ),
)


class HarnessError(RuntimeError):
    """Raised for deterministic harness failures."""


class CandidateFailure(HarnessError):
    """Raised when repository behavior fails a required check."""


class InfrastructureError(HarnessError):
    """Raised when verification infrastructure cannot execute a check."""


@dataclass(frozen=True)
class AuditFinding:
    category: str
    status: str
    path: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        if self.status not in AUDIT_STATUSES:
            raise HarnessError(f"unsupported audit status: {self.status}")
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


def ensure_safe_repository_path(path: Path) -> None:
    try:
        relative = path.relative_to(ROOT)
    except ValueError as exc:
        raise HarnessError(f"refusing path outside repository root: {path}") from exc
    candidate = ROOT
    for part in relative.parts:
        if part == "..":
            raise HarnessError(f"refusing path traversal outside repository root: {path}")
        candidate = candidate / part
        if candidate.is_symlink():
            raise HarnessError(
                f"refusing to read or write through repository symlink: {relative} (via {candidate.relative_to(ROOT)})"
            )


@dataclass(frozen=True)
class RuntimePathImage:
    kind: str
    content: bytes | None
    mode: int | None
    sha256: str | None


def runtime_file_image(content: bytes, mode: int) -> RuntimePathImage:
    return RuntimePathImage("file", content, mode & 0o7777, hashlib.sha256(content).hexdigest())


def capture_runtime_path(path: Path) -> RuntimePathImage:
    ensure_safe_repository_path(path)
    relative = path.relative_to(ROOT)
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return RuntimePathImage("missing", None, None, None)
    except OSError as exc:
        raise HarnessError(f"cannot inspect transaction path {relative}: {portable_detail(exc)}") from exc
    mode = stat.S_IMODE(metadata.st_mode)
    if stat.S_ISDIR(metadata.st_mode):
        return RuntimePathImage("directory", None, mode, None)
    if not stat.S_ISREG(metadata.st_mode):
        raise HarnessError(f"transaction path is not a regular file or directory: {relative}")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode):
                raise HarnessError(f"transaction path changed filesystem type while reading: {relative}")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
        finally:
            os.close(descriptor)
    except HarnessError:
        raise
    except OSError as exc:
        raise HarnessError(f"cannot read transaction path {relative}: {portable_detail(exc)}") from exc
    return runtime_file_image(b"".join(chunks), stat.S_IMODE(opened.st_mode))


def runtime_image_matches(path: Path, image: RuntimePathImage) -> bool:
    try:
        current = capture_runtime_path(path)
    except HarnessError:
        return False
    return (
        current.kind == image.kind
        and current.mode == image.mode
        and current.sha256 == image.sha256
    )


def write_runtime_bytes(descriptor: int, content: bytes) -> None:
    view = memoryview(content)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("short write during transaction recovery")
        view = view[written:]


def chmod_runtime_file(descriptor: int, path: Path, mode: int) -> None:
    if hasattr(os, "fchmod"):
        os.fchmod(descriptor, mode)
    else:
        os.chmod(path, mode)


def restore_runtime_file(path: Path, expected: RuntimePathImage, restored: RuntimePathImage) -> None:
    if restored.kind != "file" or restored.content is None or restored.mode is None:
        raise HarnessError("transaction file preimage is incomplete")
    ensure_safe_repository_path(path)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".reporivet-write-", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        try:
            write_runtime_bytes(descriptor, restored.content)
            chmod_runtime_file(descriptor, temporary_path, restored.mode)
        finally:
            os.close(descriptor)
        ensure_safe_repository_path(path)
        if not runtime_image_matches(path, expected):
            raise HarnessError(f"transaction preimage changed before write: {path.relative_to(ROOT)}")
        if expected.kind == "missing":
            os.link(temporary_path, path)
        else:
            os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def rollback_runtime_paths(
    records: Sequence[tuple[Path, RuntimePathImage, RuntimePathImage]],
    *,
    cause: BaseException,
    label: str,
) -> None:
    preserved: list[str] = []
    errors: list[str] = []
    for path, preimage, postimage in reversed(records):
        relative = str(path.relative_to(ROOT))
        if runtime_image_matches(path, preimage):
            continue
        if not runtime_image_matches(path, postimage):
            preserved.append(relative)
            continue
        try:
            if preimage.kind == "missing":
                if postimage.kind == "file":
                    path.unlink()
                elif postimage.kind == "directory":
                    path.rmdir()
            elif preimage.kind == "file":
                restore_runtime_file(path, postimage, preimage)
            elif preimage.kind == "directory" and postimage.kind == "missing":
                if preimage.mode is None:
                    raise HarnessError("transaction directory preimage has no mode")
                path.mkdir(mode=preimage.mode)
                os.chmod(path, preimage.mode)
            else:
                raise HarnessError("unsupported transaction rollback image")
        except (OSError, HarnessError) as exc:
            preserved.append(relative)
            errors.append(f"{relative}: {portable_detail(exc)}")
    if preserved or errors:
        detail = f"{label} failed ({cause}); rollback incomplete"
        if preserved:
            detail += "; preserved path(s): " + ", ".join(sorted(set(preserved)))
        if errors:
            detail += "; rollback error(s): " + "; ".join(errors)
        raise HarnessError(detail) from cause


@dataclass(frozen=True)
class DurableDocument:
    path: Path
    id: str
    kind: str
    status: str
    area: str
    summary: str
    applies_to: tuple[str, ...]
    supersedes: tuple[str, ...] = ()
    superseded_by: tuple[str, ...] = ()


@dataclass(frozen=True)
class Plan:
    path: Path
    metadata: dict[str, object]
    text: str

    @property
    def id(self) -> str:
        return str(self.metadata.get("id", self.path.stem))

    @property
    def status(self) -> str:
        return str(self.metadata.get("status", "missing")).lower()

    @property
    def title(self) -> str:
        match = TITLE_LINE.search(self.text)
        return match.group(1).strip() if match else self.path.stem


@dataclass
class DefinitionItem:
    section: int
    heading: str
    status: str
    text: str
    line: int


@dataclass
class DefinitionSection:
    number: int
    title: str
    items: dict[str, list[DefinitionItem]]
    empty_headings: set[str]

    @property
    def confirmed(self) -> list[DefinitionItem]:
        return self.items.get("Confirmed", [])

    @property
    def proposed(self) -> list[DefinitionItem]:
        return self.items.get("Proposed", [])

    @property
    def open_items(self) -> list[DefinitionItem]:
        return self.items.get("Open", [])

    @property
    def sources(self) -> list[DefinitionItem]:
        return self.items.get("Sources", [])

    @property
    def is_confirmed(self) -> bool:
        return bool(self.confirmed) and not any(item.status == "blocking" for item in self.open_items)


@dataclass
class DefinitionDocument:
    path: Path
    metadata: dict[str, object]
    text: str
    sections: list[DefinitionSection]
    structural_errors: list[str]


@dataclass(frozen=True)
class DefinitionDeclaration:
    id: str
    kind: str
    item: DefinitionItem
    description: str
    journeys: tuple[str, ...] = ()
    p0s: tuple[str, ...] = ()
    acceptance: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProductDeclaration:
    id: str
    kind: str
    line: int
    description: str
    journeys: tuple[str, ...] = ()
    p0s: tuple[str, ...] = ()
    acceptance: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlannedPath:
    path: str
    spec_id: str
    area: str
    summary: str


@dataclass(frozen=True)
class ModuleContract:
    path: Path
    id: str
    status: str
    area: str
    summary: str
    owner: str
    responsibility: str
    applies_to: tuple[str, ...]
    public_entry_points: tuple[str, ...]
    dependency_rules: tuple[str, ...]
    organization: str
    verification: tuple[str, ...]


@dataclass(frozen=True)
class CodeMapEntry:
    path: str
    evidence: tuple[str, ...]
    areas: tuple[str, ...]
    sources: tuple[str, ...]
    descriptions: tuple[str, ...]


@dataclass(frozen=True)
class VerificationRun:
    run_id: str
    path: Path
    started_at: str

    def check_index(self, name: str) -> int:
        return VERIFICATION_CHECKS.index(name) + 1

    def check_path(self, name: str) -> Path:
        return self.path / "checks" / f"{self.check_index(name):02d}-{name}.json"

    def builtin_log_path(self, name: str) -> Path:
        return self.path / "logs" / f"{self.check_index(name):02d}-{name}.log"

    def command_log_path(self, name: str, command_index: int) -> Path:
        return self.path / "logs" / f"{self.check_index(name):02d}-{name}-{command_index:02d}.log"


@dataclass(frozen=True)
class GroupResult:
    status: str
    detail: str
    started_at: str
    finished_at: str
    commands: tuple[dict[str, object], ...]
    returncodes: tuple[int | None, ...]
    logs: tuple[str, ...]


@dataclass(frozen=True)
class CheckResult:
    name: str
    required: bool
    status: str
    detail: str
    started_at: str
    finished_at: str
    commands: tuple[dict[str, object], ...] = ()
    returncodes: tuple[int | None, ...] = ()
    logs: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        if self.status not in CHECK_STATUSES:
            raise HarnessError(f"unsupported check status: {self.status}")
        return {
            "commands": list(self.commands),
            "detail": self.detail,
            "finished_at": self.finished_at,
            "logs": list(self.logs),
            "name": self.name,
            "required": self.required,
            "returncodes": list(self.returncodes),
            "schema": "reporivet.check/v1",
            "started_at": self.started_at,
            "status": self.status,
        }


@dataclass(frozen=True)
class GatePolicy:
    mode: str
    default_risk: str
    require_clean: bool
    protected_paths: tuple[str, ...]
    contained_paths: tuple[str, ...]
    wide_paths: tuple[str, ...]
    irreversible_paths: tuple[str, ...]
    source: str

    def as_dict(self) -> dict[str, object]:
        return {
            "contained_paths": list(self.contained_paths),
            "default_risk": self.default_risk,
            "irreversible_paths": list(self.irreversible_paths),
            "mode": self.mode,
            "protected_paths": list(self.protected_paths),
            "require_clean": self.require_clean,
            "wide_paths": list(self.wide_paths),
        }


@dataclass(frozen=True)
class VerificationResult:
    run: VerificationRun
    verification_status: str
    manifest_sha256: str
    gate: dict[str, object]


@dataclass
class Config:
    raw: dict[str, object]

    @property
    def project(self) -> dict[str, object]:
        value = self.raw.get("project", {})
        return value if isinstance(value, dict) else {}

    @property
    def documents(self) -> dict[str, object]:
        value = self.raw.get("documents", {})
        return value if isinstance(value, dict) else {}

    def project_kind(self) -> str:
        project = self.raw.get("project", {})
        if not isinstance(project, dict):
            raise InfrastructureError("[project] must be a table")
        raw_kind = project.get("kind", "other")
        if not isinstance(raw_kind, str):
            raise InfrastructureError("[project].kind must be a string")
        kind = raw_kind.strip().lower()
        if kind not in PROJECT_KIND_DOCUMENT_DEFAULTS:
            choices = ", ".join(PROJECT_CONFIG_KINDS)
            raise InfrastructureError(f"[project].kind must be one of: {choices}")
        return kind

    def document_capabilities(self) -> frozenset[str]:
        kind = self.project_kind()
        if "documents" not in self.raw:
            return PROJECT_KIND_DOCUMENT_DEFAULTS[kind]
        raw = self.raw["documents"]
        if not isinstance(raw, dict):
            raise InfrastructureError("[documents] must be a table")
        if raw.get("schema") != DOCUMENT_SCHEMA:
            raise InfrastructureError("[documents].schema must be 2")
        enabled: set[str] = set()
        for key in DOCUMENT_CAPABILITY_KEYS:
            value = raw.get(key, False)
            if not isinstance(value, bool):
                raise InfrastructureError(f"[documents].{key} must be true or false")
            if value:
                enabled.add(key)
        quality_score = raw.get("quality_score", False)
        if not isinstance(quality_score, bool):
            raise InfrastructureError("[documents].quality_score must be true or false")
        if quality_score:
            raise InfrastructureError("[documents].quality_score must remain false")
        return frozenset(enabled)

    @property
    def commands(self) -> dict[str, object]:
        value = self.raw.get("commands", {})
        return value if isinstance(value, dict) else {}

    @property
    def paths(self) -> dict[str, object]:
        value = self.raw.get("paths", {})
        return value if isinstance(value, dict) else {}

    @property
    def policy(self) -> dict[str, object]:
        value = self.raw.get("policy", {})
        return value if isinstance(value, dict) else {}

    @property
    def gate(self) -> dict[str, object]:
        if "gate" not in self.raw:
            return {}
        value = self.raw["gate"]
        if not isinstance(value, dict):
            raise InfrastructureError("[gate] must be a table")
        return value

    @property
    def gate_configured(self) -> bool:
        return "gate" in self.raw

    @property
    def baseline(self) -> str:
        return str(self.project.get("baseline", "draft")).lower()

    @property
    def lifecycle(self) -> str:
        return "active" if self.baseline == "established" else "bootstrap"

    @property
    def configuration(self) -> str:
        return str(self.project.get("configuration", "review")).lower()

    def command_group(self, name: str) -> list[list[str]]:
        value = self.commands.get(name, [])
        if not isinstance(value, list):
            raise InfrastructureError(f"[commands].{name} must be an array of command arrays")
        result: list[list[str]] = []
        for index, command in enumerate(value):
            if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
                raise InfrastructureError(f"[commands].{name}[{index}] must be a non-empty array of strings")
            result.append(list(command))
        return result

    def list_value(self, section: str, name: str) -> list[str]:
        source = {"paths": self.paths, "policy": self.policy, "gate": self.gate}.get(section, {})
        value = source.get(name, []) if isinstance(source, dict) else []
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise InfrastructureError(f"[{section}].{name} must be an array of strings")
        return list(value)


def normalize_gate_pattern(value: str, *, field: str) -> str:
    pattern = value.strip()
    path = PurePosixPath(pattern)
    if (
        not pattern
        or "\\" in pattern
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in pattern.split("/"))
    ):
        raise InfrastructureError(f"[gate].{field} contains an unsafe repository-relative pattern")
    return pattern


def gate_policy(config: Config) -> GatePolicy:
    raw = config.gate
    mode = str(raw.get("mode", DEFAULT_GATE_POLICY["mode"])).strip().lower()
    default_risk = str(raw.get("default_risk", DEFAULT_GATE_POLICY["default_risk"])).strip().lower()
    require_clean = raw.get("require_clean", DEFAULT_GATE_POLICY["require_clean"])
    if mode not in GATE_MODES:
        raise InfrastructureError("[gate].mode must be 'shadow' or 'enforce'")
    if default_risk not in GATE_RISKS:
        raise InfrastructureError("[gate].default_risk must be contained, wide, irreversible, or unknown")
    if not isinstance(require_clean, bool):
        raise InfrastructureError("[gate].require_clean must be true or false")

    patterns: dict[str, tuple[str, ...]] = {}
    for field in ("protected_paths", "contained_paths", "wide_paths", "irreversible_paths"):
        value = raw.get(field, DEFAULT_GATE_POLICY[field])
        if not isinstance(value, (list, tuple)) or not all(isinstance(item, str) for item in value):
            raise InfrastructureError(f"[gate].{field} must be an array of strings")
        normalized = tuple(normalize_gate_pattern(item, field=field) for item in value)
        if len(set(normalized)) != len(normalized):
            raise InfrastructureError(f"[gate].{field} must not contain duplicate patterns")
        patterns[field] = normalized

    return GatePolicy(
        mode=mode,
        default_risk=default_risk,
        require_clean=require_clean,
        protected_paths=patterns["protected_paths"],
        contained_paths=patterns["contained_paths"],
        wide_paths=patterns["wide_paths"],
        irreversible_paths=patterns["irreversible_paths"],
        source="configured" if config.gate_configured else "default",
    )


def default_gate_policy(*, source: str = "default") -> GatePolicy:
    config = Config({})
    policy = gate_policy(config)
    return GatePolicy(
        mode=policy.mode,
        default_risk=policy.default_risk,
        require_clean=policy.require_clean,
        protected_paths=policy.protected_paths,
        contained_paths=policy.contained_paths,
        wide_paths=policy.wide_paths,
        irreversible_paths=policy.irreversible_paths,
        source=source,
    )


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        raise InfrastructureError(f"missing deterministic configuration: {CONFIG_PATH.relative_to(ROOT)}")
    try:
        with CONFIG_PATH.open("rb") as handle:
            raw = tomllib.load(handle)
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise InfrastructureError(f"cannot read {CONFIG_PATH.relative_to(ROOT)}: {exc}") from exc
    if raw.get("version") != 1:
        raise InfrastructureError("unsupported dev/harness.toml version; expected version = 1")
    config = Config(raw)
    if config.baseline not in {"draft", "established"}:
        raise InfrastructureError("[project].baseline must be 'draft' or 'established'")
    if config.configuration not in {"ready", "review"}:
        raise InfrastructureError("[project].configuration must be 'ready' or 'review'")
    config.document_capabilities()
    gate_policy(config)
    return config


def audit_relative(path: Path) -> str:
    try:
        relative = path.relative_to(ROOT).as_posix()
    except ValueError:
        return "."
    return relative or "."


def audit_symlink_component(path: Path) -> Path | None:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return path
    candidate = ROOT
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            return candidate
    return None


def audit_repository_entries() -> tuple[list[Path], list[AuditFinding]]:
    files: list[Path] = []
    skipped: list[AuditFinding] = []

    def record_walk_error(error: OSError) -> None:
        path = Path(error.filename) if error.filename else ROOT
        skipped.append(
            AuditFinding(
                category="skipped-path",
                status="skipped",
                path=audit_relative(path),
                detail="path could not be read during inventory",
            )
        )

    for current_text, directory_names, file_names in os.walk(
        ROOT,
        topdown=True,
        followlinks=False,
        onerror=record_walk_error,
    ):
        current = Path(current_text)
        retained_directories: list[str] = []
        for name in sorted(directory_names):
            path = current / name
            relative = audit_relative(path)
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
            relative = audit_relative(path)
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


def audit_marker_line_spans(text: str, marker: str) -> list[tuple[int, int]]:
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


def audit_managed_block_span(text: str, start: str, end: str) -> tuple[int, int] | None:
    starts = audit_marker_line_spans(text, start)
    ends = audit_marker_line_spans(text, end)
    if not starts and not ends:
        return None
    if len(starts) != 1 or len(ends) != 1 or ends[0][0] < starts[0][1]:
        raise HarnessError(f"existing file has malformed managed markers: {start} / {end}")
    return starts[0][0], ends[0][1]


def audit_managed_block_state(text: str, start: str, end: str) -> str:
    try:
        span = audit_managed_block_span(text, start, end)
    except HarnessError:
        return "malformed"
    return "absent" if span is None else "present"


def audit_is_managed_file(path: Path) -> bool:
    if audit_symlink_component(path) is not None or not path.is_file():
        return False
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:3]
    except OSError:
        return False
    return any(MANAGED_MARKER.fullmatch(line) is not None for line in lines)


def audit_command_detail(command: Sequence[str], *, configured: bool) -> str:
    if configured:
        return f"configured argv command; argc={len(command)}; content=redacted"
    return json.dumps(list(command), ensure_ascii=False, separators=(",", ":"))


def audit_load_package_scripts() -> tuple[str, dict[str, str]]:
    package_path = ROOT / "package.json"
    if not package_path.exists():
        return "npm", {}
    try:
        data = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "npm", {}
    manager = "npm"
    if (ROOT / "pnpm-lock.yaml").exists():
        manager = "pnpm"
    elif (ROOT / "yarn.lock").exists():
        manager = "yarn"
    elif (ROOT / "bun.lockb").exists() or (ROOT / "bun.lock").exists():
        manager = "bun"
    scripts = data.get("scripts", {})
    return manager, scripts if isinstance(scripts, dict) else {}


def audit_node_run(manager: str, script: str) -> list[str]:
    return ["npm", "run", script] if manager == "npm" else [manager, "run", script]


def audit_has_python_test_files() -> bool:
    tests = ROOT / "tests"
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


def audit_detect_commands() -> dict[str, list[list[str]]]:
    commands: dict[str, list[list[str]]] = {
        "bootstrap": [],
        "run": [],
        "check": [],
        "verify": [],
        "smoke": [],
        "architecture": [],
    }

    if (ROOT / "package.json").exists():
        manager, scripts = audit_load_package_scripts()
        if manager == "pnpm":
            commands["bootstrap"].append(["pnpm", "install", "--frozen-lockfile"])
        elif manager == "yarn":
            commands["bootstrap"].append(["yarn", "install", "--immutable"])
        elif manager == "bun":
            commands["bootstrap"].append(["bun", "install", "--frozen-lockfile"])
        elif (ROOT / "package-lock.json").exists():
            commands["bootstrap"].append(["npm", "ci"])
        else:
            commands["bootstrap"].append(["npm", "install"])
        for candidate in ("dev", "start"):
            if candidate in scripts:
                commands["run"].append(audit_node_run(manager, candidate))
                break
        if "check" in scripts:
            commands["check"].append(audit_node_run(manager, "check"))
        else:
            for name in ("lint", "typecheck", "test"):
                if name in scripts:
                    commands["check"].append(audit_node_run(manager, name))
        if "verify" in scripts:
            commands["verify"].append(audit_node_run(manager, "verify"))
        else:
            commands["verify"].extend(commands["check"])
            if "build" in scripts:
                commands["verify"].append(audit_node_run(manager, "build"))
        for candidate in ("test:smoke", "smoke", "test:e2e"):
            if candidate in scripts:
                commands["smoke"].append(audit_node_run(manager, candidate))
                break

    pyproject_text = ""
    if (ROOT / "pyproject.toml").exists():
        pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8", errors="ignore").lower()
        if (ROOT / "uv.lock").exists():
            commands["bootstrap"].append(["uv", "sync", "--frozen"])
        elif (ROOT / "poetry.lock").exists():
            commands["bootstrap"].append(["poetry", "install", "--sync"])
        else:
            commands["bootstrap"].append(["python", "-m", "pip", "install", "-e", "."])
    elif (ROOT / "requirements.txt").exists():
        commands["bootstrap"].append(["python", "-m", "pip", "install", "-r", "requirements.txt"])

    python_checks: list[list[str]] = []
    if "ruff" in pyproject_text or (ROOT / "ruff.toml").exists():
        python_checks.append(["python", "-m", "ruff", "check", "."])
    if "mypy" in pyproject_text or (ROOT / "mypy.ini").exists():
        python_checks.append(["python", "-m", "mypy", "."])
    if (ROOT / "tests").is_dir():
        if "pytest" in pyproject_text or (ROOT / "pytest.ini").exists():
            python_checks.append(["python", "-m", "pytest"])
        elif audit_has_python_test_files():
            python_checks.append(["python", "-m", "unittest", "discover", "-s", "tests", "-v"])
    commands["check"].extend(command for command in python_checks if command not in commands["check"])
    commands["verify"].extend(command for command in python_checks if command not in commands["verify"])

    if (ROOT / "go.mod").exists():
        commands["bootstrap"].append(["go", "mod", "download"])
        commands["check"].append(["go", "test", "./..."])
        commands["verify"].extend((["go", "test", "./..."], ["go", "vet", "./..."]))
    if (ROOT / "Cargo.toml").exists():
        commands["bootstrap"].append(
            ["cargo", "fetch", "--locked"] if (ROOT / "Cargo.lock").exists() else ["cargo", "fetch"]
        )
        commands["check"].append(["cargo", "test"])
        commands["verify"].extend(
            (
                ["cargo", "fmt", "--check"],
                ["cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings"],
                ["cargo", "test", "--all-features"],
            )
        )
    if (ROOT / "mvnw").exists():
        commands["bootstrap"].append(["./mvnw", "dependency:go-offline"])
        commands["check"].append(["./mvnw", "test"])
        commands["verify"].append(["./mvnw", "verify"])
    elif (ROOT / "pom.xml").exists():
        commands["bootstrap"].append(["mvn", "dependency:go-offline"])
        commands["check"].append(["mvn", "test"])
        commands["verify"].append(["mvn", "verify"])
    if (ROOT / "gradlew").exists():
        commands["bootstrap"].append(["./gradlew", "dependencies"])
        commands["check"].append(["./gradlew", "test"])
        commands["verify"].append(["./gradlew", "check"])
    elif (ROOT / "build.gradle").exists() or (ROOT / "build.gradle.kts").exists():
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


def audit_command_findings() -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    config_component = audit_symlink_component(CONFIG_PATH)
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
    if CONFIG_PATH.exists() and not CONFIG_PATH.is_file():
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
    configured = CONFIG_PATH.is_file()
    if configured:
        try:
            with CONFIG_PATH.open("rb") as handle:
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
            if audit_symlink_component(ROOT / relative) is not None
        ]
        nonregular: list[str] = []
        for relative in command_inputs:
            if relative in unsafe:
                continue
            path = ROOT / relative
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
        package_path = ROOT / "package.json"
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
        pyproject_path = ROOT / "pyproject.toml"
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
        commands = audit_detect_commands()

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


def audit_project_document_paths() -> tuple[tuple[str, ...], list[AuditFinding]]:
    base_paths = tuple(sorted(AUDIT_PROJECT_DOCUMENT_PATHS))
    if audit_symlink_component(CONFIG_PATH) is not None:
        return base_paths, []
    if CONFIG_PATH.exists() and not CONFIG_PATH.is_file():
        return base_paths, []
    if not CONFIG_PATH.is_file():
        return base_paths, []
    try:
        with CONFIG_PATH.open("rb") as handle:
            raw = tomllib.load(handle)
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return base_paths, []
    if raw.get("version") != 1:
        return base_paths, [
            AuditFinding(
                category="document-configuration",
                status="conflict",
                path="dev/harness.toml",
                detail="unsupported dev/harness.toml version; expected version = 1",
            )
        ]
    config = Config(raw)
    try:
        capabilities = config.document_capabilities()
    except InfrastructureError as exc:
        return base_paths, [
            AuditFinding(
                category="document-configuration",
                status="conflict",
                path="dev/harness.toml",
                detail=f"dev/harness.toml {exc}",
            )
        ]
    selected = set(base_paths)
    selected.update(
        path.as_posix()
        for capability, path in DOCUMENT_CAPABILITY_KEYS.items()
        if capability in capabilities
    )
    return tuple(sorted(selected)), []


def audit_adoption_findings() -> list[AuditFinding]:
    project_document_paths, findings = audit_project_document_paths()
    shared_targets = (
        ("AGENTS.md", AGENTS_START, AGENTS_END, "agent operating contract"),
        (".gitignore", GITIGNORE_START, GITIGNORE_END, "generated evidence exclusions"),
    )
    for relative, start, end, responsibility in shared_targets:
        path = ROOT / relative
        if audit_symlink_component(path) is not None:
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
        path = ROOT / relative
        if audit_symlink_component(path) is not None:
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

    if CONFIG_PATH.is_file() and audit_symlink_component(CONFIG_PATH) is None:
        findings.append(
            AuditFinding(
                category="authority",
                status="skipped",
                path="dev/harness.toml",
                detail="existing project-owned command configuration will be preserved byte-for-byte",
            )
        )
    elif not CONFIG_PATH.exists() and not CONFIG_PATH.is_symlink():
        findings.append(
            AuditFinding(
                category="proposed-addition",
                status="inferred",
                path="dev/harness.toml",
                detail="adoption will create review-state command configuration",
            )
        )

    draft_path = ROOT / DEFINITION_DRAFT
    if draft_path.is_file() and audit_symlink_component(draft_path) is None:
        findings.append(
            AuditFinding(
                category="authority",
                status="skipped",
                path=DEFINITION_DRAFT.as_posix(),
                detail="existing project-owned definition draft will be preserved byte-for-byte",
            )
        )
    elif not draft_path.exists() and not draft_path.is_symlink():
        findings.append(
            AuditFinding(
                category="proposed-addition",
                status="inferred",
                path=DEFINITION_DRAFT.as_posix(),
                detail="adoption will create a resumable project-definition draft",
            )
        )

    for relative in sorted(AUDIT_MANAGED_RUNTIME_PATHS):
        path = ROOT / relative
        if audit_symlink_component(path) is not None:
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
        elif path.is_file() and audit_is_managed_file(path):
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


def audit_project() -> AuditReport:
    files, findings = audit_repository_entries()
    for path in files:
        relative = audit_relative(path)
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
        if (ROOT / name).is_dir() and not (ROOT / name).is_symlink()
    ]
    test_directories = [
        name
        for name in AUDIT_TEST_DIRECTORIES
        if (ROOT / name).is_dir() and not (ROOT / name).is_symlink()
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

    findings.extend(audit_command_findings())
    findings.extend(audit_adoption_findings())
    unique = {
        (finding.category, finding.status, finding.path, finding.detail): finding
        for finding in findings
    }
    ordered = tuple(
        unique[key]
        for key in sorted(unique, key=lambda item: (item[0], item[2], item[1], item[3]))
    )
    return AuditReport(ordered)


def command_audit(args: argparse.Namespace) -> int:
    del args
    print(audit_project().render(), end="")
    return 0


def parse_scalar(value: str) -> object:
    value = value.strip()
    if not value:
        return ""
    if value.startswith('"') and value.endswith('"'):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, str):
            return decoded
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("\"'") for part in inner.split(",") if part.strip()]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value.strip("\"'")


def parse_frontmatter_text(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text
    closing = text.find("\n---\n", 4)
    if closing == -1:
        return {}, text
    block = text[4:closing]
    body = text[closing + 5 :]
    data: dict[str, object] = {}
    current_list: str | None = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  - ") and current_list:
            existing = data.setdefault(current_list, [])
            if isinstance(existing, list):
                existing.append(raw[4:].strip().strip("\"'"))
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        if value.strip() == "":
            data[key] = []
            current_list = key
        else:
            data[key] = parse_scalar(value)
            current_list = None
    return data, body


def read_frontmatter(path: Path) -> tuple[dict[str, object], str, str]:
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter_text(text)
    return metadata, body, text


def update_frontmatter(text: str, updates: dict[str, str]) -> str:
    metadata, body = parse_frontmatter_text(text)
    if not metadata:
        raise HarnessError("cannot update a document without frontmatter")
    lines = text[4 : text.find("\n---\n", 4)].splitlines()
    handled: set[str] = set()
    output: list[str] = []
    for line in lines:
        if ":" not in line or line.startswith("  - "):
            output.append(line)
            continue
        key = line.split(":", 1)[0].strip()
        if key in updates:
            output.append(f"{key}: {updates[key]}")
            handled.add(key)
        else:
            output.append(line)
    for key, value in updates.items():
        if key not in handled:
            output.append(f"{key}: {value}")
    return "---\n" + "\n".join(output) + "\n---\n" + body


def definition_item_location(item: DefinitionItem) -> str:
    return f"{DEFINITION_DRAFT}:{item.line}"


def parse_definition_document() -> DefinitionDocument:
    path = ROOT / DEFINITION_DRAFT
    ensure_safe_repository_path(path)
    if not path.exists():
        raise HarnessError(
            f"definition draft is missing: {DEFINITION_DRAFT}; explicitly start it with reporivet define --root {ROOT}"
        )
    text = path.read_text(encoding="utf-8")
    metadata, _ = parse_frontmatter_text(text)
    errors: list[str] = []
    if not metadata:
        errors.append(f"{DEFINITION_DRAFT}: missing definition frontmatter")
    else:
        if str(metadata.get("kind", "")) != "project-definition-draft":
            errors.append(f"{DEFINITION_DRAFT}: kind must be 'project-definition-draft'")
        if str(metadata.get("format", "")) != "1":
            errors.append(f"{DEFINITION_DRAFT}: format must be 1")
        for field in ("created", "updated", "progress", "next", "continuation"):
            if not str(metadata.get(field, "")).strip():
                errors.append(f"{DEFINITION_DRAFT}: missing definition metadata '{field}'")

    level_two = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    parsed_headings: list[tuple[re.Match[str], int | None, str]] = []
    numbers: list[int] = []
    for match in level_two:
        raw = match.group(1).strip()
        numbered = re.fullmatch(r"(\d+)\.\s+(.+)", raw)
        if not numbered:
            errors.append(f"{DEFINITION_DRAFT}: unknown unnumbered section '## {raw}'")
            parsed_headings.append((match, None, raw))
            continue
        number = int(numbered.group(1))
        title = numbered.group(2).strip()
        parsed_headings.append((match, number, title))
        numbers.append(number)
        if number < 1 or number > len(DEFINITION_SECTIONS):
            errors.append(f"{DEFINITION_DRAFT}: unknown section number {number}")
        elif title != DEFINITION_SECTIONS[number - 1]:
            errors.append(
                f"{DEFINITION_DRAFT}: section {number} must be '{DEFINITION_SECTIONS[number - 1]}', got '{title}'"
            )

    for number, title in enumerate(DEFINITION_SECTIONS, start=1):
        count = numbers.count(number)
        if count == 0:
            errors.append(f"{DEFINITION_DRAFT}: missing section '## {number}. {title}'")
        elif count > 1:
            errors.append(f"{DEFINITION_DRAFT}: duplicate section {number} ({title})")
    expected_numbers = list(range(1, len(DEFINITION_SECTIONS) + 1))
    if numbers != expected_numbers:
        errors.append(
            f"{DEFINITION_DRAFT}: numbered sections are out of order; expected "
            + ", ".join(str(number) for number in expected_numbers)
        )

    sections: list[DefinitionSection] = []
    first_by_number: dict[int, tuple[int, re.Match[str], str]] = {}
    for index, (match, number, title) in enumerate(parsed_headings):
        if number is not None and 1 <= number <= len(DEFINITION_SECTIONS) and number not in first_by_number:
            first_by_number[number] = (index, match, title)

    for number, expected_title in enumerate(DEFINITION_SECTIONS, start=1):
        found = first_by_number.get(number)
        if found is None:
            sections.append(
                DefinitionSection(number=number, title=expected_title, items={}, empty_headings=set())
            )
            continue
        heading_index, heading_match, actual_title = found
        next_start = level_two[heading_index + 1].start() if heading_index + 1 < len(level_two) else len(text)
        block_start = heading_match.end()
        block = text[block_start:next_start]
        evidence_matches = list(DEFINITION_EVIDENCE_HEADING.finditer(block))
        evidence_names = [match.group(1).strip() for match in evidence_matches]
        for heading in DEFINITION_EVIDENCE_HEADINGS:
            count = evidence_names.count(heading)
            if count == 0:
                errors.append(f"{DEFINITION_DRAFT}: section {number} is missing evidence heading '### {heading}'")
            elif count > 1:
                errors.append(f"{DEFINITION_DRAFT}: section {number} has duplicate evidence heading '### {heading}'")
        unknown = [heading for heading in evidence_names if heading not in DEFINITION_EVIDENCE_HEADINGS]
        for heading in unknown:
            errors.append(f"{DEFINITION_DRAFT}: section {number} has unknown evidence heading '### {heading}'")
        if evidence_names != list(DEFINITION_EVIDENCE_HEADINGS):
            errors.append(
                f"{DEFINITION_DRAFT}: section {number} evidence headings are missing, duplicated, or out of order"
            )

        prefix = block[: evidence_matches[0].start()] if evidence_matches else block
        if prefix.strip():
            errors.append(f"{DEFINITION_DRAFT}: section {number} has content outside evidence headings")

        items: dict[str, list[DefinitionItem]] = {heading: [] for heading in DEFINITION_EVIDENCE_HEADINGS}
        empty_headings: set[str] = set()
        parsed_once: set[str] = set()
        for evidence_index, evidence_match in enumerate(evidence_matches):
            heading = evidence_match.group(1).strip()
            content_end = (
                evidence_matches[evidence_index + 1].start()
                if evidence_index + 1 < len(evidence_matches)
                else len(block)
            )
            if heading not in DEFINITION_EVIDENCE_HEADINGS or heading in parsed_once:
                continue
            parsed_once.add(heading)
            content_start = evidence_match.end()
            content = block[content_start:content_end]
            absolute_start = block_start + content_start
            base_line = text.count("\n", 0, absolute_start)
            none_count = 0
            saw_item = False
            for line_offset, raw_line in enumerate(content.splitlines(), start=1):
                stripped = raw_line.strip()
                if not stripped:
                    continue
                line_number = base_line + line_offset
                if stripped == "- None.":
                    none_count += 1
                    continue
                item_match = re.fullmatch(r"-\s+\[([A-Za-z][A-Za-z-]*)\]\s+(.+)", stripped)
                if not item_match:
                    errors.append(
                        f"{DEFINITION_DRAFT}:{line_number}: malformed evidence item under {heading}; "
                        "use '- [status] text' or '- None.'"
                    )
                    continue
                status = item_match.group(1).lower()
                item_text = item_match.group(2).strip()
                allowed_statuses = DEFINITION_ITEM_STATUSES[heading]
                if status not in allowed_statuses:
                    errors.append(
                        f"{DEFINITION_DRAFT}:{line_number}: unknown evidence status '[{status}]' under {heading}; "
                        f"expected {sorted(allowed_statuses)}"
                    )
                items[heading].append(
                    DefinitionItem(
                        section=number,
                        heading=heading,
                        status=status,
                        text=item_text,
                        line=line_number,
                    )
                )
                saw_item = True
            if none_count > 1:
                errors.append(f"{DEFINITION_DRAFT}: section {number} {heading} has duplicate '- None.' sentinels")
            if none_count and saw_item:
                errors.append(f"{DEFINITION_DRAFT}: section {number} {heading} cannot combine '- None.' with evidence")
            if not none_count and not saw_item:
                errors.append(f"{DEFINITION_DRAFT}: section {number} {heading} must contain evidence or '- None.'")
            if none_count:
                empty_headings.add(heading)
        sections.append(
            DefinitionSection(
                number=number,
                title=actual_title,
                items=items,
                empty_headings=empty_headings,
            )
        )
    return DefinitionDocument(path=path, metadata=metadata, text=text, sections=sections, structural_errors=errors)


def definition_section(document: DefinitionDocument, number: int) -> DefinitionSection:
    return document.sections[number - 1]


def definition_identifier_kind(identifier: str) -> str | None:
    for kind, pattern in DEFINITION_ID_PATTERNS.items():
        if pattern.fullmatch(identifier):
            return kind
    return None


def definition_field_ids(
    text: str,
    label: str,
    kind: str,
    errors: list[str],
    item: DefinitionItem,
) -> tuple[str, ...]:
    matches = list(re.finditer(rf"(?:^|\|)\s*{re.escape(label)}:\s*([^|]+)", text, re.IGNORECASE))
    if not matches:
        errors.append(f"{definition_item_location(item)}: missing '{label}:' link field")
        return ()
    if len(matches) > 1:
        errors.append(f"{definition_item_location(item)}: duplicate '{label}:' link field")
    value = matches[0].group(1).strip()
    pattern = DEFINITION_ID_PATTERNS[kind]
    identifiers = tuple(pattern.findall(value))
    value_pattern = re.compile(rf"{pattern.pattern}(?:\s*,\s*{pattern.pattern})*")
    if value_pattern.fullmatch(value) is None:
        errors.append(
            f"{definition_item_location(item)}: malformed '{label}:' links; use comma-separated {pattern.pattern} IDs"
        )
    if len(set(identifiers)) != len(identifiers):
        errors.append(f"{definition_item_location(item)}: duplicate identifier in '{label}:' links")
    return identifiers


def definition_description(text: str) -> str:
    parts = [part.strip() for part in text.split("|")]
    if parts and definition_identifier_kind(parts[0]):
        parts = parts[1:]
    retained = [
        part
        for part in parts
        if not re.match(r"^(?:Journey|Acceptance|P0):", part, re.IGNORECASE)
    ]
    return " | ".join(part for part in retained if part).strip()


def definition_part_has_label(part: str, label: str) -> bool:
    return re.fullmatch(rf"{re.escape(label)}:\s*.+", part, re.IGNORECASE) is not None


def validate_definition_declaration_shape(
    identifier: str,
    kind: str,
    item: DefinitionItem,
    errors: list[str],
) -> None:
    parts = [part.strip() for part in item.text.split("|")]
    valid = False
    expected = ""
    if kind == "journey":
        valid = len(parts) == 2
        expected = "JRN-* | description"
    elif kind == "p0":
        valid = (
            len(parts) == 4
            and definition_part_has_label(parts[1], "Journey")
            and definition_part_has_label(parts[2], "Acceptance")
        )
        expected = "REQ-P0-* | Journey: JRN-* | Acceptance: AC-* | description"
    elif kind == "acceptance":
        valid = (
            len(parts) == 4
            and definition_part_has_label(parts[1], "P0")
            and definition_part_has_label(parts[2], "Journey")
        )
        expected = "AC-* | P0: REQ-P0-* | Journey: JRN-* | observable criterion"
    if not valid:
        errors.append(
            f"{definition_item_location(item)}: {identifier} declaration must use '{expected}' form"
        )


def collect_definition_declarations(
    document: DefinitionDocument,
    errors: list[str],
) -> dict[str, DefinitionDeclaration]:
    declarations: dict[str, DefinitionDeclaration] = {}
    expected_sections = {"p0": 5, "journey": 6, "acceptance": 13}
    declaration_pattern = re.compile(r"^(JRN-[0-9]+|REQ-P0-[0-9]+|AC-[0-9]+)\s*\|\s*(.+)$")
    for section in document.sections:
        for item in section.confirmed + section.proposed:
            match = declaration_pattern.fullmatch(item.text)
            if not match:
                leading = DEFINITION_ID_CANDIDATE.match(item.text)
                if leading and definition_identifier_kind(leading.group(0)):
                    errors.append(
                        f"{definition_item_location(item)}: identifier declarations must use 'ID | description' form"
                    )
                continue
            identifier = match.group(1)
            kind = definition_identifier_kind(identifier)
            assert kind is not None
            validate_definition_declaration_shape(identifier, kind, item, errors)
            expected_section = expected_sections[kind]
            if section.number != expected_section:
                errors.append(
                    f"{definition_item_location(item)}: {identifier} declarations belong in section {expected_section}"
                )
            journeys: tuple[str, ...] = ()
            p0s: tuple[str, ...] = ()
            acceptance: tuple[str, ...] = ()
            if kind == "p0":
                journeys = definition_field_ids(item.text, "Journey", "journey", errors, item)
                acceptance = definition_field_ids(item.text, "Acceptance", "acceptance", errors, item)
            elif kind == "acceptance":
                p0s = definition_field_ids(item.text, "P0", "p0", errors, item)
                journeys = definition_field_ids(item.text, "Journey", "journey", errors, item)
            description = definition_description(item.text)
            if not definition_value_is_concrete(description):
                errors.append(f"{definition_item_location(item)}: {identifier} is missing a concrete description")
            declaration = DefinitionDeclaration(
                id=identifier,
                kind=kind,
                item=item,
                description=description,
                journeys=journeys,
                p0s=p0s,
                acceptance=acceptance,
            )
            prior = declarations.get(identifier)
            if prior:
                contradictory = (
                    prior.item.status != item.status
                    or prior.description.casefold() != description.casefold()
                    or prior.journeys != journeys
                    or prior.p0s != p0s
                    or prior.acceptance != acceptance
                )
                if contradictory:
                    errors.append(
                        f"{definition_item_location(item)}: contradictory duplicate evidence for {identifier}; "
                        f"first declared at line {prior.item.line}"
                    )
                else:
                    errors.append(
                        f"{definition_item_location(item)}: duplicate identifier {identifier}; first declared at line {prior.item.line}"
                    )
                continue
            declarations[identifier] = declaration
    return declarations


def normalized_definition_evidence(text: str) -> str:
    parts = [part.strip() for part in text.split("|")]
    if parts and definition_identifier_kind(parts[0]):
        parts = parts[1:]
    parts = [
        part
        for part in parts
        if not re.match(r"^(?:Journey|Acceptance|P0):", part, re.IGNORECASE)
    ]
    normalized = " ".join(" ".join(parts).casefold().split())
    return normalized.strip(" .")


def normalized_definition_value(value: str) -> str:
    normalized = " ".join(
        unicodedata.normalize("NFKC", value).casefold().split()
    )
    while normalized and (
        normalized[0].isspace()
        or unicodedata.category(normalized[0])[0] in {"P", "S"}
    ):
        normalized = normalized[1:]
    while normalized and (
        normalized[-1].isspace()
        or unicodedata.category(normalized[-1])[0] in {"P", "S"}
    ):
        normalized = normalized[:-1]
    return " ".join(normalized.split())


def definition_value_is_concrete(value: str) -> bool:
    normalized = normalized_definition_value(value)
    if normalized in {
        "",
        "-",
        "n/a",
        "none",
        "not decided",
        "not defined",
        "not established",
        "not known",
        "not provided",
        "not recorded",
        "not specified",
        "pending",
        "tbd",
        "to be decided",
        "to be determined",
        "todo",
        "undecided",
        "undetermined",
        "unknown",
        "unspecified",
        "unresolved",
    }:
        return False
    return re.search(r"[A-Za-z0-9가-힣]", normalized) is not None


def definition_label_occurrences(text: str, label: str) -> int:
    return len(re.findall(rf"(?:^|[|;,])\s*{re.escape(label)}\s*:", text, re.IGNORECASE))


def definition_labeled_values(items: Sequence[DefinitionItem], label: str) -> list[str]:
    prefix = label.casefold() + ":"
    return [
        item.text.split(":", 1)[1].strip()
        for item in items
        if item.text.casefold().startswith(prefix)
    ]


def definition_evidence_payload(text: str) -> str:
    first_part = text.split("|", 1)[0].strip()
    if definition_identifier_kind(first_part):
        return definition_description(text)
    if ":" in first_part:
        return first_part.split(":", 1)[1].strip()
    return first_part


def definition_confirmed_values(document: DefinitionDocument, section_number: int, label: str) -> list[str]:
    return definition_labeled_values(definition_section(document, section_number).confirmed, label)


def validate_definition_document(document: DefinitionDocument) -> tuple[list[str], dict[str, DefinitionDeclaration]]:
    errors = list(document.structural_errors)
    if errors:
        return errors, {}
    if re.search(r"\b(?:TODO|TBD)\b", document.text, re.IGNORECASE):
        errors.append(f"{DEFINITION_DRAFT}: unresolved TODO or TBD marker")
    if DEFINITION_TEMPLATE_TOKEN.search(document.text):
        errors.append(f"{DEFINITION_DRAFT}: unresolved template token")

    for section in document.sections:
        if not section.is_confirmed:
            errors.append(
                f"{DEFINITION_DRAFT}: section {section.number} ({section.title}) is unresolved; "
                "confirmed evidence and no blocking Open item are required"
            )
        for item in section.open_items:
            if item.status == "blocking":
                errors.append(f"{definition_item_location(item)}: blocking Open item must be resolved before validation")
            elif item.status == "non-blocking" and not definition_value_is_concrete(
                definition_evidence_payload(item.text)
            ):
                errors.append(
                    f"{definition_item_location(item)}: non-blocking Open item must contain a concrete unresolved question or follow-up"
                )
        for item in section.confirmed + section.proposed:
            if not definition_value_is_concrete(definition_evidence_payload(item.text)):
                errors.append(
                    f"{definition_item_location(item)}: {item.status} evidence must contain a concrete value"
                )
        seen_text: dict[str, DefinitionItem] = {}
        for item in section.confirmed + section.proposed:
            normalized = normalized_definition_evidence(item.text)
            if not normalized:
                continue
            prior = seen_text.get(normalized)
            if prior:
                if {prior.status, item.status} == {"confirmed", "proposed"}:
                    errors.append(
                        f"{definition_item_location(item)}: proposal is also represented as confirmed duplicate text; "
                        f"first recorded at line {prior.line}"
                    )
                else:
                    errors.append(
                        f"{definition_item_location(item)}: duplicate evidence text; first recorded at line {prior.line}"
                    )
            else:
                seen_text[normalized] = item

    for section in document.sections:
        for item in section.confirmed + section.proposed:
            first_part = item.text.split("|", 1)[0].strip()
            normalized_first_part = unicodedata.normalize("NFKC", first_part)
            if (
                "|" in item.text
                and DEFINITION_DECLARATION_ID_CANDIDATE.fullmatch(
                    normalized_first_part
                )
                and definition_identifier_kind(first_part) is None
            ):
                errors.append(
                    f"{definition_item_location(item)}: malformed stable declaration identifier '{first_part}'"
                )
        for heading in DEFINITION_EVIDENCE_HEADINGS:
            for item in section.items.get(heading, []):
                for candidate in DEFINITION_ID_CANDIDATE.findall(item.text):
                    if definition_identifier_kind(candidate) is None:
                        errors.append(f"{definition_item_location(item)}: malformed stable identifier '{candidate}'")

    declarations = collect_definition_declarations(document, errors)
    journeys = {identifier: declaration for identifier, declaration in declarations.items() if declaration.kind == "journey"}
    p0s = {identifier: declaration for identifier, declaration in declarations.items() if declaration.kind == "p0"}
    acceptance = {
        identifier: declaration for identifier, declaration in declarations.items() if declaration.kind == "acceptance"
    }
    confirmed_journeys = {identifier for identifier, declaration in journeys.items() if declaration.item.status == "confirmed"}
    confirmed_p0s = {identifier for identifier, declaration in p0s.items() if declaration.item.status == "confirmed"}
    confirmed_acceptance = {
        identifier for identifier, declaration in acceptance.items() if declaration.item.status == "confirmed"
    }
    if not confirmed_journeys:
        errors.append(f"{DEFINITION_DRAFT}: at least one confirmed JRN-* declaration is required")
    if not confirmed_p0s:
        errors.append(f"{DEFINITION_DRAFT}: at least one confirmed REQ-P0-* declaration is required")
    if not confirmed_acceptance:
        errors.append(f"{DEFINITION_DRAFT}: at least one confirmed AC-* declaration is required")

    for identifier, declaration in p0s.items():
        if not declaration.journeys:
            errors.append(f"{definition_item_location(declaration.item)}: {identifier} has no journey link")
        if not declaration.acceptance:
            errors.append(f"{definition_item_location(declaration.item)}: {identifier} has no acceptance link")
        for journey in declaration.journeys:
            if journey not in journeys:
                errors.append(f"{definition_item_location(declaration.item)}: {identifier} references unknown journey {journey}")
            elif declaration.item.status == "confirmed" and journey not in confirmed_journeys:
                errors.append(f"{definition_item_location(declaration.item)}: confirmed {identifier} references proposed journey {journey}")
        for criterion in declaration.acceptance:
            if criterion not in acceptance:
                errors.append(f"{definition_item_location(declaration.item)}: {identifier} references unknown acceptance {criterion}")
            elif declaration.item.status == "confirmed" and criterion not in confirmed_acceptance:
                errors.append(f"{definition_item_location(declaration.item)}: confirmed {identifier} references proposed acceptance {criterion}")

    for identifier, declaration in acceptance.items():
        if not declaration.p0s:
            errors.append(f"{definition_item_location(declaration.item)}: {identifier} has no P0 link")
        if not declaration.journeys:
            errors.append(f"{definition_item_location(declaration.item)}: {identifier} has no journey link")
        for p0 in declaration.p0s:
            if p0 not in p0s:
                errors.append(f"{definition_item_location(declaration.item)}: {identifier} references unknown P0 {p0}")
            elif declaration.item.status == "confirmed" and p0 not in confirmed_p0s:
                errors.append(f"{definition_item_location(declaration.item)}: confirmed {identifier} references proposed P0 {p0}")
        for journey in declaration.journeys:
            if journey not in journeys:
                errors.append(f"{definition_item_location(declaration.item)}: {identifier} references unknown journey {journey}")
            elif declaration.item.status == "confirmed" and journey not in confirmed_journeys:
                errors.append(f"{definition_item_location(declaration.item)}: confirmed {identifier} references proposed journey {journey}")

    for p0_id, declaration in p0s.items():
        for acceptance_id in declaration.acceptance:
            criterion = acceptance.get(acceptance_id)
            if criterion and p0_id not in criterion.p0s:
                errors.append(
                    f"{definition_item_location(declaration.item)}: {p0_id} and {acceptance_id} links are not reciprocal"
                )
            if criterion and not set(declaration.journeys).intersection(criterion.journeys):
                errors.append(
                    f"{definition_item_location(declaration.item)}: {p0_id} and {acceptance_id} do not share a journey link"
                )

    for acceptance_id, criterion in acceptance.items():
        for p0_id in criterion.p0s:
            requirement = p0s.get(p0_id)
            if requirement and acceptance_id not in requirement.acceptance:
                errors.append(
                    f"{definition_item_location(criterion.item)}: {acceptance_id} and {p0_id} links are not reciprocal"
                )
                if not set(criterion.journeys).intersection(requirement.journeys):
                    errors.append(
                        f"{definition_item_location(criterion.item)}: {acceptance_id} and {p0_id} do not share a journey link"
                    )

    singular_fields = (
        (1, "Project name", "project name"),
        (1, "Project purpose", "project purpose"),
        (2, "Problem", "problem"),
        (2, "Current alternative", "current alternative"),
        (3, "Primary user", "primary user"),
        (4, "Value proposition", "value proposition"),
        (4, "Solution boundary", "solution boundary"),
    )
    concrete_fields = singular_fields + (
        (7, "In scope", "in-scope boundary"),
        (7, "Out of scope", "out-of-scope boundary"),
        (8, "Success signal", "success signal"),
        (11, "Agent checkpoint", "agent checkpoint"),
        (12, "Read context", "repository read context"),
        (12, "Allowed writes", "repository allowed-write boundary"),
        (12, "Protected paths", "repository protected-path boundary"),
        (13, "Completion evidence", "completion evidence"),
        (14, "First verifiable slice", "first verifiable slice"),
        (14, "Dependency", "first-slice dependency"),
        (14, "Risk", "first-slice risk"),
    )
    for section_number, label, description in concrete_fields:
        values = definition_confirmed_values(document, section_number, label)
        if not any(definition_value_is_concrete(value) for value in values):
            errors.append(f"{DEFINITION_DRAFT}: missing concrete confirmed {description} ('{label}:')")

    for section_number, label, description in singular_fields:
        confirmed_count = 0
        proposed_count = 0
        for section in document.sections:
            for item in section.confirmed + section.proposed:
                count = definition_label_occurrences(item.text, label)
                if not count:
                    continue
                if section.number != section_number:
                    errors.append(
                        f"{definition_item_location(item)}: '{label}:' evidence belongs in section {section_number}"
                    )
                if count > 1:
                    errors.append(
                        f"{definition_item_location(item)}: duplicate singular '{label}:' label in one evidence item"
                    )
                if item.status == "confirmed":
                    confirmed_count += count
                elif item.status == "proposed":
                    proposed_count += count
        if confirmed_count > 1:
            errors.append(
                f"{DEFINITION_DRAFT}: multiple confirmed values for singular {description} ('{label}:')"
            )
        if confirmed_count and proposed_count:
            errors.append(
                f"{DEFINITION_DRAFT}: proposed alternative conflicts with confirmed singular {description} ('{label}:')"
            )

    slice_values = definition_confirmed_values(document, 14, "First verifiable slice")
    if len(slice_values) != 1:
        errors.append(f"{DEFINITION_DRAFT}: exactly one confirmed First verifiable slice is required")
    elif definition_value_is_concrete(slice_values[0]):
        slice_item = next(
            item
            for item in definition_section(document, 14).confirmed
            if item.text.casefold().startswith("first verifiable slice:")
        )
        slice_parts = [part.strip() for part in slice_item.text.split("|")]
        if not (
            len(slice_parts) == 4
            and definition_part_has_label(slice_parts[1], "P0")
            and definition_part_has_label(slice_parts[2], "Journey")
            and definition_part_has_label(slice_parts[3], "Acceptance")
        ):
            errors.append(
                f"{definition_item_location(slice_item)}: first slice must use "
                "'First verifiable slice: description | P0: REQ-P0-* | Journey: JRN-* | Acceptance: AC-*' form"
            )
        slice_description = slice_values[0].split("|", 1)[0].strip()
        if not definition_value_is_concrete(slice_description):
            errors.append(
                f"{definition_item_location(slice_item)}: first slice is missing a concrete description"
            )
        slice_p0s = definition_field_ids(slice_item.text, "P0", "p0", errors, slice_item)
        slice_journeys = definition_field_ids(slice_item.text, "Journey", "journey", errors, slice_item)
        slice_acceptance = definition_field_ids(slice_item.text, "Acceptance", "acceptance", errors, slice_item)
        if len(slice_p0s) != 1:
            errors.append(f"{definition_item_location(slice_item)}: first slice must reference exactly one P0")
        if len(slice_journeys) != 1:
            errors.append(f"{definition_item_location(slice_item)}: first slice must reference exactly one journey")
        if not slice_acceptance:
            errors.append(f"{definition_item_location(slice_item)}: first slice must reference at least one acceptance criterion")
        for identifier in slice_p0s:
            if identifier not in confirmed_p0s:
                errors.append(f"{definition_item_location(slice_item)}: first slice references unknown or proposed P0 {identifier}")
        for identifier in slice_journeys:
            if identifier not in confirmed_journeys:
                errors.append(
                    f"{definition_item_location(slice_item)}: first slice references unknown or proposed journey {identifier}"
                )
        for identifier in slice_acceptance:
            if identifier not in confirmed_acceptance:
                errors.append(
                    f"{definition_item_location(slice_item)}: first slice references unknown or proposed acceptance {identifier}"
                )
        if len(slice_p0s) == 1 and len(slice_journeys) == 1:
            selected_p0_id = slice_p0s[0]
            selected_journey_id = slice_journeys[0]
            selected_p0 = p0s.get(selected_p0_id)
            if selected_p0:
                if selected_journey_id not in selected_p0.journeys:
                    errors.append(
                        f"{definition_item_location(slice_item)}: first slice P0 {selected_p0_id} "
                        f"does not reference selected journey {selected_journey_id}"
                    )
                for acceptance_id in slice_acceptance:
                    if acceptance_id not in selected_p0.acceptance:
                        errors.append(
                            f"{definition_item_location(slice_item)}: first slice P0 {selected_p0_id} "
                            f"does not reference selected acceptance {acceptance_id}"
                        )
                    criterion = acceptance.get(acceptance_id)
                    if not criterion:
                        continue
                    if selected_p0_id not in criterion.p0s:
                        errors.append(
                            f"{definition_item_location(slice_item)}: first slice acceptance {acceptance_id} "
                            f"does not reference selected P0 {selected_p0_id}"
                        )
                    if selected_journey_id not in criterion.journeys:
                        errors.append(
                            f"{definition_item_location(slice_item)}: first slice acceptance {acceptance_id} "
                            f"does not reference selected journey {selected_journey_id}"
                        )
    return errors, declarations


def raise_definition_errors(errors: Sequence[str], action: str) -> None:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    raise HarnessError(f"definition {action} failed with {len(errors)} error(s)")


def definition_progress(document: DefinitionDocument) -> tuple[list[DefinitionSection], DefinitionSection | None, str]:
    confirmed = [section for section in document.sections if section.is_confirmed]
    next_section = next((section for section in document.sections if not section.is_confirmed), None)
    if next_section:
        continuation = (
            f"Resume at {next_section.number}. {next_section.title}; preserve confirmed evidence and resolve blocking Open items."
        )
    else:
        continuation = "All sections have confirmed evidence; run ./dev/define validate."
    return confirmed, next_section, continuation


def refresh_definition_metadata(document: DefinitionDocument) -> DefinitionDocument:
    confirmed, next_section, continuation = definition_progress(document)
    next_value = f"{next_section.number}. {next_section.title}" if next_section else "complete"
    updated = update_frontmatter(
        document.text,
        {
            "updated": date.today().isoformat(),
            "progress": json.dumps(f"{len(confirmed)}/{len(DEFINITION_SECTIONS)}"),
            "next": json.dumps(next_value),
            "continuation": json.dumps(continuation),
        },
    )
    if updated != document.text:
        ensure_safe_repository_path(document.path)
        document.path.write_text(updated, encoding="utf-8")
        document = parse_definition_document()
    return document


def heading_present(text: str, heading: str) -> bool:
    return re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE) is not None


def section_text(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        return ""
    tail = text[match.end() :]
    boundary = re.search(r"^##\s+", tail, re.MULTILINE)
    return tail[: boundary.start() if boundary else len(tail)].strip()


def normalize_link_target(raw_target: str) -> str:
    target = raw_target.strip().split("#", 1)[0].split("?", 1)[0]
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return target


def is_historical_plan(path: Path) -> bool:
    try:
        path.relative_to(ROOT / "docs" / "exec-plans" / "completed")
        return True
    except ValueError:
        return False


def check_links(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    historical = is_historical_plan(path)
    for raw_target in MARKDOWN_LINK.findall(text):
        target = normalize_link_target(raw_target)
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if historical:
            suffix = Path(target).suffix.lower()
            is_document_reference = suffix in {".md", ".txt"} or target.startswith(("/docs/", "docs/"))
            if not is_document_reference:
                continue
        candidate = (ROOT / target.lstrip("/")) if target.startswith("/") else (path.parent / target)
        candidate = candidate.resolve()
        try:
            candidate.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {raw_target}")
            continue
        if not candidate.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing link target: {raw_target}")


def optional_metadata_list(metadata: dict[str, object], field: str) -> tuple[str, ...]:
    value = metadata.get(field, [])
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped or stripped == "[]":
            return ()
        return (stripped,)
    if isinstance(value, list):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return ()


def durable_documents(
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
) -> list[DurableDocument]:
    sink = errors if errors is not None else []
    warning_sink = warnings if warnings is not None else []
    documents: list[DurableDocument] = []
    seen_ids: dict[str, Path] = {}
    for directory, expected_kind in CATALOG_AREAS.items():
        base = ROOT / "docs" / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name in {"README.md", "index.md", "_template.md"} or path.relative_to(ROOT) == DEFINITION_DRAFT:
                continue
            metadata, _, text = read_frontmatter(path)
            if not metadata:
                relative = path.relative_to(ROOT)
                if text.lstrip().startswith("---"):
                    sink.append(f"{relative}: malformed frontmatter for explicit authority document")
                else:
                    warning_sink.append(
                        f"{relative}: no frontmatter; excluded from authority"
                    )
                continue
            required = ("id", "kind", "status", "area", "summary")
            missing = [name for name in required if not str(metadata.get(name, "")).strip()]
            if missing:
                sink.append(f"{path.relative_to(ROOT)}: missing frontmatter fields: {', '.join(missing)}")
                continue
            doc_id = str(metadata["id"])
            kind = str(metadata["kind"])
            status = str(metadata["status"]).lower()
            if kind != expected_kind:
                sink.append(f"{path.relative_to(ROOT)}: kind must be '{expected_kind}', got '{kind}'")
            if status not in VALID_STATUSES.get(kind, set()):
                sink.append(f"{path.relative_to(ROOT)}: invalid status '{status}' for kind '{kind}'")
            if doc_id in seen_ids:
                sink.append(
                    f"{path.relative_to(ROOT)}: duplicate authority id '{doc_id}' also used by "
                    f"{seen_ids[doc_id].relative_to(ROOT)}"
                )
            else:
                seen_ids[doc_id] = path
            applies = metadata.get("applies_to", [])
            if isinstance(applies, str):
                applies_list = (applies,)
            elif isinstance(applies, list):
                applies_list = tuple(str(item) for item in applies)
            else:
                applies_list = ()
            documents.append(
                DurableDocument(
                    path=path,
                    id=doc_id,
                    kind=kind,
                    status=status,
                    area=str(metadata["area"]),
                    summary=str(metadata["summary"]),
                    applies_to=applies_list,
                    supersedes=optional_metadata_list(metadata, "supersedes"),
                    superseded_by=optional_metadata_list(metadata, "superseded_by"),
                )
            )
    return documents


def core_context_documents(errors: list[str]) -> list[DurableDocument]:
    documents: list[DurableDocument] = []
    for relative in CONTEXT_CORE_DOCUMENTS:
        path = ROOT / relative
        ensure_safe_repository_path(path)
        if not path.exists():
            continue
        if not path.is_file():
            raise HarnessError(f"core authority path is not a regular file: {relative}")
        metadata, _, _ = read_frontmatter(path)
        required = ("id", "kind", "status", "area", "summary")
        missing = [name for name in required if not str(metadata.get(name, "")).strip()]
        if missing:
            errors.append(f"{relative}: missing frontmatter fields: {', '.join(missing)}")
            continue
        status = str(metadata["status"]).lower()
        if status not in {"draft", "active"}:
            errors.append(f"{relative}: current-state status must be 'draft' or 'active'")
        documents.append(
            DurableDocument(
                path=path,
                id=str(metadata["id"]),
                kind=str(metadata["kind"]),
                status=status,
                area=str(metadata["area"]),
                summary=str(metadata["summary"]),
                applies_to=optional_metadata_list(metadata, "applies_to"),
                supersedes=optional_metadata_list(metadata, "supersedes"),
                superseded_by=optional_metadata_list(metadata, "superseded_by"),
            )
        )
    return documents


def authority_conflict_errors(documents: Sequence[DurableDocument]) -> list[str]:
    errors: list[str] = []
    by_id: dict[str, DurableDocument] = {}
    duplicate_ids: set[str] = set()
    for document in documents:
        existing = by_id.get(document.id)
        if existing is not None:
            duplicate_ids.add(document.id)
            errors.append(
                f"{document.path.relative_to(ROOT)}: duplicate authority id '{document.id}' also used by "
                f"{existing.path.relative_to(ROOT)}"
            )
        else:
            by_id[document.id] = document
    for document in documents:
        if document.id in duplicate_ids:
            continue
        if document.status == "superseded":
            for replacement_id in document.superseded_by:
                replacement = by_id.get(replacement_id)
                if replacement is None:
                    errors.append(
                        f"{document.path.relative_to(ROOT)}: superseded_by references missing authority '{replacement_id}'"
                    )
                elif document.id not in replacement.supersedes:
                    errors.append(
                        f"{document.path.relative_to(ROOT)}: supersession mismatch; {replacement.path.relative_to(ROOT)} "
                        f"does not name '{document.id}' in supersedes"
                    )
        if document.status not in DEFAULT_AUTHORITY_STATUSES:
            continue
        for replaced_id in document.supersedes:
            replaced = by_id.get(replaced_id)
            if replaced is None:
                errors.append(
                    f"{document.path.relative_to(ROOT)}: supersedes references missing authority '{replaced_id}'"
                )
                continue
            if replaced.status != "superseded":
                errors.append(
                    f"{document.path.relative_to(ROOT)}: supersession mismatch; normative authority '{document.id}' "
                    f"cannot supersede {replaced.path.relative_to(ROOT)} while its status is '{replaced.status}'"
                )
            elif replaced.superseded_by and document.id not in replaced.superseded_by:
                errors.append(
                    f"{document.path.relative_to(ROOT)}: supersession mismatch; {replaced.path.relative_to(ROOT)} "
                    f"names different superseded_by authority"
                )
    return errors


def authority_in_context(
    document: DurableDocument,
    *,
    include_drafts: bool,
    include_history: bool,
) -> bool:
    if document.status in DEFAULT_AUTHORITY_STATUSES:
        return True
    if include_drafts and document.status in DRAFT_AUTHORITY_STATUSES:
        return True
    if include_history and document.status in HISTORICAL_AUTHORITY_STATUSES:
        return True
    return False


def metadata_string_list(
    metadata: dict[str, object],
    field: str,
    location: str,
    errors: list[str],
) -> tuple[str, ...]:
    value = metadata.get(field, [])
    if isinstance(value, str):
        values = (value.strip(),) if value.strip() else ()
    elif isinstance(value, list):
        values = tuple(str(item).strip() for item in value if str(item).strip())
    else:
        values = ()
    if not values:
        errors.append(f"{location}: missing non-empty '{field}' list")
    return values


def repository_scope(
    value: str,
    location: str,
    errors: list[str],
) -> str | None:
    raw = value.strip().strip("`")
    if raw in {".", "./"}:
        return "."
    while raw.startswith("./"):
        raw = raw[2:]
    path = PurePosixPath(raw)
    if (
        not raw
        or path.is_absolute()
        or "\\" in raw
        or "//" in raw
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        errors.append(f"{location}: repository path must be a safe relative POSIX path: {value}")
        return None
    return raw


def repository_scope_matches(path: str, scope: str) -> bool:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized or "."
    if scope == ".":
        return True
    if any(character in scope for character in "*?["):
        return fnmatch.fnmatch(normalized, scope)
    return normalized == scope or normalized.startswith(scope.rstrip("/") + "/")


def repository_scopes_related(left: str, right: str) -> bool:
    return repository_scope_matches(left, right) or repository_scope_matches(right, left)


def repository_scope_exists(scope: str) -> bool:
    if scope == ".":
        return True
    if any(character in scope for character in "*?["):
        return any(
            audit_symlink_component(path) is None
            for path in ROOT.glob(scope)
        )
    path = ROOT / scope
    return path.exists() and audit_symlink_component(path) is None


def confirmed_planned_paths(errors: list[str]) -> list[PlannedPath]:
    planned: list[PlannedPath] = []
    base = ROOT / "docs" / "product-specs"
    if not base.exists():
        return planned
    for path in sorted(base.glob("*.md")):
        if path.name in {"README.md", "index.md", "_template.md"} or path.relative_to(ROOT) == DEFINITION_DRAFT:
            continue
        metadata, _, text = read_frontmatter(path)
        if str(metadata.get("kind", "")) != "product-spec" or str(metadata.get("status", "")).lower() != "active":
            continue
        spec_id = str(metadata.get("id", "")).strip()
        area = str(metadata.get("area", "")).strip()
        summary = str(metadata.get("summary", "")).strip()
        evidence_heading = ""
        for line_number, line in enumerate(text.splitlines(), start=1):
            heading = re.fullmatch(r"(#{1,6})\s+(.+?)\s*", line)
            if heading:
                level = len(heading.group(1))
                if level <= 2:
                    evidence_heading = ""
                elif level == 3:
                    evidence_heading = heading.group(2).strip().casefold()
                continue
            match = CONFIRMED_PLANNED_PATH.fullmatch(line)
            if not match or evidence_heading != "confirmed":
                continue
            location = trace_location(path, line_number)
            normalized = repository_scope(match.group(1), location, errors)
            if normalized is not None:
                planned.append(
                    PlannedPath(
                        path=normalized,
                        spec_id=spec_id,
                        area=area,
                        summary=summary,
                    )
                )
    return planned


def contract_value(
    metadata: dict[str, object],
    field: str,
    location: str,
    errors: list[str],
) -> str:
    value = str(metadata.get(field, "")).strip()
    if not value:
        errors.append(f"{location}: missing frontmatter field '{field}'")
    elif re.search(r"\b(?:TODO|TBD)\b", value, re.IGNORECASE) or DEFINITION_TEMPLATE_TOKEN.search(value):
        errors.append(f"{location}: unresolved placeholder in '{field}'")
    return value


def module_contracts(
    config: Config,
    planned: Sequence[PlannedPath],
    errors: list[str],
) -> list[ModuleContract]:
    contracts: list[ModuleContract] = []
    seen_ids: dict[str, Path] = {}
    base = ROOT / MODULE_CONTRACTS_DIR
    if not base.exists():
        return contracts
    explicit_paths: list[str] = []
    for field in ("source", "tests"):
        for value in config.list_value("paths", field):
            normalized = repository_scope(value, f"dev/harness.toml [paths].{field}", errors)
            if normalized is not None:
                explicit_paths.append(normalized)
    planned_paths = [item.path for item in planned]
    for path in sorted(base.glob("MOD-*.md")):
        location = str(path.relative_to(ROOT))
        before = len(errors)
        metadata, _, _ = read_frontmatter(path)
        contract_id = contract_value(metadata, "id", location, errors)
        kind = contract_value(metadata, "kind", location, errors)
        status = contract_value(metadata, "status", location, errors).lower()
        area = contract_value(metadata, "area", location, errors)
        summary = contract_value(metadata, "summary", location, errors)
        owner = contract_value(metadata, "owner", location, errors)
        responsibility = contract_value(metadata, "responsibility", location, errors)
        organization = contract_value(metadata, "organization", location, errors)
        applies_raw = metadata_string_list(metadata, "applies_to", location, errors)
        public_entry_points = metadata_string_list(metadata, "public_entry_points", location, errors)
        dependency_rules = metadata_string_list(metadata, "dependency_rules", location, errors)
        verification = metadata_string_list(metadata, "verification", location, errors)
        if MODULE_CONTRACT_ID.fullmatch(contract_id) is None:
            errors.append(f"{location}: id must match MOD-*")
        if kind != "module-contract":
            errors.append(f"{location}: kind must be 'module-contract'")
        if status not in {"draft", "active", "deprecated"}:
            errors.append(f"{location}: invalid module-contract status '{status}'")
        if contract_id and path.stem != contract_id and not path.stem.startswith(contract_id + "-"):
            errors.append(f"{location}: filename must begin with module contract id {contract_id}")
        if contract_id in seen_ids:
            errors.append(f"{location}: duplicate module contract id {contract_id} also used by {seen_ids[contract_id].relative_to(ROOT)}")
        elif contract_id:
            seen_ids[contract_id] = path
        applies_to: list[str] = []
        for value in applies_raw:
            normalized = repository_scope(value, f"{location} applies_to", errors)
            if normalized is not None:
                applies_to.append(normalized)
        for field, values in (
            ("public_entry_points", public_entry_points),
            ("dependency_rules", dependency_rules),
            ("verification", verification),
        ):
            for value in values:
                if re.search(r"\b(?:TODO|TBD)\b", value, re.IGNORECASE) or DEFINITION_TEMPLATE_TOKEN.search(value):
                    errors.append(f"{location}: unresolved placeholder in '{field}'")
        for scope in applies_to:
            supported = (
                repository_scope_exists(scope)
                or any(repository_scopes_related(scope, explicit) for explicit in explicit_paths)
                or any(repository_scopes_related(scope, item) for item in planned_paths)
            )
            if not supported:
                errors.append(
                    f"{location}: applies_to path '{scope}' lacks actual, configured, or confirmed-planned evidence"
                )
        if len(errors) != before:
            continue
        contracts.append(
            ModuleContract(
                path=path,
                id=contract_id,
                status=status,
                area=area,
                summary=summary,
                owner=owner,
                responsibility=responsibility,
                applies_to=tuple(applies_to),
                public_entry_points=public_entry_points,
                dependency_rules=dependency_rules,
                organization=organization,
                verification=verification,
            )
        )
    return contracts


def code_map_entries(
    config: Config,
    planned: Sequence[PlannedPath],
    contracts: Sequence[ModuleContract],
    errors: list[str],
) -> list[CodeMapEntry]:
    records: dict[str, dict[str, set[str]]] = {}

    def add(
        path: str,
        *,
        evidence: Sequence[str],
        area: str,
        source: str,
        description: str,
    ) -> None:
        record = records.setdefault(
            path,
            {"evidence": set(), "areas": set(), "sources": set(), "descriptions": set()},
        )
        record["evidence"].update(evidence)
        if area:
            record["areas"].add(area)
        if source:
            record["sources"].add(source)
        if description:
            record["descriptions"].add(description)

    configured: list[str] = []
    for field, area, description in (
        ("source", "source", "Configured source path"),
        ("tests", "test", "Configured test path"),
    ):
        for value in config.list_value("paths", field):
            normalized = repository_scope(value, f"dev/harness.toml [paths].{field}", errors)
            if normalized is None:
                continue
            configured.append(normalized)
            evidence = ["configured"]
            if repository_scope_exists(normalized):
                evidence.append("actual")
            add(
                normalized,
                evidence=evidence,
                area=area,
                source="dev/harness.toml",
                description=description,
            )

    for contract in contracts:
        if contract.status != "active":
            continue
        for scope in contract.applies_to:
            evidence = ["contract"]
            if repository_scope_exists(scope):
                evidence.append("actual")
            if any(repository_scopes_related(scope, item) for item in configured):
                evidence.append("configured")
            if any(repository_scopes_related(scope, item.path) for item in planned):
                evidence.append("confirmed-planned")
            add(
                scope,
                evidence=evidence,
                area=contract.area,
                source=contract.id,
                description=contract.summary,
            )

    for item in planned:
        evidence = ["confirmed-planned"]
        if repository_scope_exists(item.path):
            evidence.append("actual")
        add(
            item.path,
            evidence=evidence,
            area=item.area,
            source=item.spec_id,
            description=item.summary or "Confirmed planned path",
        )

    evidence_order = {"actual": 0, "configured": 1, "confirmed-planned": 2, "contract": 3}
    return [
        CodeMapEntry(
            path=path,
            evidence=tuple(sorted(record["evidence"], key=lambda value: (evidence_order.get(value, 99), value))),
            areas=tuple(sorted(record["areas"])),
            sources=tuple(sorted(record["sources"])),
            descriptions=tuple(sorted(record["descriptions"])),
        )
        for path, record in sorted(records.items())
    ]


def code_map_model(
    config: Config,
    errors: list[str],
) -> tuple[list[PlannedPath], list[ModuleContract], list[CodeMapEntry]]:
    planned = confirmed_planned_paths(errors)
    contracts = module_contracts(config, planned, errors)
    entries = code_map_entries(config, planned, contracts, errors)
    return planned, contracts, entries


def code_map_markdown(entries: Sequence[CodeMapEntry]) -> str:
    lines = [
        "# Repository Code Map",
        "",
        "Generated by `./dev/code-map` from explicit repository evidence. Do not edit this file manually.",
        "",
        "This map is non-authoritative. Source, configuration, confirmed product evidence, and module contracts remain the sources of truth.",
        "",
    ]
    if not entries:
        lines.append("- No evidence-backed paths.")
        return "\n".join(lines) + "\n"
    lines.extend(
        (
            "| Path | Evidence | Areas | Sources | Description |",
            "|---|---|---|---|---|",
        )
    )
    for entry in entries:
        values = (
            f"`{entry.path}`",
            ", ".join(entry.evidence),
            ", ".join(entry.areas) or "unknown",
            ", ".join(f"`{source}`" for source in entry.sources),
            "; ".join(entry.descriptions) or "unknown",
        )
        lines.append("| " + " | ".join(value.replace("|", "\\|") for value in values) + " |")
    return "\n".join(lines) + "\n"


def command_code_map(args: argparse.Namespace) -> int:
    config = load_config()
    errors: list[str] = []
    _, contracts, entries = code_map_model(config, errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise HarnessError(f"code map failed with {len(errors)} metadata error(s)")
    expected = code_map_markdown(entries)
    path = ROOT / CODE_MAP_PATH
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if args.check and current != expected:
        raise HarnessError("docs/generated/code-map.md is stale; run ./dev/code-map")
    if current != expected and not args.check:
        ensure_safe_repository_path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")
        print(f"Updated {CODE_MAP_PATH} ({len(entries)} path(s), {len(contracts)} module contract(s)).")
    else:
        print(f"Code map is current ({len(entries)} path(s), {len(contracts)} module contract(s)).")
    return 0


def relative_markdown_link(from_path: Path, to_path: Path) -> str:
    return os.path.relpath(to_path, from_path.parent).replace(os.sep, "/")


CATALOG_LABELS = {
    "product-spec": "Product specifications",
    "design-doc": "Design documents",
    "decision": "Decisions",
    "runbook": "Runbooks",
}


def catalog_markdown(
    documents: Sequence[DurableDocument],
    *,
    from_path: Path,
    kinds: Sequence[str],
    grouped: bool,
) -> str:
    lines = [CATALOG_START, "", "Generated by `./dev/docs-index`. Do not edit this block manually."]
    for kind in kinds:
        matching = sorted((doc for doc in documents if doc.kind == kind), key=lambda doc: (doc.area, doc.id))
        if grouped:
            lines.extend(("", f"### {CATALOG_LABELS[kind]}", ""))
        else:
            lines.append("")
        if not matching:
            lines.append("- None.")
            continue
        lines.extend(("| ID | Status | Area | Summary | Document |", "|---|---|---|---|---|"))
        for doc in matching:
            link = relative_markdown_link(from_path, doc.path)
            summary = doc.summary.replace("|", "\\|")
            lines.append(f"| `{doc.id}` | {doc.status} | {doc.area} | {summary} | [`{doc.path.name}`]({link}) |")
    lines.extend(("", CATALOG_END))
    return "\n".join(lines)


def replace_catalog(text: str, block: str, *, path: Path) -> str:
    try:
        span = audit_managed_block_span(text, CATALOG_START, CATALOG_END)
    except HarnessError as exc:
        raise HarnessError(
            f"{path.relative_to(ROOT)} is missing or has malformed reporivet catalog markers"
        ) from exc
    if span is None:
        raise HarnessError(f"{path.relative_to(ROOT)} is missing or has malformed reporivet catalog markers")
    return text[: span[0]] + block.rstrip() + text[span[1] :]


def catalog_targets() -> list[tuple[Path, tuple[str, ...], bool]]:
    return [
        (ROOT / "docs" / "README.md", tuple(CATALOG_LABELS), True),
        (ROOT / "docs" / "product-specs" / "index.md", ("product-spec",), False),
        (ROOT / "docs" / "design-docs" / "index.md", ("design-doc",), False),
        (ROOT / "docs" / "decisions" / "README.md", ("decision",), False),
        (ROOT / "docs" / "runbooks" / "index.md", ("runbook",), False),
    ]


def expected_catalog_text(path: Path, documents: Sequence[DurableDocument], kinds: Sequence[str], grouped: bool) -> str:
    if not path.exists():
        raise HarnessError(f"missing catalog target: {path.relative_to(ROOT)}")
    original = path.read_bytes().decode("utf-8")
    block = catalog_markdown(documents, from_path=path, kinds=kinds, grouped=grouped)
    return replace_catalog(original, block, path=path)


def command_docs_index(
    args: argparse.Namespace,
    *,
    transaction_records: Sequence[tuple[Path, RuntimePathImage, RuntimePathImage]] | None = None,
) -> int:
    errors: list[str] = []
    documents = durable_documents(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise HarnessError(f"cannot build document catalog with {len(errors)} metadata error(s)")
    changed: list[Path] = []
    guarded = {path: (before, after) for path, before, after in transaction_records or ()}
    for path, kinds, grouped in catalog_targets():
        if transaction_records is not None:
            preimage, postimage = guarded[path]
            if not runtime_image_matches(path, preimage):
                raise HarnessError(f"preimage changed before write: {path.relative_to(ROOT)}")
            if postimage != preimage:
                changed.append(path)
                if not args.check:
                    restore_runtime_file(path, preimage, postimage)
            continue
        original = path.read_bytes().decode("utf-8") if path.exists() else ""
        updated = expected_catalog_text(path, documents, kinds, grouped)
        if updated != original:
            changed.append(path)
            if not args.check:
                path.write_bytes(updated.encode("utf-8"))
    if args.check and changed:
        names = ", ".join(str(path.relative_to(ROOT)) for path in changed)
        raise HarnessError(f"document catalogs are stale: {names}; run ./dev/docs-index and commit the result")
    if changed:
        print(f"Updated {len(changed)} document catalog(s) ({len(documents)} durable document(s)).")
    else:
        print(f"Document catalogs are current ({len(documents)} durable document(s)).")
    return 0

def plan_files() -> list[Plan]:
    plans: list[Plan] = []
    for directory in (ROOT / "docs" / "exec-plans" / "active", ROOT / "docs" / "exec-plans" / "completed"):
        ensure_safe_repository_path(directory)
        if not directory.exists():
            continue
        if not directory.is_dir():
            raise HarnessError(
                f"plan directory is not a regular directory: {directory.relative_to(ROOT)}"
            )
        for path in sorted(directory.glob("*.md")):
            ensure_safe_repository_path(path)
            if not path.is_file():
                raise HarnessError(
                    f"plan entry is not a regular file: {path.relative_to(ROOT)}"
                )
            try:
                metadata, _, text = read_frontmatter(path)
            except UnicodeError as exc:
                raise HarnessError(
                    f"plan file is not valid UTF-8: {path.relative_to(ROOT)}"
                ) from exc
            except OSError as exc:
                raise HarnessError(
                    f"cannot read plan file: {path.relative_to(ROOT)}"
                ) from exc
            plans.append(Plan(path=path, metadata=metadata, text=text))
    return plans


def locate_plan(reference: str, *, active_only: bool = False) -> Plan:
    candidates = []
    for plan in plan_files():
        if active_only and "active" not in plan.path.relative_to(ROOT).parts:
            continue
        if reference in {plan.id, plan.path.name, plan.path.stem} or reference.lower() in plan.path.name.lower():
            candidates.append(plan)
    if not candidates:
        raise HarnessError(f"plan not found: {reference}")
    if len(candidates) > 1:
        names = ", ".join(str(plan.path.relative_to(ROOT)) for plan in candidates)
        raise HarnessError(f"plan reference is ambiguous: {reference} ({names})")
    return candidates[0]


def task_field(block: str, label: str) -> str | None:
    heading = re.search(rf"^####\s+{re.escape(label)}\s*$", block, re.MULTILINE | re.IGNORECASE)
    if heading:
        tail = block[heading.end() :]
        boundary = re.search(r"^####\s+|^###\s+|^##\s+", tail, re.MULTILINE)
        return tail[: boundary.start() if boundary else len(tail)].strip()
    legacy = re.search(rf"^\*\*{re.escape(label)}:\*\*\s*(.*)$", block, re.MULTILINE | re.IGNORECASE)
    return legacy.group(1).strip() if legacy else None


def traceability_enabled(plan: Plan) -> bool:
    return str(plan.metadata.get("traceability", "")).strip() == "1"


def trace_location(path: Path, line: int | None = None) -> str:
    location = str(path.relative_to(ROOT))
    return f"{location}:{line}" if line is not None else location


def trace_field_ids(
    value: str,
    label: str,
    kind: str,
    location: str,
    errors: list[str],
) -> tuple[str, ...]:
    matches = list(re.finditer(rf"(?:^|\|)\s*{re.escape(label)}:\s*([^|]+)", value, re.IGNORECASE))
    if not matches:
        errors.append(f"{location}: missing '{label}:' link field")
        return ()
    if len(matches) > 1:
        errors.append(f"{location}: duplicate '{label}:' link field")
    raw_ids = matches[0].group(1).strip()
    pattern = DEFINITION_ID_PATTERNS[kind]
    identifiers = tuple(pattern.findall(raw_ids))
    residue = pattern.sub("", raw_ids)
    if re.sub(r"[\s`,/]+", "", residue):
        errors.append(f"{location}: malformed '{label}:' links")
    if len(set(identifiers)) != len(identifiers):
        errors.append(f"{location}: duplicate identifier in '{label}:' links")
    return identifiers


def product_spec_for_plan(plan: Plan, errors: list[str]) -> Path | None:
    relative = plan.path.relative_to(ROOT)
    reference = str(plan.metadata.get("product_spec", "")).strip()
    if not reference:
        errors.append(f"{relative}: traceability plan is missing product_spec")
        return None
    matches: list[Path] = []
    base = ROOT / "docs" / "product-specs"
    if base.exists():
        for path in sorted(base.glob("*.md")):
            if path.name in {"README.md", "index.md", "_template.md"} or path.relative_to(ROOT) == DEFINITION_DRAFT:
                continue
            metadata, _, _ = read_frontmatter(path)
            if str(metadata.get("id", "")).strip() == reference:
                matches.append(path)
    if not matches:
        errors.append(f"{relative}: product_spec '{reference}' was not found")
        return None
    if len(matches) > 1:
        names = ", ".join(str(path.relative_to(ROOT)) for path in matches)
        errors.append(f"{relative}: product_spec '{reference}' is duplicated ({names})")
        return None
    path = matches[0]
    metadata, _, _ = read_frontmatter(path)
    if str(metadata.get("kind", "")) != "product-spec":
        errors.append(f"{trace_location(path)}: kind must be 'product-spec'")
    if str(metadata.get("status", "")).lower() != "active":
        errors.append(f"{trace_location(path)}: traceable product spec must have status 'active'")
    return path


def product_declarations(path: Path, errors: list[str]) -> dict[str, ProductDeclaration]:
    text = path.read_text(encoding="utf-8")
    declaration_pattern = re.compile(r"^(JRN-[0-9]+|REQ-P0-[0-9]+|AC-[0-9]+)\s*\|\s*(.+)$")
    evidence_heading = ""
    seen: dict[str, int] = {}
    declarations: dict[str, ProductDeclaration] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        heading = re.fullmatch(r"###\s+(.+?)\s*", raw_line)
        if heading:
            evidence_heading = heading.group(1).strip().casefold()
            continue
        item = re.fullmatch(r"\s*-\s+\[([A-Za-z][A-Za-z-]*)\]\s+(.+?)\s*", raw_line)
        if not item:
            continue
        status = item.group(1).casefold()
        payload = item.group(2).strip()
        match = declaration_pattern.fullmatch(payload)
        if not match:
            continue
        identifier = match.group(1)
        location = trace_location(path, line_number)
        if identifier in seen:
            errors.append(f"{location}: duplicate identifier {identifier}; first declared at line {seen[identifier]}")
            continue
        seen[identifier] = line_number
        if status != "confirmed" or evidence_heading != "confirmed":
            continue
        kind = definition_identifier_kind(identifier)
        assert kind is not None
        parts = [part.strip() for part in payload.split("|")]
        valid_shape = False
        expected = ""
        if kind == "journey":
            valid_shape = len(parts) == 2
            expected = "JRN-* | description"
        elif kind == "p0":
            valid_shape = (
                len(parts) == 4
                and definition_part_has_label(parts[1], "Journey")
                and definition_part_has_label(parts[2], "Acceptance")
            )
            expected = "REQ-P0-* | Journey: JRN-* | Acceptance: AC-* | description"
        elif kind == "acceptance":
            valid_shape = (
                len(parts) == 4
                and definition_part_has_label(parts[1], "P0")
                and definition_part_has_label(parts[2], "Journey")
            )
            expected = "AC-* | P0: REQ-P0-* | Journey: JRN-* | observable criterion"
        if not valid_shape:
            errors.append(f"{location}: {identifier} declaration must use '{expected}' form")
        journeys: tuple[str, ...] = ()
        p0s: tuple[str, ...] = ()
        acceptance: tuple[str, ...] = ()
        if kind == "p0":
            journeys = trace_field_ids(payload, "Journey", "journey", location, errors)
            acceptance = trace_field_ids(payload, "Acceptance", "acceptance", location, errors)
        elif kind == "acceptance":
            p0s = trace_field_ids(payload, "P0", "p0", location, errors)
            journeys = trace_field_ids(payload, "Journey", "journey", location, errors)
        description = definition_description(payload)
        if not definition_value_is_concrete(description):
            errors.append(f"{location}: {identifier} is missing a concrete description")
        declarations[identifier] = ProductDeclaration(
            id=identifier,
            kind=kind,
            line=line_number,
            description=description,
            journeys=journeys,
            p0s=p0s,
            acceptance=acceptance,
        )

    journeys = {identifier: item for identifier, item in declarations.items() if item.kind == "journey"}
    p0s = {identifier: item for identifier, item in declarations.items() if item.kind == "p0"}
    acceptance = {identifier: item for identifier, item in declarations.items() if item.kind == "acceptance"}
    for kind, values in (("JRN-*", journeys), ("REQ-P0-*", p0s), ("AC-*", acceptance)):
        if not values:
            errors.append(f"{trace_location(path)}: at least one confirmed {kind} declaration is required")

    for identifier, requirement in p0s.items():
        location = trace_location(path, requirement.line)
        for journey in requirement.journeys:
            if journey not in journeys:
                errors.append(f"{location}: {identifier} references unknown or unconfirmed journey {journey}")
        for criterion in requirement.acceptance:
            if criterion not in acceptance:
                errors.append(f"{location}: {identifier} references unknown or unconfirmed acceptance {criterion}")
    for identifier, criterion in acceptance.items():
        location = trace_location(path, criterion.line)
        for p0 in criterion.p0s:
            if p0 not in p0s:
                errors.append(f"{location}: {identifier} references unknown or unconfirmed P0 {p0}")
        for journey in criterion.journeys:
            if journey not in journeys:
                errors.append(f"{location}: {identifier} references unknown or unconfirmed journey {journey}")
    for p0_id, requirement in p0s.items():
        location = trace_location(path, requirement.line)
        for acceptance_id in requirement.acceptance:
            criterion = acceptance.get(acceptance_id)
            if criterion is None:
                continue
            if p0_id not in criterion.p0s:
                errors.append(f"{location}: {p0_id} and {acceptance_id} links are not reciprocal")
            if not set(requirement.journeys).intersection(criterion.journeys):
                errors.append(f"{location}: {p0_id} and {acceptance_id} do not share a journey link")
    for acceptance_id, criterion in acceptance.items():
        location = trace_location(path, criterion.line)
        for p0_id in criterion.p0s:
            requirement = p0s.get(p0_id)
            if requirement is None:
                continue
            if acceptance_id not in requirement.acceptance:
                errors.append(f"{location}: {acceptance_id} and {p0_id} links are not reciprocal")
            if not set(criterion.journeys).intersection(requirement.journeys):
                errors.append(f"{location}: {acceptance_id} and {p0_id} do not share a journey link")
    return declarations


def plan_table_rows(
    plan: Plan,
    heading: str,
    headers: Sequence[str],
    errors: list[str],
) -> list[tuple[str, ...]]:
    relative = plan.path.relative_to(ROOT)
    section = section_text(plan.text, heading)
    lines: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            lines.append(stripped)
        elif lines:
            break
    if len(lines) < 2:
        errors.append(f"{relative}: section '## {heading}' is missing its table")
        return []
    parsed = [tuple(cell.strip() for cell in line.strip().strip("|").split("|")) for line in lines]
    if tuple(cell.casefold() for cell in parsed[0]) != tuple(header.casefold() for header in headers):
        errors.append(f"{relative}: section '## {heading}' has an invalid table header")
        return []
    if len(parsed[1]) != len(headers) or any(re.fullmatch(r":?-{3,}:?", cell) is None for cell in parsed[1]):
        errors.append(f"{relative}: section '## {heading}' has an invalid table delimiter")
        return []
    rows: list[tuple[str, ...]] = []
    for row_number, row in enumerate(parsed[2:], start=1):
        if len(row) != len(headers):
            errors.append(f"{relative}: section '## {heading}' row {row_number} has {len(row)} cells; expected {len(headers)}")
            continue
        rows.append(row)
    if not rows:
        errors.append(f"{relative}: section '## {heading}' has no data rows")
    return rows


def trace_cell_ids(
    value: str,
    pattern: re.Pattern[str],
    label: str,
    location: str,
    errors: list[str],
    *,
    exactly_one: bool = False,
) -> tuple[str, ...]:
    identifiers = tuple(pattern.findall(value))
    residue = pattern.sub("", value)
    if re.sub(r"[\s`,/]+", "", residue):
        errors.append(f"{location}: malformed {label} cell '{value}'")
    if not identifiers:
        errors.append(f"{location}: missing {label}")
    elif exactly_one and len(identifiers) != 1:
        errors.append(f"{location}: {label} must contain exactly one identifier")
    if len(set(identifiers)) != len(identifiers):
        errors.append(f"{location}: duplicate {label} identifier")
    return identifiers


def trace_task_blocks(plan: Plan) -> dict[str, str]:
    matches = list(TASK_HEADING.finditer(plan.text))
    return {
        match.group(1): plan.text[
            match.end() : matches[index + 1].start() if index + 1 < len(matches) else len(plan.text)
        ]
        for index, match in enumerate(matches)
    }


def safe_evidence_path(value: str, run_id: str) -> bool:
    target = value.strip().strip("`")
    link = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", target)
    if link:
        target = normalize_link_target(link.group(1))
    else:
        target = normalize_link_target(target)
    raw_parts = target.split("/")
    path = PurePosixPath(target)
    return (
        bool(target)
        and not path.is_absolute()
        and "\\" not in target
        and all(part not in {"", ".", ".."} for part in raw_parts)
        and len(path.parts) >= 4
        and path.parts[:2] == (".harness", "runs")
        and path.parts[2] == run_id
    )


def validate_completed_traceability(
    plan: Plan,
    errors: list[str],
    traced_acceptance: set[str],
    known_acceptance: set[str],
    task_acceptance: dict[str, set[str]],
) -> None:
    relative = plan.path.relative_to(ROOT)
    run_id = str(plan.metadata.get("verification_run", "")).strip()
    manifest_sha = str(plan.metadata.get("manifest_sha256", "")).strip()
    verified_commit = str(plan.metadata.get("verified_commit", "")).strip()
    verdict = str(plan.metadata.get("gate_verdict", "")).strip().upper()
    review_reason = str(plan.metadata.get("gate_review_reason", "")).strip()
    if not run_id:
        errors.append(f"{relative}: complete traceable plan is missing verification_run")
    elif re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id) is None:
        errors.append(f"{relative}: verification_run is not a valid run ID")
    if re.fullmatch(r"[0-9a-fA-F]{64}", manifest_sha) is None:
        errors.append(f"{relative}: manifest_sha256 must be a 64-character SHA-256")
    if verdict not in {"PASS", "REVIEW"}:
        errors.append(f"{relative}: complete traceable plan gate_verdict must be PASS or REVIEW")
    if verdict == "REVIEW" and not definition_value_is_concrete(review_reason):
        errors.append(f"{relative}: REVIEW gate verdict requires gate_review_reason")

    rows = plan_table_rows(plan, "Validation and Evidence", ACCEPTANCE_EVIDENCE_HEADERS, errors)
    evidenced: set[str] = set()
    task_pattern = re.compile(r"T[0-9A-Za-z_-]+")
    for row_number, row in enumerate(rows, start=1):
        location = f"{relative}: Validation and Evidence row {row_number}"
        criterion_ids = trace_cell_ids(
            row[0], DEFINITION_ID_PATTERNS["acceptance"], "acceptance criterion", location, errors, exactly_one=True
        )
        criterion = criterion_ids[0] if len(criterion_ids) == 1 else ""
        if criterion:
            if criterion not in known_acceptance:
                errors.append(f"{location}: unknown acceptance criterion {criterion}")
            if criterion not in traced_acceptance:
                errors.append(f"{location}: acceptance criterion {criterion} is not in Product Trace")
            if criterion in evidenced:
                errors.append(f"{location}: duplicate evidence row for {criterion}")
            evidenced.add(criterion)
        task_ids = trace_cell_ids(row[1], task_pattern, "task", location, errors)
        for task_id in task_ids:
            if task_id not in task_acceptance:
                errors.append(f"{location}: unknown evidence task {task_id}")
            elif criterion and criterion not in task_acceptance[task_id]:
                errors.append(f"{location}: task {task_id} does not accept {criterion}")
        if run_id and not safe_evidence_path(row[2], run_id):
            errors.append(f"{location}: evidence path must stay beneath .harness/runs/{run_id}/")
        if row[3].strip().strip("`") != run_id:
            errors.append(f"{location}: Run ID does not match verification_run")
        if row[4].strip().strip("`").lower() != manifest_sha.lower():
            errors.append(f"{location}: Manifest SHA-256 does not match manifest_sha256")
        if row[5].strip().strip("`").lower() != verified_commit.lower():
            errors.append(f"{location}: Verified commit does not match verified_commit")
        if row[6].strip().strip("`").upper() != verdict:
            errors.append(f"{location}: Gate verdict does not match gate_verdict")
        row_reason = row[7].strip().strip("`")
        if verdict == "REVIEW" and row_reason != review_reason:
            errors.append(f"{location}: Review reason does not match gate_review_reason")
    for criterion in sorted(traced_acceptance - evidenced):
        errors.append(f"{relative}: complete traceable plan has no evidence row for {criterion}")


def validate_traceable_plan(plan: Plan, errors: list[str]) -> None:
    if not traceability_enabled(plan):
        return
    relative = plan.path.relative_to(ROOT)
    if not heading_present(plan.text, "Product Trace"):
        errors.append(f"{relative}: traceability plan is missing section '## Product Trace'")
    spec_path = product_spec_for_plan(plan, errors)
    declarations = product_declarations(spec_path, errors) if spec_path else {}
    known_journeys = {identifier for identifier, item in declarations.items() if item.kind == "journey"}
    known_p0s = {identifier for identifier, item in declarations.items() if item.kind == "p0"}
    known_acceptance = {identifier for identifier, item in declarations.items() if item.kind == "acceptance"}
    reference = str(plan.metadata.get("product_spec", "")).strip()

    blocks = trace_task_blocks(plan)
    task_acceptance: dict[str, set[str]] = {}
    for task_id, block in blocks.items():
        location = f"{relative} {task_id}"
        task_type_value = task_field(block, "Task type")
        task_type = task_type_value.splitlines()[0].strip().lower() if task_type_value else ""
        if not task_type:
            errors.append(f"{location}: traceability task is missing 'Task type' field")
        acceptance_value = task_field(block, "Acceptance") or ""
        acceptance_ids = set(DEFINITION_ID_PATTERNS["acceptance"].findall(acceptance_value))
        task_acceptance[task_id] = acceptance_ids
        for criterion in acceptance_ids:
            if criterion not in known_acceptance:
                errors.append(f"{location}: Acceptance references unknown criterion {criterion}")
        if task_type in {"implementation", "verification"}:
            trace_cell_ids(
                acceptance_value,
                DEFINITION_ID_PATTERNS["acceptance"],
                "known acceptance criterion",
                location,
                errors,
            )

    rows = plan_table_rows(plan, "Product Trace", PRODUCT_TRACE_HEADERS, errors)
    traced_acceptance: set[str] = set()
    task_pattern = re.compile(r"T[0-9A-Za-z_-]+")
    for row_number, row in enumerate(rows, start=1):
        location = f"{relative}: Product Trace row {row_number}"
        row_spec = row[0].strip().strip("`")
        if row_spec != reference:
            errors.append(f"{location}: Product spec '{row_spec}' does not match product_spec '{reference}'")
        journey_ids = trace_cell_ids(
            row[1], DEFINITION_ID_PATTERNS["journey"], "journey", location, errors, exactly_one=True
        )
        p0_ids = trace_cell_ids(row[2], DEFINITION_ID_PATTERNS["p0"], "P0 requirement", location, errors, exactly_one=True)
        acceptance_ids = trace_cell_ids(
            row[3], DEFINITION_ID_PATTERNS["acceptance"], "acceptance criterion", location, errors
        )
        implementation_tasks = trace_cell_ids(row[4], task_pattern, "implementation task", location, errors)
        verification_tasks = trace_cell_ids(row[5], task_pattern, "verification task", location, errors)
        for identifier in journey_ids:
            if identifier not in known_journeys:
                errors.append(f"{location}: unknown journey {identifier}")
        for identifier in p0_ids:
            if identifier not in known_p0s:
                errors.append(f"{location}: unknown P0 requirement {identifier}")
        for identifier in acceptance_ids:
            if identifier not in known_acceptance:
                errors.append(f"{location}: unknown acceptance criterion {identifier}")
            if identifier in traced_acceptance:
                errors.append(f"{location}: duplicate Product Trace acceptance criterion {identifier}")
            traced_acceptance.add(identifier)
        if len(journey_ids) == 1 and len(p0_ids) == 1:
            journey_id = journey_ids[0]
            p0_id = p0_ids[0]
            requirement = declarations.get(p0_id)
            if requirement and journey_id not in requirement.journeys:
                errors.append(f"{location}: {p0_id} does not reference {journey_id}")
            for criterion_id in acceptance_ids:
                criterion = declarations.get(criterion_id)
                if requirement and criterion_id not in requirement.acceptance:
                    errors.append(f"{location}: {p0_id} does not reference {criterion_id}")
                if criterion and p0_id not in criterion.p0s:
                    errors.append(f"{location}: {criterion_id} does not reference {p0_id}")
                if criterion and journey_id not in criterion.journeys:
                    errors.append(f"{location}: {criterion_id} does not reference {journey_id}")
        for task_id in implementation_tasks + verification_tasks:
            if task_id not in blocks:
                errors.append(f"{location}: unknown task {task_id}")
                continue
            for criterion_id in acceptance_ids:
                if criterion_id not in task_acceptance.get(task_id, set()):
                    errors.append(f"{location}: task {task_id} does not accept {criterion_id}")

    if plan.status in {"verifying", "complete"} and TRACE_TERMINAL_PLACEHOLDER.search(plan.text):
        errors.append(f"{relative}: {plan.status} traceable plan contains an unresolved placeholder")
    if plan.status == "complete":
        validate_completed_traceability(plan, errors, traced_acceptance, known_acceptance, task_acceptance)


def validate_task_packets(plan: Plan, errors: list[str], *, strict: bool) -> None:
    matches = list(TASK_HEADING.finditer(plan.text))
    if not matches:
        errors.append(f"{plan.path.relative_to(ROOT)}: no Task Packet headings found")
        return
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        task_id = match.group(1)
        if task_id in blocks:
            errors.append(f"{plan.path.relative_to(ROOT)}: duplicate task id {task_id}")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(plan.text)
        blocks[task_id] = plan.text[match.end() : end]

    dependencies: dict[str, set[str]] = {}
    terminal_plan = plan.status in {"verifying", "complete"}
    for task_id, block in blocks.items():
        fields: dict[str, str] = {}
        for label in TASK_REQUIRED_LABELS:
            value = task_field(block, label)
            if value is None:
                errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: missing '{label}' field")
            else:
                fields[label] = value
        state = fields.get("State", "").splitlines()[0].strip().lower()
        valid_states = {"ready", "blocked", "in-progress", "complete", "failed", "cancelled"}
        if state and state not in valid_states:
            errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: invalid state '{state}'")
        depends_text = fields.get("Depends on", "")
        deps = set(re.findall(r"\bT[0-9A-Za-z_-]+\b", depends_text))
        dependencies[task_id] = deps
        for dependency in deps:
            if dependency not in blocks:
                errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: unknown dependency {dependency}")
        if state == "complete" and fields.get("Result", "").strip().lower() in {"", "pending", "todo"}:
            errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: completed task has no Result evidence")
        if terminal_plan and state not in {"complete", "cancelled"}:
            errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: {plan.status} plan has non-terminal task state '{state}'")
        if strict and plan.status not in {"proposed", "blocked"} and PLACEHOLDER in block:
            errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: unresolved {PLACEHOLDER} marker")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visited:
            return
        if task_id in visiting:
            errors.append(f"{plan.path.relative_to(ROOT)}: cyclic task dependency involving {task_id}")
            return
        visiting.add(task_id)
        for dependency in dependencies.get(task_id, set()):
            if dependency in blocks:
                visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in blocks:
        visit(task_id)

def command_plan_check(args: argparse.Namespace) -> int:
    config = load_config()
    strict = bool(args.strict or config.lifecycle == "active")
    errors: list[str] = []
    plans = plan_files()
    seen_ids: dict[str, Path] = {}
    for plan in plans:
        relative = plan.path.relative_to(ROOT)
        in_active = "active" in relative.parts
        valid = ACTIVE_PLAN_STATES if in_active else COMPLETED_PLAN_STATES
        if not plan.metadata:
            errors.append(f"{relative}: missing frontmatter")
            continue
        for field in (
            "id",
            "kind",
            "status",
            "owner",
            "created",
            "updated",
            "area",
            "base_commit",
            "integrated_commit",
            "verified_commit",
        ):
            if field not in plan.metadata:
                errors.append(f"{relative}: missing frontmatter field '{field}'")
        if str(plan.metadata.get("kind", "")) != "exec-plan":
            errors.append(f"{relative}: kind must be 'exec-plan'")
        if plan.id in seen_ids:
            errors.append(f"{relative}: duplicate plan id {plan.id} also used by {seen_ids[plan.id].relative_to(ROOT)}")
        else:
            seen_ids[plan.id] = plan.path
        if plan.status not in valid:
            errors.append(f"{relative}: status '{plan.status}' invalid for this directory; expected {sorted(valid)}")
        for heading in PLAN_REQUIRED_HEADINGS:
            if not heading_present(plan.text, heading):
                errors.append(f"{relative}: missing section '## {heading}'")
        validate_task_packets(plan, errors, strict=strict and plan.status not in {"proposed", "blocked"})
        validate_traceable_plan(plan, errors)
        if strict and plan.status in {"approved", "in-progress", "verifying", "complete"} and PLACEHOLDER in plan.text:
            errors.append(f"{relative}: unresolved {PLACEHOLDER} marker in {plan.status} plan")
        if plan.status in {"verifying", "complete"}:
            if "- [ ]" in section_text(plan.text, "Progress"):
                errors.append(f"{relative}: {plan.status} plan contains unchecked Progress items")
            for evidence_section in ("Documentation Impact", "Validation and Evidence"):
                if re.search(r"\bpending\b", section_text(plan.text, evidence_section), re.IGNORECASE):
                    errors.append(f"{relative}: {evidence_section} still contains pending work")
            integrated = str(plan.metadata.get("integrated_commit", "")).strip()
            if not integrated:
                errors.append(f"{relative}: {plan.status} plan is missing integrated_commit")
            elif plan.status == "verifying" and integrated == "HEAD":
                pass
            elif not re.fullmatch(r"[0-9a-fA-F]{7,64}", integrated):
                errors.append(f"{relative}: integrated_commit must be HEAD or a Git object id while verifying")
        if plan.status == "complete":
            if "- [ ]" in plan.text:
                errors.append(f"{relative}: complete plan contains unchecked Progress items")
            verified = str(plan.metadata.get("verified_commit", "")).strip()
            if not verified:
                errors.append(f"{relative}: complete plan is missing verified_commit")
            elif not re.fullmatch(r"[0-9a-fA-F]{7,64}", verified):
                errors.append(f"{relative}: verified_commit is not a Git object id")
            integrated = str(plan.metadata.get("integrated_commit", "")).strip()
            if integrated and verified and integrated != verified:
                errors.append(f"{relative}: verified_commit must equal integrated_commit unless the plan explains a re-integration")
    if config.baseline == "established":
        for plan in plans:
            if (
                plan.id == "PLAN-0000"
                and "active" in plan.path.relative_to(ROOT).parts
                and plan.status != "verifying"
            ):
                errors.append(
                    f"{plan.path.relative_to(ROOT)}: established baseline may keep PLAN-0000 active only while verifying"
                )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise HarnessError(f"plan check failed with {len(errors)} error(s)")
    print(f"Plan check passed ({len(plans)} plan(s), strict={strict}).")
    return 0

CORE_DOCUMENT_SCHEMAS = {
    Path("ARCHITECTURE.md"): ("ARCHITECTURE", "architecture"),
    Path("docs/PRODUCT.md"): ("PRODUCT", "product"),
    Path("docs/QUALITY.md"): ("QUALITY", "quality"),
    Path("docs/SECURITY.md"): ("SECURITY", "security"),
    Path("docs/DESIGN.md"): ("DESIGN", "design"),
    Path("docs/FRONTEND.md"): ("FRONTEND", "frontend"),
    Path("docs/PRODUCT_SENSE.md"): ("PRODUCT_SENSE", "product-sense"),
    Path("docs/RELIABILITY.md"): ("RELIABILITY", "reliability"),
}
OPTIONAL_CORE_DOCUMENTS = {
    path: capability for capability, path in DOCUMENT_CAPABILITY_KEYS.items()
}


def validate_core_documents(
    errors: list[str],
    *,
    strict: bool,
    enabled: frozenset[str] | None = None,
) -> None:
    for relative, (expected_id, expected_kind) in CORE_DOCUMENT_SCHEMAS.items():
        capability = OPTIONAL_CORE_DOCUMENTS.get(relative)
        if capability is not None and enabled is not None and capability not in enabled:
            continue
        path = ROOT / relative
        if not path.exists():
            continue
        metadata, _, _ = read_frontmatter(path)
        missing = [field for field in ("id", "kind", "status", "area", "summary") if not str(metadata.get(field, "")).strip()]
        if missing:
            errors.append(f"{relative}: missing frontmatter fields: {', '.join(missing)}")
            continue
        if str(metadata.get("id")) != expected_id:
            errors.append(f"{relative}: id must be '{expected_id}'")
        if str(metadata.get("kind")) != expected_kind:
            errors.append(f"{relative}: kind must be '{expected_kind}'")
        status = str(metadata.get("status", "")).lower()
        if status not in {"draft", "active"}:
            errors.append(f"{relative}: current-state status must be 'draft' or 'active'")
        if strict and status != "active":
            errors.append(f"{relative}: established baseline requires status 'active'")


def first_present_section(text: str, headings: Sequence[str]) -> str:
    for heading in headings:
        value = section_text(text, heading)
        if value:
            return value
    return ""


def substantive_markdown_bullets(text: str) -> list[str]:
    bullets: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^\s*[-*]\s+(.+?)\s*$", line)
        if not match:
            continue
        value = match.group(1).strip()
        if definition_value_is_concrete(value) and len(value) >= 12:
            bullets.append(value)
    return bullets


def validate_durable_decisions(documents: Sequence[DurableDocument], errors: list[str]) -> None:
    for document in documents:
        if document.kind != "decision" or document.status != "accepted":
            continue
        relative = document.path.relative_to(ROOT)
        _, _, text = read_frontmatter(document.path)
        reason = first_present_section(text, ("Reason", "Context and scope", "Context"))
        if not definition_value_is_concrete(reason):
            errors.append(f"{relative}: accepted decision requires a concrete reason")
        alternatives = first_present_section(text, ("Alternatives considered", "Alternatives and trade-offs"))
        alternative_bullets = substantive_markdown_bullets(alternatives)
        rejected_alternatives = [
            bullet
            for bullet in alternative_bullets
            if re.search(r"\b(?:rejected|not selected|not chosen)\b", bullet, re.IGNORECASE)
        ]
        if len(alternative_bullets) < 2 or len(rejected_alternatives) < 2:
            errors.append(
                f"{relative}: accepted decision requires at least two substantive alternatives with rejection reasons"
            )
        verification = first_present_section(
            text,
            ("Verification and enforcement", "Verification and retirement", "Verification"),
        )
        if not definition_value_is_concrete(verification):
            errors.append(f"{relative}: accepted decision requires concrete verification or enforcement")


def generated_baseline_review_required() -> bool:
    marker = "Provenance: initialized by Reporivet"
    for relative in (Path("ARCHITECTURE.md"), Path("docs/PRODUCT.md")):
        path = ROOT / relative
        if path.exists() and marker in path.read_text(encoding="utf-8", errors="ignore"):
            return True
    return False


def validate_generated_baseline_review(errors: list[str], *, strict: bool) -> None:
    if not generated_baseline_review_required():
        return
    for relative in (
        Path("docs/generated/repository-facts.md"),
        Path("docs/generated/baseline-questions.md"),
    ):
        if not (ROOT / relative).is_file():
            errors.append(f"missing required generated baseline evidence: {relative}")
    if not strict:
        return
    required_checks = (
        "- [x] Observed repository facts reviewed:",
        "- [x] Baseline questions resolved or tracked:",
    )
    for relative in (Path("ARCHITECTURE.md"), Path("docs/PRODUCT.md")):
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "Provenance: initialized by Reporivet" not in text:
            continue
        review = section_text(text, "Baseline evidence review")
        if not review:
            errors.append(f"{relative}: established baseline requires a baseline evidence review section")
            continue
        for required in required_checks:
            if required not in review:
                errors.append(
                    f"{relative}: established baseline requires completed baseline evidence review checklists"
                )
                break
        evidence = next(
            (
                line.split(":", 1)[1].strip()
                for line in review.splitlines()
                if line.strip().startswith("- Review evidence:") and ":" in line
            ),
            "",
        )
        if not definition_value_is_concrete(evidence):
            errors.append(f"{relative}: established baseline requires concrete baseline review evidence")


def command_docs_check(args: argparse.Namespace) -> int:
    config = load_config()
    strict = bool(args.strict or config.lifecycle == "active")
    errors: list[str] = []
    warnings: list[str] = []
    enabled = config.document_capabilities()
    required = list(REQUIRED_DOCS)
    required.extend(
        path for capability, path in DOCUMENT_CAPABILITY_KEYS.items() if capability in enabled
    )
    for relative in required:
        if not (ROOT / relative).exists():
            errors.append(f"missing required file: {relative}")

    core_documents = core_context_documents(errors)
    documents = durable_documents(errors, warnings)
    errors.extend(authority_conflict_errors([*core_documents, *documents]))
    validate_durable_decisions(documents, errors)
    validate_generated_baseline_review(errors, strict=strict)
    _, _, code_entries = code_map_model(config, errors)
    validate_core_documents(errors, strict=strict, enabled=enabled)
    agents = ROOT / "AGENTS.md"
    max_lines = int(config.policy.get("agents_max_lines", 140))
    if agents.exists():
        line_count = len(agents.read_text(encoding="utf-8").splitlines())
        if line_count > max_lines:
            warnings.append(f"AGENTS.md is {line_count} lines; configured maximum is {max_lines}")

    for base in (ROOT / "docs", ROOT / "ARCHITECTURE.md", ROOT / "AGENTS.md"):
        if base.is_file():
            check_links(base, errors)
        elif base.is_dir():
            for path in base.rglob("*.md"):
                if path.relative_to(ROOT) == DEFINITION_DRAFT:
                    continue
                check_links(path, errors)

    if strict:
        strict_files = [
            ROOT / "AGENTS.md",
            ROOT / "ARCHITECTURE.md",
            ROOT / "docs" / "PRODUCT.md",
            ROOT / "docs" / "QUALITY.md",
            ROOT / "docs" / "SECURITY.md",
        ]
        strict_files.extend(
            ROOT / path
            for capability, path in DOCUMENT_CAPABILITY_KEYS.items()
            if capability in enabled
        )
        for path in strict_files:
            if path.exists() and PLACEHOLDER in path.read_text(encoding="utf-8"):
                errors.append(f"{path.relative_to(ROOT)}: unresolved {PLACEHOLDER} marker in active lifecycle")

    generated = ROOT / "docs" / "generated"
    if generated.exists():
        for path in generated.glob("*.md"):
            if path.name == "README.md":
                continue
            head = "\n".join(path.read_text(encoding="utf-8", errors="ignore").splitlines()[:8])
            if "generated" not in head.lower():
                warnings.append(f"{path.relative_to(ROOT)} does not identify its generator")

    for catalog_path, kinds, grouped in catalog_targets():
        if not catalog_path.exists():
            continue
        original = catalog_path.read_bytes().decode("utf-8")
        expected = expected_catalog_text(catalog_path, documents, kinds, grouped)
        if expected != original:
            errors.append(f"{catalog_path.relative_to(ROOT)} catalog is stale; run ./dev/docs-index")

    if (ROOT / CODE_MAP_PATH).exists():
        actual_code_map = (ROOT / CODE_MAP_PATH).read_text(encoding="utf-8")
        if actual_code_map != code_map_markdown(code_entries):
            errors.append(f"{CODE_MAP_PATH} is stale; run ./dev/code-map")

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise HarnessError(f"documentation check failed with {len(errors)} error(s)")
    print(f"Documentation check passed ({len(documents)} durable document(s), {len(warnings)} warning(s), strict={strict}).")
    return 0


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_timestamp() -> str:
    return utc_now().strftime("%Y%m%dT%H%M%S%fZ")


def json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_json_file(path: Path, value: object) -> None:
    ensure_safe_repository_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_text(value), encoding="utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes()) if path.exists() and path.is_file() else ""


class TeeTextIO:
    def __init__(self, *streams: object) -> None:
        self.streams = streams

    def write(self, value: str) -> int:
        for stream in self.streams:
            stream.write(value)  # type: ignore[attr-defined]
        return len(value)

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()  # type: ignore[attr-defined]


def create_verification_run() -> VerificationRun:
    run_id = f"{utc_timestamp()}-verify"
    path = ROOT / ".harness" / "runs" / run_id
    ensure_safe_repository_path(path)
    path.mkdir(parents=True, exist_ok=False)
    (path / "checks").mkdir()
    (path / "logs").mkdir()
    return VerificationRun(run_id=run_id, path=path, started_at=utc_now().isoformat())


def command_display(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def command_metadata(command: Sequence[str]) -> dict[str, object]:
    executable = Path(command[0]).name if Path(command[0]).is_absolute() else command[0].replace(os.sep, "/")
    return {"argc": len(command), "executable": executable}


def executable_available(command: Sequence[str]) -> bool:
    executable = command[0]
    if executable.startswith("./") or "/" in executable:
        path = (ROOT / executable).resolve() if not Path(executable).is_absolute() else Path(executable)
        return path.exists() and os.access(path, os.X_OK)
    return shutil.which(executable) is not None


def execute_group(
    name: str,
    commands: Sequence[Sequence[str]],
    *,
    allow_empty: bool = False,
    run_context: VerificationRun | None = None,
) -> GroupResult:
    started_at = utc_now().isoformat()
    if not commands:
        finished_at = utc_now().isoformat()
        if allow_empty:
            print(f"No commands configured for '{name}'.")
            return GroupResult(
                status="skipped",
                detail=f"no commands configured for '{name}'",
                started_at=started_at,
                finished_at=finished_at,
                commands=(),
                returncodes=(),
                logs=(),
            )
        return GroupResult(
            status="error",
            detail=f"no deterministic commands configured for [commands].{name}",
            started_at=started_at,
            finished_at=finished_at,
            commands=(),
            returncodes=(),
            logs=(),
        )

    standalone_dir = ROOT / ".harness" / "runs" / f"{utc_timestamp()}-{name}" if run_context is None else None
    if standalone_dir is not None:
        ensure_safe_repository_path(standalone_dir)
        standalone_dir.mkdir(parents=True, exist_ok=False)
    command_records: list[dict[str, object]] = []
    returncodes: list[int | None] = []
    logs: list[str] = []
    legacy_summary: list[dict[str, object]] = []
    status = "pass"
    detail = f"{len(commands)} configured command(s) passed"

    for index, command in enumerate(commands, start=1):
        metadata = command_metadata(command)
        command_records.append(metadata)
        executable = str(metadata["executable"])
        if not executable_available(command):
            returncodes.append(None)
            status = "error"
            detail = f"configured executable is unavailable: {executable}; run ./dev/bootstrap or fix dev/harness.toml"
            break
        printable = command_display(command)
        print(f"\n$ {printable}")
        if run_context is not None:
            log_path = run_context.command_log_path(name, index)
            log_relative = log_path.relative_to(run_context.path).as_posix()
        else:
            assert standalone_dir is not None
            log_path = standalone_dir / f"{index:02d}.log"
            log_relative = log_path.relative_to(ROOT).as_posix()
        command_started = utc_now()
        returncode: int | None = None
        try:
            with log_path.open("w", encoding="utf-8") as log:
                try:
                    process = subprocess.Popen(
                        list(command),
                        cwd=ROOT,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                    )
                except OSError as exc:
                    message = exc.strerror or exc.__class__.__name__
                    log.write(f"ERROR: could not execute configured command {index} ({executable}): {message}\n")
                    status = "error"
                    detail = f"could not execute configured command {index} ({executable}): {message}"
                else:
                    assert process.stdout is not None
                    for line in process.stdout:
                        print(line, end="")
                        log.write(line)
                    returncode = process.wait()
        except OSError as exc:
            status = "error"
            detail = f"could not write command log {log_relative}: {exc}"
        command_finished = utc_now()
        returncodes.append(returncode)
        if log_path.exists():
            logs.append(log_relative)
        legacy_summary.append(
            {
                "command": list(command),
                "finished": command_finished.isoformat(),
                "log": log_relative,
                "returncode": returncode,
                "started": command_started.isoformat(),
            }
        )
        if status == "error":
            break
        if returncode != 0:
            status = "fail"
            detail = f"configured command {index} failed with exit code {returncode}; see {log_relative}"
            break

    finished_at = utc_now().isoformat()
    result = GroupResult(
        status=status,
        detail=detail,
        started_at=started_at,
        finished_at=finished_at,
        commands=tuple(command_records),
        returncodes=tuple(returncodes),
        logs=tuple(logs),
    )
    if standalone_dir is not None:
        write_json_file(standalone_dir / "summary.json", legacy_summary)
        if result.status == "pass":
            print(f"\n{name} passed. Raw logs: {standalone_dir.relative_to(ROOT)}")
    elif result.status == "pass":
        print(f"\n{name} passed. Raw logs: {run_context.path.relative_to(ROOT) / 'logs'}")
    else:
        print(f"ERROR: {result.detail}", file=sys.stderr)
    return result


def require_group_success(result: GroupResult) -> int:
    if result.status == "fail":
        raise CandidateFailure(result.detail)
    if result.status == "error":
        raise InfrastructureError(result.detail)
    return 0


def command_bootstrap(_: argparse.Namespace) -> int:
    config = load_config()
    return require_group_success(execute_group("bootstrap", config.command_group("bootstrap"), allow_empty=True))


def command_run(_: argparse.Namespace) -> int:
    return require_group_success(execute_group("run", load_config().command_group("run")))


def command_smoke(_: argparse.Namespace) -> int:
    return require_group_success(execute_group("smoke", load_config().command_group("smoke")))


def validate_architecture_document(*, strict: bool) -> None:
    architecture = ROOT / "ARCHITECTURE.md"
    if strict and architecture.exists() and PLACEHOLDER in architecture.read_text(encoding="utf-8"):
        raise CandidateFailure(f"ARCHITECTURE.md contains unresolved {PLACEHOLDER} markers")


def command_architecture_check(args: argparse.Namespace) -> int:
    config = load_config()
    strict = bool(args.strict or config.lifecycle == "active")
    validate_architecture_document(strict=strict)
    commands = config.command_group("architecture")
    if commands:
        return require_group_success(execute_group("architecture", commands))
    print("Architecture document check passed; no machine architecture commands configured.")
    return 0


def is_example_or_template_name(name: str) -> bool:
    lowered = name.lower()
    return any(marker in lowered for marker in (".example", ".sample", ".template", "-example", "-sample", "-template"))


def sensitive_path_reason(relative: Path) -> str | None:
    lowered_parts = tuple(part.lower() for part in relative.parts)
    if any(part in SENSITIVE_DIRECTORY_NAMES for part in lowered_parts[:-1]):
        return "sensitive local directory"
    normalized = relative.as_posix().lower().lstrip("./")
    if any(normalized == suffix or normalized.endswith("/" + suffix) for suffix in SENSITIVE_PATH_SUFFIXES):
        return "sensitive local configuration"
    if any(normalized.startswith(prefix) or ("/" + prefix) in normalized for prefix in SENSITIVE_PATH_PREFIXES):
        return "sensitive local configuration"
    name = relative.name.lower()
    if is_example_or_template_name(name):
        return None
    if name in SENSITIVE_BASENAMES:
        return "sensitive local configuration"
    if name.startswith(".env.") or name.endswith(".env") or ".env." in name:
        return "environment file"
    if name.startswith(("id_rsa", "id_dsa", "id_ecdsa", "id_ed25519")) and not name.endswith(".pub"):
        return "private key filename"
    if name.startswith("client_secret") and name.endswith(".json"):
        return "OAuth client credential"
    if name.startswith("service-account") and name.endswith(".json"):
        return "service account credential"
    if name.endswith("-service-account.json") or name.startswith("firebase-adminsdk"):
        return "service account credential"
    if name.startswith("credentials.") and name.endswith(".json"):
        return "credential file"
    if name.endswith("-credentials.json"):
        return "credential file"
    if name.startswith("kubeconfig"):
        return "cluster credential file"
    suffix = relative.suffix.lower()
    if suffix in SENSITIVE_SUFFIXES:
        return f"sensitive {suffix} file"
    if name.endswith(".tfstate") or ".tfstate." in name:
        return "Terraform state"
    if name.endswith(".tfvars.json"):
        return "Terraform variable file"
    if name.startswith(("config.local.", "settings.local.")) or ".local." in name:
        return "local configuration"
    return None


def git_tracked_paths() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise InfrastructureError(message or "git ls-files failed during security check")
    return [Path(os.fsdecode(item)) for item in completed.stdout.split(b"\0") if item]


def git_tracked_ignored_paths() -> set[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "-ci", "--exclude-per-directory=.gitignore", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise InfrastructureError(message or "git ignored-path audit failed during security check")
    return {Path(os.fsdecode(item)) for item in completed.stdout.split(b"\0") if item}


def path_is_allowlisted(relative: Path, patterns: Sequence[str]) -> bool:
    normalized = relative.as_posix()
    normalized_patterns = [
        pattern[2:] if pattern.startswith("./") else pattern.lstrip("/")
        for pattern in patterns
    ]
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in normalized_patterns)


def command_security_check(_: argparse.Namespace) -> int:
    if not (ROOT / ".git").exists():
        print("Security check skipped because this project is not yet a Git repository.")
        return 0
    config = load_config()
    allowlist = config.list_value("policy", "security_allow_tracked")
    max_bytes = int(config.policy.get("security_scan_max_bytes", 2_097_152))
    violations: list[str] = []
    tracked_paths = git_tracked_paths()
    tracked_ignored = git_tracked_ignored_paths()
    for relative in tracked_paths:
        if path_is_allowlisted(relative, allowlist):
            continue
        reason = sensitive_path_reason(relative)
        if reason:
            violations.append(f"{relative.as_posix()}: tracked {reason}")
            continue
        if relative in tracked_ignored:
            violations.append(f"{relative.as_posix()}: tracked path is ignored by a repository .gitignore")
            continue
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            continue
        try:
            if path.stat().st_size > max_bytes:
                continue
            payload = path.read_bytes()
        except OSError as exc:
            raise InfrastructureError(f"cannot inspect tracked file {relative}: {exc}") from exc
        for label, pattern in SENSITIVE_CONTENT_PATTERNS:
            if pattern.search(payload):
                violations.append(f"{relative.as_posix()}: contains a {label} signature")
                break
    if violations:
        for violation in violations:
            print(f"ERROR: {violation}", file=sys.stderr)
        raise CandidateFailure(
            "security check rejected tracked sensitive material; remove it from Git, rotate real credentials, "
            "or add a narrowly reviewed [policy].security_allow_tracked entry"
        )
    print(f"Security check passed ({len(tracked_paths)} tracked path(s) inspected).")
    return 0


def command_check(_: argparse.Namespace) -> int:
    config = load_config()
    command_security_check(argparse.Namespace())
    command_docs_index(argparse.Namespace(check=True))
    command_docs_check(argparse.Namespace(strict=False))
    command_plan_check(argparse.Namespace(strict=False))
    if config.configuration != "ready":
        raise HarnessError("dev/harness.toml is still marked configuration = 'review'; confirm canonical commands first")
    commands = config.command_group("check")
    source_exists = any((ROOT / path).exists() for path in config.list_value("paths", "source"))
    return require_group_success(execute_group("check", commands, allow_empty=not source_exists))


def portable_detail(value: object) -> str:
    detail = str(value).strip() or value.__class__.__name__
    root = str(ROOT)
    detail = detail.replace(root + os.sep, "").replace(root, ".")
    return " ".join(detail.replace(os.sep, "/").splitlines())


def classify_check_exception(exc: Exception) -> str:
    if isinstance(exc, CandidateFailure):
        return "fail"
    if isinstance(exc, (InfrastructureError, OSError, UnicodeError, json.JSONDecodeError, tomllib.TOMLDecodeError)):
        return "error"
    if isinstance(exc, HarnessError):
        return "fail"
    return "error"


def execute_builtin_check(
    run: VerificationRun,
    name: str,
    *,
    required: bool,
    action: object,
    success_status: str = "pass",
) -> CheckResult:
    started_at = utc_now().isoformat()
    log_path = run.builtin_log_path(name)
    log_relative = log_path.relative_to(run.path).as_posix()
    status = success_status
    detail = f"{name} check passed"
    logs: tuple[str, ...] = ()
    try:
        with log_path.open("w", encoding="utf-8") as log:
            logs = (log_relative,)
            stdout = TeeTextIO(sys.stdout, log)
            stderr = TeeTextIO(sys.stderr, log)
            try:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    result = action()  # type: ignore[operator]
                    if result not in (None, 0):
                        raise CandidateFailure(f"{name} check returned {result}")
            except Exception as exc:
                status = classify_check_exception(exc)
                detail = portable_detail(exc)
                print(f"ERROR: {detail}", file=stderr)
    except OSError as exc:
        status = "error"
        detail = portable_detail(f"could not write {log_relative}: {exc}")
        logs = ()
    return CheckResult(
        name=name,
        required=required,
        status=status,
        detail=detail,
        started_at=started_at,
        finished_at=utc_now().isoformat(),
        logs=logs,
    )


def persist_check(run: VerificationRun, result: CheckResult) -> CheckResult:
    write_json_file(run.check_path(result.name), result.as_dict())
    return result


def combine_check_results(preflight: CheckResult, group: GroupResult, *, required: bool) -> CheckResult:
    return CheckResult(
        name=preflight.name,
        required=required,
        status=group.status,
        detail=group.detail,
        started_at=preflight.started_at,
        finished_at=group.finished_at,
        commands=group.commands,
        returncodes=group.returncodes,
        logs=preflight.logs + group.logs,
    )


def recursive_verify_reason(command: Sequence[str]) -> str:
    normalized = [part.replace("\\", "/") for part in command]
    unquoted = [part.strip().replace("'", "").replace('"', "") for part in normalized]
    for part in unquoted:
        if part in {"./dev/verify", "dev/verify"} or part.endswith("/dev/verify"):
            return "configured project verification recursively invokes dev/verify"
        if re.search(r"(?:^|[;&|()\s])(?:\./)?dev/verify(?:$|[;&|()\s])", part):
            return "configured project verification recursively invokes dev/verify"
        if re.search(r"dev/harness\.py\s+verify(?:$|\s)", part):
            return "configured project verification recursively invokes dev/harness.py verify"
        if re.search(r"(?:^|\s)-m\s+dev\.harness\s+verify(?:$|\s)", part):
            return "configured project verification recursively invokes the dev.harness module"
    for index, part in enumerate(unquoted[:-1]):
        if part.endswith("dev/harness.py") and unquoted[index + 1] == "verify":
            return "configured project verification recursively invokes dev/harness.py verify"
        if part == "-m" and unquoted[index + 1] == "dev.harness" and "verify" in unquoted[index + 2 :]:
            return "configured project verification recursively invokes the dev.harness module"
    return ""


def validate_nonrecursive_commands(commands: Sequence[Sequence[str]]) -> None:
    for command in commands:
        reason = recursive_verify_reason(command)
        if reason:
            raise InfrastructureError(reason)


def verification_security_check(run: VerificationRun) -> CheckResult:
    no_git = not (ROOT / ".git").exists()
    result = execute_builtin_check(
        run,
        "security",
        required=True,
        action=lambda: command_security_check(argparse.Namespace()),
        success_status="skipped" if no_git else "pass",
    )
    if result.status == "skipped":
        result = CheckResult(
            name=result.name,
            required=result.required,
            status=result.status,
            detail="security check is not applicable before Git initialization",
            started_at=result.started_at,
            finished_at=result.finished_at,
            logs=result.logs,
        )
    return persist_check(run, result)


def verification_builtin_check(run: VerificationRun, name: str, action: object) -> CheckResult:
    return persist_check(run, execute_builtin_check(run, name, required=True, action=action))


def verification_architecture_check(run: VerificationRun) -> CheckResult:
    state: dict[str, object] = {}

    def preflight() -> None:
        config = load_config()
        validate_architecture_document(strict=config.lifecycle == "active")
        commands = config.command_group("architecture")
        validate_nonrecursive_commands(commands)
        state["commands"] = commands
        print("Architecture document check passed.")

    built_in = execute_builtin_check(run, "architecture", required=True, action=preflight)
    if built_in.status != "pass":
        return persist_check(run, built_in)
    commands = state.get("commands", [])
    if not commands:
        result = CheckResult(
            name="architecture",
            required=True,
            status="pass",
            detail="architecture document passed; no machine architecture commands configured",
            started_at=built_in.started_at,
            finished_at=built_in.finished_at,
            logs=built_in.logs,
        )
        return persist_check(run, result)
    group = execute_group("architecture", commands, run_context=run)  # type: ignore[arg-type]
    return persist_check(run, combine_check_results(built_in, group, required=True))


def verification_project_check(run: VerificationRun) -> CheckResult:
    state: dict[str, object] = {}

    def preflight() -> None:
        config = load_config()
        if config.configuration != "ready":
            raise CandidateFailure(
                "dev/harness.toml is still marked configuration = 'review'; confirm deterministic commands first"
            )
        commands = config.command_group("verify")
        validate_nonrecursive_commands(commands)
        state["commands"] = commands
        state["source_exists"] = any(
            (ROOT / path).exists() for path in config.list_value("paths", "source")
        )
        print("Project verification configuration passed preflight.")

    preflight_result = execute_builtin_check(run, "project", required=True, action=preflight)
    if preflight_result.status != "pass":
        return persist_check(run, preflight_result)
    commands = state.get("commands", [])
    source_exists = bool(state.get("source_exists"))
    group = execute_group(
        "project",
        commands,  # type: ignore[arg-type]
        allow_empty=not source_exists,
        run_context=run,
    )
    return persist_check(run, combine_check_results(preflight_result, group, required=True))


def verification_smoke_check(run: VerificationRun) -> CheckResult:
    state: dict[str, object] = {}

    def preflight() -> None:
        config = load_config()
        commands = config.command_group("smoke")
        validate_nonrecursive_commands(commands)
        state["commands"] = commands
        print("Smoke configuration passed preflight.")

    preflight_result = execute_builtin_check(run, "smoke", required=False, action=preflight)
    if preflight_result.status != "pass":
        failed_preflight = CheckResult(
            name=preflight_result.name,
            required=True,
            status=preflight_result.status,
            detail=preflight_result.detail,
            started_at=preflight_result.started_at,
            finished_at=preflight_result.finished_at,
            commands=preflight_result.commands,
            returncodes=preflight_result.returncodes,
            logs=preflight_result.logs,
        )
        return persist_check(run, failed_preflight)
    commands = state.get("commands", [])
    if not commands:
        result = CheckResult(
            name="smoke",
            required=False,
            status="skipped",
            detail="no optional smoke commands configured",
            started_at=preflight_result.started_at,
            finished_at=preflight_result.finished_at,
            logs=preflight_result.logs,
        )
        return persist_check(run, result)
    group = execute_group("smoke", commands, run_context=run)  # type: ignore[arg-type]
    return persist_check(run, combine_check_results(preflight_result, group, required=True))


def local_git_command(*args: str) -> tuple[int | None, bytes, str]:
    if shutil.which("git") is None:
        return None, b"", "git executable is unavailable"
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        return None, b"", portable_detail(exc)
    return completed.returncode, completed.stdout, completed.stderr.decode("utf-8", errors="replace").strip()


def collect_target_evidence(
    *,
    base_sha: str | None = None,
    intended_head: str | None = None,
    target: str | None = None,
) -> dict[str, object]:
    base_sha = (os.environ.get("REPORIVET_BASE_SHA", "") if base_sha is None else base_sha).strip()
    intended_head = (os.environ.get("REPORIVET_HEAD_SHA", "") if intended_head is None else intended_head).strip()
    target = (os.environ.get("REPORIVET_TARGET", "") if target is None else target).strip()
    evidence: dict[str, object] = {
        "actual_head_sha": "",
        "base_sha": base_sha,
        "changed_paths": [],
        "changed_paths_detail": "changed-path evidence is unavailable",
        "changed_paths_method": "unknown",
        "changed_paths_status": "unknown",
        "clean": None,
        "git_status": "unknown",
        "head_matches_intended": None,
        "intended_head_sha": intended_head,
        "target": target,
        "target_reason_code": "TARGET_EVIDENCE_UNKNOWN",
        "target_status": "unknown",
    }
    git_marker = ROOT / ".git"
    if not git_marker.exists() or git_marker.is_symlink():
        evidence["git_status"] = "unavailable"
        evidence["target_reason_code"] = "GIT_UNAVAILABLE"
        evidence["changed_paths_detail"] = (
            "repository root has no safe local Git metadata; enclosing repositories were ignored and no Git parent was inferred"
        )
        return evidence
    code, stdout, _ = local_git_command("rev-parse", "--show-toplevel")
    top_level = os.fsdecode(stdout).strip() if code == 0 else ""
    try:
        matches_root = bool(top_level) and Path(top_level).resolve(strict=False) == ROOT.resolve(strict=False)
    except OSError:
        matches_root = False
    if not matches_root:
        evidence["git_status"] = "unavailable"
        evidence["target_reason_code"] = "GIT_ROOT_MISMATCH"
        evidence["changed_paths_detail"] = (
            "local Git top-level does not match the repository root; changed paths are unknown and no Git parent was inferred"
        )
        return evidence
    evidence["git_status"] = "available"

    head_code, head_stdout, head_error = local_git_command("rev-parse", "--verify", "HEAD")
    actual_head = head_stdout.decode("ascii", errors="ignore").strip() if head_code == 0 else ""
    evidence["actual_head_sha"] = actual_head
    if head_code != 0:
        evidence["target_status"] = "error" if base_sha or intended_head else "unknown"
        evidence["target_reason_code"] = "HEAD_UNAVAILABLE"
        evidence["changed_paths_detail"] = portable_detail(head_error or "local HEAD commit is unavailable")
        return evidence

    status_code, status_stdout, status_error = local_git_command(
        "status", "--porcelain=v1", "-z", "--untracked-files=all"
    )
    if status_code == 0:
        evidence["clean"] = status_stdout == b""
    else:
        evidence["git_status"] = "error"
        evidence["target_status"] = "error"
        evidence["target_reason_code"] = "GIT_STATUS_ERROR"
        evidence["changed_paths_detail"] = portable_detail(status_error or "git status failed")
        return evidence

    selected_head = actual_head
    if intended_head:
        if re.fullmatch(r"[0-9a-fA-F]{7,64}", intended_head) is None:
            evidence["target_status"] = "error"
            evidence["target_reason_code"] = "INTENDED_HEAD_INVALID"
            evidence["changed_paths_detail"] = "REPORIVET_HEAD_SHA is not a local Git object id"
            return evidence
        intended_code, intended_stdout, intended_error = local_git_command(
            "rev-parse", "--verify", f"{intended_head}^{{commit}}"
        )
        if intended_code != 0:
            evidence["target_status"] = "error"
            evidence["target_reason_code"] = "HEAD_COMMIT_UNAVAILABLE"
            evidence["changed_paths_detail"] = portable_detail(
                intended_error or "intended head commit is unavailable in the local repository"
            )
            return evidence
        selected_head = intended_stdout.decode("ascii", errors="ignore").strip()
        evidence["head_matches_intended"] = selected_head == actual_head
        if selected_head != actual_head:
            evidence["target_status"] = "mismatch"
            evidence["target_reason_code"] = "TARGET_HEAD_MISMATCH"
            evidence["changed_paths_detail"] = "explicit intended head does not match the observed local HEAD"
            return evidence

    if not base_sha:
        evidence["target_reason_code"] = "BASE_SHA_MISSING"
        evidence["changed_paths_detail"] = "REPORIVET_BASE_SHA is not set; no Git parent was inferred"
        return evidence
    if re.fullmatch(r"[0-9a-fA-F]{7,64}", base_sha) is None:
        evidence["target_status"] = "error"
        evidence["target_reason_code"] = "BASE_SHA_INVALID"
        evidence["changed_paths_detail"] = "REPORIVET_BASE_SHA is not a local Git object id"
        return evidence

    if re.fullmatch(r"[0-9a-fA-F]{7,64}", selected_head) is None:
        evidence["target_status"] = "error"
        evidence["target_reason_code"] = "HEAD_INVALID"
        evidence["changed_paths_detail"] = "no explicit or observed local head object id is available"
        return evidence
    for label, object_id in (("base", base_sha), ("head", selected_head)):
        object_code, _, object_error = local_git_command("cat-file", "-e", f"{object_id}^{{commit}}")
        if object_code != 0:
            evidence["target_status"] = "error"
            evidence["target_reason_code"] = f"{label.upper()}_COMMIT_UNAVAILABLE"
            evidence["changed_paths_detail"] = portable_detail(
                object_error or f"{label} commit is unavailable in the local repository"
            )
            return evidence
    diff_code, diff_stdout, diff_error = local_git_command(
        "diff", "--name-only", "-z", base_sha, selected_head, "--"
    )
    if diff_code != 0:
        evidence["target_status"] = "error"
        evidence["target_reason_code"] = "GIT_DIFF_ERROR"
        evidence["changed_paths_detail"] = portable_detail(diff_error or "git diff failed")
        return evidence

    changed_paths: list[str] = []
    for item in diff_stdout.split(b"\0"):
        if not item:
            continue
        path = os.fsdecode(item).replace(os.sep, "/")
        pure = PurePosixPath(path)
        if pure.is_absolute() or "\\" in path or any(part in {"", ".", ".."} for part in path.split("/")):
            evidence["target_status"] = "error"
            evidence["target_reason_code"] = "CHANGED_PATH_INVALID"
            evidence["changed_paths_detail"] = "Git reported an unsafe changed path"
            return evidence
        changed_paths.append(path)
    changed_paths.sort()
    evidence.update(
        {
            "changed_paths": changed_paths,
            "changed_paths_detail": f"{len(changed_paths)} path(s) from explicit base to local target",
            "changed_paths_method": "git-diff-explicit-base-to-target",
            "changed_paths_status": "available",
            "target_reason_code": "TARGET_CONFIRMED",
            "target_status": "available",
        }
    )
    return evidence


def verification_status(checks: Sequence[CheckResult]) -> str:
    if any(check.required and check.status == "fail" for check in checks):
        return "fail"
    if any(check.required and check.status in {"error", "unknown"} for check in checks):
        return "error"
    return "pass"


def verification_detection_summary() -> tuple[dict[str, object], str]:
    try:
        config = load_config()
        source_paths = config.list_value("paths", "source")
        effective_gate = gate_policy(config)
        summary = {
            "architecture_commands": len(config.command_group("architecture")),
            "configuration": config.configuration,
            "config_status": "available",
            "gate_mode": effective_gate.mode,
            "gate_policy_source": effective_gate.source,
            "lifecycle": config.lifecycle,
            "smoke_commands": len(config.command_group("smoke")),
            "source_paths_present": sum(1 for path in source_paths if (ROOT / path).exists()),
            "verify_commands": len(config.command_group("verify")),
        }
        policy_hash = sha256_bytes(
            json_text({"gate": effective_gate.as_dict(), "policy": config.policy}).encode("utf-8")
        )
    except Exception as exc:
        return {"config_status": "error", "detail": portable_detail(exc)}, ""
    return summary, policy_hash


def verification_manifest(
    run: VerificationRun,
    checks: Sequence[CheckResult],
    status: str,
    target_evidence: dict[str, object],
    finished_at: str,
) -> dict[str, object]:
    detection, policy_hash = verification_detection_summary()
    return {
        "artifacts": {
            "checks": [run.check_path(name).relative_to(run.path).as_posix() for name in VERIFICATION_CHECKS],
            "gate": "gate.json",
            "report": "report.md",
        },
        "checks": [check.as_dict() for check in checks],
        "command": "./dev/verify",
        "detection": detection,
        "finished_at": finished_at,
        "hashes": {
            "config_sha256": sha256_file(CONFIG_PATH),
            "policy_sha256": policy_hash,
            "runtime_sha256": sha256_file(Path(__file__)),
        },
        "run_id": run.run_id,
        "schema": "reporivet.verification-run/v1",
        "started_at": run.started_at,
        "status": status,
        "target_evidence": target_evidence,
    }


def gate_pattern_matches(path: str, pattern: str) -> bool:
    if any(character in pattern for character in "*?["):
        return fnmatch.fnmatchcase(path, pattern)
    prefix = pattern.rstrip("/")
    return path == prefix or path.startswith(prefix + "/")


def gate_paths_matching(paths: Sequence[str], patterns: Sequence[str]) -> list[str]:
    return sorted(path for path in paths if any(gate_pattern_matches(path, pattern) for pattern in patterns))


def classify_gate_risk(paths: Sequence[str], policy: GatePolicy) -> tuple[str, list[str]]:
    contained = set(gate_paths_matching(paths, policy.contained_paths))
    wide = set(gate_paths_matching(paths, policy.wide_paths))
    irreversible = set(gate_paths_matching(paths, policy.irreversible_paths))
    matched = sorted(contained | wide | irreversible)
    if irreversible:
        return "irreversible", matched
    if wide:
        return "wide", matched
    if not paths or len(contained) == len(paths):
        return "contained", matched
    return policy.default_risk, matched


def verification_gate(
    checks: Sequence[CheckResult],
    target_evidence: dict[str, object],
    manifest_hash: str,
) -> dict[str, object]:
    policy_error = ""
    try:
        policy = gate_policy(load_config())
    except Exception as exc:
        policy = default_gate_policy(source="fallback")
        policy_error = portable_detail(exc)

    changed_paths_value = target_evidence.get("changed_paths", [])
    changed_paths = (
        [str(path) for path in changed_paths_value]
        if isinstance(changed_paths_value, list)
        else []
    )
    risk, matched_paths = classify_gate_risk(changed_paths, policy)
    protected_matches = gate_paths_matching(changed_paths, policy.protected_paths)
    target_status = str(target_evidence.get("target_status", "unknown"))
    if target_status != "available":
        risk = "unknown"
        matched_paths = []
        protected_matches = []
    failed = sorted(check.name for check in checks if check.required and check.status == "fail")
    errored = sorted(
        check.name for check in checks if check.required and check.status in {"error", "unknown"}
    )
    reason_codes: list[str] = []
    reasons: list[str] = []

    if failed:
        verdict = "BLOCK"
        reason_codes.append("REQUIRED_CHECK_FAILED")
        reasons.append("Required candidate checks failed: " + ", ".join(failed) + ".")
    elif errored or policy_error or target_status in {"error", "mismatch"}:
        verdict = "INCONCLUSIVE"
        if errored:
            reason_codes.append("REQUIRED_CHECK_ERROR")
            reasons.append("Required checks could not produce candidate evidence: " + ", ".join(errored) + ".")
        if policy_error:
            reason_codes.append("GATE_CONFIG_ERROR")
            reasons.append("Gate configuration could not be evaluated: " + policy_error)
        if target_status == "mismatch":
            reason_codes.append("TARGET_MISMATCH")
            reasons.append(str(target_evidence.get("changed_paths_detail", "Explicit target evidence does not match.")))
        elif target_status == "error":
            reason_codes.append("TARGET_EVIDENCE_ERROR")
            reasons.append(str(target_evidence.get("changed_paths_detail", "Target evidence could not be evaluated.")))
    else:
        if target_status != "available":
            reason_codes.append("TARGET_EVIDENCE_UNKNOWN")
            reasons.append(str(target_evidence.get("changed_paths_detail", "Target evidence is unavailable.")))
        if risk == "unknown":
            reason_codes.append("RISK_UNKNOWN")
            reasons.append("One or more changed paths are outside the declared contained, wide, and irreversible patterns.")
        elif risk == "wide":
            reason_codes.append("RISK_WIDE")
            reasons.append("One or more changed paths match the declared wide-change patterns.")
        elif risk == "irreversible":
            reason_codes.append("RISK_IRREVERSIBLE")
            reasons.append("One or more changed paths match the declared irreversible-change patterns.")
        if protected_matches:
            reason_codes.append("PROTECTED_PATH_MATCH")
            reasons.append("Protected paths changed: " + ", ".join(protected_matches) + ".")
        if policy.require_clean and target_evidence.get("clean") is False:
            reason_codes.append("WORKTREE_DIRTY")
            reasons.append("The repository worktree is not clean.")
        elif policy.require_clean and target_status == "available" and target_evidence.get("clean") is not True:
            reason_codes.append("CLEAN_STATE_UNKNOWN")
            reasons.append("The clean-worktree requirement could not be confirmed.")
        if reason_codes:
            verdict = "REVIEW"
        else:
            verdict = "PASS"
            reason_codes.append("GATE_PASS")
            reasons.append("All required checks passed against a clean, explicit, contained local target.")

    return {
        "effective_risk": risk,
        "manifest_sha256": manifest_hash,
        "matched_paths": matched_paths,
        "mode": policy.mode,
        "policy_patterns": {
            "contained": list(policy.contained_paths),
            "irreversible": list(policy.irreversible_paths),
            "protected": list(policy.protected_paths),
            "wide": list(policy.wide_paths),
        },
        "policy_source": policy.source,
        "protected_path_matches": protected_matches,
        "reason_codes": reason_codes,
        "reasons": reasons,
        "schema": "reporivet.gate/v1",
        "target_evidence": target_evidence,
        "verdict": verdict,
    }


def markdown_code_value(value: object) -> str:
    encoded = json.dumps(str(value), ensure_ascii=False)[1:-1].replace("`", "\\u0060")
    return encoded or "unknown"


def verification_report(
    run: VerificationRun,
    checks: Sequence[CheckResult],
    status: str,
    target_evidence: dict[str, object],
    gate: dict[str, object],
) -> str:
    reason_codes = gate.get("reason_codes", [])
    primary_reason = reason_codes[0] if isinstance(reason_codes, list) and reason_codes else "UNKNOWN"
    lines = [
        f"# Verification Run `{run.run_id}`",
        "",
        f"- Verification status: **{status}**",
        f"- Gate verdict: **{gate.get('verdict', 'INCONCLUSIVE')}** (`{markdown_code_value(primary_reason)}`)",
        f"- Gate mode: **{gate.get('mode', 'shadow')}**",
        f"- Effective risk: **{gate.get('effective_risk', 'unknown')}**",
        f"- Target: `{markdown_code_value(target_evidence.get('target') or 'unknown')}`",
        f"- Actual HEAD: `{markdown_code_value(target_evidence.get('actual_head_sha') or 'unknown')}`",
        f"- Intended head: `{markdown_code_value(target_evidence.get('intended_head_sha') or 'unknown')}`",
        f"- Base: `{markdown_code_value(target_evidence.get('base_sha') or 'unknown')}`",
        f"- Changed paths: **{target_evidence.get('changed_paths_status', 'unknown')}**",
        "",
        "## Checks",
        "",
        "| # | Check | Required | Status | Evidence | Logs |",
        "|---:|---|---|---|---|---|",
    ]
    for index, check in enumerate(checks, start=1):
        check_link = run.check_path(check.name).relative_to(run.path).as_posix()
        log_links = ", ".join(f"[`{Path(path).name}`]({path})" for path in check.logs) or "—"
        lines.append(
            f"| {index} | `{check.name}` | {'yes' if check.required else 'no'} | `{check.status}` | "
            f"[`{Path(check_link).name}`]({check_link}) | {log_links} |"
        )
    lines.extend(("", "## Changed paths", ""))
    changed_paths = target_evidence.get("changed_paths", [])
    if isinstance(changed_paths, list) and changed_paths:
        lines.extend(f"- `{markdown_code_value(path)}`" for path in changed_paths)
    else:
        lines.append(f"- {target_evidence.get('changed_paths_detail', 'Unavailable.')}")
    lines.extend(("", "## Gate reasons", ""))
    reasons = gate.get("reasons", [])
    if isinstance(reason_codes, list) and isinstance(reasons, list):
        for index, code in enumerate(reason_codes):
            reason = reasons[index] if index < len(reasons) else "No detail recorded."
            lines.append(f"- `{markdown_code_value(code)}`: {reason}")
    if not reason_codes:
        lines.append("- `UNKNOWN`: no Gate reason was recorded.")
    lines.extend(
        (
            "",
            "## Rerun",
            "",
            "```sh",
            "./dev/verify",
            "```",
        )
    )
    return "\n".join(lines) + "\n"


def finalize_verification_run(
    run: VerificationRun,
    checks: Sequence[CheckResult],
    *,
    base_sha: str | None = None,
    intended_head: str | None = None,
    target: str | None = None,
) -> VerificationResult:
    status = verification_status(checks)
    target_evidence = collect_target_evidence(
        base_sha=base_sha,
        intended_head=intended_head,
        target=target,
    )
    manifest_path = run.path / "manifest.json"
    manifest = verification_manifest(run, checks, status, target_evidence, utc_now().isoformat())
    write_json_file(manifest_path, manifest)
    manifest_hash = sha256_file(manifest_path)
    gate = verification_gate(checks, target_evidence, manifest_hash)
    write_json_file(run.path / "gate.json", gate)
    report_path = run.path / "report.md"
    ensure_safe_repository_path(report_path)
    report_path.write_text(
        verification_report(run, checks, status, target_evidence, gate),
        encoding="utf-8",
    )
    return VerificationResult(
        run=run,
        verification_status=status,
        manifest_sha256=manifest_hash,
        gate=gate,
    )


def run_verification(
    *,
    base_sha: str | None = None,
    intended_head: str | None = None,
    target: str | None = None,
) -> VerificationResult:
    run = create_verification_run()
    checks: list[CheckResult] = []
    stages = (
        lambda: verification_security_check(run),
        lambda: verification_builtin_check(
            run, "docs-index", lambda: command_docs_index(argparse.Namespace(check=True))
        ),
        lambda: verification_builtin_check(
            run,
            "documentation",
            lambda: command_docs_check(argparse.Namespace(strict=load_config().lifecycle == "active")),
        ),
        lambda: verification_builtin_check(
            run,
            "plan",
            lambda: command_plan_check(argparse.Namespace(strict=load_config().lifecycle == "active")),
        ),
        lambda: verification_architecture_check(run),
        lambda: verification_project_check(run),
        lambda: verification_smoke_check(run),
    )
    for index, stage in enumerate(stages):
        name = VERIFICATION_CHECKS[index]
        try:
            result = stage()
        except Exception as exc:
            result = CheckResult(
                name=name,
                required=name != "smoke",
                status="error",
                detail=portable_detail(exc),
                started_at=utc_now().isoformat(),
                finished_at=utc_now().isoformat(),
            )
            persist_check(run, result)
        checks.append(result)
    return finalize_verification_run(
        run,
        checks,
        base_sha=base_sha,
        intended_head=intended_head,
        target=target,
    )


def verification_exit_code(result: VerificationResult) -> int:
    verdict = str(result.gate.get("verdict", "INCONCLUSIVE"))
    mode = str(result.gate.get("mode", "shadow"))
    if verdict == "INCONCLUSIVE":
        return 2
    if verdict == "BLOCK" or (verdict == "REVIEW" and mode == "enforce"):
        return 1
    if verdict in {"PASS", "REVIEW"}:
        return 0
    return 2


def command_verify(_: argparse.Namespace) -> int:
    result = run_verification()
    verdict = result.gate.get("verdict", "INCONCLUSIVE")
    mode = result.gate.get("mode", "shadow")
    print(
        f"\nVerification {result.verification_status}. Gate {verdict} ({mode}). "
        f"Evidence: {result.run.path.relative_to(ROOT)}"
    )
    return verification_exit_code(result)


def git_output(*args: str, check: bool = True) -> str:
    completed = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    if check and completed.returncode != 0:
        raise HarnessError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def git_head() -> str:
    if not (ROOT / ".git").exists():
        return ""
    return git_output("rev-parse", "HEAD", check=False)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9가-힣]+", "-", value)
    return value.strip("-") or "change"


def next_plan_id() -> str:
    year = date.today().year
    highest = 0
    for plan in plan_files():
        if not plan.id.startswith(f"PLAN-{year}-"):
            continue
        match = PLAN_ID_PATTERN.search(plan.id)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"PLAN-{year}-{highest + 1:04d}"


def command_new_plan(args: argparse.Namespace) -> int:
    title = " ".join(args.title).strip()
    if not title:
        raise HarnessError("plan title is required")
    plan_id = next_plan_id()
    template = ROOT / "docs" / "exec-plans" / "_template.md"
    if not template.exists():
        raise HarnessError("missing docs/exec-plans/_template.md")
    text = template.read_text(encoding="utf-8")
    replacements = {
        "{{PLAN_ID}}": plan_id,
        "{{PLAN_TITLE}}": title,
        "{{DATE}}": date.today().isoformat(),
        "{{AREA}}": args.area or "cross-cutting",
        "{{BASE_COMMIT}}": git_head(),
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    destination = ROOT / "docs" / "exec-plans" / "active" / f"{plan_id}-{slugify(title)}.md"
    if destination.exists():
        raise HarnessError(f"plan already exists: {destination.relative_to(ROOT)}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    print(destination.relative_to(ROOT))
    return 0


def command_define_status(_: argparse.Namespace) -> int:
    document = parse_definition_document()
    if document.structural_errors:
        raise_definition_errors(document.structural_errors, "status")
    document = refresh_definition_metadata(document)
    confirmed, next_section, continuation = definition_progress(document)
    print(f"Definition draft: {DEFINITION_DRAFT}")
    print(f"Progress: {len(confirmed)}/{len(DEFINITION_SECTIONS)} sections confirmed")
    print("Confirmed sections:")
    if confirmed:
        for section in confirmed:
            print(f"- {section.number}. {section.title}")
    else:
        print("- None")
    if next_section:
        print(f"Next unresolved section: {next_section.number}. {next_section.title}")
    else:
        print("Next unresolved section: None")
    print(f"Continuation: {continuation}")
    return 0


def command_define_validate(_: argparse.Namespace) -> int:
    document = parse_definition_document()
    errors, _ = validate_definition_document(document)
    if errors:
        raise_definition_errors(errors, "validation")
    print(f"Definition validation passed ({len(DEFINITION_SECTIONS)} confirmed sections).")
    return 0


def definition_rendered_items(items: Sequence[DefinitionItem]) -> list[str]:
    if not items:
        return ["- None."]
    return [f"- [{item.status}] {item.text}" for item in items]


def render_definition_spec(document: DefinitionDocument) -> str:
    lines = [
        "---",
        "id: SPEC-PROJECT-001",
        "kind: product-spec",
        "status: active",
        "area: product",
        "summary: Confirmed project definition with preserved proposals and open evidence",
        "applies_to: []",
        "supersedes: []",
        "---",
        "",
        "# Project Definition",
        "",
        "Finalized from `docs/product-specs/project-definition.draft.md`. Confirmed evidence remains distinct from proposals and non-blocking open items.",
    ]
    for section in document.sections:
        lines.extend(("", f"## {section.number}. {section.title}"))
        lines.extend(("", "### Confirmed", "", *definition_rendered_items(section.confirmed)))
        lines.extend(("", "### Proposed", "", *definition_rendered_items(section.proposed)))
        non_blocking = [item for item in section.open_items if item.status == "non-blocking"]
        lines.extend(("", "### Open", "", *definition_rendered_items(non_blocking)))
        lines.extend(("", "### Sources", "", *definition_rendered_items(section.sources)))
    return "\n".join(lines).rstrip() + "\n"


def definition_first_slice_item(document: DefinitionDocument) -> DefinitionItem:
    matches = [
        item
        for item in definition_section(document, 14).confirmed
        if item.text.casefold().startswith("first verifiable slice:")
    ]
    if len(matches) != 1:
        raise HarnessError("validated definition does not contain exactly one first verifiable slice")
    return matches[0]


def definition_first_slice_description(item: DefinitionItem) -> str:
    first_part = item.text.split("|", 1)[0]
    return first_part.split(":", 1)[1].strip()


def definition_confirmed_item_text(document: DefinitionDocument, section_number: int) -> list[str]:
    return [item.text for item in definition_section(document, section_number).confirmed]


def definition_markdown_bullets(values: Sequence[str]) -> list[str]:
    return [f"- {value}" for value in values] or ["- None recorded."]


def render_first_slice_plan(
    document: DefinitionDocument,
    declarations: dict[str, DefinitionDeclaration],
    plan_id: str,
) -> tuple[str, str]:
    slice_item = definition_first_slice_item(document)
    slice_description = definition_first_slice_description(slice_item)
    field_errors: list[str] = []
    slice_p0s = definition_field_ids(slice_item.text, "P0", "p0", field_errors, slice_item)
    slice_journeys = definition_field_ids(slice_item.text, "Journey", "journey", field_errors, slice_item)
    slice_acceptance = definition_field_ids(slice_item.text, "Acceptance", "acceptance", field_errors, slice_item)
    if field_errors or len(slice_p0s) != 1 or len(slice_journeys) != 1 or not slice_acceptance:
        raise HarnessError("validated first slice trace could not be rendered deterministically")
    p0_id = slice_p0s[0]
    journey_id = slice_journeys[0]
    acceptance_ids = list(slice_acceptance)
    title = f"First vertical slice — {slice_description}"
    today = date.today().isoformat()
    base_commit = git_head()
    read_context = definition_confirmed_values(document, 12, "Read context")
    allowed_writes = definition_confirmed_values(document, 12, "Allowed writes")
    protected_paths = definition_confirmed_values(document, 12, "Protected paths")
    completion_evidence = definition_confirmed_values(document, 13, "Completion evidence")
    checkpoints = definition_confirmed_values(document, 11, "Agent checkpoint")
    in_scope = definition_confirmed_values(document, 7, "In scope")
    out_of_scope = definition_confirmed_values(document, 7, "Out of scope")
    risks = definition_confirmed_values(document, 14, "Risk")
    dependencies = definition_confirmed_values(document, 14, "Dependency")
    acceptance_text = [
        f"**{identifier}:** {declarations[identifier].description}"
        for identifier in acceptance_ids
    ]
    acceptance_field = ", ".join(acceptance_ids)
    trace_rows = [
        f"| `SPEC-PROJECT-001` | `{journey_id}` | `{p0_id}` | `{identifier}` | `T1` | `T2` |"
        for identifier in acceptance_ids
    ]
    evidence_rows = [
        f"| `{identifier}` | `T1/T2` | pending | pending | pending | pending | pending | pending |"
        for identifier in acceptance_ids
    ]
    lines = [
        "---",
        f"id: {plan_id}",
        "kind: exec-plan",
        "status: proposed",
        "owner: main",
        "area: product",
        f"created: {today}",
        f"updated: {today}",
        f'base_commit: "{base_commit}"',
        'integrated_commit: ""',
        'verified_commit: ""',
        "traceability: 1",
        "product_spec: SPEC-PROJECT-001",
        'verification_run: ""',
        'manifest_sha256: ""',
        'gate_verdict: ""',
        'gate_review_reason: ""',
        "definition_plan: first-vertical-slice",
        "---",
        "",
        f"# {title}",
        "",
        "## Purpose / Big Picture",
        "",
        f"Deliver the confirmed first verifiable slice: {slice_description}",
        "",
        "## Progress",
        "",
        "- [ ] Confirm the proposed plan boundary against repository authority.",
        "- [ ] Implement the first vertical slice.",
        "- [ ] Independently verify every linked acceptance criterion.",
        "- [ ] Resolve documentation impact and follow-ups.",
        "",
        "## Context and Orientation",
        "",
        "Product authority: `docs/product-specs/SPEC-PROJECT-001-product-definition.md`.",
        "",
        *definition_markdown_bullets(read_context),
        "",
        "## Scope",
        "",
        f"- First verifiable slice: {slice_description}",
        *definition_markdown_bullets(in_scope),
        "",
        "## Non-goals",
        "",
        *definition_markdown_bullets(out_of_scope),
        "",
        "## Product Trace",
        "",
        "| Product spec | Journey | P0 requirement | Acceptance criteria | Implementation tasks | Verification tasks |",
        "|---|---|---|---|---|---|",
        *trace_rows,
        "",
        "## Acceptance Criteria",
        "",
        *[f"- {text}" for text in acceptance_text],
        "",
        "## Milestones",
        "",
        "### M1 — First verifiable slice",
        "",
        f"Implement and observe: {slice_description}",
        "",
        "## Task Packets",
        "",
        f"### T1 — Implement {slice_description}",
        "",
        "#### State",
        "",
        "ready",
        "",
        "#### Task type",
        "",
        "implementation",
        "",
        "#### Depends on",
        "",
        "none",
        "",
        "#### Outcome",
        "",
        slice_description,
        "",
        "#### Non-goals",
        "",
        *definition_markdown_bullets(out_of_scope),
        "",
        "#### Read",
        "",
        "- `docs/product-specs/SPEC-PROJECT-001-product-definition.md`",
        *definition_markdown_bullets(read_context),
        "",
        "#### Allowed writes",
        "",
        *definition_markdown_bullets(allowed_writes),
        "",
        "#### Protected paths",
        "",
        *definition_markdown_bullets(protected_paths),
        "",
        "#### Acceptance",
        "",
        acceptance_field,
        "",
        "#### Verify",
        "",
        *definition_markdown_bullets(completion_evidence),
        "",
        "#### Stop conditions",
        "",
        *definition_markdown_bullets(checkpoints + risks),
        "",
        "#### Result",
        "",
        "Pending implementation evidence.",
        "",
        f"### T2 — Independently verify {slice_description}",
        "",
        "#### State",
        "",
        "blocked",
        "",
        "#### Task type",
        "",
        "verification",
        "",
        "#### Depends on",
        "",
        "T1",
        "",
        "#### Outcome",
        "",
        "Verify the integrated first slice against the linked acceptance criteria without relying on implementer explanation.",
        "",
        "#### Non-goals",
        "",
        "Redesign, scope expansion, or implementation changes without a new bounded assignment.",
        "",
        "#### Read",
        "",
        "- This plan and the finalized project definition.",
        "- The integrated implementation, tests, and observable evidence.",
        "",
        "#### Allowed writes",
        "",
        "Verification evidence only.",
        "",
        "#### Protected paths",
        "",
        "Implementation, product authority, and acceptance criteria.",
        "",
        "#### Acceptance",
        "",
        acceptance_field,
        "",
        "#### Verify",
        "",
        *definition_markdown_bullets(completion_evidence),
        "",
        "#### Stop conditions",
        "",
        "The integrated target differs from the verification target, evidence is unavailable, or acceptance conflicts with repository authority.",
        "",
        "#### Result",
        "",
        "Pending independent verification evidence.",
        "",
        "## Architecture Impact",
        "",
        *definition_markdown_bullets(
            definition_confirmed_item_text(document, 10) + definition_confirmed_item_text(document, 12)
        ),
        "",
        "## Documentation Impact",
        "",
        "| Document | Action | Reason | Owner | Status |",
        "|---|---|---|---|---|",
        "| `docs/product-specs/SPEC-PROJECT-001-product-definition.md` | none | Product authority already finalized | Main | resolved |",
        "| Other current-state documents | review | Main must declare any implementation-driven impact before approval | Main | pending |",
        "",
        "## Interfaces and Dependencies",
        "",
        *definition_markdown_bullets(
            definition_confirmed_item_text(document, 9)
            + definition_confirmed_item_text(document, 10)
            + dependencies
        ),
        "",
        "## Migration, Rollout, and Recovery",
        "",
        "Generation asserts no migration or rollout decision. Main must resolve applicable confirmed dependencies and risks before approval.",
        "",
        "## Surprises and Discoveries",
        "",
        f"- {today} — Plan generated from the validated project definition; no implementation discoveries recorded.",
        "",
        "## Decision Log",
        "",
        f"- {today} — First slice selected from confirmed definition evidence; plan remains proposed pending Main review.",
        "",
        "## Concrete Steps",
        "",
        f"1. `./dev/context --plan {plan_id}`",
        "2. Confirm Task Packet boundaries against current repository authority.",
        "3. Implement T1 and retain criterion-level evidence.",
        "4. Run T2 independently and then the canonical `./dev/verify` gate.",
        "",
        "## Validation and Evidence",
        "",
        "### Acceptance closure",
        "",
        "| Acceptance criterion | Task | Evidence path | Run ID | Manifest SHA-256 | Verified commit | Gate verdict | Review reason |",
        "|---|---|---|---|---|---|---|---|",
        *evidence_rows,
        "",
        "- Integrated target: pending",
        "- Verified commit: pending",
        f"- Acceptance IDs: {acceptance_field}",
        "- Commands and durable summaries: pending",
        "- Raw logs: `.harness/runs/` and not committed",
        "",
        "## Outcomes and Retrospective",
        "",
        "Pending implementation and independent verification.",
        "",
        "## Follow-ups",
        "",
        "- none yet",
    ]
    return title, "\n".join(lines).rstrip() + "\n"


def existing_definition_plans() -> list[Plan]:
    return [
        plan
        for plan in plan_files()
        if str(plan.metadata.get("product_spec", "")) == "SPEC-PROJECT-001"
        or str(plan.metadata.get("definition_plan", "")) == "first-vertical-slice"
    ]


def command_define_finalize(_: argparse.Namespace) -> int:
    document = parse_definition_document()
    errors, declarations = validate_definition_document(document)
    if errors:
        raise_definition_errors(errors, "finalization")
    spec_path = ROOT / DEFINITION_SPEC
    active_plans_path = ROOT / "docs" / "exec-plans" / "active"
    catalog_entries = catalog_targets()
    for path in (spec_path, active_plans_path, *(entry[0] for entry in catalog_entries)):
        ensure_safe_repository_path(path)
    if spec_path.exists():
        raise HarnessError(f"refusing to overwrite existing final specification: {DEFINITION_SPEC}")
    existing_plans = existing_definition_plans()
    if existing_plans:
        names = ", ".join(str(plan.path.relative_to(ROOT)) for plan in existing_plans)
        raise HarnessError(f"refusing to create a second first vertical-slice plan; existing target plan: {names}")
    plan_id = next_plan_id()
    provisional_title = f"First vertical slice — {definition_first_slice_description(definition_first_slice_item(document))}"
    plan_path = active_plans_path / f"{plan_id}-{slugify(provisional_title)}.md"
    ensure_safe_repository_path(plan_path)
    if plan_path.exists():
        raise HarnessError(f"refusing to overwrite existing target plan: {plan_path.relative_to(ROOT)}")
    spec_text = render_definition_spec(document)
    rendered_title, plan_text = render_first_slice_plan(document, declarations, plan_id)
    expected_plan_path = active_plans_path / f"{plan_id}-{slugify(rendered_title)}.md"
    if expected_plan_path != plan_path:
        raise HarnessError("first plan title and destination are inconsistent")

    preimages = {
        path: capture_runtime_path(path)
        for path in (spec_path, plan_path, *(entry[0] for entry in catalog_entries))
    }
    for path, preimage in preimages.items():
        if not runtime_image_matches(path, preimage):
            raise HarnessError(f"preimage changed before mutation: {path.relative_to(ROOT)}")
    records: list[tuple[Path, RuntimePathImage, RuntimePathImage]] = []
    try:
        for path, text in ((spec_path, spec_text), (plan_path, plan_text)):
            ensure_safe_repository_path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            if preimages[path].kind != "missing" or not runtime_image_matches(path, preimages[path]):
                raise HarnessError(f"preimage changed before write: {path.relative_to(ROOT)}")
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
            try:
                # The creation mode is captured before writing; live bytes are
                # never promoted to transaction-owned postimages.
                postimage = runtime_file_image(text.encode("utf-8"), stat.S_IMODE(os.fstat(descriptor).st_mode))
                records.append((path, preimages[path], postimage))
                write_runtime_bytes(descriptor, postimage.content)
            finally:
                os.close(descriptor)

        catalog_errors: list[str] = []
        documents = durable_documents(catalog_errors)
        if catalog_errors:
            raise HarnessError(
                f"cannot build document catalog with {len(catalog_errors)} metadata error(s)"
            )
        for path, kinds, grouped in catalog_entries:
            preimage = preimages[path]
            if preimage.kind != "file" or preimage.mode is None:
                raise HarnessError(f"catalog target is not a regular file: {path.relative_to(ROOT)}")
            if not runtime_image_matches(path, preimage):
                raise HarnessError(f"preimage changed before write: {path.relative_to(ROOT)}")
            original = preimage.content.decode("utf-8")
            block = catalog_markdown(documents, from_path=path, kinds=kinds, grouped=grouped)
            updated = replace_catalog(original, block, path=path).encode("utf-8")
            records.append((path, preimage, runtime_file_image(updated, preimage.mode)))
        command_docs_index(argparse.Namespace(check=False), transaction_records=records)
    except Exception as exc:
        rollback_runtime_paths(records, cause=exc, label="definition finalization")
        raise
    print(f"Finalized definition: {DEFINITION_SPEC}")
    print(f"Created first vertical-slice plan: {plan_path.relative_to(ROOT)}")
    return 0


def extract_task(plan: Plan, task_id: str) -> str:
    matches = list(TASK_HEADING.finditer(plan.text))
    for index, match in enumerate(matches):
        if match.group(1).lower() != task_id.lower():
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(plan.text)
        return plan.text[match.start() : end].rstrip() + "\n"
    raise HarnessError(f"task {task_id} not found in {plan.id}")


def command_task(args: argparse.Namespace) -> int:
    plan = locate_plan(args.plan)
    print(f"Plan: {plan.id}")
    print(f"Path: {plan.path.relative_to(ROOT)}")
    print(f"Base commit: {plan.metadata.get('base_commit', '')}")
    print()
    print(extract_task(plan, args.task), end="")
    return 0


def normalized_repository_scope(value: str) -> str:
    normalized = value.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized or "."


def document_relevance(doc: DurableDocument, *, path: str, area: str) -> bool:
    if area and doc.area.casefold() == area.casefold():
        return True
    if path:
        normalized = normalized_repository_scope(path)
        return any(
            repository_scopes_related(normalized, normalized_repository_scope(pattern))
            for pattern in doc.applies_to
            if pattern.strip()
        )
    return not area and not path


def module_contract_relevance(contract: ModuleContract, *, path: str, area: str) -> bool:
    if contract.status != "active":
        return False
    if area and contract.area.casefold() == area.casefold():
        return True
    if path:
        normalized = normalized_repository_scope(path)
        return any(repository_scopes_related(normalized, scope) for scope in contract.applies_to)
    return not area and not path


def code_map_relevance(entry: CodeMapEntry, *, path: str, area: str) -> bool:
    if area and any(item.casefold() == area.casefold() for item in entry.areas):
        return True
    if path and repository_scopes_related(normalized_repository_scope(path), entry.path):
        return True
    return not area and not path


def command_context(args: argparse.Namespace) -> int:
    config = load_config()
    document_errors: list[str] = []
    document_warnings: list[str] = []
    core = core_context_documents(document_errors)
    durable = durable_documents(document_errors, document_warnings)
    validate_durable_decisions(durable, document_errors)
    document_errors.extend(authority_conflict_errors([*core, *durable]))
    for warning in document_warnings:
        print(f"WARNING: {warning}")
    if document_errors:
        unique_errors = list(dict.fromkeys(document_errors))
        for error in unique_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise HarnessError(
            f"context routing failed with {len(unique_errors)} authority metadata or conflict error(s)"
        )
    documents = [
        document
        for document in [*core, *durable]
        if authority_in_context(
            document,
            include_drafts=bool(args.include_drafts),
            include_history=bool(args.include_history),
        )
    ]
    model_errors: list[str] = []
    _, contracts, code_entries = code_map_model(config, model_errors)
    if model_errors:
        for error in model_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise HarnessError(f"context routing failed with {len(model_errors)} code-map metadata error(s)")

    path_filter = args.path or ""
    area_filter = args.area or ""
    selected_plan: Plan | None = locate_plan(args.plan) if args.plan else None
    if selected_plan is not None:
        selected_is_history = "completed" in selected_plan.path.relative_to(ROOT).parts
        if selected_is_history and not args.include_history:
            raise HarnessError(
                f"selected plan {selected_plan.id} is historical; retry with --include-history"
            )
    selected_authority: DurableDocument | None = None
    if selected_plan is not None:
        product_spec = str(selected_plan.metadata.get("product_spec", "")).strip()
        selected_authority = next((doc for doc in documents if doc.id == product_spec), None)

    print("# Repository context")
    print(f"- Root: `{ROOT}`")
    print(f"- Project: {config.project.get('name', ROOT.name)}")
    print(f"- Kind: {config.project.get('kind', 'other')}")
    print(f"- Baseline: {config.baseline}")
    print(f"- Command configuration: {config.configuration}")
    print(f"- Lifecycle: {config.lifecycle}")
    print(f"- Primary language: {config.project.get('primary_language', 'unknown')}")
    print(f"- Runtime: {config.project.get('runtime', 'unknown')}")
    capabilities = config.document_capabilities()
    print(f"- Document capabilities: {', '.join(sorted(capabilities)) or 'none'}")
    print("- Operating contract: `AGENTS.md`")
    print("- Knowledge map: `docs/README.md`")
    active_architecture = next(
        (document for document in core if document.path.relative_to(ROOT) == Path("ARCHITECTURE.md") and document.status == "active"),
        None,
    )
    if active_architecture is not None:
        print("- Current architecture authority is active.")
    else:
        print("- Current architecture authority is not active.")
    if selected_plan is not None:
        print("\n## Selected plan")
        print(f"- `{selected_plan.path.relative_to(ROOT)}` — {selected_plan.title} [{selected_plan.status}]")
        product_spec = str(selected_plan.metadata.get("product_spec", "")).strip()
        if selected_authority is not None:
            print(f"- Product authority: `{selected_authority.path.relative_to(ROOT)}` — {selected_authority.id}")
        elif product_spec:
            print(f"- Product authority: unresolved `{product_spec}`")

    print("\n## Relevant module contracts")
    relevant_contracts = [
        contract
        for contract in contracts
        if module_contract_relevance(contract, path=path_filter, area=area_filter)
    ]
    if not relevant_contracts:
        print("- None matched.")
    else:
        for contract in relevant_contracts:
            scopes = ", ".join(f"`{scope}`" for scope in contract.applies_to)
            print(f"- `{contract.path.relative_to(ROOT)}` — {contract.id} [{contract.status}] {contract.summary}; paths: {scopes}")

    print("\n## Relevant code-map entries")
    relevant_entries = [
        entry for entry in code_entries if code_map_relevance(entry, path=path_filter, area=area_filter)
    ]
    if not relevant_entries:
        print("- None matched.")
    else:
        for entry in relevant_entries:
            evidence = ", ".join(entry.evidence)
            areas = ", ".join(entry.areas) or "unknown"
            print(f"- `{entry.path}` — evidence: {evidence}; areas: {areas}; map: `{CODE_MAP_PATH}`")

    print("\n## Relevant durable documents")
    relevant = [
        doc for doc in documents if document_relevance(doc, path=path_filter, area=area_filter)
    ]
    if selected_authority is not None and selected_authority not in relevant:
        relevant.append(selected_authority)
    relevant.sort(key=lambda doc: str(doc.path.relative_to(ROOT)))
    if not relevant:
        print("- None matched. Read the stable entry documents and expand only with evidence.")
    else:
        for doc in relevant:
            print(f"- `{doc.path.relative_to(ROOT)}` — {doc.id} [{doc.status}] {doc.summary}")
    if (
        args.include_drafts
        and (ROOT / DEFINITION_DRAFT).exists()
        and (not path_filter and area_filter.casefold() in {"", "product", "definition"})
    ):
        print(f"- `{DEFINITION_DRAFT}` — persisted project-definition session [draft]")

    all_plans = plan_files()
    print("\n## Active plans")
    active = []
    if (
        selected_plan is not None
        and "active" in selected_plan.path.relative_to(ROOT).parts
        and selected_plan.status in ACTIVE_PLAN_STATES
    ):
        active.append(selected_plan)
    if area_filter:
        active = [plan for plan in active if str(plan.metadata.get("area", "")).casefold() == area_filter.casefold()]
    if not active:
        print("- None")
    else:
        for plan in active:
            print(f"- `{plan.path.relative_to(ROOT)}` — {plan.title} [{plan.status}]")
    if args.include_history:
        print("\n## Historical plans")
        historical = [
            plan
            for plan in all_plans
            if "completed" in plan.path.relative_to(ROOT).parts and plan.status in COMPLETED_PLAN_STATES
        ]
        if area_filter:
            historical = [
                plan
                for plan in historical
                if str(plan.metadata.get("area", "")).casefold() == area_filter.casefold()
            ]
        if not historical:
            print("- None")
        else:
            for plan in historical:
                print(f"- `{plan.path.relative_to(ROOT)}` — {plan.title} [{plan.status}]")
    print("\n## Deterministic commands")
    for name in ("bootstrap", "run", "check", "verify", "smoke", "architecture"):
        group = config.command_group(name)
        if group:
            print(f"- {name}: " + " ; ".join(f"`{command_display(command)}`" for command in group))
        else:
            print(f"- {name}: not configured")
    return 0


def safe_review_reason(value: object) -> str:
    reason = str(value or "").strip()
    if not definition_value_is_concrete(reason):
        raise HarnessError("Gate REVIEW requires a genuine non-empty --accept-review reason")
    if any(character in reason for character in "\r\n\x00|`") or any(ord(character) < 32 for character in reason):
        raise HarnessError("--accept-review must be one safe Markdown-table line without pipes or backticks")
    return reason


def load_verification_artifact(path: Path, label: str) -> dict[str, object]:
    ensure_safe_repository_path(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HarnessError(f"cannot read finalized {label}: {portable_detail(exc)}") from exc
    if not isinstance(value, dict):
        raise HarnessError(f"finalized {label} must be a JSON object")
    return value


def validate_close_verification(
    result: VerificationResult,
    *,
    base_commit: str,
    head: str,
    target: str,
) -> tuple[dict[str, object], dict[str, object]]:
    manifest_path = result.run.path / "manifest.json"
    gate_path = result.run.path / "gate.json"
    manifest = load_verification_artifact(manifest_path, "verification manifest")
    gate = load_verification_artifact(gate_path, "Gate evidence")
    manifest_hash = sha256_file(manifest_path)
    if manifest_hash != result.manifest_sha256:
        raise HarnessError("finalized verification manifest hash differs from the in-memory result")
    if str(gate.get("manifest_sha256", "")) != manifest_hash:
        raise HarnessError("Gate evidence does not bind the finalized verification manifest hash")
    if gate != result.gate:
        raise HarnessError("finalized Gate evidence differs from the in-memory verification result")
    if str(manifest.get("run_id", "")) != result.run.run_id:
        raise HarnessError("verification manifest run ID does not match its run directory")
    if str(manifest.get("status", "")) != result.verification_status:
        raise HarnessError("verification manifest status differs from the in-memory result")
    target_evidence = manifest.get("target_evidence")
    if not isinstance(target_evidence, dict) or gate.get("target_evidence") != target_evidence:
        raise HarnessError("manifest and Gate target evidence do not match")
    expected = {
        "actual_head_sha": head,
        "base_sha": base_commit,
        "intended_head_sha": head,
        "target": target,
    }
    for field, value in expected.items():
        if str(target_evidence.get(field, "")) != value:
            raise HarnessError(f"verification target field {field} does not match the closing plan")
    if target_evidence.get("head_matches_intended") is not True:
        raise HarnessError("verification did not confirm the intended closing HEAD")
    if target_evidence.get("clean") is not True:
        raise HarnessError("verification did not confirm a clean closing worktree")
    return manifest, gate


def bind_traceable_verification_rows(
    text: str,
    *,
    run_id: str,
    manifest_hash: str,
    verified_commit: str,
    verdict: str,
    review_reason: str,
) -> str:
    metadata, _ = parse_frontmatter_text(text)
    if str(metadata.get("traceability", "")).strip() != "1":
        return text
    lines = text.splitlines()
    heading_index = next(
        (index for index, line in enumerate(lines) if line.strip() == "## Validation and Evidence"),
        None,
    )
    if heading_index is None:
        raise HarnessError("traceable plan is missing its Validation and Evidence section")
    header = "| " + " | ".join(ACCEPTANCE_EVIDENCE_HEADERS) + " |"
    table_index = next(
        (
            index
            for index in range(heading_index + 1, len(lines))
            if lines[index].strip().casefold() == header.casefold()
        ),
        None,
    )
    if table_index is None or table_index + 2 >= len(lines):
        raise HarnessError("traceable plan is missing its acceptance evidence table")
    row_index = table_index + 2
    bound = 0
    evidence_path = f".harness/runs/{run_id}/manifest.json"
    row_reason = review_reason if verdict == "REVIEW" else "none"
    while row_index < len(lines) and lines[row_index].strip().startswith("|"):
        cells = [cell.strip() for cell in lines[row_index].strip().strip("|").split("|")]
        if len(cells) != len(ACCEPTANCE_EVIDENCE_HEADERS):
            raise HarnessError("traceable plan acceptance evidence table has an invalid row")
        lines[row_index] = (
            f"| {cells[0]} | {cells[1]} | `{evidence_path}` | `{run_id}` | "
            f"`{manifest_hash}` | `{verified_commit}` | `{verdict}` | {row_reason} |"
        )
        bound += 1
        row_index += 1
    if bound == 0:
        raise HarnessError("traceable plan acceptance evidence table has no criterion rows")
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def command_close_plan(args: argparse.Namespace) -> int:
    plan = locate_plan(args.plan, active_only=True)
    if plan.status != "verifying":
        raise HarnessError(f"plan must be in status 'verifying' before close; current status is '{plan.status}'")
    ensure_safe_repository_path(plan.path)
    if not plan.path.is_file():
        raise HarnessError("close-plan requires the active plan to be a regular file")
    git_marker = ROOT / ".git"
    if not git_marker.exists() or git_marker.is_symlink():
        raise HarnessError("close-plan requires safe local Git metadata")
    if git_output("status", "--porcelain"):
        raise HarnessError("close-plan requires a clean working tree so verification can bind to one integrated commit")
    head = git_head()
    if re.fullmatch(r"[0-9a-fA-F]{7,64}", head) is None:
        raise HarnessError("cannot determine the integrated Git commit")
    declared = str(plan.metadata.get("integrated_commit", "")).strip()
    if declared not in {"HEAD", head}:
        raise HarnessError(
            f"plan integrated_commit ({declared or 'missing'}) must be HEAD or match current HEAD ({head}); "
            "update and commit the verifying plan before closing"
        )
    base_commit = str(plan.metadata.get("base_commit", "")).strip()
    if re.fullmatch(r"[0-9a-fA-F]{7,64}", base_commit) is None:
        raise HarnessError("close-plan requires an explicit local base_commit Git object ID")

    completed_dir = ROOT / "docs" / "exec-plans" / "completed"
    destination = completed_dir / plan.path.name
    ensure_safe_repository_path(destination)
    if destination.exists():
        raise HarnessError(f"completed plan already exists: {destination.relative_to(ROOT)}")
    source_preimage = capture_runtime_path(plan.path)
    if source_preimage.kind != "file" or source_preimage.content is None or source_preimage.mode is None:
        raise HarnessError("close-plan requires a regular active-plan preimage")
    original_bytes = source_preimage.content
    original_mode = source_preimage.mode
    try:
        original_text = original_bytes.decode("utf-8")
    except UnicodeError as exc:
        raise HarnessError("active plan is not valid UTF-8") from exc

    result = run_verification(base_sha=base_commit, intended_head=head, target=plan.id)
    _, gate = validate_close_verification(
        result,
        base_commit=base_commit,
        head=head,
        target=plan.id,
    )
    if git_head() != head:
        raise HarnessError("closing HEAD changed during verification; the plan remains active")
    if git_output("status", "--porcelain"):
        raise HarnessError("verification changed the working tree; the plan remains active")
    if plan.path.read_bytes() != original_bytes:
        raise HarnessError("the active plan changed during verification; the plan remains active")

    verdict = str(gate.get("verdict", "INCONCLUSIVE")).upper()
    if verdict == "BLOCK":
        raise HarnessError("Gate BLOCK prevents plan closure and cannot be overridden")
    if verdict == "INCONCLUSIVE":
        raise HarnessError("Gate INCONCLUSIVE prevents plan closure and cannot be overridden")
    if verdict not in {"PASS", "REVIEW"}:
        raise HarnessError(f"unsupported Gate verdict prevents plan closure: {verdict}")
    review_reason = safe_review_reason(args.accept_review) if verdict == "REVIEW" else ""

    updated = update_frontmatter(
        original_text,
        {
            "status": "complete",
            "updated": date.today().isoformat(),
            "integrated_commit": head,
            "verified_commit": head,
            "verification_run": json.dumps(result.run.run_id),
            "manifest_sha256": json.dumps(result.manifest_sha256),
            "gate_verdict": json.dumps(verdict),
            "gate_review_reason": json.dumps(review_reason, ensure_ascii=False),
        },
    )
    updated = bind_traceable_verification_rows(
        updated,
        run_id=result.run.run_id,
        manifest_hash=result.manifest_sha256,
        verified_commit=head,
        verdict=verdict,
        review_reason=review_reason,
    )

    completed_preimage = capture_runtime_path(completed_dir)
    records: list[tuple[Path, RuntimePathImage, RuntimePathImage]] = []
    if completed_preimage.kind == "missing":
        completed_dir.mkdir(parents=True)
        records.append((completed_dir, completed_preimage, capture_runtime_path(completed_dir)))
    elif completed_preimage.kind != "directory":
        raise HarnessError("completed plan path is not a regular directory")
    destination_preimage = capture_runtime_path(destination)
    if destination_preimage.kind != "missing":
        raise HarnessError(f"completed plan already exists: {destination.relative_to(ROOT)}")
    destination_postimage = runtime_file_image(updated.encode("utf-8"), original_mode)
    source_postimage = RuntimePathImage("missing", None, None, None)
    records.extend(
        (
            (destination, destination_preimage, destination_postimage),
            (plan.path, source_preimage, source_postimage),
        )
    )
    try:
        if not runtime_image_matches(destination, destination_preimage):
            raise HarnessError("completed plan preimage changed before write")
        destination.write_bytes(destination_postimage.content or b"")
        os.chmod(destination, original_mode)
        if not runtime_image_matches(plan.path, source_preimage):
            raise HarnessError("active plan preimage changed before removal")
        plan.path.unlink()
        command_docs_index(argparse.Namespace(check=True))
        command_docs_check(argparse.Namespace(strict=True))
        command_plan_check(argparse.Namespace(strict=True))
    except BaseException as exc:
        rollback_runtime_paths(records, cause=exc, label="plan closure")
        raise
    print(
        f"Closed {plan.id} at verified commit {head} with Gate {verdict}. "
        f"Evidence: {result.run.path.relative_to(ROOT)}"
    )
    print(f"Moved to {destination.relative_to(ROOT)}. Commit the completion record separately.")
    return 0


def parse_iso_date(value: object) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def path_pattern_matches(pattern: str) -> bool:
    normalized = pattern.lstrip("./")
    if not any(char in normalized for char in "*?["):
        return (ROOT / normalized).exists()
    for path in ROOT.rglob("*"):
        relative = str(path.relative_to(ROOT)).replace(os.sep, "/")
        if fnmatch.fnmatch(relative, normalized):
            return True
    return False


def command_garden(args: argparse.Namespace) -> int:
    config = load_config()
    warnings: list[str] = []
    max_lines = int(config.policy.get("agents_max_lines", 140))
    agents = ROOT / "AGENTS.md"
    if agents.exists():
        lines = len(agents.read_text(encoding="utf-8").splitlines())
        if lines > max_lines:
            warnings.append(f"OVERSIZED-ENTRY: AGENTS.md has {lines} lines (maximum {max_lines})")
    stale_days = int(config.policy.get("stale_plan_days", 21))
    today = date.today()
    for plan in plan_files():
        if "active" not in plan.path.relative_to(ROOT).parts:
            continue
        updated = parse_iso_date(plan.metadata.get("updated"))
        if updated and (today - updated).days > stale_days:
            warnings.append(f"STALE-PLAN: {plan.path.relative_to(ROOT)} has not been updated for {(today - updated).days} days")
    metadata_errors: list[str] = []
    documents = durable_documents(metadata_errors)
    warnings.extend(f"DOC-METADATA: {error}" for error in metadata_errors)
    for doc in documents:
        for pattern in doc.applies_to:
            if pattern and not path_pattern_matches(pattern):
                warnings.append(f"STALE-PATH: {doc.id} applies_to pattern matches nothing: {pattern}")
    if config.lifecycle == "active":
        for path in (
            ROOT / "ARCHITECTURE.md",
            ROOT / "docs" / "PRODUCT.md",
            ROOT / "docs" / "DESIGN.md",
            ROOT / "docs" / "QUALITY.md",
            ROOT / "docs" / "SECURITY.md",
        ):
            if path.exists() and PLACEHOLDER in path.read_text(encoding="utf-8"):
                warnings.append(f"PLACEHOLDER: {path.relative_to(ROOT)} still contains {PLACEHOLDER}")
    deprecated = [doc for doc in documents if doc.status in {"deprecated", "superseded"}]
    deprecated_paths = {doc.path for doc in deprecated}
    current_paths = [
        path for path in (ROOT / "docs").rglob("*.md") if "completed" not in path.parts and path not in deprecated_paths
    ]
    for doc in deprecated:
        for path in current_paths:
            if doc.id in path.read_text(encoding="utf-8", errors="ignore"):
                warnings.append(f"DEPRECATED-REFERENCE: {path.relative_to(ROOT)} still references {doc.id}")
                break
    if not warnings:
        print("Garden check found no current maintenance candidates.")
        return 0
    for warning in warnings:
        print(f"WARNING: {warning}")
    print(f"Garden check found {len(warnings)} maintenance candidate(s); it made no changes.")
    if args.strict:
        raise HarnessError("garden strict mode failed because maintenance candidates exist")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    context = sub.add_parser("context", help="print a small, routed repository context")
    context.add_argument("--path", default="")
    context.add_argument("--area", default="")
    context.add_argument("--plan", default="")
    context.add_argument(
        "--include-drafts",
        action="store_true",
        help="include draft current-state/product/design/runbook documents and proposed decisions",
    )
    context.add_argument(
        "--include-history",
        action="store_true",
        help="include deprecated, superseded, and rejected authority plus completed plans",
    )
    context.set_defaults(func=command_context)
    define = sub.add_parser("define", help="inspect, validate, or finalize the project definition")
    define_actions = define.add_subparsers(dest="define_action", required=True)
    define_actions.add_parser("status", help="compute confirmed sections and the next unresolved section").set_defaults(
        func=command_define_status
    )
    define_actions.add_parser("validate", help="validate definition structure, evidence, and trace links").set_defaults(
        func=command_define_validate
    )
    define_actions.add_parser("finalize", help="create the final definition spec and first vertical-slice plan").set_defaults(
        func=command_define_finalize
    )
    sub.add_parser("audit", help="inventory repository authority without executing commands or writing files").set_defaults(
        func=command_audit
    )
    code_map = sub.add_parser("code-map", help="generate or check the evidence-backed repository code map")
    code_map.add_argument("--check", action="store_true")
    code_map.set_defaults(func=command_code_map)
    sub.add_parser("bootstrap", help="run configured dependency setup commands").set_defaults(func=command_bootstrap)
    sub.add_parser("run", help="run the configured application command").set_defaults(func=command_run)
    sub.add_parser("check", help="run the fast local feedback loop").set_defaults(func=command_check)
    sub.add_parser("verify", help="run the canonical completion gate").set_defaults(func=command_verify)
    sub.add_parser("smoke", help="run configured observable smoke checks").set_defaults(func=command_smoke)
    sub.add_parser("security-check", help="reject tracked secrets and sensitive local files").set_defaults(func=command_security_check)
    docs_index = sub.add_parser("docs-index", help="generate or check the durable document catalog")
    docs_index.add_argument("--check", action="store_true")
    docs_index.set_defaults(func=command_docs_index)
    docs_check = sub.add_parser("docs-check", help="validate document structure, metadata, and links")
    docs_check.add_argument("--strict", action="store_true")
    docs_check.set_defaults(func=command_docs_check)
    plan_check = sub.add_parser("plan-check", help="validate ExecPlan lifecycle and Task Packets")
    plan_check.add_argument("--strict", action="store_true")
    plan_check.set_defaults(func=command_plan_check)
    architecture = sub.add_parser("architecture-check", help="validate architecture documentation and configured boundaries")
    architecture.add_argument("--strict", action="store_true")
    architecture.set_defaults(func=command_architecture_check)
    new_plan = sub.add_parser("new-plan", help="create an active ExecPlan from the repository template")
    new_plan.add_argument("title", nargs="+")
    new_plan.add_argument("--area", default="")
    new_plan.set_defaults(func=command_new_plan)
    task = sub.add_parser("task", help="print one bounded Task Packet for delegation")
    task.add_argument("plan")
    task.add_argument("task")
    task.set_defaults(func=command_task)
    close = sub.add_parser("close-plan", help="verify an integrated commit and archive a completed plan")
    close.add_argument("plan")
    close.add_argument(
        "--accept-review",
        default="",
        help="explicit human rationale required only when the finalized Gate verdict is REVIEW",
    )
    close.set_defaults(func=command_close_plan)
    garden = sub.add_parser("garden", help="report stale plans, documents, paths, and references without changing them")
    garden.add_argument("--strict", action="store_true")
    garden.set_defaults(func=command_garden)
    return parser


def main() -> int:
    if RUNTIME_ROOT_IS_SYMLINKED:
        print(
            "ERROR: refusing to run through a symlinked project root or parent",
            file=sys.stderr,
        )
        return 2
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
