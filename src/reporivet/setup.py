from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .guided import (
    DEFINITION_DRAFT_PATH,
    DEFINITION_TOPICS,
    DefinitionDraft,
    SetupPreview,
    _apply_guided_setup_quiet,
    _prepare_setup_definition,
    _preview_setup_from_definition,
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

    if apply:
        preview, changes, draft = _apply_guided_setup_quiet(
            root=root,
            approve_preview=approve_preview,
            with_claude_settings=with_claude_settings,
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
            changes=changes,
            input_mode=input_mode,
            prompted=False,
            recorded=False,
            next_action="review-generated-files",
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
    preview = _preview_setup_from_definition(
        root=root,
        with_claude_settings=with_claude_settings,
        draft=step.draft,
    )
    has_conflicts = any(action.action == "conflict" for action in preview.actions)
    eligible_for_apply = not dry_run and not has_conflicts
    if has_conflicts:
        state = "conflict"
        next_action = "resolve-preview-conflicts"
    elif dry_run:
        state = "dry-run"
        next_action = "rerun-without-dry-run"
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
    )
