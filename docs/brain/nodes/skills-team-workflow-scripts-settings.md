---
id: skills-team-workflow-scripts-settings
title: settings.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/settings.py, settings.py]
upstream:
downstream:
  - "[[skills-team-workflow-scripts-addons]]"
  - "[[skills-team-workflow-scripts-audit]]"
  - "[[skills-team-workflow-scripts-dashboard]]"
  - "[[skills-team-workflow-scripts-doctor]]"
  - "[[skills-team-workflow-scripts-library]]"
  - "[[skills-team-workflow-scripts-roles]]"
  - "[[skills-team-workflow-scripts-session_start]]"
  - "[[skills-team-workflow-scripts-stop_check]]"
  - "[[skills-team-workflow-scripts-talk]]"
  - "[[skills-team-workflow-scripts-tw]]"
  - "[[tests-test_addons]]"
  - "[[tests-test_brain]]"
  - "[[tests-test_opencode]]"
  - "[[tests-test_pro]]"
  - "[[tests-test_roles]]"
  - "[[tests-test_settings]]"
  - "[[tests-test_setup_library_talk]]"
files: [skills/team-workflow/scripts/settings.py]
status: active
last_updated: 2026-11-08T16:54:25
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
- [[skills-team-workflow-scripts-addons]]
- [[skills-team-workflow-scripts-audit]]
- [[skills-team-workflow-scripts-dashboard]]
- [[skills-team-workflow-scripts-doctor]]
- [[skills-team-workflow-scripts-library]]
- [[skills-team-workflow-scripts-roles]]
- [[skills-team-workflow-scripts-session_start]]
- [[skills-team-workflow-scripts-stop_check]]
- [[skills-team-workflow-scripts-talk]]
- [[skills-team-workflow-scripts-tw]]
- [[tests-test_addons]]
- [[tests-test_brain]]
- [[tests-test_opencode]]
- [[tests-test_pro]]
- [[tests-test_roles]]
- [[tests-test_settings]]
- [[tests-test_setup_library_talk]]
- None
