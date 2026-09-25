---
name: options
description: Show what the session wizard can offer in this app right now - presets, enabled roles with type, model and effort, the models and efforts for native agents and for workers (no tokens in Claude Code and OpenCode; in agy run `!team-workflow options`)
argument-hint: "[--app claude|agy|opencode]"
disable-model-invocation: true
---

In Claude Code and OpenCode a hook answers this command without the model; you only see it
when that hook did not run. Then run `python3 <team-workflow skill folder>/scripts/tw.py options
$ARGUMENTS` from the repository root and show its output as it is.
