---
id: SPEC-REPORIVET-003
kind: product-spec
status: active
area: product
summary: Safe entrypoint initialization without a copied runtime or imposed document schema
applies_to:
  - "src/reporivet/initializer.py"
  - "src/reporivet/cli.py"
  - "src/reporivet/assets/project/root/AGENTS.md.tmpl"
  - "tests/"
supersedes:
  - SPEC-REPORIVET-001
  - SPEC-REPORIVET-002
---

# Agent entrypoints

## Product intent

Reporivet helps a fresh agent begin at a project-owned entrypoint and find the project's own current requirements, code, and checks. It does not create a second document system, execute a project's commands, or install a repository-local runtime.

## Requirements

- **REQ-ENTRY-001 — Actual entrypoint:** `init` writes only a bounded AGENTS management block and, when explicitly selected, a thin CLAUDE connection. Existing files, bytes outside the managed block, names, layout, and modes remain preserved.
- **REQ-ENTRY-002 — Observed navigation:** `audit` reports a bounded, read-only inventory of actual paths and explicit exclusions. It does not infer authority, semantic links, commands, or project quality from path names.
- **REQ-ENTRY-003 — Mechanical doctor:** `doctor` checks only mechanical entrypoint ownership, path safety, and managed-link structure. It does not claim that an agent understood the project or that project work is complete.
- **REQ-ENTRY-004 — Read-only preview:** dry-run/preview operations do not write target files or directories, execute project commands, read remote content, or create approval tokens. `init`/`upgrade` preview renders the actual immutable-operation before/after unified diff, explicitly reports no-op, escapes terminal control/bidi characters, and is a human review display rather than an executable patch. Its fingerprint is an identifier, not approval, locking, or a guarantee of the next result.
- **REQ-ENTRY-005 — Entrypoint-only target:** generated targets receive no copied Python runtime, wrappers, harness configuration, fixed document set, plan/task schema, Gate, run evidence, CI workflow, or version marker.
- **REQ-ENTRY-006 — Safe mutation:** symlink, nonregular, malformed marker, invalid UTF-8, path traversal, immutable-preimage divergence, and partial failure are rejected or rolled back without overwriting unrelated user changes.
- **REQ-ENTRY-007 — Legacy boundary:** a detected v0.2 managed runtime, version marker, or operating block is rejected before any write. There is no automatic deletion, conversion, or compatibility fallback.
- **REQ-ENTRY-008 — Evaluation honesty:** navigation quality is evaluated with controlled fixtures and fresh sessions using observable selected evidence and commands. A bounded result does not claim semantic routing or general performance. Results from PLAN-0007's prior template target are historical observations, not evidence that the current UX template improved navigation.

## Non-goals

Reporivet does not standardize document names or frontmatter, replace Spec Kit/OpenSpec/Kiro or project-owned tools, interview or judge product decisions, run project tests, supervise agents, provide an LLM service, add telemetry, generate CI, migrate old targets, or publish releases.

## Acceptance criteria

- **AC-1:** Empty and differently structured targets receive only the requested entrypoint management surface; existing user files and bytes remain unchanged.
- **AC-2:** Audit, doctor, and preview are read-only with bounded, observable output and do not execute project commands or remote content. Audit omits file contents; preview may include managed instruction content for human review and warns that it is not an applyable patch.
- **AC-3:** Unsafe paths, types, markers, concurrent edits, and transaction failures are rejected or recovered without clobbering user changes.
- **AC-4:** Legacy v0.2 targets are rejected before writing; v0.2 source/release artifacts remain unchanged and migration is manual.
- **AC-5:** Source checks preserve file-safety, contract-projection, packaging, and CLI regression coverage without requiring a target runtime.
- **AC-6:** The navigation protocol records exact fixture inputs, fresh-session prompts, selected evidence, actual commands/results, before/after limits, and independent review; it does not invent an after result.

## Verification boundary

The source check is `PYTHON=python3 ./dev/check`. It covers the repository's tests, source-only contract sync, Python compilation, and diff whitespace checks. Actual project checks remain project-owned. Independent review judges an exact candidate separately; Main or a human accepts the evidence.
