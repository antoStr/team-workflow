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
import sys
from datetime import datetime

import roles
import settings
from common import is_agy, read_hook_input, repo_root, utf8_output

# "skip setup" anywhere; "defaults" only as the whole answer ("defaults", "use defaults"), so a
# request such as "reset the parser to its defaults" keeps the setup.
SKIP = re.compile(r"\bskip setup\b|\A\W*(?:ok,? )?(?:use )?(?:the )?defaults\W*\Z", re.IGNORECASE)
TW = r"tw\.py\"?\s+"
OPTIONS = re.compile(TW + r"options\b")
QUESTIONS = re.compile(TW + r"questions\b")


def entries(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if isinstance(entry, dict):
                    yield entry
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


def setup_missing(headers, printed=None):
    """Printed headers not asked yet: Scope, Preset, every "Roles i/N" and "Skills i/N". `printed` are
    the headers the last `tw.py questions --task` printed (no "Skills" group when it found under 2
    skills); without them the groups are guessed from the asked headers."""
    if printed is not None:
        return sorted({h for h in printed if h in ("Scope", "Preset") or GROUP.match(h)} - headers)
    need = {"Scope", "Preset"}
    for kind in ("Roles", "Skills"):
        totals = {int(m.group(2)) for h in headers for m in [GROUP.match(h)] if m and m.group(1) == kind}
        need |= {f"{kind} {i}/{n}" for n in totals for i in range(1, n + 1)} if totals else {f"{kind} 1/N"}
    return sorted(need - headers)


def epoch(stamp):
    try:
        return datetime.fromisoformat(str(stamp).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def printed_headers(root, since):
    """Headers of the `tw.py questions --task` run that the transcript shows at `since`, or None."""
    if since is None:
        return None
    try:
        with open(settings.setup_state_file(root), encoding="utf-8") as f:
            state = json.load(f)
        if float(state["time"]) >= since - 2:  # written by that run, not by an older one
            return {str(h) for h in state["headers"]}
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return None


def scan(path):
    """(opted out, `options` ran, `questions` ran, headers asked, time of the last `questions --task`)."""
    shown = listed = False
    headers, since = set(), None
    for entry in entries(path):
        if SKIP.search(user_text(entry)):
            return True, shown, listed, headers, since
        message = entry.get("message")
        if entry.get("type") != "assistant" or not isinstance(message, dict):
            continue
        content = message.get("content")
        for block in content if isinstance(content, list) else []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            inp = block.get("input") if isinstance(block.get("input"), dict) else {}
            command = str(inp.get("command", "")) if block.get("name") in ("Bash", "PowerShell") else ""
            shown |= bool(OPTIONS.search(command))
            if QUESTIONS.search(command):
                listed = True
                if "--roles" not in command:
                    since = epoch(entry.get("timestamp"))
            if block.get("name") == "AskUserQuestion":
                qs = inp.get("questions")
                headers |= {str(q.get("header", "")) for q in qs if isinstance(q, dict)} if isinstance(qs, list) else set()
    return False, shown, listed, headers, since


def missing_step(path, role, root=None):
    """None when the setup is done for this role (or the user opted out), else what is missing.
    It checks what was asked, not the order, so a retry asks only the gaps. A question the model
    makes up has none of the printed headers, so it does not count."""
    skipped, shown, listed, headers, since = scan(path)
    if skipped:
        return None
    left = setup_missing(headers, printed_headers(root, since))
    missing = [] if shown else ["show the whole `tw.py options` output to the user"]
    missing += [] if listed else ["run `tw.py questions --app claude --task <words>`"]
    if left:
        missing.append("ask these printed headers, only these: " + ", ".join(left))
    if role[:12] not in headers:
        missing.append(f"ask the model and effort questions of `tw.py questions --app claude --roles {role},...` "
                       f"(header \"{role[:12]}\")")
    return "; ".join(missing) or None


def check_question(path, questions, root):
    """While the setup runs (after `tw.py questions`, before every role and skill group was asked),
    a question must carry a printed header, and model questions wait for the groups: a made-up or
    early question is refused before the user sees it. None lets it through."""
    skipped, _, listed, headers, since = scan(path)
    printed = printed_headers(root, since)
    if skipped or not listed or not setup_missing(headers, printed):
        return None
    role_heads = {r[:12] for r in roles.catalog(root)}
    asked = [str(q.get("header", "")) for q in questions if isinstance(q, dict)] if isinstance(questions, list) else []
    made_up = [h for h in asked if h not in FIXED and not GROUP.match(h) and h not in role_heads]
    if made_up:
        return (f"headers {made_up} are not from `tw.py questions`: ask the printed calls as printed (text may "
                "be translated, headers and options stay)")
    left = setup_missing(headers | set(asked), printed)
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
    missing = missing_step(data["transcript_path"], role, root)
    if not missing:
        return None
    # session_start.tw_cmd, inlined: importing session_start costs about half a second on Windows
    tw = f'"{sys.executable}" "{os.path.join(os.path.dirname(os.path.abspath(__file__)), "tw.py")}"'.replace(os.sep, "/")
    return deny(f"team-workflow: the session setup comes before the first team agent, as in agy. Next: {missing}. "
                "Ask the printed questions themselves, not a summary or a confirmation of your own; the text "
                "may be in the user's language, the headers stay as printed. "
                f"The whole setup: run `{tw} options --app claude` and show its whole output in a code "
                "block (cut by context-mode? save it to a file and read it in parts of 40 lines), then ask "
                f"with AskUserQuestion every call of `{tw} questions --app claude --task <words>` "
                "(scope, preset, every role, library skills, add-ons, team talk), then every call of "
                f"`{tw} questions --app claude --roles <chosen>` (model and effort per role), then the "
                "recap and \"Start\" (WIZARD.md, \"Session setup\"). Roles or models named in the request are "
                "the \"(Recommended)\" answers, not a reason to skip. Without AskUserQuestion, ask in text "
                "and stop. Launch the agents after the user answers.")


def main():
    utf8_output()
    try:
        verdict = decide(read_hook_input())
    except Exception as e:  # noqa: BLE001 - a crash would let the call through without a word
        print(f"team-workflow setup gate: {type(e).__name__}: {e}", file=sys.stderr)
        return
    if verdict:
        print(json.dumps(verdict))


if __name__ == "__main__":
    main()
