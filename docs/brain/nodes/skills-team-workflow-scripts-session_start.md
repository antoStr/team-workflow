---
id: skills-team-workflow-scripts-session_start
title: session_start.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/session_start.py, session_start.py]
upstream:
  - "[[skills-team-workflow-scripts-library]]"
  - "[[skills-team-workflow-scripts-opencode_cli]]"
  - "[[skills-team-workflow-scripts-roles]]"
  - "[[skills-team-workflow-scripts-settings]]"
  - "[[skills-team-workflow-scripts-update_plugin]]"
downstream:
files: [skills/team-workflow/scripts/session_start.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# session_start.py

SessionStart hook: put the project memory in the agent's context.

Prints nothing outside a git repository. In a repository without docs/memory it adds a
one-line hint, so the agent can offer to create it. It also records the repository state
for the Stop hook (stop_check.py), adds the settings that differ from the defaults, and tells
the user (not the model) when a newer version is out. It keeps the enabled roles current as
native agents of the app (~/.claude/agents, ~/.gemini/config/agents), from the settings,
and the library entries the user switched on as native skills. With activation = manual it adds
one line instead of the memory: use team-workflow only when the user calls it.

## Contracts


### Functions
- `agents_dir(app)`
- `opencode_notes()`
- `codex_notes()`
- `memory_context(root, config)`
- `save_snapshot(root, session_id)`
- `main()`

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-library]]
- [[skills-team-workflow-scripts-opencode_cli]]
- [[skills-team-workflow-scripts-roles]]
- [[skills-team-workflow-scripts-settings]]
- [[skills-team-workflow-scripts-update_plugin]]
- None
### Downstream
- None
