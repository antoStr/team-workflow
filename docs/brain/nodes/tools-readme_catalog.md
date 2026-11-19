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
last_updated: 2026-11-19T11:00:10
---

# readme_catalog.py

Write docs/CATALOG.md (English) and docs/CATALOG.it.md (Italian): every agent (role) by pack
and every library entry (skills, commands, rules) by pack, from the plugin's own files, so the
documentation never drifts from what ships.

    python3 tools/readme_catalog.py          rewrite both catalogs
    python3 tools/readme_catalog.py --check  exit 1 when one is out of date (the tests run it)

## Contracts


### Functions
- `italian()`
- `it_text(table, key, it)`
- `first_sentence(text)`
- `text_for(table, key, english, it, lang)`
- `version()`
- `agent_text(role, meta, it, lang)`
- `agents_block(lang, it)`
- `library_text(e, it, lang)`
- `library_block(lang, it)`
- `anchor(title)`
- `render(lang)`
- `main(argv)`

## Dependencies
### Upstream
- [[skills-team-scripts-library]]
- [[skills-team-scripts-roles]]
### Downstream
- None
