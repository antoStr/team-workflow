#!/usr/bin/env python3
"""Run one agent as a separate headless process with an exact model and effort, and record its
token usage in the ledger (~/.team-workflow/ledger/<repository>.jsonl) for the dashboard.

    python3 run_worker.py --harness claude --role tester --model sonnet --effort high \
        --root . --task "Verify the fix in parser.go" [--allow-edits]

Read-only by default (plan mode). --allow-edits lets the worker change files: only the user
decides that. Tools that need a permission prompt are denied in headless mode.
"""
import argparse
import json
import os
import subprocess
import sys
import time

import opencode_cli
import roles
from usage import cost_usd, ledger_path, load_pricing, resolve_model, total_tokens


def role_prompt(role, root=None):
    """System prompt of a role: the body of its role file (plugin, user or project)."""
    try:
        return roles.load(role, root)[1]
    except ValueError as e:
        raise SystemExit(str(e))


def build_command(harness, model, effort, prompt, allow_edits):
    if harness == "opencode":  # read-only through the plan agent; build may edit
        cmd = [opencode_cli.binary() or "opencode", "run", "--format", "json",
               *opencode_cli.model_args(model, effort), "--agent", "build" if allow_edits else "plan"]
        if allow_edits:
            cmd.append("--auto")
        return cmd + [prompt]
    if harness == "claude":
        cmd = [os.environ.get("TEAM_WORKFLOW_CLAUDE_BIN", "claude"), "-p", prompt,
               "--output-format", "json", "--model", model,
               "--permission-mode", "acceptEdits" if allow_edits else "plan"]
    else:
        cmd = [os.environ.get("TEAM_WORKFLOW_AGY_BIN", "agy"), "--output-format", "json",
               "--model", model, "--mode", "accept-edits" if allow_edits else "plan"]
    if effort:
        cmd += ["--effort", effort]
    if harness != "claude":
        cmd.append(f"-p={prompt}")  # agy reads the prompt only when it is attached to the flag
    return cmd


def opencode_events(stdout):
    """OpenCode's --format json prints one event per line."""
    events = []
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    return {"events": events}


def normalize(harness, data):
    """(usage, text, session, reported cost, ok, model) from the CLI's JSON output."""
    if harness == "opencode":
        usage = dict.fromkeys(("input", "cache_write_5m", "cache_write_1h", "cache_read", "output",
                               "calls"), 0)
        texts, cost, session, ok = [], None, "", True
        for e in data.get("events", []):
            part = e.get("part") or {}
            session = session or e.get("sessionID", "")
            if e.get("type") == "text":
                texts.append(part.get("text", ""))
            elif e.get("type") == "step_finish":
                t = part.get("tokens") or {}
                cache = t.get("cache") or {}
                usage["input"] += t.get("input", 0)
                usage["output"] += t.get("output", 0) + t.get("reasoning", 0)
                usage["cache_read"] += cache.get("read", 0)
                usage["cache_write_5m"] += cache.get("write", 0)
                usage["calls"] += 1
                if part.get("cost") is not None:
                    cost = (cost or 0) + part["cost"]
            elif e.get("type") == "error":
                ok = False
                texts.append("error: " + json.dumps(e.get("error", {}))[:500])
        return usage, "\n".join(texts), session, cost, ok and bool(texts), None
    u = data.get("usage") or {}
    if harness == "claude":
        split = u.get("cache_creation") or {}
        w5m, w1h = split.get("ephemeral_5m_input_tokens"), split.get("ephemeral_1h_input_tokens")
        if w5m is None and w1h is None:
            w5m, w1h = u.get("cache_creation_input_tokens", 0), 0
        usage = {"input": u.get("input_tokens", 0), "cache_write_5m": w5m or 0,
                 "cache_write_1h": w1h or 0, "cache_read": u.get("cache_read_input_tokens", 0),
                 "output": u.get("output_tokens", 0), "calls": data.get("num_turns", 1)}
        model = next(iter(data.get("modelUsage") or {}), None)
        return (usage, data.get("result", ""), data.get("session_id", ""),
                data.get("total_cost_usd"), not data.get("is_error"), model)
    usage = {"input": u.get("input_tokens", 0), "cache_write_5m": 0, "cache_write_1h": 0,
             "cache_read": u.get("cache_read_tokens", 0),
             "output": u.get("output_tokens", 0) + u.get("thinking_tokens", 0),
             "calls": data.get("num_turns", 1)}
    return (usage, data.get("response", ""), data.get("conversation_id", ""), None,
            data.get("status") == "SUCCESS", None)


def main():
    ap = argparse.ArgumentParser(description="Run an agent headless and record its token usage.")
    ap.add_argument("--harness", choices=("claude", "agy", "opencode"), required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--model", required=True, help="alias (sonnet, opus...) or model id")
    ap.add_argument("--effort", default="")
    ap.add_argument("--task", default="", help="the assignment; or use --task-file")
    ap.add_argument("--task-file")
    ap.add_argument("--root", default=".")
    ap.add_argument("--allow-edits", action="store_true")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    task = args.task
    if args.task_file:
        with open(args.task_file, encoding="utf-8") as f:
            task = f.read()
    if not task.strip():
        raise SystemExit("an assignment is required (--task or --task-file)")
    prompt = (f"{role_prompt(args.role, args.root)}\n\n## Your assignment\n\n{task.strip()}\n\n"
              "Read docs/memory/INDEX.md first when it exists. "
              "Answer in the language the assignment is written in.")
    root = os.path.abspath(args.root)
    started = time.time()
    proc = subprocess.run(build_command(args.harness, args.model, args.effort, prompt, args.allow_edits),
                          cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=args.timeout,
                          stdin=subprocess.DEVNULL)  # opencode run waits on an open stdin
    try:
        data = opencode_events(proc.stdout) if args.harness == "opencode" else json.loads(proc.stdout)
    except ValueError:
        sys.stdout.write(proc.stdout + proc.stderr)
        raise SystemExit(f"{args.harness} did not return JSON (exit {proc.returncode})")
    usage, text, session, cost, ok, model = normalize(args.harness, data)
    pricing = load_pricing()
    model = model or resolve_model(args.model, pricing)
    if cost is None:
        cost = cost_usd(usage, model, pricing)
    record = {"ts": started, "harness": {"claude": "claude-cli"}.get(args.harness, args.harness),
              "role": args.role, "model": model, "effort": args.effort, "task": task.strip()[:200],
              "usage": usage, "cost_usd": cost, "session": session, "ok": ok,
              "duration_s": round(time.time() - started, 1)}
    path = ledger_path(root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    print(text)
    price = "no price" if cost is None else f"${cost:.2f}"
    print(f"\n[team-workflow] {args.role} on {model} (effort {args.effort or 'default'}): "
          f"{total_tokens(usage):,} tokens, {price}, {record['duration_s']}s", file=sys.stderr)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
