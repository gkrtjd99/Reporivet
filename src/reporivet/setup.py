from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable

from . import migration
from .guided import (
    DEFINITION_DRAFT_PATH,
    DEFINITION_TOPICS,
    DefinitionDraft,
    SetupAction,
    SetupDiagnostic,
    SetupPreview,
    _build_guided_setup_preview,
    _prepare_setup_definition,
    _read_definition,
)
from .initializer import AuditReport, ChangeSet, InitError, audit_project, validate_root


@dataclass(frozen=True)
class SetupEnvelope:
    root: str
    mode: str
    state: str
    audit: dict[str, object]
    definition: dict[str, object]
    preview: dict[str, object]
    eligible_for_apply: bool
    changes: dict[str, object]
    input: dict[str, object]
    next_action: str
    backup: dict[str, object] = field(default_factory=dict)
    schema: str = field(default="reporivet.setup/v1", init=False)

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "root": self.root,
            "mode": self.mode,
            "state": self.state,
            "audit": self.audit,
            "definition": self.definition,
            "preview": self.preview,
            "eligible_for_apply": self.eligible_for_apply,
            "changes": self.changes,
            "input": self.input,
            "next_action": self.next_action,
            "backup": self.backup,
        }

    def render(self) -> str:
        return json.dumps(
            self.as_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _changes_as_dict(root: Path, changes: ChangeSet) -> dict[str, object]:
    return {
        "created": sorted(_relative(root, path) for path in changes.created),
        "updated": sorted(_relative(root, path) for path in changes.updated),
        "skipped": sorted(_relative(root, path) for path in changes.skipped),
    }


def _definition_as_dict(
    draft: DefinitionDraft,
    *,
    draft_state: str,
) -> dict[str, object]:
    topics: dict[str, object] = {}
    for topic in DEFINITION_TOPICS:
        evidence = draft.evidence[topic.key]
        topics[topic.key] = {
            "title": topic.title,
            "question": topic.question,
            "confirmed": list(evidence.confirmed),
            "proposed": list(evidence.proposed),
            "open": list(evidence.open),
            "sources": list(evidence.sources),
        }
    return {
        "draft": {
            "path": DEFINITION_DRAFT_PATH.as_posix(),
            "state": draft_state,
        },
        "topics": topics,
    }


def _input_mode(
    *,
    answers: Path | None,
    dry_run: bool,
    apply: bool,
    stdin_is_tty: bool,
) -> str:
    if apply:
        return "none"
    if answers is not None:
        return "answers-file"
    if dry_run:
        return "disabled-dry-run"
    if stdin_is_tty:
        return "tty"
    return "non-tty"


def _envelope(
    *,
    root: Path,
    mode: str,
    state: str,
    audit: AuditReport,
    draft: DefinitionDraft,
    draft_state: str,
    preview: SetupPreview,
    eligible_for_apply: bool,
    changes: ChangeSet,
    input_mode: str,
    prompted: bool,
    recorded: bool,
    next_action: str,
    backup: dict[str, object],
) -> SetupEnvelope:
    return SetupEnvelope(
        root=str(root),
        mode=mode,
        state=state,
        audit=audit.as_dict(),
        definition=_definition_as_dict(draft, draft_state=draft_state),
        preview=preview.as_dict(),
        eligible_for_apply=eligible_for_apply,
        changes=_changes_as_dict(root, changes),
        input={
            "mode": input_mode,
            "prompted": prompted,
            "recorded": recorded,
        },
        next_action=next_action,
        backup=backup,
    )


def _normalize_setup_backup(root: Path, backup_dir: Path | None) -> Path | None:
    if backup_dir is None:
        return None
    return migration._normalize_backup_dir(root, backup_dir)


def _has_destructive_setup_actions(preview: SetupPreview) -> bool:
    return any(
        action.action in {"remove", "convert", "update"}
        for action in preview.actions
    )


def _backup_record(
    *,
    backup_dir: Path | None,
    required: bool,
    manifest: Path | None = None,
    status: str | None = None,
) -> dict[str, object]:
    if status is None:
        if manifest is not None:
            status = "applied"
        elif required and backup_dir is None:
            status = "required"
        elif backup_dir is not None:
            status = "available"
        else:
            status = "not-required"
    return {
        "directory": None if backup_dir is None else str(backup_dir),
        "manifest": None if manifest is None else str(manifest),
        "required": required,
        "status": status,
    }


def _setup_changes(root: Path, preview: SetupPreview) -> ChangeSet:
    changes = ChangeSet()
    for action in preview.actions:
        path = root / action.path
        if action.action == "create":
            changes.created.append(path)
        elif action.action == "update":
            changes.updated.append(path)
        elif action.action == "convert":
            if action.proposed_path is not None and action.destination_current_type == "missing":
                changes.created.append(root / action.proposed_path)
            if action.proposed_path is None and action.proposed_type == "regular":
                changes.updated.append(path)
            else:
                changes.skipped.append(path)
        else:
            changes.skipped.append(path)
    return changes


_SETUP_CANONICAL_CLEANUP_MODE = 0o644


def _mode_guard_setup_preview(preview: SetupPreview) -> SetupPreview:
    """Preserve cleanup candidates whose canonical file mode is unproven."""

    guarded: list[SetupAction] = []
    changed = False
    for action in preview.actions:
        if (
            action.action not in {"remove", "convert"}
            or action.ownership != "reporivet-generated"
            or action.current_type != "regular"
            or action.current_mode == _SETUP_CANONICAL_CLEANUP_MODE
        ):
            guarded.append(action)
            continue
        observed_mode = (
            f"{action.current_mode:o}" if action.current_mode is not None else "unknown"
        )
        diagnostic = SetupDiagnostic(
            action.path,
            "ownership-unproven",
            "legacy cleanup requires exact canonical regular-file mode 0644; "
            f"observed mode {observed_mode}",
        )
        guarded.append(
            replace(
                action,
                action="preserve",
                reason=(
                    "legacy generated bytes match but canonical mode is not 0644; "
                    "preserve the path for manual review"
                ),
                ownership="ambiguous",
                proposed_sha256=action.current_sha256,
                proposed_type=action.current_type,
                proposed_mode=action.current_mode,
                proposed_path=None,
                destination_type=None,
                destination_sha256="",
                destination_mode=None,
                destination_size=None,
                destination_current_type=None,
                destination_current_sha256="",
                destination_current_mode=None,
                destination_current_size=None,
                destination_content="",
                diagnostics=(*action.diagnostics, diagnostic),
            )
        )
        changed = True
    if not changed:
        return preview
    actions = tuple(
        sorted(
            guarded,
            key=lambda action: (
                action.path,
                action.action,
                action.proposed_path or "",
            ),
        )
    )
    return migration._rebuild_setup_preview(actions, preview.diagnostics)


def _bound_setup_preview(
    *,
    root: Path,
    with_claude_settings: bool,
    draft: DefinitionDraft,
    backup_dir: Path | None,
) -> SetupPreview:
    raw = _build_guided_setup_preview(
        root=root,
        with_claude_settings=with_claude_settings,
        draft=draft,
    )
    guarded = _mode_guard_setup_preview(raw)
    return migration._bind_setup_preview(
        guarded,
        root=root,
        backup_dir=backup_dir,
    )


def coordinate_setup(
    *,
    root: Path,
    answers: Path | None,
    with_claude_settings: bool,
    dry_run: bool,
    apply: bool,
    approve_preview: str,
    stdin_is_tty: bool,
    input_fn: Callable[[str], str] = input,
    backup_dir: Path | None = None,
) -> SetupEnvelope:
    if apply and answers is not None:
        raise InitError("setup --apply does not accept --answers; update the visible draft before previewing")
    if apply and dry_run:
        raise InitError("setup --apply cannot be combined with --dry-run")
    if apply and not approve_preview:
        raise InitError("setup --apply requires a nonempty --approve-preview HASH")
    if not apply and approve_preview:
        raise InitError("--approve-preview requires setup --apply")

    root = validate_root(root)
    report = audit_project(root=root)
    input_mode = _input_mode(
        answers=answers,
        dry_run=dry_run,
        apply=apply,
        stdin_is_tty=stdin_is_tty,
    )
    normalized_backup = _normalize_setup_backup(root, backup_dir)

    if apply:
        _, draft = _read_definition(root)
        preview = _bound_setup_preview(
            root=root,
            with_claude_settings=with_claude_settings,
            draft=draft,
            backup_dir=normalized_backup,
        )
        destructive = _has_destructive_setup_actions(preview)
        if not approve_preview or approve_preview != preview.fingerprint:
            raise InitError(
                "setup preview approval does not match the current target and external backup destination; rerun setup --preview"
            )
        if destructive and normalized_backup is None:
            raise InitError(
                "setup cleanup requires an external backup directory; rerun setup preview with --backup-dir"
            )
        conflicts = [
            action.path
            for action in preview.actions
            if action.action == "conflict"
        ]
        if conflicts:
            raise InitError(
                "setup preview contains unsafe target conflicts: "
                + ", ".join(conflicts)
            )

        def preview_factory() -> SetupPreview:
            return _mode_guard_setup_preview(
                _build_guided_setup_preview(
                    root=root,
                    with_claude_settings=with_claude_settings,
                    draft=draft,
                )
            )

        manifest = migration._apply_setup_transition(
            root=root,
            preview=preview,
            backup_dir=normalized_backup,
            preview_factory=preview_factory,
        )
        return _envelope(
            root=root,
            mode="apply",
            state="applied",
            audit=report,
            draft=draft,
            draft_state="unchanged",
            preview=preview,
            eligible_for_apply=False,
            changes=_setup_changes(root, preview),
            input_mode=input_mode,
            prompted=False,
            recorded=False,
            next_action="review-generated-files",
            backup=_backup_record(
                backup_dir=normalized_backup,
                required=destructive,
                manifest=manifest,
            ),
        )

    step = _prepare_setup_definition(
        root=root,
        report=report,
        answers=answers,
        dry_run=dry_run,
        input_fn=(
            input_fn
            if stdin_is_tty and answers is None and not dry_run
            else None
        ),
    )
    preview = _bound_setup_preview(
        root=root,
        with_claude_settings=with_claude_settings,
        draft=step.draft,
        backup_dir=normalized_backup,
    )
    has_conflicts = any(action.action == "conflict" for action in preview.actions)
    destructive = _has_destructive_setup_actions(preview)
    backup_missing = destructive and normalized_backup is None
    eligible_for_apply = not dry_run and not has_conflicts and not backup_missing
    if has_conflicts:
        state = "conflict"
        next_action = "resolve-preview-conflicts"
    elif dry_run:
        state = "dry-run"
        next_action = "rerun-without-dry-run"
    elif backup_missing:
        state = "backup-required"
        next_action = "rerun-with-external-backup-dir"
    else:
        state = "awaiting-approval"
        next_action = "apply-with-exact-preview-fingerprint"

    return _envelope(
        root=root,
        mode="dry-run" if dry_run else "preview",
        state=state,
        audit=report,
        draft=step.draft,
        draft_state=step.draft_state,
        preview=preview,
        eligible_for_apply=eligible_for_apply,
        changes=step.changes,
        input_mode=input_mode,
        prompted=step.prompted,
        recorded=step.recorded,
        next_action=next_action,
        backup=_backup_record(
            backup_dir=normalized_backup,
            required=destructive,
        ),
    )
