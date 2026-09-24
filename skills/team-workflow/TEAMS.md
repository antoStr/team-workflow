# Teams

Teams are menus, not squads: you propose the roles the task needs, the user picks, and only
those agents are spawned. One agent for a simple task, two to four for a comparison or a
feature, more only for broad work that splits into independent parts. Multi-agent work costs
many times the tokens of a single conversation (Anthropic measured about 15x on research):
spend it where parallel work or an independent check pays back.

| Team | Build | Check |
|---|---|---|
| product | `product-manager`, `ui-ux-designer` | `market-researcher`, `architect` |
| frontend | `frontend-dev`, `ui-ux-designer` | `accessibility-specialist`, `e2e-tester`, `performance-engineer`, `code-reviewer` |
| backend | `backend-dev`, `database-engineer` | `tester`, `security-reviewer`, `performance-engineer`, `code-reviewer` |
| fullstack | `backend-dev`, `frontend-dev`, `database-engineer` | `tester`, `e2e-tester`, `code-reviewer`, `security-reviewer` |
| data | `data-analyst`, `database-engineer` | `tester` (for scripts that ship) |
| marketing | `market-researcher`, `marketing-strategist` | `product-manager`, `ui-ux-designer` |
| quality | none | `tester`, `e2e-tester`, `code-reviewer`, `security-reviewer`, `accessibility-specialist`, `performance-engineer` |
| release | `release-manager`, `devops-engineer` | `tester`, `technical-writer` (notes and docs) |
| maintenance | `refactor-specialist` | `tester`, `code-reviewer`, `performance-engineer` |
| docs | `technical-writer`, `doc-keeper` | none |
| architecture | `architect` | `database-engineer`, `security-reviewer`, `performance-engineer`, `devops-engineer` |

The main session is always the orchestrator and scrum master: it plans, briefs, merges the
results and keeps the memory.

## All agents

| Agent | Model | Role | Writes |
|---|---|---|---|
| `product-manager` | sonnet | scope, user stories, acceptance criteria, priorities | specs only |
| `architect` | opus, high effort | structural options and decision records | nothing |
| `ui-ux-designer` | sonnet | flows, screens, states, design system | specs; styles when assigned |
| `frontend-dev` | sonnet | UI code with tests | assigned files |
| `backend-dev` | sonnet | server, CLI, library and data code with tests | assigned files |
| `database-engineer` | sonnet | schema, migrations, queries, integrity | migrations and queries |
| `devops-engineer` | sonnet | CI/CD, containers, infrastructure, monitoring | pipeline and infra files |
| `performance-engineer` | sonnet | profiling, benchmarks, load tests | optimizations with numbers |
| `refactor-specialist` | sonnet | refactoring, cleanup, structure for scale | assigned files, same behavior |
| `tester` | sonnet | failing test first, independent verification | tests only |
| `e2e-tester` | sonnet | end-to-end user flows in a browser | end-to-end tests only |
| `accessibility-specialist` | sonnet | WCAG 2.2 AA audit | report; fixes when assigned |
| `code-reviewer` | sonnet | quality review | nothing |
| `security-reviewer` | opus, high effort | security review from input to impact | nothing |
| `release-manager` | sonnet | pipeline, version, tag, notes, publication | release files |
| `technical-writer` | sonnet | README, guides, API docs, release notes | documentation |
| `doc-keeper` | haiku | project memory from the diff | `docs/memory` |
| `data-analyst` | sonnet | spreadsheets and data: cleaning, statistics, charts, report | analysis outputs |
| `market-researcher` | sonnet | competitors, customers, market size, with sources | research report |
| `marketing-strategist` | sonnet | positioning, launch, copy, SEO, metrics | marketing copy |

Override the model per call when the task is unusually risky (up to `opus`) or mechanical
(down to `haiku`).

## Asking the user

AskUserQuestion shows at most four options per question, so ask two questions for a team:
"Who builds?" (Build column) and "Who checks?" (Check column), `multiSelect: true`, the roles
this task needs first and marked "(Recommended)". Leave out the roles the task does not need;
the user can name others in their free-text answer.

## Running a team

- Brief every agent with: the objective, the files or sources it owns, the output format and
  what is outside its scope. Vague briefs make agents duplicate or skip work.
- Run in parallel only independent work (reviews, research, separate areas in separate
  worktrees); steps that depend on each other run in order.
- Builders never approve their own work; the checkers the user chose always run.
- Merge the results yourself, check them against the evidence, then report.
