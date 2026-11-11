---
id: skills-team-scripts-settings
title: settings.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/settings.py, settings.py]
upstream:
downstream:
  - "[[skills-team-scripts-addons]]"
  - "[[skills-team-scripts-audit]]"
  - "[[skills-team-scripts-dashboard]]"
  - "[[skills-team-scripts-doctor]]"
  - "[[skills-team-scripts-library]]"
  - "[[skills-team-scripts-roles]]"
  - "[[skills-team-scripts-scan]]"
  - "[[skills-team-scripts-session_start]]"
  - "[[skills-team-scripts-stop_check]]"
  - "[[skills-team-scripts-talk]]"
  - "[[skills-team-scripts-tw]]"
  - "[[tests-test_addons]]"
  - "[[tests-test_brain]]"
  - "[[tests-test_opencode]]"
  - "[[tests-test_pro]]"
  - "[[tests-test_roles]]"
  - "[[tests-test_settings]]"
  - "[[tests-test_setup_library_talk]]"
files: [skills/team/scripts/settings.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# settings.py

team-workflow settings: defaults, then ~/.team-workflow/settings.json (every project), then
<repository>/.team-workflow.json (this project only). Read by the hooks, the scripts and the
orchestrator; changed with `tw.py settings set <key> <value>` or by editing the files.

## Contracts


### Functions
- `home_dir()`
- `user_file()`
- `project_file(root)`
- `_read(path)`
- `_merge(base, over)`
- `load(root)`
- `role_value(data, section, role, app)`
- `parse_value(key, text)`
- `save(key, value, root)`
- `default_of(key)`
- `apply_profile(name, root)`
- `flatten(data, prefix)`
- `summary(data)`

## Dependencies
### Upstream
- None
### Downstream
- [[skills-team-scripts-addons]]
- [[skills-team-scripts-audit]]
- [[skills-team-scripts-dashboard]]
- [[skills-team-scripts-doctor]]
- [[skills-team-scripts-library]]
- [[skills-team-scripts-roles]]
- [[skills-team-scripts-scan]]
- [[skills-team-scripts-session_start]]
- [[skills-team-scripts-stop_check]]
- [[skills-team-scripts-talk]]
- [[skills-team-scripts-tw]]
- [[tests-test_addons]]
- [[tests-test_brain]]
- [[tests-test_opencode]]
- [[tests-test_pro]]
- [[tests-test_roles]]
- [[tests-test_settings]]
- [[tests-test_setup_library_talk]]
