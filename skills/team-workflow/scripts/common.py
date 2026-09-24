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
        out = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


def repo_root(data):
    start = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    out = git(start, "rev-parse", "--show-toplevel")
    return out.strip() if out else None


def dirty_paths(root):
    """Paths changed in the working tree, tracked or untracked, relative to the root."""
    out = git(root, "status", "--porcelain", "--untracked-files=all") or ""
    return {line[3:].split(" -> ")[-1].strip('"') for line in out.splitlines() if len(line) > 3}


def snapshot_path(session_id):
    """Where the SessionStart hook leaves the repository state for the Stop hook."""
    safe = re.sub(r"[^A-Za-z0-9_-]", "", str(session_id or "")) or "default"
    return os.path.join(tempfile.gettempdir(), f"team-workflow-{safe}.json")
