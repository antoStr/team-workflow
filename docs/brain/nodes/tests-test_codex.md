---
id: tests-test_codex
title: test_codex.py
layer: tests
tags: [code, py]
aliases: [tests/test_codex.py, test_codex.py]
upstream:
  - "[[skills-team-workflow-scripts-addons]]"
  - "[[skills-team-workflow-scripts-install_codex]]"
  - "[[skills-team-workflow-scripts-roles]]"
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_codex.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# test_codex.py

Offline tests for Codex: install, agents in config.toml, MCP servers, uninstall.

## Contracts

### Classes
- `CodexTest` (methods: setUp, conf, read, test_install_writes_skills_agents_config_and_instructions_and_uninstall_removes_them, test_mcp_servers_go_in_our_block_and_the_users_are_left_alone, test_session_start_in_codex_names_its_skills_and_agents, test_roles_table_and_native_text_include_codex)

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-addons]]
- [[skills-team-workflow-scripts-install_codex]]
- [[skills-team-workflow-scripts-roles]]
- [[tests-isolate_home]]
- None
### Downstream
- None
