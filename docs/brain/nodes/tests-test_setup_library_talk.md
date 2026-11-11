---
id: tests-test_setup_library_talk
title: test_setup_library_talk.py
layer: tests
tags: [code, py]
aliases: [tests/test_setup_library_talk.py, test_setup_library_talk.py]
upstream:
  - "[[skills-team-scripts-library]]"
  - "[[skills-team-scripts-roles]]"
  - "[[skills-team-scripts-settings]]"
  - "[[skills-team-scripts-talk]]"
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_setup_library_talk.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# test_setup_library_talk.py

Offline tests for 0.9: activation (auto or manual), the library and team talk.

## Contracts

### Classes
- `ActivationTest` (methods: context, test_manual_replaces_the_memory_with_one_line_and_stops_the_stop_check, test_setup_shows_every_group_and_where_values_come_from)
- `LibraryTest` (methods: setUp, test_index_is_complete_and_every_entry_has_its_main_file, test_search_ranks_the_matching_entries_first, test_enable_installs_skills_with_requirements_and_disable_removes_only_ours, test_a_pack_turns_its_entries_on_and_a_single_entry_can_override_it)
- `ImportedRolesTest` (methods: test_imported_roles_are_ours_and_carry_the_shared_blocks, test_audit_keeps_eccs_defensive_phrases_low_until_someone_edits_them)
- `ReadmeCatalogTest` (methods: test_readme_lists_every_agent_and_library_entry_of_this_version)
- `TalkTest` (methods: setUp, test_challenge_stays_open_until_the_challenger_gives_a_verdict, test_messages_for_a_role_and_validation, test_each_role_reads_only_what_is_new_for_it, test_group_conversation_join_members_and_the_user, test_post_then_wait_in_one_command, test_wait_returns_on_timeout_without_messages, test_worktrees_share_the_repository_channel)

## Dependencies
### Upstream
- [[skills-team-scripts-library]]
- [[skills-team-scripts-roles]]
- [[skills-team-scripts-settings]]
- [[skills-team-scripts-talk]]
- [[tests-isolate_home]]
### Downstream
- None
