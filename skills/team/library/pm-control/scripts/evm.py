#!/usr/bin/env python3
"""Earned value management (EVM) metrics and forecasts.

    python3 evm.py --bac 10000 --pv 5000 --ev 4000 --ac 5000        one cut-off date
    python3 evm.py --bac 10000 periods.csv                          a series (columns: period, pv, ev, ac)
    add --json for machine-readable output

PV, EV and AC are cumulative values at the same cut-off date, in the same currency.
Forecasts: EAC with the work left at budget rate (atypical variance), at the current CPI
(typical variance) and at CPI x SPI (schedule pressure on cost); TCPI to finish on BAC and on
the CPI-based EAC.
"""
import argparse
import csv
import json
import sys


def ratio(a, b):
    return a / b if b else None


def metrics(bac, pv, ev, ac):
    if bac <= 0:
        raise ValueError("BAC must be greater than 0")
    if min(pv, ev, ac) < 0:
        raise ValueError("PV, EV and AC cannot be negative")
    cpi, spi = ratio(ev, ac), ratio(ev, pv)
    left = bac - ev
    m = {"bac": bac, "pv": pv, "ev": ev, "ac": ac,
         "cv": ev - ac, "sv": ev - pv, "cpi": cpi, "spi": spi,
         "percent_complete": ev / bac, "percent_spent": ac / bac, "percent_planned": pv / bac,
         "eac_atypical": ac + left}
    m["eac_cpi"] = ac + left / cpi if cpi else None
    m["eac_cpi_spi"] = ac + left / (cpi * spi) if cpi and spi else None
    for k in ("atypical", "cpi", "cpi_spi"):
        eac = m[f"eac_{k}"]
        m[f"etc_{k}"] = eac - ac if eac is not None else None
    m["vac"] = bac - m["eac_cpi"] if m["eac_cpi"] is not None else None
    m["tcpi_bac"] = ratio(left, bac - ac) if bac - ac > 0 else None
    eac = m["eac_cpi"]
    m["tcpi_eac"] = ratio(left, eac - ac) if eac is not None and eac - ac > 0 else None
    return m


def verdict(m):
    cost = "on budget" if m["cv"] == 0 else ("under budget" if m["cv"] > 0 else "over budget")
    time = "on schedule" if m["sv"] == 0 else ("ahead of schedule" if m["sv"] > 0 else "behind schedule")
    out = [f"{cost} by {abs(m['cv']):,.2f}" if m["cv"] else cost,
           f"{time} by {abs(m['sv']):,.2f} of planned value" if m["sv"] else time]
    if m["tcpi_bac"] is not None and m["tcpi_bac"] > 1.1:
        out.append(f"finishing on BAC needs a CPI of {m['tcpi_bac']:.2f} on the remaining work: "
                   "rarely achievable, plan for the EAC instead")
    elif m["tcpi_bac"] is None and m["ev"] < m["bac"]:
        out.append("the whole budget is already spent before completion")
    return out


def num(x, pct=False):
    if x is None:
        return "n/a"
    return f"{x:.1%}" if pct else (f"{x:.2f}" if abs(x) < 10 else f"{x:,.2f}")


def report(m):
    rows = [("BAC", "budget at completion", m["bac"]), ("PV", "planned value", m["pv"]),
            ("EV", "earned value", m["ev"]), ("AC", "actual cost", m["ac"]),
            ("CV", "cost variance = EV - AC", m["cv"]), ("SV", "schedule variance = EV - PV", m["sv"]),
            ("CPI", "cost performance index = EV / AC", m["cpi"]),
            ("SPI", "schedule performance index = EV / PV", m["spi"]),
            ("EAC", "at budget rate = AC + (BAC - EV)", m["eac_atypical"]),
            ("EAC", "at current CPI = AC + (BAC - EV) / CPI", m["eac_cpi"]),
            ("EAC", "at CPI x SPI = AC + (BAC - EV) / (CPI x SPI)", m["eac_cpi_spi"]),
            ("ETC", "to complete at current CPI = EAC - AC", m["etc_cpi"]),
            ("VAC", "variance at completion = BAC - EAC(CPI)", m["vac"]),
            ("TCPI", "to finish on BAC = (BAC - EV) / (BAC - AC)", m["tcpi_bac"]),
            ("TCPI", "to finish on EAC(CPI) = (BAC - EV) / (EAC - AC)", m["tcpi_eac"])]
    lines = ["| Metric | Meaning | Value |", "|---|---|---|"]
    lines += [f"| {k} | {about} | {num(v)} |" for k, about, v in rows]
    lines += ["", f"Complete {num(m['percent_complete'], True)}, planned {num(m['percent_planned'], True)}, "
                  f"spent {num(m['percent_spent'], True)} of the budget."]
    lines += [f"- {v}" for v in verdict(m)]
    return "\n".join(lines)


def series(path, bac):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = [{(k or "").strip().lower(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]
    out = []
    for i, r in enumerate(rows, 2):
        try:
            out.append((r.get("period") or r.get("date") or str(i - 1),
                        metrics(bac, float(r["pv"]), float(r["ev"]), float(r["ac"]))))
        except (KeyError, ValueError) as e:
            raise ValueError(f"{path} line {i}: needs numeric pv, ev, ac ({e})")
    if not out:
        raise ValueError(f"{path}: no rows")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Earned value metrics and forecasts.")
    ap.add_argument("csv", nargs="?", help="cumulative pv, ev, ac per period")
    ap.add_argument("--bac", type=float, required=True)
    ap.add_argument("--pv", type=float)
    ap.add_argument("--ev", type=float)
    ap.add_argument("--ac", type=float)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.csv:
            data = series(args.csv, args.bac)
        elif None in (args.pv, args.ev, args.ac):
            raise ValueError("give a CSV or all of --pv, --ev and --ac")
        else:
            data = [("now", metrics(args.bac, args.pv, args.ev, args.ac))]
    except (OSError, ValueError) as e:
        print(f"evm: {e}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({p: m for p, m in data}, indent=2))
        return 0
    if len(data) > 1:
        print("| Period | PV | EV | AC | CV | SV | CPI | SPI | EAC (CPI) |\n|---|---|---|---|---|---|---|---|---|")
        for p, m in data:
            print(f"| {p} | {num(m['pv'])} | {num(m['ev'])} | {num(m['ac'])} | {num(m['cv'])} | "
                  f"{num(m['sv'])} | {num(m['cpi'])} | {num(m['spi'])} | {num(m['eac_cpi'])} |")
        print(f"\nLatest period ({data[-1][0]}):\n")
    print(report(data[-1][1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
