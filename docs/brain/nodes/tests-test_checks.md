---
id: tests-test_checks
title: test_checks.py
layer: tests
tags: [code, py]
aliases: [tests/test_checks.py, test_checks.py]
upstream:
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_checks.py]
status: active
last_updated: 2026-11-20T11:45:45
---

# test_checks.py

Learnings with a check: enforced on every edit, at Stop and in CI, not sent as prose.

## Contracts

### Classes
- `ChecksTest` (methods: tw, record, hook, test_edit_hook_blocks_a_match_with_file_and_line, test_cli_check_exit_code_and_no_prose_vaccine, test_the_learning_text_itself_does_not_fail, test_absolute_paths_and_big_or_binary_files, test_invalid_pattern_is_refused, test_stop_blocks_on_a_changed_file_that_fails_a_check)

## Dependencies
### Upstream
- [[tests-isolate_home]]
### Downstream
- None
