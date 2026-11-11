---
id: skills-team-scripts-memcheck
title: memcheck.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/memcheck.py, memcheck.py]
upstream:
downstream:
  - "[[skills-team-scripts-dashboard]]"
  - "[[skills-team-scripts-doctor]]"
files: [skills/team/scripts/memcheck.py]
status: active
last_updated: 2026-11-11T22:06:53
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
- [[skills-team-scripts-dashboard]]
- [[skills-team-scripts-doctor]]
