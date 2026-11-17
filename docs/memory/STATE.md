# Project state

## Current version: v2.4.7 (released)

### Unreleased
- (none)

### Released highlights (full notes in git tags / GitHub Releases)
- **v2.4.7**: `setup_gate.py`, a Claude Code PreToolUse hook on `Agent|Task`, denies team roles until
  the transcript shows `tw.py options` then `AskUserQuestion` (or the user said "defaults" / "skip
  setup"); tested with Sonnet and Haiku, which skipped the setup with the SKILL.md text alone.
  Off with `TEAM_WORKFLOW_SETUP_GATE=0` or `session_wizard=false`.
- **v2.4.6**: `skills/team/SKILL.md` section 2 makes the session setup a numbered, mandatory step before any
  agent (scan, brain, library, `tw.py options`, questions, recap), the same in every app as agy's
  `rules/AGENTS.md`; roles or models named in the request pre-fill the answers, never skip them.
- **v2.4.5**: the SessionStart hook gives the model a runnable `tw.py` (the Python that runs the hook
  plus the absolute script path), because `tw.py` is on no PATH and the model skipped the scan.
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
- `v2.4.7` is released (`06f57d8`); next work starts from `main`. The setup gate is untested in an
  interactive Claude Code session: check `/team` there first.
- `main` is protected on GitHub (`main protection` ruleset: PR + green `test` checks).

- 2026-11-17: committed team skill/hooks/setup gate/questions.py locally; push to main rejected by repo rules (PR, checks, signed commits). Not pushed.
