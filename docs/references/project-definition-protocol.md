# Project Definition Protocol

This protocol converts a deterministic repository scan and plain-language human input into the canonical document-first bundle during explicit package-side setup. The default entry point is integrated `reporivet setup`; lower-level `reporivet define` remains available, while `reporivet init` is structure-only. Setup is a bounded one-shot transaction: package installation or an explicitly selected local source is needed only while the user invokes setup, and package absence afterward is expected. The protocol does not use an LLM to rewrite answers, choose filenames, or promote repository inference into authority.

## Evidence model

Every guided topic preserves these areas distinctly and in this order:

1. **Confirmed** — explicit human input, inserted verbatim apart from whitespace normalization.
2. **Proposed** — deterministic scanner observations or user-supplied candidate statements awaiting review.
3. **Open** — unanswered, uncertain, or conflicting questions.
4. **Sources** — provenance for the entries above.

Blank answers remain Open. The visible Markdown draft is the only resume state; Reporivet creates no hidden interview database, journal, task state, marker, or runtime.

## Topics

The fixed interview asks about:

- product, users, problem, and observable success;
- design direction, accessibility, and internationalization;
- project-owned test, lint, type, build, package, and smoke commands;
- running, release, observation, backup, rollback, recovery, and incidents;
- authentication, authorization, sensitive data, secrets, permissions, exposure, and retention;
- Main, implementation, and verification working agreements; and
- repeatable procedures that deserve a static runbook.

A procedure is runbook-eligible only when one complete, unique, user-confirmed, strict structured record is present in `Confirmed`. The record must contain exactly these nine fields: `slug`, `title`, `trigger`, `reads`, `actions`, `stop_conditions`, `evidence`, `permissions`, and `rollback`. All nine fields are required; no additional fields or aliases are accepted, and no values or defaults are inferred.

Only such a record produces ordinary Markdown at `docs/runbooks/<slug>.md` through resumed setup. The output has no frontmatter, executor metadata, hooks, command registration, or privilege-bearing configuration. It is descriptive project documentation, not an executor. Generic, inferred, incomplete, Proposed, Open, Sources-only, malformed, or duplicate procedure records never create a runbook; no procedure is inferred or executed.

The optional external `/reporivet-setup` wrapper is instruction-only and remains outside target assets. It only relays the deterministic setup preview/apply flow and never installs, resolves, downloads, or edits target files itself. Reporivet does not generate a target role or procedure Skill. Existing, differing, stale, or arbitrary project Skills are preserved and never deleted by procedure rendering; any explicit legacy cleanup requires separate exact ownership evidence and safety controls.

Users answer facts and procedures, not canonical filenames.

## Package-side flow

```text
reporivet setup --root .
reporivet init --root .
reporivet define start --root .
reporivet define status --root .
reporivet define resume --root . [--answers answers.json]
reporivet define finalize --root .
```

`setup` is the default integrated flow: it audits once, presents and resumes the visible draft, reports actual Open items, renders the exact preview, and applies only after explicit approval. `init` only creates missing structure without guided onboarding. `define` remains the lower-level interface. Setup and init create no Plan or runtime, execute no project commands, and do not spawn or dispatch Agents. The Main Skill creates or resumes the first ordinary Markdown Plan. `resume` updates only the visible draft. `status` and finalize preview are read-only.

Apply recomputes the complete target preview, requires the exact unchanged fingerprint, creates missing documents and eligible static runbooks, preserves existing project-owned documents and the optional exact `CLAUDE.md` adapter, and does not generate role/procedure Skills, markers, settings, runtime, or package-resolution instructions. A differing, unsafe, symlinked, nonregular, unknown, or ambiguous path is preserved or refused.

## Setup transaction and legacy ownership

The exact preview lists create, preserve, conflict, refusal, and any explicitly approved cleanup actions. Cleanup of a legacy Reporivet role/procedure Skill, marker, setting, or managed block requires exact canonical bytes or strict parse-and-rerender equality tied to the canonical path; a name, marker, frontmatter, or location alone cannot prove ownership.

Destructive cleanup requires explicit preview approval, an absolute external backup bound into the preview fingerprint, path-safety checks, and immediate preimage revalidation. A failed apply restores the whole approved transaction when safe. Later rollback uses the external manifest and refuses to overwrite a successful postimage changed by the user. Modified, project-owned, ambiguous, unsafe, symlinked, and nonregular paths are preserved or refused. Backup and rollback state remain outside the target.

No generated target artifact locates, installs, resolves, imports, invokes, or verifies Reporivet or `doctor`. There is no current `reporivet doctor` contract; setup validates only its own approved transaction and postconditions. Project commands, CI, Agents, and Plan movement remain host/project responsibilities.
