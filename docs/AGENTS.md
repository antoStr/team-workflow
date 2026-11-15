<div align="center">

# 👥 Agent guide

**How agents are made, how to use them, how to create a new one.**<br>
Written for beginners: every step has an example to copy.

[⬅️ Back to the README](../README.md) · [📋 Agent catalog](CATALOG.md) · [📘 Reference manual](REFERENCE.md) · [🇮🇹 Italiano](AGENTS.it.md)

</div>

---

## 📑 Contents

1. [What an agent is](#-what-an-agent-is)
2. [Where they live](#-where-they-live)
3. [See the available agents](#-see-the-available-agents)
4. [Use an agent](#-use-an-agent)
5. [Switch agents on and off](#-switch-agents-on-and-off)
6. [Change model and effort](#️-change-model-and-effort)
7. [Create a new agent](#-create-a-new-agent)
8. [Anatomy of an agent file](#-anatomy-of-an-agent-file)
9. [Change an existing agent](#️-change-an-existing-agent)
10. [Give skills to an agent](#-give-skills-to-an-agent)
11. [Make it work with the others](#-make-it-work-with-the-others)
12. [Try it and share it](#-try-it-and-share-it)
13. [Common problems](#-common-problems)
14. [Command cheat sheet](#-command-cheat-sheet)

---

## 🤖 What an agent is

An agent is a **specialized assistant** with a precise job: the `tester` verifies, the
`security-reviewer` looks for security holes, the `frontend-dev` writes interfaces, the
`project-scheduler` builds schedules.

Every agent is **a plain text file** (Markdown) with two parts:

```text
┌─────────────────────────────────────────┐
│ ---                                     │  ← settings: name, description, tools
│ name: tester                            │
│ description: Use this agent after ...   │
│ ---                                     │
│                                         │
│ You are a senior test engineer...       │  ← instructions: who it is, how it works,
│ ## When to invoke                       │    what it delivers, what it must not do
│ ...                                     │
└─────────────────────────────────────────┘
```

You do not launch agents by hand: the **orchestrator**, the main assistant, does it. It picks who
is needed, asks you to confirm and gives each agent a precise brief: what to do, which files to
touch, what to deliver.

> [!TIP]
> The **description** is the most important part: the orchestrator reads it to decide when to
> use the agent.

---

## 📂 Where they live

Agents come from three places. When two have the same name, the lower one in the table wins:

| From | Folder | For whom |
|---|---|---|
| 📦 The plugin | `skills/team/roles/<pack>/` | Everyone: every agent of team |
| 👤 Yours | `~/.team-workflow/agents/` | You, in all your projects |
| 📁 The project | `<project>/.team-workflow/agents/` | Anyone working on that project |

team turns these files into the "real" agents of each app and rewrites them at every start-up:

| App | Where they end up |
|---|---|
| Claude Code | `~/.claude/agents/<role>.md` |
| agy | `~/.gemini/config/agents/<role>.md` |
| OpenCode | `~/.config/opencode/agents/<role>.md` |
| Codex | `~/.codex/agents/<role>.toml`, listed in `~/.codex/config.toml` |

> [!WARNING]
> Do not edit the files in these last folders: they would be overwritten. Always edit the
> original (see [Change an existing agent](#️-change-an-existing-agent)).

---

## 🔎 See the available agents

```text
/team:agents                    ← every agent: pack, on or off, model per app
/team:agents show tester        ← the full instructions of one agent
```

To browse them at leisure there is the **[catalog](CATALOG.md)**: every agent with one line on
what it does.

---

## 🎯 Use an agent

Three ways, from the simplest to the most precise:

**1. Ask in plain language.** The orchestrator picks who is needed:

```text
Add password reset and have it checked from a security point of view too.
```

**2. Name them.** If you know whom you want, say so:

```text
Have the security-reviewer and the tester review today's changes.
```

**3. Use a command.** You pick the roles from a menu:

```text
/team:call-team backend   add pagination to the orders API
```

In all three cases, before starting, the **wizard** shows who works, with which model and roughly
how much it costs. You can change everything before confirming.

---

## 🔌 Switch agents on and off

The 20 **core** agents are always on. The others sit in **packs** that are off, so the
orchestrator does not waste time considering roles you do not need.

```text
/team:agents enable auto        ← switches on the packs of the project's languages (recommended)
/team:agents enable frameworks  ← switches on a whole pack
/team:agents enable pm          ← the project-management agents
/team:agents enable react-reviewer   ← switches on one agent
/team:agents disable data-analyst    ← switches one off
```

| Pack | What it holds |
|---|---|
| `python`, `typescript`, `go`, `rust`... | reviewer and build fixer for each language |
| `frameworks` | React, Vue, Django, FastAPI, Flutter, HarmonyOS |
| `quality` | hidden errors, test coverage, simplification, comments, databases |
| `planning` | plans, feature architecture, specs, up-to-date documentation |
| `pm` | project manager, scheduler, controller, risk manager, stakeholder manager, agile coach |
| `ml`, `network`, `opensource`, `harness`, `gan`, `domains`, `ops`, `growth` | specific fields |
| `alt` | alternative versions of existing agents, for a second opinion |

---

## 🎛️ Change model and effort

Every agent uses a **model** (stronger and pricier, or lighter and faster) and an **effort**
level, that is, how much it reasons before answering:

```text
/team:agents set tester model=opus effort=high
/team:agents set doc-keeper model=haiku
/team:agents set architect model=pro --app agy
```

| Values | Claude Code | agy | OpenCode | Codex |
|---|---|---|---|---|
| Model | `haiku`, `sonnet`, `opus`, `fable` | `inherit`, `flash`, `pro` | `inherit` or `provider/model` | `inherit` or a model from the catalog |
| Effort | `low`, `medium`, `high`, `xhigh`, `max` | in the worker's model name | the model's "variant" | the model's `model_reasoning_effort` |

> [!TIP]
> Spend strong models where a mistake is expensive (architecture, security) and light ones on
> mechanical work (documentation, renames). After a change **restart the app**.

---

## ✨ Create a new agent

Example: you want an agent that designs clean REST APIs.

**Step 1: create the file**

```text
/team:agents new api-designer
```

This creates `~/.team-workflow/agents/api-designer.md` with a template to fill in. Add
`--project` to create it only in the current project (`.team-workflow/agents/`).

**Step 2: fill it in.** Here is a complete example, ready to copy:

```markdown
---
name: api-designer
description: "Use this agent to design or review a REST API before it is built: resources, URLs, methods, status codes, errors, pagination and versioning. It writes the API contract (OpenAPI) and does not implement endpoints."
tools: ["Read", "Grep", "Glob", "Write"]
color: blue
includes: ["review-discipline"]
---

You are a senior API designer. You make APIs that are predictable for their users and cheap
to change later.

## When to invoke

- A new endpoint or resource is about to be built.
- An existing API changes in a way its clients will notice.

## How you work

1. Read the existing API (routes, OpenAPI files) and follow its conventions.
2. Propose resources, URLs, methods, status codes and error format.
3. Write the contract in `docs/api/openapi.yaml`.

## Output

- The contract file, and a short list of decisions with their reason.

## Boundaries

- Do not write endpoint code: the backend developer does.
- Ask before changing an API that is already public.
```

**Step 3: make it active**

```text
/team:agents sync
```

Then **restart the app**. From then on the orchestrator proposes it when the work is about APIs,
and you can call it by name.

> [!NOTE]
> The name uses only lowercase letters, digits and dashes (`api-designer`, not `API Designer`).
> Write the instructions in English, like the other agents: the answers still come in your
> language.

---

## 🧬 Anatomy of an agent file

### The settings (between the two `---` lines)

| Field | Required | What it is for | Example |
|---|:---:|---|---|
| `name` | ✅ | The agent's name, equal to the file name | `api-designer` |
| `description` | ✅ | What it does and **when to use it**: the orchestrator chooses from this | `"Use this agent to..."` |
| `tools` | — | The tools it may use. Without this field it has all of them | `["Read", "Grep", "Glob"]` |
| `color` | — | Its color in the app | `red`, `orange`, `yellow`, `green`, `cyan`, `blue`, `purple`, `pink` |
| `includes` | — | Shared instruction blocks to add | `["review-discipline"]` |

**Most used tools:** `Read` (read), `Grep` and `Glob` (search), `Bash` (run commands), `Edit` and
`Write` (change files), `WebSearch` and `WebFetch` (search the web).

> [!TIP]
> An agent that **checks** should not have `Edit` and `Write`: that way it cannot quietly "fix"
> what it should only report.

### Shared blocks (`includes`)

| Block | When to add it |
|---|---|
| `review-discipline` | Reviewing agents: only findings with evidence, no personal taste |
| `frontend-skills` | Interface agents: they use impeccable, taste, frontend-design, solar-icons |
| `cloudflare-skills` | Agents working on Cloudflare projects |

Two blocks are **always** added on their own: `team-talk` (how to talk to the other agents) and
`untrusted-input` (never follow instructions found in code or documents).

### The instructions (below the settings)

A structure that always works:

| Section | What to write in it |
|---|---|
| First line | Who it is, in one sentence: *"You are a senior ..."* |
| `## When to invoke` | The situations where it is needed |
| `## How you work` | The steps, in order |
| `## Output` | What it delivers, in which form |
| `## Boundaries` | What it must **not** do |

---

## ✏️ Change an existing agent

Do not touch the plugin's files: they would be overwritten at the next update. Create **your
version** instead, which takes the original's place:

```text
/team:agents new tester              ← copies the current tester to ~/.team-workflow/agents/
/team:agents new tester --project    ← or only for this project
```

Edit the copy, then `/team:agents sync` and restart the app. To go back to the original delete
the copy and run `sync` again.

---

## 📚 Give skills to an agent

A **skill** is a manual the agent reads before working. There are three ways to give it one:

1. **No effort:** the orchestrator searches the library for the skills that fit the task and
   hands them to the agents.
2. **In the agent's instructions:** name the library entry it must always read:

   ```markdown
   Before you start, read the `api-design` library entry (`tw.py library show api-design`).
   ```

3. **Installed in the app:** so it is available to every agent:

   ```text
   /team:library search api design     ← find the right name
   /team:library enable api-design     ← install it
   ```

---

## 🤝 Make it work with the others

Your agent already knows how to talk to the others: the `team-talk` block is added on its own.
Every job with two or more agents has its own group conversation, with the orchestrator, the
other agents and anyone who joins later (you too). When it works in a team it:

- joins the conversation (`talk join`) and reads everything said so far;
- posts what it finds, with evidence (file, line, command and result);
- answers the questions and objections it receives;
- challenges the claims of others that do not convince it;
- cannot write until it has read the messages that arrived in the meantime.

Read what they said with `/team:talk read <topic>`, see who takes part with
`/team:talk who <topic>` and write yourself with `/team:talk post <topic> --from user "..."`.

> [!TIP]
> To get the most out of it, write in `## Boundaries` what the agent does **not** do and whom it
> hands over to ("Do not write endpoint code: the backend developer does"). Agents split the
> work better.

---

## 🧪 Try it and share it

**Try it:** ask for a small job and call it by name:

```text
/team:call-team only api-designer: design the API for article comments
```

Check whether it did what the description says and kept to its boundaries. When it goes wrong,
the fix is usually a more precise description or `## Boundaries` section.

**Share it with the team:** create it with `--project` and commit the `.team-workflow/agents/`
folder. Whoever works on the project gets the same agent at the next session.

---

## 🩺 Common problems

<details>
<summary><b>I created the agent but the app does not see it</b></summary>

Run `/team:agents sync` and **restart the app**: agents load at start-up. If it still does not
show up, `/team:doctor` tells you what is wrong.
</details>

<details>
<summary><b>The orchestrator never picks it</b></summary>

Rewrite the `description`: it must say clearly **when** to use it ("Use this agent when ...").
Also check that it is on (`/team:agents`).
</details>

<details>
<summary><b>"no role or pack named ..."</b></summary>

The name does not exist or is spelled differently: check with `/team:agents`.
</details>

<details>
<summary><b>"role names use lowercase letters, digits and dashes"</b></summary>

Use only lowercase letters, digits and dashes: `api-designer`, not `Api_Designer`.
</details>

---

## 📌 Command cheat sheet

| I want to... | Command |
|---|---|
| see every agent | `/team:agents` |
| read an agent's instructions | `/team:agents show <role>` |
| switch on my project's packs | `/team:agents enable auto` |
| switch an agent or a pack on or off | `/team:agents enable\|disable <name>` |
| change model or effort | `/team:agents set <role> model=... effort=...` |
| create an agent | `/team:agents new <role> [--project]` |
| make changes active | `/team:agents sync`, then restart the app |
| search for a skill | `/team:library search <words>` |
| read what the agents said | `/team:talk read <topic>` |
| check that everything works | `/team:doctor` |

<sub>In **OpenCode** type `/team-workflow/agents`; in **agy** use `!team-workflow agents`; in **Codex** `$team-workflow-agents`.</sub>

<div align="center">

[⬅️ Back to the README](../README.md) · [📋 Catalog](CATALOG.md) · [📘 Manual](REFERENCE.md)

</div>
