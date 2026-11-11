---
id: skills-team-scripts-library
title: library.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/library.py, library.py]
upstream:
  - "[[skills-team-scripts-settings]]"
downstream:
  - "[[skills-team-scripts-doctor]]"
  - "[[skills-team-scripts-session_start]]"
  - "[[skills-team-scripts-tw]]"
  - "[[tests-test_scan_verify_catalog]]"
  - "[[tests-test_setup_library_talk]]"
  - "[[tools-readme_catalog]]"
files: [skills/team/scripts/library.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# library.py

The library: hundreds of skills, commands and coding rules (MIT, see ../library/NOTICE.md),
imported by tools/import_upstream.py into ../library/<id>/MAIN.md with ../library/index.json.

The orchestrator searches it (`tw.py library search <words>`) and gives an agent the path of the
entries its work needs; no app loads them by itself. The entries the user switches on
(settings library.packs.<pack>, library.skills.<id>) are installed as native skills:
    Claude Code  ~/.claude/skills/<id>/SKILL.md
    agy          ~/.gemini/config/skills/<id>/SKILL.md
    OpenCode     ~/.config/opencode/skills/<id>/SKILL.md
    Codex        ~/.codex/skills/<id>/SKILL.md
A folder holds MARK when team-workflow wrote it; any other folder with the same name is left alone.

## Contracts


### Functions
- `index()`
- `entries()`
- `main_file(eid)`
- `search(words, limit)`
- `is_on(config, entry)`
- `wanted(config)`
- `native_dir(app)`
- `installed_hash(folder)`
- `sync(app, config, root, dest, dry_run)`
- `pack_rows(config)`

## Dependencies
### Upstream
- [[skills-team-scripts-settings]]
### Downstream
- [[skills-team-scripts-doctor]]
- [[skills-team-scripts-session_start]]
- [[skills-team-scripts-tw]]
- [[tests-test_scan_verify_catalog]]
- [[tests-test_setup_library_talk]]
- [[tools-readme_catalog]]
