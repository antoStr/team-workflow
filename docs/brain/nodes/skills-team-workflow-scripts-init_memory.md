---
id: skills-team-workflow-scripts-init_memory
title: init_memory.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/init_memory.py, init_memory.py]
upstream:
downstream:
files: [skills/team-workflow/scripts/init_memory.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# init_memory.py

Create docs/memory from the templates and point AGENTS.md (and GEMINI.md, CLAUDE.md when
they exist) to it. Existing files are never overwritten; running it again changes nothing.

    python3 init_memory.py --root /path/to/repository

## Contracts


### Functions
- `detect_commands(root)`
- `copy_templates(root)`
- `fill_commands(playbooks, cmds)`
- `add_pointer(path, create)`
- `main()`

## Dependencies
### Upstream
- None
### Downstream
- None
