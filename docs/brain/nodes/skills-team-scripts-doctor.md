---
id: skills-team-scripts-doctor
title: doctor.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/doctor.py, doctor.py]
upstream:
  - "[[skills-team-scripts-addons]]"
  - "[[skills-team-scripts-audit]]"
  - "[[skills-team-scripts-library]]"
  - "[[skills-team-scripts-memcheck]]"
  - "[[skills-team-scripts-opencode_cli]]"
  - "[[skills-team-scripts-roles]]"
  - "[[skills-team-scripts-settings]]"
  - "[[skills-team-scripts-update_plugin]]"
downstream:
  - "[[skills-team-scripts-tw]]"
  - "[[tests-test_pro]]"
files: [skills/team/scripts/doctor.py]
status: active
last_updated: 2026-11-11T22:06:53
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
- [[skills-team-scripts-addons]]
- [[skills-team-scripts-audit]]
- [[skills-team-scripts-library]]
- [[skills-team-scripts-memcheck]]
- [[skills-team-scripts-opencode_cli]]
- [[skills-team-scripts-roles]]
- [[skills-team-scripts-settings]]
- [[skills-team-scripts-update_plugin]]
### Downstream
- [[skills-team-scripts-tw]]
- [[tests-test_pro]]
