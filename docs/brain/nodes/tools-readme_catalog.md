---
id: tools-readme_catalog
title: readme_catalog.py
layer: tools
tags: [code, py]
aliases: [tools/readme_catalog.py, readme_catalog.py]
upstream:
  - "[[skills-team-scripts-library]]"
  - "[[skills-team-scripts-roles]]"
downstream:
files: [tools/readme_catalog.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# readme_catalog.py

Write docs/CATALOG.md: every agent (role) by pack and every library entry (skills, commands,
rules) by pack, from the plugin's own files, so the documentation never drifts from what ships.

    python3 tools/readme_catalog.py          rewrite docs/CATALOG.md
    python3 tools/readme_catalog.py --check  exit 1 when it is out of date (the tests run it)

## Contracts


### Functions
- `italian()`
- `it_text(table, key, it)`
- `version()`
- `agent_it(role, meta, it)`
- `agents_block()`
- `library_it(e, it)`
- `library_block()`
- `render()`
- `main(argv)`

## Dependencies
### Upstream
- [[skills-team-scripts-library]]
- [[skills-team-scripts-roles]]
### Downstream
- None
