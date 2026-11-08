---
id: skills-team-workflow-scripts-memcheck
title: memcheck.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/memcheck.py, memcheck.py]
upstream:
downstream:
  - "[[skills-team-workflow-scripts-dashboard]]"
  - "[[skills-team-workflow-scripts-doctor]]"
files: [skills/team-workflow/scripts/memcheck.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# memcheck.py

Check docs/memory: file sizes, secrets and path references that do not exist.

Size limits and secrets are errors; missing paths are warnings (errors with --strict).
Exit code 1 on errors, so it can run in CI:
    python3 memcheck.py --root . [--strict]

## Contracts


### Functions
- `repo_paths(root)`
- `is_dead(ref, bases, known)`
- `check(root, strict)`
- `main()`

## Dependencies
### Upstream
- None
### Downstream
- [[skills-team-workflow-scripts-dashboard]]
- [[skills-team-workflow-scripts-doctor]]
- None
