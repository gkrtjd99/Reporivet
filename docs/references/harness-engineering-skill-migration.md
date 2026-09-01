---
id: REF-REPORIVET-002
kind: reference
status: active
owner: main
area: harness
updated: 2026-08-31
---

# HarnessEngineeringSkill Migration Boundary

## Upstream reference

- Repository: `https://github.com/gkrtjd99/HarnessEngineeringSkill`
- Default branch inspected: `main`
- Pinned commit: `dd5989d4f9de5646349b3bceec4e19806262d14d`
- Commit timestamp: `2026-07-14T06:09:25Z`
- Inspection mode: public, read-only GitHub API reads; no clone, fetch, checkout, write, backup, archive, or deletion
- Historical Reporivet Plan: [`PLAN-2026-0002`](../exec-plans/completed/PLAN-2026-0002-integrate-definition-and-retire-skill.md)

This reference records which ideas were retained from the upstream Skill and which deployment surfaces remain rejected. Current behavior is governed by [`../../AGENTS.md`](../../AGENTS.md), [`../README.md`](../README.md), the active document-first specification and design, and package code. The default onboarding path is integrated `reporivet setup`; `reporivet init` is structure-only and `reporivet define` remains lower-level.

## Current rule

A **project-owned procedural Skill is allowed** when it is instruction-only, bounded to a named role or repeatable procedure, routes to canonical repository authority, states permissions and stop conditions, and remains removable without damaging project knowledge or execution.

A **copied target bundle is rejected** when it embeds an executor, command registry, synchronized host trees, model prompt bundle, evaluator or judge, hidden state, or alternate completion authority inside the target repository.

The distinction is ownership and behavior, not the filename `SKILL.md`:

- acceptable Skills adapt host interaction to project-owned Markdown and project-owned tools;
- rejected bundles duplicate product authority, perform target execution, coordinate hidden state, or require a model-backed validation path.

## Retained capabilities

| Upstream need | Current disposition | Current Reporivet boundary |
| --- | --- | --- |
| Guided project definition | Adapt | Integrated `reporivet setup` is the default; lower-level `reporivet define` asks seven fixed plain-language topics and keeps one visible Markdown draft. |
| Existing-project scan | Replace | `reporivet audit` performs deterministic, read-only inventory without executing project commands. |
| Confirmed, Proposed, Open, and Sources separation | Absorb | Guided drafts preserve all four sections exactly; blank answers remain Open and scanner observations remain Proposed. |
| Interruptible continuation | Absorb | The visible draft is the only resume state; there is no hidden interview database or journal. |
| Product-to-acceptance traceability | Adapt | Project specifications retain stable journeys, requirements, acceptance criteria, and sources in Markdown. |
| Main, implementation, and verification roles | Absorb | `AGENTS.md`, compact Plans, and bounded Task Packets define role ownership and independent evidence. |
| Durable Plans | Adapt | One compact `format: 2` Markdown Plan carries task state, packets, checkpoint, integration, verification, and outcome. |
| Repository safety and validation | Replace | Package-side root/path safety, preview approval, doctor, project-owned checks, and independent verification cover the current boundary. |
| Starter material | Replace | Package assets create missing document-first authority and optional adapters without copying an executor. |
| Repeatable project procedures | Adapt | Through resumed `setup`, a project may create an instruction-only Skill only after a complete user-confirmed strict structured record contains exactly these nine fields: `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, and `rollback`. All nine fields are required; no additional fields or aliases are accepted, and no values or defaults are inferred. Incomplete, inferred, generic, Proposed, Open, or Sources-only records create none. |
| Host-specific role guidance | Adapt | The optional Claude profile contains a thin `CLAUDE.md` import and three instruction-only role Skills owned by the target after creation. |

## Allowed procedural Skills

A procedural Skill must:

1. identify the canonical document or project-owned command it is adapting;
2. keep its `reads`, `actions`, `permissions`, and `stop_conditions` explicit;
3. avoid secrets and avoid embedding private repository content;
4. leave durable decisions, work state, and evidence in the Plan or current authority rather than Skill-local state;
5. avoid self-approval and preserve fresh-context verification where required;
6. remain optional and removable without making the repository unusable;
7. be tested as instructions and reviewed when its referenced procedure changes.

The default Claude role Skills satisfy this boundary by routing Main, implementation, and verification behavior. A project may add another Skill only for a complete, user-confirmed project-owned procedure through resumed setup; Reporivet does not generate generic procedure Skills from guesses. The Main Skill, not Reporivet setup, creates or resumes the first ordinary Markdown Plan.

## Rejected copied bundles

Reporivet does not adopt or recreate:

- synchronized target directories for multiple agent hosts;
- copied command executors, wrappers, command registries, or maintenance programs;
- host prompt packs that duplicate `AGENTS.md` or current documents;
- model files, provider configuration, model-backed runners, judges, or trajectory evaluators;
- hidden interview state, journals, task databases, schedulers, daemons, or orchestration services;
- generated project CI, evidence archives, or automatic Plan mutation;
- Agent spawn/dispatch, project command execution, scheduler, task database, hidden state, Gate, publication, signing, or release machinery;
- blanket module contracts, code maps, or configuration unsupported by confirmed project facts.

Deterministic project checks and human or fresh-agent review may assess semantics, but no bundled model dependency becomes a prerequisite for setup or verification.

## Current package-side migration

```text
upstream scan or starter copy
    -> package-side deterministic audit
    -> plain-language guided answers
    -> visible evidence-separated Markdown draft
    -> exact document/adaptor preview
    -> explicit approved apply
    -> project-owned documents, Plans, commands, and optional Skills
```

For recognized legacy Reporivet 0.2 targets, migration is a separate external-backup transaction documented in [`../OPERATIONS.md`](../OPERATIONS.md). It retires owned legacy execution surfaces, preserves project-owned or ambiguous content, and retains historical sensitive state without reading its contents. Ordinary setup does not silently perform that migration.

## Authority and non-authorization

- Product boundary: [`../PRODUCT.md`](../PRODUCT.md) and [`../product-specs/SPEC-REPORIVET-003-document-first-harness.md`](../product-specs/SPEC-REPORIVET-003-document-first-harness.md)
- Architecture and ownership: [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)
- Design: [`../DESIGN.md`](../DESIGN.md) and [`../design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](../design-docs/DESIGN-REPORIVET-003-document-first-harness.md)
- Quality: [`../QUALITY.md`](../QUALITY.md)
- Operations and migration: [`../OPERATIONS.md`](../OPERATIONS.md)
- Security: [`../SECURITY.md`](../SECURITY.md)
- Planning: [`../PLANS.md`](../PLANS.md)

Public installation guidance is pipx-primary with pip supported from the same wheel. The completed PLAN-2026-0003 records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive. Uninstall must leave generated Markdown, ordinary Plans, Skills, Git, and project commands useful. No statement in this reference authorizes an external write, publication, deployment, signing, or release action against the upstream repository.
