from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .initializer import InitError, apply_harness, doctor_project, upgrade_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-harness",
        description="Initialize and maintain a repository-local, document-first agent harness.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize a project without overwriting project-owned documents")
    init.add_argument("--root", type=Path, default=Path.cwd())
    init.add_argument("--name", default="")
    init.add_argument("--summary", default="")
    init.add_argument(
        "--project-kind",
        default="other",
        choices=("service", "web", "application", "library", "cli", "other"),
    )
    init.add_argument("--primary-language", default="")
    init.add_argument("--runtime", default="")
    init.add_argument("--with-ci", action="store_true")
    init.add_argument("--no-baseline-plan", action="store_true")
    init.add_argument("--skip-check", action="store_true")
    init.add_argument("--dry-run", action="store_true")

    upgrade = sub.add_parser("upgrade", help="refresh only harness-owned code and managed blocks")
    upgrade.add_argument("--root", type=Path, default=Path.cwd())
    upgrade.add_argument("--with-ci", action="store_true")
    upgrade.add_argument("--skip-check", action="store_true")
    upgrade.add_argument("--dry-run", action="store_true")

    doctor = sub.add_parser("doctor", help="inspect an initialized repository without modifying it")
    doctor.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            apply_harness(
                root=args.root,
                mode="init",
                name=args.name,
                summary=args.summary,
                kind=args.project_kind,
                primary_language=args.primary_language,
                runtime=args.runtime,
                with_ci=args.with_ci,
                baseline=not args.no_baseline_plan,
                dry_run=args.dry_run,
                skip_check=args.skip_check,
            )
            return 0
        if args.command == "upgrade":
            upgrade_project(
                root=args.root,
                with_ci=args.with_ci,
                dry_run=args.dry_run,
                skip_check=args.skip_check,
            )
            return 0
        if args.command == "doctor":
            return doctor_project(args.root)
    except InitError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2
