---
owner: security
status: active
last_reviewed: 2026-08-31
---

# Security

## Authentication, authorization, data, secrets, and permissions

Reporivet operates on repositories that may contain untrusted paths and sensitive content. The installed package may inspect path metadata, read bounded project files for deterministic definition, and mutate only explicitly approved setup or migration targets. The default integrated `reporivet setup` coordinates that package-side work; `reporivet init` is structure-only and `reporivet define` remains lower-level. Generated Markdown, host adapters, and project Skills do not create a security sandbox.

Setup never executes project commands, spawns or dispatches Agents, creates a Plan, or creates a target runtime. Only a complete user-confirmed structured procedure may produce an instruction-only project Skill through resumed setup; unresolved or inferred records produce none.

The target project remains responsible for credentials, dependency policy, CI security, deployment controls, production access, logs, backups, and incident handling.

## Threat model

Relevant threats include:

- path traversal outside the selected repository root;
- symlink swaps and nonregular targets during scan or mutation;
- overwriting project-owned or ambiguous content;
- applying a stale preview after target files change;
- rollback that destroys changes made after migration;
- leaking secrets through drafts, backups, command output, diffs, or reports;
- treating generated host settings as a complete containment boundary;
- allowing procedural adapters to become hidden executors or alternate authority;
- treating retained historical state as safe current working data.

## Durable rules

### Root and path safety

- Resolve and validate the selected repository root before work begins.
- Keep reads and writes beneath that root except for the user-selected external migration backup.
- Use descriptor-relative, no-follow traversal for sensitive mutations.
- Reject symlinked, nonregular, or unexpectedly replaced targets.
- Revalidate fingerprints immediately before applying an approved preview.

### Preservation and transactions

- Create current assets only when missing unless a recognized migration explicitly owns a fingerprinted path.
- Preserve existing project-owned and ambiguous content.
- Show exact path actions before mutation.
- Use a mode-restricted backup directory outside the target for migration.
- Restore the pre-migration state after failed apply when the target can be restored safely.
- Refuse post-success rollback when later user changes would be overwritten.
- Never use a project-local backup as the only recovery source for a repository-wide migration.

### Secrets and sensitive content

- Do not place credentials, tokens, private keys, exploit details, private repository content, or personal data in Plans, generated drafts, prompts, command output, diffs, issue reports, or vulnerability reports.
- Scanner observations must be bounded and attributable; they must not be sent to a model or promoted to confirmed truth automatically.
- Treat migration backups and manifests as sensitive even when they contain only selected managed files.
- Use least-privilege local permissions and delete external migration backups only under the maintainer's retention policy.
- `.harness/runs` is retired historical sensitive state. Current code does not read its contents. Current code does not write it. Current code does not delete it. Do not use it as current evidence or working storage.

### Host adapters and settings

- `AGENTS.md` remains canonical; a host adapter may only route to it.
- Instruction-only role and complete-procedure Skills may express bounded Main, implementation, verification, or project procedure guidance, but may not contain copied command execution, Agent spawn/dispatch, hidden state management, or privileged frontmatter.
- `.claude/settings.json` is absent by default. Creation requires exact preview approval, and an existing settings file is never merged or rewritten.
- Deny-only host settings are defense in depth, not a sandbox. Repository instructions cannot prevent all tool, host, plugin, shell, network, or credential actions.
- Removing a host adapter must not remove canonical documents or project-owned evidence.

### External and irreversible actions

Agents must stop for explicit authority before publishing packages, pushing commits, opening or merging changes, changing remote systems, deploying, rotating credentials, deleting backups, or performing other external or irreversible actions. Documentation and local checks do not grant that authority.

## Security review triggers

Require explicit security review for changes to:

- root validation, traversal, no-follow file operations, or write boundaries;
- backup, manifest, apply, restore, or rollback behavior;
- settings generation or host permissions;
- handling of secrets, sensitive drafts, logs, or retained history;
- package publication, network access, authentication, authorization, CI permissions, or deployment;
- production dependencies or external services.

Record the threat, control, evidence, and residual risk in the active Plan.

## Open security work

- Unreviewed host plugins, shell configuration, project CI, deployment environments, and external backup retention have no current Reporivet security assurance.
- Project-owned CI requires separate repair and security review before its result can be treated as current evidence.

## Vulnerability reporting

Follow the repository policy in [`.github/SECURITY.md`](../.github/SECURITY.md). Use GitHub private vulnerability reporting when available. Reports must not include exploit details, credentials, private repository content, or personal data in public channels.

### Confirmed

- Current file mutation paths use root confinement and reject unsafe target types.
- Migration uses an external backup, exact fingerprints, immediate revalidation, restricted permissions, and conflict-aware rollback.
- Integrated setup is preview-first, creates no Plan/runtime, and permits only complete user-confirmed procedure Skills.
- Current package code has no production dependencies and performs no model call for definition.

### Proposed

- None.

### Open

- No security claim is made for unreviewed host plugins, shell configuration, project CI, deployment environments, or external backup retention.
- Project-owned CI requires separate repair and security review before its result can be treated as current evidence.

### Sources

- [`../.github/SECURITY.md`](../.github/SECURITY.md)
- [`product-specs/SPEC-REPORIVET-003-document-first-harness.md`](product-specs/SPEC-REPORIVET-003-document-first-harness.md)
- [`design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](design-docs/DESIGN-REPORIVET-003-document-first-harness.md)
- [`decisions/ADR-0001-document-first-product-boundary.md`](decisions/ADR-0001-document-first-product-boundary.md)
