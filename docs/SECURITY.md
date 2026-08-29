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
| Local secrets and personal state | Managed `.gitignore` prevention plus tracked-file scanning, with reviewed example and lockfile exceptions |
| Completed plans and ADRs | Historical lifecycle; supersede rather than silently rewrite |

## Required controls

- Resolve the target root before writing and reject non-directory targets.
- Refuse partial managed markers and unmarked command collisions.
- Keep common real environment files, credentials, private keys, infrastructure state, local databases, logs, caches, build output, and personal editor state outside Git through the managed `.gitignore` block.
- Keep examples, lockfiles, migrations, source, and documentation trackable.
- Run `./dev/security-check` in `check` and `verify`; force-added sensitive paths and high-confidence secret signatures fail.
- Use `[policy].security_allow_tracked` only for narrowly reviewed fixtures that are demonstrably non-secret.
- Treat ignore rules and scanning as defense-in-depth only; rotate exposed credentials and remove sensitive history rather than relying on a later rule.
- Never fetch or execute remote content during initialization.
- Never require or collect account credentials, API keys, telemetry identifiers, or LLM tokens.
- Execute only command arrays committed by the target project.
- Require a clean Git worktree and declared `HEAD` before recording verification evidence.

## Security-sensitive change gates

Changes involving path traversal, symlink semantics, file replacement, command execution, secrets, authentication, network access, Git integrity, or CI permissions require an approved ExecPlan, dedicated tests, and independent review.

## Operator responsibility

The generated runtime cannot redact secrets emitted by arbitrary project commands. Projects must keep credentials out of command output, use least-privilege environments, review `.harness/runs/` before sharing local artifacts, and inspect `git status --ignored` when adopting the harness in an existing repository. Intentional public fixtures that use key- or credential-like names must be sanitized and documented before force-adding.

## Reporting

Follow [the public repository security policy](/.github/SECURITY.md). Do not publish exploit details, credentials, private repository content, or personal data in an issue.
