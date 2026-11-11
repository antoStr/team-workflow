---
id: skills-team-scripts-usage
title: usage.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/usage.py, usage.py]
upstream:
downstream:
  - "[[tests-test_dashboard]]"
  - "[[tests-test_opencode]]"
  - "[[tests-test_usage]]"
files: [skills/team/scripts/usage.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# usage.py

Token usage and cost: Claude Code transcripts, the worker ledger and the price table.

Standard library only; shared by estimate.py, run_worker.py and dashboard.py.

## Contracts


### Functions
- `load_pricing(path)`
- `resolve_model(name, pricing)`
- `cost_usd(usage, model, pricing)`
- `total_tokens(usage)`
- `project_slug(root)`
- `claude_project_dir(root, home)`
- `ledger_path(root, home)`
- `read_jsonl(path)`
- `transcript_usage(path, sidechain)`
- `_rows(path, session, agent, description, sidechain)`
- `claude_runs(root, since, home)`
- `ledger_runs(root, since, home)`
- `opencode_db(home)`
- `opencode_runs(root, since, home)`
- `all_runs(root, days, home)`

## Dependencies
### Upstream
- None
### Downstream
- [[tests-test_dashboard]]
- [[tests-test_opencode]]
- [[tests-test_usage]]
