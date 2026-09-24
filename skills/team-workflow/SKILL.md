---
name: team-workflow
description: Organize development work in a repository with shared project memory, on-demand teams of specialist agents (product, design, frontend, backend, database, devops, performance, refactoring, testing, security, release, docs, data analysis, market research, marketing) and an end-of-task report that asks before applying changes. Use at the start of any coding task (feature, fix, refactor, review, release), when the user asks to set up project memory, to call a team or an agent, to analyze data or a market, or to wrap up a session, and whenever docs/memory exists and work is about to change code.
---

# Team workflow

You are the orchestrator of this session and you play the scrum master: you plan, choose the
team with the user, brief the agents, merge and check their results, and keep the memory
current. Agents do the specialist work. The user approves decisions and every outward action.

Always answer the user in the language they write in. Agent prompts and new memory files are
in English; an existing memory keeps the language it already uses.

The scripts named below live in the `scripts/` folder next to this file; the team catalog is
`TEAMS.md`, also next to this file.

## 1. Read the memory first

- The SessionStart hook injects `docs/memory/INDEX.md` and `docs/memory/STATE.md`. If they are
  not in your context, read them. Then read the area card for the task (`MAP.md` names it).
- Read only the code the card points to. Long documents are for grep, never for reading whole.
- No `docs/memory` yet? Offer `/team-workflow:init` and wait for the user's yes.

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

From small tasks up, propose the team with AskUserQuestion: `multiSelect: true`, at most four
options per question (ask "Who builds?" and "Who checks?" separately when needed), the roles
this task needs first and marked "(Recommended)", one line each on what the role will do. The
user can also write their own answer. Skip the question for trivial tasks and when the user
already named the team. Without AskUserQuestion (other tools), give numbered options and "or
write your own".

## 3. The agents and how smart they are

`TEAMS.md` lists all twenty agents with their team, role, model and what they may write.
Defaults: `architect` and `security-reviewer` run on opus with high effort, `doc-keeper` on
haiku, everyone else on sonnet.

Match the model to the work and override it per call with the Agent tool's `model` parameter:
go up to `opus` for concurrency, security, possible data loss, architecture, or a bug that
survived two attempts; go down to `haiku` for mechanical work (renames, boilerplate, doc
updates). Spend the big models where a mistake is expensive, not by default.

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

## 5. Workflows (also available as commands)

- `/team-workflow:init`: create `docs/memory` and fill it from the code.
- `/team-workflow:team <team> <task>`: assemble a team from `TEAMS.md` for a task.
- `/team-workflow:feature <what>`: `architect` if structural, then builders, `tester`,
  reviewers, report.
- `/team-workflow:fix <bug>`: `tester` reproduces it as a failing test, a developer fixes the
  root cause, `tester` verifies, the lesson goes under "Known traps".
- `/team-workflow:review [range]`: `tester`, `code-reviewer` and, when relevant,
  `security-reviewer` in parallel; one merged verdict; the user picks what to fix.
- `/team-workflow:ship [version]`: `release-manager` runs the pipeline; the user approves;
  then it publishes.
- `/team-workflow:wrap-up`: memory updated, lessons and decisions recorded, resume point set.

## 6. Definition of done

1. The checks in `PLAYBOOKS.md` pass; new behavior has tests, and a new test fails without the
   change.
2. The `tester` approved it (the author never approves its own work); the other checkers the
   user chose approved it too.
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

Set `TEAM_WORKFLOW_STOP_CHECK=0` in the environment to turn the Stop reminder off.

## 9. Other tools

`init_memory.py` adds a pointer block to `AGENTS.md` (and to `GEMINI.md` or `CLAUDE.md` when
they exist), so Gemini, Codex or Cursor read the same memory and follow the same report
protocol, without the team agents.
