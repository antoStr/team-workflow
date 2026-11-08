---
id: skills-team-workflow-scripts-dashboard
title: dashboard.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/dashboard.py, dashboard.py]
upstream:
  - "[[skills-team-workflow-scripts-memcheck]]"
  - "[[skills-team-workflow-scripts-roles]]"
  - "[[skills-team-workflow-scripts-settings]]"
downstream:
  - "[[tests-test_dashboard]]"
files: [skills/team-workflow/scripts/dashboard.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# dashboard.py

Token and cost dashboard of a repository: Claude Code sessions and subagents, plus the
workers launched by run_worker.py (claude -p, agy -p). Terminal tables or a self-contained
HTML page.

    python3 dashboard.py --root . [--days 30] [--session latest] [--html [FILE]] [--open] [--json]

## Contracts


### Functions
- `lang()`
- `aggregate(rows, key)`
- `catalog(root)`
- `build(root, days, session, home, pricing)`
- `fmt_tokens(n)`
- `fmt_cost(g)`
- `render_text(d, L)`
- `render_html(d, L)`
- `main()`

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-memcheck]]
- [[skills-team-workflow-scripts-roles]]
- [[skills-team-workflow-scripts-settings]]
- None
### Downstream
- [[tests-test_dashboard]]
- None
