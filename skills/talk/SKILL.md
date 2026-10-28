---
name: talk
description: Read what the agents said to each other - the team talk channels of this repository, one channel's messages, the questions and challenges still open (no tokens in Claude Code; in agy run `!team-workflow talk`)
argument-hint: "[list | read TOPIC | open TOPIC | clear TOPIC]"
disable-model-invocation: true
---

In Claude Code and OpenCode a hook answers this command without the model; you only see it
when that hook did not run. Then run `python3 <team-workflow skill folder>/scripts/tw.py talk
$ARGUMENTS` from the repository root and show its output as it is.
