---
name: addons
description: Add, remove, update or list add-on plugins (skills, plugins and MCP servers - caveman, ponytail, the frontend, token-saving, mcp and popular bundles, or any plugin from a marketplace or GitHub) in Claude Code, agy and OpenCode (no tokens in Claude Code; in agy run `!team-workflow addons`)
argument-hint: "[list | add <name|owner/repo|plugin@marketplace> [--app claude|agy|opencode] | remove <name> | update [name]]"
disable-model-invocation: true
---

In Claude Code a hook answers this command without the model; you only see it when that hook
did not run (agy, or an old install). Then:

1. Run `python3 <team-workflow skill folder>/scripts/tw.py addons $ARGUMENTS` from the repository
   root and show its output as it is.
2. If the user asked in words ("install caveman", "add the MCP servers"), translate it into
   `addons add <name>` or `addons remove <name>` and run that.
3. Remind the user to restart the app to load the change; in agy, `!team-workflow addons`
   does it without spending tokens (after `tw.py install-cli`).
