#!/usr/bin/env python3
"""Critical path method (CPM) for a project network, with optional three-point (PERT) estimates.

    python3 cpm.py activities.csv [--gantt --start 2026-01-05] [--target 30] [--json]

CSV columns (header required, extra columns are ignored):
    id            unique activity ID (letters, digits, dots, underscores)
    name          optional description
    duration      duration in any one unit (days, weeks...); or leave it empty and give
    optimistic, most_likely, pessimistic   three-point estimate: te = (o + 4m + p) / 6
    predecessors  separated by ';' -- ID, ID+lag, ID-lead, ID:SS, ID:FF+2, ID:SF-1 (FS is default)

Forward and backward pass with FS/SS/FF/SF relations and lags, total and free float, one
critical path; with three-point estimates the standard deviation of the end date along that
path and, with --target, the probability of finishing by it (normal approximation).
Calendar days only: working-day calendars and resource leveling are left to the planner.
"""
import argparse
import csv
import json
import math
import re
import sys
from datetime import datetime, timedelta

EPS = 1e-9
PRED = re.compile(r"^(?P<id>[A-Za-z0-9._]+)(?::(?P<type>(?i:FS|SS|FF|SF)))?(?P<lag>[+-]\d+(?:\.\d+)?)?$")


class ScheduleError(ValueError):
    pass


def number(text, what):
    try:
        return float(text)
    except (TypeError, ValueError):
        raise ScheduleError(f"{what}: not a number: {text!r}")


def parse_predecessors(text):
    preds = []
    for token in (text or "").replace(",", ";").split(";"):
        token = token.strip().replace(" ", "")
        if not token:
            continue
        m = PRED.match(token)
        if not m:
            raise ScheduleError(f"bad predecessor {token!r}: use ID, ID+2, ID:SS, ID:FF-1")
        preds.append((m["id"], (m["type"] or "FS").upper(), float(m["lag"] or 0)))
    return preds


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = [{(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
                for row in csv.DictReader(f)]
    return [r for r in rows if r.get("id")]


def load(rows):
    """Rows (dicts) -> activities {id: {...}} in input order."""
    acts = {}
    for r in rows:
        aid = r["id"]
        if not re.fullmatch(r"[A-Za-z0-9._]+", aid):
            raise ScheduleError(f"activity ID {aid!r}: use letters, digits, dots and underscores")
        if aid in acts:
            raise ScheduleError(f"duplicate activity ID {aid!r}")
        three = [r.get(k, "") for k in ("optimistic", "most_likely", "pessimistic")]
        if r.get("duration", "") != "":
            d, var = number(r["duration"], f"{aid} duration"), 0.0
        elif all(three):
            o, m, p = (number(x, f"{aid} three-point estimate") for x in three)
            if not o <= m <= p:
                raise ScheduleError(f"{aid}: needs optimistic <= most_likely <= pessimistic")
            d, var = (o + 4 * m + p) / 6, ((p - o) / 6) ** 2
        else:
            raise ScheduleError(f"{aid}: give a duration or optimistic, most_likely, pessimistic")
        if d < 0:
            raise ScheduleError(f"{aid}: negative duration")
        acts[aid] = {"id": aid, "name": r.get("name", ""), "duration": d, "variance": var,
                     "preds": parse_predecessors(r.get("predecessors", "")), "succs": []}
    for a in acts.values():
        for pid, kind, lag in a["preds"]:
            if pid not in acts:
                raise ScheduleError(f"{a['id']}: unknown predecessor {pid!r}")
            acts[pid]["succs"].append((a["id"], kind, lag))
    return acts


def topological(acts):
    indegree = {k: len(a["preds"]) for k, a in acts.items()}
    ready = [k for k, n in indegree.items() if n == 0]
    order = []
    while ready:
        k = ready.pop(0)
        order.append(k)
        for s, _, _ in acts[k]["succs"]:
            indegree[s] -= 1
            if indegree[s] == 0:
                ready.append(s)
    if len(order) != len(acts):
        loop = sorted(k for k, n in indegree.items() if n > 0)
        raise ScheduleError(f"the network has a loop through: {', '.join(loop)}")
    return order


def earliest_start(p, kind, lag, d):
    """Earliest start a successor of duration d may have, given predecessor p."""
    return {"FS": p["ef"] + lag, "SS": p["es"] + lag,
            "FF": p["ef"] + lag - d, "SF": p["es"] + lag - d}[kind]


def latest_finish(s, kind, lag, d):
    """Latest finish a predecessor of duration d may have, given successor s."""
    return {"FS": s["ls"] - lag, "SS": s["ls"] - lag + d,
            "FF": s["lf"] - lag, "SF": s["lf"] - lag + d}[kind]


def schedule(acts):
    order = topological(acts)
    for k in order:
        a = acts[k]
        a["es"] = max([0.0] + [earliest_start(acts[p], t, lag, a["duration"]) for p, t, lag in a["preds"]])
        a["ef"] = a["es"] + a["duration"]
    end = max((a["ef"] for a in acts.values()), default=0.0)
    for k in reversed(order):
        a = acts[k]
        a["lf"] = min([end] + [latest_finish(acts[s], t, lag, a["duration"]) for s, t, lag in a["succs"]])
        a["ls"] = a["lf"] - a["duration"]
        a["total_float"] = a["ls"] - a["es"]
        slack = [earliest_start(a, t, lag, acts[s]["duration"]) for s, t, lag in a["succs"]]
        a["free_float"] = min([end - a["ef"]] + [acts[s]["es"] - x for (s, _, _), x in zip(a["succs"], slack)])
        a["critical"] = abs(a["total_float"]) < EPS
    return {"end": end, "order": order, "path": critical_path(acts, end)}


def critical_path(acts, end):
    """One critical path, walked back from a critical activity that ends the project."""
    last = [a for a in acts.values() if a["critical"] and abs(a["ef"] - end) < EPS]
    if not last:
        return []
    path = [max(last, key=lambda a: a["es"])]  # latest start: a final zero-length milestone wins
    while True:
        a = path[-1]
        driving = [acts[p] for p, t, lag in a["preds"] if acts[p]["critical"]
                   and abs(earliest_start(acts[p], t, lag, a["duration"]) - a["es"]) < EPS]
        if not driving:
            return [x["id"] for x in reversed(path)]
        path.append(driving[0])


def summary(acts, result, target=None):
    out = {"duration": result["end"], "critical_path": result["path"]}
    if any(a["variance"] for a in acts.values()):
        sigma = math.sqrt(sum(acts[k]["variance"] for k in result["path"]))
        out["sigma"] = sigma
        if target is not None:
            out["target"] = target
            out["probability"] = (1.0 if target >= result["end"] else 0.0) if sigma == 0 else \
                0.5 * (1 + math.erf((target - result["end"]) / (sigma * math.sqrt(2))))
    return out


def fmt(x):
    return f"{x:.2f}".rstrip("0").rstrip(".") if abs(x - round(x)) > EPS else str(int(round(x)))


def markdown(acts, result, info):
    lines = ["| ID | Name | Dur | ES | EF | LS | LF | TF | FF | Critical |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for k in sorted(result["order"], key=lambda k: (acts[k]["es"], k)):
        a = acts[k]
        lines.append(f"| {k} | {a['name']} | {fmt(a['duration'])} | {fmt(a['es'])} | {fmt(a['ef'])} | "
                     f"{fmt(a['ls'])} | {fmt(a['lf'])} | {fmt(a['total_float'])} | {fmt(a['free_float'])} | "
                     f"{'yes' if a['critical'] else ''} |")
    lines += ["", f"Project duration: {fmt(info['duration'])}",
              f"Critical path: {' -> '.join(info['critical_path'])}"]
    if "sigma" in info:
        lines.append(f"Standard deviation of the end date (along that path): {fmt(info['sigma'])}")
    if "probability" in info:
        lines.append(f"Probability of finishing by {fmt(info['target'])}: {info['probability']:.1%}")
    return "\n".join(lines)


def gantt(acts, result, start):
    """Mermaid Gantt; one unit of duration = one calendar day."""
    base = datetime.strptime(start, "%Y-%m-%d")
    whole = all(abs(acts[k][f] - round(acts[k][f])) < EPS for k in acts for f in ("es", "duration"))
    lines = ["```mermaid", "gantt", "    title Project schedule",
             f"    dateFormat {'YYYY-MM-DD' if whole else 'YYYY-MM-DD HH:mm'}", "    section Activities"]
    for n, k in enumerate(sorted(result["order"], key=lambda k: (acts[k]["es"], k)), 1):
        a = acts[k]
        when = base + timedelta(days=a["es"])
        when = when.strftime("%Y-%m-%d" if whole else "%Y-%m-%d %H:%M")
        size = f"{int(round(a['duration']))}d" if whole else f"{int(round(a['duration'] * 24))}h"
        tags = [t for t, on in (("crit", a["critical"]), ("milestone", a["duration"] == 0)) if on]
        label = (a["name"] or k).replace(":", " ").replace("#", " ")
        lines.append(f"    {label} :{', '.join(tags + [f't{n}', when, size])}")
    return "\n".join(lines + ["```"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Critical path (CPM/PERT) of a project network.")
    ap.add_argument("csv")
    ap.add_argument("--gantt", action="store_true", help="add a Mermaid Gantt chart")
    ap.add_argument("--start", default=datetime.now().strftime("%Y-%m-%d"),
                    help="project start date for the Gantt chart (YYYY-MM-DD)")
    ap.add_argument("--target", type=float, help="target duration: probability of meeting it")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        acts = load(read_csv(args.csv))
        if not acts:
            raise ScheduleError("no activities in the file")
        result = schedule(acts)
    except (OSError, ScheduleError) as e:
        print(f"cpm: {e}", file=sys.stderr)
        return 1
    info = summary(acts, result, args.target)
    if args.json:
        keys = ("name", "duration", "es", "ef", "ls", "lf", "total_float", "free_float", "critical")
        print(json.dumps({"activities": {k: {f: acts[k][f] for f in keys} for k in result["order"]},
                          **info}, indent=2))
        return 0
    print(markdown(acts, result, info))
    if args.gantt:
        print("\n" + gantt(acts, result, args.start))
    return 0


if __name__ == "__main__":
    sys.exit(main())
