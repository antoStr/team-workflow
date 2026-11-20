---
id: skills-team-scripts-check_hook
title: check_hook.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/check_hook.py, check_hook.py]
upstream:
  - "[[skills-team-scripts-autolearn]]"
downstream:
files: [skills/team/scripts/check_hook.py]
status: active
last_updated: 2026-11-20T11:45:45
---

# check_hook.py

PostToolUse hook (Claude Code, Edit|Write|MultiEdit|NotebookEdit): run the learnings' checks on the
edited file. A match goes back to the model as a block with the required pattern, so a lesson learned
once is enforced every time instead of living as one more line in the prompts. Off with
TEAM_WORKFLOW_CHECKS=0.

## Contracts


### Functions
- `decide(data)`
- `main()`

## Dependencies
### Upstream
- [[skills-team-scripts-autolearn]]
### Downstream
- None
