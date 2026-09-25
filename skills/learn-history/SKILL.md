---
name: learn-history
description: Learn this repository's habits from its git history - hotspots, bug-prone files, files that change together, commit conventions, reverts - and turn them into project memory (Known traps, conventions) or a project skill, with your approval
argument-hint: "[max commits, default 2000]"
disable-model-invocation: true
---

Use the team-workflow skill to learn from the history of this repository: $ARGUMENTS

1. Run `python3 <team-workflow skill folder>/scripts/tw.py learn --json` (add `--max <n>` when
   the user gave a number) from the repository root. It reads git locally; nothing leaves the
   machine.
2. Read `docs/memory` (MAP, the area cards, PLAYBOOKS). If it is missing, offer
   `/team-workflow:setup-memory` first.
3. Turn the facts into proposals, each tied to the evidence (the files and commits):
   - bug-prone files and reverts: a "Known traps" entry in the area card, after reading the
     fix commits (`git show <hash>`) to state the trap in one line;
   - files that change together: a note in the area card, or a finding when the coupling is
     accidental;
   - commit conventions and how often tests change with code: `PLAYBOOKS.md`;
   - when the user wants it, a project skill with these conventions in
     `.claude/skills/<repo>-conventions/SKILL.md` (and `.agents/skills/` for agy).
4. Show the proposals and ask which to apply (AskUserQuestion, multiSelect; `ask_question`
   with `is_multi_select: true` in agy). Write only what the user picks, then run memcheck.
