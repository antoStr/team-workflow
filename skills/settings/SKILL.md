---
name: settings
description: Show or change the team settings - wizard depth, team size, launch mode, models and effort per role, update and memory checks (no tokens in Claude Code; in agy run `!team settings`)
argument-hint: "[set <key> <value> [--project] | reset <key> [--project]]"
disable-model-invocation: true
---

In Claude Code a hook answers this command without the model; you only see it when that hook
did not run (agy, or an old install). Then:

1. Run `python3 <team skill folder>/scripts/tw.py settings $ARGUMENTS`.
2. Show its output as it is. If the user asked in words ("ask me fewer questions", "use pro for
   the tester"), translate it into `settings set <key> <value>` and run that.
3. In agy, add once: `!team settings` in bash mode does it without spending tokens
   (after `python3 <team skill folder>/scripts/tw.py install-cli`).
