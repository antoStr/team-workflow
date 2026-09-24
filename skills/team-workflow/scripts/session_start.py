#!/usr/bin/env python3
"""SessionStart hook: put the project memory in the agent's context.

Prints nothing outside a git repository. In a repository without docs/memory it adds a
one-line hint, so the agent can offer to create it. It also records the repository state
for the Stop hook (stop_check.py).
"""
import json
import os

from common import (MEMORY_DIR, dirty_paths, git, is_agy, read_hook_input, repo_root, session_id,
                    snapshot_path)

MAX_CHARS = 12000  # INDEX + STATE within their limits stay far below this
PROTOCOL = ("team-workflow: follow the team-workflow skill. Read the area card before coding, "
            "give the end-of-task report in the user's language, ask before applying anything "
            "the user did not request, update docs/memory/STATE.md when files change.")


def memory_context(root):
    mem = os.path.join(root, MEMORY_DIR)
    if not os.path.isfile(os.path.join(mem, "INDEX.md")):
        return ("team-workflow: this repository has no docs/memory. If the user starts "
                "development work, offer to create it (/team-workflow:init).")
    parts = [PROTOCOL]
    for name in ("INDEX.md", "STATE.md"):
        path = os.path.join(mem, name)
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as f:
                parts.append(f"--- {MEMORY_DIR}/{name} ---\n{f.read()}")
    text = "\n\n".join(parts)
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n[truncated: memory files are over their limits, run memcheck]"
    return text


def save_snapshot(root, session_id):
    path = snapshot_path(session_id)
    if os.path.exists(path):  # resume or compact: keep the state of the session's start
        return
    head = (git(root, "rev-parse", "HEAD") or "").strip()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"head": head, "dirty": sorted(dirty_paths(root))}, f)


def main():
    data = read_hook_input()
    root = repo_root(data)
    if not root:
        return
    try:
        save_snapshot(root, session_id(data))
    except OSError:
        pass  # the Stop hook then looks at the working tree alone
    if is_agy(data):  # PreInvocation in agy: the memory arrives through the AGENTS.md rules
        print("{}")
        return
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": memory_context(root)}}))


if __name__ == "__main__":
    main()
