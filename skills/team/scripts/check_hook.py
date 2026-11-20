#!/usr/bin/env python3
"""PostToolUse hook (Claude Code, Edit|Write|MultiEdit|NotebookEdit): run the learnings' checks on the
edited file. A match goes back to the model as a block with the required pattern, so a lesson learned
once is enforced every time instead of living as one more line in the prompts. Off with
TEAM_WORKFLOW_CHECKS=0.
"""
import json
import os
import sys

import autolearn
from common import read_hook_input, repo_root, utf8_output


def decide(data):
    """The hook's JSON answer, or None."""
    if os.environ.get("TEAM_WORKFLOW_CHECKS") == "0":
        return None
    tool_input = data.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    root = repo_root(data) if path else None
    if not root:
        return None
    try:
        rel = os.path.relpath(os.path.abspath(os.path.join(root, path)), root)
    except ValueError:  # another drive on Windows: outside the repository
        return None
    if rel.startswith(".."):
        return None
    found = autolearn.check_violations(root, [rel])
    if not found:
        return None
    return {"decision": "block",
            "reason": "team-workflow check failed (a recorded learning, enforced): " + "; ".join(found[:5])
                      + ". Fix the root cause the check names; do not edit or delete the check to pass it."}


def main():
    utf8_output()
    try:
        verdict = decide(read_hook_input())
    except Exception as e:  # noqa: BLE001 - a crash must not block the edit
        print(f"team-workflow check hook: {type(e).__name__}: {e}", file=sys.stderr)
        return
    if verdict:
        print(json.dumps(verdict))


if __name__ == "__main__":
    main()
