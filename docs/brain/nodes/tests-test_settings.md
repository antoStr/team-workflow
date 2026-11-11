---
id: tests-test_settings
title: test_settings.py
layer: tests
tags: [code, py]
aliases: [tests/test_settings.py, test_settings.py]
upstream:
  - "[[skills-team-scripts-install_agy]]"
  - "[[skills-team-scripts-prompt_command]]"
  - "[[skills-team-scripts-settings]]"
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_settings.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# test_settings.py

Offline tests for the settings, the no-model commands and the agy subagent files.

## Contracts

### Classes
- `SettingsTest` (methods: setUp, test_project_overrides_user_overrides_defaults, test_values_are_typed_and_checked)
- `NoModelCommandTest` (methods: test_only_our_commands_are_intercepted, test_hook_answers_and_blocks_the_prompt, test_stop_check_setting_turns_the_reminder_off, test_session_context_carries_the_settings)
- `FirstSessionTest` (methods: test_first_session_writes_agents_and_asks_for_a_restart)
- `AgySubagentTest` (methods: setUp, test_every_role_becomes_a_valid_agy_agent, test_leaves_a_foreign_agent_alone)
- `RepositoryTest` (methods: read, test_versions_match, test_every_named_command_exists_with_its_name)

## Dependencies
### Upstream
- [[skills-team-scripts-install_agy]]
- [[skills-team-scripts-prompt_command]]
- [[skills-team-scripts-settings]]
- [[tests-isolate_home]]
### Downstream
- None
