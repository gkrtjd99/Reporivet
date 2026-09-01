from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import stat
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

from . import __version__
from .initializer import (
    AGENTS_END,
    AGENTS_START,
    GITIGNORE_END,
    GITIGNORE_START,
    AuditReport,
    ChangeSet,
    InitError,
    audit_project,
    ensure_safe_write_path,
    extract_block,
    is_managed_file,
    read_asset,
    symlink_component,
    upsert_block_text_preserving,
    validate_root,
)
from .procedures import ProcedureDiagnostic, build_procedure_skill_plan

DEFINITION_DRAFT_PATH = Path("docs/product-specs/project-definition.draft.md")
EVIDENCE_HEADINGS = ("Confirmed", "Proposed", "Open", "Sources")
ACTIVE_PLAN_STATES = frozenset({"proposed", "approved", "in-progress", "verifying", "blocked"})
TERMINAL_PLAN_STATES = frozenset({"complete", "cancelled", "superseded"})


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
        "Which repeated procedures deserve a runbook or optional Skill, including their trigger, stop conditions, evidence, permissions, and rollback?",
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


@dataclass(frozen=True)
class SetupAction:
    path: str
    action: str
    reason: str
    current_sha256: str
    proposed_sha256: str
    content: str

    def as_dict(self) -> dict[str, str]:
        return {
            "action": self.action,
            "content": self.content,
            "current_sha256": self.current_sha256,
            "path": self.path,
            "proposed_sha256": self.proposed_sha256,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class SetupPreview:
    actions: tuple[SetupAction, ...]
    fingerprint: str
    diagnostics: tuple[ProcedureDiagnostic, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "actions": [action.as_dict() for action in self.actions],
            "diagnostics": [diagnostic.as_dict() for diagnostic in self.diagnostics],
            "fingerprint": self.fingerprint,
            "schema": "reporivet.setup-preview/v1",
        }

    def render(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


@dataclass(frozen=True)
class DoctorFinding:
    severity: str
    path: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"detail": self.detail, "path": self.path, "severity": self.severity}


@dataclass(frozen=True)
class DoctorReport:
    findings: tuple[DoctorFinding, ...]

    @property
    def errors(self) -> tuple[DoctorFinding, ...]:
        return tuple(finding for finding in self.findings if finding.severity == "error")

    def as_dict(self) -> dict[str, object]:
        return {
            "findings": [finding.as_dict() for finding in self.findings],
            "schema": "reporivet.doctor/v2",
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

CLAUDE_PROFILE_ASSETS: dict[str, str] = {
    "CLAUDE.md": "document-first/claude/CLAUDE.md.tmpl",
    ".claude/skills/reporivet-main/SKILL.md": "document-first/claude/skills/reporivet-main/SKILL.md.tmpl",
    ".claude/skills/reporivet-implementation/SKILL.md": "document-first/claude/skills/reporivet-implementation/SKILL.md.tmpl",
    ".claude/skills/reporivet-verification/SKILL.md": "document-first/claude/skills/reporivet-verification/SKILL.md.tmpl",
}

REQUIRED_DOCUMENT_FIRST_DIRECTORIES = (
    "docs/exec-plans/active",
    "docs/exec-plans/completed",
)

REQUIRED_DOCUMENT_FIRST_PATHS = (
    "AGENTS.md",
    "ARCHITECTURE.md",
    ".reporivet-version",
    "docs/README.md",
    "docs/PRODUCT.md",
    "docs/DESIGN.md",
    "docs/QUALITY.md",
    "docs/OPERATIONS.md",
    "docs/SECURITY.md",
    "docs/PLANS.md",
    "docs/exec-plans/_template.md",
    "docs/exec-plans/active",
    "docs/exec-plans/completed",
)

CURRENT_AUTHORITY_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "AGENTS.md": (
        "# Repository Agent Operating Contract",
        "## Start here",
        "## Sources of truth",
        "## Main, implementation, and verification",
        "### Confirmed",
        "### Proposed",
        "### Open",
        "### Sources",
    ),
    "ARCHITECTURE.md": (
        "# Architecture",
        "## Current system map",
        "## Ownership and dependency direction",
        "## Runtime, data, and external systems",
        "### Confirmed",
        "### Proposed",
        "### Open",
        "### Sources",
    ),
    "docs/README.md": (
        "# Repository Knowledge Map",
        "## Reading protocol",
        "## Canonical paths",
        "## Route by work",
        "## Evidence states",
    ),
    "docs/PRODUCT.md": (
        "# Product",
        "## Product, users, problem, and success",
        "## Current scope",
        "### Confirmed",
        "### Proposed",
        "### Open",
        "### Sources",
    ),
    "docs/DESIGN.md": (
        "# Design",
        "## Design direction and accessibility",
        "## Durable defaults",
        "## Change protocol",
        "### Confirmed",
        "### Proposed",
        "### Open",
        "### Sources",
    ),
    "docs/QUALITY.md": (
        "# Quality",
        "## Required checks and commands",
        "## Evidence contract",
        "## Quality gaps",
        "### Confirmed",
        "### Proposed",
        "### Open",
        "### Sources",
    ),
    "docs/OPERATIONS.md": (
        "# Operations",
        "## Operating model",
        "## Required operational knowledge",
        "## Procedure requirements",
        "### Confirmed",
        "### Proposed",
        "### Open",
        "### Sources",
    ),
    "docs/SECURITY.md": (
        "# Security",
        "## Authentication, authorization, data, secrets, and permissions",
        "## Durable rules",
        "## Open security work",
        "### Confirmed",
        "### Proposed",
        "### Open",
        "### Sources",
    ),
    "docs/PLANS.md": (
        "# Plans",
        "## When to use a Plan",
        "## Ownership and lifecycle",
        "## Minimum active Plan content",
        "## Completion",
    ),
}

RETIRED_CURRENT_PATTERNS = (
    (re.compile(r"(?<![A-Za-z0-9_])\./dev/", re.IGNORECASE), "live reference to a retired Reporivet `./dev/*` command"),
    (re.compile(r"\.harness/runs", re.IGNORECASE), "live reference to retired Reporivet run evidence"),
    (re.compile(r"\bclose-plan\b", re.IGNORECASE), "live reference to retired automatic Plan closure"),
    (re.compile(r"\bverification run\b", re.IGNORECASE), "live reference to the retired Verification Run"),
    (re.compile(r"\bgate verdict\b|\bgate_verdict\b", re.IGNORECASE), "live reference to the retired Gate verdict"),
    (re.compile(r"(?<![A-Za-z0-9_])gate(?!s\b|[A-Za-z0-9_])", re.IGNORECASE), "live reference to the retired singular Gate mechanism"),
    (re.compile(r"\b(?:harness|reporivet|repository-local|verification)\s+runtime\b", re.IGNORECASE), "live reference to the retired Reporivet runtime"),
    (re.compile(r"\b(?:automatic|generated|reporivet|repository-local|plan)\s+(?:plan\s+)?closure\b", re.IGNORECASE), "live reference to retired automatic Plan closure"),
)

LEGACY_MANAGED_FILES = (
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
    ".github/workflows/harness-verify.yml",
    ".github/workflows/harness-garden.yml",
)

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
    values = _bundle_values(root, draft)
    contents = {
        "AGENTS.md": _read_guided_asset("document-first/root/AGENTS.md.tmpl", values),
        ".gitignore": _read_guided_asset("document-first/root/gitignore.block.tmpl", values),
        ".reporivet-version": _read_guided_asset("root/reporivet-version.tmpl", values),
    }
    for destination, asset in DOCUMENT_FIRST_DOCUMENTS.items():
        contents[destination] = _read_guided_asset(asset, values)
    for destination, asset in CLAUDE_PROFILE_ASSETS.items():
        contents[destination] = _read_guided_asset(asset, values)
    contents["docs/exec-plans/active/.gitkeep"] = ""
    contents["docs/exec-plans/completed/.gitkeep"] = ""
    if with_claude_settings:
        contents[".claude/settings.json"] = _read_guided_asset(
            "document-first/optional/claude-settings.deny-only.json.tmpl",
            values,
        )
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


def _setup_action(
    root: Path,
    relative: str,
    proposed: str,
    *,
    state_reader: Callable[[str], tuple[str, bytes]] | None = None,
) -> SetupAction:
    path = root / relative
    state, current = (
        state_reader(relative)
        if state_reader is not None
        else _regular_file_state(path)
    )
    normalized = proposed.rstrip() + "\n" if proposed else ""
    proposed_bytes = normalized.encode("utf-8")
    current_hash = _sha256_bytes(current) if state == "file" else ""
    proposed_hash = _sha256_bytes(proposed_bytes)

    if state == "conflict":
        return SetupAction(
            relative,
            "conflict",
            "target is symlinked, nonregular, or unreadable and will not be changed",
            current_hash,
            proposed_hash,
            normalized,
        )

    if relative == "AGENTS.md":
        block = extract_block(normalized, AGENTS_START, AGENTS_END)
        try:
            updated = upsert_block_text_preserving(
                current.decode("utf-8") if state == "file" else "",
                block,
                AGENTS_START,
                AGENTS_END,
            )
        except (InitError, UnicodeError):
            return SetupAction(
                relative,
                "conflict",
                "existing canonical instruction file cannot receive a safe bounded block",
                current_hash,
                proposed_hash,
                normalized,
            )
        proposed_hash = _sha256_text(updated)
        if state == "file" and current == updated.encode("utf-8"):
            return SetupAction(relative, "unchanged", "canonical instruction block is current", current_hash, proposed_hash, updated)
        return SetupAction(
            relative,
            "update" if state == "file" else "create",
            "write only the bounded Reporivet instruction block and preserve surrounding project text",
            current_hash,
            proposed_hash,
            updated,
        )

    if relative == ".gitignore":
        block = normalized.strip()
        try:
            updated = upsert_block_text_preserving(
                current.decode("utf-8") if state == "file" else "",
                block,
                GITIGNORE_START,
                GITIGNORE_END,
            )
        except (InitError, UnicodeError):
            return SetupAction(
                relative,
                "conflict",
                "existing ignore file cannot receive a safe bounded block",
                current_hash,
                proposed_hash,
                normalized,
            )
        proposed_hash = _sha256_text(updated)
        if state == "file" and current == updated.encode("utf-8"):
            return SetupAction(relative, "unchanged", "bounded ignore block is current", current_hash, proposed_hash, updated)
        return SetupAction(
            relative,
            "update" if state == "file" else "create",
            "write only the bounded Reporivet ignore block and preserve surrounding project text",
            current_hash,
            proposed_hash,
            updated,
        )

    if state == "missing":
        return SetupAction(
            relative,
            "create",
            "create the missing document-first bundle path",
            "",
            proposed_hash,
            normalized,
        )
    if current == proposed_bytes:
        return SetupAction(
            relative,
            "unchanged",
            "existing bytes already match the proposed asset",
            current_hash,
            proposed_hash,
            normalized,
        )
    if relative == ".claude/settings.json":
        reason = "existing project settings are preserved; Reporivet never merges or rewrites them"
    elif relative == "CLAUDE.md":
        reason = "existing host instructions are preserved for manual reconciliation"
    else:
        reason = "existing project-owned content is preserved byte-for-byte"
    return SetupAction(relative, "preserve", reason, current_hash, proposed_hash, normalized)


def _settings_setup_action(
    root: Path,
    proposed: str | None,
    *,
    state_reader: Callable[[str], tuple[str, bytes]] | None = None,
) -> SetupAction | None:
    relative = ".claude/settings.json"
    state, current = (
        state_reader(relative)
        if state_reader is not None
        else _regular_file_state(root / relative)
    )
    redacted_hash = _sha256_bytes(b"")
    if state == "missing":
        if proposed is None:
            return None
        return _setup_action(
            root,
            relative,
            proposed,
            state_reader=state_reader,
        )
    if state == "conflict":
        return SetupAction(
            relative,
            "conflict",
            "project settings target is unsafe, symlinked, nonregular, or unreadable; Reporivet will not expose or change its content",
            "",
            redacted_hash,
            "",
        )
    return SetupAction(
        relative,
        "preserve",
        "existing project settings are preserved; Reporivet never merges or rewrites them",
        _sha256_bytes(current),
        redacted_hash,
        "",
    )


def _build_guided_setup_preview(
    *,
    root: Path,
    with_claude_settings: bool,
    state_reader: Callable[[str], tuple[str, bytes]] | None = None,
    draft: DefinitionDraft | None = None,
) -> SetupPreview:
    if draft is None:
        _, draft = _read_definition(root)
    contents = _target_asset_contents(
        root,
        draft,
        with_claude_settings=with_claude_settings,
    )
    procedure_plan = build_procedure_skill_plan(
        draft.evidence["procedures"].confirmed
    )
    for target in procedure_plan.targets:
        contents[target.path] = target.content
    settings_proposed = contents.pop(".claude/settings.json", None)
    action_list = [
        _setup_action(
            root,
            relative,
            contents[relative],
            state_reader=state_reader,
        )
        for relative in sorted(contents)
    ]
    settings_action = _settings_setup_action(
        root,
        settings_proposed,
        state_reader=state_reader,
    )
    if settings_action is not None:
        action_list.append(settings_action)
    actions = tuple(sorted(action_list, key=lambda action: action.path))
    canonical = json.dumps(
        [action.as_dict() for action in actions],
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return SetupPreview(
        actions,
        _sha256_bytes(canonical),
        procedure_plan.diagnostics,
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
            draft=draft,
        )
    else:
        transaction = _GuidedSetupTransaction(root)
        try:
            preview = _build_guided_setup_preview(
                root=root,
                with_claude_settings=False,
                state_reader=transaction.regular_file_state,
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
    if action.action in {"update", "preserve", "unchanged"} and (
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


COMPACT_PLAN_HEADINGS = (
    "## Original goal",
    "## Observable outcome and acceptance",
    "## Scope",
    "## Non-goals",
    "## Task state",
    "## Task Packets",
    "## Current checkpoint",
    "## Exact next action",
    "## Decisions",
    "## Discoveries",
    "## Documentation impact",
    "## Integration summary",
    "## Verification summary",
    "## Follow-ups",
    "## Outcome",
)


def _markdown_section(text: str, heading: str) -> str:
    match = re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE)
    if match is None:
        return ""
    next_heading = re.search(r"^## [^#].*$", text[match.end() :], re.MULTILINE)
    end = len(text) if next_heading is None else match.end() + next_heading.start()
    return text[match.end() : end].strip()


COMPACT_PLAN_SIGNATURE_HEADINGS = (
    "## Original goal",
    "## Observable outcome and acceptance",
    "## Task state",
    "## Integration summary",
    "## Verification summary",
    "## Outcome",
)
OWNER_PLACEHOLDERS = frozenset(
    {"", "-", "none", "pending", "placeholder", "tbd", "todo", "unassigned", "unknown"}
)
UNRESOLVED_PLACEHOLDER = re.compile(
    r"\b(?:not yet|pending|placeholder|tbd|to be determined|todo|unknown|unresolved)\b",
    re.IGNORECASE,
)
TASK_ID_PATTERN = re.compile(r"T[0-9]+(?:[-.][A-Za-z0-9]+)*")


def _normalized_markdown_text(text: str) -> str:
    normalized = re.sub(r"[`*_#|\-]", " ", text)
    return re.sub(r"\s+", " ", normalized).strip(" .:;\t\r\n").casefold()


def _owner_is_placeholder(value: str) -> bool:
    normalized = _normalized_markdown_text(value)
    return (
        normalized in OWNER_PLACEHOLDERS
        or UNRESOLVED_PLACEHOLDER.search(normalized) is not None
    )


def _contains_unresolved_placeholder(normalized: str) -> bool:
    for match in UNRESOLVED_PLACEHOLDER.finditer(normalized):
        if match.group(0).casefold() != "not yet" and re.search(
            r"\b(?:no|not|without)\s+$",
            normalized[: match.start()],
        ):
            continue
        return True
    return False


def _section_is_unresolved(text: str, *, allow_none: bool) -> bool:
    normalized = _normalized_markdown_text(text)
    if not normalized or _contains_unresolved_placeholder(normalized):
        return True
    return not allow_none and normalized in {"n/a", "none", "not applicable"}


def _has_markdown_heading(text: str, heading: str) -> bool:
    return re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE) is not None


def _has_compact_plan_signature(text: str) -> bool:
    present = {
        heading for heading in COMPACT_PLAN_SIGNATURE_HEADINGS if _has_markdown_heading(text, heading)
    }
    return "## Task state" in present or len(present) >= 2


def _compact_plan_structure_findings(
    *,
    relative: str,
    text: str,
    metadata: Mapping[str, str],
    status: str,
) -> list[DoctorFinding]:
    findings: list[DoctorFinding] = []
    for heading in COMPACT_PLAN_HEADINGS:
        if not _has_markdown_heading(text, heading):
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan is missing {heading[3:]}",
                )
            )

    if _owner_is_placeholder(metadata.get("owner", "")):
        findings.append(
            DoctorFinding(
                "error",
                relative,
                "compact Plan is missing an explicit Plan owner",
            )
        )

    for heading in ("## Current checkpoint", "## Exact next action"):
        if _has_markdown_heading(text, heading) and _section_is_unresolved(
            _markdown_section(text, heading),
            allow_none=False,
        ):
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan {heading[3:]} is missing or placeholder",
                )
            )

    task_section = _markdown_section(text, "## Task state")
    rows = [line for line in task_section.splitlines() if line.strip().startswith("|")]
    header = [cell.strip() for cell in rows[0].strip().strip("|").split("|")] if rows else []
    task_ids: list[str] = []
    row_owners: dict[str, list[str]] = {}
    if "Task" not in header or "Owner" not in header:
        findings.append(
            DoctorFinding(
                "error",
                relative,
                "compact Plan task state table must contain Task and Owner columns",
            )
        )
    else:
        task_index = header.index("Task")
        owner_index = header.index("Owner")
        for row in rows[2:]:
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            if len(cells) <= max(task_index, owner_index):
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        "compact Plan task state contains a malformed task row",
                    )
                )
                continue
            task_id = cells[task_index]
            if TASK_ID_PATTERN.fullmatch(task_id) is None:
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"compact Plan task row has invalid Task id '{task_id or 'missing'}'",
                    )
                )
                continue
            owner = cells[owner_index]
            task_ids.append(task_id)
            row_owners.setdefault(task_id, []).append(owner)
            if _owner_is_placeholder(owner):
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"compact Plan task {task_id} is missing an explicit Owner",
                    )
                )
        if not task_ids:
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    "compact Plan task state must contain at least one valid task row",
                )
            )

    for task_id, count in sorted(Counter(task_ids).items()):
        if count > 1:
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan has duplicate task row id {task_id}",
                )
            )

    packet_section = _markdown_section(text, "## Task Packets")
    packet_matches = list(
        re.finditer(
            r"^### (T[0-9]+(?:[-.][A-Za-z0-9]+)*)\b.*$",
            packet_section,
            re.MULTILINE,
        )
    )
    packets: list[tuple[str, str]] = []
    for index, match in enumerate(packet_matches):
        end = (
            packet_matches[index + 1].start()
            if index + 1 < len(packet_matches)
            else len(packet_section)
        )
        packets.append((match.group(1), packet_section[match.end() : end]))
    packet_ids = [task_id for task_id, _ in packets]
    if not packet_ids:
        findings.append(
            DoctorFinding(
                "error",
                relative,
                "compact Plan Task Packets must contain at least one packet",
            )
        )
    for task_id, count in sorted(Counter(packet_ids).items()):
        if count > 1:
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan has duplicate Task Packet id {task_id}",
                )
            )

    task_id_set = set(task_ids)
    packet_id_set = set(packet_ids)
    for task_id in sorted(task_id_set - packet_id_set):
        findings.append(
            DoctorFinding(
                "error",
                relative,
                f"compact Plan task {task_id} is missing a Task Packet",
            )
        )
    for task_id in sorted(packet_id_set - task_id_set):
        findings.append(
            DoctorFinding(
                "error",
                relative,
                f"compact Plan has unexpected Task Packet {task_id} without a task row",
            )
        )

    packet_owners: dict[str, list[str]] = {}
    for task_id, packet in packets:
        owner_match = re.search(r"^- \*\*Owner:\*\*\s*(.*?)\s*$", packet, re.MULTILINE)
        owner = "" if owner_match is None else owner_match.group(1).strip()
        packet_owners.setdefault(task_id, []).append(owner)
        if _owner_is_placeholder(owner):
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan Task Packet {task_id} is missing an explicit Owner",
                )
            )

    for task_id in sorted(task_id_set & packet_id_set):
        row_values = row_owners.get(task_id, [])
        packet_values = packet_owners.get(task_id, [])
        if (
            len(row_values) == 1
            and len(packet_values) == 1
            and not _owner_is_placeholder(row_values[0])
            and not _owner_is_placeholder(packet_values[0])
            and row_values[0] != packet_values[0]
        ):
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} row and Task Packet owners disagree",
                )
            )

    terminal_status = status if status in TERMINAL_PLAN_STATES else ""
    if terminal_status:
        terminal_sections = (
            ("## Documentation impact", True),
            ("## Integration summary", False),
            ("## Verification summary", False),
            ("## Follow-ups", True),
            ("## Outcome", False),
        )
        for heading, allow_none in terminal_sections:
            if _has_markdown_heading(text, heading) and _section_is_unresolved(
                _markdown_section(text, heading),
                allow_none=allow_none,
            ):
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"terminal compact Plan must resolve {heading[3:]}",
                    )
                )
        if _has_markdown_heading(text, "## Outcome"):
            outcome = _markdown_section(text, "## Outcome")
            stated = _normalized_markdown_text(outcome)
            if stated != terminal_status:
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"compact Plan Outcome must agree with terminal status '{terminal_status}'",
                    )
                )
    return findings


_STRICT_TASK_COLUMNS = (
    "Task",
    "Owner",
    "State",
    "Depends on",
    "Parallel group",
    "Outcome",
    "Result",
)
_STRICT_PACKET_FIELDS = (
    "Owner",
    "Role",
    "Parent",
    "Parallel group",
    "May delegate",
    "Inherited boundaries",
    "Outcome",
    "Non-goals",
    "Read",
    "Allowed writes",
    "Protected paths",
    "Acceptance",
    "Verification",
    "Stop conditions",
    "Return",
    "Result",
)
_STRICT_ROLES = ("Task Owner", "leaf", "integration", "verification")
_STRICT_ROLE_BY_CASEFOLD = {role.casefold(): role for role in _STRICT_ROLES}
_STRICT_STATES = (
    "ready",
    "blocked",
    "in-progress",
    "verifying",
    "complete",
    "cancelled",
    "superseded",
)
_STRICT_RESULTS = ("pending", "complete", "cancelled", "superseded")
_STRICT_RESULT_FOR_STATE = {
    "ready": "pending",
    "blocked": "pending",
    "in-progress": "pending",
    "verifying": "pending",
    "complete": "complete",
    "cancelled": "cancelled",
    "superseded": "superseded",
}


@dataclass(frozen=True)
class _StrictTaskRow:
    task_id: str
    owner: str
    state: str
    dependencies: tuple[str, ...]
    parallel_group: str
    outcome: str
    result: str
    mapping_valid: bool
    owner_valid: bool
    state_valid: bool
    dependencies_valid: bool
    parallel_group_valid: bool
    outcome_valid: bool
    result_valid: bool


@dataclass(frozen=True)
class _StrictTaskPacket:
    task_id: str
    values: tuple[tuple[str, str], ...]
    valid: bool


@dataclass(frozen=True)
class _StrictTaskGraph:
    rows: tuple[_StrictTaskRow, ...]
    packets: tuple[_StrictTaskPacket, ...]


def _strict_packet_value(packet: _StrictTaskPacket, field: str) -> str:
    return dict(packet.values).get(field, "")


def _strict_parse_dependencies(
    *,
    relative: str,
    task_id: str,
    raw: str,
) -> tuple[tuple[str, ...], bool, list[DoctorFinding]]:
    value = raw.strip()
    if value == "none":
        return (), True, []
    if not value:
        return (
            (),
            False,
            [
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} Depends on is missing; use none for no dependencies",
                )
            ],
        )

    tokens = tuple(piece.strip() for piece in value.split(","))
    if any(not token for token in tokens):
        return (
            tokens,
            False,
            [
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} Depends on contains a blank dependency",
                )
            ],
        )
    if "none" in tokens:
        return (
            tokens,
            False,
            [
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} Depends on cannot mix none with task IDs",
                )
            ],
        )
    malformed = next(
        (token for token in tokens if TASK_ID_PATTERN.fullmatch(token) is None),
        None,
    )
    if malformed is not None:
        return (
            tokens,
            False,
            [
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} Depends on contains malformed Task ID '{malformed}'",
                )
            ],
        )
    duplicate = next(
        (token for token in tokens if tokens.count(token) > 1),
        None,
    )
    if duplicate is not None:
        return (
            tokens,
            False,
            [
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} has duplicate dependency {duplicate}",
                )
            ],
        )
    return tokens, True, []


def _strict_parse_task_rows(
    *,
    relative: str,
    text: str,
) -> tuple[tuple[_StrictTaskRow, ...], list[DoctorFinding]]:
    findings: list[DoctorFinding] = []
    task_section = _markdown_section(text, "## Task state")
    rows = [line for line in task_section.splitlines() if line.strip().startswith("|")]
    header = [cell.strip() for cell in rows[0].strip().strip("|").split("|")] if rows else []
    missing = [column for column in _STRICT_TASK_COLUMNS if column not in header]
    duplicates = [
        column
        for column in _STRICT_TASK_COLUMNS
        if header.count(column) > 1
    ]
    if missing:
        if not header or any(column not in header for column in ("Task", "Owner")):
            return (), findings
        for column in missing:
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task state table must contain {column} column",
                )
            )
        return (), findings
    if duplicates:
        for column in duplicates:
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task state table has duplicate {column} column",
                )
            )
        return (), findings

    indexes = {column: header.index(column) for column in _STRICT_TASK_COLUMNS}
    parsed: list[_StrictTaskRow] = []
    for raw_row in rows[2:]:
        cells = [cell.strip() for cell in raw_row.strip().strip("|").split("|")]
        if len(cells) <= max(indexes.values()):
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    "compact Plan task state contains a malformed task row",
                )
            )
            continue
        task_id = cells[indexes["Task"]].strip()
        if TASK_ID_PATTERN.fullmatch(task_id) is None:
            continue

        owner = cells[indexes["Owner"]].strip()
        state = cells[indexes["State"]].strip()
        parallel_group = cells[indexes["Parallel group"]].strip()
        outcome = cells[indexes["Outcome"]].strip()
        result = cells[indexes["Result"]].strip()
        dependencies, dependencies_valid, dependency_findings = _strict_parse_dependencies(
            relative=relative,
            task_id=task_id,
            raw=cells[indexes["Depends on"]],
        )
        findings.extend(dependency_findings)

        owner_valid = bool(owner) and not _owner_is_placeholder(owner)
        state_valid = state in _STRICT_STATES
        result_valid = result in _STRICT_RESULTS
        mapping_valid = True
        parallel_group_valid = bool(parallel_group)
        outcome_valid = bool(outcome)

        if not state_valid:
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} has invalid State '{state or 'missing'}'; expected one of {', '.join(_STRICT_STATES)}",
                )
            )
        if not result_valid:
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} has invalid Result '{result or 'missing'}'; expected one of {', '.join(_STRICT_RESULTS)}",
                )
            )
        if state_valid and result_valid:
            expected_result = _STRICT_RESULT_FOR_STATE[state]
            if result != expected_result:
                mapping_valid = False
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"compact Plan task {task_id} State '{state}' requires Result '{expected_result}'",
                    )
                )
        if not parallel_group_valid:
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} is missing Parallel group; use none for no group",
                )
            )
        if not outcome_valid:
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} is missing Outcome",
                )
            )

        parsed.append(
            _StrictTaskRow(
                task_id=task_id,
                owner=owner,
                state=state,
                dependencies=dependencies,
                parallel_group=parallel_group,
                outcome=outcome,
                result=result,
                mapping_valid=mapping_valid,
                owner_valid=owner_valid,
                state_valid=state_valid,
                dependencies_valid=dependencies_valid,
                parallel_group_valid=parallel_group_valid,
                outcome_valid=outcome_valid,
                result_valid=result_valid,
            )
        )
    return tuple(parsed), findings


def _strict_parse_task_packets(
    *,
    relative: str,
    text: str,
) -> tuple[tuple[_StrictTaskPacket, ...], list[DoctorFinding]]:
    findings: list[DoctorFinding] = []
    packet_section = _markdown_section(text, "## Task Packets")
    packet_matches = list(
        re.finditer(
            r"^### (T[0-9]+(?:[-.][A-Za-z0-9]+)*)\b.*$",
            packet_section,
            re.MULTILINE,
        )
    )
    parsed: list[_StrictTaskPacket] = []
    for index, match in enumerate(packet_matches):
        end = (
            packet_matches[index + 1].start()
            if index + 1 < len(packet_matches)
            else len(packet_section)
        )
        packet = packet_section[match.end() : end]
        task_id = match.group(1)
        fields: dict[str, str] = {}
        errors: list[str] = []
        for field_match in re.finditer(
            r"^- \*\*([^*]+):\*\*\s*(.*?)\s*$",
            packet,
            re.MULTILINE,
        ):
            field = field_match.group(1).strip()
            if field not in _STRICT_PACKET_FIELDS:
                continue
            value = field_match.group(2).strip()
            if field in fields:
                errors.append(field)
                continue
            fields[field] = value

        for field in _STRICT_PACKET_FIELDS:
            if field not in fields:
                if field != "Owner":
                    findings.append(
                        DoctorFinding(
                            "error",
                            relative,
                            f"compact Plan Task Packet {task_id} is missing required field {field}",
                        )
                    )
                errors.append(field)
            elif not fields[field]:
                if field != "Owner":
                    findings.append(
                        DoctorFinding(
                            "error",
                            relative,
                            f"compact Plan Task Packet {task_id} has empty required field {field}",
                        )
                    )
                errors.append(field)
        duplicate_fields: set[str] = set()
        seen_fields: set[str] = set()
        for field_match in re.finditer(
            r"^- \*\*([^*]+):\*\*\s*(.*?)\s*$",
            packet,
            re.MULTILINE,
        ):
            field = field_match.group(1).strip()
            if field not in _STRICT_PACKET_FIELDS:
                continue
            if field in seen_fields:
                duplicate_fields.add(field)
            seen_fields.add(field)
        for field in sorted(duplicate_fields):
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan Task Packet {task_id} has duplicate field {field}",
                )
            )
            errors.append(field)

        parsed.append(
            _StrictTaskPacket(
                task_id=task_id,
                values=tuple((field, fields.get(field, "")) for field in _STRICT_PACKET_FIELDS),
                valid=not errors,
            )
        )
    return tuple(parsed), findings


def _strict_lexical_parent(task_id: str) -> str | None:
    separator = max(task_id.rfind("-"), task_id.rfind("."))
    return task_id[:separator] if separator > 0 else None


def _strict_task_graph_findings(
    *,
    relative: str,
    text: str,
) -> list[DoctorFinding]:
    rows, row_findings = _strict_parse_task_rows(relative=relative, text=text)
    packets, packet_findings = _strict_parse_task_packets(relative=relative, text=text)
    findings = [*row_findings, *packet_findings]

    row_groups: dict[str, list[_StrictTaskRow]] = {}
    for row in rows:
        row_groups.setdefault(row.task_id, []).append(row)
    packet_groups: dict[str, list[_StrictTaskPacket]] = {}
    for packet in packets:
        packet_groups.setdefault(packet.task_id, []).append(packet)
    unique_rows = {
        task_id: values[0]
        for task_id, values in row_groups.items()
        if len(values) == 1
    }
    unique_packets = {
        task_id: values[0]
        for task_id, values in packet_groups.items()
        if len(values) == 1
    }
    common_ids = sorted(set(unique_rows) & set(unique_packets))

    for task_id in common_ids:
        row = unique_rows[task_id]
        packet = unique_packets[task_id]
        packet_group = _strict_packet_value(packet, "Parallel group")
        if (
            row.parallel_group_valid
            and packet_group
            and row.parallel_group != packet_group
        ):
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} row and Task Packet parallel groups disagree",
                )
            )

    graph = _StrictTaskGraph(
        rows=tuple(unique_rows[task_id] for task_id in common_ids),
        packets=tuple(unique_packets[task_id] for task_id in common_ids),
    )
    if (
        not graph.rows
        or set(unique_rows) != set(unique_packets)
        or any(len(values) != 1 for values in row_groups.values())
        or any(len(values) != 1 for values in packet_groups.values())
        or any(not row.owner_valid or not row.state_valid or not row.mapping_valid
               or not row.dependencies_valid or not row.parallel_group_valid
               or not row.outcome_valid or not row.result_valid
               for row in graph.rows)
        or any(not packet.valid for packet in graph.packets)
    ):
        return findings

    rows_by_id = {row.task_id: row for row in graph.rows}
    packets_by_id = {packet.task_id: packet for packet in graph.packets}

    dependency_references_valid = True
    for row in graph.rows:
        for dependency in row.dependencies:
            if dependency == row.task_id:
                dependency_references_valid = False
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"compact Plan task {row.task_id} cannot depend on itself",
                    )
                )
            elif dependency not in rows_by_id:
                dependency_references_valid = False
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"compact Plan task {row.task_id} depends on missing task {dependency}",
                    )
                )

    if dependency_references_valid:
        dependency_map = {
            row.task_id: row.dependencies
            for row in graph.rows
        }
        visit_state: dict[str, int] = {}
        visit_stack: list[str] = []
        reported_cycles: set[tuple[str, ...]] = set()

        def visit(task_id: str) -> None:
            visit_state[task_id] = 1
            visit_stack.append(task_id)
            for dependency in dependency_map[task_id]:
                state = visit_state.get(dependency, 0)
                if state == 0:
                    visit(dependency)
                elif state == 1:
                    start = visit_stack.index(dependency)
                    cycle = tuple((*visit_stack[start:], dependency))
                    cycle_nodes = cycle[:-1]
                    first = min(cycle_nodes)
                    first_index = cycle_nodes.index(first)
                    canonical = tuple(
                        (*cycle_nodes[first_index:], *cycle_nodes[:first_index], first)
                    )
                    if canonical not in reported_cycles:
                        reported_cycles.add(canonical)
                        findings.append(
                            DoctorFinding(
                                "error",
                                relative,
                                f"compact Plan task {first} is part of dependency cycle: {' -> '.join(canonical)}",
                            )
                        )
            visit_stack.pop()
            visit_state[task_id] = 2

        for task_id in sorted(dependency_map):
            if visit_state.get(task_id, 0) == 0:
                visit(task_id)

        if not reported_cycles:
            for row in graph.rows:
                if row.state not in {"ready", "in-progress", "verifying", "complete"}:
                    continue
                incomplete = [
                    dependency
                    for dependency in row.dependencies
                    if rows_by_id[dependency].result != "complete"
                ]
                if not incomplete:
                    continue
                role = _strict_packet_value(packets_by_id[row.task_id], "Role").casefold()
                if role == "verification":
                    detail = (
                        f"verification task {row.task_id} must remain blocked until integration dependencies complete"
                    )
                else:
                    detail = (
                        f"compact Plan task {row.task_id} must remain blocked until dependencies complete"
                    )
                findings.append(DoctorFinding("error", relative, detail))

    role_by_id: dict[str, str] = {}
    delegate_by_id: dict[str, str] = {}
    parent_by_id: dict[str, str] = {}
    packet_semantics_valid = True
    for packet in graph.packets:
        task_id = packet.task_id
        role_raw = _strict_packet_value(packet, "Role")
        role = _STRICT_ROLE_BY_CASEFOLD.get(role_raw.casefold())
        if role is None:
            packet_semantics_valid = False
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan Task Packet {task_id} has invalid Role '{role_raw}'; expected one of {', '.join(_STRICT_ROLES)}",
                )
            )
        else:
            role_by_id[task_id] = role

        delegate_raw = _strict_packet_value(packet, "May delegate")
        delegate = delegate_raw.casefold()
        if delegate not in {"yes", "no"}:
            packet_semantics_valid = False
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan Task Packet {task_id} has invalid May delegate '{delegate_raw}'; expected yes or no",
                )
            )
        else:
            delegate_by_id[task_id] = delegate

        parent = _strict_packet_value(packet, "Parent")
        if parent != "none" and TASK_ID_PATTERN.fullmatch(parent) is None:
            packet_semantics_valid = False
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan Task Packet {task_id} has invalid Parent '{parent or 'missing'}'; expected none or an exact Task ID",
                )
            )
        else:
            parent_by_id[task_id] = parent

    if not packet_semantics_valid:
        return findings

    parent_graph_valid = True
    for task_id in sorted(parent_by_id):
        parent = parent_by_id[task_id]
        expected = _strict_lexical_parent(task_id)
        if expected is None:
            if parent != "none":
                parent_graph_valid = False
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"compact Plan Task Packet {task_id} is a root packet and Parent must be none",
                    )
                )
            continue
        if parent == "none" or parent != expected:
            parent_graph_valid = False
            if parent != "none" and parent not in packets_by_id:
                detail = (
                    f"compact Plan Task Packet {task_id} Parent {parent} does not exist "
                    f"and must be exact immediate lexical prefix {expected}"
                )
            else:
                detail = (
                    f"compact Plan Task Packet {task_id} Parent must be exact immediate lexical prefix {expected}"
                )
            findings.append(DoctorFinding("error", relative, detail))
        elif parent not in packets_by_id:
            parent_graph_valid = False
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan Task Packet {task_id} Parent {parent} does not exist",
                )
            )

    if not parent_graph_valid:
        return findings

    children: dict[str, list[str]] = {task_id: [] for task_id in packets_by_id}
    for task_id, parent in parent_by_id.items():
        if parent != "none":
            children[parent].append(task_id)
    descendants: dict[str, tuple[str, ...]] = {}
    for task_id in sorted(children):
        found: list[str] = []
        pending = list(sorted(children[task_id]))
        while pending:
            child = pending.pop(0)
            found.append(child)
            pending[0:0] = sorted(children[child])
        descendants[task_id] = tuple(found)

    for task_id in sorted(role_by_id):
        role = role_by_id[task_id]
        delegate = delegate_by_id[task_id]
        has_descendants = bool(descendants[task_id])
        if role == "Task Owner" or has_descendants:
            if delegate != "yes":
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"compact Plan Task Packet {task_id} with role {role} must declare May delegate yes",
                    )
                )
        if role in {"leaf", "integration", "verification"} and delegate != "no":
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan Task Packet {task_id} with role {role} must declare May delegate no",
                )
            )

    for task_id in sorted(role_by_id):
        role = role_by_id[task_id]
        row = rows_by_id[task_id]
        dependencies = row.dependencies
        if role == "integration":
            if descendants[task_id]:
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"integration task {task_id} must not have descendants",
                    )
                )
            if dependency_references_valid:
                implementation_dependencies = [
                    dependency
                    for dependency in dependencies
                    if role_by_id.get(dependency) in {"leaf", "Task Owner"}
                ]
                if not implementation_dependencies:
                    findings.append(
                        DoctorFinding(
                            "error",
                            relative,
                            f"integration task {task_id} must depend on at least one implementation leaf or Task Owner",
                        )
                    )
                for dependency in dependencies:
                    if role_by_id.get(dependency) == "verification":
                        findings.append(
                            DoctorFinding(
                                "error",
                                relative,
                                f"integration task {task_id} must not depend on verification task {dependency}",
                            )
                        )
                parent = parent_by_id[task_id]
                if parent != "none":
                    required_siblings = [
                        sibling
                        for sibling in sorted(role_by_id)
                        if sibling != task_id
                        and parent_by_id[sibling] == parent
                        and role_by_id[sibling] in {"leaf", "Task Owner"}
                    ]
                    for sibling in required_siblings:
                        if sibling not in dependencies:
                            findings.append(
                                DoctorFinding(
                                    "error",
                                    relative,
                                    f"integration task {task_id} must depend on same-parent implementation sibling {sibling}",
                                )
                            )
        elif role == "verification":
            if descendants[task_id]:
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"verification task {task_id} must not have descendants",
                    )
                )
            if dependency_references_valid:
                integration_dependencies = [
                    dependency
                    for dependency in dependencies
                    if role_by_id.get(dependency) == "integration"
                ]
                if not integration_dependencies:
                    findings.append(
                        DoctorFinding(
                            "error",
                            relative,
                            f"verification task {task_id} must directly depend on at least one integration candidate",
                        )
                    )
                for dependency in dependencies:
                    if role_by_id.get(dependency) != "integration":
                        findings.append(
                            DoctorFinding(
                                "error",
                                relative,
                                f"verification task {task_id} may directly depend only on integration task {dependency}",
                            )
                        )
        if row.state == "verifying" and role != "verification":
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"compact Plan task {task_id} may use State verifying only with verification Role",
                )
            )

    return findings


def _plan_findings(root: Path) -> list[DoctorFinding]:
    findings: list[DoctorFinding] = []
    seen: dict[str, str] = {}
    for directory, allowed in (
        (Path("docs/exec-plans/active"), ACTIVE_PLAN_STATES),
        (Path("docs/exec-plans/completed"), TERMINAL_PLAN_STATES),
    ):
        target = root / directory
        if symlink_component(target) is not None:
            findings.append(DoctorFinding("error", directory.as_posix(), "Plan directory is behind a symlink"))
            continue
        if not target.exists():
            findings.append(DoctorFinding("error", directory.as_posix(), "required Plan directory is missing"))
            continue
        if not target.is_dir():
            findings.append(DoctorFinding("error", directory.as_posix(), "Plan path is not a directory"))
            continue
        for path in sorted(target.glob("*.md")):
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or not path.is_file():
                findings.append(DoctorFinding("error", relative, "Plan path is not a regular non-symlink file"))
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                findings.append(DoctorFinding("error", relative, "Plan file could not be read as UTF-8"))
                continue
            metadata = _parse_frontmatter(text)
            plan_id = metadata.get("id", "")
            status = metadata.get("status", "").casefold()
            if not plan_id:
                findings.append(DoctorFinding("error", relative, "Plan frontmatter is missing id"))
            elif plan_id in seen:
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"duplicate Plan id also used by {seen[plan_id]}",
                    )
                )
            else:
                seen[plan_id] = relative
            if status not in allowed:
                expected = ", ".join(sorted(allowed))
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"Plan status '{status or 'missing'}' is invalid for this directory; expected one of {expected}",
                    )
                )

            plan_format = metadata.get("format", "")
            compact_signature = _has_compact_plan_signature(text)
            strict_compact = plan_format == "2"
            if compact_signature and plan_format != "2":
                if "format" not in metadata:
                    detail = "compact Plan is missing required format: 2"
                else:
                    detail = (
                        f"compact Plan format '{plan_format or 'empty'}' is invalid; expected 2"
                    )
                findings.append(DoctorFinding("error", relative, detail))
                strict_compact = True
            elif "format" in metadata and plan_format != "2":
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"Plan format '{plan_format or 'empty'}' is invalid; expected 2",
                    )
                )

            if strict_compact:
                findings.extend(
                    _compact_plan_structure_findings(
                        relative=relative,
                        text=text,
                        metadata=metadata,
                        status=status,
                    )
                )
                if plan_format == "2" and "task_graph" in metadata:
                    task_graph_marker = metadata["task_graph"]
                    if task_graph_marker != "1":
                        findings.append(
                            DoctorFinding(
                                "error",
                                relative,
                                f"Plan task_graph marker '{task_graph_marker or 'empty'}' is invalid; expected 1",
                            )
                        )
                    else:
                        findings.extend(
                            _strict_task_graph_findings(
                                relative=relative,
                                text=text,
                            )
                        )
            elif "format" not in metadata:
                if directory.name == "completed":
                    detail = (
                        "historical pre-format grandfathered expanded Plan remains readable "
                        "without rewriting"
                    )
                else:
                    detail = (
                        "active pre-format expanded Plan remains readable; reconcile it to "
                        "format: 2 before relying on compact-schema validation"
                    )
                findings.append(DoctorFinding("warning", relative, detail))
    return findings


STRONG_CLAUSE_SEPARATOR = re.compile(
    r";\s*|[.!?](?:\s+|$)|\b(?:but|however|whereas|while)\b",
    re.IGNORECASE,
)
WEAK_CLAUSE_SEPARATOR = re.compile(
    r",(?:\s*(?:and|or|nor)\b)?\s*|\b(?:and|or|nor)\b",
    re.IGNORECASE,
)
LOCAL_NEGATION = re.compile(
    r"\b(?:cannot|did not|do not|does not|historical|never|no|no longer|not|obsolete|"
    r"remove|removed|retire|retired|should not|superseded|unsupported|without)\b",
    re.IGNORECASE,
)
CLAUSE_PREDICATE = re.compile(
    r"\b(?:am|are|be|been|being|can|cannot|could|did|do|does|had|has|have|is|may|"
    r"might|must|remain|remains|shall|should|use|uses|used|was|were|will|would)\b",
    re.IGNORECASE,
)


def _strong_clause_bounds(line: str, start: int, end: int) -> tuple[int, int]:
    clause_start = 0
    clause_end = len(line)
    for separator in STRONG_CLAUSE_SEPARATOR.finditer(line):
        if separator.end() <= start:
            clause_start = separator.end()
        elif separator.start() >= end:
            clause_end = separator.start()
            break
    return clause_start, clause_end


def _weak_clause_spans(line: str, start: int, end: int) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    cursor = start
    for separator in WEAK_CLAUSE_SEPARATOR.finditer(line, start, end):
        spans.append((cursor, separator.start()))
        cursor = separator.end()
    spans.append((cursor, end))
    return spans


def _match_is_negated(line: str, start: int, end: int) -> bool:
    clause_start, clause_end = _strong_clause_bounds(line, start, end)
    spans = _weak_clause_spans(line, clause_start, clause_end)
    match_index = next(
        (
            index
            for index, (segment_start, segment_end) in enumerate(spans)
            if segment_start <= start and end <= segment_end
        ),
        None,
    )
    if match_index is None:
        return False

    local_start, local_end = spans[match_index]
    local = line[local_start:local_end]
    if LOCAL_NEGATION.search(local) is not None:
        return True
    if CLAUSE_PREDICATE.search(local) is not None:
        return False

    for previous_start, previous_end in reversed(spans[:match_index]):
        previous = line[previous_start:previous_end]
        if not previous.strip():
            continue
        if LOCAL_NEGATION.search(previous) is not None:
            return True
        if CLAUSE_PREDICATE.search(previous) is not None:
            return False
    return False


def _current_authority_findings(root: Path) -> list[DoctorFinding]:
    findings: list[DoctorFinding] = []
    for relative, required_headings in CURRENT_AUTHORITY_REQUIREMENTS.items():
        path = root / relative
        if symlink_component(path) is not None or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    "current authority could not be read as UTF-8",
                )
            )
            continue
        for heading in required_headings:
            if not re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE):
                findings.append(
                    DoctorFinding(
                        "error",
                        relative,
                        f"current authority is missing required structure: {heading}",
                    )
                )
        for line in text.splitlines():
            for pattern, detail in RETIRED_CURRENT_PATTERNS:
                for match in pattern.finditer(line):
                    if not _match_is_negated(line, match.start(), match.end()):
                        findings.append(DoctorFinding("warning", relative, detail))
    return findings


def _looks_like_legacy_harness_config(path: Path) -> bool:
    if path.is_symlink() or not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    return (
        "version = 1" in text
        and "[project]" in text
        and "[commands]" in text
        and "[paths]" in text
    )


def _legacy_surface_findings(root: Path) -> list[DoctorFinding]:
    findings: list[DoctorFinding] = []
    for relative in LEGACY_MANAGED_FILES:
        path = root / relative
        if is_managed_file(path):
            findings.append(
                DoctorFinding(
                    "warning",
                    relative,
                    "managed legacy 0.2 surface exists and requires explicit previewed migration",
                )
            )

    config = root / "dev/harness.toml"
    if _looks_like_legacy_harness_config(config):
        findings.append(
            DoctorFinding(
                "warning",
                "dev/harness.toml",
                "legacy 0.2 harness configuration exists and requires explicit previewed migration",
            )
        )

    for relative in LEGACY_RUNTIME_PATHS:
        path = root / relative
        if path.exists() or path.is_symlink():
            detail = (
                "retained legacy run evidence exists; doctor does not read or delete its contents"
                if relative == ".harness/runs"
                else "legacy 0.2 runtime path exists and requires explicit previewed migration"
            )
            findings.append(DoctorFinding("warning", relative, detail))
    return findings


def _doctor_skill_findings(
    root: Path,
    relative: str,
    *,
    missing_detail: str,
) -> list[DoctorFinding]:
    findings: list[DoctorFinding] = []
    path = root / relative
    if symlink_component(path) is not None or _non_directory_parent(path) is not None:
        return [DoctorFinding("error", relative, "Claude Skill path is unsafe")]
    if not path.exists():
        return [DoctorFinding("warning", relative, missing_detail)]
    if not path.is_file():
        return [DoctorFinding("error", relative, "Claude Skill is not a regular file")]
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return [DoctorFinding("error", relative, "Claude Skill could not be read as UTF-8")]

    name = Path(relative).parent.name
    if not text.startswith("---\n"):
        findings.append(
            DoctorFinding(
                "error",
                relative,
                "Skill YAML frontmatter must start on line one",
            )
        )
    metadata = _parse_frontmatter(text)
    declared_name = metadata.get("name", "")
    if declared_name != name:
        findings.append(
            DoctorFinding(
                "error",
                relative,
                "Skill name must match its parent directory",
            )
        )
    if (
        not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", declared_name)
        or len(declared_name) > 64
    ):
        findings.append(
            DoctorFinding(
                "error",
                relative,
                "Skill name must use lowercase letters, digits, and single hyphens",
            )
        )
    description = metadata.get("description", "")
    if not description:
        findings.append(
            DoctorFinding("error", relative, "Skill description is required")
        )
    elif "use when" not in description.casefold():
        findings.append(
            DoctorFinding(
                "error",
                relative,
                "Skill description must state when to use it",
            )
        )
    for forbidden in ("allowed-tools", "hooks", "shell"):
        if forbidden in metadata:
            findings.append(
                DoctorFinding(
                    "error",
                    relative,
                    f"Skill must not declare privilege-bearing {forbidden} frontmatter",
                )
            )
    return findings


def doctor_document_first(root: Path) -> DoctorReport:
    root = validate_root(root)
    findings: list[DoctorFinding] = []
    for relative in REQUIRED_DOCUMENT_FIRST_PATHS:
        path = root / relative
        component = symlink_component(path)
        if component is not None:
            findings.append(DoctorFinding("error", relative, "required path is behind a symlink"))
        elif not path.exists():
            findings.append(DoctorFinding("error", relative, "required document-first path is missing"))
        elif relative in REQUIRED_DOCUMENT_FIRST_DIRECTORIES and not path.is_dir():
            findings.append(DoctorFinding("error", relative, "required Plan path is not a directory"))
        elif relative not in REQUIRED_DOCUMENT_FIRST_DIRECTORIES and not path.is_file():
            findings.append(DoctorFinding("error", relative, "required path is not a regular file"))

    agents_path = root / "AGENTS.md"
    if agents_path.is_file() and not agents_path.is_symlink():
        try:
            agents_text = agents_path.read_text(encoding="utf-8")
            marker_counts = (
                agents_text.count(AGENTS_START),
                agents_text.count(AGENTS_END),
            )
            if marker_counts != (1, 1):
                findings.append(
                    DoctorFinding(
                        "error",
                        "AGENTS.md",
                        "canonical instructions must contain one complete bounded Reporivet block",
                    )
                )
        except (OSError, UnicodeError):
            findings.append(DoctorFinding("error", "AGENTS.md", "canonical instructions could not be read as UTF-8"))

    if (root / "docs/RELIABILITY.md").exists():
        findings.append(
            DoctorFinding(
                "warning",
                "docs/RELIABILITY.md",
                "existing reliability authority is preserved but must be reconciled with docs/OPERATIONS.md",
            )
        )

    claude = root / "CLAUDE.md"
    if symlink_component(claude) is not None or _non_directory_parent(claude) is not None:
        findings.append(DoctorFinding("error", "CLAUDE.md", "Claude adapter path is unsafe"))
    elif claude.exists():
        if not claude.is_file():
            findings.append(DoctorFinding("error", "CLAUDE.md", "Claude adapter is not a regular file"))
        else:
            try:
                content = claude.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                findings.append(DoctorFinding("error", "CLAUDE.md", "Claude adapter could not be read as UTF-8"))
            else:
                if content != "@AGENTS.md\n":
                    findings.append(
                        DoctorFinding(
                            "warning",
                            "CLAUDE.md",
                            "existing Claude instructions are project-owned; the thin adapter form is exactly @AGENTS.md",
                        )
                    )
    else:
        findings.append(DoctorFinding("info", "CLAUDE.md", "optional Claude adapter is not installed"))

    for relative in CLAUDE_PROFILE_ASSETS:
        if relative == "CLAUDE.md":
            continue
        findings.extend(
            _doctor_skill_findings(
                root,
                relative,
                missing_detail="optional default Claude role Skill is not installed",
            )
        )

    settings = root / ".claude/settings.json"
    if symlink_component(settings) is not None or _non_directory_parent(settings) is not None:
        findings.append(DoctorFinding("error", ".claude/settings.json", "project settings path is unsafe"))
    elif settings.exists():
        if not settings.is_file():
            findings.append(DoctorFinding("error", ".claude/settings.json", "project settings are not a regular file"))
        else:
            try:
                parsed = json.loads(settings.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                findings.append(DoctorFinding("error", ".claude/settings.json", "project settings are not valid strict JSON"))
            else:
                expected = json.loads(
                    read_asset("document-first/optional/claude-settings.deny-only.json.tmpl")
                )
                if parsed == expected:
                    findings.append(
                        DoctorFinding(
                            "info",
                            ".claude/settings.json",
                            "reviewed Reporivet deny-only template is installed; it is defense in depth, not a sandbox",
                        )
                    )
                else:
                    findings.append(
                        DoctorFinding(
                            "info",
                            ".claude/settings.json",
                            "project-owned Claude settings are preserved and are not claimed as Reporivet policy",
                        )
                    )
    else:
        findings.append(
            DoctorFinding(
                "info",
                ".claude/settings.json",
                "live Claude settings are intentionally absent by default",
            )
        )

    draft_path = root / DEFINITION_DRAFT_PATH
    if symlink_component(draft_path) is not None or _non_directory_parent(draft_path) is not None:
        findings.append(DoctorFinding("error", DEFINITION_DRAFT_PATH.as_posix(), "definition draft path is unsafe"))
    elif draft_path.exists():
        if not draft_path.is_file():
            findings.append(DoctorFinding("error", DEFINITION_DRAFT_PATH.as_posix(), "definition draft is not a regular file"))
        else:
            try:
                draft = parse_definition_draft(
                    draft_path.read_text(encoding="utf-8")
                )
            except (OSError, UnicodeError, InitError) as exc:
                findings.append(
                    DoctorFinding(
                        "error",
                        DEFINITION_DRAFT_PATH.as_posix(),
                        str(exc),
                    )
                )
            else:
                procedure_plan = build_procedure_skill_plan(
                    draft.evidence["procedures"].confirmed
                )
                for diagnostic in procedure_plan.diagnostics:
                    findings.append(
                        DoctorFinding(
                            "warning",
                            diagnostic.path,
                            "procedure record is not Skill-eligible "
                            f"({diagnostic.code}): {diagnostic.detail}",
                        )
                    )
                for target in procedure_plan.targets:
                    findings.extend(
                        _doctor_skill_findings(
                            root,
                            target.path,
                            missing_detail=(
                                "optional confirmed procedure Skill is not installed"
                            ),
                        )
                    )

    plan_template = root / "docs/exec-plans/_template.md"
    if plan_template.is_file() and not plan_template.is_symlink():
        try:
            template_text = plan_template.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            findings.append(DoctorFinding("error", "docs/exec-plans/_template.md", "Plan template could not be read as UTF-8"))
        else:
            if _parse_frontmatter(template_text).get("format") != "2":
                findings.append(
                    DoctorFinding(
                        "error",
                        "docs/exec-plans/_template.md",
                        "compact Plan template must declare format: 2",
                    )
                )
            for heading in COMPACT_PLAN_HEADINGS:
                if not re.search(rf"^{re.escape(heading)}\s*$", template_text, re.MULTILINE):
                    findings.append(
                        DoctorFinding(
                            "error",
                            "docs/exec-plans/_template.md",
                            f"compact Plan template is missing {heading[3:]}",
                        )
                    )
            if not re.search(r"^\| Task \| Owner \|", template_text, re.MULTILINE):
                findings.append(
                    DoctorFinding(
                        "error",
                        "docs/exec-plans/_template.md",
                        "compact Plan template task table is missing the Owner column",
                    )
                )
            if not re.search(r"^- \*\*Owner:\*\*", template_text, re.MULTILINE):
                findings.append(
                    DoctorFinding(
                        "error",
                        "docs/exec-plans/_template.md",
                        "compact Plan template Task Packet is missing Owner",
                    )
                )
            for retired in (
                "verification_run:",
                "manifest_sha256:",
                "gate_verdict:",
                "Gate verdict",
                ".harness/runs",
                "./dev/",
            ):
                if retired in template_text:
                    findings.append(
                        DoctorFinding(
                            "error",
                            "docs/exec-plans/_template.md",
                            f"compact Plan template contains retired field or path: {retired}",
                        )
                    )

    findings.extend(_plan_findings(root))
    findings.extend(_current_authority_findings(root))
    findings.extend(_legacy_surface_findings(root))

    unique = {
        (finding.severity, finding.path, finding.detail): finding
        for finding in findings
    }
    ordered = tuple(
        unique[key]
        for key in sorted(unique, key=lambda value: (value[1], value[0], value[2]))
    )
    return DoctorReport(ordered)


def run_document_first_doctor(root: Path) -> int:
    report = doctor_document_first(root)
    print(report.render(), end="")
    return 2 if report.errors else 0
