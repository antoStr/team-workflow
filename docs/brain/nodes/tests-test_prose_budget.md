---
id: tests-test_prose_budget
title: test_prose_budget.py
layer: tests
tags: [code, py]
aliases: [tests/test_prose_budget.py, test_prose_budget.py]
upstream:
  - "[[skills-team-scripts-omniscience]]"
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_prose_budget.py]
status: active
last_updated: 2026-11-20T11:45:45
---

# test_prose_budget.py

Prose budget: the always-loaded instructions may not grow unnoticed. Agents skip long rules; a lesson
that must hold belongs in a check (`tw.py learn record --check-pattern`), not in more prose. Raise a
ceiling only on purpose, after trimming elsewhere.

## Contracts

### Classes
- `ProseBudgetTest` (methods: test_always_loaded_prose_stays_within_budget, test_role_mutations_are_capped)

### Functions
- `words(pattern)`

## Dependencies
### Upstream
- [[skills-team-scripts-omniscience]]
- [[tests-isolate_home]]
### Downstream
- None
