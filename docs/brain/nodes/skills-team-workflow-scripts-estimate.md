---
id: skills-team-workflow-scripts-estimate
title: estimate.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/estimate.py, estimate.py]
upstream:
downstream:
  - "[[tests-test_usage]]"
files: [skills/team-workflow/scripts/estimate.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# estimate.py

Estimate tokens and cost of an agent run before launching it.

With at least two past runs of the same role in this repository (Claude Code transcripts and
the worker ledger) the estimate is their median; otherwise it comes from profiles measured on
real Claude Code subagent runs. It is a range, not a quote.

    python3 estimate.py --role tester --size medium --effort high --models sonnet,opus --root .

## Contracts


### Functions
- `file_tokens(paths)`
- `profile_usage(size, effort, extra_tokens)`
- `history_usage(root, role, home)`
- `estimate(role, size, effort, models, paths, root, home, pricing)`
- `human(n)`
- `main()`

## Dependencies
### Upstream
- None
### Downstream
- [[tests-test_usage]]
- None
