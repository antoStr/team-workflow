# team-workflow: reference manual

The getting-started guide is the [README](../README.md); to use and create agents there is the
[agent guide](AGENTS.md); the list of every agent and library entry is in
[CATALOG.md](CATALOG.md). This page has every detail, app by app.
[Versione italiana](REFERENCE.it.md).

A plugin for **Claude Code**, **agy (Antigravity)**, **OpenCode** and **Codex** that organizes
work on a project like a small team: a shared project memory, specialist agents that step in
only when needed, and an end-of-task report that asks before applying changes nobody asked for.

| Feature | Claude Code | agy | OpenCode |
|---|---|---|---|
| Memory read at every session | start-up hook | `AGENTS.md` rules | 2.x: block in `AGENTS.md`; 1.x: plugin (system prompt) |
| Reminder to update `STATE.md` | Stop hook | Stop hook | 2.x: in the instructions; 1.x: plugin (`session.idle`) |
| Commands (`setup-memory`, `call-team`, `write-docs`, `usage-costs`...) | `/team:<name>` | skill with the same name | `/team-workflow/<name>` |
| Native agents: 20 core + optional packs + yours | `~/.claude/agents/` | `~/.gemini/config/agents/` (`invoke_subagent`) | `~/.config/opencode/agents/` (subagent tool) |
| Start-of-conversation wizard: where to save choices (conversation, user, project), preset, agents, model and effort per app, skills, add-ons, team talk | yes | yes | yes |
| Tokens measured in the dashboard | sessions and subagents | workers only | sessions, subagents and workers |
| Zero-token commands (settings, agents, add-ons, audit, doctor...) | `/team:<command>` | `!team-workflow <command>` | `/team-workflow/<command>` (1.x: 0 tokens; 2.x: the model only shows the output) and `!team-workflow <command>` |
| Add-ons: skills, plugins and MCP servers, also in bundles (`frontend`, `token-saving`, `mcp`, `popular`) | marketplace, copied skills, `claude mcp add` | plugins or copied skills, `mcp_config.json` | copied skills, plugins and `mcp` in `opencode.json` |
| Agents that talk to each other (team talk) | yes | yes | yes |
| Library: 417 skills, 94 commands, 22 rule sets | search + native skills on demand | search + native skills on demand | search + native skills on demand |
| Automatic activation or only when called | yes | Stop check only | yes |

## What came in 0.9

- **127 agents** (137 today): 20 in the core, 26 for 13 languages, and the frameworks, quality,
  planning, ml, harness, gan, opensource, network, domains, ops, growth packs (and `pm` since
  then); the `alt` pack adds 39 alternative versions of existing roles (`alt-<name>`). Full list
  in the [full catalog](CATALOG.md).
- **A library** (533 entries today) that the orchestrator searches for every task and hands to
  the agents; install entries as native skills by pack or one at a time (`/team:library`). It
  only holds entries that work on their own.
- **Add-ons, MCP and bundles**: `addons add frontend | token-saving | mcp | popular` installs
  skills, plugins and MCP servers in Claude Code, agy and OpenCode in one go (see [Add-ons](#add-ons)).
- **Agents that talk to each other**: a shared channel to debug together, challenge claims with
  evidence and verify each other (`/team:talk`, `TALK.md`).
- **`/team:setup`**: every setting in one place, activation included (automatic in every
  project, only in some, or only when you call it).
- **Frontend set**: `addons add frontend` installs impeccable, taste, frontend-design,
  solar-icons and the Cloudflare skills, used by the frontend and security agents.

## What it does

- **Shared memory (`docs/memory`)**: Markdown files inside the repository, read by people and by
  any AI. At the start of each session a hook injects `INDEX.md` and `STATE.md`; when files
  change and `STATE.md` falls behind, a hook asks to update it.
- **Teams on demand**: the main session is orchestrator and scrum master; it proposes the team
  the task needs and you choose (also with a free-text answer).
- **End-of-task report**: done, verified with evidence, findings, decisions. Questions come only
  when a decision is really needed.
- **Language**: answers come in the language you write in (English when unclear); agent
  instructions stay in English; code, commits and repository docs keep the project's language.
- **Checks**: `memcheck.py` checks lengths, secrets and cited paths; `audit` checks the security
  of the agent configuration; `ci-init` runs both in CI on every pull request.
- **Everything customizable**: agents, packs, models, effort, agent type, profiles and add-ons,
  without touching the plugin. `/team:setup` gathers it all in one place, activation included.
- **Agents that talk to each other (team talk)**: the agents of a task share a channel
  (`tw.py talk`, also across worktrees). They ask questions, challenge each other's claims with
  evidence, verify fixes and give a verdict; the work is not done while a challenge is open.
  Three modes: debugging together, cross review, debate on a decision (`TALK.md`). Each role
  reads only the messages that are new for it (`read --for <role>`), asks and waits for the
  answer in one command (`post ... --wait 90`), and cannot write until it has read what
  arrived: no crossed fixes or lost messages. `talk open` shows open challenges and unread
  messages. In a trial with one reported bug, the tester found two more and had them fixed and
  verified in about a minute and a half. Read the conversation with `/team:talk read <topic>`.
- **Library**: skills, commands and rule sets that the orchestrator searches for every task and
  hands to the agents, and that you can install as native skills by pack or one at a time
  (`/team:library`).

## Teams and agents

A team is a menu, not a squad launched all at once: the orchestrator proposes the roles the task
needs, you choose who builds and who checks (several at a time, from different teams), and only
those start.

| Team | Who builds | Who checks |
|---|---|---|
| product | product-manager, ui-ux-designer, planner | market-researcher, architect |
| frontend | frontend-dev, ui-ux-designer (with the frontend set skills) | accessibility-specialist, e2e-tester, performance-engineer, code-reviewer, typescript-reviewer, react-reviewer, vue-reviewer, flutter-reviewer |
| backend | backend-dev, database-engineer | tester, security-reviewer, performance-engineer, code-reviewer, `<lang>`-reviewer, database-reviewer, django-reviewer, fastapi-reviewer |
| fullstack | backend-dev, frontend-dev, database-engineer | tester, e2e-tester, code-reviewer, security-reviewer, `<lang>`-reviewer |
| data | data-analyst, database-engineer | tester, ml-reviewer, rag-reviewer |
| marketing | market-researcher, marketing-strategist, seo-specialist | product-manager, ui-ux-designer |
| quality | none | tester, e2e-tester, code-reviewer, security-reviewer, accessibility-specialist, performance-engineer, silent-failure-hunter, type-design-reviewer, test-coverage-reviewer, database-reviewer, comment-analyzer, commit-reviewer |
| release | release-manager, devops-engineer | tester, technical-writer, open-source-sanitizer |
| maintenance | refactor-specialist, code-simplifier, build-fixer, `<lang>`-build-fixer | tester, code-reviewer, performance-engineer |
| docs | technical-writer, doc-keeper | none |
| architecture | architect, code-architect, code-explorer, spec-miner, planner, docs-lookup | database-engineer, security-reviewer, performance-engineer, devops-engineer |
| agent setup | harness-optimizer, loop-operator | security-reviewer, agent-evaluator, conversation-analyzer |
| build loop | gan-planner, gan-generator | gan-evaluator |
| network | network-architect, homelab-architect | network-config-reviewer, network-troubleshooter, security-reviewer |
| domain | the builders of the task | healthcare-reviewer, bengali-reviewer |
| operations | chief-of-staff | none |
| project | project-manager, project-scheduler, project-controller, agile-coach | risk-manager, stakeholder-manager, product-manager |

**Packs.** The 20 **core** roles are always on; the others come from packs you switch on when
needed:

| Pack | Roles |
|---|---|
| one pack per language: `go`, `rust`, `python`, `typescript`, `java`, `kotlin`, `cpp`, `csharp`, `swift`, `dart`, `php`, `ruby`, `fsharp` | `<lang>-reviewer` (idiom, safety, frameworks such as Django, FastAPI, React, Vue, Next.js, Spring, Laravel, Rails) and `<lang>-build-fixer` (red build, type check, dependencies) |
| `frameworks` | react-reviewer, react-build-fixer, vue-reviewer, django-reviewer, django-build-fixer, fastapi-reviewer, flutter-reviewer, harmonyos-specialist |
| `quality` | silent-failure-hunter, type-design-reviewer, test-coverage-reviewer, build-fixer, code-simplifier, comment-analyzer, commit-reviewer, database-reviewer |
| `planning` | planner, code-explorer, code-architect, spec-miner, docs-lookup |
| `pm` | project-manager, project-scheduler, project-controller, risk-manager, stakeholder-manager, agile-coach |
| `ml` | ml-reviewer, rag-reviewer, pytorch-build-fixer |
| `opensource` | open-source-sanitizer, open-source-forker, open-source-packager |
| `harness` | harness-optimizer, agent-evaluator, conversation-analyzer, loop-operator |
| `gan` | gan-planner, gan-generator, gan-evaluator |
| `network` | network-architect, network-config-reviewer, network-troubleshooter, homelab-architect |
| `domains` | healthcare-reviewer, bengali-reviewer |
| `ops` | chief-of-staff |
| `alt` | 39 alternative versions of existing roles: `alt-tdd-guide` next to `tester`, `alt-architect`, `alt-code-reviewer`... |
| `growth` | seo-specialist |

The roles with `source: "imported ..."` and the library come from an open-source collection under
the MIT license (`skills/team/library/NOTICE.md`); `tools/import_upstream.py` rebuilds them. The
`pm` roles and the `project-management` library pack are original to this repository.

`/team:agents enable auto` switches on the packs of the repository's languages (at start-up the
orchestrator offers it when it finds them). Each language is a single file
(`roles/languages/<lang>.md`) that produces the reviewer and the build fixer: adding one means
writing a checklist. All reviewers share a common discipline (only findings with evidence, zero
findings is a valid answer, known false positives to drop, extra checks on AI-written code) and
every agent treats what it reads as data, never as instructions.

**Tailored agents.** For each role and each app choose type, model and effort among those the app
really offers; the plugin rewrites the native agents:

```text
/team:agents                                   # roles, packs, type/model/effort per app
/team:agents set tester model=opus effort=max --app claude
/team:agents set architect model=pro --app agy
/team:agents set code-explorer type=Explore    # the app's built-in type, briefed with the role
/team:agents disable data-analyst              # or a whole pack: disable quality
/team:agents new api-designer                  # a role of your own (or your version of one)
```

Types: `custom` (the generated agent, default), `worker` (headless process with the exact model
and effort), or a built-in type: `general-purpose`, `Explore`, `Plan` in Claude Code, `self`,
`research` in agy. Your roles live in `~/.team-workflow/agents/` (or `.team-workflow/agents/` in
the repository) and are written as native agents in every app. Whoever writes the code never
approves it alone.

## Commands

| Command | What it does |
|---|---|
| `/team <task>` | the universal command: scan, team, live verification, report (`skills/team/SKILL.md`) |
| `/team:setup [area]` | configure everything: activation (automatic, only in this project, only when called), wizard, teams, models, roles and packs, library, team talk, checks, add-ons, presets |
| `/team:setup-memory` | creates `docs/memory` and fills it by reading the code |
| `/team:call-team [team] <task>` | describe the task and pick the roles (more than one is fine); the team (frontend, backend, data...) is optional |
| `/team:new-feature <what>` | a new feature with the team |
| `/team:fix-bug <bug>` | failing test, fix of the cause, verification |
| `/team:review-changes [range]` | tests, code and security review, one verdict |
| `/team:release [version]` | a release, only after your approval |
| `/team:end-session` | closes the session: memory, lessons learned, where to resume |
| `/team:usage-costs [days\|latest]` | tokens and costs per agent, model and session |
| `/team:write-docs [architecture\|onboarding\|changelog\|readme]` | documentation for people built from the memory, checked against the code |
| `/team:learn-history` | the repository's habits from git history (hot spots, fragile files, couplings, conventions), turned into memory with your ok |

Zero-token (in Claude Code a hook runs them and the model never sees them; in agy run them in
bash mode, `!team-workflow <command>`):

| Command | What it does |
|---|---|
| `/team:settings [set <key> <value>]` | shows or changes the settings |
| `/team:agents [...]` | roles, packs, type, model and effort per role and per app, your roles |
| `/team:profile [name]` | presets: `budget`, `fast`, `balanced`, `thorough`, `security`, `research` |
| `/team:models` | models and effort each app offers |
| `/team:options` | what the start-of-conversation wizard can offer in this app, right now |
| `/team:addons [add\|remove\|update <name>]` | add-on plugins in every app |
| `/team:audit [--strict]` | security of the agent configuration |
| `/team:doctor [--fix]` | installation health and repair |
| `/team:ci-init` | GitHub Actions workflow: memory and audit on every pull request |
| `/team:update-plugin [check]` | updates team-workflow (and the chosen add-ons) in every app |
| `/team:library [search <words>\|show <id>\|enable\|disable <id\|pack>]` | the library: packs, search, install as native skills |
| `/team:talk [read\|open\|clear <topic>]` | what the agents said to each other, questions and challenges still open |

In agy create the `team-workflow` command once:
`python3 ~/.gemini/config/plugins/team-workflow/skills/team/scripts/tw.py install-cli`.
From a terminal there are also `team-workflow learn` and `team-workflow uninstall [--all]`.

## Add-ons

`/team:addons` lists the catalog with the versions installed in each app; `add` installs, `update`
updates, `remove` removes, and `update-plugin` also updates the chosen add-ons. Bundles, installed
with one command in every app:

| Bundle | Contains |
|---|---|
| `frontend` | impeccable, taste, frontend-design, solar-icons, cloudflare: `frontend-dev`, `ui-ux-designer` and `accessibility-specialist` use them when present; `security-reviewer`, `backend-dev` and `devops-engineer` use the Cloudflare skills in Cloudflare projects (`cloudflare-one` for Zero Trust, `turnstile-spin`, `workers-best-practices`) |
| `token-saving` | caveman (compressed answers), ponytail (less code), context-mode (huge outputs kept out of context), serena (navigation by symbols instead of whole files) |
| `mcp` | context7 (up-to-date library docs), playwright (browser), serena, sequential-thinking |
| `popular` | superpowers, Anthropic's skills (documents and examples), karpathy, ui-ux-pro-max, context7 |

An MCP server goes at user level: `claude mcp add --scope user` in Claude Code,
`~/.gemini/config/mcp_config.json` in agy, the `mcp` table of `~/.config/opencode/opencode.json`
in OpenCode. A server with the same name that you configured yourself is left alone.

| Add-on | What it adds | Claude Code | agy and OpenCode |
|---|---|---|---|
| `caveman` | compressed answers, fewer output tokens (MIT and BSL licenses) | marketplace | its skills copied to `~/.gemini/config/skills` |
| `ponytail` | the simplest solution that works, less code | marketplace | `agy plugin install` |
| `impeccable` | design, critique, audit and polish of interfaces (Apache-2.0) | marketplace | its skills copied |
| `taste` | art direction against "AI slop" for sites and screens (MIT) | marketplace | its skills copied |
| `frontend-design` | Anthropic's frontend-design skill (Apache-2.0) | official marketplace | the skill copied |
| `solar-icons` | Solar icons: exact names and imports per framework (MIT, icons CC BY 4.0) | skill copied to `~/.claude/skills` | the skill copied |
| `cloudflare` | Cloudflare skills: Workers best practices, Zero Trust (`cloudflare-one`), Turnstile, web perf (Apache-2.0) | marketplace | its skills copied |
| `superpowers` | plan, test, execute, review, finish workflow (MIT) | marketplace | skills copied |
| `anthropic-docs` | Anthropic's skills for Word, PDF, PowerPoint, Excel | marketplace | skills copied |
| `anthropic-examples` | Anthropic's skills: skill-creator, mcp-builder, webapp-testing... (Apache-2.0) | marketplace | skills copied |
| `karpathy` | coding guidelines: simple, targeted, verified changes | marketplace | skills copied |
| `ui-ux-pro-max` | UI/UX design rules, palettes, fonts, design systems (MIT) | marketplace | skills copied |
| `context-mode` | keeps huge tool outputs out of the context | marketplace | MCP server |
| `context7` | up-to-date, versioned library documentation (MIT) | marketplace | MCP server |
| `playwright` | a real browser the agents drive (Apache-2.0) | MCP server | MCP server |
| `serena` | code navigation and editing by symbols: fewer files read, fewer tokens (needs `uv`) | MCP server | MCP server |
| `sequential-thinking` | step-by-step reasoning on hard problems (MIT) | MCP server | MCP server |
| anything else | `addons add owner/repo` or `addons add plugin@marketplace` (for example one from Anthropic's official marketplace) | marketplace | a plugin when it has `plugin.json`, otherwise its skills |

## Assignment wizard

**At the start of a conversation** (setting `session_wizard`, on by default), at the first task
that uses agents, the wizard first shows the full list (`team-workflow options`: the models and
efforts the app offers to native agents and workers, and for every role its type, model, effort
and how it really runs; `--app all` for Claude Code, agy and OpenCode together), then asks for
the preset, the agents to use (more than one is fine) and, for **each** chosen agent, model and
effort (two agents per question, until all are asked). In agy `inherit` is the session's model
(for example `gemini-3.8-flash-high`): agy subagents accept only `inherit`, `flash` or `pro`
(Gemini 3.1 Pro, older), so a different exact model runs as a worker; the same holds in OpenCode
for a model or variant different from the agent file's, and in Claude Code for a different
effort. At the end you choose whether the choices apply to this conversation only or become the
defaults (for all projects or for this one).

Then, every time agents start (team, feature, fix, review, release) you pick the roles (several
at a time), then a summary with one block per agent shows what it works on, how, model, effort,
token and cost estimate, and the total; it starts only with your ok. With `wizard: quick`
(default) questions come only for the agents you want to change; with `full` for all of them;
with `off` none. The models offered are only those the app offers: haiku, sonnet, opus, fable in
Claude Code; `inherit`, `flash`, `pro` for agy subagents and the ids of `agy models` (e.g.
`gemini-3.8-flash-high`) for workers; in OpenCode `inherit` or a `provider/model` of any connected
provider (NanoGPT, OpenRouter, ...), with the variant as effort (only the model's own: GLM 5.3 has
`low`, `high`, `max`). The wizard shows the providers and models you use most; it finds the others
by name: `team-workflow models --app opencode --provider nano-gpt --search "glm 5.3"`.

- **Estimates**: `scripts/estimate.py`, calibrated on real runs; after two runs of a role in the
  project it uses the median of its history.
- **Native launch** (default): the agent generated for the role, with the model and effort of the
  settings (in Claude Code `subagent_type: "<role>"`, in agy `invoke_subagent`), or the built-in
  type you chose for that role.
- **Worker launch**: `scripts/run_worker.py` runs `claude -p`, `agy -p` or `opencode run` with the
  exact model and effort and records the tokens in `~/.team-workflow/ledger/`. Read-only unless
  you agree otherwise.

## Usage dashboard

`/team:usage-costs` (or `scripts/dashboard.py --root . --html`) shows cost at API list prices,
tokens, the share read from cache, usage per agent, model and session, memory health and the agent
catalog; the HTML page is self-contained, dark theme included, and in Italian when `LANG` starts
with `it`. Prices live in `skills/team/pricing.json` (with date and source, editable). With a
subscription the costs show usage, not a bill.

## agy (Antigravity)

```bash
agy plugin install https://github.com/antoStr/team-workflow   # or the local path of the repo
python3 ~/.gemini/config/plugins/team-workflow/skills/team/scripts/tw.py install-cli
# from here on, in a new terminal:
agy plugin update team-workflow     # or `agy plugin update` for every plugin, or `agy plugin update ponytail`
python3 skills/team/scripts/install_agy.py --workspace /path/to/repo   # one project only
```

agy has no `plugin update`: `install-cli` creates the `team` and `team-workflow` commands in
`~/.local/bin`. On Windows it generates native `agy.cmd`, `agy.bat`, `team.cmd` and `team.bat`
wrappers and adds `~/.local/bin` to the user's PATH in the registry (`HKCU\Environment\Path`), so
`agy plugin update [name...]` runs from any terminal (PowerShell, CMD, Bash). On Linux/macOS it
adds a transparent shell function to `~/.zshrc` and `~/.bashrc`. The update works for any plugin:
it reinstalls it from the origin agy cloned it from, first checks that the origin answers, cleans
up orphaned or legacy skills, and if the reinstall fails it puts the previous version back.

The repository is also an agy plugin (`plugin.json`, `hooks.json` and `rules/` at the root, which
Claude Code ignores). agy installs it in `~/.gemini/config/plugins/team-workflow/` with the skills
in `skills/` (`team` for the universal interface, engine and roles, plus one skill per workflow
command), the rules that carry the memory, and the hooks in agy's format.

agy does not use a plugin's agents as subagents: it takes them from `~/.gemini/config/agents/`, in
its own format (and silently drops a file with `model: sonnet` or with an unquoted description
that contains `: `). That is why the plugin writes the active roles there, converted, at every
session and with `!team-workflow agents sync`: the orchestrator launches them with
`invoke_subagent`, in parallel too. After the first installation restart agy once. Tokens are
measured only for workers (`run_worker.py --harness agy`).

You do not have to use them: just ask normally, the skill activates on development work.

## OpenCode

```bash
python3 ~/Workspace/team-workflow/skills/team/scripts/install_opencode.py   # from the repository copy
team-workflow install-opencode                                               # or with the team-workflow command
```

It works with the CLI and the desktop app (OpenCode 2.x; on Windows the app's CLI is
`%LOCALAPPDATA%\Programs\@opencodedesktop\resources\opencode-cli.exe` and is found automatically).
It writes to `~/.config/opencode/`: the `team-workflow` skill (with scripts, roles and wizard), the
`/team-workflow/<name>` commands (in a folder: on Windows colons are not allowed in file names) and
the agents of the active roles.

- **OpenCode 2.x**: plugins can no longer touch the system prompt or intercept commands, so the
  installer adds a block to `~/.config/opencode/AGENTS.md`: at the first request of every
  conversation the model runs `session_start.py --text` (memory, settings, session wizard).
  `settings`, `agents`, `profile`, `models`, `addons`, `audit`, `doctor`, `ci-init`, `options` and
  `update-plugin` run `tw.py` inside the command and the model only shows the output (few
  tokens). There is no end-of-turn hook: the `STATE.md` reminder is in the instructions.
- **OpenCode 1.x**: instead of the block there is the `team-workflow.js` plugin (memory in the
  system prompt, zero-token commands, `STATE.md` reminder at the end of the turn).

The orchestrator launches the roles with the `subagent` tool (`task` in 1.x) and asks questions
with the `question` tool. Commands and instructions use the Python that really works on the
machine: on Windows `python3` is often the Microsoft Store placeholder, which always fails.
`/team-workflow/update-plugin` (or `team-workflow update`) also updates OpenCode;
`install_opencode.py --uninstall` removes only the files team-workflow wrote (the block in
`AGENTS.md` included); `team-workflow doctor` flags old installations to redo. OpenCode also reads
the skills in `~/.claude/skills` and `~/.agents/skills`.

## Codex

```bash
python3 ~/Workspace/team-workflow/skills/team/scripts/tw.py install-codex   # from the repository copy
team-workflow install-codex                                               # or with the team-workflow command
team-workflow install-codex --workspace /path/to/repo                     # one project only
team-workflow install-codex --uninstall                                   # removes only team-workflow's files
```

It works with the Codex CLI and app, and also when Codex goes through **opencodex** (a proxy that
does not change where Codex reads skills and agents). It writes to `~/.codex/` (or `CODEX_HOME`):

- `skills/team/`: the main skill, with scripts, roles, library and wizard;
- `skills/team-workflow-<name>/`: one skill per workflow (`$team-workflow-start`,
  `$team-workflow-setup`, `$team-workflow-agents`...). The configuration ones run `tw.py` and the
  model only shows the output;
- `agents/<role>.toml`: the active roles as Codex agents (model, effort, read-only sandbox for the
  checkers), listed in a block of `config.toml` between two markers. An agent with the same name
  that you defined yourself is left alone;
- a block in `AGENTS.md`: at the first request of every conversation the model runs
  `session_start.py --text --app codex` (memory, settings, session wizard);
- `rules/team-workflow.rules`: a `prefix_rule` that allows only `<python> <team-workflow script>`
  in the Codex sandbox, leaving everything else under the normal rules.

Add-ons work here too: skills go to `~/.codex/skills`, MCP servers to an `[mcp_servers]` block of
`config.toml`. Questions use `request_user_input` when available (otherwise a numbered list of
options). `team-workflow update` also updates Codex.

## Installation

Requirements: Claude Code and/or agy, `git` and Python 3.10 or newer. Claude Code:

```bash
claude plugin marketplace add antoStr/team-workflow   # or the local path of the repo
claude plugin install team-workflow@team-workflow
```

To try it without installing: `claude --plugin-dir ~/Workspace/team-workflow`. For agy see
[agy (Antigravity)](#agy-antigravity).

### Updating

The installed version shows in `claude plugin list` (or `/plugin`) and in agy with
`agy plugin list`; the latest is in `.claude-plugin/plugin.json` and in the repository's `vX.Y.Z`
tags (on GitHub: Watch → Custom → Releases to get a notice).

The easiest way is `/team:update-plugin` in Claude Code, or `!team-workflow update` in agy: it
updates every app where the plugin is installed, without spending tokens; `check` only shows the
versions. At Claude Code start-up a notice tells you when a new version is out. From a terminal:
`python3 skills/team/scripts/tw.py update [check]`. By hand:

```bash
# Claude Code (or turn on the marketplace auto-update in /plugin → Marketplaces)
claude plugin marketplace update team-workflow
claude plugin update team-workflow@team-workflow
# agy, after `tw.py install-cli` (see the agy section)
agy plugin update team-workflow
```

Restart the session after updating. Since 0.6.0 the Claude Code agents are named like the role
(`tester`, no longer `team-workflow:tester`) and are written to `~/.claude/agents/` at the first
session in a git repository: Claude Code loads them from the next session (a notice reminds you;
meanwhile the orchestrator uses `general-purpose` with the role's instructions).
`/team:doctor` checks that everything is in place.

## Settings

Every behavior changes without touching the plugin: `/team:settings` (in agy
`!team-workflow settings`) shows them with their origin, `settings set <key> <value>` changes them
for all projects (`~/.team-workflow/settings.json`), with `--project` only for the repository
(`.team-workflow.json`); `settings reset <key>` goes back to the default.

| Key | Default | What it decides |
|---|---|---|
| `activation` | `auto` | `auto`: every session in a repository loads memory, protocol and Stop check; `manual`: team-workflow stays quiet until you call it. Only in some projects: `manual` for the user and `auto --project` in those projects |
| `talk` | `true` | the agents of a task talk to each other on the shared channel (`TALK.md`) |
| `talk_rounds` | `3` | the maximum rounds of replies before bringing the disagreement to you |
| `library.packs.<pack>` | off | library packs installed as native skills |
| `library.skills.<id>` | - | a single library entry, on or off (wins over the pack) |
| `session_wizard` | `true` | at the start of a conversation asks where to save choices, preset, agents, model and effort among those the app offers, skills, add-ons and team talk |
| `wizard` | `quick` | `quick`: summary with the recommended choices, questions only for whom you want to change; `full`: every question; `off`: none |
| `max_agents` | `4` | how many agents it proposes at most without asking |
| `launch` | `native` | `native` (the app's subagents) or `worker` (headless processes with exact model and effort) |
| `worker_edits` | `false` | whether workers may edit files without asking every time |
| `auto_security_review` | `true` | adds `security-reviewer` when the change touches sensitive code |
| `end_report` | `full` | `short`: only done, verified, decisions |
| `update_check` | `true` | new-version notice at start-up |
| `stop_check` | `true` | reminder to update `STATE.md` |
| `models.claude.<role>` | sonnet (architect and security-reviewer opus, doc-keeper haiku) | model in Claude Code |
| `models.agy.<role>` | inherit (the session's model) | model of agy subagents: inherit, flash or pro |
| `models.opencode.<role>` | inherit | model of OpenCode subagents: inherit or `provider/model` |
| `effort.<role>` | medium (architect and security-reviewer high) | effort of Claude Code agents and workers |
| `type.<app>.<role>` | `custom` | agent type (see [Teams and agents](#teams-and-agents)) |
| `packs.<pack>` | `core` only | role packs switched on |
| `enabled.<role>` | `true` | switches off a single role |
| `addons.<name>` | none | chosen add-ons (managed by `addons`) |

Changing a model, an effort, a type or a pack rewrites the native agents at once. Examples:
`/team:settings set models.agy.tester flash`, `/team:profile budget`.

## First use in a project

1. Open Claude Code in the repository and run `/team:setup-memory` (in agy: ask for the
   `setup-memory` skill).
2. The command creates `docs/memory`, detects the build and test commands (Go, Node, Rust,
   Python, Maven, Gradle) and adds a pointer in `AGENTS.md` (and in `GEMINI.md` or `CLAUDE.md`
   when they exist), so Gemini, Codex and Cursor read the same memory too.
3. Check what it wrote: every file, function and command it cites must exist.

The agents' instructions are in English; answers come in the language you write in (English when
it is unclear). An existing memory keeps its language.

## Hooks

| Hook | What it does | How to turn it off |
|---|---|---|
| SessionStart (agy: PreInvocation) | injects `INDEX.md`, `STATE.md` and the changed settings; writes the native agents from the settings; offers the packs of the repository's languages; tells you about a new version (at most once a day) | `update_check false` for the notice |
| UserPromptSubmit (Claude Code only) | answers the zero-token commands (`settings`, `agents`, `profile`, `models`, `addons`, `audit`, `doctor`, `ci-init`, `update-plugin`) without the model | by disabling the plugin |
| Stop | when files changed after `STATE.md`, asks to update it (never twice in a row) | `stop_check false` (or `TEAM_WORKFLOW_STOP_CHECK=0`) |

## Checks in CI

`/team:ci-init` writes `.github/workflows/team-workflow.yml` and copies the three check scripts
to `.github/team-workflow/` (so the CI does not have to download the plugin): on every pull
request and push it runs memcheck (when there is `docs/memory`) and the audit of the agent
configuration. By hand:

```bash
python3 <plugin folder>/skills/team/scripts/memcheck.py --root . --strict
python3 <plugin folder>/skills/team/scripts/tw.py audit --strict
```

memcheck: errors for files over the line limit and for secrets; warnings (errors with
`--strict`) for cited paths that do not exist in the repository.

## License

MIT (`LICENSE`). Content imported into the library and the `source: "imported ..."` roles keeps
its license: `skills/team/library/NOTICE.md`.

## Development

```bash
python3 -m unittest discover -s tests
python3 tools/import_upstream.py <checkout>     # rebuilds the imported roles and the library
python3 tools/readme_catalog.py                  # rebuilds docs/CATALOG.md and CATALOG.it.md (the tests check them)
for p in .claude-plugin/plugin.json skills; do claude plugin validate "$p" --strict; done
agy plugin validate .
claude plugin eval . --runs 1 --allow-tools "Bash(python3:*)"   # behavior evals (they cost)
```
