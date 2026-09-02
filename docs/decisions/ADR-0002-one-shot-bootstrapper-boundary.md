---
id: ADR-0002
kind: decision
status: accepted
area: harness
summary: Make generated targets independent after explicit one-shot setup
applies_to:
  - "src/reporivet/**"
  - "src/reporivet/assets/**"
  - "docs/**"
supersedes:
  - ADR-0001
superseded_by: ""
---

# Make setup one-shot and generated targets independent

## Context

ADR-0001 correctly retired the copied repository runtime, but retained target-installed role Skills, procedure Skills, a package version marker, optional generated settings, and package-side diagnosis. Those artifacts are non-executable, yet they still expose Reporivet concepts inside ordinary target work. Agents can misread them as current toolchain requirements, attempt to locate or install Reporivet after setup, require `doctor`, or block when the package is absent.

The durable need is simpler: Reporivet prepares a repository once, then the repository operates through its own Markdown authority, Plans, commands, Git, and host-native Agents. Initial setup may require an installed package or explicit local source. Nothing in the generated target may require Reporivet afterward.

## Decision

Reporivet is a one-shot package-side bootstrapper. An external user-scoped `/reporivet-setup` Skill may wrap the deterministic package setup preview/apply flow, but it remains outside target repositories, performs no model-authored filesystem mutation, and never installs or resolves the package. It is setup UX, not a continuing runtime.

Fresh generated targets contain project-owned Markdown authority, Plan templates and directories, deterministic static runbooks for complete Confirmed procedures, and optionally a root `CLAUDE.md` containing only `@AGENTS.md`. They contain no Reporivet role or procedure Skill, `.reporivet-version`, generated `.claude/settings.json`, copied module/runtime, doctor gate, registry instruction, or package-dependent Plan requirement.

Main, Task Owner, implementation, verification, Plan discovery, and manual terminal movement are specified in `AGENTS.md`, `docs/PLANS.md`, and the Plan template. Project commands are the only verification command boundary. Reporivet absence after setup is expected and cannot be classified as unknown, blocking, or a residual risk.

Complete unique Confirmed structured procedures render as ordinary `docs/runbooks/<slug>.md` files. They carry no Skill frontmatter, command registration, tool permissions, hooks, or executor metadata. Proposed, Open, Sources-only, incomplete, malformed, generic, or duplicate records render no runbook.

`reporivet doctor` is retired. Setup validates only the exact transaction it previews and applies; Reporivet provides no ongoing project-health command.

An owner may explicitly rerun setup against an existing target. That preview may convert/remove historical generated Skills, settings, and markers only when exact canonical evidence proves ownership. Modified, unknown, ambiguous, unsafe, nonregular, and project-owned content is preserved. Destructive apply requires an external backup, unchanged fingerprint, pre-mutation revalidation, and rollback.

This decision preserves ADR-0001's rejection of a target runtime, scheduler, dispatcher, command runner, Gate, evidence archive, hidden state, and automatic closure. It supersedes ADR-0001 only where that decision retained target Skills/settings and ongoing package maintenance concepts.

## Consequences

### Positive

- A generated project is immediately understandable and usable without Reporivet being installed.
- Agents cannot infer a Reporivet tool gate from a version marker, role Skill, procedure Skill, or doctor instruction.
- Role and Plan behavior have one durable host-neutral authority instead of duplicated Skill prose.
- Confirmed procedures remain useful as ordinary reviewed runbooks.
- Existing-target cleanup is explicit, reversible, and ownership-safe.

### Negative and risks

- Claude-specific role shortcuts and generated deny-only settings are no longer installed into targets.
- Hosts must follow `AGENTS.md` and self-contained Task Packets directly.
- Existing projects retain old artifacts until an owner explicitly reruns setup and approves cleanup.
- Exact legacy ownership catalogs and rollback tests add package-side setup complexity.
- The external setup Skill requires an available explicit Reporivet setup source at invocation time; it does not fetch one.

## Alternatives considered

- **Keep target Skills and only clarify their prose.** Rejected because duplicated adapters can drift and still advertise a continuing Reporivet concept.
- **Keep `.reporivet-version` as provenance.** Rejected because ordinary tooling and Agents reasonably interpret it as an active version requirement.
- **Make doctor optional.** Rejected because an optional ongoing diagnosis command still weakens the one-shot boundary and can leak into Plans.
- **Bundle a standalone zipapp or plugin runtime.** Rejected as unnecessary; initial explicit setup may depend on the package, while only target independence is required.
- **Delete every matching path by name.** Rejected because path names and markers do not establish ownership.

## Verification and retirement

The prior boundary is retired only when one integrated candidate proves that:

- fresh external targets contain no persistent Reporivet Skill, marker, generated settings, runtime, doctor/tool gate, or package-resolution instruction;
- generated Markdown fully carries role and Plan lifecycle behavior;
- package removal after setup does not reduce target usefulness;
- complete Confirmed procedures alone produce deterministic static runbooks;
- explicit setup rerun removes/converts only exact canonical legacy artifacts with approved backup and rollback; and
- current authority and distribution tests describe the same generated surface.

Historical ADRs and completed Plans remain readable. This decision does not authorize publication, signing, deployment, global Skill installation, or cleanup of real projects during implementation.
