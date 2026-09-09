---
id: REF-REPORIVET-002
kind: reference
status: superseded
owner: main
area: harness
updated: 2026-08-29
---

# HarnessEngineeringSkill Migration Matrix

> Historical migration input. Superseded as current product guidance by [`SPEC-REPORIVET-003-agent-entrypoints.md`](../product-specs/SPEC-REPORIVET-003-agent-entrypoints.md); upstream context and the original matrix remain preserved.

## Upstream reference

- Repository: `https://github.com/gkrtjd99/HarnessEngineeringSkill`
- Default branch inspected: `main`
- Pinned commit: `dd5989d4f9de5646349b3bceec4e19806262d14d`
- Commit timestamp: `2026-07-14T06:09:25Z`
- Inspection mode: public, read-only GitHub API reads; no clone, fetch, checkout, write, backup, archive, or deletion
- Reporivet plan: `PLAN-2026-0002` — [ExecPlan 기록](../exec-plans/)의 `active/` 또는 `completed/`에서 lifecycle 상태에 따라 확인한다.

This reference records migration input, not current Reporivet behavior. Current behavior remains authoritative in Reporivet product, architecture, quality, security, and design documents.

## Disposition meanings

- **absorb:** retain the capability with the same durable purpose inside an existing Reporivet responsibility.
- **adapt:** retain the capability but change its interface or ownership to match Reporivet invariants.
- **replace:** satisfy the need through an existing or newly extended Reporivet mechanism rather than porting the source implementation.
- **discard:** intentionally omit a deployment surface or behavior that conflicts with the target architecture or has no durable value.

## Capability matrix

| Existing capability | Upstream source of truth | Disposition | Reporivet target | Verification | Retired deployment surface | Residual risk |
|---|---|---|---|---|---|---|
| Fourteen-section project-definition workflow | `skill/references/project-definition.md` | adapt | Project-owned `docs/product-specs/project-definition.draft.md`; `reporivet define`; `./dev/define` | Definition start/resume/validate/finalize scenarios | Skill invocation and host-specific interview packaging | Semantic completeness still depends on Main/human input |
| Interruptible definition and continuation state | `skill/SKILL.md`, definition reference | absorb | Persisted progress, next questions, and continuation note in the draft | Confirmed sections are not repeated after a new process/session | Skill session state | Humans must resolve contradictory evidence |
| Confirmed / Proposed / Open separation | `skill/references/project-definition.md`, `templates.md` | absorb | Explicit draft/final-spec sections and strict validators | Proposal-as-fact, blocking Open, placeholder, and duplicate-ID failures | Host prompt conventions | Markdown authors can still write poor semantics that structural validation cannot judge |
| P0 requirements, journeys, acceptance criteria, first slice | Definition reference/templates | adapt | Stable `JRN-*`, `REQ-P0-*`, `AC-*`; finalized spec; generated first ExecPlan | Product trace and first-plan fixtures | Skill-only document templates | Structural links do not prove product quality |
| Existing-project repository scan | `skill/scripts/scan-project.sh` | replace | Package and copied-runtime deterministic audit | Byte-identical output and unchanged full-tree snapshot | Shell scan helper | Heuristics may classify uncommon layouts as unknown |
| Existing-project adoption | `skill/SKILL.md`, starter kit | adapt | Ownership-aware initializer plus explicit `define --adopt` | README/AGENTS/architecture/CI/config preservation and collision refusal | Starter-kit copy workflow | Substantial authority conflicts require human resolution |
| Language/runtime/source/test detection | Scan helper and Skill instructions | adapt | Existing `infer_language`, `infer_runtime`, `source_paths`, `test_paths` as evidence-producing detectors | Multi-language inventory tests; inferred status remains review | Shell-specific detection output | Detection is intentionally conservative and non-authoritative |
| Command detection | Scan helper and templates | adapt | Existing `detect_commands` plus explicit review configuration | Detected commands are never silently marked ready or executed by audit | Prompt-mediated command promotion | Uncommon build systems may remain unknown |
| Agent instruction and durable-doc inventory | Scan helper and Skill guidance | absorb | Deterministic audit categories and Reporivet docs map | Inventory status/category/path assertions | Skill-generated summary | Duplicate authority may require Main arbitration |
| Product → plan → task traceability | Definition/templates | adapt | Product Trace tables, Task type/Acceptance fields, strict docs/plan checks | Missing/unknown links and missing closure evidence fail | Skill-specific checklist format | Historical plans remain intentionally grandfathered |
| Criterion-level closure evidence | Templates/check-generated-harness | adapt | Verification Run, manifest hash, Gate verdict, verified SHA, plan closure table | Traceable complete plan evidence fixtures | Free-form Skill completion assertion | Evidence proves checks ran, not absolute correctness |
| Conditional module contracts | `skill/references/templates.md`, starter kit | adapt | `docs/module-contracts/` only for justified actual/configured/confirmed boundaries | Contract metadata and no-universal-contract scenarios | Blanket starter-kit files | Boundary justification remains a Main decision |
| Repository code map | Starter kit/templates | adapt | Deterministic non-authoritative `docs/generated/code-map.md`; `./dev/code-map` | Actual/configured/confirmed rows and drift tests | Static starter-kit map | Generated map can lag until regenerated; checks expose drift |
| Language-aware context routing | Skill instructions and generated files | adapt | Existing `./dev/context --path/--area` extended with contracts/map/spec | Targeted routing fixtures | Host-specific prompt routing | Unusual path ownership may need explicit metadata |
| Short agent entry-point map | `AGENTS.md`, starter kit | absorb | Existing short managed `AGENTS.md` contract and structured docs | Ownership/managed-block and context tests | Runtime-specific agent files | Projects may add local authority that creates conflict |
| Living ExecPlan and bounded Task Packets | Starter kit and Skill guidance | absorb | Existing `docs/PLANS.md`, plan template, runtime plan/task commands | Strict plan checks and lifecycle tests | Skill-managed task/checklist conventions | Complex work still depends on Main maintaining the plan |
| Deterministic documentation and plan validation | `check-generated-harness.sh` and starter kit | replace | Existing docs-index/docs-check/plan-check extended narrowly | Existing regression plus traceability failures | Upstream shell validator | Markdown is only structurally, not semantically, validated |
| Security and architecture checks | Starter kit/check script | replace | Existing Reporivet security/architecture commands inside canonical verify | Existing security tests and configured-command error tests | Upstream check wrapper | Project-specific architecture enforcement remains configured |
| Generated harness validation | `skill/scripts/check-generated-harness.sh` | replace | `./dev/check`, one `./dev/verify`, `doctor`, parity tests, wheel scenarios | Generated-project and package-removal suite | Separate generated-harness check script | Distribution tests must keep asset inventory current |
| Long-term gardening | Skill maintenance guidance | absorb | Existing `./dev/garden` and tech-debt tracker | Garden regression and current docs | Skill maintenance prompts | Garden reports candidates; it does not make semantic decisions |
| Starter kit | `starter-kit/` | replace | Package assets rendered with ownership-aware init/upgrade | Fresh init, upgrade preservation, wheel inventory | Directory-copy starter kit | Package data globs must include every new template |
| Runtime target bundles for Claude, Claude Code, Codex, OpenCode, Antigravity | `targets/` | discard | No replacement; one repository-local runtime and neutral docs | Wheel forbidden-asset scan and repository search | Five target trees | Hosts outside the neutral contract may need optional user-local setup, not project duplication |
| Target synchronization | `scripts/sync-skill-targets.sh` | discard | Managed package assets and parity tests | Canonical/dogfood version-normalized comparison | Bundle synchronization script | Parity tests must fail clearly on drift |
| Host-specific `PROMPT.md` and required bridges | Antigravity target and Skill installation docs | discard | Short neutral `AGENTS.md`; optional user-owned host configuration outside core | No generated target/prompt/mandatory `CLAUDE.md` assets | Host bridge files | Some hosts may not auto-discover `AGENTS.md`; this is not solved with duplicate project state |
| Local Skill installation/testing | `scripts/test-skill-local.sh` | discard | Wheel install, generated-project, and package-removal tests | Isolated distribution test | Skill directory installation | None for core behavior |
| Model-backed runner/judge and trajectory evaluation | Skill evaluation material | discard | No blocking replacement; deterministic checks plus independent human/Main review | Forbidden dependency/asset scan; no network/model test | Model evaluator and judge path | Semantic/product quality still requires human review; pinned evaluator is incomplete |
| External task database, daemon, journal, or orchestration service | Not a durable required upstream capability | discard | Repository files and native agent execution only | Dependency/process/asset review | Any hypothetical external state surface | Long-running coordination remains Main-owned and Git-visible |
| Duplicate completion gate | Skill validation alongside repository checks | discard | Existing `./dev/verify` extended into one fixed run | One-top-level-run and close-plan-one-run tests | Parallel validator as release authority | Standalone diagnostic commands remain non-gating |
| Old repository deprecation, backup, archive, and deletion | Original retirement request, not a retained product capability | discard from this work by later user instruction | Reporivet migration guide and this recorded boundary only | Confirm no external writes/artifacts and no backup/delete commands were run | All old-repository retirement execution | Old repository lifecycle remains entirely outside this implementation |

## Target migration map

| Old surface | Reporivet surface |
|---|---|
| Install or invoke a HarnessEngineeringSkill bundle | Install Reporivet once, then use repository-local `AGENTS.md`, `docs/`, and `dev/` |
| Skill project-definition interview state | `docs/product-specs/project-definition.draft.md` |
| Skill definition entry point | `reporivet define --root .` |
| Skill resume/validation/finalization | `./dev/define status`, `./dev/define validate`, `./dev/define finalize` |
| `scan-project.sh` | `reporivet audit --root .` or `./dev/audit` |
| Starter-kit copy/adoption | Ownership-aware `reporivet init` / explicit definition adoption |
| Static code map | `./dev/code-map` generated from repository evidence |
| Generated-harness checker | `./dev/check`, canonical `./dev/verify`, and `reporivet doctor` |
| Runtime-specific target directories | One copied `dev/harness.py` plus neutral managed wrappers |
| Free-form completion assertion | Verification Run manifest, Gate, report, verified SHA, and evidence-bound `close-plan` |

## Boundaries that remain authoritative elsewhere

- Product behavior: `docs/PRODUCT.md` and `docs/product-specs/`
- Architecture and ownership: `ARCHITECTURE.md` and `docs/design-docs/`
- Quality and Gate semantics: `docs/QUALITY.md`
- Security and evidence handling: `docs/SECURITY.md`
- Planning and closure: `docs/PLANS.md`

No statement in this reference authorizes an external write or old-repository operation.
