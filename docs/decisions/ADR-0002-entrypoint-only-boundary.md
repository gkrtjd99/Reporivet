---
id: ADR-0002
kind: decision
status: accepted
area: product
summary: Make Reporivet an entrypoint initializer without a copied target runtime
owner: main
supersedes:
  - ADR-0001
---

# Entrypoint-only boundary

## Decision

For the unreleased `0.3.0.dev1` line, Reporivet owns safe initialization, bounded read-only observation, and mechanical entrypoint checks. A target receives only a managed AGENTS block and an explicitly selected thin CLAUDE connection. It does not receive a copied runtime, wrappers, harness configuration, fixed documents, plan schema, Gate, run directory, CI workflow, or version marker.

The public `v0.2.0` release and existing runtime-shaped targets remain unchanged. A detected legacy target is refused before writes. Migration is a separately reviewed user-owned change.

## Reason and scope

The user explicitly requested a product centered on whether an agent can find and use a project's existing evidence from its entrypoint, rather than on maintaining a second runtime and document lifecycle. This decision applies to the next unreleased source and generated-target behavior; it does not rewrite completed plans, accepted historical ADR bodies, or the v0.2 release.

## Alternatives considered

- **No change:** rejected because it preserves copied runtime, imposed schema, and Gate responsibilities that the current product request explicitly removes.
- **Optional or disabled runtime:** rejected because two target models retain duplicated maintenance, ambiguous ownership, and a compatibility fallback.
- **New specification/SDD engine or task database:** rejected because project-owned tools already hold those responsibilities and a second state model would obscure authority.
- **LLM evaluation or agent supervision service:** rejected because evaluation must remain a controlled, separately reviewed observation and not become a production model dependency.
- **Automatic migration or deletion:** rejected because existing user documents, commands, CI, and runtime behavior are user-owned and cannot be safely transformed without explicit review.

## Existing capabilities reused

The decision reuses the existing standard-library file inventory, marker ownership, immutable preimage, completed temporary replacement, and postimage-aware rollback logic in `src/reporivet/initializer.py`. The source-only contract projection remains in `dev/agent_contract_sync.py`; it is not packaged into targets.

## External references

Spec Kit ([github.com/github/spec-kit](https://github.com/github/spec-kit)), OpenSpec ([github.com/Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)), and Kiro feature specifications ([kiro.dev/docs/specs/feature-specs/](https://kiro.dev/docs/specs/feature-specs/)) are referenced as examples of project-owned specification/workflow approaches. This decision separates those project procedures from Reporivet's entrypoint and does not claim to replace or reproduce them.

## Risks and controls

A bounded inventory is not semantic routing, and a repository with an already effective entrypoint needs no additional installation. The control is explicit observation limits, no authority inference, user-owned documents as authority, mechanical-only doctor output, and a navigation evaluation that reports limitations instead of generalizing from a small fixture.

The package boundary is recorded in `SPEC-REPORIVET-003`, `ARCHITECTURE.md`, and `docs/references/entrypoint-migration.md`. The source regression command is `PYTHON=python3 ./dev/check`. Revisit if real repositories show a concrete safety defect or if multiple independently reviewed navigation evaluations demonstrate a missing entrypoint capability; a separate approved plan is required for any new responsibility.
