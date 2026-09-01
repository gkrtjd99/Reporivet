---
owner: product
status: active
last_reviewed: 2026-08-31
---

# Product

## Product, users, problem, and success

Reporivet is a Python package that helps establish and safely maintain a repository-local, document-first operating contract for coding agents. It performs deterministic discovery, guided definition, setup, explicit migration, and diagnosis from the installed package. The durable result is rich project-owned Markdown authority, compact Plans, and optional thin host adapters.

Reporivet is not a permanent executor inside the target repository. The project retains ownership of commands, tests, CI, deployment, secrets, operations, and acceptance evidence.

## Default onboarding and handoff

`reporivet setup` is the default integrated onboarding path. It coordinates deterministic audit, visible guided definition, resumable answers, exact preview, and explicitly approved application. `reporivet init` remains a structure-only, non-overwriting create-if-missing path. Lower-level `reporivet define` remains available for direct draft/resume/status/finalize work.

Setup does not execute project commands, spawn or dispatch Agents, or create a Plan or runtime. The Main Skill searches active and completed history, resumes one matching active ordinary Markdown Plan, or creates the first Plan with the lowest unused current-year ID from the project template. A complete user-confirmed structured procedure may generate one deterministic, instruction-only project Skill only through resumed setup; incomplete, inferred, generic, Proposed, Open, and Sources-only records generate none.

Public installation guidance is pipx-primary (`pipx install reporivet`), with pip supported from the same wheel (`python -m pip install reporivet`). Source-checkout commands are contributor-only.

## Users and needs

- **Repository maintainers** need an inspectable operating contract that survives package removal.
- **Main agents** need canonical routing, one durable work record, bounded delegation, and explicit evidence ownership.
- **Implementation agents** need narrow Task Packets with exact reads, allowed writes, protected paths, acceptance criteria, and stop conditions.
- **Verification agents and reviewers** need fresh-context, criterion-level evidence tied to an identifiable integrated candidate.

## Current scope

The installed package may:

- scan a repository deterministically without sending project content to a model;
- coordinate the default integrated `setup` flow while retaining lower-level `define`;
- collect plain-language answers through guided definition;
- render a visible Markdown draft with separated evidence classes;
- show an exact setup or migration preview;
- apply only the approved preview after safety revalidation;
- create missing document-first assets and optional host adapters;
- render an instruction-only project Skill only for a complete user-confirmed structured procedure during resumed setup;
- diagnose structural drift without mutating the target;
- back up and explicitly migrate recognized legacy surfaces.

The durable repository contains:

- a host-neutral `AGENTS.md` entry point;
- current product, architecture, design, quality, operations, security, and Plan authority;
- versioned specifications, designs, decisions, Plans, references, and optional runbooks;
- optional instruction-only host adapters and complete-procedure project Skills;
- ordinary Markdown Plans created or resumed by the Main Skill, not by setup;
- project-owned source, tests, commands, CI, deployment, secrets, and evidence.

The product does not install a copied command executor, command registry, generated CI workflow, task database, journal, evidence archive, or package-independent Reporivet maintenance command into the target repository.

## Core workflow

1. **Set up** the target with the integrated `reporivet setup` flow; use structure-only `init` only when guided onboarding is not wanted.
2. **Scan** the target deterministically and keep observations attributable.
3. **Define** the project in plain language through setup or lower-level `define`, preserving uncertainty rather than guessing.
4. **Preview** the complete Markdown draft and exact filesystem changes.
5. **Apply** only after explicit approval and immediate revalidation.
6. **Hand off** to the Main Skill, which creates or resumes the first ordinary Markdown Plan; setup creates no Plan.
7. **Work** through canonical documents, bounded Task Packets, and project-owned commands; the host, not Reporivet, performs Agent dispatch and command execution.
8. **Verify** the integrated candidate from a fresh context and record criterion-level evidence in the Plan.
9. **Maintain or migrate** with package-side diagnosis, non-destructive updates, and explicit backup-backed transactions.

## Requirements

### Rich content

- Current authority must explain product intent, system boundaries, quality, security, operations, and Plan lifecycle without requiring package internals.
- Durable records must preserve decisions, historical execution, and unresolved follow-ups.
- Confirmed facts, proposals, open questions, and sources must remain visibly distinct.
- Historical and superseded records must not become accidental current authority.

### Thin execution

- Project-owned commands and CI are authoritative for execution; Reporivet does not execute them.
- Reporivet may run its own package-side setup behavior while installed, but generated Markdown, Plans, Skills, Git, and project commands must remain useful after uninstall.
- Host adapters and confirmed-procedure Skills may route a host into canonical Markdown; they must not duplicate product authority, spawn/dispatch Agents, or embed a copied executor.
- A fresh setup must not create legacy command wrappers, runtime configuration, run-state directories, evidence stores, or workflows.

### Safety

- Reads and writes must stay beneath a validated repository root.
- Mutating operations must reject unsafe symlinked or nonregular targets.
- Existing project-owned or ambiguous files must be preserved unless an explicit, fingerprinted migration owns the change.
- A migration must use an external backup, revalidate the approved preview before mutation, restore automatically after an apply failure when safe, and refuse rollback that would overwrite later user changes.
- Optional settings require exact preview approval and must not merge with or rewrite an existing settings file.

## Success criteria

- A maintainer can identify current authority from `AGENTS.md` and `docs/README.md`.
- A substantive change can be coordinated using only one compact Markdown Plan and its Task Packets.
- A verifier can tie results to an integrated candidate and each acceptance criterion.
- Removing Reporivet leaves generated Markdown, ordinary Plans, Skills, Git, and project commands useful; only package-side maintenance capability disappears.
- Package diagnosis reports structural problems without silently repairing or deleting project state.
- The generated surface stays bounded to current documents, templates, metadata, selected host adapters, and complete-procedure Skills.

## Non-goals

Reporivet does not aim to:

- replace project-specific build, test, release, deployment, observability, backup, recovery, or incident systems;
- provide a general workflow engine, scheduler, queue, lock manager, policy server, or evidence database;
- infer project facts or promote scanner observations to confirmed requirements;
- install model bundles, prompts that encode project authority outside Markdown, or hidden agent memory;
- support arbitrary compatibility layers for retired repository layouts;
- claim that a source checkout, package artifact, release, installation, or deployment has been verified without direct evidence;
- spawn or dispatch Agents, execute project commands, operate CI or deployment, manage execution evidence, or move Plans to terminal states automatically;
- publish, sign, or release packages as part of package-side behavior.

## Evidence model

### Confirmed

- The source tree implements the package-side scan, guided definition, document-first setup, diagnosis, compact Plan checks, and explicit migration boundary through the previously verified document-first candidate.
- Historical verification of that candidate passed AC-1 through AC-10 and AC-12; this is historical evidence, not evidence for a later integrated product candidate.
- Python 3.11 or newer is required and the package declares no production dependencies.
- The console entry point is `reporivet`.
- Completed PLAN-2026-0003 records that source candidate `c1f8c72d684106a5a6896f957945dab177b538f964a57a71f47107f02eee9cf4` and exact wheel SHA-256 `512e304c231f830ce64e6b822d57f8fe8df5705b76ff440ae53f8b7941110ae4` passed the recorded isolated pipx and pip install/use/uninstall lifecycle. The verification artifacts are temporary and are not a durable or downloadable evidence archive.

### Proposed

- None.

### Open

- Publication, signing, release, deployment, CI repair/readiness, and a permanent evidence archive remain unestablished and outside this product boundary.
- Project-specific deployment, service-level, backup, and recovery requirements remain undefined because Reporivet is currently a local CLI/package rather than a documented deployed service.

### Sources

- [`product-specs/SPEC-REPORIVET-003-document-first-harness.md`](product-specs/SPEC-REPORIVET-003-document-first-harness.md)
- [`design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](design-docs/DESIGN-REPORIVET-003-document-first-harness.md)
- [`decisions/ADR-0001-document-first-product-boundary.md`](decisions/ADR-0001-document-first-product-boundary.md)
- [`../pyproject.toml`](../pyproject.toml)
