---
id: ADR-0001
kind: decision
status: accepted
area: harness
summary: Keep Reporivet as a repository-native document-first harness with an independent copied runtime
applies_to:
  - "AGENTS.md"
  - "ARCHITECTURE.md"
  - "docs/**"
  - "dev/**"
  - "src/reporivet/**"
supersedes: []
superseded_by:
---

# Repository-native harness boundary

## Context

Reporivet initializes and maintains a repository that must remain understandable and usable across sessions, hosts, and package-installation states. The installed initializer can safely render files, but ordinary target work must not depend on a continuing package process, provider-specific instructions, an external task service, or a model service. The target repository already has a durable document surface, deterministic `dev/*` commands, an ExecPlan lifecycle, and a copied runtime that can carry the operating contract forward.

The boundary is consequential: replacing the repository-local runtime with a one-shot bootstrapper or a provider-specific bundle would change the product, ownership model, recovery path, and package-removal contract. Such a change must therefore explicitly supersede this decision rather than being introduced through incidental template or documentation edits.

## Decision

Reporivet is a general-purpose, repository-native, document-first agent-harness initializer with two explicit lifetimes:

- `AGENTS.md` is the generated repository's concise, provider-neutral entry point and common operating contract.
- Durable project knowledge belongs in project-owned Markdown under `docs/`, including current-state authority, specifications, designs, decisions, runbooks, and ExecPlans.
- Complex work is represented by a repository-owned ExecPlan; Main and Sub responsibilities are expressed in that contract rather than in a hidden scheduler or task database.
- Verification is exposed through the project-owned `dev/harness.toml` and deterministic `dev/*` interfaces, including the copied `dev/harness.py`, `./dev/check`, `./dev/verify`, and `./dev/close-plan`.
- A generated repository remains operational after the installed `reporivet` package is removed. Its copied runtime may use the Python standard library, repository files, local Git, and explicitly configured project commands, but it must not import the installed package.
- The initializer owns package-side rendering, ownership-aware initialization and upgrade, audit/adoption entry points, and diagnostics; it does not become a continuing target runtime or external orchestration service.
- Project-owned documents and configuration are preserved during upgrade. Managed artifacts are refreshed only within their explicit ownership boundary.
- Scanner observations and inferences remain evidence for review and never become normative project authority automatically.
- Reporivet adds no required external daemon, scheduler, task database, provider-specific LLM plugin, model judge, or remote state service.

## Consequences

### Positive

- Target repositories retain a portable, inspectable operating contract after package removal.
- Agents can resume from ordinary version-controlled documents, plans, local commands, and Git history without hidden state.
- Project intent and configuration remain owned by the project instead of being overwritten by an initializer upgrade.
- Provider-neutral boundaries avoid coupling the generated repository to one host, model, plugin, or external service.
- Verification, evidence, and recovery behavior remain testable through deterministic repository-local interfaces.

### Negative and risks

- The package-side initializer and copied runtime are separate lifetimes, so their observable behavior and managed assets require parity tests.
- Repository-local commands inherit the caller's environment and permissions; they cannot replace human judgment about product intent, semantic completeness, or REVIEW acceptance.
- The current generated wrappers are POSIX shell scripts, and optional smoke coverage remains project-specific.
- Changes crossing runtime, ownership, verification, CI, or security boundaries are intentionally wide and require explicit review evidence.

## Alternatives considered

- **One-shot document bootstrapper:** Rejected because removing the repository-local runtime would make ordinary target work depend on the package or host after initialization and would discard the existing package-removal contract.
- **Provider-specific Skill or plugin bundle:** Rejected because it duplicates ownership and installation state and makes a general-purpose target depend on one host integration.
- **External daemon, scheduler, or task database:** Rejected because repository-owned Markdown plans and deterministic commands provide durable, inspectable state without another runtime or service.
- **Installed package as the target runtime:** Rejected because package availability, version drift, and environment access would become prerequisites for repository operation.

## Verification and retirement

- `./dev/check` and `./dev/verify` must keep the fixed repository-local command boundary, reject recursive verification, and preserve inspectable run artifacts.
- The distribution regression must build and inspect the wheel, exercise an installed initializer, uninstall Reporivet, and prove that generated `dev/context`, `dev/check`, `dev/verify`, planning, and closure operations still work locally.
- The copied runtime and package assets must remain free of a runtime import edge back to `reporivet`; CI must retain explicit target evidence, immutable actions, read-only contents permission, and artifact upload on success or failure.
- If a future product decision changes this boundary, add an accepted ADR that names `ADR-0001` in `supersedes`, records the replacement and migration/recovery consequences, and removes or updates current references only as part of that approved change. Do not rewrite this accepted record.

Related authority: [`ARCHITECTURE.md`](../../ARCHITECTURE.md), [`QUALITY.md`](../QUALITY.md), and [`DESIGN-REPORIVET-001`](../design-docs/DESIGN-REPORIVET-001-initializer-and-runtime.md).
