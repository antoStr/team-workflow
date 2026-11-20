---
id: tests-test_update
title: test_update.py
layer: tests
tags: [code, py]
aliases: [tests/test_update.py, test_update.py]
upstream:
  - "[[skills-team-scripts-update_plugin]]"
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_update.py]
status: active
last_updated: 2026-11-20T13:06:59
---

# test_update.py

Offline tests for the version parsing in update_plugin.py.

## Contracts

### Classes
- `UpdateTest` (methods: test_latest_tag_compares_numbers_not_text, test_claude_version_from_plugin_list, test_update_targets_the_installed_plugin_id)
- `AutoUpdateTest` (methods: test_starts_one_detached_update_per_window_and_only_when_newer, test_only_team_prompts_trigger_the_check, test_finds_the_opencode_and_codex_installs_where_their_installers_put_them, test_update_opencode_clears_read_only_git_temp_dirs)
- `UpdateLockTest` (methods: test_one_update_at_a_time, test_main_releases_the_lock)

## Dependencies
### Upstream
- [[skills-team-scripts-update_plugin]]
- [[tests-isolate_home]]
### Downstream
- None
