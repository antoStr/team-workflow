---
id: skills-team-scripts-run_worker
title: run_worker.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/run_worker.py, run_worker.py]
upstream:
  - "[[skills-team-scripts-opencode_cli]]"
  - "[[skills-team-scripts-roles]]"
downstream:
  - "[[tests-test_opencode]]"
files: [skills/team/scripts/run_worker.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# run_worker.py

Run one agent as a separate headless process with an exact model and effort, and record its
token usage in the ledger (~/.team-workflow/ledger/<repository>.jsonl) for the dashboard.

    python3 run_worker.py --harness claude --role tester --model sonnet --effort high         --root . --task "Verify the fix in parser.go" [--allow-edits]

Read-only by default (plan mode). --allow-edits lets the worker change files: only the user
decides that. Tools that need a permission prompt are denied in headless mode.

## Contracts


### Functions
- `role_prompt(role, root)`
- `cli(variable, default)`
- `build_command(harness, model, effort, prompt, allow_edits)`
- `opencode_events(stdout)`
- `normalize(harness, data)`
- `main()`

## Dependencies
### Upstream
- [[skills-team-scripts-opencode_cli]]
- [[skills-team-scripts-roles]]
### Downstream
- [[tests-test_opencode]]
