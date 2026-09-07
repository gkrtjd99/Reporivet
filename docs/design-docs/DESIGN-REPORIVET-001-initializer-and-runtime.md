---
id: DESIGN-REPORIVET-001
kind: design-doc
status: active
area: harness
summary: Separation between the installed initializer and independent repository-local runtime
applies_to:
  - "src/reporivet/initializer.py"
  - "src/reporivet/assets/project/dev/harness.py"
  - "src/reporivet/assets/project/root/**"
  - "src/reporivet/assets/project/docs/**"
supersedes: []
---

# Initializer and repository-local runtime

## Context

A target repository needs durable operating rules after the initializer is gone. Requiring an installed package, host plugin, model service, or external state system during ordinary development would make the repository less portable and less legible to a fresh agent.

## Current design

The system has two lifetimes with one-way dependency direction.

### Initializer lifetime

The installed `reporivet` package:

- inventories a target without executing project commands;
- renders packaged assets and establishes ownership boundaries;
- initializes a greenfield or existing repository;
- explicitly starts definition or performs audit-first adoption;
- creates target-centered authority drafts, generated repository facts, generated baseline questions, review-state configuration, and a baseline plan when inferred implementation evidence requires confirmation;
- refreshes only managed artifacts during upgrade;
- renders one canonical repository-relative mutation plan for preview and apply, including final code-map/catalog postimages, then guards preimages and rollback by type, mode, and content hash; and
- diagnoses required files, executability, runtime version, catalogs, plans, and Gate configuration.

### Repository lifetime

The copied `dev/harness.py`, shell wrappers, Markdown, TOML, local Git history, and optional CI operate independently. The runtime uses the Python standard library plus only the project's configured tools and provides:

- definition status, validation, and transactional finalization;
- deterministic read-only audit;
- contract/code-map/context routing;
- document, plan, traceability, architecture, and security checks;
- one shared Verification Run with structured artifacts;
- explicit local target evidence and conservative Gate policy;
- evidence-bound transactional plan closure; and
- maintenance-candidate reporting.

Dependency direction remains:

```text
installed CLI -> initializer -> packaged assets
repository wrapper -> copied runtime -> repository files, Git, configured commands
```

## Ownership model

- Current-state documents, definition drafts/final specs, plans, decisions, and `dev/harness.toml` are project-owned.
- Runtime code, wrappers, workflows, and `.reporivet-version` are managed only when they carry the ownership marker.
- `AGENTS.md` and `.gitignore` use bounded managed blocks.
- Generated facts and questions remain non-authoritative path-bound evidence. Fresh authority drafts carry a provenance marker and structural baseline-review record; legacy project-owned authority without that marker is not forced through a hidden schema migration.
- Fresh initialization leaves `docs/design-docs/` with its index and reusable template only. Upgrade preserves any existing project-owned technical documents, including `core-beliefs.md`.
- Upgrade creates a missing newly introduced project-owned scaffold but never rewrites an existing one.
- New configurations receive explicit Gate defaults. Existing configurations remain byte-identical; missing Gate settings use conservative in-memory defaults and a doctor advisory.

## Invariants and boundaries

- The copied runtime never imports `reporivet`.
- Package and dogfood runtime differ only by the rendered version token; wrappers come from one `PYTHON`-aware template and remain executable.
- Project intent and current-state knowledge remain project-owned.
- Definition commands do not generate semantic answers, and command inference never equals approval.
- Audit does not write or execute configured/detected project commands.
- A tool update cannot require rewriting historical plans or decisions.
- Verification operates on one repository root, one committed command configuration, and one explicit local base/head/target.
- Verification never infers a Git parent, assumes a remote, or fetches network evidence.
- Repository hygiene combines preventive ignore rules with tracked-file scanning.
- Initializer rendering is scoped per artifact so future repository-local tokens are not consumed during installation.
- Main/Sub policies live in `AGENTS.md`, durable docs, and Task Packets rather than a hidden scheduler.
- Mutation fingerprints are deterministic descriptions, not authorization. The initializer does not bind an earlier dry run to apply or persist a backup registry.
- Planning uses a temporary local staging tree to derive deterministic final bytes. This does not claim process, kernel, container, or adversarial filesystem isolation; ordinary caller permissions and concurrent filesystem behavior remain the operating boundary.
- Rollback changes a touched path only when its current type, mode, and content hash still match the transaction postimage. Divergent user state is preserved and reported rather than overwritten.

## CI and distribution

Generated CI checks out the explicit candidate, retains full history, binds explicit target evidence, runs the repository gate once, and preserves run artifacts on success or failure with immutable actions and read-only contents permission.

The local distribution check builds a complete `0.2.0` wheel without network or dependencies, installs it in isolation, initializes and diagnoses generated repositories, uninstalls the package, and reruns repository-local definition, audit, context, planning, checks, verification, closure, and gardening.

## Alternatives considered

- A global Skill, plugin, or host-specific target bundle was rejected because it creates duplicated installation and upgrade state.
- A task database or daemon was rejected because one ExecPlan is sufficient durable state for the intended single-Main model.
- Model-backed completion judgment was rejected as nondeterministic and unnecessary for structural evidence.
- Runtime stack auto-probing was rejected because environment-dependent detection can silently change verification.
- Whole-document overwrite was rejected because it destroys project knowledge after initialization.
- A second generated-harness completion gate was rejected in favor of extending the existing canonical `./dev/verify` once.

## Verification

Regression tests initialize and adopt temporary repositories, exercise copied runtime behavior in isolated processes, preserve and upgrade project-owned files, validate definition/traceability/evidence/Gate behavior, close plans against real Git commits, compare managed assets, inspect the wheel, install it into a fresh environment, uninstall Reporivet, and repeat repository-local operations.

Detailed definition, evidence, Gate, and closure choices are recorded in [`DESIGN-REPORIVET-002`](DESIGN-REPORIVET-002-project-definition-adoption-and-evidence-gate.md).
