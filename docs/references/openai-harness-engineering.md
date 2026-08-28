# OpenAI harness engineering references

## Primary reference

- Source: [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/ko-KR/index/harness-engineering/)
- Role: primary design authority for the short `AGENTS.md` map, repository-as-system-of-record model, agent legibility, mechanical architecture constraints, observability, and recurring garbage collection.
- Retrieved context: the reference is external and remains authoritative upstream; this repository stores only a concise implementation mapping.

## ExecPlan reference

- Source: [Codex Exec Plans](https://cookbook.openai.com/articles/codex_exec_plans)
- Role: self-contained living plans, continuously updated progress and decisions, restartability without chat history, concrete steps, validation, recovery, and outcomes.

## Agent instruction and delegation references

- Source: [AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- Role: repository and directory-scoped instruction discovery.
- Source: [Subagents](https://developers.openai.com/codex/agent-configuration/subagents)
- Role: bounded delegation, fresh contexts, and caution around parallel write-heavy work.

## Local interpretation

OpenAI guidance is the primary source. Project-specific engineering defaults and the earlier Metis-inspired bounded packet ideas are subordinate implementation choices. The repository does not attempt to reproduce a durable orchestration runtime.
