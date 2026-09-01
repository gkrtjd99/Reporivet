from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import stat
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .guided import (
    ACTIVE_PLAN_STATES,
    LEGACY_RUNTIME_PATHS,
    SetupAction,
    SetupPreview,
    _GuidedSetupTransaction,
    _assert_action_current,
    _build_guided_setup_preview,
    _initial_definition,
    _open_absolute_directory,
    _open_directory_component,
    _parse_frontmatter,
    _read_open_regular_file,
    _regular_file_open_flags,
    _stat_content_identity,
    _stat_identity,
)
from .initializer import MANAGED_MARKER, InitError, validate_root

MIGRATION_FROM = "0.2"
LEGACY_ASSET_VERSION = "0.2.0"
MANIFEST_NAME = "manifest.json"
LEGACY_PLAN_FIELDS = frozenset(
    {
        "gate_review_reason",
        "gate_verdict",
        "manifest_sha256",
        "verification_run",
    }
)

LEGACY_FILE_SHA256: dict[str, str] = {
    ".github/workflows/harness-garden.yml": "414cca121d113dc41e7984ea63439ea8627efbc46e7bdfb99973008727cfcf8b",
    ".github/workflows/harness-verify.yml": "254b4713cc86036db5a4e607172396e0ebf565a691561c721019cccd9d107e5b",
    "dev/architecture-check": "4ab4affa9a2e09271df378ecf41d0a3fb48e07aeb0b4b4b6def053eb22b5ffc6",
    "dev/audit": "470bb782beb161cade211f283fac59cc3b36734dcbd9ded149c7b1c9d9279600",
    "dev/bootstrap": "c9260423aba57fba61be5f2cfdcd78e8bc81c73e9bb1e8a723fd36388e35d030",
    "dev/check": "a915de45a9e5f16f7c28948d9ee0c6669ac706d700822260162978d83c6e4304",
    "dev/close-plan": "4c6fe573e128041d662fa688a9a6b25b602e79823fe82213865dcc075d97a48d",
    "dev/code-map": "d091acb2e18995bbec5b73e81c34103480f22ba642e240fb79b3b32cc206c262",
    "dev/context": "6df64c2b0caad59a52c898c5c3f0afef167d5b0e2e1a6b57721ac9378bce743f",
    "dev/define": "e6022aa8abee879a1fe10a35e791dfacf03791b781cd9027cea07f75e7d40cfd",
    "dev/docs-check": "afc704ac65588f29099af21bc440eb1fdc880aac8bc591300ba36344d7f38b96",
    "dev/docs-index": "183dcb06e411b4bb655ea9a0cff8cfdebe4f29581f4a232b96a58ae3878904af",
    "dev/garden": "035e3a8c301c37c0dffe3b5be3a8c85e5133579f0044276bd30fa60c42276077",
    "dev/harness.py": "64fb8ff42365245807119e97ecf683505f09d0feae09beb15897dae6ae6cfa6c",
    "dev/new-plan": "026adce3926ec7c7fd770442f9b986c8ce9764b142968e65b7e69b5472d2be4c",
    "dev/plan-check": "594b105edd93672f7e8c4816b009eb03c936348aaddf428c046e1826d9eacea7",
    "dev/run": "368e5551336cddce8ede8063fa48993f19665a835f35f3c3598d38d150724c58",
    "dev/security-check": "74ccf4efc97ea32a276452d79ee2efa3515ce7e9295e6bc003db7e0734c4d309",
    "dev/smoke": "0dc8757d622e4f3c1183a47593d64962b3d907840165477b0635f5c10f6f80e5",
    "dev/task": "6ce675be6be3c61c8156d77062e5a8d919812e9b48444faf6ea178ad11bb26da",
    "dev/verify": "6c9672783489546473d1511b1d81cd39c2bec8fcb55e0fc3ccf584f129e7859c",
}


@dataclass(frozen=True)
class _PathState:
    kind: str
    mode: int | None = None
    sha256: str = ""
    content: bytes | None = None
    children: tuple[str, ...] = ()


@dataclass(frozen=True)
class LegacyInventoryEntry:
    path: str
    lstat_type: str
    current_sha256: str
    current_mode: int | None
    ownership: str
    action: str
    reason: str
    reversible: bool
    review_required: bool
    backup_destination: str | None

    def as_dict(self) -> dict[str, object]:
        return {
            "action": self.action,
            "backup_destination": self.backup_destination,
            "current_mode": self.current_mode,
            "current_sha256": self.current_sha256,
            "lstat_type": self.lstat_type,
            "ownership": self.ownership,
            "path": self.path,
            "reason": self.reason,
            "reversible": self.reversible,
            "review_required": self.review_required,
        }


@dataclass(frozen=True)
class MigrationPreview:
    root: Path
    backup_dir: Path
    from_version: str
    setup_preview: SetupPreview
    setup_inputs: tuple[dict[str, object], ...]
    legacy_inventory: tuple[LegacyInventoryEntry, ...]
    plan_blockers: tuple[dict[str, object], ...]
    blockers: tuple[dict[str, str], ...]
    fingerprint: str

    def _payload(self) -> dict[str, object]:
        return {
            "backup_dir": str(self.backup_dir),
            "blockers": list(self.blockers),
            "from": self.from_version,
            "legacy_inventory": [entry.as_dict() for entry in self.legacy_inventory],
            "plan_blockers": list(self.plan_blockers),
            "root": str(self.root),
            "schema": "reporivet.migration-preview/v1",
            "setup_actions": [action.as_dict() for action in self.setup_preview.actions],
            "setup_fingerprint": self.setup_preview.fingerprint,
            "setup_inputs": list(self.setup_inputs),
        }

    def as_dict(self) -> dict[str, object]:
        return {**self._payload(), "fingerprint": self.fingerprint}

    def render(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


@dataclass(frozen=True)
class MigrationResult:
    status: str
    root: Path
    manifest: Path
    fingerprint: str

    def as_dict(self) -> dict[str, str]:
        return {
            "fingerprint": self.fingerprint,
            "manifest": str(self.manifest),
            "root": str(self.root),
            "schema": "reporivet.migration-result/v1",
            "status": self.status,
        }

    def render(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


@dataclass(frozen=True)
class _MutationSpec:
    path: str
    operation: str
    expected_type: str
    expected_sha256: str = ""
    expected_mode: int | None = None
    proposed_content: bytes | None = None


class _MissingParent(FileNotFoundError):
    pass


class _RootView:
    def __init__(self, root: Path) -> None:
        self.root = root
        try:
            self.descriptor = _open_absolute_directory(root)
        except OSError as exc:
            raise InitError(f"cannot anchor migration at the validated root: {exc}") from exc
        self.closed = False

    @staticmethod
    def _parts(relative: str) -> tuple[str, ...]:
        path = Path(relative)
        parts = path.parts
        if (
            path.is_absolute()
            or not parts
            or any(part in {"", ".", ".."} for part in parts)
        ):
            raise InitError(f"migration path is not a safe relative path: {relative}")
        return parts

    def _open_parent(self, relative: str) -> tuple[int, str]:
        parts = self._parts(relative)
        descriptor = os.dup(self.descriptor)
        try:
            for component in parts[:-1]:
                try:
                    child = _open_directory_component(descriptor, component)
                except FileNotFoundError as exc:
                    raise _MissingParent(relative) from exc
                os.close(descriptor)
                descriptor = child
            return descriptor, parts[-1]
        except Exception:
            os.close(descriptor)
            raise

    def snapshot(
        self,
        relative: str,
        *,
        read_regular: bool = True,
        list_directory: bool = False,
    ) -> _PathState:
        try:
            parent_descriptor, name = self._open_parent(relative)
        except _MissingParent:
            return _PathState("missing")
        except (OSError, InitError):
            return _PathState("unsafe-ancestor")
        try:
            try:
                metadata = os.stat(
                    name,
                    dir_fd=parent_descriptor,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                return _PathState("missing")
            except OSError:
                return _PathState("unreadable")
            mode = stat.S_IMODE(metadata.st_mode)
            if stat.S_ISREG(metadata.st_mode):
                if not read_regular:
                    return _PathState("regular", mode=mode)
                descriptor = -1
                try:
                    descriptor = os.open(
                        name,
                        _regular_file_open_flags(),
                        dir_fd=parent_descriptor,
                    )
                    opened = os.fstat(descriptor)
                    if _stat_content_identity(metadata) != _stat_content_identity(opened):
                        return _PathState("unreadable")
                    content = _read_open_regular_file(descriptor)
                    current = os.stat(
                        name,
                        dir_fd=parent_descriptor,
                        follow_symlinks=False,
                    )
                    after = os.fstat(descriptor)
                    if (
                        _stat_content_identity(current) != _stat_content_identity(after)
                        or _stat_content_identity(opened) != _stat_content_identity(after)
                    ):
                        return _PathState("unreadable")
                    return _PathState(
                        "regular",
                        mode=mode,
                        sha256=_sha256(content),
                        content=content,
                    )
                except OSError:
                    return _PathState("unreadable")
                finally:
                    if descriptor >= 0:
                        os.close(descriptor)
            if stat.S_ISDIR(metadata.st_mode):
                children: tuple[str, ...] = ()
                if list_directory:
                    descriptor = -1
                    try:
                        descriptor = _open_directory_component(parent_descriptor, name)
                        children = tuple(sorted(os.listdir(descriptor)))
                    except OSError:
                        return _PathState("unreadable", mode=mode)
                    finally:
                        if descriptor >= 0:
                            os.close(descriptor)
                return _PathState("directory", mode=mode, children=children)
            if stat.S_ISLNK(metadata.st_mode):
                return _PathState("symlink", mode=mode)
            if stat.S_ISFIFO(metadata.st_mode):
                return _PathState("fifo", mode=mode)
            if stat.S_ISSOCK(metadata.st_mode):
                return _PathState("socket", mode=mode)
            if stat.S_ISCHR(metadata.st_mode):
                return _PathState("character-device", mode=mode)
            if stat.S_ISBLK(metadata.st_mode):
                return _PathState("block-device", mode=mode)
            return _PathState("nonregular", mode=mode)
        finally:
            os.close(parent_descriptor)

    def regular_file_state(self, relative: str) -> tuple[str, bytes]:
        state = self.snapshot(relative)
        if state.kind == "missing":
            return "missing", b""
        if state.kind == "regular" and state.content is not None:
            return "file", state.content
        return "conflict", b""

    @staticmethod
    def _write_all(descriptor: int, content: bytes) -> None:
        view = memoryview(content)
        written = 0
        while written < len(view):
            count = os.write(descriptor, view[written:])
            if count <= 0:
                raise OSError(errno.EIO, "write returned no progress")
            written += count

    def unlink_regular(
        self,
        relative: str,
        *,
        expected_sha256: str,
        expected_mode: int | None = None,
    ) -> None:
        parent_descriptor, name = self._open_parent(relative)
        descriptor = -1
        try:
            before = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
            if not stat.S_ISREG(before.st_mode):
                raise InitError(f"migration removal target is no longer regular: {relative}")
            descriptor = os.open(
                name,
                _regular_file_open_flags(),
                dir_fd=parent_descriptor,
            )
            opened = os.fstat(descriptor)
            if _stat_content_identity(before) != _stat_content_identity(opened):
                raise InitError(f"migration removal target changed before open: {relative}")
            content = _read_open_regular_file(descriptor)
            current = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
            after = os.fstat(descriptor)
            if (
                _stat_content_identity(opened) != _stat_content_identity(after)
                or _stat_content_identity(current) != _stat_content_identity(after)
                or _sha256(content) != expected_sha256
                or (
                    expected_mode is not None
                    and stat.S_IMODE(after.st_mode) != expected_mode
                )
            ):
                raise InitError(f"migration removal target changed after preview: {relative}")
            os.unlink(name, dir_fd=parent_descriptor)
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            os.close(parent_descriptor)

    def create_regular(self, relative: str, content: bytes, mode: int) -> None:
        parent_descriptor, name = self._open_parent(relative)
        descriptor = -1
        try:
            try:
                os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise InitError(f"rollback target is no longer missing: {relative}")
            descriptor = os.open(
                name,
                _regular_file_open_flags(writable=True, create=True),
                mode,
                dir_fd=parent_descriptor,
            )
            self._write_all(descriptor, content)
            os.fchmod(descriptor, mode)
            opened = os.fstat(descriptor)
            current = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
            if (
                not stat.S_ISREG(opened.st_mode)
                or _stat_identity(opened) != _stat_identity(current)
            ):
                raise InitError(f"rollback target changed during create: {relative}")
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            os.close(parent_descriptor)

    def replace_regular(
        self,
        relative: str,
        *,
        expected_sha256: str,
        expected_mode: int | None,
        content: bytes,
        mode: int,
    ) -> None:
        parent_descriptor, name = self._open_parent(relative)
        descriptor = -1
        try:
            before = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
            if not stat.S_ISREG(before.st_mode):
                raise InitError(f"rollback update target is no longer regular: {relative}")
            descriptor = os.open(
                name,
                _regular_file_open_flags(writable=True),
                dir_fd=parent_descriptor,
            )
            opened = os.fstat(descriptor)
            if _stat_content_identity(before) != _stat_content_identity(opened):
                raise InitError(f"rollback update target changed before open: {relative}")
            current_content = _read_open_regular_file(descriptor)
            current = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
            after_read = os.fstat(descriptor)
            if (
                _stat_content_identity(opened) != _stat_content_identity(after_read)
                or _stat_content_identity(current) != _stat_content_identity(after_read)
                or _sha256(current_content) != expected_sha256
                or (
                    expected_mode is not None
                    and stat.S_IMODE(after_read.st_mode) != expected_mode
                )
            ):
                raise InitError(f"rollback update target contains a later change: {relative}")
            os.ftruncate(descriptor, 0)
            os.lseek(descriptor, 0, os.SEEK_SET)
            self._write_all(descriptor, content)
            os.fchmod(descriptor, mode)
            after = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
            if _stat_identity(after) != _stat_identity(opened):
                raise InitError(f"rollback update target changed during restore: {relative}")
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            os.close(parent_descriptor)

    def make_directory(self, relative: str, mode: int) -> None:
        parent_descriptor, name = self._open_parent(relative)
        try:
            try:
                os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise InitError(f"rollback directory target is no longer missing: {relative}")
            os.mkdir(name, mode=mode, dir_fd=parent_descriptor)
            current = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
            if not stat.S_ISDIR(current.st_mode):
                raise InitError(f"rollback directory target is not a directory: {relative}")
            os.chmod(name, mode, dir_fd=parent_descriptor, follow_symlinks=False)
        finally:
            os.close(parent_descriptor)

    def remove_empty_directory(
        self,
        relative: str,
        *,
        expected_mode: int | None = None,
    ) -> None:
        parent_descriptor, name = self._open_parent(relative)
        descriptor = -1
        try:
            before = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
            if not stat.S_ISDIR(before.st_mode):
                raise InitError(f"migration directory target is no longer a directory: {relative}")
            if expected_mode is not None and stat.S_IMODE(before.st_mode) != expected_mode:
                raise InitError(f"migration directory mode changed after preview: {relative}")
            descriptor = _open_directory_component(parent_descriptor, name)
            if os.listdir(descriptor):
                raise InitError(f"migration directory is not empty and will be preserved: {relative}")
            current = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
            opened = os.fstat(descriptor)
            if _stat_identity(current) != _stat_identity(opened):
                raise InitError(f"migration directory changed before removal: {relative}")
            os.rmdir(name, dir_fd=parent_descriptor)
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            os.close(parent_descriptor)

    def close(self) -> None:
        if not self.closed:
            os.close(self.descriptor)
            self.closed = True


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _canonical_json(payload: object) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _require_from_version(from_version: str) -> None:
    if from_version != MIGRATION_FROM:
        raise InitError("migration supports only --from 0.2")


def _normalize_backup_dir(root: Path, backup_dir: Path) -> Path:
    expanded = backup_dir.expanduser()
    absolute = Path(os.path.abspath(expanded))
    normalized = Path(os.path.realpath(absolute.parent)) / absolute.name
    if normalized == root or root in normalized.parents:
        raise InitError("migration backup directory must be outside the repository")
    if not normalized.name or normalized.name in {".", ".."}:
        raise InitError("migration backup directory must name one external directory")
    return normalized


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _canonical_legacy_config(project: Mapping[str, object]) -> bytes:
    lines = [
        "# Project-owned configuration. The initializer never overwrites this file.",
        '# Review detected commands against the repository before setting configuration = "ready".',
        "version = 1",
        "",
        "[project]",
        f"name = {_toml_string(str(project['name']))}",
        f"summary = {_toml_string(str(project['summary']))}",
        f"kind = {_toml_string(str(project['kind']))}",
        f"primary_language = {_toml_string(str(project['primary_language']))}",
        f"runtime = {_toml_string(str(project['runtime']))}",
        'baseline = "draft" # change to "established" after PLAN-0000 is complete',
        f'configuration = "{project["configuration"]}"',
        'default_branch = "main"',
        "",
        "[commands]",
        "bootstrap = []",
        "run = []",
        "check = []",
        "verify = []",
        "smoke = []",
        "architecture = []",
        "",
        "[paths]",
        'source = ["src"]',
        'tests = ["tests"]',
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
        'protected_paths = [".github/workflows/**", "AGENTS.md", "dev/harness.py", "dev/harness.toml", "docs/SECURITY.md"]',
        'contained_paths = ["docs/**", "src/**", "tests/**"]',
        'wide_paths = [".github/**", "ARCHITECTURE.md", "Cargo.toml", "build.gradle", "build.gradle.kts", "dev/**", "go.mod", "package.json", "pom.xml", "pyproject.toml"]',
        'irreversible_paths = ["db/migrations/**", "infrastructure/**", "migrations/**", "schema/migrations/**", "terraform/**"]',
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _has_managed_marker(content: bytes) -> bool:
    lines = content.decode("utf-8", errors="ignore").splitlines()[:3]
    return any(MANAGED_MARKER.fullmatch(line) is not None for line in lines)


def _has_02_managed_marker(content: bytes) -> bool:
    marker = f"# reporivet:managed version={LEGACY_ASSET_VERSION}"
    return marker in content.decode("utf-8", errors="ignore").splitlines()[:3]


def _is_exact_generated_config(content: bytes) -> bool:
    try:
        data = tomllib.loads(content.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError):
        return False
    project = data.get("project")
    commands = data.get("commands")
    paths = data.get("paths")
    if not isinstance(project, dict) or not isinstance(commands, dict) or not isinstance(paths, dict):
        return False
    command_names = ("bootstrap", "run", "check", "verify", "smoke", "architecture")
    if any(commands.get(name) != [] for name in command_names):
        return False
    if paths.get("source") != ["src"] or paths.get("tests") != ["tests"]:
        return False
    fields = ("name", "summary", "kind", "primary_language", "runtime", "configuration")
    if any(not isinstance(project.get(field), str) for field in fields):
        return False
    if project["configuration"] not in {"ready", "review"}:
        return False
    return content == _canonical_legacy_config(project)


def _backup_destination(backup_dir: Path, relative: str, *, directory: bool = False) -> str:
    if directory:
        return str(backup_dir / MANIFEST_NAME)
    return str(backup_dir / "preimages" / relative)


def _file_inventory_entry(
    *,
    backup_dir: Path,
    relative: str,
    state: _PathState,
) -> LegacyInventoryEntry:
    if state.kind == "missing":
        return LegacyInventoryEntry(
            relative,
            "missing",
            "",
            None,
            "absent",
            "absent",
            "known 0.2 path is absent",
            True,
            False,
            None,
        )
    if state.kind != "regular" or state.content is None:
        return LegacyInventoryEntry(
            relative,
            state.kind,
            "",
            state.mode,
            "unsafe",
            "refuse",
            "known 0.2 file target is symlinked, nonregular, or unreadable; migration will not follow or replace it",
            False,
            True,
            None,
        )

    if relative == "dev/harness.toml":
        if _is_exact_generated_config(state.content):
            return LegacyInventoryEntry(
                relative,
                state.kind,
                state.sha256,
                state.mode,
                "reporivet-canonical-0.2",
                "remove",
                "exact generated 0.2 default contains no project command or path reference",
                True,
                False,
                _backup_destination(backup_dir, relative),
            )
        return LegacyInventoryEntry(
            relative,
            state.kind,
            state.sha256,
            state.mode,
            "project-owned",
            "preserve",
            "configuration is customized, ambiguous, or contains project references",
            True,
            True,
            None,
        )

    expected_sha256 = LEGACY_FILE_SHA256[relative]
    has_marker = _has_managed_marker(state.content)
    if has_marker and state.sha256 == expected_sha256:
        return LegacyInventoryEntry(
            relative,
            state.kind,
            state.sha256,
            state.mode,
            "reporivet-canonical-0.2",
            "remove",
            "expected path, required marker, and exact canonical 0.2 bytes all match",
            True,
            False,
            _backup_destination(backup_dir, relative),
        )
    if has_marker:
        return LegacyInventoryEntry(
            relative,
            state.kind,
            state.sha256,
            state.mode,
            "reporivet-customized",
            "preserve",
            "marker-bearing file differs from canonical 0.2 bytes; a marker alone is not deletion authority",
            True,
            True,
            None,
        )
    return LegacyInventoryEntry(
        relative,
        state.kind,
        state.sha256,
        state.mode,
        "project-owned",
        "preserve",
        "unmarked file at a known path is project-owned and is not claimed",
        True,
        True,
        None,
    )


def _retained_runtime_entry(relative: str, state: _PathState) -> LegacyInventoryEntry:
    if state.kind == "missing":
        return LegacyInventoryEntry(
            relative,
            "missing",
            "",
            None,
            "absent",
            "retain",
            "retained legacy runtime path is absent",
            True,
            False,
            None,
        )
    if state.kind == "directory":
        if relative == ".harness/runs":
            reason = "retained historical run directory; existence and type only were inspected"
            owner = "retained-history"
            review = False
        else:
            reason = "legacy runtime state directory is preserved because directory ownership is not byte-provable"
            owner = "ambiguous"
            review = True
        return LegacyInventoryEntry(
            relative,
            state.kind,
            "",
            None if relative == ".harness/runs" else state.mode,
            owner,
            "retain",
            reason,
            True,
            review,
            None,
        )
    return LegacyInventoryEntry(
        relative,
        state.kind,
        "",
        None if relative == ".harness/runs" else state.mode,
        "unsafe",
        "refuse",
        "retained legacy runtime path has an unexpected or symlinked type; migration will not follow it",
        False,
        True,
        None,
    )


def _scan_active_plan_blockers(view: _RootView) -> tuple[dict[str, object], ...]:
    directory = "docs/exec-plans/active"
    state = view.snapshot(directory, read_regular=False, list_directory=True)
    if state.kind == "missing":
        return ()
    if state.kind != "directory":
        return (
            {
                "fields": [],
                "path": directory,
                "reason": "active Plan directory is unsafe or nonregular",
            },
        )
    blockers: list[dict[str, object]] = []
    for name in state.children:
        if not name.endswith(".md"):
            continue
        relative = f"{directory}/{name}"
        plan_state = view.snapshot(relative)
        if plan_state.kind != "regular" or plan_state.content is None:
            blockers.append(
                {
                    "fields": [],
                    "path": relative,
                    "reason": "active Plan path is unsafe or nonregular",
                }
            )
            continue
        try:
            text = plan_state.content.decode("utf-8")
        except UnicodeError:
            blockers.append(
                {
                    "fields": [],
                    "path": relative,
                    "reason": "active Plan is not readable UTF-8",
                }
            )
            continue
        metadata = _parse_frontmatter(text)
        status_value = metadata.get("status", "").casefold()
        fields = sorted(LEGACY_PLAN_FIELDS.intersection(metadata))
        if status_value in ACTIVE_PLAN_STATES and fields:
            blockers.append(
                {
                    "fields": fields,
                    "path": relative,
                    "reason": "active Plan still declares exact legacy Gate or Verification Run dependency fields",
                }
            )
    return tuple(sorted(blockers, key=lambda item: str(item["path"])))


def _build_legacy_inventory(
    *,
    backup_dir: Path,
    view: _RootView,
) -> tuple[LegacyInventoryEntry, ...]:
    entries: dict[str, LegacyInventoryEntry] = {}
    for relative in sorted((*LEGACY_FILE_SHA256, "dev/harness.toml")):
        entries[relative] = _file_inventory_entry(
            backup_dir=backup_dir,
            relative=relative,
            state=view.snapshot(relative),
        )

    for relative in LEGACY_RUNTIME_PATHS:
        entries[relative] = _retained_runtime_entry(
            relative,
            view.snapshot(relative, read_regular=False, list_directory=False),
        )

    dev_state = view.snapshot("dev", read_regular=False, list_directory=True)
    if dev_state.kind == "missing":
        entries["dev"] = LegacyInventoryEntry(
            "dev",
            "missing",
            "",
            None,
            "absent",
            "absent",
            "legacy command directory is absent",
            True,
            False,
            None,
        )
    elif dev_state.kind != "directory":
        entries["dev"] = LegacyInventoryEntry(
            "dev",
            dev_state.kind,
            "",
            dev_state.mode,
            "unsafe",
            "refuse",
            "legacy command directory is symlinked, nonregular, or unreadable",
            False,
            True,
            None,
        )
    else:
        removable_names = {
            Path(relative).name
            for relative, entry in entries.items()
            if relative.startswith("dev/") and entry.action == "remove"
        }
        all_children_are_removable = set(dev_state.children) == removable_names
        if all_children_are_removable:
            entries["dev"] = LegacyInventoryEntry(
                "dev",
                "directory",
                "",
                dev_state.mode,
                "reporivet-canonical-0.2",
                "remove",
                "directory will be removed only after every proven-owned canonical child is removed and it is empty",
                True,
                False,
                _backup_destination(backup_dir, "dev", directory=True),
            )
        else:
            entries["dev"] = LegacyInventoryEntry(
                "dev",
                "directory",
                "",
                dev_state.mode,
                "mixed-or-project-owned",
                "preserve",
                "project-owned or preserved content remains after proven-owned removals",
                True,
                True,
                None,
            )
    return tuple(entries[path] for path in sorted(entries))


def _setup_input_states(view: _RootView, setup: SetupPreview) -> tuple[dict[str, object], ...]:
    values: list[dict[str, object]] = []
    for action in setup.actions:
        state = view.snapshot(action.path, read_regular=False)
        values.append(
            {
                "current_mode": state.mode,
                "lstat_type": state.kind,
                "path": action.path,
            }
        )
    return tuple(sorted(values, key=lambda item: str(item["path"])))


def preview_migration(
    *,
    root: Path,
    from_version: str,
    backup_dir: Path,
) -> MigrationPreview:
    _require_from_version(from_version)
    root = validate_root(root)
    normalized_backup = _normalize_backup_dir(root, backup_dir)
    view = _RootView(root)
    try:
        draft = _initial_definition(root, None)
        setup = _build_guided_setup_preview(
            root=root,
            with_claude_settings=False,
            state_reader=view.regular_file_state,
            draft=draft,
        )
        setup_inputs = _setup_input_states(view, setup)
        inventory = _build_legacy_inventory(
            backup_dir=normalized_backup,
            view=view,
        )
        plan_blockers = _scan_active_plan_blockers(view)
    finally:
        view.close()

    blockers: list[dict[str, str]] = []
    for action in setup.actions:
        if action.action == "conflict":
            blockers.append(
                {
                    "path": action.path,
                    "reason": "document-first setup target is unsafe or conflicting",
                }
            )
    for entry in inventory:
        if entry.action == "refuse":
            blockers.append({"path": entry.path, "reason": entry.reason})
    for blocker in plan_blockers:
        blockers.append({"path": str(blocker["path"]), "reason": str(blocker["reason"])})
    ordered_blockers = tuple(sorted(blockers, key=lambda item: (item["path"], item["reason"])))

    provisional = MigrationPreview(
        root=root,
        backup_dir=normalized_backup,
        from_version=from_version,
        setup_preview=setup,
        setup_inputs=setup_inputs,
        legacy_inventory=inventory,
        plan_blockers=plan_blockers,
        blockers=ordered_blockers,
        fingerprint="",
    )
    fingerprint = _sha256(_canonical_json(provisional._payload()))
    return MigrationPreview(
        root=root,
        backup_dir=normalized_backup,
        from_version=from_version,
        setup_preview=setup,
        setup_inputs=setup_inputs,
        legacy_inventory=inventory,
        plan_blockers=plan_blockers,
        blockers=ordered_blockers,
        fingerprint=fingerprint,
    )


def _mutation_specs(preview: MigrationPreview) -> tuple[_MutationSpec, ...]:
    specs: dict[str, _MutationSpec] = {}
    view = _RootView(preview.root)
    try:
        for action in preview.setup_preview.actions:
            if action.action not in {"create", "update"}:
                continue
            operation = f"setup-{action.action}"
            expected_type = "missing" if action.action == "create" else "regular"
            specs[action.path] = _MutationSpec(
                path=action.path,
                operation=operation,
                expected_type=expected_type,
                expected_sha256=action.current_sha256,
                proposed_content=action.content.encode("utf-8"),
            )
            if action.action != "create":
                continue
            path = Path(action.path)
            parents = [parent for parent in path.parents if parent != Path(".")]
            for parent in reversed(parents):
                relative = parent.as_posix()
                state = view.snapshot(relative, read_regular=False)
                if state.kind == "missing":
                    specs.setdefault(
                        relative,
                        _MutationSpec(
                            path=relative,
                            operation="setup-create-directory",
                            expected_type="missing",
                        ),
                    )
                elif state.kind != "directory":
                    raise InitError(f"document-first setup parent is unsafe: {relative}")

        for entry in preview.legacy_inventory:
            if entry.action != "remove":
                continue
            operation = "remove-directory" if entry.path == "dev" else "remove-file"
            specs[entry.path] = _MutationSpec(
                path=entry.path,
                operation=operation,
                expected_type="directory" if entry.path == "dev" else "regular",
                expected_sha256=entry.current_sha256,
                expected_mode=entry.current_mode,
            )
    finally:
        view.close()
    return tuple(specs[path] for path in sorted(specs))


def _state_matches_spec(state: _PathState, spec: _MutationSpec) -> bool:
    if state.kind != spec.expected_type:
        return False
    if spec.expected_type == "regular" and state.sha256 != spec.expected_sha256:
        return False
    if spec.expected_mode is not None and state.mode != spec.expected_mode:
        return False
    return True


def _preimage_dict(state: _PathState, backup_path: str | None) -> dict[str, object]:
    return {
        "backup_path": backup_path,
        "children": list(state.children),
        "mode": state.mode,
        "prior_existence": state.kind != "missing",
        "sha256": state.sha256,
        "type": state.kind,
    }


def _planned_postimage(spec: _MutationSpec, preimage: _PathState) -> dict[str, object]:
    if spec.operation in {"remove-file", "remove-directory"}:
        return {"children": [], "mode": None, "sha256": "", "type": "missing"}
    if spec.operation == "setup-create-directory":
        return {"children": [], "mode": None, "sha256": "", "type": "directory"}
    proposed = spec.proposed_content or b""
    mode = preimage.mode if spec.operation == "setup-update" else None
    return {
        "children": [],
        "mode": mode,
        "sha256": _sha256(proposed),
        "type": "regular",
    }


def _manifest_payload(
    *,
    preview: MigrationPreview,
    entries: Sequence[dict[str, object]],
    status_value: str,
    unrecovered: Sequence[str] = (),
) -> dict[str, object]:
    return {
        "backup_dir": str(preview.backup_dir),
        "entries": list(entries),
        "from": preview.from_version,
        "preview_fingerprint": preview.fingerprint,
        "root": str(preview.root),
        "schema": "reporivet.migration-backup/v1",
        "status": status_value,
        "unrecovered": list(unrecovered),
    }


def _write_manifest(path: Path, payload: Mapping[str, object]) -> None:
    content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    temporary = path.parent / f".{path.name}.tmp"
    if temporary.exists() or temporary.is_symlink():
        raise InitError(f"backup manifest temporary path already exists: {temporary}")
    descriptor = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    try:
        _RootView._write_all(descriptor, content)
        os.fchmod(descriptor, 0o600)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    try:
        if path.exists() and (path.is_symlink() or not path.is_file()):
            raise InitError(f"backup manifest path is unsafe: {path}")
        os.replace(temporary, path)
        path.chmod(0o600)
    except Exception:
        try:
            temporary.unlink()
        except OSError:
            pass
        raise


def _create_external_backup(
    preview: MigrationPreview,
    specs: Sequence[_MutationSpec],
) -> tuple[Path, dict[str, object]]:
    backup = preview.backup_dir
    parent = backup.parent
    if not parent.exists() or not parent.is_dir():
        raise InitError("migration backup parent must already exist as an external directory")
    if backup.exists() or backup.is_symlink():
        raise InitError("migration backup directory must not already exist")
    try:
        backup.mkdir(mode=0o700, parents=False, exist_ok=False)
        backup.chmod(0o700)
    except OSError as exc:
        raise InitError(f"cannot create external migration backup: {exc}") from exc

    entries: list[dict[str, object]] = []
    view = _RootView(preview.root)
    try:
        for spec in specs:
            state = view.snapshot(
                spec.path,
                list_directory=spec.expected_type == "directory",
            )
            if not _state_matches_spec(state, spec):
                raise InitError(
                    f"migration target changed before backup: {spec.path}; rerun preview"
                )
            backup_path: str | None = None
            if state.kind == "regular":
                if state.content is None:
                    raise InitError(f"migration preimage could not be read safely: {spec.path}")
                relative_backup = Path("preimages") / spec.path
                destination = backup / relative_backup
                destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                for parent_path in (destination.parent, *destination.parent.parents):
                    if parent_path == backup.parent:
                        break
                    if parent_path == backup or backup in parent_path.parents:
                        parent_path.chmod(0o700)
                descriptor = os.open(
                    destination,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                    0o600,
                )
                try:
                    _RootView._write_all(descriptor, state.content)
                    os.fchmod(descriptor, 0o600)
                finally:
                    os.close(descriptor)
                backup_path = relative_backup.as_posix()
            entries.append(
                {
                    "operation": spec.operation,
                    "path": spec.path,
                    "postimage": _planned_postimage(spec, state),
                    "preimage": _preimage_dict(state, backup_path),
                }
            )
    except Exception:
        view.close()
        raise
    view.close()

    manifest = _manifest_payload(
        preview=preview,
        entries=entries,
        status_value="prepared",
    )
    manifest_path = backup / MANIFEST_NAME
    _write_manifest(manifest_path, manifest)
    return manifest_path, manifest


def _image_matches(state: _PathState, image: Mapping[str, object]) -> bool:
    kind = image.get("type")
    if state.kind != kind:
        return False
    if kind == "regular":
        if state.sha256 != image.get("sha256"):
            return False
        mode = image.get("mode")
        return mode is None or state.mode == mode
    if kind == "directory":
        mode = image.get("mode")
        children = image.get("children", [])
        return (
            (mode is None or state.mode == mode)
            and list(state.children) == list(children)
        )
    return kind == "missing"


def _validate_preimages_current(root: Path, entries: Sequence[Mapping[str, object]]) -> None:
    view = _RootView(root)
    changed: list[str] = []
    try:
        for entry in entries:
            path = str(entry["path"])
            image = entry["preimage"]
            assert isinstance(image, Mapping)
            state = view.snapshot(
                path,
                list_directory=image.get("type") == "directory",
            )
            if not _image_matches(state, image):
                changed.append(path)
    finally:
        view.close()
    if changed:
        raise InitError(
            "migration target changed immediately before mutation: "
            + ", ".join(sorted(changed))
            + "; rerun preview"
        )


def _apply_setup_create(transaction: _GuidedSetupTransaction, action: SetupAction) -> None:
    transaction.create_file(action.path, action.content.encode("utf-8"))


def _apply_setup_update(transaction: _GuidedSetupTransaction, action: SetupAction) -> None:
    transaction.update_file(
        action.path,
        action.content.encode("utf-8"),
        action.current_sha256,
    )


def _apply_document_first_setup(preview: MigrationPreview) -> None:
    transaction = _GuidedSetupTransaction(preview.root)
    try:
        try:
            draft = _initial_definition(preview.root, None)
            current = _build_guided_setup_preview(
                root=preview.root,
                with_claude_settings=False,
                state_reader=transaction.regular_file_state,
                draft=draft,
            )
            if current.fingerprint != preview.setup_preview.fingerprint:
                raise InitError("document-first setup input changed after migration preview")
            for action in current.actions:
                _assert_action_current(
                    preview.root,
                    action,
                    state_reader=transaction.regular_file_state,
                )
            for action in current.actions:
                if action.action == "create":
                    _assert_action_current(
                        preview.root,
                        action,
                        state_reader=transaction.regular_file_state,
                    )
                    _apply_setup_create(transaction, action)
                elif action.action == "update":
                    _assert_action_current(
                        preview.root,
                        action,
                        state_reader=transaction.regular_file_state,
                    )
                    _apply_setup_update(transaction, action)
                else:
                    _assert_action_current(
                        preview.root,
                        action,
                        state_reader=transaction.regular_file_state,
                    )
            transaction.commit()
        except Exception as exc:
            try:
                transaction.rollback()
            except InitError as rollback_exc:
                raise InitError(
                    f"document-first setup failed ({exc}); setup rollback failed ({rollback_exc})"
                ) from rollback_exc
            raise
    finally:
        transaction.close()


def _apply_remove_file(view: _RootView, entry: LegacyInventoryEntry) -> None:
    view.unlink_regular(
        entry.path,
        expected_sha256=entry.current_sha256,
        expected_mode=entry.current_mode,
    )


def _apply_remove_directory(view: _RootView, entry: LegacyInventoryEntry) -> None:
    view.remove_empty_directory(entry.path, expected_mode=entry.current_mode)


def _capture_postimages(
    root: Path,
    entries: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    view = _RootView(root)
    updated: list[dict[str, object]] = []
    try:
        for entry in entries:
            path = str(entry["path"])
            operation = str(entry["operation"])
            state = view.snapshot(
                path,
                list_directory=operation == "setup-create-directory",
            )
            expected_type = (
                "missing"
                if operation in {"remove-file", "remove-directory"}
                else "directory"
                if operation == "setup-create-directory"
                else "regular"
            )
            if state.kind != expected_type:
                raise InitError(f"migration postimage has an unexpected type: {path}")
            planned = entry["postimage"]
            assert isinstance(planned, Mapping)
            if state.kind == "regular" and state.sha256 != planned.get("sha256"):
                raise InitError(f"migration postimage bytes do not match the preview: {path}")
            if state.kind == "regular" and state.content is None:
                raise InitError(f"migration postimage could not be read safely: {path}")
            postimage = {
                "children": list(state.children),
                "mode": state.mode,
                "sha256": state.sha256,
                "type": state.kind,
            }
            updated.append({**entry, "postimage": postimage})
    finally:
        view.close()
    return updated


def _read_backup_content(backup: Path, image: Mapping[str, object]) -> bytes:
    relative = image.get("backup_path")
    if not isinstance(relative, str) or not relative:
        raise InitError("backup manifest is missing a regular-file preimage path")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "preimages":
        raise InitError("backup manifest contains an unsafe preimage path")
    view = _RootView(backup)
    try:
        state = view.snapshot(relative)
    finally:
        view.close()
    if (
        state.kind != "regular"
        or state.content is None
        or state.sha256 != image.get("sha256")
    ):
        raise InitError("backup preimage bytes or checksum do not match the manifest")
    if state.mode is None or state.mode & 0o077:
        raise InitError("backup preimage permissions are not mode-restricted")
    return state.content


def _directory_state_is_safe_subset(state: _PathState, image: Mapping[str, object]) -> bool:
    if state.kind != "directory" or state.mode != image.get("mode"):
        return False
    expected = image.get("children", [])
    return isinstance(expected, list) and set(state.children).issubset(set(str(item) for item in expected))


def _automatic_restore(
    *,
    root: Path,
    backup: Path,
    entries: Sequence[Mapping[str, object]],
) -> list[str]:
    errors: list[str] = []
    view = _RootView(root)
    try:
        preexisting_directories = sorted(
            (
                entry
                for entry in entries
                if isinstance(entry.get("preimage"), Mapping)
                and entry["preimage"].get("type") == "directory"  # type: ignore[union-attr]
            ),
            key=lambda entry: len(Path(str(entry["path"])).parts),
        )
        for entry in preexisting_directories:
            path = str(entry["path"])
            image = entry["preimage"]
            assert isinstance(image, Mapping)
            current = view.snapshot(path, read_regular=False, list_directory=True)
            try:
                if current.kind == "missing":
                    mode = image.get("mode")
                    if not isinstance(mode, int):
                        raise InitError("backup directory preimage is missing its mode")
                    view.make_directory(path, mode)
                elif not _directory_state_is_safe_subset(current, image):
                    raise InitError("directory contains an unrecognized change")
            except Exception as exc:
                errors.append(f"{path}: {exc}")

        regular_preimages = sorted(
            (
                entry
                for entry in entries
                if isinstance(entry.get("preimage"), Mapping)
                and entry["preimage"].get("type") == "regular"  # type: ignore[union-attr]
            ),
            key=lambda entry: len(Path(str(entry["path"])).parts),
        )
        for entry in regular_preimages:
            path = str(entry["path"])
            preimage = entry["preimage"]
            postimage = entry["postimage"]
            assert isinstance(preimage, Mapping) and isinstance(postimage, Mapping)
            current = view.snapshot(path)
            try:
                if _image_matches(current, preimage):
                    continue
                content = _read_backup_content(backup, preimage)
                mode = preimage.get("mode")
                if not isinstance(mode, int):
                    raise InitError("regular preimage is missing its mode")
                if current.kind == "missing" and postimage.get("type") == "missing":
                    view.create_regular(path, content, mode)
                elif current.kind == "regular" and _image_matches(current, postimage):
                    view.replace_regular(
                        path,
                        expected_sha256=current.sha256,
                        expected_mode=current.mode,
                        content=content,
                        mode=mode,
                    )
                else:
                    raise InitError("path contains an unrecognized concurrent change")
            except Exception as exc:
                errors.append(f"{path}: {exc}")

        created_files = sorted(
            (
                entry
                for entry in entries
                if isinstance(entry.get("preimage"), Mapping)
                and entry["preimage"].get("type") == "missing"  # type: ignore[union-attr]
                and isinstance(entry.get("postimage"), Mapping)
                and entry["postimage"].get("type") == "regular"  # type: ignore[union-attr]
            ),
            key=lambda entry: len(Path(str(entry["path"])).parts),
            reverse=True,
        )
        for entry in created_files:
            path = str(entry["path"])
            postimage = entry["postimage"]
            assert isinstance(postimage, Mapping)
            current = view.snapshot(path)
            try:
                if current.kind == "missing":
                    continue
                if not _image_matches(current, postimage):
                    raise InitError("created path contains an unrecognized concurrent change")
                view.unlink_regular(
                    path,
                    expected_sha256=current.sha256,
                    expected_mode=current.mode,
                )
            except Exception as exc:
                errors.append(f"{path}: {exc}")

        created_directories = sorted(
            (
                entry
                for entry in entries
                if isinstance(entry.get("preimage"), Mapping)
                and entry["preimage"].get("type") == "missing"  # type: ignore[union-attr]
                and isinstance(entry.get("postimage"), Mapping)
                and entry["postimage"].get("type") == "directory"  # type: ignore[union-attr]
            ),
            key=lambda entry: len(Path(str(entry["path"])).parts),
            reverse=True,
        )
        for entry in created_directories:
            path = str(entry["path"])
            current = view.snapshot(path, read_regular=False, list_directory=True)
            try:
                if current.kind == "missing":
                    continue
                if current.kind != "directory" or current.children:
                    raise InitError("created directory contains a later or unrecovered path")
                view.remove_empty_directory(path, expected_mode=current.mode)
            except Exception as exc:
                errors.append(f"{path}: {exc}")
    finally:
        view.close()

    if not errors:
        verification = _RootView(root)
        try:
            for entry in entries:
                path = str(entry["path"])
                image = entry["preimage"]
                assert isinstance(image, Mapping)
                state = verification.snapshot(
                    path,
                    list_directory=image.get("type") == "directory",
                )
                if not _image_matches(state, image):
                    errors.append(f"{path}: restored state does not match the preimage")
        finally:
            verification.close()
    return errors


def apply_migration(
    *,
    root: Path,
    from_version: str,
    approve_preview: str,
    backup_dir: Path,
) -> MigrationResult:
    preview = preview_migration(
        root=root,
        from_version=from_version,
        backup_dir=backup_dir,
    )
    if not approve_preview or approve_preview != preview.fingerprint:
        raise InitError(
            "migration preview approval does not match the current target and external backup destination; rerun migrate --preview"
        )
    if preview.plan_blockers:
        paths = ", ".join(str(item["path"]) for item in preview.plan_blockers)
        raise InitError(
            "active Plan still depends on legacy Gate or Verification Run fields; reconcile it before migration: "
            + paths
        )
    if preview.blockers:
        paths = ", ".join(item["path"] for item in preview.blockers)
        raise InitError("migration preview contains a blocker; no backup or repository mutation occurred: " + paths)

    specs = _mutation_specs(preview)
    manifest_path, manifest = _create_external_backup(preview, specs)
    entries = manifest["entries"]
    assert isinstance(entries, list)
    try:
        immediate = preview_migration(
            root=preview.root,
            from_version=from_version,
            backup_dir=preview.backup_dir,
        )
        if immediate.fingerprint != preview.fingerprint:
            raise InitError(
                "migration target or fingerprint changed after backup and immediately before mutation"
            )
        _validate_preimages_current(preview.root, entries)

        _apply_document_first_setup(preview)

        removal_view = _RootView(preview.root)
        try:
            for entry in preview.legacy_inventory:
                if entry.action == "remove" and entry.path != "dev":
                    _apply_remove_file(removal_view, entry)
            dev_entry = next(
                (entry for entry in preview.legacy_inventory if entry.path == "dev"),
                None,
            )
            if dev_entry is not None and dev_entry.action == "remove":
                _apply_remove_directory(removal_view, dev_entry)
        finally:
            removal_view.close()

        successful_entries = _capture_postimages(preview.root, entries)
        successful_manifest = _manifest_payload(
            preview=preview,
            entries=successful_entries,
            status_value="successful",
        )
        _write_manifest(manifest_path, successful_manifest)
        return MigrationResult("applied", preview.root, manifest_path, preview.fingerprint)
    except Exception as exc:
        unrecovered = _automatic_restore(
            root=preview.root,
            backup=preview.backup_dir,
            entries=entries,
        )
        failure_manifest = _manifest_payload(
            preview=preview,
            entries=entries,
            status_value=(
                "failed-with-unrecovered-paths"
                if unrecovered
                else "rolled-back-after-failure"
            ),
            unrecovered=unrecovered,
        )
        try:
            _write_manifest(manifest_path, failure_manifest)
        except Exception as manifest_exc:
            unrecovered.append(f"backup manifest status: {manifest_exc}")
        if unrecovered:
            raise InitError(
                f"migration failed ({exc}); automatic rollback left unrecovered truth: "
                + "; ".join(unrecovered)
            ) from exc
        raise InitError(f"migration failed ({exc}) and was automatically rolled back") from exc


def _safe_manifest_path(manifest: Path) -> Path:
    expanded = manifest.expanduser()
    absolute = Path(os.path.abspath(expanded))
    if absolute.is_symlink():
        raise InitError("rollback manifest must be a regular non-symlink file")
    normalized = Path(os.path.realpath(absolute.parent)) / absolute.name
    if not normalized.exists() or normalized.is_symlink() or not normalized.is_file():
        raise InitError("rollback manifest is missing or not a regular non-symlink file")
    if stat.S_IMODE(normalized.stat().st_mode) & 0o077:
        raise InitError("rollback manifest permissions are not mode-restricted")
    return normalized


def _load_successful_manifest(manifest_path: Path) -> dict[str, object]:
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InitError(f"cannot read rollback manifest: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema") != "reporivet.migration-backup/v1":
        raise InitError("rollback manifest schema is invalid")
    if payload.get("status") != "successful":
        raise InitError("rollback requires a successful migration backup manifest")
    root_value = payload.get("root")
    backup_value = payload.get("backup_dir")
    fingerprint = payload.get("preview_fingerprint")
    entries = payload.get("entries")
    if not isinstance(root_value, str) or not Path(root_value).is_absolute():
        raise InitError("rollback manifest root is invalid")
    if not isinstance(backup_value, str) or Path(backup_value) != manifest_path.parent:
        raise InitError("rollback manifest backup directory does not match its location")
    if not isinstance(fingerprint, str) or re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None:
        raise InitError("rollback manifest fingerprint is invalid")
    if not isinstance(entries, list):
        raise InitError("rollback manifest entries are invalid")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise InitError("rollback manifest contains a malformed entry")
        relative = entry.get("path")
        if not isinstance(relative, str):
            raise InitError("rollback manifest entry path is invalid")
        parts = Path(relative).parts
        if (
            Path(relative).is_absolute()
            or not parts
            or any(part in {"", ".", ".."} for part in parts)
            or relative in seen
        ):
            raise InitError("rollback manifest contains an unsafe or duplicate target path")
        if relative == ".harness/runs" or relative.startswith(".harness/runs/"):
            raise InitError("rollback manifest must not contain retained .harness/runs content")
        seen.add(relative)
        preimage = entry.get("preimage")
        postimage = entry.get("postimage")
        if not isinstance(preimage, dict) or not isinstance(postimage, dict):
            raise InitError("rollback manifest entry is missing preimage or postimage")
        if preimage.get("type") == "regular":
            _read_backup_content(manifest_path.parent, preimage)
    return payload


def _validate_postimages_current(
    root: Path,
    entries: Sequence[Mapping[str, object]],
) -> None:
    changed: list[str] = []
    view = _RootView(root)
    try:
        for entry in entries:
            path = str(entry["path"])
            image = entry["postimage"]
            assert isinstance(image, Mapping)
            state = view.snapshot(
                path,
                list_directory=image.get("type") == "directory",
            )
            if not _image_matches(state, image):
                changed.append(path)
    finally:
        view.close()
    if changed:
        raise InitError(
            "post-migration user change detected at "
            + ", ".join(sorted(changed))
            + "; refusing rollback without modifying the repository"
        )


def _strict_restore(
    *,
    root: Path,
    backup: Path,
    entries: Sequence[Mapping[str, object]],
) -> None:
    view = _RootView(root)
    try:
        preexisting_directories = sorted(
            (
                entry
                for entry in entries
                if isinstance(entry.get("preimage"), Mapping)
                and entry["preimage"].get("type") == "directory"  # type: ignore[union-attr]
            ),
            key=lambda entry: len(Path(str(entry["path"])).parts),
        )
        for entry in preexisting_directories:
            path = str(entry["path"])
            preimage = entry["preimage"]
            assert isinstance(preimage, Mapping)
            current = view.snapshot(path, read_regular=False)
            if current.kind != "missing":
                raise InitError(f"rollback target changed after validation: {path}")
            mode = preimage.get("mode")
            if not isinstance(mode, int):
                raise InitError(f"rollback directory preimage has no mode: {path}")
            view.make_directory(path, mode)

        regular_preimages = sorted(
            (
                entry
                for entry in entries
                if isinstance(entry.get("preimage"), Mapping)
                and entry["preimage"].get("type") == "regular"  # type: ignore[union-attr]
            ),
            key=lambda entry: len(Path(str(entry["path"])).parts),
        )
        for entry in regular_preimages:
            path = str(entry["path"])
            preimage = entry["preimage"]
            postimage = entry["postimage"]
            assert isinstance(preimage, Mapping) and isinstance(postimage, Mapping)
            content = _read_backup_content(backup, preimage)
            mode = preimage.get("mode")
            if not isinstance(mode, int):
                raise InitError(f"rollback regular preimage has no mode: {path}")
            current = view.snapshot(path)
            if postimage.get("type") == "missing":
                if current.kind != "missing":
                    raise InitError(f"rollback target changed after validation: {path}")
                view.create_regular(path, content, mode)
            else:
                if not _image_matches(current, postimage):
                    raise InitError(f"rollback target changed after validation: {path}")
                view.replace_regular(
                    path,
                    expected_sha256=current.sha256,
                    expected_mode=current.mode,
                    content=content,
                    mode=mode,
                )

        created_files = sorted(
            (
                entry
                for entry in entries
                if isinstance(entry.get("preimage"), Mapping)
                and entry["preimage"].get("type") == "missing"  # type: ignore[union-attr]
                and isinstance(entry.get("postimage"), Mapping)
                and entry["postimage"].get("type") == "regular"  # type: ignore[union-attr]
            ),
            key=lambda entry: len(Path(str(entry["path"])).parts),
            reverse=True,
        )
        for entry in created_files:
            path = str(entry["path"])
            postimage = entry["postimage"]
            assert isinstance(postimage, Mapping)
            current = view.snapshot(path)
            if not _image_matches(current, postimage):
                raise InitError(f"rollback target changed after validation: {path}")
            view.unlink_regular(
                path,
                expected_sha256=current.sha256,
                expected_mode=current.mode,
            )

        created_directories = sorted(
            (
                entry
                for entry in entries
                if isinstance(entry.get("preimage"), Mapping)
                and entry["preimage"].get("type") == "missing"  # type: ignore[union-attr]
                and isinstance(entry.get("postimage"), Mapping)
                and entry["postimage"].get("type") == "directory"  # type: ignore[union-attr]
            ),
            key=lambda entry: len(Path(str(entry["path"])).parts),
            reverse=True,
        )
        for entry in created_directories:
            path = str(entry["path"])
            current = view.snapshot(path, read_regular=False, list_directory=True)
            if current.kind != "directory" or current.children:
                raise InitError(f"rollback directory changed after validation: {path}")
            view.remove_empty_directory(path, expected_mode=current.mode)
    finally:
        view.close()

    verification = _RootView(root)
    failures: list[str] = []
    try:
        for entry in entries:
            path = str(entry["path"])
            preimage = entry["preimage"]
            assert isinstance(preimage, Mapping)
            state = verification.snapshot(
                path,
                list_directory=preimage.get("type") == "directory",
            )
            if not _image_matches(state, preimage):
                failures.append(path)
    finally:
        verification.close()
    if failures:
        raise InitError("rollback restoration did not match preimages: " + ", ".join(failures))


def rollback_migration(*, manifest: Path) -> MigrationResult:
    manifest_path = _safe_manifest_path(manifest)
    payload = _load_successful_manifest(manifest_path)
    root = validate_root(Path(str(payload["root"])))
    backup = manifest_path.parent
    if stat.S_IMODE(backup.stat().st_mode) & 0o077:
        raise InitError("rollback backup directory permissions are not mode-restricted")
    entries = payload["entries"]
    assert isinstance(entries, list)
    _validate_postimages_current(root, entries)
    _strict_restore(root=root, backup=backup, entries=entries)
    payload["status"] = "rolled-back"
    _write_manifest(manifest_path, payload)
    return MigrationResult(
        "rolled-back",
        root,
        manifest_path,
        str(payload["preview_fingerprint"]),
    )


def legacy_02_upgrade_surfaces_present(root: Path) -> bool:
    view = _RootView(root)
    try:
        for relative in sorted(LEGACY_FILE_SHA256):
            state = view.snapshot(relative)
            if state.kind == "missing":
                continue
            if state.kind != "regular" or state.content is None:
                return True
            if _has_02_managed_marker(state.content):
                return True
        for relative in LEGACY_RUNTIME_PATHS:
            if relative == ".harness/runs":
                continue
            if view.snapshot(relative, read_regular=False, list_directory=False).kind != "missing":
                return True
        config = view.snapshot("dev/harness.toml")
        if config.kind == "missing":
            return False
        if config.kind != "regular" or config.content is None:
            return True
        try:
            text = config.content.decode("utf-8")
        except UnicodeError:
            return True
        return all(token in text for token in ("version = 1", "[project]", "[commands]", "[paths]"))
    finally:
        view.close()
