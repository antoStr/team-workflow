---
id: tests-test_roles
title: test_roles.py
layer: tests
tags: [code, py]
aliases: [tests/test_roles.py, test_roles.py]
upstream:
  - "[[skills-team-workflow-scripts-roles]]"
  - "[[skills-team-workflow-scripts-settings]]"
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_roles.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# test_roles.py

Offline tests for the modular roles: packs, overrides and the native files of both apps.

## Contracts

### Classes
- `RolesTest` (methods: setUp, native, test_claude_agents_carry_model_and_only_a_valid_effort, test_settings_switch_type_model_and_packs, test_user_roles_override_and_extend, test_foreign_files_are_left_alone_and_stale_ones_removed, test_language_packs_expand_detect_and_switch_on, test_shared_blocks_are_composed_into_every_role)

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-roles]]
- [[skills-team-workflow-scripts-settings]]
- [[tests-isolate_home]]
- None
### Downstream
- None
