# Reporivet

**Help agents find the documentation and code your project already has.**

Reporivet is a CLI that observes a repository and adds a small navigation entrypoint to `AGENTS.md`. It gives a new agent a place to start while keeping your existing documents and tools in charge.

[![CI](https://github.com/gkrtjd99/Reporivet/actions/workflows/ci.yml/badge.svg)](https://github.com/gkrtjd99/Reporivet/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[한국어](README.md) · [Quick start](#quick-start) · [Commands](#commands) · [Safety and limits](#safety-and-limits) · [Documentation](#documentation)

> **v0.3.0a1 is a prerelease.** The published [v0.2.0](https://github.com/gkrtjd99/Reporivet/releases/tag/v0.2.0) is the previous runtime-based product. Existing projects are not migrated automatically; read the [migration guide](docs/references/entrypoint-migration.md) first.

## Why Reporivet?

Requirements, design notes, code, and checks often live in different places. Rather than copying them into a new documentation system, Reporivet creates **a short list of paths it actually observed**.

```text
AGENTS.md / optional CLAUDE.md
    → the project's existing docs, specs, code, and checks
    → the agent reads relevant evidence and uses existing tools
```

- **Keep your structure:** no required document names, directories, frontmatter, or task workflow. Keep using Spec Kit, OpenSpec, Kiro, or your own system.
- **Bounded writes:** only the managed `AGENTS.md` block and an optional `CLAUDE.md` pointer are written. Existing bytes outside the blocks and file modes are preserved.
- **Review first:** use content-free `audit` and `--dry-run` to inspect proposed changes before applying them.
- **Plain Markdown:** no target runtime, CI, configuration file, or task store is installed. The files remain useful after the package is removed.

An observed path is **not proof of current authority**. The project owner and agent remain responsible for identifying current requirements and appropriate checks. A repository that is already well connected may not need Reporivet.

## Quick start

**Requirements:** Python 3.11 or later on Linux or macOS. Windows is not currently supported. CI is configured for Python 3.11–3.15 on both supported OSes.

### Install

Install the wheel from the [v0.3.0a1 GitHub prerelease](https://github.com/gkrtjd99/Reporivet/releases/tag/v0.3.0a1) into a virtual environment. This does not assume the version is published on PyPI.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install https://github.com/gkrtjd99/Reporivet/releases/download/v0.3.0a1/reporivet-0.3.0a1-py3-none-any.whl
reporivet --version
```

Alternatively, install from a source checkout with `python -m pip install .`. Choose a supported Python 3.11+ interpreter when creating the environment.

### Inspect and initialize a project

Replace the example path with **your actual project**. Review the observation and preview before applying changes.

```bash
reporivet audit --root /path/to/project
reporivet init --root /path/to/project --dry-run
reporivet init --root /path/to/project
reporivet doctor --root /path/to/project
```

To add a Claude Code pointer, include `--claude` in **both** the preview and apply commands:

```bash
reporivet init --root /path/to/project --claude --dry-run
reporivet init --root /path/to/project --claude
```

The pointer is plain text asking the agent to read `AGENTS.md`. Claude Code instruction loading varies by version and configuration, and an existing nested `AGENTS.md` can be affected. See [agent compatibility](docs/references/agent-compatibility.md).

## Commands

| Command | Purpose |
|---|---|
| `init` | Create or refresh the bounded `AGENTS.md` block; add a pointer with `--claude`. |
| `audit` | Report observed paths and exclusions as read-only JSON. It does not print file contents or infer and execute commands. Exit 0 means the report was produced. |
| `upgrade` | Refresh observed paths and managed blocks. Pass `--claude` again to refresh the optional pointer. |
| `doctor` | Mechanically check managed structure and local links. It exits 2 on errors and does not judge document meaning or task completion. |

`init` and `upgrade` support `--dry-run`. Use `reporivet --help` or a command's `--help` for all options. The parent of a new project root must already exist.

## Managing project instructions

Reporivet owns only the area between these markers. **A later `init` or `upgrade` regenerates this block.** Put instructions you want to keep outside it.

```markdown
<!-- reporivet:entrypoints:start -->
Navigation guidance managed by Reporivet
<!-- reporivet:entrypoints:end -->
```

Outside the block, you can document where current requirements live, how to distinguish historical documents, and which checks the project actually uses. After adding, moving, or removing files, review `upgrade --dry-run`, apply with the same options, and run `doctor`.

Removing the package does not remove the managed blocks. There is no automatic removal command: do not delete a whole file containing user content; follow the [manual removal procedure](docs/references/entrypoint-migration.md).

## Safety and limits

- `audit` does not print file contents, but **path names themselves may contain sensitive information**.
- `--dry-run` renders a human-readable before/after diff, not an executable patch. It can include existing instructions and surrounding context; review before sharing. A fingerprint is not approval, a lock, or a guarantee about the next run.
- Observation is limited to 512 visited entries and a bounded depth, with at most 80 output files. Up to 40 slots are initially allocated to each of documentation-like and other paths, with unused slots reallocated. A particular document or check is not guaranteed to appear, and names do not establish authority.
- New files follow the OS creation policy, normally including the caller's umask. Default ACL behavior depends on the OS and filesystem. File protections are not complete OS-level concurrency isolation or a sandbox; use a directory where other users cannot concurrently replace entries. See [security and limitations](docs/SECURITY.md).

## Does it improve navigation?

The [navigation evaluation](docs/references/agent-navigation-evaluation.md) records fresh-agent before/after observations. In the small synthetic cases tested so far, agents diagnosed the tasks correctly even before initialization; **an improvement in task success or cost has not been established**. Results for larger real repositories and other models still need evaluation.

## Development and contributions

Run source checks from a checkout. Distribution tests require pip/setuptools capable of building a wheel.

```bash
PYTHON=python3 ./dev/check
```

Report bugs and propose improvements in [GitHub Issues](https://github.com/gkrtjd99/Reporivet/issues). Do not post vulnerabilities or secrets in public issues; follow the [security policy](.github/SECURITY.md).

## Documentation

- [Documentation map](docs/README.md) · [Product requirements](docs/PRODUCT.md) · [Architecture](ARCHITECTURE.md)
- [Agent compatibility](docs/references/agent-compatibility.md) · [Navigation evaluation](docs/references/agent-navigation-evaluation.md)
- [v0.2 migration and block removal](docs/references/entrypoint-migration.md) · [Quality](docs/QUALITY.md) · [Security and limits](docs/SECURITY.md)

## License

[MIT License](LICENSE)
