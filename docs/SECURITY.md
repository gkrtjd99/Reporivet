---
id: SECURITY
kind: security
status: active
area: security
summary: Current trust boundaries, filesystem protections, command execution, evidence handling, and security limits
applies_to:
  - "src/**"
  - "dev/**"
  - "tests/**"
---

# Security

## Trust boundaries

- The caller chooses the target root and grants ordinary filesystem permissions there.
- Packaged templates and generated runtime code are trusted local release artifacts.
- Existing repository files, paths, definition evidence, and metadata are untrusted input until validated.
- Human or Main owns semantic definition answers, conflict resolution, and REVIEW acceptance. Commands perform structural validation only.
- `audit` is read-only inventory and must not execute project commands. Adoption writes only after a conflict-free audit.
- Commands in `dev/harness.toml` are trusted project configuration and execute with the caller's environment and permissions.
- Git history, explicit base/head/target values, and worktree cleanliness provide integrity evidence; they are not authorization.
- CI uses repository content with `contents: read`; uploaded run artifacts remain potentially sensitive operational output.

## Protected assets

| Asset | Protection |
|---|---|
| Project-owned documents and definition draft | Create-if-missing semantics; no upgrade overwrite |
| Final product specifications and plans | Structural validation, stable IDs, lifecycle rules, transactional finalization/closure |
| `dev/harness.toml` | Project-owned bytes; upgrade never rewrites it |
| Canonical managed paths | Preflight collision, symlink, expected-type, and regular-file checks; explicit ownership marker; full-plan and per-write preimage validation |
| Shared files | Paired managed block markers; malformed or fenced lookalikes fail |
| Configured commands | Argument arrays, no shell interpolation, explicit executable and recursion checks |
| Verification manifest, Gate, report, and check JSON | One run root, sanitized command metadata, manifest hashing, target binding |
| Raw logs | Stored under ignored `.harness/runs/`; review before sharing and never commit |
| Local secrets and personal state | Managed `.gitignore` prevention plus tracked-file scanning with narrow reviewed exceptions |
| Completed plans and decisions | Historical lifecycle; supersede rather than silently rewrite |

## Required controls

- Resolve the target root and reject non-directory, symlinked, out-of-root, or nonregular paths before reading or writing sensitive entries.
- Refuse partial managed markers, unmarked canonical command collisions, FIFO/nonregular inputs, and expected file/directory type mismatches before any adoption or initialization write.
- Render preview and apply from the same canonical repository-relative mutation entries. Validate every type/mode/content-hash preimage before mutation and revalidate each target immediately before its write.
- Include generated code-map and catalog postimages in the transaction rather than leaving follow-up writes outside rollback. Restore a touched path only while it still matches the transaction postimage; preserve and report concurrent divergence.
- Keep audit deterministic and byte-stable; do not run configured or detected project commands during inventory.
- Preserve existing README, instruction, architecture, CI, and configuration authority during adoption.
- Keep Confirmed, Proposed, Open, and Sources evidence separate; blocking Open items and contradictions prevent finalization.
- Execute configured project commands only as argument arrays committed in `dev/harness.toml`; keep built-in validation and local Git-evidence operations on fixed runtime-owned argument arrays, and reject direct or shell-hidden recursive verification.
- Run `./dev/security-check` before project commands in `check` and `verify`; force-added sensitive paths and high-confidence secret signatures fail.
- Use `[policy].security_allow_tracked` only for narrowly reviewed non-secret fixtures.
- Use only explicit local `REPORIVET_BASE_SHA`, `REPORIVET_HEAD_SHA`, `REPORIVET_TARGET`, plan base, and observed HEAD evidence. Never fetch, assume a remote, or fabricate a parent.
- Treat missing, malformed, mismatched, or unknown target evidence conservatively; it cannot produce PASS.
- Preserve run artifacts on candidate failure and infrastructure error without copying raw argv or raw logs into structured reports.
- Keep CI actions pinned to immutable SHAs, retain `contents: read`, use full checkout history, verify the explicit head, invoke the gate once, and upload `.harness/runs/` with `if: always()`.
- Never require or collect account credentials, API keys, telemetry identifiers, LLM tokens, or model-service access.
- Never fetch or execute remote content during initialization, definition, audit, adoption, local verification, or distribution tests.

## Gate and closure controls

Required check failure produces `BLOCK`; required error/unknown or target mismatch produces `INCONCLUSIVE`; neither can be overridden. Protected, unknown, wide, irreversible, or policy-required dirty conditions produce `REVIEW`, which requires a genuine safe human reason before closure. Structural PASS or REVIEW acceptance does not certify semantic correctness or authorize deployment/publication.

`close-plan` verifies one clean current commit once, binds the manifest hash and Gate verdict to the plan, and guards both active and completed paths during post-move rollback. Unchanged transaction postimages are restored to exact bytes and mode; concurrent edits are preserved and reported. Verification artifacts remain for diagnosis.

## Security-sensitive change gates

Path traversal, symlink semantics, file replacement, audit/adoption, command execution, secrets, authentication, authorization, network access, Git evidence, Gate policy, CI permissions, or artifact publication require an approved ExecPlan, dedicated tests, and independent review.

## Operator responsibility

The runtime cannot redact secrets emitted by arbitrary project commands. Keep credentials out of command output, use least-privilege environments, review `.harness/runs/` before sharing, and inspect ignored/tracked state during adoption. Rotate and revoke any exposed credential and remove sensitive history as required; ignore rules and scanning are defense-in-depth only.

Mutation staging and postimage guards do not provide OS, container, process, permission, or adversarial concurrency isolation. The caller's ordinary filesystem authority remains the trust boundary. Preview fingerprints describe current planned bytes; they are not approvals, capabilities, or a substitute for reviewing the target and diff.

A person accepting REVIEW must inspect the report, changed paths, protected matches, recovery path, and relevant raw logs, then provide their own reason. An agent must not generate that acceptance on their behalf.

## Reporting

Follow [the public repository security policy](/.github/SECURITY.md). Do not publish exploit details, credentials, private repository content, raw verification logs, or personal data in an issue.
