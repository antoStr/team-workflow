---
id: tests-test_pro
title: test_pro.py
layer: tests
tags: [code, py]
aliases: [tests/test_pro.py, test_pro.py]
upstream:
  - "[[skills-team-scripts-audit]]"
  - "[[skills-team-scripts-doctor]]"
  - "[[skills-team-scripts-learn]]"
  - "[[skills-team-scripts-roles]]"
  - "[[skills-team-scripts-settings]]"
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_pro.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# test_pro.py

Offline tests for the local Pro tools: audit, doctor and uninstall, learn, profiles, ci-init.

## Contracts

### Classes
- `ProTest` (methods: setUp, test_audit_finds_risky_settings_mcp_instructions_and_custom_rules, test_clean_setup_has_no_findings_and_strict_passes, test_audit_mcp_flags_remote_http_lookalikes_and_malformed_urls, test_audit_mcp_allows_loopback_http_and_https, test_uninstall_removes_only_what_team_workflow_wrote, test_doctor_repairs_invalid_settings, test_learn_finds_hotspots_bug_prone_files_and_coupling, test_profiles_apply_and_balanced_restores, test_ci_init_writes_a_pinned_workflow_once, test_agy_update_never_loses_a_plugin, test_shell_hook_is_added_once_and_refreshed)

## Dependencies
### Upstream
- [[skills-team-scripts-audit]]
- [[skills-team-scripts-doctor]]
- [[skills-team-scripts-learn]]
- [[skills-team-scripts-roles]]
- [[skills-team-scripts-settings]]
- [[tests-isolate_home]]
### Downstream
- None
