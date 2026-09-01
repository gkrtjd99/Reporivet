---
id: MOD-HARNESS-RUNTIME
kind: module-contract
status: superseded
area: harness
summary: Canonical package asset and copied repository-local runtime boundary
owner: Reporivet maintainers
responsibility: Keep package asset and copied runtime behavior aligned without installed-package imports.
applies_to:
  - "src/reporivet/assets/project/dev/harness.py"
  - "dev/harness.py"
public_entry_points:
  - "dev/harness.py"
  - "managed dev wrappers"
dependency_rules:
  - "The repository-local runtime uses only the Python standard library and repository files."
  - "The package asset is canonical; the dogfood runtime may differ only at the managed version token."
organization: Runtime behavior is implemented in the canonical package asset and copied into initialized repositories.
verification:
  - "python3 -m py_compile src/reporivet/assets/project/dev/harness.py dev/harness.py"
  - "normalize the managed version token and compare the canonical and dogfood runtime bytes"
---

# Repository-local harness runtime

> Historical/superseded module contract retained without deletion. It describes the retired copied runtime and is not current routing, setup input, or evidence. Use [`../README.md`](../README.md), [`../OPERATIONS.md`](../OPERATIONS.md), and the active Markdown Plan for the document-first authority. The historical body below remains for readability; its old runtime commands are not to be run.

## Boundary

The installed package owns initialization and upgrades. The canonical runtime asset is copied to `dev/harness.py`, which must continue to operate after the installed package is removed.

## Responsibilities

- Keep command behavior byte-aligned after normalizing only the managed version token.
- Preserve standard-library-only execution and repository-local authority.
- Expose behavior through the managed `dev/*` wrappers.

## Non-goals

- Package-side initialization logic.
- A plugin, daemon, task database, or model execution layer.
- Contracts for directories that do not form a durable boundary.

## Verification

Run the frontmatter verification commands and the focused generated-project tests.
