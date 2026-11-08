# team-workflow

- Project memory: read `docs/memory/INDEX.md` first, then `STATE.md` and the area card of your task.
- Before spawning agents, run the assignment wizard of the team-workflow skill (`WIZARD.md`);
  at the first team-workflow task of each conversation start with its session setup: where the
  choices go (this conversation, user defaults, this project), preset, roles, model and effort
  per role among what agy offers now (`tw.py options --app agy --json` shows the session model
  that `inherit` means, the tiers and the worker model ids), skills and add-ons, team talk.
- A request to fix, review, refactor or build something, including a detailed brief the user
  pastes, is work to dispatch: size it with the table in the team-workflow skill. Work alone
  only on trivial tasks; for anything larger choose delegation, run the wizard and launch the
  roles with `invoke_subagent` (`TypeName` = the role, for example `tester`), several
  independent roles in one call.
- Ask the user with the `ask_question` tool: `is_multi_select: true` only when several answers
  make sense (which roles), single choice otherwise.
- The user's settings: `python3 <team-workflow skill folder>/scripts/tw.py settings --json`;
  the roles with their type and model: `tw.py agents`. A role whose type is a built-in
  (`self`, `research`) is launched as that type with `tw.py agents show <role>` as its brief.
- Every task with two or more agents gets its own channel, a group conversation of you (as
  `orchestrator`), every agent and anyone who joins: they debug together, challenge and verify
  each other (`TALK.md` of the team-workflow skill, `tw.py talk`); the task
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
