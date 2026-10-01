# agent-agile-team

> **Status: under construction — private.** Not released, no install instructions yet. Vietnamese
> version: [README.vi.md](README.vi.md).

An agile method for AI agent teams: one process (intake → spec → plan → execute ↔ verify → report →
lessons, with two human gates), role cards with tiers instead of model names, sprint and registry
templates, a small set of skills, and three standard-library Python tools (`init`, `check`, `index`)
that keep the documents consistent.

The core in this repository is neutral: it knows nothing about any particular machine, person or
project. A host environment plugs in through two environment variables (`AGENT_AGILE_TIERS`,
`AGENT_AGILE_DENYLIST`) and its own session-start loader.

## Layout

| Path | Purpose |
|---|---|
| `AGENTS.md` | Core rules loaded at session start (size budget: ≤120 lines, ≤10 KB) |
| `method/` | Process, sizing, severity scale, evidence, conventions |
| `roles/` | Role cards: executors and verifiers (with specialist cards) |
| `tiers/` | Tier definitions and the tier-table contract |
| `skills/` | Skills, flat (`skills/<name>/SKILL.md`) |
| `agents/` | Reviewer and helper agents |
| `templates/` | Sprint documents, project registries, project config |
| `scripts/` | `init`, `check`, `index` |
| `tests/` · `samples/` | Tests and a sample project with expected results |
| `hosts/` | Per-harness notes (Claude, Codex, Claude Desktop, Antigravity) |

## Licence

Not chosen yet; all rights reserved while private. Third-party sources are tracked in
[UPSTREAM.md](UPSTREAM.md), [NOTICE](NOTICE) and [THIRD_PARTY.md](THIRD_PARTY.md).
