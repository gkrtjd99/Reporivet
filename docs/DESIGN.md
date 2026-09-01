---
owner: design
status: active
last_reviewed: 2026-08-31
---

# Design

## Design direction and accessibility

Reporivet favors rich, inspectable repository knowledge and thin execution. The installed package helps a maintainer establish or migrate the contract; the repository then explains itself through Markdown and runs through project-owned tools.

The previously verified document-first source behavior exists. For source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4`, the recorded isolated pipx and pip install/use/uninstall lifecycle passed. The verification artifacts are temporary and are not a durable or downloadable evidence archive; this design does not establish publication, signing, release, deployment, or CI readiness.

The default onboarding design is integrated `reporivet setup`; `reporivet init` remains structure-only and `reporivet define` remains the lower-level resumable interface. Setup does not create a Plan or runtime, spawn or dispatch Agents, or execute project commands. Main Skill creates or resumes the first ordinary Markdown Plan. Complete user-confirmed structured procedures may create instruction-only project Skills only through resumed setup.

The design optimizes for safe adoption, agent legibility, human review, and useful operation after package removal.

## Durable defaults

### Canonical authority over duplicated instructions

- `AGENTS.md` is the host-neutral entry point.
- `docs/README.md` maps current authority and generated surfaces.
- One matching active Plan carries substantive work state.
- Versioned specifications, designs, decisions, and completed Plans preserve durable context without becoming general startup material.
- Host adapters remain thin and removable; they must not become alternate product authority.

### Rich content over hidden state

- Product intent, system structure, quality, security, operations, decisions, work state, and evidence stay in readable Markdown.
- A Plan contains one task table and matching Task Packets rather than referring to a separate task database.
- Main records decisions, discoveries, integration, verification, and terminal outcome in the Plan.
- Generated documents remain useful with ordinary repository tools.

### Thin execution over copied machinery

- Reporivet supplies package-side integrated setup, lower-level definition, diagnosis, and explicit migration only while installed.
- The target project owns commands, CI, deployment, observability, backup, recovery, incidents, secrets, and evidence retention; Reporivet does not execute project commands or operate CI/deployment.
- Setup does not create command wrappers, generated workflows, background services, evidence stores, Plans, or a target runtime.
- A complete user-confirmed structured procedure may produce a deterministic, instruction-only project Skill through resumed setup; incomplete or inferred procedures do not. Such Skills may summarize a supported procedure, but they may not spawn/dispatch Agents, embed an executor, copied model bundle, hidden state, or alternate completion authority.

### Visible evidence over inference

Every guided definition draft separates:

- **Confirmed**: facts explicitly supported by user input or cited repository evidence;
- **Proposed**: suggestions awaiting approval;
- **Open**: unresolved questions, unavailable facts, and assumptions that must not drive mutation;
- **Sources**: paths or references that support confirmed statements.

Deterministic scan results remain observations until a person approves their use. A model is not required for scanning, drafting, previewing, or applying setup.

### Exact preview over implicit mutation

- The user sees the complete Markdown draft before setup.
- The user sees exact path actions before apply.
- Apply revalidates the approved inputs instead of trusting an old preview.
- Existing project-owned or ambiguous content is preserved.
- Migration requires an external backup and refuses unsafe rollback.
- Optional host settings are shown exactly and never merged into an existing file.

### Bounded roles over self-approval

- Broad or multi-part roots default to `Role: Task Owner` with `May delegate: yes`; narrow or inherently serial roots remain direct nondelegating leaves.
- Main owns intent, acceptance, decomposition, root-owner dispatch, integration, serialized Plan edits, and evidence judgment; Main dispatches independent root Owners concurrently, while Reporivet does not spawn or dispatch Agents.
- Each Owner first returns a finite child manifest inside its approved envelope. Main alone serializes accepted child rows and complete matching packets into the Plan and resumes that serialized Owner; only the resumed Task Owner dispatches its declared dependency-ready descendants. Ordinary leaves never delegate.
- Descendants inherit scope, acceptance, non-goals, protected paths, child budget, and frozen interfaces. Mutable siblings use disjoint allowed-write sets and separate exact-baseline worktrees. Owner-local aggregation is distinct from Main's final repository integration.
- A Verification Sub starts fresh, identifies the integrated candidate, and checks each acceptance criterion independently. Verification is read-only, nonrepairing, and nondelegating; Reporivet does not execute those project checks.
- Verification narration is not evidence; command output, inspected behavior, and explicit residual risks are. Reporivet provides no scheduler, dispatcher, task database, command runner, Gate, evidence archive, automatic closure, hidden state, or workflow runtime.

## Change protocol

1. Validate the selected repository root and classify relevant paths without following unsafe links.
2. Present deterministic observations in understandable language.
3. Ask guided questions in plain language; do not require the user to know the documentation schema.
4. Render one visible draft covering identity and goals, users and workflows, system boundary, quality, security, operations, and Plan working agreements.
5. Keep uncertain claims in Proposed or Open.
6. Show exact create, preserve, refuse, and opt-in actions.
7. Apply only the preview the user approved.
8. Return a concise summary and route future work through canonical repository documents.

Resume must preserve the visible draft and evidence separation. Finalization must reject unresolved required fields rather than manufacture answers.

## Information design

- Use descriptive headings and explicit relative links.
- Keep current summaries short enough to route readers, while versioned records hold detail.
- Keep terminal history immutable except for explicit supersession metadata.
- Use searchable role names, task identifiers, acceptance identifiers, and path names.
- Put exact commands in `QUALITY.md` or `OPERATIONS.md`, not in generic agent instructions.
- Label unavailable facts Open instead of substituting placeholders that look authoritative.

## Accessibility

- Do not rely on color, icon shape, or interface position alone to convey status.
- Prefer plain text labels such as Confirmed, Proposed, Open, accepted, failed, and not run.
- Keep headings hierarchical and tables readable as linear text.
- Give actions descriptive names and include complete command text where execution is required.
- Make errors actionable by naming the unsafe path, failed condition, and non-destructive next step.
- Avoid unnecessary jargon; define package-specific terms where first used.

## Non-goals

The design does not introduce:

- a general orchestration platform;
- hidden agent memory or autonomous Plan mutation;
- project-independent build, deployment, or incident procedures;
- provider-specific authority in canonical documents;
- a compatibility layer that silently preserves retired behavior;
- speculative configuration for projects that have not supplied facts.

### Confirmed

- Integrated `setup` is the default onboarding path; `init` is structure-only and `define` remains lower-level.
- Current setup and migration are preview-first and path-safe; setup creates no Plan or runtime.
- Canonical documents, ordinary Plans, project Skills, Git, and project commands remain useful without an installed Reporivet package.
- Claude integration and confirmed-procedure Skills are instruction-only and removable; deny-only settings are opt-in.
- Source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive.

### Proposed

- None.

### Open

- Publication, signing, release, deployment, CI readiness, and durable evidence archival remain unestablished or outside this design's authority.
- No release, publication, signing, or deployment readiness is established by this candidate.
- No additional host adapter is currently defined.
- Project-specific interface or service accessibility requirements are not applicable until such a surface is introduced and documented.

### Sources

- [`design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](design-docs/DESIGN-REPORIVET-003-document-first-harness.md)
- [`product-specs/SPEC-REPORIVET-003-document-first-harness.md`](product-specs/SPEC-REPORIVET-003-document-first-harness.md)
- [`decisions/ADR-0001-document-first-product-boundary.md`](decisions/ADR-0001-document-first-product-boundary.md)
- [`references/project-definition-protocol.md`](references/project-definition-protocol.md)
