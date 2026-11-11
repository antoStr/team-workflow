---
id: skills-team-scripts-verify_docs
title: verify_docs.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/verify_docs.py, verify_docs.py]
upstream:
  - "[[skills-team-scripts-brain]]"
downstream:
  - "[[tests-test_scan_verify_catalog]]"
files: [skills/team/scripts/verify_docs.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# verify_docs.py

Verify documentation, memory integrity, and workflow execution proofs.

Ensures docs/memory/STATE.md, INDEX.md, and Obsidian Brain graph are in sync
with recent repository changes, preventing unverified or ghosted workflows.

## Contracts


### Functions
- `repo_root()`
- `verify_documentation(root, strict)`
- `print_verify_report(res)`
- `main(argv)`

## Dependencies
### Upstream
- [[skills-team-scripts-brain]]
### Downstream
- [[tests-test_scan_verify_catalog]]
