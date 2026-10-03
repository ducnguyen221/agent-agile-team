# agent-agile-team

> **Status: private pre-release (`0.2.0-dev`).** Installable on Claude Code, Codex and Antigravity; not
> published. Vietnamese version: [README.vi.md](README.vi.md). Skill bodies and method documents are written
> in Vietnamese; frontmatter is English.

An agile method for AI agent teams. One person gives the request in plain words and answers at exactly
two gates; a team of agents does the rest and records it.

- **One process, six steps, two human gates:** intake → spec + plan (**Gate 1:** approve or adjust) →
  execute ↔ verify (loop, three rounds recommended) → report (**Gate 2:** pass / conditional pass / fail) →
  lessons. Agents stop to ask only in four named cases; asking anywhere else is a process error.
- **Roles by tier, not by model name:** Analyst, Architect, Implementer, QA, Business Reviewer, Tech
  Reviewer; tiers `T1` thinking · `T2` execution · `T3` chores and test runs. **Whoever does the work never
  grades it.**
- **Documents an agent can search cheaply:** four sprint documents (SPEC, PLAN, PROGRESS, REPORT, or one
  merged file for tiny jobs) and three project registries (requests, sprints, living specs) with an
  "open now" block at the top. Every item has a two-letter code (`FR3.2`, `TK4`, `RF2`).
- **28 skills and 7 read-only reviewer agents** for process, engineering technique, verification,
  communication and token economy.
- **Three standard-library Python tools:** `init` builds the skeleton without overwriting anything,
  `check` enforces the document rules, `index` regenerates the "open now" blocks.

The core is neutral: it knows nothing about any machine, person or project. A host environment plugs in
through five declared points — session-start loading, `AGENT_AGILE_TIERS`, `AGENT_AGILE_DENYLIST`, lesson
storage, and a cross-vendor bridge ([`hosts/README.md`](hosts/README.md)).

## Install

Paste the prompt at the end of [INSTALL.md](INSTALL.md) into your agent; it follows that file and asks
before touching anything. Manual steps per harness: [`hosts/`](hosts/README.md). Claude Code in short:

```bash
git clone https://github.com/ducnguyen221/agent-agile-team ~/agent-agile-team            # macOS, bash
claude plugin marketplace add ~/agent-agile-team
claude plugin install agent-agile-team@agent-agile-team
```

```powershell
git clone https://github.com/ducnguyen221/agent-agile-team "$HOME\agent-agile-team"      # Windows PowerShell
claude plugin marketplace add "$HOME\agent-agile-team"
claude plugin install agent-agile-team@agent-agile-team
```

then add `@~/agent-agile-team/AGENTS.md` to `~/.claude/CLAUDE.md` so the core rules load in every session.
Check: `python scripts/check.py --self` ends with `Đạt` (pass). Common problems:
[docs/troubleshooting.md](docs/troubleshooting.md).

## First sprint

[GUIDE.md](GUIDE.md) walks a newcomer through one sprint; [`samples/order-desk/`](samples/README.md) shows
a project after two sprints.

## Layout

| Path | Purpose |
|---|---|
| `AGENTS.md` | Core rules loaded at session start (budget: ≤120 lines, ≤10 KB) |
| `method/` | Process, sizing, severity scale, evidence, conventions |
| `roles/` · `tiers/` | Role cards (executors, verifiers, specialists); tier definitions and the tier-table contract |
| `skills/` · `agents/` | Skills, flat (`skills/<name>/SKILL.md`); read-only reviewer agents |
| `templates/` | Sprint documents, project registries, project config |
| `scripts/` · `tests/` · `samples/` | `init`, `check`, `index`; tests; a sample project with expected results |
| `hosts/` | Install and loading per harness, and the host plug points |
| `docs/` | Migration map from older skill names; standardization record |

## Acknowledgments

Distilled from Superpowers (obra), Everything Claude Code (affaan-m), gstack (garrytan), with concepts from
GitHub Spec Kit, OpenSpec, BMAD-METHOD and Kiro/EARS. Exact commits, licences and per-skill sources:
[UPSTREAM.md](UPSTREAM.md), [NOTICE](NOTICE), [THIRD_PARTY.md](THIRD_PARTY.md). Updating or extending from
those sources: [docs/updating-from-upstream.md](docs/updating-from-upstream.md).

## Licence

Not chosen yet; all rights reserved while private ([LICENSE](LICENSE)). Third-party content keeps its own
licence.

## Author

Nguyễn Quang Đức — <https://ducnguyen.vn>. Repository: <https://github.com/ducnguyen221/agent-agile-team> (private).
