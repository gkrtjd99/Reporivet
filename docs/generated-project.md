# Generated project

A service or application profile produces this shape:

```text
.
├── AGENTS.md
├── ARCHITECTURE.md
├── dev/
│   ├── harness.toml
│   ├── harness.py
│   ├── bootstrap
│   ├── context
│   ├── run
│   ├── check
│   ├── verify
│   ├── smoke
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

A new empty repository starts with `baseline = "draft"` and a command configuration that is ready for documentation-only verification. An existing implementation also receives `PLAN-0000-establish-repository-baseline.md` and starts with `configuration = "review"` so inferred commands cannot produce a false green result.

After the repository is inspected, current-state documents are made active, canonical commands are confirmed, the baseline plan is completed, and `baseline = "established"` enables strict completion gates.
