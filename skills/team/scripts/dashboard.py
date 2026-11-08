#!/usr/bin/env python3
"""Token and cost dashboard of a repository: Claude Code sessions and subagents, plus the
workers launched by run_worker.py (claude -p, agy -p). Terminal tables or a self-contained
HTML page.

    python3 dashboard.py --root . [--days 30] [--session latest] [--html [FILE]] [--open] [--json]
"""
import argparse
import html
import json
import os
import time
import webbrowser

import memcheck
import roles
import settings
from usage import KEYS, all_runs, cost_usd, load_pricing, project_slug, total_tokens

HERE = os.path.dirname(os.path.abspath(__file__))
T = {
    "en": dict(title="Team workflow dashboard", period="Period", days="last {} days", all="all time",
               cost="Cost (API rates)", tokens="Tokens", calls="API calls", hit="Read from cache",
               unpriced="Tokens without a price", by_agent="By agent", by_model="By model",
               sessions="Sessions", memory="Project memory", catalog="Agents available",
               agent="Agent", model="Model", effort="Effort", runs="Runs", share="Share",
               session="Session", start="Start", errors="errors", warnings="warnings",
               nodata="No usage recorded for this repository yet.", nomem="No docs/memory here.",
               note="Costs at API list prices; on a subscription they are usage, not a bill."),
    "it": dict(title="Dashboard team workflow", period="Periodo", days="ultimi {} giorni", all="tutto",
               cost="Costo (prezzi API)", tokens="Token", calls="Chiamate API", hit="Letti dalla cache",
               unpriced="Token senza prezzo", by_agent="Per agente", by_model="Per modello",
               sessions="Sessioni", memory="Memoria di progetto", catalog="Agenti disponibili",
               agent="Agente", model="Modello", effort="Effort", runs="Esecuzioni", share="Quota",
               session="Sessione", start="Inizio", errors="errori", warnings="avvisi",
               nodata="Nessun consumo registrato per questo repository.", nomem="Nessuna docs/memory qui.",
               note="Costi a prezzi di listino API; con un abbonamento indicano consumo, non una fattura."),
}


def lang():
    return "it" if os.environ.get("LANG", "").lower().startswith("it") else "en"


def aggregate(rows, key):
    groups = {}
    for r in rows:
        g = groups.setdefault(key(r), dict(dict.fromkeys(KEYS, 0), tokens=0, cost=0.0, runs=0,
                                           unpriced=0, models=set(), start=r.get("start") or ""))
        for k in KEYS:
            g[k] += r.get(k, 0)
        g["tokens"] += r["tokens"]
        g["runs"] += 1
        g["models"].add(r["model"])
        g["start"] = min(filter(None, (g["start"], r.get("start"))), default="")
        if r["cost"] is None:
            g["unpriced"] += r["tokens"]
        else:
            g["cost"] += r["cost"]
    return sorted(groups.items(), key=lambda kv: -kv[1]["tokens"])


def catalog(root=None):
    """(role, Claude Code model, effort) of every enabled role, from the settings."""
    config = settings.load(root)
    rows = []
    for role, info in roles.catalog(root).items():
        if roles.is_enabled(config, role, info["pack"]):
            p = roles.plan(config, role, "claude")
            rows.append((role, p["model"], p["effort"] if roles.efforts(p["model"]) != [] else "-"))
    return rows


def build(root, days=None, session=None, home=None, pricing=None):
    pricing = pricing or load_pricing()
    rows = all_runs(root, days, home)
    if session:
        if session == "latest" and rows:
            session = max(rows, key=lambda r: r.get("start") or "")["session"]
        rows = [r for r in rows if r["session"] == session]
    for r in rows:
        reported = r.get("cost_reported")
        r["cost"] = reported if reported is not None else cost_usd(r, r["model"], pricing)
        r["tokens"] = total_tokens(r)
    total = aggregate(rows, lambda r: "all")
    t = total[0][1] if total else dict(dict.fromkeys(KEYS, 0), tokens=0, cost=0.0, unpriced=0)
    prompt = t["input"] + t["cache_write_5m"] + t["cache_write_1h"] + t["cache_read"]
    errors, warnings = memcheck.check(os.path.abspath(root))
    has_memory = os.path.isdir(os.path.join(root, "docs", "memory"))
    return {"root": os.path.abspath(root), "days": days, "session": session, "rows": rows,
            "total": t, "hit": t["cache_read"] / prompt if prompt else 0.0,
            "by_agent": aggregate(rows, lambda r: r["agent"]),
            "by_model": aggregate(rows, lambda r: r["model"]),
            "sessions": sorted(aggregate(rows, lambda r: r["session"]), key=lambda kv: kv[1]["start"],
                               reverse=True)[:15],
            "memory": (len(errors), len(warnings)) if has_memory else None, "catalog": catalog(root)}


def fmt_tokens(n):
    return f"{n / 1e6:.2f}M" if n >= 1e6 else f"{n / 1e3:.1f}k" if n >= 1e3 else str(n)


def fmt_cost(g):
    text = f"${g['cost']:.2f}"
    return text + (" +" if g["unpriced"] else "")


def render_text(d, L):
    t = d["total"]
    out = [f"{L['title']} - {os.path.basename(d['root'])} "
           f"({L['days'].format(d['days']) if d['days'] else L['all']})",
           f"{L['cost']}: ${t['cost']:.2f}   {L['tokens']}: {fmt_tokens(t['tokens'])}   "
           f"{L['calls']}: {t['calls']}   {L['hit']}: {d['hit']:.0%}   {L['unpriced']}: {fmt_tokens(t['unpriced'])}"]
    if not d["rows"]:
        out.append(L["nodata"])
    for title, groups in ((L["by_agent"], d["by_agent"]), (L["by_model"], d["by_model"])):
        out.append(f"\n{title}")
        for name, g in groups:
            out.append(f"  {name[:34]:34} {fmt_tokens(g['tokens']):>9} {fmt_cost(g):>10} {g['runs']:>4}x")
    out.append(f"\n{L['memory']}: " + (L["nomem"] if d["memory"] is None else
                                          f"{d['memory'][0]} {L['errors']}, {d['memory'][1]} {L['warnings']}"))
    out.append(L["note"])
    return "\n".join(out)


def render_html(d, L):
    e = html.escape
    t = d["total"]
    peak = max((g["tokens"] for _, g in d["by_agent"]), default=1) or 1

    def table(groups, first):
        rows = "".join(
            f"<tr><td>{e(name)}</td><td class=n>{fmt_tokens(g['tokens'])}</td><td class=n>{e(fmt_cost(g))}</td>"
            f"<td class=n>{g['runs']}</td><td><div class=bar style='width:{100 * g['tokens'] / peak:.1f}%'></div></td></tr>"
            for name, g in groups)
        return (f"<div class=wrap><table><tr><th>{e(first)}</th><th class=n>{L['tokens']}</th>"
                f"<th class=n>{L['cost']}</th><th class=n>{L['runs']}</th><th>{L['share']}</th></tr>{rows}</table></div>")

    sessions = "".join(f"<tr><td>{e(s[:8])}</td><td>{e((g['start'] or '')[:16].replace('T', ' '))}</td>"
                       f"<td class=n>{fmt_tokens(g['tokens'])}</td><td class=n>{e(fmt_cost(g))}</td></tr>"
                       for s, g in d["sessions"])
    agents = "".join(f"<tr><td>{e(n)}</td><td>{e(m)}</td><td>{e(ef)}</td></tr>" for n, m, ef in d["catalog"])
    memory = L["nomem"] if d["memory"] is None else f"{d['memory'][0]} {L['errors']}, {d['memory'][1]} {L['warnings']}"
    kpis = [(L["cost"], f"${t['cost']:.2f}"), (L["tokens"], fmt_tokens(t["tokens"])),
            (L["calls"], str(t["calls"])), (L["hit"], f"{d['hit']:.0%}"),
            (L["unpriced"], fmt_tokens(t["unpriced"]))]
    tiles = "".join(f"<div class='card kpi'><b>{e(v)}</b><span>{e(k)}</span></div>" for k, v in kpis)
    period = L["days"].format(d["days"]) if d["days"] else L["all"]
    return f"""<!doctype html><html lang="{L is T['it'] and 'it' or 'en'}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(L['title'])}</title>
<style>
:root{{--bg:#f6f7f9;--card:#fff;--fg:#1c1d21;--muted:#6a6d76;--line:#e2e4ea;--bar:#4f6bed}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111316;--card:#1a1c20;--fg:#eceef3;--muted:#9a9ea8;--line:#2a2d33;--bar:#7d93ff}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 16px}} h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:15px;margin:28px 0 10px}}
.muted{{color:var(--muted)}} .kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:16px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}}
.kpi b{{display:block;font-size:22px}} .kpi span{{color:var(--muted);font-size:12px}}
.wrap{{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px}}
table{{width:100%;border-collapse:collapse}} th,td{{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}}
th{{font-size:12px;color:var(--muted);font-weight:600}} .n{{text-align:right;font-variant-numeric:tabular-nums}}
.bar{{height:8px;min-width:2px;background:var(--bar);border-radius:4px}} td:last-child{{width:30%}}
</style></head><body><main>
<h1>{e(L['title'])}</h1><div class=muted>{e(os.path.basename(d['root']))} &middot; {L['period']}: {e(period)} &middot; {time.strftime('%Y-%m-%d %H:%M')}</div>
<div class=kpis>{tiles}</div>
<h2>{L['by_agent']}</h2>{table(d['by_agent'], L['agent'])}
<h2>{L['by_model']}</h2>{table(d['by_model'], L['model'])}
<h2>{L['sessions']}</h2><div class=wrap><table><tr><th>{L['session']}</th><th>{L['start']}</th><th class=n>{L['tokens']}</th><th class=n>{L['cost']}</th></tr>{sessions}</table></div>
<h2>{L['memory']}</h2><div class=card>{e(memory)}</div>
<h2>{L['catalog']}</h2><div class=wrap><table><tr><th>{L['agent']}</th><th>{L['model']}</th><th>{L['effort']}</th></tr>{agents}</table></div>
<p class=muted>{e(L['note'])}{'' if d['rows'] else ' ' + e(L['nodata'])}</p>
</main></body></html>"""


def main():
    ap = argparse.ArgumentParser(description="Token and cost dashboard of a repository.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--days", type=int, default=30, help="0 for all time")
    ap.add_argument("--session", help="a session id, or 'latest'")
    ap.add_argument("--html", nargs="?", const="", help="write an HTML page (default path if empty)")
    ap.add_argument("--open", action="store_true", help="open the HTML page in the browser")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    L = T[lang()]
    d = build(args.root, args.days or None, args.session)
    if args.json:
        print(json.dumps({k: v for k, v in d.items() if k != "rows"}, default=list, indent=2))
        return
    print(render_text(d, L))
    if args.html is not None:
        path = args.html or os.path.join(os.path.expanduser("~"), ".team-workflow", "dashboards",
                                         project_slug(args.root) + ".html")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(render_html(d, L))
        print(f"\nHTML: {path}")
        if args.open:
            webbrowser.open("file://" + os.path.abspath(path))


if __name__ == "__main__":
    main()
