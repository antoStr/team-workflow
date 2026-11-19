---
id: skills-team-scripts-setup_gate
title: setup_gate.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/setup_gate.py, setup_gate.py]
upstream:
  - "[[skills-team-scripts-roles]]"
  - "[[skills-team-scripts-settings]]"
downstream:
files: [skills/team/scripts/setup_gate.py]
status: active
last_updated: 2026-11-19T11:00:10
---

# setup_gate.py

PreToolUse hook (Claude Code, Agent and AskUserQuestion): the session setup comes first.

agy follows the session setup from its always-loaded rules; Claude Code skipped it and went from
the scan straight to the agents. This hook denies the launch of a team role until the transcript
shows `tw.py options`, `tw.py questions`, AskUserQuestion calls with all its headers (Scope,
Preset, every "Roles i/N" and "Skills i/N") and the model question of the role being launched
(header = role[:12], from `tw.py questions --roles`), or the user said "defaults" or "skip
setup". During the setup it also refuses a question with a made-up header, or a model question
before every role and skill group, before the user sees it. Headers are checked, not the text,
which may be translated. Built-in agents (Explore, general-purpose...) are never blocked.

## Contracts


### Functions
- `entries(path)`
- `user_text(entry)`
- `setup_missing(headers)`
- `scan(path)`
- `missing_step(path, role)`
- `check_question(path, questions, root)`
- `deny(reason)`
- `decide(data)`
- `main()`

## Dependencies
### Upstream
- [[skills-team-scripts-roles]]
- [[skills-team-scripts-settings]]
### Downstream
- None
