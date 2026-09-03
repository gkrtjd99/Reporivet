---
owner: security
status: active
last_reviewed: 2026-09-02
---

# Security

## Authentication, authorization, data, secrets, and permissions

Reporivet operates on repositories that may contain untrusted paths and sensitive content. During explicit setup or legacy transition, the installed package or an explicitly selected local source may inspect bounded path metadata and project files and mutate only an approved target transaction. Setup is a bounded one-shot package-side operation; it does not leave a target runtime or package requirement.

Fresh targets receive project-owned Markdown, Plans, static runbooks, and at most an exact root `CLAUDE.md` adapter. They receive no Reporivet role or procedure Skill, marker, generated settings, copied runtime, doctor gate, command registry, or hidden state. Generated documents and the optional adapter do not create a security sandbox.

Setup never executes project commands, spawns or dispatches Agents, or creates a Plan. Only a complete, unique, user-confirmed strict nine-field procedure record can render a static runbook under `docs/runbooks/<slug>.md`; the ordinary Markdown output has no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration. Reporivet does not infer or execute procedures.

The target project remains responsible for credentials, dependency policy, CI security, deployment controls, production access, logs, backups, incident handling, and project-command execution. Package removal after setup is expected and is not a security or operational blocker for ordinary target work.

## Conditional capability artifacts

`docs/FRONTEND.md` is project-owned frontend implementation and client-side behavior guidance only when `web_ui=yes` is explicitly Confirmed. `docs/RELIABILITY.md` is project-owned service/runtime reliability guidance only when `deployed_runtime=yes` is explicitly Confirmed, and it remains supplemental and subordinate to `docs/OPERATIONS.md`. Neither artifact grants permissions, changes the security boundary, or replaces this document.

Keep capability answers and artifact claims in separate **Confirmed**, **Proposed**, **Open**, and **Sources** states. Missing, conflicting, inferred, or unverified values remain Open or Proposed; scanner signals and provenance do not establish confirmation. Cite the owner, source, environment, and candidate or time range for security-relevant statements, and use project-owned checks and operational procedures for verification. Setup selection, audit output, and Plan state are distinct and are not security evidence by themselves.

## Threat model

Relevant threats include:

- path traversal outside the selected repository root;
- symlink swaps and nonregular targets during scan or mutation;
- overwriting project-owned or ambiguous content;
- applying a stale preview after target files change;
- rollback that destroys changes made after a successful transition;
- leaking secrets through drafts, backups, command output, diffs, or reports;
- treating host adapters or deny settings as a complete containment boundary;
- allowing legacy procedural artifacts to be mistaken for current executors or authority;
- allowing an external setup wrapper to become an installer or target mutator; and
- treating retained historical state as safe current working data.

## Durable rules

### Root and path safety

- Resolve and validate the selected repository root before work begins.
- Keep reads and writes beneath that root except for the user-selected external transition backup.
- Use descriptor-relative, no-follow traversal for sensitive mutations.
- Reject symlinked, nonregular, or unexpectedly replaced targets.
- Revalidate the complete preview and every preimage immediately before applying an approved transaction.

### Preservation and transactions

- Create current assets only when missing unless an explicit setup rerun or recognized transition proves ownership of a fingerprinted path.
- Preserve existing project-owned, customized, ambiguous, unknown, unsafe, symlinked, and nonregular content.
- Show exact path actions before mutation and bind destructive actions to the exact approval fingerprint.
- Use a mode-restricted backup directory outside the target for destructive transition actions.
- Restore the approved preimage after failed apply when the target can be restored safely.
- Refuse post-success rollback when later user changes would be overwritten.
- Never use a project-local backup as the only recovery source for a repository-wide transition.
- Do not recursively delete `.claude`; remove only transaction-proven empty child directories.

### Secrets and sensitive content

- Do not place credentials, tokens, private keys, exploit details, private repository content, or personal data in Plans, generated drafts, prompts, command output, diffs, issue reports, or vulnerability reports.
- Scanner observations must be bounded and attributable; they must not be sent to a model or promoted to confirmed truth automatically.
- Treat transition backups and manifests as sensitive even when they contain only selected managed files.
- Use least-privilege local permissions and delete external transition backups only under the maintainer's retention policy.
- `.harness/runs` is retired historical sensitive state. Current code does not read its contents, write it, or delete it. Do not use it as current evidence or working storage.

### Host adapters and generated content

- `AGENTS.md` remains canonical; a host adapter may only route to it.
- The optional root `CLAUDE.md`, when selected, is exactly `@AGENTS.md\n` and contains no additional authority.
- Reporivet generates no target role or procedure Skill. A complete procedure becomes a static ordinary Markdown runbook only; it never contains an executor, hooks, command registration, or privilege-bearing configuration.
- An optional external user-scoped `/reporivet-setup` wrapper remains outside the target, is instruction-only, and only relays deterministic preview/apply; it never installs, resolves, or edits target files itself.
- `.claude/settings.json` is not a fresh setup output. An existing settings path is considered for cleanup only when exact canonical ownership evidence proves it, and it is never merged or rewritten.
- Removing a host adapter or the package must not remove canonical documents, Plans, runbooks, or project-owned evidence.

### External and irreversible actions

Agents must stop for explicit authority before publishing packages, pushing commits, opening or merging changes, changing remote systems, deploying, rotating credentials, deleting backups, or performing other external or irreversible actions. Documentation and local checks do not grant that authority.

## Security review triggers

Require explicit security review for changes to:

- root validation, traversal, no-follow file operations, or write boundaries;
- backup, manifest, apply, restore, or rollback behavior;
- settings cleanup, host permissions, or adapter handling;
- handling of secrets, sensitive drafts, logs, or retained history;
- package publication, network access, authentication, authorization, CI permissions, or deployment; and
- production dependencies or external services.

Record the threat, control, evidence, and residual risk in the active Plan.

## Open security work

- Unreviewed host plugins, shell configuration, project CI, deployment environments, and external backup retention have no current Reporivet security assurance.
- Project-owned CI requires separate repair and security review before its result can be treated as current evidence.
- No security claim is made for the target's own commands, credentials, deployment, or project-owned operational controls.

## Vulnerability reporting

Follow the repository policy in [`.github/SECURITY.md`](../.github/SECURITY.md). Use GitHub private vulnerability reporting when available. Reports must not include exploit details, credentials, private repository content, or personal data in public channels.

### Confirmed

- Current file mutation paths use root confinement and reject unsafe target types.
- Setup and transition use exact previews, external backups, immediate preimage revalidation, restricted permissions, transaction restoration, and conflict-aware rollback.
- Integrated setup is preview-first, creates no Plan or runtime, and permits only static runbooks from complete unique user-confirmed procedure records.
- Current package code has no production dependencies and performs no model call for definition.
- Package absence after approved setup is expected and is not an unknown, blocker, or residual security risk for ordinary target work.

### Proposed

- None.

### Open

- No security claim is made for unreviewed host plugins, shell configuration, project CI, deployment environments, or external backup retention.
- Project-owned CI requires separate repair and security review before its result can be treated as current evidence.

### Sources

- [`../.github/SECURITY.md`](../.github/SECURITY.md)
- [`../docs/decisions/ADR-0002-one-shot-bootstrapper-boundary.md`](../docs/decisions/ADR-0002-one-shot-bootstrapper-boundary.md)
- [`../docs/product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md`](../docs/product-specs/SPEC-REPORIVET-004-one-shot-bootstrapper.md)
- [`../docs/design-docs/DESIGN-REPORIVET-004-one-shot-setup.md`](../docs/design-docs/DESIGN-REPORIVET-004-one-shot-setup.md)
- [`../docs/product-specs/SPEC-REPORIVET-003-document-first-harness.md`](../docs/product-specs/SPEC-REPORIVET-003-document-first-harness.md) (historical)
- [`../docs/design-docs/DESIGN-REPORIVET-003-document-first-harness.md`](../docs/design-docs/DESIGN-REPORIVET-003-document-first-harness.md) (historical)
