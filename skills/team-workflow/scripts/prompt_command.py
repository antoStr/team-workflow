#!/usr/bin/env python3
"""UserPromptSubmit hook (Claude Code): answer /team-workflow:update-plugin, :settings, :models,
:addons, :agents, :profile, :audit, :doctor and :ci-init by running tw.py, and block the prompt so the model never sees it (no tokens spent).
Any other prompt passes through untouched."""
import json
import os
import re
import shlex
import subprocess
import sys

from common import read_hook_input

HERE = os.path.dirname(os.path.abspath(__file__))
COMMANDS = {"update-plugin": "update", "settings": "settings", "models": "models",
            "addons": "addons", "agents": "agents", "profile": "profile", "audit": "audit",
            "doctor": "doctor", "ci-init": "ci-init", "options": "options"}
PATTERN = re.compile(r"\A\s*/team-workflow:(" + "|".join(COMMANDS) + r")(?![\w-])(.*)\Z", re.S)


def tw_args(prompt):
    """tw.py arguments for a prompt that is one of our commands, else None."""
    m = PATTERN.match(prompt or "")
    if not m:
        return None
    try:
        rest = shlex.split(m.group(2))
    except ValueError:
        rest = m.group(2).split()
    return [COMMANDS[m.group(1)], *rest]


def main():
    data = read_hook_input()
    args = tw_args(data.get("prompt"))
    if args is None:
        return
    try:
        out = subprocess.run([sys.executable, os.path.join(HERE, "tw.py"), *args],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=280,
                             cwd=data.get("cwd") or None)
        text = (out.stdout + out.stderr).strip() or "(no output)"
    except (OSError, subprocess.SubprocessError) as e:
        text = f"team-workflow: {e}"
    print(json.dumps({"decision": "block", "reason": text}))


if __name__ == "__main__":
    main()
