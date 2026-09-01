---
id: ADR-0001
kind: decision
status: accepted
area: harness
summary: Retire the copied repository runtime in favor of a document-first product boundary
applies_to:
  - "src/reporivet/**"
  - "src/reporivet/assets/**"
  - "docs/**"
supersedes: []
superseded_by: ""
---

# Retire the copied repository runtime boundary

## Context

Reporivet's earlier product and design records made a copied repository-local runtime the center of ordinary work. [`SPEC-REPORIVET-001`](../product-specs/SPEC-REPORIVET-001-generated-project.md) and [`DESIGN-REPORIVET-001`](../design-docs/DESIGN-REPORIVET-001-initializer-and-runtime.md) describe generated `dev/` wrappers, `dev/harness.toml`, `harness.py`, package-independent commands, generated CI, and a two-lifetime runtime. [`SPEC-REPORIVET-002`](../product-specs/SPEC-REPORIVET-002-project-definition-adoption-and-evidence-gate.md) and [`DESIGN-REPORIVET-002`](../design-docs/DESIGN-REPORIVET-002-project-definition-adoption-and-evidence-gate.md) extend that boundary with repository-local context and code-map routing, Verification Runs, Gate policy, evidence artifacts, evidence-bound `close-plan`, and gardening.

Those contracts make the target repository carry a second execution system whose behavior can drift from the installed package and from project-owned commands. They also imply that Reporivet can provide a uniform command, CI, evidence, and completion boundary after installation. That promise is larger than the durable product need and encourages more machinery rather than clearer authority.

The approved replacement is documented in [`SPEC-REPORIVET-003`](../product-specs/SPEC-REPORIVET-003-document-first-harness.md), [`DESIGN-REPORIVET-003`](../design-docs/DESIGN-REPORIVET-003-document-first-harness.md), and [`PLAN-2026-0003`](../exec-plans/active/PLAN-2026-0003-document-first-harness.md). The records retain the useful evidence and ownership ideas while changing where execution and authority live.

## Decision

Retire the repository-local runtime, Gate, evidence-run, generated-CI, and derived-routing boundary rather than repairing it with more machinery.

Reporivet will be a package-side initializer and explicit migration tool. It may inspect a target read-only, guide definition, classify ownership, render canonical authority documents, install explicitly requested Claude adapters, and perform an approved reversible 0.2 migration. It will not copy a target executor or promise a Reporivet maintenance command after package removal.

The generated repository will instead contain a host-neutral `AGENTS.md`, a navigable `docs/README.md`, rich project-owned authority documents, and durable Markdown Plans. `docs/OPERATIONS.md` is the one current operations authority. Claude Code is the first optional adapter through a thin `CLAUDE.md`, catalogued Skills, and minimal settings; those assets route to the documents and Plans without becoming authority.

The project owns its commands, tests, CI, deployment, secrets, operational procedures, and any evidence produced by those systems. Main owns one active Plan and its integration judgment. Bounded implementation Sub-Agents and fresh Verification Sub-Agents use project-owned commands and return compact criterion-level evidence. There is no generated wrapper, `dev/harness.toml`, `harness.py`, `./dev/*` command group, Verification Run writer, Gate, evidence archive, automatic Plan closure, context/code-map executor, garden command, or generated CI workflow in a fresh target.

The following current contracts are superseded where they require that retired boundary:

- the generated runtime and package-removal guarantees in SPEC-001;
- the two-lifetime copied-runtime ownership and wrapper/runtime parity in DESIGN-001;
- the repository-local definition, audit, context, checks, Verification Run, Gate, closure, and gardening command contract in SPEC-002; and
- the copied-runtime, Gate, evidence artifact, generated-CI, and closure design in DESIGN-002.

The supersession is not a rejection of durable project definition. Read-only audit, safe ownership classification, explicit Confirmed/Proposed/Open/Sources evidence states, rich authority documents, durable Plans, historical readability, and project-owned verification remain required. Existing `.harness/runs/` and project-owned or historical files are preserved as history; the new boundary writes no new Reporivet run evidence there.

## Consequences

### Positive

- The generated repository is legible without understanding or executing a copied Reporivet runtime.
- `AGENTS.md`, authority documents, Skills, and Plans are inspectable, portable, and recoverable through ordinary Git history.
- Project commands and CI remain under project ownership instead of being shadowed by generated wrappers or a second policy engine.
- Removing the installed package does not remove the document, Plan, Git, command, or CI foundation.
- There is one current operations authority and one durable Plan resume model rather than parallel reliability, context, Gate, run, and closure systems.
- Setup and migration can preserve uncertainty and ownership without requiring semantic model judgment or a hidden state service.
- Historical Plans and evidence remain readable because retirement is not history rewriting.

### Negative and risks

- Projects must own and maintain their commands, CI, verification depth, and operational completeness; results are less uniform across repositories.
- Main and human reviewers carry more responsibility for semantic completeness, evidence sufficiency, and Plan discipline.
- Rich Markdown and explicit Plan updates add maintenance work that a runtime or automatic closure engine previously attempted to hide.
- Package-side setup and migration remain dependent on the installed package, and Claude ergonomics are optional rather than universal.
- Removing automatic context maps, Gate verdicts, and evidence archives loses convenience and may expose gaps in project verification.
- A 0.2 migration requires preview, approval, an external visible backup, ownership classification, and rollback, which makes retirement slower but prevents guessed deletion.
- Legacy generated files and `.harness/runs/` may remain until an explicit ownership-safe migration; the repository can temporarily contain readable historical material alongside the new boundary.

## Alternatives considered

- **Repair the copied runtime with more machinery.** Rejected. More wrappers, registries, Gate rules, or synchronization would deepen the duplicate-runtime boundary and its drift risk.
- **Keep the two-lifetime runtime and make documents thinner.** Rejected. It preserves package-removal behavior at the cost of a hidden execution authority and continued generated command/CI contracts.
- **Move the runtime into a global Skill, plugin, daemon, or task database.** Rejected. That replaces repository-local duplication with host-specific installation state and reduces portability.
- **Generate project wrappers, a universal command runner, and CI anyway.** Rejected. Commands, CI, deployment, secrets, and verification scope belong to each project; Reporivet should not impersonate them.
- **Retain Verification Runs, Gate, context/code-map, garden, and automatic close-plan as a smaller replacement runtime.** Rejected. These are the same boundary in smaller form, not the document-first product.
- **Automatically infer and confirm setup answers or delete all legacy assets.** Rejected. Inference must remain Proposed or Open, and destructive migration requires preview, explicit approval, visible external backup, ownership preservation, and rollback.
- **Provide non-Claude adapters in this decision.** Deferred. Claude is the first optional host profile; host neutrality is preserved by keeping `AGENTS.md` and documents canonical.

## Verification and retirement

Implementation must verify the decision against the exact candidate described by [`PLAN-2026-0003`](../exec-plans/active/PLAN-2026-0003-document-first-harness.md):

- fresh initialization and wheel contents contain no copied runtime, wrappers, `dev` configuration, generated CI, Gate/evidence runner, context/code-map, garden, or package-independent Reporivet command;
- `AGENTS.md`, `docs/README.md`, `docs/OPERATIONS.md`, optional Claude assets, and one active Plan route Main/Sub/Verifier work without a hidden executor;
- guided setup preserves Confirmed, Proposed, Open, and Sources, and audit/ownership behavior is deterministic and read-only;
- project-owned commands and CI remain the execution boundary, while package removal leaves documents, Plans, Git, and project commands useful;
- 0.2 migration requires an unchanged preview fingerprint, explicit approval, an external visible backup, ownership preservation, and safe automatic and post-success rollback; and
- superseded runtime/Gate/evidence references are historical or explicitly marked as superseded, not live current authority.

The old contracts are retired only when these conditions are demonstrated by focused and independent verification; no implementation summary alone retires them. ADR-0001 remains the accepted boundary decision until a later accepted ADR explicitly changes or retires it. The migration and retirement must not delete project-owned content, rewrite completed Plans, or overwrite post-migration user changes during rollback.
