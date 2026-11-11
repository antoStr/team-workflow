# team

- Project memory: read `docs/memory/INDEX.md` first, then `STATE.md` and the area card of your task.
- Zero-Ghosting for In-Between Questions ("writing-in-between"): if the user's prompt contains questions, doubts, curiosities, or remarks interleaved in the text, you MUST answer each and every one of them explicitly and thoroughly at the start of your response before or alongside executing actions. Never skip or ghost an in-between question.
- Dynamic Agent Selection & Full Catalog: never limit the user to 4 fixed options or rigid agent presets. The user has access to the full catalog of 131 specialists (`tw.py agents catalog`). Strictly respect the exact number and roles of agents requested by the user. Support dynamic addition, removal, and modification of agents at any time.
- Mandatory Repository Scan (`tw.py scan`): on every `/team` invocation, run `python skills/team/scripts/tw.py scan` to survey repository status, branch, detected stack (Next.js, React, Tailwind, Python, etc.), frontend UI component stack, and memory health.
- Mandatory Documentation & Workflow Verification Gate (`tw.py verify-docs`): before concluding any team task or workflow, run `python skills/team/scripts/tw.py verify-docs` to ensure `STATE.md`, Brain nodes, and project documentation have been created or updated accurately matching the work performed.
- Modern Frontend Components: for frontend and UI tasks, leverage the `frontend-components` library pack (`pick-ui-library`, `shadcn-ui`, `base-ui`, `radix-ui`, `sonner-toast`, `vaul-drawer`, `cmdk-palette`, `number-flow`, `beautiful-ui`, `rare-ui`, `magic-ui`, `aceternity-ui`, `registry-21st-dev`) and assign to `design-engineer` or `frontend-dev`.
- Before spawning agents, run the assignment wizard of the team skill (`WIZARD.md`);
  at the first team-workflow task of each conversation start with its session setup: where the
  choices go (this conversation, user defaults, this project), preset, roles, model and effort
  per role among what agy offers now (`tw.py options --app agy --json` shows the session model
  that `inherit` means, the tiers and the worker model ids), skills and add-ons, team talk.
- A request to fix, review, refactor or build something, including a detailed brief the user
  pastes, is work to dispatch: size it with the table in the team skill. Work alone
  only on trivial tasks; for anything larger choose delegation, run the wizard and launch the
  roles with `invoke_subagent` (`TypeName` = the role, for example `tester`), several
  independent roles in one call.
- Ask the user with the `ask_question` tool: `is_multi_select: true` only when several answers
  make sense (which roles), single choice otherwise.
- The user's settings: `python3 <team skill folder>/scripts/tw.py settings --json`;
  the roles with their type and model: `tw.py agents`. A role whose type is a built-in
  (`self`, `research`) is launched as that type with `tw.py agents show <role>` as its brief.
- Every task with two or more agents gets its own channel, a group conversation of you (as
  `orchestrator`), every agent and anyone who joins: they debug together, challenge and verify
  each other (`TALK.md` of the team skill, `tw.py talk`); the task
  is not done while `tw.py talk open <topic>` lists anything.
- Before briefing agents, `tw.py library search <task words>` finds skills, commands and
  rules; give each agent the paths it needs.
- End every task with a report: done, verified with evidence, findings, decisions. Ask before
  applying anything the user did not request.
- Live Execution Gate (Zero Fake-Solved): never claim an application, game, or UI bug is solved
  without actually launching the process (`tw.py smoke "<command>" --timeout 5`) and capturing
  real runtime proof that it booted and ran stably without crashes or fatal exceptions.
- WSL Bridge: On Windows, WSL (Windows Subsystem for Linux) is fully available and should be
  used whenever Linux-specific features (`/proc`, systemd, ext4), Linux ELF binaries, POSIX tools,
  or Linux test environments are required (`wsl <command>` or `tw.py smoke "<cmd>" --wsl`).
- Large Codebase Navigation: use `tw.py brain context <module>` to inspect 1-hop dependencies
  and active vaccines instead of scanning entire codebases with grep.
- Auto-Learning: whenever a bug is fixed or an adversarial gate passes after a challenge,
  record the anti-pattern with `tw.py learn record` so the team never repeats it.
- When files change, update `docs/memory/STATE.md`.
- Answer in the language the user writes in.
