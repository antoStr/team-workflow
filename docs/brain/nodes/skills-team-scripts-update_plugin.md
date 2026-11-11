---
id: skills-team-scripts-update_plugin
title: update_plugin.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/update_plugin.py, update_plugin.py]
upstream:
downstream:
  - "[[skills-team-scripts-doctor]]"
  - "[[skills-team-scripts-session_start]]"
  - "[[skills-team-scripts-tw]]"
  - "[[tests-test_update]]"
files: [skills/team/scripts/update_plugin.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# update_plugin.py

Show the installed team-workflow versions and update them, in Claude Code and in agy.

Latest version: the highest vX.Y.Z tag of the repository. Claude Code updates through its
marketplace; agy has no update command, so the plugin is uninstalled and installed again.

    python3 update_plugin.py [--check] [--harness claude|agy|all] [--source URL_OR_PATH]

## Contracts


### Functions
- `run()`
- `vkey(v)`
- `latest_tag(ls_remote)`
- `fetch_latest(timeout)`
- `own_version()`
- `newer_version(max_age)`
- `claude_version(plugin_list)`
- `agy_version()`
- `opencode_payload()`
- `codex_payload()`
- `payload_version(harness)`
- `opencode_version()`
- `installed(harness)`
- `update_opencode(harness)`
- `update(harness, source)`
- ... and 5 more functions

## Dependencies
### Upstream
- None
### Downstream
- [[skills-team-scripts-doctor]]
- [[skills-team-scripts-session_start]]
- [[skills-team-scripts-tw]]
- [[tests-test_update]]
