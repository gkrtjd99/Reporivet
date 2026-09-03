---
owner: main
status: active
last_reviewed: 2026-09-02
---

# Repository Knowledge Map

This file maps current repository authority and the paths produced by the one-shot document-first setup. Reporivet creates missing project-owned documents from package assets during explicit setup; after creation, substantive repository content belongs to the target project. Setup is a bounded package-side transaction, creates no active Plan, and leaves the target independently useful when the package is removed.

The default onboarding entry point is integrated `reporivet setup`: it coordinates audit, visible guided definition, exact preview, and approved apply. `reporivet init` is structure-only and `reporivet define` remains the lower-level resumable definition interface. Setup creates no Plan or runtime, executes no project commands, and does not spawn or dispatch Agents. Main Skill creates or resumes the first ordinary Markdown Plan through the host/project workflow.

## Reading protocol

1. Start at [`../AGENTS.md`](../AGENTS.md).
2. Open the one matching Plan in [`exec-plans/active/`](exec-plans/active/), if the work is substantive.
3. Read only the current authority, code, tests, and durable records relevant to the task.
4. Use project-owned commands from [`QUALITY.md`](QUALITY.md) and [`OPERATIONS.md`](OPERATIONS.md).

Completed Plans, superseded documents, and accepted decisions are durable records, not general startup context.

## Route by work

| Work | Read first | Then narrow to |
| --- | --- | --- |
| Product behavior | [`PRODUCT.md`](PRODUCT.md) | Matching active specification and acceptance criteria. |
| Structure or dependencies | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | Matching design record, source modules, and architecture checks. |
| Implementation or verification | Matching active Plan | Task Packet, assigned code/tests, and [`QUALITY.md`](QUALITY.md). |
| Running, release, migration, or recovery | [`OPERATIONS.md`](OPERATIONS.md) | A confirmed procedure-specific static runbook when one exists. |
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
| `FRONTEND.md` | Optional project-owned frontend implementation and client-side loading, error, and retry guidance when `web_ui=yes` is explicitly Confirmed. | Created only for exact Confirmed `yes`; not a generic output and not service reliability authority. |
| `RELIABILITY.md` | Optional project-owned service/runtime reliability guidance when `deployed_runtime=yes` is explicitly Confirmed. | Created only for exact Confirmed `yes`; supplemental and subordinate to `OPERATIONS.md`, never a replacement. |

## Conditional capability artifacts

`OPERATIONS.md` is universal. The optional artifacts below are created only when the visible definition evidence contains the exact capability answer in **Confirmed**:

- `FRONTEND.md` covers frontend source ownership, framework/routing/components, state and data fetching, forms, styling, accessibility, performance, and client-side loading/error/retry behavior. It does not become service or deployed-runtime reliability guidance.
- `RELIABILITY.md` covers service/runtime failure modes, SLI/SLO, observability, deployment/rollback, recovery, and incident boundaries. It supplements and remains subordinate to `OPERATIONS.md`.

A missing, `no`, Proposed, Open, Sources-only, inferred, or otherwise unverified `web_ui` or `deployed_runtime` value creates no optional artifact. Audit output and source provenance are observations, not confirmation. Setup performs only the bounded selection/preview/apply transaction; it does not create a Plan or execute project commands. Plan state remains the host/project work record and is not capability evidence. Each optional document must cite its owner and sources, keep unsupported facts Open or Proposed, and rely on project-owned checks named by `QUALITY.md` and operational procedures named by `OPERATIONS.md`.

## Durable document families

| Path | Owner and purpose | Optionality and removal boundary |
| --- | --- | --- |
| [`product-specs/index.md`](product-specs/index.md), [`product-specs/_template.md`](product-specs/_template.md), and `product-specs/SPEC-*.md` | Project-owned requirement catalog, template, and versioned product contracts. | Individual records are created as needed; do not remove records that remain authoritative or historically referenced. |
| `product-specs/project-definition.draft.md` | Project-owned visible guided-answer and resume state created while setup or lower-level `define` is in progress; it preserves Confirmed, Proposed, Open, and Sources. | Present only while definition needs resuming; remove deliberately after approved setup and after no resume or provenance need remains. |
| [`design-docs/index.md`](design-docs/index.md), [`design-docs/_template.md`](design-docs/_template.md), and `design-docs/DESIGN-*.md` | Project-owned design catalog, template, and durable design records. | Individual records are optional; preserve accepted or superseded history while referenced. |
| [`design-docs/core-beliefs.md`](design-docs/core-beliefs.md) | Project-owned seed for durable engineering defaults shared across changes. | Keep, supersede, or remove only after current design authority and incoming links reflect the project's chosen replacement. |
| [`decisions/README.md`](decisions/README.md), [`decisions/_template.md`](decisions/_template.md), and `decisions/ADR-*.md` | Project-owned decision index, template, and append-only decision history. | ADRs are created as needed; do not rewrite accepted history to describe a later state. |
| [`exec-plans/_template.md`](exec-plans/_template.md) | Project-owned compact `format: 2` Plan contract. | Required when Plans are used; update deliberately with lifecycle policy. |
| [`exec-plans/active/`](exec-plans/active/) | Main-owned home for the one active Markdown Plan matching substantive work. | Empty when no work needs a Plan; Main alone edits shared state and moves terminal Plans. |
| [`exec-plans/completed/`](exec-plans/completed/) | Project-owned historical outcomes and verification summaries. | Do not use as startup context or rewrite historical bodies. |
| `exec-plans/active/.gitkeep` and `exec-plans/completed/.gitkeep` | Empty sentinels that make both Plan directories visible to Git before they contain records. | Remove a sentinel when the directory contains tracked Plans; do not remove the directory while the Plan lifecycle is in use. |
| [`exec-plans/tech-debt-tracker.md`](exec-plans/tech-debt-tracker.md) | Project-owned list of bounded discoveries that were not implemented in their originating task. | Keep only while tracked items remain useful; it is not a second task system. |
| [`references/README.md`](references/README.md), [`references/project-definition-protocol.md`](references/project-definition-protocol.md), and other reference notes | Project-owned protocol and reusable explanatory material. | Add only when a durable reference is needed; remove only after repairing current links. |
| [`runbooks/index.md`](runbooks/index.md), [`runbooks/_template.md`](runbooks/_template.md), and `runbooks/<slug>.md` | Project-owned catalog, template, and ordinary Markdown procedure runbooks subordinate to `OPERATIONS.md`. | A project may have no separate runbooks; remove obsolete runbooks only after current operational links and ownership are resolved. |

A complete, unique, user-confirmed strict nine-field procedure record is the only Reporivet procedure input that produces a runbook. The fields are `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, and `rollback`. The output is ordinary Markdown under `docs/runbooks/<slug>.md`, with no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration. Incomplete, malformed, generic, inferred, Proposed, Open, Sources-only, or duplicate records produce no runbook.

Setup may create the empty `docs/exec-plans/active/` and `docs/exec-plans/completed/` directories so Plan movement remains explicit and inspectable, but it does not create a Plan file. The Main Skill searches active and completed history, resumes one matching active Plan, or creates the first ordinary Markdown Plan with the lowest unused current-year ID.

## Retired paths and host boundary

The following are not fresh generated outputs: `/.reporivet-version`, Reporivet role or procedure Skills under `/.claude/skills/`, generated `/.claude/settings.json`, and the old managed `/.gitignore` block. An explicit setup rerun may inspect a legacy path only as a transition candidate when exact canonical ownership evidence proves that Reporivet created it. Exact bytes or a strict parse-and-rerender proof are required; names, markers, frontmatter, or location alone are insufficient. Modified, unknown, ambiguous, unsafe, symlinked, nonregular, and project-owned paths are preserved or refused.

Destructive transition cleanup is bound to an exact visible setup preview, requires an absolute external backup, revalidates the target preimages immediately before mutation, restores the whole transaction after a safe failure, and refuses later rollback when a successful postimage has changed. Backup manifests and rollback state remain outside the target. No Reporivet role/procedure Skill, target runtime, doctor command, package-resolution instruction, or hidden journal is generated.

The optional root [`../CLAUDE.md`](../CLAUDE.md) is a thin host adapter whose entire content is `@AGENTS.md` plus one trailing newline. An optional external user-scoped `/reporivet-setup` wrapper is outside this target tree; it is instruction-only, only relays the deterministic setup preview/apply flow, never installs or resolves Reporivet, and never edits target files itself. Removing the adapter or package does not remove canonical documents or project-owned evidence.

## Dogfood-only retained paths

This repository predates the one-shot boundary and intentionally retains two project-owned surfaces that fresh setup does not receive:

- `dev/harness.toml` is inactive legacy configuration, not execution authority. Current work takes commands from [`QUALITY.md`](QUALITY.md) and [`OPERATIONS.md`](OPERATIONS.md).
- `.harness/runs` is retired historical sensitive state. Current code does not read its contents, write that path, or delete that path. Do not use it as current evidence or working storage.

Their presence here does not expand the generated product surface.

## Retained historical generated records

`docs/generated/**` and `docs/module-contracts/**` are retained historical/superseded records from retired generated code-map and module-contract surfaces. They are not current routing, package inputs, or setup outputs. Do not use their old commands or contracts; route through this map, current authority documents, and the active Plan instead. Their bodies remain available for historical readability and are not current evidence.

## Evidence states

- **Confirmed** contains explicit user input or attributable repository facts that support current work.
- **Proposed** contains suggestions and deterministic observations awaiting approval.
- **Open** contains missing, uncertain, conflicting, or unavailable facts that must not be treated as authority.
- **Sources** names the paths or references supporting the other sections.

Keep all four states visibly separate in guided drafts and current authority. Scanner inference never enters Confirmed automatically.

## Boundary

The durable product is project-owned Markdown authority, ordinary Plans, static runbooks, and an optional exact host adapter. Reporivet temporarily supplies deterministic audit, visible definition, and one-shot setup from an installed package or explicitly selected local source, plus a separately invoked legacy transition transaction when needed. It provides no ongoing diagnosis contract. The target repository owns its commands, tests, CI, deployment, operations, secrets, and acceptance evidence. Removing the package after setup is expected and leaves generated Markdown, Plans, runbooks, Git, and project commands useful.

### Confirmed

- Integrated `setup` is the default onboarding path; `init` remains structure-only and `define` remains available at lower level.
- Current setup creates missing document-first assets without overwriting project-owned content, creates no Plan, and ends as a package-independent target handoff.
- Fresh setup creates neither a target Skill, marker, generated settings, runtime, nor hidden state; complete unique Confirmed procedures alone produce static runbooks.
- The exact root `CLAUDE.md` adapter is optional and contains only `@AGENTS.md` plus one trailing newline.
- Package absence after approved setup is expected and is not `UNKNOWN`, blocking, or a residual risk for ordinary target work.

### Proposed

- None.

### Open

- Project-specific runbooks may be added when confirmed procedures exceed the scope of `OPERATIONS.md`.

### Sources

- [`decisions/ADR-0002-one-shot-bootstrapper-boundary.md`](decisions/ADR-0002-one-shot-bootstrapper-boundary.md)
- [`product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md`](product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md)
- [`design-docs/DESIGN-REPORIVET-004-one-shot-setup.md`](design-docs/DESIGN-REPORIVET-004-one-shot-setup.md)
- [`PLANS.md`](PLANS.md)
- [`decisions/ADR-0001-document-first-product-boundary.md`](decisions/ADR-0001-document-first-product-boundary.md) (historical)
