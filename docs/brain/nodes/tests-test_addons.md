---
id: tests-test_addons
title: test_addons.py
layer: tests
tags: [code, py]
aliases: [tests/test_addons.py, test_addons.py]
upstream:
  - "[[skills-team-workflow-scripts-addons]]"
  - "[[skills-team-workflow-scripts-settings]]"
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_addons.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# test_addons.py

Offline tests for the add-on manager (no network, no real apps).

## Contracts

### Classes
- `AddonsTest` (methods: setUp, write, test_resolves_catalog_names_and_marketplace_ids, test_claude_adds_an_unknown_marketplace_then_installs, test_agy_skills_are_copied_marked_and_only_ours_removed, test_chosen_addons_are_saved_and_removed, test_frontend_bundle_copies_skills_from_their_folder_also_into_claude)
- `McpTest` (methods: test_mcp_servers_are_written_per_app_and_foreign_ones_left_alone, test_bundles_name_only_catalog_entries)

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-addons]]
- [[skills-team-workflow-scripts-settings]]
- [[tests-isolate_home]]
- None
### Downstream
- None
