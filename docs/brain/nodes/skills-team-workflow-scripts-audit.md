---
id: skills-team-workflow-scripts-audit
title: audit.py
layer: skills
tags: [code, py]
aliases: [skills/team-workflow/scripts/audit.py, audit.py]
upstream:
  - "[[skills-team-workflow-scripts-settings]]"
downstream:
  - "[[skills-team-workflow-scripts-doctor]]"
  - "[[skills-team-workflow-scripts-tw]]"
  - "[[tests-test_pro]]"
files: [skills/team-workflow/scripts/audit.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# audit.py

Security audit of the AI agent setup, local and free: Claude Code and agy settings,
permissions, hooks, MCP servers, instruction files, agents and skills of the user and of the
repository.

Findings: {"severity", "file", "what", "fix"}; severities: critical, high, medium, low.
Custom rules (your own policy pack): ~/.team-workflow/audit-rules.json and
<repository>/.team-workflow-audit.json, a list of
    {"id": "no-prod-urls", "severity": "high", "pattern": "prod\\.example\\.com",
     "files": ["*.md", "*.json"], "message": "production host in agent config", "fix": "..."}

## Contracts


### Functions
- `finding(severity, path, what, fix)`
- `read(path, limit)`
- `load_json(path)`
- `mask(value)`
- `scan_text(path, text, instructions)`
- `scan_command(path, where, command)`
- `plain_secrets(path, where, table)`
- `scan_settings(path)`
- `plain_remote_http(url)`
- `scan_mcp(path, servers)`
- `targets(root)`
- `custom_rules(root)`
- `from_imported(path, text)`
- `audit(root)`
- `main()`
- ... and 1 more functions

## Dependencies
### Upstream
- [[skills-team-workflow-scripts-settings]]
- None
### Downstream
- [[skills-team-workflow-scripts-doctor]]
- [[skills-team-workflow-scripts-tw]]
- [[tests-test_pro]]
- None
