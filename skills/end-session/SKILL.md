---
name: end-session
description: Close the session - update the project memory, record lessons and decisions, report what is left
disable-model-invocation: true
---

Use the team-workflow skill to close this session.

1. List what changed in this session: `git status` and the commits made since it started.
2. Update the memory: yourself for a small change, `doc-keeper` for a larger one (give it the
   commits, the decisions and lessons to record, and the memcheck command).
3. Record the lessons that would have saved time under "Known traps" in the area card, and
   the structural decisions in `DECISIONS.md`.
4. Run memcheck and set the resume point in `STATE.md`.
5. Propose a commit of the work and of the memory (AskUserQuestion); commit only after the
   user agrees, and push only if they ask for it.
6. Give the end-of-task report, including what is left for the next session.
