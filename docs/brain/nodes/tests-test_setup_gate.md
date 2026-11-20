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
last_updated: 2026-11-20T11:45:45
---

# test_setup_gate.py

No module docstring.

## Contracts

### Classes
- `SetupGateTest` (methods: gate, test_denies_team_role_after_scan_only, setup, test_allows_after_the_whole_setup, test_translated_text_counts_by_header, test_made_up_question_does_not_count, test_a_retry_asks_only_the_gaps, test_question_check_during_the_setup, test_user_opt_out_and_builtin_agents_pass, printed_setup, test_gate_follows_the_headers_questions_printed, test_no_skills_question_when_none_was_printed, test_code_mode_counts_the_recorded_steps, test_single_quoted_tw_command_counts, test_defaults_inside_a_request_keeps_the_setup, test_malformed_transcript_lines_still_deny, test_session_wizard_off)
- `QuestionsTest` (methods: questions, test_every_enabled_role_is_offered_within_the_tool_limits, test_model_and_effort_for_every_chosen_role)

### Functions
- `user(text)`
- `tool(name)`

## Dependencies
### Upstream
- [[tests-isolate_home]]
### Downstream
- None
