# Project state

## Current version: v2.5.1 (released)

### v2.5.1
- Setup gate: a `claude -p "/team ..."` test showed Sonnet and Haiku skipping the setup, and under
  load the hooks timed out (SessionStart ~12 s, PreToolUse:Agent 13-17 s, limit 10 s), so Claude
  Code dropped them and let the agents start. Fixes:
  - `hooks/hooks.json`: `session_start.py` and `setup_gate.py` timeouts 10 -> 30 s.
  - `setup_gate.py` imports in 0.02 s (was 0.9 s): lazy `shutil`/`tempfile` in `common.py`,
    `tw_cmd` inlined; a crash prints to stderr.
  - The gate asks for the groups the last `tw.py questions --task` printed
    (`settings.save_setup_headers`, `~/.team-workflow/setup/`): no endless deny without a "Skills"
    group, no stale "Skills i/N" after a second run.
  - "defaults" opts out only as the whole answer; "skip setup" anywhere. Malformed transcript
    lines no longer crash the hook (`tests/test_setup_gate.py`, 5 new tests).
- Retested with Sonnet and Haiku (also two sessions at once): no team agent without the setup;
  with "skip setup" both launch code-reviewer and tester.

### Released highlights (full notes in git tags / GitHub Releases)
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
- `python -m unittest discover -s tests` (Python 3.10+).
- `python tools/readme_catalog.py --check`, `python skills/team/scripts/tw.py verify-docs --strict`.
- `python skills/team/scripts/memcheck.py --root . --strict`, `tw.py brain check --strict`.

### Where to resume
- `v2.5.1` is released; next work starts from `main`. The setup gate is tested headless
  (`claude -p`); the interactive AskUserQuestion path is covered by unit tests only.
- `main` is protected on GitHub (`main protection` ruleset: PR + green `test` checks).
