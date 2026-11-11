---
id: skills-team-scripts-tw
title: tw.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/tw.py, tw.py]
upstream:
  - "[[skills-team-scripts-addons]]"
  - "[[skills-team-scripts-audit]]"
  - "[[skills-team-scripts-autolearn]]"
  - "[[skills-team-scripts-brain]]"
  - "[[skills-team-scripts-doctor]]"
  - "[[skills-team-scripts-gate]]"
  - "[[skills-team-scripts-learn]]"
  - "[[skills-team-scripts-library]]"
  - "[[skills-team-scripts-opencode_cli]]"
  - "[[skills-team-scripts-roles]]"
  - "[[skills-team-scripts-settings]]"
  - "[[skills-team-scripts-smoke]]"
  - "[[skills-team-scripts-talk]]"
  - "[[skills-team-scripts-update_plugin]]"
downstream:
files: [skills/team/scripts/tw.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# tw.py

team-workflow commands that run without the model, so they spend no tokens.

    tw.py update [--check]                 update the plugin in Claude Code and agy
    tw.py settings                         show every setting and where it comes from
    tw.py settings set KEY VALUE [--project]
    tw.py settings reset KEY [--project]
    tw.py models                           models and efforts each app offers
    tw.py models --app opencode [--provider P] [--search TEXT] [--json]
                                           OpenCode: providers, favorite and recent models, search
    tw.py agents [list]                    roles with pack, on/off, type, model, effort per app
    tw.py agents set ROLE model=M effort=E type=T [--app claude|agy] [--project]
    tw.py agents enable|disable ROLE|PACK  switch a role or a whole pack
    tw.py agents show ROLE                 the full instructions of a role
    tw.py agents new ROLE                  your own role (or an override) to edit
    tw.py agents sync                      rewrite the native agents of both apps
    tw.py addons [list]                    add-on plugins, MCP servers and bundles
    tw.py addons add NAME|owner/repo|plugin@marketplace [--app claude|agy]
    tw.py addons remove NAME
    tw.py addons update [NAME]
    tw.py profile [NAME] [--project]       presets: budget, fast, balanced, thorough, security, research
    tw.py audit [--strict] [--json]        security scan of settings, hooks, MCP, agents, skills
    tw.py doctor [--fix]                   health check and repair of the installation
    tw.py uninstall [--all]                remove what team-workflow wrote outside the plugins
    tw.py learn [--max N] [--json]         habits of this repository from its git history
    tw.py ci-init                          GitHub Actions workflow: memory and audit on every PR
    tw.py agy-update [NAME...]             what `agy plugin update` would be: reinstall from source
    tw.py options [--app A|all] [--json]   models, efforts and roles the session wizard can offer
    tw.py install-opencode [--workspace R] install team-workflow into OpenCode
    tw.py install-cli [--no-shell]         `team-workflow` command, and `agy plugin update` in the shell
    tw.py setup                            everything in one place: activation, wizard, team, talk,
                                           checks, roles, library, add-ons, and how to change them
    tw.py library [list [PACK...]]         the library: packs, or the entries of some packs
    tw.py library search WORDS...          entries for a task, best first, with their path
    tw.py library show ID                  one entry's instructions
    tw.py library enable|disable ID|PACK [--project]   install it as a native skill, or remove it
    tw.py library sync                     rewrite the installed library skills of every app
    tw.py talk [list]                      team talk channels of this repository
    tw.py talk join TOPIC --as ROLE [WHAT I OWN]   take part, then read the whole conversation
    tw.py talk who TOPIC                   who takes part and what each one owns
    tw.py talk post TOPIC --from ROLE [--to ROLE] [--kind K] [--re ID] [--wait SECONDS] TEXT...
    tw.py talk read TOPIC [--for ROLE] [--since ID] [--wait SECONDS]   --for: only unread ones
    tw.py talk open TOPIC [--strict]       open questions and challenges, unread messages per role
    tw.py talk clear TOPIC

In Claude Code, /team-workflow:<command> for update-plugin, settings, models, agents, addons,
profile, audit, doctor, library and talk is answered by a hook that runs this script, with no
tokens. In agy, use its bash mode: !team-workflow <command>.

## Contracts


### Functions
- `output(cmd, timeout)`
- `repo_root()`
- `cmd_settings(args)`
- `cmd_models(args)`
- `opencode_models()`
- `model_line(m)`
- `print_opencode_models(data, provider, text)`
- `cmd_agents(args)`
- `app_options(app, root)`
- `runs_as(app, p, native)`
- `print_options(data)`
- `cmd_options(args)`
- `cmd_profile(args)`
- `cmd_audit(args)`
- `cmd_doctor(args)`
- ... and 25 more functions

## Dependencies
### Upstream
- [[skills-team-scripts-addons]]
- [[skills-team-scripts-audit]]
- [[skills-team-scripts-autolearn]]
- [[skills-team-scripts-brain]]
- [[skills-team-scripts-doctor]]
- [[skills-team-scripts-gate]]
- [[skills-team-scripts-learn]]
- [[skills-team-scripts-library]]
- [[skills-team-scripts-opencode_cli]]
- [[skills-team-scripts-roles]]
- [[skills-team-scripts-settings]]
- [[skills-team-scripts-smoke]]
- [[skills-team-scripts-talk]]
- [[skills-team-scripts-update_plugin]]
### Downstream
- None
