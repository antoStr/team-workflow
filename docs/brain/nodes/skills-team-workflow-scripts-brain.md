---
id: skills-team-workflow-scripts-brain
title: brain.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/brain.py, brain.py]
upstream:
downstream:
  - "[[skills-team-workflow-scripts-tw]]"
  - "[[tests-test_brain]]"
files: [skills/team-workflow/scripts/brain.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# brain.py

team-workflow Brain: Obsidian-compatible graph memory engine (standard library only).

Manages an interconnected knowledge vault in docs/brain/ with bi-directional wikilinks [[...]],
AST-based repository mapping, fast BFS-expanded context queries, and vault health checks.

## Contracts


### Functions
- `_ensure_dir(path)`
- `_validate_vault_path(root, vault_dir)`
- `init_vault(vault_dir, root, force)`
- `_slugify(text)`
- `_extract_py_contracts(filepath)`
- `_extract_regex_contracts(filepath, ext)`
- `map_repo(root, vault_dir, incremental)`
- `_parse_frontmatter(text)`
- `_load_all_nodes(vault_path)`
- `query_context(target_or_query, vault_dir, root, hops, format)`
- `context_briefing(target_or_query, vault_dir, root, hops, role)`
- `check_vault(vault_dir, root, strict)`
- `rollover_state(root, vault_dir)`

## Dependencies
### Upstream
- None
### Downstream
- [[skills-team-workflow-scripts-tw]]
- [[tests-test_brain]]
- None
