---
id: tests-test_hook_wrapper
title: test_hook_wrapper.py
layer: tests
tags: [code, py]
aliases: [tests/test_hook_wrapper.py, test_hook_wrapper.py]
upstream:
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_hook_wrapper.py]
status: active
last_updated: 2026-11-19T11:00:10
---

# test_hook_wrapper.py

The Claude Code hooks run through hooks/run-py.cmd, which finds a Python that really runs.

## Contracts

### Classes
- `HookWrapperTest` (methods: test_every_claude_hook_goes_through_the_wrapper, test_skips_a_python3_that_does_not_run_and_keeps_the_hook_input)

## Dependencies
### Upstream
- [[tests-isolate_home]]
### Downstream
- None
