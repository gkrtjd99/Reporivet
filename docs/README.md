---
owner: main
status: active
last_reviewed: 2026-08-31
---

# Repository Knowledge Map

This file maps current repository authority and every path family produced by the document-first setup. Reporivet creates missing files from package assets; after creation, substantive repository content is project-owned. Existing project-owned or ambiguous files are preserved rather than silently replaced.

The default onboarding entry point is integrated `reporivet setup`: it coordinates audit, visible guided definition, exact preview, and approved apply. `reporivet init` is structure-only and `reporivet define` remains the lower-level resumable definition interface. Setup creates no Plan or runtime, executes no project commands, and does not spawn or dispatch Agents. Main Skill creates or resumes the first ordinary Markdown Plan.

## Reading protocol

1. Start at [`../AGENTS.md`](../AGENTS.md).
2. Open the one matching Plan in [`exec-plans/active/`](exec-plans/active/), if the work is substantive.
3. Read only the current authority, code, tests, and durable records relevant to the task.
4. Use project-owned commands from [`QUALITY.md`](QUALITY.md) and [`OPERATIONS.md`](OPERATIONS.md).

Completed Plans, superseded documents, and accepted decisions are durable records, not general startup context.

## Route by work

| Work | Read first | Then narrow to |
| --- | --- | --- |
| Product behavior | [`PRODUCT.md`](PRODUCT.md) | Matching current specification and acceptance criteria. |
| Structure or dependencies | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | Matching design record, source modules, and architecture checks. |
| Implementation or verification | Matching active Plan | Task Packet, assigned code/tests, and [`QUALITY.md`](QUALITY.md). |
| Running, release, migration, or recovery | [`OPERATIONS.md`](OPERATIONS.md) | A confirmed procedure-specific runbook when one exists. |
| Security-sensitive work | [`SECURITY.md`](SECURITY.md) | Applicable threat boundary, policy, code, and tests. |
| Durable decision or historical outcome | Current summary first | Relevant ADR, completed Plan, or superseded record only after current routing. |

## Canonical paths

| Path | Owner and purpose | Optionality and removal boundary |
| --- | --- | --- |
| [`../AGENTS.md`](../AGENTS.md) | Project-owned, host-neutral agent entry point and role contract. | Required while the document-first operating contract is in use. |
| [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | Project-owned current structure, ownership, and dependency direction. | Required current authority. |
| [`README.md`](README.md) | Project-owned knowledge map and generated-surface inventory. | Required current authority. |
| [`PRODUCT.md`](PRODUCT.md) | Project-owned current product intent, boundary, requirements, and evidence classes. | Required current authority. |
| [`DESIGN.md`](DESIGN.md) | Project-owned current design principles and accessibility expectations. | Required current authority. |
| [`QUALITY.md`](QUALITY.md) | Project-owned source of truth for local checks and acceptance evidence. | Required current authority. |
| [`OPERATIONS.md`](OPERATIONS.md) | Project-owned sole current authority for running, releasing, observing, backup, rollback, recovery, and incidents. | Required current authority. Remove only with an explicit replacement and repaired links. |
| [`SECURITY.md`](SECURITY.md) | Project-owned security boundary and reporting route. | Required current authority. |
| [`PLANS.md`](PLANS.md) | Project-owned compact Plan lifecycle and role rules. | Required current authority while Plans coordinate substantive work. |

## Durable document families

| Path | Owner and purpose | Optionality and removal boundary |
| --- | --- | --- |
| [`product-specs/index.md`](product-specs/index.md), [`product-specs/_template.md`](product-specs/_template.md), and `product-specs/SPEC-*.md` | Project-owned requirement catalog, template, and versioned product contracts. | Individual records are created as needed; do not remove records that remain authoritative or historically referenced. |
| `product-specs/project-definition.draft.md` | Project-owned visible guided-answer and resume state created by integrated `setup` or lower-level `define start`; it preserves Confirmed, Proposed, Open, and Sources. | Present only while guided definition is in progress or needs resuming. Remove deliberately only after approved setup and after no resume or provenance need remains. |
| [`design-docs/index.md`](design-docs/index.md), [`design-docs/_template.md`](design-docs/_template.md), and `design-docs/DESIGN-*.md` | Project-owned design catalog, template, and durable design records. | Individual records are optional; preserve accepted or superseded history while referenced. |
| [`design-docs/core-beliefs.md`](design-docs/core-beliefs.md) | Project-owned seed for durable engineering defaults shared across changes. | Keep, supersede, or remove only after current design authority and incoming links reflect the project's chosen replacement. |
| [`decisions/README.md`](decisions/README.md), [`decisions/_template.md`](decisions/_template.md), and `decisions/ADR-*.md` | Project-owned decision index, template, and append-only decision history. | ADRs are created as needed; do not rewrite accepted history to describe a later state. |
| [`exec-plans/_template.md`](exec-plans/_template.md) | Project-owned compact `format: 2` Plan contract. | Required when Plans are used; update deliberately with lifecycle policy. |
| [`exec-plans/active/`](exec-plans/active/) | Main-owned home for the one active Markdown Plan matching substantive work. | Empty when no work needs a Plan; Main alone edits shared state and moves terminal Plans. |
| [`exec-plans/completed/`](exec-plans/completed/) | Project-owned historical outcomes and verification summaries. | Do not use as startup context or rewrite historical bodies. |
| `exec-plans/active/.gitkeep` and `exec-plans/completed/.gitkeep` | Reporivet-created empty sentinels that make both Plan directories visible to Git before they contain records. | Remove a sentinel when the directory contains tracked Plans; do not remove the directory while the Plan lifecycle is in use. |
| [`exec-plans/tech-debt-tracker.md`](exec-plans/tech-debt-tracker.md) | Project-owned list of bounded discoveries that were not implemented in their originating task. | Keep only while tracked items remain useful; it is not a second task system. |
| [`references/README.md`](references/README.md), [`references/project-definition-protocol.md`](references/project-definition-protocol.md), and other reference notes | Project-owned protocol and reusable explanatory material. | Add only when a durable reference is needed; remove only after repairing current links. |
| [`runbooks/index.md`](runbooks/index.md), [`runbooks/_template.md`](runbooks/_template.md), and `runbooks/RUNBOOK-*.md` | Project-owned catalog, template, and optional procedure-specific runbooks subordinate to `OPERATIONS.md`. | A project may have no separate runbooks. Remove obsolete runbooks only after current operational links and ownership are resolved. |

The setup may also create the empty `docs/exec-plans/active/` and `docs/exec-plans/completed/` directories so Plan movement remains explicit and inspectable, but it does not create a Plan file. The Main Skill searches active and completed history, resumes one matching active Plan, or creates the first ordinary Markdown Plan with the lowest unused current-year ID.

## Hidden metadata and host adapters

| Path | Owner and purpose | Optionality and removal boundary |
| --- | --- | --- |
| `/.reporivet-version` | Reporivet-owned format marker used by package maintenance and diagnosis. It is not project authority. | Keep while using package-side maintenance. Remove only after intentionally ending that relationship; removing it does not remove project documents. |
| `/.gitignore` managed block | Bounded Reporivet block that ignores only machine-local Claude settings while keeping shared Skills and approved project settings visible. Content outside the block remains project-owned. | Keep while that local-settings rule applies. Remove only the managed block, never unrelated ignore rules, when the host integration is intentionally retired. |
| [`../CLAUDE.md`](../CLAUDE.md) | Thin Claude host adapter whose entire content is `@AGENTS.md` plus one trailing newline. | Host-specific and operationally optional. Remove it when Claude is not a supported host; canonical authority remains in `AGENTS.md`. |
| `/.claude/skills/reporivet-main/SKILL.md` | Instruction-only adapter for the Main role. | Host-specific and removable with the Claude profile; it must not become a copied executor or alternate authority. |
| `/.claude/skills/reporivet-implementation/SKILL.md` | Instruction-only adapter for bounded implementation work. | Host-specific and removable with the Claude profile; task authority remains in the Plan packet. |
| `/.claude/skills/reporivet-verification/SKILL.md` | Instruction-only adapter for fresh-context verification. | Host-specific and removable with the Claude profile; project checks remain in `QUALITY.md`. |
| `/.claude/skills/<project-procedure>/SKILL.md` | Optional instruction-only adapter for one complete, user-confirmed structured project procedure created through resumed setup. | Project-owned and removable; incomplete, inferred, generic, Proposed, Open, or Sources-only records create none, and the Skill never executes commands or stores state. |
| `/.claude/settings.json` | Optional deny-only defense-in-depth settings shown in an exact preview. | Not generated by default. Creation requires explicit approval; an existing file is never merged or rewritten. Remove only after reviewing the host-side protection being withdrawn. |

The Claude adapter and Skills are part of the default Claude-profile output when their paths are missing, but they remain removable host integration rather than product authority. Removing an adapter must not delete the canonical Markdown documents or project-owned evidence.

## Dogfood-only retained paths

This repository predates the document-first boundary and intentionally retains two project-owned surfaces that fresh installs do not receive:

- `dev/harness.toml` is inactive as an execution authority. Current work takes commands from `docs/QUALITY.md` and `docs/OPERATIONS.md`, and new document-first installs do not generate this file.
- `.harness/runs` is retired historical sensitive state. Current code does not read its contents. Current code does not write that path. Current code does not delete that path. Do not use it as current evidence or working storage.

Their presence here does not expand the generated product surface.

## Retained historical generated records

`docs/generated/**` and `docs/module-contracts/**` are retained historical/superseded records from the retired generated code-map and module-contract surfaces. They are not current routing, package inputs, or setup outputs. Do not use their old commands or contracts; route through this map, the current authority documents, and the active Plan instead. Their bodies remain available for historical readability and are not current evidence.

## Evidence states

- **Confirmed** contains explicit user input or attributable repository facts that support current work.
- **Proposed** contains suggestions and deterministic observations awaiting approval.
- **Open** contains missing, uncertain, conflicting, or unavailable facts that must not be treated as authority.
- **Sources** names the paths or references supporting the other sections.

Keep all four states visibly separate in guided drafts and current authority. Scanner inference never enters Confirmed automatically.

## Boundary

The durable product is Markdown authority, ordinary Plans, and optional host/procedure adapters. Reporivet temporarily supplies deterministic scan, integrated setup, lower-level definition, migration, and diagnosis from the installed package. The target repository owns its commands, tests, CI, deployment, operations, secrets, and acceptance evidence. Removing the package must leave generated Markdown, Plans, Skills, Git, and project commands useful.

### Confirmed

- Integrated `setup` is the default onboarding path; `init` remains structure-only and `define` remains available at lower level.
- Current setup creates missing document-first assets without overwriting project-owned content and creates no Plan or runtime.
- Fresh setup creates neither a `dev/` command surface nor a `.harness/` state tree; complete user-confirmed structured procedures alone may create instruction-only project Skills through resumed setup.
- Claude settings remain opt-in and require exact preview approval.
- Generated Markdown, Plans, Skills, Git, and project commands remain useful after uninstall.

### Proposed

- None.

### Open

- Project-specific runbooks may be added when confirmed procedures exceed the scope of `OPERATIONS.md`.

### Sources

- [`product-specs/SPEC-REPORIVET-003-document-first-harness.md`](product-specs/SPEC-REPORIVET-003-document-first-harness.md)
- [`design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](design-docs/DESIGN-REPORIVET-003-document-first-harness.md)
- [`decisions/ADR-0001-document-first-product-boundary.md`](decisions/ADR-0001-document-first-product-boundary.md)
