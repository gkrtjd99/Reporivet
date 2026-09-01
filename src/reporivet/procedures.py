"""Validation and rendering for confirmed project procedure Skills.

This module is deliberately pure.  It parses the visible Confirmed values from
``project-definition.draft.md`` and calculates instruction-only Skill targets;
filesystem classification, preservation, and writes belong to guided setup.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path


PROCEDURE_FIELDS = (
    "slug",
    "title",
    "trigger",
    "reads",
    "actions",
    "stop_conditions",
    "evidence",
    "permissions",
    "rollback",
)

PROCEDURE_SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
RESERVED_PROCEDURE_SLUGS = frozenset(
    {
        "reporivet-main",
        "reporivet-implementation",
        "reporivet-verification",
    }
)
_TUPLE_FIELDS = frozenset(PROCEDURE_FIELDS[3:])


class ProcedureValidationError(ValueError):
    """Raised when a procedure record is not a complete valid record."""


@dataclass(frozen=True, slots=True)
class ProcedureSpec:
    """An immutable, complete description of one repeatable procedure."""

    slug: str
    title: str
    trigger: str
    reads: tuple[str, ...]
    actions: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    evidence: tuple[str, ...]
    permissions: tuple[str, ...]
    rollback: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "slug", _validate_slug(self.slug))
        for field_name in ("title", "trigger"):
            object.__setattr__(
                self,
                field_name,
                _validate_scalar(getattr(self, field_name), field_name),
            )
        for field_name in _TUPLE_FIELDS:
            object.__setattr__(
                self,
                field_name,
                _validate_items(getattr(self, field_name), field_name),
            )

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "ProcedureSpec":
        """Build a spec from a strict nine-field JSON object mapping."""

        if not isinstance(value, Mapping):
            raise ProcedureValidationError("procedure record must be a JSON object")
        keys = set(value)
        expected = set(PROCEDURE_FIELDS)
        missing = [field for field in PROCEDURE_FIELDS if field not in keys]
        unknown = sorted(keys - expected)
        if missing:
            raise ProcedureValidationError(
                "procedure record is incomplete; missing fields: " + ", ".join(missing)
            )
        if unknown:
            raise ProcedureValidationError(
                "procedure record contains unknown fields: " + ", ".join(unknown)
            )
        return cls(
            slug=value["slug"],
            title=value["title"],
            trigger=value["trigger"],
            reads=value["reads"],
            actions=value["actions"],
            stop_conditions=value["stop_conditions"],
            evidence=value["evidence"],
            permissions=value["permissions"],
            rollback=value["rollback"],
        )

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-ready copy in the canonical field set."""

        return {
            "slug": self.slug,
            "title": self.title,
            "trigger": self.trigger,
            "reads": list(self.reads),
            "actions": list(self.actions),
            "stop_conditions": list(self.stop_conditions),
            "evidence": list(self.evidence),
            "permissions": list(self.permissions),
            "rollback": list(self.rollback),
        }

    def canonical_record(self) -> str:
        """Return the one-line canonical visible Confirmed record."""

        return _canonical_json(self.as_dict())

    # ``to_record`` is a convenient spelling for guided callers and keeps the
    # serialization operation attached to the immutable value.
    def to_record(self) -> str:
        return self.canonical_record()


@dataclass(frozen=True, slots=True)
class ProcedureDiagnostic:
    """A non-throwing diagnostic for one ineligible Confirmed value."""

    index: int
    code: str
    detail: str

    @property
    def message(self) -> str:
        """Compatibility spelling for integrations that call diagnostics messages."""

        return self.detail

    @property
    def path(self) -> str:
        return f"procedures.confirmed[{self.index}]"

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "detail": self.detail,
            "index": self.index,
            "path": self.path,
        }


@dataclass(frozen=True, slots=True)
class ProcedureCollection:
    """Validated procedures and diagnostics from one Confirmed collection."""

    procedures: tuple[ProcedureSpec, ...]
    diagnostics: tuple[ProcedureDiagnostic, ...]

    @property
    def eligible(self) -> tuple[ProcedureSpec, ...]:
        return self.procedures

    @property
    def specs(self) -> tuple[ProcedureSpec, ...]:
        return self.procedures

    @property
    def valid(self) -> bool:
        return not self.diagnostics

    def as_dict(self) -> dict[str, object]:
        return {
            "diagnostics": [diagnostic.as_dict() for diagnostic in self.diagnostics],
            "procedures": [procedure.as_dict() for procedure in self.procedures],
        }


@dataclass(frozen=True, slots=True)
class ProcedureSkillTarget:
    """Pure calculated content for one project-owned Skill target."""

    procedure: ProcedureSpec
    path: str
    content: str

    @property
    def slug(self) -> str:
        return self.procedure.slug

    def as_dict(self) -> dict[str, object]:
        return {
            "content": self.content,
            "path": self.path,
            "slug": self.slug,
        }


@dataclass(frozen=True, slots=True)
class ProcedureSkillPlan:
    """Calculated Skill targets plus parse diagnostics for guided integration."""

    targets: tuple[ProcedureSkillTarget, ...]
    diagnostics: tuple[ProcedureDiagnostic, ...]

    @property
    def skills(self) -> tuple[ProcedureSkillTarget, ...]:
        return self.targets

    @property
    def procedures(self) -> tuple[ProcedureSpec, ...]:
        return tuple(target.procedure for target in self.targets)

    @property
    def eligible(self) -> tuple[ProcedureSkillTarget, ...]:
        return self.targets

    def as_dict(self) -> dict[str, object]:
        return {
            "diagnostics": [diagnostic.as_dict() for diagnostic in self.diagnostics],
            "targets": [target.as_dict() for target in self.targets],
        }


def _validate_scalar(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ProcedureValidationError(
            f"procedure field '{field_name}' must be a string"
        )
    normalized = value.strip()
    if not normalized:
        raise ProcedureValidationError(
            f"procedure field '{field_name}' must contain a non-empty value"
        )
    if "\n" in normalized or "\r" in normalized:
        raise ProcedureValidationError(
            f"procedure field '{field_name}' must be a single line"
        )
    return normalized


def _validate_items(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        raise ProcedureValidationError(
            f"procedure field '{field_name}' must be an array of strings"
        )
    if not value:
        raise ProcedureValidationError(
            f"procedure field '{field_name}' must contain at least one value"
        )
    normalized: list[str] = []
    for index, item in enumerate(value):
        try:
            normalized.append(_validate_scalar(item, f"{field_name}[{index}]"))
        except ProcedureValidationError:
            raise
    return tuple(normalized)


def _validate_slug(value: object) -> str:
    slug = _validate_scalar(value, "slug")
    if len(slug) > 64 or PROCEDURE_SLUG_PATTERN.fullmatch(slug) is None:
        raise ProcedureValidationError(
            "procedure field 'slug' must use lowercase letters, digits, and single hyphens and be at most 64 characters"
        )
    if slug in RESERVED_PROCEDURE_SLUGS:
        raise ProcedureValidationError(
            f"procedure field 'slug' is reserved for the default Claude Skill: {slug}"
        )
    return slug


def _canonical_json(value: Mapping[str, object]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def serialize_procedure_spec(spec: ProcedureSpec) -> str:
    """Serialize a validated spec as one compact canonical JSON object."""

    if not isinstance(spec, ProcedureSpec):
        raise ProcedureValidationError("serialize_procedure_spec expects a ProcedureSpec")
    return spec.canonical_record()


def serialize_procedure_record(spec: ProcedureSpec) -> str:
    """Alias with terminology matching the visible draft record."""

    return serialize_procedure_spec(spec)


def canonicalize_procedure_record(record: str) -> str:
    """Parse and canonicalize one structured Confirmed procedure record."""

    return parse_procedure_record(record).canonical_record()


def _strict_object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> object:
    raise ValueError(f"non-standard JSON constant: {value}")


def parse_procedure_record(record: object) -> ProcedureSpec:
    """Parse one complete procedure record or raise ``ProcedureValidationError``."""

    if not isinstance(record, str):
        raise ProcedureValidationError("procedure Confirmed value must be a JSON string")
    try:
        decoded = json.loads(
            record,
            object_pairs_hook=_strict_object_pairs,
            parse_constant=_reject_json_constant,
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ProcedureValidationError(
            f"procedure Confirmed value is malformed JSON: {exc}"
        ) from exc
    if not isinstance(decoded, dict):
        raise ProcedureValidationError(
            "procedure Confirmed value must contain a JSON object"
        )
    try:
        return ProcedureSpec.from_mapping(decoded)
    except ProcedureValidationError:
        raise
    except (TypeError, ValueError) as exc:
        raise ProcedureValidationError(str(exc)) from exc


def _diagnostic(index: int, code: str, detail: str) -> ProcedureDiagnostic:
    return ProcedureDiagnostic(index=index, code=code, detail=detail)


def _classify_validation_error(exc: ProcedureValidationError) -> str:
    detail = str(exc).casefold()
    if "malformed json" in detail:
        return "malformed-json"
    if "must contain a json object" in detail:
        return "non-object"
    if "incomplete" in detail or "unknown fields" in detail:
        return "incomplete-record" if "incomplete" in detail else "unknown-fields"
    if "slug" in detail:
        return "invalid-slug"
    return "invalid-record"


def _confirmed_values(confirmed: Iterable[object] | object) -> tuple[object, ...]:
    """Extract only Confirmed values when a topic evidence object is supplied."""

    if isinstance(confirmed, Mapping) and "confirmed" in confirmed:
        confirmed = confirmed["confirmed"]
    elif not isinstance(confirmed, (str, bytes)) and hasattr(confirmed, "confirmed"):
        confirmed = getattr(confirmed, "confirmed")
    if isinstance(confirmed, (str, bytes)) or not isinstance(confirmed, Iterable):
        return (confirmed,)
    return tuple(confirmed)


def parse_confirmed_procedures(
    confirmed: Iterable[object] | object,
) -> ProcedureCollection:
    """Validate only Confirmed values and retain diagnostics for exclusions.

    The caller supplies the ``procedures`` topic's Confirmed values explicitly.
    Proposed, Open, and Sources values therefore cannot accidentally become
    Skills through this API.  No value is executed or read from the filesystem.
    """

    values = _confirmed_values(confirmed)

    parsed: list[tuple[int, ProcedureSpec]] = []
    diagnostics: list[ProcedureDiagnostic] = []
    for index, record in enumerate(values):
        if isinstance(record, str) and not record.strip().startswith("{"):
            diagnostics.append(
                _diagnostic(
                    index,
                    "generic",
                    "procedure Confirmed value is generic evidence, not a structured JSON procedure record",
                )
            )
            continue
        try:
            parsed.append((index, parse_procedure_record(record)))
        except ProcedureValidationError as exc:
            diagnostics.append(
                _diagnostic(index, _classify_validation_error(exc), str(exc))
            )

    slug_counts = Counter(spec.slug for _, spec in parsed)
    procedures: list[ProcedureSpec] = []
    for index, spec in parsed:
        if slug_counts[spec.slug] > 1:
            diagnostics.append(
                _diagnostic(
                    index,
                    "duplicate-slug",
                    f"procedure slug '{spec.slug}' is duplicated in Confirmed values; no duplicate record is eligible",
                )
            )
        else:
            procedures.append(spec)

    diagnostics.sort(key=lambda item: (item.index, item.code, item.detail))
    return ProcedureCollection(tuple(procedures), tuple(diagnostics))


# Explicit aliases for integrations that use alternate draft-oriented wording.
parse_confirmed_procedure_records = parse_confirmed_procedures
canonical_procedure_record = canonicalize_procedure_record


def procedure_skill_path(procedure: ProcedureSpec | str) -> Path:
    """Calculate the relative target path for a procedure Skill."""

    slug = procedure.slug if isinstance(procedure, ProcedureSpec) else _validate_slug(procedure)
    return Path(".claude") / "skills" / slug / "SKILL.md"


def calculate_procedure_skill_path(procedure: ProcedureSpec | str) -> str:
    """Return the calculated Skill path in repository-relative POSIX form."""

    return procedure_skill_path(procedure).as_posix()


def _frontmatter_scalar(value: str) -> str:
    # Keep ordinary output as readable as the fixed role Skills.  Quote values
    # containing YAML-significant punctuation while retaining deterministic UTF-8.
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _.,;!?()/+'`-]*", value):
        return value
    return json.dumps(value, ensure_ascii=False)


def _bullet_section(title: str, values: tuple[str, ...]) -> list[str]:
    return [f"## {title}", "", *(f"- {value}" for value in values)]


def render_procedure_skill(procedure: ProcedureSpec) -> str:
    """Render one deterministic instruction-only Claude Skill."""

    if not isinstance(procedure, ProcedureSpec):
        raise ProcedureValidationError("render_procedure_skill expects a ProcedureSpec")
    description = f"{procedure.title}. Use when {procedure.trigger}."
    lines = [
        "---",
        f"name: {procedure.slug}",
        f"description: {_frontmatter_scalar(description)}",
        "---",
        "",
        f"# {procedure.title}",
        "",
        "## Trigger",
        "",
        procedure.trigger,
        "",
        *_bullet_section("Required reads", procedure.reads),
        "",
        *_bullet_section("Actions", procedure.actions),
        "",
        *_bullet_section("Stop conditions", procedure.stop_conditions),
        "",
        *_bullet_section("Evidence", procedure.evidence),
        "",
        *_bullet_section("Permissions", procedure.permissions),
        "",
        *_bullet_section("Rollback", procedure.rollback),
    ]
    return "\n".join(lines).rstrip() + "\n"


# A descriptive alias for callers that treat the rendered file as content.
procedure_skill_content = render_procedure_skill


def build_procedure_skill_plan(
    confirmed: Iterable[object] | object,
) -> ProcedureSkillPlan:
    """Calculate eligible Skill targets and preserve all validation diagnostics."""

    collection = parse_confirmed_procedures(confirmed)
    targets = tuple(
        ProcedureSkillTarget(
            procedure=procedure,
            path=calculate_procedure_skill_path(procedure),
            content=render_procedure_skill(procedure),
        )
        for procedure in collection.procedures
    )
    return ProcedureSkillPlan(targets=targets, diagnostics=collection.diagnostics)


# Integration-friendly aliases; all are pure calculations and perform no I/O.
procedure_skill_targets = build_procedure_skill_plan
confirmed_procedure_skills = build_procedure_skill_plan


__all__ = [
    "PROCEDURE_FIELDS",
    "PROCEDURE_SLUG_PATTERN",
    "RESERVED_PROCEDURE_SLUGS",
    "ProcedureCollection",
    "ProcedureDiagnostic",
    "ProcedureSkillPlan",
    "ProcedureSkillTarget",
    "ProcedureSpec",
    "ProcedureValidationError",
    "build_procedure_skill_plan",
    "calculate_procedure_skill_path",
    "canonical_procedure_record",
    "canonicalize_procedure_record",
    "confirmed_procedure_skills",
    "parse_confirmed_procedure_records",
    "parse_confirmed_procedures",
    "procedure_skill_content",
    "procedure_skill_path",
    "procedure_skill_targets",
    "render_procedure_skill",
    "serialize_procedure_record",
    "serialize_procedure_spec",
]
