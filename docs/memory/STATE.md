# Project state

## Current version: v2.5.3 (released)

### v2.5.3
- Stop hook without noise: committed files are dated by their commit (`stop_check.change_times`),
  so a pull no longer asks for a STATE.md that came in the same commit; `_auto_evolve_session` runs
  once per set of changes (one cortex "pass", not one per turn); `brain.map_repo` and the genome skip
  a rewrite that would change only the date (`tests/test_stop_noise.py`).

### v2.5.2 (from the "All Code Is Slop" talk review: checks over prose)
- Setup gate in Code Mode: the transcript logs only some shell calls of a REPL script, so
  `tw.py options`/`questions --task` and the gate record the steps in the setup state
  (`settings.update_setup_state`, asked headers keyed by session id, atomic write).
- Learnings as checks: `tw.py learn record --check-pattern REGEX --check-glob GLOB`; PostToolUse
  hook `check_hook.py`, the Stop hook and `tw.py learn check` (CI) enforce them; checked learnings
  are no longer prose vaccines. Checks skip docs/brain, docs/memory, files over 1 MB and binaries.
- Prose budget test; `mutate_role_agent` keeps 10 lessons; ruff (pyflakes) in CI.
- Untested live: AskUserQuestion inside a Code Mode script (unit tests only).

### Released highlights (full notes in git tags / GitHub Releases)
- **v2.5.1**: setup gate holds team agents under load: hook timeouts 10 -> 30 s, lazy imports, the
  gate follows the groups `tw.py questions --task` printed; "skip setup" anywhere, "defaults" alone.
- **v2.5.0**: Cortex v3 (`cortex.py`, `omniscience.py`): neural routing, vibecode booster
  (`roles/_shared/vibecode-booster.md`), `sense`, `spec`, `shield`, `contracts`, `circuit`,
  `mutate`; hooked into `scan.py`, `questions.py`, the hooks and `addons.py` (`vibecoding`).
- **v2.4.7**: `setup_gate.py`, PreToolUse hook on `Agent|Task`, holds team roles until the setup
  ran; off with `TEAM_WORKFLOW_SETUP_GATE=0` or `session_wizard=false`.
- **v2.4.6**: `SKILL.md` section 2: the session setup is a numbered, mandatory step before any
  agent; roles or models named in the request pre-fill the answers, never skip them.
- **v2.4.5**: the SessionStart hook gives the model a runnable `tw.py` (absolute paths).
- **v2.4.4**: imperative setup line in every app; `update_plugin` `safe_rmtree` on Windows.
- **v2.4.3**: Windows hook wrapper `hooks/run-py.cmd`; `talk` verdict and `join` checks.
- **v2.4.0-2.4.2**: English-first docs + `*.it.md`; `pm` packs (137 agents, 533 library
  entries); `auto_update`; Claude 5.5 aliases; OpenCode/Codex `payload_dir()` updates.
- **v2.3.0**: `preview`, `patch`, `component`, `visual-check`, `scan`, `verify-docs`.

### Verify
- `python -m unittest discover -s tests` (Python 3.10+); `python -m ruff check .`.
- `python tools/readme_catalog.py --check`, `python skills/team/scripts/tw.py verify-docs --strict`.
- `python skills/team/scripts/memcheck.py --root . --strict`, `tw.py brain check --strict`.

### Where to resume
- `v2.5.3` is released; next work starts from `main`. Check live: the setup in a Code Mode session.
- `main` is protected on GitHub (`main protection` ruleset: PR + green `test` checks).
