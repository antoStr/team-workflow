---
id: skills-team-scripts-roles
title: roles.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/roles.py, roles.py]
upstream:
  - "[[skills-team-scripts-settings]]"
downstream:
  - "[[skills-team-scripts-dashboard]]"
  - "[[skills-team-scripts-doctor]]"
  - "[[skills-team-scripts-install_agy]]"
  - "[[skills-team-scripts-install_codex]]"
  - "[[skills-team-scripts-install_opencode]]"
  - "[[skills-team-scripts-run_worker]]"
  - "[[skills-team-scripts-scan]]"
  - "[[skills-team-scripts-session_start]]"
  - "[[skills-team-scripts-tw]]"
  - "[[tests-test_codex]]"
  - "[[tests-test_opencode]]"
  - "[[tests-test_pro]]"
  - "[[tests-test_roles]]"
  - "[[tests-test_scan_verify_catalog]]"
  - "[[tests-test_setup_library_talk]]"
  - "[[tools-readme_catalog]]"
files: [skills/team/scripts/roles.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# roles.py

Roles: the agents team-workflow can launch, grouped in packs, and the native agent files each
app loads, written from the settings (type, model and effort per role and per app).

Sources, later ones win for the same role name:
    <plugin>/skills/team-workflow/roles/<pack>/<role>.md   core and the optional packs
    <plugin>/skills/team-workflow/roles/languages/<lang>.md one pack per language: with the
        _reviewer.md and _build-fixer.md templates it gives <lang>-reviewer, <lang>-build-fixer
    ~/.team-workflow/agents/<role>.md                        your own roles or overrides
    <repository>/.team-workflow/agents/<role>.md             roles for one project

Shared blocks in roles/_shared/<name>.md are appended to the body of a role: team-talk and
untrusted-input to every role, the others when the role's frontmatter lists them in `includes`.
Roles with `source: "imported ..."` come from tools/import_upstream.py (MIT, see library/NOTICE.md).

Native files, written only for enabled roles whose type is "custom" and marked as ours:
    Claude Code  ~/.claude/agents/<role>.md
    agy          ~/.gemini/config/agents/<role>.md   (agy drops a file whose `model` is not
                 inherit, flash or pro, or whose description has an unquoted ": ")
    OpenCode     ~/.config/opencode/agents/<role>.md
    Codex        ~/.codex/agents/<role>.toml, listed in ~/.codex/config.toml (install_codex.py)

## Contracts


### Functions
- `ours(text)`
- `installed_apps()`
- `parse(text)`
- `read(info)`
- `sections(body)`
- `languages()`
- `language_roles()`
- `detect(root)`
- `compose(meta, body)`
- `user_dir()`
- `catalog(root)`
- `load(role, root)`
- `is_enabled(config, role, pack)`
- `plan(config, role, app)`
- `efforts(model)`
- ... and 8 more functions

## Dependencies
### Upstream
- [[skills-team-scripts-settings]]
### Downstream
- [[skills-team-scripts-dashboard]]
- [[skills-team-scripts-doctor]]
- [[skills-team-scripts-install_agy]]
- [[skills-team-scripts-install_codex]]
- [[skills-team-scripts-install_opencode]]
- [[skills-team-scripts-run_worker]]
- [[skills-team-scripts-scan]]
- [[skills-team-scripts-session_start]]
- [[skills-team-scripts-tw]]
- [[tests-test_codex]]
- [[tests-test_opencode]]
- [[tests-test_pro]]
- [[tests-test_roles]]
- [[tests-test_scan_verify_catalog]]
- [[tests-test_setup_library_talk]]
- [[tools-readme_catalog]]
