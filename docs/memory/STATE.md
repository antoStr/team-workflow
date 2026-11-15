# Project state

## Current version: v2.4.1 (released)

### v2.4.1 (released): fixes from live team runs on Claude Code, Codex and agy
A 3-agent run (2 haiku builders, 1 sonnet reviewer, team talk in review mode) showed:
- **Team talk is a group conversation for real**: `talk.for_role` no longer hides `--to X`
  messages from the others; the orchestrator and newcomers read every message (2.4.0 hid
  questions and challenges between agents). `to` only says who must answer.
- **Claude models**: `pricing.json` aliases are only `fable`, `opus`, `sonnet`, `haiku`, mapped to
  `claude-fable-5-2`, `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5` with the
  2026-11-15 prices; the gpt-4o, gemini-2.0 and claude-3 entries that `options --app claude`
  listed as native models are gone. Haiku 5.5 takes an effort.
- **Per-launch effort**: `options`, `runs_as` and `WIZARD.md` say the Agent tool's `model` and
  `effort` override the agent file for one launch (no worker needed); the wizard explains how to
  check the model and effort a subagent really ran from its transcript.
- **Hardware**: `settings.hardware_status()` returns the data and its age; `tw.py hardware` and
  doctor report telemetry older than 60 s as stale (guard not running) instead of a CRITICAL.
- **Smoke**: a process still running at the timeout prints "still running" instead of the kill's
  exit code.
- `team-talk` include: talk messages in English. `WIZARD.md` step 5: the usage dashboard needs
  the folder the app was started in.
- **auto_update** (off by default): at session start, every agy invocation and every `/team`
  prompt, a newer tag starts `update_plugin.py --harness all` detached (lock 15 min, log
  `~/.team-workflow/update.log`), with no model.
- Same test in **Codex** and **agy** (smart orchestrator, two fast agents):
  - talk: when `.git` is read-only (Codex sandbox) the channel moves with its messages to
    `<worktree>/.team-workflow/talk/` (git-ignored); TALK.md forbids posting as another role.
  - agy agent files use agy's tool names (`read_file`, `edit_file`, `write_file`,
    `run_command`, `manage_task`, `search_web`), list them all for roles with every tool (an
    omitted `tools` is agy's read-only default) and carry `subagent: true`, `mainAgent: false`.
  - agy tiers include `flash_lite`; `invoke_subagent`'s `Model` sets the tier per launch. In an
    unattended agy run use native subagents: workers need to leave agy's sandbox.
  - Codex: `spawn_agent` changes the model, not the effort (the `.toml`'s); report the effort the
    rollout shows. `tw.py models --app X` lists only that app. `scan` counts new files and tells
    unittest from pytest.

### v2.4.0 (released)
- **English first**: `README.md`, `docs/AGENTS.md`, `docs/REFERENCE.md`, `docs/CATALOG.md` and
  `ALPHA_TESTING.md` are English; the Italian copies are `*.it.md`. `tools/readme_catalog.py`
  writes both catalogs (English text from the role and entry descriptions, Italian from
  `docs/catalog.it.json`); the tests check both.
- **Language rule** in `skills/team/SKILL.md` (now English): reply in the user's language,
  English when unclear; briefs to agents in English; repository files keep the project's language.
- **Runtime strings in English**: `tw.py hardware`, `scan.py`, `brain.py` rollover template,
  `autolearn.py` table, `tools/*guard.ps1`, `tools/remote_dashboard.py`. The dashboard keeps its
  `it` locale (chosen by `LANG`).
- **Project management**: agent pack `pm` (`skills/team/roles/pm/`: project-manager,
  project-scheduler, project-controller, risk-manager, stakeholder-manager, agile-coach) and
  library pack `project-management` (pm-lifecycle, pm-scope-wbs, pm-schedule, pm-control, pm-risk,
  pm-stakeholders, pm-procurement, pm-agile). Calculators `skills/team/library/pm-schedule/scripts/cpm.py` (CPM, PERT,
  Mermaid Gantt) and `skills/team/library/pm-control/scripts/evm.py` (earned value), tested in
  `tests/test_pm.py`.
  Content is original, written from public standards (ISO 21502, Scrum Guide, Agile Manifesto).
- **Fixes**: CI matrix 3.9 -> 3.10/3.15 (3.9 no longer exists on ubuntu-latest = 26.04),
  `fail-fast: false`, actions on Node 24 (checkout@v5, setup-python@v6, action-gh-release@v3);
  hard-coded trycloudflare URL removed; `tw.py hardware --start` finds the guard in the plugin,
  not in the current project; `verify-docs` reports a catalog check that could not run instead
  of skipping it; docs use the `/team:` namespace and `skills/team/` paths.
- **Name `team` everywhere**: marketplace and plugin are `team` (install `team@team`);
  `update_plugin.claude_ids` keeps updating old `team-workflow@team-workflow` installs.
- **Hardware files** (status, mode, alerts, log) live in `~/.team-workflow/hardware`
  (`settings.hardware_dir()`), shared by the guards, `tw.py hardware`, doctor and dashboard.
- **Hardening**: workflows with least-privilege `permissions`, actions pinned to commit SHAs,
  `persist-credentials: false`, timeouts; `.github/dependabot.yml`; `SECURITY.md`.
- Totals: **137 agents**, **533 library entries** (417 skills, 94 commands, 22 rule sets).

### v2.3.0 (released)
- `tw.py preview` (dev server start/status/stop), `tw.py patch` (atomic unified diffs,
  `--dry-run`), `tw.py component list|add`, `tw.py visual-check`, `tw.py talk close`.
- `frontend-components` library pack (13 skills) and the `design-engineer` role.
- `tw.py scan` at every `/team` call, `tw.py verify-docs [--strict]` as documentation gate,
  zero-ghosting rule, dynamic agent choice (`tw.py agents catalog`, no 4-choice cap).

### Verify
- `python -m unittest discover -s tests` (Python 3.10+).
- `python tools/readme_catalog.py --check`, `python skills/team/scripts/tw.py verify-docs --strict`.
- `python skills/team/scripts/memcheck.py --root . --strict`, `tw.py brain check --strict`.

### Where to resume
- Release the unreleased work as v2.4.0 (version in `.claude-plugin/plugin.json` and
  `plugin.json`, tag `v2.4.0`) once CI is green on GitHub.
- `main` is protected on GitHub: changes go through a pull request with green `test` checks.
