from __future__ import annotations

import argparse
import contextlib
import sys
from pathlib import Path

from .guided import (
    apply_guided_setup,
    definition_status,
    preview_guided_setup,
    resume_guided_definition,
    run_document_first_doctor,
    start_guided_definition,
)
from .initializer import (
    InitError,
    audit_project,
    initialize_project,
    upgrade_project,
)
from .migration import apply_migration, preview_migration, rollback_migration


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reporivet",
        description="Initialize and maintain a repository-local, document-first agent harness.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    setup = sub.add_parser("setup", help="audit, define, preview, and apply repository setup")
    setup.add_argument("--root", type=Path, required=True)
    setup.add_argument("--answers", type=Path, help="JSON answers keyed by guided topic")
    setup.add_argument("--with-claude-settings", action="store_true", help="include the optional deny-only Claude settings file")
    setup.add_argument("--dry-run", action="store_true")
    setup.add_argument("--apply", action="store_true", help="apply the exact current setup preview")
    setup.add_argument("--approve-preview", default="", help="SHA-256 fingerprint emitted by setup preview")

    define = sub.add_parser("define", help="start, resume, inspect, or apply a visible project definition")
    define.add_argument("action", choices=("start", "resume", "status", "finalize"))
    define.add_argument("--root", type=Path, default=Path.cwd())
    define.add_argument("--answers", type=Path, help="JSON answers keyed by guided topic for deterministic resume")
    define.add_argument("--apply", action="store_true", help="apply the exact current finalize preview")
    define.add_argument("--approve-preview", default="", help="SHA-256 fingerprint emitted by finalize preview")
    define.add_argument("--with-claude-settings", action="store_true", help="include the optional deny-only Claude settings file in the exact preview")
    define.add_argument("--dry-run", action="store_true")

    audit = sub.add_parser("audit", help="inventory an existing repository without executing project commands or writing files")
    audit.add_argument("--root", type=Path, default=Path.cwd())

    init = sub.add_parser("init", help="initialize a project without overwriting project-owned documents")
    init.add_argument("--root", type=Path, default=Path.cwd())
    init.add_argument("--name", default="")
    init.add_argument("--summary", default="")
    init.add_argument("--dry-run", action="store_true")

    upgrade = sub.add_parser("upgrade", help="maintain missing document-first bundle paths")
    upgrade.add_argument("--root", type=Path, default=Path.cwd())
    upgrade.add_argument("--dry-run", action="store_true")

    migrate = sub.add_parser(
        "migrate",
        help="retire exact legacy 0.2 runtime surfaces through an approved external-backup transaction",
    )
    migrate.add_argument("--root", type=Path)
    migrate.add_argument("--from", dest="from_version")
    mode = migrate.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--rollback", type=Path, metavar="MANIFEST")
    migrate.add_argument("--approve-preview", default="")
    migrate.add_argument("--backup-dir", type=Path)

    doctor = sub.add_parser("doctor", help="inspect document-first repository structure without modifying it")
    doctor.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "setup":
            approval = args.approve_preview.strip()
            if args.apply and not approval:
                raise InitError("setup --apply requires --approve-preview HASH")
            if args.approve_preview and not args.apply:
                raise InitError("--approve-preview requires setup --apply")
            if args.apply and args.answers:
                raise InitError("setup --apply does not accept --answers")
            if args.apply and args.dry_run:
                raise InitError("setup --apply cannot be combined with --dry-run")
            from .setup import coordinate_setup

            with contextlib.redirect_stdout(sys.stderr):
                envelope = coordinate_setup(
                    root=args.root,
                    answers=args.answers,
                    with_claude_settings=args.with_claude_settings,
                    dry_run=args.dry_run,
                    apply=args.apply,
                    approve_preview=args.approve_preview,
                    stdin_is_tty=sys.stdin.isatty(),
                )
            print(envelope.render(), end="")
            return 0
        if args.command == "define":
            if args.action == "start":
                if args.answers or args.apply or args.approve_preview or args.with_claude_settings:
                    raise InitError("define start accepts only --root and --dry-run")
                start_guided_definition(root=args.root, dry_run=args.dry_run)
                return 0
            if args.action == "resume":
                if args.apply or args.approve_preview or args.with_claude_settings:
                    raise InitError("define resume accepts --answers and --dry-run, not finalize options")
                resume_guided_definition(
                    root=args.root,
                    answers=args.answers,
                    dry_run=args.dry_run,
                )
                return 0
            if args.action == "status":
                if args.answers or args.apply or args.approve_preview or args.with_claude_settings or args.dry_run:
                    raise InitError("define status accepts only --root and is always read-only")
                print(definition_status(root=args.root), end="")
                return 0
            if args.answers:
                raise InitError("define finalize does not accept --answers; resume the visible draft first")
            if args.dry_run and args.apply:
                raise InitError("define finalize --apply cannot be combined with --dry-run")
            if args.apply:
                apply_guided_setup(
                    root=args.root,
                    approve_preview=args.approve_preview,
                    with_claude_settings=args.with_claude_settings,
                )
                return 0
            if args.approve_preview:
                raise InitError("--approve-preview requires define finalize --apply")
            print(
                preview_guided_setup(
                    root=args.root,
                    with_claude_settings=args.with_claude_settings,
                ).render(),
                end="",
            )
            return 0
        if args.command == "audit":
            print(audit_project(root=args.root).render(), end="")
            return 0
        if args.command == "init":
            initialize_project(
                root=args.root,
                name=args.name,
                summary=args.summary,
                dry_run=args.dry_run,
            )
            return 0
        if args.command == "upgrade":
            upgrade_project(
                root=args.root,
                dry_run=args.dry_run,
            )
            return 0
        if args.command == "migrate":
            if args.rollback is not None:
                if args.root is not None or args.from_version or args.backup_dir or args.approve_preview:
                    raise InitError(
                        "migrate --rollback accepts only the manifest path; do not combine it with preview or apply options"
                    )
                print(rollback_migration(manifest=args.rollback).render(), end="")
                return 0
            if args.root is None:
                raise InitError("migrate --preview and --apply require --root PATH")
            if args.from_version is None:
                raise InitError("migrate --preview and --apply require --from 0.2")
            if args.backup_dir is None:
                raise InitError(
                    "migrate --preview and --apply require an explicit external --backup-dir"
                )
            if args.preview:
                if args.approve_preview:
                    raise InitError("--approve-preview requires migrate --apply")
                print(
                    preview_migration(
                        root=args.root,
                        from_version=args.from_version,
                        backup_dir=args.backup_dir,
                    ).render(),
                    end="",
                )
                return 0
            if not args.approve_preview:
                raise InitError("migrate --apply requires --approve-preview HASH")
            print(
                apply_migration(
                    root=args.root,
                    from_version=args.from_version,
                    approve_preview=args.approve_preview,
                    backup_dir=args.backup_dir,
                ).render(),
                end="",
            )
            return 0
        if args.command == "doctor":
            return run_document_first_doctor(args.root)
    except InitError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2
