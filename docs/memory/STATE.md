# Project state

## Current version: v2.3.0 (released) + unreleased work on `main`

### Unreleased (after v2.3.0)
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
- Totals: **137 agents**, **533 library entries** (417 skills, 94 commands, 22 rule sets).

### v2.3.0 (released)
- `tw.py preview` (dev server start/status/stop), `tw.py patch` (atomic unified diffs,
  `--dry-run`), `tw.py component list|add`, `tw.py visual-check`, `tw.py talk close`.
- `frontend-components` library pack (13 skills) and the `design-engineer` role.
- `tw.py scan` at every `/team` call; `tw.py verify-docs [--strict]` as the documentation gate.
- Zero-ghosting rule (answer in-between questions first) and dynamic agent choice
  (`tw.py agents catalog`, no 4-choice cap).

### Verify
- `python -m unittest discover -s tests` (Python 3.10+).
- `python tools/readme_catalog.py --check`, `python skills/team/scripts/tw.py verify-docs --strict`.
- `python skills/team/scripts/memcheck.py --root . --strict`, `tw.py brain check --strict`.

### Where to resume
- Release the unreleased work as v2.4.0 (version in `.claude-plugin/plugin.json` and
  `plugin.json`, tag `v2.4.0`) once CI is green on GitHub.
- Open points: plugin name `team` in `plugin.json` vs `team-workflow` in `marketplace.json`;
  `tw.py hardware` writes its JSON files in the current repository root.
