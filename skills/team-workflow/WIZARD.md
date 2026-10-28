# Assignment wizard

Run it every time you are about to spawn one or more agents: a team, a feature, a fix, a
review, a release, or a direct request. It turns "call the team" into one precise brief per
agent, with the model, the effort and the expected cost agreed before anything starts.

## Session setup (first team-workflow task of every conversation)

When the setting `session_wizard` is true (the default), before the first agent of a
conversation is launched, agree with the user which agents this conversation uses and how,
among what the app offers right now. Do it once; later tasks in the same conversation reuse
it and go straight to the board. Skip it when the user says "defaults" or "skip setup".

1. Run `python3 <skill>/scripts/tw.py options --app <claude|agy|opencode>` for the app you
   run in and show its output to the user as it is, in a code block: the models and efforts
   the app offers to native agents and to workers, every enabled role with its current type,
   model, effort and how it really runs, and when each can be changed. The user must see this
   before any question. (`--json` gives the same data for you; `--app all` the three apps.)
2. One call, two single-choice questions: **where the choices go**, "This conversation only
   (Recommended)", "My defaults for every project" (user file), "This project's defaults"
   (project file; in a git repository only), and the **preset**: "Keep my settings
   (Recommended)", `budget`, `fast`, `thorough`, `security`, `research`.
3. One call, multi-select: the **roles** this conversation will use ("Who builds?", "Who
   checks?", the enabled roles the likely work needs first); mention packs that are off when
   the repository needs them (`languages_here`).
4. For **every** chosen role, a **model** and an **effort** question, never merged across
   roles: two roles per call (four questions), repeated until all chosen roles are asked.
   Only values from step 1. The role's current value is the first option, marked
   "(current)"; fill the other options with the closest alternatives (a question has at most
   four options: the rest of the step 1 list stays available through the free-text answer).
   Each option says how it runs:
   - Claude Code: any model through the Agent tool's `model` parameter (native); an effort
     different from the agent file's runs as a worker in this conversation. haiku has no
     effort: skip the effort question for it.
   - agy: model `inherit` = the session model (name it, for example `gemini-3.8-flash-high`),
     `flash`, `pro` (native, no effort: the effort question offers "session effort
     (current)" or an exact worker id such as `gemini-3.8-flash-low`); any other exact id
     from step 1 runs as a worker, its effort is the id's suffix. `pro` is Gemini 3.1 Pro,
     older than the 3.8 flash models.
   - OpenCode: the agent file's model and variant (native); any other `provider/model` or
     variant runs as a worker. OpenCode's own model picker and variant key work on the
     conversation's model only, and a skill cannot open them or draw a slider: the question
     tool, with the model search below, is how models and efforts are chosen here. A role set
     to `inherit` follows what the user picked in OpenCode's picker.
     Models, never from the short list alone: step 1 shows only favorites and recent picks, but
     the user may have hundreds of models (NanoGPT, OpenRouter...). First ask, single choice,
     "Which model for the roles?": "Keep inherit: the conversation's model (Recommended)",
     one option per favorite or recent model, "One model for all chosen roles: I search it",
     "Different per role". For a search, ask the family in free text (for example `glm 5.3`),
     run `tw.py models --app opencode --provider <id> --search <words> --json`, and offer the
     matches (name, id, variants) as options, the closest first; with more than four, say how
     many there are and let the user narrow the words. Take the effort from that model's
     variants only (none listed = no effort question) and ask it once for "all roles" or per
     role, as the user chose. Never answer "only these models exist" from the short list.
5. One call, up to two multi-select questions: the **skills** and the **add-ons** for this
   conversation. Skills: run `tw.py library search <words of the task, or the repository's
   languages> --json` and offer the three best entries plus `rules-<language>` of the
   repository; chosen entries are given to the agents by path (nothing is installed unless the
   scope is a default: then `tw.py library enable <id> [--project]`). Add-ons: the bundles not
   chosen yet (`frontend`, `token-saving`, `mcp`, `popular`, from step 1) and single add-ons
   the work needs; installing one downloads it and writes the apps' configuration, so run
   `tw.py addons add <name>` only for what the user picked, and say a restart loads it.
6. When two or more roles were chosen, one single choice for **team talk** (`TALK.md`): "On,
   up to 3 rounds (Recommended)", "On, 1 round (cheaper)", "Off: each agent reports only to
   you". Skip it with one role.
7. Always show the session recap before asking to confirm; never skip it: a code block with
   the scope, the preset, one block per role (type, model, effort, native or worker), the
   skills, the add-ons and team talk. Ask, single choice: "Start (Recommended)", "Change".
   With a default scope, save: `tw.py agents set <role> model=... effort=... [--app <app>]
   [--project]`, `tw.py profile <name> [--project]`, `tw.py settings set talk|talk_rounds ...
   [--project]`; native agents pick saved changes up after the app restarts, so for this
   conversation keep the worker launch where step 4 said so.

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
- `models.<app>.<role>`, `effort.<role>` and `type.<app>.<role>`: the recommended model,
  effort and agent type of each role (`default` for the others); `packs.<pack>` and
  `enabled.<role>`: which roles exist at all. Propose only enabled roles; when the task needs
  a role whose pack is off (a language reviewer, the quality pack), say which pack to enable.

Offer only models and efforts the app really has (`tw.py models` lists them):

- **Claude Code**: `haiku`, `sonnet`, `opus`, `fable` (or a full model id); effort `low`,
  `medium`, `high`, `xhigh`, `max` where the model supports it (haiku has none). A custom
  agent runs at the effort of its generated file: to change it for good, `tw.py agents set
  <role> effort=<e>`; for one run only, use a worker.
- **agy custom subagent**: `inherit` (the session's model), `flash` or `pro`, set per role
  (`tw.py agents set <role> model=pro --app agy`), not per launch.
- **agy worker**: any id from `agy models` (for example `gemini-3.8-flash-high`,
  `gemini-3.1-pro-low`, `claude-sonnet-4-6`); the effort is part of the id.
- **OpenCode custom subagent**: `inherit` (the calling agent's model) or a `provider/model` of
  any provider the user connected (NanoGPT, OpenRouter, Anthropic...), and a variant (the
  effort), set per role in the agent file. Offer only the variants that model lists (for
  example GLM 5.3: `low`, `high`, `max`; none listed = no effort question). The options show
  the providers and the models used most; for any other, ask the user for a provider and a
  name, then `tw.py models --app opencode --provider <id> --search <text> --json` and offer
  what it finds (the model's name, its id, its variants).
- **OpenCode worker**: any `provider/model` with a variant (run as `provider/model#variant`).

Asking: in Claude Code use AskUserQuestion; in agy its `ask_question` tool; in OpenCode its
`question` tool. Set multi-select (`multiSelect: true`, in agy `is_multi_select: true`, in
OpenCode the question tool's multiple answers) only where several answers make sense, the roles; every other
question is single-choice, so the user is never shown checkboxes for a one-answer question.
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
the boundaries (SKILL.md, section 4). How each agent starts depends on its type in the
settings (`type.<app>.<role>`, shown by `tw.py agents`):

- **custom** (default): the generated agent named after the role, with the model and effort
  of the settings.
  - Claude Code: the Agent tool with `subagent_type: "<role>"` (for example `"tester"`); add
    `model` only when the user chose a different model for this run.
  - agy: `invoke_subagent` with `TypeName: "<role>"`, `Role` a short job title and `Prompt` the
    brief; independent agents go in one call and run in parallel.
  - OpenCode: the subagent tool with `agent: "<role>"`, a short `description` and the brief as
    `prompt` (OpenCode 1.x: the task tool with `subagent_type`); several calls in one message
    run in parallel.
  If the role is not in the app's agent list (first session after an install or a settings
  change), run `python3 <skill>/scripts/tw.py agents sync`, tell the user to restart the app,
  and for now launch it as a built-in type briefed with the role.
- **built-in** (`general-purpose`, `Explore`, `Plan` in Claude Code; `self`, `research` in
  agy; `general`, `explore` in OpenCode): launch that type and put the role's instructions first in the prompt; get them with
  `python3 <skill>/scripts/tw.py agents show <role>`.
- **worker**: an exact model and effort, or measured usage in agy:

  `python3 <skill>/scripts/run_worker.py --harness claude|agy|opencode --role <role> --model <model> --effort <effort> --root <repository> --task-file <brief.md> [--allow-edits]`

  Workers are read-only unless the user agreed to `--allow-edits` for that agent (or the
  setting `worker_edits` is true). Tools that need a permission prompt are denied in headless
  runs, so roles that must run tests or builds are better launched as custom agents.

## 5. After the run

Show real against estimated use:
`python3 <skill>/scripts/dashboard.py --root <repository> --session latest`.
The next estimates for the same role use this history.
