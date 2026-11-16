# Project state

## Current version: v2.4.3 (released)

### Unreleased
- `skills/team/scripts/update_plugin.py`: `update_opencode` and `agy_update` now use
  `safe_rmtree` so Windows read-only `.git` pack files do not break OpenCode or Codex updates;
  regression test added in `tests/test_update.py`.
- `docs/memory/STATE.md`: summarized to satisfy `memcheck` size/path rules and updated
  `Where to resume` after `v2.4.3`.

### Released highlights (full notes in git tags / GitHub Releases)
- **v2.4.3** (`e63d0a3`): Windows hook wrapper `hooks/run-py.cmd` (skips Store `python3` alias),
  `talk` challenge verdict & duplicate `join` checks, OpenCode leftover-session note in `WIZARD.md`.
- **v2.4.2**: `update_plugin` uses OpenCode/Codex `payload_dir()` and updates any behind app.
- **v2.4.1**: `talk.for_role` shares all messages; Claude 5.5 aliases; per-launch effort;
  `auto_update`; Codex read-only `.git` fallback; agy tool names & tiers (`flash_lite`).
- **v2.4.0**: English-first docs + `*.it.md`; `pm` & `project-management` packs (137 agents,
  533 library entries); `team` naming everywhere; `~/.team-workflow/hardware`; CI hardening.
- **v2.3.0**: `preview`, `patch`, `component`, `visual-check`, `talk close`, `scan`, `verify-docs`,
  `frontend-components` pack, zero-ghosting & dynamic agent catalog.

### Verify
- `python -m unittest discover -s tests` (Python 3.10+).
- `python tools/readme_catalog.py --check`, `python skills/team/scripts/tw.py verify-docs --strict`.
- `python skills/team/scripts/memcheck.py --root . --strict`, `tw.py brain check --strict`.

### Where to resume
- Release `v2.4.3` is tagged and published on GitHub (`e63d0a3`), and all 4 apps are on `2.4.3`.
- Merge this PR after green `test (3.10)` / `test (3.15)` checks; tag `v2.4.4` when ready to ship
  the `update_plugin.py` Windows `safe_rmtree` fix.
- `main` is protected on GitHub (`main protection` ruleset: PR + green `test` checks).
