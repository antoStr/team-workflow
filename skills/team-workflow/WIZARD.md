# Assignment wizard

Run it every time you are about to spawn one or more agents: a team, a feature, a fix, a
review, a release, or a direct request. It turns "call the team" into one precise brief per
agent, with the model, the effort and the expected cost agreed before anything starts.
Quick mode: when the user says "defaults" (or "veloce"), skip step 2 and go straight to the
board with the recommended choices.

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

## 2. One round of questions per chosen agent

First estimate every model option you will offer:

`python3 <skill>/scripts/estimate.py --role <role> --size small|medium|large --effort <default> --models haiku,sonnet,opus,fable --files <paths it will read> --root <repository>`

In agy use its model ids (`agy models`, for example `gemini-3.8-flash-high,claude-sonnet-4-6`):
they have no price in `pricing.json`, so show tokens only.

Then ask up to four questions in one call, recommended option first:

1. **What it works on**: two or three concrete scopes you derived from the task (area, files,
   deliverable).
2. **How**: the approach, adapted to the role, for example "smallest change with tests",
   "thorough, with extra edge cases", "analysis first, then ask".
3. **Model**: four models, each description with its estimate, for example
   "~2.6M tokens, $1.20 ($0.60-1.92)". Recommend the role's default unless the task needs more
   or less.
4. **Effort**: low, medium, high, xhigh (max through the free-text answer); recommend the
   role's default. Haiku has no effort.

The user can always write their own answer instead. All four are single-choice.

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

## 4. Launch

Write the agreed "what" and "how" into each brief, with the owned files, the output format and
the boundaries (SKILL.md, section 4).

- **Native** (default): in Claude Code, the Agent tool with `subagent_type: team-workflow:<role>`
  and `model: <choice>`; the effort is the one in the agent definition, because Claude Code
  cannot change it per launch. agy does not offer plugin agents as subagents yet: there, launch
  roles as workers, or brief its `self` subagent with `agents/<role>.md`.
- **Worker**: when the user wants an exact effort, a model the native launch cannot use, or
  measured usage in agy:

  `python3 <skill>/scripts/run_worker.py --harness claude|agy --role <role> --model <model> --effort <effort> --root <repository> --task-file <brief.md> [--allow-edits]`

  Workers are read-only unless the user agreed to `--allow-edits` for that agent. Tools that
  need a permission prompt are denied in headless runs, so roles that must run tests or builds
  are better launched natively.

## 5. After the run

Show real against estimated use:
`python3 <skill>/scripts/dashboard.py --root <repository> --session latest`.
The next estimates for the same role use this history.
