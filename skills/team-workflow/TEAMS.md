# Teams

Teams are menus, not squads: you propose the roles the task needs, the user picks, and only
those agents are spawned. One agent for a simple task, two to four for a comparison or a
feature, more only for broad work that splits into independent parts. Multi-agent work costs
many times the tokens of a single conversation (Anthropic measured about 15x on research):
spend it where parallel work or an independent check pays back.

| Team | Build | Check |
|---|---|---|
| product | `product-manager`, `ui-ux-designer`, `planner` | `market-researcher`, `architect` |
| frontend | `frontend-dev`, `ui-ux-designer` (with the frontend add-on skills: impeccable, taste, frontend-design, solar-icons) | `accessibility-specialist`, `e2e-tester`, `performance-engineer`, `code-reviewer`, `typescript-reviewer`, `react-reviewer`, `vue-reviewer`, `flutter-reviewer` |
| backend | `backend-dev`, `database-engineer` | `tester`, `security-reviewer`, `performance-engineer`, `code-reviewer`, `<lang>-reviewer`, `database-reviewer`, `django-reviewer`, `fastapi-reviewer` |
| fullstack | `backend-dev`, `frontend-dev`, `database-engineer` | `tester`, `e2e-tester`, `code-reviewer`, `security-reviewer`, `<lang>-reviewer` |
| data | `data-analyst`, `database-engineer`, `pytorch-build-fixer` | `tester` (for scripts that ship), `ml-reviewer`, `rag-reviewer` |
| marketing | `market-researcher`, `marketing-strategist`, `seo-specialist` | `product-manager`, `ui-ux-designer` |
| quality | none | `tester`, `e2e-tester`, `code-reviewer`, `security-reviewer`, `accessibility-specialist`, `performance-engineer`, `silent-failure-hunter`, `type-design-reviewer`, `test-coverage-reviewer`, `database-reviewer`, `comment-analyzer`, `commit-reviewer` |
| release | `release-manager`, `devops-engineer`, `open-source-packager`, `open-source-forker` | `tester`, `technical-writer` (notes and docs), `open-source-sanitizer` (public releases) |
| maintenance | `refactor-specialist`, `code-simplifier`, `build-fixer`, `<lang>-build-fixer`, `<framework>-build-fixer` | `tester`, `code-reviewer`, `performance-engineer` |
| docs | `technical-writer`, `doc-keeper` | none |
| architecture | `architect`, `code-architect`, `code-explorer`, `spec-miner`, `planner`, `docs-lookup` | `database-engineer`, `security-reviewer`, `performance-engineer`, `devops-engineer` |
| agent setup | `harness-optimizer`, `loop-operator` | `security-reviewer`, `agent-evaluator`, `conversation-analyzer` |
| build loop | `gan-planner`, `gan-generator` | `gan-evaluator` (scores each round until it passes) |
| network | `network-architect`, `homelab-architect` | `network-config-reviewer`, `network-troubleshooter`, `security-reviewer` |
| domain | the builders of the task | `healthcare-reviewer` (clinical, PHI), `bengali-reviewer` (Bengali text and NLP) |
| operations | `chief-of-staff` (email, chat and calendar triage, drafts) | none |

Roles outside the core come from packs the user switches on (`tw.py agents enable <pack>`, or
`auto` for the languages of the repository). Propose a pack role only when its pack is on; when
it is off and the task needs it, say which pack to enable. `<lang>` is the repository's
language: `go`, `rust`, `python`, `typescript`, `java`, `kotlin`, `cpp`, `csharp`, `swift`,
`dart`, `php`, `ruby`, `fsharp`; `<framework>` is `react`, `django` or `pytorch`
(pack `frameworks`, with `react-reviewer`, `vue-reviewer`, `django-reviewer`,
`fastapi-reviewer`, `flutter-reviewer`, `harmonyos-specialist`).

When two or more roles work on one task, they talk to each other through the team channel
(`TALK.md`): builders and checkers challenge and verify each other directly.

The main session is always the orchestrator and scrum master: it plans, briefs, merges the
results and keeps the memory.

## All agents

The core pack is always on; model, effort and agent type of every role come from the settings
(`tw.py agents` shows them per app). By default `architect` and `security-reviewer` use the
strongest model with high effort, `doc-keeper` the lightest, the rest the standard model.

| Agent | Pack | Role | Writes |
|---|---|---|---|
| `product-manager` | core | scope, user stories, acceptance criteria, priorities | specs only |
| `architect` | core | structural options and decision records | nothing |
| `ui-ux-designer` | core | flows, screens, states, design system | specs; styles when assigned |
| `frontend-dev` | core | UI code with tests | assigned files |
| `backend-dev` | core | server, CLI, library and data code with tests | assigned files |
| `database-engineer` | core | schema, migrations, queries, integrity | migrations and queries |
| `devops-engineer` | core | CI/CD, containers, infrastructure, monitoring | pipeline and infra files |
| `performance-engineer` | core | profiling, benchmarks, load tests | optimizations with numbers |
| `refactor-specialist` | core | refactoring, cleanup, structure for scale | assigned files, same behavior |
| `tester` | core | failing test first, independent verification | tests only |
| `e2e-tester` | core | end-to-end user flows in a browser | end-to-end tests only |
| `accessibility-specialist` | core | WCAG 2.2 AA audit | report; fixes when assigned |
| `code-reviewer` | core | quality review | nothing |
| `security-reviewer` | core | security review from input to impact, including LLM features | nothing |
| `release-manager` | core | pipeline, version, tag, notes, publication | release files |
| `technical-writer` | core | README, guides, API docs, release notes, docs from the memory | documentation |
| `doc-keeper` | core | project memory from the diff | `docs/memory` |
| `data-analyst` | core | spreadsheets and data: cleaning, statistics, charts, report | analysis outputs |
| `market-researcher` | core | competitors, customers, market size, with sources | research report |
| `marketing-strategist` | core | positioning, launch, copy, SEO, metrics | marketing copy |
| `<lang>-reviewer` | `<lang>` | idiom, safety and correctness of one language, with its tools | nothing |
| `<lang>-build-fixer` | `<lang>` | smallest fix for a red build, type check or dependency error | assigned files |
| `silent-failure-hunter` | quality | swallowed errors, hiding fallbacks, missing timeouts | nothing |
| `type-design-reviewer` | quality | invariants and illegal states in types and schemas | nothing |
| `test-coverage-reviewer` | quality | whether the tests would catch the bugs that matter | nothing |
| `planner` | planning | step-by-step implementation plan with owners and tests | plans |
| `code-explorer` | planning | traces how an existing feature works | nothing |
| `ml-reviewer` | ml | data, training, evaluation, serving and monitoring of models | nothing |
| `rag-reviewer` | ml | ingestion, retrieval, grounding, injection and evaluation of RAG | nothing |
| `open-source-sanitizer` | opensource | secrets, personal data and internal references before publishing | nothing |
| `harness-optimizer` | harness | agent setup: permissions, hooks, MCP, context and cost | proposals |
| `seo-specialist` | growth | technical and on-page SEO, structured data, Core Web Vitals | report; fixes when assigned |
| `build-fixer` | quality | any red build or type check, smallest diff | assigned files |
| `code-simplifier` | quality | simpler code with the same behavior | assigned files |
| `comment-analyzer` | quality | comments that lie, rot or say nothing | nothing |
| `commit-reviewer` | quality | reviews the staged diff and drafts a commit message in the repository's style | nothing |
| `database-reviewer` | quality | queries, schema, indexes, migrations, RLS | nothing |
| `code-architect` | planning | feature blueprint from the existing patterns: files, interfaces, order | plans |
| `spec-miner` | planning | the spec an existing codebase implements, recovered from code and tests | specs |
| `docs-lookup` | planning | current library and API docs, quoted with sources | nothing |
| `react-reviewer`, `vue-reviewer`, `django-reviewer`, `fastapi-reviewer`, `flutter-reviewer` | frameworks | framework idiom, safety and performance | nothing |
| `react-build-fixer`, `django-build-fixer` | frameworks | red builds of that framework | assigned files |
| `harmonyos-specialist` | frameworks | HarmonyOS apps in ArkTS and ArkUI: state, navigation, APIs | assigned files |
| `pytorch-build-fixer` | ml | PyTorch runtime, CUDA, shape and dtype errors | assigned files |
| `agent-evaluator` | harness | scores an agent's output on accuracy, completeness, clarity, actionability, concision | nothing |
| `conversation-analyzer` | harness | finds behaviors in agent transcripts worth preventing with hooks | nothing |
| `loop-operator` | harness | runs and watches autonomous loops, stops them when stuck | loop state |
| `gan-planner`, `gan-generator`, `gan-evaluator` | gan | plan, build and score in rounds until the evaluator passes it | spec; assigned files; scores |
| `open-source-forker`, `open-source-packager` | opensource | a public fork without private parts; README, license, packaging | assigned files |
| `network-architect`, `homelab-architect` | network | network and homelab designs: VLANs, DNS, VPN, routing | plans |
| `network-config-reviewer`, `network-troubleshooter` | network | router and switch configs; connectivity diagnosis | nothing |
| `healthcare-reviewer` | domains | clinical safety, PHI and compliance of healthcare code | nothing |
| `bengali-reviewer` | domains | Bengali text, NLP and localization | nothing |
| `chief-of-staff` | ops | triage of email, chat and calendar, drafted replies | drafts |

The user can add roles or override one (`tw.py agents new <role>`) and choose, per role and per
app, the agent type: `custom` (the generated agent), `worker`, or a built-in type briefed with
the role (Claude Code `general-purpose`, `Explore`, `Plan`; agy `self`, `research`).

## Asking the user

A team is not fixed: the roles can come from several teams. AskUserQuestion (agy:
`ask_question`) shows at most four options per question, so ask two multi-select questions in
one call: "Who builds?" (Build column) and "Who checks?" (Check column), the roles this task
needs first and marked "(Recommended)". Leave out the roles the task does not need; the user
can name others in their free-text answer.

## Running a team

- Brief every agent with: the objective, the files or sources it owns, the output format and
  what is outside its scope. Vague briefs make agents duplicate or skip work.
- Run in parallel only independent work (reviews, research, separate areas in separate
  worktrees); steps that depend on each other run in order.
- Builders never approve their own work; the checkers the user chose always run.
- Merge the results yourself, check them against the evidence, then report.
