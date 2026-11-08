---
id: tests-test_scripts
title: test_scripts.py
layer: tests
tags: [code, py]
aliases: [tests/test_scripts.py, test_scripts.py]
upstream:
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_scripts.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# test_scripts.py

Offline tests for the team-workflow scripts:  python3 -m unittest discover -s tests

## Contracts

### Classes
- `ScriptTest` (methods: setUp, git, run_script, write, read, init_memory)
- `InitMemoryTest` (methods: test_creates_memory_commands_and_pointers_once)
- `MemcheckTest` (methods: memcheck, test_fresh_memory_passes_strict, test_limits_secrets_and_missing_paths)
- `SessionStartTest` (methods: context, test_silent_outside_git, test_hint_without_memory, test_injects_index_and_state)
- `StopCheckTest` (methods: setUp, stop, test_nothing_changed, test_code_change_without_state_update_blocks, test_never_twice_and_opt_out, test_state_must_be_newer_than_the_latest_change, test_commit_without_state_update_blocks, test_silent_without_memory)

## Dependencies
### Upstream
- [[tests-isolate_home]]
- None
### Downstream
- None
