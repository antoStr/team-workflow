---
id: tests-test_agy
title: test_agy.py
layer: tests
tags: [code, py]
aliases: [tests/test_agy.py, test_agy.py]
upstream:
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_agy.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# test_agy.py

Offline tests for agy support: hook payloads in agy's format and the agy plugin builder.

## Contracts

### Classes
- `AgyHooksTest` (methods: setUp, test_pre_invocation_saves_snapshot_without_injecting, test_stop_continues_once_when_state_is_behind, test_finds_the_repository_through_agy_process_without_workspace_paths)
- `AgyPluginTest` (methods: build, test_builds_plugin_with_skills_roles_rules_and_hooks, test_never_replaces_a_foreign_folder)

## Dependencies
### Upstream
- [[tests-isolate_home]]
- None
### Downstream
- None
