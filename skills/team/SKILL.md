---
name: team
description: The quick, universal team command. It handles any task (bug, feature, refactor, audit, project plan) by running teams of agents on its own, navigating large codebases through the project brain and verifying for real (the app or game is started and tested before the problem is called solved).
argument-hint: "<what you want to do or which problem to solve>"
---

# /team — Autonomous Engineering & Live-Verified Team Execution

This is the main, simplified command of **team**. There are no long commands or settings to
remember: write `/team <task>` and the orchestrator runs the whole cycle.

`tw.py` below is `<team skill folder>/scripts/tw.py`, run with `python3` from the repository root.

## How the orchestrator runs `/team`

When you receive `/team $ARGUMENTS`:

- **If the argument is a zero-token system action**, run it and stop:
  - `upgrade` or `update`: `tw.py update`. Show the result.
  - `doctor`: `tw.py doctor`; `tw.py doctor --fix` when the user asks for a fix.
  - `audit`: `tw.py audit`.
  - `settings`: `tw.py settings`.
  - `status`, `hardware` or `thermal`: `tw.py hardware`.
  - `scan`: `tw.py scan`.
  - `cortex`: `tw.py cortex status` (or `tw.py cortex route <task>` / `tw.py cortex boost <vibe prompt>`).
  - `verify-docs`: `tw.py verify-docs`.
  - `catalog`: `tw.py agents catalog`.
  - Do not spawn agents or spend inference on these actions.

- **The v1 commands live inside `/team`**: `fix-bug`, `new-feature`, `call-team`,
  `review-changes`, `setup-memory`, `start`, `release`, `ci-init` and `end-session` start their
  flow from here, for example `/team fix-bug <problem>`, `/team new-feature <idea>` or
  `/team call-team <roles>`.

### 0. Language

- Reply in the language of the user's latest message. When it is mixed or unclear, use the
  language of the conversation so far; with no signal at all, use English.
- Brief agents in English; they report back in English and you translate for the user.
- Files you write follow the project, not the chat: code, comments, commits and docs keep the
  language the repository already uses (English when it has none). A document the user asks
  for in their language (a plan, a report, a charter) is written in that language.

### 1. Never ignore a question in between

> [!IMPORTANT]
> **Never skip the user's questions.** When the request mixes doubts, remarks or questions with
> the task ("writing in between"), the orchestrator and every agent first find each question
> and answer it in full at the start of the reply, before or while the work starts.

### 2. First scan and session setup (mandatory, before any agent)

> [!IMPORTANT]
> These steps are the same in every app (Claude Code, agy, OpenCode, Codex) and run in this
> order. Never launch an agent before step 4 is done.

1. At the start of every `/team` call on a codebase, scan the stack and the environment:
   `tw.py scan`. It finds languages, frameworks, UI libraries, git state and project memory.
2. For a large or unknown codebase, ask the project brain: `tw.py brain context <module_or_area>`.
   In under 2,000 tokens you get who calls the module, what it depends on and the
   **vaccines** (past mistakes) recorded for that area. Skip it only when the brain is empty.
3. Search the library for skills that fit the task: `tw.py library search <keywords>`.
   Also run the **Neural Cortex Router** to perceive available resources (hardware capacity,
   models, enabled & dormant roles, library + learned skills, Brain blast radius, and project
   genome) against required task resources:
   `tw.py cortex route "<task>" --app <claude|agy|opencode|codex>`.
   Use its activated neurons, model/effort allocations, bound skills, topology, and default
   **Vibecode Agent Booster** (AST skeleton map + caveman/ponytail/karpathy/context-mode diet
   cutting ~55-65% token cost) as the neural prior for every agent brief (`tw.py cortex boost`).
4. **Session setup** (`WIZARD.md`, "Session setup"), once per conversation while
   `session_wizard` is on: show the output of `tw.py options --app <claude|agy|opencode|codex>`
   in a code block, whole (when a tool such as context-mode cuts it, save it to a file and read
   it in parts of 40 lines), then ask with the app's question tool (Claude Code `AskUserQuestion`, agy
   `ask_question`, OpenCode `question`) every call of `tw.py questions --app <app> --task <words>`
   as printed: where the choices go and the preset; **every** enabled role; the library skills;
   add-ons; team talk. Then every call of `tw.py questions --app <app> --roles <chosen>`: model
   and effort for **every** chosen role. Then the recap and "Start".
   - Roles, models or a number of agents named in the request ("2 sonnet agents", "tester and
     pentester") do not skip the setup: they become the first, "(Recommended)" option of the
     matching questions.
   - Skip it only when the user says "skip setup" or answers just "defaults", when the request is a plain
     question that launches no agent, or when it already ran in this conversation.
5. Only then brief and launch the agents.

### 3. Flexible team size and free choice of agents

- **No forced choice**: do not limit the user to four fixed options or preset sizes.
- **Full catalog**: the user can browse every agent with `tw.py agents catalog`.
- **Exactness**: follow the number and the roles the user asks for to the letter (for example
  "I want 3 agents: frontend-dev, tester, pentester"). They pre-fill the session setup
  answers (section 2, step 4); they never replace it.
- **Changes at any time**: the user can add, remove, replace or scale roles while the work runs.
- **Frontend components (`frontend-components` pack)**, for frontend, design system or UI tasks:
  - `pick-ui-library` to choose a library instead of reinventing components;
  - `shadcn-ui`, `base-ui`, `radix-ui` for accessible primitives (WCAG 2.2 AA);
  - `sonner-toast`, `vaul-drawer`, `cmdk-palette`, `number-flow` for feedback, gestures and palettes;
  - `magic-ui`, `aceternity-ui`, `21st.dev`, `beautiful-ui`, `rare-ui` for visual effects and blocks;
  - the `design-engineer` role, next to `frontend-dev` and `ui-ux-designer`.
- **Project management (`pm` agent pack, `project-management` library pack)**, for plans,
  schedules, budgets, risks, stakeholders and agile delivery: `project-manager`,
  `project-scheduler`, `project-controller`, `risk-manager`, `stakeholder-manager`,
  `agile-coach` (see `TEAMS.md`).

### 4. The core rule: verify by running it ("zero fake-solved")

> [!CAUTION]
> **Never call a problem solved without starting and testing the real application.** Reading
> the code or passing one isolated unit test is not enough when the app then crashes at boot.

Before you call the work done:
1. **Run the real start-up smoke test**: `tw.py smoke "<command that starts the app or game>" --timeout 5`
2. **Check that it does not crash**:
   - the process starts;
   - `stderr` and the runtime logs hold no `Traceback`, `Fatal Error`, `Exception`,
     `NullPointer` or `Segmentation fault`;
   - for a game or GUI: the main loop starts and stays alive for the whole test;
   - for a website or frontend: the server answers on localhost with 200 and no JS console errors.
3. If the application crashes, the problem is **not** solved: read the crash log, fix it and
   run the smoke test again.

For work that is not code (a plan, a schedule, a report), "running it" means checking every
number and date against its source and every formula with the inputs given.

### WSL bridge (Linux on Windows)

On Windows, **WSL** is available:
- use `wsl <command>` for POSIX tools (`bash`, `grep`, `awk`, `sed`), ELF binaries, Linux
  compilers or `/proc`;
- smoke tests of Linux runtimes: `tw.py smoke "<command>" --wsl`;
- `reverse-engineer` and `pentester` can use the native Linux environment through WSL;
- **do not skip Linux checks on Windows**: when a tool needs Linux, run it through `wsl`.

### 5. Adversarial gate, neural plasticity, and self-evolving skills

- Have the tester or pentester challenge the change, so edge cases do not break the app.
- Record every mistake found and avoided in the brain, so later tasks are vaccinated:
  `tw.py learn record --title "..." --trigger "..." --anti-pattern "..." --solution "..."`
- **Project Genome Assimilation**: extract architectural hubs, git co-change coupling rules,
  fragility hotspots, and verification commands into `.team-workflow/project_knowledge.json` and
  `docs/brain/PROJECT_GENOME.md`:
  `tw.py cortex assimilate`
- **Hebbian Feedback & Meta-Skill Evolution**: reinforce or dampen synaptic weights from the
  outcome, and synthesize reusable project & meta-orchestration skills (`team-meta-cortex` +
  domain guard skills in `.team-workflow/skills/`):
  `tw.py cortex feedback --outcome pass|fail|blocked --roles "<r1,r2>" --skills "<s1,s2>"`
  `tw.py cortex evolve`

### 6. Documentation gate

Before you release or close any workflow:
1. `tw.py verify-docs --strict`.
2. Make sure `docs/memory/STATE.md` was updated with the real changes.
3. Make sure the brain graph has no broken links or missing files.

### 7. GitHub cycle (issues, PRs, CI/CD, releases)

When the task touches GitHub (`issue`, `pr`, `review`, `ci`, `release`):
- **Issue fix**: read it with `gh issue view`, create a branch, fix and verify with `tw.py smoke`,
  open the PR that closes it (`Closes #num`).
- **Pull request**: `gh pr create` with a summary, the reason and the smoke-test evidence.
- **PR review**: `code-reviewer` reads the diff (`gh pr diff`) and checks for regressions.
- **CI/CD debugging**: when a GitHub Actions workflow fails, get the logs with
  `gh run view --log-failed` and hand them to `build-fixer`.
- **Releases**: `release-manager` handles semantic versioning, changelog, tag and
  `gh release create`.

### 8. Hardware and thermal guard (home vs away)

Zero-token hardware and thermal monitoring, to prevent overheating and watch the host:
- **Current state**: `tw.py hardware` (or `team hardware` from a terminal).
- **User at home** (`tw.py hardware --home`): sound alarm ON; above the critical thresholds
  (CPU > 85°C, GPU > 80°C) a beep warns the user at the desk.
- **User away** (`tw.py hardware --remote`): silent mode, no beeps; telemetry and alerts go to
  the dashboard on `http://127.0.0.1:8080`, which the user can expose to a phone with
  `cloudflared tunnel --url http://127.0.0.1:8080`.

### 9. Final report

Show the user only what matters, in their language:
- **Answers to the questions in between** (when the prompt had any).
- **What was done**, clearly and briefly.
- **Scan and documentation result** (`tw.py scan` and `tw.py verify-docs`).
- **Evidence from the real run** (smoke-test output, run time without crashes).
- **What to check with your own eyes** (the exact command to play or use the app).
