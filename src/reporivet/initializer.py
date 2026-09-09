from __future__ import annotations

import difflib
import hashlib
import html
import json
import os
import re
import stat
import tempfile
import unicodedata
from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from typing import Iterable

from . import __version__

PACKAGE_ROOT = Path(__file__).resolve().parent
ASSETS = PACKAGE_ROOT / "assets" / "project"
AGENTS_START = "<!-- reporivet:entrypoints:start -->"
AGENTS_END = "<!-- reporivet:entrypoints:end -->"
CLAUDE_START = "<!-- reporivet:entrypoints:claude:start -->"
CLAUDE_END = "<!-- reporivet:entrypoints:claude:end -->"
LEGACY_AGENTS_START = "<!-- reporivet:start -->"
LEGACY_AGENTS_END = "<!-- reporivet:end -->"
LEGACY_VERSION = "0.2"
SOURCE_REPOSITORY_URL = "https://github.com/gkrtjd99/Reporivet"
IGNORED_DIRECTORIES = frozenset({
    ".git", ".harness", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox",
    ".venv", "__pycache__", "build", "coverage", "dist", "node_modules", "out",
    "target", "vendor",
})
MANIFESTS = frozenset({
    "Cargo.toml", "Gemfile", "Package.swift", "Pipfile", "build.gradle",
    "build.gradle.kts", "composer.json", "go.mod", "package.json", "pom.xml",
    "pyproject.toml", "requirements.txt",
})
LOCKFILES = frozenset({
    "Cargo.lock", "Gemfile.lock", "Package.resolved", "Pipfile.lock", "bun.lock",
    "bun.lockb", "composer.lock", "go.sum", "gradle.lockfile", "package-lock.json",
    "pnpm-lock.yaml", "poetry.lock", "uv.lock", "yarn.lock",
})
SOURCE_ROOTS = ("src", "app", "lib", "packages", "services")
TEST_ROOTS = ("tests", "test", "spec", "__tests__")
ENTRYPOINT_ROOTS = ("dev", "scripts", "bin")
MAX_OBSERVED_PATHS = 80
MAX_OBSERVED_DEPTH = 3
MAX_VISITED_ENTRIES = 512
MAX_EXCLUSIONS = 64


class InitError(RuntimeError):
    """Raised when an operation cannot complete safely."""


@dataclass
class ChangeSet:
    created: list[Path] = field(default_factory=list)
    updated: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    fingerprint: str = ""

    def print(
        self,
        root: Path,
        *,
        dry_run: bool = False,
        operations: tuple[_Operation, ...] = (),
    ) -> None:
        print("Planned Reporivet changes" if dry_run else "Applied Reporivet changes")
        for label, paths in (("created", self.created), ("updated", self.updated), ("skipped", self.skipped)):
            print(f"\n{label}:")
            for path in paths or [Path("(none)")]:
                if path.name == "(none)":
                    print("  - none")
                else:
                    print(f"  - {path.relative_to(root)}")
        if not self.created and not self.updated:
            print("\nNo changes (no-op).")
        if dry_run:
            print("\n주의: 아래 diff는 사람이 검토하는 이스케이프된 미리보기이며, 적용 가능한 patch가 아닙니다.")
            print("fingerprint는 승인·잠금·다음 실행 결과를 보장하지 않습니다.")
            print("\nUnified diff:")
            diff = _operations_diff(operations)
            if diff:
                print(diff, end="" if diff.endswith("\n") else "\n")
            else:
                print("(no changes)")
        if self.fingerprint:
            print(f"\nMutation plan fingerprint: {self.fingerprint}")


@dataclass(frozen=True)
class _Image:
    kind: str
    mode: int | None
    digest: str | None
    content: bytes | None = None


@dataclass(frozen=True)
class _Operation:
    root: Path
    relative: str
    before: _Image
    after: _Image

    @property
    def path(self) -> Path:
        return self.root / self.relative


def symlink_component(path: Path) -> Path | None:
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            return candidate
    return None


def validate_root(root: Path, *, create: bool = False, dry_run: bool = False) -> Path:
    expanded = root.expanduser()
    raw = expanded if expanded.is_absolute() else Path.cwd() / expanded
    component = symlink_component(raw)
    if component is not None:
        raise InitError(f"refusing to use a symlinked project root or parent: {root} (via {component})")
    absolute = Path(os.path.abspath(raw))
    if not absolute.exists():
        if not create:
            raise InitError(f"project root does not exist: {root}")
        if not absolute.parent.is_dir():
            raise InitError(f"project root parent is unavailable: {absolute.parent}; create the parent directory first")
        if not dry_run:
            absolute.mkdir(parents=True, exist_ok=False)
    elif not absolute.is_dir():
        raise InitError(f"project root is not a directory: {root}")
    return absolute


def ensure_safe_write_path(path: Path) -> None:
    component = symlink_component(path)
    if component is not None:
        raise InitError(f"refusing to write through symlink path: {path} (via {component})")


_PLACEHOLDER = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")


def read_asset(relative: str, values: dict[str, str] | None = None) -> str:
    path = ASSETS / relative
    if not path.is_file():
        raise InitError(f"missing packaged asset: {relative}")
    text = path.read_text(encoding="utf-8")
    replacements = values or {}
    return _PLACEHOLDER.sub(lambda match: replacements.get(match.group(1), match.group(0)), text)


def _image(path: Path, root: Path) -> _Image:
    ensure_safe_write_path(path)
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return _Image("missing", None, None)
    except OSError as exc:
        raise InitError(f"cannot inspect {path.relative_to(root)}: {exc}") from exc
    mode = stat.S_IMODE(metadata.st_mode)
    if stat.S_ISDIR(metadata.st_mode):
        return _Image("directory", mode, None)
    if not stat.S_ISREG(metadata.st_mode):
        raise InitError(f"mutation target is not a regular file: {path.relative_to(root)}")
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise InitError(f"cannot read {path.relative_to(root)}: {exc}") from exc
    return _Image("file", mode, hashlib.sha256(content).hexdigest(), content)


def _same(path: Path, expected: _Image, root: Path) -> bool:
    try:
        current = _image(path, root)
    except InitError:
        return False
    return (current.kind, current.mode, current.digest) == (expected.kind, expected.mode, expected.digest)


def _operation(root: Path, relative: str, content: bytes, *, before: _Image | None = None) -> _Operation:
    path = root / relative
    frozen = before if before is not None else _image(path, root)
    after = _Image("file", frozen.mode if frozen.mode is not None else 0o644, hashlib.sha256(content).hexdigest(), content)
    return _Operation(root, relative, frozen, after)


def _escape_terminal(text: str) -> str:
    """제어 문자와 bidi 문자를 실행되지 않는 표시 문자열로 바꾼다."""
    escaped: list[str] = []
    for char in text:
        category = unicodedata.category(char)
        if char == "\n":
            escaped.append(char)
        elif category == "Cc":
            names = {"\r": "\\r", "\t": "\\t", "\b": "\\b", "\f": "\\f", "\v": "\\v"}
            escaped.append(names.get(char, f"\\x{ord(char):02x}"))
        elif category == "Cf":
            escaped.append(f"\\u{ord(char):04x}")
        else:
            escaped.append(char)
    return "".join(escaped)


def _operations_diff(operations: Iterable[_Operation]) -> str:
    """불변 operation 이미지의 before/after에서 실제 unified diff를 만든다."""
    rendered: list[str] = []
    for operation in sorted(operations, key=lambda item: item.relative):
        before = operation.before.content or b""
        after = operation.after.content or b""
        if before == after and operation.before.kind == operation.after.kind and operation.before.mode == operation.after.mode:
            continue
        before_lines = re.findall(r"[^\n]*\n|[^\n]+$", before.decode("utf-8"))
        after_lines = re.findall(r"[^\n]*\n|[^\n]+$", after.decode("utf-8"))
        lines = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=operation.relative,
            tofile=operation.relative,
        )
        for line in lines:
            rendered.append(_escape_terminal(line))
            if not line.endswith("\n"):
                rendered.append("\n\\ No newline at end of file\n")
    return "".join(rendered)


def _fingerprint(operations: Iterable[_Operation]) -> str:
    rows = []
    for op in sorted(operations, key=lambda item: item.relative):
        rows.append({
            "path": op.relative,
            "preimage": {"type": op.before.kind, "mode": op.before.mode, "sha256": op.before.digest},
            "postimage": {"type": op.after.kind, "mode": op.after.mode, "sha256": op.after.digest},
        })
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _atomic_write(op: _Operation) -> None:
    path = op.path
    ensure_safe_write_path(path)
    if not _same(path, op.before, op.root):
        raise InitError(f"preimage changed before write: {op.relative}")
    if op.after.content is None or op.after.mode is None:
        raise InitError(f"mutation image is incomplete: {op.relative}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".reporivet-write-", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        try:
            view = memoryview(op.after.content)
            while view:
                count = os.write(descriptor, view)
                if count <= 0:
                    raise OSError("short write while applying mutation")
                view = view[count:]
            os.fchmod(descriptor, op.after.mode)
        finally:
            os.close(descriptor)
        ensure_safe_write_path(path)
        if not _same(path, op.before, op.root):
            raise InitError(f"preimage changed before write: {op.relative}")
        if op.before.kind == "missing":
            os.link(temporary_path, path)
        else:
            os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _restore_owned(op: _Operation) -> bool:
    """Restore only an unchanged postimage; return false on divergence."""
    if _same(op.path, op.before, op.root):
        return True
    if not _same(op.path, op.after, op.root):
        return False
    if op.before.kind == "missing":
        ensure_safe_write_path(op.path)
        op.path.unlink()
        return _same(op.path, op.before, op.root)
    if op.before.kind == "file" and op.before.content is not None:
        _atomic_write(_Operation(op.root, op.relative, op.after, op.before))
        return _same(op.path, op.before, op.root)
    return False


def _apply(operations: tuple[_Operation, ...]) -> None:
    for op in operations:
        if not _same(op.path, op.before, op.root):
            raise InitError(f"preimage changed before mutation: {op.relative}")
    attempted: list[_Operation] = []
    try:
        for op in operations:
            if _same(op.path, op.after, op.root):
                continue
            attempted.append(op)
            _atomic_write(op)
    except BaseException as exc:
        preserved: list[str] = []
        for op in reversed(attempted):
            try:
                if not _restore_owned(op):
                    preserved.append(op.relative)
            except BaseException:
                preserved.append(op.relative)
        if preserved:
            raise InitError(f"mutation failed ({exc}); rollback incomplete; preserved path(s): {', '.join(sorted(set(preserved))) }") from exc
        raise InitError(f"mutation failed and was rolled back: {exc}") from exc


def _managed_span(text: str, start: str, end: str) -> tuple[int, int] | None:
    """Find exact standalone marker lines while ignoring fenced/inline examples."""
    starts: list[int] = []
    ends: list[int] = []
    malformed = False
    offset = 0
    fence: tuple[str, int] | None = None
    # Markdown 행 경계는 LF/CR/CRLF뿐이며 Python의 다른 Unicode 구분자는 포함하지 않는다.
    for match in re.finditer(r"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+$", text):
        line = match.group()
        logical = line.rstrip("\r\n")
        if fence is None:
            fence_match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", logical)
            if fence_match and not (fence_match.group(1)[0] == "`" and "`" in fence_match.group(2)):
                fence = (fence_match.group(1)[0], len(fence_match.group(1)))
                offset += len(line)
                continue
            if logical == start:
                starts.append(offset)
            elif logical == end:
                ends.append(offset)
            elif logical.lstrip().startswith((start[:-4], end[:-4])):
                malformed = True
        else:
            char, count = fence
            if re.match(r"^ {0,3}" + re.escape(char) + "{" + str(count) + r",}[ \t]*$", logical):
                fence = None
        offset += len(line)
    if fence is not None:
        raise InitError("existing instruction file has an unclosed Markdown fence")
    if malformed or (starts or ends) and (len(starts) != 1 or len(ends) != 1):
        raise InitError(f"existing file has malformed managed markers: {start} / {end}")
    if not starts and not ends:
        return None
    if len(starts) != 1 or len(ends) != 1 or ends[0] < starts[0]:
        raise InitError(f"existing file has malformed managed markers: {start} / {end}")
    return starts[0], ends[0] + len(end)


def _upsert(original: bytes, block: str, start: str, end: str) -> bytes:
    try:
        text = original.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InitError("existing instruction file is not valid UTF-8") from exc
    span = _managed_span(text, start, end)
    replacement = block.rstrip()
    if span is not None:
        return (text[:span[0]] + replacement + text[span[1]:]).encode("utf-8")
    separator = "" if not text else ("" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n"))
    return (text + separator + replacement + "\n").encode("utf-8")


def _reserved_head(path: Path, label: str, *, limit: int = 8192) -> str | None:
    """Read only a bounded legacy probe; an uncheckable reserved path is an error."""
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise InitError(f"reserved legacy probe cannot inspect {label}: {exc}") from exc
    if symlink_component(path) is not None or stat.S_ISLNK(metadata.st_mode):
        raise InitError(f"reserved legacy probe is a symlink: {label}")
    if not stat.S_ISREG(metadata.st_mode):
        raise InitError(f"reserved legacy probe is not a regular file: {label}")
    try:
        with path.open("rb") as stream:
            data = stream.read(limit)
    except OSError as exc:
        raise InitError(f"reserved legacy probe cannot read {label}: {exc}") from exc
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InitError(f"reserved legacy probe is not valid UTF-8: {label}") from exc


def _legacy_reason(root: Path) -> str | None:
    version = _reserved_head(root / ".reporivet-version", ".reporivet-version")
    if version is not None:
        value = version.strip()
        if re.fullmatch(r"0\.2(?:\.\d+)*", value) or "reporivet:managed version=0.2" in value:
            return ".reporivet-version identifies the released 0.2 target"
    runtime = _reserved_head(root / "dev" / "harness.py", "dev/harness.py")
    if runtime is not None and "reporivet:managed version=0.2" in runtime:
        return "dev/harness.py is a released 0.2 managed runtime"
    agents = root / "AGENTS.md"
    if agents.exists() and not agents.is_symlink():
        try:
            metadata = agents.lstat()
        except OSError as exc:
            raise InitError(f"cannot inspect AGENTS.md for legacy ownership: {exc}") from exc
        if stat.S_ISREG(metadata.st_mode):
            try:
                text = agents.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                raise InitError("AGENTS.md is not valid UTF-8 during legacy ownership probe") from exc
            except OSError as exc:
                raise InitError(f"cannot inspect AGENTS.md for legacy ownership: {exc}") from exc
            span = _managed_span(text, LEGACY_AGENTS_START, LEGACY_AGENTS_END)
            if span is not None and ("dev/harness.toml" in text[span[0]:span[1]] or "repository-local runtime" in text[span[0]:span[1]]):
                return "AGENTS.md contains the released 0.2 managed operating block"
    return None


def _observed_paths(root: Path, *, include_instructions: bool = True) -> tuple[list[str], list[str]]:
    paths: list[str] = []
    exclusions: list[str] = []
    pending = [root]
    visited = 0
    truncated = False

    def exclude(relative: str, reason: str) -> None:
        exclusions.append(f"{relative} ({reason})")

    while pending and visited < MAX_VISITED_ENTRIES:
        current = pending.pop()
        try:
            with os.scandir(current) as scan:
                entries = []
                for entry in islice(scan, MAX_VISITED_ENTRIES - visited):
                    entries.append(entry)
                    visited += 1
        except OSError as exc:
            relative = current.relative_to(root).as_posix() or "."
            exclude(relative, f"directory unreadable: {exc}")
            continue
        entries.sort(key=lambda item: item.name)
        children: list[Path] = []
        for entry in entries:
            path = Path(entry.path)
            relative = path.relative_to(root).as_posix()
            try:
                is_link = entry.is_symlink()
                is_dir = entry.is_dir(follow_symlinks=False)
                is_file = entry.is_file(follow_symlinks=False)
            except OSError as exc:
                exclude(relative, f"entry unreadable: {exc}")
                continue
            if is_link:
                exclude(relative, "symbolic link")
            elif is_dir:
                if entry.name in IGNORED_DIRECTORIES:
                    exclude(relative, "dependency, cache, generated output, or repository state")
                elif len(Path(relative).parts) <= MAX_OBSERVED_DEPTH:
                    children.append(path)
                else:
                    exclude(relative, "depth limit")
            elif is_file:
                if not include_instructions and entry.name in {"AGENTS.md", "CLAUDE.md"}:
                    continue
                elif len(paths) < MAX_OBSERVED_PATHS:
                    paths.append(relative)
                else:
                    exclude(relative, "file observation limit reached")
            else:
                exclude(relative, "non-regular entry")
        pending.extend(reversed(children))
    if pending or visited >= MAX_VISITED_ENTRIES:
        truncated = True
    if truncated:
        exclusions.append(". (observation work/exclusion budget reached; remaining entries omitted and ordering is not complete)")
    return sorted(paths), sorted(set(exclusions))


def _category(relative: str) -> str | None:
    path = Path(relative)
    if path.name in {"AGENTS.md", "CLAUDE.md"}:
        return "instruction"
    if path.name in MANIFESTS:
        return "manifest"
    if path.name in LOCKFILES:
        return "lockfile"
    if path.parts and path.parts[0] in ENTRYPOINT_ROOTS:
        return "entry-point"
    if path.parts and path.parts[0] in {".github", ".gitlab"}:
        return "ci"
    if relative.casefold().startswith("docs/") or path.suffix.casefold() == ".md":
        return "document"
    return None


def _bounded_exclusions(exclusions: list[str]) -> list[str]:
    if len(exclusions) <= MAX_EXCLUSIONS:
        return exclusions
    return exclusions[:MAX_EXCLUSIONS] + [". (exclusion output truncated; observation is incomplete)"]


def audit_project(*, root: Path) -> "AuditReport":
    root = validate_root(root)
    observed, exclusions = _observed_paths(root)
    exclusions = _bounded_exclusions(exclusions)
    findings: list[AuditFinding] = []
    for relative in observed:
        category = _category(relative)
        findings.append(AuditFinding(category or "observed-path", "confirmed", relative, "observed path; not authority"))
    for relative in SOURCE_ROOTS:
        path = root / relative
        if path.is_dir() and not path.is_symlink():
            findings.append(AuditFinding("source-root", "confirmed", relative, "observed source entry path; not authority"))
    for relative in TEST_ROOTS:
        path = root / relative
        if path.is_dir() and not path.is_symlink():
            findings.append(AuditFinding("test-root", "confirmed", relative, "observed test entry path; not authority"))
    reason = _legacy_reason(root)
    if reason:
        findings.append(AuditFinding("legacy", "conflict", ".", reason + "; init/upgrade require explicit migration"))
    findings.append(AuditFinding("scope", "confirmed", ".", f"observed paths are bounded to depth {MAX_OBSERVED_DEPTH} and {MAX_OBSERVED_PATHS} files; commands and file contents are omitted"))
    findings.extend(AuditFinding("exclusion", "skipped", item.split(" (", 1)[0], item) for item in exclusions)
    return AuditReport(tuple(sorted(findings, key=lambda item: (item.category, item.path, item.status, item.detail))))


@dataclass(frozen=True)
class AuditFinding:
    category: str
    status: str
    path: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"category": self.category, "detail": self.detail, "path": self.path, "status": self.status}


@dataclass(frozen=True)
class AuditReport:
    findings: tuple[AuditFinding, ...]

    def as_dict(self) -> dict[str, object]:
        statuses = ("confirmed", "inferred", "unknown", "conflict", "skipped")
        return {"schema": "reporivet.audit/v2", "counts": {s: sum(f.status == s for f in self.findings) for s in statuses}, "findings": [f.as_dict() for f in self.findings]}

    def render(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _markdown_path(value: str) -> str:
    # destination은 URL-safe하게, 표시 label은 _markdown_label에서 처리한다.
    return quote(value, safe="/._-~")


def _markdown_label(value: str) -> str:
    """읽기 쉬운 Unicode label을 유지하면서 Markdown/제어 입력을 inert하게 만든다."""
    safe: list[str] = []
    for char in value:
        category = unicodedata.category(char)
        if char == "\n":
            safe.append("\\n")
        elif char == "\r":
            safe.append("\\r")
        elif category == "Cc":
            safe.append(f"\\u{{{ord(char):04x}}}")
        elif category == "Cf":
            safe.append(f"\\u{{{ord(char):04x}}}")
        else:
            safe.append(char)
    rendered = html.escape("".join(safe), quote=False)
    for char in "[]!\\`*_":
        rendered = rendered.replace(char, f"&#{ord(char)};")
    return rendered


def _safe_heading(value: str, fallback: str) -> str:
    value = " ".join((value or fallback).split())
    return _markdown_label(value)


def _agent_block(root: Path, name: str, summary: str) -> str:
    observed, exclusions = _observed_paths(root, include_instructions=False)
    rows = "\n".join(f"- [{_markdown_label(item)}](./{_markdown_path(item)}) (observed path; not authority)" for item in observed[:MAX_OBSERVED_PATHS]) or "- No bounded paths observed; establish purpose and verification method before changing files."
    displayed_exclusions = exclusions[:12]
    if len(exclusions) > 12:
        displayed_exclusions.append("... (exclusion output truncated; observation is incomplete)")
    excluded = ", ".join(_markdown_label(item) for item in displayed_exclusions) or "none recorded"
    project = _safe_heading(name, root.name or "Repository")
    purpose = _safe_heading(summary, "Use the repository's existing documentation and code as the authority.")
    return read_asset("root/AGENTS.md.tmpl", {"PROJECT_NAME": project, "PROJECT_SUMMARY": purpose, "OBSERVED_PATH_ROWS": rows, "OBSERVED_EXCLUSIONS": excluded}).rstrip()


def _claude_block() -> str:
    return f"""{CLAUDE_START}
Reporivet entrypoint pointer: read `AGENTS.md` for repository-local navigation guidance. This pointer is not a second instruction authority.
{CLAUDE_END}"""


def _existing_name(content: bytes) -> str:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return ""
    span = _managed_span(text, AGENTS_START, AGENTS_END)
    if span is None:
        return ""
    for line in text[span[0]:span[1]].splitlines():
        if line.startswith("# ") and line.endswith(" agent entrypoints"):
            return html.unescape(line[2:-len(" agent entrypoints")])
    return ""


def _legacy_guidance(reason: str) -> str:
    return (
        "legacy Reporivet 0.2 target detected: " + reason + ". No files were changed. "
        "Either keep using the released-compatible 0.2 tool, or review a separate migration change that removes "
        "the old Reporivet-owned markers, runtime, and CI dependencies; leave this target unchanged until that review. "
        f"Use the source repository root {SOURCE_REPOSITORY_URL} and, in a checked-out source tree, "
        "read docs/references/entrypoint-migration.md (this development document may not exist on the remote default branch)."
    )


def _prepare(root: Path, *, name: str, summary: str, claude: bool) -> tuple[tuple[_Operation, ...], ChangeSet]:
    legacy = _legacy_reason(root)
    if legacy:
        raise InitError(_legacy_guidance(legacy))
    agents_path = root / "AGENTS.md"
    ensure_safe_write_path(agents_path)
    if agents_path.exists() and not agents_path.is_file():
        raise InitError("AGENTS.md is not a regular file")
    agents_before = _image(agents_path, root)
    agents_original = agents_before.content or b""
    targets = [("AGENTS.md", _agent_block(root, name or _existing_name(agents_original), summary), AGENTS_START, AGENTS_END, agents_before)]
    if claude:
        claude_path = root / "CLAUDE.md"
        ensure_safe_write_path(claude_path)
        if claude_path.exists() and not claude_path.is_file():
            raise InitError("CLAUDE.md is not a regular file")
        targets.append(("CLAUDE.md", _claude_block(), CLAUDE_START, CLAUDE_END, _image(claude_path, root)))
    operations: list[_Operation] = []
    changes = ChangeSet()
    for relative, block, start, end, before in targets:
        updated = _upsert(before.content or b"", block, start, end)
        op = _operation(root, relative, updated, before=before)
        operations.append(op)
        path = root / relative
        if op.before.kind == "missing":
            changes.created.append(path)
        elif op.before.digest != op.after.digest or op.before.mode != op.after.mode:
            changes.updated.append(path)
        else:
            changes.skipped.append(path)
    changes.fingerprint = _fingerprint(operations)
    return tuple(operations), changes


def apply_harness(*, root: Path, mode: str, name: str = "", summary: str = "", claude: bool = False, dry_run: bool = False) -> ChangeSet:
    if mode not in {"init", "upgrade"}:
        raise InitError(f"unsupported lifecycle mode: {mode}")
    requested = root.expanduser()
    raw = requested if requested.is_absolute() else Path.cwd() / requested
    created_root = mode == "init" and not raw.exists() and not dry_run
    root = validate_root(root, create=mode == "init", dry_run=dry_run)
    try:
        operations, changes = _prepare(root, name=name, summary=summary, claude=claude)
        if not dry_run:
            _apply(operations)
    except BaseException:
        if created_root:
            try:
                if root.is_dir() and not any(root.iterdir()):
                    root.rmdir()
            except OSError:
                pass
        raise
    changes.print(root, dry_run=dry_run, operations=operations)
    return changes


def init_project(*, root: Path, name: str = "", summary: str = "", claude: bool = False, dry_run: bool = False) -> ChangeSet:
    return apply_harness(root=root, mode="init", name=name, summary=summary, claude=claude, dry_run=dry_run)


def upgrade_project(*, root: Path, claude: bool = False, dry_run: bool = False) -> ChangeSet:
    root = validate_root(root)
    return apply_harness(root=root, mode="upgrade", claude=claude, dry_run=dry_run)


def _check_managed_links(root: Path, text: str, span: tuple[int, int], errors: list[str]) -> None:
    body = text[span[0] + len(AGENTS_START):span[1] - len(AGENTS_END)]
    if not body.strip():
        errors.append("AGENTS.md managed entrypoint block is empty")
        return
    for match in re.finditer(r"\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)", body):
        raw = match.group(1)
        try:
            parsed = urlsplit(raw)
        except ValueError:
            errors.append(f"AGENTS.md managed link is malformed: {raw}")
            continue
        if parsed.scheme or parsed.netloc or not raw.startswith("./"):
            errors.append(f"AGENTS.md managed link is not a relative path: {raw}")
            continue
        relative = unquote(parsed.path[2:])
        if not relative or "\x00" in relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
            errors.append(f"AGENTS.md managed link escapes project root: {raw}")
            continue
        target = root / relative
        if symlink_component(target) is not None:
            errors.append(f"AGENTS.md managed link targets a symlink: {relative}")
            continue
        try:
            metadata = target.lstat()
        except FileNotFoundError:
            errors.append(f"AGENTS.md managed link target is missing: {relative}")
            continue
        except OSError as exc:
            errors.append(f"AGENTS.md managed link target cannot be checked: {relative}: {exc}")
            continue
        if not stat.S_ISREG(metadata.st_mode):
            errors.append(f"AGENTS.md managed link target is not a regular file: {relative}")


def doctor_project(root: Path) -> int:
    root = validate_root(root)
    errors: list[str] = []
    reason = _legacy_reason(root)
    if reason:
        errors.append(_legacy_guidance(reason))
    agents = root / "AGENTS.md"
    agents_text = ""
    agents_span: tuple[int, int] | None = None
    if symlink_component(agents) is not None:
        errors.append("AGENTS.md is a symlink or has a symlinked parent")
    elif not agents.exists():
        errors.append("AGENTS.md is missing; run reporivet init")
    elif not agents.is_file():
        errors.append("AGENTS.md is not a regular file")
    else:
        try:
            agents_text = agents.read_text(encoding="utf-8")
            agents_span = _managed_span(agents_text, AGENTS_START, AGENTS_END)
            if agents_span is None:
                errors.append("AGENTS.md has no Reporivet entrypoint block")
            else:
                _check_managed_links(root, agents_text, agents_span, errors)
        except (OSError, UnicodeError, InitError) as exc:
            errors.append(f"AGENTS.md cannot be checked: {exc}")
    claude = root / "CLAUDE.md"
    if claude.exists() or symlink_component(claude) is not None:
        if symlink_component(claude) is not None:
            errors.append("CLAUDE.md is a symlink or has a symlinked parent")
        elif not claude.is_file():
            errors.append("CLAUDE.md is not a regular file")
        else:
            try:
                text = claude.read_text(encoding="utf-8")
                span = _managed_span(text, CLAUDE_START, CLAUDE_END)
                if span is not None and text[span[0]:span[1]] != _claude_block():
                    errors.append("CLAUDE.md managed pointer does not reference AGENTS.md exactly")
            except (OSError, UnicodeError, InitError) as exc:
                errors.append(f"CLAUDE.md cannot be checked: {exc}")
    for error in errors:
        print("ERROR: " + error, file=__import__("sys").stderr)
    if errors:
        return 2
    print("Reporivet entrypoint ownership checks passed; no semantic or agent-capability verdict was made.")
    return 0
