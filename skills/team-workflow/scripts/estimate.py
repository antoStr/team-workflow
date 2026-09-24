#!/usr/bin/env python3
"""Estimate tokens and cost of an agent run before launching it.

With at least two past runs of the same role in this repository (Claude Code transcripts and
the worker ledger) the estimate is their median; otherwise it comes from profiles measured on
real Claude Code subagent runs. It is a range, not a quote.

    python3 estimate.py --role tester --size medium --effort high --models sonnet,opus --root .
"""
import argparse
import json
import os
import statistics

from usage import KEYS, all_runs, cost_usd, load_pricing, resolve_model, total_tokens

# At effort "high": API calls, average context read from cache per call, tokens written to
# cache per call, output per call. Measured on Claude Code subagent runs (14-49 calls, 1-6M
# tokens read from cache, 120-280k written).
PROFILES = {"small": (10, 45_000, 5_000, 400), "medium": (30, 80_000, 5_000, 400),
            "large": (60, 120_000, 5_000, 400)}
EFFORT = {"low": 0.6, "medium": 0.8, "high": 1.0, "xhigh": 1.25, "max": 1.6}
LOW, HIGH = 0.5, 1.6


def file_tokens(paths):
    """About 3.5 bytes per token for source code and prose."""
    size = 0
    for p in paths:
        if os.path.isdir(p):
            size += sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(p) for f in fs)
        elif os.path.isfile(p):
            size += os.path.getsize(p)
    return int(size / 3.5)


def profile_usage(size, effort, extra_tokens=0):
    calls, context, write, out = PROFILES[size]
    k = EFFORT.get(effort, 1.0)
    n = max(1, round(calls * k))
    return {"calls": n, "input": n * 50, "cache_write_5m": 0,
            "cache_write_1h": n * write + extra_tokens,
            "cache_read": n * (context + extra_tokens // 2), "output": round(n * out * k)}


def history_usage(root, role, home=None):
    """Median usage of this role's past runs here, or (None, count) with fewer than two."""
    names = {role, f"team-workflow:{role}"}
    runs = [r for r in all_runs(root, home=home) if r["agent"] in names]
    if len(runs) < 2:
        return None, len(runs)
    return {k: round(statistics.median(r[k] for r in runs)) for k in KEYS}, len(runs)


def estimate(role, size, effort, models, paths=(), root=".", home=None, pricing=None):
    pricing = pricing or load_pricing()
    history, n = history_usage(root, role, home) if role else (None, 0)
    usage = history or profile_usage(size, effort, file_tokens(paths))
    source = f"median of {n} past runs" if history else f"{size} profile, effort {effort}"
    result = []
    for m in models:
        c, tok = cost_usd(usage, m, pricing), total_tokens(usage)
        result.append({"model": m, "model_id": resolve_model(m, pricing), "source": source,
                       "tokens": tok, "tokens_range": [round(tok * LOW), round(tok * HIGH)],
                       "cost": c, "cost_range": None if c is None else [c * LOW, c * HIGH],
                       "usage": usage})
    return result


def human(n):
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}k"


def main():
    ap = argparse.ArgumentParser(description="Estimate tokens and cost of an agent run.")
    ap.add_argument("--role", default="")
    ap.add_argument("--size", choices=sorted(PROFILES), default="medium")
    ap.add_argument("--effort", choices=list(EFFORT), default="high")
    ap.add_argument("--models", default="sonnet", help="comma separated aliases or model ids")
    ap.add_argument("--files", nargs="*", default=[], help="files or folders the agent will read")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = estimate(args.role, args.size, args.effort, args.models.split(","), args.files, args.root)
    if args.json:
        print(json.dumps(rows, indent=2))
        return
    print(f"{args.role or 'agent'}: {rows[0]['source']}")
    for r in rows:
        price = "price n/a" if r["cost"] is None else \
            f"${r['cost']:.2f} (${r['cost_range'][0]:.2f}-{r['cost_range'][1]:.2f})"
        print(f"  {r['model']:8} {r['model_id']:22} ~{human(r['tokens'])} tokens  {price}")


if __name__ == "__main__":
    main()
