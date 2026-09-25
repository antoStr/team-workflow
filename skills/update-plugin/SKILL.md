---
name: update-plugin
description: Update the team-workflow plugin to the latest version in Claude Code and agy, or just check which version is installed (no tokens in Claude Code; in agy run `!team-workflow update`)
argument-hint: "[check]"
disable-model-invocation: true
---

In Claude Code a hook answers this command without the model; you only see it when that hook
did not run (agy, or an old install). Then:

1. Run `python3 <team-workflow skill folder>/scripts/tw.py update`, adding `check` when the user
   wrote "check" (show the versions, change nothing): $ARGUMENTS
2. Show its output as it is, and tell the user to restart the session to load the new version.
3. In agy, add once: next time `!team-workflow update` in bash mode does it without spending
   tokens (after `python3 <team-workflow skill folder>/scripts/tw.py install-cli`).
