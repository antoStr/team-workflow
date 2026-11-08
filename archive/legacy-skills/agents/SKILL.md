---
name: agents
description: List and customize the team-workflow roles - type, model and effort per role and per app, packs (languages, quality, planning, ML...), your own roles (no tokens in Claude Code; in agy run `!team-workflow agents`)
argument-hint: "[list | set <role> model=<m> effort=<e> type=<t> [--app claude|agy] | enable|disable <role|pack|auto|languages> | new <role> | sync]"
disable-model-invocation: true
---

In Claude Code a hook answers this command without the model; you only see it when that hook
did not run (agy, or an old install). Then run
`python3 <team-workflow skill folder>/scripts/tw.py agents $ARGUMENTS` from the repository root
and show its output as it is. If the user asked in words ("use opus with max effort for the
tester", "turn on the Go reviewers"), translate it into `agents set` or `agents enable` and run
that. Remind the user to restart the app so it loads the changed agents.
