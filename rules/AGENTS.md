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
- When two or more agents work on one task, give them a shared channel so they debug together,
  challenge and verify each other (`TALK.md` of the team-workflow skill, `tw.py talk`); the task
  is not done while `tw.py talk open <topic>` lists anything.
- Before briefing agents, `tw.py library search <task words>` finds skills, commands and
  rules; give each agent the paths it needs.
- End every task with a report: done, verified with evidence, findings, decisions. Ask before
  applying anything the user did not request.
- When files change, update `docs/memory/STATE.md`.
- Answer in the language the user writes in.
