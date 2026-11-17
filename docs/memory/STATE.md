# Project state

## Current version: v2.4.4 (released)

### Unreleased
- (none)

### Released highlights (full notes in git tags / GitHub Releases)
- **v2.4.4**: session setup line is imperative in every app (first project reply: `tw.py scan`, then
  `WIZARD.md` by absolute path; repos without memory get a Brain-init question); `update_plugin`
  uses `safe_rmtree` on Windows for OpenCode and Codex updates.
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
- `v2.4.4` ships the wizard parity fix and the `safe_rmtree` fix: merge the PR after green
  `test (3.10)` / `test (3.15)` checks, then tag `v2.4.4` and publish the GitHub Release.
- `main` is protected on GitHub (`main protection` ruleset: PR + green `test` checks).
