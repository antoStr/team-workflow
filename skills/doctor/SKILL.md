---
name: doctor
description: Health check of team in Claude Code and agy - versions, settings, native agents, add-ons, launcher, memory and audit - and repair with --fix (no tokens in Claude Code; in agy run `!team doctor`)
argument-hint: "[--fix]"
disable-model-invocation: true
---

In Claude Code a hook answers this command without the model; you only see it when that hook
did not run. Then run `python3 <team skill folder>/scripts/tw.py doctor $ARGUMENTS`
from the repository root and show its output as it is.
