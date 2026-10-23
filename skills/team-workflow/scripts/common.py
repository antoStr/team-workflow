"""Helpers shared by the team-workflow scripts (standard library only)."""
import json
import os
import re
import subprocess
import sys
import tempfile

MEMORY_DIR = "docs/memory"


def read_hook_input():
    """The JSON a hook receives on stdin; {} when there is none."""
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def git(root, *args):
    """stdout of a git command, or None when git fails or is missing."""
    try:
        out = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


def is_agy(data):
    """agy (Antigravity) hook payloads use camelCase keys and list the workspace paths."""
    return "conversationId" in data or "workspacePaths" in data


def session_id(data):
    return data.get("session_id") or data.get("conversationId")


def ancestor_dirs(levels=3):
    """Working folders of the parent processes (Linux /proc). agy runs hooks from the plugin
    folder and, in print mode, sends no workspace path: its own folder is the repository."""
    pid, dirs = os.getppid(), []
    for _ in range(levels):
        try:
            dirs.append(os.readlink(f"/proc/{pid}/cwd"))
            with open(f"/proc/{pid}/stat", encoding="utf-8") as f:
                pid = int(f.read().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            break
    return dirs


def repo_root(data):
    """Claude Code: the session's folder. agy: its workspaces, else the folder of the agy
    process that runs the hook. None outside a git repository."""
    if is_agy(data):
        candidates = [*(data.get("workspacePaths") or []), *ancestor_dirs(), os.getcwd()]
    else:
        candidates = [data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()]
    for start in filter(None, candidates):
        out = git(start, "rev-parse", "--show-toplevel")
        if out:
            return out.strip()
    return None


def dirty_paths(root):
    """Paths changed in the working tree, tracked or untracked, relative to the root."""
    out = git(root, "status", "--porcelain", "--untracked-files=all") or ""
    return {line[3:].split(" -> ")[-1].strip('"') for line in out.splitlines() if len(line) > 3}


def snapshot_path(session_id):
    """Where the SessionStart hook leaves the repository state for the Stop hook."""
    safe = re.sub(r"[^A-Za-z0-9_-]", "", str(session_id or "")) or "default"
    return os.path.join(tempfile.gettempdir(), f"team-workflow-{safe}.json")
