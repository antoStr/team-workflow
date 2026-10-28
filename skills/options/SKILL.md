---
name: options
description: Show the models and efforts each app offers (native agents and workers), every role with its type, model, effort and how it runs, and when to change them (no tokens in Claude Code and OpenCode; in agy run `!team-workflow options`)
argument-hint: "[--app claude|agy|opencode|codex|all]"
disable-model-invocation: true
---

In Claude Code and OpenCode a hook answers this command without the model; you only see it
when that hook did not run. Then run `python3 <team-workflow skill folder>/scripts/tw.py options
$ARGUMENTS` from the repository root and show its output as it is.
