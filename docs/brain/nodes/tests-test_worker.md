---
id: tests-test_worker
title: test_worker.py
layer: tests
tags: [code, py]
aliases: [tests/test_worker.py, test_worker.py]
upstream:
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_worker.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# test_worker.py

Offline tests for run_worker.py with fake claude and agy CLIs.

## Contracts

### Classes
- `WorkerTest` (methods: setUp, run_worker, test_claude_worker_is_read_only_by_default_and_recorded, test_agy_worker_with_edits_counts_thinking_as_output)

## Dependencies
### Upstream
- [[tests-isolate_home]]
### Downstream
- None
