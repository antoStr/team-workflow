---
id: skills-team-workflow-scripts-doctor
title: doctor.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/doctor.py, doctor.py]
upstream:
  - "[[skills-team-workflow-scripts-addons]]"
  - "[[skills-team-workflow-scripts-audit]]"
  - "[[skills-team-workflow-scripts-library]]"
  - "[[skills-team-workflow-scripts-memcheck]]"
  - "[[skills-team-workflow-scripts-opencode_cli]]"
  - "[[skills-team-workflow-scripts-roles]]"
  - "[[skills-team-workflow-scripts-settings]]"
  - "[[skills-team-workflow-scripts-update_plugin]]"
downstream:
  - "[[skills-team-workflow-scripts-tw]]"
  - "[[tests-test_pro]]"
files: [skills/team-workflow/scripts/doctor.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# doctor.py

Health check, repair and clean uninstall of team-workflow in Claude Code and agy (the doctor,
repair and uninstall, local and free).

    checks(root)            -> [(status, area, message)]   status: ok, warn, fail
    repair(root)            -> [message]                    what --fix changed
    uninstall(everything)   -> [message]                    remove what team-workflow wrote

## Contracts


### Functions
- `launcher_path()`
- `invalid_settings(path)`
- `opencode_checks(version, newer)`
- `checks(root)`
- `repair(root)`
- `uninstall(everything)`

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-addons]]
- [[skills-team-workflow-scripts-audit]]
- [[skills-team-workflow-scripts-library]]
- [[skills-team-workflow-scripts-memcheck]]
- [[skills-team-workflow-scripts-opencode_cli]]
- [[skills-team-workflow-scripts-roles]]
- [[skills-team-workflow-scripts-settings]]
- [[skills-team-workflow-scripts-update_plugin]]
- None
### Downstream
- [[skills-team-workflow-scripts-tw]]
- [[tests-test_pro]]
- None
