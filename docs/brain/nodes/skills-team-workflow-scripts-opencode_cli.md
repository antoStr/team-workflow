---
id: skills-team-workflow-scripts-opencode_cli
title: opencode_cli.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/opencode_cli.py, opencode_cli.py]
upstream:
downstream:
  - "[[skills-team-workflow-scripts-doctor]]"
  - "[[skills-team-workflow-scripts-install_opencode]]"
  - "[[skills-team-workflow-scripts-run_worker]]"
  - "[[skills-team-workflow-scripts-session_start]]"
  - "[[skills-team-workflow-scripts-tw]]"
  - "[[tests-test_opencode]]"
files: [skills/team-workflow/scripts/opencode_cli.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# opencode_cli.py

OpenCode, as the scripts see it: where its CLI is, which version, which models the user can
pick (every provider they connected, with the model's name and reasoning variants), the models
they use most, and how a model with a variant is passed to `opencode run`.

OpenCode 2.x (the desktop app ships the CLI as resources/opencode-cli) lists the models with
names and variants through its local server (`opencode api GET /api/model`); 1.x only prints
`provider/model` ids (`opencode models`), and those are what is returned there.

## Contracts


### Functions
- `candidates()`
- `binary()`
- `run()`
- `version()`
- `is_v2(ver)`
- `model_args(model, variant, ver)`
- `api(path, directory)`
- `catalog()`
- `providers(models)`
- `search(models, provider, text)`
- `db_path(home)`
- `state_models(home)`
- `recent(limit, home)`
- `used_most(home)`
- `python_command()`

## Dependencies
### Upstream
- None
### Downstream
- [[skills-team-workflow-scripts-doctor]]
- [[skills-team-workflow-scripts-install_opencode]]
- [[skills-team-workflow-scripts-run_worker]]
- [[skills-team-workflow-scripts-session_start]]
- [[skills-team-workflow-scripts-tw]]
- [[tests-test_opencode]]
- None
