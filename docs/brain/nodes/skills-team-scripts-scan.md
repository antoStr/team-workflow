---
id: skills-team-scripts-scan
title: scan.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/scan.py, scan.py]
upstream:
  - "[[skills-team-scripts-brain]]"
  - "[[skills-team-scripts-roles]]"
  - "[[skills-team-scripts-settings]]"
downstream:
  - "[[tests-test_scan_verify_catalog]]"
files: [skills/team/scripts/scan.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# scan.py

Repository scanner and stack profiler for team-workflow.

Analyzes repository structure, git status, detected languages, frameworks,
frontend UI components stack, and project documentation/memory health.

## Contracts


### Functions
- `repo_root()`
- `git_info(root)`
- `detect_stack(root)`
- `check_docs_memory(root)`
- `scan_repository(root)`
- `print_scan_report(report)`
- `main(argv)`

## Dependencies
### Upstream
- [[skills-team-scripts-brain]]
- [[skills-team-scripts-roles]]
- [[skills-team-scripts-settings]]
### Downstream
- [[tests-test_scan_verify_catalog]]
