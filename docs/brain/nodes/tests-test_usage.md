---
id: tests-test_usage
title: test_usage.py
layer: tests
tags: [code, py]
aliases: [tests/test_usage.py, test_usage.py]
upstream:
  - "[[skills-team-scripts-estimate]]"
  - "[[skills-team-scripts-usage]]"
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_usage.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# test_usage.py

Offline tests for usage.py and estimate.py:  python3 -m unittest discover -s tests

## Contracts

### Classes
- `Fixture` (methods: setUp, jsonl, add_subagent)
- `UsageTest` (methods: test_message_blocks_counted_once_and_labelled, test_cost_and_ledger)
- `EstimateTest` (methods: test_profile_scales_with_effort_and_files, test_history_calibrates_and_unknown_model_has_no_price)

### Functions
- `assistant(msg_id, block, model, sidechain)`

## Dependencies
### Upstream
- [[skills-team-scripts-estimate]]
- [[skills-team-scripts-usage]]
- [[tests-isolate_home]]
### Downstream
- None
