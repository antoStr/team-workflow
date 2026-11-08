---
id: skills-team-workflow-scripts-smoke
title: smoke.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/smoke.py, smoke.py]
upstream:
downstream:
  - "[[skills-team-workflow-scripts-tw]]"
  - "[[tests-test_autolearn_gate_smoke]]"
files: [skills/team-workflow/scripts/smoke.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# smoke.py

Smoke-test & Live Run Verifier for applications, games, and servers.

Eliminates the AI hallucination of 'Problem solved!' without actually testing.
Launches the real application process in a monitored environment, checks for boot
crashes, unhandled exceptions, stderr errors, or immediate aborts.

Returns empirical proof of whether an application or game truly boots and runs.

## Contracts


### Functions
- `to_wsl_path(path)`
- `run_smoke(cmd, timeout, cwd, env, wsl)`
- `format_report(result)`

## Dependencies
### Upstream
- None
### Downstream
- [[skills-team-workflow-scripts-tw]]
- [[tests-test_autolearn_gate_smoke]]
- None
