---
id: skills-team-scripts-addons
title: addons.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/addons.py, addons.py]
upstream:
  - "[[skills-team-scripts-settings]]"
downstream:
  - "[[skills-team-scripts-doctor]]"
  - "[[skills-team-scripts-tw]]"
  - "[[tests-test_addons]]"
  - "[[tests-test_codex]]"
  - "[[tests-test_opencode]]"
files: [skills/team/scripts/addons.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# addons.py

Add-on plugins that team-workflow installs, updates and removes in Claude Code and agy.

The catalog lists the known ones; any other GitHub repository with a Claude Code marketplace
(or `plugin@marketplace` already known to Claude Code) can be added too. The chosen add-ons are
kept in the settings (`addons.<name>`), so `update` refreshes them with team-workflow.

How each app installs an add-on:
- Claude Code: its marketplace (`claude plugin marketplace add`, `claude plugin install`);
  "skills" (a repository without a marketplace): its skills copied into ~/.claude/skills.
- agy, "plugin": `agy plugin install <GitHub URL>` (the repository has a plugin.json).
- agy, "skills": agy has no plugin for it, so the repository's skills/<name>/SKILL.md folders
  (or <skills_dir>/<name>/SKILL.md) are copied into ~/.gemini/config/skills (marked, so only ours are ever removed).
- agy, "ecc": an upstream installer, per project (kept for add-ons chosen before 0.9.1).
- OpenCode, "skills": the skills copied into ~/.config/opencode/skills (OpenCode also reads
  ~/.claude/skills and ~/.agents/skills: skills already there are not copied twice).
- OpenCode, "plugin-file": the repository's .opencode/plugins/<name>.mjs, from a local clone,
  listed in the "plugin" array of ~/.config/opencode/opencode.json.
- OpenCode, "ecc": the same upstream installer (kept for add-ons chosen before 0.9.1).
- Codex: the repository's skills copied into ~/.codex/skills, or an MCP server in a block of
  ~/.codex/config.toml (install_codex.py); Codex has no marketplace for these.
- any app, "mcp": an MCP server at user level: `claude mcp add --scope user`, the "mcpServers"
  of ~/.gemini/config/mcp_config.json, the "mcp" table of ~/.config/opencode/opencode.json.
  A server with the same name the user configured is never replaced.

Bundles (`addons add frontend`, `token-saving`, `mcp`, `popular`) add several at once.

## Contracts


### Functions
- `present(app)`
- `codex_kind(entry)`
- `codex_skills_dir()`
- `codex_version(name, entry)`
- `codex_apply(action, name, entry)`
- `opencode_dir()`
- `home()`
- `run()`
- `fetch_json(url)`
- `resolve(spec)`
- `plugin_file_hint(repo)`
- `chosen(config)`
- `claude_skills_dir()`
- `claude_version(entry, name)`
- `claude_markets()`
- ... and 25 more functions

## Dependencies
### Upstream
- [[skills-team-scripts-settings]]
### Downstream
- [[skills-team-scripts-doctor]]
- [[skills-team-scripts-tw]]
- [[tests-test_addons]]
- [[tests-test_codex]]
- [[tests-test_opencode]]
