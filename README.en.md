# Reporivet

Reporivet is a small entrypoint initializer for helping an agent find a project's existing evidence. The current source is unreleased `0.3.0.dev1`; the public [`v0.2.0`](https://github.com/gkrtjd99/Reporivet/releases/tag/v0.2.0) release remains the previous runtime-shaped product. Installing the new package does not migrate an existing target.

## Boundary

Reporivet observes a bounded set of paths and writes only a managed block in `AGENTS.md`, plus an optional thin pointer in `CLAUDE.md` when `--claude` is explicitly selected. It does not install a target runtime, wrapper, fixed document set, plan or task schema, Gate, CI, or hidden state. Existing project documents, commands, and tools remain the authority; observed paths are not semantic routing.

User-owned instructions belong outside the managed markers:

```text
<!-- reporivet:entrypoints:start -->
<!-- reporivet:entrypoints:end -->
```

The optional Claude pointer uses:

```text
<!-- reporivet:entrypoints:claude:start -->
<!-- reporivet:entrypoints:claude:end -->
```

Content inside either managed block may be replaced by a later `init` or `upgrade`; bytes and mode outside it are preserved. If a project is already well connected, do not add another entrypoint.

## Use from the source checkout

These commands run from the root of this source checkout and do not assume an unreleased package is on an index:

```bash
PYTHONPATH=src python3 -m reporivet audit --root /absolute/path/to/project
PYTHONPATH=src python3 -m reporivet init --root /absolute/path/to/project --dry-run
PYTHONPATH=src python3 -m reporivet init --root /absolute/path/to/project
PYTHONPATH=src python3 -m reporivet doctor --root /absolute/path/to/project
```

With an installed CLI:

```bash
reporivet init --root ./project --name "Project" --claude --dry-run
reporivet init --root ./project --name "Project" --claude
reporivet upgrade --root ./project --claude --dry-run
reporivet upgrade --root ./project --claude
```

`audit` is read-only bounded path observation and does not print file contents or execute project commands. `doctor` performs mechanical ownership and link checks only. `--claude` must be supplied on both an upgrade preview and its apply command if the optional `CLAUDE.md` pointer is to be created or refreshed.

## Preview and privacy

`init` and `upgrade --dry-run` show the actual before/after unified diff from one immutable operation, and explicitly show a no-op when there is no change. Terminal control and bidirectional characters are escaped. This is a human review preview, not an executable patch. A mutation-plan fingerprint identifies the prepared operation; it is not approval, a lock, or a guarantee of the next execution result.

Unlike `audit`, a preview can include existing managed instructions and nearby context. Review it for secrets before sharing it externally.

## Legacy targets and removal

A detected released `v0.2` version marker, runtime, or managed block is rejected before any write. Legacy runtime and CI removal is a separate target-maintainer-owned change requiring compatibility and CI review. See [`entrypoint-migration.md`](docs/references/entrypoint-migration.md) for the manual procedure when working from a source checkout; the public source repository root is [`github.com/gkrtjd99/Reporivet`](https://github.com/gkrtjd99/Reporivet), and an unreleased documentation path is not assumed to exist on its remote default branch.

Package removal and document removal are separate. There is no automatic removal command. For a mixed file, manually inspect and remove only the exact two marker pairs above, preserving all user content before, after, or between them; remove the optional CLAUDE pointer with the AGENTS block only after reviewing both files. Do not delete the whole `AGENTS.md` or `CLAUDE.md`, and do not guess on malformed, duplicated, indented, fenced, or partial markers.

## Evaluation and development

The [`navigation evaluation`](docs/references/agent-navigation-evaluation.md) preserves the PLAN-0007 historical experiment. Its before/after sessions used the template available at that time and both fixtures already succeeded before application; it is not evidence that the current UX template improves navigation. Historical values and artifacts are retained without rewriting them.

Run source checks with:

```bash
PYTHON=python3 ./dev/check
```

This checks the source repository only. Reporivet does not run or supervise target work, provide an LLM service, or publish releases.
