---
id: QUALITY
kind: quality
status: active
area: repository
summary: Current quality model, test layers, release checks, and residual risks
applies_to:
  - "**"
---

# Quality

## Quality model

Quality means a target repository is created safely, remains understandable after sessions change, fails visibly when its configured evidence is unavailable, and can be upgraded without losing project-owned knowledge.

## Verification layers

| Layer | Purpose | Canonical command | Evidence |
|---|---|---|---|
| Syntax | Compile Python sources and tests | `python3 -m compileall -q src tests` | Zero exit status |
| Regression | Exercise initializer and generated runtime end to end | `python3 -m unittest discover -s tests -v` | Twelve passing tests |
| Repository fast feedback | Structural checks plus regression suite | `./dev/check` | Catalog, document, plan, and test output |
| Completion gate | Strict repository checks plus regression suite | `./dev/verify` | Integrated command logs under `.harness/runs/` |
| Distribution smoke | Build and install a wheel, initialize a project, run its verify and doctor commands | Release procedure | Installed CLI and generated project succeed |

## Test ownership

`tests/test_project_harness.py` owns black-box and integration behavior for:

- blank and existing repository initialization;
- baseline plan and command-review state;
- project-owned content preservation;
- managed-block idempotence;
- durable document catalog drift;
- future ExecPlan template-token preservation and creation-time rendering;
- ExecPlan creation and Task Packet routing;
- strict baseline readiness;
- missing executable failures;
- dry-run non-mutation;
- canonical command path conflicts; and
- Git-bound plan closure.

## Review expectations

Changes to ownership rules, file replacement behavior, command execution, frontmatter parsing, plan closure, packaged assets, or CI templates require regression tests and independent review of destructive edge cases.

## Release gate

1. Run `./dev/verify` from a clean worktree.
2. Build a wheel with no build isolation.
3. Confirm the wheel contains every asset and no bytecode cache.
4. Install it into an isolated virtual environment.
5. Initialize a service project with CI.
6. Run the generated project's `verify` and initializer `doctor` commands.

## Known gaps

- Tests run on the current POSIX environment; Windows-native wrappers are not covered.
- Frontmatter parsing intentionally supports the limited schema emitted by templates, not arbitrary YAML.
- Semantic documentation quality remains a review responsibility rather than a parser guarantee.
