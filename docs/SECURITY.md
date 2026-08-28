---
id: SECURITY
kind: security
status: active
area: security
summary: Current trust boundaries, filesystem protections, command execution model, and security limits
applies_to:
  - "src/**"
  - "dev/**"
  - "tests/**"
---

# Security

## Trust boundaries

- The caller chooses the target root and grants the process ordinary filesystem permissions there.
- Packaged templates and generated runtime code are trusted release artifacts.
- Existing target repository files are untrusted input and are preserved unless ownership is explicit.
- Commands in `dev/harness.toml` are trusted project configuration and execute with the caller's environment and permissions.
- Git history and worktree cleanliness provide integrity evidence for plan closure; they are not an authorization system.

## Protected assets

| Asset | Protection |
|---|---|
| Project-owned documents | Create-if-missing semantics; no upgrade overwrite |
| Canonical `dev/*` paths | Initialization conflict check for unmarked existing files |
| Shared files | Paired managed block markers; malformed markers fail |
| Configured commands | Argument arrays, no shell interpolation, explicit executable check |
| Raw logs | Stored under ignored `.harness/runs/`; callers must avoid printing secrets |
| Completed plans and ADRs | Historical lifecycle; supersede rather than silently rewrite |

## Required controls

- Resolve the target root before writing and reject non-directory targets.
- Refuse partial managed markers and unmarked command collisions.
- Never fetch or execute remote content during initialization.
- Never require or collect account credentials, API keys, telemetry identifiers, or LLM tokens.
- Execute only command arrays committed by the target project.
- Require a clean Git worktree and declared `HEAD` before recording verification evidence.

## Security-sensitive change gates

Changes involving path traversal, symlink semantics, file replacement, command execution, secrets, authentication, network access, Git integrity, or CI permissions require an approved ExecPlan, dedicated tests, and independent review.

## Operator responsibility

The generated runtime cannot redact secrets emitted by arbitrary project commands. Projects must keep credentials out of command output, use least-privilege environments, and review `.harness/runs/` before sharing local artifacts.

## Reporting

Until a public security contact is established, report suspected vulnerabilities privately to the repository owner rather than opening an issue containing exploit details or secrets.
