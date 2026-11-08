---
id: tests-isolate_home
title: isolate_home.py
layer: tests
tags: [code, py]
aliases: [tests/isolate_home.py, isolate_home.py]
upstream:
downstream:
  - "[[tests-test_addons]]"
  - "[[tests-test_agy]]"
  - "[[tests-test_brain]]"
  - "[[tests-test_codex]]"
  - "[[tests-test_dashboard]]"
  - "[[tests-test_opencode]]"
  - "[[tests-test_pro]]"
  - "[[tests-test_roles]]"
  - "[[tests-test_scripts]]"
  - "[[tests-test_settings]]"
  - "[[tests-test_setup_library_talk]]"
  - "[[tests-test_update]]"
  - "[[tests-test_usage]]"
  - "[[tests-test_worker]]"
files: [tests/isolate_home.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# isolate_home.py

Imported first by every test module: the whole run gets a throwaway home, so no test can
write to the real ~/.claude, ~/.gemini, ~/.config/opencode or ~/.team-workflow. Windows reads
the home from USERPROFILE, not HOME, so both are set.

## Contracts


## Dependencies
### Upstream
- None
### Downstream
- [[tests-test_addons]]
- [[tests-test_agy]]
- [[tests-test_brain]]
- [[tests-test_codex]]
- [[tests-test_dashboard]]
- [[tests-test_opencode]]
- [[tests-test_pro]]
- [[tests-test_roles]]
- [[tests-test_scripts]]
- [[tests-test_settings]]
- [[tests-test_setup_library_talk]]
- [[tests-test_update]]
- [[tests-test_usage]]
- [[tests-test_worker]]
- None
