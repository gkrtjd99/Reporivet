---
id: DESIGN-REPORIVET-004
kind: design-doc
status: active
area: harness
summary: Generator and transaction design for one-shot setup and independent targets
applies_to:
  - "src/reporivet/**"
  - "src/reporivet/assets/project/**"
  - "AGENTS.md"
  - "docs/**"
supersedes:
  - DESIGN-REPORIVET-003
---

# One-shot setup and independent-target design

## Context

The prior document-first design removed the copied executor but retained target Skills, a version marker, optional generated settings, procedure Skill rendering, and doctor. Those surfaces duplicate durable Markdown and can be interpreted as an ongoing Reporivet dependency. The new design makes the package lifetime end at approved setup while preserving ownership-safe adoption and rollback.

## Current design

```text
explicit installed/local Reporivet setup
    ├─ optional external user-scoped /reporivet-setup wrapper
    ├─ audit + visible definition + exact preview
    ├─ approved create/preserve/cleanup transaction
    └─ target-owned Markdown, Plans, runbooks, optional CLAUDE.md
         └─ project commands + Git + host-native Agents
```

The external Skill is a thin user interface outside the target asset tree. It invokes the deterministic setup command, relays the exact preview/fingerprint, and requests approval. It does not write target files, reconstruct package logic, install dependencies, query a registry, or persist execution state.

The target asset planner produces canonical documents and directories plus optional exact `CLAUDE.md`. `AGENTS.md`, `docs/PLANS.md`, and the Plan template contain the complete Main, Task Owner, implementation, verification, and manual Plan-lifecycle contract. No role Skill is generated.

`ProcedureSpec` remains a strict immutable nine-field value. Confirmed-only parsing, duplicate detection, canonical JSON, and diagnostics remain pure. Eligible procedures render plain deterministic `docs/runbooks/<slug>.md`. Runbooks have no frontmatter or execution metadata and become project-owned after creation.

An explicit setup rerun may include transition cleanup. The setup preview contains create/preserve/conflict actions plus cleanup/conversion actions and their exact preimages. Cleanup ownership is proven only by path-bound canonical hashes for fixed generated files, exact known marker bytes, or strict legacy procedure parsing followed by exact rerender equality. This new target-Skill/settings/marker cleanup is not routed through the existing legacy 0.2 `migrate` command and adds no transition command; that historical migration contract remains unchanged unless separately retired.

Destructive apply requires an absolute external backup directory and binds it into the approved preview fingerprint. Apply recomputes and compares the complete preview, revalidates preimages immediately before mutation, captures backups, performs creates/conversions/removals as one transaction, validates planned postconditions, and automatically restores on failure. Later rollback requires the external manifest and refuses if any successful postimage changed.

`doctor` is removed. Private setup validation checks only the exact approved transaction: planned document/runbook bytes, approved removals, preserved preimages, optional adapter bytes, and transaction/backup result. It does not diagnose unrelated repository state.

## Invariants and boundaries

- Initial explicit setup may depend on the package; generated targets never do.
- Fresh targets contain no `.claude/skills`, generated `.claude/settings.json`, `.reporivet-version`, Reporivet runtime/module, doctor/tool gate, or package-resolution instruction.
- Root `CLAUDE.md`, when selected, is exactly `@AGENTS.md\n`.
- Setup and package commands create no active Plan and dispatch no Agent.
- Generated Plans use only project-owned commands and never require Reporivet.
- Complete unique Confirmed procedures alone generate runbooks.
- Existing differing runbooks and documents are preserved.
- Filenames, directories, marker text, or Skill frontmatter alone never prove deletion ownership.
- Modified, unknown, ambiguous, unsafe, symlinked, and nonregular paths are preserved or refused.
- No recursive deletion is used for `.claude`; only transaction-proven empty child directories may be removed.
- Preview approval, backup, transaction manifests, and rollback state remain external to the target; no hidden target journal is created.
- This source repository is not treated as a cleanup target during implementation or tests.
- Historical ADRs, completed Plans, and fixtures remain readable.

## Interfaces and reuse

- Keep `coordinate_setup` in `src/reporivet/setup.py` as the integrated package entry point and evolve its envelope only as required to represent cleanup and backup-bound approval.
- Keep target classification, exact preview fingerprinting, and `_GuidedSetupTransaction` behavior in `src/reporivet/guided.py`; extend rather than duplicate them.
- Reuse setup-neutral inventory, backup, guarded mutation, restore, and postimage validation primitives extracted from `src/reporivet/migration.py`; do not invoke a second migration command.
- Keep `ProcedureSpec`, `parse_confirmed_procedures`, and canonical serialization in `src/reporivet/procedures.py`; replace only Skill-oriented target/render interfaces with runbook interfaces.
- Keep `audit_project` and root/path validation in `src/reporivet/initializer.py`.
- Store the external setup Skill source outside `src/reporivet/assets/project/**` so target generation cannot include it.

## Alternatives and trade-offs

- **Clarified target Skills:** less code churn but preserves duplicated instructions and the misleading dependency surface.
- **Provenance marker:** useful for maintenance detection but too easily interpreted as an active version requirement.
- **Optional doctor:** convenient for package maintainers but remains an ongoing contract that can leak into Plan evidence.
- **Standalone bundled runtime:** removes package installation at setup time but adds a second distribution/runtime without solving a target requirement.
- **Separate transition command:** isolates destructive behavior but adds another lifecycle entry point; explicit setup rerun already has preview/approval semantics.
- **Leave procedure data only in the draft:** smallest output but less usable than reviewed static runbooks.

The accepted trade-off is more setup-side ownership and rollback testing in exchange for a materially simpler generated target and one durable authority path.

## Verification

- Unit-test pure runbook validation/rendering and exact legacy ownership proof.
- Integration-test fresh target inventory and generated authority with no forbidden artifacts.
- Integration-test setup-rerun cleanup against temporary targets with exact, modified, unsafe, and unrelated files.
- Verify external backup permissions, stale-fingerprint refusal, automatic rollback, and later rollback refusal after changes.
- Verify CLI help contains no doctor and target templates contain no operational Reporivet command/install requirement.
- Inspect package data and built artifacts to prove the external setup Skill is not a target asset and retired templates are absent.
- Run independent criterion-level verification against one integrated candidate.
