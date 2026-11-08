---
name: library
description: The library inside team-workflow - 296 skills, 94 commands and 22 coding rule sets - list packs, search entries for a task, show one, install packs or entries as native skills (no tokens in Claude Code; in agy run `!team-workflow library`)
argument-hint: "[list [PACK...] | search WORDS | show ID | enable|disable ID|PACK [--project] | sync]"
disable-model-invocation: true
---

In Claude Code and OpenCode a hook answers this command without the model; you only see it
when that hook did not run. Then run `python3 <team-workflow skill folder>/scripts/tw.py library
$ARGUMENTS` from the repository root and show its output as it is.
