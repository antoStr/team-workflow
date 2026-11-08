---
id: skills-team-workflow-scripts-install_codex
title: install_codex.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/install_codex.py, install_codex.py]
upstream:
  - "[[skills-team-workflow-scripts-install_opencode]]"
  - "[[skills-team-workflow-scripts-roles]]"
downstream:
  - "[[tests-test_codex]]"
files: [skills/team-workflow/scripts/install_codex.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# install_codex.py

Install team-workflow into Codex (the OpenAI Codex CLI and app, also behind opencodex):

    ~/.codex/skills/team-workflow/                  the team-workflow skill: SKILL.md, WIZARD,
                                                    TEAMS, TALK, scripts, roles, library
    ~/.codex/skills/team-workflow-<name>/SKILL.md   one skill per workflow ($team-workflow-start,
                                                    $team-workflow-agents...)
    ~/.codex/agents/<role>.toml                     the enabled roles as Codex agents, listed in
                                                    ~/.codex/config.toml (a block we manage)
    ~/.codex/AGENTS.md                              a block: memory, settings and session setup
                                                    at the first task (session_start.py --text)
    ~/.codex/rules/team-workflow.rules              Codex's sandbox reads only the project: this
                                                    rule lets `<python> <our script>` run, and
                                                    nothing else

With --workspace the same goes into <repository>/.codex and the block into
<repository>/AGENTS.md. CODEX_HOME moves ~/.codex, as it does for Codex. Only what we wrote is
changed or removed: our files carry a mark, our config.toml lines sit between two markers.

    python3 install_codex.py [--workspace REPOSITORY] [--uninstall]

## Contracts


### Functions
- `config_dir(workspace)`
- `payload_dir(workspace)`
- `agents_md(workspace)`
- `python_path()`
- `present()`
- `read_text(path)`
- `split_block(text, begin, end)`
- `write_block(path, begin, end, body)`
- `table_names(text, table)`
- `defined_outside(path, begin, end, table)`
- `toml_key(name)`
- `register_agents(agents_dir)`
- `mcp_servers(workspace)`
- `our_mcp(inside)`
- `set_mcp(name, command, workspace)`
- ... and 11 more functions

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-install_opencode]]
- [[skills-team-workflow-scripts-roles]]
- None
### Downstream
- [[tests-test_codex]]
- None
