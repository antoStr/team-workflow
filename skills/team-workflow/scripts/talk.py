"""Team talk: a channel where the agents of one task talk to each other directly, so they can
debug together, challenge each other's claims and verify each other's work (TALK.md).

A topic is one JSON line per message in <git common dir>/team-workflow/talk/<topic>.jsonl: the
common dir is shared by every worktree of the repository, so agents in separate worktrees see
the same channel, and it is never committed. Outside a repository: ~/.team-workflow/talk/.

Message: {"id", "time", "from", "to" (a role, or null for everyone), "kind", "re" (the id it
answers), "text"}. A question stays open until a reply with re=its id; a challenge stays open
until a verdict with re=its id. `open_threads` is the orchestrator's gate before "done".
"""
import json
import os
import re
import subprocess
import time

import settings

KINDS = ("note", "finding", "question", "answer", "challenge", "fix", "verdict")
REPLIES = ("answer", "fix", "verdict")  # they need --re
CLOSED_BY = {"question": ("answer", "fix", "verdict"), "challenge": ("verdict",)}
TOPIC = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")


def channel_dir(cwd=None):
    try:
        out = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace",
                             timeout=10, cwd=cwd, stdin=subprocess.DEVNULL)
        common = out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        common = ""
    base = os.path.join(common, "team-workflow") if common else settings.home_dir()
    return os.path.join(base, "talk")


def path(topic, cwd=None):
    if not TOPIC.fullmatch(topic or ""):
        raise ValueError("a topic uses lowercase letters, digits and dashes (for example fix-login)")
    return os.path.join(channel_dir(cwd), topic + ".jsonl")


def read(topic, cwd=None):
    try:
        with open(path(topic, cwd), encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except OSError:
        return []


class _Lock:
    """An exclusive lock file, so two agents posting at once never get the same id."""

    def __init__(self, target, timeout=10.0):
        self.path, self.timeout = target + ".lock", timeout

    def __enter__(self):
        end = time.time() + self.timeout
        while True:
            try:
                os.close(os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.path) > 30:  # left by a killed process
                        os.remove(self.path)
                        continue
                except OSError:
                    continue
                if time.time() > end:
                    raise TimeoutError(f"channel busy: {self.path}")
                time.sleep(0.05)

    def __exit__(self, *_):
        try:
            os.remove(self.path)
        except OSError:
            pass


def post(topic, sender, text, kind="note", to=None, re_id=None, cwd=None):
    if kind not in KINDS:
        raise ValueError(f"kind is one of: {', '.join(KINDS)}")
    if kind in REPLIES and not re_id:
        raise ValueError(f"a {kind} answers a message: give --re ID")
    if not (sender and text.strip()):
        raise ValueError("a message needs --from and a text")
    file = path(topic, cwd)
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with _Lock(file):
        msgs = read(topic, cwd)
        if re_id and not any(m["id"] == re_id for m in msgs):
            raise ValueError(f"no message #{re_id} in {topic}")
        msg = {"id": len(msgs) + 1, "time": time.strftime("%Y-%m-%dT%H:%M:%S"), "from": sender,
               "to": to or None, "kind": kind, "re": re_id or None, "text": text.strip()}
        with open(file, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    return msg


def for_role(msgs, role, since=0):
    """Messages after `since` that a role should read: to it or to everyone, not its own."""
    return [m for m in msgs if m["id"] > since and m["from"] != role and m["to"] in (None, role)]


def wait(topic, role, since=0, timeout=120, poll=1.0, cwd=None):
    """Block until a message for the role arrives after `since`, or the timeout; returns them."""
    end = time.time() + timeout
    while True:
        found = for_role(read(topic, cwd), role, since) if role else [
            m for m in read(topic, cwd) if m["id"] > since]
        if found or time.time() >= end:
            return found
        time.sleep(poll)


def open_threads(msgs):
    """Questions without a reply and challenges without a verdict."""
    replies = {}
    for m in msgs:
        if m.get("re"):
            replies.setdefault(m["re"], []).append(m["kind"])
    return [m for m in msgs if m["kind"] in CLOSED_BY
            and not set(replies.get(m["id"], [])) & set(CLOSED_BY[m["kind"]])]


def topics(cwd=None):
    folder = channel_dir(cwd)
    names = sorted(n[:-6] for n in os.listdir(folder) if n.endswith(".jsonl")) if os.path.isdir(folder) else []
    return [(n, read(n, cwd)) for n in names]


def clear(topic, cwd=None):
    try:
        os.remove(path(topic, cwd))
        return True
    except FileNotFoundError:
        return False


def line(m):
    to = f" -> {m['to']}" if m.get("to") else ""
    re_ = f" re #{m['re']}" if m.get("re") else ""
    return f"#{m['id']} {m['time'][11:]} {m['from']}{to} [{m['kind']}]{re_}: {m['text']}"
