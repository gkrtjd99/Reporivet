from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import stat
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

from . import __version__
from .initializer import (
    AuditReport,
    ChangeSet,
    InitError,
    audit_project,
    ensure_safe_write_path,
    read_asset,
    symlink_component,
    validate_root,
)
from .procedures import (
    build_procedure_runbook_plan,
    calculate_procedure_runbook_path,
    render_procedure_runbook,
    _legacy_procedure_skill_ownership_proof,
)

DEFINITION_DRAFT_PATH = Path("docs/product-specs/project-definition.draft.md")
EVIDENCE_HEADINGS = ("Confirmed", "Proposed", "Open", "Sources")
ACTIVE_PLAN_STATES = frozenset({"proposed", "approved", "in-progress", "verifying", "blocked"})


@dataclass(frozen=True)
class DefinitionTopic:
    key: str
    title: str
    question: str


DEFINITION_TOPICS = (
    DefinitionTopic(
        "product",
        "Product, users, and success",
        "Who is this for, what problem should it solve, and what observable result means it is useful?",
    ),
    DefinitionTopic(
        "design",
        "Design direction and accessibility",
        "What design principles, interaction expectations, accessibility needs, or internationalization constraints should work preserve?",
    ),
    DefinitionTopic(
        "quality",
        "Quality and project commands",
        "Which project-owned test, lint, type, build, package, or smoke commands are required, and what evidence should they produce?",
    ),
    DefinitionTopic(
        "operations",
        "Running and operating the service",
        "How is the service run, released, observed, backed up, rolled back, recovered, and handled during an incident?",
    ),
    DefinitionTopic(
        "security",
        "Security and sensitive data",
        "What authentication, authorization, sensitive data, secrets, permissions, exposure, retention, and disclosure boundaries apply?",
    ),
    DefinitionTopic(
        "agents",
        "Main, implementation, and verification workflow",
        "How should Main divide work, what may implementation agents change, and what independent evidence must verification agents return?",
    ),
    DefinitionTopic(
        "procedures",
        "Repeatable procedures",
        "Which repeated procedures deserve a static runbook, including their trigger, stop conditions, evidence, permissions, and rollback?",
    ),
)
TOPIC_BY_KEY = {topic.key: topic for topic in DEFINITION_TOPICS}


@dataclass
class TopicEvidence:
    confirmed: list[str] = field(default_factory=list)
    proposed: list[str] = field(default_factory=list)
    open: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    def values(self, heading: str) -> list[str]:
        return getattr(self, heading.casefold())


@dataclass
class DefinitionDraft:
    evidence: dict[str, TopicEvidence]

    @property
    def confirmed_count(self) -> int:
        return sum(bool(self.evidence[topic.key].confirmed) for topic in DEFINITION_TOPICS)

    @property
    def next_topic(self) -> DefinitionTopic | None:
        return next(
            (topic for topic in DEFINITION_TOPICS if not self.evidence[topic.key].confirmed),
            None,
        )


@dataclass(frozen=True)
class _SetupDefinitionStep:
    draft: DefinitionDraft
    changes: ChangeSet
    draft_state: str
    prompted: bool
    recorded: bool


@dataclass(frozen=True, slots=True)
class SetupDiagnostic:
    """A deterministic diagnostic attached to one setup classification."""

    path: str
    code: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "detail": self.detail, "path": self.path}


@dataclass(frozen=True, slots=True)
class SetupAction:
    """One preview classification and its safe, bounded postimage proposal.

    The first six fields are retained for migration compatibility.  The
    additional fields make the classification self-describing without exposing
    existing file bytes in the serialized preview.
    """

    path: str
    action: str
    reason: str
    current_sha256: str
    proposed_sha256: str
    content: str
    ownership: str = "project-owned"
    current_type: str = "missing"
    current_mode: int | None = None
    current_size: int | None = None
    current_children: tuple[str, ...] = ()
    proposed_type: str = "regular"
    proposed_mode: int | None = None
    proposed_path: str | None = None
    destination_type: str | None = None
    destination_sha256: str = ""
    destination_mode: int | None = None
    destination_size: int | None = None
    destination_current_type: str | None = None
    destination_current_sha256: str = ""
    destination_current_mode: int | None = None
    destination_current_size: int | None = None
    destination_content: str = field(default="", repr=False, compare=False)
    diagnostics: tuple[SetupDiagnostic, ...] = ()

    @property
    def operation(self) -> str:
        """Descriptive alias for the legacy ``action`` field."""

        return self.action

    @property
    def preimage(self) -> dict[str, object]:
        return {
            "children": list(self.current_children),
            "mode": self.current_mode,
            "sha256": self.current_sha256 or None,
            "size": self.current_size,
            "type": self.current_type,
        }

    @property
    def postimage(self) -> dict[str, object]:
        if self.action in {"preserve", "conflict"}:
            return {
                "mode": self.current_mode,
                "sha256": self.current_sha256 or None,
                "size": self.current_size,
                "type": self.current_type,
            }
        result: dict[str, object] = {
            "mode": self.proposed_mode,
            "sha256": self.proposed_sha256 or None,
            "size": (
                len(self.content.encode("utf-8"))
                if self.proposed_type == "regular"
                else None
            ),
            "type": self.proposed_type,
        }
        if self.proposed_path is not None:
            result["path"] = self.proposed_path
        return result

    @property
    def destination(self) -> dict[str, object] | None:
        if self.proposed_path is None:
            return None
        return {
            "content": self.destination_content or None,
            "current": {
                "mode": self.destination_current_mode,
                "sha256": self.destination_current_sha256 or None,
                "size": self.destination_current_size,
                "type": self.destination_current_type,
            },
            "mode": self.destination_mode,
            "path": self.proposed_path,
            "sha256": self.destination_sha256 or None,
            "size": self.destination_size,
            "type": self.destination_type,
        }

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            # Legacy fields remain stable for migration consumers.
            "action": self.action,
            "content": self.content,
            "current_sha256": self.current_sha256,
            "path": self.path,
            "proposed_sha256": self.proposed_sha256,
            "reason": self.reason,
            # The frozen classification contract.
            "current_mode": self.current_mode,
            "current_type": self.current_type,
            "diagnostics": [diagnostic.as_dict() for diagnostic in self.diagnostics],
            "operation": self.operation,
            "ownership": self.ownership,
            "postimage": self.postimage,
            "preimage": self.preimage,
            "proposed_mode": self.proposed_mode,
            "proposed_path": self.proposed_path,
            "proposed_type": self.proposed_type,
        }
        destination = self.destination
        if destination is not None:
            result["destination"] = destination
        return result


@dataclass(frozen=True, slots=True)
class SetupPreview:
    actions: tuple[SetupAction, ...]
    fingerprint: str
    diagnostics: tuple[object, ...] = ()

    @staticmethod
    def _diagnostic_dict(diagnostic: object) -> dict[str, object] | str:
        as_dict = getattr(diagnostic, "as_dict", None)
        if callable(as_dict):
            value = as_dict()
            if isinstance(value, dict):
                return value
        return str(diagnostic)

    def as_dict(self) -> dict[str, object]:
        return {
            "actions": [action.as_dict() for action in self.actions],
            "diagnostics": [
                self._diagnostic_dict(diagnostic) for diagnostic in self.diagnostics
            ],
            "fingerprint": self.fingerprint,
            "schema": "reporivet.setup-preview/v1",
        }

    def render(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


DOCUMENT_FIRST_DOCUMENTS: dict[str, str] = {
    "ARCHITECTURE.md": "document-first/root/ARCHITECTURE.md.tmpl",
    "docs/README.md": "document-first/docs/README.md.tmpl",
    "docs/PRODUCT.md": "document-first/docs/PRODUCT.md.tmpl",
    "docs/DESIGN.md": "document-first/docs/DESIGN.md.tmpl",
    "docs/QUALITY.md": "document-first/docs/QUALITY.md.tmpl",
    "docs/OPERATIONS.md": "document-first/docs/OPERATIONS.md.tmpl",
    "docs/SECURITY.md": "document-first/docs/SECURITY.md.tmpl",
    "docs/PLANS.md": "document-first/docs/PLANS.md.tmpl",
    "docs/product-specs/index.md": "document-first/docs/product-specs/index.md.tmpl",
    "docs/product-specs/_template.md": "document-first/docs/product-specs/_template.md.tmpl",
    "docs/design-docs/index.md": "document-first/docs/design-docs/index.md.tmpl",
    "docs/design-docs/core-beliefs.md": "document-first/docs/design-docs/core-beliefs.md.tmpl",
    "docs/design-docs/_template.md": "document-first/docs/design-docs/_template.md.tmpl",
    "docs/exec-plans/_template.md": "document-first/docs/exec-plans/_template.md.tmpl",
    "docs/exec-plans/tech-debt-tracker.md": "document-first/docs/exec-plans/tech-debt-tracker.md.tmpl",
    "docs/decisions/README.md": "document-first/docs/decisions/README.md.tmpl",
    "docs/decisions/_template.md": "document-first/docs/decisions/_template.md.tmpl",
    "docs/references/README.md": "document-first/docs/references/README.md.tmpl",
    "docs/references/project-definition-protocol.md": "document-first/docs/references/project-definition-protocol.md.tmpl",
    "docs/runbooks/index.md": "document-first/docs/runbooks/index.md.tmpl",
    "docs/runbooks/_template.md": "document-first/docs/runbooks/_template.md.tmpl",
}

CLAUDE_ADAPTER_ASSET = "document-first/claude/CLAUDE.md.tmpl"


LEGACY_RUNTIME_PATHS = (
    ".harness/runs",
    ".harness/tmp",
    ".harness/worktrees",
)


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256_text(content: str) -> str:
    return _sha256_bytes(content.encode("utf-8"))


def _normalized_lines(values: object, *, field_name: str) -> list[str]:
    if isinstance(values, str):
        candidates = [values]
    elif isinstance(values, list) and all(isinstance(value, str) for value in values):
        candidates = list(values)
    else:
        raise InitError(f"definition answers field '{field_name}' must be a string or array of strings")
    normalized = [value.strip() for value in candidates if value.strip()]
    if not normalized:
        raise InitError(f"definition answers field '{field_name}' must contain a non-empty value")
    if any("\n" in value or "\r" in value for value in normalized):
        raise InitError(
            f"definition answers field '{field_name}' must use one Markdown bullet per string; use an array for multiple entries"
        )
    return normalized


def _initial_definition(root: Path, report: AuditReport | None) -> DefinitionDraft:
    evidence = {
        topic.key: TopicEvidence(
            open=[topic.question],
            sources=[],
        )
        for topic in DEFINITION_TOPICS
    }
    evidence["product"].proposed.append(f"Project name: {root.name}")
    evidence["product"].sources.append("Repository directory name observed during the read-only scan.")

    if report is not None:
        source_paths = sorted(
            finding.path
            for finding in report.findings
            if finding.category in {"manifest", "instruction", "durable-document", "ci", "source-path", "test-path"}
            and finding.status == "confirmed"
        )
        if source_paths:
            evidence["product"].sources.extend(f"Repository path: `{path}`." for path in source_paths)

        command_findings = [
            finding
            for finding in report.findings
            if finding.category == "command"
            and finding.status in {"confirmed", "inferred"}
            and finding.path.count("/") == 2
        ]
        for finding in command_findings:
            evidence["quality"].proposed.append(
                f"Candidate project command ({finding.path}): `{finding.detail}`"
            )
            evidence["quality"].sources.append(
                "Command candidate observed or inferred from repository files without execution; guided setup keeps it Proposed."
            )

        ci_paths = sorted(
            finding.path
            for finding in report.findings
            if finding.category == "ci" and finding.status == "confirmed"
        )
        for path in ci_paths:
            evidence["quality"].proposed.append(
                f"Existing project CI may provide verification: `{path}`"
            )
            evidence["quality"].sources.append(f"Repository path: `{path}`.")

    for topic_evidence in evidence.values():
        topic_evidence.proposed = _deduplicate(topic_evidence.proposed)
        topic_evidence.sources = _deduplicate(topic_evidence.sources)
    return DefinitionDraft(evidence)


def _deduplicate(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if normalized and normalized not in seen:
            result.append(normalized)
            seen.add(normalized)
    return result


def _evidence_lines(values: Sequence[str], marker: str) -> list[str]:
    if not values:
        return ["- None."]
    return [f"- [{marker}] {value}" for value in values]


def render_definition_draft(draft: DefinitionDraft, *, created: str, updated: str) -> str:
    next_topic = draft.next_topic
    next_value = "complete" if next_topic is None else f"{DEFINITION_TOPICS.index(next_topic) + 1}. {next_topic.title}"
    continuation = (
        "All core topics contain explicit confirmed input; review remaining Proposed and Open items before apply."
        if next_topic is None
        else f"Resume at {next_value}; preserve Confirmed, Proposed, Open, and Sources as separate evidence."
    )
    lines = [
        "---",
        "kind: project-definition-draft",
        "format: 2",
        f"created: {created}",
        f"updated: {updated}",
        f'progress: "{draft.confirmed_count}/{len(DEFINITION_TOPICS)}"',
        f'next: "{next_value}"',
        f'continuation: "{continuation}"',
        "---",
        "",
        "# Project Definition Draft",
        "",
        "This visible, project-owned draft is the only resume state. Scanner observations remain Proposed, explicit answers enter Confirmed without semantic rewriting, uncertainty remains Open, and Sources record provenance.",
        "",
        "The canonical bundle chooses its own filenames. Answer the plain-language questions below; do not add a hidden state file or promote a repository inference into Confirmed.",
    ]
    for index, topic in enumerate(DEFINITION_TOPICS, start=1):
        topic_evidence = draft.evidence[topic.key]
        lines.extend(("", f"## {index}. {topic.title}", "", f"Question: {topic.question}"))
        for heading, marker in (
            ("Confirmed", "confirmed"),
            ("Proposed", "proposed"),
            ("Open", "open"),
            ("Sources", "source"),
        ):
            lines.extend(("", f"### {heading}", ""))
            lines.extend(_evidence_lines(topic_evidence.values(heading), marker))
    return "\n".join(lines).rstrip() + "\n"


def _parse_evidence_block(block: str, *, topic: DefinitionTopic) -> TopicEvidence:
    headings = list(re.finditer(r"^### (Confirmed|Proposed|Open|Sources)\s*$", block, re.MULTILINE))
    if [match.group(1) for match in headings] != list(EVIDENCE_HEADINGS):
        raise InitError(
            f"definition topic '{topic.title}' must contain Confirmed, Proposed, Open, and Sources exactly once in order"
        )
    parsed: dict[str, list[str]] = {}
    markers = {
        "Confirmed": "confirmed",
        "Proposed": "proposed",
        "Open": "open",
        "Sources": "source",
    }
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(block)
        body = block[match.end() : end]
        values: list[str] = []
        saw_none = False
        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line == "- None.":
                saw_none = True
                continue
            expected = markers[match.group(1)]
            prefix = f"- [{expected}] "
            if not line.startswith(prefix) or not line[len(prefix) :].strip():
                raise InitError(
                    f"definition topic '{topic.title}' has malformed {match.group(1)} evidence"
                )
            values.append(line[len(prefix) :].strip())
        if saw_none and values:
            raise InitError(
                f"definition topic '{topic.title}' mixes the None sentinel with {match.group(1)} evidence"
            )
        parsed[match.group(1).casefold()] = values
    return TopicEvidence(**parsed)


def parse_definition_draft(text: str) -> DefinitionDraft:
    matches = list(re.finditer(r"^## ([0-9]+)\. (.+?)\s*$", text, re.MULTILINE))
    expected = [(str(index), topic.title) for index, topic in enumerate(DEFINITION_TOPICS, start=1)]
    actual = [(match.group(1), match.group(2)) for match in matches]
    if actual != expected:
        raise InitError("definition draft topics are missing, duplicated, renamed, or out of order")
    evidence: dict[str, TopicEvidence] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        topic = DEFINITION_TOPICS[index]
        evidence[topic.key] = _parse_evidence_block(text[match.end() : end], topic=topic)
    return DefinitionDraft(evidence)


def _draft_dates(text: str) -> tuple[str, str]:
    created_match = re.search(r"^created:\s*([^\s]+)\s*$", text, re.MULTILINE)
    updated_match = re.search(r"^updated:\s*([^\s]+)\s*$", text, re.MULTILINE)
    today = date.today().isoformat()
    return (
        created_match.group(1) if created_match else today,
        updated_match.group(1) if updated_match else today,
    )


def _read_definition(root: Path) -> tuple[str, DefinitionDraft]:
    path = root / DEFINITION_DRAFT_PATH
    ensure_safe_write_path(path)
    if not path.is_file():
        raise InitError(
            f"definition draft is missing: {DEFINITION_DRAFT_PATH}; run 'reporivet define --root <path> start'"
        )
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise InitError(f"cannot read definition draft: {exc}") from exc
    return text, parse_definition_draft(text)


def start_guided_definition(*, root: Path, dry_run: bool) -> ChangeSet:
    root = validate_root(root, create=True, dry_run=dry_run)
    path = root / DEFINITION_DRAFT_PATH
    ensure_safe_write_path(path)
    changes = ChangeSet()
    state, _ = _regular_file_state(path)
    if state == "conflict":
        raise InitError(f"definition draft path is unsafe or nonregular: {DEFINITION_DRAFT_PATH}")
    if state == "file":
        changes.skipped.append(path)
        changes.print(root, dry_run=dry_run)
        return changes

    report = audit_project(root=root) if root.exists() else None
    today = date.today().isoformat()
    content = render_definition_draft(_initial_definition(root, report), created=today, updated=today)
    changes.created.append(path)
    if not dry_run:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise InitError(f"cannot create definition draft: {exc}") from exc
    changes.print(root, dry_run=dry_run)
    return changes


def definition_status(*, root: Path) -> str:
    root = validate_root(root)
    _, draft = _read_definition(root)
    next_topic = draft.next_topic
    payload = {
        "confirmed_topics": draft.confirmed_count,
        "next": None if next_topic is None else next_topic.key,
        "question": None if next_topic is None else next_topic.question,
        "schema": "reporivet.definition-status/v2",
        "total_topics": len(DEFINITION_TOPICS),
        "unresolved": [
            topic.key for topic in DEFINITION_TOPICS if not draft.evidence[topic.key].confirmed
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _apply_answer_payload(draft: DefinitionDraft, payload: Mapping[str, object]) -> None:
    unknown = sorted(set(payload) - set(TOPIC_BY_KEY))
    if unknown:
        raise InitError("definition answers contain unknown topics: " + ", ".join(unknown))
    for key, raw in payload.items():
        topic_evidence = draft.evidence[key]
        if isinstance(raw, str):
            data: Mapping[str, object] = {"confirmed": raw}
        elif isinstance(raw, dict):
            data = raw
        else:
            raise InitError(f"definition answer for '{key}' must be a string or object")
        unknown_fields = sorted(set(data) - {"confirmed", "proposed", "open", "sources"})
        if unknown_fields:
            raise InitError(
                f"definition answer for '{key}' contains unknown fields: "
                + ", ".join(unknown_fields)
            )
        explicit_open = "open" in data
        for field_name, values in data.items():
            normalized = _normalized_lines(values, field_name=f"{key}.{field_name}")
            setattr(topic_evidence, field_name, normalized)
        if "confirmed" in data and not explicit_open:
            topic_evidence.open = []


def _load_definition_answers(answers: Path) -> Mapping[str, object]:
    answer_path = answers.expanduser()
    component = symlink_component(Path(os.path.abspath(answer_path)))
    if component is not None:
        raise InitError(f"refusing to read definition answers through a symlink path: {answers}")
    if not answer_path.is_file():
        raise InitError(f"definition answers file is missing or not regular: {answers}")
    try:
        decoded = json.loads(answer_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InitError(f"cannot read definition answers JSON: {exc}") from exc
    if not isinstance(decoded, dict):
        raise InitError("definition answers JSON must contain an object keyed by topic")
    return decoded


def resume_guided_definition(
    *,
    root: Path,
    answers: Path | None,
    dry_run: bool,
) -> ChangeSet:
    root = validate_root(root)
    original, draft = _read_definition(root)
    if answers is None:
        next_topic = draft.next_topic
        if next_topic is None:
            print("All core topics contain confirmed input; review Proposed and Open evidence before preview.")
            return ChangeSet(skipped=[root / DEFINITION_DRAFT_PATH])
        response = input(next_topic.question + "\n> ").strip()
        if not response:
            print("No answer recorded; the topic remains Open.")
            return ChangeSet(skipped=[root / DEFINITION_DRAFT_PATH])
        payload: Mapping[str, object] = {next_topic.key: response}
    else:
        payload = _load_definition_answers(answers)

    _apply_answer_payload(draft, payload)
    created, _ = _draft_dates(original)
    updated = render_definition_draft(
        draft,
        created=created,
        updated=date.today().isoformat(),
    )
    path = root / DEFINITION_DRAFT_PATH
    changes = ChangeSet()
    if updated.encode("utf-8") == original.encode("utf-8"):
        changes.skipped.append(path)
    else:
        changes.updated.append(path)
        if not dry_run:
            try:
                path.write_text(updated, encoding="utf-8")
            except OSError as exc:
                raise InitError(f"cannot update definition draft: {exc}") from exc
    changes.print(root, dry_run=dry_run)
    return changes


def _evidence_markdown(evidence: TopicEvidence) -> str:
    lines: list[str] = []
    for heading, marker in (
        ("Confirmed", "confirmed"),
        ("Proposed", "proposed"),
        ("Open", "open"),
        ("Sources", "source"),
    ):
        lines.extend((f"### {heading}", ""))
        lines.extend(_evidence_lines(evidence.values(heading), marker))
        lines.append("")
    return "\n".join(lines).rstrip()


def _architecture_evidence(root: Path) -> TopicEvidence:
    evidence = TopicEvidence(
        open=[
            "Confirm the implemented repository map, dependency direction, runtime processes, deployment units, storage, external systems, and enforced architecture checks."
        ]
    )
    language_signals = (
        ("package.json", "TypeScript/JavaScript or another Node.js language"),
        ("pyproject.toml", "Python"),
        ("requirements.txt", "Python"),
        ("go.mod", "Go"),
        ("Cargo.toml", "Rust"),
        ("pom.xml", "Java"),
        ("build.gradle", "Java/Kotlin"),
        ("build.gradle.kts", "Kotlin/Java"),
    )
    for relative, language in language_signals:
        path = root / relative
        if path.is_file() and not path.is_symlink():
            evidence.proposed.append(f"Observed manifest suggests a {language} project: `{relative}`")
            evidence.sources.append(f"Repository path: `{relative}`.")
    return evidence


def _read_guided_asset(relative: str, values: Mapping[str, str] | None = None) -> str:
    template = read_asset(relative)
    replacements = values or {}
    return re.sub(
        r"\{\{([A-Z0-9_]+)\}\}",
        lambda match: replacements.get(match.group(1), match.group(0)),
        template,
    )


def _bundle_values(root: Path, draft: DefinitionDraft) -> dict[str, str]:
    return {
        "HARNESS_VERSION": __version__,
        "PRODUCT_EVIDENCE": _evidence_markdown(draft.evidence["product"]),
        "DESIGN_EVIDENCE": _evidence_markdown(draft.evidence["design"]),
        "QUALITY_EVIDENCE": _evidence_markdown(draft.evidence["quality"]),
        "OPERATIONS_EVIDENCE": _evidence_markdown(draft.evidence["operations"]),
        "SECURITY_EVIDENCE": _evidence_markdown(draft.evidence["security"]),
        "AGENT_EVIDENCE": _evidence_markdown(draft.evidence["agents"]),
        "PROCEDURE_EVIDENCE": _evidence_markdown(draft.evidence["procedures"]),
        "ARCHITECTURE_EVIDENCE": _evidence_markdown(_architecture_evidence(root)),
    }


def _target_asset_contents(
    root: Path,
    draft: DefinitionDraft,
    *,
    with_claude_settings: bool,
) -> dict[str, str]:
    # Keep the protected compatibility parameter, but generate only surviving
    # project Markdown plus the thin optional host adapter.
    del with_claude_settings
    values = _bundle_values(root, draft)
    contents = {
        "AGENTS.md": _read_guided_asset("document-first/root/AGENTS.md.tmpl", values),
        "CLAUDE.md": _read_guided_asset(CLAUDE_ADAPTER_ASSET, values),
    }
    for destination, asset in DOCUMENT_FIRST_DOCUMENTS.items():
        contents[destination] = _read_guided_asset(asset, values)
    # Lifecycle directories remain available without creating an active Plan.
    contents["docs/exec-plans/active/.gitkeep"] = ""
    contents["docs/exec-plans/completed/.gitkeep"] = ""
    return contents


def _non_directory_parent(path: Path) -> Path | None:
    return next(
        (
            parent
            for parent in path.parents
            if parent.exists() and not parent.is_dir()
        ),
        None,
    )


def _directory_open_flags() -> int:
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    if not no_follow or os.stat not in os.supports_dir_fd:
        raise OSError(
            errno.ENOTSUP,
            "descriptor-relative no-follow traversal is unavailable",
        )
    flags = os.O_RDONLY | no_follow
    for flag_name in ("O_CLOEXEC", "O_DIRECTORY", "O_NONBLOCK"):
        flags |= getattr(os, flag_name, 0)
    return flags


def _regular_file_open_flags(*, writable: bool = False, create: bool = False) -> int:
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    if not no_follow or os.stat not in os.supports_dir_fd:
        raise OSError(
            errno.ENOTSUP,
            "descriptor-relative no-follow traversal is unavailable",
        )
    flags = (os.O_RDWR if writable else os.O_RDONLY) | no_follow
    for flag_name in ("O_CLOEXEC", "O_NONBLOCK"):
        flags |= getattr(os, flag_name, 0)
    if create:
        flags |= os.O_CREAT | os.O_EXCL
    return flags


def _stat_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        stat.S_IFMT(metadata.st_mode),
    )


def _stat_content_identity(metadata: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        *_stat_identity(metadata),
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _open_directory_component(parent_descriptor: int, name: str) -> int:
    before = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    if not stat.S_ISDIR(before.st_mode):
        raise OSError(errno.ENOTDIR, "path component is not a directory", name)
    descriptor = os.open(
        name,
        _directory_open_flags(),
        dir_fd=parent_descriptor,
    )
    try:
        opened = os.fstat(descriptor)
        current = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
        if (
            not stat.S_ISDIR(opened.st_mode)
            or _stat_identity(before) != _stat_identity(opened)
            or _stat_identity(current) != _stat_identity(opened)
        ):
            raise OSError(errno.ESTALE, "directory identity changed during traversal", name)
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _open_absolute_directory(path: Path) -> int:
    absolute = Path(os.path.abspath(path))
    if not absolute.is_absolute():
        raise OSError(errno.EINVAL, "safe traversal requires an absolute path")
    descriptor = os.open(os.path.abspath(os.sep), _directory_open_flags())
    try:
        for component in absolute.parts[1:]:
            child = _open_directory_component(descriptor, component)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _open_absolute_parent(path: Path) -> tuple[int, str]:
    absolute = Path(os.path.abspath(path))
    if not absolute.is_absolute() or absolute.name in {"", ".", ".."}:
        raise OSError(errno.EINVAL, "safe traversal requires a named absolute path")
    descriptor = os.open(os.path.abspath(os.sep), _directory_open_flags())
    try:
        for component in absolute.parts[1:-1]:
            child = _open_directory_component(descriptor, component)
            os.close(descriptor)
            descriptor = child
        return descriptor, absolute.name
    except Exception:
        os.close(descriptor)
        raise


def _read_open_regular_file(descriptor: int) -> bytes:
    before = os.fstat(descriptor)
    if not stat.S_ISREG(before.st_mode):
        raise OSError(errno.EINVAL, "opened path is not a regular file")
    os.lseek(descriptor, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while True:
        chunk = os.read(descriptor, 1024 * 1024)
        if not chunk:
            break
        chunks.append(chunk)
    after = os.fstat(descriptor)
    if _stat_content_identity(before) != _stat_content_identity(after):
        raise OSError(errno.ESTALE, "file changed while it was being read")
    return b"".join(chunks)


def _read_regular_file_from_parent(parent_descriptor: int, name: str) -> bytes:
    before = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode):
        raise OSError(errno.EINVAL, "target is not a regular file", name)
    descriptor = os.open(
        name,
        _regular_file_open_flags(),
        dir_fd=parent_descriptor,
    )
    try:
        opened = os.fstat(descriptor)
        if _stat_content_identity(before) != _stat_content_identity(opened):
            raise OSError(errno.ESTALE, "file identity changed before read", name)
        content = _read_open_regular_file(descriptor)
        current = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
        after = os.fstat(descriptor)
        if (
            _stat_content_identity(opened) != _stat_content_identity(after)
            or _stat_content_identity(current) != _stat_content_identity(after)
        ):
            raise OSError(errno.ESTALE, "file identity changed during read", name)
        return content
    finally:
        os.close(descriptor)


def _read_regular_file_bytes(
    path: Path,
    *,
    parent_descriptor: int | None = None,
    name: str | None = None,
) -> bytes:
    if parent_descriptor is not None or name is not None:
        if parent_descriptor is None or name is None:
            raise OSError(errno.EINVAL, "safe file read requires both parent descriptor and name")
        return _read_regular_file_from_parent(parent_descriptor, name)
    opened_parent, opened_name = _open_absolute_parent(path)
    try:
        return _read_regular_file_from_parent(opened_parent, opened_name)
    finally:
        os.close(opened_parent)


def _absolute_parent_binding_is_current(
    path: Path,
    expected: os.stat_result,
) -> bool:
    try:
        descriptor, _ = _open_absolute_parent(path)
    except OSError:
        return False
    try:
        return _stat_identity(os.fstat(descriptor)) == _stat_identity(expected)
    finally:
        os.close(descriptor)


def _regular_file_state(path: Path) -> tuple[str, bytes]:
    try:
        parent_descriptor, name = _open_absolute_parent(path)
    except FileNotFoundError:
        return "missing", b""
    except OSError:
        return "conflict", b""
    try:
        try:
            metadata = os.stat(
                name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return "missing", b""
        except OSError:
            return "conflict", b""
        if not stat.S_ISREG(metadata.st_mode):
            return "conflict", b""
        parent_metadata = os.fstat(parent_descriptor)
        try:
            content = _read_regular_file_bytes(
                path,
                parent_descriptor=parent_descriptor,
                name=name,
            )
        except OSError:
            return "conflict", b""
        if not _absolute_parent_binding_is_current(path, parent_metadata):
            return "conflict", b""
        return "file", content
    finally:
        os.close(parent_descriptor)


@dataclass
class _GuidedSetupUndo:
    kind: str
    relative: str
    parent_descriptor: int | None = None
    name: str = ""
    identity: tuple[int, int, int] | None = None
    content: bytes | None = None
    mode: int | None = None
    file_descriptor: int | None = None


class _GuidedSetupTransaction:
    def __init__(self, root: Path) -> None:
        self.root = root
        try:
            self.root_descriptor = _open_absolute_directory(root)
        except OSError as exc:
            raise InitError(f"cannot anchor guided setup at the validated root: {exc}") from exc
        self.undo: list[_GuidedSetupUndo] = []
        self.finished = False

    @staticmethod
    def _parts(relative: str) -> tuple[str, ...]:
        path = Path(relative)
        parts = path.parts
        if (
            path.is_absolute()
            or not parts
            or any(part in {"", ".", ".."} for part in parts)
        ):
            raise InitError(f"guided setup target is not a safe relative path: {relative}")
        return parts

    def _parent_binding_is_current(
        self,
        parent_parts: Sequence[str],
        expected: os.stat_result,
    ) -> bool:
        descriptor = os.dup(self.root_descriptor)
        try:
            for component in parent_parts:
                child = _open_directory_component(descriptor, component)
                os.close(descriptor)
                descriptor = child
            return _stat_identity(os.fstat(descriptor)) == _stat_identity(expected)
        except OSError:
            return False
        finally:
            os.close(descriptor)

    def _open_parent(
        self,
        relative: str,
        *,
        create: bool,
    ) -> tuple[int, str, tuple[str, ...], os.stat_result]:
        parts = self._parts(relative)
        parent_parts = parts[:-1]
        descriptor = os.dup(self.root_descriptor)
        traversed: list[str] = []
        try:
            for component in parent_parts:
                try:
                    child = _open_directory_component(descriptor, component)
                except FileNotFoundError:
                    if not create:
                        raise
                    os.mkdir(component, mode=0o777, dir_fd=descriptor)
                    try:
                        child = _open_directory_component(descriptor, component)
                    except Exception:
                        try:
                            current = os.stat(
                                component,
                                dir_fd=descriptor,
                                follow_symlinks=False,
                            )
                            if stat.S_ISDIR(current.st_mode):
                                os.rmdir(component, dir_fd=descriptor)
                        except OSError:
                            pass
                        raise
                    opened = os.fstat(child)
                    self.undo.append(
                        _GuidedSetupUndo(
                            kind="directory",
                            relative="/".join((*traversed, component)),
                            parent_descriptor=os.dup(descriptor),
                            name=component,
                            identity=_stat_identity(opened),
                        )
                    )
                os.close(descriptor)
                descriptor = child
                traversed.append(component)
            metadata = os.fstat(descriptor)
            if not self._parent_binding_is_current(parent_parts, metadata):
                raise OSError(
                    errno.ESTALE,
                    "parent directory changed during descriptor traversal",
                    relative,
                )
            return descriptor, parts[-1], parent_parts, metadata
        except Exception:
            os.close(descriptor)
            raise

    def regular_file_state(self, relative: str) -> tuple[str, bytes]:
        try:
            parent_descriptor, name, parent_parts, parent_metadata = self._open_parent(
                relative,
                create=False,
            )
        except FileNotFoundError:
            return "missing", b""
        except (OSError, InitError):
            return "conflict", b""
        try:
            try:
                metadata = os.stat(
                    name,
                    dir_fd=parent_descriptor,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                return "missing", b""
            except OSError:
                return "conflict", b""
            if not stat.S_ISREG(metadata.st_mode):
                return "conflict", b""
            try:
                content = _read_regular_file_bytes(
                    self.root / relative,
                    parent_descriptor=parent_descriptor,
                    name=name,
                )
            except OSError:
                return "conflict", b""
            if not self._parent_binding_is_current(parent_parts, parent_metadata):
                return "conflict", b""
            return "file", content
        finally:
            os.close(parent_descriptor)

    @staticmethod
    def _write_all(descriptor: int, content: bytes) -> None:
        view = memoryview(content)
        written = 0
        while written < len(view):
            count = os.write(descriptor, view[written:])
            if count <= 0:
                raise OSError(errno.EIO, "write returned no progress")
            written += count

    def create_file(self, relative: str, content: bytes) -> None:
        ensure_safe_write_path(self.root / relative)
        try:
            parent_descriptor, name, parent_parts, parent_metadata = self._open_parent(
                relative,
                create=True,
            )
        except (OSError, InitError) as exc:
            raise InitError(f"setup target path is unsafe or changed: {relative}: {exc}") from exc
        descriptor = -1
        try:
            if not self._parent_binding_is_current(parent_parts, parent_metadata):
                raise InitError(f"setup target parent changed before create: {relative}")
            try:
                os.stat(
                    name,
                    dir_fd=parent_descriptor,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                pass
            else:
                raise InitError(f"setup target changed after preview: {relative}; rerun finalize preview")
            descriptor = os.open(
                name,
                _regular_file_open_flags(writable=True, create=True),
                0o666,
                dir_fd=parent_descriptor,
            )
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode):
                raise OSError(errno.EINVAL, "created setup target is not regular", relative)
            self.undo.append(
                _GuidedSetupUndo(
                    kind="file",
                    relative=relative,
                    parent_descriptor=os.dup(parent_descriptor),
                    name=name,
                    identity=_stat_identity(opened),
                )
            )
            self._write_all(descriptor, content)
            current = os.stat(
                name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            if (
                _stat_identity(current) != _stat_identity(opened)
                or not self._parent_binding_is_current(parent_parts, parent_metadata)
            ):
                raise InitError(f"setup target changed during create: {relative}")
        except InitError:
            raise
        except OSError as exc:
            raise InitError(f"cannot safely create guided setup target {relative}: {exc}") from exc
        finally:
            if descriptor >= 0:
                os.close(descriptor)
            os.close(parent_descriptor)

    def update_file(self, relative: str, content: bytes, current_sha256: str) -> None:
        ensure_safe_write_path(self.root / relative)
        try:
            parent_descriptor, name, parent_parts, parent_metadata = self._open_parent(
                relative,
                create=False,
            )
        except (OSError, InitError) as exc:
            raise InitError(f"setup target path is unsafe or changed: {relative}: {exc}") from exc
        descriptor = -1
        recorded = False
        try:
            before = os.stat(
                name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            if not stat.S_ISREG(before.st_mode):
                raise InitError(f"setup update target is not a regular file: {relative}")
            descriptor = os.open(
                name,
                _regular_file_open_flags(writable=True),
                dir_fd=parent_descriptor,
            )
            opened = os.fstat(descriptor)
            if _stat_content_identity(before) != _stat_content_identity(opened):
                raise InitError(f"setup target changed before update: {relative}")
            original = _read_open_regular_file(descriptor)
            after_read = os.fstat(descriptor)
            current = os.stat(
                name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            if (
                _stat_content_identity(current)
                != _stat_content_identity(after_read)
                or not self._parent_binding_is_current(parent_parts, parent_metadata)
                or _sha256_bytes(original) != current_sha256
            ):
                raise InitError(f"setup target changed after preview: {relative}; rerun finalize preview")
            self.undo.append(
                _GuidedSetupUndo(
                    kind="update",
                    relative=relative,
                    content=original,
                    mode=opened.st_mode & 0o7777,
                    file_descriptor=descriptor,
                )
            )
            recorded = True
            os.ftruncate(descriptor, 0)
            os.lseek(descriptor, 0, os.SEEK_SET)
            self._write_all(descriptor, content)
            after = os.stat(
                name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            if (
                _stat_identity(after) != _stat_identity(opened)
                or not self._parent_binding_is_current(parent_parts, parent_metadata)
            ):
                raise InitError(f"setup target changed during update: {relative}")
        except InitError:
            raise
        except OSError as exc:
            raise InitError(f"cannot safely update guided setup target {relative}: {exc}") from exc
        finally:
            if descriptor >= 0 and not recorded:
                os.close(descriptor)
            os.close(parent_descriptor)

    def _close_undo_descriptors(self) -> None:
        for entry in self.undo:
            if entry.parent_descriptor is not None:
                os.close(entry.parent_descriptor)
                entry.parent_descriptor = None
            if entry.file_descriptor is not None:
                os.close(entry.file_descriptor)
                entry.file_descriptor = None
        self.undo.clear()

    def rollback(self) -> None:
        errors: list[str] = []
        for entry in reversed(self.undo):
            try:
                if entry.kind == "update":
                    if entry.file_descriptor is None:
                        raise OSError(errno.EBADF, "update descriptor is unavailable")
                    os.ftruncate(entry.file_descriptor, 0)
                    os.lseek(entry.file_descriptor, 0, os.SEEK_SET)
                    self._write_all(entry.file_descriptor, entry.content or b"")
                    if entry.mode is not None:
                        os.fchmod(entry.file_descriptor, entry.mode)
                    continue

                if (
                    entry.parent_descriptor is None
                    or entry.identity is None
                    or not entry.name
                ):
                    raise OSError(errno.EBADF, "rollback descriptor is unavailable")
                try:
                    current = os.stat(
                        entry.name,
                        dir_fd=entry.parent_descriptor,
                        follow_symlinks=False,
                    )
                except FileNotFoundError:
                    continue
                if _stat_identity(current) != entry.identity:
                    raise OSError(errno.ESTALE, "path identity changed; refusing removal")
                if entry.kind == "file":
                    os.unlink(entry.name, dir_fd=entry.parent_descriptor)
                elif entry.kind == "directory":
                    os.rmdir(entry.name, dir_fd=entry.parent_descriptor)
                else:
                    raise OSError(errno.EINVAL, f"unknown rollback entry {entry.kind}")
            except OSError as exc:
                errors.append(f"{entry.relative}: {exc}")
        self._close_undo_descriptors()
        self.finished = True
        if errors:
            raise InitError(
                "guided setup rollback refused changed paths without traversing them: "
                + "; ".join(errors)
            )

    def commit(self) -> None:
        self._close_undo_descriptors()
        self.finished = True

    def close(self) -> None:
        if not self.finished:
            self._close_undo_descriptors()
            self.finished = True
        os.close(self.root_descriptor)


def _write_setup_definition(
    *,
    root: Path,
    relative: str,
    content: bytes,
    current_state: str,
    current_content: bytes,
) -> None:
    transaction = _GuidedSetupTransaction(root)
    try:
        try:
            if current_state == "missing":
                transaction.create_file(relative, content)
            else:
                transaction.update_file(
                    relative,
                    content,
                    _sha256_bytes(current_content),
                )
            transaction.commit()
        except Exception as exc:
            try:
                transaction.rollback()
            except InitError as rollback_exc:
                raise InitError(
                    f"guided definition update failed ({exc}); {rollback_exc}"
                ) from rollback_exc
            if isinstance(exc, InitError):
                raise
            raise InitError(
                f"guided definition update failed and was rolled back: {exc}"
            ) from exc
    finally:
        transaction.close()


def _prepare_setup_definition(
    *,
    root: Path,
    report: AuditReport,
    answers: Path | None,
    dry_run: bool,
    input_fn: Callable[[str], str] | None,
) -> _SetupDefinitionStep:
    root = validate_root(root)
    path = root / DEFINITION_DRAFT_PATH
    state, original_bytes = _regular_file_state(path)
    if state == "conflict":
        raise InitError(
            f"definition draft path is unsafe or nonregular: {DEFINITION_DRAFT_PATH}"
        )

    today = date.today().isoformat()
    if state == "file":
        try:
            original = original_bytes.decode("utf-8")
        except UnicodeError as exc:
            raise InitError(f"cannot read definition draft: {exc}") from exc
        draft = parse_definition_draft(original)
        created, _ = _draft_dates(original)
    else:
        original = ""
        draft = _initial_definition(root, report)
        created = today

    payload: Mapping[str, object] | None = None
    prompted = False
    recorded = False
    if answers is not None:
        payload = _load_definition_answers(answers)
        recorded = bool(payload)
    elif input_fn is not None and draft.next_topic is not None:
        prompted = True
        response = input_fn(draft.next_topic.question + "\n> ").strip()
        if response:
            payload = {draft.next_topic.key: response}
            recorded = True

    if payload is not None:
        _apply_answer_payload(draft, payload)

    should_render = state == "missing" or payload is not None
    updated = (
        render_definition_draft(draft, created=created, updated=today)
        if should_render
        else original
    )
    updated_bytes = updated.encode("utf-8")
    changes = ChangeSet()
    if state == "missing":
        changes.created.append(path)
        draft_state = "planned-create" if dry_run else "created"
    elif updated_bytes != original_bytes:
        changes.updated.append(path)
        draft_state = "planned-update" if dry_run else "updated"
    else:
        changes.skipped.append(path)
        draft_state = "unchanged"

    if not dry_run and (state == "missing" or updated_bytes != original_bytes):
        _write_setup_definition(
            root=root,
            relative=DEFINITION_DRAFT_PATH.as_posix(),
            content=updated_bytes,
            current_state=state,
            current_content=original_bytes,
        )

    return _SetupDefinitionStep(
        draft=draft,
        changes=changes,
        draft_state=draft_state,
        prompted=prompted,
        recorded=recorded,
    )


@dataclass(frozen=True, slots=True)
class _SetupPathState:
    """Safe, read-only filesystem facts used by one preview classification."""

    kind: str
    content: bytes = field(default=b"", repr=False, compare=False)
    mode: int | None = None
    size: int | None = None
    children: tuple[str, ...] = ()
    error: str = ""

    @property
    def sha256(self) -> str:
        return _sha256_bytes(self.content) if self.kind == "regular" else ""


def _filesystem_type(mode: int) -> str:
    if stat.S_ISREG(mode):
        return "regular"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISFIFO(mode):
        return "fifo"
    if stat.S_ISSOCK(mode):
        return "socket"
    if stat.S_ISCHR(mode):
        return "character-device"
    if stat.S_ISBLK(mode):
        return "block-device"
    return "nonregular"


def _safe_relative_parts(relative: str) -> tuple[str, ...]:
    path = Path(relative)
    parts = path.parts
    if (
        path.is_absolute()
        or not parts
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise InitError(f"guided setup target is not a safe relative path: {relative}")
    return parts


def _path_state(root: Path, relative: str) -> _SetupPathState:
    """Read one path without following target symlinks or unsafe ancestors."""

    _safe_relative_parts(relative)
    path = root / relative
    try:
        parent_descriptor, name = _open_absolute_parent(path)
    except FileNotFoundError:
        return _SetupPathState("missing")
    except OSError as exc:
        return _SetupPathState("unsafe-ancestor", error=str(exc))

    try:
        try:
            metadata = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
        except FileNotFoundError:
            return _SetupPathState("missing")
        except OSError as exc:
            return _SetupPathState("unreadable", error=str(exc))

        kind = _filesystem_type(metadata.st_mode)
        mode = stat.S_IMODE(metadata.st_mode)
        parent_metadata = os.fstat(parent_descriptor)
        if kind == "regular":
            try:
                content = _read_regular_file_bytes(
                    path,
                    parent_descriptor=parent_descriptor,
                    name=name,
                )
            except OSError as exc:
                return _SetupPathState(
                    "unreadable",
                    mode=mode,
                    size=metadata.st_size,
                    error=str(exc),
                )
            if not _absolute_parent_binding_is_current(path, parent_metadata):
                return _SetupPathState(
                    "unsafe-ancestor",
                    mode=mode,
                    size=len(content),
                    error="parent directory identity changed during read",
                )
            return _SetupPathState(
                "regular",
                content=content,
                mode=mode,
                size=len(content),
            )
        if kind == "directory":
            directory_descriptor = -1
            try:
                directory_descriptor = _open_directory_component(parent_descriptor, name)
                children = tuple(sorted(os.listdir(directory_descriptor)))
                opened = os.fstat(directory_descriptor)
                current = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
                if (
                    _stat_identity(opened) != _stat_identity(metadata)
                    or _stat_identity(current) != _stat_identity(metadata)
                    or not _absolute_parent_binding_is_current(path, parent_metadata)
                ):
                    return _SetupPathState(
                        "unsafe-ancestor",
                        mode=mode,
                        size=metadata.st_size,
                        children=children,
                        error="directory identity changed during inventory",
                    )
            except OSError as exc:
                return _SetupPathState(
                    "unreadable",
                    mode=mode,
                    size=metadata.st_size,
                    error=str(exc),
                )
            finally:
                if directory_descriptor >= 0:
                    os.close(directory_descriptor)
            return _SetupPathState(
                "directory",
                mode=mode,
                size=metadata.st_size,
                children=children,
            )
        return _SetupPathState(kind, mode=mode, size=metadata.st_size)
    finally:
        os.close(parent_descriptor)


def _state_from_reader(
    relative: str,
    state_reader: Callable[[str], tuple[str, bytes]],
) -> _SetupPathState:
    state, content = state_reader(relative)
    if state == "file":
        return _SetupPathState("regular", content=content, size=len(content))
    if state == "missing":
        return _SetupPathState("missing")
    return _SetupPathState("unsafe")


AGENTS_START = "<!-- reporivet:start -->"
AGENTS_END = "<!-- reporivet:end -->"
GITIGNORE_START = "# reporivet:start"
GITIGNORE_END = "# reporivet:end"


def _marker_line_spans(text: str, marker: str) -> list[tuple[int, int]]:
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


def _managed_marker_span(text: str, start: str, end: str) -> tuple[int, int] | None:
    starts = _marker_line_spans(text, start)
    ends = _marker_line_spans(text, end)
    if not starts and not ends:
        return None
    if len(starts) != 1 or len(ends) != 1 or ends[0][0] < starts[0][1]:
        raise InitError(f"existing file has malformed managed markers: {start} / {end}")
    return starts[0][0], ends[0][1]


# These are retained as data for exact, one-shot cleanup proof only.  They are
# never emitted by current guided generation.
_LEGACY_AGENTS_TEMPLATE = "<!-- reporivet:start -->\n# Repository Agent Operating Contract\n\n`AGENTS.md` is the canonical, host-neutral entry point for repository work. Host adapters may import it, but they do not replace its authority.\n\n## Start here\n\n1. Read [`docs/README.md`](docs/README.md) for the knowledge map.\n2. For a substantive goal, create or resume exactly one matching Plan in [`docs/exec-plans/active/`](docs/exec-plans/active/).\n3. Read only the current authority and code named by that Plan or the local task.\n4. Use commands already owned by this project. Reporivet documents commands; it does not wrap or execute them.\n\nThe default onboarding entry point is integrated `reporivet setup`. `reporivet init` remains structure-only, and the lower-level `reporivet define` flow remains available for staged definition work.\n\n## Sources of truth\n\n- Product intent and requirements: [`docs/PRODUCT.md`](docs/PRODUCT.md) and [`docs/product-specs/`](docs/product-specs/)\n- Architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)\n- Design and accessibility: [`docs/DESIGN.md`](docs/DESIGN.md) and [`docs/design-docs/`](docs/design-docs/)\n- Quality and project-owned checks: [`docs/QUALITY.md`](docs/QUALITY.md)\n- Operations, deployment, backup, rollback, recovery, and incidents: [`docs/OPERATIONS.md`](docs/OPERATIONS.md) and [`docs/runbooks/`](docs/runbooks/)\n- Security: [`docs/SECURITY.md`](docs/SECURITY.md)\n- Plan lifecycle: [`docs/PLANS.md`](docs/PLANS.md)\n\nWhen current sources conflict, stop and report the conflict. Do not silently choose the easiest interpretation.\n\n## Main, implementation, and verification\n\n- **Main** owns user intent, scope, acceptance criteria, decomposition, dispatch, integration order, decisions, the serialized Plan lifecycle, and final evidence judgment. Main keeps context small and does not normally repeat a Verification Sub's detailed command run.\n- **Implementation Sub** receives one bounded Task Packet, reads only named authority, stays within allowed writes and protected paths, uses project-owned commands, and returns changed paths, command results, discoveries, and residual risks. A default leaf may not broaden scope, change acceptance, delegate, move the Plan, or approve its own candidate.\n- **Verification Sub** uses a fresh context, reads the Plan goal and acceptance criteria plus current authority and the integrated candidate, treats implementer narration as unverified, runs project-owned checks, and returns criterion-level pass/fail, candidate identity, and residual risks. Fresh verification is read-only, nonrepairing, and nondelegating; it does not repair the candidate unless Main assigns a separate implementation packet.\n\n### Broad-milestone native-Agent dispatch\n\nFor every milestone classified as broad, this is a common installed-project rule:\n\n`T<n> (broad milestone) -> T<n>-A/B/C/... (owned child packets, all ready leaves dispatched concurrently) -> T<n>-I (integration) -> T<n>-V1/V2/... (parallel fresh verification)`\n\nMain serializes a finite accepted manifest before resuming an Owner. Broad or multi-part roots default to `Role: Task Owner` and `May delegate: yes`; narrow or inherently serial roots remain direct nondelegating leaves. Main dispatches independent root Owners concurrently using only the host's native Agent execution. A resumed Owner dispatches its complete dependency-ready descendants through host-native Agent execution and only within the predeclared child budget. Main still dispatches the complete dependency-ready root set concurrently: independent Owners for broad work and direct leaves for narrow or inherently serial work.\n\nEvery child row retains an explicit owner and matching bounded packet. Owner boundaries, child budget, disjoint allowed-write sets, exact baseline, and separate worktrees remain explicit. Descendants inherit parent scope, protected paths, acceptance, exact baseline, and frozen shared interfaces and cannot broaden them. An Owner performs local aggregation of descendant results and returns one evidence package to Main without editing the shared Plan; Main alone performs final integration. This rule does not apply to inherently single or serial milestones.\n\nIf a child is itself broad, only a packet explicitly marked `Role: Task Owner` and `May delegate: yes` may run its predeclared bounded descendant packets such as `T<n>-A-1`; ordinary leaf Agents do not delegate. Existing narrow or inherently serial packets remain compatible as direct nondelegating leaves and may omit hierarchy-only fields.\n\nParallel mutable siblings require disjoint allowed-write sets, frozen shared interfaces, an exact common baseline, and separate worktrees. Read-only review and verification lanes may run concurrently. Siblings converge on an explicit integration node; fresh verification nodes depend on the integrated candidate and do not repair it.\n\nReporivet installs no scheduler, task store, lease, lock, or automatic dispatcher; it also installs no dispatcher, runtime, hidden state, task DB, runner, generated CI, Gate, evidence archive, deployment engine, or automatic closure.\n\nMeaningful behavior changes should separate implementation and verification contexts. Explanations are not evidence.\n\nDynamic procedure Skills are project-owned under `.claude/skills/<slug>/SKILL.md`. Only complete Confirmed structured procedure records can produce an instruction-only Skill through resumed `reporivet setup`; no project-specific Skill is pre-generated. Keep frontmatter instruction-only and least privilege. No procedure is inferred or executed, and an existing differing, stale, or arbitrary Skill is preserved rather than deleted. Main—not package runtime—creates/resumes Plans and keeps their state in visible Markdown.\n\n## Working boundaries\n\n- Prefer the smallest durable change that satisfies current requirements.\n- Preserve explicit ownership and dependency direction.\n- Do not add speculative infrastructure, compatibility shims, generated command runners, CI, deployment engines, task databases, journals, Gates, evidence archives, or hidden orchestration state. Reporivet installs no scheduler, dispatcher, task DB, runner, generated CI, Gate, evidence archive, deployment engine, or automatic closure.\n- Stop before changing public APIs, persisted data, authentication, authorization, payments, infrastructure, or production deployment unless the approved Plan explicitly covers the change.\n- Do not weaken acceptance tests, rewrite unrelated code, add production dependencies, or perform external actions without explicit authority.\n- Record out-of-scope discoveries in the active Plan; do not implement them implicitly.\n\n## Project-specific working agreements\n\n{{AGENT_EVIDENCE}}\n<!-- reporivet:end -->\n"
_LEGACY_GITIGNORE_BLOCK = """# reporivet:start
# Claude Code machine-local settings. Shared project Skills and explicitly reviewed
# .claude/settings.json remain visible and version-controlled when present.
.claude/settings.local.json
# reporivet:end"""
_LEGACY_FIXED_HASHES = {
    ".claude/skills/reporivet-main/SKILL.md":
        "42d62ba802c6c385183d84d5a40fe35fa63a97af39c9bc6464992d9f322e8a1d",
    ".claude/skills/reporivet-implementation/SKILL.md":
        "697ef4a2138ce91dbea007a6dd17b2c9856b895784a95207eda0a9a41649a0cc",
    ".claude/skills/reporivet-verification/SKILL.md":
        "672bf819ddf43ee7bb20b7e20385eacfc2534cbbc70fd8cad8efbe639f582b09",
    ".claude/settings.json":
        "aa661eccd0aa127c2ae60fdaa42997e7eae1cc4926ea380281dcc7967dc4b82c",
}
_LEGACY_VERSION_CONTENT = f"# reporivet:managed version={__version__}\n{__version__}\n"
_LEGACY_FIXED_HASHES[".reporivet-version"] = _sha256_text(_LEGACY_VERSION_CONTENT)


def _legacy_agents_content(values: Mapping[str, str]) -> str:
    return re.sub(
        r"\{\{([A-Z0-9_]+)\}\}",
        lambda match: values.get(match.group(1), match.group(0)),
        _LEGACY_AGENTS_TEMPLATE,
    )


def _legacy_marker_expected(relative: str, values: Mapping[str, str]) -> str:
    if relative == "AGENTS.md":
        return _legacy_agents_content(values).rstrip("\n")
    return _LEGACY_GITIGNORE_BLOCK


def _make_setup_action(
    relative: str,
    operation: str,
    reason: str,
    state: _SetupPathState,
    *,
    proposed: str = "",
    ownership: str | None = None,
    proposed_type: str | None = None,
    proposed_path: str | None = None,
    destination_state: _SetupPathState | None = None,
    destination_content: str = "",
    diagnostics: tuple[SetupDiagnostic, ...] = (),
    normalize_proposed: bool = True,
) -> SetupAction:
    normalized = (
        proposed.rstrip() + "\n"
        if proposed and normalize_proposed
        else proposed
    )
    current_hash = state.sha256
    if ownership is None:
        ownership = "absent" if state.kind == "missing" else "project-owned"
    if proposed_type is None:
        if operation == "remove":
            proposed_type = "missing"
        elif operation == "preserve":
            proposed_type = state.kind
        else:
            proposed_type = "regular"

    if operation in {"preserve", "conflict"}:
        proposed_hash = current_hash if operation == "preserve" else (
            _sha256_text(normalized) if normalized else ""
        )
    elif proposed_type == "regular":
        proposed_hash = _sha256_text(normalized)
    else:
        proposed_hash = ""

    destination_normalized = (
        destination_content.rstrip() + "\n" if destination_content else ""
    )
    destination_type = None
    destination_hash = ""
    destination_mode = None
    destination_size = None
    destination_current_type = None
    destination_current_hash = ""
    destination_current_mode = None
    destination_current_size = None
    if destination_state is not None:
        destination_type = "regular" if destination_normalized else "missing"
        destination_hash = (
            _sha256_text(destination_normalized) if destination_normalized else ""
        )
        destination_mode = None
        destination_size = len(destination_normalized.encode("utf-8")) if destination_normalized else None
        destination_current_type = destination_state.kind
        destination_current_hash = destination_state.sha256
        destination_current_mode = destination_state.mode
        destination_current_size = destination_state.size

    return SetupAction(
        path=relative,
        action=operation,
        reason=reason,
        current_sha256=current_hash,
        proposed_sha256=proposed_hash,
        content=normalized,
        ownership=ownership,
        current_type=state.kind,
        current_mode=state.mode,
        current_size=state.size,
        current_children=state.children,
        proposed_type=proposed_type,
        proposed_mode=None,
        proposed_path=proposed_path,
        destination_type=destination_type,
        destination_sha256=destination_hash,
        destination_mode=destination_mode,
        destination_size=destination_size,
        destination_current_type=destination_current_type,
        destination_current_sha256=destination_current_hash,
        destination_current_mode=destination_current_mode,
        destination_current_size=destination_current_size,
        destination_content=destination_normalized,
        diagnostics=diagnostics,
    )


def _setup_action(
    root: Path,
    relative: str,
    proposed: str,
    *,
    state_reader: Callable[[str], tuple[str, bytes]] | None = None,
    path_state: _SetupPathState | None = None,
) -> SetupAction:
    state = path_state or (
        _path_state(root, relative)
        if state_reader is None
        else _state_from_reader(relative, state_reader)
    )
    normalized = proposed.rstrip() + "\n" if proposed else ""
    proposed_bytes = normalized.encode("utf-8")

    if state.kind not in {"missing", "regular"}:
        return _make_setup_action(
            relative,
            "conflict",
            "target is symlinked, nonregular, unsafe, or unreadable and will not be changed",
            state,
            proposed=normalized,
            ownership="ambiguous",
            diagnostics=(
                SetupDiagnostic(
                    relative,
                    "unsafe-path",
                    "current filesystem type is not a safely readable regular file or absence",
                ),
            ),
        )
    if state.kind == "missing":
        return _make_setup_action(
            relative,
            "create",
            "create the missing document-first Markdown asset",
            state,
            proposed=normalized,
        )
    if state.content == proposed_bytes:
        return _make_setup_action(
            relative,
            "unchanged",
            "existing bytes already match the proposed Markdown asset",
            state,
            proposed=normalized,
        )
    reason = (
        "existing host instructions are preserved for manual reconciliation"
        if relative == "CLAUDE.md"
        else "existing project-owned content is preserved byte-for-byte"
    )
    return _make_setup_action(
        relative,
        "preserve",
        reason,
        state,
        proposed=normalized,
    )


def _legacy_fixed_action(
    root: Path,
    relative: str,
    *,
    path_state_reader: Callable[[str], _SetupPathState],
) -> SetupAction | None:
    state = path_state_reader(relative)
    if state.kind == "missing":
        return None
    expected_hash = _LEGACY_FIXED_HASHES[relative]
    if state.kind != "regular":
        return _make_setup_action(
            relative,
            "conflict",
            "retired generated path is unsafe or nonregular; ownership cannot be proved",
            state,
            ownership="ambiguous",
            diagnostics=(
                SetupDiagnostic(
                    relative,
                    "unsafe-path",
                    "cleanup refuses symlinked, nonregular, or unreadable retired content",
                ),
            ),
        )
    if state.sha256 == expected_hash:
        return _make_setup_action(
            relative,
            "remove",
            "exact legacy generated bytes are proven package-owned and may be removed by cleanup",
            state,
            ownership="reporivet-generated",
            proposed_type="missing",
        )
    return _make_setup_action(
        relative,
        "preserve",
        "retired path is not an exact known generated artifact; preserve project-owned bytes",
        state,
        ownership="ambiguous",
        diagnostics=(
            SetupDiagnostic(
                relative,
                "ownership-unproven",
                "path name and location do not establish Reporivet ownership",
            ),
        ),
    )


def _legacy_marker_action(
    root: Path,
    relative: str,
    desired: str,
    values: Mapping[str, str],
    *,
    path_state_reader: Callable[[str], _SetupPathState],
) -> SetupAction | None:
    state = path_state_reader(relative)
    if state.kind == "missing":
        return None
    if state.kind != "regular":
        return _make_setup_action(
            relative,
            "conflict",
            "managed-marker cleanup cannot inspect an unsafe or nonregular path",
            state,
            ownership="ambiguous",
            diagnostics=(
                SetupDiagnostic(
                    relative,
                    "unsafe-path",
                    "marker cleanup refuses symlinked, nonregular, or unreadable paths",
                ),
            ),
        )
    try:
        text = state.content.decode("utf-8")
    except UnicodeDecodeError:
        return _make_setup_action(
            relative,
            "preserve",
            "marker-bearing bytes are not valid UTF-8; ownership cannot be proved",
            state,
            ownership="ambiguous",
            diagnostics=(
                SetupDiagnostic(
                    relative,
                    "ownership-unproven",
                    "managed marker cleanup requires exact UTF-8 canonical bytes",
                ),
            ),
        )
    markers = (
        (AGENTS_START, AGENTS_END)
        if relative == "AGENTS.md"
        else (GITIGNORE_START, GITIGNORE_END)
    )
    try:
        span = _managed_marker_span(text, *markers)
    except InitError as exc:
        return _make_setup_action(
            relative,
            "conflict",
            "managed marker structure is malformed and cannot be classified safely",
            state,
            ownership="ambiguous",
            diagnostics=(SetupDiagnostic(relative, "malformed-markers", str(exc)),),
        )
    if span is None:
        return None
    expected = _legacy_marker_expected(relative, values)
    if text[span[0] : span[1]] != expected:
        return _make_setup_action(
            relative,
            "preserve",
            "marker bytes are present but do not exactly match the known generated block",
            state,
            ownership="ambiguous",
            diagnostics=(
                SetupDiagnostic(
                    relative,
                    "ownership-unproven",
                    "marker names alone never establish generated ownership",
                ),
            ),
        )

    updated = text[: span[0]] + text[span[1] :]
    if not updated.strip():
        if relative == "AGENTS.md":
            return _make_setup_action(
                relative,
                "convert",
                "replace the exact legacy managed instruction file with the current unmarked asset",
                state,
                proposed=desired,
                ownership="reporivet-generated",
            )
        return _make_setup_action(
            relative,
            "remove",
            "exact legacy generated marker block is proven package-owned and may be removed by cleanup",
            state,
            ownership="reporivet-generated",
            proposed_type="missing",
        )
    return _make_setup_action(
        relative,
        "convert",
        "remove only the exact legacy generated marker block and preserve surrounding project bytes",
        state,
        proposed=updated,
        ownership="reporivet-generated",
        normalize_proposed=False,
    )


def _legacy_procedure_action(
    root: Path,
    relative: str,
    state: _SetupPathState,
    *,
    path_state_reader: Callable[[str], _SetupPathState],
) -> SetupAction:
    if state.kind != "regular":
        return _make_setup_action(
            relative,
            "conflict",
            "legacy procedure candidate is unsafe or nonregular; ownership cannot be proved",
            state,
            ownership="ambiguous",
            diagnostics=(
                SetupDiagnostic(
                    relative,
                    "unsafe-path",
                    "legacy procedure cleanup refuses symlinked, nonregular, or unreadable paths",
                ),
            ),
        )
    procedure = _legacy_procedure_skill_ownership_proof(state.content)
    if procedure is None:
        return _make_setup_action(
            relative,
            "preserve",
            "Claude Skill is not an exact known legacy procedure rendering; preserve project-owned bytes",
            state,
            ownership="ambiguous",
            diagnostics=(
                SetupDiagnostic(
                    relative,
                    "ownership-unproven",
                    "strict legacy parser and byte-for-byte canonical rerender did not prove ownership",
                ),
            ),
        )
    destination = calculate_procedure_runbook_path(procedure)
    runbook = render_procedure_runbook(procedure)
    destination_state = path_state_reader(destination)
    if destination_state.kind == "missing":
        return _make_setup_action(
            relative,
            "convert",
            "convert the exact legacy procedure Skill into a static Markdown runbook during cleanup",
            state,
            ownership="reporivet-generated",
            proposed_type="missing",
            proposed_path=destination,
            destination_state=destination_state,
            destination_content=runbook,
        )
    if (
        destination_state.kind == "regular"
        and destination_state.content == runbook.encode("utf-8")
    ):
        return _make_setup_action(
            relative,
            "remove",
            "remove the exact legacy procedure Skill; its exact static runbook already exists",
            state,
            ownership="reporivet-generated",
            proposed_type="missing",
            proposed_path=destination,
            destination_state=destination_state,
            destination_content=runbook,
        )
    return _make_setup_action(
        relative,
        "conflict",
        "exact legacy procedure Skill cannot be converted because the runbook destination is occupied or unsafe",
        state,
        ownership="ambiguous",
        proposed_path=destination,
        destination_state=destination_state,
        destination_content=runbook,
        diagnostics=(
            SetupDiagnostic(
                relative,
                "runbook-collision",
                f"conversion destination is not the exact expected runbook: {destination}",
            ),
        ),
    )


def _legacy_cleanup_actions(
    *,
    root: Path,
    draft: DefinitionDraft,
    desired_contents: Mapping[str, str],
    path_state_reader: Callable[[str], _SetupPathState],
) -> tuple[dict[str, SetupAction], tuple[SetupDiagnostic, ...]]:
    values = _bundle_values(root, draft)
    actions: dict[str, SetupAction] = {}
    diagnostics: list[SetupDiagnostic] = []

    for relative in (*_LEGACY_FIXED_HASHES,):
        action = _legacy_fixed_action(
            root,
            relative,
            path_state_reader=path_state_reader,
        )
        if action is not None:
            actions[relative] = action
            diagnostics.extend(action.diagnostics)

    for relative in ("AGENTS.md", ".gitignore"):
        action = _legacy_marker_action(
            root,
            relative,
            desired_contents.get(relative, ""),
            values,
            path_state_reader=path_state_reader,
        )
        if action is not None:
            actions[relative] = action
            diagnostics.extend(action.diagnostics)

    skills_root = path_state_reader(".claude/skills")
    if skills_root.kind == "missing":
        return actions, tuple(diagnostics)
    if skills_root.kind != "directory":
        action = _make_setup_action(
            ".claude/skills",
            "conflict",
            "Claude Skill inventory root is unsafe or nonregular; cleanup will not traverse it",
            skills_root,
            ownership="ambiguous",
            diagnostics=(
                SetupDiagnostic(
                    ".claude/skills",
                    "unsafe-path",
                    "cleanup uses no-follow traversal and refuses an unsafe Skill inventory root",
                ),
            ),
        )
        actions[".claude/skills"] = action
        diagnostics.extend(action.diagnostics)
        return actions, tuple(diagnostics)

    for child in skills_root.children:
        child_relative = f".claude/skills/{child}"
        child_state = path_state_reader(child_relative)
        if child_state.kind != "directory":
            if child_state.kind != "missing":
                action = _make_setup_action(
                    child_relative,
                    "conflict",
                    "Claude Skill directory candidate is unsafe or nonregular",
                    child_state,
                    ownership="ambiguous",
                    diagnostics=(
                        SetupDiagnostic(
                            child_relative,
                            "unsafe-path",
                            "cleanup refuses to traverse a symlinked or non-directory Skill child",
                        ),
                    ),
                )
                actions[child_relative] = action
                diagnostics.extend(action.diagnostics)
            continue
        relative = f"{child_relative}/SKILL.md"
        if relative in actions:
            continue
        state = path_state_reader(relative)
        if state.kind == "missing":
            continue
        action = _legacy_procedure_action(
            root,
            relative,
            state,
            path_state_reader=path_state_reader,
        )
        actions[relative] = action
        diagnostics.extend(action.diagnostics)
    return actions, tuple(diagnostics)


def _build_guided_setup_preview(
    *,
    root: Path,
    with_claude_settings: bool,
    state_reader: Callable[[str], tuple[str, bytes]] | None = None,
    path_state_reader: Callable[[str], _SetupPathState] | None = None,
    draft: DefinitionDraft | None = None,
) -> SetupPreview:
    # The compatibility argument remains accepted by protected callers, but no
    # settings asset is generated in the one-shot bundle.
    del with_claude_settings
    if draft is None:
        _, draft = _read_definition(root)
    contents = _target_asset_contents(
        root,
        draft,
        with_claude_settings=False,
    )
    procedure_plan = build_procedure_runbook_plan(
        draft.evidence["procedures"].confirmed
    )
    for target in procedure_plan.targets:
        contents[target.path] = target.content

    reader = path_state_reader or (lambda relative: _path_state(root, relative))
    cleanup_actions, cleanup_diagnostics = _legacy_cleanup_actions(
        root=root,
        draft=draft,
        desired_contents=contents,
        path_state_reader=reader,
    )
    conversion_destinations = {
        action.proposed_path
        for action in cleanup_actions.values()
        if action.action == "convert"
        and action.proposed_path is not None
        and action.destination_current_type == "missing"
    }
    for destination in conversion_destinations:
        contents.pop(destination, None)

    action_map: dict[str, SetupAction] = {
        relative: _setup_action(
            root,
            relative,
            contents[relative],
            state_reader=state_reader,
            path_state=reader(relative),
        )
        for relative in sorted(contents)
    }
    # Cleanup classification is authoritative for paths it claims, including
    # the unmarked replacement of an exact old AGENTS.md file.
    action_map.update(cleanup_actions)
    actions = tuple(
        sorted(
            action_map.values(),
            key=lambda action: (
                action.path,
                action.action,
                action.proposed_path or "",
            ),
        )
    )
    diagnostics: list[object] = [*procedure_plan.diagnostics, *cleanup_diagnostics]
    diagnostics = sorted(
        {
            json.dumps(
                SetupPreview._diagnostic_dict(diagnostic),
                ensure_ascii=False,
                sort_keys=True,
            ): diagnostic
            for diagnostic in diagnostics
        }.values(),
        key=lambda diagnostic: json.dumps(
            SetupPreview._diagnostic_dict(diagnostic),
            ensure_ascii=False,
            sort_keys=True,
        ),
    )
    fingerprint_payload = {
        "actions": [action.as_dict() for action in actions],
        "diagnostics": [
            SetupPreview._diagnostic_dict(diagnostic) for diagnostic in diagnostics
        ],
        "schema": "reporivet.setup-preview/v1",
    }
    canonical = json.dumps(
        fingerprint_payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return SetupPreview(
        actions,
        _sha256_bytes(canonical),
        tuple(diagnostics),
    )


def _initialization_definition(
    root: Path,
    *,
    name: str,
    summary: str,
) -> DefinitionDraft:
    draft = _initial_definition(root, None)
    explicit_name = name.strip()
    explicit_summary = summary.strip()
    if any("\n" in value or "\r" in value for value in (explicit_name, explicit_summary)):
        raise InitError("init name and summary must each be a single line")
    confirmed: list[str] = []
    if explicit_name:
        confirmed.append(f"Project name: {explicit_name}")
    if explicit_summary:
        confirmed.append(f"Project purpose: {explicit_summary}")
    if confirmed:
        product = draft.evidence["product"]
        product.confirmed = confirmed
        product.sources.append("Project metadata supplied explicitly to reporivet init.")
        if explicit_summary:
            product.open = []
    return draft


def maintain_document_first_bundle(
    *,
    root: Path,
    name: str = "",
    summary: str = "",
    create: bool,
    dry_run: bool,
) -> ChangeSet:
    root = validate_root(root, create=create, dry_run=dry_run)
    draft = _initialization_definition(root, name=name, summary=summary)
    transaction: _GuidedSetupTransaction | None = None
    if dry_run and not root.exists():
        preview = _build_guided_setup_preview(
            root=root,
            with_claude_settings=False,
            state_reader=lambda _relative: ("missing", b""),
            path_state_reader=lambda _relative: _SetupPathState("missing"),
            draft=draft,
        )
    else:
        transaction = _GuidedSetupTransaction(root)
        try:
            preview = _build_guided_setup_preview(
                root=root,
                with_claude_settings=False,
                state_reader=transaction.regular_file_state,
                path_state_reader=lambda relative: _path_state(root, relative),
                draft=draft,
            )
        except BaseException:
            transaction.close()
            raise

    changes = ChangeSet()
    conflicts = [action.path for action in preview.actions if action.action == "conflict"]
    if conflicts:
        if transaction is not None:
            transaction.close()
        raise InitError(
            "document-first setup contains unsafe target conflicts: "
            + ", ".join(conflicts)
        )
    for action in preview.actions:
        path = root / action.path
        if action.action == "create":
            changes.created.append(path)
        elif action.action == "update":
            changes.updated.append(path)
        else:
            changes.skipped.append(path)
    if dry_run:
        if transaction is not None:
            transaction.close()
        changes.print(root, dry_run=True)
        return changes

    assert transaction is not None
    try:
        try:
            for action in preview.actions:
                _assert_action_current(
                    root,
                    action,
                    state_reader=transaction.regular_file_state,
                )
            for action in preview.actions:
                if action.action == "create":
                    transaction.create_file(
                        action.path,
                        action.content.encode("utf-8"),
                    )
                elif action.action == "update":
                    transaction.update_file(
                        action.path,
                        action.content.encode("utf-8"),
                        action.current_sha256,
                    )
            transaction.commit()
        except Exception as exc:
            try:
                transaction.rollback()
            except InitError as rollback_exc:
                raise InitError(
                    f"document-first setup failed ({exc}); {rollback_exc}"
                ) from rollback_exc
            if isinstance(exc, InitError):
                raise
            raise InitError(
                f"document-first setup failed and was rolled back: {exc}"
            ) from exc
    finally:
        transaction.close()
    changes.print(root)
    return changes


def _preview_setup_from_definition(
    *,
    root: Path,
    with_claude_settings: bool,
    draft: DefinitionDraft,
) -> SetupPreview:
    root = validate_root(root)
    transaction = _GuidedSetupTransaction(root)
    try:
        return _build_guided_setup_preview(
            root=root,
            with_claude_settings=with_claude_settings,
            state_reader=transaction.regular_file_state,
            path_state_reader=lambda relative: _path_state(root, relative),
            draft=draft,
        )
    finally:
        transaction.close()


def preview_guided_setup(
    *,
    root: Path,
    with_claude_settings: bool,
) -> SetupPreview:
    root = validate_root(root)
    transaction = _GuidedSetupTransaction(root)
    try:
        return _build_guided_setup_preview(
            root=root,
            with_claude_settings=with_claude_settings,
            state_reader=transaction.regular_file_state,
            path_state_reader=lambda relative: _path_state(root, relative),
        )
    finally:
        transaction.close()


def _assert_action_current(
    root: Path,
    action: SetupAction,
    *,
    state_reader: Callable[[str], tuple[str, bytes]] | None = None,
) -> None:
    if action.action == "conflict":
        return
    state, content = (
        state_reader(action.path)
        if state_reader is not None
        else _regular_file_state(root / action.path)
    )
    if action.action == "create" and state != "missing":
        raise InitError(
            f"setup target changed after preview: {action.path}; rerun finalize preview"
        )
    if action.action in {"update", "preserve", "unchanged", "remove", "convert"} and (
        state != "file" or _sha256_bytes(content) != action.current_sha256
    ):
        raise InitError(
            f"setup target changed after preview: {action.path}; rerun finalize preview"
        )


def _apply_guided_setup_quiet(
    *,
    root: Path,
    approve_preview: str,
    with_claude_settings: bool,
) -> tuple[SetupPreview, ChangeSet, DefinitionDraft]:
    root = validate_root(root)
    transaction = _GuidedSetupTransaction(root)
    changes = ChangeSet()
    try:
        try:
            _, draft = _read_definition(root)
            preview = _build_guided_setup_preview(
                root=root,
                with_claude_settings=with_claude_settings,
                state_reader=transaction.regular_file_state,
                path_state_reader=lambda relative: _path_state(root, relative),
                draft=draft,
            )
            if not approve_preview or approve_preview != preview.fingerprint:
                raise InitError(
                    "setup preview approval does not match the current target; rerun finalize preview and approve its exact fingerprint"
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

            for action in preview.actions:
                _assert_action_current(
                    root,
                    action,
                    state_reader=transaction.regular_file_state,
                )
            for action in preview.actions:
                path = root / action.path
                if action.action == "create":
                    _assert_action_current(
                        root,
                        action,
                        state_reader=transaction.regular_file_state,
                    )
                    transaction.create_file(
                        action.path,
                        action.content.encode("utf-8"),
                    )
                    changes.created.append(path)
                elif action.action == "update":
                    _assert_action_current(
                        root,
                        action,
                        state_reader=transaction.regular_file_state,
                    )
                    transaction.update_file(
                        action.path,
                        action.content.encode("utf-8"),
                        action.current_sha256,
                    )
                    changes.updated.append(path)
                else:
                    _assert_action_current(
                        root,
                        action,
                        state_reader=transaction.regular_file_state,
                    )
                    changes.skipped.append(path)
            transaction.commit()
        except Exception as exc:
            try:
                transaction.rollback()
            except InitError as rollback_exc:
                raise InitError(
                    f"guided setup failed ({exc}); {rollback_exc}"
                ) from rollback_exc
            if isinstance(exc, InitError):
                raise
            raise InitError(
                f"guided setup failed and was rolled back: {exc}"
            ) from exc
    finally:
        transaction.close()
    return preview, changes, draft


def apply_guided_setup(
    *,
    root: Path,
    approve_preview: str,
    with_claude_settings: bool,
) -> ChangeSet:
    root = validate_root(root)
    _, changes, _ = _apply_guided_setup_quiet(
        root=root,
        approve_preview=approve_preview,
        with_claude_settings=with_claude_settings,
    )
    changes.print(root)
    return changes

# Narrow compatibility helper retained for migration's legacy Plan inventory.
# Guided setup no longer diagnoses or validates active Plans.
def _parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line or line.startswith((" ", "\t", "-")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values
