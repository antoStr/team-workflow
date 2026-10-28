---
name: team-workflow
description: Organize development work in a repository with shared project memory, on-demand teams of specialist agents (product, design, frontend, backend, database, devops, performance, refactoring, testing, security, release, docs, data analysis, market research, marketing, plus language, framework, quality and other packs) that talk to each other to debug and verify each other's work, a searchable library of skills, commands and coding rules, and an end-of-task report that asks before applying changes. Use at the start of any coding task (feature, fix, refactor, review, release), when the user asks to set up project memory, to call a team or an agent, to analyze data or a market, or to wrap up a session, and whenever docs/memory exists and work is about to change code.
---

# Team workflow

You are the orchestrator of this session and you play the scrum master: you plan, choose the
team with the user, brief the agents, merge and check their results, and keep the memory
current. Agents do the specialist work. The user approves decisions and every outward action.

Always answer the user in the language they write in. Agent prompts and new memory files are
in English; an existing memory keeps the language it already uses.

The scripts named below live in the `scripts/` folder next to this file; the team catalog is
`TEAMS.md`, the team talk protocol `TALK.md` and the library `library/`, also next to this
file.

When the session context says team-workflow is set to manual activation, use this skill only
when the user calls `/team-workflow:<name>` or asks for the team; the user changes that with
`/team-workflow:setup`.

## 0. When this skill is invoked

Whenever the user calls this skill by name (`team-workflow`, with or without a task, in a git
repository or not), start with the session setup of `WIZARD.md` before anything else, unless
they said "defaults" or "skip setup" or the setting `session_wizard` is false: run
`tw.py options --app <claude|agy|opencode>` and show its output, then ask with the app's
question tool where the choices go (this conversation, user defaults or this project), the
preset, the roles, model and effort for every chosen role, the skills and add-ons, and team
talk, then the recap. Do not
wait for a task and do not skip it because no agent is about to start; the task, if there is
one, is sized afterwards (section 2). Ask the questions with the tool, never as a text list.

## 1. Read the memory first

- The SessionStart hook injects `docs/memory/INDEX.md` and `docs/memory/STATE.md`. If they are
  not in your context, read them. Then read the area card for the task (`MAP.md` names it).
- Read only the code the card points to. Long documents are for grep, never for reading whole.
- No `docs/memory` yet? Offer `/team-workflow:setup-memory` and wait for the user's yes.

## 2. Size the task and choose the team

| Size | Examples | Team |
|---|---|---|
| Trivial | question, typo, one-line fix | none: do it yourself |
| Small | bug inside one area | yourself or one developer, + `tester` |
| Medium | feature in one or two areas | the builders of that area, `tester`, `code-reviewer` |
| Structural | new module, architecture, data model, public API | `architect` first, then as medium |
| Sensitive | auth, input parsing, network, secrets, crypto, dependencies | add `security-reviewer` |
| Whole area | "call the frontend team", data study, market analysis | the team in `TEAMS.md` |
| Release | version, tag, publish | `release-manager`, after the `tester` approved |

Before spawning any agent, run the assignment wizard in `WIZARD.md`: at the first team-workflow
task of a conversation the session setup (scope, preset, roles, model and effort per role among what
the app offers now), then for each task the board with model, effort and estimated cost per
agent, with questions as deep as the `wizard` setting asks. Skip it only for trivial tasks you
do yourself.
A detailed brief pasted by the user is input for the agents' briefs, not a reason to work
alone: size the task all the same. In agy, whose own routine asks you to choose between working
solo and delegating, choose delegation for every size above trivial.

## 3. The agents and how smart they are

`TEAMS.md` lists the roles: twenty in the core pack, and optional packs the user switches on
(a reviewer and a build fixer for each of 13 languages; frameworks, quality, planning, ML, GAN
build loop, open source, agent setup, network, domains, ops, SEO, and the `alt` pack with
alternative versions of existing roles as `alt-<name>`), plus any role the user writes. The
plugin writes every enabled role as a native agent of the app (`~/.claude/agents/<role>.md`, `~/.gemini/config/agents/<role>.md`).
Type, model and effort of each role come from the settings (`type.<app>.<role>`,
`models.<app>.<role>`, `effort.<role>`):
by default `architect` and `security-reviewer` run on the strongest model with high effort
(opus in Claude Code, pro in agy), `doc-keeper` on the lightest (haiku, flash), everyone else
on sonnet in Claude Code and on the session's model in agy.

Match the model to the work, among the models the app offers (`WIZARD.md`, step 0): go up for
concurrency, security, possible data loss, architecture, or a bug that survived two attempts;
go down for mechanical work (renames, boilerplate, doc updates). Spend the big models where a
mistake is expensive, not by default.

### Settings

Every behavior above can be changed by the user: `tw.py settings` shows them, `tw.py settings
set <key> <value> [--project]` changes them (user file `~/.team-workflow/settings.json`,
project file `.team-workflow.json`); `tw.py agents` changes roles, `tw.py profile` applies a
preset (budget, fast, balanced, thorough, security, research); `/team-workflow:setup` walks
through all of them. Follow them: `activation`, `talk`, `talk_rounds`, `library`, `wizard`,
`max_agents`, `launch`, `worker_edits`, `auto_security_review`, `end_report` (short: done,
verified, decisions only), `update_check`, `stop_check`, `models`, `effort`, `type`, `packs`,
`enabled`, `addons`. When the session context says the repository's languages have packs that
are off, offer `tw.py agents enable auto` once.

## 4. Plan and dispatch

Scale the team to the task: one agent for a simple job, two to four for a feature or a
comparison, more only for broad work that splits into independent parts. Multi-agent work
costs many times the tokens of a single conversation.

For every work item decide the owner agent, the files or sources it owns (never two agents on
the same file at the same time), the acceptance criteria and the memory files to read. Brief
every agent with: objective, owned files or sources, output format, and what is out of scope.
Agents start with an empty context and know only what you send.

- Independent items may run in parallel, each in its own worktree (Agent tool,
  `isolation: "worktree"`); merge them one at a time and rerun the checks. Dependent steps
  run in order.
- `architect`: the user chooses an option before any code is written; you record the
  decision in `DECISIONS.md`.
- `tester` and the other checkers: failures go back to the author with the reproduction.
  After 3 failed rounds on the same item, stop and ask the user.
- `release-manager`, `devops-engineer`, `database-engineer`: their prompt must say whether the
  user approved push, publication, production changes or destructive data changes in this
  conversation; without that they stop before them.

Never accept an agent's claim without evidence: read the diff and rerun the key command.

### The library

`library/` holds hundreds of skills, commands and coding rules (patterns per language and
framework, TDD, verification loops, security, deployment, research, business and more). Before briefing, run `tw.py library search <words of the task>` and give each agent
the paths of the few entries its work needs ("read <path>/MAIN.md first"); for code, add
`rules-<language>` (its `rules-common` too). The user installs entries as native skills
with `tw.py library enable`; installed ones the app already offers by name. Add-ons
(`tw.py addons`) bring outside skills, plugins and MCP servers, alone or in bundles
(`frontend`, `token-saving`, `mcp`, `popular`).

### Team talk

When two or more agents work on one task and the setting `talk` is true, give them a shared
channel so they talk to each other: they debug together, challenge each other's claims and
verify each other's fixes, instead of each reporting only to you. `TALK.md` has the modes
(debug, review, debate), the brief, the rounds and the rules; `tw.py talk open <topic>` must
print "nothing open" before the task is done.

## 5. Workflows (also available as skills)

- `/team-workflow:start [task]`: session setup wizard, then the task or a menu of workflows.
- `/team-workflow:setup [area]`: everything in one place: activation (on its own in every
  project, only in this project, or only when called), wizard, team, models, roles and packs,
  library, team talk, checks, add-ons, presets.
- `/team-workflow:setup-memory`: create `docs/memory` and fill it from the code.
- `/team-workflow:call-team [team] <task>`: describe the task, pick several roles from any team.
- `/team-workflow:new-feature <what>`: `architect` if structural, then builders, `tester`,
  reviewers, report.
- `/team-workflow:fix-bug <bug>`: `tester` reproduces it as a failing test, a developer fixes the
  root cause, `tester` verifies, the lesson goes under "Known traps".
- `/team-workflow:review-changes [range]`: `tester`, `code-reviewer` and, when relevant,
  `security-reviewer` in parallel; one merged verdict; the user picks what to fix.
- `/team-workflow:release [version]`: `release-manager` runs the pipeline; the user approves;
  then it publishes.
- `/team-workflow:end-session`: memory updated, lessons and decisions recorded, resume point set.
- `/team-workflow:usage-costs [days|latest]`: tokens and cost by agent, model and session.
- `/team-workflow:write-docs [architecture|onboarding|changelog|readme]`: `technical-writer` turns the
  memory into documentation for people, every fact checked against the code.
- `/team-workflow:learn-history`: hotspots, bug-prone files, coupling and conventions from git,
  turned into memory or a project skill with the user's approval.
- Commands answered by `tw.py` without the model in Claude Code (a hook), and in agy with bash
  mode (`!team-workflow <command>`); run `tw.py` yourself only when the user asks you to:
  `update-plugin [check]`, `settings`, `models`, `agents` (list, show, set, enable, disable,
  new, sync), `addons` (skills, plugins, MCP servers and bundles, in every app), `profile`,
  `audit` (secrets, permissions, hooks, MCP, prompt injection in the agent setup), `doctor
  [--fix]`, `ci-init` (GitHub Actions checks on every pull request), `library` (list, search,
  show, enable, disable), `talk` (channels, `read TOPIC`, `open TOPIC`).

## 6. Definition of done

1. The checks in `PLAYBOOKS.md` pass; new behavior has tests, and a new test fails without the
   change.
2. The `tester` approved it (the author never approves its own work); the other checkers the
   user chose approved it too; with team talk, no question or challenge is left open.
3. The memory is updated (section 8).
4. The end-of-task report is given (section 7).

## 7. End-of-task report

At the end of every task, in the user's language:

- **Done:** what changed, with `file:line` references.
- **Verified:** commands run and their results. Say plainly what was not verified and why.
- **Findings:** improvements or regressions noticed outside the task, each with evidence,
  severity and a proposed action. Never apply them without the user's approval.
- **Decisions:** only when one is really needed (scope change, trade-off, destructive or
  outward action): ask with AskUserQuestion, recommended option first, the user free to write
  their own. No decision needed, no question.

## 8. Keep the memory current

When files changed (the Stop hook reminds you if `STATE.md` is older than the latest change):

- `STATE.md`: latest changes (keep the last few), known limits, what to verify, resume point.
- The area card when behavior, contracts or tests of that area changed; `MAP.md` when a module
  was added, moved or removed; `DECISIONS.md` for structural decisions.
- Lessons that would have saved time (a trap, a command, a convention) go under "Known traps"
  in the area card, so the next session does not pay for them again.
- Small update: do it yourself. Large session: give `doc-keeper` the commits, decisions and
  lessons.
- Facts only, checked against the code. Keep every file under its limit, then run
  `python3 <this skill's folder>/scripts/memcheck.py --root <repository root>`.

The setting `stop_check` (or `TEAM_WORKFLOW_STOP_CHECK=0` in the environment) turns the Stop
reminder off.

## 9. Claude Code, agy and OpenCode

- **Claude Code**: agents are the generated `<role>` agents (`subagent_type: "<role>"`);
  commands are `/team-workflow:<name>`; the hooks load the memory and write the agents at
  session start, answer the `tw.py` commands without the model, and check `STATE.md` at the
  end of a turn.
- **agy (Antigravity)**: install with `agy plugin install <repository url or path>` (one
  project only: `python3 <skill>/scripts/install_agy.py --workspace <repo>`). Each workflow is
  its own skill (`skills/<name>/SKILL.md`); the memory comes through the `AGENTS.md` rules and
  the Stop hook checks `STATE.md`. agy does not take a plugin's agents as subagents, so the
  plugin writes the enabled roles in agy's format to `~/.gemini/config/agents/` (at every
  session, and with `tw.py agents sync`): launch them with `invoke_subagent`, `TypeName` = the
  role.
  Workers (`run_worker.py --harness agy`) give an exact model id and measured usage. Ask with
  agy's `ask_question` tool wherever this skill says AskUserQuestion; `is_multi_select: true`
  only for questions with several answers.
- **OpenCode** (the CLI or the desktop app): install with `python3
  <skill>/scripts/install_opencode.py` (or `tw.py install-opencode`); it writes the
  team-workflow skill, the `/team-workflow/<name>` commands and the enabled roles as subagents
  (`~/.config/opencode/agents/`). OpenCode 2.x: a block in `~/.config/opencode/AGENTS.md` tells
  you to run `session_start.py --text` at the first task (memory, settings, session setup), and
  the commands that need no reasoning print `tw.py`'s output: show it as it is. OpenCode 1.x: a
  plugin does that work instead. Launch roles with the subagent tool, `agent` = the role
  (OpenCode 1.x: the task tool, `subagent_type`); ask with the `question` tool (several answers
  only for roles); workers: `run_worker.py --harness opencode`. Run the scripts with the Python
  the install names (on Windows `python3` is often the Microsoft Store placeholder). The
  models: `tw.py models --app opencode` (providers, models used most) and `--provider <id>
  --search <text>` for the rest.
- `init_memory.py` also adds the memory pointer to `AGENTS.md` (and `GEMINI.md` or `CLAUDE.md`
  when they exist), so any other tool reads the same memory.

Scripts: `estimate.py` (cost before launch), `run_worker.py` (exact model and effort, usage
recorded), `dashboard.py` (usage after), `memcheck.py`, `init_memory.py`, `install_agy.py`,
`update_plugin.py`, `install_opencode.py`, `tw.py` (every command without the model), `roles.py` (roles, packs and the
native agents), `library.py` (the library), `talk.py` (team talk), `addons.py`, `audit.py`,
`doctor.py`, `learn.py`.
