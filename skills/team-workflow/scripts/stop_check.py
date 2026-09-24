#!/usr/bin/env python3
"""Stop hook: ask for a memory update when files changed after docs/memory/STATE.md.

It looks at the changes of this session (working tree, and commits since SessionStart),
never blocks twice in a row (stop_hook_active) and is off with TEAM_WORKFLOW_STOP_CHECK=0.
"""
import json
import os

from common import MEMORY_DIR, dirty_paths, git, read_hook_input, repo_root, snapshot_path

STATE = f"{MEMORY_DIR}/STATE.md"
REASON = ("team-workflow: files changed after docs/memory/STATE.md was last updated. Before "
          "stopping, update STATE.md (and the area card, MAP.md or DECISIONS.md when they are "
          "affected), then give the end-of-task report in the user's language.")


def changed_this_session(root, snap):
    # ponytail: files already dirty at session start count only once committed; hash them at
    # SessionStart if later edits to them must be caught too.
    changed = dirty_paths(root) - set(snap.get("dirty", []))
    head = snap.get("head")
    if head:
        changed |= set((git(root, "diff", "--name-only", head, "HEAD") or "").splitlines())
    return changed


def newest_mtime(root, paths):
    full = (os.path.join(root, p) for p in paths)
    return max((os.path.getmtime(p) for p in full if os.path.exists(p)), default=0.0)


def decide(data):
    if data.get("stop_hook_active") or os.environ.get("TEAM_WORKFLOW_STOP_CHECK") == "0":
        return None
    root = repo_root(data)
    if not root or not os.path.isfile(os.path.join(root, STATE)):
        return None
    try:
        with open(snapshot_path(data.get("session_id")), encoding="utf-8") as f:
            snap = json.load(f)
    except (OSError, ValueError):
        snap = {}
    changed = changed_this_session(root, snap)
    work = [p for p in changed if not p.startswith(MEMORY_DIR + "/")]
    if not work:
        return None
    if STATE in changed and os.path.getmtime(os.path.join(root, STATE)) >= newest_mtime(root, work):
        return None
    return {"decision": "block", "reason": REASON}


def main():
    verdict = decide(read_hook_input())
    if verdict:
        print(json.dumps(verdict))


if __name__ == "__main__":
    main()
