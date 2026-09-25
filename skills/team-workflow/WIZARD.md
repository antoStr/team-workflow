# Assignment wizard

Run it every time you are about to spawn one or more agents: a team, a feature, a fix, a
review, a release, or a direct request. It turns "call the team" into one precise brief per
agent, with the model, the effort and the expected cost agreed before anything starts.

## 0. Settings and the models on offer

The user's settings decide how much you ask. In Claude Code the non-default ones are in your
context ("team-workflow settings: ..."); elsewhere read them with
`python3 <skill>/scripts/tw.py settings --json`.

- `wizard`: `quick` (default) goes from step 1 straight to the board with the recommended
  choices and asks step 2 only for the agents the user wants to change; `full` asks step 2 for
  every agent; `off` skips the questions and launches with the recommended choices after
  showing the board. The user saying "defaults" (or "veloce") means `quick` for this run.
- `max_agents`: propose at most this many agents unless the user asks for more.
- `launch`, `worker_edits`, `auto_security_review`, `end_report`: as named.
- `models.<app>.<role>` and `effort.<role>`: the recommended model and effort of each role
  (`default` for the others).

Offer only models and efforts the app really has (`tw.py models` lists them):

- **Claude Code**: `haiku`, `sonnet`, `opus`, `fable` (or a full model id); effort `low`,
  `medium`, `high`, `xhigh`, `max`, but a native subagent runs at the effort of its agent file,
  so a different effort means a worker. Haiku has no effort.
- **agy native subagent**: `inherit` (the session's model), `flash` or `pro`; it is set in the
  role's agy agent file (`models.agy.<role>`, then `tw.py agents`), not per launch.
- **agy worker**: any id from `agy models` (for example `gemini-3.8-flash-high`,
  `gemini-3.1-pro-low`, `claude-sonnet-4-6`); the effort is part of the id.

Asking: in Claude Code use AskUserQuestion; in agy use its `ask_question` tool. Set multi-select
(`multiSelect: true`, in agy `is_multi_select: true`) only where several answers make sense,
the roles in step 1; every other question is single-choice (`multiSelect: false`,
`is_multi_select: false`), so the user is never shown checkboxes for a one-answer question.
Never fake a question as a markdown list with `[ ]` boxes.

## 1. Roles

Propose the roles this task needs (`TEAMS.md`), from any team, and let the user pick several
at once (multi-select). Ask "Who builds?" and "Who checks?" in the same call, at most four
options each, the roles the task needs first and marked "(Recommended)"; the user can name
other roles in the free-text answer.

## 2. Questions per agent (`wizard: full`, or the agents the user wants to change)

First estimate every model option you will offer:

`python3 <skill>/scripts/estimate.py --role <role> --size small|medium|large --effort <effort> --models <models> --files <paths it will read> --root <repository>`

Pass the models of the current app: `haiku,sonnet,opus,fable` in Claude Code; agy ids such as
`gemini-3.8-flash-high,gemini-3.1-pro-low` in agy (Gemini ids are priced in `pricing.json`).

Then ask up to four single-choice questions in one call, recommended option first:

1. **What it works on**: two or three concrete scopes you derived from the task (area, files,
   deliverable).
2. **How**: the approach, adapted to the role, for example "smallest change with tests",
   "thorough, with extra edge cases", "analysis first, then ask".
3. **Model**: up to four models of this app, each description with its estimate, for example
   "~2.6M tokens, $1.20 ($0.60-1.92)". Recommend the role's model from the settings unless the
   task needs more or less.
4. **Effort**: only where the launch can apply it (a worker, or agy where it is in the model
   id); recommend the role's effort from the settings.

The user can always write their own answer instead.

## 3. Assignment board

Show one block per agent, never a wide table (terminals wrap long cells and misalign the
columns), then the total, and ask for the go, single-choice ("Start (Recommended)", "Change an
agent", "Cancel"):

```
1. backend-dev    sonnet, medium, native      ~2.6M tokens, $1.20
   works on: src/api/orders.py and its tests
   how:      smallest change with tests
2. tester         sonnet, medium, native      ~1.1M tokens, $0.50
   works on: ...
   how:      ...
Total ~3.7M tokens, $1.70
```

"Change an agent" asks which one, then step 2 for it, then shows the board again.

## 4. Launch

Write the agreed "what" and "how" into each brief, with the owned files, the output format and
the boundaries (SKILL.md, section 4).

- **Native** (default, setting `launch`):
  - Claude Code: the Agent tool with `subagent_type: team-workflow:<role>` and
    `model: <choice>`.
  - agy: `invoke_subagent` with `TypeName: "<role>"` (the plugin keeps the roles in
    `~/.gemini/config/agents/` as agy subagents), `Role` a short job title and `Prompt` the
    brief; several independent agents go in one call and run in parallel. If a role is not in
    the subagent list, run `python3 <skill>/scripts/tw.py agents`, tell the user to restart agy,
    and meanwhile launch it as a worker.
- **Worker**: when the user wants an exact model or effort the native launch cannot give, or
  measured usage in agy:

  `python3 <skill>/scripts/run_worker.py --harness claude|agy --role <role> --model <model> --effort <effort> --root <repository> --task-file <brief.md> [--allow-edits]`

  Workers are read-only unless the user agreed to `--allow-edits` for that agent (or the
  setting `worker_edits` is true). Tools that need a permission prompt are denied in headless
  runs, so roles that must run tests or builds are better launched natively.

## 5. After the run

Show real against estimated use:
`python3 <skill>/scripts/dashboard.py --root <repository> --session latest`.
The next estimates for the same role use this history.
