---
id: DESIGN
kind: design
status: active
area: repository
summary: Current interaction, ownership, and implementation conventions for Reporivet
applies_to:
  - "src/**"
  - "tests/**"
  - "docs/**"
---

# Design

## Design intent

The repository, not a hidden conversation or external control plane, is the operating system for agent work. Every durable fact needed to resume, constrain, verify, or maintain work should be discoverable through a short entry map and version-controlled artifacts.

## Interaction conventions

- CLI commands use explicit subcommands, visible exit codes, and actionable error messages.
- `--dry-run` must not create or modify a target path.
- Potentially destructive ambiguity fails closed rather than guessing.
- A successful operation prints created, updated, and preserved files.
- Generated entry points use stable names under `dev/` so agents do not invent project commands.

## Ownership conventions

- Project-owned files are created only when absent.
- Harness-owned files have `reporivet:managed` in their first lines.
- Shared files use bounded managed blocks with paired start and end markers.
- The managed `.gitignore` block protects common sensitive and local-only files, but keeps example configuration and reproducibility artifacts eligible for tracking.
- Malformed or partial markers are errors, not opportunities to append a second block.
- Upgrades preserve unmarked files even when that means reporting a version mismatch for manual resolution.

## Knowledge conventions

- `AGENTS.md` remains a compact routing contract.
- Current-state documents describe implemented reality and verified intent.
- Detailed durable knowledge receives stable metadata and appears in generated catalogs.
- Active ExecPlans are living execution state; completed plans and accepted decisions are history.
- Generated facts identify their generator; raw command logs remain disposable and ignored by Git.

## Main and Sub conventions

- Main defines acceptance, non-goals, allowed writes, protected paths, integration order, and evidence requirements.
- Sub Agents return structured results rather than mutating shared plan state concurrently.
- Read-heavy work may be parallelized; mutable work is sequential unless paths and worktrees are isolated.
- Implementation claims are not accepted as verification evidence.

## Implementation conventions

- Use the Python standard library unless a dependency materially reduces total lifecycle complexity.
- Execute configured commands as argument arrays without shell interpolation.
- Keep command detection separate from command approval.
- Prefer small, inspectable templates and validators over opaque framework behavior.
- Add a mechanical rule only when it is objective, stable, and produces an actionable repair path.

## Accessibility and internationalization

The CLI emits plain UTF-8 text and accepts Unicode project names, summaries, areas, and plan titles. Generated operational documents use English headings for predictable parsing; project content may use any UTF-8 language.
