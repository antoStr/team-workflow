---
id: tests-test_autolearn_gate_smoke
title: test_autolearn_gate_smoke.py
layer: tests
tags: [code, py]
aliases: [tests/test_autolearn_gate_smoke.py, test_autolearn_gate_smoke.py]
upstream:
  - "[[skills-team-workflow-scripts-autolearn]]"
  - "[[skills-team-workflow-scripts-gate]]"
  - "[[skills-team-workflow-scripts-smoke]]"
downstream:
files: [tests/test_autolearn_gate_smoke.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# test_autolearn_gate_smoke.py

Tests for autolearn, adversarial gate, and smoke live execution verification.

## Contracts

### Classes
- `AutoLearnTest` (methods: setUp, tearDown, test_record_and_get_vaccines)
- `AdversarialGateTest` (methods: setUp, tearDown, test_gate_lifecycle_and_autolearn_feed)
- `SmokeExecutionTest` (methods: test_clean_exit_command, test_crashed_command_detected, test_wsl_smoke_execution)

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-autolearn]]
- [[skills-team-workflow-scripts-gate]]
- [[skills-team-workflow-scripts-smoke]]
- None
### Downstream
- None
