"""Project the source-only CLAUDE portable block without normalizing its bytes."""
from __future__ import annotations

import argparse
import os
import re
import stat
import sys
import tempfile
from pathlib import Path


START = b"<!-- reporivet:portable:start -->"
END = b"<!-- reporivet:portable:end -->"


def safe_directories(path: Path) -> None:
    for directory in (*reversed(path.parents), path):
        if not stat.S_ISDIR(directory.lstat().st_mode):
            raise ValueError(f"unsafe directory (symlink or non-directory): {directory}")


def snapshot(path: Path) -> tuple[bytes, int, int, int, int] | None:
    """Inspect before opening, then verify the opened regular-file identity."""
    safe_directories(path.parent)
    try:
        before = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"unsafe nonregular file or symlink: {path}")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError(f"file changed before read: {path}")
        data = stream.read()
    data.decode("utf-8")
    return data, stat.S_IMODE(opened.st_mode), opened.st_dev, opened.st_ino, opened.st_mtime_ns


def portable_payload(data: bytes) -> bytes:
    data.decode("utf-8")
    markers: list[tuple[bytes, int, int]] = []
    offset = 0
    fence: bytes | None = None
    # Split only on LF: Unicode separators and CRLF inside the payload are bytes.
    lines = data.split(b"\n")
    for index, part in enumerate(lines):
        raw = part + (b"\n" if index < len(lines) - 1 else b"")
        line = raw.removesuffix(b"\n").removesuffix(b"\r")
        if b"reporivet:portable" in line:
            if line not in (START, END) or fence is not None:
                raise ValueError("portable marker must be standalone and outside fenced code")
            markers.append((line, offset, offset + len(raw)))
        match = re.match(rb"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if match:
            run, suffix = match.groups()
            if fence is None:
                fence = run
            elif run[:1] == fence[:1] and len(run) >= len(fence) and not suffix.strip():
                fence = None
        offset += len(raw)
    if [marker[0] for marker in markers] != [START, END]:
        raise ValueError("expected exactly one ordered portable start/end marker pair")
    return data[markers[0][2]:markers[1][1]]


def sync(root: Path, *, check: bool) -> bool:
    """Return whether in sync; reject observed divergence before atomic replacement.

    Preimage checks are not OS-level isolation against arbitrary concurrent writers.
    """
    root = Path(root)
    if not root.is_absolute():
        root = Path.cwd() / root
    # Inspect every original prefix before any symlink/.. traversal can be hidden.
    safe_directories(root)
    source, target = root / "CLAUDE.md", root / "AGENTS.md"
    # Check both file types before either can be opened (notably FIFO inputs).
    for path in (source, target):
        try:
            info = path.lstat()
        except FileNotFoundError:
            if path == source:
                raise ValueError(f"missing source contract: {path}") from None
        else:
            if not stat.S_ISREG(info.st_mode):
                raise ValueError(f"unsafe nonregular file or symlink: {path}")
    source_before, target_before = snapshot(source), snapshot(target)
    if source_before is None:
        raise ValueError(f"missing source contract: {source}")
    payload = portable_payload(source_before[0])
    if target_before is not None and target_before[0] == payload:
        return True
    if check:
        return False
    descriptor, name = tempfile.mkstemp(prefix=".AGENTS.md.", dir=root)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fchmod(stream.fileno(), target_before[1] if target_before else 0o644)
            os.fsync(stream.fileno())
        if snapshot(source) != source_before or snapshot(target) != target_before:
            raise ValueError("contract preimage changed; refusing replacement")
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift without writing")
    args = parser.parse_args()
    try:
        if not sync(Path(__file__).parent.parent, check=args.check):
            print("AGENTS.md drift: run ./dev/agent-contract-sync", file=sys.stderr)
            return 1
    except (OSError, ValueError) as error:
        print(f"agent-contract-sync: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
