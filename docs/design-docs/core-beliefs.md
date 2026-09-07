---
id: DESIGN-CORE-001
kind: design-doc
status: active
area: repository
summary: Durable engineering defaults for agent-readable, maintainable software
applies_to:
  - "**"
supersedes: []
---

# Core engineering beliefs

## Repository as operating environment

The repository, not a hidden conversation or external control plane, is the operating system for agent work. Durable facts needed to define, resume, constrain, verify, or maintain work are discoverable through a short entry map and version-controlled artifacts.

## Working behavior first

Deliver changes as observable end-to-end slices. After each integrated slice, the repository remains runnable and passes the applicable feedback gate.

## Smallest durable design

Choose the smallest implementation that satisfies current observable requirements and known operating constraints. Do not build extension points for hypothetical futures, and do not knowingly introduce architecture intended to be discarded later.

## Explicit boundaries

Keep ownership, concerns, and dependency direction explicit. Stable boundaries should be enforced by tests or lint where practical.

## Agent legibility

Prefer searchable source, deterministic commands, structured output, inspectable schemas, and actionable errors. Important state must not exist only in chat history.

## Dependency choice

Inspect current project facilities and dependency documentation, types, and relevant source before adding infrastructure or packages. Choose the option with the lowest total lifecycle complexity and reliability risk, whether that is an existing dependency, an established library, or a small fully tested local implementation.

## Implementation conventions

- Use the Python standard library unless a production dependency materially reduces total lifecycle complexity and is explicitly approved.
- Prefer narrow parsers, fixed data structures, and deterministic schemas over a registry, plugin system, policy DSL, or compatibility framework.
- Add a mechanical rule only when it is objective, stable, and produces an actionable repair path.
- Preserve explicit local evidence rather than inferring Git parents, remotes, or network state.

## Compatibility

Remove obsolete internal paths atomically rather than leaving accidental shims. Public contracts, persisted data, deployed protocols, and external configuration require explicit migration, rollout, rollback, and retirement decisions.

## Temporary exceptions

A temporary exception requires an owner, exit criteria, removal trigger, and tracked follow-up.
