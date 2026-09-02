---
name: reporivet-setup
description: Use when a maintainer explicitly requests one Reporivet setup preview or approved apply.
---

# Reporivet setup

This is a user-scoped launcher for one explicit setup transaction. It is not a
project asset and must remain outside every target repository. It only relays
the deterministic package-side `reporivet setup` preview and, after explicit
approval, the matching apply.

## Before starting

- Get the target repository's explicit absolute path from the maintainer.
- Use an already available `reporivet` command or an explicitly supplied local
  source command. If neither is available, stop and report that setup cannot
  start. Do not install, download, resolve, or reproduce Reporivet.
- Do not infer a target, edit a target, create a Plan, dispatch an Agent, or run
  a project command on the maintainer's behalf.
- For a transition that may remove historical generated artifacts, get an
  explicit backup directory outside the target. The backup path is part of the
  approval fingerprint.

## Preview first

Run only the deterministic setup command, using the exact target path and any
maintainer-supplied answers file:

```text
reporivet setup --root /absolute/path/to/target [--answers /absolute/path/to/answers.json] [--backup-dir /absolute/path/outside/target/backup]
```

The command's normal mode is a read-only preview. Relay its JSON output without
rewriting it. The maintainer must review the audit, definition state, every
preview action, diagnostics, backup requirement, and exact SHA-256 fingerprint.
Do not approve a preview on the maintainer's behalf. If the preview reports a
conflict, unsafe path, missing external backup, or changed target, stop and
return that result.

## Approved apply

After the maintainer explicitly approves the exact fingerprint, run the same
setup command with only the approved apply arguments:

```text
reporivet setup --root /absolute/path/to/target --apply --approve-preview <PREVIEW_SHA256> [--backup-dir /absolute/path/outside/target/backup]
```

Use the same target, answers state, and external backup destination represented
by the approved preview. Relay the resulting setup envelope. Never substitute a
new fingerprint, target, backup path, or answer source. If revalidation rejects
the approval, stop and request a fresh preview rather than retrying with a
modified command.

## Boundary

This Skill is instruction-only. It does not itself write target files, mutate
filesystem paths, install itself globally, install or manage packages, execute
project commands, act as a runtime, keep a task store or journal, create an
execution hook, declare tools or permissions, or perform model-authored
filesystem mutation. The package command is the sole setup actor, and only the
maintainer's explicit approval permits its apply transaction.

Setup ends after the approved package transaction. The target must contain only
project-owned Markdown, ordinary Plan directories/templates, static runbooks,
and the optional exact host adapter. The target must not receive this launcher
or an ongoing Reporivet dependency.
