---
id: SPEC-REPORIVET-004
kind: product-spec
status: active
area: harness
summary: One-shot setup with independent generated targets and static runbooks
applies_to:
  - "src/reporivet/**"
  - "src/reporivet/assets/project/**"
  - "AGENTS.md"
  - "CLAUDE.md"
  - "docs/**"
supersedes:
  - SPEC-REPORIVET-003
---

# One-shot bootstrapper and independent generated target

## Observable behavior

A user may run Reporivet from an installed package or an explicit local source to audit, define, preview, and apply setup to another repository. An optional external user-scoped `/reporivet-setup` Skill may guide that exact preview/approval flow, but the Skill is not copied into the target and does not install, download, resolve, or reproduce Reporivet.

After approved setup, the generated repository operates only through project-owned Markdown, ordinary Plans, Git, project commands, and host-native Agents. Reporivet can be removed immediately without reducing ordinary project work.

A fresh target receives the canonical authority documents, Plan template/directories, and deterministic static runbooks for eligible Confirmed procedures. A requested Claude adapter is a root `CLAUDE.md` containing exactly `@AGENTS.md` and one trailing newline. Setup creates no active Plan.

A fresh target receives no `.claude/skills/**`, generated `.claude/settings.json`, `.reporivet-version`, Reporivet runtime/module, package-independent command, doctor gate, registry instruction, scheduler, dispatcher, task store, command runner, Gate, evidence archive, hidden state, or automatic closure.

## Traceability

### Confirmed

- [confirmed] JRN-001 | A maintainer performs explicit one-shot setup, removes Reporivet, and continues work from generated Markdown only.
- [confirmed] REQ-P0-001 | Journey: JRN-001 | Acceptance: AC-001 | Fresh targets contain no continuing Reporivet dependency.
- [confirmed] AC-001 | P0: REQ-P0-001 | Journey: JRN-001 | A temporary fresh target contains no Reporivet Skill, marker, generated settings, runtime, doctor/tool gate, or package-resolution instruction and remains usable after package removal.
- [confirmed] REQ-P0-002 | Journey: JRN-001 | Acceptance: AC-002 | Main and Sub-Agent behavior is durable Markdown authority.
- [confirmed] AC-002 | P0: REQ-P0-002 | Journey: JRN-001 | Generated `AGENTS.md`, `docs/PLANS.md`, and the Plan template define Plan discovery, Task Owner delegation, bounded implementation, fresh verification, evidence return, and manual terminal movement without a Skill.
- [confirmed] REQ-P0-003 | Journey: JRN-001 | Acceptance: AC-003 | Confirmed procedures become static runbooks.
- [confirmed] AC-003 | P0: REQ-P0-003 | Journey: JRN-001 | Only complete unique Confirmed records produce deterministic `docs/runbooks/<slug>.md` without Skill/executor metadata.
- [confirmed] JRN-002 | An owner reruns setup against a target containing historical Reporivet-generated artifacts.
- [confirmed] REQ-P0-004 | Journey: JRN-002 | Acceptance: AC-004 | Cleanup is exact, explicit, backed up, and reversible.
- [confirmed] AC-004 | P0: REQ-P0-004 | Journey: JRN-002 | Setup preview removes/converts only exact canonical artifacts, preserves modified or ambiguous content, requires an external backup, rejects stale approval, and supports guarded rollback.
- [confirmed] REQ-P0-005 | Journey: JRN-001 | Acceptance: AC-005 | Reporivet provides no ongoing diagnosis contract.
- [confirmed] AC-005 | P0: REQ-P0-005 | Journey: JRN-001 | `doctor` is absent and approved setup validates only its own transaction postconditions.

### Proposed

- None.

### Open

- Publication, signing, hosted distribution, and release version remain separate release decisions.

### Sources

- [`../decisions/ADR-0002-one-shot-bootstrapper-boundary.md`](../decisions/ADR-0002-one-shot-bootstrapper-boundary.md)
- [`../exec-plans/active/PLAN-2026-0006-one-shot-bootstrapper.md`](../exec-plans/active/PLAN-2026-0006-one-shot-bootstrapper.md)

## Requirements

- **REQ-1:** Setup may depend on an installed package or explicit local source only while the user invokes setup.
- **REQ-2:** Generated authority must never instruct an Agent to locate, install, resolve, import, invoke, or verify Reporivet or doctor.
- **REQ-3:** Reporivet absence after setup is expected and must not be recorded as `UNKNOWN`, blocking, or risky.
- **REQ-4:** The optional external setup Skill invokes deterministic package behavior only and performs no target Write/Edit logic itself.
- **REQ-5:** Target role and Plan behavior must remain host-neutral and readable from ordinary Markdown.
- **REQ-6:** Procedure runbooks preserve the strict nine-field Confirmed record and never become executors.
- **REQ-7:** Existing differing documents, runbooks, settings, Skills, symlinks, and nonregular paths are preserved or refused rather than overwritten or guessed-owned.
- **REQ-8:** Legacy deletion authority requires exact canonical bytes or an exact strict parse-and-rerender proof; path names and markers alone are insufficient.
- **REQ-9:** Destructive setup rerun requires exact preview approval, external backup, preimage revalidation, whole-transaction failure rollback, and later rollback refusal after user edits.
- **REQ-10:** Setup, init, define, and package maintenance never create a Plan, dispatch Agents, execute project commands, or provide a target runtime.

## Non-goals

- No plugin runtime, standalone zipapp, automatic package resolver, network installer, non-Claude adapter, scheduler, dispatcher, task database, command runner, CI generator, deployment engine, Gate, evidence archive, model judge, or automatic Plan closure.
- No publication, signing, release, deployment, global Skill installation, or mutation of real external projects during implementation.
- No rewrite of accepted historical ADRs, completed Plans, or legacy fixtures merely to adopt current wording.

## Edge cases and failure behavior

- If the external Skill cannot find the explicit setup command/source, it stops without attempting installation or registry lookup.
- A differing target file remains project-owned and is preserved.
- A complete Confirmed procedure with a differing existing runbook reports a collision and does not overwrite it.
- A legacy procedure Skill is converted only after known-format strict parsing and exact byte-for-byte rerender equality.
- An unsafe, symlinked, nonregular, unknown, or changed cleanup candidate is preserved or blocks apply.
- A preview requiring removals is not apply-eligible until an explicit external backup location is included in the fingerprint.
- Any preimage change rejects apply. Any failed mutation restores the approved transaction or reports exact rollback failure.
- Later rollback refuses when a successful postimage has changed.

## Verification

- Run the project-owned full unit suite, compile check, focused distribution tests, and patch hygiene checks.
- Bootstrap a fresh temporary target, remove the setup environment, and verify the target remains usable with no forbidden dependency artifact.
- Seed a temporary existing target with exact and modified historical artifacts; verify cleanup classification, backup, apply, automatic rollback, and guarded later rollback.
- Use fresh nonrepairing verification contexts and record criterion-level evidence against one integrated candidate.
