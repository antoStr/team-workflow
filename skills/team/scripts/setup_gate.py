"""PreToolUse hook (Claude Code, Agent and AskUserQuestion): the session setup comes first.

agy follows the session setup from its always-loaded rules; Claude Code skipped it and went from
the scan straight to the agents. This hook denies the launch of a team role until the transcript
shows `tw.py options`, `tw.py questions`, AskUserQuestion calls with all its headers (Scope,
Preset, every "Roles i/N" and "Skills i/N") and the model question of the role being launched
(header = role[:12], from `tw.py questions --roles`), or the user said "defaults" or "skip
setup". During the setup it also refuses a question with a made-up header, or a model question
before every role and skill group, before the user sees it. Headers are checked, not the text,
which may be translated. Built-in agents (Explore, general-purpose...) are never blocked.
"""
import json
import os
import re

import roles
import settings
from common import is_agy, read_hook_input, repo_root, utf8_output
from session_start import tw_cmd

SKIP = re.compile(r"\b(defaults|skip setup)\b", re.IGNORECASE)
TW = r"tw\.py\"?\s+"
OPTIONS = re.compile(TW + r"options\b")
QUESTIONS = re.compile(TW + r"questions\b")


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


GROUP = re.compile(r"(Roles|Skills) \d+/(\d+)$")
FIXED = {"Scope", "Preset", "Add-ons", "Team talk", "Start"}


def setup_missing(headers):
    """Printed headers not asked yet: Scope, Preset, every "Roles i/N" and "Skills i/N"."""
    need = {"Scope", "Preset"}
    for kind in ("Roles", "Skills"):
        totals = {int(m.group(2)) for h in headers for m in [GROUP.match(h)] if m and m.group(1) == kind}
        need |= {f"{kind} {i}/{n}" for n in totals for i in range(1, n + 1)} if totals else {f"{kind} 1/N"}
    return sorted(need - headers)


def scan(path):
    """(opted out, `options` ran, `questions` ran, headers asked) from the transcript."""
    shown = listed = False
    headers = set()
    for entry in entries(path):
        if SKIP.search(user_text(entry)):
            return True, shown, listed, headers
        if entry.get("type") != "assistant":
            continue
        for block in (entry.get("message") or {}).get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            inp = block.get("input") or {}
            command = str(inp.get("command", "")) if block.get("name") in ("Bash", "PowerShell") else ""
            shown |= bool(OPTIONS.search(command))
            listed |= bool(QUESTIONS.search(command))
            if block.get("name") == "AskUserQuestion":
                headers |= {str(q.get("header", "")) for q in inp.get("questions") or []}
    return False, shown, listed, headers


def missing_step(path, role):
    """None when the setup is done for this role (or the user opted out), else what is missing.
    It checks what was asked, not the order, so a retry asks only the gaps. A question the model
    makes up has none of the printed headers, so it does not count."""
    skipped, shown, listed, headers = scan(path)
    if skipped:
        return None
    missing = [] if shown else ["show the whole `tw.py options` output to the user"]
    missing += [] if listed else ["run `tw.py questions --app claude --task <words>`"]
    if setup_missing(headers):
        missing.append("ask these printed headers, only these: " + ", ".join(setup_missing(headers)))
    if role[:12] not in headers:
        missing.append(f"ask the model and effort questions of `tw.py questions --app claude --roles {role},...` "
                       f"(header \"{role[:12]}\")")
    return "; ".join(missing) or None


def check_question(path, questions, root):
    """While the setup runs (after `tw.py questions`, before every role and skill group was asked),
    a question must carry a printed header, and model questions wait for the groups: a made-up or
    early question is refused before the user sees it. None lets it through."""
    skipped, _, listed, headers = scan(path)
    if skipped or not listed or not setup_missing(headers):
        return None
    role_heads = {r[:12] for r in roles.catalog(root)}
    asked = [str(q.get("header", "")) for q in questions or []]
    made_up = [h for h in asked if h not in FIXED and not GROUP.match(h) and h not in role_heads]
    if made_up:
        return (f"headers {made_up} are not from `tw.py questions`: ask the printed calls as printed (text may "
                "be translated, headers and options stay)")
    left = setup_missing(headers | set(asked))
    if any(h in role_heads for h in asked) and left:
        return "model and effort questions come after every group: ask first " + ", ".join(left)
    return None


def deny(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def decide(data):
    """The hook's JSON answer, or None to let the call go."""
    if is_agy(data) or os.environ.get("TEAM_WORKFLOW_SETUP_GATE") == "0" or not data.get("transcript_path"):
        return None
    root = repo_root(data)
    config = settings.load(root)
    if not config.get("session_wizard", True) or config["activation"] == "manual":
        return None
    tool_input = data.get("tool_input") or {}
    if data.get("tool_name") == "AskUserQuestion":
        wrong = check_question(data["transcript_path"], tool_input.get("questions"), root)
        return deny(f"team-workflow session setup: {wrong}.") if wrong else None
    role = str(tool_input.get("subagent_type") or "").split(":")[-1]
    if role not in roles.catalog(root):
        return None
    missing = missing_step(data["transcript_path"], role)
    if not missing:
        return None
    return deny(f"team-workflow: the session setup comes before the first team agent, as in agy. Next: {missing}. "
                "Ask the printed questions themselves, not a summary or a confirmation of your own; the text "
                "may be in the user's language, the headers stay as printed. "
                f"The whole setup: run `{tw_cmd()} options --app claude` and show its whole output in a code "
                "block (cut by context-mode? save it to a file and read it in parts of 40 lines), then ask "
                f"with AskUserQuestion every call of `{tw_cmd()} questions --app claude --task <words>` "
                "(scope, preset, every role, library skills, add-ons, team talk), then every call of "
                f"`{tw_cmd()} questions --app claude --roles <chosen>` (model and effort per role), then the "
                "recap and \"Start\" (WIZARD.md, \"Session setup\"). Roles or models named in the request are "
                "the \"(Recommended)\" answers, not a reason to skip. Without AskUserQuestion, ask in text "
                "and stop. Launch the agents after the user answers.")


def main():
    utf8_output()
    verdict = decide(read_hook_input())
    if verdict:
        print(json.dumps(verdict))


if __name__ == "__main__":
    main()
