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
last_updated: 2026-11-20T13:06:59
---

# setup_gate.py

PreToolUse hook (Claude Code, Agent and AskUserQuestion): the session setup comes first.

agy follows the session setup from its always-loaded rules; Claude Code skipped it and went from
the scan straight to the agents. This hook denies the launch of a team role until the transcript
shows `tw.py options`, `tw.py questions`, AskUserQuestion calls with all its headers (Scope,
Preset, every "Roles i/N" and "Skills i/N") and the model question of the role being launched
(header = role[:12], from `tw.py questions --roles`), or the user said "defaults" or "skip
setup", or answered the first question, "Mode", with Auto or Skip setup (recorded by
`tw.py questions --mode auto|skip` once "Mode" was asked). During the setup it also refuses a question with a made-up header, or a model question
before every role and skill group, before the user sees it. Headers are checked, not the text,
which may be translated. Built-in agents (Explore, general-purpose...) are never blocked.

Code Mode runs the shell from a REPL script and logs only some of those calls in the transcript, so
the steps also come from the setup state (`settings.update_setup_state`): `tw.py options` and
`questions` record their run, this hook the headers it let through. Only records made after the
transcript's first entry count.

## Contracts


### Functions
- `entries(path)`
- `user_text(entry)`
- `setup_missing(headers, printed)`
- `epoch(stamp)`
- `recorded(root, start, session)`
- `record_asked(root, session, questions)`
- `scan(path, root, session)`
- `missing_step(path, role, root, session)`
- `check_question(path, questions, root, session)`
- `deny(reason)`
- `decide(data)`
- `main()`

## Dependencies
### Upstream
- [[skills-team-scripts-roles]]
- [[skills-team-scripts-settings]]
### Downstream
- None
