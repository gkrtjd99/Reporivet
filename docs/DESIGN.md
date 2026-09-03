---
owner: design
status: active
last_reviewed: 2026-09-02
---

# Design

## Design direction and accessibility

Reporivet favors rich, inspectable repository knowledge and thin package-side execution. The installed package helps a maintainer establish a target contract once; the target then explains itself through Markdown, ordinary Plans, static runbooks, Git, and project-owned tools.

The one-shot design optimizes for safe adoption, agent legibility, human review, and useful operation after package removal. Setup is a bounded package-side transaction, not a runtime installed into the target. An optional external user-scoped `/reporivet-setup` wrapper may relay setup preview/apply, but it remains outside target assets, does not install or resolve Reporivet, and never edits target files itself.

The prior source candidate and wheel lifecycle remain recorded historical evidence: source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive; this does not establish a continuing target dependency, publication, signing, release, deployment, or CI readiness.

## Universal design boundary

`DESIGN.md` is universal and remains focused on visual language, interaction behavior, information architecture, and accessibility. It is the authority route for those principles across the project; it does not become a frontend implementation inventory or a service/runtime reliability record. When `web_ui=yes` is explicitly Confirmed, `docs/FRONTEND.md` may supplement this document with implementation and client-side loading/error/retry details. When `deployed_runtime=yes` is explicitly Confirmed, `docs/RELIABILITY.md` may supplement `OPERATIONS.md` with service/runtime reliability details; it does not change this document's design scope.

Design statements require an accountable owner and a source. Keep explicit facts **Confirmed**, candidate guidance **Proposed**, missing or conflicting requirements **Open**, and provenance in **Sources**. Scanner signals and audit output do not establish a design decision. `QUALITY.md` names project-owned checks; a fresh Verification Sub records criterion-level evidence for the integrated candidate rather than treating this document as proof that a design or accessibility requirement passed.

## Durable defaults

### Canonical authority over duplicated instructions

- `AGENTS.md` is the host-neutral entry point.
- `docs/README.md` maps current authority and the generated target surface.
- One matching active Plan carries substantive work state.
- Versioned specifications, designs, decisions, and completed Plans preserve durable context without becoming general startup material.
- The optional exact `CLAUDE.md` adapter is removable and points only to `AGENTS.md`; it is not product authority.

### Rich content over hidden state

- Product intent, system structure, quality, security, operations, decisions, work state, and evidence stay in readable Markdown.
- A Plan contains one task table and matching Task Packets rather than referring to a separate task database.
- Main records decisions, discoveries, integration, verification, and terminal outcome in the Plan.
- Generated documents and static runbooks remain useful with ordinary repository tools.
- No target marker, hidden journal, runtime, package-resolution instruction, or generated settings is needed after setup.

### Thin package-side setup over copied machinery

- Reporivet supplies deterministic audit, visible definition, one-shot setup, and explicit legacy transition only while the user invokes the package or an explicitly selected local source.
- The target project owns commands, CI, deployment, observability, backup, recovery, incidents, secrets, and evidence retention; Reporivet does not execute project commands or operate CI/deployment.
- Setup does not create command wrappers, generated workflows, background services, evidence stores, Plans, a target runtime, or Agent dispatch state.
- Reporivet provides no ongoing `doctor` or target diagnosis contract.

### Static runbooks over procedure executors

- A procedure is eligible only when exactly one complete, unique, user-confirmed strict structured record is present in `Confirmed`.
- The record has exactly nine fields: `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, and `rollback`.
- The deterministic output is ordinary Markdown at `docs/runbooks/<slug>.md`.
- A runbook has no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration. It is reviewed project documentation, not an executor.
- Incomplete, malformed, generic, inferred, Proposed, Open, Sources-only, or duplicate records produce no runbook.

### Visible evidence over inference

Every guided definition draft separates:

- **Confirmed**: facts explicitly supported by user input or cited repository evidence;
- **Proposed**: suggestions awaiting approval;
- **Open**: unresolved questions, unavailable facts, and assumptions that must not drive mutation; and
- **Sources**: paths or references that support confirmed statements.

Deterministic scan results remain observations until a person approves their use. A model is not required for scanning, drafting, previewing, or applying setup.

### Exact preview over implicit mutation

- The user sees the complete Markdown draft before setup.
- The user sees exact create, preserve, conflict, refusal, and cleanup actions before apply.
- Destructive cleanup is bound to the exact approved preview fingerprint and an external backup location.
- Apply revalidates the complete preview and all preimages immediately before mutation.
- Existing project-owned, customized, ambiguous, unsafe, symlinked, and nonregular content is preserved or refused.
- A failed transaction restores the approved preimage when safe; guarded later rollback refuses to overwrite post-success user changes.
- Backup manifests and rollback state remain external to the target.

### Bounded roles over self-approval

- Broad or multi-part roots default to `Role: Task Owner` with `May delegate: yes`; narrow or inherently serial roots remain direct nondelegating leaves.
- Main owns intent, acceptance, decomposition, root-owner dispatch, integration, serialized Plan edits, and evidence judgment; Main dispatches through host-native facilities, while Reporivet does not spawn or dispatch Agents.
- Each Owner first returns a finite child manifest inside its approved envelope. Main alone serializes accepted child rows and complete matching packets into the Plan and resumes that serialized Owner; only the resumed Task Owner dispatches its declared dependency-ready descendants.
- Descendants inherit scope, acceptance, non-goals, protected paths, child budget, and frozen interfaces. Mutable siblings use disjoint allowed-write sets and separate exact-baseline worktrees.
- Owner-local aggregation is distinct from Main's final repository integration.
- A Verification Sub starts fresh, identifies the integrated candidate, and checks each acceptance criterion independently. Verification is read-only, nonrepairing, and nondelegating; project/host workflows execute project commands.
- Reporivet provides no scheduler, dispatcher, task database, command runner, Gate, evidence archive, automatic closure, hidden state, or workflow runtime.

## Change protocol

1. Validate the selected repository root and classify relevant paths without following unsafe links.
2. Present deterministic observations in understandable language.
3. Ask guided questions in plain language; do not require the user to know the documentation schema.
4. Render one visible draft covering identity and goals, users and workflows, system boundary, quality, security, operations, and Plan working agreements.
5. Keep uncertain claims in Proposed or Open.
6. Show exact create, preserve, conflict, refuse, and opt-in actions.
7. Bind destructive transition actions to an external backup and an unchanged preview fingerprint.
8. Apply only the preview the user approved after immediate preimage revalidation.
9. Return a concise summary and route future work through canonical repository documents.

Resume must preserve the visible draft and evidence separation. Finalization must reject unresolved required fields rather than manufacture answers.

## Information design

- Use descriptive headings and explicit relative links.
- Keep current summaries short enough to route readers, while versioned records hold detail.
- Keep terminal history immutable except for explicit supersession metadata.
- Use searchable role names, task identifiers, acceptance identifiers, and path names.
- Put exact project commands in `QUALITY.md` or `OPERATIONS.md`, not in generic agent instructions.
- Label unavailable facts Open instead of substituting placeholders that look authoritative.
- Describe package-side setup as setup-time only and describe package absence after handoff as expected.

## Accessibility

- Do not rely on color, icon shape, or interface position alone to convey status.
- Prefer plain text labels such as Confirmed, Proposed, Open, accepted, failed, and not run.
- Keep headings hierarchical and tables readable as linear text.
- Give actions descriptive names and include complete command text where execution is required.
- Make errors actionable by naming the unsafe path, failed condition, and non-destructive next step.
- Avoid unnecessary jargon; define package-specific terms where first used.
- Keep static runbooks readable as ordinary Markdown without host-specific metadata.

## Non-goals

The design does not introduce:

- a general orchestration platform, scheduler, dispatcher, task store, or workflow runtime;
- hidden agent memory or autonomous Plan mutation;
- project-independent build, deployment, or incident procedures;
- provider-specific authority in canonical documents;
- a target Skill, package marker, generated settings, copied executor, or package-resolution requirement after setup;
- a compatibility layer that silently preserves retired behavior; or
- speculative configuration for projects that have not supplied facts.

### Confirmed

- Integrated `setup` is the default onboarding path; `init` is structure-only and `define` remains lower-level.
- Current setup and transition operations are preview-first and path-safe; setup creates no Plan, runtime, target Skill, marker, or generated settings.
- Canonical documents, ordinary Plans, static runbooks, Git, and project commands remain useful without an installed Reporivet package.
- The exact optional `CLAUDE.md` adapter contains only `@AGENTS.md` plus one trailing newline.
- Source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive; the record is not a continuing target-dependency claim.

### Proposed

- None.

### Open

- Publication, signing, release, deployment, CI readiness, and durable evidence archival remain unestablished or outside this design's authority.
- No release, publication, signing, or deployment readiness is established by this candidate.
- No additional host adapter is currently defined.
- Project-specific interface or service accessibility requirements are not applicable until such a surface is introduced and documented.

### Sources

- [`design-docs/DESIGN-REPORIVET-004-one-shot-setup.md`](design-docs/DESIGN-REPORIVET-004-one-shot-setup.md)
- [`product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md`](product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md)
- [`decisions/ADR-0002-one-shot-bootstrapper-boundary.md`](decisions/ADR-0002-one-shot-bootstrapper-boundary.md)
- [`references/project-definition-protocol.md`](references/project-definition-protocol.md)
- [`design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](design-docs/DESIGN-REPORIVET-003-document-first-harness.md) (historical)
- [`product-specs/SPEC-REPORIVET-003-document-first-harness.md`](product-specs/SPEC-REPORIVET-003-document-first-harness.md) (historical)
