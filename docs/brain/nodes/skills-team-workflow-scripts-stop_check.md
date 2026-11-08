---
id: skills-team-workflow-scripts-stop_check
title: stop_check.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/stop_check.py, stop_check.py]
upstream:
  - "[[skills-team-workflow-scripts-settings]]"
downstream:
files: [skills/team-workflow/scripts/stop_check.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# stop_check.py

Stop hook: ask for a memory update when files changed after docs/memory/STATE.md.

It looks at the changes of this session (working tree, and commits since SessionStart),
never blocks twice in a row (stop_hook_active) and is off with the setting stop_check=false
(or TEAM_WORKFLOW_STOP_CHECK=0), and with activation=manual.

## Contracts


### Functions
- `changed_this_session(root, snap)`
- `newest_mtime(root, paths)`
- `decide(data)`
- `main()`

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-settings]]
- None
### Downstream
- None
