# team-workflow

- Project memory: read `docs/memory/INDEX.md` first, then `STATE.md` and the area card of your task.
- Before spawning agents, run the assignment wizard of the team-workflow skill (`WIZARD.md`).
- A request to fix, review, refactor or build something, including a detailed brief the user
  pastes, is work to dispatch: size it with the table in the team-workflow skill. Work alone
  only on trivial tasks; for anything larger choose delegation, run the wizard and launch the
  roles with `invoke_subagent` (`TypeName` = the role, for example `tester`), several
  independent roles in one call.
- Ask the user with the `ask_question` tool: `is_multi_select: true` only when several answers
  make sense (which roles), single choice otherwise.
- The user's settings: `python3 <team-workflow skill folder>/scripts/tw.py settings --json`.
- End every task with a report: done, verified with evidence, findings, decisions. Ask before
  applying anything the user did not request.
- When files change, update `docs/memory/STATE.md`.
- Answer in the language the user writes in.
