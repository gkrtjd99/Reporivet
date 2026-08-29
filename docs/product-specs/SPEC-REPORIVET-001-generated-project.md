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

A service or application profile creates:

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
│   ├── DESIGN.md
│   ├── QUALITY.md
│   ├── SECURITY.md
│   ├── RELIABILITY.md
│   ├── PLANS.md
│   ├── product-specs/
│   ├── design-docs/
│   ├── exec-plans/{active,completed}/
│   ├── decisions/
│   ├── runbooks/
│   ├── generated/
│   └── references/
└── .harness/runs/
```

Library, CLI, and other profiles omit `RELIABILITY.md` unless the project needs service operations knowledge.

## New empty repository lifecycle

- Starts with `baseline = "draft"`.
- Starts with `configuration = "ready"` because no implementation command is being claimed.
- Can run documentation-only `./dev/verify` while configured source paths do not exist.
- Must add canonical commands when implementation appears.

## Existing implementation lifecycle

- Receives `PLAN-0000-establish-repository-baseline.md`.
- Starts with `configuration = "review"` even when commands were inferred.
- Requires evidence-based current-state documents and confirmed command arrays.
- Becomes strict only after current-state documents are active and `baseline = "established"`.

## Upgrade behavior

- Managed code and blocks may be refreshed.
- Future-work tokens in the ExecPlan template remain unresolved until `./dev/new-plan` creates a plan.
- Missing newly introduced scaffold files may be created.
- Project-owned current-state documents, specifications, plans, decisions, runbooks, and command configuration are preserved.
- Unmarked existing canonical command paths are never silently replaced.

## Repository hygiene behavior

- The managed `.gitignore` blocks common environment files, credentials, private keys, local infrastructure state, databases, build output, logs, caches, and personal editor state.
- Documented example, sample, and template environment or credential files remain trackable.
- `./dev/security-check` catches sensitive files that were force-added or already tracked; narrow non-secret fixtures require an explicit policy allowlist.

## Verification behavior

- Tracked sensitive paths and high-confidence secret signatures are rejected before project commands.
- Catalog, document, plan, and architecture checks run before project commands.
- Missing configured executables fail visibly.
- Source-bearing projects cannot pass with an empty verification group.
- Command output is streamed and written to ignored raw logs.
- Completed plans record the clean integrated Git commit actually verified.
