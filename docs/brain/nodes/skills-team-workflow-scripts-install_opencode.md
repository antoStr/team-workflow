---
id: skills-team-workflow-scripts-install_opencode
title: install_opencode.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/install_opencode.py, install_opencode.py]
upstream:
  - "[[skills-team-workflow-scripts-opencode_cli]]"
  - "[[skills-team-workflow-scripts-roles]]"
downstream:
  - "[[skills-team-workflow-scripts-install_codex]]"
  - "[[tests-test_opencode]]"
files: [skills/team-workflow/scripts/install_opencode.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# install_opencode.py

Install team-workflow into OpenCode (~/.config/opencode, or <repository>/.opencode).

What it writes, every file marked as ours so updates and uninstall touch nothing else:
    skills/team-workflow/            the team-workflow skill: SKILL.md, WIZARD, TEAMS, scripts, roles
    commands/team-workflow/<name>.md one command per workflow: /team-workflow/<name>
    agents/<role>.md                 the enabled roles as OpenCode subagents (roles.py)
    OpenCode 2.x: a team-workflow block in AGENTS.md (~/.config/opencode/AGENTS.md, or the
                  repository's AGENTS.md): load the memory at the first task, the notes.
                  The commands that need no reasoning print tw.py's output (!`...` in the
                  command), so the model only shows it.
    OpenCode 1.x: plugins/team-workflow.js: memory in the system prompt, no-token commands,
                  STATE reminder. OpenCode 2.x plugins cannot do that, so it is not written.

The commands live in a folder because a colon is not allowed in a Windows file name.

    python3 install_opencode.py [--workspace REPOSITORY] [--source URL_OR_PATH]
    python3 install_opencode.py --uninstall

## Contracts


### Functions
- `config_dir(workspace)`
- `payload_dir(workspace)`
- `commands_dir(workspace)`
- `agents_md(workspace)`
- `own_version()`
- `installed_version(workspace)`
- `installed_source(workspace)`
- `posix(path)`
- `with_python(text, python)`
- `command_text(name, skill_md, scripts, python, v2)`
- `ours(path)`
- `remove_commands(conf, keep)`
- `agents_block(scripts, python)`
- `write_block(path, block)`
- `strip_block(text)`
- ... and 4 more functions

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-opencode_cli]]
- [[skills-team-workflow-scripts-roles]]
- None
### Downstream
- [[skills-team-workflow-scripts-install_codex]]
- [[tests-test_opencode]]
- None
