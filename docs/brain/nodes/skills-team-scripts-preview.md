---
id: skills-team-scripts-preview
title: preview.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/preview.py, preview.py]
upstream:
downstream:
  - "[[tests-test_v230_features]]"
files: [skills/team/scripts/preview.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# preview.py

Project Preview & Dev Server Management.

Automates starting, monitoring, and stopping development preview servers
(Next.js, Vite, static HTML, Python http.server, Django, FastAPI) without
manual port allocation or dangling background processes.

## Contracts


### Functions
- `find_free_port(start_port, max_attempts)`
- `detect_command(root, port)`
- `state_path(root)`
- `start_preview(root, port, cmd, background)`
- `stop_preview(root)`
- `get_status(root)`

## Dependencies
### Upstream
- None
### Downstream
- [[tests-test_v230_features]]
