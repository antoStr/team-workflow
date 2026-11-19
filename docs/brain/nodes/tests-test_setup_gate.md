---
id: tests-test_setup_gate
title: test_setup_gate.py
layer: tests
tags: [code, py]
aliases: [tests/test_setup_gate.py, test_setup_gate.py]
upstream:
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_setup_gate.py]
status: active
last_updated: 2026-11-19T11:00:10
---

# test_setup_gate.py

No module docstring.

## Contracts

### Classes
- `SetupGateTest` (methods: gate, test_denies_team_role_after_scan_only, setup, test_allows_after_the_whole_setup, test_translated_text_counts_by_header, test_made_up_question_does_not_count, test_a_retry_asks_only_the_gaps, test_question_check_during_the_setup, test_user_opt_out_and_builtin_agents_pass, test_session_wizard_off)
- `QuestionsTest` (methods: questions, test_every_enabled_role_is_offered_within_the_tool_limits, test_model_and_effort_for_every_chosen_role)

### Functions
- `user(text)`
- `tool(name)`

## Dependencies
### Upstream
- [[tests-isolate_home]]
### Downstream
- None
