#!/usr/bin/env python3
# project-harness:managed version={{HARNESS_VERSION}}
"""Repository-local entrypoints for agent-readable context, plans, checks, and verification."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "dev" / "harness.toml"
CATALOG_START = "<!-- project-harness:catalog:start -->"
CATALOG_END = "<!-- project-harness:catalog:end -->"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
TITLE_LINE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
TASK_HEADING = re.compile(r"^###\s+(T[0-9A-Za-z_-]+)\s*(?:—|-)\s*(.+)$", re.MULTILINE)
PLAN_ID_PATTERN = re.compile(r"PLAN-(?:\d{4}-)?(\d{4})")
PLACEHOLDER = "TODO"
REQUIRED_DOCS = (
    Path("AGENTS.md"),
    Path("ARCHITECTURE.md"),
    Path("docs/README.md"),
    Path("docs/PRODUCT.md"),
    Path("docs/DESIGN.md"),
    Path("docs/QUALITY.md"),
    Path("docs/SECURITY.md"),
    Path("docs/PLANS.md"),
    Path("docs/product-specs/index.md"),
    Path("docs/product-specs/_template.md"),
    Path("docs/design-docs/index.md"),
    Path("docs/design-docs/_template.md"),
    Path("docs/design-docs/core-beliefs.md"),
    Path("docs/exec-plans/_template.md"),
    Path("docs/exec-plans/tech-debt-tracker.md"),
    Path("docs/decisions/README.md"),
    Path("docs/decisions/_template.md"),
    Path("docs/runbooks/index.md"),
    Path("docs/runbooks/_template.md"),
    Path("docs/generated/README.md"),
    Path("docs/references/README.md"),
    Path("dev/harness.toml"),
)
CATALOG_AREAS = {
    "product-specs": "product-spec",
    "design-docs": "design-doc",
    "decisions": "decision",
    "runbooks": "runbook",
}
VALID_STATUSES = {
    "product-spec": {"draft", "active", "deprecated", "superseded"},
    "design-doc": {"draft", "active", "deprecated", "superseded"},
    "decision": {"proposed", "accepted", "rejected", "superseded"},
    "runbook": {"draft", "active", "deprecated"},
}
ACTIVE_PLAN_STATES = {"proposed", "approved", "in-progress", "verifying", "blocked"}
COMPLETED_PLAN_STATES = {"complete", "cancelled", "superseded"}
PLAN_REQUIRED_HEADINGS = (
    "Purpose / Big Picture",
    "Progress",
    "Context and Orientation",
    "Scope",
    "Non-goals",
    "Acceptance Criteria",
    "Milestones",
    "Task Packets",
    "Architecture Impact",
    "Documentation Impact",
    "Interfaces and Dependencies",
    "Migration, Rollout, and Recovery",
    "Surprises and Discoveries",
    "Decision Log",
    "Concrete Steps",
    "Validation and Evidence",
    "Outcomes and Retrospective",
    "Follow-ups",
)
TASK_REQUIRED_LABELS = (
    "State",
    "Depends on",
    "Outcome",
    "Non-goals",
    "Read",
    "Allowed writes",
    "Protected paths",
    "Acceptance",
    "Verify",
    "Stop conditions",
    "Result",
)


class HarnessError(RuntimeError):
    """Raised for deterministic harness failures."""


@dataclass(frozen=True)
class DurableDocument:
    path: Path
    id: str
    kind: str
    status: str
    area: str
    summary: str
    applies_to: tuple[str, ...]


@dataclass(frozen=True)
class Plan:
    path: Path
    metadata: dict[str, object]
    text: str

    @property
    def id(self) -> str:
        return str(self.metadata.get("id", self.path.stem))

    @property
    def status(self) -> str:
        return str(self.metadata.get("status", "missing")).lower()

    @property
    def title(self) -> str:
        match = TITLE_LINE.search(self.text)
        return match.group(1).strip() if match else self.path.stem


@dataclass
class Config:
    raw: dict[str, object]

    @property
    def project(self) -> dict[str, object]:
        value = self.raw.get("project", {})
        return value if isinstance(value, dict) else {}

    @property
    def commands(self) -> dict[str, object]:
        value = self.raw.get("commands", {})
        return value if isinstance(value, dict) else {}

    @property
    def paths(self) -> dict[str, object]:
        value = self.raw.get("paths", {})
        return value if isinstance(value, dict) else {}

    @property
    def policy(self) -> dict[str, object]:
        value = self.raw.get("policy", {})
        return value if isinstance(value, dict) else {}

    @property
    def baseline(self) -> str:
        return str(self.project.get("baseline", "draft")).lower()

    @property
    def lifecycle(self) -> str:
        return "active" if self.baseline == "established" else "bootstrap"

    @property
    def configuration(self) -> str:
        return str(self.project.get("configuration", "review")).lower()

    def command_group(self, name: str) -> list[list[str]]:
        value = self.commands.get(name, [])
        if not isinstance(value, list):
            raise HarnessError(f"[commands].{name} must be an array of command arrays")
        result: list[list[str]] = []
        for index, command in enumerate(value):
            if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
                raise HarnessError(f"[commands].{name}[{index}] must be a non-empty array of strings")
            result.append(list(command))
        return result

    def list_value(self, section: str, name: str) -> list[str]:
        source = {"paths": self.paths, "policy": self.policy}.get(section, {})
        value = source.get(name, []) if isinstance(source, dict) else []
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise HarnessError(f"[{section}].{name} must be an array of strings")
        return list(value)


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        raise HarnessError(f"missing deterministic configuration: {CONFIG_PATH.relative_to(ROOT)}")
    try:
        with CONFIG_PATH.open("rb") as handle:
            raw = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise HarnessError(f"cannot read {CONFIG_PATH.relative_to(ROOT)}: {exc}") from exc
    if raw.get("version") != 1:
        raise HarnessError("unsupported dev/harness.toml version; expected version = 1")
    config = Config(raw)
    if config.baseline not in {"draft", "established"}:
        raise HarnessError("[project].baseline must be 'draft' or 'established'")
    if config.configuration not in {"ready", "review"}:
        raise HarnessError("[project].configuration must be 'ready' or 'review'")
    return config


def parse_scalar(value: str) -> object:
    value = value.strip()
    if not value:
        return ""
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("\"'") for part in inner.split(",") if part.strip()]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value.strip("\"'")


def parse_frontmatter_text(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text
    closing = text.find("\n---\n", 4)
    if closing == -1:
        return {}, text
    block = text[4:closing]
    body = text[closing + 5 :]
    data: dict[str, object] = {}
    current_list: str | None = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  - ") and current_list:
            existing = data.setdefault(current_list, [])
            if isinstance(existing, list):
                existing.append(raw[4:].strip().strip("\"'"))
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        data[key] = parse_scalar(value)
        current_list = key if value.strip() == "" else None
    return data, body


def read_frontmatter(path: Path) -> tuple[dict[str, object], str, str]:
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter_text(text)
    return metadata, body, text


def update_frontmatter(text: str, updates: dict[str, str]) -> str:
    metadata, body = parse_frontmatter_text(text)
    if not metadata:
        raise HarnessError("cannot update a document without frontmatter")
    lines = text[4 : text.find("\n---\n", 4)].splitlines()
    handled: set[str] = set()
    output: list[str] = []
    for line in lines:
        if ":" not in line or line.startswith("  - "):
            output.append(line)
            continue
        key = line.split(":", 1)[0].strip()
        if key in updates:
            output.append(f"{key}: {updates[key]}")
            handled.add(key)
        else:
            output.append(line)
    for key, value in updates.items():
        if key not in handled:
            output.append(f"{key}: {value}")
    return "---\n" + "\n".join(output) + "\n---\n" + body


def heading_present(text: str, heading: str) -> bool:
    return re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE) is not None


def section_text(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        return ""
    tail = text[match.end() :]
    boundary = re.search(r"^##\s+", tail, re.MULTILINE)
    return tail[: boundary.start() if boundary else len(tail)].strip()


def normalize_link_target(raw_target: str) -> str:
    target = raw_target.strip().split("#", 1)[0].split("?", 1)[0]
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return target


def is_historical_plan(path: Path) -> bool:
    try:
        path.relative_to(ROOT / "docs" / "exec-plans" / "completed")
        return True
    except ValueError:
        return False


def check_links(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    historical = is_historical_plan(path)
    for raw_target in MARKDOWN_LINK.findall(text):
        target = normalize_link_target(raw_target)
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if historical:
            suffix = Path(target).suffix.lower()
            is_document_reference = suffix in {".md", ".txt"} or target.startswith(("/docs/", "docs/"))
            if not is_document_reference:
                continue
        candidate = (ROOT / target.lstrip("/")) if target.startswith("/") else (path.parent / target)
        candidate = candidate.resolve()
        try:
            candidate.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {raw_target}")
            continue
        if not candidate.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing link target: {raw_target}")


def durable_documents(errors: list[str] | None = None) -> list[DurableDocument]:
    sink = errors if errors is not None else []
    documents: list[DurableDocument] = []
    seen_ids: dict[str, Path] = {}
    for directory, expected_kind in CATALOG_AREAS.items():
        base = ROOT / "docs" / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name in {"README.md", "index.md", "_template.md"}:
                continue
            metadata, _, _ = read_frontmatter(path)
            required = ("id", "kind", "status", "area", "summary")
            missing = [name for name in required if not str(metadata.get(name, "")).strip()]
            if missing:
                sink.append(f"{path.relative_to(ROOT)}: missing frontmatter fields: {', '.join(missing)}")
                continue
            doc_id = str(metadata["id"])
            kind = str(metadata["kind"])
            status = str(metadata["status"]).lower()
            if kind != expected_kind:
                sink.append(f"{path.relative_to(ROOT)}: kind must be '{expected_kind}', got '{kind}'")
            if status not in VALID_STATUSES.get(kind, set()):
                sink.append(f"{path.relative_to(ROOT)}: invalid status '{status}' for kind '{kind}'")
            if doc_id in seen_ids:
                sink.append(f"{path.relative_to(ROOT)}: duplicate id '{doc_id}' also used by {seen_ids[doc_id].relative_to(ROOT)}")
            else:
                seen_ids[doc_id] = path
            applies = metadata.get("applies_to", [])
            if isinstance(applies, str):
                applies_list = (applies,)
            elif isinstance(applies, list):
                applies_list = tuple(str(item) for item in applies)
            else:
                applies_list = ()
            documents.append(
                DurableDocument(
                    path=path,
                    id=doc_id,
                    kind=kind,
                    status=status,
                    area=str(metadata["area"]),
                    summary=str(metadata["summary"]),
                    applies_to=applies_list,
                )
            )
    return documents


def relative_markdown_link(from_path: Path, to_path: Path) -> str:
    return os.path.relpath(to_path, from_path.parent).replace(os.sep, "/")


CATALOG_LABELS = {
    "product-spec": "Product specifications",
    "design-doc": "Design documents",
    "decision": "Decisions",
    "runbook": "Runbooks",
}


def catalog_markdown(
    documents: Sequence[DurableDocument],
    *,
    from_path: Path,
    kinds: Sequence[str],
    grouped: bool,
) -> str:
    lines = [CATALOG_START, "", "Generated by `./dev/docs-index`. Do not edit this block manually."]
    for kind in kinds:
        matching = sorted((doc for doc in documents if doc.kind == kind), key=lambda doc: (doc.area, doc.id))
        if grouped:
            lines.extend(("", f"### {CATALOG_LABELS[kind]}", ""))
        else:
            lines.append("")
        if not matching:
            lines.append("- None.")
            continue
        lines.extend(("| ID | Status | Area | Summary | Document |", "|---|---|---|---|---|"))
        for doc in matching:
            link = relative_markdown_link(from_path, doc.path)
            summary = doc.summary.replace("|", "\\|")
            lines.append(f"| `{doc.id}` | {doc.status} | {doc.area} | {summary} | [`{doc.path.name}`]({link}) |")
    lines.extend(("", CATALOG_END))
    return "\n".join(lines)


def replace_catalog(text: str, block: str, *, path: Path) -> str:
    start = text.find(CATALOG_START)
    end = text.find(CATALOG_END)
    if start == -1 or end == -1 or end < start:
        raise HarnessError(f"{path.relative_to(ROOT)} is missing project-harness catalog markers")
    end += len(CATALOG_END)
    return text[:start].rstrip() + "\n\n" + block.rstrip() + "\n" + text[end:].lstrip("\n")


def catalog_targets() -> list[tuple[Path, tuple[str, ...], bool]]:
    return [
        (ROOT / "docs" / "README.md", tuple(CATALOG_LABELS), True),
        (ROOT / "docs" / "product-specs" / "index.md", ("product-spec",), False),
        (ROOT / "docs" / "design-docs" / "index.md", ("design-doc",), False),
        (ROOT / "docs" / "decisions" / "README.md", ("decision",), False),
        (ROOT / "docs" / "runbooks" / "index.md", ("runbook",), False),
    ]


def expected_catalog_text(path: Path, documents: Sequence[DurableDocument], kinds: Sequence[str], grouped: bool) -> str:
    if not path.exists():
        raise HarnessError(f"missing catalog target: {path.relative_to(ROOT)}")
    original = path.read_text(encoding="utf-8")
    block = catalog_markdown(documents, from_path=path, kinds=kinds, grouped=grouped)
    return replace_catalog(original, block, path=path)


def command_docs_index(args: argparse.Namespace) -> int:
    errors: list[str] = []
    documents = durable_documents(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise HarnessError(f"cannot build document catalog with {len(errors)} metadata error(s)")
    changed: list[Path] = []
    for path, kinds, grouped in catalog_targets():
        original = path.read_text(encoding="utf-8") if path.exists() else ""
        updated = expected_catalog_text(path, documents, kinds, grouped)
        if updated != original:
            changed.append(path)
            if not args.check:
                path.write_text(updated, encoding="utf-8")
    if args.check and changed:
        names = ", ".join(str(path.relative_to(ROOT)) for path in changed)
        raise HarnessError(f"document catalogs are stale: {names}; run ./dev/docs-index and commit the result")
    if changed:
        print(f"Updated {len(changed)} document catalog(s) ({len(documents)} durable document(s)).")
    else:
        print(f"Document catalogs are current ({len(documents)} durable document(s)).")
    return 0

def plan_files() -> list[Plan]:
    plans: list[Plan] = []
    for directory in (ROOT / "docs" / "exec-plans" / "active", ROOT / "docs" / "exec-plans" / "completed"):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            metadata, _, text = read_frontmatter(path)
            plans.append(Plan(path=path, metadata=metadata, text=text))
    return plans


def locate_plan(reference: str, *, active_only: bool = False) -> Plan:
    candidates = []
    for plan in plan_files():
        if active_only and "active" not in plan.path.relative_to(ROOT).parts:
            continue
        if reference in {plan.id, plan.path.name, plan.path.stem} or reference.lower() in plan.path.name.lower():
            candidates.append(plan)
    if not candidates:
        raise HarnessError(f"plan not found: {reference}")
    if len(candidates) > 1:
        names = ", ".join(str(plan.path.relative_to(ROOT)) for plan in candidates)
        raise HarnessError(f"plan reference is ambiguous: {reference} ({names})")
    return candidates[0]


def task_field(block: str, label: str) -> str | None:
    heading = re.search(rf"^####\s+{re.escape(label)}\s*$", block, re.MULTILINE | re.IGNORECASE)
    if heading:
        tail = block[heading.end() :]
        boundary = re.search(r"^####\s+|^###\s+|^##\s+", tail, re.MULTILINE)
        return tail[: boundary.start() if boundary else len(tail)].strip()
    legacy = re.search(rf"^\*\*{re.escape(label)}:\*\*\s*(.*)$", block, re.MULTILINE | re.IGNORECASE)
    return legacy.group(1).strip() if legacy else None


def validate_task_packets(plan: Plan, errors: list[str], *, strict: bool) -> None:
    matches = list(TASK_HEADING.finditer(plan.text))
    if not matches:
        errors.append(f"{plan.path.relative_to(ROOT)}: no Task Packet headings found")
        return
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        task_id = match.group(1)
        if task_id in blocks:
            errors.append(f"{plan.path.relative_to(ROOT)}: duplicate task id {task_id}")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(plan.text)
        blocks[task_id] = plan.text[match.end() : end]

    dependencies: dict[str, set[str]] = {}
    terminal_plan = plan.status in {"verifying", "complete"}
    for task_id, block in blocks.items():
        fields: dict[str, str] = {}
        for label in TASK_REQUIRED_LABELS:
            value = task_field(block, label)
            if value is None:
                errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: missing '{label}' field")
            else:
                fields[label] = value
        state = fields.get("State", "").splitlines()[0].strip().lower()
        valid_states = {"ready", "blocked", "in-progress", "complete", "failed", "cancelled"}
        if state and state not in valid_states:
            errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: invalid state '{state}'")
        depends_text = fields.get("Depends on", "")
        deps = set(re.findall(r"\bT[0-9A-Za-z_-]+\b", depends_text))
        dependencies[task_id] = deps
        for dependency in deps:
            if dependency not in blocks:
                errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: unknown dependency {dependency}")
        if state == "complete" and fields.get("Result", "").strip().lower() in {"", "pending", "todo"}:
            errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: completed task has no Result evidence")
        if terminal_plan and state not in {"complete", "cancelled"}:
            errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: {plan.status} plan has non-terminal task state '{state}'")
        if strict and plan.status not in {"proposed", "blocked"} and PLACEHOLDER in block:
            errors.append(f"{plan.path.relative_to(ROOT)} {task_id}: unresolved {PLACEHOLDER} marker")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visited:
            return
        if task_id in visiting:
            errors.append(f"{plan.path.relative_to(ROOT)}: cyclic task dependency involving {task_id}")
            return
        visiting.add(task_id)
        for dependency in dependencies.get(task_id, set()):
            if dependency in blocks:
                visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in blocks:
        visit(task_id)

def command_plan_check(args: argparse.Namespace) -> int:
    config = load_config()
    strict = bool(args.strict or config.lifecycle == "active")
    errors: list[str] = []
    plans = plan_files()
    seen_ids: dict[str, Path] = {}
    for plan in plans:
        relative = plan.path.relative_to(ROOT)
        in_active = "active" in relative.parts
        valid = ACTIVE_PLAN_STATES if in_active else COMPLETED_PLAN_STATES
        if not plan.metadata:
            errors.append(f"{relative}: missing frontmatter")
            continue
        for field in (
            "id",
            "kind",
            "status",
            "owner",
            "created",
            "updated",
            "area",
            "base_commit",
            "integrated_commit",
            "verified_commit",
        ):
            if field not in plan.metadata:
                errors.append(f"{relative}: missing frontmatter field '{field}'")
        if str(plan.metadata.get("kind", "")) != "exec-plan":
            errors.append(f"{relative}: kind must be 'exec-plan'")
        if plan.id in seen_ids:
            errors.append(f"{relative}: duplicate plan id {plan.id} also used by {seen_ids[plan.id].relative_to(ROOT)}")
        else:
            seen_ids[plan.id] = plan.path
        if plan.status not in valid:
            errors.append(f"{relative}: status '{plan.status}' invalid for this directory; expected {sorted(valid)}")
        for heading in PLAN_REQUIRED_HEADINGS:
            if not heading_present(plan.text, heading):
                errors.append(f"{relative}: missing section '## {heading}'")
        validate_task_packets(plan, errors, strict=strict and plan.status not in {"proposed", "blocked"})
        if strict and plan.status in {"approved", "in-progress", "verifying", "complete"} and PLACEHOLDER in plan.text:
            errors.append(f"{relative}: unresolved {PLACEHOLDER} marker in {plan.status} plan")
        if plan.status in {"verifying", "complete"}:
            if "- [ ]" in section_text(plan.text, "Progress"):
                errors.append(f"{relative}: {plan.status} plan contains unchecked Progress items")
            for evidence_section in ("Documentation Impact", "Validation and Evidence"):
                if re.search(r"\bpending\b", section_text(plan.text, evidence_section), re.IGNORECASE):
                    errors.append(f"{relative}: {evidence_section} still contains pending work")
            integrated = str(plan.metadata.get("integrated_commit", "")).strip()
            if not integrated:
                errors.append(f"{relative}: {plan.status} plan is missing integrated_commit")
            elif plan.status == "verifying" and integrated == "HEAD":
                pass
            elif not re.fullmatch(r"[0-9a-fA-F]{7,64}", integrated):
                errors.append(f"{relative}: integrated_commit must be HEAD or a Git object id while verifying")
        if plan.status == "complete":
            if "- [ ]" in plan.text:
                errors.append(f"{relative}: complete plan contains unchecked Progress items")
            verified = str(plan.metadata.get("verified_commit", "")).strip()
            if not verified:
                errors.append(f"{relative}: complete plan is missing verified_commit")
            elif not re.fullmatch(r"[0-9a-fA-F]{7,64}", verified):
                errors.append(f"{relative}: verified_commit is not a Git object id")
            integrated = str(plan.metadata.get("integrated_commit", "")).strip()
            if integrated and verified and integrated != verified:
                errors.append(f"{relative}: verified_commit must equal integrated_commit unless the plan explains a re-integration")
    if config.baseline == "established":
        for plan in plans:
            if (
                plan.id == "PLAN-0000"
                and "active" in plan.path.relative_to(ROOT).parts
                and plan.status != "verifying"
            ):
                errors.append(
                    f"{plan.path.relative_to(ROOT)}: established baseline may keep PLAN-0000 active only while verifying"
                )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise HarnessError(f"plan check failed with {len(errors)} error(s)")
    print(f"Plan check passed ({len(plans)} plan(s), strict={strict}).")
    return 0

CORE_DOCUMENT_SCHEMAS = {
    Path("ARCHITECTURE.md"): ("ARCHITECTURE", "architecture"),
    Path("docs/PRODUCT.md"): ("PRODUCT", "product"),
    Path("docs/DESIGN.md"): ("DESIGN", "design"),
    Path("docs/QUALITY.md"): ("QUALITY", "quality"),
    Path("docs/SECURITY.md"): ("SECURITY", "security"),
    Path("docs/RELIABILITY.md"): ("RELIABILITY", "reliability"),
}


def validate_core_documents(errors: list[str], *, strict: bool) -> None:
    for relative, (expected_id, expected_kind) in CORE_DOCUMENT_SCHEMAS.items():
        path = ROOT / relative
        if not path.exists():
            continue
        metadata, _, _ = read_frontmatter(path)
        missing = [field for field in ("id", "kind", "status", "area", "summary") if not str(metadata.get(field, "")).strip()]
        if missing:
            errors.append(f"{relative}: missing frontmatter fields: {', '.join(missing)}")
            continue
        if str(metadata.get("id")) != expected_id:
            errors.append(f"{relative}: id must be '{expected_id}'")
        if str(metadata.get("kind")) != expected_kind:
            errors.append(f"{relative}: kind must be '{expected_kind}'")
        status = str(metadata.get("status", "")).lower()
        if status not in {"draft", "active"}:
            errors.append(f"{relative}: current-state status must be 'draft' or 'active'")
        if strict and status != "active":
            errors.append(f"{relative}: established baseline requires status 'active'")


def command_docs_check(args: argparse.Namespace) -> int:
    config = load_config()
    strict = bool(args.strict or config.lifecycle == "active")
    errors: list[str] = []
    warnings: list[str] = []
    required = list(REQUIRED_DOCS)
    if str(config.project.get("kind", "")).lower() in {"service", "web", "application", "app"}:
        required.extend((Path("docs/RELIABILITY.md"), Path("docs/runbooks/index.md")))
    for relative in required:
        if not (ROOT / relative).exists():
            errors.append(f"missing required file: {relative}")

    documents = durable_documents(errors)
    validate_core_documents(errors, strict=strict)
    agents = ROOT / "AGENTS.md"
    max_lines = int(config.policy.get("agents_max_lines", 140))
    if agents.exists():
        line_count = len(agents.read_text(encoding="utf-8").splitlines())
        if line_count > max_lines:
            warnings.append(f"AGENTS.md is {line_count} lines; configured maximum is {max_lines}")

    for base in (ROOT / "docs", ROOT / "ARCHITECTURE.md", ROOT / "AGENTS.md"):
        if base.is_file():
            check_links(base, errors)
        elif base.is_dir():
            for path in base.rglob("*.md"):
                check_links(path, errors)

    if strict:
        strict_files = [
            ROOT / "AGENTS.md",
            ROOT / "ARCHITECTURE.md",
            ROOT / "docs" / "PRODUCT.md",
            ROOT / "docs" / "DESIGN.md",
            ROOT / "docs" / "QUALITY.md",
            ROOT / "docs" / "SECURITY.md",
        ]
        if (ROOT / "docs" / "RELIABILITY.md").exists():
            strict_files.append(ROOT / "docs" / "RELIABILITY.md")
        for path in strict_files:
            if path.exists() and PLACEHOLDER in path.read_text(encoding="utf-8"):
                errors.append(f"{path.relative_to(ROOT)}: unresolved {PLACEHOLDER} marker in active lifecycle")

    generated = ROOT / "docs" / "generated"
    if generated.exists():
        for path in generated.glob("*.md"):
            if path.name == "README.md":
                continue
            head = "\n".join(path.read_text(encoding="utf-8", errors="ignore").splitlines()[:8])
            if "generated" not in head.lower():
                warnings.append(f"{path.relative_to(ROOT)} does not identify its generator")

    for catalog_path, kinds, grouped in catalog_targets():
        if not catalog_path.exists():
            continue
        original = catalog_path.read_text(encoding="utf-8")
        expected = expected_catalog_text(catalog_path, documents, kinds, grouped)
        if expected != original:
            errors.append(f"{catalog_path.relative_to(ROOT)} catalog is stale; run ./dev/docs-index")

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise HarnessError(f"documentation check failed with {len(errors)} error(s)")
    print(f"Documentation check passed ({len(documents)} durable document(s), {len(warnings)} warning(s), strict={strict}).")
    return 0


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def command_display(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def executable_available(command: Sequence[str]) -> bool:
    executable = command[0]
    if executable.startswith("./") or "/" in executable:
        path = (ROOT / executable).resolve() if not Path(executable).is_absolute() else Path(executable)
        return path.exists() and os.access(path, os.X_OK)
    return shutil.which(executable) is not None


def execute_group(name: str, commands: Sequence[Sequence[str]], *, allow_empty: bool = False) -> int:
    if not commands:
        if allow_empty:
            print(f"No commands configured for '{name}'.")
            return 0
        raise HarnessError(f"no deterministic commands configured for [commands].{name}")
    run_dir = ROOT / ".harness" / "runs" / f"{utc_timestamp()}-{name}"
    run_dir.mkdir(parents=True, exist_ok=True)
    summary: list[dict[str, object]] = []
    for index, command in enumerate(commands, start=1):
        if not executable_available(command):
            raise HarnessError(f"configured executable is unavailable: {command[0]}; run ./dev/bootstrap or fix dev/harness.toml")
        printable = command_display(command)
        print(f"\n$ {printable}")
        log_path = run_dir / f"{index:02d}.log"
        started = datetime.now(timezone.utc)
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                list(command),
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert process.stdout is not None
            for line in process.stdout:
                print(line, end="")
                log.write(line)
            returncode = process.wait()
        finished = datetime.now(timezone.utc)
        summary.append(
            {
                "command": list(command),
                "returncode": returncode,
                "started": started.isoformat(),
                "finished": finished.isoformat(),
                "log": str(log_path.relative_to(ROOT)),
            }
        )
        if returncode != 0:
            (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            raise HarnessError(f"command failed with exit code {returncode}: {printable}")
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n{name} passed. Raw logs: {run_dir.relative_to(ROOT)}")
    return 0


def command_bootstrap(_: argparse.Namespace) -> int:
    config = load_config()
    return execute_group("bootstrap", config.command_group("bootstrap"), allow_empty=True)


def command_run(_: argparse.Namespace) -> int:
    return execute_group("run", load_config().command_group("run"))


def command_smoke(_: argparse.Namespace) -> int:
    return execute_group("smoke", load_config().command_group("smoke"))


def command_architecture_check(args: argparse.Namespace) -> int:
    config = load_config()
    strict = bool(args.strict or config.lifecycle == "active")
    architecture = ROOT / "ARCHITECTURE.md"
    if strict and architecture.exists() and PLACEHOLDER in architecture.read_text(encoding="utf-8"):
        raise HarnessError(f"ARCHITECTURE.md contains unresolved {PLACEHOLDER} markers")
    commands = config.command_group("architecture")
    if commands:
        execute_group("architecture", commands)
    else:
        print("Architecture document check passed; no machine architecture commands configured.")
    return 0


def command_check(_: argparse.Namespace) -> int:
    config = load_config()
    command_docs_index(argparse.Namespace(check=True))
    command_docs_check(argparse.Namespace(strict=False))
    command_plan_check(argparse.Namespace(strict=False))
    if config.configuration != "ready":
        raise HarnessError("dev/harness.toml is still marked configuration = 'review'; confirm canonical commands first")
    commands = config.command_group("check")
    source_exists = any((ROOT / path).exists() for path in config.list_value("paths", "source"))
    return execute_group("check", commands, allow_empty=not source_exists)


def command_verify(_: argparse.Namespace) -> int:
    config = load_config()
    command_docs_index(argparse.Namespace(check=True))
    strict = config.lifecycle == "active"
    command_docs_check(argparse.Namespace(strict=strict))
    command_plan_check(argparse.Namespace(strict=strict))
    command_architecture_check(argparse.Namespace(strict=strict))
    if config.configuration != "ready":
        raise HarnessError("dev/harness.toml is still marked configuration = 'review'; confirm deterministic commands first")
    commands = config.command_group("verify")
    source_exists = any((ROOT / path).exists() for path in config.list_value("paths", "source"))
    result = execute_group("verify", commands, allow_empty=not source_exists)
    smoke = config.command_group("smoke")
    if smoke:
        execute_group("smoke", smoke)
    return result


def git_output(*args: str, check: bool = True) -> str:
    completed = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    if check and completed.returncode != 0:
        raise HarnessError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def git_head() -> str:
    if not (ROOT / ".git").exists():
        return ""
    return git_output("rev-parse", "HEAD", check=False)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9가-힣]+", "-", value)
    return value.strip("-") or "change"


def next_plan_id() -> str:
    year = date.today().year
    highest = 0
    for plan in plan_files():
        if not plan.id.startswith(f"PLAN-{year}-"):
            continue
        match = PLAN_ID_PATTERN.search(plan.id)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"PLAN-{year}-{highest + 1:04d}"


def command_new_plan(args: argparse.Namespace) -> int:
    title = " ".join(args.title).strip()
    if not title:
        raise HarnessError("plan title is required")
    plan_id = next_plan_id()
    template = ROOT / "docs" / "exec-plans" / "_template.md"
    if not template.exists():
        raise HarnessError("missing docs/exec-plans/_template.md")
    text = template.read_text(encoding="utf-8")
    replacements = {
        "{{PLAN_ID}}": plan_id,
        "{{PLAN_TITLE}}": title,
        "{{DATE}}": date.today().isoformat(),
        "{{AREA}}": args.area or "cross-cutting",
        "{{BASE_COMMIT}}": git_head(),
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    destination = ROOT / "docs" / "exec-plans" / "active" / f"{plan_id}-{slugify(title)}.md"
    if destination.exists():
        raise HarnessError(f"plan already exists: {destination.relative_to(ROOT)}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    print(destination.relative_to(ROOT))
    return 0


def extract_task(plan: Plan, task_id: str) -> str:
    matches = list(TASK_HEADING.finditer(plan.text))
    for index, match in enumerate(matches):
        if match.group(1).lower() != task_id.lower():
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(plan.text)
        return plan.text[match.start() : end].rstrip() + "\n"
    raise HarnessError(f"task {task_id} not found in {plan.id}")


def command_task(args: argparse.Namespace) -> int:
    plan = locate_plan(args.plan)
    print(f"Plan: {plan.id}")
    print(f"Path: {plan.path.relative_to(ROOT)}")
    print(f"Base commit: {plan.metadata.get('base_commit', '')}")
    print()
    print(extract_task(plan, args.task), end="")
    return 0


def document_relevance(doc: DurableDocument, *, path: str, area: str) -> bool:
    if area and doc.area.lower() == area.lower():
        return True
    if path:
        normalized = path.replace("\\", "/").lstrip("./")
        return any(fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch("./" + normalized, pattern) for pattern in doc.applies_to)
    return not area and not path


def command_context(args: argparse.Namespace) -> int:
    config = load_config()
    errors: list[str] = []
    documents = durable_documents(errors)
    for error in errors:
        print(f"WARNING: {error}")
    print("# Repository context")
    print(f"- Root: `{ROOT}`")
    print(f"- Project: {config.project.get('name', ROOT.name)}")
    print(f"- Kind: {config.project.get('kind', 'other')}")
    print(f"- Baseline: {config.baseline}")
    print(f"- Command configuration: {config.configuration}")
    print(f"- Lifecycle: {config.lifecycle}")
    print(f"- Primary language: {config.project.get('primary_language', 'unknown')}")
    print(f"- Runtime: {config.project.get('runtime', 'unknown')}")
    print("- Operating contract: `AGENTS.md`")
    print("- Knowledge map: `docs/README.md`")
    print("- Current architecture: `ARCHITECTURE.md`")
    if args.plan:
        plan = locate_plan(args.plan)
        print("\n## Selected plan")
        print(f"- `{plan.path.relative_to(ROOT)}` — {plan.title} [{plan.status}]")
    print("\n## Relevant durable documents")
    relevant = [doc for doc in documents if document_relevance(doc, path=args.path or "", area=args.area or "")]
    if not relevant:
        print("- None matched. Read the stable entry documents and expand only with evidence.")
    else:
        for doc in relevant:
            print(f"- `{doc.path.relative_to(ROOT)}` — {doc.id} [{doc.status}] {doc.summary}")
    print("\n## Active plans")
    active = [plan for plan in plan_files() if "active" in plan.path.relative_to(ROOT).parts]
    if args.area:
        active = [plan for plan in active if str(plan.metadata.get("area", "")).lower() == args.area.lower()]
    if not active:
        print("- None")
    else:
        for plan in active:
            print(f"- `{plan.path.relative_to(ROOT)}` — {plan.title} [{plan.status}]")
    print("\n## Deterministic commands")
    for name in ("bootstrap", "run", "check", "verify", "smoke", "architecture"):
        group = config.command_group(name)
        if group:
            print(f"- {name}: " + " ; ".join(f"`{command_display(command)}`" for command in group))
        else:
            print(f"- {name}: not configured")
    return 0


def command_close_plan(args: argparse.Namespace) -> int:
    plan = locate_plan(args.plan, active_only=True)
    if plan.status != "verifying":
        raise HarnessError(f"plan must be in status 'verifying' before close; current status is '{plan.status}'")
    if not (ROOT / ".git").exists():
        raise HarnessError("close-plan requires a Git repository")
    if git_output("status", "--porcelain"):
        raise HarnessError("close-plan requires a clean working tree so verification can bind to one integrated commit")
    head = git_head()
    if not head:
        raise HarnessError("cannot determine integrated Git commit")
    declared = str(plan.metadata.get("integrated_commit", "")).strip()
    if declared not in {"HEAD", head}:
        raise HarnessError(
            f"plan integrated_commit ({declared or 'missing'}) must be HEAD or match current HEAD ({head}); "
            "update and commit the verifying plan before closing"
        )
    command_verify(argparse.Namespace())
    original_text = plan.text
    completed_dir = ROOT / "docs" / "exec-plans" / "completed"
    completed_dir.mkdir(parents=True, exist_ok=True)
    destination = completed_dir / plan.path.name
    if destination.exists():
        raise HarnessError(f"completed plan already exists: {destination.relative_to(ROOT)}")
    updated = update_frontmatter(
        original_text,
        {"status": "complete", "updated": date.today().isoformat(), "integrated_commit": head, "verified_commit": head},
    )
    plan.path.unlink()
    destination.write_text(updated, encoding="utf-8")
    try:
        command_docs_index(argparse.Namespace(check=True))
        command_docs_check(argparse.Namespace(strict=True))
        command_plan_check(argparse.Namespace(strict=True))
    except Exception:
        destination.unlink(missing_ok=True)
        plan.path.write_text(original_text, encoding="utf-8")
        raise
    print(f"Closed {plan.id} at verified commit {head}.")
    print(f"Moved to {destination.relative_to(ROOT)}. Commit the completion record separately.")
    return 0


def parse_iso_date(value: object) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def path_pattern_matches(pattern: str) -> bool:
    normalized = pattern.lstrip("./")
    if not any(char in normalized for char in "*?["):
        return (ROOT / normalized).exists()
    for path in ROOT.rglob("*"):
        relative = str(path.relative_to(ROOT)).replace(os.sep, "/")
        if fnmatch.fnmatch(relative, normalized):
            return True
    return False


def command_garden(args: argparse.Namespace) -> int:
    config = load_config()
    warnings: list[str] = []
    max_lines = int(config.policy.get("agents_max_lines", 140))
    agents = ROOT / "AGENTS.md"
    if agents.exists():
        lines = len(agents.read_text(encoding="utf-8").splitlines())
        if lines > max_lines:
            warnings.append(f"OVERSIZED-ENTRY: AGENTS.md has {lines} lines (maximum {max_lines})")
    stale_days = int(config.policy.get("stale_plan_days", 21))
    today = date.today()
    for plan in plan_files():
        if "active" not in plan.path.relative_to(ROOT).parts:
            continue
        updated = parse_iso_date(plan.metadata.get("updated"))
        if updated and (today - updated).days > stale_days:
            warnings.append(f"STALE-PLAN: {plan.path.relative_to(ROOT)} has not been updated for {(today - updated).days} days")
    metadata_errors: list[str] = []
    documents = durable_documents(metadata_errors)
    warnings.extend(f"DOC-METADATA: {error}" for error in metadata_errors)
    for doc in documents:
        for pattern in doc.applies_to:
            if pattern and not path_pattern_matches(pattern):
                warnings.append(f"STALE-PATH: {doc.id} applies_to pattern matches nothing: {pattern}")
    if config.lifecycle == "active":
        for path in (
            ROOT / "ARCHITECTURE.md",
            ROOT / "docs" / "PRODUCT.md",
            ROOT / "docs" / "DESIGN.md",
            ROOT / "docs" / "QUALITY.md",
            ROOT / "docs" / "SECURITY.md",
        ):
            if path.exists() and PLACEHOLDER in path.read_text(encoding="utf-8"):
                warnings.append(f"PLACEHOLDER: {path.relative_to(ROOT)} still contains {PLACEHOLDER}")
    deprecated = [doc for doc in documents if doc.status in {"deprecated", "superseded"}]
    deprecated_paths = {doc.path for doc in deprecated}
    current_paths = [
        path for path in (ROOT / "docs").rglob("*.md") if "completed" not in path.parts and path not in deprecated_paths
    ]
    for doc in deprecated:
        for path in current_paths:
            if doc.id in path.read_text(encoding="utf-8", errors="ignore"):
                warnings.append(f"DEPRECATED-REFERENCE: {path.relative_to(ROOT)} still references {doc.id}")
                break
    if not warnings:
        print("Garden check found no current maintenance candidates.")
        return 0
    for warning in warnings:
        print(f"WARNING: {warning}")
    print(f"Garden check found {len(warnings)} maintenance candidate(s); it made no changes.")
    if args.strict:
        raise HarnessError("garden strict mode failed because maintenance candidates exist")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    context = sub.add_parser("context", help="print a small, routed repository context")
    context.add_argument("--path", default="")
    context.add_argument("--area", default="")
    context.add_argument("--plan", default="")
    context.set_defaults(func=command_context)
    sub.add_parser("bootstrap", help="run configured dependency setup commands").set_defaults(func=command_bootstrap)
    sub.add_parser("run", help="run the configured application command").set_defaults(func=command_run)
    sub.add_parser("check", help="run the fast local feedback loop").set_defaults(func=command_check)
    sub.add_parser("verify", help="run the canonical completion gate").set_defaults(func=command_verify)
    sub.add_parser("smoke", help="run configured observable smoke checks").set_defaults(func=command_smoke)
    docs_index = sub.add_parser("docs-index", help="generate or check the durable document catalog")
    docs_index.add_argument("--check", action="store_true")
    docs_index.set_defaults(func=command_docs_index)
    docs_check = sub.add_parser("docs-check", help="validate document structure, metadata, and links")
    docs_check.add_argument("--strict", action="store_true")
    docs_check.set_defaults(func=command_docs_check)
    plan_check = sub.add_parser("plan-check", help="validate ExecPlan lifecycle and Task Packets")
    plan_check.add_argument("--strict", action="store_true")
    plan_check.set_defaults(func=command_plan_check)
    architecture = sub.add_parser("architecture-check", help="validate architecture documentation and configured boundaries")
    architecture.add_argument("--strict", action="store_true")
    architecture.set_defaults(func=command_architecture_check)
    new_plan = sub.add_parser("new-plan", help="create an active ExecPlan from the repository template")
    new_plan.add_argument("title", nargs="+")
    new_plan.add_argument("--area", default="")
    new_plan.set_defaults(func=command_new_plan)
    task = sub.add_parser("task", help="print one bounded Task Packet for delegation")
    task.add_argument("plan")
    task.add_argument("task")
    task.set_defaults(func=command_task)
    close = sub.add_parser("close-plan", help="verify an integrated commit and archive a completed plan")
    close.add_argument("plan")
    close.set_defaults(func=command_close_plan)
    garden = sub.add_parser("garden", help="report stale plans, documents, paths, and references without changing them")
    garden.add_argument("--strict", action="store_true")
    garden.set_defaults(func=command_garden)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
