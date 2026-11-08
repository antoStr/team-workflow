---
id: tests-test_opencode
title: test_opencode.py
layer: tests
tags: [code, py]
aliases: [tests/test_opencode.py, test_opencode.py]
upstream:
  - "[[skills-team-workflow-scripts-addons]]"
  - "[[skills-team-workflow-scripts-install_opencode]]"
  - "[[skills-team-workflow-scripts-opencode_cli]]"
  - "[[skills-team-workflow-scripts-roles]]"
  - "[[skills-team-workflow-scripts-run_worker]]"
  - "[[skills-team-workflow-scripts-settings]]"
  - "[[skills-team-workflow-scripts-usage]]"
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_opencode.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# test_opencode.py

Offline tests for OpenCode support: agents, installer, plugin, workers, usage, add-ons,
and the options the session wizard offers.

## Contracts

### Classes
- `OpenCodeTest` (methods: setUp, conf, test_roles_become_opencode_subagents, test_installer_for_opencode_2_writes_a_command_folder_and_the_agents_md_block, test_installer_removes_the_old_colon_commands, test_installer_for_opencode_1_writes_the_plugin, test_worker_command_and_usage_from_events, test_usage_reads_the_opencode_store_for_this_repository, opencode2_db, test_usage_and_recent_models_from_the_opencode_2_store, test_catalog_lists_every_provider_with_names_and_variants, test_wizard_options_show_providers_and_the_models_used_most, test_python_command_skips_a_python3_that_does_not_run, test_addons_list_a_plugin_file_in_opencode_json, test_session_wizard_options_and_context)

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-addons]]
- [[skills-team-workflow-scripts-install_opencode]]
- [[skills-team-workflow-scripts-opencode_cli]]
- [[skills-team-workflow-scripts-roles]]
- [[skills-team-workflow-scripts-run_worker]]
- [[skills-team-workflow-scripts-settings]]
- [[skills-team-workflow-scripts-usage]]
- [[tests-isolate_home]]
- None
### Downstream
- None
