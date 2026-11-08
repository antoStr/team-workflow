---
id: skills-team-workflow-scripts-prompt_command
title: prompt_command.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/prompt_command.py, prompt_command.py]
upstream:
downstream:
  - "[[tests-test_settings]]"
files: [skills/team-workflow/scripts/prompt_command.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# prompt_command.py

UserPromptSubmit hook (Claude Code): answer /team-workflow:update-plugin, :settings, :models,
:addons, :agents, :profile, :audit, :doctor, :ci-init, :options, :library and :talk by running
tw.py, and block the prompt so the model never sees it (no tokens spent).
Any other prompt passes through untouched.

## Contracts


### Functions
- `tw_args(prompt)`
- `main()`

## Dependencies
### Upstream
- None
### Downstream
- [[tests-test_settings]]
- None
