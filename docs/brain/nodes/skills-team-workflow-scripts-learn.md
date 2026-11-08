---
id: skills-team-workflow-scripts-learn
title: learn.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/learn.py, learn.py]
upstream:
downstream:
  - "[[skills-team-workflow-scripts-tw]]"
  - "[[tests-test_pro]]"
files: [skills/team-workflow/scripts/learn.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# learn.py

Learn a repository's habits from its git history, locally and without limits: hotspots,
bug-prone files, files that change together, commit conventions, tests changed with code, reverts. The orchestrator turns the
facts into memory (Known traps, PLAYBOOKS conventions) or a project skill, with the user's yes.

    python3 learn.py --root . [--max 2000] [--json]

## Contracts


### Functions
- `commits(root, limit)`
- `analyze(root, limit)`
- `report(data)`
- `main()`

## Dependencies
### Upstream
- None
### Downstream
- [[skills-team-workflow-scripts-tw]]
- [[tests-test_pro]]
- None
