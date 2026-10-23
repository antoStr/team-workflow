"""Token usage and cost: Claude Code transcripts, the worker ledger and the price table.

Standard library only; shared by estimate.py, run_worker.py and dashboard.py.
"""
import glob
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PRICING_FILE = os.path.join(HERE, "..", "pricing.json")
KEYS = ("input", "cache_write_5m", "cache_write_1h", "cache_read", "output", "calls")


def load_pricing(path=PRICING_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def resolve_model(name, pricing):
    """Alias (fable, opus, sonnet, haiku) or model id -> model id."""
    return pricing.get("aliases", {}).get(name, name)


def cost_usd(usage, model, pricing):
    """Cost of a usage dict in USD, or None when the model has no price in the table."""
    model = resolve_model(model, pricing)
    prices = pricing.get("models", {})
    model = model.split("/", 1)[-1]  # OpenCode ids: provider/model
    p = (prices.get(model) or prices.get(re.sub(r"-\d{8}$", "", model))  # dated ids: -20251001
         or prices.get(re.sub(r"-(high|medium|low|thinking)$", "", model)))  # agy ids
    if not p:
        return None
    inp = p["input"]
    read = p.get("cache_read", inp * 0.1)
    w5m, w1h = (p["cache_write"],) * 2 if "cache_write" in p else (inp * 1.25, inp * 2)
    return (usage.get("input", 0) * inp + usage.get("cache_write_5m", 0) * w5m
            + usage.get("cache_write_1h", 0) * w1h + usage.get("cache_read", 0) * read
            + usage.get("output", 0) * p["output"]) / 1e6


def total_tokens(usage):
    return sum(usage.get(k, 0) for k in KEYS if k != "calls")


def project_slug(root):
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(root))


def claude_project_dir(root, home=None):
    return os.path.join(home or os.path.expanduser("~"), ".claude", "projects", project_slug(root))


def ledger_path(root, home=None):
    return os.path.join(home or os.path.expanduser("~"), ".team-workflow", "ledger",
                        project_slug(root) + ".jsonl")


def read_jsonl(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def transcript_usage(path, sidechain=None):
    """Usage per model of one Claude Code transcript.

    Every content block of an API message repeats that message's usage, so each
    (message id, request id) pair is counted once. sidechain=None counts every record;
    True or False keeps only the records with that isSidechain value.
    """
    seen, per_model, first, last = set(), {}, None, None
    for rec in read_jsonl(path):
        if rec.get("type") != "assistant":
            continue
        if sidechain is not None and bool(rec.get("isSidechain")) != sidechain:
            continue
        msg = rec.get("message") or {}
        key = (msg.get("id"), rec.get("requestId"))
        if key in seen:
            continue
        seen.add(key)
        u = msg.get("usage") or {}
        split = u.get("cache_creation") or {}
        w5m, w1h = split.get("ephemeral_5m_input_tokens"), split.get("ephemeral_1h_input_tokens")
        if w5m is None and w1h is None:
            w5m, w1h = u.get("cache_creation_input_tokens", 0), 0
        row = per_model.setdefault(msg.get("model") or "unknown", dict.fromkeys(KEYS, 0))
        row["input"] += u.get("input_tokens") or 0
        row["cache_write_5m"] += w5m or 0
        row["cache_write_1h"] += w1h or 0
        row["cache_read"] += u.get("cache_read_input_tokens") or 0
        row["output"] += u.get("output_tokens") or 0
        row["calls"] += 1
        first = first or rec.get("timestamp")
        last = rec.get("timestamp") or last
    return per_model, first, last


def _rows(path, session, agent, description, sidechain=None):
    per_model, first, last = transcript_usage(path, sidechain)
    return [dict(usage, harness="claude-code", session=session, agent=agent,
                 description=description, model=model, start=first, end=last)
            for model, usage in per_model.items()
            if usage["calls"] and not model.startswith("<")]


def claude_runs(root, since=None, home=None):
    """One row per (session, agent, model) of this repository in Claude Code."""
    pdir = claude_project_dir(root, home)
    rows = []
    for main in glob.glob(os.path.join(pdir, "*.jsonl")):
        if since and os.path.getmtime(main) < since:
            continue
        session = os.path.basename(main)[:-len(".jsonl")]
        subs = glob.glob(os.path.join(pdir, session, "subagents", "agent-*.jsonl"))
        rows += _rows(main, session, "main", "", sidechain=False)
        if not subs:  # older transcripts keep subagent messages in the main file
            rows += _rows(main, session, "subagent", "", sidechain=True)
        for sub in subs:
            meta = {}
            try:
                with open(sub[:-len(".jsonl")] + ".meta.json", encoding="utf-8") as f:
                    meta = json.load(f)
            except (OSError, ValueError):
                pass
            rows += _rows(sub, session, meta.get("agentType", "subagent"), meta.get("description", ""))
    return rows


def ledger_runs(root, since=None, home=None):
    """Rows of the workers launched by run_worker.py (claude -p, agy -p)."""
    path = ledger_path(root, home)
    if not os.path.exists(path):
        return []
    rows = []
    for rec in read_jsonl(path):
        if since and rec.get("ts", 0) < since:
            continue
        usage = rec.get("usage") or {}
        when = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(rec.get("ts", 0)))  # like transcripts
        rows.append(dict({k: usage.get(k, 0) for k in KEYS}, harness=rec.get("harness", "worker"),
                         session=rec.get("session", ""), agent=rec.get("role", "worker"),
                         description=rec.get("task", "")[:80], model=rec.get("model", ""),
                         start=when, end=when, effort=rec.get("effort"),
                         cost_reported=rec.get("cost_usd")))
    return rows


def opencode_db(home=None):
    return os.path.join(home or os.path.expanduser("~"), ".local", "share", "opencode", "opencode.db")


def opencode_runs(root, since=None, home=None):
    """One row per (session, agent, model) of this repository in OpenCode (its SQLite store)."""
    path = opencode_db(home)
    if not os.path.isfile(path):
        return []
    import sqlite3
    try:
        db = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=2)
        try:
            tables = {r[0] for r in db.execute("select name from sqlite_master where type='table'")}
            if "session_v2" in tables:  # OpenCode 2.x: the message type is a column, the model an object
                sessions = db.execute("select id, parent_id, directory from session_v2").fetchall()
                messages = db.execute("select session_id, time_created, data from session_message "
                                      "where type = 'assistant'").fetchall()
            else:
                sessions = db.execute("select id, parent_id, directory from session").fetchall()
                messages = db.execute("select session_id, time_created, data from message").fetchall()
        finally:
            db.close()
    except sqlite3.Error:
        return []
    root = os.path.abspath(root)
    here = {sid: parent for sid, parent, d in sessions
            if d and (os.path.abspath(d) == root or os.path.abspath(d).startswith(root + os.sep))}
    groups = {}
    for sid, created, raw in messages:
        if sid not in here or (since and created / 1000 < since):
            continue
        try:
            msg = json.loads(raw)
        except ValueError:
            continue
        if msg.get("role", "assistant") != "assistant" or not msg.get("tokens"):
            continue
        t, cache = msg["tokens"], msg["tokens"].get("cache") or {}
        ref = msg.get("model") if isinstance(msg.get("model"), dict) else {}
        model = (f"{msg.get('providerID') or ref.get('providerID', '')}/"
                 f"{msg.get('modelID') or ref.get('id', '')}").strip("/")
        agent = msg.get("agent") or "main"
        if not here[sid] and agent in ("build", "plan"):
            agent = "main"  # the session the user talks to
        key = (here[sid] or sid, sid, agent, model)
        row = groups.setdefault(key, dict(dict.fromkeys(KEYS, 0), cost_reported=0.0, first=created,
                                          last=created))
        row["input"] += t.get("input", 0)
        row["output"] += t.get("output", 0) + t.get("reasoning", 0)
        row["cache_read"] += cache.get("read", 0)
        row["cache_write_5m"] += cache.get("write", 0)
        row["calls"] += 1
        row["cost_reported"] += msg.get("cost") or 0
        row["first"], row["last"] = min(row["first"], created), max(row["last"], created)
    stamp = lambda ms: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ms / 1000))
    return [dict({k: row[k] for k in KEYS}, harness="opencode", session=session, agent=agent,
                 description="", model=model, start=stamp(row["first"]), end=stamp(row["last"]),
                 cost_reported=row["cost_reported"], opencode_session=sid)
            for (session, sid, agent, model), row in groups.items()]


def all_runs(root, days=None, home=None):
    """Claude Code runs plus worker runs, each counted once."""
    since = time.time() - days * 86400 if days else None
    rows = claude_runs(root, since, home)
    workers = ledger_runs(root, since, home)
    roles = {w["session"]: w for w in workers if w["harness"] == "claude-cli" and w["session"]}
    for r in rows:  # a claude -p worker also leaves a transcript: keep it, labelled with its role
        if r["agent"] == "main" and r["session"] in roles:
            r["agent"], r["harness"] = roles[r["session"]]["agent"], "claude-cli"
            r["effort"] = roles[r["session"]].get("effort")
    opencode = opencode_runs(root, since, home)
    worker_sessions = {w["session"]: w for w in workers if w["harness"] == "opencode"}
    for r in opencode:  # an opencode run worker is a session of its own: label it with the role
        w = worker_sessions.get(r["opencode_session"])
        if w:
            r["agent"], r["effort"] = w["agent"], w.get("effort")
    seen = {r["session"] for r in rows} | {r["opencode_session"] for r in opencode}
    return rows + opencode + [w for w in workers if w["harness"] not in ("claude-cli", "opencode")
                              or w["session"] not in seen]
