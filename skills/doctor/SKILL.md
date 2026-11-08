---
name: doctor
description: Health check of team-workflow in Claude Code and agy - versions, settings, native agents, add-ons, launcher, memory and audit - and repair with --fix (no tokens in Claude Code; in agy run `!team-workflow doctor`)
argument-hint: "[--fix]"
disable-model-invocation: true
---

In Claude Code a hook answers this command without the model; you only see it when that hook
did not run. Then run `python3 <team-workflow skill folder>/scripts/tw.py doctor $ARGUMENTS`
from the repository root and show its output as it is.
