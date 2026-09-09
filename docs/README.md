# Reporivet Knowledge Map

This directory records current product intent, architecture, quality, security, source plans, decisions, experiments, and historical context. It does not impose a document schema on initialized projects.

## Reading protocol

1. Read root [`AGENTS.md`](../AGENTS.md), or the selected execution environment's entrypoint.
2. Read [`PRODUCT.md`](PRODUCT.md) and the current product specification.
3. Read [`../ARCHITECTURE.md`](../ARCHITECTURE.md), [`QUALITY.md`](QUALITY.md), and [`SECURITY.md`](SECURITY.md).
4. Check [`exec-plans/active/`](exec-plans/active/) for matching complex work.
5. Read only the source-of-truth documents and code needed by the current task; distinguish observed paths from authority.

## Stable entry points

| Need | Read |
|---|---|
| Product purpose and current requirements | [`PRODUCT.md`](PRODUCT.md), [`product-specs/SPEC-REPORIVET-003-agent-entrypoints.md`](product-specs/SPEC-REPORIVET-003-agent-entrypoints.md) |
| Current architecture and dependency direction | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) |
| Quality expectations and evaluation limits | [`QUALITY.md`](QUALITY.md) |
| Security boundaries and controls | [`SECURITY.md`](SECURITY.md) |
| Engineering principles | [`design-docs/core-beliefs.md`](design-docs/core-beliefs.md) |
| Current complex work and manual plan policy | [`PLANS.md`](PLANS.md), [`exec-plans/active/`](exec-plans/active/) |
| Entrypoint migration | [`references/entrypoint-migration.md`](references/entrypoint-migration.md) |
| Agent navigation evaluation | [`references/agent-navigation-evaluation.md`](references/agent-navigation-evaluation.md) |
| Durable decisions | [`decisions/`](decisions/) |
| Historical execution | [`exec-plans/completed/`](exec-plans/completed/) |

## Route by change type

| Change | Minimum context |
|---|---|
| Product behavior | Product overview, current product specification, relevant source and tests |
| Entrypoint or file ownership | Architecture, security, initializer and focused tests |
| User-visible behavior | Product overview, relevant source, reproduction, and tests |
| Complex work | [`PLANS.md`](PLANS.md) and the matching active plan |
| Documentation correction | Authoritative source or configuration plus affected current-state document |
| Agent navigation evaluation | Evaluation protocol, controlled fixture, fresh prompt, and observable command evidence |

## Document authority and lifecycle

- `AGENTS.md` remains a compact portable routing contract. This source repository authors its portable block in `CLAUDE.md` and projects it with `./dev/agent-contract-sync`; generated targets do not receive the helper or this source-only file.
- Current-state documents describe implemented reality and verified intent. User-owned target documents remain authoritative for their own meaning.
- Observed paths are non-authoritative evidence. A path's existence does not prove that its contents are current requirements or a runnable command.
- Active ExecPlans are living source records manually copied from the template. Completed plans and accepted decisions are historical records; supersede them rather than rewriting their bodies.
- Evaluation notes distinguish actual before/after observations from hypotheses and do not claim semantic routing or general performance from a bounded fixture. PLAN-0007's prior-template observations remain historical and are not evidence for the current UX template.
- `init`/`upgrade --dry-run` previews are escaped human unified diffs from one immutable operation and may contain instruction content; `audit` remains content-free. Fingerprints identify a plan but are not approval or locking.
- Retirement requires an explicit plan action, replacement or rationale, and removal of current references.

## Historical material

The previous runtime-centered specifications, designs, module contract, and migration note remain in this repository as historical records with supersession banners. They are not current product authority. The accepted ADR-0001 body is preserved unchanged; the current boundary is ADR-0002.
