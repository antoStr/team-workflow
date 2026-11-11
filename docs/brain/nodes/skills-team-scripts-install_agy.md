---
id: skills-team-scripts-install_agy
title: install_agy.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/install_agy.py, install_agy.py]
upstream:
  - "[[skills-team-scripts-roles]]"
downstream:
  - "[[tests-test_settings]]"
files: [skills/team/scripts/install_agy.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# install_agy.py

Copy the team-workflow plugin into an agy (Antigravity CLI) plugins folder.

The repository itself is an agy plugin: the usual install is
`agy plugin install https://github.com/antoStr/team-workflow` (or a local path). Use this script
for one project only (--workspace) or to copy just the files agy needs.

agy discovers plugins in its customization roots: ~/.gemini/config/plugins/<name>/ for every
project, <repository>/.agents/plugins/<name>/ for one. agy loads skills/<name>/SKILL.md (the
workflows are skills, so both harnesses read them), rules/, hooks.json and plugin.json.

agy does not offer a plugin's agents as subagents: it takes them from ~/.gemini/config/agents/
(or <repository>/.agents/agents/), in its own format. sync_agents() writes the roles there
(roles.py); the agy hook refreshes them at every session; --agents-only does it by hand.

    python3 install_agy.py [--workspace REPOSITORY | --dest DIR] [--agents-only]

## Contracts


### Functions
- `ours(dest)`
- `agents_dir(workspace)`
- `sync_agents(dest, config)`
- `safe_rmtree(path)`
- `build(dest)`
- `main()`

## Dependencies
### Upstream
- [[skills-team-scripts-roles]]
### Downstream
- [[tests-test_settings]]
