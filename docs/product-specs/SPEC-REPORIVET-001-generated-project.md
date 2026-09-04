---
id: SPEC-REPORIVET-001
kind: product-spec
status: active
area: harness
summary: Observable structure and lifecycle of a generated repository harness
applies_to:
  - "src/reporivet/assets/project/**"
  - "src/reporivet/initializer.py"
supersedes: []
---

# Generated repository harness

## Observable structure

A generated profile creates this operating surface. Optional document entries appear only when selected by project kind or the project-owned `[documents]` configuration:

```text
.
├── AGENTS.md
├── ARCHITECTURE.md
├── .reporivet-version
├── dev/
│   ├── harness.toml
│   ├── harness.py
│   ├── bootstrap
│   ├── context
│   ├── define
│   ├── audit
│   ├── code-map
│   ├── run
│   ├── check
│   ├── verify
│   ├── smoke
│   ├── security-check
│   ├── docs-index
│   ├── docs-check
│   ├── plan-check
│   ├── architecture-check
│   ├── new-plan
│   ├── task
│   ├── close-plan
│   └── garden
├── docs/
│   ├── README.md
│   ├── PRODUCT.md
│   ├── PRODUCT_SENSE.md             # optional: product_sense
│   ├── DESIGN.md                    # optional: visual_design
│   ├── FRONTEND.md                  # optional: frontend
│   ├── QUALITY.md
│   ├── SECURITY.md
│   ├── RELIABILITY.md               # optional: reliability
│   ├── PLANS.md
│   ├── product-specs/
│   │   └── project-definition.draft.md  # only after explicit definition
│   ├── design-docs/
│   ├── exec-plans/{active,completed}/
│   ├── module-contracts/
│   ├── decisions/
│   ├── runbooks/
│   ├── generated/code-map.md
│   └── references/project-definition-protocol.md
└── .harness/runs/
```

Service and application profiles select `RELIABILITY.md` by default; web profiles also select `DESIGN.md` and `FRONTEND.md`; library, CLI, and other profiles select no optional documents by default. Explicit capabilities may select optional documents in schema 2 configuration. CI workflows are added only with `--with-ci` or when an existing managed CI surface is upgraded.

## New empty repository lifecycle

- Starts with `baseline = "draft"` and `configuration = "ready"` because no implementation command is being claimed.
- Can run documentation-only `./dev/verify` while configured source paths do not exist.
- Must add and review canonical command arrays when implementation appears.
- Does not receive a definition draft unless `reporivet define` is explicitly invoked.

## Existing implementation lifecycle

- `init` receives `PLAN-0000-establish-repository-baseline.md`.
- Inferred commands start with `configuration = "review"` and cannot produce a false-green check or verify.
- The project becomes strict only after current-state documents are active, commands are confirmed, and `baseline = "established"`.

## Definition and adoption lifecycle

- `reporivet define --root <path>` installs missing harness responsibilities and creates the project-owned fourteen-section draft.
- `./dev/define status` reports persisted progress; `validate` rejects structural uncertainty that blocks handoff; `finalize` transactionally creates one final spec and one first-slice plan.
- `reporivet audit` and `./dev/audit` are deterministic, read-only, and do not execute project commands.
- `reporivet define --adopt` audits first, preserves current authority, adds only missing responsibilities, refuses collisions before writing, and keeps inferred commands in review.

## Context and traceability behavior

- Module contracts are created only for justified actual, configured, or confirmed planned multi-file boundaries.
- `./dev/code-map` emits only evidence-backed rows and marks the map as generated/non-authoritative.
- `./dev/context --path`, `--area`, or `--plan` routes to matching current-state docs, product specs, contracts, map entries, and active plans.
- Plans opt into product-to-evidence traceability through `traceability: 1` and one active `product_spec`; historical non-opt-in plans remain valid.

## Upgrade behavior

- Managed runtime, wrappers, workflows, and bounded blocks may be refreshed.
- Future-work tokens in templates remain unresolved until a repository-local command creates the corresponding artifact.
- Missing newly introduced scaffold files may be created.
- Project-owned current-state documents, specifications, plans, decisions, runbooks, definition evidence, and command configuration are preserved.
- New configurations include explicit conservative `[gate]` shadow defaults.
- Existing configuration bytes are never rewritten. Missing `[gate]` uses conservative in-memory defaults and produces a doctor advisory.
- Unmarked, symlinked, or nonregular canonical managed paths are never silently replaced.

## Repository hygiene behavior

- The managed `.gitignore` blocks common environment files, credentials, private keys, local infrastructure state, databases, build output, logs, caches, and personal editor state.
- Documented examples, samples, templates, source, migrations, documentation, and dependency lockfiles remain trackable.
- `./dev/security-check` catches sensitive files that were force-added or already tracked; narrow non-secret fixtures require an explicit reviewed allowlist.

## Verification Run and Gate behavior

- One `./dev/verify` invocation creates exactly one `.harness/runs/<run>-verify/`.
- Security, catalog, documentation, plan, architecture, project, and optional smoke checks execute in fixed order.
- Checks record `pass`, `fail`, `error`, `skipped`, or `unknown`; required candidate failure takes precedence over required infrastructure error.
- Missing configured executables, malformed command groups, recursive verify configuration, and source-bearing empty project verification fail visibly.
- Manifest, Gate, report, check JSON, and available logs survive pass, candidate failure, and infrastructure error.
- Structured artifacts contain sanitized command metadata rather than raw arguments or raw logs.
- Gate uses only explicit local base/head/target evidence and explicit changed paths. It never infers a parent, remote, or network state.
- Verdicts are `PASS`, `REVIEW`, `BLOCK`, or `INCONCLUSIVE`; shadow and enforce modes apply declared exit semantics without overriding BLOCK/INCONCLUSIVE.

## Plan closure behavior

- `./dev/close-plan` requires a clean current HEAD and the plan's explicit base.
- It invokes canonical verification exactly once, then records run ID, manifest hash, Gate verdict, verified SHA, criterion evidence, and a genuine human REVIEW reason when required.
- PASS closes directly; REVIEW requires the reason; BLOCK and INCONCLUSIVE cannot be overridden.
- Post-move structural failure restores the exact active plan while retaining run evidence.

## CI behavior

The generated verify workflow keeps immutable action SHAs and `contents: read`, checks out the explicit PR/push head with full history, exports base/head/target evidence, runs bootstrap then verify once, appends the latest report to the step summary, and uploads `.harness/runs/` with `if: always()`. An all-zero push base remains unavailable.

## Package-removal behavior

The copied runtime does not import the installed package. After Reporivet is uninstalled, generated definition, audit, context, planning, checks, verification, closure, and gardening continue through repository-local wrappers and Python standard-library code.
