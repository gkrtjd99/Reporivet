# Design

## Primary source

The primary design reference is OpenAI's “Harness engineering: leveraging Codex in an agent-first world.” The implementation follows its central pattern: keep `AGENTS.md` short, make the repository the system of record, provide deterministic feedback interfaces, enforce stable invariants mechanically, and continuously report repository drift.

The ExecPlan model also follows OpenAI's guidance that plans for complex work are self-contained, living documents that a fresh agent can use to resume work without chat history.

## What this repository is

`project-harness` is a one-time initializer and safe updater. It installs a repository-local operating environment made of Markdown, Python standard-library tooling, shell entry points, Git, and optional GitHub Actions.

It is not an agent scheduler, state database, lease manager, replay system, or long-running orchestration service.

## Ownership model

Project-owned files are created only when missing and are never overwritten later. These include product, design, architecture, quality, security, reliability, plans, decisions, runbooks, and `dev/harness.toml`.

Harness-owned files contain a visible managed marker. Upgrade may refresh only those files and the managed blocks in `AGENTS.md` and `.gitignore`. Existing project-owned command paths cause initialization to stop rather than silently replacing them.

## Runtime model

The generated project routes all operations through `dev/harness.py` and committed `dev/harness.toml` commands. It does not probe the environment at verification time and silently drop checks. A configured executable that is unavailable is a visible failure.

Complex work is one ExecPlan under `docs/exec-plans/active/`. Main owns plan state and integration. Sub Agents receive one bounded Task Packet. Read-heavy work may run in parallel; writes are sequential unless isolated by disjoint scopes and separate Git worktrees.
