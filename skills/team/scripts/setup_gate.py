"""PreToolUse hook (Claude Code, tool Agent): no team role starts before the session setup.

agy follows the session setup from its always-loaded rules; Claude Code skipped it and went from
the scan straight to the agents. This hook denies the launch of a team role until the
transcript shows `tw.py options` and an AskUserQuestion call after it, or the user said
"defaults" or "skip setup". Built-in agents (Explore, general-purpose...) are never blocked.
"""
import json
import os
import re

import roles
import settings
from common import is_agy, read_hook_input, repo_root, utf8_output
from session_start import tw_cmd

SKIP = re.compile(r"\b(defaults|skip setup)\b", re.IGNORECASE)
OPTIONS = re.compile(r"tw\.py\"?\s+options\b")


def entries(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    yield json.loads(line)
                except ValueError:
                    continue
    except OSError:
        return


def user_text(entry):
    """Text the user typed: not skill bodies (isMeta), tool results or task notifications."""
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("toolUseResult") is not None:
        return ""
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        content = " ".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    if not isinstance(content, str) or content.lstrip().startswith("<task-notification>"):
        return ""
    return content


def setup_done(path):
    """True when the transcript has `tw.py options` then AskUserQuestion, or the user opted out."""
    shown = False
    for entry in entries(path):
        if SKIP.search(user_text(entry)):
            return True
        if entry.get("type") != "assistant":
            continue
        for block in (entry.get("message") or {}).get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if block.get("name") == "Bash" and OPTIONS.search(str((block.get("input") or {}).get("command", ""))):
                shown = True
            elif block.get("name") == "AskUserQuestion" and shown:
                return True
    return False


def decide(data):
    """The hook's JSON answer, or None to let the launch go."""
    if is_agy(data) or os.environ.get("TEAM_WORKFLOW_SETUP_GATE") == "0":
        return None
    role = str((data.get("tool_input") or {}).get("subagent_type") or "").split(":")[-1]
    root = repo_root(data)
    config = settings.load(root)
    if (not config.get("session_wizard", True) or config["activation"] == "manual"
            or role not in roles.catalog(root) or not data.get("transcript_path")
            or setup_done(data["transcript_path"])):
        return None
    reason = (f"team-workflow: the session setup comes before the first team agent, as in agy. "
              f"Run `{tw_cmd()} options --app claude` and show its whole output in a code block (cut by context-mode? save it "
              "to a file and read it in parts of 40 lines), then ask "
              "with AskUserQuestion (WIZARD.md, \"Session setup\"): where the choices go and the "
              "preset; the roles; model and effort for every chosen role; skills and add-ons; team "
              "talk; the recap and \"Start\". Roles or models named in the request are the "
              "\"(Recommended)\" answers, not a reason to skip. Without AskUserQuestion, ask in "
              "text and stop. Launch the agents after the user answers.")
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def main():
    utf8_output()
    verdict = decide(read_hook_input())
    if verdict:
        print(json.dumps(verdict))


if __name__ == "__main__":
    main()
