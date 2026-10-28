---
name: library
description: The ECC library inside team-workflow - 311 skills, 97 commands and 22 rule sets from Everything Claude Code - list packs, search entries for a task, show one, install packs or entries as native skills (no tokens in Claude Code; in agy run `!team-workflow library`)
argument-hint: "[list [PACK...] | search WORDS | show ID | enable|disable ID|PACK [--project] | sync]"
disable-model-invocation: true
---

In Claude Code and OpenCode a hook answers this command without the model; you only see it
when that hook did not run. Then run `python3 <team-workflow skill folder>/scripts/tw.py library
$ARGUMENTS` from the repository root and show its output as it is.
