---
name: setup
description: Set up team-workflow in one place - activation (on its own in every project, only in this project, or only when you call it), session wizard, team size and launch, models and effort, roles and packs, the library, agents that talk to each other, checks, add-ons and presets
argument-hint: "[area to change, for example activation or library]"
disable-model-invocation: true
---

Run `python3 <team-workflow skill folder>/scripts/tw.py setup` from the repository root and
show its output as it is. It is the current configuration: every value says whether it comes
from the project file, the user file or the defaults.

Then ask with the question tool (AskUserQuestion; agy `ask_question`; OpenCode `question`; Codex
`request_user_input`, or a numbered list), in
the user's language, recommended option first. If the user named an area ($ARGUMENTS), start
there and skip the questions about the others.

1. **Activation** (single choice):
   - "On its own in every project": `settings set activation auto`.
   - "Only in this project": `settings set activation manual`, then
     `settings set activation auto --project` (needs a git repository).
   - "Only when I call it": `settings set activation manual` (add `--project` when the user
     wants it for this repository alone).
   Auto loads the memory, the protocol and the Stop check at every session; manual keeps
   team-workflow quiet until `/team-workflow:<name>`. In agy the plugin's rules always load:
   manual there only turns off the Stop check.
2. **What else to change** (multi-select, at most four options per question, so ask two
   questions in one call): session setup and questions; team size and launch; models and
   effort; roles and packs; the library; agents talking to each other; checks; add-ons;
   a preset. Nothing chosen: go to step 4.
3. For each chosen area, one question with the concrete choices, then run the command:
   - Session setup and questions: `session_wizard` true or false, `wizard` quick, full or off,
     `end_report` full or short.
   - Team: `max_agents` (2, 4, 6), `launch` native or worker, `worker_edits`,
     `auto_security_review`.
   - Models and effort: show `tw.py options --app <this app>`; set the defaults
     (`settings set models.claude.default sonnet`, `effort.default medium`) or one role
     (`agents set ROLE model=M effort=E`).
   - Roles and packs: show `tw.py agents`; offer the packs that are off (languages of the
     repository first: `agents enable auto`; quality, planning, frameworks, harness, gan, ml,
     opensource, network, domains, ops, growth, alt) with `agents enable PACK`.
   - The library: show `tw.py library`; offer packs or entries to install as native skills
     (`library enable PACK|ID`), the language rules of this repository first
     (`library enable rules-<language>`). Say that the orchestrator can use any entry by path
     without installing it, and that installed skills take room in every session's context.
   - Agents talking to each other: `talk` true or false, `talk_rounds` 1 to 5 (`TALK.md`).
   - Checks: `stop_check`, `update_check`.
   - Add-ons: show `tw.py addons`; `addons add NAME`, or a bundle: `frontend` (impeccable,
     taste, frontend-design, solar-icons, cloudflare: the frontend roles use them),
     `token-saving` (caveman, ponytail, context-mode, serena), `mcp` (context7, playwright,
     serena, sequential-thinking), `popular` (superpowers, Anthropic's skills, karpathy,
     ui-ux-pro-max, context7).
   - A preset: `tw.py profile` lists them; `profile NAME`.
   Ask each time whether the change is for every project (user file) or this repository
   (`--project`) when the user did not say.
4. Run `tw.py setup` again, show the lines that changed, and say what needs a restart of the
   app (new or changed agents and library skills load at the next session).

The commands are `python3 <team-workflow skill folder>/scripts/tw.py <command>`; on Windows
use the Python the install names when `python3` is the Microsoft Store placeholder.
