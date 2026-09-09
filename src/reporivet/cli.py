from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .initializer import InitError, audit_project, doctor_project, init_project, upgrade_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reporivet",
        description="Provide optional repository entrypoint guidance without installing a target runtime.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="add a bounded AGENTS entrypoint block without overwriting user files")
    init.add_argument("--root", type=Path, default=Path.cwd())
    init.add_argument("--name", default="")
    init.add_argument("--claude", action="store_true", help="also add a thin pointer in CLAUDE.md")
    init.add_argument("--dry-run", action="store_true")

    audit = sub.add_parser("audit", help="read-only bounded inventory of repository entry paths")
    audit.add_argument("--root", type=Path, default=Path.cwd())

    upgrade = sub.add_parser("upgrade", help="refresh the entrypoint block; refuse released 0.2 targets")
    upgrade.add_argument("--root", type=Path, default=Path.cwd())
    upgrade.add_argument("--claude", action="store_true", help="also add or refresh a thin CLAUDE.md pointer")
    upgrade.add_argument("--dry-run", action="store_true")

    doctor = sub.add_parser("doctor", help="check entrypoint ownership mechanically without modifying files")
    doctor.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            init_project(root=args.root, name=args.name, claude=args.claude, dry_run=args.dry_run)
            return 0
        if args.command == "audit":
            print(audit_project(root=args.root).render(), end="")
            return 0
        if args.command == "upgrade":
            upgrade_project(root=args.root, claude=args.claude, dry_run=args.dry_run)
            return 0
        if args.command == "doctor":
            return doctor_project(args.root)
    except InitError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2
